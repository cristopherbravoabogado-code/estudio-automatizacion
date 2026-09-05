#!/usr/bin/env python3
"""F12 — QUIZ LEGAL (estructura extraída del viral-02, estilo "Neriquiz"). Sandbox de Higgsfield, US$0.

Uso:  python3 quiz.py pieza.json salida.mp4
pieza.json:
{ "intro": {"titulo": "...", "sub": "...", "voz": "intro.wav"},            # opcional
  "preguntas": [ {"q": "...", "foto": "laboral.png", "op": ["A","B","C"], "ok": 1,
                  "voz_q": "q1.wav", "voz_a": "a1.wav"} , ... ],
  "cierre": {"titulo": "...", "sub": "...", "voz": "out.wav"},
  "tick_s": 3.0 }
Cada pregunta: tarjeta con efecto máquina de escribir (1 s) + voz que lee la pregunta → opciones entran una a una
→ barra de tiempo con tic-tac (tick_s) → la correcta se pinta verde + "ding" + voz que dice la respuesta.
Render: Pillow compone cuadros a 30 fps y los manda por tubería a ffmpeg (libx264). Audio: voz + efectos sintetizados con numpy.
Voces: quiz_voces.py (Kokoro). Probado 05/09/2026: 7 preguntas → 96 s, ~1 min de render en el sandbox.
"""
import sys, json, math, subprocess, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
SR = 24000
FONT_DIR = "/usr/share/fonts/truetype"
def font(size, bold=True):
    for name in (["Montserrat-ExtraBold.ttf", "Montserrat-Bold.ttf"] if bold else ["Montserrat-SemiBold.ttf", "Montserrat-Medium.ttf", "Metropolis-Medium.otf", "Montserrat-ExtraBold.ttf"]):
        for root, _, files in os.walk(FONT_DIR):
            if name in files:
                return ImageFont.truetype(os.path.join(root, name), size)
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)

BG = (246, 231, 214); TINTA = (17, 34, 64); ROJO = (214, 48, 49); VERDE = (76, 175, 80); CARD = (255, 255, 255)
ACENTO = (240, 182, 44); GRIS = (120, 120, 130)

def wrap(draw, text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def fondo():
    im = Image.new("RGB", (W, H), BG); d = ImageDraw.Draw(im)
    f = font(46)
    for y in range(-40, H, 150):
        for x in range(-40, W, 170):
            d.text((x + (y // 150 % 2) * 85, y), "§", font=f, fill=(236, 216, 196))
    d.rectangle([0, 0, W, 130], fill=TINTA)
    d.text((W // 2, 65), "TRIVIA LEGAL · SAN BERNARDO", font=font(38), fill=(255, 255, 255), anchor="mm")
    d.text((W // 2, H - 60), "Estudio Jurídico San Bernardo · primera consulta gratis · WhatsApp en la descripción", font=font(26, False), fill=TINTA, anchor="mm")
    return im

def tarjeta_pregunta(base, texto):
    im = base.copy(); d = ImageDraw.Draw(im)
    x0, y0, x1, y1 = 70, 190, W - 70, 560
    d.rounded_rectangle([x0 + 8, y0 + 10, x1 + 8, y1 + 10], 36, fill=(200, 185, 170))
    d.rounded_rectangle([x0, y0, x1, y1], 36, fill=CARD, outline=TINTA, width=6)
    f = font(50); lines = wrap(d, texto, f, x1 - x0 - 90)
    if len(lines) > 4: f = font(42); lines = wrap(d, texto, f, x1 - x0 - 90)
    lh = f.size + 14; ty = (y0 + y1) // 2 - lh * len(lines) // 2 + lh // 2
    for i, l in enumerate(lines):
        d.text((W // 2, ty + i * lh), l, font=f, fill=TINTA, anchor="mm")
    return im

def _rot_rect(w, h, ang, size):
    cx, cy = size[0] / 2, size[1] / 2; a = math.radians(ang); pts = []
    for px, py in [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]:
        pts.append((cx + px * math.cos(a) - py * math.sin(a), cy + px * math.sin(a) + py * math.cos(a)))
    return pts

def foto_marco(base, path):
    im = base.copy()
    try:
        ph = Image.open(path).convert("RGB")
    except Exception:
        ph = Image.new("RGB", (800, 600), GRIS)
    tw, th = 760, 470
    r = max(tw / ph.width, th / ph.height); ph = ph.resize((int(ph.width * r) + 1, int(ph.height * r) + 1))
    l = (ph.width - tw) // 2; t = (ph.height - th) // 2; ph = ph.crop((l, t, l + tw, t + th))
    marco = Image.new("RGB", (tw + 24, th + 24), CARD); marco.paste(ph, (12, 12))
    marco = marco.rotate(-2.5, expand=True, fillcolor=BG)
    sombra = Image.new("RGBA", marco.size, (0, 0, 0, 0)); ImageDraw.Draw(sombra).rectangle([10, 14, marco.width - 4, marco.height], fill=(0, 0, 0, 90))
    sombra = sombra.filter(ImageFilter.GaussianBlur(12))
    x = (W - marco.width) // 2; y = 590
    im.paste(sombra, (x, y), sombra)
    mask = Image.new("L", marco.size, 0); ImageDraw.Draw(mask).polygon(_rot_rect(tw + 24, th + 24, -2.5, marco.size), fill=255)
    im.paste(marco, (x, y), mask)
    return im

OPC_Y = [1230, 1400, 1570]
def opcion(base, i, texto, estado):
    """estado: 'normal' | 'ok'"""
    im = base.copy(); d = ImageDraw.Draw(im)
    y = OPC_Y[i]; x0, x1 = 90, W - 90; h = 130
    col = VERDE if estado == "ok" else CARD; letra_bg = VERDE if estado == "ok" else ROJO
    d.rounded_rectangle([x0 + 6, y - h // 2 + 8, x1 + 6, y + h // 2 + 8], 65, fill=(205, 190, 175))
    d.rounded_rectangle([x0, y - h // 2, x1, y + h // 2], 65, fill=col, outline=TINTA, width=5)
    d.ellipse([x0 - 10, y - 72, x0 + 134, y + 72], fill=letra_bg, outline=CARD, width=6)
    d.text((x0 + 62, y), "ABC"[i], font=font(70), fill=CARD, anchor="mm")
    f = font(44); lines = wrap(d, texto, f, x1 - x0 - 200)
    if len(lines) > 2: f = font(36); lines = wrap(d, texto, f, x1 - x0 - 200)
    lh = f.size + 6; ty = y - lh * (len(lines) - 1) // 2
    for k, l in enumerate(lines):
        d.text((x0 + 150 + (x1 - x0 - 150) // 2, ty + k * lh), l, font=f, fill=TINTA if estado != "ok" else CARD, anchor="mm")
    return im

def barra(im, frac):
    d = ImageDraw.Draw(im); x0, x1, y = 160, W - 160, 1150
    d.rounded_rectangle([x0, y - 16, x1, y + 16], 16, fill=(230, 225, 215), outline=TINTA, width=3)
    xe = x0 + int((x1 - x0) * frac)
    if xe > x0 + 20:
        d.rounded_rectangle([x0, y - 16, xe, y + 16], 16, fill=ACENTO)
        for s in range(x0, xe, 40):
            d.polygon([(s, y - 13), (s + 16, y - 13), (s + 4, y + 13), (s - 12, y + 13)], fill=(255, 210, 100))
    return im

def placa(base, titulo, sub):
    im = base.copy(); d = ImageDraw.Draw(im)
    d.rounded_rectangle([80, 640, W - 80, 1280], 40, fill=TINTA)
    d.rectangle([80, 640, 104, 1280], fill=ACENTO)
    f = font(66); lines = wrap(d, titulo, f, W - 260); lh = 84; ty = 780
    for i, l in enumerate(lines): d.text((W // 2, ty + i * lh), l, font=f, fill=CARD, anchor="mm")
    f2 = font(40, False); lines2 = wrap(d, sub, f2, W - 260); ty = 780 + lh * len(lines) + 60
    for i, l in enumerate(lines2): d.text((W // 2, ty + i * 54), l, font=f2, fill=(230, 230, 235), anchor="mm")
    return im

# ---------- audio ----------
def wav_dur(p):
    try:
        return float(subprocess.run(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{p}"', shell=True, capture_output=True, text=True).stdout.strip())
    except Exception:
        return 0.0
def load(p):
    if not p or not os.path.exists(p): return np.zeros(0, np.float32)
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32)
def tono(f, dur, vol=0.5, decay=6.0):
    t = np.arange(int(SR * dur)) / SR
    return (vol * np.sin(2 * math.pi * f * t) * np.exp(-decay * t)).astype(np.float32)
def tick(dur):
    out = np.zeros(int(SR * dur), np.float32)
    n = int(dur / 0.5)
    for k in range(n):
        s = int(k * 0.5 * SR); c = tono(1500 + 60 * k, 0.05, 0.35, 60)
        out[s:s + len(c)] += c[:len(out) - s]
    return out
def ding():
    return tono(880, 0.9, 0.5, 4) + tono(1320, 0.9, 0.3, 5) + tono(1760, 0.9, 0.15, 8)
def whoosh(dur=0.25):
    n = int(SR * dur); noise = np.random.randn(n).astype(np.float32) * 0.15
    env = np.sin(np.linspace(0, math.pi, n)) ** 2
    return (noise * env).astype(np.float32)

# ---------- plan ----------
def plan(p):
    """Devuelve la línea de tiempo: lista de eventos con cuadros y la pista de audio."""
    ev = []; t = 0.0; audio = []
    def put(a, at): audio.append((at, a))
    if p.get("intro"):
        d = max(wav_dur(p["intro"].get("voz", "")) + 0.4, 2.5)
        ev.append(("intro", t, t + d)); put(load(p["intro"].get("voz")), t + 0.2); t += d
    T = float(p.get("tick_s", 3.0))
    for i, q in enumerate(p["preguntas"]):
        vq = load(q.get("voz_q")); va = load(q.get("voz_a"))
        dq = len(vq) / SR; da = len(va) / SR
        t0 = t
        put(whoosh(), t0); put(vq, t0 + 0.25)
        t_ops = max(1.1, dq * 0.5)                    # opciones entran mientras habla
        t_bar = max(t_ops + 1.4, dq + 0.3)            # barra parte cuando termina la voz
        put(tick(T), t0 + t_bar)
        t_rev = t_bar + T
        put(ding(), t0 + t_rev); put(va, t0 + t_rev + 0.5)
        dur = t_rev + max(da + 0.6, 1.5)
        ev.append(("q", t0, t0 + dur, i, t_ops, t_bar, t_rev)); t = t0 + dur
    if p.get("cierre"):
        d = max(wav_dur(p["cierre"].get("voz", "")) + 0.6, 3.0)
        ev.append(("cierre", t, t + d)); put(load(p["cierre"].get("voz")), t + 0.2); t += d
    total = t + 0.3
    mix = np.zeros(int(SR * total) + SR, np.float32)
    for at, a in audio:
        s = int(at * SR); n = min(len(a), len(mix) - s)
        if n > 0: mix[s:s + n] += a[:n]
    return ev, total, mix

def render(p, out):
    ev, total, mix = plan(p)
    import soundfile as sf
    sf.write("_quiz_mix.wav", np.clip(mix, -1, 1), SR)
    base = fondo()
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", "_quiz_mix.wav", "-af", "loudnorm=I=-15:TP=-1.5:LRA=11", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "128k", "-shortest", "-movflags", "+faststart", out]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    nframes = int(total * FPS)
    cache = {}
    for e in ev:
        if e[0] == "q":
            q = p["preguntas"][e[3]]
            b = foto_marco(base, q["foto"])
            full = tarjeta_pregunta(b, q["q"])
            ops = full
            for k in range(3): ops = opcion(ops, k, q["op"][k], "normal")
            rev = full
            for k in range(3): rev = opcion(rev, k, q["op"][k], "ok" if k == q["ok"] else "normal")
            cache[e[3]] = {"full": full, "ops": ops, "rev": rev,
                           "typ": [tarjeta_pregunta(b, q["q"][:int(len(q["q"]) * j / 12)] + ("|" if j < 12 else "")) for j in range(1, 13)]}
    intro = placa(base, p["intro"]["titulo"], p["intro"].get("sub", "")) if p.get("intro") else None
    cierre = placa(base, p["cierre"]["titulo"], p["cierre"].get("sub", "")) if p.get("cierre") else None
    for n in range(nframes):
        t = n / FPS; fr = base
        for e in ev:
            if e[1] <= t < e[2]:
                rel = t - e[1]
                if e[0] == "intro": fr = intro; break
                if e[0] == "cierre": fr = cierre; break
                c = cache[e[3]]; _, t0, t1, i, t_ops, t_bar, t_rev = e
                if rel < 1.0:
                    fr = c["typ"][min(11, int(rel * 12))]
                elif rel < t_rev:
                    nops = min(3, int((rel - t_ops) / 0.4) + 1) if rel >= t_ops else 0
                    if nops == 3: fr = c["ops"]
                    elif nops > 0:
                        fr = c["full"]
                        for k in range(nops): fr = opcion(fr, k, p["preguntas"][i]["op"][k], "normal")
                    else: fr = c["full"]
                    if rel >= t_bar:
                        fr = barra(fr.copy(), min(1.0, (rel - t_bar) / float(p.get("tick_s", 3.0))))
                else:
                    fr = barra(c["rev"].copy(), 1.0)
                break
        ff.stdin.write(fr.tobytes())
    ff.stdin.close(); ff.wait()
    print(f"QUIZ_OK dur={total:.1f}s preguntas={len(p['preguntas'])} out={out}")

if __name__ == "__main__":
    p = json.load(open(sys.argv[1])); render(p, sys.argv[2])
