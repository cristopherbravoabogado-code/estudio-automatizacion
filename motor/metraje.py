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


# Consultas curadas por materia. NO salen del titular.
#
# El 20/09/2026 se miraron por fin por dentro las primeras piezas armadas con fotografia
# automatica, y las dos habia que tirarlas:
#   - "Las muertes en carretera del 18 subieron 87%" trajo grabados del siglo XIX -soldados de
#     la Guerra del Pacifico, un vapor, una araucaria-, porque Commons busca a texto completo
#     sobre la frase entera y lo unico que casaba era "Chile".
#   - "Faltar dos dias seguidos tras el 18" trajo fotos de una fiesta de trabajadores con CARAS
#     RECONOCIBLES (credito NOIRLab/NSF/AURA). La licencia permitia usarlas; ponerlas al lado de
#     "te pueden despedir" da a entender que esas personas son el caso. Eso no lo arregla una
#     atribucion.
#
# Un titular es una frase, no una consulta. Lo que si funciona es apuntar a la INSTITUCION de la
# que habla la noticia: el frontis de la Corte Suprema ES la noticia, y ademas no tiene dueno de
# su cara.
CONSULTAS_MATERIA = {
    "transito": ["Carabineros de Chile control carretera", "Ruta 5 Chile carretera",
                 "autopista Chile"],
    "penal":    ["Policia de Investigaciones de Chile edificio", "Carabineros de Chile cuartel",
                 "Palacio de Tribunales Santiago"],
    "laboral":  ["Ministerio del Trabajo Chile", "Palacio de La Moneda Santiago",
                 "Santiago de Chile centro edificios"],
    "civil":    ["Corte Suprema de Chile edificio", "Palacio de Tribunales Santiago",
                 "Poder Judicial Chile edificio"],
    "familia":  ["Corte de Apelaciones Chile edificio", "Palacio de Tribunales Santiago"],
}
CONSULTAS_POR_DEFECTO = ["Palacio de Tribunales Santiago", "Corte Suprema de Chile edificio"]

# Palabras vacias: no sirven para decidir si una foto viene a cuento. "chile" NO esta aqui a
# proposito: es el termino que mas discrimina de todos. Sin el, "Ruta 5 Chile carretera" trae la
# Carrera Panamericana de Mexico y "Poder Judicial Chile" la inauguracion de un juzgado en
# Misiones, Argentina. Va aparte, como requisito propio (es_de_chile).
VACIAS = set("""a al ante bajo con contra de del desde durante en entre hacia hasta la las lo los
mas mediante para por segun se sin sobre tras un una unos unas y o u e que el su sus este esta
estos estas ese esa aquel como cuando donde""".split())

# Marcadores de que la foto tiene PERSONAS como asunto. Se rechaza por omision: una foto de un
# edificio con gente de espaldas al fondo seria aceptable, un retrato no, y desde aqui no se
# puede distinguir sin mirar. Ante la duda, fuera: quedarse sin fotos para una pieza para la
# cadena, y eso se ve; publicar la cara de alguien ajeno al caso no se deshace.
#
# SE COMPARAN PALABRAS ENTERAS, NO PEDAZOS. La primera version buscaba subcadenas y fue peor que
# no tener filtro: "men" cae dentro de "monumento" y "documento", "face" dentro de "superficie",
# "person" dentro de "personal". Medido el 20/09: tiraba el edificio del Ministerio del Trabajo
# y el logo de la Direccion del Trabajo -donde no hay nadie- y en cambio dejaba pasar la
# inauguracion de un juzgado, que es una sala llena de gente. Justo al reves de lo que se pedia.
GENTE = ("people", "persons", "person", "portrait", "portraits", "retrato", "retratos",
         "personas", "hombres", "mujeres", "men", "women", "children", "ninos", "kids",
         "faces", "face", "selfie", "staff", "employees", "students", "crowd", "attendees",
         "participants", "party", "fiesta", "fiestas", "band", "musicians", "concert",
         "wedding", "family", "familia", "team", "inauguracion", "ceremonia", "visita",
         "reunion", "firma", "autoridades", "funcionarios", "manifestacion", "marcha")


def _bolsa(cand):
    """Todo el texto con el que se puede juzgar una foto, plegado y en minusculas."""
    return _plano(" ".join([cand.get("titulo") or "", cand.get("descripcion") or "",
                            cand.get("categorias") or "", cand.get("atribucion") or ""]))


def terminos_de(consulta):
    """Las palabras de la consulta que de verdad discriminan."""
    import re as _re
    return [w for w in _re.split(r"[^a-z0-9]+", _plano(consulta))
            if len(w) > 3 and w not in VACIAS]


# Lo que no es una fotografia de la noticia aunque case con la consulta. Medido el 20/09:
# "Ministerio del Trabajo Chile" devolvia el edificio UNA vez y seis variantes del mismo avatar
# de redes sociales. Seis logos seguidos con un zoom lento no son un video, son un error.
DESCARTE = ("logo", "logos", "logotipo", "avatar", "icon", "icono", "escudo", "coat", "arms",
            "mapa", "map", "diagrama", "diagram", "grafico", "chart", "bandera", "flag",
            "sello", "seal", "banner", "emblema", "emblem")


def es_ilustracion(cand):
    """True si es un logo, un mapa o un escudo: no es una foto de la noticia."""
    return bool(_palabras(_bolsa(cand)) & set(DESCARTE))


def _raiz(titulo):
    """Las primeras palabras del titulo, para no elegir seis variantes del mismo archivo."""
    import re as _re
    ws = [w for w in _re.split(r"[^a-z0-9]+", _plano(titulo)) if w]
    return " ".join(ws[:4])


def _palabras(texto):
    import re as _re
    return set(_re.split(r"[^a-z0-9]+", texto)) - {""}


def es_de_chile(cand):
    """La noticia es chilena; la foto tambien tiene que serlo."""
    return "chile" in _palabras(_bolsa(cand)) or "chilean" in _palabras(_bolsa(cand))


def pertinente(cand, terminos, minimo=2):
    """Cuantas palabras de la consulta menciona la foto.

    Con UNA basta para que casi cualquier cosa entre: "Ruta 5 Chile carretera" casaba con
    "Carrera Panamericana" solo por "carretera". Se piden dos, o todas si la consulta trae
    menos de dos palabras con contenido.
    """
    if not terminos:
        return True
    p = _palabras(_bolsa(cand))
    return sum(1 for t in terminos if t in p) >= min(minimo, len(terminos))


def tiene_gente(cand):
    """True si la foto parece tener personas como asunto. Palabras enteras, nunca pedazos."""
    return bool(_palabras(_bolsa(cand)) & set(GENTE))


def buscar(consulta, limite=6, max_mb=120, timeout=45, tipo="video", exigir=None,
           sin_gente=False):
    """Devuelve candidatos de Commons, ya filtrados por licencia y tamano.

    tipo="imagen" es lo que hace autosuficiente a la cadena. Medido el 19/09 sobre los temas
    reales del dia: en VIDEO Commons devolvio candidatos en 1 de cada 3 busquedas ("poder
    judicial chile" y "policia chile" no devolvieron nada). En FOTOGRAFIA devolvio 8 de 8, en
    los ocho temas probados: Carabineros, Poder Judicial, Corte Suprema, Congreso, PDI, Fiestas
    Patrias, carretera y Direccion del Trabajo.

    Por eso las piezas se arman con FOTOGRAFIA real animada y no con video de banco: una foto
    del frontis de la Corte Suprema es la noticia; un clip generico de un martillo de juez, no.

    LA PERTINENCIA YA NO SE DA POR SUPUESTA. Hasta el 20/09 este docstring decia que el filtro
    garantiza que se puede usar, no que sirva, y que "quien arma la cola tiene que mirar lo que
    eligio". Despues la cadena se hizo autosuficiente y ese alguien dejo de existir, sin que
    esta frase cambiara: el aviso quedo escrito y el control no. Por eso ahora 'exigir' y
    'sin_gente' filtran aqui, y CONSULTAS_MATERIA reemplaza al titular como consulta.
    """
    filtro = "filetype:bitmap" if tipo == "imagen" else "filetype:video"
    params = {
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": "%s %s" % (filtro, consulta), "gsrlimit": str(limite * 3),
        "gsrnamespace": "6", "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata|user",
        "iiextmetadatafilter": "LicenseShortName|Artist|ImageDescription|Categories|ObjectName",
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

    salida, raices = [], set()
    for pag in ((datos.get("query") or {}).get("pages") or {}).values():
        ii = (pag.get("imageinfo") or [{}])[0]
        em = ii.get("extmetadata") or {}
        lic = ((em.get("LicenseShortName") or {}).get("value") or "").strip()
        autor = ((em.get("Artist") or {}).get("value") or ii.get("user") or "").strip()
        # El campo Artist viene con HTML (enlaces). Se limpia: va a ir en pantalla.
        import re as _re
        autor = _re.sub(r"<[^>]+>", "", autor).strip()
        mb = round((ii.get("size") or 0) / 1e6, 1)
        desc = _re.sub(r"<[^>]+>", " ",
                       ((em.get("ImageDescription") or {}).get("value") or "")).strip()
        cats = ((em.get("Categories") or {}).get("value") or "").replace("|", " ").strip()

        if not licencia_sirve(lic):
            continue
        if mb > max_mb or mb == 0:
            continue
        if tipo == "imagen" and not (ii.get("mime") or "").startswith("image/"):
            continue
        cand = {
            "titulo": pag["title"][5:],
            "url": ii.get("url"),
            "licencia": lic,
            "atribucion": autor or "Wikimedia Commons",
            "fuente": "Wikimedia Commons",
            "pagina": ii.get("descriptionurl"),
            "mime": ii.get("mime"),
            "mb": mb,
            "descripcion": desc,
            "categorias": cats,
        }
        if exigir and not pertinente(cand, exigir):
            continue
        if exigir and not es_de_chile(cand):
            continue
        if sin_gente and tiene_gente(cand):
            continue
        if exigir and es_ilustracion(cand):
            continue
        if _raiz(cand["titulo"]) in raices:
            continue
        raices.add(_raiz(cand["titulo"]))
        salida.append(cand)
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


ANCHO_CREDITO = 62   # lo que cabe en el ancho de la pieza sin salirse por la derecha


def credito_varias(clips, max_nombres=3, ancho=ANCHO_CREDITO):
    """Una sola linea de credito para una pieza armada con VARIAS fotos.

    CC BY exige nombrar al autor de cada una. Con cuatro fotos, cuatro lineas no caben en
    pantalla ni se leen. Se nombran hasta tres y se dice cuantas mas hay: la mencion existe,
    es verificable y no convierte la pieza en una ficha bibliografica.

    Y SE MIDE EL LARGO. Mirando las piezas del 20/09 el credito se salia por el borde derecho:
    "Fotos: Desconocido - Revista Vea, Desconocido - En Revista Zig-..." cortado a media
    palabra. Un credito que no se lee entero no cumple la atribucion que dice cumplir, asi que
    se recorta por autores -nombrando menos y diciendo cuantos faltan- y no por caracteres.
    """
    nombres, licencias = [], []
    for c in clips:
        a_ = " ".join((c.get("atribucion") or "").split())
        if a_ and a_ not in nombres:
            nombres.append(a_)
        l_ = (c.get("licencia") or "").strip()
        if l_ and l_ not in licencias:
            licencias.append(l_)

    def linea(cuantos):
        resto = len(nombres) - cuantos
        vis = ", ".join(nombres[:cuantos]) or "?"
        if resto > 0:
            vis += " y %d mas" % resto
        return "Fotos: %s / Wikimedia Commons (%s)" % (vis, ", ".join(licencias[:2]) or "?")

    for cuantos in range(min(max_nombres, len(nombres)), 0, -1):
        if len(linea(cuantos)) <= ancho:
            return linea(cuantos)
    # Ni con un solo autor cabe. Se acorta ESE nombre hasta que quepa, no la mencion: la
    # licencia y el "y N mas" se quedan enteros porque son lo que hace verificable el credito.
    if nombres:
        resto = len(nombres) - 1
        cola = (" y %d mas" % resto if resto > 0 else "")
        molde = "Fotos: %s" + cola + " / Wikimedia Commons (%s)"
        lic = ", ".join(licencias[:1]) or "?"
        hueco = ancho - len(molde % ("", lic))
        corto = nombres[0][:max(4, hueco - 3)].rstrip(" ,-") + "..."
        return molde % (corto, lic)
    return "Fotos: Wikimedia Commons (%s)" % (", ".join(licencias[:2]) or "?")


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
