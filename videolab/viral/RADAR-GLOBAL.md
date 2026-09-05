# RADAR GLOBAL — cómo se enchufan las tendencias reales del mundo a la producción

Cristopher lo pidió el 05/09/2026: *"cómo conectamos a nuestra infraestructura los virales reales
del día de todo el mundo"*. Esta es la respuesta y su código: `videolab/viral/radar.py`.

## La idea en una línea
El video del día no se elige copiando "el video viral del mundo" (casi siempre es fútbol, farándula
o un baile: no vende asesoría). Se arma cruzando **dos ejes**:

```
EJE 1 — TEMA          qué le importa al mundo HOY      → radar.py
EJE 2 — ESTRUCTURA    cómo se cuenta lo que retiene    → analizar.py + biblioteca.json
VIDEO DEL DÍA = TEMA del eje 1  ×  ESTRUCTURA del eje 2
```

## EJE 1 — El radar (4 fuentes, gratis, sin clave, ~3 segundos)
`python3 radar.py salida.json [--video]`

| Fuente | Qué entrega | Cobertura |
|---|---|---|
| Google Trends RSS | tema + volumen de búsqueda + titulares asociados | CL, MX, ES, AR, US (ampliable a cualquier país) |
| Google News RSS | titulares del día | mismos países, en su idioma |
| Wikipedia pageviews | los 25 artículos más leídos ayer | es y en (el mundo entero) |
| trends24 | tendencias de X/Twitter | por país |

Medido el 05/09/2026: **230 temas distintos en 2,8 s**, de los cuales 24 tenían ángulo jurídico.

Cada tema pasa por `score_legal()`: un diccionario de 7 materias (laboral, familia, penal, civil,
consumidor, tránsito, salud) + palabras de conflicto (ley, corte, demanda, fallo, multa…), y se
multiplica por el **peso del país** (Chile ×3: es el mercado; el resto ×1 a ×1,5). Así, una noticia
chilena de un detenido sube por encima de una tendencia mundial de fútbol.

Con `--video`, los 4 temas mejor puntuados pasan por yt-dlp: busca en YouTube Shorts ese tema
(primero acotado a Chile y ≤120 s; si no hay, abierto y ≤180 s) y devuelve **el video real con sus
vistas**. Ese es el viral que se radiografía con `analizar.py`.

## Puertas cerradas (probadas el 05/09/2026 — no volver a intentarlas)
- **Reddit**: `r/all/top.json` responde "Blocked - network policy". La IP del datacenter está vetada.
- **TikTok Creative Center** (el ranking oficial de hashtags y videos): `code 40101 no permission`.
  Su API pide firma (`user-sign`) que se calcula en el navegador. Sin eso, no hay ranking de TikTok.
- **YouTube /feed/trending**: YouTube retiró la página de tendencias; yt-dlp devuelve "does not exist".
- Queda como sustituto de TikTok: las **cuentas semilla** (yt-dlp `--impersonate chrome` sobre
  perfiles) y la **búsqueda de YouTube Shorts**, que sí dan vistas reales.

## Lo que sí aporta el conector de TikTok (conectado el 05/09)
`tiktok_music_trending` (Higgsfield, connector f23f2205-…): las 100 pistas más usadas del día en
Chile, de la Biblioteca de Música Comercial. **No son los sonidos virales de usuarios**, son pistas
licenciadas para marcas: sirven como música de fondo legal, no como "el sonido del momento".

## Cómo entra a la producción
1. **Tendencia del día** (10:00) corre `radar.py --video`, elige el tema mejor puntuado con video,
   lo radiografía, lo replica con la estructura y lo publica esa misma mañana.
2. **Viral Lab** (15:00) usa el mismo radar cuando no hay un video mandado por Cristopher.
3. Cada corrida guarda su JSON en `videolab/viral/radar/<fecha>.json`: con el tiempo es la serie
   histórica de qué se habló cada día y qué rindió, que es lo que permite anticipar en vez de reaccionar.
4. La medición sigue siendo de Metricool a 72 h (vistas, % completado, comentarios, fuente del tráfico).

## Ética (igual que el resto del Viral Lab)
Se copia la ESTRUCTURA, nunca el contenido: cero frases, clips o música del original. Los temas de
actualidad se tratan como contexto para explicar un derecho, sin opinar de causas en curso, sin
nombrar a personas involucradas y sin prometer resultados.
