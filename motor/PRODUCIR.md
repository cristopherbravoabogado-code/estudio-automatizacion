# PRODUCIR — cómo se hace una tanda (13/09/2026)

Compañero de `motor/PUBLICAR.md` (cómo sale al aire) y de `motor/RECETA-MOTOR-NUBE.md` (las cinco
reglas duras). Este archivo es el **procedimiento corto** que reemplaza al de pegar el pipeline
entero dentro del comando del sandbox.

## El procedimiento (5 llamadas, no más)

1. **Verificar el derecho ANTES de escribir el guion.** Una llamada `sandbox_exec` con
   `https://www.leychile.cl/Consulta/obtxml?opt=7&idNorma=<id>`, normalizando espacios con
   `re.sub(r'\s+',' ',...)` antes de buscar. ⚠️ **La búsqueda es sensible a mayúsculas**: buscar
   `robidad` encuentra "Falta de probidad", buscar `falta de probidad` no. Y el número de
   artículo no siempre está en `NombreParte`: buscar por una frase del texto es más seguro.
   idNorma medidos: **Código del Trabajo 207436 · Código Penal 1984 · Código Procesal Penal
   176595 · Código Civil 172986 · Ley 20.084 244803 · Ley 19.973 230132 · Ley 21.840 1227843**.
2. **Elegir el metraje real.** `curl -A "Mozilla/5.0" https://mixkit.co/free-stock-video/<cat>/`
   y `grep -o 'assets.mixkit.co/videos/[0-9]*/'`. Bajar siempre el **-720.mp4** (el -1080 da 403
   en muchos). Categorías que respondieron el 13/09: travel, party, smartphone, police, money,
   family, home, paperwork, documents (`nightlife` viene vacía).
   ⚠️ **Mirar QUÉ sale en el clip, no solo que baje**: el clip 18247 de "money" es un billete de
   dólar estadounidense — en una pieza de familia chilena queda fuera de lugar y además mete 11
   cajas de texto en inglés dentro del video. Elegir planos de OBJETOS y sin texto.
3. **Pedir las `upload_url` ANTES de lanzar** (`media_upload` con un `files[]` por pieza).
4. **UNA llamada `sandbox_exec` con `background:true`** que baja `produce.py` y le pasa un
   `job.json`. El formato del job está en el encabezado de `motor/produce.py`.
   produce.py hace todo: deps del repo → pip → gancho → voz Kokoro → karaoke → motor →
   **los cuatro controles** (audio `aac,48000,2`; duración 22-34 s; pantalla chica; código HTTP
   de la subida) → PUT a la upload_url. Deja `resultado.json` con una línea por pieza.
5. **`media_confirm`** con los media_id de las que subieron 200, y una **tarea de un solo disparo
   por pieza** (`motor/PUBLICAR.md`).

**Tamaño de la tanda: 3 piezas por llamada.** El comando del sandbox se topa en 16.000 caracteres
y cada `upload_url` presignada mide ~2.400: con tres piezas el job ocupa ~10.000 y cabe cómodo.
Con cinco no cabe el job. Eso, y no otra cosa, fija el tamaño del lote.

## Sondeo del trabajo en background
`sleep 45` como máximo por llamada. **Medido de nuevo el 13/09: una llamada de `sleep 110` murió
con 502 de Cloudflare.** Esta vez el contenedor sobrevivió y el trabajo siguió corriendo, pero es
suerte, no diseño: la receta ya avisaba que el 502 se puede llevar el contenedor entero.

## Cómo se lee el control de pantalla chica (la trampa que costó dos re-renders)
`pantalla_chica.py` cuenta cajas fuera de la zona segura **sin distinguir el texto propio del
contenido del clip del gancho**. Su "NO PASA" no significa que la pieza esté mala:

- El criterio del MOTOR es **0 cajas de TEXTO PROPIO fuera**. El recall se estabiliza en 0,77-0,84
  porque el pie legal es chico por diseño: se informa y **no bloquea**.
- Cuando reporta cajas fuera, **hay que volcar las detecciones con su texto** antes de tocar nada:

```python
from rapidocr_onnxruntime import RapidOCR
ocr = RapidOCR()
# ffmpeg -v error -i <pieza>.mp4 -vf fps=1 _d/%03d.png
for p in sorted(glob.glob("_d/*.png")):
    r, _ = ocr(p)
    for box, txt, conf in (r or []):
        xs = [q[0] for q in box]; ys = [q[1] for q in box]
        if min(xs) < 95 or max(xs) > 930 or min(ys) < 200 or max(ys) > 1586:
            print(round(min(xs)), round(max(xs)), round(min(ys)), round(max(ys)), txt)
```

Medido el 13/09 con eso: en la 941 las 6 cajas eran **"Artículo 160 del Código del Trabajo"**,
texto propio → defecto real, arreglado en motor v5.2. En la 944 la única caja era **"NEWS"** del
furgón del clip → no es defecto, la pieza pasa. En la 945, 11 de 12 eran el billete del gancho.
**Contar cajas lleva a re-renderizar piezas sanas y a dar por buenas piezas malas.**

## Lo que se aprendió el 13/09 y ya está en el código
- `motor.py` **v5.2**: el inset de la zona segura era asimétrico (SEG_X0 a 35 px del borde,
  SEG_X1 a 5 px). Ahora 45 px a los dos lados: **SEG_X0=140, SEG_X1=885**. Un título de ancho
  completo pasó de 6 cajas fuera a 0.
- `karaoke.py` **v3.1**: mismos márgenes de dibujo (MarginL 130 / MarginR 185, ANCHO_MAX 730) e
  imprime `borde_der=` para poder verificarlo sin renderizar.
- Regla general que se desprende de las dos: **el inset tiene que ser ≥ el sobresalto de la caja
  de OCR de la fuente MÁS GRANDE de la pieza, y aplicarse a los dos lados.** Medido: hasta 37 px
  con la fuente de 96 px del título, de ahí los 45.
- Y la de siempre, que volvió a cobrarse dos re-renders: **una corrección de encuadre no está
  hecha hasta que se mide.** El v5 "metió el margen 35 px" y dejó el otro lado en el borde.
