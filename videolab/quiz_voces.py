#!/usr/bin/env python3
"""Voces para el F12 (quiz legal): una por pregunta (texto_q → voz_q) y una por respuesta (texto_a → voz_a),
más intro y cierre. Kokoro em_alex (gratis, sin clave), loudnorm y recorte de silencios. ~5 s por pieza en CPU.
Uso en el sandbox:  pip install -q kokoro soundfile ; python3 quiz_voces.py pieza.json   (background:true, ~2 min)
"""
import sys, json, warnings, subprocess
import numpy as np, soundfile as sf
warnings.filterwarnings("ignore")
from kokoro import KPipeline

P = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "pieza.json"))
p = KPipeline(lang_code="e", repo_id="hexgrad/Kokoro-82M")
jobs = []
if P.get("intro"): jobs.append((P["intro"]["texto_voz"], P["intro"]["voz"]))
if P.get("cierre"): jobs.append((P["cierre"]["texto_voz"], P["cierre"]["voz"]))
for q in P["preguntas"]:
    jobs += [(q["texto_q"], q["voz_q"]), (q["texto_a"], q["voz_a"])]
for txt, dst in jobs:
    a = np.concatenate([x for _, _, x in p(txt, voice="em_alex", speed=1.06)])
    sf.write("_t.wav", a, 24000)
    subprocess.run(f'ffmpeg -y -v error -i _t.wav -af "loudnorm=I=-16:TP=-1.5:LRA=11,silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse" -ar 24000 -ac 1 {dst}', shell=True)
    print("VOZ", dst, round(len(a) / 24000, 2), flush=True)
print("VOCES_OK")
