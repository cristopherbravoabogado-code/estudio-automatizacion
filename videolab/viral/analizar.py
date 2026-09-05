#!/usr/bin/env python3
"""VIRAL LAB — radiografía numérica de un video viral (sandbox de Higgsfield).

Uso:  python3 analizar.py <url_o_archivo> <salida.json>
- URL de TikTok o YouTube: se baja con yt-dlp (--impersonate chrome para TikTok). Archivo local: se usa tal cual.
Mide: duración, cortes de escena (ffmpeg scene>0.3) y ritmo de corte, palabras/s, pausas > 0,5 s, loudness,
transcripción con marcas de tiempo (faster-whisper small), texto de los primeros 3 s (el gancho hablado),
y una segmentación por bloques (pausas > 0,8 s) para leer la ESTRUCTURA.
Salida: JSON con todo + resumen imprimible. Costo: 0. Tiempo: ~1-2 min por video de 2-3 min en CPU.
Requisitos: pip install -q "yt-dlp[default]" curl_cffi ; faster-whisper ya viene en el sandbox.
Validado 05/09/2026 con el viral-01: 104 cortes, 4,68 palabras/s, -17,5 dB.
"""
import sys, json, re, subprocess, os, warnings
warnings.filterwarnings("ignore")

def sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)

def bajar(url):
    out = "viral_in.mp4"
    imp = "--impersonate chrome" if "tiktok" in url else ""
    r = sh(f'yt-dlp -q {imp} -f "bv*[height<=720]+ba/b" --merge-output-format mp4 -o "{out}" "{url}"')
    if not os.path.exists(out):
        sys.exit("DESCARGA_FALLO " + r.stderr[-300:])
    meta = sh(f'yt-dlp -q {imp} -j --no-download "{url}"').stdout
    try:
        m = json.loads(meta)
        meta = {k: m.get(k) for k in ("id", "title", "uploader", "channel", "view_count", "like_count", "comment_count", "repost_count", "upload_date", "duration", "webpage_url")}
    except Exception:
        meta = {"webpage_url": url}
    return out, meta

def main():
    src, salida = sys.argv[1], sys.argv[2]
    meta = {}
    if src.startswith("http"):
        src, meta = bajar(src)
    dur = float(sh(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{src}"').stdout.strip())
    wh = sh(f'ffprobe -v error -select_streams v -show_entries stream=width,height -of csv=p=0 "{src}"').stdout.strip()
    r = sh(f'ffmpeg -i "{src}" -vf "select=\'gt(scene,0.3)\',showinfo" -an -f null -')
    cortes = [float(x) for x in re.findall(r"pts_time:([\d.]+)", r.stdout + r.stderr)]
    r = sh(f'ffmpeg -i "{src}" -af volumedetect -f null -')
    vd = r.stdout + r.stderr
    mean_db = re.search(r"mean_volume: ([-\d.]+)", vd); max_db = re.search(r"max_volume: ([-\d.]+)", vd)
    sh(f'ffmpeg -v error -y -i "{src}" -vn -ac 1 -ar 16000 viral_a.wav')
    from faster_whisper import WhisperModel
    m = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = m.transcribe("viral_a.wav", language="es", vad_filter=True, word_timestamps=True)
    S = []; words = []
    for s in segs:
        S.append({"t0": round(s.start, 1), "t1": round(s.end, 1), "texto": s.text.strip()})
        words += [(w.start, w.end, w.word) for w in s.words]
    n_words = len(words)
    habla = sum(s["t1"] - s["t0"] for s in S) or 1
    gaps = [(words[i+1][0] - words[i][1], words[i][1]) for i in range(len(words) - 1)]
    pausas = [(round(g, 2), round(t, 1)) for g, t in gaps if g > 0.5]
    gancho = " ".join(w.strip() for a, b, w in words if a < 3.0).strip()
    bloques, ini = [], 0.0
    for g, t in gaps:
        if g > 0.8 and t - ini > 6:
            bloques.append((round(ini, 1), round(t, 1))); ini = t + g
    bloques.append((round(ini, 1), round(dur, 1)))
    res = {"fuente": meta, "archivo": src, "duracion_s": round(dur, 1), "resolucion": wh,
           "cortes": len(cortes), "seg_por_corte": round(dur / max(len(cortes), 1), 2),
           "palabras": n_words, "palabras_por_s": round(n_words / dur, 2), "palabras_por_s_hablando": round(n_words / habla, 2),
           "pausas_mayores_0_5s": len(pausas), "pausas": pausas[:20],
           "loudness_media_db": mean_db.group(1) if mean_db else None, "pico_db": max_db.group(1) if max_db else None,
           "gancho_hablado_3s": gancho, "bloques": bloques, "transcripcion": S}
    json.dump(res, open(salida, "w"), ensure_ascii=False, indent=1)
    print(f"RADIOGRAFIA_OK dur={dur:.0f}s cortes={len(cortes)} (1 cada {res['seg_por_corte']} s) palabras/s={res['palabras_por_s']} pausas>0.5s={len(pausas)} loud={res['loudness_media_db']} dB")
    print("GANCHO 3s:", gancho)
    print("BLOQUES:", bloques)
    for s in S[:6]:
        print(f"  [{s['t0']:5.1f}] {s['texto'][:110]}")

if __name__ == "__main__":
    main()
