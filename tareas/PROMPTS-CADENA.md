# Los prompts de la cadena diaria (19/09/2026)

Cadena de 10 piezas de noticia al día. Reemplaza al diseño del 11/09, en que una tarea larga
hacía el día entero y, cuando abandonaba, se llevaba el día con ella.

**La regla de diseño, ahora sí ejecutable:** una tarea es corta cuando no tiene nada que
averiguar. Un prompt breve que obliga a leer el estado, decidir qué pieza toca y buscar su URL
es una tarea larga con un prompt breve. Por eso cada prompt de abajo empieza corriendo un
comando que le dice exactamente qué hacer.

## El día, de un vistazo

| Hora Chile | Quién | Qué |
|---|---|---|
| 19:00 | **T1-NOCHE** (Claude) | Encola las ranuras 1–5 de mañana |
| 05:00 | Actions | Renderiza las ranuras 1–5 |
| 08:00 | **T1-MAÑANA** (Claude) | Encola las ranuras 6–10 con la noticia fresca |
| 09:00 | Actions | Rescate: renderiza lo que quedó de la mañana |
| 13:00 | Actions | Renderiza las ranuras 6–10 |
| 17:00 | Actions | Rescate final |
| cada hora | **T2-PUBLICAR** (Claude) | Publica lo que esté vencido y sin publicar |
| cada 3 h | **T3-VIGILANTE** (Claude) | Audita y avisa; no produce |

Las ranuras salen a las 07, 09, 11, 13, 15, 17, 19, 20, 21 y 22 de Chile.

---

## T1-NOCHE — encolar mañana (19:00 Chile · cron `0 22 * * *`)

```
Encola las ranuras 1 a 5 de MAÑANA en el repo estudio-automatizacion (rama main).

1. git pull. Corre: python3 motor/cadena.py abrir --meta 10 --fecha <mañana>
2. Elige 5 noticias jurídicas chilenas del día de hoy. Para cada una, VERIFICA el derecho
   contra LeyChile ANTES de escribir el guion (motor/PRODUCIR.md paso 1): necesitas idNorma,
   artículo y una frase textual del articulado.
3. Para cada pieza pide una upload_url con media_upload de Higgsfield, escribe el JSON de la
   pieza (el formato está en el docstring de motor/cola.py) y encólala:
       python3 motor/cola.py agregar --slot N --archivo pieza.json --fecha <mañana>
   Si cola.py rechaza la pieza, ARREGLA lo que te dice y vuelve a llamar: ninguno de sus
   reproches cuesta un render, todos se ven en el texto.
4. Al final: python3 motor/cola.py revisar --fecha <mañana>
5. git add cola/ estado/ && git commit && git push.

Si te alcanza el tiempo para 3 piezas y no para 5, encola 3 y termina. Tres encoladas valen
más que cinco a medio hacer: el rescate de las 09:00 no puede recuperar lo que no quedó escrito.
Reporte: 3 líneas.
```

## T1-MAÑANA — encolar la tarde (08:00 Chile · cron `0 11 * * *`)

```
Encola las ranuras 6 a 10 de HOY en el repo estudio-automatizacion (rama main).

Igual que T1-NOCHE pero con la noticia fresca de esta mañana, y con --fecha de hoy.
Empieza por: git pull && python3 motor/cadena.py resumen

Si el resumen dice que ya hay piezas en las ranuras 6-10, no las toques: encola solo las que
estén en 'vacio'.

Las piezas de reacción a un titular van con "prensa": true, que las exime del banco de ganchos
(su gancho es el titular). Las demás tienen que usar un gancho de motor/ganchos/cola.json.
Reporte: 3 líneas.
```

## T2-PUBLICAR — cada hora (cron `0 * * * *`)

```
Publica lo que esté vencido en el repo estudio-automatizacion (rama main).

1. git pull && python3 motor/publicar.py listo
2. Si dice "nada vencido para publicar": TERMINA AHÍ. No produzcas, no revises, no audites.
   Responde una línea y cierra.
3. Si hay ranuras para publicar, para CADA UNA:
       python3 motor/publicar.py ficha N
   Sigue los cuatro pasos que imprime, tal como los imprime.
   Al terminar: python3 motor/cadena.py marcar N publicado --campo publish_id=<id>
   Si falla:   python3 motor/cadena.py fallar N --motivo "<lo que dijo TikTok>"
4. git add estado/ && git commit && git push.

Si la ficha dice ALTO, esa pieza ya salió: NO la vuelvas a publicar. Con cuota de 13/24 h una
republicación por descuido cuesta una pieza real del día.
Reporte: 3 líneas.
```

## T3-VIGILANTE — cada 3 h (cron `4 */3 * * *`)

```
Audita el día en el repo estudio-automatizacion (rama main). NO produces ni publicas.

1. git pull
2. python3 motor/cadena.py auditar
3. python3 motor/cadena.py reserva
4. python3 motor/publicar.py cupo

Si las tres salen limpias, responde UNA línea: "día <fecha>: N/10, sin discrepancias" y cierra.

Si hay discrepancias, escríbelas tal cual y di cuál es la siguiente acción concreta. No la
ejecutes: para eso están las otras tareas. Tu trabajo es que nadie pueda decir "no sabíamos".

Excepción, la única: si hay una ranura ALOJADA y vencida hace más de 2 horas y la tarea horaria
no la publicó, publícala tú con motor/publicar.py ficha N. Eso es lo que significa que el
vigilante tape huecos.
```

---

## Por qué una tarea horaria y no diez de un disparo

El diseño del 11/09 creaba una tarea de un solo disparo por pieza. Funcionaba, pero tenía dos
costos: había que crear diez tareas cada día —y si la tarea que las crea abandona, no se crea
ninguna—, y si una fallaba a su hora, nadie reintentaba.

Una sola tarea horaria que publica lo vencido no se crea nunca de nuevo, y la corrida de la hora
siguiente reintenta sola lo que la anterior no alcanzó. El antidoble que impide publicar dos
veces la misma pieza ya no es una promesa: está en `cadena.py` y sale con código 2.

Las tareas de un disparo siguen sirviendo para una pieza fuera de grilla (una reacción a un
titular que tiene que salir a una hora exacta). `python3 motor/publicar.py plan` las lista.
