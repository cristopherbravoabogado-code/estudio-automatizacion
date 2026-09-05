# VIRAL LAB — De videos que ya funcionaron a videos del estudio (05/09/2026)

Cristopher lo pidió el 05/09/2026 después del piloto F11: "armar una estructura donde creamos y publiquemos videos a base de videos virales que ya funcionaron para otras personas". Es un módulo del VIDEO LAB; nada se copia, se **extrae la estructura** (gancho, ritmo, orden de bloques, dónde entra el anuncio, cómo cierra) y se vuelve a escribir con contenido jurídico propio, ilustrativo y ético.

## El ciclo (una vuelta por día)
1. **DESCUBRIR** — dónde buscar virales que sirvan:
   - YouTube Shorts por búsqueda (`yt-dlp "ytsearch20:<tema> abogado shorts"`) → devuelve vistas y duración sin cuenta ni clave. Se filtra ≤ 90 s y se ordena por vistas/día desde la subida. Temas rotando: finiquito, despido, pensión de alimentos, detención, arriendo, licencia médica, deudas, herencias, tránsito, "abogado responde", "cosas que un abogado nunca haría".
   - TikTok: yt-dlp NO lista hashtags (extractor roto) pero SÍ baja videos y perfiles (`--impersonate chrome`). Se mantiene una lista de cuentas semilla en `biblioteca.json` (creadores legales de Chile/LatAm y cuentas "clipper" de ensayos) y se revisan sus últimos 10 videos con `-j` para leer view_count y like_count.
   - Lo que mande Cristopher (como el viral-01 y el viral-02) entra directo y con prioridad.
   - Fuera de nicho a propósito: 1 de cada 3 virales analizados debe ser de OTRO rubro (tech, finanzas, salud) porque de ahí salen las estructuras nuevas; el nicho legal solo confirma temas.
2. **RADIOGRAFIAR** — `viral/analizar.py <url> salida.json` en el sandbox: duración, cortes por segundo, palabras/s, pausas, loudness, gancho hablado de los 3 primeros segundos, bloques y transcripción completa. Sin opinión: números. Si el original no está en línea (como el viral-02), se mide el archivo con ffmpeg (cuadros, cortes, envolvente y tono del audio).
3. **EXTRAER LA PLANTILLA** — de la radiografía se escribe una ficha de 8 líneas: tipo de gancho (anécdota / dato / pregunta / confesión / conflicto), promesa, bloques con tiempos, dónde y cómo entra el anuncio o CTA, ritmo (cortes y palabras/s), tono, cierre (CTA / cliffhanger / remate), y **por qué funcionó** (una hipótesis). La ficha va a `biblioteca.json` y, si es una estructura nueva, a `videolab/formatos.json` como formato F-nuevo.
4. **ADAPTAR** — se escribe el guion del estudio con esa plantilla: misma estructura, mismo ritmo, tema jurídico propio, San Bernardo, anécdota marcada DRAMATIZACIÓN, el estudio como argumento (no como pausa), CTA al final del bloque, cierre en serie si el original lo tenía. 10 ganchos, se elige uno. Regla dura: cero frases del original; cero personas reales; nada contra jueces, fiscales o colegas; nada de resultados prometidos.
5. **PRODUCIR** — pipeline v2: `voz.py` (Kokoro) → `karaoke.py` → `ensayo.py` (planos cortos, placas) o `motor.py` (F01) según la plantilla; para F12, `quiz_voces.py` → `quiz.py`. Fotos: banco + Pollinations (una a la vez). US$0.
6. **PUBLICAR** — Metricool, franja 21:30 (la "séptima" del día, reservada a este módulo: D-13). Descripción con "Parte n" si es serie.
7. **MEDIR Y APRENDER** — a las 72 h se compara con la mediana del canal (vistas, % completo, comentarios). La ficha de `biblioteca.json` recibe el resultado; si supera 2× la mediana, la plantilla pasa a la rotación de la Fábrica; si queda bajo la mediana dos veces, se retira. Cada aprendizaje vuelve a MASTER_STATE.

## Ética y legal (no negociable)
- Se estudia la ESTRUCTURA, no se reproduce el contenido: nada de clips, música ni frases del original. Guion 100% propio.
- Las anécdotas son ilustrativas y se marcan DRAMATIZACIÓN; nunca clientes reales.
- Nada de "patrocinado oculto": el estudio se presenta como lo que es (el estudio), aunque entre como argumento.
- Nada que denigre a jueces, fiscales o colegas; nada de resultados prometidos ni testimonios inventados.

## F12 — Quiz legal (desde el 05/09, viral-02)
Cristopher mandó un quiz de derecho estilo "Neriquiz" y pidió copiar el estilo y meterlo a producción. Estructura: 7 preguntas × ~12 s (tarjeta + voz → opciones A/B/C → barra de 3 s con tic-tac → verde + ding + voz con la respuesta y su consecuencia), intro y cierre que pide el puntaje en comentarios. Render `videolab/quiz.py`, voces `videolab/quiz_voces.py`, ejemplo `videolab/piloto-quiz-01.json`, análisis `videolab/ANALISIS-viral-02.md`. Regla dura: cada pregunta lleva `fuente` (artículo) y se verifica antes de renderizar; las preguntas usadas se guardan en `viral/quizzes/<fecha>.json` para no repetir. Rotación: día por medio quiz / ensayo hasta tener datos a 72 h; el quiz va a las 21:30 o a las 20:00 si hay una parte de serie ese día.

## Archivos
- `viral/analizar.py` — radiografía numérica (probado con viral-01).
- `viral/biblioteca.json` — virales analizados: fuente, números, plantilla extraída, adaptación producida, resultado a 72 h.
- `videolab/ensayo.py` — render de formatos de planos cortos.
- `videolab/formatos.json` — F11 y F12 nacieron de aquí; los siguientes también.
- `videolab/quiz.py`, `videolab/quiz_voces.py` — render y voces del F12.
- `viral/quizzes/` — preguntas ya usadas (una por archivo/fecha).

## Tarea programada
"Viral Lab" diaria 15:00 Chile (`trig_018CyFgUac4dbAC5gpzic9o5`): descubre 1 viral (o toma el que mandó Cristopher), radiografía, ficha, guion adaptado, producción (ensayo o quiz, día por medio), programación 21:30, bitácora, correo de 5 líneas. Un video por día; el volumen sube solo si los datos lo justifican.
