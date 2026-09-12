# RECETA — Motor de video 100% nube (v1 05/09/2026 · v2 05/09/2026 · voz Eleven por tramos 08/09/2026 · **v3 audio 11/09/2026** · **v4 pantalla chica 11/09/2026** · **v5 zona segura medida + canal único 12/09/2026**)

Produce y publica TikToks del Estudio Jurídico San Bernardo sin tocar el Mac ni Drive.
Probada de punta a punta con el lote 09 (901-908): 8 videos generados, alojados y programados en ~40 minutos.

**Para PUBLICAR (y para fijar una hora) ver `motor/PUBLICAR.md`. Para el encuadre medido ver `motor/ZONA-SEGURA-v5.md`.**

---

## ⛔ LAS CINCO REGLAS DURAS (si se rompe una, la pieza no sale)

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

Formato F11 ENSAYO (videolab/ensayo.py, 05/09; v2 zona segura 11/09): guion de 4 párrafos, voz con `voz.py`,
karaoke, 26-30 fotos, `python3 ensayo.py pieza.json salida.mp4` (~45 s). Ver videolab/ANALISIS-viral-01.md.

Lo que NO hacer en v2: no pasar el texto a voz.py sin líneas en blanco; no usar edge-tts como primaria; no mezclar voces dentro de una pieza.

## Piezas (v1)
- `motor.py` — render (Pillow + ffmpeg). Entrada `pieza.json`; salida mp4 1080x1920 h264 + aac 48k estéreo, 24-33 s
- `render.sh` — bucle: lee `urls/<n>.voz` y `urls/<n>.hook`, descarga, renderiza a `out/<id>.mp4`
- `piezas.json` — guiones: `{id, materia, gancho, puntos:[{t,d}x3], cierre, hook_prompt, hashtags, rotulo?}`
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

**Control de audio obligatorio (desde 08/09/2026; ampliado el 11/09/2026)** — un mp4 renderizado no es un mp4 bueno; se mide:
1. `ffprobe -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels` → **debe decir `aac,48000,2`**. Si no, la pieza se re-muxea; no se publica en mono ni a 44,1 kHz.
2. `ffmpeg -i <n>.mp4 -vn -ac 1 -ar 16000 <n>.wav` y transcribir con faster-whisper `small`, `language="es"`, `word_timestamps=True`, `vad_filter=False`.
3. Normalizar (minúsculas, sin tildes) y contar las palabras transcritas que NO están en el vocabulario del guion. **Debe dar 0**, descontando:
   - **cifras**: el guion dice "dieciocho" y whisper escribe "18". Ignorar todo token que sea solo dígitos o puntuación.
   - **homófonos conocidos** de whisper (`filiación`→`afiliación`, `SOAP`→`swap`, `criar`→`crear`, `golpean`→`colpean`, `bencineras`→`vencineras`): son error del transcriptor, se corrigen en el `.ass` SIN tocar los tiempos.
   - **cortes de palabra**: whisper a veces parte "a una" en "aun". Si el token de sobra es un pedazo de una palabra del guion y las uniones miden silencio real, es segmentación del transcriptor, no basura de audio.
   - Cualquier otra palabra fuera del guion **no es alucinación hasta que se mida el RMS** (lección de la 917).
4. Medir el RMS de cada hueco entre tramos con numpy (`f32le` a 16 kHz), ventana [límite−0,62 s, límite−0,10 s].
   **Silencio real ≤ −35 dBFS** (con voz.py v3 dan −240 dBFS). Si un hueco mide como la voz (≈ −15 dBFS), rehacer la pieza.
   ⚠️ En piezas de **reacción** este control se mide sobre el **mp3 de la voz**, no sobre el mp4: el mp4 lleva el audio
   del clip de prensa durante el gancho, así que la primera unión y la transcripción traen la voz del noticiero — que
   es deliberada, no un defecto.

## Grilla
6 diarias (D-10 rev. 05/09): 09:00, 12:00, 13:00, 16:00, 18:00, 20:00. Recalcular con `getBestTimeToPostByNetwork` cada lunes.
Viernes 18:00 queda tomado por la SERIE "¿Delito o no delito?".
Tope de la API de TikTok por terceros: ~25 publicaciones por 24 h; el conector de Higgsfield corta antes: 13/24 h.
**RESERVA: siempre 3 piezas o más renderizadas, con control de audio limpio y alojadas en CloudFront.** Publicar nunca
puede depender de producir: si un día falla el render, se publica de la reserva y el día no queda en cero. Toda tarea de
producción deja la reserva en 3 antes de terminar.

## Costos por pieza
v2/v3/v4/v5: 0 créditos (voz Kokoro, metraje Mixkit o clip de prensa, karaoke whisper, QC rapidocr). v1 (brazo A): voz ~350 créditos ≈ US$0,08; foto nueva ~818 solo cada 3 días por materia.

## Lo que NO hacer
- **NUNCA poner etiquetas `<break time="..." />` en el texto que se manda a ElevenLabs.** Es la causa del defecto de audio del lote 911-917 (diagnosticado 08/09/2026). `eleven_multilingual_v2` a veces NO interpreta la etiqueta como pausa: la LEE EN VOZ ALTA y salen sílabas sin sentido al volumen normal de la voz.
  - Caso medido, pieza **917**: tras "…nunca lo reconoció" soltaba **1,26 s de basura entre 2,42 s y 3,68 s**, justo en la unión donde iba el primer `<break>`. Ese tramo medía **−15,55 dBFS**, igual que la voz (−15,60), mientras las uniones sanas median entre −38 y −59 dBFS.
  - **Whisper no estaba alucinando**: transcribía el ruido real. Si whisper mete palabras en una unión de tramos, **medir el RMS antes de borrar nada**.
  - El fallo es **intermitente**: que una pieza salga limpia NO valida la etiqueta.
  - Las piezas Kokoro nunca lo tuvieron: `voz.py` ya sintetizaba tramo por tramo.
- **No escribir los guiones sin tildes.** Ver regla dura 2.
- **No unir audio con el demuxer `concat` ni entregar mono/44,1 kHz.** Ver regla dura 3.
- **No poner texto con contorno y sin caja, ni fuera de x[95,930] y[200,1586].** Ver regla dura 4.
- **No dar por corregida una regla de encuadre sin medirla con `pantalla_chica.py`**, y buscar TODAS las funciones que dibujan el mismo bloque: `pie()` y `lamina_cierre()` dibujan los dos el CTA. Ver regla dura 4d.
- **No publicar una pieza de más de 34 s.** Ver regla dura 5.
- **No volver a probar "subir el tamaño de la fuente" para que se lea mejor**: medido el 11/09, 78 px y 96 px dan exactamente lo mismo (0,29) sin caja. Lo que decide es el fondo detrás de la letra.
- **No recortar con `crop` un clip de prensa**: se come el cintillo del medio. Fondo desenfocado + clip centrado.
- **No programar en Metricool ni probar si su tope se soltó**, y **no volver a intentar Zernio**. Ver paso 9.
- **No contar los publicados con `getScheduledPosts` de Metricool**: lo que sale por Higgsfield no aparece ahí y se lee como día vacío. Peor: en Metricool quedaron posts viejos en ERROR cuyas piezas ya salieron por Higgsfield, y "republicar lo que está en ERROR" genera duplicados.
- **No dar por imposible publicar desde una tarea programada sin haberlo intentado en esa corrida.** Ver paso 9.
- No mandar `motor.py` en base64 dentro del comando: se corrompe al transcribirlo.
- No lanzar `render.sh &` en una llamada sin `background:true`: la herramienta espera y mata la llamada.
- No dejar una llamada de `sandbox_exec` corriendo más de ~60 s: el 502 de Cloudflare se lleva el contenedor entero.
- **No encadenar dos llamadas background ni dar por presentes los .py y los paquetes de una llamada anterior**: el sandbox se reinicia solo. Ver paso 7.
- No confiar en un `ls` justo después de una llamada background: puede estar aún escribiendo.
- No correr más de 5 nodos de Eleven a la vez.
- No dar por buena una pieza sin el control de audio completo ni sin el control de pantalla chica.
- No republicar un video defectuoso que ya salió al aire (regla de Cristopher del 07/09/2026): ensucia la muestra de métricas. La corrección se aplica solo a la producción nueva.
- **No comentar a un juez, fiscal o colega por su nombre** en una pieza de noticia: se comenta la institución.
