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
