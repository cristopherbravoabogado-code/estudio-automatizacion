# RECETA — Motor de video 100% nube (v1 05/09/2026 · v2 05/09/2026 · voz Eleven por tramos 08/09/2026 · **v3 audio 11/09/2026** · **v4 pantalla chica 11/09/2026** · **v5 zona segura medida + canal único 12/09/2026** · **v6 control de stock 15/09/2026** · **v7 control de voz 16/09/2026** · **v8 cama musical con ducking 18/09/2026** · **v9 ningún control se apaga por omisión 20/09/2026** · **v10 un control declara qué parte miró 21/09/2026** · **v11 qué nota le pone el control al objeto vacío 22/09/2026** · **v12 movimiento real sobre foto fija 23/09/2026**)

Produce y publica TikToks del Estudio Jurídico San Bernardo sin tocar el Mac ni Drive.
Probada de punta a punta con el lote 09 (901-908): 8 videos generados, alojados y programados en ~40 minutos.

**Para PUBLICAR (y para fijar una hora) ver `motor/PUBLICAR.md`. Para el encuadre medido ver `motor/ZONA-SEGURA-v5.md`. Para la cama musical ver `motor/REGLA-6-MUSICA.md`. Para el movimiento de las fotos ver `motor/REGLA-7-MOVIMIENTO.md`.**

---

## ⛔ LAS SIETE REGLAS DURAS (si se rompe una, la pieza no sale)

### 1. NUNCA una etiqueta `<break>` en el texto que va a ElevenLabs
`eleven_multilingual_v2` a veces **vocaliza** la etiqueta en vez de callar. Detalle y medición en "Lo que NO hacer".
Sustituto: un nodo tts por tramo + silencio real con `anullsrc`.

### 2. TILDES SIEMPRE — en pantalla y en el texto de la voz (regla del 07/09/2026)
Escribir los guiones **sin tildes** "para evitar problemas de fuente" **corrompe la VOZ**, no solo el rótulo:
Kokoro leyó *"indemnización por anos de servicio"*. Las tres fuentes del motor (Montserrat-ExtraBold,
DejaVuSans, DejaVuSans-Bold) tienen tildes, ñ, ¿ y ¡: verificado glifo por glifo.
- Los textos van **siempre acentuados**: en `pieza.json` (gancho, títulos, detalles, cierre) y en `urls/<n>.txt`.
- Los archivos se escriben en UTF-8, con heredoc entre comillas (`<<'TXT'`), nunca con escapes.
- Números que la voz debe leer bien van **en palabras** en `urls/<n>.txt` ("ciento sesenta y uno A",
  "diecinueve mil novecientos setenta y tres") y en **cifras** en la lámina. Son dos textos distintos a propósito.
- Palabras que el TTS español pronuncia mal (p. ej. "mall") se reemplazan por su equivalente
  ("la tienda", "el supermercado"): el karaoke sale de transcribir el audio, así que no sirve escribirlas fonéticamente.

**2-bis. ESTA REGLA ESTUVO ESCRITA Y SIN IMPLEMENTAR OCHO DÍAS, Y VOLVIÓ A SALIR AL AIRE (medido el 16/09/2026).**
La pieza **967b** (`78e2d3d8-…`, publicada el 15/09 a las 12:11) dice *"indemnización por **anos** de servicio"*:
el ejemplo textual con el que esta regla está escrita desde el 07/09. Medido sobre el mp4 publicado con
faster-whisper `medium`, que transcribe "indemnización" acentuada y aun así escribe "anos" — no es error del
transcriptor, es lo que la pieza dice. Dos causas sumadas, las dos ya corregidas:
- **`control.py` no tenía ningún control de voz.** Sus cinco controles miraban el continente (audio, duración,
  volumen, uniones, encuadre) y ninguno el CONTENIDO. La transcripción contra el guion se hacía **a mano en cada
  corrida**, así que la corrida que no la hacía publicaba el defecto. Es la misma lección de la regla 3-ter:
  **medir no es controlar si el resultado no puede bloquear la subida** — y un control que depende de que alguien
  se acuerde de correrlo no es un control.
- **El procedimiento escrito que debía cazarlo estaba roto de origen.** Ver el paso 3 de "Control de audio
  obligatorio": mandaba plegar las tildes antes de comparar, y plegadas "anos" y "años" son el mismo token.
- ✅ **Control 6 — `control.texto(guion)`, ANTES del TTS. BLOQUEA.** Determinista y sin falsos positivos: lista de
  palabras que perdieron la ñ (`anos`, `dano`, `senor`, `nino`, `dueno`…), lista de tildes obligatorias
  (`articulo`, `codigo`, `dia`…) y la regla **-ción / -sión singular**, que en español SIEMPRE va acentuada
  (el plural no la lleva: "indemnizaciones", "acciones", y por eso no se toca). Mirar el texto sale gratis;
  descubrirlo después cuesta la síntesis, el render y —si nadie escucha la pieza— la publicación.
- ✅ **Control 7 — `control.voz(media, guion)`, después del render. BLOQUEA solo por ñ.** Ver paso 3b.
- ⛔ **Una pieza que reprueba el control 6 o el 7 se REHACE desde el guion.** El remux arregla el contenedor de
  audio, no lo que la voz dice. Y si ya salió al aire, no se republica (regla de Cristopher del 07/09).

**2-ter. NINGÚN CONTROL SE APAGA POR OMISIÓN (norma del 20/09/2026).**
Un control que se desactiva solo cuando el llamador no le pasa un dato no es un control: es una intención con
nombre de función. Si le falta lo que necesita para medir, **falla CERRADA** — `pasa: False` y la pieza no sube.
Ya pasó dos veces, con el mismo mecanismo y un control de distancia:
- **19/09 — controles 6 y 7.** `controlar()` los omitía si no se le pasaba el guion y devolvía `pasa: True`
  igual. Corregido en `control.py` v3: sin guion, `pasa: False`. Para mirar una pieza ya publicada sin guion
  existe `auditar()`, que **no sube nada**.
- **20/09 — control 4 (uniones).** `uniones()` empezaba con `if not cortes: return True, []`. Medido sobre la
  **1003** (`0b199268-…`, alojada y sin publicar): `controlar()` sin cortes devolvía
  `uniones {'ok': True, 'valor': []}` y `pasa: True` — es decir, la puerta aprobaba una pieza cuyos empalmes
  nadie había medido. Y no era teórico: `produce.py` pasa `cortes = []` cuando le falta el
  `<id>.mp3.tramos.json`, y `build_sv.py` pasa `t0[1:]`, que puede venir vacío. Es justamente el control que
  corresponde al defecto de **la pieza con la segunda mitad muda**.
  - ✅ Corregido en `control.py` **v4**: `cortes_auto(media)` **encuentra los empalmes sola** (silencedetect a
    −25 dB, se queda con las pausas de ≥ 0,6 s y descarta la cola de silencio del final; el corte es el centro
    de la pausa). `uniones()` sin cortes los busca; si no aparece ninguno, **`pasa: False`**.
  - 🔑 **Se acabó el LEAD de 0,5 s** de la regla dura 6: existía solo porque la pausa se buscaba en el mp3 y se
    medía en el mp4. Ahora se detecta y se mide **sobre el mismo archivo**, así que no hay desfase que corregir.
  - ⚠️ En **REACCIÓN** se le pasa `media_voz` (el mp3 de la voz) y `saltar_primero=True`.
    ⛔ **Hasta el 21/09 aquí decía que si se le pasa el mp4 "no encuentra empalmes y bloquea diciéndolo — que es
    la conducta correcta". ESO ES FALSO y estaba escrito sin medirlo.** Medido el 21/09 sobre la **1004**
    (`17d36226-…`, F15 de reacción): con el mp4 **encuentra 4 empalmes** (5,89 · 13,61 · 18,33 · 26,01 s) y
    **emite veredicto igual**. La red de seguridad que esta línea prometía no existía: pasarle el mp4 no hace que
    el control se abstenga, hace que mida otra cosa y no lo diga. Se corrige con la `cobertura` de la 2-quater,
    y **la obligación sigue siendo pasarle el mp3**.
  - Verificado el 20/09 contra la 1003: encuentra los 4 empalmes (6,41 · 12,94 · 18,31 · 24,60 s), mide
    −42,0 / −40,2 / −40,4 / −40,7 dBFS (tope −35) y deja fuera las 3 pausas de coma de 0,27-0,34 s.
- 🔑 **La prueba que hay que correrle a todo control nuevo**: llamarlo SIN el dato que necesita. Si contesta que
  sí, está roto. No basta con arreglar el caso concreto — el 19/09 se arregló el del guion mirando la voz en vez
  de la forma del defecto, y por eso el control 4 quedó abierto un día más.

**2-quater. UN CONTROL NO INFORMA SOLO SU VEREDICTO: INFORMA QUÉ PARTE DEL OBJETO MIRÓ (norma del 21/09/2026).**
La 2-ter cubre el control que se apaga. Este es el escalón siguiente y más difícil de ver: el control que **sí
corre, sí devuelve un número cierto, y el número es de otro intervalo**. Nadie lo nota, porque un control que
contesta parece un control que funciona.
- **Medido el 21/09 sobre la 1004** (`17d36226-…`, alojada, con marca `🔒 TOMANDO` y a un paso de publicarse).
  `cortes_auto` define el corte como el **centro** de la pausa, y `uniones()` v4 medía `max_volume` en una
  ventana de **±0,12 s** alrededor de ese centro. Las pausas entre tramos duran **~1,1 s**: el control abría
  **0,24 s de 1,1 s** y daba veredicto sobre los otros **0,86 s — el 78 % de la pausa — sin haberlos mirado**.
  En la cuarta pausa de esa pieza (25,43-26,59 s):

  | | intervalo medido | resultado |
  |---|---|---|
  | **v4** | 25,89-26,13 (0,24 s) | **−50,1 dBFS** → "empalme limpio" |
  | **real** | transitorio en 26,43-26,48 | **−33,4 dBFS** → sobre el tope de −35 |

  El número de la v4 **era cierto y era del intervalo equivocado**. Es un **falso PASE**, no un falso positivo:
  el modo de fallo que deja salir la pieza. Y es precisamente el control que le corresponde al segundo de los
  tres defectos que salieron al aire — **la pieza con la segunda mitad muda** —, que es un defecto que vive
  DENTRO de una pausa.
- ✅ Corregido en **`control.py` v5**: en modo automático `uniones()` barre la **pausa ENTERA** menos
  `GUARDA_PAUSA` (**0,15 s**) en cada borde, que es donde está la cola del último fonema y el ataque del
  siguiente (en la 1004 el primer instante bajo −25 dB marca **−24,2 dBFS**: eso es voz, no chasquido, y
  medirlo daría el falso positivo simétrico). El barrido sube de **0,96 s a 3,25 s** en una pieza de 5 tramos.
- ✅ El informe ahora trae **`cobertura`**, **`barrido_s`** e **`intervalos`**. Con los cortes dados a mano —un
  `tramos.json` trae la costura exacta y ahí la ventana ±0,12 s es lo correcto— el informe lo declara:
  *"PARCIAL: … lo que pase en el resto de la pausa NO está medido"*. Nadie puede volver a leer un barrido
  parcial como si fuera la pausa completa.
- ✅ **`auditar()` corre ahora también el control 4.** Hasta el 21/09 la auditoría de una pieza ya publicada ni
  siquiera miraba las uniones, que es donde vive el defecto de la segunda mitad muda.
- 🔑 **La prueba que hay que correrle a todo control nuevo, además de la de la 2-ter**: preguntarle **qué
  fracción del objeto abrió**. Si mide una muestra y reporta como si fuera el todo, está roto aunque su número
  sea exacto. Un control tiene que poder decir su cobertura, y esa cobertura tiene que ir en el informe, no en
  la cabeza de quien lo escribió.
- 🔑 **Tres días, tres defectos, la misma FORMA**: 19/09 plegar la tilde que se busca · 20/09 aprobar sin medir ·
  21/09 medir una rendija y llamarla el todo. Las tres veces el arreglo anterior se escribió mirando **el caso
  concreto** en vez de **la forma del defecto**, y por eso el siguiente estaba servido. Cuando se corrija un
  control, la pregunta no es "¿arreglé esto?" sino **"¿qué otro control tiene esta misma forma?"** — y hay que
  ir a mirarlo en la misma corrida.

**2-quinquies. UN CONTROL QUE SOLO MIDE TECHOS ES CIEGO A LO QUE FALTA (norma del 22/09/2026).**
A todo control hay que preguntarle **qué nota le pone al objeto VACÍO**. Si el silencio, el cuadro en negro o el
texto en blanco sacan su mejor nota, el control mide en una sola dirección y le falta el piso.
- **Medido el 22/09/2026 sobre la 1003** (`0b199268-…`, limpia en los siete controles) con el audio silenciado a
  partir del segundo 16 — o sea, el segundo de los tres defectos que salieron al aire, la pieza con la segunda
  mitad muda, reproducido tal cual contra la puerta v5:

  ```
  controlar("mudo_cola.mp4", guion=guion) -> pasa: True, falla: []
  ```

  Los siete controles la aprobaron: audio `aac,48000,2` ok · duración 31,04 s ok · volumen −17,7 dB ok ·
  uniones ok (2 empalmes, −35,0 / −38,7) · voz ok con `enie_perdida: []`, aunque el guion dice "años" en el
  tramo 4, que es justamente el que está mudo.
- **Por qué ninguno lo vio:**
  - El **control 4** mide el TECHO de la pausa — busca un pico por encima de −35 dBFS — y este defecto es de
    PISO. El silencio no solo no lo reprueba: en la variante con el hueco en medio, midió los 11,7 s mudos como
    si fueran un empalme y los puntuó **−91,0 dBFS, la unión más limpia de la pieza**. Los docstrings de la v4 y
    la v5 afirmaban que a este control le correspondía la segunda mitad muda "porque vive dentro de una pausa":
    era falso y ya está corregido en el repo.
  - El **volumen** es un PROMEDIO sobre el archivo entero: media pieza muda solo lo baja de −15,0 a −17,7 dB,
    adentro de la franja.
  - El **control 7** bloquea por ñ mal OÍDA, y una palabra que no suena nunca no está mal oída. El recall de la
    pasada plegada sí lo habría notado, pero informa y no bloquea por decisión expresa.
- 🔑 **Los siete controles preguntaban si algo SOBRA o suena mal. Ninguno preguntaba si algo FALTA.**
- ✅ **CONTROL 8 — COBERTURA DE VOZ** (`control.py` v6, `cobertura_voz()`): qué fracción de la LÍNEA DE TIEMPO
  ENTERA lleva voz y cuánto dura el hueco más largo, la cola incluida. BLOQUEA bajo 65 % de cobertura o con
  cualquier hueco de más de 3,0 s. Se mide sobre la misma media que el control 4, así que en **REACCIÓN** hay
  que pasarle el mp3 de la voz: sobre el mp4 el audio del noticiero tapa los huecos y la cobertura da ~100 %
  aunque la voz se haya caído entera.
- Calibrado sobre cuatro piezas reales — 1003, 1002, 1004 y 1000: cobertura 81,0 / 81,0 / 84,0 / 75,6 % y mayor
  hueco 1,52 / 1,51 / 1,10 / 1,54 s — contra las dos mutiladas a propósito: 44,4 % con 15,07 s y 49,3 % con
  12,01 s. La peor pieza sana queda 10 puntos sobre el piso y el tope de hueco deja el doble de margen.
- `huecos_voz()` es deliberadamente lo contrario de `cortes_auto()`: aquella descarta la cola de silencio del
  final porque "no es un empalme", y ahí es exactamente donde se esconde media pieza muda. El control 8 no
  descarta nada de la línea de tiempo.
- ✅ `texto("")` devolvía True — cero palabras, cero palabras malas: otro objeto vacío sacando la mejor nota.
  Ahora un guion en blanco **BLOQUEA**.
- 🔑 **LA PRUEBA QUE HAY QUE CORRERLE A TODO CONTROL NUEVO**, y a los viejos cada vez que cae uno, son ahora
  **TRES** preguntas:
  1. **(2-ter)** Llamarlo SIN el dato que necesita. Si contesta que sí, está roto.
  2. **(2-quater)** Preguntarle qué fracción del objeto abrió. Si mide una muestra y la reporta como el todo,
     está roto aunque su número sea exacto.
  3. **(2-quinquies)** Preguntarle qué nota le pone al objeto VACÍO. Si el silencio saca su mejor nota, le falta
     el piso.
- Corrida el 22/09 sobre los ocho controles: `audio` sobre un mp4 sin pista da `""` y bloquea · `duración` da
  0,0 y bloquea · `volumen` sobre silencio total da −91,0 dB y bloquea, así que su ceguera es al defecto
  PARCIAL, que es lo que cubre el control 8 · `uniones` sobre silencio TOTAL bloquea pero de rebote, porque no
  encuentra ningún empalme y cae en la 2-ter, y sobre silencio PARCIAL aprueba y encima puntúa el tramo mudo
  como la unión más limpia: ese era el agujero · `texto` con guion vacío aprobaba, corregido · `voz` sin guion
  bloquea desde la v3 · `pantalla_chica` informa y no bloquea, así que no aplica.
- 🔑 **Tres días, cuatro defectos, y la lección se repite**: el arreglo de cada día se escribió mirando el caso
  concreto y no la FORMA. Al corregir un control la pregunta no es "¿arreglé esto?" sino **"¿qué otro control
  tiene esta misma forma?"** — y hay que ir a mirarlo en la misma corrida.

### 3. AUDIO 48 kHz ESTÉREO, UNIDO CON EL FILTRO `concat` (norma del 11/09/2026)
Toda la cadena de audio corre a **48000 Hz, 2 canales**, y los tramos se empalman con el **filtro** `concat`
(no con el demuxer), que re-muestrea cada entrada antes de unirla:
```
[k:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[ak]; ... concat=n=N:v=0:a=1[out]
```
- `videolab/voz.py` v3 sintetiza, normaliza (`loudnorm=I=-16:TP=-1.5:LRA=11`) y entrega mp3 **48 kHz estéreo**;
  el silencio de unión es `anullsrc=r=48000:cl=stereo`.
- `motor/motor.py` v3 cierra el mux con `-c:a aac -b:a 192k -ar 48000 -ac 2` y **imprime el formato real**
  del mp4 al terminar (`OK salida.mp4 32.0 s audio= 48000,2`).
- Por qué: el demuxer `concat` empalma sin mirar los parámetros de cada entrada — basta que un tramo venga a
  otra frecuencia o en mono para que el empalme quede sucio. Con el filtro es imposible. Y 48 kHz estéreo es
  el formato que TikTok espera: entregarle 44,1 mono lo obliga a re-muestrear, que es calidad que se regala.

**3-bis. EL STOCK VIEJO NO CUMPLE UNA REGLA QUE NACIÓ DESPUÉS QUE ÉL (medido el 15/09/2026).**
Arreglar el código NO arregla lo ya renderizado. La regla 3 se implementó el 11/09 (`voz.py` v3 + `motor.py` v3);
todo lo anterior sigue alojado en CloudFront con el audio viejo y **la RESERVA publica desde ahí sin volver a medir**.
Medición del 15/09 sobre las 7 piezas vivas del lote: las 4 renderizadas el 11/09 o después dan `aac,48000,2`;
las 2 renderizadas el **07/09** dan **`aac,96000,1`** — mono, al doble de frecuencia. Eran justo las dos piezas de
la RESERVA (compensación económica y choque/SOAP), o sea las que el VIGILANTE publica cuando el día viene en cero:
el defecto estaba a un día seco de salir al aire. La correlación es exacta por fecha de render, no por tema.
- ✅ **Remuxear, no re-renderizar**: el video está bien, lo único malo es el contenedor de audio.
  `ffmpeg -y -i viejo.mp4 -c:v copy -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart nuevo.mp4`
  Conserva duración y encuadre (verificado: 22,20 s y 24,07 s idénticos) y cuesta ~3 s por pieza y 0 créditos.
- ⛔ **"Con control de audio limpio" caduca.** Una pieza marcada como controlada lo fue contra el control de SU día.
  Cuando cambia una regla dura, la etiqueta vieja miente. **Toda pieza de la RESERVA se re-mide con `ffprobe`
  (`codec_name,sample_rate,channels`) INMEDIATAMENTE ANTES de publicarla**, aunque la bitácora la dé por limpia.
  Son 2 segundos y es lo único que separa el stock viejo del aire.
- 🔑 **Regla general**: cuando se agregue o cambie una regla dura, la misma jugada re-mide TODO el stock alojado
  que pueda publicarse sin pasar por el motor. Si no se re-mide, la corrección solo cubre la producción futura
  y el stock viejo queda como una mina enterrada en la reserva.
  📌 **Aplicado el 21/09 con la 2-quater**: re-medidas las dos piezas alojadas con `control.py` v5. La **1003**
  sigue limpia (−35,0 en el peor empalme, justo en el tope); la **1004** —que el 20/09 nadie había medido y que
  ya tenía marca `🔒 TOMANDO`— **reprueba con −33,4 y −34,9 dBFS**. El re-medido de la reserva es lo que la
  atajó antes del aire.

**3-ter. LA REGLA 3 VIVE DENTRO DE `motor.py`, ASÍ QUE TODO LO QUE NO PASA POR `motor.py` SE LA SALTA
(medido el 15/09/2026).**
El QC del 15/09 midió las 11 piezas vivas del lote del lunes 14/09. Las **10 salidas del motor** dieron
`aac,48000,2`, 1080x1920, 23,1-30,5 s, volumen medio −17,7 a −18,1 dB y las 4 uniones entre −87 y −92 dBFS:
el motor está sano y la regla 3 se cumple sola ahí. La única que falló es la **11ª, el SUPERVIDEO A**
(`b035baf5-865a-40f0-a363-293a9c807643`, despido por IA, publicado el 14/09 a las 20:26), que salió
**`aac,48000,1` — MONO —, 60,74 s y volumen medio −19,8 dB**: rompe la regla dura 3, la regla dura 5 y la
franja de volumen, las tres a la vez. No es un motor enfermo: es que la receta de `videolab/supervideo/`
produce su mp4 por fuera de `motor.py` y **ningún control la obliga a cerrar como cierra el motor**.
- ⛔ **Ninguna pieza se publica sin haber pasado el control de audio, la produzca quien la produzca.**
  El cierre del mux es SIEMPRE `-c:a aac -b:a 192k -ar 48000 -ac 2`, y después `ffprobe` imprimiendo
  `codec_name,sample_rate,channels` — en `motor.py`, en `videolab/supervideo/` y en cualquier receta nueva.
  Una receta que no termina imprimiendo `aac,48000,2` no está terminada.
- 🔑 **Toda receta nueva nace con los controles o no nace**: formato de audio, duración en franja, volumen medio
  entre −14 y −19 dB, RMS de cada unión ≤ −35 dBFS y **los dos controles de voz de la regla 2-bis**. Copiar el
  bloque de verificación del motor es más barato que descubrir el defecto cuando la pieza ya está al aire y no se
  puede republicar. Desde el 15/09 esto no se copia: **se importa `motor/control.py`**, que es LA PUERTA.
- 📏 **El supervideo también rompe la franja de duración**: 60,7 s contra el tope de 34 s de la regla 5.
  Si el formato largo se quiere mantener, la regla 5 tiene que decirlo explícitamente con su propia franja
  medida; mientras no lo diga, un supervideo de 60 s es una pieza fuera de norma publicada sin decidirlo.

### 4. TODO EL TEXTO CON CAJA OPACA Y DENTRO DE LA ZONA SEGURA (norma del 11/09/2026)
El video no se ve en un monitor: se ve en un teléfono, comprimido, y con la interfaz de TikTok encima.
Las dos medidas del 11/09 sobre el piloto F11 (25 cuadros, OCR a tamaño completo contra OCR al 25% de escala):

**a) Caja opaca, no contorno.** Al 25% de escala sobrevivía el **29%** de las palabras con el contorno
que usábamos; con caja opaca detrás, el **100%**. n=24 intentos de palabra por estilo, 6 fondos fotográficos,
render libass real. Subir la fuente de 78 a 96 px **no cambió nada** (0,29 con contorno en ambos tamaños):
lo que decide la legibilidad es el fondo detrás de la letra, no el tamaño de la letra.
Estilo vigente en `videolab/karaoke.py` v2 — `BorderStyle 3`, `OutlineColour &H23101010` (negro al 86%), `Outline 6`:
```
Style: K,Montserrat ExtraBold,78,&H00FFFFFF,&H00FFFFFF,&H23101010,&H00101010,-1,0,0,0,100,100,0,0,3,6,0,2,95,150,560,1
```
Cuesta **0 s y 0 créditos**: es el mismo filtro `ass` de siempre.

**b) Zona segura de TikTok 1080x1920 (spec 2026): x[95,930], y[200,1586].**
Arriba 200 px se los come el buscador y las pestañas; abajo 334 px el nombre, el copy y la marquesina de audio;
a la izquierda 86 px el bisel; a la derecha 140 px la columna de avatar, corazón, comentarios y compartir.
En el piloto medido, **83 de 137 cajas de texto caían fuera** — entre ellas la línea de marca + WhatsApp,
que estaba en y=1770, debajo del copy de TikTok: **el CTA con el teléfono existía en el archivo y nadie lo veía nunca**.
Corregido en `videolab/ensayo.py` v2 (etiqueta 150→215, marca 1770→1470, placas 60..1020 → 95..930, subtítulo de placa 46→58 px).

**c) Umbral de tamaño medido**: bajo 40 px de alto de caja sobrevive el 22% de las palabras al 25% de escala;
sobre 80 px, el 85%. Ningún texto de una pieza baja de 80 px de alto salvo que lleve caja opaca.

**d) La zona segura también es regla del MOTOR — y el motor NO la cumplía (medido el 12/09/2026).**
El v4 "corrigió" `motor/motor.py` de memoria, sin medirlo. La primera corrida real de `pantalla_chica.py`
sobre una pieza del motor dio **236 cajas de texto fuera de la zona segura y recall 0,71**. Lo que estaba mal:
`pie()` dejaba el WhatsApp terminando en y=1593 y el descargo en y=1650 (se corrigió la posición de dibujo pero
no se midió el ALTO de la caja); **`lamina_cierre()` tiene su PROPIO pie y el v4 no lo tocó** (descargo en 1618,
marca y teléfono pasados de x=930); `cabecera()` dibujaba en y=205 y la caja empezaba en 182; y los anchos
`W-190`/`W-260` llevaban texto hasta x=1002. Corregido en **`motor.py` v5**: 236 → **26 cajas fuera**, y esas 26
son los gráficos del clip de prensa del gancho, no texto del motor. **Todos los números, los cinco arreglos y
las reglas que se desprenden están en `motor/ZONA-SEGURA-v5.md`: leerlo antes de tocar el encuadre.**
Tres cosas de ahí que hay que tener presentes siempre:
- `SEG_X0`/`SEG_X1` del motor valen **130 y 925**: son el margen de **DIBUJO**, metido 35 px dentro del borde real
  (95 y 930), porque la caja que mide el OCR se extiende ~17 px más allá del glifo.
- Un mismo bloque dibujado en **dos funciones** se corrige en las dos, o la mitad de las piezas sale mal.
- **Una regla de encuadre no está implementada hasta que `pantalla_chica.py` la mide.** "Lo corregí" sin número
  es exactamente cómo el v4 pasó por corregido llevando el WhatsApp tapado.

**Verificación obligatoria antes de publicar**: `python3 videolab/pantalla_chica.py <n>.mp4`
(requiere `pip install -q rapidocr-onnxruntime`, ~20 s, CPU, sin GPU; ~22 s por pieza de 46 s).
- Criterio para el **formato ENSAYO**: recall ≥ 0,80 y 0 cajas fuera de la zona segura.
- Criterio para el **MOTOR**: **0 cajas de texto PROPIO fuera de la zona segura**. El recall del motor se
  estabiliza en **0,77** porque el pie legal (marca, teléfono, descargo) es texto chico por diseño: se informa
  y no bloquea. En piezas de **reacción** se mide aparte el tramo de láminas
  (`ffmpeg -ss <fin del gancho> -i out.mp4 -c copy laminas.mp4`), porque el cintillo y el ticker del clip de
  prensa cuentan como cajas fuera y no hay nada que mover.

### 5. DURACIÓN 22-34 SEGUNDOS (norma del 12/09/2026)
La franja de mayor tasa de finalización está entre 22 y 34 s. Las tres piezas del 12/09 salieron de **46, 48 y 47 s**
porque el guion traía 5 tramos largos y Kokoro lee a velocidad normal: se pasaron de la franja que retiene.
- Guion de **4 tramos** y frases cortas para piezas de reacción y noticia.
- Con 5 tramos, ninguno pasa de ~55 caracteres por frase.
- `voz.py` imprime `dur=` antes de renderizar: **si pasa de 34 s, se recorta el guion y se re-sintetiza**, no se
  publica y se anota "quedó largo". Cuesta 20 segundos de sandbox y es lo único que mide la retención antes de subir.

### 6. LA MÚSICA VA CON DUCKING, NUNCA ESTÁTICA (norma del 18/09/2026 — M6 corrida 2)
Las piezas salían **sin música**: entre frase y frase quedaban **−26,0 LUFS de aire muerto**, seis veces por pieza,
mientras la voz se entrega a −14,2. La cama musical tapa ese hueco, pero **solo con ducking**.
Medición completa, tabla de 9 mezclas y comandos en **`motor/REGLA-6-MUSICA.md`**. Lo que manda:
- **Fuente: Openverse `license=cc0`** (`videolab/musica.py buscar`). Sin clave, sin cuenta, US$0, y CC0 **no obliga
  a acreditar**. Si degrada a `cc-by`, el autor que devuelve el campo `atribucion` **va sí o sí en la descripción**.
  Probado desde el sandbox: Openverse 200, efectos de Mixkit 200, incompetech 200 (pero CC-BY);
  **403 Mixkit música, 403 Pixabay, 403 Free Music Archive, 401 Freesound** — no insistir con esos cuatro.
- **Ducking a 0 dB** (`sidechaincompress=threshold=0.03:ratio=12:attack=15:release=350:makeup=1`):
  los silencios suben de −26,0 a **−13,4 LUFS** (12,6 dB de relleno) y la voz entregada se mueve **0,2 dB**
  (−14,2 → −14,4).
- ⛔ **Música estática descartada con número.** Para rellenar igual hay que ponerla a 0 dB y la mezcla se va a
  **−13,1 LUFS**: TikTok normaliza a ~−14 y **baja la pieza entera**, o sea la voz llega más callada que sin música.
  A −16 dB no molesta pero tampoco se oye (silencios en −24,9, casi aire muerto). No volver a probarla.
- ⛔ **WER no sirve para decidir el nivel de la música.** faster-whisper `small` dio **WER 0,0000 en las 12 mezclas**,
  incluida música **6 dB más fuerte que la voz**. El juez es el par (voz entregada, silencios) en LUFS.
- ✅ **Control obligatorio**: `python3 videolab/musica.py control <mezcla> <tramos.json>` → `MUSICA_OK`.
  Bloquea si la voz entregada baja de −14,8 LUFS, si la mezcla sube de −15,5 o si los silencios pasan de −12,0.
- Costo real de punta a punta: **≈ 8 s y US$0 por pieza** (búsqueda 0,7 s, descarga 4,0 s, mezcla 1,0 s, control 2,3 s),
  y la salida es `48000, 2` — cumple la regla dura 3.

### 7. NINGUNA FOTO QUIETA SALE CON KEN BURNS (norma del 23/09/2026 — M6 corrida 3)
El supervídeo A quedó en **3,99 de movimiento** con la banda de los virales en **4,6–9,9**, y el culpable era el
plano nacido de foto: `zoompan` da **1,14 de media** (medido sobre 5 fotos reales, clips de 6 s a 1080x1920).
Medición completa y tabla en **`motor/REGLA-7-MOVIMIENTO.md`**. Lo que manda:
- **Todo plano que nace de una foto se mueve con `videolab/movimiento.py clip`** (parallax 2.5D: profundidad
  MiDaS-small en ONNX sobre CPU + órbita de cámara ×3). **4,85 de media**, US$0, 5,1 s por clip de 6 s.
- Eso es **4,25× el Ken Burns** que reemplaza y **más que la animación de pago** que veníamos usando
  (ltx-v2-fast de ElevenLabs, 4,67 a **US$0,26 el plano**). Una pieza de 9 planos pasa de US$2,34 a **US$0**.
- ⛔ **La profundidad suave está descartada con número**: amplitud 0,045 y 1 órbita dan **0,86**, o sea PEOR que
  Ken Burns. Lo que mueve la métrica es la velocidad del recorrido (3 órbitas), no el mapa de profundidad.
- ⛔ **Zoom rápido puro descartado**: 1,00→1,75 da 3,76 de media, deja 2 de 3 fotos bajo la banda y se come el
  43 % del encuadre, que además choca con la zona segura de la regla dura 4.
- ✅ **Control obligatorio antes de armar**: `python3 videolab/movimiento.py control <plano.mp4>` →
  `MOVIMIENTO_OK`. Bloquea (código 1) cualquier plano bajo **4,0**.
- Nitidez sin pérdida: laplaciano 28/8/14 contra 30/9/14 del Ken Burns. El warp no borronea.

---

## ⭐ PIPELINE v2 (VIDEO LAB, 05/09/2026) — voz gratis + subtítulos karaoke. ES EL VIGENTE.
Cambia solo los pasos 2 y 7; todo lo demás igual. Costo por pieza: 0 créditos (salvo foto nueva del banco cada 3 días).
Muestra real de v2 (Kokoro + karaoke + foto del banco): https://d2ol7oe51mr4n9.cloudfront.net/user_3IkWukwrqRk5HTPle6Rx8WbYgS3/a328c1ec-6553-4812-bfa2-8ca1d4d9de12.mp4

**Experimento E-01 vigente**: de las 6 piezas del día, 3 llevan voz Kokoro (brazo B, campo `"voz_motor":"kokoro"`) y 3 voz Eleven Cristian Cornejo (brazo A, `"voz_motor":"eleven"`), alternando en la grilla. Todas llevan karaoke. Corte: 30 piezas por brazo.

2v2. **Voz gratis** (brazo B) en el sandbox, dentro de la misma llamada background que instala:
   `pip install -q kokoro soundfile faster-whisper numpy pillow` (~90 s la primera vez por sandbox; después ~5 s).
   Escribir `videolab/voz.py` y `videolab/karaoke.py` desde GitHub COMO TEXTO PLANO (heredoc), y por pieza un
   `urls/<n>.txt` con los 5 tramos separados por UNA LÍNEA EN BLANCO (gancho / punto 1 / punto 2 / punto 3 / cierre).
   `python3 voz.py urls/<n>.txt <n>.mp3 kokoro` → imprime `VOZ_OK motor=kokoro dur=.. tramos=5 audio=48000,2`
   y deja `<n>.mp3.tramos.json` con 6 límites. Cadena: kokoro → piper → edge; si las tres fallan, la pieza pasa al brazo A.
7v2. **Subtítulos**: `python3 karaoke.py <n>.mp3 <n>.ass` (→ `KARAOKE_OK`), ~6 s. Sirve para ambos brazos.
   En `pieza.json` agregar `"subs":"<n>.ass"` y `"tramos": <contenido de <n>.mp3.tramos.json>`.
   `motor.py` v2+ quema el karaoke (solo desde el fin del gancho), deja las láminas con título solo y re-encodea.
   Desde el 11/09 el estilo lleva **caja opaca** (regla dura 4a): es la versión de `karaoke.py` que está en GitHub.
7v3. **Cama musical** (desde el 18/09, regla dura 6): `python3 musica.py buscar "<clima de la pieza>" 5`,
   `python3 musica.py mezclar <n>.mp3 mus.mp3 <n>_mus.wav 0` y `python3 musica.py control <n>_mus.wav <n>.mp3.tramos.json`.
   La mezcla reemplaza al mp3 de voz en el mux del motor. **No se publica una pieza con música sin `MUSICA_OK`.**
Verificación numérica extra: en 2 cuadros de láminas debe haber píxeles amarillos (R>200,G>200,B<90) entre y=1150 y y=1400.

### Campo `rotulo` (v3) — el rótulo de la esquina del gancho
Por defecto dice `DRAMATIZACIÓN`. Con `"rotulo":"¿DELITO O NO DELITO?"` (o `"NOTICIA DE HOY"`, `"18 DE SEPTIEMBRE"`,
o el nombre de la serie que sea) el motor lo cambia y ajusta solo el ancho de la caja. **Así se produce la serie
semanal y las piezas de reacción/noticia sin escribir un motor aparte**: gancho = clip real (mp4) con el rótulo de
la serie, punto 1 = "Comenta antes del veredicto", puntos 2 y 3 = el veredicto con su artículo y su pena, cierre = la marca.
El rótulo va **dentro de la zona segura** (y ≥ 200, x ≥ 95): si se dibuja más arriba lo tapa el buscador de TikTok.

### Metraje real para el gancho (doctrina: TOMAS REALES por sobre imágenes generadas)
Desde el sandbox, **Mixkit** sí responde (Pexels y Pixabay dan 403):
`curl -A "Mozilla/5.0" https://mixkit.co/free-stock-video/<categoria>/` y de ahí
`https://assets.mixkit.co/videos/<id>/<id>-720.mp4` (el `-1080` devuelve 403 en la mayoría).
Prepararlo SIEMPRE antes de dárselo al motor — sube la nitidez y garantiza que tenga pista de audio:
```
ffmpeg -y -i raw.mp4 -f lavfi -t 12 -i anullsrc=r=48000:cl=stereo \
  -vf "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,unsharp=5:5:0.9:5:5:0.0,fps=30" \
  -map 0:v -map 1:a -t 12 -c:v libx264 -preset veryfast -crf 19 -c:a aac -ar 48000 -ac 2 -b:a 128k hook.mp4
```
Sin pista de audio el motor falla al mezclar el ambiente del clip. Elegir planos de OBJETOS, sin rostros identificables.

**⚠️ Para CLIPS DE PRENSA (formato reacción) ese `crop` NO sirve**: un 1280x720 de noticiero recortado a 1080x1920
pierde el cintillo y los rótulos del medio, que son justo lo que da credibilidad. Se usa **fondo desenfocado +
clip centrado**, que conserva el cuadro completo, y se mantiene el AUDIO ORIGINAL del clip (`-map 0:a`, no `anullsrc`):
```
ffmpeg -y -ss <inicio> -t 9 -i crudo.mp4 -filter_complex \
 "[0:v]split=2[bg][fg];\
  [bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:2,eq=brightness=-0.14[b];\
  [fg]scale=1080:-2:flags=lanczos,unsharp=5:5:0.9:5:5:0.0[f];\
  [b][f]overlay=(W-w)/2:(H-h)/2,fps=30[v];\
  [0:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[a]" \
 -map "[v]" -map "[a]" -t 9 -c:v libx264 -preset veryfast -crf 19 -c:a aac -ar 48000 -ac 2 -b:a 128k hook.mp4
```
El motor mezcla solo ese audio a `volume=0.35` durante el gancho, con `afade` de salida. El gancho dura lo que dure
el **tramo 1 de la voz**: para que se escuche el momento fuerte del clip, el tramo 1 tiene que dar unos 6 s y el corte
del clip debe dejar la frase de impacto dentro de los primeros 2 s. Acreditar siempre el medio en la descripción
("Imágenes: Meganoticias").

⚠️ **En una pieza de reacción las UNIONES se miden saltando el primer corte interior** (`tramos[2:-1]`, no
`tramos[1:-1]`): ese primer corte cae donde se desvanece el audio del noticiero del gancho, así que mide como voz
y **reprueba una pieza sana, bloqueando la subida**. Lo hace solo `produce.py` v3 cuando la pieza trae `prensa:true`.
Por lo mismo, el control 7 de voz escucha el **mp3**, no el mp4.
⚠️ **Y el control 4 también tiene que escuchar el mp3** (`media_voz=`). Medido el 21/09 sobre la 1004: pasarle el
mp4 **no** hace que el control se abstenga —encuentra los 4 empalmes igual y emite veredicto—, así que la
protección no viene de que el control se dé cuenta, viene de que la receta le pase el archivo correcto. Ver la
regla dura 2-quater.
⚠️ **Y el control 8 (cobertura de voz) también va sobre el mp3**: sobre el mp4 el audio del noticiero tapa los
huecos y la cobertura da ~100 % aunque la voz se haya caído entera. Ver la regla dura 2-quinquies.

Formato F11 ENSAYO (videolab/ensayo.py, 05/09; v2 zona segura 11/09): guion de 4 párrafos, voz con `voz.py`,
karaoke, 26-30 fotos, `python3 ensayo.py pieza.json salida.mp4` (~45 s). Ver videolab/ANALISIS-viral-01.md.

Lo que NO hacer en v2: no pasar el texto a voz.py sin líneas en blanco; no usar edge-tts como primaria; no mezclar voces dentro de una pieza.

## Piezas (v1)
- `motor.py` — render (Pillow + ffmpeg). Entrada `pieza.json`; salida mp4 1080x1920 h264 + aac 48k estéreo, 24-33 s
- `render.sh` — bucle: lee `urls/<n>.voz` y `urls/<n>.hook`, descarga, renderiza a `out/<id>.mp4`
- `piezas.json` — guiones: `{id, materia, gancho, puntos:[{t,d}x3], cierre, hook_prompt, hashtags, rotulo?}`
- `control.py` — **LA PUERTA**: los ocho controles en un solo lugar. Toda receta lo importa o no sube (regla 3-ter)
- `produce.py` — driver de producción de punta a punta; llama a `control.py` y decide nada por su cuenta
- `videolab/musica.py` — cama musical CC0 con ducking y su control (regla dura 6)
- ⚠️ `render.sh` NO sirve para el pipeline v2: no inyecta `subs` ni `tramos` en pieza.json. Usar un driver en python sobre el mismo `motor.py`.

## Flujo (cada paso es una herramienta distinta)
1. **Guiones** (Claude): gancho en segunda persona y dolor concreto, nunca "¿Sabías que…". Local: "en San Bernardo". Materias rotando laboral/familia/penal/civil. 60% temas ya probados.
2. **Voz** (conector Eleven, brazo A) — ⚠️ **UNA LLAMADA TTS POR TRAMO, SIN NINGUNA ETIQUETA `<break>`**:
   un flow con `creative_create_flow`; **5 nodos `tts` por pieza**, modelo `eleven_multilingual_v2`, voz `ClNifCEVq1smkl4M3aTk` (Cristian Cornejo), `generations_count: 1`.
   El prompt de cada nodo es SOLO el texto de ese tramo, con tildes y eñes, sin etiquetas.
   Los 5 mp3 se bajan al sandbox y se unen ahí con el **filtro concat** a 48 kHz estéreo, intercalando silencio
   `anullsrc` de **1,05 s**, con `loudnorm=I=-16:TP=-1.5:LRA=11`. Se escribe `<n>.mp3.tramos.json`.
   Largo de la pausa: 1,05 s (con 0,45 s la pieza cae bajo los 20 s). ~350 créditos por pieza.
3. **Gancho** (conector Eleven): nodo `image-generation`, modelo `bytedance-seedream-5-pro`, `model_parameters: {"aspect_ratio":"9:16","resolution":"2K"}`. Prompt fotorrealista, persona de espaldas o solo manos, "face not visible", sin texto. 818 créditos.
   **Preferir metraje real de Mixkit o un clip de prensa** (ver arriba) cuando exista: lo generado por IA es último recurso.
4. **Correr** con `creative_run_flow_nodes`. ⚠️ **Máximo 5 nodos por corrida**.
5. **Recoger URLs** con `creative_get_flow_run_status` (`media[].master_url`, firmadas por 2 horas).
6. **Alojamiento** (Higgsfield): `media_upload` con `files[]` devuelve `upload_url` S3 (PUT) y la `url` CloudFront definitiva.
7. **Sandbox** (Higgsfield `sandbox_exec`):
   - 🔑 **EL GUION DE PRODUCCIÓN TIENE QUE SER AUTOCONTENIDO EN UNA SOLA LLAMADA `background:true`.** El sandbox
     **se reinicia solo entre llamadas** y se lleva `voz.py`, `karaoke.py`, `pantalla_chica.py` y todo lo instalado
     con pip, incluso cuando una llamada anterior con `sleep 800` parecía tener el lease vivo (pasó dos veces el
     12/09/2026 y costó rehacer una producción completa). Entonces: el guion **empieza** re-bajando los .py del repo
     y corriendo `pip install`, y **termina** con el `curl PUT` de subida — con las `upload_url` pedidas ANTES de
     lanzarlo. No encadenar dos background distintos ni dar por presente nada de una llamada anterior.
   - Una llamada que pasa de ~60 s muere con **502 de Cloudflare** y **se lleva el contenedor**. Todo trabajo largo
     va con `nohup ... &` escribiendo a un archivo, y se sondea con `sleep 45` como máximo por llamada.
   - Los .py del repo se bajan directo con `curl` desde `raw.githubusercontent.com/cristopherbravoabogado-code/estudio-automatizacion/main/<ruta>` (el repo es público, responde 200 y no pide token). **Es mejor que pegarlos por heredoc**: no se corrompen y no gastan los 16.000 caracteres del comando.
     ⚠️ `raw.githubusercontent.com` **cachea ~5 minutos**: recién subido un cambio, el sandbox todavía baja la versión
     anterior. **El truco de `?t=<epoch>` NO lo salta** (probado el 18/09/2026). Lo que sí funciona es pedir el archivo
     **por el SHA del commit** en vez de por `main`:
     `raw.githubusercontent.com/<owner>/<repo>/<sha-del-commit>/<ruta>` → llega fresco al instante.
   - Escribir código por heredoc COMO TEXTO PLANO (no base64: al transcribirlo se corrompe). Tope 16.000 caracteres por llamada.
   - Render: ~20 s por pieza. Subida: `curl -X PUT -H "Content-Type: video/mp4" --data-binary @out/<id>.mp4 '<upload_url>'` → 200.
   - `apt-get install` NO funciona (no hay root). `pip install` SÍ. Por eso el OCR del QC es `rapidocr-onnxruntime`
     (Apache 2.0, CPU, sin torch) y no tesseract.
   - **Verificar leyes desde el sandbox**: `curl -A "Mozilla/5.0" "https://www.leychile.cl/Consulta/obtxml?opt=7&idNorma=<N>"`
     devuelve la norma COMPLETA en XML (1,7 MB el Código Penal) y se busca con python. **`bcn.cl/leychile/navegar`
     NO sirve: renderiza por JS y WebFetch solo ve "este proceso demora demasiado".**
     idNorma útiles: **1984** Código Penal · **176595** Código Procesal Penal · **207436** Código del Trabajo.
8. **Confirmar** con `media_confirm` (`media_ids[]`, type video).
9. **Publicar / fijar la hora** — ver `motor/PUBLICAR.md`. **CANAL ÚNICO desde el 12/09/2026:**
   - ✅ **Higgsfield → TikTok**: `tiktok_prepare_publish` + `tiktok_publish` en **DIRECT_POST**, connector_id
     `f23f2205-1ae6-4259-8240-e6f4165bbe79`. Cupos 5 posts/minuto y 13/24 h. Ajustes fijos de Cristopher:
     `PUBLIC_TO_EVERYONE`, `is_aigc: true`, comentarios/dúo/stitch habilitados, sin divulgación de contenido
     comercial, sin música añadida (las piezas traen voz y música propias). Si el clasificador de modo rechaza el
     primer intento, **reintentar la MISMA llamada con el mismo `publish_session_id`**.
   - Publica **al instante**, así que **la hora se fija con UNA TAREA DE UN SOLO DISPARO POR PIEZA**
     (`create_trigger` con `run_once_at`; UTC = hora de Chile + 3), llevando dentro la URL de CloudFront, el título,
     el texto completo y la orden de verificar el estado. Una por pieza y no una para todas: si falla, cae UNA.
   - ⛔ **Metricool NO publica.** Su **plan gratis** llegó al tope el 08/09/2026 y no se libera sin pago: devuelve
     `providers[].status = ERROR` con "You have reached your Metricool account limit". **No programar ahí ni gastar
     una pieza probando si el tope se soltó.** Queda solo para LEER: `getBestTimeToPostByNetwork` y
     `getAnalyticsDataByMetrics`, que sí leen la cuenta de TikTok.
   - ⛔ **Zernio: probado y no funciona.** No volver a intentarlo.
   - 🔑 **Lo publicado por Higgsfield NO aparece en Metricool**, así que `getScheduledPosts` dará 0 aunque el día
     esté completo. **La fuente de verdad de lo publicado es la bitácora de memoria** (`/areas/tiktok-vigilante.md`),
     confirmada con `tiktok_publish_status`. Al cambiar el canal hay que cambiar el MEDIDOR en la misma jugada: el
     12/09 las 6 tareas programadas seguían contando con Metricool y estaban a punto de republicar duplicados.
   - 🔑 **Una corrida programada SÍ puede publicar.** El 11/09 `tiktok_publish` fue denegado por permisos tres veces
     y se concluyó que era estructural; el 12/09 pasó al primer intento cinco veces seguidas. Es intermitente:
     **intentarlo siempre antes de darlo por imposible en esa corrida**, y publicar una pieza de la reserva al
     EMPEZAR la corrida en vez de al final.
10. **Verificar**: `tiktok_publish_status` hasta `PUBLISH_COMPLETE` (trae el `post_ids`). Un 200 no es publicado.

## Verificación sin ojos
El contenedor de Claude no puede bajar de CloudFront ni WebFetch acepta imágenes. Se verifica por números en el sandbox: extraer cuadros con ffmpeg, medir con numpy la caja de píxeles claros (L>215) y comprobar que no toque bordes ni se salga de **x[95,930] y[200,1586]** — la zona segura de TikTok (regla dura 4b; hasta el 11/09/2026 este límite decía x[60,1020] y[120,1730], que es el borde del archivo, no lo que el espectador ve).

**Control de pantalla chica obligatorio (desde 11/09/2026)** — `python3 videolab/pantalla_chica.py <n>.mp4`:
ver los criterios por formato en la regla dura 4. Para el motor manda **0 cajas de texto propio fuera de la zona
segura**; para el ensayo, además recall ≥ 0,80. Devuelve código 1 si no pasa su umbral interno.
Diagnóstico cuando no pasa: volcar las detecciones de un cuadro con `RapidOCR` e imprimir las que caen fuera con
su caja y su texto. Así se distingue texto propio mal puesto de gráficos del clip de prensa, que no se tocan.

**Control de música obligatorio (desde 18/09/2026, solo si la pieza lleva cama musical)** —
`python3 videolab/musica.py control <mezcla> <tramos.json>` → **`MUSICA_OK`** o no sube. Mide en LUFS, después de
normalizar a −14 como hace TikTok: voz entregada ≥ −14,8 · mezcla ≤ −15,5 · silencios ≤ −12,0. Ver regla dura 6
y `motor/REGLA-6-MUSICA.md`.

**Control de audio obligatorio (desde 08/09/2026; ampliado el 11/09/2026; paso 3 corregido el 16/09/2026)** —
un mp4 renderizado no es un mp4 bueno; se mide. **Todo esto está implementado en `motor/control.py`: se corre
importándolo, no copiándolo.**
1. `ffprobe -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels` → **debe decir `aac,48000,2`**. Si no, la pieza se re-muxea; no se publica en mono ni a 44,1 kHz.
2. `ffmpeg -i <n>.mp4 -vn -ac 1 -ar 16000 <n>.wav` y transcribir con faster-whisper `small`, `language="es"`, `word_timestamps=True`, `vad_filter=False`.
3. **La comparación contra el guion son DOS pasadas, y hay que hacer las dos.** Hasta el 16/09/2026 aquí decía una
   sola cosa — *"normalizar (minúsculas, sin tildes) y contar las palabras que no están en el guion"* — y ese
   plegado es exactamente lo que dejó salir la **967b** diciendo *"por anos de servicio"*: plegadas las tildes,
   `anos` y `años` son el mismo token y el control informaba **0 palabras fuera del guion**. Un control que
   normaliza la diferencia que busca no puede encontrarla nunca. Ver regla dura 2-bis.
   - **3a. PLEGADA (minúsculas, sin tildes) — INFORMA.** Cuenta las palabras transcritas que NO están en el
     vocabulario del guion. Sirve para basura de audio y para etiquetas leídas en voz alta. **No bloquea**, porque
     whisper se equivoca solo: en la 967b escribió "haya impactado" por "hayan pactado" y "Cres" por "Crece".
     Descontando siempre:
     - **cifras**: el guion dice "dieciocho" y whisper escribe "18". Ignorar todo token que sea solo dígitos o puntuación.
     - **homófonos conocidos** de whisper (`filiación`→`afiliación`, `SOAP`→`swap`, `criar`→`crear`, `golpean`→`colpean`, `bencineras`→`vencineras`, `cayó`→`calló`): son error del transcriptor, se corrigen en el `.ass` SIN tocar los tiempos.
     - **cortes de palabra**: whisper a veces parte "a una" en "aun". Si el token de sobra es un pedazo de una palabra del guion y las uniones miden silencio real, es segmentación del transcriptor, no basura de audio.
     - Cualquier otra palabra fuera del guion **no es alucinación hasta que se mida el RMS** (lección de la 917).
   - **3b. SENSIBLE A DIACRÍTICOS — BLOQUEA.** Cada palabra del guion que lleva **ñ** tiene que OÍRSE con ñ.
     Whisper conserva los diacríticos cuando están (en la 991 escribió "daños" y "dueño" sin ayuda), así que oír
     "anos" donde el guion dice "años" es señal del TTS, no del transcriptor. Se bloquea por ñ y no por tilde
     porque la ñ es la que cambia la palabra entera.
     ⚠️ **El pegado**: whisper transcribe "por años" como UN token, `poranos`. Buscar `anos` como palabra suelta
     NO lo encuentra — medido el 16/09 contra el audio real de la 967b, y fue el primer falso negativo de este
     mismo control. Por eso también se mira el **sufijo** de los tokens que están fuera del guion, exigiendo que
     el prefijo que queda sea a su vez palabra del guion: `poranos` = `por` + `anos` y `por` está en el guion, así
     que se marca; en `mano` el sufijo `ano` deja `m`, que no es palabra del guion, así que no se marca.
   ⚠️ **Si la pieza lleva cama musical, los controles 2, 3a y 3b se corren sobre el MP3 DE VOZ, no sobre la mezcla**
   (igual que en las piezas de reacción): la música no cambia lo que la voz dice, pero sí ensucia la transcripción.
4. Medir el RMS de cada hueco entre tramos con numpy (`f32le` a 16 kHz), ventana [límite−0,62 s, límite−0,10 s].
   **Silencio real ≤ −35 dBFS** (con voz.py v3 dan −240 dBFS). Si un hueco mide como la voz (≈ −15 dBFS), rehacer la pieza.
   ⚠️ En piezas de **reacción** este control se mide sobre el **mp3 de la voz**, no sobre el mp4: el mp4 lleva el audio
   del clip de prensa durante el gancho, así que la primera unión y la transcripción traen la voz del noticiero — que
   es deliberada, no un defecto. Además se salta el primer corte interior (`tramos[2:-1]`): ver el bloque de clips de prensa.
   ⚠️ **Lo mismo con música**: con cama musical los huecos ya NO miden silencio por diseño (suben a ≈ −13 LUFS).
   Este control 4 se mide **siempre sobre el mp3 de voz**, nunca sobre la mezcla, o reprueba una pieza sana.
   🔑 **Desde el 20/09 (control.py v4) no hay que calcularlos a mano**: `control.cortes_auto()` encuentra los
   empalmes sola y `uniones()` los busca si no se los dan. Si no aparece ninguno, **bloquea**. Ver regla dura 2-ter.
   🔑 **Desde el 21/09 (control.py v5) se barre la PAUSA COMPLETA**, no una ventana de ±0,12 s en su centro, y el
   informe declara su `cobertura`, su `barrido_s` y los `intervalos` que abrió. La ventana chica dejaba sin mirar
   el 78 % de cada pausa y dio un **falso PASE medido** en la 1004 (−50,1 dBFS donde había −33,4). Ver regla dura
   2-quater. Un informe de uniones sin `cobertura` es de una versión vieja: no vale.
   ⛔ **Y este control mide el TECHO de la pausa, no el piso**: un tramo mudo saca su MEJOR nota (−91,0 dBFS en la
   variante medida el 22/09). El defecto de lo que FALTA lo cubre el control 8, no este. Ver regla dura 2-quinquies.
5. **Control 8 — cobertura de voz (desde el 22/09/2026, `control.py` v6)**: `control.cobertura_voz(media)` mide qué
   fracción de la LÍNEA DE TIEMPO ENTERA lleva voz y cuánto dura el hueco más largo, la cola incluida. **BLOQUEA
   bajo 65 % de cobertura o con cualquier hueco de más de 3,0 s.** En piezas de **reacción** y con cama musical va
   sobre el **mp3 de voz**: sobre el mp4 el audio del noticiero tapa los huecos y la cobertura da ~100 %. Ver regla
   dura 2-quinquies.

## Grilla
6 diarias (D-10 rev. 05/09): 09:00, 12:00, 13:00, 16:00, 18:00, 20:00. Recalcular con `getBestTimeToPostByNetwork` cada lunes.
Viernes 18:00 queda tomado por la SERIE "¿Delito o no delito?".
Tope de la API de TikTok por terceros: ~25 publicaciones por 24 h; el conector de Higgsfield corta antes: 13/24 h.
**RESERVA: siempre 3 piezas o más renderizadas, con control de audio limpio y alojadas en CloudFront.** Publicar nunca
puede depender de producir: si un día falla el render, se publica de la reserva y el día no queda en cero. Toda tarea de
producción deja la reserva en 3 antes de terminar.

## Costos por pieza
v2/v3/v4/v5: 0 créditos (voz Kokoro, metraje Mixkit o clip de prensa, karaoke whisper, QC rapidocr).
v8 agrega la cama musical: **también 0** (Openverse CC0, ≈ 8 s de sandbox).
v1 (brazo A): voz ~350 créditos ≈ US$0,08; foto nueva ~818 solo cada 3 días por materia.

## Lo que NO hacer
- **NUNCA poner etiquetas `<break time="..." />` en el texto que se manda a ElevenLabs.** Es la causa del defecto de audio del lote 911-917 (diagnosticado 08/09/2026). `eleven_multilingual_v2` a veces NO interpreta la etiqueta como pausa: la LEE EN VOZ ALTA y salen sílabas sin sentido al volumen normal de la voz.
  - Caso medido, pieza **917**: tras "…nunca lo reconoció" soltaba **1,26 s de basura entre 2,42 s y 3,68 s**, justo en la unión donde iba el primer `<break>`. Ese tramo medía **−15,55 dBFS**, igual que la voz (−15,60), mientras las uniones sanas median entre −38 y −59 dBFS.
  - **Whisper no estaba alucinando**: transcribía el ruido real. Si whisper mete palabras en una unión de tramos, **medir el RMS antes de borrar nada**.
  - El fallo es **intermitente**: que una pieza salga limpia NO valida la etiqueta.
  - Las piezas Kokoro nunca lo tuvieron: `voz.py` ya sintetizaba tramo por tramo.
- **No escribir los guiones sin tildes.** Ver regla dura 2.
- **No plegar las tildes antes de comparar la transcripción con el guion.** Es lo que dejó salir la 967b diciendo
  "por anos de servicio" con el control marcando 0 palabras fuera. Ver regla dura 2-bis y el paso 3b.
- **No dejar un control de contenido en manos de que alguien se acuerde de correrlo a mano.** Si no está en
  `control.py` y no puede bloquear la subida, no es un control: es una intención. Ver regla dura 3-ter.
- **No dejar que un control se apague porque el llamador no le pasó un dato.** Si le falta lo que necesita para
  medir, falla CERRADA. La prueba: llamarlo SIN ese dato; si contesta que sí, está roto. Ver regla dura 2-ter.
- **No dejar que un control mida una muestra y la informe como si fuera el todo.** Tiene que declarar su
  cobertura en el informe. La prueba: preguntarle qué fracción del objeto abrió; si no lo sabe decir, su
  veredicto no vale. Medido el 21/09: el control 4 abría 0,24 s de una pausa de 1,1 s y dejó pasar −33,4 dBFS
  reportando −50,1. Ver regla dura 2-quater.
- **No dar por controlado un control que solo mide TECHOS.** La prueba: preguntarle qué nota le pone al objeto
  VACÍO; si el silencio, el cuadro en negro o el guion en blanco sacan su mejor nota, le falta el piso. Medido el
  22/09: la 1003 con la segunda mitad muda pasaba la puerta v5 completa, y el control 4 puntuó los 11,7 s mudos
  como **la unión más limpia de la pieza**. De ahí el control 8. Ver regla dura 2-quinquies.
- **No unir audio con el demuxer `concat` ni entregar mono/44,1 kHz.** Ver regla dura 3.
- **No publicar de la RESERVA sin re-medir el audio con `ffprobe` justo antes.** El stock renderizado antes de una regla dura no la cumple, y la etiqueta "control de audio limpio" de la bitácora es del día en que se escribió. Ver regla dura 3-bis.
- **No poner texto con contorno y sin caja, ni fuera de x[95,930] y[200,1586].** Ver regla dura 4.
- **No dar por corregida una regla de encuadre sin medirla con `pantalla_chica.py`**, y buscar TODAS las funciones que dibujan el mismo bloque: `pie()` y `lamina_cierre()` dibujan los dos el CTA. Ver regla dura 4d.
- **No publicar una pieza de más de 34 s.** Ver regla dura 5.
- **No poner música estática debajo de la voz.** Medido el 18/09: para que se oiga hay que subirla a 0 dB y ahí la
  mezcla se va a −13,1 LUFS, TikTok la normaliza y **baja la pieza entera**. Va siempre con `sidechaincompress`. Ver regla dura 6.
- **No usar WER para decidir el nivel de la música.** faster-whisper dio 0,0000 en las 12 mezclas, incluso con la
  música 6 dB MÁS FUERTE que la voz: no distingue nada. El juez es (voz entregada, silencios) en LUFS. Ver regla dura 6.
- **No medir los huecos entre tramos ni transcribir sobre la MEZCLA con música**: con cama musical los silencios
  miden ≈ −13 LUFS por diseño y reprueban una pieza sana. Esos controles se corren sobre el mp3 de voz.
- **No correr el control 8 sobre el mp4 en una pieza de reacción**: el audio del noticiero tapa los huecos y la
  cobertura da ~100 % aunque la voz se haya caído entera. Va sobre el mp3. Ver regla dura 2-quinquies.
- **No publicar una pista de licencia desconocida, ni una `cc-by` sin acreditar al autor en la descripción.** Ver regla dura 6.
- **No mover una foto fija con `zoompan`.** Medido el 23/09 sobre 5 fotos: 1,14 de movimiento contra 4,85 del
  parallax 2.5D, con la banda viral en 4,6–9,9 y el mismo costo cero. Y **no "suavizar" el parallax**: con
  amplitud baja cae a 0,86, peor que el Ken Burns que vino a reemplazar. Ver regla dura 7.
- **No publicar NINGUNA pieza sin control de audio, aunque no la haya hecho `motor.py`.** El supervideo A salió mono y de 60,7 s el 14/09 porque su receta cierra el mux por fuera del motor. Ver regla dura 3-ter.
- **No volver a probar "subir el tamaño de la fuente" para que se lea mejor**: medido el 11/09, 78 px y 96 px dan exactamente lo mismo (0,29) sin caja. Lo que decide es el fondo detrás de la letra.
- **No recortar con `crop` un clip de prensa**: se come el cintillo del medio. Fondo desenfocado + clip centrado.
- **No medir las uniones de una pieza de reacción sobre el mp4 ni desde el primer corte interior**: reprueba piezas sanas. `tramos[2:-1]` y el mp3. Y ojo: si igual se le pasa el mp4, el control **no se abstiene** — encuentra empalmes y contesta (medido el 21/09 en la 1004). La protección es pasarle el mp3, no esperar que el control se dé cuenta.
- **No programar en Metricool ni probar si su tope se soltó**, y **no volver a intentar Zernio**. Ver paso 9.
- **No contar los publicados con `getScheduledPosts` de Metricool**: lo que sale por Higgsfield no aparece ahí y se lee como día vacío. Peor: en Metricool quedaron posts viejos en ERROR cuyas piezas ya salieron por Higgsfield, y "republicar lo que está en ERROR" genera duplicados.
- **No dar por imposible publicar desde una tarea programada sin haberlo intentado en esa corrida.** Ver paso 9.
- **No confiar en `?t=<epoch>` para saltar el caché de `raw.githubusercontent.com`**: no lo salta. Pedir el archivo por el SHA del commit. Ver paso 7.
- **No buscar música en Mixkit, Pixabay, Free Music Archive ni Freesound directo**: 403, 403, 403 y 401 desde el sandbox. Openverse CC0. Ver regla dura 6.
- No mandar `motor.py` en base64 dentro del comando: se corrompe al transcribirlo.
- No lanzar `render.sh &` en una llamada sin `background:true`: la herramienta espera y mata la llamada.
- No dejar una llamada de `sandbox_exec` corriendo más de ~60 s: el 502 de Cloudflare se lleva el contenedor entero.
- **No encadenar dos llamadas background ni dar por presentes los .py y los paquetes de una llamada anterior**: el sandbox se reinicia solo. Ver paso 7.
- No confiar en un `ls` justo después de una llamada background: puede estar aún escribiendo.
- No correr más de 5 nodos de Eleven a la vez.
- No dar por buena una pieza sin el control de audio completo ni sin el control de pantalla chica.
- No republicar un video defectuoso que ya salió al aire (regla de Cristopher del 07/09/2026): ensucia la muestra de métricas. La corrección se aplica solo a la producción nueva.
- **No comentar a un juez, fiscal o colega por su nombre** en una pieza de noticia: se comenta la institución.
