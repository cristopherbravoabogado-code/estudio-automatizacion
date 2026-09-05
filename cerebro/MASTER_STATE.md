# MASTER_STATE — Estudio Jurídico San Bernardo

> Archivo cerebro. Todo lo demás cuelga de aquí. Se ACTUALIZA, no se reescribe: cada sesión y cada tarea lo lee primero y lo edita al final (versión nueva en la misma carpeta de Drive, la vieja a la papelera; copia en GitHub cerebro/MASTER_STATE.md).
> Última actualización: 5 de septiembre de 2026, 11:50 Chile (rev. 6 — VIRAL LAB, F11 publicado, tareas atascadas)

## 0. IDENTIDAD Y DOCTRINA
- Estudio Jurídico San Bernardo · Cristopher Jesús Bravo Cea y Natali Saavedra · Pasaje Juan Rau 611, San Bernardo · L-V 08:00-14:00 · WhatsApp +56 9 9690 5994 · defensapenalsanbernardo.cl
- TikTok @abogadocristopherjesus "Estudio Jurídico San Bernardo", ~43.300 seguidores · Metricool brand 6851786 · GitHub cristopherbravoabogado-code/estudio-automatizacion
- Materias: penal (principal), familia, laboral, civil, consumidor, tránsito
- Rige el PROMPT MAESTRO (05/09/2026): autonomía total; regla de las tres vías antes de pedirle algo; a él un solo paso en una frase; verificar, nunca suponer; reportar corto y honesto. Cristopher NO aparece en cámara (fijo). Voz fija: Cristian Cornejo `ClNifCEVq1smkl4M3aTk`, eleven_multilingual_v2.
- Doctrina de contenido: gancho en 2ª persona y dolor concreto en 1,5 s; prohibido "¿Sabías que…"; 5 versiones por gancho; siempre "en San Bernardo"; 60% temas probados (pensión, detención, finiquito, arriendo, licencias) + 1 nuevo al día; libertad creativa total; límites éticos: nada reconocible de un cliente real, nada de resultados prometidos, nada que denigre a jueces/fiscales/colegas por nombre.

## 1. OBJETIVO
400 clientes en cartera. Indicador único de éxito: consultas que llegan al WhatsApp y a la agenda.

## 2. EL SISTEMA — estado al 05/09/2026 11:50
### Cadena 100% nube — PIPELINE v2 (VIDEO LAB, validado 05/09 con un video completo)
guiones (10 ganchos, formato de `videolab/formatos.json`) → voz gratis `videolab/voz.py` (Kokoro → Piper → edge) o Eleven (brazo A del experimento E-01) → foto de gancho del banco → subtítulos karaoke `videolab/karaoke.py` (faster-whisper + libass) → render `motor/motor.py` v2 en sandbox Higgsfield → media_upload Higgsfield (CloudFront) → Metricool createScheduledPost → TikTok.
Receta: GitHub `motor/RECETA-MOTOR-NUBE.md` (sección PIPELINE v2). Costo por pieza v2: 0 créditos. Muestra: https://d2ol7oe51mr4n9.cloudfront.net/user_3IkWukwrqRk5HTPle6Rx8WbYgS3/a328c1ec-6553-4812-bfa2-8ca1d4d9de12.mp4
Cero pasos manuales. Ni Mac ni Drive en la cadena.

### VIRAL LAB (05/09/2026, pedido por Cristopher tras ver el piloto F11)
Ciclo diario: descubrir → radiografiar (`videolab/viral/analizar.py`) → extraer plantilla → adaptar → producir → publicar 21:30 → medir a 72 h. Biblioteca: `videolab/viral/biblioteca.json`. Análisis ejemplo: `videolab/ANALISIS-viral-01.md` (viral: corte cada 1,45 s, 4,7 palabras/s, anuncio de 36 s integrado como argumento).

### VIDEO LAB (módulo de I+D audiovisual, encargado el 05/09/2026)
Carta: `videolab/VIDEO-LAB.md` · Auditoría 01: `videolab/AUDITORIA-2026-09-05.md` · Ranking vivo: `videolab/ranking.json` · Formatos-hipótesis F01-F11: `videolab/formatos.json`.
Veredicto de la auditoría: Eleven ya no es imprescindible (3 voces gratis en CPU con WER igual o mejor); karaoke gratis es el salto de calidad más barato; Higgsfield y Artlist no tienen créditos para generar (Higgsfield 1 crédito, Artlist 1 imagen + 1 video); lo que vale de Higgsfield es gratis (sandbox + CloudFront). El problema sigue siendo conversión y medición, no tecnología.

### Tareas programadas (todas en la nube)
| Tarea | id | Cuándo (Chile) | Hace |
|---|---|---|---|
| Fábrica de videos | trig_01JUV3SAyCc2ncatq5XfkFum | diaria 06:00 | pipeline v2: 6 publicaciones/día, E-01 (3 Kokoro + 3 Eleven alternadas), karaoke en todas, banco de fotos (≤1 nueva por corrida), formatos rotando; reporta 5 líneas |
| Viral Lab | trig_018CyFgUac4dbAC5gpzic9o5 | diaria 15:00 | descubre 1 viral (YouTube Shorts / cuentas semilla de TikTok / lo que mande Cristopher), radiografía con viral/analizar.py, extrae plantilla, adapta guion, produce (pipeline v2 + ensayo.py) y programa a las 21:30; mide a 72 h; bitácora + correo |
| Video Lab I+D | trig_01BV8JLe18MxRn3eyxePSsg6 | mar/jue/sáb 07:00 | investiga UNA pregunta (voz, imagen, b-roll, cómputo gratis, conectores), prueba una herramienta en el sandbox con el texto de referencia, actualiza ranking.json y la auditoría, propone al BACKLOG, reporta 5 líneas |
| Primera respuesta | trig_01GPaDyBcEj2wEjwYi5LH853 | diaria 08:00 | responde consultas de Gmail ofreciendo 2 horas de Calendar, reporta |
| Métricas y aprendizaje | trig_01Gk936c2YuxzPyUnskUYCi1 | lunes 09:00 | lee Metricool, mata/duplica formatos, recalcula grilla, actualiza este archivo |
| Mejora del sistema | trig_01MU1LD9SDfs3nhcrmH6a4PE | diaria 22:00 | verifica lo publicado, implementa UNA mejora, mantiene cerebro/BACKLOG.md |
| Primera lectura de datos | trig_01FxPBHjPv2zkDmwp2ByEwLm | una vez, dom 07/09 10:00 | cierra H-01 con datos |

### Publicaciones en Metricool
- PUBLISHED 04/09: 371318289 fuero maternal · 371318417 guardar silencio
- Sáb 05/09: 371366995 detención hijo 09:00 (PUBLISHED) · 371318444 pensión hasta qué edad 10:00 (PUBLISHED) · 371318462 carta de despido 12:00 · 371314690 promesa compraventa 13:00 · 371367016 pensión impaga 14:30 · 371367026 finiquito firma 16:00 · 371318490 retención sueldo 18:00 · 371367032 arriendo chapa 20:00 · **371468784 F11 piloto 'firmar el finiquito rápido' parte 1 21:30** (voz Kokoro, karaoke, 75 s; primer video del VIRAL LAB)
- PENDING dom 06/09: 371367077 no ver al hijo 10:00 · 371367094 licencia rechazada 12:00 · 371367122 citación fiscalía 15:00 · 371367127 cobranza acoso 18:00 · 371472450 F11 parte 2 'el notario no es un juez' 21:30
- Borrador técnico 371357009 (no publica; borrable)
- Temas ya usados (no repetir): fuero maternal, guardar silencio, pensión hasta qué edad, carta de despido, promesa de compraventa, retención de sueldo, finiquito firma con reserva, pensión impaga/arresto, detención de hijo/24 h, arriendo cambio de chapa, licencia rechazada/Compín, citación Fiscalía, relación directa y regular, cobranza/acoso, finiquito rápido/reserva/notario (serie F11)

## 3. MÉTRICAS
Casi todo vacío todavía. Metricool se conectó el 05/09 y devuelve ceros; la primera lectura real es el domingo 07/09.
- Seguidores ~43.300 · vistas por video del formato anterior ~30 · clientes atribuidos a TikTok: 0 confirmados
- De dónde vienen los clientes hoy: captadoras (la mayoría), web, letreros/volantes, TikTok ~0

## 4. EL PROBLEMA CENTRAL
No es alcance ni producción: es conversión y medición. De los 7 saltos del embudo (ver video → perfil → web → WhatsApp → agenda → consulta → contrato) se mide uno. Corolario: instrumentar el embudo es la mejora de mayor impacto pendiente.

## 5. COSTOS Y LÍMITES QUE GOBIERNAN EL VOLUMEN
- v1 (referencia): voz Eleven ~500 créditos por pieza; imagen de gancho ~818 solo cuando se genera una nueva. Ya gastados ~12.000 el 05/09 en el lote 09 y el banco.
- Banco de fotos de gancho: `motor/ganchos/banco.json` (8 fotos 9:16 por materia, alojadas en CloudFront, sembradas el 05/09). La Fábrica usa la menos usada de la materia; genera 1 nueva por corrida como máximo.
- Pipeline v2: voz Kokoro 0 créditos; Eleven solo en el brazo A de E-01 (3 piezas/día ≈ 1.500 cr/día ≈ 45.000/mes) + 1 foto cada 3 días por materia (≈8.000/mes) → ~53.000/mes, holgado dentro del plan. Si E-01 confirma Kokoro, Eleven queda solo para fotos. Viral Lab: 0 créditos (Kokoro + banco + Pollinations).
- Eleven: máximo 5 generaciones concurrentes por corrida.
- TikTok por API de terceros: ~25 publicaciones/24 h.
- Sandbox Higgsfield: 120 s por llamada, 15 min de vida con background:true, 16.000 caracteres por comando.

## 6. DECISIONES (no volver a discutirlas)
D-01 marca de estudio · D-02 sin la cara de Cristopher · D-03 entretenido, sin tecnicismos · D-04 noticias rehechas en placa propia · D-05 descripción con teléfono, sitio, CTA y descargo · D-06 Metricool publica (Zernio respaldo) · D-07 autonomía total con regla de las tres vías · D-08 nada de clientes, RUT ni causas en herramientas · D-09 producción en el sandbox de Higgsfield, no en el Mac · D-10 (05/09, revisada 03:10) 6 publicaciones diarias en la grilla 09:00 12:00 13:00 16:00 18:00 20:00, con banco de fotos de gancho; subir volumen solo cuando los datos lo justifiquen · D-11 (05/09) VIDEO LAB: ninguna herramienta es imprescindible; prioridad gratis → open source → free tier → bajo costo → premium con datos; toda etapa con primaria, fallback y premium; un experimento a la vez · D-12 (05/09) karaoke palabra por palabra en todas las piezas (costo 0) · D-13 (05/09) VIRAL LAB: una pieza diaria a las 21:30 basada en la ESTRUCTURA de un viral ajeno (nunca su contenido), séptima franja del día; sube de volumen solo con datos

## 7. APRENDIZAJES TÉCNICOS (no repetir el error)
- TikTok no acepta carga por navegador; TikTok Studio corta al superar su tope TOTAL de programados (no son 20 por tanda). Con Metricool los videos no aparecen en TikTok Studio: se publican a la hora.
- El contenedor de Claude no puede publicar bytes ni bajar de CloudFront; el sandbox de Higgsfield sí tiene internet. WebFetch no acepta imágenes: la verificación visual se hace por números (numpy en el sandbox).
- No mandar código en base64 dentro de un comando: se corrompe al transcribirlo. Texto plano por heredoc.
- Un `&` en una llamada normal del sandbox la cuelga; usar background:true. No confiar en `ls` inmediato tras una llamada background.
- Un 200 de la API no es publicado. Verificar estado real.
- Pexels y Pixabay bloquean la búsqueda con Cloudflare; Mixkit responde pero todo es horizontal. Por eso el gancho es imagen 9:16 generada con zoompan.
- `create_file` de Drive exige base64 inline (inviable para video); Drive no edita contenido, solo crea/renombra/papelera.
- Tareas programadas: el 05/09 las corridas de las 06:00, 07:00 y 08:00 quedaron en 'pendiente' más de 5 horas sin ejecutar (problema de la plataforma, no de los prompts). Vigilar: si una corrida lleva >60 min pendiente sin bitácora ni correo, relanzar con fire_trigger o producir a mano.
- Viral Lab: yt-dlp lista YouTube (ytsearch, con vistas) pero NO hashtags de TikTok; sí baja videos y perfiles de TikTok con --impersonate chrome. Pollinations: 1 petición en cola por IP (~40 s c/u). El contenedor de Claude no sube bytes a S3/Google ni instala de PyPI: todo el trabajo pesado va al sandbox.
- Sandbox: sin GPU (8 CPU, 7 GB RAM); pip instala kokoro/piper/edge-tts en ~90 s la primera vez. Kokoro no acepta pausas SSML: se sintetiza por tramos y se unen con 0,7 s de silencio (voz.py entrega los límites exactos). edge-tts es un servicio no oficial: solo fallback. Pollinations sin cuenta entrega 576×1024. Higgsfield generación = 1 crédito; Artlist = 1 imagen + 1 video de por vida.

## 8. HIPÓTESIS ABIERTAS
- H-01 el formato con voz IA no retiene → datos el 07/09
- H-02 el cuello está entre perfil y WhatsApp → sin instrumentar (mejora nº 1 del backlog)
- H-03 penal genera más consultas que civil → sin datos
- H-04 el horario importa menos que el gancho → sin correr
- H-05 el gancho con foto fotorrealista + texto con contorno retiene más que la placa pura → comparar lote 09 contra los 6 anteriores
- E-01 (05/09) voz Kokoro gratis vs Eleven: 3+3 diarias alternadas, corte a 30 por brazo; si Kokoro ≥ 85% de la retención de Eleven → migración total
- H-06 (05/09) el formato F11 'ensayo con anuncio integrado' (anécdota → tesis → estudio como argumento → mitos → parte 2) retiene y convierte más que F01 → 3 ensayos vs F01 de la semana; Cristopher dijo que a él lo retuvo más
- E-02 karaoke vs placas: lote 10+ contra lote 09 · E-03 formatos: 2 nuevos por semana, se mata bajo la mediana a 7 días · E-04 gancho animado (necesita Modal o Artlist) · E-05 voz chilena edge vs Kokoro (después de E-01)

## 9. PRÓXIMOS PASOS
1. Dom 07/09: primera lectura de datos (tarea programada).
2. Instrumentar el embudo (tarea nocturna): link rastreable en la bio, conteo de WhatsApp, origen en cada cita.
3. E-01 voz gratis vs Eleven corre desde la próxima Fábrica; cierre a 30 piezas por brazo (~10 días) en la tarea de Métricas.
4. Formatos nuevos (E-03): 2 por semana desde `videolab/formatos.json`; matar bajo la mediana a 7 días. Serie F11 finiquito: parte 3 ('te pago en dos cuotas') la produce el Viral Lab el 06/09 para el 07/09 21:30.
5. Opcionales de un paso para Cristopher (ninguno bloquea): clave gratis de Pexels (b-roll real) y cuenta gratis en Modal (US$30/mes de GPU: Chatterbox y ganchos animados), ambas en un `claves.txt` de la carpeta Cerebro de Drive, nunca en GitHub.
