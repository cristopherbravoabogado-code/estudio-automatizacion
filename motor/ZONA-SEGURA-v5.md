# ANEXO A LA REGLA DURA 4 — la zona segura MEDIDA en el motor (12/09/2026)

Este archivo es parte de `motor/RECETA-MOTOR-NUBE.md`. **Leerlo junto con la regla dura 4.**
Lo que sigue no es una opinión de diseño: son números de `videolab/pantalla_chica.py` (rapidocr) sobre
piezas reales del motor.

## El defecto: la regla estaba escrita y el motor no la cumplía

El 11/09 se midió el formato **ENSAYO** (`videolab/ensayo.py`) y se corrigió. El 12/09 por la mañana se
"corrigió" `motor/motor.py` a v4 **sin medirlo**, de memoria. La primera medición real del motor, la misma
mañana, dio:

| Medición | Cajas fuera de la zona segura | Recall pantalla chica |
|---|---|---|
| motor v4 (el que se creía corregido) | **236** | 0,71 |
| v5 paso 1 (pie + cabecera + SEG_X0=112) | 127 | 0,76 |
| v5 paso 2 (anchos de bloque) | 68 | 0,77 |
| v5 paso 3 (lamina_cierre + SEG_X0=130) | **26** | 0,77 |

Las 26 que quedan son los gráficos del clip de noticia del gancho (cintillo y ticker del medio),
no texto del motor.

## Lo que estaba mal, uno por uno

1. **`pie()`**: la línea del WhatsApp terminaba en y=1593 y el descargo en y=1650. Los dos **por debajo de
   1586**, o sea tapados por el copy de TikTok. El v4 los había bajado de 1620/1665 a 1490/1535 y creyó
   que con eso bastaba: no midió el ALTO de la caja del texto, que suma ~58 px con fuente de 30 px.
2. **`lamina_cierre()` tiene su PROPIO pie** y el v4 no lo tocó. Ahí el descargo iba en y=1618-1650, y la
   marca y el WhatsApp se pasaban del borde derecho (llegaban a x=1041 y x=975 contra el límite 930).
   🔑 Lección: **antes de dar por corregida una regla de encuadre, buscar TODAS las funciones que dibujan
   el mismo bloque.** El CTA se dibujaba en dos lugares distintos.
3. **`cabecera()`**: el texto se dibujaba en y=205, pero la CAJA del texto empieza ~23 px más arriba
   (y=182), bajo el buscador de TikTok. Corregido a y=245.
4. **Anchos de bloque**: `bloque()` recibía `W-190` (890 px) y el gancho `W-260`. Desde x=95 eso llega a
   x=985-1002, fuera del borde 930. Ahora todos reciben `SEG_X1 - SEG_X0`.
5. **`SEG_X0` pasa de 95 a 130.** Dibujar justo en el borde 95 dejaba **la mitad de las cajas medidas en
   x=78**: la caja que devuelve el OCR se extiende ~17 px más allá del glifo. `SEG_X0`/`SEG_X1` son el
   margen de **DIBUJO** (130 y 925), metidos 35 px dentro del borde real de la zona segura (95 y 930).

## Reglas que se desprenden (aplican a cualquier motor nuevo)

- **Una regla de encuadre no está implementada hasta que `pantalla_chica.py` la mide.** "Lo corregí" sin
  número es exactamente cómo el v4 pasó por corregido llevando el WhatsApp tapado.
- **Dibujar con 35 px de holgura**, nunca en el borde exacto: el OCR (y el recorte de algunos teléfonos)
  se come esos píxeles.
- **Un mismo bloque dibujado en dos funciones se corrige en las dos**, o la mitad de las piezas sale mal.
- **El recall de pantalla chica del motor se estabiliza en 0,77**, bajo el umbral 0,80 calibrado con el
  formato ENSAYO. La causa es que el pie legal (marca, teléfono, descargo) es texto chico por diseño.
  El criterio que sí decide en el motor es **0 cajas de texto PROPIO fuera de la zona segura**; el recall
  se informa pero no bloquea. Subirlo por sobre 0,80 exige rediseñar el pie, no mover texto.

## Consecuencia para las métricas

Si el bloque de contacto venía tapado en todas las piezas anteriores del motor, **el embudo al WhatsApp
estaba roto desde antes**. Cualquier conclusión previa del tipo "el contenido no convierte" está sucia:
el teléfono existía en el archivo y el espectador no lo veía nunca.

## Formato de reacción: el clip ajeno también mete texto fuera de la zona

En las piezas de reacción el gancho es un clip de prensa con su cintillo y su ticker, que caen en los
bordes. `pantalla_chica.py` los cuenta como cajas fuera de zona y no hay nada que mover. Al medir una
pieza de reacción, **medir aparte el tramo de láminas** (`ffmpeg -ss <fin del gancho> -c copy`) y exigir
0 cajas fuera **ahí**; lo del gancho es del medio, no del motor.

## Cómo se preparó el clip de prensa (v5, formato reacción)

El recorte `crop=1080:1920` de la receta destruye un clip de noticia 1280x720: se come el cintillo y los
rótulos del medio, que son justo lo que da credibilidad. Para clips de prensa se usa **fondo desenfocado
+ clip centrado**, que conserva el cuadro completo:

```
ffmpeg -y -ss <inicio> -t 9 -i crudo.mp4 -filter_complex \
 "[0:v]split=2[bg][fg];\
  [bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:2,eq=brightness=-0.14[b];\
  [fg]scale=1080:-2:flags=lanczos,unsharp=5:5:0.9:5:5:0.0[f];\
  [b][f]overlay=(W-w)/2:(H-h)/2,fps=30[v];\
  [0:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[a]" \
 -map "[v]" -map "[a]" -t 9 -c:v libx264 -preset veryfast -crf 19 -c:a aac -ar 48000 -ac 2 -b:a 128k hook.mp4
```

El audio original del clip lo mezcla el motor solo, a `volume=0.35` durante el gancho y con `afade` de
salida. El tramo del gancho dura lo que dure el **tramo 1 de la voz**: para que se escuche el momento
fuerte del clip, ese tramo 1 tiene que ser de 6 s o más y el corte del clip debe dejar la frase de impacto
dentro de los primeros 2 s.

## Trampa de operación (costó dos veces el mismo trabajo el 12/09)

El sandbox de Higgsfield **se reinicia solo** y se lleva `voz.py`, `karaoke.py` y los paquetes de pip,
aunque una llamada anterior con `sleep 800` pareciera tener el lease vivo. Todo guion de producción debe
**empezar** re-bajando los .py del repo y corriendo `pip install`, no darlos por presentes.
