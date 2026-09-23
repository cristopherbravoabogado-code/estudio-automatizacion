# REGLA DURA 7 — MOVIMIENTO REAL SOBRE FOTO FIJA (23/09/2026, M6 corrida 3)

**Ninguna foto quieta sale con `zoompan`. Sale con `videolab/movimiento.py`, y con la métrica de movimiento
medida y sobre 4,0.**

## El problema que existía y estaba medido
El supervídeo A (11 sueldos, 14/09) quedó en **3,99 de movimiento**, bajo la banda de los virales de referencia
(**4,6–9,9**), y la causa anotada fue "clips de oficina quietos". El plano que nace de una foto —la foto de prensa
del formato noticia, el banco de imágenes, la lámina— se movía con Ken Burns (`zoompan`), y Ken Burns **no alcanza
la banda ni de lejos**. La única alternativa conocida hasta hoy era pagar animación: **ltx-v2-fast de ElevenLabs,
US$0,26 por plano**.

## La prueba (23/09/2026)
5 fotos reales (3 fotogramas del F13 v3 publicado + 2 fotos fotorrealistas), clips de 6 s a 1080x1920 y 30 fps,
render real en el sandbox. Métrica de movimiento del VIDEO LAB: diferencia media por píxel entre cuadros a 1/15 s,
en gris a 96 px de ancho.

| técnica | movimiento (5 fotos) | media | costo | tiempo |
|---|---|---|---|---|
| **parallax 2.5D (MiDaS-small, órbita ×3)** | 4,21 · 5,09 · 5,67 · 4,75 · 4,53 | **4,85** | **US$0** | 0,3 s profundidad + 4,8 s render |
| Ken Burns `zoompan` 1,00→1,12 (lo de hoy) | 0,69 · 1,11 · 1,87 · 0,93 · 1,12 | 1,14 | US$0 | 1,7–2,2 s |
| ltx-v2-fast (ElevenLabs), referencia pagada | 4,67 (medido el 12/09) | 4,67 | US$0,26/plano | minutos de cola |
| zoom rápido sin profundidad 1,00→1,75 | 5,41 · 2,96 · 2,92 (n=3) | 3,76 | US$0 | 4,3 s |
| parallax suave (amp 0,045, 1 órbita) | 0,51 · 0,80 · 1,33 · 0,82 · 0,75 | 0,86 | US$0 | 5,1 s |

**4,25× el movimiento de Ken Burns, al mismo costo (cero), y por encima de la animación que pagábamos a US$0,26.**

Nitidez (varianza del laplaciano, media por clip): parallax **28 / 8 / 14** contra Ken Burns **30 / 9 / 14**.
El warp por profundidad **no borronea**: la diferencia está dentro del ruido.

## Lo que aprendimos y no hay que volver a probar
- ⛔ **La profundidad sola no da movimiento.** Con amplitud suave el parallax da **0,86**, es decir **peor que el
  Ken Burns que reemplaza**. Lo que mueve la métrica es la **velocidad del recorrido de cámara** (3 órbitas en el
  clip); la profundidad es lo que hace que esa velocidad parezca una cámara y no un zoom, y lo que permite llegar
  a la banda con un zoom de apenas 1,20→1,02 en vez de deformar el encuadre.
- ⛔ **Zoom rápido puro descartado**: para acercarse a la banda hay que irse a 1,75× (se come el 43 % del encuadre,
  choca con la zona segura de la regla 4) y aun así 2 de 3 fotos quedan bajo 4,6.
- ⛔ **`depthflow` (el paquete de PyPI) no instala en el sandbox** — probado el 23/09, `ModuleNotFoundError` tras
  `pip install`. No insistir: MiDaS-small en ONNX resuelve lo mismo con `onnxruntime` y 66 MB.
- 🔑 `cv2.remap` **rechaza mapas float64**: si un escalar de numpy se cuela, el mapa cambia de tipo, el render
  muere y ffmpeg deja un mp4 de 262 bytes que parece válido. Todo el camino va en float32 (así está en el script).

## Cómo se usa
```bash
pip install onnxruntime opencv-python-headless           # ~20 s, una vez por sandbox
python3 videolab/movimiento.py clip foto.jpg plano_03.mp4 6
python3 videolab/movimiento.py control plano_03.mp4      # MOVIMIENTO_OK o BLOQUEA
```
El control sale con código 1 si el clip queda bajo **4,0**. Va sobre cada plano nacido de foto, antes de armar.

## Lo que ahorra
Una pieza de 9 planos animados con ltx-v2-fast costaba **US$2,34**. Con esto cuesta **US$0** y suma ~45 s de CPU.
