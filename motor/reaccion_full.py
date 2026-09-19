#!/usr/bin/env python3
"""reaccion_full.py v1.1 (17/09/2026) - formato F15 REACCION FULL.
Pedido de Cristopher (17/09): toda la duracion con VIDEO VERTICAL de la noticia (sin lamina, sin
clip horizontal), narracion encima que comenta la noticia, delitos, penas y cierre con CTA.
Uso: python3 reaccion_full.py clip.mp4 voz.mp3 subs.ass salida.mp4 "TAG SUPERIOR" "credito"
Recorta el clip 16:9 a 9:16 (escala a 1920 de alto, ventana de 1080 con paneo lento), lo pasa dos
veces ralentizado para cubrir la voz, tapa el cintillo del canal con un pie oscuro (bajo la zona
segura, donde va la UI de TikTok), mete rotulo propio arriba, CTA al final y el karaoke de karaoke.py.
v1.1: el rotulo lleva caja propia (drawtext box) para que el ancho siga al texto -con drawbox fijo el
"VIRAL ARGENTINO / VALE EN CHILE?" se salia de la caja- y la linea del WhatsApp del CTA baja a 24 px:
con 28 px media ~900 px y pantalla_chica.py contaba 21 cajas propias fuera del borde derecho (930).
Regla: el TAG cabe en ~20 caracteres ("ESTO VALE EN CHILE?"); lo largo va al credito. La cama del
audio ajeno queda en 0.032 (~-30 dB): con 0.045 las uniones median -34.4 dBFS y no pasaban el tope -35.
El clip puede ser una concatenacion de clips de Mixkit (16:9, 30 fps, pista muda) cuando no hay clip de
prensa utilizable: ver motor/lotes/1000_guion.txt (pieza 1000, clips 48973 + 12877 + 49020).
"""
import json, os, subprocess, sys
clip, voz, ass, out, tag, cred = sys.argv[1:7]
# 7o argumento opcional: el TITULAR REAL de la noticia, que se muestra los primeros segundos.
#
# POR QUE (19/09/2026, pedido de Cristopher): "no tiene clip de noticias reales, que es lo que
# llama la atencion". Tiene razon en el diagnostico. Lo que NO se hace aqui es bajar el metraje
# del noticiero: el CDN de los medios devuelve 403 a toda descarga y solo cede si un navegador
# reproduce el video, o sea hay que saltarse un control de acceso puesto a proposito para
# republicar material ajeno bajo la marca del estudio. Para un abogado eso es exposicion, no
# una optimizacion.
#
# Lo que SI se puede: abrir con el TITULAR y el MEDIO, citados y atribuidos. Un titular es un
# hecho y citarlo con su fuente es practica periodistica corriente. Y va donde decide la
# retencion: los tres primeros segundos.
titular = sys.argv[7] if len(sys.argv) > 7 else ""

# EL PIE NEGRO SOLO SI HAY CINTILLO QUE TAPAR (19/09/2026)
# Las dos franjas oscuras del final existen, en palabras del docstring original, para "tapar el
# cintillo del canal". Con un clip de noticiero eso es imprescindible. Con metraje de archivo no
# hay cintillo que tapar y esas franjas se comen un QUINTO de la pantalla: medido en el fotograma
# del segundo 12 de la pieza 1201, la imagen muere en y=1545 de 1920 y debajo queda un bloque
# negro que hace parecer la pieza un repost recortado. Se controla con REACCION_PIE (1 por
# defecto, 0 cuando el clip no trae cintillo).
PIE = os.environ.get("REACCION_PIE", "1") != "0"

# LA FUENTE, RESUELTA Y NO SUPUESTA (19/09/2026)
# Hasta hoy FONT era una ruta fija del sandbox de Higgsfield. Al conectar este formato a la
# cadena automatica quedo a la vista: en un runner de GitHub Actions esa carpeta NO existe, y
# ffmpeg no avisa "falta la fuente" - falla el drawtext entero y la pieza muere sin decir por
# que. Ahora se busca en varios sitios y, si no hay ninguna, se dice con todas sus letras.
CANDIDATAS = [os.environ.get("REACCION_FONT", ""),
              "/usr/share/fonts/truetype/higgsfield/Montserrat-ExtraBold.ttf",
              "fonts/Montserrat-ExtraBold.ttf",
              "Montserrat-ExtraBold.ttf",
              "/usr/share/fonts/truetype/montserrat/Montserrat-ExtraBold.ttf",
              "fonts/Poppins-Bold.ttf"]
FONT = next((f for f in CANDIDATAS if f and os.path.exists(f)), None)
if not FONT:
    print("SIN_FUENTE: no se encontro Montserrat-ExtraBold.ttf en ninguna de estas rutas: "
          + " | ".join(f for f in CANDIDATAS if f))
    sys.exit(2)
def dur(f):
    return float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f]).decode().strip())
V = dur(voz); C = dur(clip)
LEAD = 0.5                      # la voz entra a los 0,5 s
COLA = 1.3                      # cola con el CTA visible

# LA DURACION DEJA DE SER UNA LOTERIA (19/09/2026)
# Primera tanda real de diez piezas F15: las cuatro que pasaron midieron 22,73 · 23,14 · 23,28
# y 23,57 s, contra el minimo de 22,0 de control.py. TODAS al borde. Las otras cinco cayeron
# por "duracion" quedando apenas por debajo. Y el largo no se puede predecir escribiendo mas
# palabras: una pieza de 36 palabras dio 23,28 s y una de 51 dio 22,73, porque lo que manda son
# los silencios que voz.py pone entre los cinco tramos, no el texto.
#
# Una pieza no puede morir por dos decimas despues de haber gastado el render entero. Si la
# narracion queda corta, se alarga la cola con el CTA en pantalla -que es tiempo util, no
# relleno- hasta entrar en la franja. Pero con tope: si hace falta estirar mas de PAD_MAX, el
# guion es DEMASIADO corto y eso hay que arreglarlo escribiendo, no estirando. Ahi se para con
# un mensaje que lo dice.
T_MIN = float(os.environ.get("REACCION_T_MIN", "23.0"))   # con holgura sobre el minimo de 22,0
T_MAX = float(os.environ.get("REACCION_T_MAX", "34.0"))   # el maximo de control.py
PAD_MAX = 4.0
T_nat = LEAD + V + COLA
T = round(min(max(T_nat, T_MIN), T_nat + PAD_MAX), 2)
if T < T_MIN:
    print("GUION_CORTO: la narracion dura %.2f s y la pieza sale en %.2f s, bajo el minimo de "
          "%.1f s incluso estirando la cola %.1f s. Alarga el guion: no se estira mas."
          % (V, T, T_MIN, PAD_MAX))
    sys.exit(3)
if T > T_MAX:
    print("GUION_LARGO: la narracion dura %.2f s y la pieza sale en %.2f s, sobre el maximo de "
          "%.1f s. Acorta el guion." % (V, T, T_MAX))
    sys.exit(4)
s1 = 0.82; s2 = 0.75; a = 1.5; b = min(C, 13.0)
d1 = C / s1; d2 = (b - a) / s2
s3 = 0.7 if d1 + d2 < T + 0.5 else None
XF = 0.6
def vpass(i, ss, to, s, label, zoom=False):
    z = ",scale=1188:2112,crop=1080:1920:54+30*sin(t/3):96+20*sin(t/4)" if zoom else ""
    return (f"[0:v]trim=start={ss}:end={to},setpts=(PTS-STARTPTS)/{s},"
            f"scale=-2:1920:flags=lanczos,crop=1080:1920:x='(iw-1080)/2+220*sin(2*PI*t/16+{i})':y=0"
            f"{z},fps=30,format=yuv420p[{label}]")
def apass(ss, to, s, label):
    return f"[0:a]atrim=start={ss}:end={to},asetpts=PTS-STARTPTS,atempo={s},aresample=48000[{label}]"
fc = [vpass(0, 0, C, s1, "v1"), vpass(1, a, b, s2, "v2", zoom=True), apass(0, C, s1, "a1"), apass(a, b, s2, "a2")]
if s3:
    fc += [vpass(2, 0, C, s3, "v3"), apass(0, C, s3, "a3"),
           f"[v1][v2]xfade=transition=fade:duration={XF}:offset={d1-XF:.3f}[v12]",
           f"[v12][v3]xfade=transition=fade:duration={XF}:offset={d1+d2-2*XF:.3f}[vv]",
           f"[a1][a2]acrossfade=d={XF}[a12]", f"[a12][a3]acrossfade=d={XF}[aa]"]
else:
    fc += [f"[v1][v2]xfade=transition=fade:duration={XF}:offset={d1-XF:.3f}[vv]",
           f"[a1][a2]acrossfade=d={XF}[aa]"]
esc = lambda s: s.replace("\\","\\\\").replace(":", "\\:").replace("'", "\\\\\\'").replace("%","\\%")

# El titular se parte a mano: drawtext no hace saltos de linea y un titular largo se sale de la
# zona segura. 30 caracteres por linea con fuente de 52 px cabe en los 900 px de la caja.
def _partir(s, ancho=26, maxlin=3):
    palabras, lineas, actual = s.split(), [], ""
    for w in palabras:
        if len(actual) + len(w) + 1 > ancho and actual:
            lineas.append(actual); actual = w
            if len(lineas) == maxlin: break
        else:
            actual = (actual + " " + w).strip()
    if actual and len(lineas) < maxlin: lineas.append(actual)
    return lineas or [""]

TIT_LINEAS = _partir(titular) if titular else []
TIT_T = 4.2                                    # segundos con la tarjeta en pantalla
TIT_Y = 610                                    # arriba del karaoke, dentro de la zona segura
TIT_H = len(TIT_LINEAS) * 60 + 84
cta_in = LEAD + V - 6.0
tx = (f"[vv]trim=0:{T},setpts=PTS-STARTPTS,"
      # rotulo propio arriba, dentro de la zona segura (x 130-925, y >= 245)
      f"drawtext=fontfile={FONT}:text='{esc(tag)}':fontsize=40:fontcolor=white:x=130:y=272:"
      f"box=1:boxcolor=0xE5261F@0.92:boxborderw=16,"
      # El credito va ARRIBA solo si no hay tarjeta: con tarjeta ya aparece dentro de ella y
      # repetirlo dos veces en los mismos 4 segundos se ve como un error. (Medido en el
      # fotograma del segundo 2 de la pieza 1201.)
      + ((f"drawtext=fontfile={FONT}:text='{esc(cred)}':fontsize=26:fontcolor=white@0.85:"
          f"x=130:y=348:shadowcolor=black@0.7:shadowx=2:shadowy=2,") if not titular else "")
      # CTA final sobre las palabras del cierre (y 1080-1230, encima del karaoke)
      + f"drawbox=x=130:y=1080:w=795:h=150:color=0x101010@0.86:t=fill:enable='gte(t,{cta_in:.2f})',"
      f"drawtext=fontfile={FONT}:text='¿Necesitas asesoría? Escríbenos':fontsize=40:fontcolor=0xFFE500:"
      f"x=(1080-tw)/2:y=1102:enable='gte(t,{cta_in:.2f})',"
      f"drawtext=fontfile={FONT}:text='WhatsApp +56 9 9690 5994 · Estudio Jurídico San Bernardo':fontsize=24:"
      f"fontcolor=white:x=(1080-tw)/2:y=1168:enable='gte(t,{cta_in:.2f})',"
      # pie oscuro: tapa el cintillo y el ticker del canal (bajo la zona segura, y >= 1545)
      # TARJETA DE TITULAR los primeros segundos: filete rojo de prensa + el titular + el
      # medio y la fecha. Medidas pegadas a la zona segura de ZONA-SEGURA-v5 (x 95-930):
      # caja 110..922, texto desde x=130 con fuente de 46 px y 26 caracteres por linea, que
      # da ~650 px de ancho y termina cerca de 780. Asi pantalla_chica.py no cuenta cajas fuera.
      + ((f"drawbox=x=110:y=markY:w=812:h=markH:color=0x0B0B0B@0.90:t=fill:"
          f"enable='lt(t,{TIT_T})',"
          f"drawbox=x=110:y=markY:w=9:h=markH:color=0xE5261F:t=fill:enable='lt(t,{TIT_T})',"
          + "".join(
            f"drawtext=fontfile={FONT}:text='{esc(l)}':fontsize=46:fontcolor=white:"
            f"x=130:y={TIT_Y + 30 + k * 60}:enable='lt(t,{TIT_T})',"
            for k, l in enumerate(TIT_LINEAS))
          + f"drawtext=fontfile={FONT}:text='{esc(cred)}':fontsize=28:fontcolor=0xFFE500:"
            f"x=130:y={TIT_Y + 30 + len(TIT_LINEAS) * 60 + 14}:enable='lt(t,{TIT_T})',"
         ).replace("markY", str(TIT_Y)).replace("markH", str(TIT_H)) if titular else "")
      + ((f"drawbox=x=0:y=1545:w=1080:h=45:color=black@0.55:t=fill,"
          f"drawbox=x=0:y=1590:w=1080:h=330:color=black@0.94:t=fill,") if PIE else "")
      + f"ass={ass}[vout]")
fc.append(tx)
# audio: noticia audible 1,2 s, luego cama a -30 dB (0.032, bajo el tope de uniones de control.py);
# voz encima con 0,5 s de entrada; loudnorm al final
fc.append(f"[aa]atrim=0:{T},asetpts=PTS-STARTPTS,"
          f"volume='if(lt(t,1.2),0.55,max(0.032,0.55-0.518*(t-1.2)/1.0))':eval=frame[news]")
fc.append(f"[1:a]adelay={int(LEAD*1000)}|{int(LEAD*1000)},aresample=48000[vz]")
# LOUDNESS: I=-11, y la tercera medicion del dia es la que manda (19/09/2026).
#
# -16 era el original. Se subio a -14 al ver que el volumen medio quedaba a 0,1 dB del piso de
# control.py. Con -14 la pieza mide exactamente -14,23 LUFS, que es el objetivo "correcto" de
# plataforma... y Cristopher igual tuvo que poner el telefono al 100% para oirla normal.
#
# Tenia razon el, no el estandar. TikTok NORMALIZA HACIA ABAJO lo que llega mas fuerte que su
# objetivo, pero no sube lo que llega mas bajo: masterizar justo en -14 deja la pieza en el
# piso, y fuera de la app -al revisarla en el telefono, al mandarla por WhatsApp- se oye casi
# nada. Por eso -11, como la mayoria del contenido corto: dentro de TikTok suena igual porque
# la app lo baja, y fuera de TikTok se oye. El control de uniones no se resiente (midio -91
# dBFS contra un tope de -35) y el volumen medio sube de -20,4 a unos -17,4, comodo dentro de
# la franja [-21,-13] de control.py.
fc.append(f"[news][vz]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-11:TP=-1.0:LRA=11,"
          f"aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[aout]")
cmd = ["ffmpeg","-y","-hide_banner","-loglevel","error","-i",clip,"-i",voz,
       "-filter_complex",";".join(fc),"-map","[vout]","-map","[aout]","-t",str(T),
       "-c:v","libx264","-preset","medium","-crf","19","-pix_fmt","yuv420p","-r","30",
       "-c:a","aac","-ar","48000","-ac","2","-b:a","160k","-movflags","+faststart",out]
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode:
    print("FF_ERR", r.stderr[-1500:]); sys.exit(1)
print(json.dumps({"ok":True,"T":T,"voz":V,"clip":C,"pasadas":3 if s3 else 2,"out":out}))
