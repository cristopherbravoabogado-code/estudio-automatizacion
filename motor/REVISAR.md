# REVISAR — cómo una revisión mira el estado de las tareas sin ahogarse (17/09/2026)

Compañero de `motor/PRODUCIR.md` (cómo se hace una tanda) y `motor/PUBLICAR.md` (cómo sale al
aire). Este archivo trata **el primer paso de toda revisión SB**: saber qué tareas corrieron, qué
quedó colgado y qué hay en la cola.

## La regla

> **Ninguna revisión llama `mcp__claude-code-remote__list_triggers` directamente.**
> La llama un subagente, que devuelve una tabla compacta.

## Por qué

`list_triggers` devuelve **el prompt entero de cada tarea**. Con 35 tareas eso son ~360.000
caracteres. Toda revisión SB empieza llamándolo, así que toda revisión SB arranca metiéndose
360.000 caracteres en el contexto **antes de haber hecho nada útil** — y después tiene que
producir cuatro piezas, controlarlas, subirlas y escribir en memoria.

El patrón calza con lo que se ve en los estados:

| Revisión | Qué hace | Estado al 17/09 |
|---|---|---|
| SB 12:00 | mira y corrige | SUCCEEDED |
| SB 15:00 | produce **una** pieza | SUCCEEDED |
| SB 06:00 | produce **el día entero** | ABANDONED, 8 días seguidos |
| SB 19:00 | cierra el día + métricas | PENDING sin `finished_at`, 5 días |
| SB 00:00 | auditoría + cola de mañana | ABANDONED 3 días, cerró el 17/09 |

Las que hacen poco cierran; las que hacen mucho, no. El volcado de `list_triggers` es carga fija
que pagan todas por igual, y es la primera que se puede sacar sin perder información.

## Medido el 17/09/2026

La auditoría de esa madrugada lo hizo con un subagente en vez de llamarlo de frente:

- respuesta de `list_triggers`: **~360.000 caracteres** (35 tareas, una sola página, `has_more:false`)
- lo que volvió al contexto de la revisión: **~4.000 caracteres** — la tabla, el estado de las cinco
  SB, las tareas de un disparo pendientes y el conteo
- **98,9 % menos**, con el mismo dato útil

Ese fue el trabajo entero del primer paso, y la revisión siguió con contexto para producir.

## El procedimiento

1. Lanzar el subagente (`Agent`, tipo `general-purpose`) con el prompt de abajo.
2. Trabajar con la tabla que devuelve.
3. Si hace falta el prompt de UNA tarea concreta (por ejemplo para reescribirlo), pedírselo al
   mismo subagente con `SendMessage` — él ya tiene el volcado y devuelve solo ese prompt.

### Prompt exacto del subagente

```
Tarea acotada y de solo lectura. NO escribas en memoria, NO crees ni modifiques tareas,
NO publiques nada.

1. Carga el esquema con ToolSearch: `select:mcp__claude-code-remote__list_triggers`.
2. Llama `mcp__claude-code-remote__list_triggers` con `limit: 100` (y pagina con `cursor`
   si viene `next_cursor`). OJO: la respuesta es enorme (~360.000 caracteres, incluye el
   prompt entero de cada tarea). NO la copies en tu respuesta.
3. Devuélveme SOLO una tabla compacta, sin ningún prompt, una línea por tarea habilitada:
   `id | nombre | cron o run_once_at | enabled | next_run_at | last_run.status |
    last_run.fired_at | last_run.finished_at`
4. Además tres listas cortas:
   - SB: las tareas cuyo nombre empieza con "SB " (revisiones de 00:00, 06:00, 12:00,
     15:00 y 19:00), con su last_run.
   - ONE-SHOTS PENDIENTES: tareas con `run_once_at` futuro y habilitadas — id, nombre,
     run_once_at. Si el nombre contiene "Publicar", dilo explícitamente.
   - CONTEO: total, habilitadas, deshabilitadas.

Sé literal: no inventes ni completes campos ausentes; si falta uno, escribe "—".
Tu respuesta final debe caber en menos de 120 líneas.
```

## Lo que NO arregla

Esto baja la carga de entrada de la revisión. **No** prueba que ese fuera el único motivo por el
que SB 06:00 y SB 19:00 se cuelgan, y no hay que darlo por probado hasta ver a las dos cerrar
varios días seguidos. Si siguen colgándose con el contexto liviano, la vía siguiente ya está
escrita en la bitácora: **partirlas en dos revisiones más cortas**, porque lo enfermo es el cierre
de las tareas largas, no la publicación.

## Regla general que se desprende

**Una herramienta que devuelve el prompt de otras tareas es una bomba de contexto.** Antes de
llamar cualquier tool de listado desde una tarea que además tiene que producir, preguntarse
cuánto devuelve; si no se sabe, delegarla. El dato que la revisión necesita casi nunca es el
volcado: son diez líneas.
