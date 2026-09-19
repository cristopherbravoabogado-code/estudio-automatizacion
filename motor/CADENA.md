# CADENA — el libro de cuentas del día (19/09/2026)

Compañero de `motor/PRODUCIR.md` (cómo se hace una tanda) y `motor/PUBLICAR.md` (cómo sale al
aire). Este archivo explica **quién lleva la cuenta** de que el día se cumpla.

## El defecto que cierra

Al 19/09/2026 el estudio publicaba 1 o 2 piezas los días que debía publicar 6. La lectura de
tareas de esa mañana:

```
SB 06:00 — Producción del día ........ ABANDONED
M8 10:00 — Verificación legal ........ ABANDONED
```

Ninguna pieza de código estaba mala. El defecto era que **nada en el sistema sabía cuántas
piezas debía tener el día ni en qué estado iba cada una**. Cada rutina lo deducía de nuevo
preguntándole a Metricool, a Higgsfield y al repo; y cuando una tarea larga moría a la mitad
—y morían— el trabajo hecho se perdía sin dejar rastro, porque `resultado.json` y `urls/<id>.txt`
viven en el sandbox y mueren con él.

El número de videos del día no era una decisión: era el resultado de si una sesión larga alcanzó
a terminar. `motor/cadena.py` lo convierte en una decisión.

Es la misma doctrina de `control.py` un piso más arriba. Aquel cerró la puerta que fallaba
abierta en la **pieza**; éste la cierra en el **día**: un paso sin sus datos no se anota, una
pieza que `control.py` reprobó no se puede marcar renderizada, y una pieza ya publicada no se
vuelve a publicar.

## Las tres propiedades

1. **El estado vive fuera de la sesión**, en `estado/<fecha>.json`, versionado en git. Una tarea
   que muere deja escrito lo que alcanzó a hacer; la siguiente sigue desde ahí.
2. **Las tareas pueden ser cortas de verdad.** `tareas/INDEX.md` ya había deducido la regla
   —"tareas cortas, un solo trabajo, reporte de 3 líneas"— pero una tarea corta que no puede
   consultar ni dejar estado tiene que releer el mundo entero para saber qué hacer, y deja de
   ser corta. Ahora `resumen` da el reporte y `siguiente` dice el único trabajo que toca.
3. **El antidoble es código, no prosa.** Vivía como regla escrita en
   `/areas/tiktok-programacion.md`. Con cuota de 13 publicaciones/24 h en la vía B, una
   republicación por descuido cuesta una pieza real del día.

## La cadena

```
vacio → tema → derecho → guion → renderizado → alojado → [programado] → publicado
```

`programado` es el único paso opcional: la vía B (Higgsfield) publica al momento y no pasa por
él; la vía A (Metricool) sí. Solo se avanza hacia adelante. Para volver atrás: `fallar` y
`reintentar`, que dejan la vuelta anotada en la historia de la pieza.

Cada paso exige sus datos, y sin ellos **no se anota**:

| Paso | Exige | Por qué |
|---|---|---|
| `tema` | `tema`, `fuente` | una noticia sin fuente no es noticia |
| `derecho` | `norma`, `articulo`, `frase` | `PRODUCIR.md` paso 1: el derecho se verifica **antes** del guion |
| `guion` | `gancho`, `tramos` | los 5 tramos de la regla dura 1 |
| `renderizado` | `control` con `pasa: true` | LA PUERTA. Si `control.py` reprobó, no se anota |
| `alojado` | `url` | sin URL no hay qué publicar. Desde el 19/09 la pone el workflow: sube el mp4 como asset de una Release de GitHub y la url es corta, pública y sin caducidad. Antes la pieza traía una `upload_url` presignada de Higgsfield de ~2.400 caracteres que **una sesión copiaba a mano**: diez piezas al día eran 24.000 caracteres transcritos sin un solo error |
| `programado` | `trigger_id`, `hora_utc` | para poder cancelar y para el antidoble |
| `publicado` | `publish_id` | solo `PUBLISH_COMPLETE` cuenta |

## Lo que corre cada rutina (tres líneas, siempre las mismas)

```bash
python3 motor/cadena.py resumen      # dónde va el día
python3 motor/cadena.py siguiente    # el único trabajo que toca ahora
# ...hacer ese trabajo...
python3 motor/cadena.py marcar <n> <estado> --campo k=v
```

Y al terminar, **commit del `estado/<fecha>.json`**. Si no se commitea, el estado muere con el
contenedor y volvemos al problema original.

Comandos de vigilancia:

```bash
python3 motor/cadena.py auditar      # discrepancias; código 1 si hay alguna
python3 motor/cadena.py reserva      # piezas alojadas sin publicar; código 1 si son < 3
```

## Las diez ranuras

`07:00 · 09:00 · 11:00 · 12:30 · 14:00 · 15:30 · 17:00 · 19:00 · 21:00 · 22:30` (hora de Chile).

Repartidas parejo a propósito. La rev. 12 del archivo cerebro cerró **H-12: lo que separa una
pieza de 150 vistas de una de 5.000 es el TEMA, no el formato, ni la voz, ni la hora.** Optimizar
una franja sería optimizar una variable que los datos no sostienen.

## El tope que hay que mirar con 10 diarias

`motor/PUBLICAR.md` mide la cuota de la vía B: **13 publicaciones por 24 h**. Con meta de 10
quedan **3 reintentos para todo el día**. `cadena.py abrir` lo avisa al abrir el día. Si un día
se gastan los 3 reintentos, la pieza 11 no sale aunque esté lista: no es un error del sistema,
es la cuota de TikTok.

## Lo que este archivo NO resuelve

Lleva la cuenta; no produce. Mientras el render siga corriendo dentro de una llamada
`sandbox_exec` de 3 piezas por vez —tope fijado por los 16.000 caracteres del comando y los
~2.400 que mide cada `upload_url` presignada (`PRODUCIR.md`)— diez piezas diarias son cuatro
llamadas encadenadas dentro de una sesión que puede morir. La diferencia es que ahora, cuando
muera, se sabe exactamente en qué ranura quedó y la siguiente tarea retoma ahí.

Mover el render a GitHub Actions (internet sin proxy, 2.000 minutos/mes, sin tope de caracteres
en el comando — ver `docs/RED-Y-BLOQUEOS.md`) es el paso que quita la sesión del camino crítico.
Queda pendiente y necesita dos cosas que el conector de Claude no puede hacer solo: crear
`.github/workflows/` desde github.com y cargar los Secrets.
