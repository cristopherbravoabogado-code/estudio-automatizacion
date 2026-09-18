#!/usr/bin/env python3
"""
videolab/musica.py — CAMA MUSICAL GRATIS CON DUCKING (M6 corrida 2, 18/09/2026)

Qué hace:
  1) busca música/efectos CC0 en Openverse (sin clave, sin cuenta) y baja el archivo
  2) la mezcla bajo una narración con DUCKING (sidechaincompress): la música baja sola
     cuando habla la voz y sube sola en los silencios
  3) mide lo que decide: nivel de voz entregado y relleno de los silencios, en LUFS

Por qué ducking y no música estática (medido el 18/09/2026, ver RECETA regla dura 6):
  la voz entregada queda igual (-14,4 contra -14,2 LUFS de la voz sola) pero los
  silencios pasan de -26,0 a -13,4 LUFS. Para rellenar igual con música estática hay
  que ponerla a 0 dB, y ahí la mezcla sube a -13,1 LUFS: TikTok normaliza a ~-14 y
  baja la pieza entera, o sea la voz se entrega más callada que sin música.

Uso:
  python3 musica.py buscar "cinematic tension" 5
  python3 musica.py mezclar voz.wav musica.mp3 salida.wav [ganancia_db=0]
  python3 musica.py medir salida.wav tramos.json
  python3 musica.py control salida.wav tramos.json   # devuelve 1 si no pasa
"""
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request

OPENVERSE = "https://api.openverse.org/v1/audio/"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36"
AF = "aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo"
LN = "loudnorm=I=-16:TP=-1.5:LRA=11"


def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def buscar(q, n=5, licencia="cc0"):
    """Openverse, sin clave. licencia=cc0 => no exige atribución.
    Con cc-by hay que acreditar al autor en la descripción del video."""
    url = OPENVERSE + "?" + urllib.parse.urlencode(
        {"q": q, "license": licencia, "page_size": n})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    d = json.load(urllib.request.urlopen(req, timeout=30))
    out = []
    for r in d.get("results", []):
        out.append({"titulo": r.get("title"), "licencia": r.get("license"),
                    "proveedor": r.get("provider"), "url": r.get("url"),
                    "duracion_ms": r.get("duration")})
    return out


def bajar(url, destino):
    r = sh(f'curl -s -L -m 120 -A "{UA}" -o "{destino}" -w "%{{http_code}}" "{url}"')
    if r.stdout.strip() != "200" or not os.path.exists(destino):
        raise RuntimeError(f"descarga fallida {r.stdout}")
    return destino


def mezclar(voz, musica, salida, ganancia_db=0, desde=0):
    """Ducking real. ganancia_db=0 => música al mismo nivel nominal que la voz;
    el sidechain la mantiene abajo mientras hay voz."""
    fc = (f'[0:a]{LN},{AF},asplit=2[v][sc];'
          f'[1:a]atrim={desde},asetpts=N/SR/TB,{LN},'
          f'volume={ganancia_db}dB,{AF}[m];'
          f'[m][sc]sidechaincompress=threshold=0.03:ratio=12:attack=15:'
          f'release=350:makeup=1[md];'
          f'[v][md]amix=inputs=2:duration=first:normalize=0,{AF}[a]')
    # -stream_loop -1 repite la pista si es más corta que la narración
    cmd = (f'ffmpeg -y -v error -i "{voz}" -stream_loop -1 -i "{musica}" '
           f'-filter_complex "{fc}" -map "[a]" -ar 48000 -ac 2 "{salida}"')
    r = sh(cmd)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-400:])
    return salida


def lufs(f):
    r = sh(f'ffmpeg -hide_banner -i "{f}" -af '
           f'loudnorm=I=-14:TP=-1.0:print_format=json -f null -')
    m = re.search(r'"input_i"\s*:\s*"(-?[\d.]+)"', r.stderr + r.stdout)
    return float(m.group(1)) if m else None


def medir(mezcla, tramos_json):
    """tramos_json: lista de [inicio,fin] de los tramos CON VOZ (segundos).
    Devuelve el nivel entregado de la voz y el relleno de los silencios,
    ya normalizado a -14 LUFS como hace TikTok."""
    spans = json.load(open(tramos_json)) if isinstance(tramos_json, str) else tramos_json
    gaps = [[spans[i][1], spans[i + 1][0]] for i in range(len(spans) - 1)
            if spans[i + 1][0] - spans[i][1] > 0.15]
    sel = lambda sp: "+".join(f"between(t,{a},{b})" for a, b in sp)
    sh(f'ffmpeg -y -v error -i "{mezcla}" -af loudnorm=I=-14:TP=-1.0:LRA=11 _n.wav')
    sh(f'ffmpeg -y -v error -i _n.wav -af "aselect=\'{sel(spans)}\',asetpts=N/SR/TB" _s.wav')
    res = {"lufs_mezcla": lufs(mezcla), "voz_entregada": lufs("_s.wav")}
    if gaps:
        sh(f'ffmpeg -y -v error -i _n.wav -af "aselect=\'{sel(gaps)}\',asetpts=N/SR/TB" _g.wav')
        res["silencios"] = lufs("_g.wav")
    return res


CRITERIO = {
    # una pieza con cama musical pasa si:
    "voz_entregada_min": -14.8,   # no más de 0,6 dB bajo la voz sola (-14,2)
    "lufs_mezcla_max": -15.5,     # si sube de aquí, TikTok baja la pieza entera
    "silencios_max": -12.0,       # relleno, no invasión
}


def control(mezcla, tramos_json):
    m = medir(mezcla, tramos_json)
    fallas = []
    if m["voz_entregada"] < CRITERIO["voz_entregada_min"]:
        fallas.append(f"voz entregada {m['voz_entregada']} < {CRITERIO['voz_entregada_min']}")
    if m["lufs_mezcla"] > CRITERIO["lufs_mezcla_max"]:
        fallas.append(f"mezcla {m['lufs_mezcla']} > {CRITERIO['lufs_mezcla_max']} (TikTok la bajara)")
    if m.get("silencios", -99) > CRITERIO["silencios_max"]:
        fallas.append(f"silencios {m['silencios']} > {CRITERIO['silencios_max']}")
    print("MUSICA_" + ("OK " if not fallas else "FALLA ") + json.dumps(m))
    for f in fallas:
        print("  BLOQUEA:", f)
    return 0 if not fallas else 1


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__)
    elif a[0] == "buscar":
        print(json.dumps(buscar(a[1], int(a[2]) if len(a) > 2 else 5),
                         ensure_ascii=False, indent=1))
    elif a[0] == "mezclar":
        print(mezclar(a[1], a[2], a[3], float(a[4]) if len(a) > 4 else 0))
    elif a[0] == "medir":
        print(json.dumps(medir(a[1], a[2]), indent=1))
    elif a[0] == "control":
        sys.exit(control(a[1], a[2]))
