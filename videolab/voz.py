#!/usr/bin/env python3
"""VIDEO LAB — módulo de VOZ con cadena de respaldo (validado 05/09/2026 en el sandbox de Higgsfield, CPU, sin GPU).

Uso:  python3 voz.py texto.txt salida.mp3 [motor]
motor: kokoro | piper | edge | auto (por defecto: auto = kokoro → piper → edge)

- kokoro  : Kokoro-82M (Apache 2.0), voz 'em_alex' español, ~8 s por pieza de 25 s en CPU. Gratis, sin clave. WER 0,0 en la prueba.
- piper   : Piper (MIT/ONNX), voz es_MX-claude-high, ~2,5 s por pieza. Gratis, offline. WER 0,06.
- edge    : edge-tts (voz es-CL-LorenzoNeural de Microsoft, servicio no oficial: puede cortarse). ~4 s. WER 0,03.
- Eleven (Cristian Cornejo, ClNifCEVq1smkl4M3aTk) queda como motor PREMIUM: se usa desde el conector, no desde aquí,
  solo para las piezas del brazo A del experimento de voz o cuando el guion exige emoción que los gratuitos no dan.

Instalación en el sandbox (una vez por sesión, ~90 s la primera vez):
  pip install -q piper-tts edge-tts kokoro soundfile && python3 -m piper.download_voices es_MX-claude-high
Ninguna clave, ningún archivo secreto. Salida: mp3 96 kbps, 44,1 kHz mono, normalizado a -16 LUFS (el motor vuelve a normalizar al mezclar).

El texto puede traer TRAMOS separados por líneas en blanco (gancho / punto 1 / punto 2 / punto 3 / cierre). Cada tramo se
sintetiza aparte y se une con PAUSA s de silencio; se escribe <salida>.tramos.json con los límites [t0..tn] para que
motor.py v2 corte exacto (campo "tramos" de la pieza).
"""
import sys, subprocess, warnings, os
warnings.filterwarnings("ignore")

def _norm(src, dst):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "44100", "-ac", "1"] + (["-b:a", "96k"] if dst.endswith(".mp3") else []) + [dst], check=True)

def kokoro(texto, dst):
    from kokoro import KPipeline
    import soundfile as sf, numpy as np
    p = KPipeline(lang_code="e", repo_id="hexgrad/Kokoro-82M")
    audio = np.concatenate([a for _, _, a in p(texto, voice="em_alex")])
    sf.write("_voz_tmp.wav", audio, 24000)
    _norm("_voz_tmp.wav", dst)

def piper(texto, dst, voz="es_MX-claude-high"):
    subprocess.run(["python3", "-m", "piper", "-m", voz, "-f", "_voz_tmp.wav", "--", texto], check=True, capture_output=True)
    _norm("_voz_tmp.wav", dst)

def edge(texto, dst, voz="es-CL-LorenzoNeural"):
    subprocess.run(["edge-tts", "--voice", voz, "--text", texto, "--write-media", "_voz_tmp.mp3"], check=True, capture_output=True)
    _norm("_voz_tmp.mp3", dst)

MOTORES = {"kokoro": kokoro, "piper": piper, "edge": edge}

def _dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]).decode().strip())

PAUSA = 0.7  # segundos de silencio entre tramos

def main():
    texto = open(sys.argv[1], encoding="utf-8").read().strip()
    dst = sys.argv[2]
    pedido = sys.argv[3] if len(sys.argv) > 3 else "auto"
    orden = ["kokoro", "piper", "edge"] if pedido == "auto" else [pedido]
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
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-t", str(PAUSA), "-i", "anullsrc=r=44100:cl=mono", "-ar", "44100", "-ac", "1", "_sil.wav"], check=True)
            lista = "".join(f"file '{p}'\nfile '_sil.wav'\n" for p in partes[:-1]) + f"file '{partes[-1]}'\n"
            open("_lista_voz.txt", "w").write(lista)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "_lista_voz.txt", "-b:a", "96k", dst], check=True)
            import json
            json.dump(limites, open(dst + ".tramos.json", "w"))
            print(f"VOZ_OK motor={m} dur={_dur(dst):.1f}s tramos={len(tramos)} -> {dst}")
            return
        except Exception as e:
            print(f"VOZ_FALLO motor={m}: {str(e)[:120]}")
    sys.exit("VOZ_SIN_MOTOR: usar Eleven desde el conector")

if __name__ == "__main__":
    main()
