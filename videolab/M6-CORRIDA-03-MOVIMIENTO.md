# M6 · corrida 3 (23/09/2026) — MOVIMIENTO SOBRE FOTO FIJA

**Pregunta de la rotación:** efectos de zoom y movimiento sobre foto fija (nunca probada; voz, subtítulos,
pantalla chica y música ya lo estaban).
**Herramienta nueva probada:** **MiDaS-small en ONNX** (MIT, CPU, 66 MB, `onnxruntime`) como estimador de
profundidad para un parallax 2.5D hecho con `cv2.remap`, contra el `zoompan` (Ken Burns) del motor.

## Por qué esta pregunta
El 14/09 el supervídeo A quedó en **3,99** de movimiento con la banda de los virales en **4,6–9,9**, y la causa
anotada fue "clips de oficina quietos". El único remedio conocido era pagar animación (**ltx-v2-fast de
ElevenLabs, US$0,26 el plano**, medido en 4,67 el 12/09). La pregunta concreta: **¿se alcanza esa banda gratis,
sin GPU, partiendo de una foto?**

## Qué se investigó
- DepthFlow (BrokenSource), el estándar open source de imagen→video parallax, y su fork en ComfyUI: pide OpenGL
  real. **`pip install depthflow` en el sandbox termina sin módulo** (2 intentos) → puerta cerrada, anotada.
- Parallax-maker (provos) y los servicios de pago tipo ImmersityAI: mismo principio (mapa de profundidad +
  desplazamiento diferencial), pero uno necesita entorno gráfico y el otro cobra.
- Camino elegido, sin GPU ni cuentas: **MiDaS-small ONNX + `cv2.remap` por cuadro**, escrito en 120 líneas.

## Método
5 fotos reales (3 fotogramas del F13 v3 ya publicado + 2 fotos fotorrealistas), clips de **6 s, 1080x1920, 30 fps**,
render real en el sandbox de Higgsfield (8 núcleos, sin GPU). Métrica del VIDEO LAB: diferencia media por píxel
entre cuadros a **1/15 s**, en gris a 96 px de ancho. Control de daño: varianza del laplaciano (nitidez).

## El número que decidió

| técnica | movimiento por foto | media | costo | tiempo/clip |
|---|---|---|---|---|
| **parallax 2.5D (amp 0,14 · 3 órbitas · zoom 1,20→1,02)** | 4,21 · 5,09 · 5,67 · 4,75 · 4,53 | **4,85** | **US$0** | 5,1 s |
| Ken Burns `zoompan` 1,00→1,12 *(lo que hay hoy)* | 0,69 · 1,11 · 1,87 · 0,93 · 1,12 | **1,14** | US$0 | 1,9 s |
| ltx-v2-fast *(animación de pago, 12/09)* | 4,67 | 4,67 | US$0,26/plano | minutos |
| zoom rápido sin profundidad 1,00→1,75 | 5,41 · 2,96 · 2,92 | 3,76 | US$0 | 4,3 s |
| parallax suave (amp 0,045 · 1 órbita) | 0,51 · 0,80 · 1,33 · 0,82 · 0,75 | 0,86 | US$0 | 5,1 s |

**4,25× el movimiento actual, gratis, y por encima de lo que pagábamos.**
Nitidez sin pérdida: **28 / 8 / 14** contra **30 / 9 / 14** del Ken Burns (varianza del laplaciano por clip).

Comparación lado a lado renderizada (izquierda Ken Burns, derecha parallax):
https://d2ol7oe51mr4n9.cloudfront.net/user_3IkWukwrqRk5HTPle6Rx8WbYgS3/a3ddbb10-c437-48cc-8b46-17e15b898d0c.mp4

## Descartes con número (para no repetirlos)
- ⛔ **Parallax suave: 0,86** — peor que el Ken Burns que venía a reemplazar. **La profundidad no da movimiento;
  lo da la velocidad del recorrido de cámara.** La profundidad es lo que permite esa velocidad sin deformar el
  encuadre.
- ⛔ **Zoom rápido puro: 3,76**, con 2 de 3 fotos bajo la banda, y a 1,75× se come el 43 % del encuadre, que
  choca con la zona segura de la regla dura 4.
- ⛔ **`depthflow` de PyPI**: no instala en el sandbox. No reintentar.

## Lecciones técnicas
- `cv2.remap` **rechaza mapas float64**: basta que un escalar de numpy se cuele para que el render muera y ffmpeg
  deje un **mp4 de 262 bytes** que parece un archivo válido. Todo el camino va en float32.
- El sandbox se borra ~10 s después de una llamada **sin trabajo en segundo plano**: se perdió una corrida
  entera. Todo va con `nohup … &` y se sondea con `sleep 40-55` (una llamada de más de ~60 s devuelve 502).
- Pollinations devolvió una imagen corrupta de 1 KB en 1 de 3 intentos: siempre verificar con `-s` el tamaño
  antes de usarla.
- La lectura de `raw.githubusercontent` sigue cacheada ~5 min: pedir por SHA del commit.

## Implementado
- `videolab/movimiento.py` — `clip` (render) y `control` (bloquea bajo 4,0).
- `motor/REGLA-7-MOVIMIENTO.md` — la regla con su tabla.
- `motor/RECETA-MOTOR-NUBE.md` **v12** — ahora son SIETE reglas duras; regla 7 + línea en "Lo que NO hacer".
- `videolab/ranking.json` — parallax 2.5D 🟢; Ken Burns sobre foto, parallax suave, zoom rápido y depthflow 🔴.

## Pendiente (un paso, no bloquea)
Enchufar `movimiento.py` a `produce.py` y a `build_sv.py` para que cada plano nacido de foto pase por ahí sin
que nadie lo pida, igual que se hizo con `musica.py`.
