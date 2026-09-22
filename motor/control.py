#!/usr/bin/env python3
"""control.py v6 (22/09/2026) - LA PUERTA: los controles duros, en UN solo lugar.

POR QUE EXISTE
--------------
Hasta el 15/09 la regla dura 3 (audio aac 48 kHz ESTEREO) vivia DENTRO de `motor/motor.py` y el
control de subida vivia DENTRO de `motor/produce.py`. Toda receta que produce su mp4 por fuera
del motor se los saltaba entera. El 14/09/2026 eso salio al aire: el SUPERVIDEO A
(`videolab/supervideo/build_sv.py`) subio `aac,48000,1` - MONO -, 60,74 s y volumen medio
-19,8 dB, rompiendo las reglas 3 y 5 a la vez. Su `final()` medias las cosas con `print("VERIF")`
y despues subia igual: **medir no es controlar si el resultado no puede bloquear la subida.**

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

v3 (19/09/2026) - LA PUERTA FALLABA ABIERTA. Regla dura 2-ter de la receta.
El QC del 19/09 midio las tres piezas publicadas el 18/09 (1001c, R03 y 1002): las tres limpias
en los siete controles. El defecto no estaba en ninguna pieza, estaba AQUI. Medido sobre esta
misma funcion, con la R03 ya publicada:

    >>> control.controlar("R03.mp4")          # sin guion
    pasa = True | falla = []
    texto: {'ok': True, 'valor': 'sin guion; control omitido'}
    voz  : {'ok': True, 'valor': 'sin guion; control omitido'}

O sea: **los dos controles de CONTENIDO se apagaban solos con no pasarles el guion, y la pieza
pasaba la puerta igual.** Es el agujero de la 967b una capa mas arriba. No es hipotetico: el
docstring de `produce.py` v3 dice, textual, *"se ABREN los controles 6 y 7 (voz), que control.py
v2 traia pero que aqui quedaban inertes porque `controlar()` los omite si no se le pasa el guion
- y no se le pasaba"*. Ese arreglo se hizo EN EL LLAMADOR, asi que cubrio a `produce.py` y a
nadie mas: cualquier receta nueva -un supervideo, una serie, una reaccion escrita a mano- vuelve
a nacer con los controles 6 y 7 apagados y no se entera, porque la puerta le dice `pasa: True`.
Un control que se apaga por omision no es un control: es una intencion con nombre de funcion.

  - `controlar()` ahora exige el guion (`exigir_guion=True` por defecto): sin guion, los
    controles 6 y 7 quedan `ok: False` y **`pasa: False`**. Falla CERRADA.
  - `voz()` sin `faster-whisper` instalado tambien BLOQUEA. Antes devolvia `None` ("control
    omitido") y `controlar()` lo dejaba pasar con `z_ok is not False`: un sandbox sin el paquete
    borraba el control de voz entero sin que nadie lo viera.
  - `auditar(mp4)` es el unico camino sin guion, y NO sube nada: es para revisar lo YA publicado
    dias despues, cuando el `urls/<n>.txt` murio con el sandbox que lo escribio. Busca la n-tilde
    perdida en lo que se OYE, sin nada con que comparar (ver su docstring).

v4 (20/09/2026) - EL MISMO AGUJERO, UN CONTROL MAS ABAJO. Regla dura 2-ter de la receta.
La v3 cerro los controles 6 y 7, que se apagaban si no se les pasaba el guion. El control 4
seguia abierto por la misma razon exacta y nadie lo miro, porque el arreglo de la v3 se escribio
mirando el caso de la voz en vez de la FORMA del defecto. Medido el 20/09 sobre la 1003
(`0b199268-...`), alojada y sin publicar:

    >>> control.controlar("1003.mp4", exigir_guion=False)["uniones"]
    {'ok': True, 'valor': [], 'tope': -35.0}     # y 'pasa': True

`uniones()` empezaba con `if not cortes: return True, []`. O sea: **el control de los empalmes se
apagaba con no pasarle los cortes y la pieza pasaba la puerta igual**, igual que el guion apagaba
los controles 6 y 7 antes de la v3. Y hay dos llamadores que entran por ahi: `produce.py` pasa
`cortes = []` cuando le falta el `<id>.mp3.tramos.json`, y `build_sv.py` pasa `t0[1:]`, que puede
venir vacio.

  - `cortes_auto(media)` encuentra los empalmes sola (silencedetect a -25 dB, pausas >= 0,6 s,
    descartando la cola de silencio del final). Ya nadie tiene que acordarse de calcularlos.
  - `uniones()` sin cortes los BUSCA; si no encuentra ninguno devuelve False y la pieza NO SUBE.
  - Detecta y mide sobre el MISMO archivo, asi que el LEAD de 0,5 s de la regla dura 6 deja de
    hacer falta: existia solo porque la pausa se buscaba en el mp3 y se media en el mp4.
  - En REACCION se le pasa `media_voz` (el mp3) y `saltar_primero=True`.

v5 (21/09/2026) - EL CONTROL 4 MEDIA UNA RENDIJA Y LA LLAMABA "EL EMPALME". Regla dura 2-quater.
La v4 dejo de apagarse, pero seguia mirando por el ojo de la cerradura: `cortes_auto` define el
corte como el CENTRO de la pausa y `uniones()` media `max_volume` en una ventana de +-0,12 s en
torno a el. Las pausas entre tramos duran ~1,1 s, asi que el control abria 0,24 s y daba
veredicto sobre los otros 0,86 s -el 78 % de la pausa- sin haberlos mirado. Medido el 21/09
sobre la 1004 (`17d36226-...`), pausa 25,43-26,59 s:

    v4:   ventana 25,89-26,13   ->  -50,1 dBFS  ->  "empalme limpio"
    real: transitorio 26,43-26,48  ->  -33,4 dBFS, sobre el tope de -35

El numero de la v4 era cierto y era del intervalo equivocado: un FALSO PASE, no un falso
positivo. Es la tercera vez seguida que el defecto tiene la misma FORMA -el control contesta una
pregunta que no tiene con que contestar- y las tres veces el arreglo anterior se escribio mirando
el caso concreto en vez de la forma. De ahi la regla 2-quater: **un control no informa solo su
veredicto, informa que parte del objeto miro.**

  - `uniones()` en modo automatico barre la pausa ENTERA menos `GUARDA_PAUSA` (0,15 s) en cada
    borde, donde vive la cola del ultimo fonema y el ataque del siguiente (-24,2 dBFS en la 1004:
    es voz, no chasquido). El barrido sube de 0,96 s a 3,25 s en una pieza de 5 tramos.
  - Con los cortes dados a mano se sigue midiendo la ventana de +-0,12 s -un `tramos.json` trae
    la costura exacta y ahi la ventana es lo correcto- pero el informe lo DICE en `cobertura`,
    junto con `barrido_s` y los `intervalos` medidos. Nadie puede volver a leer un barrido
    parcial como si fuera la pausa completa.
  - `auditar()` corre ahora tambien el control 4.

v6 (22/09/2026) - UNA PUERTA HECHA SOLO DE TECHOS. Regla dura 2-quinquies.
Medido hoy sobre la 1003 (`0b199268-...`, limpia en los siete controles) con el audio silenciado
a partir del segundo 16 - o sea, EL SEGUNDO DE LOS TRES DEFECTOS QUE SALIERON AL AIRE, la pieza
con la segunda mitad muda, reproducido tal cual contra la puerta v5:

    >>> control.controlar("mudo_cola.mp4", guion=guion)["pasa"]
    True                      # falla: []   los SIETE controles la aprueban

    audio  aac,48000,2  ok  |  duracion 31,04 s  ok  |  volumen -17,7 dB  ok (franja -21/-13)
    uniones  ok: True   empalmes: 2   dbfs: [-35,0 / -38,7]
    voz      ok: True   enie_perdida: []      (el guion dice "anos" en el tramo 4... que es mudo)

La v4 y la v5 decian las dos, en este mismo docstring, que el control 4 era "el control que le
corresponde al segundo de los tres defectos que salieron al aire, la pieza con la segunda mitad
muda, porque es un defecto que vive DENTRO de una pausa". Es FALSO, y hoy esta medido: el control
4 mide el TECHO de una pausa -busca un pico por encima de -35 dBFS- y este defecto es de PISO. El
silencio no solo no lo reprueba: saca la mejor nota que ese control sabe dar. En la variante con
el hueco en el medio, el control 4 midio los 11,7 s mudos como si fueran un empalme y los puntuo
-91,0 dBFS, LA UNION MAS LIMPIA DE LA PIEZA. Los demas tampoco lo ven: el volumen es un PROMEDIO
sobre el archivo entero y media pieza muda solo lo baja de -15,0 a -17,7 dB, adentro de la
franja; el control 7 bloquea por n-tilde OIDA MAL, y una palabra que no suena nunca no esta mal
oida -"anos" desaparecio con el tramo 4 y `enie_perdida` volvio vacia-; el recall de la pasada 3a,
que si lo habria notado, INFORMA y no bloquea por decision expresa. Los siete controles preguntan
si algo SOBRA o suena mal. Ninguno preguntaba si algo FALTA.

  - CONTROL 8, `cobertura_voz()`: que fraccion de la LINEA DE TIEMPO ENTERA lleva voz y cuanto
    dura el hueco mas largo, la cola incluida. BLOQUEA bajo 65 % de cobertura o con cualquier
    hueco de mas de 3,0 s. Calibrado el 22/09 sobre cuatro piezas reales -1003, 1002, 1004 y
    1000: cobertura 81,0 / 81,0 / 84,0 / 75,6 % y mayor hueco 1,52 / 1,51 / 1,10 / 1,54 s- contra
    las dos mutiladas: 44,4 % con 15,07 s y 49,3 % con 12,01 s. Las dos ahora NO PASAN.
  - `huecos_voz()` es deliberadamente lo contrario de `cortes_auto()`: aquella descarta la cola
    de silencio del final porque "no es un empalme", y ahi es exactamente donde se esconde media
    pieza muda. El control 8 no descarta nada de la linea de tiempo.
  - `texto()` con un guion vacio devolvia True: cero palabras, cero palabras malas. Otro objeto
    vacio sacando la mejor nota. Ahora un guion en blanco BLOQUEA como si no existiera.
  - LA REGLA (2-quinquies de la receta): **a todo control hay que preguntarle que nota le pone al
    objeto VACIO.** Si el silencio, el cuadro en negro o el texto en blanco sacan su mejor nota,
    el control mide en una sola direccion y le falta el piso. Es la pregunta hermana de la 2-ter
    (llamarlo SIN el dato que necesita: si contesta que si, esta roto) y de la 2-quater (que
    parte del objeto miro). Las tres se le corren a todo control nuevo, y a los viejos cuando
    cae uno.
  - Corrida hoy sobre los ocho, con la 1003 silenciada entera y por partes: `audio` sobre un mp4
    sin pista da "" y bloquea; `duracion` da 0,0 y bloquea; `volumen` sobre silencio total da
    -91,0 dB y bloquea, asi que su ceguera es al defecto PARCIAL -que es justo lo que cubre el
    control 8-; `uniones` sobre silencio TOTAL bloquea pero DE REBOTE (no encuentra ningun
    empalme y cae en la 2-ter), y sobre silencio PARCIAL aprueba y encima puntua el tramo mudo
    como la union mas limpia: ese era el agujero; `texto` con guion vacio aprobaba (corregido
    aqui); `voz` sin guion bloquea desde la v3.

LOS CONTROLES
-------------
 1. AUDIO      ffprobe tiene que decir exactamente aac,48000,2          (regla dura 3)
 2. DURACION   22-34 s por defecto, franja configurable                 (regla dura 5)
 3. VOLUMEN    volumen medio dentro de [-21, -13] dB                    (franja medida del motor)
 4. UNIONES    pico de cada empalme <= -35 dBFS                           BLOQUEA
               -> si no le dan los cortes los BUSCA; si no aparece ninguno, NO PASA (v4)
               -> barre la PAUSA ENTERA, no una ventana en su centro, y declara su
                  `cobertura` y su `barrido_s` en el informe (v5)
 5. PANTALLA   0 cajas de TEXTO PROPIO fuera de x[95,930] y[200,1586]   (regla dura 4)
               -> se delega en videolab/pantalla_chica.py; INFORMA, no bloquea (ver PRODUCIR.md)
 6. TEXTO      el guion, antes del TTS: n-tilde y tildes                (regla dura 2) BLOQUEA
 7. VOZ        lo que se OYE contra el guion, n-tilde sensible          (regla dura 2) BLOQUEA
               solo por n-tilde; lo demas informa.
 8. COBERTURA  >= 65 % de la linea de tiempo con voz, ningun hueco > 3,0 s  BLOQUEA (v6)
               -> es el PISO del control 4: aquel caza el pico que SOBRA dentro de una pausa,
                  este la voz que FALTA. Cuenta la cola del final, que `cortes_auto` descarta
                  por no ser un empalme, que es donde se escondio la pieza medio muda
 -> Los controles 6 y 7 YA NO SE OMITEN: sin guion, `controlar()` devuelve `pasa: False`
    (regla dura 2-ter). Para mirar una pieza sin guion existe `auditar()`, que no sube.

USO COMO MODULO
---------------
    from control import controlar, subir, texto, auditar
    ok, malas = texto(guion_completo)            # ANTES de sintetizar: coste cero
    r = controlar("981.mp4", cortes=[6.1, 12.4, 18.9, 24.2], guion=guion_completo)
    subir("981.mp4", upload_url, r)              # levanta RuntimeError si r["pasa"] es False
    auditar("ya_publicada.mp4")                  # QC sin guion; NO sube

USO COMO CLI
------------
    python3 control.py 981.mp4 --uniones 6.1,12.4,18.9 --guion urls/981.txt --put "<upload_url>"
    python3 control.py --solo-texto urls/981.txt          # el control 6 suelto, antes del TTS
    python3 control.py ya_publicada.mp4 --auditar         # QC de lo ya publicado, sin guion
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
VENTANA_UNION = 0.12          # s a cada lado del corte, SOLO cuando los cortes vienen
                              # dados a mano (un tramos.json trae la costura exacta).
GUARDA_PAUSA = 0.15           # s que se descartan en CADA borde de la pausa detectada:
                              # ahi vive la cola del ultimo fonema y el ataque del
                              # siguiente. Medido el 21/09 en la 1004: el primer
                              # instante bajo -25 dB marca -24,2 dBFS. Sin guarda, la
                              # cola de la voz se leeria como chasquido.
UNION_NOISE_DB = -25.0        # umbral con que se DETECTA la pausa. 10 dB por encima del tope
                              # del control: un chasquido de -30 dB cae DENTRO de la pausa
                              # detectada y el control lo ve; uno mas fuerte parte la pausa en
                              # dos, no llega a 0,6 s y el empalme NO se encuentra - que es
                              # justamente por lo que "no encontre empalmes" tiene que
                              # BLOQUEAR y no pasar.
UNION_MIN_PAUSA = 0.60        # s - solo los empalmes ENTRE TRAMOS. Las pausas de coma (0,27 a
                              # 0,34 s en la 1003) quedan fuera: pasarlas da falsos -33/-34 y
                              # rechaza una pieza sana (medido el 18/09 con la 1002).
ZONA = (95, 930, 200, 1586)   # x0, x1, y0, y1 - zona segura de TikTok

# --- Control 8 (v6). Calibrado el 22/09/2026 sobre cuatro piezas reales de F15 -------------
#   1003 81,0 % / mayor hueco 1,52 s | 1002 81,0 % / 1,51 s | 1004 84,0 % / 1,10 s
#   1000 75,6 % / 1,54 s   <- la peor pieza real queda 10 puntos por encima del piso
# y contra la 1003 mutilada a proposito: cola muda 44,4 % / 15,07 s y hueco interior
# 49,3 % / 12,01 s. Las dos reprueban. El hueco mas largo de una pieza sana es SIEMPRE la
# cola del cierre (~1,5 s), asi que el tope de 3,0 s deja el doble de margen.
COBERTURA_MIN = 0.65          # fraccion minima de la pieza que tiene que llevar voz
VOZ_HUECO_MAX = 3.0           # s - ningun tramo sin voz puede durar mas, ni en medio ni al final
VOZ_NOISE_DB = -35.0          # umbral con el que se decide "aqui no hay voz". Mas bajo que el
                              # -25 dB de `cortes_auto`: aquel quiere encontrar la pausa entera,
                              # este quiere no contar como muda una respiracion o la cola de un
                              # fonema (-24,2 dBFS en la 1004)
VOZ_MIN_HUECO = 0.30          # s - por debajo de esto es respiracion, no es un hueco

# Regla dura 2-ter: lo que dice la puerta cuando le falta el guion. No es un aviso, es un NO.
FALTA_GUION = ("SIN GUION: los controles 6 y 7 (contenido de la voz) NO se pueden correr, "
               "asi que la pieza NO SE SUBE. Regla dura 2-ter. Para mirar una pieza ya "
               "publicada sin guion, usar auditar(), que no sube nada.")
FALTA_CORTES = ("SIN EMPALMES MEDIBLES: el control 4 no encontro ninguna pausa entre tramos, "
                "asi que nadie puede afirmar que las uniones esten limpias y la pieza NO SE "
                "SUBE. Regla dura 2-ter. En una pieza de REACCION esto es lo esperable si se "
                "le pasa el mp4: el audio del noticiero tapa las pausas. Hay que darle el mp3 "
                "de la voz en `media_voz`.")
FALTA_MEDIA = ("MEDIA ILEGIBLE: no se pudo leer la duracion, asi que el control 8 no puede decir "
               "que fraccion de la pieza lleva voz y la pieza NO SE SUBE. Regla dura 2-ter.")
FALTA_WHISPER = ("faster-whisper NO esta instalado: el control 7 no se puede correr, asi que "
                 "la pieza NO SE SUBE. `pip install -q faster-whisper`. Regla dura 2-ter.")

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


def cortes_auto(media, noise=UNION_NOISE_DB, min_pausa=UNION_MIN_PAUSA):
    """Encuentra sola los empalmes entre tramos. Devuelve (cortes, pausas).

    Existe porque hasta hoy `uniones()` se apagaba con no pasarle los cortes, y cada receta
    tenia que calcularlos por su cuenta. Un control que depende de que el llamador se acuerde
    de alimentarlo es un control opcional.

    silencedetect a -25 dB sobre la MISMA media que se va a medir; se queda con las pausas de
    >= 0,6 s y descarta la que toca el final del archivo (la cola de silencio no es un empalme).
    El corte es el centro de la pausa. Al detectar y medir sobre el mismo archivo desaparece el
    LEAD de 0,5 s de la regla dura 6: existia solo porque la pausa se buscaba en el mp3 y se
    media en el mp4, y esa diferencia de origen era una fuente de error, no un ajuste.

    ⚠️ El CENTRO de la pausa es una convencion, no la costura. La v4 lo trataba como si fuera
    el empalme y medio 0,24 s a su alrededor; el chasquido puede caer en cualquier punto de la
    pausa. Por eso `uniones()` v5 usa `pausas`, no `cortes`: ver su docstring.

    ⚠️ Y descarta la cola de silencio del final, que es CORRECTO para buscar empalmes y es
    exactamente donde se esconde una pieza con la segunda mitad muda. Ese hueco lo mide el
    control 8 (`huecos_voz`), que no descarta nada de la linea de tiempo. Ver el v6 de arriba.

    Medido el 20/09 sobre la 1003 (`0b199268-...`), guion de 5 tramos: encuentra exactamente los
    4 empalmes (6,41 · 12,94 · 18,31 · 24,60 s) y deja fuera las 3 pausas de coma de 0,27-0,34 s.
    """
    r = _sh(f'ffmpeg -hide_banner -nostats -i "{media}" '
            f'-af silencedetect=noise={noise}dB:d=0.25 -f null - 2>&1')
    txt = r.stderr + r.stdout
    ds = _sh(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{media}"').stdout
    total = float(ds.strip()) if ds.strip() else 0.0
    pausas, ini = [], None
    for m in re.finditer(r"silence_(start|end):\s*(-?[\d.]+)", txt):
        if m.group(1) == "start":
            ini = float(m.group(2))
        elif ini is not None:
            fin = float(m.group(2))
            if fin - ini >= min_pausa and not (total and fin >= total - 0.05):
                pausas.append((round(ini, 3), round(fin, 3)))
            ini = None
    return [round((a + b) / 2, 3) for a, b in pausas], pausas


def uniones(mp4, cortes=None, media_voz=None, saltar_primero=False):
    """Control 4. Pico de cada empalme entre tramos; un chasquido se oye como pico sobre -35 dBFS.

    20/09/2026 - SE APAGABA SOLO: `if not cortes: return True, []` aprobaba una pieza cuyos
    empalmes nadie habia medido. Cerrado en la v4 con `cortes_auto`.

    21/09/2026 - MEDIA UNA RENDIJA Y LA LLAMABA "EL EMPALME". La v4 media `max_volume` en una
    ventana de +-0,12 s centrada en el corte, y `cortes_auto` define el corte como el CENTRO de
    la pausa. Las pausas entre tramos duran ~1,1 s: el control miraba 0,24 s de 1,1 s y daba
    veredicto sobre los otros 0,86 s -el 78 % de la pausa- sin haberlos abierto. Medido sobre la
    1004 (`17d36226-...`), pausa 25,43-26,59 s:

        v4:  ventana 25,89-26,13  ->  -50,1 dBFS  ->  "empalme limpio"
        real: hay un transitorio en 26,43-26,48  ->  -33,4 dBFS, sobre el tope de -35

    El numero de la v4 era cierto y era del intervalo equivocado. Es el mismo defecto de FORMA
    que el del 19/09 (plegar la tilde que se busca) y el del 20/09 (aprobar sin medir): el
    control contesta una pregunta que no tiene con que contestar.

    ⚠️ 22/09/2026 - ESTE CONTROL NO ES EL DE LA SEGUNDA MITAD MUDA. La v4 y la v5 decian que si,
    "porque ese defecto vive DENTRO de una pausa". Medido: es falso. Este control mide el TECHO
    de la pausa -un pico que SOBRA- y la segunda mitad muda es un defecto de PISO. El silencio
    saca aqui la mejor nota posible: con un hueco mudo de 11,7 s en el medio de la 1003, este
    control lo midio como un empalme y lo puntuo -91,0 dBFS, la union mas limpia de la pieza.
    Ese defecto lo caza el CONTROL 8 (`cobertura_voz`), no este. Regla dura 2-quinquies.

    Desde la v5, en modo automatico se barre la pausa ENTERA, descontando `GUARDA_PAUSA` en cada
    borde (ahi esta la cola del ultimo fonema, que marca -24 dBFS y no es un chasquido). Cuando
    los cortes se pasan a mano se sigue midiendo la ventana de +-0,12 s -un `tramos.json` trae la
    costura exacta y ahi la ventana es lo correcto- pero el informe lo DICE en `cobertura`:
    ningun lector puede volver a leer un barrido parcial como si fuera la pausa completa.

    media_voz:      en REACCION, el mp3 de la voz. Se detecta Y se mide sobre el, no sobre el
                    mp4: el audio del noticiero tapa las pausas.
    saltar_primero: en REACCION, el primer empalme interior lleva el noticiero encima y no es
                    defecto (el `tramos[2:-1]` de la receta).
    """
    media = media_voz or mp4
    auto = not cortes
    tramos = []                      # [(ini, fin)] de lo que REALMENTE se mide
    if auto:
        cortes, pausas = cortes_auto(media)
        if saltar_primero:
            cortes, pausas = cortes[1:], pausas[1:]
        for (a, b) in pausas:
            ia, ib = a + GUARDA_PAUSA, b - GUARDA_PAUSA
            if ib > ia:
                tramos.append((round(ia, 3), round(ib, 3)))
    else:
        for t in cortes:
            tramos.append((round(max(0.0, float(t) - VENTANA_UNION), 3),
                           round(float(t) + VENTANA_UNION, 3)))
    if not tramos:
        return False, FALTA_CORTES
    peor, detalle, donde = -999.0, [], []
    for (ia, ib) in tramos:
        r = _sh(f'ffmpeg -hide_banner -nostats -ss {ia:.3f} -t {ib - ia:.3f} '
                f'-i "{media}" -af volumedetect -f null - 2>&1')
        m = re.search(r"max_volume:\s*(-?[\d.]+) dB", r.stderr + r.stdout)
        v = float(m.group(1)) if m else -999.0
        detalle.append(round(v, 1))
        donde.append([ia, ib])
        peor = max(peor, v)
    barrido = round(sum(b - a for a, b in tramos), 2)
    return peor <= UNION_MAX_DBFS, {
        "empalmes": len(tramos), "cortes": cortes, "dbfs": detalle, "peor": round(peor, 1),
        "origen": "auto" if auto else "dados",
        "cobertura": ("pausa completa menos %.2f s por borde" % GUARDA_PAUSA) if auto
                     else ("PARCIAL: ventana de +-%.2f s en torno al corte dado; lo que pase "
                           "en el resto de la pausa NO esta medido" % VENTANA_UNION),
        "barrido_s": barrido, "intervalos": donde,
        "medido_en": os.path.basename(media)}


def huecos_voz(media, noise=VOZ_NOISE_DB, dmin=VOZ_MIN_HUECO):
    """Todos los tramos SIN voz de la pieza, LA COLA INCLUIDA. Devuelve (huecos, duracion).

    Es a proposito lo contrario de `cortes_auto()`: aquella busca los empalmes ENTRE tramos y por
    eso tira dos cosas a la basura -las pausas cortas y el silencio que toca el final del
    archivo-. El hueco que le importa al control 8 es justamente el que aquella descarta: la
    pieza con la segunda mitad muda termina en un silencio de 15 s que `cortes_auto` lee como
    "cola" y por eso ni siquiera devuelve.
    """
    r = _sh(f'ffmpeg -hide_banner -nostats -i "{media}" '
            f'-af silencedetect=noise={noise}dB:d={dmin} -f null - 2>&1')
    txt = r.stderr + r.stdout
    ds = _sh(f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{media}"').stdout
    total = float(ds.strip()) if ds.strip() else 0.0
    hue, ini = [], None
    for m in re.finditer(r"silence_(start|end):\s*(-?[\d.]+)", txt):
        if m.group(1) == "start":
            ini = float(m.group(2))
        elif ini is not None:
            hue.append((round(ini, 2), round(float(m.group(2)), 2)))
            ini = None
    if ini is not None:              # hueco que nunca cierra = llega hasta el final del archivo
        hue.append((round(ini, 2), round(total, 2)))
    return hue, total


def cobertura_voz(mp4, media_voz=None):
    """Control 8 - CUANTA pieza lleva voz. BLOQUEA. Es el PISO del control 4.

    22/09/2026 - LOS SIETE CONTROLES MEDIAN TECHOS. La 1003 con el audio silenciado del segundo
    16 en adelante -el defecto de la segunda mitad muda, el segundo de los tres que salieron al
    aire- pasaba la puerta v5 entera, con `pasa: True` y `falla: []`. El control 4 no lo ve
    porque busca un PICO por encima de -35 dBFS dentro de una pausa, y el silencio saca su mejor
    nota: en la variante con el hueco en el medio puntuo los 11,7 s mudos como la union mas
    limpia de la pieza, -91,0 dBFS. El volumen no lo ve porque es un promedio sobre el archivo
    entero. El control 7 no lo ve porque bloquea por n-tilde mal OIDA, y una palabra que no suena
    nunca no esta mal oida. Este control hace la pregunta que faltaba: no si algo suena mal, sino
    si la voz esta DONDE TIENE QUE ESTAR, a lo largo de toda la linea de tiempo.

    Mide sobre la misma media que el control 4 (`media_voz or mp4`), asi que en REACCION hay que
    pasarle el mp3 de la voz: sobre el mp4 el audio del noticiero tapa los huecos y la cobertura
    da ~100 % aunque la voz se haya caido entera.
    """
    media = media_voz or mp4
    hue, total = huecos_voz(media)
    if total <= 0:                                        # regla dura 2-ter: falla CERRADA
        return False, FALTA_MEDIA
    mudo = round(sum(b - a for a, b in hue), 2)
    cob = round((total - mudo) / total, 3)
    mayor = round(max((b - a for a, b in hue), default=0.0), 2)
    cola = round(total - hue[-1][0], 2) if hue and hue[-1][1] >= total - 0.05 else 0.0
    return (cob >= COBERTURA_MIN and mayor <= VOZ_HUECO_MAX), {
        "cobertura_voz": cob, "minimo": COBERTURA_MIN,
        "mudo_s": mudo, "mayor_hueco_s": mayor, "tope_hueco_s": VOZ_HUECO_MAX,
        "cola_muda_s": cola, "huecos": hue, "duracion_s": round(total, 2),
        "cobertura": "la LINEA DE TIEMPO ENTERA, de 0 a la duracion, sin descartar la cola",
        "medido_en": os.path.basename(media)}


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

    22/09/2026: un guion VACIO devolvia True -cero palabras, cero palabras malas-, o sea el
    objeto vacio sacaba la mejor nota que este control sabe dar. Regla dura 2-quinquies: ahora
    bloquea igual que si no lo hubieran pasado.
    """
    if not (guion or "").strip():      # objeto vacio, mejor nota: cero palabras, cero malas.
        return False, FALTA_GUION      # regla dura 2-quinquies (v6)
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


def _transcribir(media, modelo="small"):
    """Transcribe con faster-whisper. Devuelve (texto, None) o (None, motivo del fallo)."""
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return None, FALTA_WHISPER
    wav = os.path.splitext(media)[0] + ".ctrl.wav"
    _sh(f'ffmpeg -y -v error -i "{media}" -vn -ac 1 -ar 16000 "{wav}"')
    m = WhisperModel(modelo, device="cpu", compute_type="int8")
    segs, _ = m.transcribe(wav, language="es", vad_filter=False, word_timestamps=True)
    return " ".join(s.text for s in segs).strip(), None


# PALABRAS CRITICAS (19/09/2026) - terminos juridicos que TIENEN que oirse como se escriben.
#
# Medido en la primera tanda real de piezas F15, transcribiendo el mp4 publicable:
#     guion "conducir en estado de ebriedad"  ->  se oye "en estado de heredad"
#     guion "se llama falta de probidad"      ->  se oye "se llama falta de providad"
#
# Las dos las CAZO el control 7 y las dos las dejo pasar, porque solo bloquea por n-tilde. Esa
# regla es correcta para palabras corrientes -whisper se equivoca solo y bloquear por cada
# rareza re-renderiza piezas sanas-, pero no para estas: "falta de providad" y "estado de
# heredad" no son un desliz del transcriptor, son la pieza diciendo una palabra que no existe.
# Y las dice un estudio juridico citando la ley.
#
# El criterio para entrar a esta lista: termino tecnico cuyo error cambia o destruye el sentido
# juridico, y que por raro es dificil que whisper invente. No entran palabras comunes.
PALABRAS_CRITICAS = {
    "ebriedad", "probidad", "irrenunciable", "irrenunciables", "finiquito", "indemnizacion",
    "prescripcion", "flagrante", "flagrancia", "imputado", "querella", "usufructo",
    "subordinacion", "cotizaciones", "negligencia", "fianza", "arrendamiento", "microtrafico",
    "estupefacientes", "sicotropicas", "emplazamiento", "caducidad", "menoscabo",
}


def voz(media, guion, modelo="small"):
    """Control 7 - lo que se OYE contra el guion. BLOQUEA SOLO por n-tilde perdida.

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

    ⚠️ 22/09/2026 - LO QUE ESTE CONTROL NO PUEDE VER: bloquea por n-tilde mal OIDA, y una
    palabra que NO SUENA NUNCA no esta mal oida. Con la 1003 silenciada desde el segundo 16,
    "años" desaparecio junto con el tramo 4 y `enie_perdida` volvio vacia. El recall de la
    pasada plegada lo habria notado, pero INFORMA por decision expresa (bloquear por el
    re-renderiza piezas sanas). La voz que FALTA es del control 8, no de aqui.

    v3: sin guion o sin faster-whisper devuelve False (BLOQUEA). Antes devolvia True y None
    respectivamente, y en los dos casos la pieza subia con el control de voz apagado.
    """
    if not guion:
        return False, FALTA_GUION
    dicho, fallo = _transcribir(media, modelo)
    if fallo:
        return False, fallo

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
    # BLOQUEA: los terminos juridicos criticos tienen que oirse. Misma forma que la n-tilde,
    # distinta razon: alli el defecto es del TTS al leer; aqui es el TTS inventando una palabra.
    criticas = []
    for w in sorted({w for w in _tok(guion) if _plano(w) in PALABRAS_CRITICAS}):
        if _plano(w) not in oido_plano:
            criticas.append(w)

    return (not perdidas and not criticas), {"enie_perdida": perdidas,
                                             "termino_critico_no_oido": criticas,
                                             "fuera_del_guion": fuera[:15],
                            "dicho": dicho[:500]}


def auditar(mp4, media_voz=None, modelo="small"):
    """QC de una pieza YA PUBLICADA, cuando el guion ya no existe. NO SUBE NADA.

    Por que existe (19/09/2026): el guion vive en `urls/<n>.txt` dentro del sandbox, y el
    sandbox se descarta ~10 s despues de la llamada que lo escribio. Dias despues, la revision
    que audita lo que salio al aire tiene el mp4 de CloudFront y NADA con que compararlo, asi
    que los controles 6 y 7 son inaplicables por construccion. Antes de v3 eso se veia como
    "control omitido" y la pieza figuraba aprobada; desde v3 `controlar()` lo rechaza. Este es
    el camino correcto para ese caso, y es explicitamente una auditoria, no una puerta.

    Como caza la 967b SIN guion: no compara contra nada, busca en lo que se OYE las palabras
    que en estos guiones SIEMPRE llevan n-tilde (`anos`, `dano`, `senor`, `nino`...) y sus
    formas pegadas (`poranos` = `por` + `anos`). Si la pieza dice "por anos de servicio", aqui
    sale `anos` aunque nadie tenga ya el guion. Es lo que el QC del 19/09 tuvo que escribir a
    mano para poder revisar las tres piezas del 18/09.

    v5 (21/09): la auditoria corre tambien el CONTROL 4 con la cobertura nueva.

    v6 (22/09): y el CONTROL 8, que es el que de verdad caza la segunda mitad muda. La v5 sumo
    el control 4 creyendo que era ese; medido, no lo es -el control 4 mide el techo de la pausa
    y ese defecto es de piso-. Una pieza medio muda YA PUBLICADA se detecta aqui.
    """
    dicho, fallo = _transcribir(media_voz or mp4, modelo)
    if fallo:
        return {"pieza": os.path.basename(mp4), "error": fallo}
    toks = _tok(dicho)
    sueltas = sorted({w for w in toks if w in SIN_ENIE})
    pegadas = sorted({w for w in toks if w not in SIN_ENIE and
                      any(w != k and w.endswith(k) and len(w) - len(k) >= 2 for k in SIN_ENIE)})
    tildes = sorted({w for w in toks if w in SIN_TILDE or
                     re.fullmatch(r"[a-z]{4,}cion", w) or re.fullmatch(r"[a-z]{4,}sion", w)})
    a_ok, a = audio(mp4)
    d_ok, d = duracion(mp4)
    v_ok, v = volumen(mp4)
    u_ok, u = uniones(mp4, None, media_voz=media_voz)
    c_ok, c = cobertura_voz(mp4, media_voz=media_voz)
    return {"pieza": os.path.basename(mp4),
            "audio": {"ok": a_ok, "valor": a, "esperado": AUDIO_OK},
            "duracion": {"ok": d_ok, "valor": d, "franja": [DUR_MIN, DUR_MAX]},
            "volumen": {"ok": v_ok, "valor": v, "franja": [VOL_MIN, VOL_MAX]},
            "uniones": {"ok": u_ok, "valor": u, "tope": UNION_MAX_DBFS},
            "cobertura_voz": {"ok": c_ok, "valor": c, "minimo": COBERTURA_MIN},
            "enie": {"ok": not (sueltas or pegadas), "sueltas": sueltas, "pegadas": pegadas},
            "tildes_oidas": {"ok": not tildes, "valor": tildes},
            "dicho": dicho,
            "nota": "AUDITORIA sin guion: no reemplaza a los controles 6 y 7 ni habilita subir."}


def controlar(mp4, dmin=DUR_MIN, dmax=DUR_MAX, cortes=None, guion=None, media_voz=None,
              exigir_guion=True, saltar_primero=False):
    """Corre los controles y devuelve el informe. 'pasa' es la conjuncion de los que BLOQUEAN.

    guion:         texto completo de la voz. OBLIGATORIO: sin el, 'pasa' es False (v3).
    media_voz:     en piezas de REACCION, el mp3 de la voz; el control 7 lo escucha en vez del mp4.
    exigir_guion:  solo se pone en False para mirar una pieza a sabiendas de que los controles de
                   contenido no corren. No lo usa ninguna receta de produccion: lo que necesita
                   revisar algo ya publicado es `auditar()`. Dejarlo en False para poder subir es
                   exactamente el agujero que v3 vino a tapar (regla dura 2-ter).
    """
    a_ok, a = audio(mp4)
    d_ok, d = duracion(mp4, dmin, dmax)
    v_ok, v = volumen(mp4)
    u_ok, u = uniones(mp4, cortes, media_voz=media_voz, saltar_primero=saltar_primero)
    c_ok, c = cobertura_voz(mp4, media_voz=media_voz)
    _, p = pantalla(mp4)
    if guion:
        t_ok, t = texto(guion)
        z_ok, z = voz(media_voz or mp4, guion)
    elif exigir_guion:
        t_ok, t = False, FALTA_GUION
        z_ok, z = False, FALTA_GUION
    else:
        t_ok, t = True, "sin guion y exigir_guion=False; control 6 omitido - NO habilita subir"
        z_ok, z = True, "sin guion y exigir_guion=False; control 7 omitido - NO habilita subir"
    r = {"pieza": os.path.basename(mp4),
         "audio": {"ok": a_ok, "valor": a, "esperado": AUDIO_OK},
         "duracion": {"ok": d_ok, "valor": d, "franja": [dmin, dmax]},
         "volumen": {"ok": v_ok, "valor": v, "franja": [VOL_MIN, VOL_MAX]},
         "uniones": {"ok": u_ok, "valor": u, "tope": UNION_MAX_DBFS},
         "cobertura_voz": {"ok": c_ok, "valor": c, "minimo": COBERTURA_MIN},
         "pantalla_chica": {"ok": None, "valor": p},
         "texto": {"ok": t_ok, "valor": t},
         "voz": {"ok": z_ok, "valor": z},
         "pasa": bool(a_ok and d_ok and v_ok and u_ok and c_ok and t_ok and z_ok)}
    r["falla"] = [k for k in ("audio", "duracion", "volumen", "uniones", "cobertura_voz",
                              "texto", "voz")
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
    Devuelve el codigo HTTP (200 = subida buena).

    v3: sin guion esto ya no sube. Si una receta llega aqui sin el, el error dice que falta el
    guion, no que el video este malo: el video puede estar perfecto y aun asi nadie escucho
    lo que dice."""
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
    ap.add_argument("--guion", default="", help="archivo urls/<n>.txt; OBLIGATORIO para subir")
    ap.add_argument("--voz", default="", help="mp3 de la voz; en piezas de reaccion, en vez del mp4")
    ap.add_argument("--solo-texto", default="", help="corre SOLO el control 6 sobre ese archivo")
    ap.add_argument("--auditar", action="store_true",
                    help="QC de una pieza YA PUBLICADA sin guion; no sube nada")
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

    # Auditoria de lo ya publicado: sin guion, sin subida, sin veredicto de puerta.
    if a.auditar:
        r = auditar(a.mp4, a.voz or None)
        print(json.dumps(r, ensure_ascii=False, indent=1))
        malo = (bool(r.get("error")) or r.get("enie", {}).get("ok") is False
                or r.get("uniones", {}).get("ok") is False
                or r.get("cobertura_voz", {}).get("ok") is False)
        if malo:
            print("AUDITORIA CON HALLAZGOS -> anotar el defecto; NO se republica lo que ya salio",
                  file=sys.stderr)
            return 1
        return 0

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
        if not guion:
            print("FALTA EL GUION: pasalo con --guion urls/<n>.txt. Para revisar una pieza ya "
                  "publicada sin guion, usa --auditar.", file=sys.stderr)
        return 1
    if a.put:
        print("PUT", subir(mp4, a.put, r))
    return 0


if __name__ == "__main__":
    sys.exit(main())
