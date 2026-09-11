#!/usr/bin/env python3
"""VIDEO LAB - modulo de VOZ (v3, 11/09/2026): 48 kHz ESTEREO y union con FILTRO concat.
Uso:  python3 voz.py texto.txt salida.mp3 [kokoro|piper|edge|auto]
El texto trae 5 TRAMOS separados por lineas en blanco. Cada tramo se sintetiza aparte y se une
con silencio real; se escribe <salida>.tramos.json con los limites para motor.py v2.
v3: toda la cadena es 48000 Hz estereo y la union usa el FILTRO concat (no el demuxer), que
normaliza formato por entrada y hace imposible un empalme con parametros distintos.
"""
import sys, subprocess, warnings, json
warnings.filterwarnings("ignore")
SR, CH, CL = 48000, 2, "stereo"

def _norm(src, dst):
    subprocess.run(["ffmpeg","-v","error","-y","-i",src,"-af","loudnorm=I=-16:TP=-1.5:LRA=11",
                    "-ar",str(SR),"-ac",str(CH)] + (["-b:a","128k"] if dst.endswith(".mp3") else []) + [dst], check=True)

def kokoro(texto, dst):
    from kokoro import KPipeline
    import soundfile as sf, numpy as np
    p = KPipeline(lang_code="e", repo_id="hexgrad/Kokoro-82M")
    audio = np.concatenate([a for _, _, a in p(texto, voice="em_alex")])
    sf.write("_voz_tmp.wav", audio, 24000)
    _norm("_voz_tmp.wav", dst)

def piper(texto, dst, voz="es_MX-claude-high"):
    subprocess.run(["python3","-m","piper","-m",voz,"-f","_voz_tmp.wav","--",texto], check=True, capture_output=True)
    _norm("_voz_tmp.wav", dst)

def edge(texto, dst, voz="es-CL-LorenzoNeural"):
    subprocess.run(["edge-tts","--voice",voz,"--text",texto,"--write-media","_voz_tmp.mp3"], check=True, capture_output=True)
    _norm("_voz_tmp.mp3", dst)

MOTORES = {"kokoro": kokoro, "piper": piper, "edge": edge}
PAUSA = 0.7

def _dur(f):
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]).decode().strip())

def unir(partes, sil, dst):
    """Union con FILTRO concat: cada entrada se re-muestrea a 48k estereo antes de empalmar."""
    seq = []
    for i, p in enumerate(partes):
        seq.append(p)
        if i < len(partes) - 1:
            seq.append(sil)
    cmd = ["ffmpeg","-v","error","-y"]
    for f in seq:
        cmd += ["-i", f]
    pre = "".join(f"[{k}:a]aresample={SR},aformat=sample_fmts=fltp:channel_layouts={CL}[a{k}];" for k in range(len(seq)))
    filt = pre + "".join(f"[a{k}]" for k in range(len(seq))) + f"concat=n={len(seq)}:v=0:a=1[out]"
    cmd += ["-filter_complex", filt, "-map", "[out]", "-ar", str(SR), "-ac", str(CH), "-b:a", "128k", dst]
    subprocess.run(cmd, check=True)

def main():
    texto = open(sys.argv[1], encoding="utf-8").read().strip()
    dst = sys.argv[2]
    pedido = sys.argv[3] if len(sys.argv) > 3 else "auto"
    orden = ["kokoro","piper","edge"] if pedido == "auto" else [pedido]
    tramos = [t.strip() for t in texto.split("\n\n") if t.strip()]
    for m in orden:
        try:
            partes, limites, acc = [], [0.0], 0.0
            for i, tr in enumerate(tramos):
                f = f"_tramo{i}.wav"
                MOTORES[m](tr, f)
                partes.append(f)
                acc += _dur(f) + (PAUSA if i < len(tramos) - 1 else 0)
                limites.append(round(acc, 3))
            subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-t",str(PAUSA),
                            "-i",f"anullsrc=r={SR}:cl={CL}","-ar",str(SR),"-ac",str(CH),"_sil.wav"], check=True)
            unir(partes, "_sil.wav", dst)
            json.dump(limites, open(dst + ".tramos.json", "w"))
            info = subprocess.check_output(["ffprobe","-v","error","-select_streams","a:0",
                   "-show_entries","stream=sample_rate,channels","-of","csv=p=0",dst]).decode().strip()
            print(f"VOZ_OK motor={m} dur={_dur(dst):.1f}s tramos={len(tramos)} audio={info} -> {dst}")
            return
        except Exception as e:
            print(f"VOZ_FALLO motor={m}: {str(e)[:160]}")
    sys.exit("VOZ_SIN_MOTOR: usar Eleven desde el conector")

if __name__ == "__main__":
    main()
