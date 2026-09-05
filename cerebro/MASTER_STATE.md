# MASTER_STATE — Estudio Jurídico San Bernardo

> Archivo cerebro. Todo lo demás cuelga de aquí. Se ACTUALIZA, no se reescribe: cada sesión y cada tarea lo lee primero y lo edita al final (versión nueva en la misma carpeta de Drive, la vieja a la papelera; copia en GitHub cerebro/MASTER_STATE.md).
> Última actualización: 5 de septiembre de 2026, 02:15 Chile (rev. 3 — fábrica en marcha)

## 0. IDENTIDAD Y DOCTRINA
- Estudio Jurídico San Bernardo · Cristopher Jesús Bravo Cea y Natali Saavedra · Pasaje Juan Rau 611, San Bernardo · L-V 08:00-14:00 · WhatsApp +56 9 9690 5994 · defensapenalsanbernardo.cl
- TikTok @abogadocristopherjesus "Estudio Jurídico San Bernardo", ~43.300 seguidores · Metricool brand 6851786 · GitHub cristopherbravoabogado-code/estudio-automatizacion
- Materias: penal (principal), familia, laboral, civil, consumidor, tránsito
- Rige el PROMPT MAESTRO (05/09/2026): autonomía total; regla de las tres vías antes de pedirle algo; a él un solo paso en una frase; verificar, nunca suponer; reportar corto y honesto. Cristopher NO aparece en cámara (fijo). Voz fija: Cristian Cornejo `ClNifCEVq1smkl4M3aTk`, eleven_multilingual_v2.
- Doctrina de contenido: gancho en 2ª persona y dolor concreto en 1,5 s; prohibido "¿Sabías que…"; 5 versiones por gancho; siempre "en San Bernardo"; 60% temas probados (pensión, detención, finiquito, arriendo, licencias) + 1 nuevo al día; libertad creativa total; límites éticos: nada reconocible de un cliente real, nada de resultados prometidos, nada que denigre a jueces/fiscales/colegas por nombre.

## 1. OBJETIVO
400 clientes en cartera. Indicador único de éxito: consultas que llegan al WhatsApp y a la agenda.

## 2. EL SISTEMA — estado al 05/09/2026 02:15
### Cadena 100% nube (validada de punta a punta con el lote 09)
guiones → voz (Eleven, tts) + imagen 9:16 (Eleven, seedream-5-pro) → render motor.py en sandbox Higgsfield → media_upload Higgsfield (URL CloudFront pública) → Metricool createScheduledPost → TikTok.
Receta completa: GitHub `motor/RECETA-MOTOR-NUBE.md`. Código: `motor/motor.py`, `motor/render.sh`. Guiones del lote 09: `motor/piezas-lote09.json`.
Cero pasos manuales. Ni Mac ni Drive en la cadena.

### Tareas programadas (todas en la nube)
| Tarea | id | Cuándo (Chile) | Hace |
|---|---|---|---|
| Fábrica de videos | trig_01JUV3SAyCc2ncatq5XfkFum | diaria 06:00 | completa 8 publicaciones hoy y mañana siguiendo la RECETA, reporta 5 líneas |
| Primera respuesta | trig_01GPaDyBcEj2wEjwYi5LH853 | diaria 08:00 | responde consultas de Gmail ofreciendo 2 horas de Calendar, reporta |
| Métricas y aprendizaje | trig_01Gk936c2YuxzPyUnskUYCi1 | lunes 09:00 | lee Metricool, mata/duplica formatos, recalcula grilla, actualiza este archivo |
| Mejora del sistema | trig_01MU1LD9SDfs3nhcrmH6a4PE | diaria 22:00 | verifica lo publicado, implementa UNA mejora, mantiene cerebro/BACKLOG.md |
| Primera lectura de datos | trig_01FxPBHjPv2zkDmwp2ByEwLm | una vez, dom 07/09 10:00 | cierra H-01 con datos |

### Publicaciones en Metricool
- PUBLISHED 04/09: 371318289 fuero maternal · 371318417 guardar silencio
- PENDING sáb 05/09: 371366995 detención hijo 09:00 · 371318444 pensión hasta qué edad 10:00 · 371318462 carta de despido 12:00 · 371314690 promesa compraventa 13:00 · 371367016 pensión impaga 14:30 · 371367026 finiquito firma 16:00 · 371318490 retención sueldo 18:00 · 371367032 arriendo chapa 20:00
- PENDING dom 06/09: 371367077 no ver al hijo 10:00 · 371367094 licencia rechazada 12:00 · 371367122 citación fiscalía 15:00 · 371367127 cobranza acoso 18:00
- Borrador técnico 371357009 (no publica; borrable)
- Temas ya usados (no repetir): fuero maternal, guardar silencio, pensión hasta qué edad, carta de despido, promesa de compraventa, retención de sueldo, finiquito firma con reserva, pensión impaga/arresto, detención de hijo/24 h, arriendo cambio de chapa, licencia rechazada/Compín, citación Fiscalía, relación directa y regular, cobranza/acoso

## 3. MÉTRICAS
Casi todo vacío todavía. Metricool se conectó el 05/09 y devuelve ceros; la primera lectura real es el domingo 07/09.
- Seguidores ~43.300 · vistas por video del formato anterior ~30 · clientes atribuidos a TikTok: 0 confirmados
- De dónde vienen los clientes hoy: captadoras (la mayoría), web, letreros/volantes, TikTok ~0

## 4. EL PROBLEMA CENTRAL
No es alcance ni producción: es conversión y medición. De los 7 saltos del embudo (ver video → perfil → web → WhatsApp → agenda → consulta → contrato) se mide uno. Corolario: instrumentar el embudo es la mejora de mayor impacto pendiente.

## 5. COSTOS Y LÍMITES QUE GOBIERNAN EL VOLUMEN
- Por pieza: voz ~500 créditos Eleven + imagen ~818 = ~1.320 (≈US$0,24). 8 diarias ≈ 10.500 créditos/día ≈ 317.000/mes.
- ⚠️ El plan Creator de ElevenLabs trae 100.000 créditos/mes. A 8 diarias se agota en ~10 días. Opciones (decisión de Cristopher, es un pago): subir el plan, o reusar la imagen de gancho por materia (baja a ~4.600/día ≈ 140.000/mes) y bajar a 6 diarias (~100.000/mes).
- Eleven: máximo 5 generaciones concurrentes por corrida.
- TikTok por API de terceros: ~25 publicaciones/24 h.
- Sandbox Higgsfield: 120 s por llamada, 15 min de vida con background:true, 16.000 caracteres por comando.

## 6. DECISIONES (no volver a discutirlas)
D-01 marca de estudio · D-02 sin la cara de Cristopher · D-03 entretenido, sin tecnicismos · D-04 noticias rehechas en placa propia · D-05 descripción con teléfono, sitio, CTA y descargo · D-06 Metricool publica (Zernio respaldo) · D-07 autonomía total con regla de las tres vías · D-08 nada de clientes, RUT ni causas en herramientas · D-09 producción en el sandbox de Higgsfield, no en el Mac · D-10 (05/09) 8 publicaciones diarias, ni más ni menos, en la grilla 09:00 10:00 12:00 13:00 14:30 16:00 18:00 20:00

## 7. APRENDIZAJES TÉCNICOS (no repetir el error)
- TikTok no acepta carga por navegador; TikTok Studio corta al superar su tope TOTAL de programados (no son 20 por tanda). Con Metricool los videos no aparecen en TikTok Studio: se publican a la hora.
- El contenedor de Claude no puede publicar bytes ni bajar de CloudFront; el sandbox de Higgsfield sí tiene internet. WebFetch no acepta imágenes: la verificación visual se hace por números (numpy en el sandbox).
- No mandar código en base64 dentro de un comando: se corrompe al transcribirlo. Texto plano por heredoc.
- Un `&` en una llamada normal del sandbox la cuelga; usar background:true. No confiar en `ls` inmediato tras una llamada background.
- Un 200 de la API no es publicado. Verificar estado real.
- Pexels y Pixabay bloquean la búsqueda con Cloudflare; Mixkit responde pero todo es horizontal. Por eso el gancho es imagen 9:16 generada con zoompan.
- `create_file` de Drive exige base64 inline (inviable para video); Drive no edita contenido, solo crea/renombra/papelera.

## 8. HIPÓTESIS ABIERTAS
- H-01 el formato con voz IA no retiene → datos el 07/09
- H-02 el cuello está entre perfil y WhatsApp → sin instrumentar (mejora nº 1 del backlog)
- H-03 penal genera más consultas que civil → sin datos
- H-04 el horario importa menos que el gancho → sin correr
- H-05 (nueva) el gancho con foto fotorrealista + texto con contorno retiene más que la placa pura → comparar lote 09 contra los 6 anteriores

## 9. PRÓXIMOS PASOS
1. Dom 07/09: primera lectura de datos (tarea programada).
2. Instrumentar el embudo (tarea nocturna): link rastreable en la bio, conteo de WhatsApp, origen en cada cita.
3. Resolver el tope de créditos de Eleven (decisión de pago de Cristopher).
4. Karaoke y variantes de formato en el motor (tarea nocturna, una por noche).
