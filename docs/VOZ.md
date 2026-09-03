# Voz

## Decision vigente

**Cristian Cornejo - Espanol Chileno Fluido** (10/10)
`ClNifCEVq1smkl4M3aTk` - ElevenLabs - modelo `eleven_multilingual_v2`

Segunda voz para alternar: **Catalina - Espanol Chileno** (9/10)
`6Gr4AVmTax1pMJO0lHRK`

Criterio del estudio: *"un chileno neutro o un espanol neutro neutro"*.
Cualquier marca regional ajena se nota y molesta.

## Voces descartadas y por que

| Voz | Motivo |
|---|---|
| Jorge - Espanol Latino Neutro Unico | Acento mexicano. **No volver a proponerla** |
| Eugenio - Cinematic Narration | Acento venezolano |
| Kokoro (es) | Sale con acento frances: sus voces no inglesas de la v1.0 estan poco entrenadas y el vocabulario hubo que reconstruirlo a mano |
| Piper es_MX-claude-high | Mexicano. Sirve solo como respaldo offline |
| Voces de Artlist | Los 73 registros son multilingues con acentos American, British, Australian e Indian |
| Voces del Mac (Monica, Paulina) | Compactas a 22 kHz, planas. Las Eloquence suenan a robot de los 80 |
| Luis, Mateo, ROGUS | Bloqueadas en plan gratis (piden Creator) |

## Como buscar voces en ElevenLabs

`creative_list_voices` filtra por **texto libre sobre nombre y descripcion**.
Buscar por el **codigo de acento**, no por descripciones genericas:

```
search="es-chilean"     search="es-mexican"     search="es-argentine"
```

Buscando "spanish latin american" las voces chilenas **no aparecen**.

## Costos y trampas

- **1 credito por caracter.** Un video de 5 lineas / 379 caracteres = 378 creditos
- 100 videos = ~37.900 caracteres = ~37.900 creditos
- `generations_count` viene en **4 por defecto**: ponerlo en 1 o se cobra
  cuatro veces
- Para elegir voz sin gastar en descargas: generar y usar
  `creative_show_flow_results`, que las reproduce en la app
- El precio va por caracteres, no por duracion: una voz mas agil acorta
  el video sin costar mas

## Ritmo medido (misma frase de 137 caracteres)

Cristian 6,2 s - Eugenio 6,6 s - Ignacio 7,8 s - Catalina 9,2 s -
Elio 9,4 s - Mac Mc 9,7 s - Andre 10,0 s - Cesar 11,2 s

Para videos de 25 s conviene el rango de 6-8 s. Con Cristian el video 707
completo quedo en 23,3 s; con Catalina, 28,2 s, mismo guion.

## Respaldo local (voz2.py)

Modelos **Piper VITS** desde las releases de `k2-fsa/sherpa-onnx`, tag
`tts-models`, p. ej. `vits-piper-es_MX-claude-high.tar.bz2`. Traen su
propio `phoneme_id_map` dentro del `.onnx.json`: cero adivinanza.

El binario piper del tarball no puede cargarlos (onnxruntime 1.14 solo
llega a IR version 8). Hay que correrlos desde Python:
espeak-ng `--ipa=3` con el idioma que declara el config -> mapa del json ->
entradas `input` / `input_lengths` / `scales`, intercalando PAD 0 entre
fonemas, BOS 1 al inicio y EOS 2 al final. `scales = [ruido, 1/velocidad, ruido_w]`.
Velocidad 1,12. 22050 Hz.

`voz2.revisar(texto)` lista los caracteres que el modelo no conoce. Es la
forma barata de validar pronunciacion sin poder escuchar.

espeak-ng + espeak-ng-data vienen dentro de `piper_linux_x86_64.tar.gz`
de rhasspy/piper (chmod +x).

**Regla:** nunca reconstruir vocabularios a mano.
