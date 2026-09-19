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
  E. destino: upload_url y media_id, que salen de `media_upload` de Higgsfield.

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
     "voz":["tramo1","tramo2","tramo3","tramo4","tramo5"],
     "upload_url":"https://...s3.amazonaws.com/...","media_id":"aaa111"}
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

CAMPOS = ("id", "materia", "rotulo", "hook", "gancho", "puntos", "cierre", "voz",
          "upload_url", "media_id", "tema", "fuente", "norma", "articulo", "frase")
CDN = "https://d2ol7oe51mr4n9.cloudfront.net/user_3IkWukwrqRk5HTPle6Rx8WbYgS3/%s.mp4"


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


def control_6(p):
    """El control 6 de control.py sobre todo el texto de la pieza: voz y pantalla."""
    try:
        import control
    except ImportError as e:
        return ["no se pudo importar motor/control.py (%s): el control 6 NO corrio. "
                "FALLA CERRADA: la pieza no se encola." % e]
    partes = list(p.get("voz") or [])
    partes += [p.get("gancho", ""), p.get("cierre", "")]
    for pt in (p.get("puntos") or []):
        partes += [pt.get("t", ""), pt.get("d", "")]
    ok, malas = control.texto(" ".join(partes))
    if ok:
        return []
    return ["regla dura 2: '%s' deberia ser '%s' (%s)" % (m["dice"], m["deberia"], m["por"])
            for m in malas]


def control_0(p):
    """El gancho de una pieza de lamina sale del banco. Las de prensa estan exentas."""
    if p.get("prensa"):
        return []
    g = _norm(p.get("gancho", ""))
    if not g:
        return ["CONTROL 0: la pieza no trae gancho."]
    with open(BANCO, encoding="utf-8") as f:
        banco = json.load(f)
    for e in banco["cola"]:
        t = _norm(e["texto"])
        if t == g or t.startswith(g[:40]) or g.startswith(t[:40]):
            return []
    return ["CONTROL 0: el gancho no esta en motor/ganchos/cola.json. Una pieza de lamina con "
            "gancho improvisado no se produce (doctrina del 13/09). Usa uno del banco o marca "
            "la pieza como prensa:true si su gancho es el titular del dia."]


def estructura(p):
    fallas = []
    for c in CAMPOS:
        if not p.get(c):
            fallas.append("falta el campo '%s'" % c)
    voz = p.get("voz") or []
    if len(voz) != 5:
        fallas.append("la voz tiene %d tramos y la regla dura 1 pide 5 (un nodo tts por tramo, "
                      "sin etiquetas <break>)" % len(voz))
    if any("<break" in str(t) for t in voz):
        fallas.append("hay una etiqueta <break> en la voz: regla dura 1, eleven la vocaliza")
    puntos = p.get("puntos") or []
    if len(puntos) != 3:
        fallas.append("hay %d puntos y el formato pide 3" % len(puntos))
    if p.get("upload_url") and not p["upload_url"].startswith("http"):
        fallas.append("upload_url no parece una URL")
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
    p["url"] = CDN % p.get("media_id", "")

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
        ("guion", ["--campo", "gancho=%s" % p["gancho"],
                   "--json", json.dumps({"tramos": p["voz"], "pieza_id": p["id"]}, ensure_ascii=False)]),
    ]
    for estado, extra in pasos:
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
