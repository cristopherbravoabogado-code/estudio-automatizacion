# Tareas programadas del Estudio Jurídico San Bernardo

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
- Vía de respaldo: `media_import_url` → `tiktok_prepare_publish` → `tiktok_publish`. Cupos 5/minuto y 13/24 h
- Solo `PUBLISHED` cuenta como publicado. Un 200 al crear un post no prueba nada
- Reglas duras del motor: un nodo de voz por tramo sin etiquetas `<break>`; textos siempre con tildes y ñ; audio estéreo 48 kHz; concatenar con el filtro `concat`, nunca con `-c copy`; control de audio antes de publicar (0 palabras fuera del guion, RMS de uniones ≤ −35 dBFS)

## Columna vertebral — las 5 revisiones + vigilante

| Tarea | id | cron UTC | Chile | Qué hace |
|---|---|---|---|---|
| SB 06:00 Producción del día | `trig_01R2vJVkPRhzSqfU7vt2Sehc` | `0 9 * * *` | 06:00 | Cuenta la cola y produce lo que falte |
| SB 12:00 ¿Salieron al aire? | `trig_01NUjhWgu3AAA6ah6njxgVQy` | `0 15 * * *` | 12:00 | Verifica publicación real y republica lo caído |
| SB 15:00 Viral y noticia | `trig_0131ftuMmRUmhdgoC47eaQiP` | `0 18 * * *` | 15:00 | Pieza de reacción o noticia, publicada el mismo día |
| SB 19:00 Cierre del día | `trig_01ByZCVLhuBMRvSAH1vjbP9v` | `0 22 * * *` | 19:00 | Publicación, consultas, métricas, cola de mañana |
| SB 00:00 Auditoría | `trig_01UDYCznrf4Yr5TXDHiNVrmE` | `0 3 * * *` | 00:00 | Audita protocolos y cubre a las otras cuatro |
| SB Vigilante | `trig_018BGjU648of7vJq2YiRUhe7` | `4 */3 * * *` | cada 3 h | Detecta tareas a medias y publica de la reserva |

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
