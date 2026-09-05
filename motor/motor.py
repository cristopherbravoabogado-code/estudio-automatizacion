#!/usr/bin/env python3
"""motor.py — motor de video en la nube del Estudio Jurídico San Bernardo.
Uso: python3 motor.py pieza.json salida.mp4
pieza.json: {id, materia, gancho, puntos:[{t,d} x3], cierre, voz:"voz.mp3", hook:"hook.jpg|hook.mp4",
             subs:"voz.ass" (opcional, v2: karaoke de videolab/karaoke.py), tramos:[t0..t5] (opcional, v2: de videolab/voz.py)}
v1: la voz es UNA narración completa con pausas (<break>) entre los 5 tramos; se parte por silencios.
v2 (05/09/2026): si viene "tramos" se corta exacto; si viene "subs" se quema el karaoke desde el fin del gancho y las láminas llevan solo título.
"""
import json, subprocess, sys, os, re, math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
FPS = 30
F_HEAD = "/usr/share/fonts/truetype/higgsfield/Montserrat-ExtraBold.ttf"
F_BODY = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
F_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
TINTA = (20, 32, 46)
CREMA = (244, 241, 233)
LATON = (168, 135, 78)
ACENTO = {  # color de materia
    "penal": (176, 58, 50), "laboral": (204, 140, 30), "familia": (120, 80, 170),
    "civil": (40, 130, 130), "consumidor": (220, 110, 40), "transito": (50, 100, 190),
    "previsional": (60, 140, 80), "salud": (40, 150, 170),
}
TEL = "+56 9 9690 5994"
MARCA = "ESTUDIO JURÍDICO SAN BERNARDO"


def sh(cmd, check=True):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if check and r.returncode != 0:
        print(r.stderr[-3000:], file=sys.stderr)
        raise SystemExit(f"fallo: {cmd[:120]}")
    return r


def dur(path):
    r = sh(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{path}"')
    return float(r.stdout.strip())


def silencios(path, ruido=-35, minimo=0.55):
    r = sh(f'ffmpeg -hide_banner -i "{path}" -af silencedetect=noise={ruido}dB:d={minimo} -f null - 2>&1', check=False)
    ini = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r.stdout + r.stderr)]
    fin = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r.stdout + r.stderr)]
    return list(zip(ini, fin[: len(ini)]))


def cortes(voz, textos):
    """Devuelve 5 límites de escena [t0..t5] a partir de los silencios de la voz."""
    total = dur(voz)
    gaps = [(a, b) for a, b in silencios(voz) if a > 0.3 and b < total - 0.3]
    gaps.sort(key=lambda g: g[1] - g[0], reverse=True)
    gaps = sorted(gaps[:4], key=lambda g: g[0])
    if len(gaps) == 4:
        mids = [(a + b) / 2 for a, b in gaps]
    else:  # respaldo: proporcional al largo del texto
        n = [len(t) for t in textos]
        acc, mids = 0, []
        for k in n[:-1]:
            acc += k
            mids.append(total * acc / sum(n))
    return [0.0] + mids + [total + 0.5]


def fuente(path, tam):
    return ImageFont.truetype(path, tam)


def envolver(draw, texto, f, ancho):
    palabras, lineas, linea = texto.split(), [], ""
    for p in palabras:
        prueba = (linea + " " + p).strip()
        if draw.textlength(prueba, font=f) <= ancho:
            linea = prueba
        else:
            if linea:
                lineas.append(linea)
            linea = p
    if linea:
        lineas.append(linea)
    return lineas


def bloque(draw, texto, path, tam_max, ancho, max_lineas, tam_min=40):
    """Elige el tamaño más grande que cabe en max_lineas. Devuelve (fuente, lineas)."""
    tam = tam_max
    while tam >= tam_min:
        f = fuente(path, tam)
        ls = envolver(draw, texto, f, ancho)
        if len(ls) <= max_lineas:
            return f, ls
        tam -= 4
    f = fuente(path, tam_min)
    return f, envolver(draw, texto, f, ancho)[:max_lineas]


def pintar_lineas(draw, lineas, f, y, color, interlinea=1.12, sombra=True, ancla="centro"):
    alto = f.size * interlinea
    for ln in lineas:
        w = draw.textlength(ln, font=f)
        x = (W - w) / 2 if ancla == "centro" else 90
        if sombra:
            draw.text((x + 3, y + 4), ln, font=f, fill=(0, 0, 0, 160))
        draw.text((x, y), ln, font=f, fill=color)
        y += alto
    return y


def fondo(materia):
    """Fondo tinta con un resplandor del color de la materia y un filete latón."""
    acc = ACENTO.get(materia, LATON)
    img = Image.new("RGB", (W, H), TINTA)
    glow = Image.new("RGB", (W, H), TINTA)
    g = ImageDraw.Draw(glow)
    g.ellipse((-300, H * 0.45, W + 300, H * 1.35), fill=tuple(int(TINTA[i] * 0.55 + acc[i] * 0.45) for i in range(3)))
    glow = glow.filter(ImageFilter.GaussianBlur(220))
    img = Image.blend(img, glow, 0.85)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 14), fill=acc)
    return img


def cabecera(d, materia, k):
    acc = ACENTO.get(materia, LATON)
    f = fuente(F_BOLD, 34)
    etiqueta = materia.upper()
    d.text((90, 150), etiqueta, font=f, fill=acc)
    # puntos de progreso (5 escenas)
    for i in range(5):
        x = W - 90 - (4 - i) * 34
        d.ellipse((x - 9, 158, x + 9, 176), fill=CREMA if i <= k else (90, 100, 115))


def pie(d):
    f1 = fuente(F_BOLD, 30)
    f2 = fuente(F_BODY, 30)
    d.text((90, H - 300), MARCA, font=f1, fill=LATON)
    d.text((90, H - 255), f"WhatsApp {TEL}  ·  1ª consulta gratis", font=f2, fill=(200, 206, 214))
    d.text((90, H - 200), "Información general, no reemplaza asesoría", font=fuente(F_BODY, 24), fill=(120, 130, 142))


def lamina_punto(materia, k, titulo, detalle, out):
    img = fondo(materia)
    d = ImageDraw.Draw(img)
    cabecera(d, materia, k)
    f_t, l_t = bloque(d, titulo, F_HEAD, 96, W - 180, 3, 56)
    f_d, l_d = bloque(d, detalle, F_BODY, 50, W - 180, 5, 34) if detalle else (None, [])
    alto = len(l_t) * f_t.size * 1.12 + 50 + (len(l_d) * f_d.size * 1.3 if detalle else 0)
    y = H * 0.5 - alto / 2 - (120 if not detalle else 0)  # v2 (solo título): sube para dejar sitio al karaoke
    y = pintar_lineas(d, l_t, f_t, y, CREMA, sombra=False, ancla="izq")
    d.rectangle((90, y + 14, 90 + 140, y + 20), fill=ACENTO.get(materia, LATON))
    if detalle:
        pintar_lineas(d, l_d, f_d, y + 50, (214, 219, 226), 1.3, sombra=False, ancla="izq")
    pie(d)
    img.save(out)


def lamina_cierre(materia, cierre, out):
    img = fondo(materia)
    d = ImageDraw.Draw(img)
    cabecera(d, materia, 4)
    f_c, l_c = bloque(d, cierre, F_HEAD, 84, W - 180, 4, 52)
    y = H * 0.36
    y = pintar_lineas(d, l_c, f_c, y, CREMA, sombra=False, ancla="izq")
    y += 60
    d.rectangle((90, y, W - 90, y + 4), fill=LATON)
    y += 50
    d.text((90, y), MARCA, font=fuente(F_HEAD, 46), fill=LATON)
    y += 80
    d.text((90, y), "1ª consulta presencial GRATIS", font=fuente(F_BOLD, 44), fill=CREMA)
    y += 80
    d.text((90, y), f"WhatsApp {TEL}", font=fuente(F_HEAD, 56), fill=CREMA)
    y += 90
    d.text((90, y), "Pasaje Juan Rau 611, San Bernardo", font=fuente(F_BODY, 34), fill=(200, 206, 214))
    d.text((90, H - 200), "Información general, no reemplaza asesoría", font=fuente(F_BODY, 24), fill=(120, 130, 142))
    img.save(out)


def overlay_gancho(materia, gancho, out):
    """Capa RGBA: velo oscuro arriba y abajo + gancho grande en el tercio inferior + rótulo."""
    acc = ACENTO.get(materia, LATON)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i in range(1100):  # velo inferior: arranca a H*0.43 y llega a 230 de alfa
        a = int(230 * (i / 1100) ** 1.1)
        d.line((0, H - 1100 + i, W, H - 1100 + i), fill=(8, 12, 18, a))
    for i in range(320):  # velo superior
        a = int(150 * (1 - i / 320) ** 1.6)
        d.line((0, i, W, i), fill=(8, 12, 18, a))
    d.rounded_rectangle((90, 150, 90 + 300, 150 + 52), 8, fill=(0, 0, 0, 140))
    d.text((112, 158), "DRAMATIZACIÓN", font=fuente(F_BOLD, 28), fill=(230, 230, 230, 255))
    f, ls = bloque(d, gancho, F_HEAD, 104, W - 160, 4, 60)
    alto = len(ls) * f.size * 1.08
    y = H * 0.78 - alto
    d.rectangle((80, y - 6, 80 + 16, y + alto - 10), fill=acc + (255,))
    for ln in ls:
        d.text((118, y), ln, font=f, fill=(255, 255, 255, 255), stroke_width=5, stroke_fill=(8, 12, 18, 235))
        y += f.size * 1.08
    d.text((118, H * 0.78 + 30), MARCA, font=fuente(F_BOLD, 30), fill=LATON + (255,))
    img.save(out)


def escena_gancho(hook, overlay, d0, out):
    frames = int(d0 * FPS) + 1
    if hook.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        vf = (f"scale=2160:3840:force_original_aspect_ratio=increase,crop=2160:3840,"
              f"zoompan=z='min(1.0+0.00075*on,1.14)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s={W}x{H}:fps={FPS}")
        src = f'-loop 1 -i "{hook}"'
    else:
        vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}"
        src = f'-stream_loop -1 -i "{hook}"'
    sh(f'ffmpeg -y -hide_banner -loglevel error {src} -i "{overlay}" -filter_complex '
       f'"[0:v]{vf}[b];[b][1:v]overlay=0:0:format=auto,format=yuv420p" -t {d0:.3f} -an '
       f'-c:v libx264 -preset veryfast -crf 20 -r {FPS} "{out}"')


def escena_lamina(png, dseg, out, k):
    frames = int(dseg * FPS) + 1
    z = "min(1.0+0.0005*on,1.06)" if k % 2 == 0 else "max(1.06-0.0005*on,1.0)"
    sh(f'ffmpeg -y -hide_banner -loglevel error -loop 1 -i "{png}" -filter_complex '
       f'"[0:v]scale=2160:3840,zoompan=z=\'{z}\':x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':d={frames}:s={W}x{H}:fps={FPS},'
       f'fade=t=in:st=0:d=0.25,format=yuv420p" -t {dseg:.3f} -an -c:v libx264 -preset veryfast -crf 20 -r {FPS} "{out}"')


def filtrar_ass(src, dst, desde):
    """v2: deja fuera las líneas karaoke que empiezan antes de `desde` (el gancho ya muestra su texto grande)."""
    def seg(ts):
        h, m_, s = ts.split(":")
        return int(h) * 3600 + int(m_) * 60 + float(s)
    out = []
    for ln in open(src, encoding="utf-8"):
        if ln.startswith("Dialogue:") and seg(ln.split(",")[1]) < desde:
            continue
        out.append(ln)
    open(dst, "w", encoding="utf-8").write("".join(out))


def main(pj, salida):
    p = json.load(open(pj))
    m = p["materia"]
    subs = p.get("subs")  # v2: ruta a .ass de videolab/karaoke.py; si existe, las láminas llevan solo título
    textos = [p["gancho"]] + [q["t"] + " " + q["d"] for q in p["puntos"]] + [p["cierre"]]
    if p.get("tramos") and len(p["tramos"]) == 6:  # v2: límites exactos que entrega videolab/voz.py
        t = list(p["tramos"]); t[-1] = dur(p["voz"]) + 0.5
    else:
        t = cortes(p["voz"], textos)
    d = [t[i + 1] - t[i] for i in range(5)]
    print("tramos:", [round(x, 2) for x in d], "total", round(t[-1], 2))
    os.makedirs("_e", exist_ok=True)
    overlay_gancho(m, p["gancho"], "_e/ov.png")
    escena_gancho(p["hook"], "_e/ov.png", d[0], "_e/e0.mp4")
    for k, q in enumerate(p["puntos"], start=1):
        lamina_punto(m, k, q["t"], "" if subs else q["d"], f"_e/l{k}.png")
        escena_lamina(f"_e/l{k}.png", d[k], f"_e/e{k}.mp4", k)
    lamina_cierre(m, p["cierre"], "_e/l4.png")
    escena_lamina("_e/l4.png", d[4], "_e/e4.mp4", 4)
    open("_e/lista.txt", "w").write("".join(f"file 'e{k}.mp4'\n" for k in range(5)))
    sh('ffmpeg -y -hide_banner -loglevel error -f concat -safe 0 -i _e/lista.txt -c copy _e/video.mp4')
    # audio: voz + ambiente del clip si el gancho es video
    amb = ""
    filtro = "[1:a]apad,atrim=0:{T},loudnorm=I=-14:TP=-1.5:LRA=11[a]".format(T=t[-1])
    if not p["hook"].lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        amb = f' -stream_loop -1 -i "{p["hook"]}"'
        filtro = (f"[2:a]volume=0.35,atrim=0:{d[0]:.3f},afade=t=out:st={max(d[0]-0.8,0):.3f}:d=0.8,apad[amb];"
                  f"[1:a]apad,atrim=0:{t[-1]:.3f}[v];[v][amb]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
    video = "-map 0:v -c:v copy"
    if subs and os.path.exists(subs):
        filtrar_ass(subs, "_e/subs.ass", d[0])
        video = "-map \"[vs]\" -c:v libx264 -preset veryfast -crf 20"
        filtro = "[0:v]ass=_e/subs.ass[vs];" + filtro
    sh(f'ffmpeg -y -hide_banner -loglevel error -i _e/video.mp4 -i "{p["voz"]}"{amb} -filter_complex "{filtro}" '
       f'{video} -map "[a]" -c:a aac -b:a 160k -shortest -movflags +faststart "{salida}"')
    print("OK", salida, round(dur(salida), 2), "s")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
