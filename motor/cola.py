#!/usr/bin/env python3
"""cola.py v1 (19/09/2026) - arma la tanda del dia, pieza por pieza, validando antes de encolar.

POR QUE EXISTE
--------------
`render-diario.yml` renderiza lo que encuentre en `cola/<fecha>.json`. Alguien tiene que
escribir ese archivo, y hasta el 19/09 ese alguien era una tarea larga que armaba el job entero
en memoria y lo mandaba de una vez: si moria en la pieza 7, las 6 anteriores se perdian con ella.

Aqui la tanda se arma DE A UNA PIEZA y cada una queda escrita en el acto. Una tarea que muere en
la pieza 7 deja 6 encoladas y la siguiente sigue en la 7. Es la misma idea del libro de cuentas,
aplicada al paso anterior.

VALIDA ANTES DE ENCOLAR, NO DESPUES
-----------------------------------
El razonamiento es el del control 6 de `control.py`: *"esto se caza mirando el texto, no la
pieza: sale gratis y evita gastar una sintesis entera."* Si el guion llega con "anos" en vez de
"años", el lugar barato de pararlo es aqui -antes de que el runner gaste 3 minutos de render- y
no en el control de la pieza ya hecha. Lo mismo con el gancho: `produce.py` ya rechaza una pieza
de lamina cuyo gancho no este en el banco (CONTROL 0), pero lo rechaza despues de haber armado
la tanda. Aqui se rechaza al encolar.

Los controles que corre, todos BLOQUEANTES:
  A. control 6 de control.py sobre TODO el texto: los 5 tramos de voz y lo que va en pantalla
     (gancho, los 3 puntos y el cierre). Regla dura 2.
  B. CONTROL 0: el gancho de una pieza de lamina sale de motor/ganchos/cola.json (exentas las
     de prensa, cuyo gancho es el titular del dia).
  C. estructura: 5 tramos de voz, 3 puntos, y los campos que produce.py necesita.
  D. derecho: norma (idNorma de LeyChile), articulo y frase verificada. PRODUCIR.md paso 1.
  E. (retirado el 19/09) destino. Antes se exigia una `upload_url` presignada de Higgsfield
     escrita en la pieza. Se quito por una razon de transcripcion, no de gusto: esa url mide
     ~2.400 caracteres y la copiaba A MANO la sesion que armaba la cola, caracter por caracter.
     Diez piezas al dia eran 24.000 caracteres transcritos sin equivocarse ni una vez. Ahora el
     mp4 lo aloja el workflow como asset de una Release de GitHub: url corta, publica, sin
     caducidad y sin que nadie copie nada.

Si pasa los cinco, la pieza entra a la cola Y la ranura avanza en el libro de cuentas hasta
`guion`, llamando a `cadena.py` (las reglas viven en un solo lugar).

USO
---
    python3 motor/cola.py agregar --slot 3 --archivo pieza.json
    python3 motor/cola.py revisar            # valida la cola entera antes del render
    python3 motor/cola.py ver

Formato de pieza.json (es el job.json de produce.py mas los campos de trazabilidad):

    {"id":"1103","materia":"laboral","rotulo":"NOTICIA DE HOY","prensa":false,
     "tema":"Finiquito: el plazo real son 10 dias habiles",
     "fuente":"Direccion del Trabajo, dictamen 19/09/2026",
     "norma":"207436","articulo":"177","frase":"dentro de diez dias habiles",
     "hook":"https://assets.mixkit.co/videos/39912/39912-720.mp4",
     "gancho":"Te pusieron turno el 18 y el 19 sin preguntarte.",
     "puntos":[{"t":"...","d":"..."},{"t":"...","d":"..."},{"t":"...","d":"..."}],
     "cierre":"...",
     "voz":["tramo1","tramo2","tramo3","tramo4","tramo5"]}
"""

import argparse
import json
import os
import re
import subprocess
import sys
import unicodedata

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "motor"))

import cadena as C                                            # noqa: E402  mismo libro de cuentas

DIR_COLA = os.path.join(RAIZ, "cola")
BANCO = os.path.join(RAIZ, "motor", "ganchos", "cola.json")
CADENA_PY = os.path.join(RAIZ, "motor", "cadena.py")

# Los campos comunes a los dos formatos, y los propios de cada uno.
# F15 REACCION FULL es el formato de las piezas de NOTICIA: video vertical toda la duracion con
# la noticia y la narracion encima (motor/reaccion_full.py). Es lo que rinde -rev. 12 del cerebro,
# H-12: manda el TEMA- y hasta el 19/09 no estaba conectado a la cadena automatica, que por eso
# publicaba solo laminas de relleno.
CAMPOS = ("id", "materia", "voz", "tema", "fuente", "norma", "articulo", "frase")
CAMPOS_LAMINA = ("rotulo", "hook", "gancho", "puntos", "cierre")
CAMPOS_F15 = ("clips", "tag")


def ruta_cola(fecha):
    return os.path.join(DIR_COLA, "%s.json" % fecha)


def cargar_cola(fecha):
    r = ruta_cola(fecha)
    if os.path.exists(r):
        with open(r, encoding="utf-8") as f:
            return json.load(f)
    return {"fecha": fecha, "piezas": []}


def guardar_cola(tanda):
    os.makedirs(DIR_COLA, exist_ok=True)
    with open(ruta_cola(tanda["fecha"]), "w", encoding="utf-8") as f:
        json.dump(tanda, f, ensure_ascii=False, indent=1)
        f.write("\n")


def _norm(s):
    """Compara ganchos sin que una tilde decida. Copiado de produce.py a proposito: alli
    tambien se pliegan las tildes PARA ESTO, al reves que en el control 6."""
    s = unicodedata.normalize("NFD", (s or "").lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s)).strip()


def es_f15(p):
    return p.get("formato") == "F15"


def control_6(p):
    """El control 6 de control.py sobre todo el texto de la pieza: voz y pantalla."""
    try:
        import control
    except ImportError as e:
        return ["no se pudo importar motor/control.py (%s): el control 6 NO corrio. "
                "FALLA CERRADA: la pieza no se encola." % e]
    partes = list(p.get("voz") or [])
    if es_f15(p):
        # En una F15 lo que va en pantalla es el rotulo y el credito; el resto es el karaoke,
        # que sale de la propia voz.
        partes += [p.get("tag", ""), p.get("credito", "")]
    else:
        partes += [p.get("gancho", ""), p.get("cierre", "")]
        for pt in (p.get("puntos") or []):
            partes += [pt.get("t", ""), pt.get("d", "")]
    ok, malas = control.texto(" ".join(partes))
    if ok:
        return []
    return ["regla dura 2: '%s' deberia ser '%s' (%s)" % (m["dice"], m["deberia"], m["por"])
            for m in malas]


def control_0(p):
    """El gancho de una pieza de lamina sale del banco Y NO ESTA GASTADO.

    Las de prensa estan exentas: su gancho es el titular del dia.

    El segundo requisito entro el 19/09, al traer `motor/ganchos/cargar.py`: el banco lleva
    seguimiento de `usado` y su dedupe existe, en palabras de ese archivo, porque dos entradas
    indistinguibles "rompen el seguimiento de 'usado'". Un banco que registra lo gastado y un
    control que no lo mira dejan pasar la repeticion que el registro existe para evitar - que
    es el mismo defecto que `control.py` v3 arreglo en la puerta: medir sin poder bloquear.
    """
    if p.get("prensa") or es_f15(p):
        return []
    g = _norm(p.get("gancho", ""))
    if not g:
        return ["CONTROL 0: la pieza no trae gancho."]
    with open(BANCO, encoding="utf-8") as f:
        banco = json.load(f)
    libres = sum(1 for e in banco["cola"] if not e.get("usado"))
    for e in banco["cola"]:
        t = _norm(e["texto"])
        if t == g or t.startswith(g[:40]) or g.startswith(t[:40]):
            if e.get("usado"):
                return ["CONTROL 0: el gancho %s ya se gasto el %s (pieza %s). Elige uno de los "
                        "%d libres del banco: repetirlo es publicar dos veces la misma apertura."
                        % (e["id"], e["usado"], e.get("pieza", "?"), libres)]
            return []
    return ["CONTROL 0: el gancho no esta en motor/ganchos/cola.json (%d libres disponibles). "
            "Una pieza de lamina con gancho improvisado no se produce (doctrina del 13/09). Usa "
            "uno del banco o marca la pieza como prensa:true si su gancho es el titular del dia."
            % libres]


def estructura(p):
    fallas = []
    propios = CAMPOS_F15 if es_f15(p) else CAMPOS_LAMINA
    for c in CAMPOS + propios:
        if not p.get(c):
            fallas.append("falta el campo '%s'" % c)
    voz = p.get("voz") or []
    if len(voz) != 5:
        fallas.append("la voz tiene %d tramos y la regla dura 1 pide 5 (un nodo tts por tramo, "
                      "sin etiquetas <break>)" % len(voz))
    if any("<break" in str(t) for t in voz):
        fallas.append("hay una etiqueta <break> en la voz: regla dura 1, eleven la vocaliza")

    if es_f15(p):
        clips = p.get("clips") or []
        if not isinstance(clips, list) or not clips:
            fallas.append("'clips' tiene que ser una lista con al menos una URL de video")
        for u in clips:
            if not str(u).startswith("http"):
                fallas.append("un clip no parece una URL: %s" % str(u)[:60])
        # reaccion_full.py v1.1: "el TAG cabe en ~20 caracteres; lo largo va al credito".
        # Con mas, el rotulo se sale de la zona segura y pantalla_chica.py lo cuenta fuera.
        if len(p.get("tag", "")) > 20:
            fallas.append("el tag mide %d caracteres y reaccion_full.py pide ~20: lo largo va "
                          "al credito" % len(p["tag"]))
    else:
        puntos = p.get("puntos") or []
        if len(puntos) != 3:
            fallas.append("hay %d puntos y el formato pide 3" % len(puntos))
        if not str(p.get("hook", "")).startswith("http"):
            fallas.append("el clip de gancho ('hook') no parece una URL")
    return fallas


def validar(p):
    return estructura(p) + control_0(p) + control_6(p)


def cadena_cmd(*args):
    r = subprocess.run([sys.executable, CADENA_PY] + list(args),
                       capture_output=True, text=True, cwd=RAIZ)
    return r.returncode == 0, (r.stdout + r.stderr).strip()


def cmd_agregar(args):
    fecha = args.fecha or C.hoy()
    with open(args.archivo, encoding="utf-8") as f:
        p = json.load(f)
    p["slot"] = args.slot
    p.setdefault("prensa", False)

    fallas = validar(p)
    if fallas:
        print("La pieza NO se encola. %d problema(s):" % len(fallas))
        for x in fallas:
            print("  - %s" % x)
        print("\nNinguno cuesta un render: todos se ven en el texto. Corrige y vuelve a llamar.")
        return 2

    tanda = cargar_cola(fecha)
    tanda["piezas"] = [q for q in tanda["piezas"] if q.get("slot") != args.slot]
    tanda["piezas"].append(p)
    tanda["piezas"].sort(key=lambda q: q["slot"])
    guardar_cola(tanda)
    print("pieza %s encolada en la ranura #%d (%d en la cola de %s)"
          % (p["id"], args.slot, len(tanda["piezas"]), fecha))

    # El libro de cuentas avanza hasta 'guion'. Si cadena.py rechaza un paso, se dice y se para:
    # la cola queda escrita pero la ranura no miente sobre su estado.
    pasos = [
        ("tema", ["--campo", "tema=%s" % p["tema"], "--campo", "fuente=%s" % p["fuente"]]),
        ("derecho", ["--campo", "norma=%s" % p["norma"], "--campo", "articulo=%s" % p["articulo"],
                     "--campo", "frase=%s" % p["frase"]]),
        # En una F15 el papel del gancho lo hace el rotulo: es lo que abre la pieza en pantalla.
        # Se anota igual en el libro de cuentas para que 'guion' exija siempre lo mismo.
        ("guion", ["--campo", "gancho=%s" % (p.get("gancho") or p.get("tag", "")),
                   "--json", json.dumps({"tramos": p["voz"], "pieza_id": p["id"]}, ensure_ascii=False)]),
    ]
    # Saltarse los pasos que la ranura YA dio. Hace falta para re-encolar una pieza caida:
    # `reintentar` la devuelve a 'guion' y volver a marcar 'tema' seria ir hacia atras, que
    # cadena.py rechaza -con razon-. Sin esto, arreglar un guion y reponerlo era imposible.
    dia = C.cargar(fecha, obligatorio=False) or {"piezas": []}
    actual = next((q["estado"] for q in dia.get("piezas", []) if q["slot"] == args.slot), "vacio")
    for estado, extra in pasos:
        if C.indice(actual) >= C.indice(estado):
            print("  ranura #%d ya estaba en '%s'; se salta '%s'" % (args.slot, actual, estado))
            continue
        ok, salida = cadena_cmd("marcar", str(args.slot), estado, "--fecha", fecha, *extra)
        print("  %s" % salida.splitlines()[0] if salida else "")
        if not ok:
            print("  cadena.py se planto en '%s'. La cola quedo escrita; el estado no avanzo mas."
                  % estado)
            return 1
    return 0


def cmd_revisar(args):
    """Valida la cola entera. Lo corre la tarea de la noche antes de irse a dormir."""
    fecha = args.fecha or C.hoy()
    if not os.path.exists(ruta_cola(fecha)):
        print("no hay cola para %s. El render diario no tendra nada que hacer." % fecha)
        return 1
    tanda = cargar_cola(fecha)
    malas = 0
    for p in tanda["piezas"]:
        fallas = validar(p)
        if fallas:
            malas += 1
            print("#%s (%s) %d problema(s):" % (p.get("slot"), p.get("id"), len(fallas)))
            for x in fallas:
                print("   - %s" % x)
    print("COLA %s: %d piezas, %d con problemas" % (fecha, len(tanda["piezas"]), malas))
    usados = [p["slot"] for p in tanda["piezas"]]
    if len(usados) != len(set(usados)):
        print("HAY RANURAS REPETIDAS: %s" % sorted(usados))
        return 1
    return 1 if malas else 0


def cmd_ver(args):
    fecha = args.fecha or C.hoy()
    tanda = cargar_cola(fecha)
    print("COLA %s: %d piezas" % (fecha, len(tanda["piezas"])))
    for p in tanda["piezas"]:
        print("  #%-2s %-6s %s%s" % (p.get("slot"), p.get("id"),
                                     (p.get("tema") or "")[:60],
                                     "  [prensa]" if p.get("prensa") else ""))
    return 0


def main():
    ap = argparse.ArgumentParser(description="Arma la tanda del dia, validando antes de encolar.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("agregar", help="valida una pieza y la encola")
    a.add_argument("--slot", type=int, required=True)
    a.add_argument("--archivo", required=True, help="JSON de la pieza")
    a.add_argument("--fecha")
    a.set_defaults(func=cmd_agregar)

    r = sub.add_parser("revisar", help="valida la cola entera")
    r.add_argument("--fecha")
    r.set_defaults(func=cmd_revisar)

    v = sub.add_parser("ver", help="lista la cola")
    v.add_argument("--fecha")
    v.set_defaults(func=cmd_ver)

    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
