#!/usr/bin/env python3
"""produce.py v1 (13/09/2026) - driver de produccion del Estudio Juridico San Bernardo.

POR QUE EXISTE
--------------
Hasta el 12/09 cada tanda se producia pegando el pipeline COMPLETO dentro del comando de
`sandbox_exec`, que tiene un tope de 16.000 caracteres. Como cada `upload_url` presignada de
Higgsfield mide ~2.400 caracteres, con cinco piezas las URLs solas se comian 12.000 y no cabia
el codigo: habia que partir la tanda a mano, reescribir el pipeline cada noche y cada reescritura
era una oportunidad nueva de equivocarse. Ese fue el costo repetido de las corridas del 11 y 12/09.

Con este driver el comando del sandbox se reduce a: bajar produce.py + un job.json compacto +
`python3 produce.py job.json`. El pipeline vive versionado en el repo, no en el prompt.

QUE HACE (una pieza completa, de punta a punta)
-----------------------------------------------
 1. baja videolab/voz.py, videolab/karaoke.py, videolab/pantalla_chica.py y motor/motor.py del repo
 2. pip install de lo que hace falta (kokoro, soundfile, faster-whisper, numpy, pillow, rapidocr)
 3. baja el clip de gancho y lo prepara (crop 9:16 + pista de audio silenciosa, o fondo
    desenfocado + audio original si es clip de prensa: "prensa": true)
 4. escribe urls/<id>.txt con los 5 tramos de voz separados por linea en blanco  (regla dura 2)
 5. voz.py (kokoro, 48 kHz estereo)  ->  karaoke.py  ->  motor.py
 6. CONTROL DE AUDIO: ffprobe tiene que decir aac,48000,2                         (regla dura 3)
 7. CONTROL DE DURACION: 22-34 s, si no avisa y marca la pieza                    (regla dura 5)
 8. CONTROL DE PANTALLA CHICA: videolab/pantalla_chica.py                         (regla dura 4)
 9. sube el mp4 con PUT a la upload_url presignada
Deja un informe en resultado.json con una linea por pieza.

job.json
--------
{"piezas":[{"id":"941","materia":"laboral","rotulo":"NOTICIA DE HOY",
            "hook":"https://assets.mixkit.co/videos/39912/39912-720.mp4","prensa":false,
            "gancho":"...","puntos":[{"t":"...","d":"..."} x3],"cierre":"...",
            "voz":["tramo1","tramo2","tramo3","tramo4","tramo5"],
            "upload_url":"https://...s3.amazonaws.com/..."}]}

Uso: python3 produce.py job.json   (dentro de UNA llamada sandbox_exec con background:true)
"""
import json, os, re, subprocess, sys, urllib.request

RAW = "https://raw.githubusercontent.com/cristopherbravoabogado-code/estudio-automatizacion/main/"
DEPS = ["videolab/voz.py", "videolab/karaoke.py", "videolab/pantalla_chica.py", "motor/motor.py"]
PIP = "kokoro soundfile faster-whisper numpy pillow rapidocr-onnxruntime"
DUR_MIN, DUR_MAX = 22.0, 34.0


def sh(cmd, check=True, t=900):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=t)
    if check and r.returncode != 0:
        raise RuntimeError(f"{cmd[:90]} -> {r.stderr[-1200:]}")
    return r


def preparar():
    for d in DEPS:
        urllib.request.urlretrieve(RAW + d, os.path.basename(d))
    print("DEPS_OK", flush=True)
    sh(f"pip install -q {PIP}", check=False, t=900)
    print("PIP_OK", flush=True)


def hook(url, dst, prensa):
    urllib.request.urlretrieve(url, "raw_hook.mp4")
    if prensa:
        # clip de prensa: fondo desenfocado + clip centrado, conserva cintillo y AUDIO ORIGINAL
        f = ("[0:v]split=2[bg][fg];"
             "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
             "boxblur=25:2,eq=brightness=-0.14[b];"
             "[fg]scale=1080:-2:flags=lanczos,unsharp=5:5:0.9:5:5:0.0[f];"
             "[b][f]overlay=(W-w)/2:(H-h)/2,fps=30[v];"
             "[0:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[a]")
        sh(f'ffmpeg -y -hide_banner -loglevel error -t 12 -i raw_hook.mp4 -filter_complex "{f}" '
           f'-map "[v]" -map "[a]" -t 12 -c:v libx264 -preset veryfast -crf 19 '
           f'-c:a aac -ar 48000 -ac 2 -b:a 128k {dst}')
    else:
        # metraje real de stock: crop 9:16 + pista de audio silenciosa (sin ella el mux falla)
        sh(f'ffmpeg -y -hide_banner -loglevel error -i raw_hook.mp4 -f lavfi -t 12 '
           f'-i anullsrc=r=48000:cl=stereo -vf "scale=1080:1920:'
           f'force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,'
           f'unsharp=5:5:0.9:5:5:0.0,fps=30" -map 0:v -map 1:a -t 12 -c:v libx264 '
           f'-preset veryfast -crf 19 -c:a aac -ar 48000 -ac 2 -b:a 128k {dst}')


def una(p):
    i = p["id"]
    r = {"id": i, "pasos": []}
    hook(p["hook"], f"hook{i}.mp4", p.get("prensa", False))
    r["pasos"].append("hook")

    os.makedirs("urls", exist_ok=True)
    txt = "\n\n".join(t.strip() for t in p["voz"])          # regla dura 2: tildes, UTF-8, 5 tramos
    open(f"urls/{i}.txt", "w", encoding="utf-8").write(txt + "\n")
    v = sh(f"python3 voz.py urls/{i}.txt {i}.mp3 kokoro")
    r["voz"] = v.stdout.strip().splitlines()[-1] if v.stdout.strip() else ""
    sh(f"python3 karaoke.py {i}.mp3 {i}.ass")
    r["pasos"].append("voz+karaoke")

    pieza = {"id": i, "materia": p["materia"], "gancho": p["gancho"], "puntos": p["puntos"],
             "cierre": p["cierre"], "voz": f"{i}.mp3", "hook": f"hook{i}.mp4",
             "subs": f"{i}.ass", "tramos": json.load(open(f"{i}.mp3.tramos.json"))}
    if p.get("rotulo"):
        pieza["rotulo"] = p["rotulo"]
    json.dump(pieza, open(f"pieza{i}.json", "w"), ensure_ascii=False)
    m = sh(f"python3 motor.py pieza{i}.json {i}.mp4")
    r["motor"] = m.stdout.strip().splitlines()[-1]
    r["pasos"].append("motor")

    # --- controles obligatorios -------------------------------------------------
    a = sh(f'ffprobe -v error -select_streams a:0 -show_entries '
           f'stream=codec_name,sample_rate,channels -of csv=p=0 {i}.mp4').stdout.strip()
    r["audio"] = a
    r["audio_ok"] = a.replace(" ", "") == "aac,48000,2"                      # regla dura 3
    d = float(sh(f'ffprobe -v error -show_entries format=duration -of csv=p=0 {i}.mp4').stdout)
    r["dur"] = round(d, 2)
    r["dur_ok"] = DUR_MIN <= d <= DUR_MAX                                    # regla dura 5
    q = sh(f"python3 pantalla_chica.py {i}.mp4", check=False, t=600)         # regla dura 4
    r["pantalla_chica"] = (q.stdout + q.stderr).strip()[-600:]
    r["pantalla_exit"] = q.returncode

    if not r["audio_ok"]:
        r["subida"] = "NO SUBIDA: audio fuera de norma"
        return r
    if not r["dur_ok"]:
        r["subida"] = f"NO SUBIDA: dura {r['dur']} s, fuera de 22-34"
        return r
    u = sh(f'curl -s -o /dev/null -w "%{{http_code}}" -X PUT '
           f'-H "Content-Type: video/mp4" --data-binary @{i}.mp4 \'{p["upload_url"]}\'')
    r["subida"] = u.stdout.strip()
    return r


def main(job):
    preparar()
    out = []
    for p in json.load(open(job))["piezas"]:
        try:
            out.append(una(p))
        except Exception as e:
            out.append({"id": p["id"], "error": str(e)[-800:]})
        json.dump(out, open("resultado.json", "w"), ensure_ascii=False, indent=1)
        print("PIEZA", p["id"], "lista", flush=True)
    print("PRODUCE_FIN")
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1])
