# TikTok Studio: procedimiento validado

> Validado el 31/08/2026 con 10 videos seguidos sin caidas, y de nuevo el
> 01/09/2026 con 27 videos desde el Mac.

## Limites que condicionan todo

- El programador de TikTok Studio agenda **solo 10 dias adelante**. A 7
  diarios son ~70 videos por sesion de carga
- **Las publicaciones programadas no se pueden editar.** Mensaje textual
  de TikTok: "Las publicaciones programadas no se pueden editar". Para
  cambiar algo hay que eliminarlas y volver a subir el archivo
- Un video subido por **carga masiva no puede llevar musica de TikTok**.
  Solo los de BORRADORES (subidos de a uno) pasan por el editor de tijeras
- **Solucion de raiz aplicada**: la musica va DENTRO del mp4. Asi la carga
  masiva sirve y nunca mas depende del editor de TikTok
- **De a 10 videos por tanda.** Con 30 la pagina colapsa

## Los 10 pasos

1. **JS solo para ubicar**: `[...document.querySelectorAll('[contenteditable="true"]')]`
   devuelve uno por fila; su `innerText` es el nombre del archivo. Subir
   por `parentElement` hasta el nodo que contenga `[class*="task-operation"]`.
   `row.scrollIntoView({block:'center'})` deja la descripcion en y~263
2. **Clic real** sobre `[class*="caption-text-content"]` -> se despliega el
   cuadro con contador n/4000
3. **cmd+a** (Mac) o ctrl+a (Windows), luego Backspace, luego UNA sola
   accion `type` con la descripcion completa, saltos de linea incluidos.
   Los emoji pasan sin problema
4. **Escape** para cerrar el panel de sugerencias de hashtags
5. **Clic real** en la flecha rosada de confirmar. Toast
   "La descripcion se ha actualizado"
6. Reubicar la fila para la hora: el selector se abre HACIA ARRIBA y
   necesita ~305 px libres (o hacia abajo si la fila esta en la mitad
   superior; mirar con screenshot y recalcular)
7. **Clic real** en `[class*="input-value-text"]` -> calendario + columnas de hora
8. El **dia se elige con clic real** (`.click()` por JS NO funciona en el calendario)
9. La **hora si se elige por JS**: `.tiktok-timer-left` son las horas y
   `.tiktok-timer-right` los minutos (de 5 en 5). Funcionan aunque esten
   fuera de la vista
10. **Clic real** en el boton Programado. Toast "La programacion se ha actualizado"

Nada queda programado de verdad hasta pulsar **Publicar (N)**.

## Trampas verificadas

| Trampa | Consecuencia |
|---|---|
| Escribir la descripcion por JS (`execCommand('insertText')`) | **Destruye el estado de React.** La pagina cae en "Hubo un problema" y la cola entera se pierde. Solo pulsaciones reales |
| Usar el numero de fila | La lista **se reordena sola** entre acciones. Buscar siempre por texto |
| El lapiz de la columna Accion | Abre la ficha y **borra todas las descripciones ya escritas** |
| ctrl+a en Mac | El select-all no ocurre: el texto se inserta al inicio y el nombre del archivo queda pegado al final |
| Hora con menos de 15 min de antelacion | "Guardar y volver a la lista" queda desactivado |
| `javascript_tool` dentro de `browser_batch` | El batch entero falla. El JS va en llamadas propias |
| `outerHTML` en el JS de la extension | Devuelve "[BLOCKED: Cookie/query string data]". Devolver solo texto y medidas |
| Recargar la pestana con la cola cargada | Vacia la cola y hay que arrastrar todo de nuevo |

## Verificacion

La lista de contenido es **virtualizada** y muestra ~7 filas a la vez.
Hay que scrollear y sumar los tramos para contar bien.

## Reglas de seguridad

- Claude NO aprieta confirmaciones de borrado irreversible. Esos borrados
  los hace Cristopher
- Preferir siempre programar a futuro antes que publicar inmediato

## Plantilla de descripcion (~530 caracteres)

```
[Gancho en segunda persona, sobre un problema concreto]

[1 parrafo de valor]

Siguenos: si nos sigues, tu 1a consulta PRESENCIAL es gratis
WhatsApp +56 9 9690 5994
defensapenalsanbernardo.cl
Reserva tu hora en el link de la bio

Estudio Juridico San Bernardo
Informacion general, no reemplaza asesoria para tu caso.

[8 hashtags de la materia]
```

Cada linea del bloque de CTA lleva su emoji (estrella, celular, globo,
dedo hacia arriba). Los ganchos de pregunta de dolor rinden ~23% mas que
las introducciones genericas.

## Calendario vigente

Lote 4 (701-800): 3 publicaciones diarias a las 13:00, 18:30 y 21:15
hora de Chile, intercaladas por materia, del 05/09 al 08/10/2026.
