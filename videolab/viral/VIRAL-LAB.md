# VIRAL LAB — De videos que ya funcionaron a videos del estudio (05/09/2026)

Cristopher lo pidió el 05/09/2026 después del piloto F11: "armar una estructura donde creamos y publiquemos videos a base de videos virales que ya funcionaron para otras personas". Es un módulo del VIDEO LAB; nada se copia, se **extrae la estructura** (gancho, ritmo, orden de bloques, dónde entra el anuncio, cómo cierra) y se vuelve a escribir con contenido jurídico propio, ilustrativo y ético.

## El ciclo (una vuelta por día)
0. **RADAR GLOBAL** (desde el 05/09/2026) — `radar.py` trae ~230 temas del día del mundo real en 3 s:
   Google Trends RSS, Google News RSS, Wikipedia pageviews y X/trends24 de CL, MX, ES, AR y US, cada
   uno con puntaje de ángulo jurídico y peso por país (Chile ×3). Con `--video` busca en YouTube
   Shorts el viral que ya funcionó con ese tema. **La regla madre: video del día = TEMA del radar ×
   ESTRUCTURA radiografiada.** Detalle, límites y puertas cerradas: `RADAR-GLOBAL.md`.
1. **DESCUBRIR** — dónde buscar virales que sirvan:
   - YouTube Shorts por búsqueda (`yt-dlp "ytsearch20:<tema> abogado shorts"`) → devuelve vistas y duración sin cuenta ni clave. Se filtra ≤ 90 s y se ordena por vistas/día desde la subida. Temas rotando: finiquito, despido, pensión de alimentos, detención, arriendo, licencia médica, deudas, herencias, tránsito, "abogado responde", "cosas que un abogado nunca haría".
   - TikTok: yt-dlp NO lista hashtags (extractor roto) pero SÍ baja videos y perfiles (`--impersonate chrome`). Se mantiene una lista de cuentas semilla en `biblioteca.json` (creadores legales de Chile/LatAm y cuentas "clipper" de ensayos) y se revisan sus últimos 10 videos con `-j` para leer view_count y like_count.
   - Lo que mande Cristopher (como el viral-01 y el viral-02) entra directo y con prioridad.
   - El radar manda el tema; estas fuentes mandan la estructura. Nunca al revés.
   - Fuera de nicho a propósito: 1 de cada 3 virales analizados debe ser de OTRO rubro (tech, finanzas, salud) porque de ahí salen las estructuras nuevas; el nicho legal solo confirma temas.
2. **RADIOGRAFIAR** — `viral/analizar.py <url> salida.json` en el sandbox: duración, cortes por segundo, palabras/s, pausas, loudness, gancho hablado de los 3 primeros segundos, bloques y transcripción completa. Sin opinión: números. Si el original no está en línea (como el viral-02), se mide el archivo con ffmpeg (cuadros, cortes, envolvente y tono del audio).
3. **EXTRAER LA PLANTILLA** — de la radiografía se escribe una ficha de 8 líneas: tipo de gancho (anécdota / dato / pregunta / confesión / conflicto), promesa, bloques con tiempos, dónde y cómo entra el anuncio o CTA, ritmo (cortes y palabras/s), tono, cierre (CTA / cliffhanger / remate), y **por qué funcionó** (una hipótesis). La ficha va a `biblioteca.json` y, si es una estructura nueva, a `videolab/formatos.json` como formato F-nuevo.
4. **ADAPTAR** — se escribe el guion del estudio con esa plantilla: misma estructura, mismo ritmo, tema jurídico propio, San Bernardo (en ensayos; en los quiz la comuna va en la descripción), anécdota marcada DRAMATIZACIÓN, el estudio como argumento (no como pausa), CTA al final del bloque, cierre en serie si el original lo tenía. 10 ganchos, se elige uno. Regla dura: cero frases del original; cero personas reales; nada contra jueces, fiscales o colegas; nada de resultados prometidos. Si el tema viene del radar y es de actualidad, entra como CONTEXTO para explicar un derecho: sin opinar de causas en curso ni nombrar a los involucrados.
5. **PRODUCIR** — pipeline v2: `voz.py` (Kokoro) → `karaoke.py` → `ensayo.py` (planos cortos, placas) o `motor.py` (F01) según la plantilla; para F12, `quiz_voces.py` → `quiz.py`. Fotos: banco + Pollinations (una a la vez). US$0.
6. **PUBLICAR** — Metricool, franja 21:30 (la "séptima" del día, reservada a este módulo: D-13). Descripción con "Parte n" si es serie.
7. **MEDIR Y APRENDER** — a las 72 h se compara con la mediana del canal (vistas, % completo, comentarios). La ficha de `biblioteca.json` recibe el resultado; si supera 2× la mediana, la plantilla pasa a la rotación de la Fábrica; si queda bajo la mediana dos veces, se retira. Cada aprendizaje vuelve a MASTER_STATE.

## Ética y legal (no negociable)
- Se estudia la ESTRUCTURA, no se reproduce el contenido: nada de clips, música ni frases del original. Guion 100% propio.
- Las anécdotas son ilustrativas y se marcan DRAMATIZACIÓN; nunca clientes reales.
- Nada de "patrocinado oculto": el estudio se presenta como lo que es (el estudio), aunque entre como argumento.
- Nada que denigre a jueces, fiscales o colegas; nada de resultados prometidos ni testimonios inventados.

## F12 — Quiz legal (desde el 05/09, viral-02)
Cristopher mandó un quiz de derecho estilo "Neriquiz" y pidió copiar el estilo y meterlo a producción. Estructura v2 (su criterio del 05/09): SIN intro, la pregunta 1 es el gancho desde el segundo 0; 7 preguntas × ~13 s (tarjeta + voz → opciones A/B/C → barra de 3 s con tic-tac → verde + ding + voz con la respuesta y su consecuencia); cierre que pide el puntaje en comentarios; sin comuna ni dirección en pantalla (van en la descripción); preguntas de la vida diaria, no técnicas. Render `videolab/quiz.py`, voces `videolab/quiz_voces.py`, modelo vigente `videolab/piloto-quiz-02.json`, análisis `videolab/ANALISIS-viral-02.md`. Regla dura: cada pregunta lleva `fuente` (artículo) y se verifica antes de renderizar (si admite dos lecturas, se cambia); las preguntas usadas se guardan en `viral/quizzes/<fecha>.json` para no repetir. Rotación: día por medio quiz / ensayo hasta tener datos a 72 h; el quiz va a las 21:30 o a las 20:00 si hay una parte de serie ese día.

## Tarea secundaria: TENDENCIA DEL DÍA (desde el 06/09, pedida por Cristopher el 05/09)
"Qué video está en tendencia hoy, lo descargo, lo analizo, lo replico y lo publico de inmediato." Tarea diaria a las 10:00 Chile (`trig_012g4GgzsCQusrCuQPD439w3`): corre el RADAR GLOBAL (`radar.py --video`), elige el tema del día con mejor ángulo jurídico que tenga un viral real detrás, lo radiografía con analizar.py, replica la ESTRUCTURA con contenido propio (quiz.py / ensayo.py / motor.py) y lo programa en Metricool en la primera franja libre ≥ 20 min después de terminar (misma mañana). Complementa con cuentas semilla de TikTok y con los sonidos del día (Higgsfield, connector f23f2205-…, CL/1DAY). Mide con Metricool (posts: views, fullVideoWatchedRate, forYou, sound, hashtag) los de días anteriores y ajusta la hora con getBestTimeToPostByNetwork los lunes. Registro: biblioteca.json ("tendencias_del_dia", "tendencia-<fecha>"), `viral/radar/<fecha>.json`, `viral/tendencias/`, bitácora, correo de 5 líneas. Vía alterna de publicación: tiktok_publish de Higgsfield (DIRECT_POST con música) si Metricool falla, o los martes y jueves como experimento E-06.

## Archivos
- `viral/radar.py` + `viral/RADAR-GLOBAL.md` — el radar de tendencias del día y su arquitectura.
- `viral/radar/<fecha>.json` — la foto de qué se habló ese día (serie histórica).
- `viral/analizar.py` — radiografía numérica (probado con viral-01).
- `viral/biblioteca.json` — virales analizados: fuente, números, plantilla extraída, adaptación producida, resultado a 72 h.
- `videolab/ensayo.py` — render de formatos de planos cortos.
- `videolab/formatos.json` — F11 y F12 nacieron de aquí; los siguientes también.
- `videolab/quiz.py`, `videolab/quiz_voces.py` — render y voces del F12.
- `viral/quizzes/` — preguntas ya usadas (una por archivo/fecha).
- `viral/tendencias/` — guiones/JSON de las réplicas de la Tendencia del día.

## Tareas programadas
- "Viral Lab" diaria 15:00 Chile (`trig_018CyFgUac4dbAC5gpzic9o5`): descubre 1 viral (o toma el que mandó Cristopher), radiografía, ficha, guion adaptado, producción (ensayo o quiz, día por medio), programación 21:30, bitácora, correo de 5 líneas.
- "Tendencia del día" diaria 10:00 Chile (`trig_012g4GgzsCQusrCuQPD439w3`): radar global → réplica → publicación la misma mañana.
Un video por tarea y por día; el volumen sube solo si los datos lo justifican.
