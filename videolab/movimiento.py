#!/usr/bin/env python3
"""
movimiento.py — MOVIMIENTO REAL SOBRE FOTO FIJA (regla dura 7, M6 corrida 3, 23/09/2026)

Reemplaza al Ken Burns de `zoompan` en todo plano que nace de una foto quieta.
Estima profundidad con MiDaS-small (ONNX, CPU, sin GPU, US$0) y mueve la cámara en
órbita: los píxeles cercanos se desplazan más que los lejanos, así que hay PARALAJE
y no solo un zoom.

Números medidos el 23/09/2026 (5 fotos reales, clips de 6 s, 1080x1920, 30 fps,
métrica de movimiento = diferencia media por píxel entre cuadros a 1/15 s, gris, 96 px
de ancho; banda de los virales de referencia 4,6–9,9):

    Ken Burns actual (zoompan 1,00→1,12) ......... 1,14 de media (0,69 · 1,11 · 1,87 · 0,93 · 1,12)
    parallax 2.5D de este script ................. 4,85 de media (4,21 · 5,09 · 5,67 · 4,75 · 4,53)
    ltx-v2-fast de ElevenLabs (US$0,26/plano) .... 4,67  ← lo que veníamos pagando
    zoom rápido sin profundidad (1,00→1,75) ...... 3,76, y 2 de 3 fotos bajo la banda
    parallax suave (amp 0,045, 1 órbita) ......... 0,86  ⛔ PEOR que Ken Burns: no usarlo

Nitidez (varianza del laplaciano, media por clip): 28 vs 30, 8 vs 9, 14 vs 14 contra
Ken Burns — el warp NO degrada el detalle.

Costo US$0. Tiempo: 0,3 s de profundidad + 4,8 s de render por clip de 6 s en 8 núcleos.

Uso:
    python3 movimiento.py clip foto.jpg salida.mp4 [segundos]
    python3 movimiento.py control salida.mp4        # BLOQUEA si el movimiento < 4,0

Dependencias en el sandbox:  pip install onnxruntime opencv-python-headless
Modelo: https://github.com/isl-org/MiDaS/releases/download/v2_1/model-small.onnx (66 MB,
se descarga solo la primera vez y queda en MODELO).
"""
import math
import os
import subprocess
import sys
import time

import cv2
import numpy as np

MODELO = os.environ.get("MIDAS_ONNX", "/tmp/midas_small.onnx")
URL_MODELO = "https://github.com/isl-org/MiDaS/releases/download/v2_1/model-small.onnx"

# Ajustes GANADORES medidos el 23/09. No bajarlos "para que se vea más suave":
# con amp 0,045 y 1 órbita la métrica cae a 0,86 y queda por debajo del Ken Burns que reemplaza.
AMP = 0.14        # amplitud de la órbita (fracción del ancho)
ORBITAS = 3.0     # vueltas completas en todo el clip  <-- la variable que decide
Z0, Z1 = 1.20, 1.02   # el zoom retrocede; el movimiento no viene del zoom
PISO = 4.0        # umbral del control

_SESION = None


def _sesion():
    global _SESION
    if _SESION is None:
        import onnxruntime as ort
        if not os.path.exists(MODELO):
            subprocess.run(["curl", "-sL", "-o", MODELO, URL_MODELO], check=True)
        _SESION = ort.InferenceSession(MODELO, providers=["CPUExecutionProvider"])
    return _SESION


def profundidad(img):
    """Mapa de profundidad normalizado 0..1 (1 = cerca), del tamaño de la imagen."""
    s = _sesion()
    h, w = img.shape[:2]
    x = cv2.resize(img, (256, 256)).astype(np.float32) / 255.0
    x = (x - np.array([0.485, 0.456, 0.406], np.float32)) / np.array([0.229, 0.224, 0.225], np.float32)
    x = np.transpose(x, (2, 0, 1))[None]
    out = np.squeeze(s.run(None, {s.get_inputs()[0].name: x})[0])
    d = cv2.resize(out, (w, h)).astype(np.float32)
    d = (d - d.min()) / (d.max() - d.min() + 1e-6)
    # suavizar el mapa evita que los bordes de profundidad se rasguen al desplazar
    return cv2.GaussianBlur(d, (0, 0), max(w, h) * 0.008)


def encuadrar(img, W, H):
    ih, iw = img.shape[:2]
    tr = W / H
    if iw / ih > tr:
        nw = int(ih * tr)
        img = img[:, (iw - nw) // 2:(iw - nw) // 2 + nw]
    else:
        nh = int(iw / tr)
        img = img[(ih - nh) // 2:(ih - nh) // 2 + nh, :]
    return cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA)


def clip(src, out, dur=6.0, fps=30, W=1080, H=1920, amp=AMP, orbitas=ORBITAS, z0=Z0, z1=Z1):
    img = cv2.imread(src)
    if img is None:
        raise SystemExit(f"no pude leer {src}")
    img = encuadrar(img, W, H)
    t0 = time.time()
    d = profundidad(img)
    t_dep = time.time() - t0
    xs, ys = np.meshgrid(np.arange(W, dtype=np.float32), np.arange(H, dtype=np.float32))
    k = (d - 0.5).astype(np.float32)
    n = int(dur * fps)
    p = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24",
         "-s", f"{W}x{H}", "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "20", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    t1 = time.time()
    cx, cy = np.float32(W / 2), np.float32(H / 2)
    for i in range(n):
        u = i / max(n - 1, 1)
        z = np.float32(z0 + (z1 - z0) * u)
        a = 2 * math.pi * orbitas * u
        ox = np.float32(math.sin(a) * amp * W)
        oy = np.float32(math.cos(a * 0.7) * amp * 0.4 * H)
        mx = cx + (xs - cx) / z + ox * k          # float32 de punta a punta:
        my = cy + (ys - cy) / z + oy * k          # cv2.remap rechaza mapas float64
        f = cv2.remap(img, mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        p.stdin.write(f.tobytes())
    p.stdin.close()
    p.wait()
    return t_dep, time.time() - t1


def medir(path):
    """Métrica de movimiento del VIDEO LAB: banda viral 4,6–9,9; Ken Burns ≈ 1."""
    c = cv2.VideoCapture(path)
    fps = c.get(cv2.CAP_PROP_FPS) or 30
    paso = max(int(round(fps / 15.0)), 1)
    prev, ds, i = None, [], 0
    while True:
        ok, f = c.read()
        if not ok:
            break
        if i % paso == 0:
            g = cv2.cvtColor(cv2.resize(f, (96, int(96 * f.shape[0] / f.shape[1]))),
                             cv2.COLOR_BGR2GRAY).astype(np.float32)
            if prev is not None:
                ds.append(np.abs(g - prev).mean())
            prev = g
        i += 1
    c.release()
    return float(np.mean(ds)) if ds else 0.0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    modo = sys.argv[1]
    if modo == "clip":
        dur = float(sys.argv[4]) if len(sys.argv) > 4 else 6.0
        td, tr = clip(sys.argv[2], sys.argv[3], dur=dur)
        m = medir(sys.argv[3])
        print(f"CLIP {sys.argv[3]} movimiento={m:.2f} profundidad={td:.2f}s render={tr:.2f}s costo=US$0")
        if m < PISO:
            print(f"AVISO: {m:.2f} < {PISO} — subir ORBITAS antes de publicar")
    elif modo == "control":
        malos = []
        for v in sys.argv[2:]:
            m = medir(v)
            print(f"MOVIMIENTO\t{v}\t{m:.2f}")
            if m < PISO:
                malos.append((v, m))
        if malos:
            for v, m in malos:
                print(f"BLOQUEA {v}: movimiento {m:.2f} < {PISO} (regla dura 7)")
            sys.exit(1)
        print("MOVIMIENTO_OK")
    else:
        raise SystemExit(__doc__)
