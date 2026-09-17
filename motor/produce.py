#!/usr/bin/env python3
"""produce.py v4 (17/09/2026) - driver de produccion del Estudio Juridico San Bernardo.

POR QUE EXISTE
--------------
Hasta el 12/09 cada tanda se producia pegando el pipeline COMPLETO dentro del comando de
`sandbox_exec`, que tiene un tope de 16.000 caracteres. Como cada `upload_url` presignada de
Higgsfield mide ~2.400 caracteres, con cinco piezas las URLs solas se comian 12.000 y no cabia
el codigo: habia que partir la tanda a mano, reescribir el pipeline cada noche y cada reescritura
era una oportunidad nueva de equivocarse. Ese fue el costo repetido de las corridas del 11 y 12/09.

Con este driver el comando del sandbox se reduce a: bajar produce.py + un job.json compacto +
`python3 produce.py job.json`. El pipeline vive versionado en el repo, no en el prompt.

v2 (15/09/2026): los controles salieron de aqui y se fueron a `motor/control.py`, que es LA
PUERTA comun a todas las recetas (regla dura 3-ter). Este archivo ya no decide si una pieza sube:
se lo pregunta a control.py, igual que `videolab/supervideo/build_sv.py`. De paso entraron los
dos controles que aqui faltaban y que el 14/09 costaron una pieza mala al aire: VOLUMEN MEDIO y
RMS DE LAS UNIONES entre tramos (los cortes salen de `<id>.mp3.tramos.json`, que ya se calculaba).

v3 (16/09/2026): se ABREN los controles 6 y 7 (voz), que control.py v2 traia pero que aqui
quedaban inertes porque `controlar()` los omite si no se le pasa el guion - y no se le pasaba.
Ese es el agujero por el que la 967b salio al aire el 15/09 diciendo "indemnizacion por ANOS de
servicio". Ahora el guion se arma primero y el control 6 corre ANTES de `voz.py`: un guion sin
n-tilde se para sin haber gastado una sintesis. Ademas sube el parche de uniones de las piezas
de reaccion que el 15/09 se aplico a mano en el sandbox y nunca llego al repo.

v4 (17/09/2026): entra el CONTROL 0 - GANCHO DEL BANCO. La doctrina manda desde el 13/09 que el
gancho salga del banco medido (tipo ESCENA), y las auditorias del 14, 15 y 16/09 verificaron
pieza por pieza que NINGUNA de las ~130 publicaciones lo hizo. El diagnostico de esas tres noches
fue siempre el mismo -"la produccion improvisa el gancho al momento"- y la respuesta fue siempre
la misma: escribir quince ganchos mas. El problema no era el stock (34 limpios sin usar): era que
la regla vivia en prosa dentro de un archivo de memoria y NINGUNA pieza de codigo podia leerla.
Ahora el banco es `motor/ganchos/cola.json` y esta funcion lo abre antes de gastar un solo
credito de TTS: pieza de lamina con gancho que no esta en el banco, no se produce. Las piezas de
reaccion (prensa:true) quedan exentas, porque su gancho es el titular de la noticia del dia.

QUE HACE (una pieza completa, de punta a punta)
-----------------------------------------------
 0. CONTROL 0: el gancho sale de motor/ganchos/cola.json (salvo piezas de reaccion)
 1. baja videolab/voz.py, videolab/karaoke.py, videolab/pantalla_chica.py, motor/motor.py
    y motor/control.py del repo
 2. pip install de lo que hace falta (kokoro, soundfile, faster-whisper, numpy, pillow, rapidocr)
 3. baja el clip de gancho y lo prepara (crop 9:16 + pista de audio silenciosa, o fondo
    desenfocado + audio original si es clip de prensa: "prensa": true)
 4. CONTROL 6: revisa el guion (n-tilde y tildes) ANTES de sintetizar      (regla dura 2)
 5. escribe urls/<id>.txt con los 5 tramos de voz separados por linea en blanco  (regla dura 2)
 6. voz.py (kokoro, 48 kHz estereo)  ->  karaoke.py  ->  motor.py
 7. CONTROL: control.controlar() corre los siete (audio, duracion, volumen, uniones, pantalla,
    texto y voz)
 8. SUBIDA: control.subir() hace el PUT y SOLO si el control paso
Deja un informe en resultado.json con una linea por pieza, con el informe de control completo.

job.json
--------
{"piezas":[{"id":"941","materia":"laboral","rotulo":"NOTICIA DE HOY",
            "hook":"https://assets.mixkit.co/videos/39912/39912-720.mp4","prensa":false,
            "gancho":"...","puntos":[{"t":"...","d":"..."} x3],"cierre":"...",
            "voz":["tramo1","tramo2","tramo3","tramo4","tramo5"],
            "upload_url":"https://...s3.amazonaws.com/..."}]}

El campo "gancho" de una pieza de lamina tiene que coincidir con una entrada de
motor/ganchos/cola.json. Si no coincide, la pieza no se produce y resultado.json dice por que.

Uso: python3 produce.py job.json   (dentro de UNA llamada sandbox_exec con background:true)
"""
import json, os, re, subprocess, sys, unicodedata, urllib.request

RAW = "https://raw.githubusercontent.com/cristopherbravoabogado-code/estudio-automatizacion/main/"
DEPS = ["videolab/voz.py", "videolab/karaoke.py", "videolab/pantalla_chica.py",
        "motor/motor.py", "motor/control.py"]
BANCO_URL = RAW + "motor/ganchos/cola.json"
PIP = "kokoro soundfile faster-whisper numpy pillow rapidocr-onnxruntime"
DUR_MIN, DUR_MAX = 22.0, 34.0
_BANCO = None


def sh(cmd, check=True, t=900):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=t)
    if check and r.returncode != 0:
        raise RuntimeError(f"{cmd[:90]} -> {r.stderr[-1200:]}")
    return r


def _norm(s):
    """Compara ganchos sin que una tilde o un signo decidan. OJO: aqui SI se pliegan las
    tildes, al reves que en el control 6 de texto. Son dos preguntas distintas: alla se
    busca la diferencia entre 'anos' y 'anios' y plegarla la borra; aca se busca si dos
    redacciones del mismo gancho son la misma frase."""
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s)).strip()


def banco(p):
    """CONTROL 0 (regla de doctrina del 13/09/2026, ejecutable desde el 17/09).

    Devuelve (ok, id_del_gancho_o_motivo). Las piezas de reaccion estan exentas: su gancho
    es el titular de la noticia del dia y no puede estar escrito de antemano en un banco.
    """
    global _BANCO
    if p.get("prensa"):
        return True, "exenta: pieza de reaccion"
    if _BANCO is None:
        _BANCO = json.loads(urllib.request.urlopen(BANCO_URL, timeout=90).read().decode("utf-8"))
    g = _norm(p.get("gancho", ""))
    if not g:
        return False, "SIN GANCHO"
    for e in _BANCO["cola"]:
        t = _norm(e["texto"])
        if t == g or t.startswith(g[:40]) or g.startswith(t[:40]):
            return True, e["id"]
    return False, "SIN BANCO"


def preparar():
    for d in DEPS:
        urllib.request.urlretrieve(RAW + d, os.path.basename(d))
    print("DEPS_OK", flush=True)
    sh(f"pip install -q {PIP}", check=False, t=900)
    print("PIP_OK", flush=True)


def hook(url, dst, prensa):
    urllib.request.urlretrieve(url, "raw_hook.mp4")
    if prensa:
        # clip de prensa: fondo desenfocado + clip centrado, conserva cintillo y AUDIO ORIGINAL
        # OJO: esta rama muere en [0:a] si el clip viene MUDO. ffprobe el clip antes de elegirla.
        f = ("[0:v]split=2[bg][fg];"
             "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
             "boxblur=25:2,eq=brightness=-0.14[b];"
             "[fg]scale=1080:-2:flags=lanczos,unsharp=5:5:0.9:5:5:0.0[f];"
             "[b][f]overlay=(W-w)/2:(H-h)/2,fps=30[v];"
             "[0:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[a]")
        sh(f'ffmpeg -y -hide_banner -loglevel error -t 12 -i raw_hook.mp4 -filter_complex "{f}" '
           f'-map "[v]" -map "[a]" -t 12 -c:v libx264 -preset veryfast -crf 19 '
           f'-c:a aac -ar 48000 -ac 2 -b:a 128k {dst}')
    else:
        # metraje real de stock: crop 9:16 + pista de audio silenciosa (sin ella el mux falla)
        sh(f'ffmpeg -y -hide_banner -loglevel error -i raw_hook.mp4 -f lavfi -t 12 '
           f'-i anullsrc=r=48000:cl=stereo -vf "scale=1080:1920:'
           f'force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,'
           f'unsharp=5:5:0.9:5:5:0.0,fps=30" -map 0:v -map 1:a -t 12 -c:v libx264 '
           f'-preset veryfast -crf 19 -c:a aac -ar 48000 -ac 2 -b:a 128k {dst}')


def una(p):
    import control                                   # se bajo en preparar(); LA PUERTA
    i = p["id"]
    prensa = bool(p.get("prensa", False))
    r = {"id": i, "pasos": []}

    # --- CONTROL 0: el gancho sale del banco medido -----------------------------------------
    # Se corre PRIMERO, antes que nada: es el unico control que puede evitar producir entera
    # una pieza que la doctrina no queria. Cuesta una descarga de 6 KB.
    ok_b, gid = banco(p)
    r["gancho_banco"] = gid
    if not ok_b:
        r["subida"] = (f"NO PRODUCIDA: gancho fuera del banco ({gid}). El gancho de una pieza "
                       "de lamina tiene que estar en motor/ganchos/cola.json (doctrina del "
                       "13/09/2026). Si el gancho es nuevo y bueno, agregalo AL BANCO primero.")
        return r
    r["pasos"].append("banco")

    # --- CONTROL 6 (regla dura 2), ANTES de gastar TTS -------------------------------------
    # Un guion sin n-tilde no se nota en pantalla pero SI en la voz: el 15/09 la 967b salio al
    # aire diciendo "indemnizacion por ANOS de servicio". Mirar el texto sale gratis; descubrirlo
    # despues cuesta la sintesis, el render y -si nadie escucha la pieza- la publicacion.
    guion = "\n\n".join(t.strip() for t in p["voz"])   # regla dura 2: tildes, UTF-8, 5 tramos
    ok_txt, malas = control.texto(guion)
    if not ok_txt:
        r["control_texto"] = malas
        r["subida"] = ("NO PRODUCIDA: texto (regla dura 2) -> " +
                       ", ".join(f"{m['dice']}->{m['deberia']}" for m in malas))
        return r
    r["pasos"].append("texto")

    hook(p["hook"], f"hook{i}.mp4", prensa)
    r["pasos"].append("hook")

    os.makedirs("urls", exist_ok=True)
    open(f"urls/{i}.txt", "w", encoding="utf-8").write(guion + "\n")
    v = sh(f"python3 voz.py urls/{i}.txt {i}.mp3 kokoro")
    r["voz"] = v.stdout.strip().splitlines()[-1] if v.stdout.strip() else ""
    sh(f"python3 karaoke.py {i}.mp3 {i}.ass")
    r["pasos"].append("voz+karaoke")

    tramos = json.load(open(f"{i}.mp3.tramos.json"))
    pieza = {"id": i, "materia": p["materia"], "gancho": p["gancho"], "puntos": p["puntos"],
             "cierre": p["cierre"], "voz": f"{i}.mp3", "hook": f"hook{i}.mp4",
             "subs": f"{i}.ass", "tramos": tramos}
    if p.get("rotulo"):
        pieza["rotulo"] = p["rotulo"]
    json.dump(pieza, open(f"pieza{i}.json", "w"), ensure_ascii=False)
    m = sh(f"python3 motor.py pieza{i}.json {i}.mp4")
    r["motor"] = m.stdout.strip().splitlines()[-1]
    r["pasos"].append("motor")

    # --- LA PUERTA: los controles viven en control.py (regla dura 3-ter) --------------------
    # Los empalmes entre tramos de voz son los cortes interiores de tramos[]: ahi es donde
    # aparecen los chasquidos si la union de audio se hizo mal.
    #
    # PIEZAS DE REACCION (prensa:true): el PRIMER corte interior cae donde se desvanece el audio
    # del noticiero del gancho, asi que mide como voz y reprueba una pieza sana, bloqueando la
    # subida. Se salta. (Parche aplicado a mano el 15/09 en la 991 y subido al repo el 16/09.)
    # Por lo mismo el control 7 escucha el mp3 de la voz y no el mp4, que lleva el audio del
    # noticiero a proposito.
    if isinstance(tramos, list) and len(tramos) > (3 if prensa else 2):
        cortes = [float(t) for t in (tramos[2:-1] if prensa else tramos[1:-1])]
    else:
        cortes = []
    c = control.controlar(f"{i}.mp4", DUR_MIN, DUR_MAX, cortes,
                          guion=guion, media_voz=f"{i}.mp3" if prensa else None)
    r["control"] = c
    r["audio"], r["audio_ok"] = c["audio"]["valor"], c["audio"]["ok"]
    r["dur"], r["dur_ok"] = c["duracion"]["valor"], c["duracion"]["ok"]
    r["volumen"] = c["volumen"]["valor"]
    r["uniones"] = c["uniones"]["valor"]
    r["pantalla_chica"] = c["pantalla_chica"]["valor"]
    r["voz_control"] = c["voz"]["valor"]

    if not c["pasa"]:
        r["subida"] = "NO SUBIDA: " + ", ".join(c["falla"])
        return r
    r["subida"] = control.subir(f"{i}.mp4", p["upload_url"], c)
    return r


def main(job):
    preparar()
    out = []
    for p in json.load(open(job))["piezas"]:
        try:
            out.append(una(p))
        except Exception as e:
            out.append({"id": p["id"], "error": str(e)[-800:]})
        json.dump(out, open("resultado.json", "w"), ensure_ascii=False, indent=1)
        print("PIEZA", p["id"], "lista", flush=True)
    print("PRODUCE_FIN")
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main(sys.argv[1])
