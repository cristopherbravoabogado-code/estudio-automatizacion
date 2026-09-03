# Arquitectura de la fabrica de video

## Cadena completa

```
tema + guion
   -> voz (ElevenLabs, Cristian Cornejo)
   -> gancho visual (clip Higgsfield o imagen animada con zoompan)
   -> ilustracion animada (arte.py + escenas.py)
   -> montaje (render5.py / render6.py)
   -> musica sintetizada (moderna.py)
   -> mp4 1080x1920
```

## Modulos

| Archivo | Que hace |
|---|---|
| `arte.py` | Ilustracion plana con PIL a supermuestreo 3x, reducida con LANCZOS. Personas con gestos (saluda / presenta / piensa), 4 tonos de piel y pelo, ~24 objetos (documento, balanza, mazo, casa, auto, escudo, reloj, celular, sobre, billete, corazon, edificio, libro, mascota, hospital, semaforo, globo, candado, avion, calculadora, cerca, graduacion) |
| `escenas.py` | Arma las 5 escenas de 3 elementos en 4 disposiciones que rotan |
| `render5.py` | Motor ilustrado v5. Entrada escalonada con ease-back, flotacion senoidal, giro suave, fondo con dos capas de parallax |
| `render6.py` | Motor hibrido: primeros ~6 s de metraje cinematografico + resto ilustrado. Reutiliza los ayudantes de render5 y solo cambia la escena 0 |
| `musica.py` | Motor clasico: estilos sobrio y lofi |
| `moderna.py` | Motor actual: reggaeton/dembow, trap latino con 808 y glide, phonk con cencerro, pop electronico |
| `voz2.py` | Piper VITS por onnxruntime. Respaldo local si ElevenLabs no esta disponible |

## Formato de video (afinado con evidencia)

- **22 s exactos**: gancho 3,6 s + 3 puntos de 4,6 s + cierre 4,6 s
- La franja 21-34 s es la de mayor tasa de finalizacion. En 2026 se
  necesita ~70% de finalizacion para que el video corra
- **Corte de atencion cada ~2 s**: ademas del cambio de placa, el detalle
  de cada punto entra a los 0,85 s con fundido de 0,22 s
- **Sin fundido a negro al final**: la ultima placa queda en pantalla para
  que el bucle sea limpio. Solo oscurecido de entrada (0,32 s)
- **Zoom lento alternado** (1,12) recalculado 15 veces por segundo y
  memorizado. Recalcularlo por cuadro duplica el render sin diferencia visible
- **Zona segura TikTok**: cabecera a 230 px del borde superior, barra de
  progreso a 330 px del inferior, contenido centrado en H*0,50

## Paleta por materia

penal rojo - laboral ambar - familia violeta - civil verde azulado -
consumidor naranjo - transito azul - previsional verde - salud cian -
tributario dorado - digital cian - migratorio azul claro - vecinal arena -
educacional celeste - animal verde lima

## Musica: se sintetiza, no se descarga

Los bancos de musica libre estan bloqueados por el proxy del contenedor
(pixabay, freemusicarchive, incompetech, archive.org, freesound). Por eso
`musica.py` y `moderna.py` generan la pista desde cero con numpy + scipy.

Dos ventajas que resultaron mejores que descargar:

1. Al ser original no hay derechos que TikTok pueda reclamar
2. El algoritmo de TikTok 2026 **prioriza el audio original** por sobre
   los sonidos de tendencia

La semilla sale del hash del nombre del archivo, asi que cada video tiene
tonalidad, tempo y progresion propias, y el resultado es reproducible.

## Motor hibrido render6.py

- Los cuadros del clip se leen en **streaming** desde un pipe de ffmpeg
  reescalado a 1080x1920@30 (`scale=...:force_original_aspect_ratio=increase,crop`).
  Nunca se cargan todos en RAM
- **Velo degradado** oscuro arriba y abajo compuesto sobre el video: sin
  el, el texto blanco se pierde
- El gancho va en el **tercio inferior** (H*0,60), no arriba
- Audio de tres fuentes: voz + musica al 0,12 + ambiente del clip al 0,55
  con `afade` de salida, todo a `loudnorm=I=-14`
- **Economia**: el clip de cine cuesta creditos, el resto es gratis. Un
  clip de gancho se puede reutilizar en varias piezas de la misma materia
- **Gancho a costo cero**: una imagen generada gratis (Artlist Seedream,
  9:16) + `zoompan` de ffmpeg da un clip de 6 s que entra a render6 como
  si fuera metraje real:
  `-loop 1 -i img.jpg` + `anullsrc` +
  `scale=2160:3840,crop,zoompan=z='min(1+0.00055*on,1.11)':d=180:s=1080x1920`

## Maquetacion: lecciones que costaron caro

- Los textos deben **armarse por bloque** (titulo con max_lineas y cuerpo
  auto-reducido, detalle debajo, subtitulo karaoke fijo abajo) o el titulo
  choca con el subtitulo
- Hay que **recortar la posicion de cada sprite** dentro del cuadro o las
  manos se salen
- Las rutas del archivo de concat de ffmpeg deben ser **absolutas**
  (`os.path.abspath`). ffmpeg las resuelve respecto al archivo de lista y
  las duplica, y ningun mp4 se genera
- Chromium headless intenta salir a la red y el proxy lo rechaza: lanzarlo
  con `--disable-background-networking --disable-component-update
  --disable-sync --no-first-run` y sin variables de proxy

## Rendimiento y ejecucion

- ~30-40 s por video con 2 procesos en paralelo. 300 videos = ~2,5 h
- El contenedor se reclama cuando la sesion queda inactiva y **mata los
  procesos en segundo plano**. Renderizar EN PRIMER PLANO por tandas
  (`tanda.sh`, ~9 min por llamada)
- Ojo con `pkill -f`: matcha el propio shell de la herramienta
- En GitHub Actions nada de esto aplica: el job corre hasta terminar
