# Que alcanza cada entorno

Mapa de lo verificado. Evita perder horas probando lo que ya se sabe que falla.

## Contenedor de Claude (nube)

| Destino | Estado |
|---|---|
| pypi / npm | OK |
| GitHub Releases (`objects.githubusercontent.com`) | OK |
| `api.github.com` / codeload | 403 |
| HuggingFace | 403 |
| apt | 403 |
| pixabay, freemusicarchive, incompetech, archive.org, freesound | 403 |
| CDN de Higgsfield (cloudfront, cdn.higgsfield.ai) | 403 |
| `storage.googleapis.com` (mp3 de ElevenLabs) | bloqueado para curl |
| zernio.com | bloqueado por egress |

El contenedor es **efimero**: si la sesion muere hay que reconstruirlo.
Es justamente el problema que este repo resuelve.

## Runners de GitHub Actions

**Internet sin proxy.** Todo lo de arriba funciona: pip, apt, cualquier CDN,
las APIs de ElevenLabs / Higgsfield / Artlist, y los bancos de musica libre.

Cuota en repos privados (plan Free): **2.000 minutos Linux al mes** y
500 MB de artifacts. A ~35 s por video, un lote de 100 usa ~60 minutos.
El gasto por sobre la cuota esta bloqueado por defecto (limite $0), asi
que los jobs se detienen en vez de cobrar.

Ojo con los **500 MB de artifacts**: un lote de 100 videos son ~500 MB.
Bajar el artifact y borrarlo, o publicar los mp4 como Release en vez de
artifact (las Releases no cuentan contra esa cuota).

## Mac

- `device_bash` **no borra** por defecto: hay que pedir
  `device_request_delete_permission` sobre la carpeta raiz. El usuario
  aprueba una vez y queda habilitado el resto de la sesion
- `device_bash` **no alcanza `~/Library`**. Para medir ahi hay que dejar un
  `.command` y abrirlo con doble clic
- Terminal solo se controla en **modo clic**: no se puede teclear en el.
  Por eso los `.command` van sin preguntas, con la salida a un `.log`
- Los menus desplegables de macOS pertenecen a un proceso fuera de la lista
  de apps permitidas: **no se pueden clicar, se navegan con flechas y Enter**
- El `displayName` con tilde debe ir en forma **descompuesta (NFD)**
- El panel de navegador de la app **bloquea las descargas normales**
  (`net::ERR_ABORTED`). Ver `RESCATE-ARCHIVOS.md`
- Si las `mcp__remote-devices__*` desaparecen, **`RefreshMcpTools` las
  recupera**. No dar por muerta la conexion sin intentarlo
- Los permisos de computer use se caen solos a veces: volver a llamar
  resolve + request_access
- Carpetas conectadas: `/Users/ithansnake/Movies` y `/Users/ithansnake/Downloads`.
  Carpeta de trabajo: `/Users/ithansnake/Movies/TikTok Estudio`

## Topes de transferencia

| Via | Tope |
|---|---|
| `SendUserFile` | 30 MiB por archivo |
| `device_commit_files` | 100 MB por llamada (24 archivos de 3,6 MB; 16 de 5,9 MB) |
| GitHub | 100 MB por archivo; repo recomendado < 1 GB |
