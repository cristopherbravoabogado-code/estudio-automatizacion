# RECETA — Formato animado 3D "Abogado Vegetal" (v1)

Prototipo: `PROTOTIPO_ABOGADO_VEGETAL.mp4` (48,5 s · 720x1280 · 30 fps · 8,7 MB)
Referencia copiada: video de @habitosanimados1 aportado por Cristopher (75 s, personaje con cabeza de vela).

## 1. Qué se copia del referente

| Elemento | Referente | Nuestra versión |
|---|---|---|
| Estilo | 3D animado tipo largometraje, luz cálida, poca profundidad de campo | idéntico |
| Gancho visual | personaje normal con la cabeza convertida en objeto absurdo (vela) | abogado con **corona de brócoli** en vez de pelo |
| Subtítulos | **una palabra a la vez**, MAYÚSCULAS, amarillo negrita cursiva con contorno negro | idéntico (ASS, y ≈ 847 px) |
| Ritmo | un plano por frase de narración (3–8 s) | idéntico (9 escenas) |
| Sonido | narración continua + golpes de atención en cada corte | whoosh en cada corte + stinger heroico en la entrada + pop cómico |
| Duración | 75 s | 48 s (mejor retención en TikTok) |

## 2. Pipeline (sin créditos de Higgsfield ni Artlist)

**Imágenes, voz y SFX: Runway (plan gratis, 500 créditos).**

- `generate_image` — 20 créditos/imagen. Modelo `nano-banana-pro`, ratio `720:1280`.
- `generate_speech` — 1 crédito por cada 50 caracteres. Modelo `eleven_multilingual_v2`, `languageCode: es`, voz **Bernard**. Un segmento por escena (así el corte calza exacto con la frase).
- `generate_sound_effect` — 1 crédito/segundo. Sirve también para una **cama musical** en loop (`loop: true`, 25 s).
- `generate_video` y `generate_music` **requieren plan de pago**: no se usan. El movimiento se hace con Ken Burns en ffmpeg y queda igual de bien a velocidad de scroll.

Costo del prototipo completo: **~200 créditos** de 500.

### Consistencia de personajes
Generar primero el plano 1 (trabajador) y el plano del abogado. Después pasar esos `taskId` como `referenceImages` con etiqueta (`@worker`, `@lawyer`) y llamarlos por etiqueta dentro del prompt. Es lo que mantiene la cara igual en las 9 escenas.

### Moderación
Runway rechaza prompts con marcas registradas de estudios de animación (devuelve `moderationCategory: CHARACTER`). Describir el estilo sin nombrarlas: *"modern 3D animated feature-film still, glossy stylized characters with large expressive eyes, soft global illumination, shallow depth of field"*.

## 3. Armado

El armado se hace en el **sandbox de Higgsfield** (`sandbox_exec`), no en el contenedor de Claude:

- El contenedor de Claude **no alcanza** `dnznrvs05pmza.cloudfront.net` (egress bloqueado). El sandbox sí.
- El sandbox **sí persiste** entre llamadas y tiene 8 núcleos, ffmpeg 5.1 con libass, python3.
- Trabajos largos: `nohup ./build_all.sh > build.log 2>&1 &` y después revisar el log. El prototipo completo se renderizó en **14 segundos**.
- La salida de `sandbox_exec` se corta cerca de los 20.000 caracteres: para sacar una imagen en base64 hay que partirla con `head -c` / `tail -c +N`.

### Movimiento (Ken Burns)
```
scale=1440:-2,crop=1440:2560,
zoompan=z='1+0.14*on/D':d=D:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=720x1280:fps=30
```
Alternar acercamiento (`1+0.14*on/D`) y alejamiento (`1.14-0.14*on/D`) entre escenas. Renderizar las 9 escenas en paralelo con `&` + `wait`.

### Subtítulos (ASS)
```
PlayResX: 720 · PlayResY: 1280
Style: KAR,Liberation Sans,58,&H0000DEFF,&H0000DEFF,&H00000000,&H64000000,-1,-1,0,0,100,100,0,0,1,4,3,2,40,40,400,1
```
Una palabra por evento `Dialogue`, en MAYÚSCULAS, con `{\fad(40,40)}`. El reparto de tiempo dentro de cada frase es proporcional a `len(palabra)+1` sobre la duración real del mp3 de esa escena.

`MarginV: 400` con `Alignment: 2` deja el texto centrado en **y ≈ 847 px**: dentro de la zona segura de TikTok y por encima de la interfaz.

### Audio
- Voz: `adelay` de cada segmento al inicio de su escena.
- Cama musical: `aloop` + `atrim` + `volume=0.09` + fades de 1,2 s.
- SFX: whoosh 0,12 s **antes** de cada corte; stinger en la entrada del abogado; pop en el remate.
- Mezcla: `amix=normalize=0` + `alimiter=limit=0.95`.

Huecos entre frases: **0,30 s**, salvo el plano de entrada del abogado que lleva **1,30 s** para que respire el stinger.

## 4. Verificación obligatoria antes de publicar

No basta con que ffmpeg termine sin error. Hay que comprobar:

1. **Subtítulos quemados**: contar píxeles amarillos (`R>200, G>150, B<90`) por escena y sacar su fila media. Debe dar ~500–1.500 px centrados en y ≈ 847. *Un diff contra el video mudo en escala reducida NO sirve: da cifras bajísimas aunque el texto esté (error cometido en esta sesión).*
2. **9 escenas distintas**: hash de un frame por escena, las 9 deben diferir.
3. **Audio**: voz entre −21 y −24 dBFS, golpes de corte entre −15 y −19 dBFS, pico bajo −1 dBFS, cola final bajo −50 dBFS.
4. Duración de audio y video coincidentes (±0,05 s).

## 5. Base legal del prototipo (verificada)

- **Art. 31 CT** — máximo **2 horas extraordinarias por día**. (Fuente oficial: XML de BCN, idNorma 207436.)
- **Art. 32 inc. 3 CT** — las horas extras se pagan con **recargo del 50 %** sobre el sueldo convenido y deben liquidarse junto con las remuneraciones del período. (Fuente oficial: XML de BCN.)
- **Art. 162 inc. 5 CT ("Ley Bustos")** — si al momento del despido el empleador no ha enterado las cotizaciones previsionales, **el despido no produce el efecto de poner término al contrato**; debe seguir pagando remuneraciones hasta convalidarlo (inc. 6 y 7). (Fuente oficial: Compendio SUSESO.)
- **Art. 510 inc. 4 CT** — el cobro de horas extraordinarias **prescribe en 6 meses** desde que debieron pagarse. Es el gancho de urgencia del cierre.
- **Art. 171 CT** — despido indirecto: 60 días hábiles, indemnización aumentada hasta 50 % (causal N°7). *No verificado contra fuente oficial — confirmar antes de usarlo en un video.*

Nota de acceso: desde el contenedor de Claude, `leychile.cl`, `bcn.cl`, `dt.gob.cl` y `suseso.gob.cl` están bloqueados por el proxy. El XML de BCN sí se puede leer con **WebFetch**, pero llega truncado en el **art. 34 bis**: los artículos posteriores hay que contrastarlos en dos fuentes independientes.

## 6. Escaleta del prototipo

| # | Plano | Narración |
|---|---|---|
| 1 | Oficina de noche, trabajador agotado, reloj en las 11 | Tu jefe te tiene hasta las once de la noche y no te paga ni un peso extra. |
| 2 | El jefe le tira otra pila de carpetas encima | Te dice que es compromiso con la empresa. La ley dice otra cosa. |
| 3 | Mirando la liquidación en el pasillo | Llega fin de mes, y las horas extras no aparecen por ninguna parte. |
| 4 | Mesón de la clínica, sin cobertura | Vas al médico y te enteras de lo peor: nunca pagó tus cotizaciones. |
| 5 | **Entra el abogado brócoli** a contraluz | Y ahí aparece el abogado vegetal. |
| 6 | Los dos en el escritorio, Código abierto | Las horas extras se pagan con un cincuenta por ciento de recargo. Artículo treinta y dos. |
| 7 | El abogado le pasa la demanda al jefe | Y si no pagó tus cotizaciones, tu despido no produce efecto. Tiene que seguir pagándote el sueldo. |
| 8 | Juzgado del Trabajo | Por eso el jefe termina pálido en el Juzgado del Trabajo. |
| 9 | Apretón de manos en la escalinata | Ojo: las horas extras prescriben en seis meses. No lo dejes pasar. |

## 7. Pendiente

- El prototipo **no lleva el bloque de marca ni el WhatsApp** (se dejó fuera para copiar el referente puro). Si el formato se aprueba, agregarlos dentro de la zona segura `x[130,930] · y[200,1586]` según `motor/ZONA-SEGURA-v5.md`.
- El prototipo **no se publicó**, por instrucción expresa.
