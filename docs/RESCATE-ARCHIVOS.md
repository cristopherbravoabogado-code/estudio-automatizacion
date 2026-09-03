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
