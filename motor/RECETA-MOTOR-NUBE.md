# RECETA — Motor de video 100% nube (v1 05/09/2026 · v2 05/09/2026 · voz Eleven por tramos 08/09/2026 · **v3 audio 11/09/2026**)

Produce y programa TikToks del Estudio Jurídico San Bernardo sin tocar el Mac ni Drive.
Probada de punta a punta con el lote 09 (901-908): 8 videos generados, alojados y programados en ~40 minutos.

**Para PUBLICAR (y para programar una hora sin Metricool) ver `motor/PUBLICAR.md`.**

---

## ⛔ LAS TRES REGLAS DURAS (si se rompe una, la pieza no sale)

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
Verificación numérica extra: en 2 cuadros de láminas debe haber píxeles amarillos (R>200,G>200,B<90) entre y=1150 y y=1400.

### Campo `rotulo` (v3) — el rótulo de la esquina del gancho
Por defecto dice `DRAMATIZACIÓN`. Con `"rotulo":"¿DELITO O NO DELITO?"` (o `"18 DE SEPTIEMBRE"`, o el nombre de
la serie que sea) el motor lo cambia y ajusta solo el ancho de la caja. **Así se produce la serie semanal y las
piezas de reacción/noticia sin escribir un motor aparte**: gancho = clip real (mp4) con el rótulo de la serie,
punto 1 = "Comenta antes del veredicto", puntos 2 y 3 = el veredicto con su artículo y su pena, cierre = la marca.

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

Formato F11 ENSAYO (videolab/ensayo.py, 05/09): guion de 4 párrafos, voz con `voz.py`, karaoke, 26-30 fotos,
`python3 ensayo.py pieza.json salida.mp4` (~45 s). Ver videolab/ANALISIS-viral-01.md.

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
   **Preferir metraje real de Mixkit** (ver arriba) cuando exista: lo generado por IA es último recurso.
4. **Correr** con `creative_run_flow_nodes`. ⚠️ **Máximo 5 nodos por corrida**.
5. **Recoger URLs** con `creative_get_flow_run_status` (`media[].master_url`, firmadas por 2 horas).
6. **Alojamiento** (Higgsfield): `media_upload` con `files[]` devuelve `upload_url` S3 (PUT) y la `url` CloudFront definitiva.
7. **Sandbox** (Higgsfield `sandbox_exec`):
   - El sandbox es efímero: se descarta ~10 s después de cada llamada. Con `background:true` se toma un lease de
     15 minutos; terminar el comando con `sleep 800` mantiene vivos los archivos para las llamadas siguientes.
   - Escribir `motor.py` COMO TEXTO PLANO (no base64: al transcribirlo se corrompe). Tope 16.000 caracteres por llamada.
   - Render: ~15 s por pieza. Subida: `curl -X PUT -H "Content-Type: video/mp4" --data-binary @out/<id>.mp4 '<upload_url>'` → 200.
8. **Confirmar** con `media_confirm` (`media_ids[]`, type video).
9. **Publicar / programar**: ver `motor/PUBLICAR.md`. Metricool está topado desde el 08/09/2026; la vía viva es
   Higgsfield → TikTok, y la hora se fija con una tarea de un solo disparo por pieza.
10. **Verificar**: `PUBLISH_COMPLETE` o `PUBLISHED`. Un 200 no es publicado.

## Verificación sin ojos
El contenedor de Claude no puede bajar de CloudFront ni WebFetch acepta imágenes. Se verifica por números en el sandbox: extraer cuadros con ffmpeg, medir con numpy la caja de píxeles claros (L>215) y comprobar que no toque bordes ni se salga de x[60,1020] y[120,1730].

**Control de audio obligatorio (desde 08/09/2026; ampliado el 11/09/2026)** — un mp4 renderizado no es un mp4 bueno; se mide:
1. `ffprobe -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels` → **debe decir `aac,48000,2`**. Si no, la pieza se re-muxea; no se publica en mono ni a 44,1 kHz.
2. `ffmpeg -i <n>.mp4 -vn -ac 1 -ar 16000 <n>.wav` y transcribir con faster-whisper `small`, `language="es"`, `word_timestamps=True`, `vad_filter=False`.
3. Normalizar (minúsculas, sin tildes) y contar las palabras transcritas que NO están en el vocabulario del guion. **Debe dar 0**, descontando:
   - **cifras**: el guion dice "dieciocho" y whisper escribe "18". Ignorar todo token que sea solo dígitos o puntuación.
   - **homófonos conocidos** de whisper (`filiación`→`afiliación`, `SOAP`→`swap`, `criar`→`crear`, `golpean`→`colpean`, `bencineras`→`vencineras`): son error del transcriptor, se corrigen en el `.ass` SIN tocar los tiempos.
   - Cualquier otra palabra fuera del guion **no es alucinación hasta que se mida el RMS** (lección de la 917).
4. Medir el RMS de cada hueco entre tramos con numpy (`f32le` a 16 kHz), ventana [límite−0,62 s, límite−0,10 s].
   **Silencio real ≤ −35 dBFS** (con voz.py v3 dan −240 dBFS). Si un hueco mide como la voz (≈ −15 dBFS), rehacer la pieza.

## Grilla
6 diarias (D-10 rev. 05/09): 09:00, 12:00, 13:00, 16:00, 18:00, 20:00. Recalcular con `getBestTimeToPostByNetwork` cada lunes.
Viernes 18:00 queda tomado por la SERIE "¿Delito o no delito?".
Tope de la API de TikTok por terceros: ~25 publicaciones por 24 h; el conector de Higgsfield corta antes: 13/24 h.

## Costos por pieza
v2/v3: 0 créditos (voz Kokoro, metraje Mixkit, karaoke whisper). v1 (brazo A): voz ~350 créditos ≈ US$0,08; foto nueva ~818 solo cada 3 días por materia.

## Lo que NO hacer
- **NUNCA poner etiquetas `<break time="..." />` en el texto que se manda a ElevenLabs.** Es la causa del defecto de audio del lote 911-917 (diagnosticado 08/09/2026). `eleven_multilingual_v2` a veces NO interpreta la etiqueta como pausa: la LEE EN VOZ ALTA y salen sílabas sin sentido al volumen normal de la voz.
  - Caso medido, pieza **917**: tras "…nunca lo reconoció" soltaba **1,26 s de basura entre 2,42 s y 3,68 s**, justo en la unión donde iba el primer `<break>`. Ese tramo medía **−15,55 dBFS**, igual que la voz (−15,60), mientras las uniones sanas median entre −38 y −59 dBFS.
  - **Whisper no estaba alucinando**: transcribía el ruido real. Si whisper mete palabras en una unión de tramos, **medir el RMS antes de borrar nada**.
  - El fallo es **intermitente**: que una pieza salga limpia NO valida la etiqueta.
  - Las piezas Kokoro nunca lo tuvieron: `voz.py` ya sintetizaba tramo por tramo.
- **No escribir los guiones sin tildes.** Ver regla dura 2.
- **No unir audio con el demuxer `concat` ni entregar mono/44,1 kHz.** Ver regla dura 3.
- No mandar `motor.py` en base64 dentro del comando: se corrompe al transcribirlo.
- No lanzar `render.sh &` en una llamada sin `background:true`: la herramienta espera y mata la llamada.
- No confiar en un `ls` justo después de una llamada background: puede estar aún escribiendo.
- No correr más de 5 nodos de Eleven a la vez.
- No dar por buena una pieza sin el control de audio completo.
- No republicar un video defectuoso que ya salió al aire (regla de Cristopher del 07/09/2026): ensucia la muestra de métricas. La corrección se aplica solo a la producción nueva.
