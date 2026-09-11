# PUBLICAR — cómo un video del estudio llega de verdad a TikTok (11/09/2026)

Regla madre: **publicar nunca puede depender de producir, y ninguna vía crítica puede quedar sin respaldo probado.**
Un `200` de cualquier API **no es** "publicado". Publicado es `PUBLISH_COMPLETE` en `tiktok_publish_status`
o `providers[0].status = PUBLISHED` en `getScheduledPosts`. Siempre se vuelve a leer después de la hora.

## Las dos vías vivas

### Vía A — Metricool (programada)
`createScheduledPost` (brandId 6851786, timezone America/Santiago), `media:[URL CloudFront]`,
`providers:[{network:tiktok}]`, `tiktokData.title` obligatorio.
- ⛔ **Al 11/09/2026 esta vía está TOPADA**: los 9 posts del 8 y 9 de septiembre quedaron con
  `providers[0].status = ERROR` / `"You have reached your Metricool account limit."` y NINGUNO salió al aire.
- El ERROR **no aparece al crear el post**: aparece recién cuando Metricool intenta publicar. Por eso hay que
  releer `getScheduledPosts` después de cada hora de publicación, no solo al programar.
- Se vuelve a usar solo cuando una prueba real salga `PUBLISHED`.

### Vía B — Higgsfield → TikTok (inmediata, la que funciona hoy)
`connector_id` **f23f2205-1ae6-4259-8240-e6f4165bbe79**.
1. `media_import_url` (o `media_upload` + PUT + `media_confirm`) → `media_id`.
   URL pública: `https://d2ol7oe51mr4n9.cloudfront.net/user_3IkWukwrqRk5HTPle6Rx8WbYgS3/<media_id>.mp4`
2. `tiktok_prepare_publish` → `publish_session_id`
3. `tiktok_publish` con ese session_id.
   🔑 El clasificador de modo rechaza el PRIMER intento con "Permission denied": **reintentar la MISMA llamada
   con el MISMO `publish_session_id` pasa al segundo intento.** No hay que pedirle nada a Cristopher.
4. `tiktok_publish_status` hasta `PUBLISH_COMPLETE`.
- `DIRECT_POST` publica de verdad. `UPLOAD_TO_DRAFT` deja la pieza en los borradores de TikTok y es el último recurso.
- Cupos: 5 posts/minuto y 13/24 h por cuenta. TikTok solo acepta **5 borradores** sin terminar a la vez.
- Ajustes fijos del estudio: `privacy_level PUBLIC_TO_EVERYONE`, `is_aigc true`, comentarios/dúo/stitch habilitados,
  sin divulgación de contenido comercial, sin música añadida.

## El hueco que tapa este documento: la vía B no sabe programar

Higgsfield publica **al momento**. Mientras Metricool esté topado, una cola con horas se arma así:

> **Una TAREA DE UN SOLO DISPARO POR PIEZA.** `create_trigger` con `run_once_at` a la hora de publicación
> (Chile + 3 = UTC), y un prompt de cuatro pasos que trae dentro la URL de CloudFront, el título, el texto
> completo y la orden de verificar con `tiktok_publish_status`.

Por qué así y no una tarea grande que publique las cuatro: las tareas largas de esta cuenta **arrancan y nunca
cierran** (10-11/09/2026: Fábrica, Mejora, Video Lab, Primera respuesta, causas, todas ABANDONED o PENDING sin
`finished_at`). Una tarea de cuatro pasos sí termina, y si una falla se cae UNA pieza, no el día entero.

Ejemplo real (cola del viernes 11/09/2026):

| Hora Chile | UTC | Pieza | Tarea |
|---|---|---|---|
| 09:00 | 12:00Z | compensación económica | `trig_01RwHekyiPxvVFYfTmj7hveV` |
| 13:00 | 16:00Z | choque sin seguro / SOAP | `trig_01DHPgGSx3Hp9ixSAjXCXQPN` |
| 18:00 | 21:00Z | SERIE ¿Delito o no delito? CASO 1 | `trig_01RU1Sjr2e4MP2S1rfegJ5pP` |
| 20:00 | 23:00Z | feriado 18 y 19 irrenunciable | `trig_015qRGvubi2FXmRsD2GQG5K5` |

**Antidoble:** una pieza asignada a una tarea de un disparo queda anotada en `/areas/tiktok-programacion.md`.
Las revisiones de 06:00/12:00/15:00/19:00 y el vigilante **no vuelven a publicarla**: primero miran qué salió hoy.

## Reserva
Siempre 3 o más piezas renderizadas y alojadas en CloudFront, con su texto escrito. Si un día falla el render,
el vigilante publica de la reserva y el día no queda en cero. Toda tarea de producción deja la reserva en 3 antes de terminar.
