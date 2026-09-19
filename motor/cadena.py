#!/usr/bin/env python3
"""cadena.py v1 (19/09/2026) - EL LIBRO DE CUENTAS DEL DIA.

POR QUE EXISTE
--------------
El 19/09/2026, con la fabrica entera escrita y documentada, el estudio seguia publicando 1 o 2
piezas los dias que debia publicar 6. La lectura de tareas de esa manana explica por que:

    SB 06:00 - Produccion del dia .......... ultima corrida: ABANDONED
    M8 10:00 - Verificacion legal .......... ultima corrida: ABANDONED

El defecto no estaba en `motor.py`, ni en `produce.py`, ni en `control.py`: los tres hacen bien
lo suyo. Estaba en que NADA en el sistema sabia cuantas piezas debia tener el dia ni en que
estado iba cada una. Cada rutina lo deducia de nuevo preguntandole a Metricool, a Higgsfield y
al repo, y cuando una tarea larga moria a la mitad -y morian- el trabajo hecho se perdia sin
dejar rastro: `resultado.json` y `urls/<id>.txt` viven en el sandbox y mueren con el.

Asi, el numero de videos del dia no era una decision: era el resultado de si una sesion larga
alcanzo a terminar o no. De ahi las tres propiedades que este archivo tiene que dar:

  1. ESTADO FUERA DE LA SESION. El dia vive en `estado/<fecha>.json`, versionado en git. Una
     tarea que muere deja escrito lo que alcanzo a hacer, y la siguiente sigue desde ahi en vez
     de empezar de cero.
  2. TAREAS CORTAS DE VERDAD. `tareas/INDEX.md` ya dedujo la regla -"tareas cortas, un solo
     trabajo, reporte de 3 lineas"- pero una tarea corta que no puede consultar ni dejar estado
     tiene que releer el mundo entero para saber que hacer, y deja de ser corta. `resumen` da
     el reporte de 3 lineas y `siguiente` dice el UNICO trabajo que toca ahora.
  3. ANTIDOBLE EN CODIGO. La regla vivia en prosa en `/areas/tiktok-programacion.md`: las
     revisiones "no vuelven a publicar" una pieza ya asignada. Aqui marcar `publicado` una pieza
     ya publicada sale con codigo 2 y no escribe nada. Con cuota de 13 publicaciones por 24 h
     (`motor/PUBLICAR.md`), una republicacion por descuido cuesta una pieza real del dia.

LA MISMA DOCTRINA QUE control.py, UNA CAPA MAS ARRIBA
-----------------------------------------------------
`control.py` v3 cerro el agujero de la puerta que fallaba ABIERTA: sin guion, los controles de
contenido se apagaban solos y la pieza pasaba igual. Aqui vale lo mismo para el ESTADO: un paso
sin sus datos no se puede marcar. No se puede marcar `renderizado` sin el informe de control con
`pasa: True`; no se puede marcar `alojado` sin `media_id`; no se puede marcar `publicado` una
pieza que nunca paso por la puerta. Un registro que se deja escribir con cualquier cosa no es un
registro: es una nota adhesiva.

LA CADENA
---------
    vacio -> tema -> derecho -> guion -> renderizado -> alojado -> [programado] -> publicado

`programado` es el unico paso opcional: la via B de `motor/PUBLICAR.md` (Higgsfield) publica al
momento y no pasa por el. La via A (Metricool, hoy topada) si lo usa. Solo se avanza hacia
adelante; para volver atras esta `fallar` + `reintentar`, que dejan la vuelta anotada.

Cada paso exige sus datos:
    tema         tema, fuente
    derecho      norma (idNorma de LeyChile), articulo, frase (la frase buscada en el texto)
    guion        gancho, tramos (los 5 de la regla dura 1)
    renderizado  control (el dict que devuelve control.controlar(), con pasa=True)
    alojado      media_id, url
    programado   trigger_id, hora_utc
    publicado    publish_id

USO
---
    python3 motor/cadena.py abrir --meta 10        # abre el dia con 10 ranuras
    python3 motor/cadena.py resumen                # el reporte de 3 lineas de toda rutina
    python3 motor/cadena.py siguiente              # el unico trabajo que toca ahora
    python3 motor/cadena.py marcar 4 alojado --campo media_id=abc --campo url=https://...
    python3 motor/cadena.py fallar 4 --motivo "mixkit 403 en el clip de gancho"
    python3 motor/cadena.py reintentar 4
    python3 motor/cadena.py reserva                # piezas alojadas sin publicar (regla: >= 3)
    python3 motor/cadena.py auditar                # discrepancias; codigo 1 si hay alguna

Sin tildes ni n-tilde en la salida a proposito: este archivo corre dentro de sandboxes y su
salida se pega en prompts. Las tildes obligatorias de la regla dura 2 son las del texto que ve
el publico y las del texto que lee la voz, no las de un reporte de operacion.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta, timezone

# Chile esta en UTC-3 desde el 06/09/2026 (cambio de hora anotado en cerebro/MASTER_STATE.md).
# REVISAR en abril de 2027, cuando vuelva a UTC-4: mezclar los dos corre las piezas una hora.
TZ_CHILE = timezone(timedelta(hours=-3))

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_ESTADO = os.path.join(RAIZ, "estado")

CADENA = ["vacio", "tema", "derecho", "guion", "renderizado", "alojado", "programado", "publicado"]
OPCIONALES = {"programado"}
FALLIDO = "fallido"

EXIGE = {
    "tema": ("tema", "fuente"),
    "derecho": ("norma", "articulo", "frase"),
    "guion": ("gancho", "tramos"),
    "renderizado": ("control",),
    "alojado": ("media_id", "url"),
    "programado": ("trigger_id", "hora_utc"),
    "publicado": ("publish_id",),
}

# Diez ranuras repartidas entre las 07:00 y las 22:30 de Chile. La rev. 12 del archivo cerebro
# cerro que la hora no es la variable que decide (H-12: manda el TEMA), asi que se reparten
# parejo y no se optimiza una franja que los datos no sostienen.
HORARIOS = ["07:00", "09:00", "11:00", "12:30", "14:00",
            "15:30", "17:00", "19:00", "21:00", "22:30"]

RESERVA_MINIMA = 3          # tareas/INDEX.md, regla 2 del sistema
CUOTA_TIKTOK_24H = 13       # motor/PUBLICAR.md, via B


# --------------------------------------------------------------------------- utilidades

def ahora_chile():
    return datetime.now(TZ_CHILE)


def hoy():
    return ahora_chile().strftime("%Y-%m-%d")


def ruta(fecha):
    return os.path.join(DIR_ESTADO, "%s.json" % fecha)


def cargar(fecha, obligatorio=True):
    r = ruta(fecha)
    if not os.path.exists(r):
        if obligatorio:
            salir("no hay dia abierto para %s. Abrelo con: cadena.py abrir --fecha %s" % (fecha, fecha))
        return None
    with open(r, encoding="utf-8") as f:
        return json.load(f)


def guardar(dia):
    os.makedirs(DIR_ESTADO, exist_ok=True)
    dia["actualizado"] = ahora_chile().isoformat(timespec="seconds")
    with open(ruta(dia["fecha"]), "w", encoding="utf-8") as f:
        json.dump(dia, f, ensure_ascii=False, indent=2)
        f.write("\n")


def salir(mensaje, codigo=2):
    print("ERROR: %s" % mensaje)
    sys.exit(codigo)


def buscar(dia, slot):
    for p in dia["piezas"]:
        if p["slot"] == slot:
            return p
    salir("el dia %s no tiene ranura %s (tiene 1..%d)" % (dia["fecha"], slot, len(dia["piezas"])))


def indice(estado):
    return CADENA.index(estado)


def anotar(pieza, que):
    pieza.setdefault("historia", []).append({
        "cuando": ahora_chile().isoformat(timespec="seconds"),
        "que": que,
    })


def utc_de(fecha, hhmm):
    h, m = hhmm.split(":")
    local = datetime.strptime(fecha, "%Y-%m-%d").replace(hour=int(h), minute=int(m), tzinfo=TZ_CHILE)
    return local.astimezone(timezone.utc)


def vencida(pieza, fecha, margen_min=30):
    """True si la hora de publicacion de la ranura ya paso hace mas de `margen_min`."""
    return ahora_chile() > utc_de(fecha, pieza["hora_chile"]).astimezone(TZ_CHILE) + timedelta(minutes=margen_min)


# --------------------------------------------------------------------------- comandos

def cmd_abrir(args):
    fecha = args.fecha or hoy()
    if os.path.exists(ruta(fecha)) and not args.rehacer:
        dia = cargar(fecha)
        print("el dia %s ya estaba abierto con %d ranuras; no se toca." % (fecha, len(dia["piezas"])))
        print("usa --rehacer solo si quieres perder lo anotado.")
        return 0
    if args.meta > len(HORARIOS):
        salir("la meta es %d pero solo hay %d horarios definidos en HORARIOS" % (args.meta, len(HORARIOS)))
    dia = {
        "fecha": fecha,
        "meta": args.meta,
        "formato": args.formato,
        "creado": ahora_chile().isoformat(timespec="seconds"),
        "piezas": [],
    }
    for i in range(args.meta):
        dia["piezas"].append({
            "slot": i + 1,
            "hora_chile": HORARIOS[i],
            "hora_utc": utc_de(fecha, HORARIOS[i]).strftime("%Y-%m-%dT%H:%M:00Z"),
            "estado": "vacio",
            "intentos": 0,
            "historia": [],
        })
    guardar(dia)
    print("dia %s abierto: %d ranuras (%s) formato=%s" %
          (fecha, args.meta, ", ".join(HORARIOS[:args.meta]), args.formato))
    if args.meta + RESERVA_MINIMA > CUOTA_TIKTOK_24H:
        print("AVISO: meta %d + reserva %d supera la cuota de %d publicaciones/24 h de la via B "
              "(motor/PUBLICAR.md). Quedan %d reintentos para todo el dia."
              % (args.meta, RESERVA_MINIMA, CUOTA_TIKTOK_24H, CUOTA_TIKTOK_24H - args.meta))
    return 0


def cmd_resumen(args):
    fecha = args.fecha or hoy()
    dia = cargar(fecha)
    cuenta = {}
    for p in dia["piezas"]:
        cuenta[p["estado"]] = cuenta.get(p["estado"], 0) + 1
    publicadas = cuenta.get("publicado", 0)
    listas = cuenta.get("alojado", 0) + cuenta.get("programado", 0)
    fallidas = cuenta.get(FALLIDO, 0)

    print("DIA %s  %d/%d publicadas  %d listas para salir  %d fallidas"
          % (fecha, publicadas, dia["meta"], listas, fallidas))
    print("estados: " + " ".join("%s=%d" % (e, cuenta[e]) for e in CADENA + [FALLIDO] if cuenta.get(e)))
    atrasadas = [p for p in dia["piezas"]
                 if p["estado"] not in ("publicado", FALLIDO) and vencida(p, fecha)]
    if atrasadas:
        print("ATRASADAS (paso su hora): " +
              ", ".join("#%d %s(%s)" % (p["slot"], p["hora_chile"], p["estado"]) for p in atrasadas))
    else:
        print("sin ranuras atrasadas.")
    return 0


def cmd_siguiente(args):
    fecha = args.fecha or hoy()
    dia = cargar(fecha)
    # Prioridad 1: lo que ya esta listo y vencido -> publicar es siempre lo mas urgente.
    # (tareas/INDEX.md regla 2: publicar nunca depende de producir.)
    pendientes = [p for p in dia["piezas"] if p["estado"] not in ("publicado", FALLIDO)]
    if not pendientes:
        print("nada que hacer: el dia %s esta cerrado." % fecha)
        return 0

    def prioridad(p):
        listo = indice(p["estado"]) >= indice("alojado")
        return (0 if (listo and vencida(p, fecha, 0)) else 1,
                0 if listo else 1,
                p["slot"])

    for p in sorted(pendientes, key=prioridad)[:args.n]:
        sig = siguiente_estado(p["estado"])
        print("RANURA #%d (%s Chile / %s) esta en '%s' -> toca: %s"
              % (p["slot"], p["hora_chile"], p["hora_utc"], p["estado"], sig))
        print("  exige: %s" % ", ".join(EXIGE.get(sig, ("-",))))
        if p.get("tema"):
            print("  tema: %s" % p["tema"])
        if p.get("url"):
            print("  url: %s" % p["url"])
        print("  al terminar: python3 motor/cadena.py marcar %d %s --campo ..." % (p["slot"], sig))
    return 0


def siguiente_estado(estado):
    if estado == FALLIDO:
        return "reintentar"
    i = indice(estado) + 1
    while i < len(CADENA) and CADENA[i] in OPCIONALES:
        i += 1                      # programado se salta: la via B publica al momento
    return CADENA[i] if i < len(CADENA) else "publicado"


def cmd_marcar(args):
    fecha = args.fecha or hoy()
    dia = cargar(fecha)
    p = buscar(dia, args.slot)
    nuevo = args.estado

    if nuevo not in CADENA:
        salir("estado desconocido '%s'. Son: %s" % (nuevo, ", ".join(CADENA)))

    # ANTIDOBLE: una pieza publicada no se vuelve a publicar. Cuesta una pieza real del dia.
    if p["estado"] == "publicado":
        salir("la ranura #%d YA esta publicada (publish_id=%s, %s). No se vuelve a tocar."
              % (p["slot"], p.get("publish_id", "?"), p.get("publicado_en", "?")))

    if p["estado"] == FALLIDO:
        salir("la ranura #%d esta fallida (%s). Usa 'reintentar' antes de marcar."
              % (p["slot"], p.get("motivo", "sin motivo")))

    if indice(nuevo) <= indice(p["estado"]):
        salir("la ranura #%d ya esta en '%s'; '%s' es hacia atras. Solo se avanza."
              % (p["slot"], p["estado"], nuevo))

    saltados = [e for e in CADENA[indice(p["estado"]) + 1:indice(nuevo)] if e not in OPCIONALES]
    if saltados:
        salir("no se puede saltar de '%s' a '%s': falta %s."
              % (p["estado"], nuevo, " y ".join(saltados)))

    campos = dict(kv.split("=", 1) for kv in args.campo) if args.campo else {}
    if args.json:
        campos.update(json.loads(args.json))

    faltan = [c for c in EXIGE.get(nuevo, ()) if c not in campos and c not in p]
    if faltan:
        salir("'%s' exige %s y falta %s. FALLA CERRADA: sin sus datos el paso no se anota."
              % (nuevo, ", ".join(EXIGE[nuevo]), ", ".join(faltan)))

    # LA PUERTA, un piso mas arriba: no se anota como renderizada una pieza que control.py reprobo.
    if nuevo == "renderizado":
        control = campos.get("control", p.get("control"))
        if isinstance(control, str):
            try:
                control = json.loads(control)
            except ValueError:
                salir("el campo 'control' tiene que ser el JSON que devuelve control.controlar()")
        if not isinstance(control, dict) or control.get("pasa") is not True:
            salir("control.pasa no es True. La pieza NO paso la puerta (motor/control.py): no se "
                  "anota como renderizada. Fallas: %s"
                  % (control.get("falla") if isinstance(control, dict) else "informe ilegible"))
        campos["control"] = control

    if nuevo == "publicado":
        if indice(p["estado"]) < indice("alojado"):
            salir("la ranura #%d nunca se alojo: no puede estar publicada." % p["slot"])
        campos["publicado_en"] = ahora_chile().isoformat(timespec="seconds")

    anterior = p["estado"]
    p.update(campos)
    p["estado"] = nuevo
    anotar(p, "%s -> %s" % (anterior, nuevo))
    guardar(dia)
    print("ranura #%d: %s -> %s" % (p["slot"], anterior, nuevo))
    if nuevo == "publicado":
        vivas = sum(1 for q in dia["piezas"] if q["estado"] == "publicado")
        print("van %d/%d publicadas hoy (cuota via B: %d/24 h)" % (vivas, dia["meta"], CUOTA_TIKTOK_24H))
    return 0


def cmd_fallar(args):
    fecha = args.fecha or hoy()
    dia = cargar(fecha)
    p = buscar(dia, args.slot)
    if p["estado"] == "publicado":
        salir("la ranura #%d ya esta publicada; no se marca fallida." % p["slot"])
    p["estado_previo"] = p["estado"]
    p["estado"] = FALLIDO
    p["motivo"] = args.motivo
    p["intentos"] = p.get("intentos", 0) + 1
    anotar(p, "%s -> fallido: %s" % (p["estado_previo"], args.motivo))
    guardar(dia)
    print("ranura #%d fallida en '%s' (intento %d): %s"
          % (p["slot"], p["estado_previo"], p["intentos"], args.motivo))
    return 0


def cmd_reintentar(args):
    fecha = args.fecha or hoy()
    dia = cargar(fecha)
    p = buscar(dia, args.slot)
    if p["estado"] != FALLIDO:
        salir("la ranura #%d no esta fallida (esta en '%s')." % (p["slot"], p["estado"]))
    vuelve = p.pop("estado_previo", "vacio")
    p["estado"] = vuelve
    motivo = p.pop("motivo", "")
    anotar(p, "reintento desde fallido -> %s (era: %s)" % (vuelve, motivo))
    guardar(dia)
    print("ranura #%d vuelve a '%s'. Toca: %s" % (p["slot"], vuelve, siguiente_estado(vuelve)))
    return 0


def cmd_reserva(args):
    """Piezas alojadas y sin publicar, de cualquier dia. Regla 2: nunca menos de 3."""
    total = []
    if os.path.isdir(DIR_ESTADO):
        for nombre in sorted(os.listdir(DIR_ESTADO)):
            if not nombre.endswith(".json"):
                continue
            dia = cargar(nombre[:-5])
            for p in dia["piezas"]:
                if p["estado"] in ("alojado", "programado"):
                    total.append((dia["fecha"], p))
    print("RESERVA: %d piezas alojadas sin publicar (minimo %d)" % (len(total), RESERVA_MINIMA))
    for fecha, p in total:
        print("  %s #%-2d %s  %s" % (fecha, p["slot"], p.get("tema", "(sin tema)")[:50], p.get("url", "")))
    if len(total) < RESERVA_MINIMA:
        print("POR DEBAJO DEL MINIMO: si hoy falla el render, el dia queda corto. "
              "Produce %d mas." % (RESERVA_MINIMA - len(total)))
        return 1
    return 0


def cmd_auditar(args):
    """Discrepancias entre lo que el dia deberia ser y lo que es. Codigo 1 si hay alguna."""
    fecha = args.fecha or hoy()
    dia = cargar(fecha)
    problemas = []

    for p in dia["piezas"]:
        if p["estado"] == "publicado":
            if not p.get("control"):
                problemas.append("#%d publicada SIN informe de control: nunca paso la puerta." % p["slot"])
            if not p.get("norma"):
                problemas.append("#%d publicada sin norma verificada (paso 'derecho' saltado)." % p["slot"])
        elif p["estado"] == FALLIDO:
            problemas.append("#%d fallida en '%s' (%d intentos): %s"
                             % (p["slot"], p.get("estado_previo", "?"), p.get("intentos", 0),
                                p.get("motivo", "sin motivo")))
        elif vencida(p, fecha):
            problemas.append("#%d atrasada: su hora (%s) paso y sigue en '%s'."
                             % (p["slot"], p["hora_chile"], p["estado"]))

    publicadas = sum(1 for p in dia["piezas"] if p["estado"] == "publicado")
    restantes = [p for p in dia["piezas"] if p["estado"] not in ("publicado", FALLIDO)]
    if publicadas + len(restantes) < dia["meta"]:
        problemas.append("el dia no alcanza la meta: %d publicadas + %d vivas < %d."
                         % (publicadas, len(restantes), dia["meta"]))

    if not problemas:
        print("AUDITORIA %s: sin discrepancias. %d/%d publicadas." % (fecha, publicadas, dia["meta"]))
        return 0
    print("AUDITORIA %s: %d discrepancias" % (fecha, len(problemas)))
    for x in problemas:
        print("  - %s" % x)
    return 1


def cmd_json(args):
    print(json.dumps(cargar(args.fecha or hoy()), ensure_ascii=False, indent=2))
    return 0


# --------------------------------------------------------------------------- cli

def main():
    ap = argparse.ArgumentParser(description="Libro de cuentas del dia de publicacion.")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def con_fecha(p):
        p.add_argument("--fecha", help="AAAA-MM-DD (por defecto, hoy en Chile)")
        return p

    a = con_fecha(sub.add_parser("abrir", help="abre el dia con sus ranuras"))
    a.add_argument("--meta", type=int, default=10)
    a.add_argument("--formato", default="noticia-vertical-relatada-sin-rostro")
    a.add_argument("--rehacer", action="store_true", help="pisa un dia ya abierto (pierde lo anotado)")
    a.set_defaults(func=cmd_abrir)

    con_fecha(sub.add_parser("resumen", help="reporte de 3 lineas")).set_defaults(func=cmd_resumen)

    s = con_fecha(sub.add_parser("siguiente", help="el unico trabajo que toca ahora"))
    s.add_argument("-n", type=int, default=1)
    s.set_defaults(func=cmd_siguiente)

    m = con_fecha(sub.add_parser("marcar", help="avanza una ranura"))
    m.add_argument("slot", type=int)
    m.add_argument("estado", choices=CADENA)
    m.add_argument("--campo", action="append", metavar="k=v")
    m.add_argument("--json", help="campos adicionales como objeto JSON")
    m.set_defaults(func=cmd_marcar)

    f = con_fecha(sub.add_parser("fallar", help="marca una ranura como fallida"))
    f.add_argument("slot", type=int)
    f.add_argument("--motivo", required=True)
    f.set_defaults(func=cmd_fallar)

    r = con_fecha(sub.add_parser("reintentar", help="devuelve una ranura fallida a su paso previo"))
    r.add_argument("slot", type=int)
    r.set_defaults(func=cmd_reintentar)

    sub.add_parser("reserva", help="piezas alojadas sin publicar").set_defaults(func=cmd_reserva, fecha=None)
    con_fecha(sub.add_parser("auditar", help="discrepancias del dia")).set_defaults(func=cmd_auditar)
    con_fecha(sub.add_parser("json", help="vuelca el dia")).set_defaults(func=cmd_json)

    args = ap.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
