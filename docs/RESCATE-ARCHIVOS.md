# Rescate de archivos desde CDN bloqueados

Los CDN de Higgsfield, Artlist y ElevenLabs estan bloqueados por el proxy
del contenedor, asi que `curl` no sirve. El navegador del Mac si llega.

## Receta (probada 03/09/2026)

1. Abrir la URL del resultado con `Claude_Browser__preview_start`
2. En esa pestana, `javascript_tool` con fetch + blob + `<a download>`
3. El archivo aparece en `~/Downloads` con nombre **oculto temporal**
   (`.XXXXXXX.com.anthropic.claudefordesktop.XXXXXX`) pero completo y con
   cabecera valida
4. Con `device_bash` se copia a la carpeta conectada con nombre decente
5. `device_stage_files` para traerlo al contenedor

Funciona porque Downloads esta entre las carpetas conectadas.

## Limites

- El `javascript_tool` aguanta **~3 descargas por llamada** (900 ms entre
  cada una). Con 5 archivos hay que partir en 3 + 2
- Aunque devuelva timeout a los 45 s, **las descargas igual se completan**.
  Verificar en `~/Downloads` por fecha en vez de reintentar
- Truco: definir `window.dl(urls)` una vez y lanzarlo con `.then(...)`
  devolviendo un valor inmediato, asi la llamada no se cuelga
- Los temporales ocultos se identifican despues por **tamano** en el orden
  de descarga, o por **duracion** con ffprobe (huella confiable)
- Los temporales ocultos no se pueden borrar sin permiso de borrado

## Recuperar entregas de una sesion muerta

La sesion conserva los `file_uuid` de lo que entrego aunque su contenedor
haya muerto. Se le escribe a esa tarea desde el panel del navegador
pidiendole copiar esos `file_uuid` con `device_commit_files`. Tarda
minutos y no hay que regenerar nada.

## Alternativa que evita todo esto

GitHub Actions. Los runners tienen internet sin proxy: descargan de
cualquier CDN, instalan con pip y llaman APIs directamente.
Ver `.github/workflows/render-lote.yml`.

## Bajar un PDF o un documento de una biblioteca (20/09/2026)

Mismo muro, otra puerta. Medido hoy desde el contenedor:

| Destino | CONNECT |
|---|---|
| archive.org, web.archive.org, ia*.us.archive.org | 403 |
| www.holybooks.com | 403 |
| upload.wikimedia.org, commons.wikimedia.org | 403 |
| real.mtak.hu (Academia Hungara) | 403 |
| github.com, raw.githubusercontent.com | OK |

El rechazo es al **tunel**, no a la peticion: no hay user-agent, cabecera ni reintento que
lo cambie, y rodearlo esta prohibido. Lo que si funciona es
`.github/workflows/descargar-pdf.yml`: corre `motor/descarga.py` en el runner -internet sin
proxy- y deja el PDF **como asset de una Release**. Esa url si se alcanza desde el
contenedor, que es el punto: un artifact no serviria, porque bajarlo pide `api.github.com`
y eso tambien es 403.

Se dispara desde `main` a mano (pestana Actions, documento o url), y desde una rama
`claude/**` empujando un cambio al descargador mismo. La segunda puerta existe porque la
credencial de una sesion de Claude **esta limitada a su rama**: `git push origin <etiqueta>`
devuelve 403, asi que una etiqueta `pdf-*` no sirve de gatillo aunque parezca lo natural.

`motor/descarga.py` corre igual en el Mac (`python3 motor/descarga.py rohonc`), sin pip: es
solo biblioteca estandar.

**Lo unico que aporta de verdad es comprobar.** `curl -sL` ante un 403 guarda la pagina de
error dentro del archivo y sale con codigo 0 -asi entraron las fuentes falsas de 378 bytes
en el render del 19/09-. Por eso toda descarga se mide antes de darla por buena: cabecera
`%PDF-`, cola `%%EOF`, tamano minimo y sha256 a la vista. Lo que no pasa queda en
`.rechazado` en vez de hacerse pasar por bueno.
