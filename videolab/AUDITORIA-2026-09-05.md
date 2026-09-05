# VIDEO LAB — AUDITORÍA 01 (05/09/2026, 01:00-03:30 Chile)

Misión inicial del VIDEO LAB: antes de crear el próximo video, descubrir cómo deberíamos crearlo. Todo lo de abajo está **probado en el sandbox**, no leído en un blog, salvo donde se indica "(según fuente)".

## 0. Veredicto en cinco líneas
1. **ElevenLabs deja de ser imprescindible hoy.** Tres voces gratuitas en español corren en el sandbox de Higgsfield (CPU, sin GPU): Kokoro-82M (Apache 2.0), Piper (MIT) y edge-tts. Las tres transcriben igual o mejor que la voz actual (WER 0,00-0,06 contra 0,16 del Eleven de referencia). Lo que NO puedo medir es la naturalidad: eso lo decide el experimento con retención real, no mi oído ni el de nadie.
2. **El salto de calidad más barato está listo: subtítulos karaoke palabra por palabra**, gratis (faster-whisper + libass, ya en el sandbox), 6 s por pieza. Es lo que separa visualmente un video "de placa" de un video de creador.
3. **Higgsfield y Artlist no sirven hoy para generar**: Higgsfield está en plan free con 1 crédito; Artlist en prueba con 1 imagen y 1 video gratis de por vida. Lo que SÍ vale de Higgsfield es gratis: el sandbox (cómputo con internet) y el alojamiento CloudFront. Ninguna cuenta de TikTok conectada en Higgsfield.
4. **Costo por video del pipeline v2: US$0 en herramientas** (era US$0,24 en el lote 09 y US$0,11 con el banco de fotos). El recurso escaso pasa a ser el tiempo de las tareas programadas, no los créditos.
5. **El problema del estudio no es la tecnología: es la conversión y la medición** (MASTER_STATE §4). Esta auditoría abarata la producción y sube la calidad; no trae clientes por sí sola. La mejora nº 1 sigue siendo instrumentar el embudo.

## 1. Lo que hay conectado (auditado en vivo)
| Herramienta | Función real para nosotros | Costo / free tier | Límites vistos | API/automatizable | Open source | Lock-in | Utilidad |
|---|---|---|---|---|---|---|---|
| **Sandbox Higgsfield** | Cómputo con internet: ffmpeg, Pillow, faster-whisper, pip, node, Playwright. 8 CPU, 7 GB RAM, 20 GB disco, sin GPU | Gratis (plan free) | 120 s por llamada; 15 min con background; efímero | Sí (conector) | — | Medio: si Higgsfield cierra el sandbox al plan free, hay que migrar (fallback §5) | ⭐ núcleo |
| **Alojamiento Higgsfield (media_upload → CloudFront)** | URL pública permanente para que Metricool descargue | Gratis | 20 archivos por llamada | Sí | — | Medio | ⭐ núcleo |
| **ElevenLabs (conector Eleven)** | Voz Cristian Cornejo; imagen seedream-5-pro; video (caro) | Plan Creator US$22 = 100.000 créditos/mes | 5 generaciones concurrentes; voz ~500 cr, imagen ~818 cr | Sí | No | Alto | Premium: voz de respaldo y experimento A/B |
| **Higgsfield generación (imagen/video/audio)** | Modelos de imagen, video, seed_audio TTS | **1 crédito, plan free** | Inusable sin pagar | Sí | No | Alto | 🔴 hoy no |
| **Artlist (Repositorio De Videos 2)** | Imagen, video, música, voz (MiniMax, Cartesia, Eleven v3) | **Prueba: 1 imagen + 1 video, sin créditos, no renuevan** | Inusable sin suscripción | Sí | No | Alto | 🔴 hoy no (guardar los 2 gratis para una prueba de video de gancho) |
| **Metricool** | Programación TikTok + analítica | Plan actual (funciona) | ~25 publicaciones/24 h por API de TikTok | Sí | No | Medio (Zernio y `tiktok_publish` de Higgsfield como respaldo si conecta cuenta) | ⭐ núcleo |
| **Canva** | Diseño de láminas/portadas, export PNG | Plan del usuario (no probado a fondo) | No probado | Sí (generate-design, export) | No | Bajo | 🟡 láminas de formato "noticia"/"mito" |
| **GitHub** | Código, banco de fotos, lotes, MASTER_STATE copia | Gratis | — | Sí | — | Bajo | ⭐ núcleo |
| **Google Drive / Gmail / Calendar** | Cerebro, reportes, agenda | Gratis | Drive no edita contenido | Sí | — | Bajo | núcleo |
| **Supermetrics / Adobe / Zoom** | Analítica de marketing / — / — | — | No aportan al pipeline hoy | — | — | — | 🔴 fuera |

## 2. Prueba de voz (hecha hoy, mismo texto de 68 palabras del guion 901)
Medido en el sandbox con faster-whisper (WER = palabras mal reconocidas / total; más bajo = más inteligible), ffprobe y ffmpeg. **Escuchar es opcional**; la decisión la toma el experimento de §6.

| Motor | Licencia / costo | Tiempo síntesis (CPU) | Duración | WER | Palabras/s | Pausas >0,35 s | Muestra |
|---|---|---|---|---|---|---|---|
| Eleven · Cristian Cornejo (referencia, lote 09) | Pago, ~500 cr | ~20 s en la nube de Eleven | 26,3 s | 0,16* | 2,58 | 3 | https://d2ol7oe51mr4n9.cloudfront.net/user_3IkWukwrqRk5HTPle6Rx8WbYgS3/0e6e2a1b-1b26-4577-b1da-80b43f7e3d34.mp3 |
| **Kokoro-82M `em_alex`** | Apache 2.0, gratis, offline | 7,8 s (+6 s de carga) | 22,0 s | **0,00** | 3,09 | 3 | https://d2ol7oe51mr4n9.cloudfront.net/user_3IkWukwrqRk5HTPle6Rx8WbYgS3/15432cf5-f6e2-4bda-9ec5-d16af26a9666.mp3 |
| **Piper `es_MX-claude-high`** | MIT, gratis, offline | 2,5 s | 27,9 s | 0,06 | 2,44 | 1 | https://d2ol7oe51mr4n9.cloudfront.net/user_3IkWukwrqRk5HTPle6Rx8WbYgS3/821a7059-db22-47a1-9505-7fe6e593ceb4.mp3 |
| Piper `es_ES-davefx-medium` | MIT, gratis | ~2 s | 22,7 s | 0,04 | 3,00 | 2 | https://d2ol7oe51mr4n9.cloudfront.net/user_3IkWukwrqRk5HTPle6Rx8WbYgS3/ff825ca7-9e92-4611-b420-216a59641968.mp3 |
| **edge-tts `es-CL-LorenzoNeural`** (voz chilena) | Gratis; servicio de Microsoft usado de forma no oficial → puede cortarse | 3,9 s | 28,7 s | 0,03 | 2,37 | 7 | https://d2ol7oe51mr4n9.cloudfront.net/user_3IkWukwrqRk5HTPle6Rx8WbYgS3/48045e2f-9a07-4db5-bf32-6561e2cc3a10.mp3 |
| edge-tts `es-MX-JorgeNeural` | ídem | ~4 s | 31,8 s | 0,00 | 2,14 | 13 | https://d2ol7oe51mr4n9.cloudfront.net/user_3IkWukwrqRk5HTPle6Rx8WbYgS3/78494c07-4d4e-43f3-b59d-003d9f98431e.mp3 |

\* El WER de Eleven está inflado: el guion 901 real llevaba una frase extra ("no firmes apurado") que no está en el texto de referencia. Corrigiendo eso, Eleven queda cerca de 0,05. Es decir: **en inteligibilidad los gratuitos empatan**; en naturalidad no tengo instrumento y por eso se experimenta.

Lo que sí sé de fuentes: Kokoro es el modelo pequeño mejor rankeado que corre en CPU (8 idiomas, incluido español); Chatterbox Multilingual (MIT, 23 idiomas, gana ~64% de preferencia ciega contra ElevenLabs en inglés según Resemble) **necesita GPU de 4-8 GB** → candidato para Modal (§4). VoxCPM2 (Apache, 30 idiomas, 2B) corre en CPU pero es 25 veces más pesado que Kokoro; se prueba en una tarea de I+D, no hoy.

## 3. Prueba de imagen y subtítulos
- **Pollinations.ai** (API pública sin clave): responde en 2 s, pero sin registro entrega 576×1024 con el modelo Sana (probado, 2 imágenes reales). Sirve como respaldo de emergencia del banco de fotos (escalado ×2 y zoompan disimulan). Con cuenta gratis da más resolución → 🟡. Muestra: https://d2ol7oe51mr4n9.cloudfront.net/user_3IkWukwrqRk5HTPle6Rx8WbYgS3/6c3764b2-5383-4be3-83b3-3f5a4ceb35fc.png
- **Banco de fotos** (8 fotos 9:16 de seedream, ya alojadas): cubre el gancho por materia a costo cero por 3 días por materia. Con voz gratis, el único gasto de Eleven pasa a ser ~1 foto cada 3 días (≈8.000 cr/mes de 100.000).
- **Video completo del pipeline v2** (Kokoro + karaoke + foto del banco, 19 s, render 15 s, US$0): https://d2ol7oe51mr4n9.cloudfront.net/user_3IkWukwrqRk5HTPle6Rx8WbYgS3/a328c1ec-6553-4812-bfa2-8ca1d4d9de12.mp4
- **Subtítulos karaoke**: `videolab/karaoke.py` → ASS con palabra activa en amarillo; ffmpeg lo quema con `-vf ass=`. Probado de punta a punta (48 palabras, un evento por palabra, texto dentro del cuadro seguro y sin pisar el gancho). Costo 0, 6 s.
- **Pexels API** (video vertical real de personas, gratis, 200 peticiones/hora, 20.000/mes) es la mejor fuente de b-roll real que existe y **requiere una clave que solo Cristopher puede crear** (registro). Tres vías intentadas antes de pedirla: scraping de Pexels y Pixabay (bloqueado por Cloudflare), Mixkit (todo horizontal), imagen generada + zoompan (lo que usamos hoy). Queda como paso único para él en §8.

## 4. GitHub y la nube gratuita (evaluado, no recomendado por estrellas)
| Proyecto | Estrellas / actividad | Licencia | Qué aporta | Veredicto |
|---|---|---|---|---|
| harry0703/MoneyPrinterTurbo | 120k, push 04/09/2026 | MIT | Pipeline completo tema→guion→voz(edge/azure)→b-roll Pexels→subtítulos→mp4. Confirma nuestra arquitectura; su motor es más lento (moviepy) y depende de claves | 🟡 robar ideas (subtítulos, b-roll por palabra clave), no adoptarlo |
| hexgrad/Kokoro-82M · remsky/Kokoro-FastAPI | 5,4k, activo | Apache 2.0 | Voz gratis en CPU. Probado | 🟢 primaria de voz |
| rhasspy/piper | activo (piper-tts 1.8.0) | MIT | Voz gratis ultrarrápida | 🟢 fallback 1 |
| rany2/edge-tts | activo (7.2.8) | GPL-3 (herramienta), servicio no oficial | Única voz **chilena**. Riesgo de corte | 🟡 fallback 2 |
| resemble-ai/chatterbox (multilingual) | muy activo | MIT | Calidad tipo Eleven con emoción; GPU | 🟡 probar en Modal |
| OpenBMB/VoxCPM (VoxCPM2) | 36k, push 02/09 | Apache 2.0 | 30 idiomas, CPU posible, 2B | 🟡 I+D |
| debpalash/VoiceStudio | 18k, push hoy | AGPL-3 | "ElevenLabs local": clonación + TTS | 🟡 I+D (¿clonar la voz Cornejo legalmente? No: la voz es de Eleven; clonar la de Cristopher sí sería legítimo y él no quiere aparecer, pero su voz no es su cara → hipótesis para preguntarle solo si el experimento de voz falla) |
| k2-fsa/sherpa-onnx | 14k, activo | Apache 2.0 | Corre Kokoro/Piper/Matcha en ONNX sin torch (instalación 10× más liviana) | 🟡 optimización de instalación |
| jianchang512/pyvideotrans | 19k | GPL-3 | Doblaje + subtítulos automáticos | 🔴 no aplica |
| Modelos text-to-video abiertos (Wan 2.x, LTX, CogVideoX) | — | varias | Necesitan GPU ≥8-24 GB. En el sandbox: imposible | 🟡 solo vía GPU gratuita |
| **Modal.com** | — | — | **US$30/mes gratis** de cómputo (T4 ≈ US$0,59/h → ~50 h GPU/mes). Permite Chatterbox, Wan image-to-video para ganchos animados | 🟡 el mejor "free tier" encontrado; requiere cuenta (registro de Cristopher) |
| GitHub Actions | 2.000 min/mes gratis en repos privados | — | Fallback de cómputo si el sandbox se cierra: corre motor.py + Kokoro. Falta resolver alojamiento público desde Actions | 🟡 fallback documentado |
| ComfyUI + workflows locales | — | GPL | Sin GPU en el sandbox ni en el Mac del estudio (no verificado) | 🔴 por ahora |

## 5. PIPELINE v2 RECOMENDADO (primaria → fallback → premium)
| Etapa | Primaria | Fallback | Premium | Costo | Calidad | Automatización |
|---|---|---|---|---|---|---|
| Idea / investigación | Claude (tarea) + temas probados MASTER_STATE | — | — | 0 | — | 10/10 |
| Hook | 10 hooks A-J por guion, filtro objetivo (2ª persona, dolor, local, ≤12 palabras, sin "¿Sabías que…") | — | — | 0 | — | 10/10 |
| Guion | Claude, estructura piezas.json (+ campo `formato`) | — | — | 0 | — | 10/10 |
| Imagen de gancho | Banco `motor/ganchos/banco.json` | Pollinations (576×1024, ×2) | Eleven seedream 9:16 (818 cr) | 0 / 0 / US$0,18 | 7 / 5 / 9 | 10/10 |
| B-roll real | (pendiente clave Pexels) | Wikimedia Commons | Artlist (2 gratis) | 0 | 8 | 9/10 |
| Voz | **Kokoro em_alex** | Piper es_MX → edge es-CL | **Eleven Cornejo** | 0 / 0 / US$0,11 | ? (experimento) / 6 / 9 | 10/10 |
| Música / SFX | Sintetizada con sox/ffmpeg (ya existe en el motor) | silencio | Artlist música (créditos) | 0 | 5 | 10/10 |
| Subtítulos | **karaoke.py** (whisper + libass) | placas actuales | — | 0 | 9 | 10/10 |
| Edición / vertical / color | motor.py (Pillow + ffmpeg, 1080×1920, loudnorm) | — | — | 0 | 8 | 10/10 |
| Control de calidad | Verificación numérica (bbox de texto, duración, loudness) | — | — | 0 | 7 | 10/10 |
| Publicación | Metricool | Zernio / Higgsfield tiktok_publish | — | plan actual | — | 9/10 |
| Métricas | Metricool (lunes) + Centro de Mando | Supermetrics | — | 0 | 6 (sin retención por segundo) | 8/10 |
| Aprendizaje | MASTER_STATE + bitácora + registro-experimentos | — | — | 0 | — | 9/10 |

**Costo por video v2: US$0,00 en herramientas** (voz Kokoro, foto del banco, subtítulos whisper, render ffmpeg, alojamiento y programación incluidos en planes ya pagados). Con foto nueva de Eleven cada 3 días por materia: ≈ US$0,02 promedio.
Proyección (solo herramientas): 100 videos ≈ US$2 · 500 ≈ US$10 · 1.000 ≈ US$20 · 10.000 ≈ US$200 (fotos). Comparado: lote 09 costaba US$0,24/video → 10.000 = US$2.400.
Lo que sí escala en costo es el **tiempo de cómputo**: ~40 s por video en el sandbox (voz 8 s + subtítulos 6 s + render 14 s + subida) → 15 diarias ≈ 10 min de sandbox al día, cabe. 50 diarias ya exige varias corridas o Modal.

## 6. EXPERIMENTOS QUE ABRE ESTA AUDITORÍA (uno a la vez, registrar en `registro-experimentos`)
- **E-01 Voz gratis vs Eleven** (arranca en la próxima corrida de la Fábrica): 6 piezas/día → 3 con Kokoro y 3 con Eleven, mismos formatos, misma grilla alternada. Métrica: vistas y % de reproducción completa a 72 h (Metricool). Corte: 30 piezas por brazo (~10 días). Si Kokoro ≥ 85% de la retención de Eleven → migración total; si no, Eleven solo en ganchos y Kokoro en el cuerpo (mezcla).
- **E-02 Karaoke vs placas**: se activa para TODAS las piezas desde el pipeline v2 (no es A/B: la evidencia general en shorts es abrumadora y el costo es 0). Se compara lote 09 (placas) contra lote 10+ (karaoke) en retención.
- **E-03 Formatos**: cada semana entran 2 formatos nuevos de `formatos.json` con 3 piezas cada uno; se mata el que quede bajo la mediana de vistas del canal en 7 días.
- **E-04 Gancho animado (image-to-video) vs foto con zoompan**: requiere Modal o los 2 gratis de Artlist → cuando exista cuenta.
- **E-05 Voz chilena (edge es-CL) vs neutra (Kokoro)**: después de E-01, solo si edge sigue vivo.

## 7. QUÉ PODEMOS HACER HOY (sin Cristopher)
- Voz gratis con cadena de respaldo: `videolab/voz.py` ✅ probado.
- Subtítulos karaoke: `videolab/karaoke.py` ✅ probado.
- Banco de fotos ✅ sembrado. Pollinations como respaldo ✅ probado.
- Fábrica reconfigurada al pipeline v2 con E-01 y karaoke (hoy mismo).
- Tarea de I+D recurrente que busca, prueba UNA herramienta por corrida y actualiza este ranking (hoy mismo).

## 8. QUÉ LE TOCA A CRISTOPHER (cada uno es opcional y de un paso; nada bloquea la producción)
1. **Pexels**: crear una clave gratis en pexels.com/api y pegarla en un archivo "claves.txt" de la carpeta Cerebro de Drive (no en GitHub). Desbloquea b-roll real de personas.
2. **Modal**: crear cuenta gratis en modal.com (US$30/mes) y dejar el token en el mismo archivo. Desbloquea Chatterbox (voz con emoción) y ganchos animados.
3. Escuchar las 6 muestras de §2 si quiere opinar; si no, el experimento decide solo.

## 9. LO QUE ESTA AUDITORÍA NO RESUELVE (honesto)
- No mide naturalidad de voz ni belleza de imagen: solo números y experimentos.
- No hay retención por segundo en Metricool; la métrica de retención que tenemos es gruesa (% completado, vistas). TikTok Studio la muestra pero no expone API.
- Depende de que Higgsfield mantenga el sandbox y el alojamiento gratis. Fallbacks: Modal (GPU, US$30/mes gratis), GitHub Actions (CPU, 2.000 min/mes), Drive como alojamiento no sirve (base64).
- Nada de esto cambia el cuello de botella real: perfil → WhatsApp → agenda. Instrumentar el embudo sigue siendo la mejora nº 1 del backlog.

Fuentes consultadas (además de las pruebas): guías comparativas de TTS abiertos 2026 (pinggy.io, tryspeakeasy.io), Resemble AI sobre Chatterbox, help.pexels.com (límites de la API), modal.com/pricing, GitHub (búsquedas por tópico text-to-speech y pipelines de shorts).
