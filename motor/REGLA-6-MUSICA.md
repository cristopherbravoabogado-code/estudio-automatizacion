# REGLA DURA 6 — CAMA MUSICAL CC0 CON DUCKING (medida el 18/09/2026, M6 corrida 2)

> Este archivo es la versión larga de la **regla dura 6** de `motor/RECETA-MOTOR-NUBE.md`,
> igual que `motor/ZONA-SEGURA-v5.md` lo es de la regla dura 4. Lo implementa `videolab/musica.py`.

---

## El problema que se midió

Las piezas del motor salen **sin música**. Entre frase y frase queda aire muerto: medido sobre una
narración real de 19,8 s (HeyGen, voz Diego Martinez, guion de Ley Bustos), los silencios entre
tramos están en **−26,0 LUFS** mientras la voz se entrega a −14,2 LUFS. Son 12 dB de nada, seis
veces por pieza. Los referentes virales radiografiados (viral-01, viral-02, fruit drama) no tienen
ese hueco: llevan cama musical o efectos.

La pregunta de la corrida: **¿se puede poner música gratis sin que la voz pierda nivel?**

## Fuentes gratis: lo que responde y lo que no (probado desde el sandbox el 18/09/2026)

| Fuente | Código | Veredicto |
|---|---|---|
| **Openverse API** `api.openverse.org/v1/audio/` | 200 | ✅ **LA FUENTE**. Sin clave, sin cuenta. Filtro `license=cc0` = sin obligación de acreditar. Devuelve el CDN de Freesound, que baja directo |
| **Mixkit efectos** `assets.mixkit.co/active_storage/sfx/<id>/<id>-preview.mp3` | 200 | ✅ efectos sueltos (whoosh, boom) |
| incompetech (Kevin MacLeod) | 200 | 🟡 baja el mp3 completo (7,3 MB), pero es **CC-BY: obliga a acreditar al autor en la descripción**. Solo si Openverse no trae nada |
| archive.org | 200 | 🟡 sirve, hay que filtrar a mano |
| Mixkit música `assets.mixkit.co/music/preview/...` | **403** | ⛔ no insistir |
| Pixabay CDN de audio | **403** | ⛔ no insistir |
| Freesound API directo | **401** | ⛔ exige clave |
| Free Music Archive | **403** | ⛔ no insistir |

## El número que decidió: DUCKING, no música estática

Nueve mezclas de la misma narración, misma pista, medidas en LUFS después de normalizar a −14
(que es lo que hace TikTok con todo lo que se le sube):

| Mezcla | LUFS mezcla | Voz entregada | Silencios |
|---|---|---|---|
| **voz sola (base)** | −17,0 | **−14,2** | −26,0 |
| estática −24 dB | −17,0 | −14,2 | −27,8 |
| estática −16 dB | −17,1 | −14,0 | −24,9 |
| estática −8 dB | −16,4 | −13,9 | −19,4 |
| estática 0 dB | **−13,1** ⛔ | −14,1 | −14,9 |
| estática +6 dB | **−8,6** ⛔ | −14,2 | −13,7 |
| **ducking 0 dB** | **−16,2** ✅ | **−14,4** | **−13,4** |
| ducking −4 dB | −16,9 | −14,1 | −16,6 |
| ducking −8 dB | −17,2 | −14,0 | −19,9 |

**Lo que dice la tabla:** con ducking a 0 dB el aire muerto pasa de −26,0 a −13,4 LUFS —**12,6 dB de
relleno**— y la voz entregada se mueve 0,2 dB (−14,2 → −14,4). Para rellenar lo mismo con música
estática hay que ponerla a 0 dB, y entonces la mezcla sube a −13,1 LUFS: **TikTok normaliza a ~−14 y
baja la pieza entera**, o sea la voz le llega al espectador más callada que si no hubiera música.
Esa es toda la diferencia: el ducking compra presencia en los silencios sin pagarla con nivel de voz.

Corrida real de punta a punta con `videolab/musica.py` y una pista CC0 de Openverse
("Suspense Motif", freesound, cc0, 15 s, repetida con `-stream_loop`):
**búsqueda 0,73 s · descarga 4,0 s · mezcla 1,0 s · control 2,3 s ≈ 8 s por pieza, US$0**,
salida `pcm_s16le, 48000, 2` (cumple la regla dura 3). Resultado:
`MUSICA_OK {"lufs_mezcla": −16,79, "voz_entregada": −14,2, "silencios": −17,06}`.

## ⛔ DESCARTADO CON NÚMERO — no volver a probarlo

- **Música estática a cualquier nivel.** O no se oye (−16 dB y abajo: silencios en −24,9, casi aire
  muerto) o se come la pieza en la normalización (0 dB: mezcla en −13,1). Dominada por el ducking
  en las tres columnas a la vez.
- **WER como juez del nivel de música.** Se midió con faster-whisper `small` en las **12** mezclas,
  incluida música **6 dB MÁS FUERTE que la voz**: **WER = 0,0000 en todas**. Whisper entiende a
  través de la música, así que no distingue nada y **no sirve para decidir el nivel de una cama
  musical**. El que decide es el par (voz entregada, silencios) en LUFS. WER sigue siendo el juez
  para lo que sí mide: calidad de la voz sintética y palabras fuera del guion (control 6 y 7).

## Cómo se usa

```bash
python3 musica.py buscar "cinematic tension" 5          # Openverse CC0, sin clave
python3 musica.py mezclar voz.mp3 mus.mp3 final.wav 0   # ducking a 0 dB
python3 musica.py control final.wav tramos.json         # BLOQUEA si no pasa
```

`tramos.json` es la lista de `[inicio,fin]` de los tramos CON VOZ (los mismos límites que ya deja
`voz.py` en `<n>.mp3.tramos.json`, o los `word_timestamps` de HeyGen).

**Criterio del control** (`CRITERIO` en `musica.py`):

- voz entregada **≥ −14,8 LUFS** (no más de 0,6 dB bajo la voz sola)
- mezcla **≤ −15,5 LUFS** (si sube, TikTok baja la pieza entera)
- silencios **≤ −12,0 LUFS** (relleno, no invasión)

El filtro, por si hay que replicarlo fuera de `musica.py`:

```
[0:a]loudnorm=I=-16:TP=-1.5:LRA=11,aformat=...48000...,asplit=2[v][sc];
[1:a]atrim=0,asetpts=N/SR/TB,loudnorm=I=-16:TP=-1.5:LRA=11,volume=0dB,aformat=...[m];
[m][sc]sidechaincompress=threshold=0.03:ratio=12:attack=15:release=350:makeup=1[md];
[v][md]amix=inputs=2:duration=first:normalize=0[a]
```

## Licencia: por qué CC0 y no CC-BY

`buscar()` pide `license=cc0` por defecto: **CC0 no obliga a acreditar a nadie**, así que la
descripción del TikTok queda libre para el gancho y el CTA. Si Openverse no devuelve nada, la
función degrada sola a `cc-by` y **rellena el campo `atribucion` con el autor: si sale una pieza con
una pista cc-by, ese nombre TIENE que ir en la descripción**. Nunca se publica música cuya licencia
no se conozca.

## Lección de sandbox de esta corrida

`raw.githubusercontent.com/<owner>/<repo>/main/<ruta>` **cachea ~5 minutos y el truco del
`?t=<epoch>` NO lo salta** (probado: siguió bajando la versión anterior). Lo que sí funciona es pedir
el archivo **por el SHA del commit**:
`raw.githubusercontent.com/<owner>/<repo>/<sha-del-commit>/<ruta>` — llega fresco al instante.
Vale para toda receta que acabe de commitear un `.py` y quiera probarlo en la misma corrida.
