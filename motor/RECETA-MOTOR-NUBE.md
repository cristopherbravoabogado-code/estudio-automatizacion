# RECETA — Motor de video 100% nube (v1 validada 05/09/2026 · v2 validada 05/09/2026 03:10 · voz Eleven por tramos 08/09/2026)

Produce y programa TikToks del Estudio Jurídico San Bernardo sin tocar el Mac ni Drive.
Probada de punta a punta con el lote 09 (901-908): 8 videos generados, alojados y programados en ~40 minutos.


## ⭐ PIPELINE v2 (VIDEO LAB, 05/09/2026) — voz gratis + subtítulos karaoke. ES EL VIGENTE.
Cambia solo los pasos 2 y 7; todo lo demás igual. Costo por pieza: 0 créditos (salvo foto nueva del banco cada 3 días).
Muestra real de v2 (Kokoro + karaoke + foto del banco): https://d2ol7oe51mr4n9.cloudfront.net/user_3IkWukwrqRk5HTPle6Rx8WbYgS3/a328c1ec-6553-4812-bfa2-8ca1d4d9de12.mp4

**Experimento E-01 vigente**: de las 6 piezas del día, 3 llevan voz Kokoro (brazo B, campo `"voz_motor":"kokoro"` en la pieza) y 3 voz Eleven Cristian Cornejo (brazo A, `"voz_motor":"eleven"`), alternando en la grilla (09 B, 12 A, 13 B, 16 A, 18 B, 20 A). Todas llevan karaoke. Se registra el brazo en el piezas-<fecha>.json y en la bitácora. Corte: 30 piezas por brazo.

2v2. **Voz gratis** (brazo B) en el sandbox, dentro de la misma llamada background que instala:
   `pip install -q piper-tts edge-tts kokoro soundfile && python3 -m piper.download_voices es_MX-claude-high` (~90 s la primera vez por sandbox; las siguientes ~5 s).
   Escribir `videolab/voz.py` y `videolab/karaoke.py` desde GitHub COMO TEXTO PLANO (heredoc), y por pieza un `urls/<n>.txt` con los 5 tramos separados por UNA LÍNEA EN BLANCO (gancho / punto 1 / punto 2 / punto 3 / cierre; cada punto = "Título. Detalle.").
   `python3 voz.py urls/<n>.txt <n>.mp3 auto` → imprime `VOZ_OK motor=kokoro dur=.. tramos=5` y deja `<n>.mp3.tramos.json` con 6 límites. Cadena: kokoro → piper → edge; si las tres fallan, la pieza pasa al brazo A (Eleven) y se anota.
   Para el brazo A (Eleven) se sigue el paso 2 de v1 — que desde el 08/09/2026 TAMBIÉN es por tramos y TAMBIÉN deja `tramos.json`.
7v2. **Subtítulos**: `python3 karaoke.py <n>.mp3 <n>.ass` (→ `KARAOKE_OK`), ~6 s. Sirve para ambos brazos.
   En `pieza.json` agregar `"subs":"<n>.ass"` y, si existe, `"tramos": <contenido de <n>.mp3.tramos.json>`. `motor.py` v2 quema el karaoke (solo desde el fin del gancho), deja las láminas con título solo y re-encodea (≈15 s por pieza).
Verificación numérica extra: en 2 cuadros de láminas debe haber píxeles amarillos (R>200,G>200,B<90) entre y=1150 y y=1400 → el karaoke está.

Formato F11 ENSAYO (videolab/ensayo.py, 05/09): guion de 4 párrafos (anécdota / tesis+promesa / puente+estudio / mitos+parte 2), voz con `voz.py guion.txt v.mp3 kokoro`, karaoke, 26-30 fotos (banco + Pollinations de a UNA por vez: el servicio admite 1 petición en cola por IP, ~40 s cada una, reintentar ante 429), `pieza.json` con shots y placas (tiempos sacados de los timestamps de whisper: tesis, GRATIS·PRESENCIAL, MITO 1-3, PARTE 2), `python3 ensayo.py pieza.json salida.mp4` (~45 s). Ver videolab/ANALISIS-viral-01.md.

Lo que NO hacer en v2: no pasar el texto a voz.py sin líneas en blanco (saldría un solo tramo y el motor cortaría por silencios de 0,4 s que no existen); no usar edge-tts como primaria (servicio no oficial); no mezclar voces dentro de una pieza.

## Piezas (v1)
- `motor.py` — render (Pillow + ffmpeg). Entrada `pieza.json` con voz.mp3 y hook.png; salida mp4 1080x1920 h264+aac, 24-29 s
- `render.sh` — bucle: lee `urls/<n>.voz` y `urls/<n>.hook`, descarga, renderiza a `out/<id>.mp4`, escribe `out/log.txt`
- `piezas.json` — guiones: `{id, materia, gancho, puntos:[{t,d}x3], cierre, hook_prompt, hashtags}`

## Flujo (cada paso es una herramienta distinta)
1. **Guiones** (Claude): 8 piezas. Gancho en segunda persona y dolor concreto, nunca "¿Sabías que…". Local: "en San Bernardo". Materias rotando laboral/familia/penal/civil. 60% temas ya probados (pensión, detención, finiquito, arriendo, licencias).
2. **Voz** (conector Eleven) — ⚠️ **UNA LLAMADA TTS POR TRAMO, SIN NINGUNA ETIQUETA `<break>`** (corregido 08/09/2026, ver "Lo que NO hacer"):
   un flow con `creative_create_flow`; **5 nodos `tts` por pieza** (gancho / punto 1 / punto 2 / punto 3 / cierre), cada uno con `creative_add_flow_node`, modelo `eleven_multilingual_v2`, voz `ClNifCEVq1smkl4M3aTk` (Cristian Cornejo), `generations_count: 1`.
   El prompt de cada nodo es SOLO el texto de ese tramo, con tildes y eñes, sin etiquetas de ningún tipo.
   Los 5 mp3 se bajan al sandbox y se unen ahí con ffmpeg intercalando SILENCIO REAL generado con `anullsrc`:
   decodificar cada tramo a wav 44100 mono, concatenar `w1 sil w2 sil w3 sil w4 sil w5` con el demuxer `concat`, `loudnorm=I=-16:TP=-1.5:LRA=11`, salida mp3 96k.
   Al hacerlo se escribe `<n>.mp3.tramos.json` con los 6 límites acumulados (fin de tramo i + pausa), igual que `videolab/voz.py`, y se pasa en el campo `"tramos"` de la pieza: el motor corta exacto y ya no depende de `silencedetect`.
   **Largo de la pausa**: 1,05 s. Con 0,45 s la pieza queda en ~18,5 s y se sale de la ventana 20-35 s; 1,05 s deja ~21 s y reproduce la cadencia de las piezas que ya salían bien (sus uniones medían 0,96-1,30 s). ~350 créditos por pieza (5 llamadas cortas).
3. **Gancho** (conector Eleven): `creative_add_flow_node` tipo `image-generation`, modelo `bytedance-seedream-5-pro`, `model_parameters: {"aspect_ratio":"9:16","resolution":"2K"}` (si no se pasa, sale 16:9). Prompt fotorrealista, persona de espaldas o solo manos, "face not visible", sin texto. 818 créditos por imagen.
4. **Correr** con `creative_run_flow_nodes` y `generations_count: 1`. ⚠️ **Máximo 5 nodos por corrida**: el plan admite 5 generaciones concurrentes y las demás fallan con "Too many concurrent requests". Con la voz por tramos, los 5 nodos tts de UNA pieza llenan exactamente la corrida: la imagen del gancho va en otra corrida. Relanzar solo los nodos fallidos.
5. **Recoger URLs** con `creative_get_flow_run_status` (campo `media[].master_url`; el mp3 y el png están en storage.googleapis.com, firmados por 2 horas).
6. **Alojamiento** (Higgsfield): `media_upload` con `files[]` (hasta 20) devuelve por archivo una `upload_url` S3 (PUT) y la `url` pública CloudFront definitiva.
7. **Sandbox** (Higgsfield `sandbox_exec`):
   - Llamada 0 con `background:true`: crear carpetas, escribir `motor.py` COMO TEXTO PLANO (no base64: al transcribirlo a mano se corrompe), `piezas.json`, `render.sh`, y terminar con `sleep 850`. Ese proceso mantiene vivo el sandbox 15 minutos; las llamadas siguientes ven los mismos archivos.
   - Llamadas 1..n (≤16.000 caracteres cada una): escribir `urls/<n>.voz` y `urls/<n>.hook` con heredocs. Caben 3 piezas por llamada.
   - Render: `./render.sh 901 902 903` en `background:true` (14 s por pieza). Poll con `cat out/log.txt`.
   - Subida: `curl -X PUT -H "Content-Type: video/mp4" --data-binary @out/<id>.mp4 '<upload_url>'` → debe devolver 200. Caben 3 por llamada.
8. **Confirmar** con `media_confirm` (`media_ids[]`, type video).
9. **Programar** (Metricool `createScheduledPost`, blogId 6851786, timezone America/Santiago): `media:[url CloudFront]`, `providers:[{network:tiktok}]`, `tiktokData.title` = gancho (obligatorio), `privacyOption PUBLIC_TO_EVERYONE`, text = gancho / 3 líneas "Título: detalle." / cierre / bloque CTA / 8 hashtags. Metricool descarga y re-aloja en static.metricool.com.
10. **Verificar** con `getScheduledPosts` que estén PENDING, y al día siguiente que estén PUBLISHED. Un 200 no es publicado.

## Verificación sin ojos
El contenedor de Claude no puede bajar de CloudFront ni WebFetch acepta imágenes. Se verifica por números en el sandbox: extraer 5 cuadros con ffmpeg, medir con numpy la caja de píxeles claros (L>215) y comprobar que no toque bordes (franja de 40 px) y que quede dentro de x[60,1020] y[120,1730].

**Control de audio obligatorio (desde 08/09/2026, por el defecto del `<break>`)** — un mp4 renderizado no es un mp4 bueno; se mide:
1. `ffmpeg -i <n>.mp4 -vn -ac 1 -ar 16000 <n>.wav` y transcribir con faster-whisper `small`, `language="es"`, `word_timestamps=True`, `vad_filter=False`.
2. Normalizar (minúsculas, sin tildes) y contar cuántas palabras transcritas NO están en el vocabulario del guion. **Debe dar 0.** Tolerar solo homófonos conocidos de whisper (`filiación`→`afiliación`, `SOAP`→`swap`, `criar`→`crear`, `golpean`→`colpean`): son error del transcriptor, no ruido del audio, y se corrigen en el `.ass` SIN tocar los tiempos.
3. Medir el RMS de cada hueco entre tramos con numpy (`f32le` a 16 kHz). **Silencio real ≤ -35 dBFS.** Si un hueco mide como la voz (≈ -15 dBFS) es que el motor de voz vocalizó algo que no debía: rehacer la pieza.

## Grilla
6 diarias (D-10 rev. 05/09): 09:00, 12:00, 13:00, 16:00, 18:00, 20:00. Recalcular con `getBestTimeToPostByNetwork` cada lunes.
Tope de la API de TikTok por terceros: ~25 publicaciones por 24 h.

## Costos por pieza
v2: 0 créditos (voz Kokoro, foto del banco, karaoke whisper). v1 (brazo A de E-01): voz ~350 créditos ≈ US$0,08 con las 5 llamadas por tramo; foto nueva ~818 solo cada 3 días por materia. Metricool y Higgsfield: sin costo (alojamiento incluido).

## Lo que NO hacer
- **NUNCA poner etiquetas `<break time="..." />` en el texto que se manda a ElevenLabs.** Es la causa del defecto de audio del lote 911-917 (diagnosticado 08/09/2026). `eleven_multilingual_v2` a veces NO interpreta la etiqueta como pausa: la LEE EN VOZ ALTA como si fuera texto, y salen sílabas sin sentido al volumen normal de la voz.
  - Caso medido, pieza **917**: la voz decía "…nunca lo reconoció" y acto seguido soltaba **1,26 s de basura entre 2,42 s y 3,68 s** ("y sigue con VIE", según whisper), justo en la unión gancho → punto 1, es decir exactamente donde iba el primer `<break time="1.2s" />`. Ese tramo medía **-15,55 dBFS**, idéntico a la voz normal (-15,60 dBFS), mientras que las uniones sanas de las otras piezas medían entre -38 y -59 dBFS.
  - **Whisper no estaba alucinando.** En el karaoke de la 917 whisper transcribió "y sigue con VIE." y se borró del subtítulo creyendo que era alucinación: estaba transcribiendo el ruido real. Si whisper mete palabras que no están en el guion justo en una unión de tramos, **es audio de verdad, no alucinación** — hay que ir a mirar el RMS antes de borrar nada.
  - El fallo es **intermitente**: de las 4 piezas Eleven del lote (912, 914, 916, 917) solo la 917 lo mostró, y solo en 1 de sus 4 uniones. Que una pieza salga limpia NO valida la receta con `<break>`; hay que medir pieza por pieza. Por eso se elimina la etiqueta del todo.
  - Sustituto: 5 nodos `tts` (uno por tramo) + silencio real con `anullsrc` unido con ffmpeg en el sandbox. Con eso las 4 uniones de la 917 rehecha miden **-240 dBFS (pico 0,0000)**: silencio digital, imposible que suene nada.
  - Las piezas Kokoro (911, 913, 915) nunca tuvieron el defecto: `videolab/voz.py` ya sintetizaba tramo por tramo y unía con silencio real. La lección es solo para el brazo Eleven.
- No mandar `motor.py` en base64 dentro del comando: se corrompe al transcribirlo.
- No lanzar `render.sh &` en una llamada sin `background:true`: la herramienta espera y mata la llamada.
- No confiar en un `ls` justo después de una llamada background: puede estar aún escribiendo.
- No correr más de 5 nodos de Eleven a la vez.
- No dar por buena una pieza sin el control de audio de "Verificación sin ojos": el defecto del `<break>` era inaudible para el pipeline hasta que se midió.
