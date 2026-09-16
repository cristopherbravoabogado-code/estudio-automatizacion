# Radiografía viral-03 — @xabatzz, "279 expertos gratis (The Agency en GitHub)" — 16/09/2026

Referente que mandó Cristopher ("nos puede servir para mejorar"). 70,9 s · 576x1024 · 30 fps.

## Medido (OpenCV sobre el archivo)
- **20 cortes, uno cada 3,55 s** (5,0 · 10,9 · 13,4 · 15,6 · 18,0 · 20,1 · 23,0 · 26,8 · 29,0 · 30,9 · 34,2 · 36,3 · 39,2 · 41,3 · 47,2 · 51,2 · 56,1 · 58,5 · 60,9 · 66,9). El gancho dura **5 s** completos antes del primer corte.
- **Movimiento medio 2,41** (p10 0,01 · p90 4,09): es un video QUIETO. Retiene por el corte y el subtítulo, no por el movimiento. La banda 4,6-9,9 del fruit drama NO aplica a este formato.
- Audio: voz sola, sin música perceptible, 0 silencios de más de 0,5 s en 71 s (narración continua).

## Estructura (dos planos que se alternan)
1. **PERSONA** (talking head, gorra, fondo cortina, plano medio-corto): 12 de los 21 planos. Gesticula, mira a cámara. Subtítulo de **UNA palabra**, blanco con borde, centrado en el pecho.
2. **PIZARRA BLANCA** (motion graphic limpio, fondo blanco/crema con degradado suave): 9 planos. Composición fija:
   - etiqueta gris chica arriba ("GITHUB · REPOSITORIO REAL", "PASO 03", "THE AGENCY · GUÍA")
   - título en negro extra-bold con **una frase o palabra en rojo** ("The Agency **Está en GitHub.**", "Una persona. **Un equipo de apoyo.**")
   - una tarjeta blanca con sombra que imita una interfaz (lista con ✓, carpeta, cuadro de texto, botón) — el "dato" en forma de objeto
   - **línea de fuente en gris chico al pie** ("github.com/... · Captura del repositorio público · septiembre 2026", "Recreación del flujo · respuesta de ejemplo") ← credibilidad barata
   - subtítulo de una palabra en **rojo** cuando el fondo es blanco
3. Variante: **pantalla partida** (pizarra arriba, persona abajo) en el tramo final.
4. Gancho (0-5 s): persona + tarjeta oscura de 3 líneas con la palabra clave en rojo ("Todos los empleados de una empresa **GRATIS**, a tu alcance") y el número repetido ("279").
5. Cierre: pizarra "Tienes el link en la descripción" → tarjeta negra con el @.

## Qué nos sirve (y qué no)
- ✅ **Pizarra blanca en vez de lámina oscura**: nuestras láminas son fondo azul-negro con texto crema; la de él es blanco con negro+rojo. Más legible en pantalla chica y se ve "de verdad", no de plantilla. Implementar como formato **F14 PIZARRA** en `motor.py` (paleta, etiqueta de paso, tarjeta con sombra, línea de fuente).
- ✅ **Línea de fuente al pie de cada lámina**: para nosotros es la jugada natural — "Código del Trabajo, art. 163 · texto vigente LeyChile 2026". Es lo que ningún otro abogado de TikTok pone.
- ✅ **Dos planos por punto**: hoy hacemos gancho + 3 láminas + cierre (5 planos en 30 s = uno cada 6 s). Él corta cada 3,5 s. Partir cada punto en título → tarjeta, e intercalar el clip del gancho como plano de respiro. Meta: 9-10 planos en 30 s.
- ✅ **Subtítulo de una palabra, en rojo sobre blanco**: ya hacemos karaoke por palabra (karaoke.py); falta el color por fondo.
- ✅ **Etiqueta de paso** ("PASO 01 · LA CARTA"): ordena y da sensación de guía, no de charla.
- ⚠️ **La cara real**: es el 57% del video y es lo que más pesa. No se puede sintetizar sin costo (HeyGen en 0, ElevenLabs en 0). Vía real: que Cristopher se grabe leyendo el guion con el teléfono, en vertical, sentado, sin editar; el motor lo corta por tramos y lo intercala con las pizarras. Sin su cara, F14 funciona igual con el clip real de gancho como plano "persona".
- ❌ No copiar: la música (no tiene), el tema, el ritmo de gestos.

## Siguiente paso técnico
`motor.py` v6 con `"formato": "pizarra"`: fondo #F7F5F2 → blanco, título Montserrat ExtraBold negro con `**...**` en rojo #E5261F, tarjeta blanca con sombra para el detalle, etiqueta de paso arriba, línea de fuente gris al pie (dentro de la zona segura), karaoke rojo. Probar con una pieza real y medir pantalla chica antes de publicar.
