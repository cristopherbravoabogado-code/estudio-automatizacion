#!/usr/bin/env python3
"""VIDEO LAB — QC DE PANTALLA CHICA (11/09/2026). Mide dos cosas que no se ven mirando el video en grande:

  1) ¿Se lee el texto en un teléfono? Se remuestrea cada cuadro al 25% (270x480, que es lo que queda tras la
     compresión de TikTok y lo que alcanza a leer el ojo de pasada) y se compara lo que el OCR reconoce ahí
     contra lo que reconoce a tamaño completo. RECALL = palabras que sobreviven / palabras del cuadro.
  2) ¿Hay texto debajo de la interfaz de TikTok? Zona segura medida para 1080x1920 (spec 2026):
     arriba 200 px (buscador y pestañas), abajo 334 px (usuario, copy y marquesina de audio),
     izquierda 86 px (bisel), derecha 140 px (avatar, corazón, comentarios, compartir).
     Lo que cae fuera existe en el archivo pero el espectador NO lo ve.

Uso:      python3 pantalla_chica.py pieza.mp4 [cada_seg=3]
Requiere: pip install -q rapidocr-onnxruntime   (CPU, sin GPU, ~20 s la primera vez por sandbox)
Corte:    recall >= 0.80 y 0 cajas fuera de la zona segura. Devuelve código 1 si no pasa.

Medición base (piloto F11 del 05/09, 25 cuadros): recall 0,34 · 83 de 137 cajas fuera de la zona segura
(25 arriba = etiqueta DRAMATIZACIÓN, 25 abajo = línea de marca + WhatsApp, 32 a la derecha = placas).
Umbral medido de tamaño: bajo 40 px de alto de caja sobrevive el 22% de las palabras; sobre 80 px, el 85%.
"""
import sys, os, glob, json, re, time, subprocess, unicodedata, tempfile
import numpy as np
from PIL import Image

SEGURA = dict(arriba=200, abajo=1920 - 334, izq=86, der=1080 - 140)
MIN_RECALL, MIN_ALTO = 0.80, 80


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s)


def leer(ocr, im):
    """Devuelve [(palabra_normalizada, caja)] con confianza >= 0.5 y 3+ caracteres."""
    out = []
    res, _ = ocr(np.array(im))
    for caja, txt, conf in (res or []):
        if conf < 0.5:
            continue
        for w in txt.split():
            n = norm(w)
            if len(n) >= 3:
                out.append((n, caja))
    return out


def main(mp4, cada=3):
    from rapidocr_onnxruntime import RapidOCR
    ocr = RapidOCR()
    t0 = time.time()
    tmp = tempfile.mkdtemp()
    subprocess.run(f'ffmpeg -v error -y -i "{mp4}" -vf fps=1/{cada} -q:v 2 {tmp}/%03d.jpg',
                   shell=True, check=True)
    rec, altos, nref = [], [], 0
    fuera = dict(arriba=0, abajo=0, izq=0, der=0, ok=0)
    chicas = 0
    for p in sorted(glob.glob(f"{tmp}/*.jpg")):
        im = Image.open(p).convert("RGB")
        grande = leer(ocr, im)
        chica = set(w for w, _ in leer(ocr, im.resize((270, 480), Image.LANCZOS)
                                          .resize((1080, 1920), Image.BICUBIC)))
        vistas = set(w for w, _ in grande)
        if vistas:
            rec.append(len(vistas & chica) / len(vistas))
            nref += len(vistas)
        for w, caja in grande:
            xs = [q[0] for q in caja]; ys = [q[1] for q in caja]
            alto = max(ys) - min(ys)
            altos.append(alto)
            if alto < MIN_ALTO:
                chicas += 1
            mal = False
            if min(ys) < SEGURA["arriba"]:  fuera["arriba"] += 1; mal = True
            if max(ys) > SEGURA["abajo"]:   fuera["abajo"] += 1;  mal = True
            if min(xs) < SEGURA["izq"]:     fuera["izq"] += 1;    mal = True
            if max(xs) > SEGURA["der"]:     fuera["der"] += 1;    mal = True
            if not mal:
                fuera["ok"] += 1
    recall = round(float(np.mean(rec)), 2) if rec else 0.0
    n_fuera = sum(v for k, v in fuera.items() if k != "ok")
    r = {
        "archivo": os.path.basename(mp4),
        "cuadros": len(rec),
        "palabras_medidas": nref,
        "recall_pantalla_chica": recall,
        "cajas_fuera_zona_segura": n_fuera,
        "detalle_fuera": {k: v for k, v in fuera.items() if k != "ok"},
        "cajas_dentro": fuera["ok"],
        "alto_texto_mediana_px": round(float(np.median(altos)), 0) if altos else 0,
        "cajas_bajo_80px": chicas,
        "seg": round(time.time() - t0, 1),
    }
    r["veredicto"] = "PASA" if (recall >= MIN_RECALL and n_fuera == 0) else "NO PASA"
    print(json.dumps(r, ensure_ascii=False))
    return 0 if r["veredicto"] == "PASA" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 3))
