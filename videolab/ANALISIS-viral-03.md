# ANÁLISIS viral-03 — "¿Cómo recuperar tu dinero si te equivocaste en una transferencia?" (06/09/2026)

Descubierto en la corrida del Viral Lab del 06/09. La búsqueda del nicho legal ("finiquito chile abogado shorts",
"abogado responde shorts") no devolvió ningún short ≤ 90 s con volumen real: el nicho legal en YouTube publica
videos largos. Se aplicó entonces la regla de "1 de cada 3 de otro rubro" (finanzas personales) y apareció este.

## Fuente
- YouTube Shorts `5z5jrfVqLKo` — canal **NMás** (noticiero mexicano), subido el 19/09/2023.
- 127.027 vistas · 316 me gusta · 62 comentarios · 58 s · 1280x720 (horizontal, no vertical).
- https://www.youtube.com/watch?v=5z5jrfVqLKo

## Radiografía (analizar.py, números, sin opinión)
- Duración 58,0 s · **12 cortes** · un corte cada **4,84 s** (viral-01: 1,45 s).
- 111 palabras · **1,91 palabras/s** (2,68 hablando) · **9 pausas** mayores a 0,5 s.
- Loudness media −17,5 dB · pico −2,2 dB · sin música audible por sobre la voz.
- Gancho hablado de los 3 primeros segundos: la pregunta del título, dicha literal.
- Bloques detectados: 0–13 s · 14,3–21,6 s · 22,9–58 s.
- Sin rostro de narrador: voz en off sobre imágenes de apoyo y placas.

## La plantilla en 8 líneas (F13 — "Protocolo por escenarios")
1. **Gancho**: la pregunta-problema dicha literal en el segundo 0, sin preámbulo ni saludo ("¿Cómo recuperar tu dinero si…").
2. **Promesa**: implícita y total — no promete explicar, promete resolver: aquí está el protocolo.
3. **Bloques**: escenario A (0–13 s: "si pasó de esta forma, no se puede detener") → escenario B (14–22 s) → escenario C (23–43 s) → dato de cierre que da esperanza (43–58 s).
4. **Anuncio/CTA**: ninguno en el original. En la adaptación, el estudio entra como el escenario D ("si ya pasaron los días, esto se pelea") con dirección y WhatsApp al final de ese bloque.
5. **Ritmo**: lento y hablado — 1,9 palabras/s, corte cada 4,8 s, 9 pausas. Al revés del viral-01: aquí la pausa es el recurso, porque el espectador está memorizando pasos.
6. **Tono**: noticiero de servicio. Cero ironía, cero anécdota, cero primera persona.
7. **Cierre**: no hay CTA ni cliffhanger; termina en el dato que hace sentir que todavía se puede ("los depósitos interbancarios tardan más de 24 horas").
8. **Por qué funcionó (hipótesis)**: es un video que se guarda, no que se comenta. El espectador no busca entretención sino un procedimiento, y la ramificación "si te pasó A… si te pasó B…" hace que cada uno se reconozca en una rama y se quede hasta la suya. Las pausas y el ritmo lento existen para que se pueda anotar.

## Por qué sirve al estudio
Es la estructura natural de la primera consulta: casi ninguna pregunta legal tiene una sola respuesta, tiene ramas.
"Te despidieron: si te dieron carta… si no te dieron carta… si te lo dijeron por WhatsApp…" es exactamente este
formato, y produce el video que la gente guarda y vuelve a ver, que es el que después llega al WhatsApp.
Se propone como **F13** en `videolab/formatos.json` para producir en la próxima corrida de ensayo.

## Límite ético aplicado
Del original no se toma ninguna frase, imagen, música ni el tema (transferencias bancarias en México). Se toma
únicamente la arquitectura: pregunta-problema literal en el segundo 0, tres ramas por escenario, ritmo lento con
pausas, cierre en el dato que da esperanza.
