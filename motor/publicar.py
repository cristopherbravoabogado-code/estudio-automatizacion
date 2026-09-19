#!/usr/bin/env python3
"""publicar.py v1 (19/09/2026) - le deja resuelto el trabajo a la micro-tarea que publica.

POR QUE EXISTE
--------------
Publicar es lo unico de la cadena que sigue necesitando una sesion de Claude: la via B de
`motor/PUBLICAR.md` (Higgsfield -> TikTok) es MCP y no tiene API REST documentada, asi que el
runner de Actions no puede hacerla. Metricool, la otra via, quedo descartada el 19/09 por el
tope de la cuenta.

Y las sesiones ABANDONAN cuando la tarea es larga: medido el 10, 11 y 19/09. La unica defensa
es que la tarea sea corta de verdad. "Corta" no es escribir un prompt breve: es que la sesion no
tenga que AVERIGUAR nada. Si la tarea tiene que leer el estado, decidir que pieza toca, buscar
su URL y recordar los cupos, ya es larga aunque el prompt tenga cinco lineas.

Este archivo le entrega todo masticado: `ficha` imprime los cuatro pasos con la URL puesta, y
lo unico que la sesion hace es ejecutarlos y anotar el resultado.

LO QUE NO HACE
--------------
No publica. No puede: no tiene las herramientas MCP. Es deliberado - asi el mismo archivo sirve
para verificar desde Actions, desde el Mac o desde una sesion, sin credenciales.

USO
---
    python3 motor/publicar.py listo          # ranuras alojadas cuya hora ya llego
    python3 motor/publicar.py ficha 3        # los 4 pasos de la ranura 3, con la URL puesta
    python3 motor/publicar.py plan           # las tareas de un disparo a crear para el dia
    python3 motor/publicar.py cupo           # cuantas van hoy contra el tope de 13/24 h
"""

import argparse
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "motor"))

import cadena as C                                            # noqa: E402

CONNECTOR = "f23f2205-1ae6-4259-8240-e6f4165bbe79"            # motor/PUBLICAR.md


def listas(dia, solo_vencidas=True):
    out = []
    for p in dia["piezas"]:
        if p["estado"] not in ("alojado", "programado"):
            continue
        if solo_vencidas and not C.vencida(p, dia["fecha"], 0):
            continue
        out.append(p)
    return out


def cmd_listo(args):
    fecha = args.fecha or C.hoy()
    dia = C.cargar(fecha)
    ahora = listas(dia)
    luego = [p for p in listas(dia, solo_vencidas=False) if p not in ahora]
    if ahora:
        print("PARA PUBLICAR AHORA (%d):" % len(ahora))
        for p in ahora:
            print("  #%d  %s  %s" % (p["slot"], p["hora_chile"], (p.get("tema") or "")[:55]))
    else:
        print("nada vencido para publicar en este momento.")
    if luego:
        print("listas y esperando su hora (%d): %s"
              % (len(luego), ", ".join("#%d a las %s" % (p["slot"], p["hora_chile"]) for p in luego)))
    return 0 if ahora else 1


def cmd_ficha(args):
    fecha = args.fecha or C.hoy()
    dia = C.cargar(fecha)
    p = C.buscar(dia, args.slot)

    if p["estado"] == "publicado":
        print("ALTO. La ranura #%d ya esta publicada (publish_id=%s, %s)."
              % (p["slot"], p.get("publish_id", "?"), p.get("publicado_en", "?")))
        print("NO la publiques de nuevo: con cuota de %d/24 h, una republicacion por descuido "
              "cuesta una pieza real del dia." % C.CUOTA_TIKTOK_24H)
        return 2
    if C.indice(p["estado"]) < C.indice("alojado"):
        print("La ranura #%d esta en '%s': todavia no hay mp4 alojado que publicar."
              % (p["slot"], p["estado"]))
        print("No es tu trabajo arreglarlo. Anotalo y termina.")
        return 1

    publicadas = sum(1 for q in dia["piezas"] if q["estado"] == "publicado")
    print("RANURA #%d - %s de %s" % (p["slot"], p["hora_chile"], fecha))
    print("tema: %s" % p.get("tema", "(sin tema)"))
    print("hoy van %d publicadas; el tope de la via B son %d/24 h."
          % (publicadas, C.CUOTA_TIKTOK_24H))
    print()
    print("LOS CUATRO PASOS (motor/PUBLICAR.md, via B):")
    print("  1. media_import_url  con: %s" % p.get("url"))
    print("  2. tiktok_prepare_publish  connector_id=%s  -> publish_session_id" % CONNECTOR)
    print("  3. tiktok_publish  con ESE publish_session_id.")
    print("     El clasificador rechaza el PRIMER intento con 'Permission denied':")
    print("     repetir la MISMA llamada con el MISMO publish_session_id pasa al segundo.")
    print("     No hay que pedirle nada a Cristopher.")
    print("  4. tiktok_publish_status hasta PUBLISH_COMPLETE. Solo eso cuenta como publicado.")
    print()
    print("ajustes fijos: privacy_level PUBLIC_TO_EVERYONE, is_aigc true, comentarios/duo/stitch")
    print("habilitados, sin divulgacion comercial, sin musica anadida.")
    print()
    print("AL TERMINAR, una sola linea:")
    print("  python3 motor/cadena.py marcar %d publicado --campo publish_id=<el id>" % p["slot"])
    print("SI FALLA:")
    print("  python3 motor/cadena.py fallar %d --motivo \"<lo que dijo TikTok>\"" % p["slot"])
    print("Y COMMITEA estado/%s.json. Si no lo commiteas, el estado muere con el contenedor." % fecha)
    return 0


def cmd_plan(args):
    """Las tareas de un disparo del dia. Una por pieza: si una falla, cae UNA, no el dia."""
    fecha = args.fecha or C.hoy()
    dia = C.cargar(fecha)
    print("TAREAS DE UN DISPARO PARA %s (create_trigger con run_once_at)" % fecha)
    print("%-6s %-7s %-22s %s" % ("ranura", "Chile", "run_once_at (UTC)", "estado"))
    for p in dia["piezas"]:
        if p["estado"] == "publicado":
            continue
        print("%-6d %-7s %-22s %s" % (p["slot"], p["hora_chile"], p["hora_utc"], p["estado"]))
    print()
    print("prompt de cada una (cuatro lineas, sin nada que averiguar):")
    print('  "Publica la ranura N del %s. Corre: python3 motor/publicar.py ficha N' % fecha)
    print('   Sigue los cuatro pasos que imprime, marca el resultado con cadena.py y commitea.')
    print('   Si la ficha dice ALTO o que no hay mp4, NO hagas nada mas: anotalo y termina."')
    return 0


def cmd_cupo(args):
    fecha = args.fecha or C.hoy()
    dia = C.cargar(fecha)
    pub = sum(1 for p in dia["piezas"] if p["estado"] == "publicado")
    fall = sum(1 for p in dia["piezas"] if p["estado"] == C.FALLIDO)
    resto = C.CUOTA_TIKTOK_24H - pub
    print("CUPO %s: %d publicadas de %d de meta. Quedan %d publicaciones de las %d/24 h."
          % (fecha, pub, dia["meta"], resto, C.CUOTA_TIKTOK_24H))
    pendientes = dia["meta"] - pub
    if resto < pendientes:
        print("AVISO: faltan %d piezas por publicar y solo quedan %d cupos. Van a quedar %d fuera."
              % (pendientes, resto, pendientes - resto))
        return 1
    if fall:
        print("%d ranuras fallidas: cada reintento gasta un cupo de los %d que quedan." % (fall, resto))
    return 0


def main():
    ap = argparse.ArgumentParser(description="Le deja resuelto el trabajo a la tarea que publica.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    for nombre, fn, ayuda in (("listo", cmd_listo, "ranuras cuya hora ya llego"),
                              ("plan", cmd_plan, "tareas de un disparo del dia"),
                              ("cupo", cmd_cupo, "cuantas van contra el tope de 13/24 h")):
        p = sub.add_parser(nombre, help=ayuda)
        p.add_argument("--fecha")
        p.set_defaults(func=fn)
    f = sub.add_parser("ficha", help="los 4 pasos de una ranura, con la URL puesta")
    f.add_argument("slot", type=int)
    f.add_argument("--fecha")
    f.set_defaults(func=cmd_ficha)
    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
