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
1. **Nada.** La pieza ya está subida: el libro de cuentas trae su `media_id`.
   `python3 motor/publicar.py ficha N` lo imprime. Si no hay `media_id`, y solo entonces, hay que
   subirla (abajo).

   ⚠️ **La URL de la Release de GitHub NO sirve para `media_import_url`.** Medido el 19/09/2026,
   dos veces y desde los dos lados:
   - lo que GitHub **guarda** está bien: la API dice `content_type: video/mp4` en los 24 assets del día;
   - lo que GitHub **sirve** no: la url firmada de descarga trae
     `response-content-type=application/octet-stream`, y la respuesta final llega con ese tipo.

   Higgsfield contesta `Unsupported content-type: application/octet-stream`. **El que sube no puede
   cambiarlo**: así entrega GitHub *todos* los assets de una Release. No es un error del render ni
   se arregla subiendo "mejor" — el 19/09 se intentó exactamente eso y fue un callejón sin salida.

   Por eso la pieza se sube a Higgsfield **antes** de su hora y lo que se guarda es el `media_id`.
   La Release sigue siendo útil: es de donde la pre-subida saca los bytes, y para `curl` el tipo
   servido da lo mismo.

### La pre-subida (fuera de la hora de publicar)
La hace **T1.5** (`trig_01JUV3SAyCc2ncatq5XfkFum`, 09:00 UTC / 06:00 Chile), después del render de
las 08:00 UTC y una hora antes de la primera ranura. `python3 motor/publicar.py presubir` imprime
qué falta y los cinco pasos exactos; no hay que averiguar nada.

Por pieza, con los bytes bajados de la Release:
`media_upload` (nombre, `video/mp4`) → PUT de los bytes a la `upload_url` firmada → `media_confirm`
→ `python3 motor/cadena.py anotar N --campo media_id=<id>`.

⚠️ El PUT **necesita** la cabecera `Content-Type: video/mp4`: la firma incluye `content-type`
(`X-Amz-SignedHeaders=content-type;host`), así que sin ella el PUT falla.

Es la parte lenta —la `upload_url` mide ~1.800 caracteres y hay que escribirla— y por eso **no va
a la hora de publicar**: va justo después del render, cuando nada corre contra el reloj. Cada pieza
se anota apenas se confirma, así que si la sesión abandona se pierde el resto, nunca lo hecho.
Ese es el reparto que importa: lo lento, temprano y reanudable; lo de la hora, corto y sin averiguar.

2. `tiktok_prepare_publish` → `publish_session_id`. Pide **`video_url`** (la del CDN:
   `https://d2ol7oe51mr4n9.cloudfront.net/user_3IkWukwrqRk5HTPle6Rx8WbYgS3/<media_id>.mp4`),
   **no** un `media_id`; y **`mode`**, no `post_mode`. Además `media_type: VIDEO`.
   ⚠️ **El título no puede pasar de 150 caracteres** o rechaza la llamada entera
   (`title: Too big: expected string to have <=150 characters`). `publicar.py` lo arma contando
   y la ficha imprime el largo. La sesión caduca en ~2 h.
3. `tiktok_publish` con ese session_id, y **todas** las banderas de `required_confirmations` que
   devolvió el paso 2 en `true`: `user_confirmed`, `preview_confirmed`, `music_usage_confirmed`,
   `processing_notice_acknowledged`, `privacy_level_selected_by_user`,
   `interaction_settings_selected_by_user`, `commercial_content_disclosure_selected_by_user`.
   ⛔ Si una herramienta **niega el permiso**, eso no es un fallo de red y no se sortea
   reintentando: se anota el motivo literal con `cadena.py fallar` y se sigue con la siguiente
   pieza. Un motivo escrito tal cual es lo que permite arreglarlo después; insistir, no.
4. `tiktok_publish_status` hasta `PUBLISH_COMPLETE`.
- `DIRECT_POST` publica de verdad. `UPLOAD_TO_DRAFT` deja la pieza en los borradores de TikTok y es el último recurso.
- Cupos: 5 posts/minuto y 13/24 h por cuenta. TikTok solo acepta **5 borradores** sin terminar a la vez.
- Ajustes fijos del estudio: `privacy_level PUBLIC_TO_EVERYONE`, `is_aigc true`, comentarios/dúo/stitch habilitados,
  sin divulgación de contenido comercial, sin música añadida.

## ⛔ 19/09/2026, 16:50 Chile: `tiktok_publish` DESAPARECIÓ de la caja de herramientas

Las ranuras 1 a 4 de hoy salieron por la vía B y quedaron con su `publish_id`. A las 16:50, al
publicar la pieza de Cerro Chuño, el paso 3 **ya no existía**:

- `tiktok_prepare_publish` responde bien y entrega `publish_session_id` (probado: sesión
  `793d0f7f-7c6c-4157-9233-8f96795e9c6b`, válida 2 h).
- `tiktok_publish_status` sigue disponible.
- `tiktok_publish` **no aparece** en la lista de herramientas, ni por nombre exacto
  (`select:mcp__Higgsfield__tiktok_publish` → *No matching deferred tools found*) ni por búsqueda.
- La cuenta NO es el problema: `tiktok_accounts` la da `active`.
- Tampoco hay una app del Marketplace que lo reemplace: `apps_search("tiktok")` → vacío.

Lo dice el propio `tiktok_prepare_publish` en su respuesta: *"Publication requires authorization
supplied privately to the widget. **Clients without MCP Apps cannot publish**"*. O sea: el paso 3
se sirve solo a clientes que saben dibujar el formulario. Una sesión de Claude Code —esta y, por lo
mismo, **también las tareas programadas**— no lo es.

**Consecuencia para la fábrica:** mientras esto siga así, la vía B produce, sube y prepara, pero
**no publica sola**. El último clic queda en la app. No se arregla reintentando ni cambiando el
título; no es un error, es un permiso que no se entrega por aquí. Antes de dar por perdida la
tarde, el paso 3 se vuelve a buscar: si reaparece, la ficha sigue sirviendo tal cual está.

### Y la vía A no es el respaldo: está muerta
El 19/09 se probó Metricool con esta misma pieza (post 378684028). Lo aceptó y quedó `PENDING`…
y Cristopher lo cortó de inmediato: **"Metricool no funciona hace tiempo, eso ya se sabe."**
El post se dejó en borrador y fuera de fecha. **No volver a proponerlo.** Lo del tope de la cuenta
sigue siendo cierto, pero el punto es más simple: esa vía no se usa más.

### Lo que queda mientras tanto
1. La pieza se termina igual: render, subida a Higgsfield y `tiktok_prepare_publish`.
2. Se le pasa a Cristopher el link de CloudFront y el texto ya contado, y él publica desde su
   teléfono. Es un minuto suyo, no una tarde.
3. **Lo pendiente de verdad:** una tercera vía que publique sin formulario, o confirmar que
   `tiktok_publish` vuelve. Hasta que eso exista, "10 al día sin tocar nada" es prometer de más,
   y decirlo es parte del trabajo.

## ⛔ La causa de verdad por la que el día no salía (19/09/2026)

Durante semanas la explicación fue "las tareas largas de esta cuenta arrancan y nunca cierran".
Es verdad que no cierran. **La razón no era el largo.** El 19/09, mirando las dos sesiones de T2
por dentro, quedó a la vista:

| Corrida | Dónde quedó | Resultado |
|---|---|---|
| 10:08 | `mcp__Github_1__search_repositories` (paso 1, a los 19 s) | no publicó nada |
| 12:08 | `mcp__Github_1__create_or_update_file` (el commit, al final) | **publicó bien** y quedó sin anotar |

Las dos con `status_bucket: SESSION_STATUS_BUCKET_BLOCKED` y `session_status:
SESSION_STATUS_REQUIRES_ACTION`. **Estaban esperando que alguien aprobara un permiso.** Las
herramientas MCP de GitHub no vienen aprobadas en una tarea programada: la lista de herramientas
de esas sesiones es `Bash, Write, Edit, Read, Glob, Grep, …` y nada de `mcp__Github_1__*`. A las
04:00 de la mañana no hay nadie para contestar el permiso, así que la tarea se queda ahí. Para
siempre. No falla: espera.

**La regla, entonces:** en una tarea programada, el repositorio se toca con `git` por Bash y con
nada más. `git` no pide permiso. Si `git push` falla, se dice en el reporte y se termina; buscar
otra herramienta es garantizar que la tarea quede colgada.

Y hay una consecuencia que no es obvia: **una publicación sin commitear es peor que no publicar.**
El antidoble de `cadena.py` lee el libro de cuentas; si el libro sigue diciendo `alojado`, la
corrida siguiente ve la ranura vencida y **la publica de nuevo**. El 19/09 la corrida de las 13:07
habría repetido el post de las 12:08. Se evitó anotando a mano antes de esa hora.

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
