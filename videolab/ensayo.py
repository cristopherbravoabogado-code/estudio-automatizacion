#!/usr/bin/env python3
"""VIDEO LAB — formato ENSAYO (F11): narración continua sobre muchos planos cortos (corte cada ~2,5 s),
subtítulos karaoke, placas de texto en momentos clave y el "anuncio" del estudio integrado como un argumento más.
Aprendido del análisis del viral-01 (05/09/2026): anécdota → tesis polémica → promesa → puente → anuncio → mitos → cliffhanger.

Uso: python3 ensayo.py pieza.json salida.mp4   (requiere motor.py en la misma carpeta)
pieza.json: {"voz":"v.mp3", "subs":"v.ass", "materia":"laboral", "etiqueta":"DRAMATIZACIÓN",
             "shots":["f01.png", "f02.png", ...],            # planos en orden; se reparten el tiempo a partes iguales
             "placas":[{"t0":14.0,"t1":19.0,"titulo":"...","sub":"..."}, ...]}   # tarjetas que aparecen entre t0 y t1

v2 (11/09/2026) — ZONA SEGURA DE TIKTOK. Todo el texto vive dentro de x[95,930] y[200,1586]:
fuera de ahí lo tapan el buscador (arriba 200 px), el bloque de usuario y copy (abajo 334 px),
el bisel (izq 86 px) y la columna de corazón/comentarios/compartir (der 140 px).
En el piloto del 05/09, 83 de 137 cajas de texto caían fuera — incluida la línea de marca + WhatsApp,
que estaba en y=1770, debajo del copy de TikTok: el CTA existía en el archivo y nadie lo veía nunca.
Verificar con `python3 pantalla_chica.py salida.mp4`.
"""
import json, sys, os
from PIL import Image, ImageDraw
from motor import sh, dur, fuente, bloque, W, H, FPS, F_HEAD, F_BOLD, F_BODY, CREMA, LATON, TINTA, ACENTO, MARCA, TEL

# Zona segura TikTok 1080x1920 (spec 2026)
SX0, SX1, SY0, SY1 = 95, 930, 200, 1586

def escena(img, d, out, k):
    frames = int(d * FPS) + 1
    modo = k % 3
    if modo == 0:   # zoom in
        z = "min(1.0+0.0012*on,1.18)"; x = "iw/2-(iw/zoom/2)"; y = "ih/2-(ih/zoom/2)"
    elif modo == 1: # zoom out
        z = "max(1.18-0.0012*on,1.0)"; x = "iw/2-(iw/zoom/2)"; y = "ih/2-(ih/zoom/2)"
    else:           # paneo lateral con zoom fijo
        z = "1.15"; x = f"(iw-iw/zoom)*on/{frames}"; y = "ih/2-(ih/zoom/2)"
    sh(f'ffmpeg -y -hide_banner -loglevel error -loop 1 -i "{img}" -filter_complex '
       f'"[0:v]scale=2160:3840:force_original_aspect_ratio=increase,crop=2160:3840,'
       f'zoompan=z=\'{z}\':x=\'{x}\':y=\'{y}\':d={frames}:s={W}x{H}:fps={FPS},format=yuv420p" '
       f'-t {d:.3f} -an -c:v libx264 -preset veryfast -crf 20 -r {FPS} "{out}"')

def placa(materia, titulo, sub, out):
    """Tarjeta tipo '$150 vs $23': fondo tinta translúcido, título enorme, subtítulo, filete de materia.
    v2: la tarjeta va de x=95 a x=930 (zona segura) y el subtítulo sube de 46 a 58 px —
    bajo 80 px de alto de caja solo sobrevive el 22% de las palabras al 25% de escala."""
    acc = ACENTO.get(materia, LATON)
    ancho = SX1 - SX0
    cx = (SX0 + SX1) / 2
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f_t, l_t = bloque(d, titulo, F_HEAD, 120, ancho - 80, 4, 64)
    f_s, l_s = bloque(d, sub, F_BODY, 58, ancho - 100, 3, 40) if sub else (None, [])
    alto = len(l_t) * f_t.size * 1.08 + (40 + len(l_s) * f_s.size * 1.3 if sub else 0) + 120
    y0 = min(max(H * 0.42 - alto / 2, SY0 + 20), SY1 - alto - 20)
    d.rounded_rectangle((SX0, y0, SX1, y0 + alto), 28, fill=TINTA + (225,))
    d.rectangle((SX0, y0, SX0 + 14, y0 + alto), fill=acc + (255,))
    y = y0 + 60
    for ln in l_t:
        d.text((cx - d.textlength(ln, font=f_t) / 2, y), ln, font=f_t, fill=CREMA + (255,))
        y += f_t.size * 1.08
    if sub:
        y += 40
        for ln in l_s:
            d.text((cx - d.textlength(ln, font=f_s) / 2, y), ln, font=f_s, fill=(214, 219, 226, 255))
            y += f_s.size * 1.3
    img.save(out)

def etiqueta(texto, out):
    """v2: la etiqueta baja de y=150 a y=215 (el buscador de TikTok se come los primeros 200 px) y la línea
    de marca + WhatsApp sube de y=1770 a y=1470, sobre el bloque de copy. Ambas con caja opaca detrás:
    con caja sobrevive el 100% del texto al 25% de escala; con contorno solo, el 29%."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f_e = fuente(F_BOLD, 34)
    w_e = d.textlength(texto, font=f_e)
    d.rounded_rectangle((SX0, 215, SX0 + w_e + 44, 215 + 66), 8, fill=(16, 16, 16, 220))
    d.text((SX0 + 22, 227), texto, font=f_e, fill=(235, 235, 235, 255))
    f_m = fuente(F_BOLD, 40)
    marca = MARCA + "  ·  WhatsApp " + TEL
    w_m = d.textlength(marca, font=f_m)
    d.rounded_rectangle((SX0, 1470, min(SX0 + w_m + 44, SX1), 1470 + 72), 8, fill=(16, 16, 16, 220))
    d.text((SX0 + 22, 1484), marca, font=f_m, fill=LATON + (255,))
    img.save(out)

def main(pj, salida):
    p = json.load(open(pj))
    total = dur(p["voz"]) + 0.4
    shots = p["shots"]; n = len(shots); d = total / n
    os.makedirs("_e", exist_ok=True)
    for k, s in enumerate(shots):
        escena(s, d, f"_e/s{k:02d}.mp4", k)
    open("_e/lista.txt", "w").write("".join(f"file 's{k:02d}.mp4'\n" for k in range(n)))
    sh('ffmpeg -y -hide_banner -loglevel error -f concat -safe 0 -i _e/lista.txt -c copy _e/video.mp4')
    # capas: etiqueta permanente + placas por tiempo + karaoke
    etiqueta(p.get("etiqueta", "DRAMATIZACIÓN"), "_e/etq.png")
    inputs = f'-i _e/video.mp4 -i "{p["voz"]}" -i _e/etq.png'
    fc = "[0:v][2:v]overlay=0:0:format=auto[v0]"; last = "v0"; idx = 3
    for i, pl in enumerate(p.get("placas", [])):
        placa(p.get("materia", "laboral"), pl["titulo"], pl.get("sub", ""), f"_e/pl{i}.png")
        inputs += f' -i _e/pl{i}.png'
        fc += f";[{last}][{idx}:v]overlay=0:0:format=auto:enable='between(t,{pl['t0']},{pl['t1']})'[v{idx}]"
        last = f"v{idx}"; idx += 1
    if p.get("subs") and os.path.exists(p["subs"]):
        fc += f";[{last}]ass={p['subs']}[vs]"; last = "vs"
    fc += f";[1:a]apad,atrim=0:{total:.3f},loudnorm=I=-14:TP=-1.5:LRA=11[a]"
    sh(f'ffmpeg -y -hide_banner -loglevel error {inputs} -filter_complex "{fc}" -map "[{last}]" -map "[a]" '
       f'-c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -c:a aac -b:a 160k -shortest -movflags +faststart "{salida}"')
    print("OK", salida, round(dur(salida), 2), "s", n, "planos de", round(d, 2), "s")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
