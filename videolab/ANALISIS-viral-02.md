# ANÁLISIS viral-02 — Quiz legal estilo "Neriquiz" (05/09/2026)

Cristopher lo mandó el 05/09 ("Copiemos este estilo de videos y agreguémoslos a la producción"). Archivo: `Neriquiz_video_no_watermark.mp4`, 1080×1920, 30 fps, **70,0 s**. No encontré la cuenta original en TikTok ni YouTube (perfil @neriquiz vacío; variantes privadas), así que la radiografía se hizo sobre el archivo: cuadros cada 2 s (contact sheets), cortes de escena, envolvente y análisis de tono del audio. Ninguna frase, foto ni sonido del original se reutiliza.

## Qué es
Un **quiz de 7 preguntas de derecho general** (Constitución, presunción de inocencia, hábeas corpus, derecho civil, poder legislativo, indemnización, tratado internacional). Cero narrador, cero cara, cero storytelling. Todo el video es el mismo "juego" repetido 7 veces, **10,0 s exactos por pregunta**.

## Radiografía (medida)
| Métrica | Valor |
|---|---|
| Duración | 70,0 s (7 × 10 s) |
| Cortes de escena (scene>0,3) | **0** — no hay cortes; todo son transiciones de elementos sobre el mismo fondo |
| Loudness | media −23 dB, picos en la lectura de la pregunta |
| Voz | sí: una voz sintética lee la pregunta (f0 80–225 Hz, 0–3,2 s de cada bloque); **no lee la respuesta** |
| Efectos | tic-tac agudo (~5 kHz) mientras corre la barra (3,2–7,7 s); "ding" armónico (131/262 Hz) al revelar (7,8–8,8 s); 0,5 s de silencio; siguiente pregunta |
| Música de fondo | no (RMS 0,01 durante el tic-tac) |

## Estructura de cada bloque de 10 s
1. **0,0–1,0 s** — tarjeta metálica arriba con la pregunta apareciendo con efecto máquina de escribir; a la vez entra la voz leyendo la pregunta (hasta ~3,2 s).
2. **~1,0–2,0 s** — foto de stock en marco blanco inclinado (mazo, balanza, libro "The Law", billetes, apretón de manos); las tres opciones A/B/C aparecen en píldoras blancas con círculo rojo.
3. **3,2–7,7 s** — barra de progreso con rayas amarillas/celestes ("de peligro") que se llena de izquierda a derecha con tic-tac. **4,5 s de tensión**: el espectador responde en su cabeza.
4. **7,8–9,5 s** — la opción correcta se pinta verde + ding. Nadie explica por qué.
5. **9,5–10,0 s** — vacío, y entra la siguiente pregunta sin transición.

Fondo salmón con patrón de garabatos (libros, lupas, bocadillos) fijo todo el video; tipografía negra pesada; layout idéntico en las 7 preguntas.

## Por qué funciona (hipótesis)
- **Participación obligada**: una pregunta con barra de tiempo convierte al espectador en jugador. No se puede "ver" un quiz sin responder; eso es retención por diseño, no por guion.
- **Bucle de 10 s**: cada 10 s hay una micro-recompensa (verde + ding). Si te aburres de una pregunta, la siguiente ya está entrando. Funciona igual que un carrusel.
- **Costo de producción casi cero**: plantilla + 7 preguntas + fotos de stock + TTS. Escala a 1 video/día sin esfuerzo. Es un formato de **volumen**, no de "obra".
- **Comentarios gratis**: "acerté 6/7", "la 3 está mal" → el algoritmo lee interacción. El quiz genera debate aunque las respuestas sean correctas.
- **Sin cara ni voz humana**: encaja perfecto con la regla de Cristopher (nunca aparece).

## Lo que NO copiamos
- Las preguntas de "cultura general jurídica" (¿qué es la Constitución?) no venden nada al que las ve: son de trivia escolar. **Las nuestras son preguntas que cuestan plata** (plazos, montos, derechos que la gente pierde por no saber). Es la misma mecánica con el gancho de la doctrina: 2ª persona + dolor concreto.
- El silencio tras la respuesta. Nosotros **decimos la respuesta con una frase de consecuencia** ("Sesenta días hábiles. Después, el derecho se pierde"): 2 s más por pregunta y ahí va el valor.
- El anonimato total. Nuestro fondo lleva la marca (franja "TRIVIA LEGAL · SAN BERNARDO" + pie con la consulta gratis), y el cierre pide el puntaje en comentarios y ofrece revisar "la que fallaste" en el estudio.
- Fotos de stock genéricas: usamos el banco propio (`motor/banco.json`) por materia.

## Traducción al estudio → formato **F12 "Quiz legal"**
- 1 intro (placa + voz, ~8 s): "7 preguntas que te pueden costar plata".
- 7 preguntas × ~12 s: pregunta en 2ª persona con situación concreta ("Te despiden y no estás de acuerdo…") → opciones → barra 3 s con tic-tac → verde + ding + voz con la respuesta y la consecuencia.
- Cierre (placa + voz, ~9 s): "¿Cuántas acertaste? Comenta tu puntaje. La que fallaste la revisamos gratis…".
- Total 96 s (medido). Render: `videolab/quiz.py` (Pillow → ffmpeg por tubería, efectos sintetizados con numpy, sin música con derechos); voces `videolab/quiz_voces.py` (Kokoro). Costo US$0, ~1 min de render + ~2 min de voces en el sandbox.
- Rotación de materias dentro del mismo quiz (laboral, familia, penal) → la Fábrica/Viral Lab puede sacar 1 quiz día por medio con 7 preguntas nuevas.

## Ética
Todas las respuestas del piloto llevan fuente (artículo de ley) en `piloto-quiz-01.json`; nada de clientes, nada de jueces/fiscales, nada de resultados prometidos. Un quiz con una respuesta equivocada destruye la credibilidad del estudio: **cada pregunta nueva se verifica contra la norma antes de renderizar** (regla dura para la Fábrica y el Viral Lab).

## Piloto
`piloto-quiz-01.json` → `quiz_voces.py` → `quiz.py` → CloudFront `22f76be2-da45-4e24-8fa1-2ec26523c08d.mp4` (96,7 s, 4,5 MB, −16,7 dB) → Metricool 371526566, lunes 07/09 20:00 (el domingo ya tenía 7 piezas; el 21:30 del lunes queda para la parte 3 de F11). Medición a 72 h contra la mediana del canal; el número que importa aquí es **comentarios** (puntajes) y % completado.
