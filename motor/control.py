#!/usr/bin/env python3
"""control.py v2 (16/09/2026) - LA PUERTA: los controles duros, en UN solo lugar.

POR QUE EXISTE
--------------
Hasta el 15/09 la regla dura 3 (audio aac 48 kHz ESTEREO) vivia DENTRO de `motor/motor.py` y el
control de subida vivia DENTRO de `motor/produce.py`. Toda receta que produce su mp4 por fuera
del motor se los saltaba entera. El 14/09/2026 eso salio al aire: el SUPERVIDEO A
(`videolab/supervideo/build_sv.py`) subio `aac,48000,1` - MONO -, 60,74 s y volumen medio
-19,8 dB, rompiendo las reglas 3 y 5 a la vez. Su `final()` medias las cosas con `print("VERIF")`
y despues subia igual: **medir no es controlar si el resultado no puede bloquear la subida.**

Esto es la regla dura 3-ter de `motor/RECETA-MOTOR-NUBE.md` convertida en codigo: ninguna pieza
se sube sin pasar por aqui, la produzca quien la produzca. Una receta nueva no "nace con los
controles": importa este modulo o no sube.

v2 (16/09/2026) - EL AGUJERO DE LA VOZ. El 15/09 la pieza 967b salio al aire diciendo
*"indemnizacion por ANOS de servicio"*. Es exactamente el ejemplo con el que la regla dura 2 de
la receta esta escrita desde el 07/09, y volvio a pasar por dos razones que se sumaron:

  1. AQUI no habia ningun control de voz. Los cinco controles miraban el continente (audio,
     duracion, volumen, uniones, encuadre) y ninguno el CONTENIDO. La transcripcion contra el
     guion se hacia a mano en cada corrida, asi que la corrida que no la hacia publicaba igual.

  2. El unico procedimiento escrito que lo cazaba estaba roto de origen: "Verificacion sin ojos"
     paso 3 mandaba normalizar *"minusculas, sin tildes"* antes de comparar guion contra
     transcripcion. Plegando las tildes, "anos" y "años" son el mismo token y el control informa
     **0 palabras fuera del guion**. El control hecho para cazar esto era ciego a esto.

De ahi los controles 6 y 7. El 6 (`texto`) es determinista y BLOQUEA: mira el guion ANTES de
gastar TTS. El 7 (`voz`) escucha la pieza y BLOQUEA SOLO por n-tilde perdida; las demas palabras
fuera del guion las INFORMA, porque whisper se equivoca solo -en esta misma pieza escribio
"haya impactado" por "hayan pactado"- y bloquear a ciegas lleva a re-renderizar piezas sanas.

LOS CONTROLES
-------------
 1. AUDIO      ffprobe tiene que decir exactamente aac,48000,2          (regla dura 3)
 2. DURACION   22-34 s por defecto, franja configurable                 (regla dura 5)
 3. VOLUMEN    volumen medio dentro de [-21, -13] dB                    (franja medida del motor)
 4. UNIONES    RMS de cada empalme <= -35 dBFS (solo si se dan los cortes)
 5. PANTALLA   0 cajas de TEXTO PROPIO fuera de x[95,930] y[200,1586]   (regla dura 4)
               -> se delega en videolab/pantalla_chica.py; INFORMA, no bloquea (ver PRODUCIR.md)
 6. TEXTO      el guion, antes del TTS: n-tilde y tildes                (regla dura 2) BLOQUEA
 7. VOZ        lo que se OYE contra el guion, n-tilde sensible          (regla dura 2) BLOQUEA
               solo por n-tilde; lo demas informa. Se omite si no se le pasa el guion.

USO COMO MODULO
---------------
    from control import controlar, subir, texto
    ok, malas = texto(guion_completo)            # ANTES de sintetizar: coste cero
    r = controlar("981.mp4", uniones=[6.1, 12.4, 18.9, 24.2], guion=guion_completo)
    subir("981.mp4", upload_url, r)              # levanta RuntimeError si r["pasa"] es False

USO COMO CLI
------------
    python3 control.py 981.mp4 --uniones 6.1,12.4,18.9 --guion urls/981.txt --put "<upload_url>"
    python3 control.py --solo-texto urls/981.txt          # el control 6 suelto, antes del TTS
    exit 0 = PASA (y subio, si habia --put) | exit 1 = NO PASA (y NO subio nada)

ARREGLO SIN RE-RENDER
---------------------
    python3 control.py pieza.mp4 --remux    # re-encodea SOLO el audio a aac 48k estereo.
Conserva duracion y encuadre, ~3 s y 0 creditos. Metodo medido el 14/09/2026. Sirve para el
stock viejo (regla dura 3-bis): toda pieza de la RESERVA se re-mide con esto justo antes de
publicar, aunque la bitacora la de por limpia - esa etiqueta es del dia en que se escribio.
OJO: el remux NO arregla la voz. Una pieza que reprueba el control 7 se REHACE; no hay parche.
"""
import argparse, json, os, re, subprocess, sys, unicodedata

AUDIO_OK = "aac,48000,2"
DUR_MIN, DUR_MAX = 22.0, 34.0
VOL_MIN, VOL_MAX = -21.0, -13.0
UNION_MAX_DBFS = -35.0
VENTANA_UNION = 0.12          # s a cada lado del corte que se mide
ZONA = (95, 930, 200, 1586)   # x0, x1, y0, y1 - zona segura de TikTok

# Palabras que en estos guiones SIEMPRE llevan n-tilde. Si aparecen asi, la perdieron.
# Solo coincidencia de palabra entera: "mano", "sano" y "plano" no se tocan.
SIN_ENIE = {
    "ano": "año", "anos": "años", "dano": "daño", "danos": "daños",
    "senor": "señor", "senora": "señora", "senores": "señores", "senalar": "señalar",
    "senala": "señala", "senalado": "señalado", "nino": "niño", "nina": "niña",
    "ninos": "niños", "ninas": "niñas", "manana": "mañana", "ensenar": "enseñar",
    "diseno": "diseño", "pequeno": "pequeño", "pequena": "pequeña",
    "companero": "compañero", "companera": "compañera", "compania": "compañía",
    "dueno": "dueño", "duena": "dueña", "duenos": "dueños", "engano": "engaño",
    "espanol": "español", "sueno": "sueño", "bano": "baño", "cana": "caña",
}
# Palabras sin n-tilde pero con tilde obligatoria que el TTS lee mal si falta.
SIN_TILDE = {
    "articulo": "artículo", "articulos": "artículos", "codigo": "código",
    "dia": "día", "dias": "días", "numero": "número", "ultimo": "último",
    "ultima": "última", "practica": "práctica", "juridico": "jurídico",
    "juridica": "jurídica", "publico": "público", "publica": "pública",
    "economico": "económico", "economica": "económica", "minimo": "mínimo",
    "maximo": "máximo", "termino": "término", "credito": "crédito",
}


def _sh(cmd):
    return subprocess.run(cmd, shell=True, capture_output=True, text=True)


def _tok(s):
    """Palabras en minusculas, conservando n-tilde y tildes."""
    return re.findall(r"[0-9a-zñáéíóúü]+", (s or "").lower())


def _plano(s):
    """Sin tildes NI n-tilde. Solo para la comparacion que NO mira diacriticos."""
    return "".join(c for c in unicodedata.normalize("NFD", s or "")
                   if unicodedata.category(c) != "Mn")


def audio(mp4):
    """Regla dura 3: aac, 48000 Hz, 2 canales. Devuelve (ok, lo_que_dijo_ffprobe)."""
    s = _sh(f'ffprobe -v error -select_streams a:0 -show_entries '
            f'stream=codec_name,sample_rate,channels -of csv=p=0 "{mp4}"').stdout
    return s.strip().replace(" ", "") == AUDIO_OK, s.strip()


def duracion(mp4, dmin=DUR_MIN, dmax=DUR_MAX):
    """Regla dura 5: la pieza tiene que caer en la franja medida."""
    s = _sh(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{mp4}"').stdout.strip()
    d = float(s) if s else 0.0
    return dmin <= d <= dmax, round(d, 2)


def volumen(mp4):
    """Volumen medio dentro de la franja del motor. Fuera de franja = pieza rara, se mira."""
    # OJO: volumedetect imprime en nivel "info". Con -v error el resumen NO sale y el
    # regex no encuentra nada (medido el 15/09: devolvia 0.0 y reprobaba piezas sanas).
    r = _sh(f'ffmpeg -hide_banner -nostats -i "{mp4}" -af volumedetect -f null - 2>&1')
    m = re.search(r"mean_volume:\s*(-?[\d.]+) dB", r.stderr + r.stdout)
    v = float(m.group(1)) if m else 0.0
    return VOL_MIN <= v <= VOL_MAX, v


def uniones(mp4, cortes):
    """RMS en cada empalme entre tramos. Un chasquido audible se oye como pico sobre -35 dBFS."""
    peor, detalle = -999.0, []
    for t in cortes or []:
        ini = max(0.0, float(t) - VENTANA_UNION)
        r = _sh(f'ffmpeg -hide_banner -nostats -ss {ini:.3f} -t {VENTANA_UNION * 2:.3f} '
                f'-i "{mp4}" -af volumedetect -f null - 2>&1')
        m = re.search(r"max_volume:\s*(-?[\d.]+) dB", r.stderr + r.stdout)
        v = float(m.group(1)) if m else -999.0
        detalle.append(round(v, 1))
        peor = max(peor, v)
    if not cortes:
        return True, []
    return peor <= UNION_MAX_DBFS, detalle


def pantalla(mp4):
    """Regla dura 4. INFORMA, no bloquea: pantalla_chica.py no distingue el texto propio del
    texto que trae el clip del gancho, y contar cajas a ciegas lleva a re-renderizar piezas
    sanas (medido el 13/09). Ver 'Como se lee el control de pantalla chica' en PRODUCIR.md."""
    if not os.path.exists("pantalla_chica.py"):
        return None, "pantalla_chica.py no esta al lado; control omitido"
    r = _sh(f'python3 pantalla_chica.py "{mp4}"')
    return None, (r.stdout or r.stderr).strip()[-400:]


def texto(guion):
    """Control 6 - regla dura 2, ANTES del TTS. Determinista, coste cero, BLOQUEA.

    Un guion escrito sin n-tilde no se nota en pantalla (las tres fuentes tienen el glifo)
    pero SI en la voz: Kokoro lee "anos" donde el guion quiso decir "años". Esto se caza
    mirando el texto, no la pieza: sale gratis y evita gastar una sintesis entera.

    La regla -cion / -sion es dura: en español el singular SIEMPRE va acentuado
    ("indemnizacion" mal, "indemnización" bien), mientras que el plural NO la lleva
    ("indemnizaciones", "acciones"), asi que el plural no se toca.
    """
    malas = []
    for w in set(_tok(guion)):
        if w in SIN_ENIE:
            malas.append({"dice": w, "deberia": SIN_ENIE[w], "por": "n-tilde"})
        elif w in SIN_TILDE:
            malas.append({"dice": w, "deberia": SIN_TILDE[w], "por": "tilde"})
        elif re.fullmatch(r"[a-z]{4,}cion", w):
            malas.append({"dice": w, "deberia": w[:-4] + "ción", "por": "-cion singular"})
        elif re.fullmatch(r"[a-z]{4,}sion", w):
            malas.append({"dice": w, "deberia": w[:-4] + "sión", "por": "-sion singular"})
    malas.sort(key=lambda m: m["dice"])
    return (not malas), malas


def voz(media, guion, modelo="small"):
    """Control 7 - lo que se OYE contra el guion. BLOQUEA SOLO por n-tilde perdida.

    Se omite solo si no hay guion, asi que ninguna receta vieja se rompe al actualizar.

    Por que la n-tilde bloquea y el resto no: whisper conserva los diacriticos cuando estan
    (en la 991 del 15/09 escribio "daños" sin ayuda), asi que oir "anos" donde el guion dice
    "años" es senal del TTS, no del transcriptor. En cambio las palabras sueltas fuera del
    guion son casi siempre del transcriptor - en la 967b escribio "haya impactado" por
    "hayan pactado" - y bloquear por ellas re-renderiza piezas sanas. Por eso se informan.

    EL PEGADO (medido el 16/09 contra el audio real de la 967b): whisper transcribio "por años"
    como UN token, "poranos". Buscar "anos" como palabra suelta NO lo encuentra, y esa fue la
    primera version de este control - un falso negativo sobre la pieza misma que lo motivo. Por
    eso tambien se mira el sufijo de los tokens que estan fuera del guion, exigiendo que el
    prefijo que queda sea a su vez palabra del guion: "poranos" = "por" + "anos" y "por" esta en
    el guion, asi que se marca; en "mano" el sufijo "ano" deja "m", que no es palabra del guion,
    asi que no se marca.

    ⚠️ En piezas de REACCION hay que pasarle el **mp3 de la voz**, no el mp4: el mp4 lleva a
    proposito el audio del noticiero durante el gancho y su texto no esta en el guion.
    """
    if not guion:
        return True, "sin guion; control omitido"
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None, "faster-whisper no instalado; control omitido"
    wav = os.path.splitext(media)[0] + ".ctrl.wav"
    _sh(f'ffmpeg -y -v error -i "{media}" -vn -ac 1 -ar 16000 "{wav}"')
    m = WhisperModel(modelo, device="cpu", compute_type="int8")
    segs, _ = m.transcribe(wav, language="es", vad_filter=False, word_timestamps=True)
    dicho = " ".join(s.text for s in segs).strip()

    oido = set(_tok(dicho))
    oido_plano = {_plano(w) for w in oido}
    vocab = {_plano(w) for w in _tok(guion)}
    # INFORMA: palabras fuera del guion, plegando diacriticos (la comparacion de siempre)
    fuera = sorted({w for w in _tok(_plano(dicho)) if w not in vocab and not w.isdigit()})

    # BLOQUEA: cada palabra del guion con n-tilde tiene que oirse CON su n-tilde
    perdidas = []
    for w in sorted({w for w in _tok(guion) if "ñ" in w}):
        if w in oido:
            continue                                  # se oyo bien
        p = _plano(w)
        pegada = any(f != p and f.endswith(p) and f[:-len(p)] in vocab for f in fuera)
        if p in oido_plano or pegada:
            perdidas.append(w)
    return (not perdidas), {"enie_perdida": perdidas, "fuera_del_guion": fuera[:15],
                            "dicho": dicho[:500]}


def controlar(mp4, dmin=DUR_MIN, dmax=DUR_MAX, cortes=None, guion=None, media_voz=None):
    """Corre los controles y devuelve el informe. 'pasa' es la conjuncion de los que BLOQUEAN.

    guion:      texto completo de la voz. Sin el, los controles 6 y 7 se omiten.
    media_voz:  en piezas de REACCION, el mp3 de la voz; el control 7 lo escucha en vez del mp4.
    """
    a_ok, a = audio(mp4)
    d_ok, d = duracion(mp4, dmin, dmax)
    v_ok, v = volumen(mp4)
    u_ok, u = uniones(mp4, cortes)
    _, p = pantalla(mp4)
    t_ok, t = texto(guion) if guion else (True, "sin guion; control omitido")
    z_ok, z = voz(media_voz or mp4, guion)
    r = {"pieza": os.path.basename(mp4),
         "audio": {"ok": a_ok, "valor": a, "esperado": AUDIO_OK},
         "duracion": {"ok": d_ok, "valor": d, "franja": [dmin, dmax]},
         "volumen": {"ok": v_ok, "valor": v, "franja": [VOL_MIN, VOL_MAX]},
         "uniones": {"ok": u_ok, "valor": u, "tope": UNION_MAX_DBFS},
         "pantalla_chica": {"ok": None, "valor": p},
         "texto": {"ok": t_ok, "valor": t},
         "voz": {"ok": z_ok, "valor": z},
         "pasa": bool(a_ok and d_ok and v_ok and u_ok and t_ok and z_ok is not False)}
    r["falla"] = [k for k in ("audio", "duracion", "volumen", "uniones", "texto", "voz")
                  if r[k]["ok"] is False]
    return r


def remux(mp4, salida=None):
    """Arregla SOLO el audio a aac 48k estereo. No re-renderiza: conserva duracion y encuadre.
    NO arregla la voz: una pieza que reprueba el control 6 o 7 se rehace desde el guion."""
    salida = salida or mp4.replace(".mp4", "_48k2.mp4")
    r = _sh(f'ffmpeg -y -v error -i "{mp4}" -c:v copy -c:a aac -ar 48000 -ac 2 -b:a 192k '
            f'-movflags +faststart "{salida}"')
    if r.returncode:
        raise RuntimeError(f"remux fallo: {r.stderr[-400:]}")
    return salida


def subir(mp4, upload_url, informe=None, dmin=DUR_MIN, dmax=DUR_MAX, cortes=None,
          guion=None, media_voz=None):
    """PUT a la upload_url presignada. NO sube si el control no pasa: ese es todo el punto.
    Devuelve el codigo HTTP (200 = subida buena)."""
    r = informe or controlar(mp4, dmin, dmax, cortes, guion, media_voz)
    if not r["pasa"]:
        raise RuntimeError(f"CONTROL NO PASA ({', '.join(r['falla'])}) -> no se sube {mp4}. "
                           f"{json.dumps({k: r[k] for k in r['falla']}, ensure_ascii=False)}")
    c = _sh(f'curl -s -o /dev/null -w "%{{http_code}}" -X PUT -H "Content-Type: video/mp4" '
            f'--data-binary @"{mp4}" "{upload_url}"').stdout.strip()
    return c


def main():
    ap = argparse.ArgumentParser(description="Los controles duros antes de publicar.")
    ap.add_argument("mp4", nargs="?")
    ap.add_argument("--dur-min", type=float, default=DUR_MIN)
    ap.add_argument("--dur-max", type=float, default=DUR_MAX)
    ap.add_argument("--uniones", default="", help="tiempos de corte en segundos, separados por coma")
    ap.add_argument("--guion", default="", help="archivo urls/<n>.txt; activa los controles 6 y 7")
    ap.add_argument("--voz", default="", help="mp3 de la voz; en piezas de reaccion, en vez del mp4")
    ap.add_argument("--solo-texto", default="", help="corre SOLO el control 6 sobre ese archivo")
    ap.add_argument("--put", default="", help="upload_url presignada; solo sube si el control pasa")
    ap.add_argument("--remux", action="store_true", help="arregla el audio a 48k estereo y re-mide")
    a = ap.parse_args()

    # Control 6 suelto: se corre ANTES de sintetizar, cuando todavia no hay mp4.
    if a.solo_texto:
        ok, malas = texto(open(a.solo_texto, encoding="utf-8").read())
        print(json.dumps({"texto": {"ok": ok, "valor": malas}}, ensure_ascii=False, indent=1))
        if not ok:
            print("NO PASA: texto -> corrige el guion ANTES de gastar TTS", file=sys.stderr)
            return 1
        return 0

    if not a.mp4:
        ap.error("falta el mp4 (o usa --solo-texto)")
    mp4 = a.mp4
    cortes = [float(x) for x in a.uniones.split(",") if x.strip()]
    guion = open(a.guion, encoding="utf-8").read() if a.guion else None
    r = controlar(mp4, a.dur_min, a.dur_max, cortes, guion, a.voz or None)

    if a.remux and not r["audio"]["ok"]:
        mp4 = remux(mp4)
        print(f"REMUX -> {mp4}")
        r = controlar(mp4, a.dur_min, a.dur_max, cortes, guion, a.voz or None)

    print(json.dumps(r, ensure_ascii=False, indent=1))
    if not r["pasa"]:
        print("NO PASA:", ", ".join(r["falla"]), "-> no se sube nada", file=sys.stderr)
        return 1
    if a.put:
        print("PUT", subir(mp4, a.put, r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
