# Supervideo (receta v1 — 14/09/2026)

Dos videos de prueba de ~60 s, costo $0, hechos 100% en el sandbox de Higgsfield:

- A `supervideo_A_ia_indemnizacion.mp4` — media_id `b035baf5-865a-40f0-a363-293a9c807643` (60.7 s)
- B `supervideo_B_puma_ovejas.mp4` — media_id `2dd1cdd0-dfd4-4d13-89dc-125628d8ea75` (59.3 s)

## Capas
1. **Narración**: HeyGen `create_speech` (voz Diego Martinez, gratis) → `word_timestamps`. `build_sv.py prep` recorta silencios (MAXGAP .42) y genera el timeline `tl_K.json` (t0 por segmento + palabras con tiempos comprimidos).
2. **Video base** (`mute_K.mp4`): plano 0 = foto de prensa real (og:image BioBio) como tarjeta de noticia sobre la misma foto desenfocada; planos 1-6 = clips Mixkit (OCR-verificados) en loop; cortes con `xfade` (slideleft, wipeup, fade, slideright, wipedown, fade) en `T0[k]`.
3. **Overlay animado** (`ov_K.webm`, VP9 con alfa): HyperFrames local (`setup_hf.sh`) + GSAP. `overlay.py` escribe `hf_K/index.html` usando los tiempos **comprimidos** de `tl_K.json` (no los crudos de HeyGen). Render: `cd hf_K && npx hyperframes render --output ../ov_K.webm --format webm` (~1m40 por 60 s).
4. **Audio master** (numpy): voz 0.98, música Mixkit 0.20 con ducking, boom al inicio y en la palabra-golpe, whoosh en cada corte, riser 2.4 s antes del giro, limitador tanh.
5. **Subtítulos karaoke** (ASS, 84 px, Y flotante) + **final**: `ffmpeg -i mute -c:v libvpx-vp9 -i ov.webm -i master.wav ... overlay,ass` → `final_K.mp4` → PUT a la URL prefirmada de `media_upload` → `media_confirm`.

## Orden en el sandbox
`media_upload` (2 URLs) → `sandbox_exec background:true` con `run.sh` (setup → prep A/B en paralelo → init hf_A/hf_B con `hyperframes init --example swiss-grid --resolution portrait` y reemplazo del index.html → render A/B en paralelo → final A/B) → sondeos cortos (`sleep ≤45`) → `media_confirm`.

## Verificación
`VERIF` imprime duración, códecs, movimiento medio (A 3.99 / B 5.91) y frames con subtítulo (A 115/121, B 107/119). Revisión visual: hoja de 8 fotogramas clave (`select=eq(n,...)`, `tile=4x2`, q16) exportada en base64 por trozos de 12 000 chars con md5 por trozo.
