# Workflow de Actions pendiente de activar

Este archivo debe vivir en `.github/workflows/render-lote.yml`, pero el
conector de Claude **no tiene permiso para escribir workflows** (GitHub
exige el permiso "Workflows" aparte, y la app solo trae "Contents").

## Como activarlo (una sola vez, desde github.com)

1. Abrir el repo en el navegador
2. **Add file > Create new file**
3. En el nombre escribir exactamente: `.github/workflows/render-lote.yml`
4. Pegar el contenido de `render-lote.yml` (esta misma carpeta)
5. **Commit changes**

Despues cargar los Secrets en **Settings > Secrets and variables > Actions**:
`ELEVENLABS_API_KEY` y, si se usa, `HIGGSFIELD_API_KEY`.

El workflow fallara con un mensaje claro mientras `motor/render5.py` no
exista en el repo. Eso es esperado.
