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

# EL TOPE DE 150 CARACTERES, medido el 19/09/2026. `tiktok_prepare_publish` responde
#     title: Too big: expected string to have <=150 characters
# y rechaza la llamada entera. La primera version de este texto salia en 220 y habria reventado
# a la hora de publicar, con la tarea ya corriendo y el reloj encima. Por eso el texto se arma
# CONTANDO, y por eso `ficha` imprime el largo: lo que no se mide se publica roto.
MAX_TITULO = 150

# De donde se sirve una pieza ya subida a Higgsfield. `tiktok_prepare_publish` NO acepta un
# media_id: pide `video_url`, y la url es esta base + el media_id. Medido el 19/09 contra la
# herramienta, que contesto primero "video_url is required" y despues genero el preview.
CDN = "https://d2ol7oe51mr4n9.cloudfront.net/user_3IkWukwrqRk5HTPle6Rx8WbYgS3/%s.mp4"

# Fijas a proposito: la marca se reconoce por repeticion, y una sesion que improvisa el texto
# cada vez es una sesion que tarda y que un dia escribe algo que no corresponde firmar.
ETIQUETAS = "#chile #derecho #noticias"


VACIAS = {"del", "la", "el", "los", "las", "de", "en", "y", "por", "con", "que",
          "un", "una", "al", "su", "sus", "para", "es", "no"}


def _plano(t):
    """Minusculas y sin tildes, solo para COMPARAR. Lo que se publica conserva sus tildes."""
    import unicodedata
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if unicodedata.category(c) != "Mn")


def _aporta(gancho, tema):
    """¿El gancho agrega algo, o solo repite el tema?

    Medido sobre las diez piezas del 19/09: el gancho casi siempre repite la primera palabra del
    tema, y el texto salia "MICROTRAFICO: Microtrafico: que separa..." o "245 PARTES: 245
    infracciones...". Eso se lee como un error, que es lo ultimo que puede parecer el post de un
    abogado. El gancho tiene su lugar -en pantalla, dentro del video-; aqui solo entra si suma.
    """
    if not gancho or not tema:
        return bool(gancho)
    palabras = [w for w in _plano(gancho).replace(":", " ").split()
                if len(w) >= 3 and w not in VACIAS]
    cuerpo = _plano(tema)
    return not any(w in cuerpo for w in palabras)


def _recortar(texto, tope):
    """Recorta en el ultimo espacio que quepa. Cortar a media palabra se ve a la legua."""
    if len(texto) <= tope:
        return texto
    corte = texto[:tope].rstrip()
    if " " in corte:
        corte = corte[:corte.rindex(" ")].rstrip()
    return corte.rstrip(".,;:") + "..."


def texto_tiktok(p):
    """El texto del post, armado SOLO con lo que ya esta verificado en el libro de cuentas.

    POR QUE AQUI Y NO EN LA CABEZA DE LA SESION: hasta el 19/09 la ficha imprimia los pasos pero
    no el texto, asi que cada tarea horaria lo inventaba. Eso es un problema de tres caras: la
    tarea se alarga (y las largas no cierran), la voz del estudio cambia de pieza en pieza, y
    -la grave- un texto improvisado puede afirmar de derecho algo que la pieza no verifico.
    Aqui no se inventa nada: el gancho, el tema y el articulo salen tal cual del dia.

    El nombre del estudio NO va en el texto: no cabe en 150 caracteres junto al titular, y ya
    esta en pantalla dentro del video. Entre repetir la firma y que se entienda la noticia,
    gana la noticia: el primer renglon es lo unico que se lee antes de deslizar.
    """
    tema = (p.get("tema") or "").strip()
    gancho = (p.get("gancho") or "").strip()
    art = (p.get("articulo") or "").strip()

    # Sin nombre de ley a menos que el dia lo traiga: el 19/09 una ley "recordada" de memoria
    # resulto ser otra norma. Se cita lo que esta verificado y nada mas.
    ley = (p.get("ley") or "").strip()
    cita = ("Art. %s%s." % (art, " %s" % ley if ley else "")) if art else ""

    cola = "\n".join(x for x in (cita, ETIQUETAS) if x)
    sitio = MAX_TITULO - len(cola) - (1 if cola else 0)

    if tema and gancho and _aporta(gancho, tema):
        titular = "%s: %s" % (gancho, tema)
    else:
        titular = tema or gancho or "Noticia del dia"
    titular = _recortar(titular, sitio)

    texto = "\n".join(x for x in (titular, cola) if x)
    if len(texto) > MAX_TITULO:                       # cinturon: nunca sale algo que TikTok rechace
        texto = texto[:MAX_TITULO].rstrip()
    return texto


# UNA SOLA OPORTUNIDAD POR RANURA, Y ES UNA DEFENSA, NO UNA COMODIDAD (19/09/2026)
#
# Medido hoy: la tarea programada NO puede escribir en el repositorio. Se le pidio que empujara
# un archivo de prueba y no aparecio nunca. Eso explica por que ninguna de las tres publicaciones
# del dia quedo anotada sola.
#
# Y tiene una consecuencia que no es obvia: si la publicacion ocurre pero el libro de cuentas no
# se entera, la ranura sigue figurando como 'alojado' y VENCIDA. Con la regla vieja -"vencida es
# cualquier cosa cuya hora ya paso"- la corrida siguiente la ve pendiente y la publica OTRA VEZ.
# Y la siguiente. Una pieza publicada y no anotada se convertia en un post repetido cada hora.
#
# Mientras la tarea no pueda anotar, la unica defensa que no depende de anotar es el RELOJ: cada
# ranura se ofrece solo dentro de su propia ventana. Si a las 14:07 le tocaba a la ranura de las
# 14:00, a las 15:07 ya no le toca a nadie. Una oportunidad por ranura.
#
# El precio, dicho claro: una pieza que falle de verdad se pierde por hoy en vez de reintentarse.
# Se acepta a proposito. Un hueco se recupera; un post duplicado en la cuenta de un abogado, no.
VENTANA_MIN = 55


def listas(dia, solo_vencidas=True, ventana=VENTANA_MIN):
    out = []
    for p in dia["piezas"]:
        if p["estado"] not in ("alojado", "programado"):
            continue
        if solo_vencidas:
            if not C.vencida(p, dia["fecha"], 0):
                continue
            if ventana is not None and C.vencida(p, dia["fecha"], ventana):
                continue      # se le paso su turno: no se reintenta a ciegas
        out.append(p)
    return out


def pasadas(dia, ventana=VENTANA_MIN):
    """Ranuras alojadas cuya ventana ya se cerro. Puede que salieran y nadie lo anotara."""
    return [p for p in dia["piezas"]
            if p["estado"] in ("alojado", "programado") and C.vencida(p, dia["fecha"], ventana)]


def cmd_listo(args):
    fecha = args.fecha or C.hoy()
    dia = C.cargar(fecha)
    ahora = listas(dia)
    viejas_ids = {q["slot"] for q in pasadas(dia)}
    luego = [p for p in listas(dia, solo_vencidas=False)
             if p not in ahora and p["slot"] not in viejas_ids]
    if ahora:
        print("PARA PUBLICAR AHORA (%d):" % len(ahora))
        for p in ahora:
            print("  #%d  %s  %s" % (p["slot"], p["hora_chile"], (p.get("tema") or "")[:55]))
    else:
        print("nada vencido para publicar en este momento.")
    if luego:
        print("listas y esperando su hora (%d): %s"
              % (len(luego), ", ".join("#%d a las %s" % (p["slot"], p["hora_chile"]) for p in luego)))
    viejas = pasadas(dia)
    if viejas:
        print()
        print("SE LES PASO LA VENTANA (%d): %s"
              % (len(viejas), ", ".join("#%d (%s)" % (p["slot"], p["hora_chile"]) for p in viejas)))
        print("NO las publiques: puede que hayan salido y que nadie alcanzara a anotarlo, y")
        print("republicar cuesta un cupo y deja un post repetido. Son para que un humano mire.")
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
    print("pre-subida: %s" % ("SI, media_id=%s" % p["media_id"] if p.get("media_id")
                              else "NO - esta tarea va a ser larga (ver paso 1)"))
    print()
    txt = texto_tiktok(p)
    print("EL TEXTO DEL POST (copiar TAL CUAL, no reescribir) - %d de %d caracteres:"
          % (len(txt), MAX_TITULO))
    print("---8<---")
    print(txt)
    print("--->8---")
    print()
    print("LOS PASOS (motor/PUBLICAR.md, via B):")
    if p.get("media_id"):
        print("  1. NADA QUE SUBIR. media_id=%s (pre-subido)." % p["media_id"])
    else:
        print("  1. FALTA EL media_id. La pieza no esta pre-subida, asi que hay que subirla:")
        print("       media_upload (nombre %s.mp4, video/mp4) -> upload_url"
              % (p.get("pieza_id") or p["slot"]))
        print("       bajar los bytes:  curl -sL '%s' -o /tmp/p.mp4" % p.get("url"))
        print("       PUT de /tmp/p.mp4 a esa upload_url, y despues media_confirm.")
        print("       anotalo:  python3 motor/cadena.py anotar %d --campo media_id=<id>" % p["slot"])
        print("     OJO: media_import_url con la url de la Release NO funciona. GitHub la sirve")
        print("     como application/octet-stream y Higgsfield la rechaza. Medido el 19/09.")
    print("  2. tiktok_prepare_publish -> publish_session_id. Los parametros exactos, medidos:")
    print("       connector_id = %s" % CONNECTOR)
    if p.get("media_id"):
        print("       video_url    = %s" % (CDN % p["media_id"]))
    else:
        print("       video_url    = %s   (la del CDN, con el media_id del paso 1)" % (CDN % "<media_id>"))
    print("       media_type   = VIDEO          mode = DIRECT_POST")
    print("       title        = el texto de arriba, tal cual")
    print("       privacy_level=PUBLIC_TO_EVERYONE  is_aigc=true")
    print("       disable_comment/duet/stitch = false")
    print("     OJO: pide 'video_url', NO 'media_id', y 'mode', NO 'post_mode'. El titulo no")
    print("     puede pasar de %d caracteres o rechaza la llamada entera." % MAX_TITULO)
    print("  3. tiktok_publish  con ESE publish_session_id.")
    print("     Van en true TODAS las de required_confirmations que devuelva el paso 2:")
    print("     user_confirmed, preview_confirmed, music_usage_confirmed,")
    print("     processing_notice_acknowledged, privacy_level_selected_by_user,")
    print("     interaction_settings_selected_by_user,")
    print("     commercial_content_disclosure_selected_by_user.")
    print("     Sin musica anadida: no llames a tiktok_music_trending.")
    print("     Si te NIEGAN el permiso, no insistas: eso no es un error de red. Anota el")
    print("     motivo literal con 'fallar' y sigue con la siguiente ranura.")
    print("  4. tiktok_publish_status hasta PUBLISH_COMPLETE. Solo eso cuenta como publicado.")
    print("     La sesion del paso 2 caduca en ~2 h: si se vence, repite el paso 2.")
    print()
    print("AL TERMINAR, una sola linea:")
    print("  python3 motor/cadena.py marcar %d publicado --campo publish_id=<el id>" % p["slot"])
    print("SI FALLA:")
    print("  python3 motor/cadena.py fallar %d --motivo \"<lo que dijo TikTok>\"" % p["slot"])
    print()
    print("Y COMMITEA, con git y NADA MAS que git (copiar tal cual):")
    print("  git add estado/%s.json" % fecha)
    print("  git -c user.name=publicador -c user.email=publicador@local \\")
    print("      commit -m \"estado %s: ranura %d publicada\"" % (fecha, p["slot"]))
    print("  git push origin main")
    print()
    print("  ⛔ NO uses las herramientas de GitHub (create_or_update_file, push_files,")
    print("     search_repositories ni ninguna otra): en una tarea programada piden permiso,")
    print("     y no hay nadie despierto para darlo. La tarea se queda colgada ahi para")
    print("     siempre. Paso el 19/09 dos veces: a las 10:08 se colgo en el primer paso y")
    print("     no publico nada, y a las 12:08 publico bien pero se colgo al commitear, con")
    print("     lo cual la publicacion quedo sin anotar. git por Bash no pide permiso.")
    print("  Si 'git push' falla, DILO en el reporte y termina. No busques otra herramienta:")
    print("     la que busques va a pedir permiso y vas a dejar la tarea colgada.")
    print("Sin el commit el estado muere con el contenedor, y peor: como el antidoble de")
    print("cadena.py lee el libro, la corrida siguiente republicaria esta misma pieza.")
    return 0


def cmd_presubir(args):
    """Las piezas alojadas que todavia no tienen su media_id de Higgsfield.

    POR QUE ES UN COMANDO Y NO UN PARRAFO EN UN PROMPT: la tarea que pre-sube no tiene que
    AVERIGUAR cuales faltan. Si tiene que leer el estado y decidir, ya es una tarea larga, y las
    largas de esta cuenta no cierran. Aqui sale la lista y los comandos exactos, en orden.
    """
    fecha = args.fecha or C.hoy()
    dia = C.cargar(fecha)
    faltan = [p for p in dia["piezas"]
              if p["estado"] in ("alojado", "programado") and not p.get("media_id")]

    if not faltan:
        listas = sum(1 for p in dia["piezas"] if p.get("media_id"))
        print("NADA QUE PRE-SUBIR en %s: las %d piezas alojadas ya tienen su media_id." %
              (fecha, listas))
        print("Ese es el final normal. Responde una linea y termina.")
        return 0

    print("POR PRE-SUBIR EN %s: %d piezas." % (fecha, len(faltan)))
    print("Una por una, y COMMITEA despues de cada una. Si la sesion se corta, lo anotado queda.")
    print()
    for p in faltan:
        pid = p.get("pieza_id") or p["slot"]
        print("--- ranura #%d (%s) ---" % (p["slot"], p["hora_chile"]))
        print("  1. media_upload  filename=sb-%s.mp4  content_type=video/mp4" % pid)
        print("  2. curl -sL '%s' -o /tmp/p%d.mp4" % (p.get("url"), p["slot"]))
        print("  3. PUT /tmp/p%d.mp4 a la upload_url, con cabecera Content-Type: video/mp4." % p["slot"])
        print("     La firma incluye content-type: sin esa cabecera el PUT falla.")
        print("     Espera http=200 y que los bytes enviados cuadren con el archivo.")
        print("  4. media_confirm  media_id=<el que devolvio media_upload>  type=video")
        print("  5. python3 motor/cadena.py anotar %d --campo media_id=<ese id>" % p["slot"])
        print()
    print("NO publiques nada aqui: pre-subir no es publicar. De eso se encarga la tarea horaria.")
    return 1


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
                              ("presubir", cmd_presubir, "piezas alojadas sin media_id"),
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
