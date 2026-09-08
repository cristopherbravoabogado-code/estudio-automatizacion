# ANÁLISIS viral-04 — "Alerta: anatomía del engaño" (07/09/2026)

Fuente: YouTube Shorts `2JyVepHjSKE`, canal **UnoTV**, "Envían supuestos mensajes de bancos diciendo que retiraron dinero de tu cuenta, pero es fraude". 40.404 vistas, 84 likes, 3 comentarios, 83 s, subido el 11/11/2022.

Rubro: **finanzas personales / seguridad**. Es la corrida "fuera de nicho" (1 de cada 3), y por eso vale: la estructura no existía todavía en la biblioteca.

Búsqueda que lo trajo: `ytsearch25:"estafa transferencia banco" shorts`, filtrado a ≤ 90 s y ordenado por vistas.

## Radiografía (analizar.py, números, sin opinión)

| medida | valor |
| :-- | :-- |
| duración | 82,7 s |
| resolución | 1280x720 |
| cortes de escena | 20 → **1 cada 4,13 s** |
| palabras | 202 → **2,44 palabras/s** (2,71 hablando) |
| pausas > 0,5 s | **2 en todo el video** (0,62 s en 22,8 y 0,58 s en 63,6) |
| loudness medio | −23,6 dB (pico −2,8) |
| cara del narrador | no |
| gancho hablado de los 3 s | "Si te ha llegado un mensaje como este no" |

Las dos únicas pausas caen exactamente en las dos junturas de la estructura. No son respiros: son puntos y aparte.

## La plantilla en 8 líneas (F14)

1. **Tipo de gancho**: orden. Imperativo negativo en 2ª persona señalando un objeto que el espectador probablemente tiene en la mano ("un mensaje como este"). Segundo cero, sin saludo, sin marca, sin pregunta.
2. **Promesa**: no te voy a enseñar algo, te voy a evitar una pérdida que ya está en curso.
3. **Bloques**: 0–6 la orden · 6–23 qué es y por qué cuela (te hacen creer que ya te robaron) · 23–34 el paso exacto que no hay que dar · 34–53 la cadena de consecuencias si lo das · 53–64 el nombre del fraude y la regla general · 64–78 qué hacer en cambio y la regla que lo desarma todo.
4. **Dónde entra el CTA**: no hay CTA comercial. El lugar equivalente es el bloque 6: "acude a una sucursal". El anuncio, si lo hubiera, va ahí, como la salida del problema, nunca antes.
5. **Ritmo**: lento y parejo. 2,44 palabras/s, corte cada 4,13 s, sin silencios dramáticos. El espectador está memorizando, no siguiendo un chiste.
6. **Tono**: servicio, cero ironía, cero anécdota, cero primera persona. Voz en off sobre planos de apoyo.
7. **Cierre**: no cliffhanger y no pregunta. Cierra con una **regla portátil** que el espectador puede repetirle a otra persona ("los bancos nunca van a pedir esa información por esas vías").
8. **Por qué funcionó (hipótesis H-13)**: el video no compite por curiosidad sino por miedo concreto y presente. El espectador se queda porque necesita saber si el mensaje que tiene en el teléfono es ese. Y comparte porque el cierre le da una frase corta que le sirve para advertir a su mamá.

## Diferencia con lo que ya teníamos

- Contra **F11 (ensayo)**: F11 abre con anécdota en 1ª persona a 3,3 palabras/s. F14 no tiene narrador con biografía y va a 2,44. F11 pide complicidad; F14 pide obediencia.
- Contra **F13 (protocolo por escenarios)**: F13 abre con una pregunta ("¿cómo recuperas tu plata si…") y ramifica en A/B/C. F14 abre con una orden y avanza en línea recta: qué es → qué no hacer → qué pasa si lo haces → la regla. F13 se guarda; F14 se reenvía.

## Adaptación producida el 07/09

Tema propio: **trabajo temporal para el 18 de septiembre ofrecido "a boleta"**. Misma estructura, mismo ritmo (voz Kokoro em_alex a atempo 0,82 para bajar de 2,97 a 2,44 palabras/s), contenido 100% propio, cero frases del original.

Guion y verificación legal: `videolab/viral/guiones/2026-09-07-trabajo-a-boleta-dieciocho.txt`.

## Hallazgo técnico del día (corrige la nota del 06/09)

El 06/09 se anotó en `biblioteca.json` que **yt-dlp ya no descarga de YouTube desde el sandbox** ("Sign in to confirm you are not a bot"). **El 07/09 sí descargó**, dos videos seguidos, con `-f "bv*[height<=720]+ba/b"` y sin cookies. Solo advierte que no hay runtime de JavaScript y que algunos formatos pueden faltar. La puerta no está cerrada: estaba con llave ese día. Reintentar siempre antes de dar por perdida la descarga (afecta también a la Tendencia del día, que el 07/09 replicó una estructura vieja por creer que no podía bajar el video del tema).

## Error del propio analizar.py (arreglar)

`bajar()` escribe siempre en `viral_in.mp4` y yt-dlp **omite la descarga si el archivo ya existe**. Al analizar dos videos en la misma sesión, el segundo JSON queda con el audio del primero. Se detectó porque las dos radiografías salieron idénticas al decimal. Mientras no se corrija en el repo: borrar `viral_in.mp4` y `viral_a.wav` entre corridas.
