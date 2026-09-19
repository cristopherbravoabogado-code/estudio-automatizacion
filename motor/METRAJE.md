# De dónde sale el metraje (medido el 19/09/2026)

Cristopher: *"lo ideal es que el clip sea de la noticia y todo el rato se esté mostrando"*.
Es la petición correcta. Este documento dice qué se probó, qué sirve y qué no, para que nadie
vuelva a gastar una tarde en los callejones ya recorridos.

## Primero, un dato que corrige la memoria del proyecto

**Nunca hubo extracción de YouTube.** Se revisaron los 95 commits del repositorio: `yt-dlp` no
aparece nunca y `youtube` aparece solo en la especificación de tareas, donde se usaba para
**elegir el tema** (búsqueda y número de vistas), jamás como fuente de imágenes. Los clips
siempre salieron de **Mixkit**, un banco de video gratis — por eso se ven genéricos: lo son.

Y ya estaba anotado en el propio repo, el 07/09: *"yt-dlp ya no descarga de YouTube desde el
sandbox — Sign in to confirm you're not a bot"*. O sea, descargar de YouTube se intentó entonces
y ya había dejado de funcionar.

## Lo que se midió el 19/09

| Fuente | Resultado |
|---|---|
| `pjud.cl`, `fiscaliadechile.cl`, `senado.cl`, `tv.senado.cl`, `pdichile.cl` | HTTP 200, pero **cero** `.mp4` y cero `.m3u8` en el HTML |
| `camara.cl` | 403 al datacenter |
| `prensa.presidencia.cl`, `dt.gob.cl` | fallan TLS: el servidor no manda el intermedio de Sectigo (mala configuración de ellos, no un problema de seguridad) |
| Wikimedia Commons | **sirve video real, descargable, con licencia legible por máquina** |

**La conclusión incómoda:** las instituciones chilenas no publican archivos de video
descargables. Publican en **YouTube**. Así que "metraje real de fuentes que permiten reuso"
desemboca, en la práctica, otra vez en YouTube.

## Lo que sí sirve

**Wikimedia Commons.** Devuelve video real con licencia explícita y atribución obligatoria, y
tiene material chileno oficial (p. ej. una presentación de reforma al Código Procesal Penal bajo
**CC BY 3.0 cl**). Limitaciones medidas: la cobertura de la noticia chilena del día es delgada
—"carabineros chile" no devuelve nada— y algunos archivos pesan más de 1 GB.

Sirve como fuente **complementaria y honesta**, no como el sustento de diez piezas diarias.

## Lo que no se hace, y por qué

No se descarga metraje de los canales desde YouTube. No es una duda técnica: es material con
derechos de terceros, republicado bajo la marca de un estudio jurídico. El expuesto sería
Cristopher, que es el que tiene el título.

## La regla del módulo

Un clip **no entra** a una pieza sin tres datos anotados: **de dónde salió, con qué licencia y a
quién hay que acreditar**. Sin eso, el control lo rechaza. Es la misma doctrina de `control.py`:
un control que se apaga por omisión no es un control. Y aquí tiene una razón extra: la atribución
no es burocracia, es literalmente la condición de la licencia CC BY.

## Cómo lo lleva una pieza

La pieza puede traer un objeto `metraje`. Si lo trae, **manda sobre el crédito del estudio**:

```json
"metraje": {
  "url": "https://upload.wikimedia.org/.../Archivo.webm",
  "licencia": "CC BY 3.0 cl",
  "atribucion": "Dirección de Prensa, Presidencia de la República de Chile",
  "fuente": "Wikimedia Commons"
}
```

En pantalla sale `Dirección de Prensa, Presidencia de la República de Chile / Wikimedia Commons
(CC BY 3.0 cl)`, en el lugar donde antes iba el nombre del estudio.

`produce.py` **no renderiza** una pieza cuyo `metraje` no traiga los tres campos. No es una
validación de formato: es que un clip prestado sin acreditar incumple la licencia con la que se
tomó, y eso lo firma el estudio.

## Lo que esto NO resuelve

El clip **del hecho concreto de cada día** —ese control carretero, esa audiencia— no está en
Commons ni en las páginas institucionales. Para eso hay una sola vía limpia: **licenciar agencia**
(ATON o AgenciaUno en Chile; AP, Reuters o Getty fuera). Cuesta dinero y se contrata a nombre del
estudio. El módulo queda preparado para recibir esa fuente el día que exista contrato.

Mientras tanto, lo honesto es la combinación que ya rinde: **placa con el titular real citado a su
medio** + metraje temático con licencia + el gancho en los primeros segundos.

## La entrada de clips de prensa (`motor/crudo.py`)

Cristopher consigue el clip y anota cuatro datos. De ahí en adelante la cadena sigue sola.

```
python3 motor/crudo.py agregar --slot 3 \
    --url "https://.../clip.mp4" \
    --fuente "24 Horas" --titulo "Balance de Fiestas Patrias" --segundos 7
```

- Si la ranura ya está encolada, el clip se pega ahí mismo.
- Si todavía no existe, queda en `crudo/<fecha>.json` y `crudo.py aplicar` lo pega cuando la
  tarea de la noche escriba la cola.
- `crudo.py revisar` dice qué piezas del día llevan clip de prensa y cuáles no.

**No se guarda el video.** Regla del repositorio: nada de media. Se guarda la URL y la cita.

### El recorte se aplica, no se declara

`--segundos 7` no es una promesa: `produce.py` corta el clip a esos segundos con ffmpeg, y nunca
por encima del tope. Un número en un JSON no recorta nada; si el clip original durara 40 s y nadie
lo cortara, la pieza publicaría 40 s de obra ajena con un `"segundos": 7` al lado.

### El tope lo decide el abogado, no el programa

El art. 71 B dice "fragmentos breves" y no da un número. El tope por defecto son 8 s y se mueve
con `--tope`. Lo que aporta el programa no es saber cuánto es breve: es que la decisión se tome
una vez y se cumpla igual en las diez piezas del día, incluso a las cuatro de la mañana.

## La vía autosuficiente: fotografía real animada (19/09/2026)

Cristopher, después de ver la entrada manual: *"no es la idea, la idea es que sea autosuficiente"*.
Tenía razón. Una entrada que él tiene que llenar todos los días es el mismo problema que
arrastrábamos desde el principio, con otra cara.

**Lo que lo desbloqueó fue mirar fotografía en vez de video.** Medido sobre los temas reales del
día:

| | candidatos con licencia usable |
|---|---|
| video | 1 de 3 búsquedas |
| **fotografía** | **8 de 8 búsquedas** |

Carabineros, Poder Judicial, Corte Suprema, Congreso, PDI, Fiestas Patrias, carretera, Dirección
del Trabajo: las ocho devolvieron material. Así que una pieza sin clip propio se arma con
**fotografía real con licencia, animada con zoom lento**, que el render busca solo a partir del
titular. Nadie consigue nada.

Una foto del frontis de la Corte Suprema ocupando la pantalla **es** la noticia. Un clip genérico
de un martillo de juez no lo es.

`clips` dejó de ser obligatorio en `cola.py`: era el último eslabón que obligaba a un humano a
conseguir metraje. A cambio, sin clips se exige un **titular de 15 caracteres o más**, porque es
lo que el render usa para buscar: un titular vago da fotos vagas.

### El límite honesto

La **licencia** se filtra sola; la **pertinencia** no. En la prueba, "Dirección del Trabajo Chile"
devolvió un logo sin relación. El filtro garantiza que se *puede* usar, no que sirva. Con menos de
dos fotos útiles la pieza se para y lo dice: una sola foto no es una pieza, es una diapositiva.

Y algo que no se verificó: **el resultado no se ha mirado con ojos humanos.** Se comprobó que son
1920x1080, 30 fps, 12,03 s y tres fotogramas distintos —o sea que el concat no colapsó— pero el
proxy del contenedor no deja traer la imagen para verla. Queda pendiente mirar la primera pieza real.
