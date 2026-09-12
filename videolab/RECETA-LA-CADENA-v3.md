# RECETA v3 — "LA CADENA" (formato Fruit Drama aplicado)

Video: 74.3 s · 13 planos · vertical 1080x1920 · giro en el segundo 40.3 (54 % del metraje).
**No publicado.** Link de revisión:
https://d2ol7oe51mr4n9.cloudfront.net/user_3IkWukwrqRk5HTPle6Rx8WbYgS3/045ea2aa-527d-4e3f-9fdb-2839b97bfea4.mp4

## 1. Personajes (regla del permiso emocional)
Todos los protagonistas son vegetales. El cráneo **ES** el vegetal (formado de granos/floretes, cara humana incrustada al frente, transición orgánica continua: "no seam, no hat, no costume"). Todo lo demás fotorrealista.

| Personaje | Vegetal | Función | Gancho irrelevante |
|---|---|---|---|
| Choclo | maíz | víctima | reloj de pulsera trizado que sobrevive hasta el final |
| El Ají | ají rojo brillante | villano | perro chihuahua diminuto bajo el brazo (4 planos) |
| El Brócoli | brócoli | abogado | no cabe por ninguna puerta |

## 2. Guion aprobado (13 planos)
1. A Choclo lo tenían encadenado a la máquina. Catorce horas al día, seis días a la semana.
2. Su jefe le decía que era por su bien. Que así no se distraía y rendía más.
3. Que afuera no valía nada. Que nadie lo iba a contratar. Que tenía suerte.
4. A fin de mes le pagaba la mitad. La otra mitad, decía, era un tema de confianza.
5. Cuando se enfermó y llegó al hospital, le dijeron que no figuraba en ninguna parte.
6. Que nadie había pagado nunca un peso por él. Que para el sistema, no existía.
7. Esa noche se quedó dormido en el suelo de la fábrica. Alguien golpeó la puerta.
8. **Era el brócoli. No cabía. Tuvo que entrar de lado.** ← giro, stinger grave
9. No dijo ni una palabra. Se agachó, miró la cadena, y después miró al ají.
10. Abrió el maletín y sacó un papel: el historial de cotizaciones de Choclo. Estaba en blanco.
11. El ají lo leyó dos veces. Se le cayó el perro de las manos.
12. Al otro día Choclo llegó a la fábrica y la cadena ya no estaba. El ají le pagó todo.
13. Pero esa misma noche, el ají hizo una llamada. → placa **PARTE 2 MAÑANA**

Regla de trama: el abogado nunca cita un artículo; **hace algo** por el trabajador.

## 3. Pipeline que funcionó
1. **Imágenes** — ElevenLabs `creative_generate_image` (gemini-3-pro-image). Vertical solo con el rodeo: `estimate_only:true` → `creative_update_node` con `{"aspect_ratio":"9:16","resolution":"1K"}` → `creative_run_flow_nodes` (hasta 20 nodos de una vez).
2. **Animación** — `ltx-v2-fast`, 6 s, 1080p, audio nativo ON, `connect_from` = nodo imagen. Plano 11 se hizo en Artlist con **Kling 2.5 Turbo Pro I2V** (modelId 2017).
3. **Narración** — HeyGen `create_speech`, voz *Diego Martinez – Broadcaster* (`87bf17e8c82a4e1a966a5fbca3cab12c`), `speed 0.96`, `language es`. **Gratis y devuelve word_timestamps.**
4. **Montaje** — sandbox de Higgsfield (ffmpeg + numpy).

## 4. Reglas de animación (verificadas con métrica)
Métrica de movimiento = diferencia media por píxel entre frames a 1/15 s, gris, 96 px de ancho. Banda de los virales de referencia: **4.6 – 9.9**.

- Prompts con **acción física grande + cámara explícita** ("shoves his finger into his chest three times", "the camera cranes down fast"). Los 10 planos salieron entre 5.5 y 13.3 a la primera.
- Prompts sutiles ("respira lento", "parpadea") dan clips casi estáticos (0.7 – 1.8). No usarlos nunca.
- El movimiento no empieza en t=0: arranca entre 1.6 y 2.0 s. Hay que perfilar y cortar cada plano desde su mejor ventana.
- Resultado final medido: **motion medio 10.74**.

## 5. Audio
- Voz al 0.98, ambiente nativo de cada clip al 0.135.
- Whoosh de ruido filtrado 0.5 s antes de cada corte (12 cortes).
- Golpe grave (46 Hz + 69 Hz, decay 2.6) en los planos 7, 8, 11 y 13.
- Pulso de tensión cada 1.15 s desde el inicio hasta el giro, al 0.09.
- Limitador tanh final. Medido: pico 0.74, rms 0.118.

## 6. Subtítulos
ASS quemado, `Liberation Sans` 86 sobre PlayResY 1920, blanco `&H00FFFFFF`, Outline 5 / Shadow 4, `{\an5\pos(540,Y)\fad(35,35)}`, **una palabra a la vez en MAYÚSCULAS**, Y flotante por plano (1160–1350).
Timings tomados de los `word_timestamps` de HeyGen, recalculados tras comprimir los silencios.

**Verificación obligatoria:** contar píxeles blancos (>235) en la banda inferior y su media por fila. Nunca usar un diff en gris contra el video mudo: da falso negativo.

## 7. Truco de ritmo
Comprimir todo silencio interno de la narración a **0.42 s máximo** usando los word_timestamps. Ahorró ~8 s de aire muerto sin acelerar la voz.

## 8. Restricciones operativas del entorno
- El sandbox de Higgsfield se borra entre llamadas y el comando tiene tope de **16000 caracteres**. Trocear en etapas y pasar los intermedios por `media_upload` (PUT presignado) → URL CloudFront corta y permanente.
- Las URLs firmadas de GCS se comprimen a la mitad guardando solo sesión, genid, fecha y firma, y reconstruyendo la URL en bash.
- El contenedor propio no alcanza googleapis / heygen / artlist (proxy 403). Todo el armado va por el sandbox.

## 9. Estado de créditos tras este video
ElevenLabs 50 · Runway 16 · Higgsfield 1 · AgentOpus 0 · HeyGen video 0 · Artlist gratis usada.
Único recurso gratis que queda: **HeyGen TTS**.
