#!/usr/bin/env python3
"""leychile.py v1 (19/09/2026) - verifica una afirmacion legal contra LeyChile, sin fallar callado.

POR QUE EXISTE
--------------
`motor/PRODUCIR.md` paso 1 manda verificar el derecho ANTES de escribir el guion, con una
llamada a `https://www.leychile.cl/Consulta/obtxml?opt=7&idNorma=<id>`. Medido el 19/09/2026,
ese procedimiento esta ROTO y falla en silencio:

    curl "https://www.leychile.cl/Consulta/obtxml?opt=7&idNorma=230132"
      -> http=401  bytes=0   y curl SALE CON CODIGO 0

    el mismo con -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
      -> http=200  bytes=5754

LeyChile empezo a exigir User-Agent de navegador. Sin el devuelve 401 con cuerpo vacio, y como
curl termina en 0, el archivo queda vacio sin que nadie se entere. Una tarea que siga el
procedimiento al pie de la letra busca la frase en un documento de cero bytes, no la encuentra,
y **no tiene forma de distinguir "la ley no dice eso" de "no descargue nada"**. Para un estudio
juridico esa confusion es la peor de todas: es la que deja salir al aire una afirmacion legal
que nadie comprobo.

SEGUNDA TRAMPA, la de las tildes al reves
-----------------------------------------
El XML de LeyChile trae las tildes como entidades: dice `d&#237;as`, no `días`. Buscar "días"
en el XML crudo no encuentra nada aunque la frase este ahi. Es el mismo genero de defecto que
el del 15/09 -plegar tildes y volverse ciego a "anos"- pero al reves: aqui hay que DESPLEGAR
las entidades antes de comparar, o el control da negativo sobre texto que si esta.

Por eso este archivo hace las dos cosas: manda el User-Agent y decodifica las entidades. Y si
el documento llega vacio, corto o sin <Norma>, **no dice "no encontrado": dice que no pudo
verificar**, que es una respuesta distinta y sale con otro codigo.

DONDE CORRE
-----------
LeyChile NO se alcanza desde el contenedor de Claude (medido el 19/09: el proxy de egress
responde `connect_rejected`). Si se alcanza desde el sandbox de Higgsfield y desde los runners
de GitHub Actions. Por eso la verificacion de verdad vive en `.github/workflows/render-diario.yml`,
que corre en un runner: ahi hay red y ahi el control puede BLOQUEAR el render de una pieza cuya
afirmacion legal no cuadre. `motor/cola.py` tambien lo intenta al encolar y, cuando no hay red,
lo dice y deja constancia en vez de aparentar que verifico.

CODIGOS DE SALIDA
-----------------
    0  la frase esta en la norma
    1  la norma se leyo bien y la frase NO esta            -> la afirmacion es falsa o mal citada
    2  no se pudo verificar (sin red, 401, documento vacio) -> NO es lo mismo que 1

USO
---
    python3 motor/leychile.py 230132 "feriados obligatorios e irrenunciables"
    python3 motor/leychile.py --cola cola/2026-09-19.json     # verifica una tanda entera
"""

import argparse
import html
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.request

URL = "https://www.leychile.cl/Consulta/obtxml?opt=7&idNorma=%s"
# Sin esto LeyChile devuelve 401 con cuerpo vacio (medido 19/09/2026).
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
MIN_BYTES = 500          # una norma real no baja de esto; menos es un documento roto

NO_VERIFICABLE = 2
NO_ESTA = 1
OK = 0
OTRO_ARTICULO = 3        # la frase esta en la norma, pero en un articulo distinto del citado
ART_NO_UBICADO = 4       # la frase esta, pero no se pudo ubicar el articulo citado para cotejar

# Como LeyChile encabeza cada articulo. El Codigo del Trabajo escribe "Art. 160.", el Codigo
# Civil "Art. 2314." y la Ley de Transito "Articulo 196 C.-". Se busca sobre el texto YA
# plegado, donde la puntuacion es espacio, asi que la forma comun es "art" o "articulo" y el
# numero. El sufijo (bis, ter, o una letra suelta) es parte del numero: sin el, 196 y 196 C
# serian el mismo articulo, que es justo el error que este control existe para cazar.
RE_ART = re.compile(r"\bart(?:iculo)?\s+(\d{1,4})(?:\s+(bis|ter|quater|[a-z](?![a-z])))?\b")


def _plano(s):
    """Pliega tildes y signos para comparar DOS REDACCIONES de la misma frase.

    Ojo con no confundir esto con el control 6 de control.py, que hace lo contrario a proposito:
    alli plegar tildes seria ceguera ('anos' vs 'años'), porque la pregunta es si el texto esta
    bien escrito. Aqui la pregunta es otra -si la frase citada aparece en la norma- y un acento
    de mas o de menos en la cita no puede decidirla.
    """
    return _plano_con_mapa(s)[0]


def _plano_con_mapa(s):
    """Como _plano, pero devuelve ademas el indice ORIGINAL de cada caracter plegado.

    Hace falta para citar el contexto correcto. Estimar la posicion por regla de tres sobre
    los largos -que era la primera version- apunta a otro parrafo de la norma, y el contexto
    existe justamente para que un humano compruebe de un vistazo que la cita es la que dice
    ser. Un contexto que apunta a otra parte es peor que no mostrarlo.
    """
    salida, mapa = [], []
    for i, ch in enumerate(s or ""):
        d = unicodedata.normalize("NFD", ch.lower())
        d = "".join(c for c in d if unicodedata.category(c) != "Mn")
        for c in d:
            if not re.match(r"[a-z0-9]", c):
                c = " "
            if c == " " and (not salida or salida[-1] == " "):
                continue
            salida.append(c)
            mapa.append(i)
    while salida and salida[-1] == " ":
        salida.pop()
        mapa.pop()
    return "".join(salida), mapa


def clave_art(numero, sufijo=None):
    """'196', 'C' -> '196c'. Normaliza para comparar la cita con el encabezado de la norma."""
    n = re.sub(r"[^0-9a-z]", "", _plano(str(numero or "")))
    if sufijo:
        n += re.sub(r"[^0-9a-z]", "", _plano(str(sufijo)))
    return n


def _orden(numero, sufijo):
    """Clave de orden de un articulo. 196 < 196 A < 196 B; 5 < 5 bis."""
    return (int(numero), (sufijo or ""))


def encabezados(plano_norma):
    """[(orden, clave, posicion)] de todo lo que se lee como encabezado de articulo, SIN filtrar."""
    return [(_orden(m.group(1), m.group(2)), clave_art(m.group(1), m.group(2)), m.start())
            for m in RE_ART.finditer(plano_norma)]


def tramos_de(marcas, quiere):
    """Los tramos que ocupa el articulo 'quiere' (clave ya normalizada).

    Un articulo empieza en su encabezado y termina en el del SIGUIENTE, pero "el siguiente" no
    es el proximo texto que parezca un encabezado: el XML intercala, dentro del cuerpo, las
    notas que dicen que ley modifico ese articulo, y se leen igual. En mitad del articulo 160
    del Codigo del Trabajo aparece "Art. 2o invocando una o mas de las siguientes causales", y
    despues del 2313 del Codigo Civil, "2313 (DEL ART. 2)". Tomarlas por encabezados partia el
    articulo en dos y dejaba la frase fuera de su propio articulo.

    Como los articulos de una norma van en orden creciente, el siguiente es el primer
    encabezado POSTERIOR cuyo numero sea mayor. Lo que quede en medio con un numero menor es
    una nota, y va dentro. Un tramo que llega al final de la norma se marca con fin None.
    """
    tramos = []
    for i, (orden, clave, pos) in enumerate(marcas):
        if clave != quiere:
            continue
        fin_t = None
        for orden2, _, pos2 in marcas[i + 1:]:
            if orden2 > orden:
                fin_t = pos2
                break
        tramos.append((pos, fin_t))
    return tramos


def bajar(id_norma, timeout=60):
    """Devuelve (texto_plano, None) o (None, motivo_por_el_que_no_se_pudo)."""
    req = urllib.request.Request(URL % id_norma, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            crudo = r.read().decode("utf-8", "replace")
            codigo = r.getcode()
    except urllib.error.HTTPError as e:
        motivo = "LeyChile respondio HTTP %s" % e.code
        if e.code == 401:
            motivo += " (falta el User-Agent de navegador: es la trampa del 19/09)"
        return None, motivo
    except Exception as e:
        return None, "no se pudo alcanzar LeyChile (%s: %s)" % (type(e).__name__, e)

    if len(crudo) < MIN_BYTES:
        return None, ("LeyChile devolvio %d bytes con HTTP %s: documento vacio o truncado. "
                      "NO es que la frase no este; es que no hay norma que leer."
                      % (len(crudo), codigo))
    if "<Norma" not in crudo:
        return None, "la respuesta no es una norma (no trae <Norma>): %s" % crudo[:160]

    # Las tildes vienen como entidades (d&#237;as). Sin desplegarlas, el control da negativo
    # sobre texto que si esta.
    texto = html.unescape(crudo)
    texto = re.sub(r"<[^>]+>", " ", texto)
    return re.sub(r"\s+", " ", texto), None


def verificar(id_norma, frase, timeout=60, articulo=None):
    """Devuelve (codigo, detalle).

    Con 'articulo' no basta con que la frase este EN LA NORMA: tiene que estar en ESE articulo.
    El 19/09/2026 tres piezas publicadas citaban 'Ley 18.290, articulo 110' para hablar de
    manejar en estado de ebriedad. La frase existe en la ley -en los articulos 115 A y 196 E-
    pero el articulo 110 trata de los semaforos. El control anterior las daba por buenas porque
    solo preguntaba si la frase aparecia en alguna parte, y "en alguna parte" no es una cita."""
    texto, motivo = bajar(id_norma, timeout)
    if texto is None:
        return NO_VERIFICABLE, motivo

    plano_norma, mapa = _plano_con_mapa(texto)
    plano_frase = _plano(frase)
    if not plano_frase:
        return NO_VERIFICABLE, "la frase a buscar esta vacia"

    posiciones = [m.start() for m in re.finditer(re.escape(plano_frase), plano_norma)]
    if not posiciones:
        # El XML intercala las notas al margen DENTRO del texto. Medido el 19/09 en el articulo
        # 8 del Codigo del Trabajo, que se lee literalmente:
        #     "hace presumir la ART. PRIMERO existencia de un contrato de trabajo"
        # La ley SI dice lo que se le atribuye, pero "hace presumir la existencia" -veintisiete
        # caracteres- no aparece, porque una nota la parte por la mitad. El aviso va SIEMPRE y
        # no solo en citas largas: ese caso demostro que basta con muy poco para cruzar una nota.
        aviso = (" AVISO: el XML de LeyChile intercala notas al margen DENTRO del texto (medido: "
                 "'hace presumir la ART. PRIMERO existencia de un contrato de trabajo'), asi que "
                 "una cita puede quedar partida y dar falso negativo. Antes de darla por falsa, "
                 "reintenta con un tramo mas corto y continuo.")
        return NO_ESTA, ("la norma %s se leyo completa (%d caracteres) y NO contiene esa frase. "
                         "O la cita esta mal, o el articulo es otro, o la partio una nota.%s"
                         % (id_norma, len(texto), aviso))

    def contexto_de(i):
        """Contexto en el texto ORIGINAL, con sus tildes, anclado en la posicion real."""
        ini = mapa[i]
        fin = mapa[min(i + len(plano_frase), len(mapa)) - 1] + 1
        return texto[max(0, ini - 170):fin + 170].strip()

    if not articulo:
        return OK, contexto_de(posiciones[0])

    quiere = clave_art(articulo)
    marcas = encabezados(plano_norma)
    tramos = tramos_de(marcas, quiere)
    if not tramos:
        return ART_NO_UBICADO, ("la frase SI esta en la norma %s, pero no se pudo ubicar el "
                                "articulo %s para cotejar. Revisalo a mano antes de publicar. "
                                "contexto: ...%s..." % (id_norma, articulo, contexto_de(posiciones[0])))

    # Una frase puede repetirse en varios articulos -la prohibicion en uno y la pena en otro-.
    # Basta con que UNA aparicion caiga en el articulo citado para que la cita sea correcta.
    for i in posiciones:
        for ini_t, fin_t in tramos:
            if ini_t <= i and (fin_t is None or i < fin_t):
                return OK, contexto_de(i)

    donde = []
    for i in posiciones:
        previo = [c for _, c, pos in marcas if pos <= i]
        if previo and previo[-1] not in donde:
            donde.append(previo[-1])
    return OTRO_ARTICULO, ("la frase esta en la norma %s pero en el articulo %s, NO en el %s que "
                           "cita la pieza. Corrige la cita o cambia el articulo. contexto: ...%s..."
                           % (id_norma, ", ".join(donde) or "?", articulo, contexto_de(posiciones[0])))


def cmd_cola(ruta, timeout=60):
    """Verifica la tanda entera. Devuelve el numero de piezas que NO pasaron."""
    with open(ruta, encoding="utf-8") as f:
        piezas = json.load(f)["piezas"]
    malas = 0
    for p in piezas:
        codigo, detalle = verificar(p.get("norma", ""), p.get("frase", ""), timeout,
                                    articulo=p.get("articulo"))
        etiqueta = {OK: "OK", NO_ESTA: "FALSA", NO_VERIFICABLE: "NO VERIFICABLE",
                    OTRO_ARTICULO: "OTRO ARTICULO", ART_NO_UBICADO: "ARTICULO SIN UBICAR"}[codigo]
        print("#%-2s %-6s norma %-8s art %-6s %s"
              % (p.get("slot"), p.get("id"), p.get("norma"), p.get("articulo"), etiqueta))
        print("     frase: %s" % (p.get("frase") or "")[:100])
        print("     %s" % detalle[:300])
        if codigo != OK:
            malas += 1
    print("\nVERIFICACION LEGAL: %d piezas, %d sin verificar o falsas" % (len(piezas), malas))
    return malas


def main():
    ap = argparse.ArgumentParser(description="Verifica una afirmacion legal contra LeyChile.")
    ap.add_argument("norma", nargs="?", help="idNorma de LeyChile (ej. 230132)")
    ap.add_argument("frase", nargs="?", help="frase textual que debe aparecer en la norma")
    ap.add_argument("--articulo", help="exige ademas que la frase caiga DENTRO de ese articulo")
    ap.add_argument("--cola", help="verifica todas las piezas de una cola")
    ap.add_argument("--timeout", type=int, default=60)
    args = ap.parse_args()

    if args.cola:
        sys.exit(1 if cmd_cola(args.cola, args.timeout) else 0)
    if not args.norma or not args.frase:
        ap.error("da norma y frase, o --cola")

    codigo, detalle = verificar(args.norma, args.frase, args.timeout, articulo=args.articulo)
    if codigo == OK:
        print("OK - la norma %s contiene la frase%s."
              % (args.norma, (" en el articulo %s" % args.articulo) if args.articulo else ""))
        print("contexto: ...%s..." % detalle)
    elif codigo == NO_ESTA:
        print("FALSA - %s" % detalle)
    elif codigo == OTRO_ARTICULO:
        print("OTRO ARTICULO - %s" % detalle)
    elif codigo == ART_NO_UBICADO:
        print("ARTICULO SIN UBICAR - %s" % detalle)
    else:
        print("NO VERIFICABLE - %s" % detalle)
        print("(no es lo mismo que falsa: aqui no se pudo leer la norma)")
    sys.exit(codigo)


if __name__ == "__main__":
    main()
