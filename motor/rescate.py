#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rescate.py - una pieza terminada no se muere porque se le paso la hora.

EL DEFECTO QUE CIERRA (medido el 20/09/2026 sobre el dia 19/09)

    DIA 2026-09-19  4/10 publicadas  6 listas para salir  0 fallidas
    SE LES PASO LA VENTANA (6): #5, #6, #7, #8, #9, #10
    "NO las publiques (...) Son para que un humano mire."

Seis piezas renderizadas, medidas, aprobadas por control.py y ya subidas a Higgsfield con su
media_id se quedaron sin salir. No fallo el render ni el derecho ni la subida: fallo que la
ventana de 55 minutos de publicar.py es TERMINAL. Cuando se cierra, la pieza no tiene camino de
vuelta, y el camino que el mensaje nombra -"que un humano mire"- no existe: el sistema corre de
madrugada, sin nadie.

La ventana esta bien y no se toca. Su razon es real y esta escrita en publicar.py: mientras la
tarea no pueda anotar lo que publico, republicar a ciegas produce posts repetidos. Lo que estaba
mal es la OTRA MITAD: proteger en un sentido y no dejar salida en el otro. Es la tercera vez que
aparece la misma forma de defecto en este motor, y conviene nombrarla junto a las otras dos:

    control 4 (uniones)   aprobaba una pieza cuyos empalmes nadie midio   -> fallaba ABIERTA
    marca TOMANDO         sin vencimiento, enterraba una pieza sana       -> fallaba CERRADA
    ventana de 55 min     sin rescate, entierra la pieza terminada        -> fallaba CERRADA

LA SALIDA NO ES CONFIAR, ES MEDIR. "Puede que hayan salido y que nadie lo anotara" es una duda
sobre un hecho comprobable: la cuenta de TikTok es publica y dice que salio y que no. Asi que el
rescate no le cree al libro de cuentas ni a la buena voluntad: le cree al TESTIGO, que es el
listado real de la cuenta. Si el testigo no esta, esto no rescata nada (regla dura 2-ter de
RECETA-MOTOR-NUBE.md: un control sin su dato falla CERRADO).

    # 1. el testigo, en el sandbox (el contenedor de Claude no alcanza tiktok.com)
    pip install "yt-dlp[default,curl-cffi]"
    yt-dlp --impersonate chrome --flat-playlist --playlist-end 30 -j \
        https://www.tiktok.com/@abogadocristopherjesus > testigo.jsonl

    # 2. el rescate
    python3 motor/rescate.py rescatar --de 2026-09-19 --a 2026-09-20 --testigo testigo.jsonl

LO QUE EL TESTIGO NO PRUEBA, dicho aqui para que nadie lo descubra tarde: un post RESTRINGIDO
por TikTok no aparece en el listado publico aunque exista (paso con la 998f el 17/09). Por eso
el rescate exige ADEMAS que la ranura no tenga publish_id: si alguna corrida llego a publicarla
de verdad, el id quedo anotado. Las dos condiciones juntas -sin publish_id y sin post en la
cuenta- son lo mas cerca de la certeza que se puede llegar sin la API de TikTok.
"""

import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cadena as C  # noqa: E402

RESCATABLES = ("alojado", "programado")

# Una pieza del motor dura entre 22 y 34 s (regla dura 6 de RECETA-MOTOR-NUBE.md). El margen de
# 20 a 40 cubre el redondeo de TikTok y cualquier pieza vieja de antes de esa regla.
#
# POR QUE ESTO IMPORTA. La cuenta no publica solo lo que publica el motor: Cristopher sube cosas
# a mano. Medido el 20/09: el sabado 19/09 la cuenta tenia 5 posts y el libro anotaba 4, y el que
# sobraba duraba 102 segundos. Contar posts a secas habria dicho "hay una publicacion sin anotar,
# no rescato nada" y habria enterrado seis piezas por culpa de un video que no es del motor.
# La duracion es el unico discriminador que la cuenta publica regala y que no depende del libro.
DUR_MIN, DUR_MAX = 20, 40


def es_del_motor(post):
    """None cuando el post no trae duracion: en ese caso no se puede afirmar nada y cuenta."""
    d = post.get("duration")
    if d is None:
        return None
    return DUR_MIN <= d <= DUR_MAX


def leer_testigo(ruta):
    """Acepta el .jsonl de `yt-dlp -j` o un JSON con una lista de objetos."""
    if not os.path.exists(ruta):
        C.salir("no existe el testigo %s. Sin testigo no se rescata nada (ver cabecera)." % ruta)
    posts = []
    with open(ruta, encoding="utf-8") as f:
        crudo = f.read().strip()
    if not crudo:
        C.salir("el testigo %s esta vacio." % ruta)
    if crudo.lstrip().startswith("["):
        posts = json.loads(crudo)
    else:
        for linea in crudo.splitlines():
            linea = linea.strip()
            if not linea:
                continue
            try:
                posts.append(json.loads(linea))
            except json.JSONDecodeError:
                continue
    if not posts:
        C.salir("el testigo %s no trae ningun post legible." % ruta)
    fuera = [p for p in posts if not p.get("timestamp")]
    if fuera:
        C.salir("el testigo trae %d post(s) sin timestamp: no se puede saber de que dia son." % len(fuera))
    return posts


def media_ya_encolados(excepto):
    """Los media_id que ya ocupan una ranura en CUALQUIER otro dia del libro.

    ANTIDOBLE ENTRE DIAS. Una pieza rescatada existe dos veces: en su dia de origen (marcada
    fallida) y en el dia al que paso. Si el dia de origen no llega a commitearse -y en una tarea
    programada el commit es justo lo que falla-, la noche siguiente la ve otra vez 'alojada' y la
    rescata DE NUEVO, a otro dia. La misma pieza en dos ranuras es un post repetido, que es
    exactamente lo que todo esto trata de evitar.
    Contra eso no sirve confiar en el commit: sirve mirar el media_id, que es el que identifica
    al mp4 de verdad. Si ya esta encolado en otro dia, esta pieza no se vuelve a mover.
    """
    vistos = {}
    if not os.path.isdir(C.DIR_ESTADO):
        return vistos
    for nombre in sorted(os.listdir(C.DIR_ESTADO)):
        if not nombre.endswith(".json") or nombre[:-5] == excepto:
            continue
        try:
            with open(os.path.join(C.DIR_ESTADO, nombre), encoding="utf-8") as f:
                dia = json.load(f)
        except (OSError, ValueError):
            continue
        for p in dia.get("piezas", []):
            if p.get("media_id") and p.get("estado") != C.FALLIDO:
                vistos.setdefault(p["media_id"], "%s #%s" % (nombre[:-5], p.get("slot")))
    return vistos


def posts_del_dia(posts, fecha):
    """Los posts del testigo que caen dentro del dia `fecha` en hora de Chile."""
    ini = datetime.datetime.strptime(fecha, "%Y-%m-%d").replace(tzinfo=C.TZ_CHILE)
    fin = ini + datetime.timedelta(days=1)
    out = []
    for p in posts:
        t = datetime.datetime.fromtimestamp(p["timestamp"], datetime.timezone.utc).astimezone(C.TZ_CHILE)
        if ini <= t < fin:
            out.append((t, p))
    return sorted(out, key=lambda x: x[0])


def cmd_rescatar(args):
    origen = C.cargar(args.de)
    destino = C.cargar(args.a)
    posts = leer_testigo(args.testigo)
    reales = posts_del_dia(posts, args.de)

    anotadas = [p for p in origen["piezas"] if p["estado"] == "publicado"]
    encolados = media_ya_encolados(excepto=args.de)
    candidatas, ya_movidas = [], []
    for p in origen["piezas"]:
        if (p["estado"] not in RESCATABLES or p.get("publish_id")
                or not p.get("media_id") or not C.vencida(p, args.de, 0)):
            continue
        if p["media_id"] in encolados:
            ya_movidas.append((p, encolados[p["media_id"]]))
        else:
            candidatas.append(p)

    nuestros, ajenos = [], []
    for t, p in reales:
        (ajenos if es_del_motor(p) is False else nuestros).append((t, p))

    print("TESTIGO: %d post(s) reales en la cuenta el %s" % (len(reales), args.de))
    for t, p in reales:
        d = p.get("duration")
        marca = "AJENO (no es del motor)" if es_del_motor(p) is False else ""
        print("   %s  %s  %ss  %s" % (t.strftime("%H:%M"), p.get("id", "?"), d, marca))
    if ajenos:
        print("   -> %d descartado(s) por duracion fuera de %d-%d s: no los publico el motor."
              % (len(ajenos), DUR_MIN, DUR_MAX))
    print("LIBRO:   %d ranura(s) anotadas como publicadas ese dia" % len(anotadas))
    print("CANDIDATAS a rescate (alojadas, sin publish_id, vencidas): %d -> %s"
          % (len(candidatas), ", ".join("#%d" % p["slot"] for p in candidatas) or "ninguna"))
    if ya_movidas:
        print("YA ENCOLADAS en otro dia (antidoble por media_id), no se tocan: %s"
              % ", ".join("#%d -> %s" % (p["slot"], donde) for p, donde in ya_movidas))
    print()

    # LA PUERTA. Falla CERRADA en los tres casos en que no se puede afirmar que no salieron.
    if not candidatas:
        print("no hay nada que rescatar del %s." % args.de)
        return 1
    if len(nuestros) > len(anotadas):
        print("ALTO: la cuenta tiene %d post(s) del motor el %s y el libro solo anota %d."
              % (len(nuestros), args.de, len(anotadas)))
        print("Hay al menos %d publicacion que nadie anoto, y podria ser una de las candidatas."
              % (len(nuestros) - len(anotadas)))
        print("NO se rescata nada. Primero hay que emparejar el libro con la cuenta a mano.")
        return 2

    libres = [p for p in destino["piezas"] if p["estado"] == "vacio"]
    if not libres:
        print("ALTO: el dia %s no tiene ninguna ranura vacia donde poner las rescatadas." % args.a)
        return 2

    cupo = min(len(candidatas), len(libres), args.max or len(candidatas))
    print("se rescatan %d pieza(s) hacia %s (ranuras vacias disponibles: %d)"
          % (cupo, args.a, len(libres)))
    print()

    COPIAR = ("tema", "fuente", "titular", "gancho", "tramos", "norma", "articulo", "frase",
              "derecho", "url", "media_id", "control", "metraje", "clips", "texto")
    movidas = []
    for pieza, hueco in zip(candidatas[:cupo], libres[:cupo]):
        for k in COPIAR:
            if pieza.get(k) is not None:
                hueco[k] = pieza[k]
        hueco["estado"] = "alojado"
        hueco["intentos"] = 0
        hueco["rescatada_de"] = {"fecha": args.de, "slot": pieza["slot"]}
        C.anotar(hueco, "rescatada de %s ranura #%d: estaba alojada con media_id y se le paso la "
                        "ventana; el testigo de la cuenta prueba que no salio (%d post reales, "
                        "%d anotados)" % (args.de, pieza["slot"], len(reales), len(anotadas)))

        pieza["estado"] = C.FALLIDO
        pieza["motivo"] = "rescatada a %s ranura #%d" % (args.a, hueco["slot"])
        C.anotar(pieza, pieza["motivo"])

        movidas.append((pieza["slot"], hueco["slot"], hueco["hora_chile"], hueco.get("tema", "")))
        print("  %s #%d  ->  %s #%d a las %s  %s"
              % (args.de, pieza["slot"], args.a, hueco["slot"], hueco["hora_chile"],
                 (hueco.get("tema") or "")[:50]))

    if args.seco:
        print()
        print("--seco: no se escribio nada.")
        return 0

    C.guardar(origen)
    C.guardar(destino)
    print()
    print("escrito. Acuerdate del commit, o esto muere con el contenedor:")
    print("  git add estado/%s.json estado/%s.json && \\" % (args.de, args.a))
    print("  git commit -m 'rescate: %d pieza(s) del %s pasan al %s' && git push"
          % (len(movidas), args.de, args.a))
    return 0


def cmd_testigo(args):
    print("Corre esto en el sandbox de Higgsfield (el contenedor de Claude no alcanza tiktok.com):")
    print()
    print('  pip install -q "yt-dlp[default,curl-cffi]" && \\')
    print("  yt-dlp --impersonate chrome --flat-playlist --playlist-end %d -j \\" % args.n)
    print("      https://www.tiktok.com/@%s > testigo.jsonl" % args.cuenta)
    print()
    print("Y despues:  python3 motor/rescate.py rescatar --de <fecha> --a <fecha> --testigo testigo.jsonl")
    return 0


def main():
    ap = argparse.ArgumentParser(
        description="Devuelve a la cola las piezas terminadas a las que se les paso la ventana.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("rescatar", help="mueve piezas alojadas de un dia pasado a ranuras vacias de otro")
    r.add_argument("--de", required=True, help="fecha de origen, YYYY-MM-DD")
    r.add_argument("--a", required=True, help="fecha de destino, YYYY-MM-DD")
    r.add_argument("--testigo", required=True, help="jsonl de yt-dlp con los posts reales de la cuenta")
    r.add_argument("--max", type=int, help="rescatar como mucho N piezas (para dejar reserva)")
    r.add_argument("--seco", action="store_true", help="muestra lo que haria y no escribe")
    r.set_defaults(func=cmd_rescatar)

    t = sub.add_parser("testigo", help="imprime como obtener el testigo")
    t.add_argument("--cuenta", default="abogadocristopherjesus")
    t.add_argument("-n", type=int, default=30)
    t.set_defaults(func=cmd_testigo)

    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
