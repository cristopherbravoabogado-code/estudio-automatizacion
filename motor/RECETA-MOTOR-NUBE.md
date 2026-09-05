# RECETA — Motor de video 100% nube (validada el 05/09/2026)

Produce y programa TikToks del Estudio Jurídico San Bernardo sin tocar el Mac ni Drive.
Probada de punta a punta con el lote 09 (901-908): 8 videos generados, alojados y programados en ~40 minutos.

## Piezas
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
8 diarias: 09:00, 10:00, 12:00, 13:00, 14:30, 16:00, 18:00, 20:00. Recalcular con `getBestTimeToPostByNetwork` cada lunes.
Tope de la API de TikTok por terceros: ~25 publicaciones por 24 h.

## Costos por pieza
Voz ~500 créditos + imagen ~818 = ~1.320 créditos ≈ US$0,24. Ocho diarias ≈ US$1,9/día. Metricool y Higgsfield: sin costo (alojamiento incluido).

## Lo que NO hacer
- No mandar `motor.py` en base64 dentro del comando: se corrompe al transcribirlo.
- No lanzar `render.sh &` en una llamada sin `background:true`: la herramienta espera y mata la llamada.
- No confiar en un `ls` justo después de una llamada background: puede estar aún escribiendo.
- No correr más de 5 nodos de Eleven a la vez.
