#!/usr/bin/env python3
"""control.py v1 (15/09/2026) - LA PUERTA: los cuatro controles duros, en UN solo lugar.

POR QUE EXISTE
--------------
Hasta hoy la regla dura 3 (audio aac 48 kHz ESTEREO) vivia DENTRO de `motor/motor.py` y el
control de subida vivia DENTRO de `motor/produce.py`. Toda receta que produce su mp4 por fuera
del motor se los saltaba entera. El 14/09/2026 eso salio al aire: el SUPERVIDEO A
(`videolab/supervideo/build_sv.py`) subio `aac,48000,1` - MONO -, 60,74 s y volumen medio
-19,8 dB, rompiendo las reglas 3 y 5 a la vez. Su `final()` medias las cosas con `print("VERIF")`
y despues subia igual: **medir no es controlar si el resultado no puede bloquear la subida.**

Esto es la regla dura 3-ter de `motor/RECETA-MOTOR-NUBE.md` convertida en codigo: ninguna pieza
se sube sin pasar por aqui, la produzca quien la produzca. Una receta nueva no "nace con los
cuatro controles": importa este modulo o no sube.

LOS CONTROLES
-------------
 1. AUDIO      ffprobe tiene que decir exactamente aac,48000,2          (regla dura 3)
 2. DURACION   22-34 s por defecto, franja configurable                 (regla dura 5)
 3. VOLUMEN    volumen medio dentro de [-21, -13] dB                    (franja medida del motor)
 4. UNIONES    RMS de cada empalme <= -35 dBFS (solo si se dan los cortes)
 5. PANTALLA   0 cajas de TEXTO PROPIO fuera de x[95,930] y[200,1586]   (regla dura 4)
               -> se delega en videolab/pantalla_chica.py; INFORMA, no bloquea (ver PRODUCIR.md)

USO COMO MODULO
---------------
    from control import controlar, subir
    r = controlar("981.mp4", uniones=[6.1, 12.4, 18.9, 24.2])
    subir("981.mp4", upload_url, r)      # levanta RuntimeError si r["pasa"] es False

USO COMO CLI
------------
    python3 control.py 981.mp4 --uniones 6.1,12.4,18.9 --put "<upload_url>"
    exit 0 = PASA (y subio, si habia --put) | exit 1 = NO PASA (y NO subio nada)

ARREGLO SIN RE-RENDER
---------------------
    python3 control.py pieza.mp4 --remux    # re-encodea SOLO el audio a aac 48k estereo.
Conserva duracion y encuadre, ~3 s y 0 creditos. Metodo medido el 14/09/2026. Sirve para el
stock viejo (regla dura 3-bis): toda pieza de la RESERVA se re-mide con esto justo antes de
publicar, aunque la bitacora la de por limpia - esa etiqueta es del dia en que se escribio.
"""
import argparse, json, os, re, subprocess, sys

AUDIO_OK = "aac,48000,2"
DUR_MIN, DUR_MAX = 22.0, 34.0
VOL_MIN, VOL_MAX = -21.0, -13.0
UNION_MAX_DBFS = -35.0
VENTANA_UNION = 0.12          # s a cada lado del corte que se mide
ZONA = (95, 930, 200, 1586)   # x0, x1, y0, y1 - zona segura de TikTok


def _sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def audio(mp4):
    """Regla dura 3: aac, 48000 Hz, 2 canales. Devuelve (ok, lo_que_dijo_ffprobe)."""
    s = _sh(f'ffprobe -v error -select_streams a:0 -show_entries '
            f'stream=codec_name,sample_rate,channels -of csv=p=0 "{mp4}"').stdout
    return s.strip().replace(" ", "") == AUDIO_OK, s.strip()


def duracion(mp4, dmin=DUR_MIN, dmax=DUR_MAX):
    """Regla dura 5: la pieza tiene que caer en la franja medida."""
    s = _sh(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{mp4}"').stdout.strip()
    d = float(s) if s else 0.0
    return dmin <= d <= dmax, round(d, 2)


def volumen(mp4):
    """Volumen medio dentro de la franja del motor. Fuera de franja = pieza rara, se mira."""
    # OJO: volumedetect imprime en nivel "info". Con -v error el resumen NO sale y el
    # regex no encuentra nada (medido el 15/09: devolvia 0.0 y reprobaba piezas sanas).
    r = _sh(f'ffmpeg -hide_banner -nostats -i "{mp4}" -af volumedetect -f null - 2>&1')
    m = re.search(r"mean_volume:\s*(-?[\d.]+) dB", r.stderr + r.stdout)
    v = float(m.group(1)) if m else 0.0
    return VOL_MIN <= v <= VOL_MAX, v


def uniones(mp4, cortes):
    """RMS en cada empalme entre tramos. Un chasquido audible se oye como pico sobre -35 dBFS."""
    peor, detalle = -999.0, []
    for t in cortes or []:
        ini = max(0.0, float(t) - VENTANA_UNION)
        r = _sh(f'ffmpeg -hide_banner -nostats -ss {ini:.3f} -t {VENTANA_UNION * 2:.3f} '
                f'-i "{mp4}" -af volumedetect -f null - 2>&1')
        m = re.search(r"max_volume:\s*(-?[\d.]+) dB", r.stderr + r.stdout)
        v = float(m.group(1)) if m else -999.0
        detalle.append(round(v, 1))
        peor = max(peor, v)
    if not cortes:
        return True, []
    return peor <= UNION_MAX_DBFS, detalle


def pantalla(mp4):
    """Regla dura 4. INFORMA, no bloquea: pantalla_chica.py no distingue el texto propio del
    texto que trae el clip del gancho, y contar cajas a ciegas lleva a re-renderizar piezas
    sanas (medido el 13/09). Ver 'Como se lee el control de pantalla chica' en PRODUCIR.md."""
    if not os.path.exists("pantalla_chica.py"):
        return None, "pantalla_chica.py no esta al lado; control omitido"
    r = _sh(f'python3 pantalla_chica.py "{mp4}"')
    return None, (r.stdout or r.stderr).strip()[-400:]


def controlar(mp4, dmin=DUR_MIN, dmax=DUR_MAX, cortes=None):
    """Corre los cinco y devuelve el informe. 'pasa' es la conjuncion de los que BLOQUEAN."""
    a_ok, a = audio(mp4)
    d_ok, d = duracion(mp4, dmin, dmax)
    v_ok, v = volumen(mp4)
    u_ok, u = uniones(mp4, cortes)
    _, p = pantalla(mp4)
    r = {"pieza": os.path.basename(mp4),
         "audio": {"ok": a_ok, "valor": a, "esperado": AUDIO_OK},
         "duracion": {"ok": d_ok, "valor": d, "franja": [dmin, dmax]},
         "volumen": {"ok": v_ok, "valor": v, "franja": [VOL_MIN, VOL_MAX]},
         "uniones": {"ok": u_ok, "valor": u, "tope": UNION_MAX_DBFS},
         "pantalla_chica": {"ok": None, "valor": p},
         "pasa": bool(a_ok and d_ok and v_ok and u_ok)}
    r["falla"] = [k for k in ("audio", "duracion", "volumen", "uniones") if not r[k]["ok"]]
    return r


def remux(mp4, salida=None):
    """Arregla SOLO el audio a aac 48k estereo. No re-renderiza: conserva duracion y encuadre."""
    salida = salida or mp4.replace(".mp4", "_48k2.mp4")
    r = _sh(f'ffmpeg -y -v error -i "{mp4}" -c:v copy -c:a aac -ar 48000 -ac 2 -b:a 192k '
            f'-movflags +faststart "{salida}"')
    if r.returncode:
        raise RuntimeError(f"remux fallo: {r.stderr[-400:]}")
    return salida


def subir(mp4, upload_url, informe=None, dmin=DUR_MIN, dmax=DUR_MAX, cortes=None):
    """PUT a la upload_url presignada. NO sube si el control no pasa: ese es todo el punto.
    Devuelve el codigo HTTP (200 = subida buena)."""
    r = informe or controlar(mp4, dmin, dmax, cortes)
    if not r["pasa"]:
        raise RuntimeError(f"CONTROL NO PASA ({', '.join(r['falla'])}) -> no se sube {mp4}. "
                           f"{json.dumps({k: r[k] for k in r['falla']}, ensure_ascii=False)}")
    c = _sh(f'curl -s -o /dev/null -w "%{{http_code}}" -X PUT -H "Content-Type: video/mp4" '
            f'--data-binary @"{mp4}" "{upload_url}"').stdout.strip()
    return c


def main():
    ap = argparse.ArgumentParser(description="Los cuatro controles duros antes de publicar.")
    ap.add_argument("mp4")
    ap.add_argument("--dur-min", type=float, default=DUR_MIN)
    ap.add_argument("--dur-max", type=float, default=DUR_MAX)
    ap.add_argument("--uniones", default="", help="tiempos de corte en segundos, separados por coma")
    ap.add_argument("--put", default="", help="upload_url presignada; solo sube si el control pasa")
    ap.add_argument("--remux", action="store_true", help="arregla el audio a 48k estereo y re-mide")
    a = ap.parse_args()

    mp4 = a.mp4
    cortes = [float(x) for x in a.uniones.split(",") if x.strip()]
    r = controlar(mp4, a.dur_min, a.dur_max, cortes)

    if a.remux and not r["audio"]["ok"]:
        mp4 = remux(mp4)
        print(f"REMUX -> {mp4}")
        r = controlar(mp4, a.dur_min, a.dur_max, cortes)

    print(json.dumps(r, ensure_ascii=False, indent=1))
    if not r["pasa"]:
        print("NO PASA:", ", ".join(r["falla"]), "-> no se sube nada", file=sys.stderr)
        return 1
    if a.put:
        print("PUT", subir(mp4, a.put, r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
