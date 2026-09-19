#!/usr/bin/env python3
"""crudo.py v1 (19/09/2026) - la entrada de clips de prensa a la cadena.

POR QUE EXISTE
--------------
Cristopher quiere piezas con metraje real de la noticia, y tiene razon: es lo que rinde y es lo
que el estudio ya habia logrado antes. Lo que cambia es COMO entra ese clip.

Hasta hoy entraba a mano, dentro de una sesion de chat, sin que quedara escrito de donde salio.
Eso tiene dos problemas: no se puede automatizar, y -el grave- no deja constancia de con que
derecho se uso un video ajeno. Este modulo es esa constancia, y es lo que permite automatizar el
resto: Cristopher consigue el clip y anota cuatro datos; de ahi en adelante la cadena sigue sola.

LA PUERTA ES LA DEL ART. 71 B
-----------------------------
No se reimplementa aqui: se le pregunta a `motor/metraje.py`, que guarda el texto verificado de
la Ley 17.336 (idNorma 28933) y sus tres condiciones. Un clip que no las cumpla no entra a la
cola, y por lo tanto no se renderiza ni se publica. Si algun dia hay que discutir una pieza, la
respuesta esta escrita en el repo, con fecha, y no en la memoria de nadie.

QUE NO GUARDA
-------------
No guarda el video. Regla del repositorio: nada de media. Guarda la URL y los datos de la cita.

Uso:
    python3 motor/crudo.py agregar --slot 3 \\
        --url https://.../clip.mp4 \\
        --fuente "24 Horas" --titulo "Balance de Fiestas Patrias" --autor "TVN" --segundos 7
    python3 motor/crudo.py revisar
"""

import argparse
import json
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "motor"))

import cadena as C                                            # noqa: E402
import metraje as M                                           # noqa: E402

DIR_CRUDO = os.path.join(RAIZ, "crudo")


def ruta_cola(fecha):
    return os.path.join(RAIZ, "cola", "%s.json" % fecha)


def ruta_pendientes(fecha):
    return os.path.join(DIR_CRUDO, "%s.json" % fecha)


def cargar_pendientes(fecha):
    r = ruta_pendientes(fecha)
    if os.path.exists(r):
        with open(r, encoding="utf-8") as f:
            return json.load(f)
    return {}


def guardar_pendientes(fecha, datos):
    os.makedirs(DIR_CRUDO, exist_ok=True)
    with open(ruta_pendientes(fecha), "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)


def cmd_agregar(a):
    fecha = a.fecha or C.hoy()
    met = {
        "base": "cita",
        "url": a.url,
        "fuente": a.fuente,
        "titulo": a.titulo,
        "autor": a.autor or a.fuente,   # en prensa el autor suele SER el medio
        "segundos": a.segundos,
        "proposito": a.proposito,
    }

    ok, motivos = M.validar(met, tope_cita=a.tope)
    if not ok:
        print("RECHAZADO. El clip no entra a la cola:")
        for m in motivos:
            print("  - %s" % m)
        print()
        print("Nada de esto es un capricho del programa: son las tres condiciones del art. 71 B")
        print("de la Ley 17.336, que es lo que permite usar un clip ajeno sin pedir permiso.")
        return 2

    print("ACEPTADO para la ranura #%d del %s" % (a.slot, fecha))
    print("  credito que va EN PANTALLA: %s" % M.credito(met))
    print("  fragmento: %.1f s (tope %.1f)" % (float(a.segundos), a.tope))

    # Si la pieza ya esta encolada, se le pega el metraje. Si no, queda pendiente y se aplica
    # sola cuando la tarea de la noche escriba la cola.
    cola = ruta_cola(fecha)
    if os.path.exists(cola):
        with open(cola, encoding="utf-8") as f:
            datos = json.load(f)
        for p in datos.get("piezas", []):
            if int(p.get("slot", -1)) == a.slot:
                p["metraje"] = met
                p["prensa"] = True
                with open(cola, "w", encoding="utf-8") as f:
                    json.dump(datos, f, ensure_ascii=False, indent=1)
                print("  pegado a la pieza %s de cola/%s.json" % (p.get("id", "?"), fecha))
                print("  COMMITEA cola/%s.json o el render no lo vera." % fecha)
                return 0
        print("  la ranura #%d no esta en la cola todavia." % a.slot)

    pend = cargar_pendientes(fecha)
    pend[str(a.slot)] = met
    guardar_pendientes(fecha, pend)
    print("  guardado en crudo/%s.json; 'aplicar' lo pega cuando la cola exista." % fecha)
    print("  COMMITEA crudo/%s.json." % fecha)
    return 0


def cmd_aplicar(a):
    """Pega los pendientes a la cola. Lo corre la tarea de la noche despues de encolar."""
    fecha = a.fecha or C.hoy()
    pend = cargar_pendientes(fecha)
    if not pend:
        print("no hay clips pendientes para %s." % fecha)
        return 0
    cola = ruta_cola(fecha)
    if not os.path.exists(cola):
        print("hay %d clips pendientes pero cola/%s.json no existe todavia." % (len(pend), fecha))
        return 1
    with open(cola, encoding="utf-8") as f:
        datos = json.load(f)
    pegados = 0
    for p in datos.get("piezas", []):
        met = pend.get(str(p.get("slot")))
        if not met:
            continue
        ok, motivos = M.validar(met, tope_cita=a.tope)
        if not ok:
            print("  #%s NO se pega: %s" % (p.get("slot"), motivos[0]))
            continue
        p["metraje"] = met
        p["prensa"] = True
        pegados += 1
        print("  #%s <- %s" % (p.get("slot"), M.credito(met)))
    with open(cola, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=1)
    print("%d clips pegados a la cola de %s. COMMITEA cola/ y crudo/." % (pegados, fecha))
    return 0


def cmd_revisar(a):
    fecha = a.fecha or C.hoy()
    pend = cargar_pendientes(fecha)
    cola = ruta_cola(fecha)
    con, sin = [], []
    if os.path.exists(cola):
        with open(cola, encoding="utf-8") as f:
            for p in json.load(f).get("piezas", []):
                (con if (p.get("metraje") or {}).get("url") else sin).append(p)
    print("CLIPS DE PRENSA EN %s" % fecha)
    print("  pegados a la cola : %d" % len(con))
    for p in con:
        print("      #%-2s %s" % (p.get("slot"), M.credito(p["metraje"])))
    print("  pendientes        : %d %s" % (len(pend), sorted(pend) or ""))
    print("  piezas sin clip   : %d %s" % (len(sin), [p.get("slot") for p in sin] or ""))
    if sin:
        print()
        print("Las que no tienen clip de prensa salen con metraje de banco. No es un fallo:")
        print("es lo que hay cuando no se consiguio clip para ese tema.")
    return 0


def main():
    ap = argparse.ArgumentParser(description="Entrada de clips de prensa, con su cita.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("agregar", help="anota un clip para una ranura")
    g.add_argument("--slot", type=int, required=True)
    g.add_argument("--url", required=True, help="de donde se baja el clip")
    g.add_argument("--fuente", required=True, help="el medio: '24 Horas', 'Meganoticias'...")
    g.add_argument("--titulo", required=True, help="titulo de la nota citada")
    g.add_argument("--autor", help="si no se pasa, se usa la fuente")
    g.add_argument("--segundos", type=float, required=True, help="cuanto dura el fragmento")
    g.add_argument("--proposito", default="critica", choices=list(M.PROPOSITOS))
    g.set_defaults(func=cmd_agregar)

    p2 = sub.add_parser("aplicar", help="pega los pendientes a la cola del dia")
    p2.set_defaults(func=cmd_aplicar)

    p3 = sub.add_parser("revisar", help="que piezas llevan clip de prensa")
    p3.set_defaults(func=cmd_revisar)

    for x in (g, p2, p3):
        x.add_argument("--fecha")
        x.add_argument("--tope", type=float, default=M.SEGUNDOS_CITA,
                       help="segundos maximos del fragmento (decision del estudio, no de la ley)")
    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
