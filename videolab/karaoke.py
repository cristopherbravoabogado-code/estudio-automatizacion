#!/usr/bin/env python3
"""VIDEO LAB — subtítulos karaoke palabra por palabra, gratis (faster-whisper + libass). Validado 05/09/2026 en el sandbox.

Uso:  python3 karaoke.py voz.mp3 salida.ass [palabras_por_linea_max=4]
Luego en el motor (motor.py v2 lo hace solo con el campo "subs"):  ffmpeg ... -vf "ass=salida.ass" ...

Estilo v2 (11/09/2026 — CAJA OPACA, medido): Montserrat ExtraBold 78 px, blanco sobre CAJA OPACA #101010 al 86%
(ASS BorderStyle 3, OutlineColour &H23101010, Outline 6 = relleno de la caja). La palabra que se está diciendo va
en amarillo (un evento por palabra, así solo la activa cambia de color).
Por qué la caja y no el contorno: con el contorno solo, a 25% de escala (teléfono / vista previa / bitrate bajo)
se leía el 29% de las palabras; con la caja, el 100%. n=24 intentos por estilo, 6 fondos, render libass real.
Subir la fuente a 96 px NO cambia nada (0,29 con contorno, 1,00 con caja): lo que decide es el fondo, no el tamaño.

v3 (12/09/2026 — ANCHO MEDIDO, no palabras fijas). Defecto encontrado con rapidocr sobre la pieza 934: la línea
"identificación. Fingir ser autoridad" (4 palabras, 36 caracteres) midió **922 px** de ancho y se salió por los DOS
lados de la zona segura (x=52 y x=974, contra el límite 95-930). Con `WrapStyle: 2` libass NO corta solo: la línea
se desborda centrada, la mitad para cada lado.
Ahora cada grupo se mide con PIL usando la fuente real y se corta antes de pasar de ANCHO_MAX.
`palabras_por_linea_max` sigue siendo un TOPE, nunca un mínimo: un grupo puede quedar de 2 palabras si son largas.
Imprime `ancho_max=<px>` para poder verificarlo por números, sin mirar el video.

v3.1 (13/09/2026 — MÁRGENES DE DIBUJO, medido sobre la pieza 941). El v3 midió el ancho pero dejó los márgenes
en el BORDE CRUDO de la zona segura (MarginL 95 / MarginR 150), y ahí seguía saliéndose:
  - con alineación centrada libass centra en (95 + 930) / 2 = **512,5**;
  - una línea de ANCHO_MAX = 800 px ocupa 512,5 ± 400 → llega a **x = 912,5**;
  - la caja que mide el OCR se extiende **~17 px más allá del glifo** → **929,5**, es decir el borde exacto (930),
    y el ruido de medición empuja algunas cajas afuera.
Medición del 13/09 sobre el tramo de láminas de la 941: **3 cajas fuera por la derecha**, todas de karaoke.
`motor.py` ya había aprendido esto en su v5 (e) y metió sus márgenes de DIBUJO 35 px hacia dentro (SEG_X0 130,
SEG_X1 925); el karaoke se había quedado con el borde crudo. Ahora hace lo mismo:
  - **MarginL 130 / MarginR 185** (ancho útil 1080 − 130 − 185 = 765 px),
  - **ANCHO_MAX = 730 px** → la línea más ancha llega a x = 877 y su caja medida a x = 894, con 35 px de holgura.
⚠️ Por qué no se vio antes: con alineación centrada **solo se sale la pieza que trae líneas largas**. Las piezas
942 y 943 de la misma tanda dieron 0 cajas fuera con el mismo código. El defecto es INTERMITENTE, así que no
sirve validar el karaoke con una pieza: hay que mirar `ancho_max` que imprime este script en TODAS.
"""
import sys, warnings
warnings.filterwarnings("ignore")
from faster_whisper import WhisperModel
from PIL import ImageFont

audio, out = sys.argv[1], sys.argv[2]
N = int(sys.argv[3]) if len(sys.argv) > 3 else 4
TAM = 78
# Márgenes de DIBUJO, 35 px dentro del borde real de la zona segura (95 / 930), igual que
# SEG_X0/SEG_X1 en motor.py v5. NO son el borde: la caja del OCR sobresale ~17 px del glifo.
MARGEN_L, MARGEN_R = 130, 185
ANCHO_MAX = 730          # 765 px útiles entre los márgenes, con 35 px de holgura
F_HEAD = "/usr/share/fonts/truetype/higgsfield/Montserrat-ExtraBold.ttf"
try:
    FUENTE = ImageFont.truetype(F_HEAD, TAM)
except Exception:
    FUENTE = None

def ancho(texto):
    """Ancho real en px de la línea, con la fuente del estilo. Sin PIL, estima por caracteres."""
    if FUENTE is None:
        return len(texto) * TAM * 0.33
    return FUENTE.getlength(texto)

m = WhisperModel("small", device="cpu", compute_type="int8")
segs, _ = m.transcribe(audio, language="es", word_timestamps=True)
words = [w for s in segs for w in s.words]

def ts(t):
    return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"

def grupos(ws):
    """Agrupa por ancho medido: corta cuando la línea pasaría de ANCHO_MAX o del tope de palabras."""
    out, act = [], []
    for w in ws:
        prueba = act + [w]
        texto = " ".join(x.word.strip() for x in prueba)
        if act and (ancho(texto) > ANCHO_MAX or len(prueba) > N):
            out.append(act)
            act = [w]
        else:
            act = prueba
    if act:
        out.append(act)
    return out

lines = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "WrapStyle: 2", "", "[V4+ Styles]",
 "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
 f"Style: K,Montserrat ExtraBold,{TAM},&H00FFFFFF,&H00FFFFFF,&H23101010,&H00101010,-1,0,0,0,100,100,0,0,3,6,0,2,{MARGEN_L},{MARGEN_R},560,1",
 "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
AMAR = "{\\c&H00E5FF&}"; BLANCO = "{\\c&HFFFFFF&}"
n_ev = 0
gs = grupos(words)
anchos = []
for grp in gs:
    anchos.append(ancho(" ".join(x.word.strip() for x in grp)))
    for j, w in enumerate(grp):
        fin = grp[j+1].start if j + 1 < len(grp) else w.end + 0.08
        txt = " ".join((AMAR + x.word.strip() + BLANCO) if k == j else x.word.strip() for k, x in enumerate(grp))
        lines.append(f"Dialogue: 0,{ts(w.start)},{ts(fin)},K,,0,0,0,,{txt}")
        n_ev += 1
open(out, "w", encoding="utf-8").write("\n".join(lines))
peor = max(anchos) if anchos else 0
# x del borde derecho de la línea más ancha, centrada entre los márgenes, + 17 px de caja OCR
centro = (MARGEN_L + (1080 - MARGEN_R)) / 2
borde = centro + peor / 2 + 17
print(f"KARAOKE_OK palabras={len(words)} lineas={len(gs)} eventos={n_ev} "
      f"ancho_max={peor:.0f}px borde_der={borde:.0f}px "
      f"({'OK' if peor <= ANCHO_MAX and borde <= 930 else 'SE PASA'}) -> {out}")
