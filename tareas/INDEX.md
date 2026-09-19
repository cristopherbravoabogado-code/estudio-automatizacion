# Tareas programadas del Estudio Jurídico San Bernardo

> **Rediseño del 19/09/2026 — la cadena de 10 piezas diarias.** El diseño que describe el resto
> de este archivo (11/09) sigue siendo el registro de respaldo de las tareas que no cambiaron,
> pero la columna vertebral de producción y publicación se reemplazó. Los prompts vigentes están
> en `tareas/PROMPTS-CADENA.md` y la doctrina en `motor/CADENA.md`.
>
> **Qué cambió y por qué.** La lectura del 19/09 mostró "SB 06:00 Producción del día: ABANDONED"
> y "M8 Verificación legal: ABANDONED". Ninguna pieza de código estaba mala: nada en el sistema
> sabía cuántas piezas debía tener el día ni en qué estado iba cada una, así que una tarea que
> moría a la mitad perdía su trabajo sin dejar rastro. Ahora el día vive en `estado/<fecha>.json`,
> versionado, y cada tarea lee y escribe ahí.
>
> | Antes | Ahora |
> |---|---|
> | Una tarea larga produce el día entero | Actions renderiza; las tareas de Claude solo encolan y publican |
> | 3 piezas por tanda (tope de caracteres del sandbox) | sin tope: las upload_url van en un archivo del repo |
> | 10 tareas de un disparo, creadas cada día | una tarea horaria que publica lo vencido y reintenta sola |
> | El antidoble es una regla escrita en prosa | `cadena.py` sale con código 2 si intentas republicar |
> | Metricool programaba | descartada el 19/09 por el tope de la cuenta; solo vía B |
>
> Las tareas M1 a M10 y las de causas y consultas **no se tocaron**.

Respaldo del diseño del sistema al **11/09/2026**. Si una tarea se borra o se corrompe, se reconstruye desde aquí con `create_trigger`.

**La hora de Chile es la hora UTC menos 3** (Chile está en UTC−3 desde el 06/09/2026). Los cron están en UTC.

## Por qué existe este archivo

El 8 y 9 de septiembre el estudio pasó dos días sin publicar. Los videos estaban hechos y programados, pero Metricool los rechazó con `providers[].status = ERROR` y el detalle "You have reached your Metricool account limit", y ninguna pieza del sistema leía ese campo. Se construyó la fábrica pero no el termómetro.

Además se midió que **ninguna de las tareas caídas tenía `finished_at`**: no fallaban a mitad, arrancaban y nunca cerraban. Las dos únicas que sí cerraron (07/09) eran cortas y de solo lectura. La más liviana de todas también murió el 10/09, así que el peso del prompt no lo explica todo — pero la regla de diseño que quedó es clara: **tareas cortas, un solo trabajo, reporte de 3 líneas**.

## Las tres reglas del sistema

1. **Toda tarea crítica necesita otra que la mire.** Las 5 revisiones se cubren entre sí, la de 00:00 cubre a las cuatro, y el Vigilante cada 3 h cubre a la de 00:00.
2. **Publicar nunca puede depender de producir.** Siempre debe haber una reserva de al menos 3 videos ya renderizados y alojados. Si falla el render, el Vigilante publica de la reserva.
3. **Ningún camino crítico sin respaldo probado.** Un respaldo que nunca se ejecutó no es un respaldo.

## Constantes operativas

- Metricool: `brandId 6851786`, zona `America/Santiago`
- TikTok en Higgsfield: `connector_id f23f2205-1ae6-4259-8240-e6f4165bbe79`
- URL de publicación: `https://d2ol7oe51mr4n9.cloudfront.net/user_3IkWukwrqRk5HTPle6Rx8WbYgS3/<media_id>.mp4`
- Vía viva: `tiktok_prepare_publish` → `tiktok_publish` → `tiktok_publish_status`. Cupos 5/minuto y 13/24 h
- ⚠️ `media_import_url` **no** sirve con la url de la Release de GitHub: GitHub sirve todos los
  assets de una Release como `application/octet-stream` (aunque los guarde como `video/mp4`) y
  Higgsfield los rechaza. Medido el 19/09 desde los dos lados. Por eso existe T1.5: los bytes
  suben antes de la hora y lo que viaja después es el `media_id`
- Solo `PUBLISHED` cuenta como publicado. Un 200 al crear un post no prueba nada
- Reglas duras del motor: un nodo de voz por tramo sin etiquetas `<break>`; textos siempre con tildes y ñ; audio estéreo 48 kHz; concatenar con el filtro `concat`, nunca con `-c copy`; control de audio antes de publicar (0 palabras fuera del guion, RMS de uniones ≤ −35 dBFS)

## Columna vertebral — reescrita el 19/09/2026

Las cuatro tareas se **reconvirtieron**, no se crearon de nuevo: conservan sus 17 conectores
guardados. Eso importa — una tarea creada desde una sesión de Claude Code nace SIN conectores y
no podría publicar en TikTok. Si alguna hay que rehacerla, hay que hacerlo desde claude.ai o
desde un chat que tenga los conectores, nunca desde Claude Code.

Los prompts vigentes están en `tareas/PROMPTS-CADENA.md`.

| Tarea | id | cron UTC | Chile | Qué hace |
|---|---|---|---|---|
| **T1-NOCHE** encolar mañana | `trig_01ByZCVLhuBMRvSAH1vjbP9v` | `0 22 * * *` | 19:00 | Encola las ranuras 1–5 de mañana |
| **T1-MAÑANA** encolar la tarde | `trig_01R2vJVkPRhzSqfU7vt2Sehc` | `0 11 * * *` | 08:00 | Encola las ranuras 6–10 con noticia fresca |
| **T1.5** Pre-subida | `trig_01JUV3SAyCc2ncatq5XfkFum` | `0 9,13,17 * * *` | 06/10/14 | Sube a Higgsfield las piezas ya renderizadas y guarda su `media_id` |
| **T2** Publicador | `trig_01NUjhWgu3AAA6ah6njxgVQy` | `0 0,1,10-23 * * *` | 16 veces/día | Publica lo vencido; reintenta solo a la hora siguiente |
| **T3** Vigilante | `trig_018BGjU648of7vJq2YiRUhe7` | `34 */3 * * *` | cada 3 h | Audita; solo publica si algo venció hace +2 h |
| SB 15:00 Viral y noticia | `trig_0131ftuMmRUmhdgoC47eaQiP` | `0 18 * * *` | 15:00 | Sin cambios: pieza de reacción del día |
| SB 00:00 Auditoría | `trig_01UDYCznrf4Yr5TXDHiNVrmE` | `0 3 * * *` | 00:00 | Sin cambios |

El render ya no lo hace ninguna de ellas: lo hace `.github/workflows/render-diario.yml` a las
05:00, 09:00, 13:00 y 17:00 de Chile, sin sesión de por medio.

**Por qué T1.5 corre tres veces y no una.** T1-MAÑANA encola las ranuras 6–10 a las 11:00 UTC,
o sea *después* de la pasada de las 09:00. Con una sola corrida, esas cinco piezas se
renderizarían pero nunca se pre-subirían, y la tarea horaria volvería al camino largo justo en la
mitad del día. Las pasadas de 13:00 y 17:00 las recogen con horas de margen (la ranura 6 vence a
las 20:00 UTC). Cuando no hay nada pendiente, `presubir` lo dice en una línea y la tarea cierra:
una corrida vacía no cuesta casi nada, y una pieza sin pre-subir cuesta el hueco del día.

**El reparto por tiempo (19/09).** T1.5 existe porque el trabajo pesado no puede caer a la hora de
publicar. El 19/09 la ranura de las 07:00 no salió: T2 disparó a las 10:08 UTC y seguía `PENDING`
sin `finished_at` a las 10:20, porque le tocaba subir 10 MB y transcribir una url firmada de 1.800
caracteres. Con la pieza ya subida, T2 hace tres llamadas y cierra. **Lo lento va temprano y es
reanudable; lo de la hora es corto y no averigua nada.**

**Los prompts traen una guarda**: si `motor/cadena.py` no existe en `main`, la tarea responde una
línea y termina sin hacer nada. Así no hacen daño mientras el rediseño no esté mergeado.

## Mejora del video — M1 a M10

| Tarea | id | cron UTC | Chile | Qué hace |
|---|---|---|---|---|
| M1 Banco de clips virales | `trig_01KxrVyybA4gQ1cWLfTUo1nF` | `0 8 * * *` | 05:00 | Deja 3 clips recortados y alojados con su ángulo legal |
| M2 Radar de noticias legales | `trig_015kDL6fHEMJL3CNtUh1Wjut` | `0 10 * * *` | 07:00 | 3 fichas de prensa con la norma verificada |
| M8 Verificación legal de la cola | `trig_01TXifCaWXReeHb7hECqcaoi` | `0 13 * * *` | 10:00 | Contrasta cada afirmación contra fuente primaria |
| M4 Laboratorio de ganchos | `trig_01ULGiX3Xv2Uud932bQVDMiJ` | `0 16 * * *` | 13:00 | Mide qué tipo de gancho retiene y escribe 15 nuevos |
| M6 Herramienta nueva | `trig_019AZBmEMvhJygNmTGvHQG2L` | `0 19 * * 1,3,5` | 16:00 L/X/V | Prueba una técnica nueva con números y la implementa o descarta |
| M7 Competencia | `trig_01TfmL3FwvmAetWU8q9DqtLE` | `0 20 * * 2,4` | 17:00 Ma/J | Mecánica de los abogados que sí funcionan |
| M9 Comentarios | `trig_016KsewKNAXgP2e52jEqTFex` | `0 23 * * *` | 20:00 | Preguntas repetidas a fichas de video; aparta consultas |
| M3 Autopsia | `trig_01TtbKfakimHDs9GqkxBFuPa` | `0 0 * * *` | 21:00 | 3 mejores y 3 peores; escribe la orden de mañana |
| M5 Calidad técnica | `trig_0187pienqrfGKRHac84c5hEv` | `0 2 * * *` | 23:00 | Transcribe y mide cada mp4 publicado y en cola |
| M10 Experimento semanal | `trig_018oCGfR96kkeGvQNTvccva6` | `0 12 * * 0` | dom 09:00 | Cierra el A/B con números y diseña el siguiente |

## Series

| Tarea | id | cron UTC | Chile | Qué hace |
|---|---|---|---|---|
| ¿Delito o no delito? | `trig_01DQG9HieY5c5HiaQVL9Lfdx` | `0 21 * * 5` | vie 18:00 | Capítulo semanal: clip discutible + veredicto con artículo |

## Cadena de alimentación

M1 y M2 dejan materia prima → la revisión de las 15:00 produce → M8 verifica el derecho y M5 la técnica antes de salir → M3, M4, M9 y M7 dicen qué cambiar mañana → M6 y M10 cambian el pipeline y el estándar → las 5 revisiones publican y el Vigilante tapa los huecos.

## Tareas desactivadas (no reactivar sin rediseñarlas cortas)

Se colgaban siempre en ABANDONED o PENDING y su trabajo quedó absorbido en las nuevas: Fábrica de videos 06:00 `trig_01JUV3SAyCc2ncatq5XfkFum`, Viral Lab 15:00 `trig_018CyFgUac4dbAC5gpzic9o5`, Tendencia del día 10:00 `trig_012g4GgzsCQusrCuQPD439w3`, Mejora del sistema 22:00 `trig_01MU1LD9SDfs3nhcrmH6a4PE`, Video Lab I+D `trig_01BV8JLe18MxRn3eyxePSsg6`.

Siguen activas y sin tocar: Primera respuesta a consultas 08:00, Revisión diaria de causas 07:00, Métricas de los lunes y los recordatorios de audiencias.
