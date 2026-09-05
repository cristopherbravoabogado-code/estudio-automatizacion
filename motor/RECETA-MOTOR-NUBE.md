# RECETA — Motor de video 100% nube (v1 validada 05/09/2026 · v2 validada 05/09/2026 03:10)

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
   Para el brazo A (Eleven) se sigue el paso 2 de v1 y NO hay tramos.json (el motor corta por silencios como siempre).
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
2. **Voz** (conector Eleven): un flow con `creative_create_flow`; por pieza `creative_add_flow_node` tipo `tts`, modelo `eleven_multilingual_v2`, voz `ClNifCEVq1smkl4M3aTk` (Cristian Cornejo), prompt = gancho + `<break time="1.2s" />` + los 3 puntos + break + cierre. ~500 créditos por pieza.
3. **Gancho** (conector Eleven): `creative_add_flow_node` tipo `image-generation`, modelo `bytedance-seedream-5-pro`, `model_parameters: {"aspect_ratio":"9:16","resolution":"2K"}` (si no se pasa, sale 16:9). Prompt fotorrealista, persona de espaldas o solo manos, "face not visible", sin texto. 818 créditos por imagen.
4. **Correr** con `creative_run_flow_nodes` y `generations_count: 1`. ⚠️ **Máximo 5 nodos por corrida**: el plan admite 5 generaciones concurrentes y las demás fallan con "Too many concurrent requests". Relanzar solo los nodos fallidos.
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

## Grilla
6 diarias (D-10 rev. 05/09): 09:00, 12:00, 13:00, 16:00, 18:00, 20:00. Recalcular con `getBestTimeToPostByNetwork` cada lunes.
Tope de la API de TikTok por terceros: ~25 publicaciones por 24 h.

## Costos por pieza
v2: 0 créditos (voz Kokoro, foto del banco, karaoke whisper). v1 (brazo A de E-01): voz ~500 créditos ≈ US$0,11; foto nueva ~818 solo cada 3 días por materia. Metricool y Higgsfield: sin costo (alojamiento incluido).

## Lo que NO hacer
- No mandar `motor.py` en base64 dentro del comando: se corrompe al transcribirlo.
- No lanzar `render.sh &` en una llamada sin `background:true`: la herramienta espera y mata la llamada.
- No confiar en un `ls` justo después de una llamada background: puede estar aún escribiendo.
- No correr más de 5 nodos de Eleven a la vez.
