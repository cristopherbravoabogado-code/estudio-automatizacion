#!/usr/bin/env python3
"""VIDEO LAB — subtítulos karaoke palabra por palabra, gratis (faster-whisper + libass). Validado 05/09/2026 en el sandbox.

Uso:  python3 karaoke.py voz.mp3 salida.ass [palabras_por_linea=4]
Luego en el motor (motor.py v2 lo hace solo con el campo "subs"):  ffmpeg ... -vf "ass=salida.ass" ...
Estilo: Montserrat ExtraBold 78 px, blanco con borde oscuro; la palabra que se está diciendo va en amarillo
(un evento por palabra, así solo la activa cambia de color). Alineación centro, MarginV 560 → sobre el tercio inferior,
fuera de la interfaz de TikTok y debajo del título de la lámina. Costo: 0. Tiempo: ~6 s por pieza de 25 s (CPU, modelo small int8).
"""
import sys, warnings
warnings.filterwarnings("ignore")
from faster_whisper import WhisperModel

audio, out = sys.argv[1], sys.argv[2]
N = int(sys.argv[3]) if len(sys.argv) > 3 else 4
m = WhisperModel("small", device="cpu", compute_type="int8")
segs, _ = m.transcribe(audio, language="es", word_timestamps=True)
words = [w for s in segs for w in s.words]

def ts(t):
    return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"

lines = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 2", "", "[V4+ Styles]",
 "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
 "Style: K,Montserrat ExtraBold,78,&H00FFFFFF,&H00FFFFFF,&H00101010,&H80000000,-1,0,0,0,100,100,0,0,1,6,0,2,60,60,560,1",
 "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
AMAR = "{\\c&H00E5FF&}"; BLANCO = "{\\c&HFFFFFF&}"
n_ev = 0
for i in range(0, len(words), N):
    grp = words[i:i+N]
    for j, w in enumerate(grp):
        fin = grp[j+1].start if j + 1 < len(grp) else w.end + 0.08
        txt = " ".join((AMAR + x.word.strip() + BLANCO) if k == j else x.word.strip() for k, x in enumerate(grp))
        lines.append(f"Dialogue: 0,{ts(w.start)},{ts(fin)},K,,0,0,0,,{txt}")
        n_ev += 1
open(out, "w", encoding="utf-8").write("\n".join(lines))
print(f"KARAOKE_OK palabras={len(words)} eventos={n_ev} -> {out}")
