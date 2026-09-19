#!/usr/bin/env python3
"""metraje.py v1 (19/09/2026) - de donde sale el video de una pieza, y con que derecho.

POR QUE EXISTE
--------------
Cristopher, el 19/09: "no tiene clip de noticias reales, que es lo que llama la atencion... son
clips estandar de un repositorio". Tiene razon y es literal: hasta hoy el metraje salia de
Mixkit, un banco gratis, y el mismo clip de carretera vale para cualquier noticia de carretera.

Lo que pidio -el clip DE la noticia- choca con algo medido el 19/09 y anotado en METRAJE.md: las
instituciones chilenas (Poder Judicial, Fiscalia, Senado, PDI) no publican archivos de video
descargables; publican en YouTube. Y de YouTube no se baja metraje ajeno para republicarlo bajo
la marca del estudio: el expuesto seria el abogado, no el programa.

Asi que este modulo hace lo que SI se puede hacer bien: busca metraje con licencia libre, real y
descargable, y -esto es lo que lo distingue del banco de stock- obliga a que cada clip llegue con
su PROCEDENCIA.

LA REGLA, Y ES UNA PUERTA CERRADA
---------------------------------
Un clip no entra a una pieza sin tres datos: de donde salio, con que licencia, y a quien hay que
acreditar. Si falta uno, `validar()` lo rechaza. Misma doctrina que control.py -un control que se
apaga por omision no es un control- con una razon extra que aqui no es burocratica: la atribucion
es la condicion de la licencia CC BY. Publicar sin acreditar es incumplirla.

FUENTES
-------
  commons   Wikimedia Commons. Video real, licencia legible por maquina, atribucion en los
            metadatos. Cobertura delgada para la noticia chilena del dia (medido: "carabineros
            chile" no devuelve nada) y hay archivos de mas de 1 GB, asi que se filtra por tamano.

Se deja preparado para recibir una fuente de agencia licenciada (AP, Reuters, ATON) el dia que
exista contrato: es la unica via que entrega metraje del hecho concreto de cada dia.

Uso:
    python3 motor/metraje.py buscar "tribunal justicia chile" --max-mb 80
    python3 motor/metraje.py validar clip.json
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request

API = "https://commons.wikimedia.org/w/api.php"
# Identificarse es la norma de la API de Wikimedia, y ademas es lo correcto: quien sirve el
# archivo tiene derecho a saber quien lo pide.
UA = "EstudioSanBernardo/1.0 (https://github.com/cristopherbravoabogado-code/estudio-automatizacion)"

# DOS BASES LEGALES DISTINTAS, cada una con sus condiciones. Un clip entra por UNA de las dos.
#
#   base "licencia" -> el clip tiene licencia libre (Commons, CC BY, dominio publico).
#   base "cita"     -> el clip es de un medio y se usa al amparo del derecho de cita.
#
# EL TEXTO, verificado contra LeyChile el 19/09/2026 (Ley 17.336, idNorma 28933, art. 71 B):
#
#   "Es licita la inclusion en una obra, sin remunerar ni obtener autorizacion del titular, de
#    FRAGMENTOS BREVES de obra protegida, que haya sido LICITAMENTE DIVULGADA, y su inclusion se
#    realice a titulo de cita o con fines de CRITICA, ilustracion, ensenanza e investigacion,
#    siempre que SE MENCIONE SU FUENTE, TITULO Y AUTOR."
#
# Tres condiciones, y las tres son verificables por una maquina: breve, con proposito de los
# nombrados, y con fuente + titulo + autor en pantalla. Esta puerta las exige.
#
# Y un dato que importa por lo que NO dice: en toda la ley no aparece "actualidad" ni "noticias
# del dia". Chile no tiene una excepcion aparte para informar sobre la noticia. O sea que "las
# noticias son publicas" vale para los HECHOS -que no los protege nadie- pero no para la
# GRABACION que hizo un canal, que es una obra con dueno. La puerta para usarla es el 71 B.
EXIGE = ("url", "licencia", "atribucion")
EXIGE_CITA = ("url", "fuente", "titulo", "autor", "segundos", "proposito")

# El 71 B pide que la cita sea con fines de critica, ilustracion, ensenanza o investigacion.
# Comentar juridicamente una noticia es critica. Publicar el clip porque "rinde" no lo es.
PROPOSITOS = ("critica", "ilustracion", "ensenanza", "investigacion")

# "Fragmentos breves" no trae numero en la ley. Este tope NO es la ley: es el limite que el
# estudio se fija para no discutir despues, y se puede mover con --segundos. Quien decide cuanto
# es "breve" es el abogado, no el programa; lo que hace el programa es que la decision quede
# escrita y se cumpla igual en las diez piezas del dia.
SEGUNDOS_CITA = 8.0

# Licencias que permiten reuso comercial con atribucion. Se listan por nombre exacto: una
# licencia que no este aqui NO se asume buena. En particular quedan fuera las -NC (no comercial):
# el estudio publica para captar clientes, que es uso comercial, aunque no se cobre por el video.
ACEPTADAS = (
    "cc0", "public domain", "dominio publico",
    "cc by", "cc by-sa", "cc by 2.0", "cc by 3.0", "cc by 4.0",
    "cc by-sa 2.0", "cc by-sa 3.0", "cc by-sa 4.0", "cc by 3.0 cl", "cc by-sa 3.0 cl",
)


class SinRed(RuntimeError):
    """No se pudo llegar a la fuente. No es lo mismo que 'no hay candidatos'."""


def _plano(t):
    import unicodedata
    t = unicodedata.normalize("NFD", (t or "").lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def licencia_sirve(nombre):
    """True solo si la licencia esta en la lista blanca. Ante la duda, NO sirve."""
    n = _plano(nombre).replace("-", " ").strip()
    if "nc" in n.split() or "noncommercial" in n or "no comercial" in n:
        return False   # el estudio publica para captar clientes: es uso comercial
    return any(_plano(a).replace("-", " ") == n or n.startswith(_plano(a).replace("-", " "))
               for a in ACEPTADAS)


def buscar(consulta, limite=6, max_mb=120, timeout=45, tipo="video"):
    """Devuelve candidatos de Commons, ya filtrados por licencia y tamano.

    tipo="imagen" es lo que hace autosuficiente a la cadena. Medido el 19/09 sobre los temas
    reales del dia: en VIDEO Commons devolvio candidatos en 1 de cada 3 busquedas ("poder
    judicial chile" y "policia chile" no devolvieron nada). En FOTOGRAFIA devolvio 8 de 8, en
    los ocho temas probados: Carabineros, Poder Judicial, Corte Suprema, Congreso, PDI, Fiestas
    Patrias, carretera y Direccion del Trabajo.

    Por eso las piezas se arman con FOTOGRAFIA real animada y no con video de banco: una foto
    del frontis de la Corte Suprema es la noticia; un clip generico de un martillo de juez, no.

    OJO, y es el limite honesto de esto: la licencia se filtra sola, la PERTINENCIA no. En la
    prueba, "Direccion del Trabajo Chile" devolvio un logo que no tenia nada que ver. El filtro
    garantiza que se puede usar, no que sirva. Quien arma la cola tiene que mirar lo que eligio.
    """
    filtro = "filetype:bitmap" if tipo == "imagen" else "filetype:video"
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": "%s %s" % (filtro, consulta), "gsrlimit": str(limite * 3),
        "gsrnamespace": "6", "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata|user",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            datos = json.loads(r.read().decode("utf-8"))
    except Exception as e:
        # DONDE CORRE ESTO IMPORTA. El contenedor de Claude sale por un proxy que deniega
        # commons.wikimedia.org (403 al CONNECT), igual que ya pasaba con Google Trends el
        # 05/09. No es un fallo del script. Se dice con todas sus letras en vez de escupir un
        # traceback: una tarea desatendida que ve un traceback se pone a improvisar, y eso es
        # justo lo que no queremos que haga.
        raise SinRed(
            "no se pudo consultar Wikimedia Commons (%s: %s).\n"
            "Esto corre donde hay internet sin proxy: el runner de GitHub Actions o el sandbox "
            "de Higgsfield. Desde el contenedor de Claude el proxy lo deniega, y no es algo que "
            "se arregle reintentando." % (type(e).__name__, e))

    salida = []
    for pag in ((datos.get("query") or {}).get("pages") or {}).values():
        ii = (pag.get("imageinfo") or [{}])[0]
        em = ii.get("extmetadata") or {}
        lic = ((em.get("LicenseShortName") or {}).get("value") or "").strip()
        autor = ((em.get("Artist") or {}).get("value") or ii.get("user") or "").strip()
        # El campo Artist viene con HTML (enlaces). Se limpia: va a ir en pantalla.
        import re as _re
        autor = _re.sub(r"<[^>]+>", "", autor).strip()
        mb = round((ii.get("size") or 0) / 1e6, 1)

        if not licencia_sirve(lic):
            continue
        if mb > max_mb or mb == 0:
            continue
        if tipo == "imagen" and not (ii.get("mime") or "").startswith("image/"):
            continue
        salida.append({
            "titulo": pag["title"][5:],
            "url": ii.get("url"),
            "licencia": lic,
            "atribucion": autor or "Wikimedia Commons",
            "fuente": "Wikimedia Commons",
            "pagina": ii.get("descriptionurl"),
            "mime": ii.get("mime"),
            "mb": mb,
        })
        if len(salida) >= limite:
            break
    return salida


def validar(clip, tope_cita=SEGUNDOS_CITA):
    """La puerta. Devuelve (ok, motivos). Un clip entra por licencia libre o por cita."""
    if (clip.get("base") or "licencia") == "cita":
        return _validar_cita(clip, tope_cita)
    faltan = [c for c in EXIGE if not str(clip.get(c) or "").strip()]
    if faltan:
        return False, ["falta %s: sin procedencia el clip no entra" % ", ".join(faltan)]
    if not licencia_sirve(clip["licencia"]):
        return False, ["licencia '%s' no esta en la lista blanca. Ante la duda no se usa; "
                       "las -NC quedan fuera porque el estudio publica para captar clientes, "
                       "y eso es uso comercial aunque el video sea gratis." % clip["licencia"]]
    return True, []


def _validar_cita(clip, tope):
    """Las tres condiciones del art. 71 B, una por una."""
    malos = []
    faltan = [c for c in EXIGE_CITA if not str(clip.get(c) or "").strip()]
    if faltan:
        malos.append("falta %s. El 71 B exige mencionar FUENTE, TITULO y AUTOR: sin esos datos "
                     "no hay cita, hay copia." % ", ".join(faltan))

    prop = _plano(clip.get("proposito") or "")
    if prop and prop not in PROPOSITOS:
        malos.append("proposito '%s' no es uno de los del 71 B (%s). Comentar juridicamente una "
                     "noticia es critica; usarla porque rinde, no."
                     % (clip["proposito"], ", ".join(PROPOSITOS)))

    try:
        seg = float(clip.get("segundos") or 0)
    except (TypeError, ValueError):
        seg = 0.0
        malos.append("'segundos' no es un numero: no se puede comprobar que el fragmento sea breve.")
    if seg > tope:
        malos.append("el fragmento dura %.1f s y el tope del estudio es %.1f s. El 71 B habla de "
                     "FRAGMENTOS BREVES; un clip que se ve entero deja de ser cita y pasa a "
                     "sustituir al original." % (seg, tope))

    if clip.get("tapa_cintillo"):
        malos.append("este clip taparia el cintillo del medio. Justo al reves: el 71 B exige "
                     "mencionar la fuente, y ademas la propia receta del estudio dice que el "
                     "cintillo 'es lo que da credibilidad'. Se deja a la vista.")
    return (not malos), malos


def credito(clip):
    """La linea que va EN PANTALLA. No es adorno: es la condicion de poder usar el clip."""
    if (clip.get("base") or "licencia") == "cita":
        # El 71 B pide los tres: fuente, titulo y autor. Van los tres.
        autor = clip.get("autor", "?")
        titulo = clip.get("titulo", "?")
        fuente = clip.get("fuente", "?")
        if _plano(autor) == _plano(fuente):      # en prensa el autor suele SER el medio
            return "%s - \"%s\"" % (fuente, titulo)
        return "%s / %s - \"%s\"" % (autor, fuente, titulo)
    return "%s / %s (%s)" % (clip.get("atribucion", "?"), clip.get("fuente", "?"),
                             clip.get("licencia", "?"))


def cmd_buscar(a):
    try:
        res = buscar(a.consulta, limite=a.limite, max_mb=a.max_mb, tipo=a.tipo)
    except SinRed as e:
        # Codigo 2: NO SE PUDO MIRAR. Distinto de 1, que es "se miro y no hay". Misma
        # distincion que leychile.py, y por la misma razon: confundirlas hace que una tarea
        # de por bueno un "no hay" que en realidad nunca se comprobo.
        print("SIN RED: %s" % e)
        return 2
    if not res:
        print("SIN CANDIDATOS con licencia usable para: %s" % a.consulta)
        print("Es el resultado esperado en buena parte de la noticia chilena del dia: Commons")
        print("tiene poca cobertura local (ver motor/METRAJE.md). No inventes una fuente:")
        print("usa el banco de stock y deja la placa del titular citado.")
        return 1
    print("CANDIDATOS para '%s' (%d):" % (a.consulta, len(res)))
    for c in res:
        print("  %s  [%s MB, %s]" % (c["titulo"][:58], c["mb"], c["mime"]))
        print("     licencia: %-16s credito en pantalla: %s" % (c["licencia"], credito(c)))
        print("     %s" % c["url"])
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
        print("escritos en %s" % a.json)
    return 0


def cmd_validar(a):
    with open(a.archivo, encoding="utf-8") as f:
        datos = json.load(f)
    clips = datos if isinstance(datos, list) else [datos]
    malos = 0
    for c in clips:
        ok, motivos = validar(c)
        print("%-50s %s" % ((c.get("titulo") or c.get("url") or "?")[:50],
                            "OK  " + credito(c) if ok else "RECHAZADO"))
        for m in motivos:
            print("    %s" % m)
        malos += 0 if ok else 1
    print("%d de %d rechazados" % (malos, len(clips)))
    return 1 if malos else 0


def main():
    ap = argparse.ArgumentParser(description="Metraje con licencia, y con su procedencia anotada.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("buscar", help="candidatos con licencia usable")
    b.add_argument("consulta")
    b.add_argument("--limite", type=int, default=6)
    b.add_argument("--max-mb", type=float, default=120)
    b.add_argument("--json", help="escribe los candidatos en este archivo")
    b.add_argument("--tipo", default="video", choices=("video", "imagen"))
    b.set_defaults(func=cmd_buscar)
    v = sub.add_parser("validar", help="aplica la puerta a un clip o lista de clips")
    v.add_argument("archivo")
    v.set_defaults(func=cmd_validar)
    a = ap.parse_args()
    return a.func(a)


if __name__ == "__main__":
    sys.exit(main())
