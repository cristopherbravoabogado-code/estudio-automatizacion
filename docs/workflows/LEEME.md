# Workflows de GitHub Actions

## Estado al 19/09/2026

| Archivo | Situación |
|---|---|
| `.github/workflows/render-diario.yml` | **Instalado y activo.** Renderiza la tanda del día y anota el resultado en `estado/<fecha>.json`. Ver `motor/CADENA.md`. |
| `render-lote.yml` (esta carpeta) | **Obsoleto.** Llama a `motor/render5.py`, que no existe: era del motor viejo. Se conserva como referencia del arranque manual por lotes. |

## Corrección al aviso anterior

Este archivo decía que el conector de Claude **no puede escribir workflows**, porque GitHub
exige el permiso "Workflows" aparte y la app solo trae "Contents". Eso es cierto para el
conector de GitHub de los chats, pero **no** para Claude Code: desde una sesión de Claude Code
el push va por git normal y GitHub lo aceptó sin problema (medido el 19/09/2026, empujando un
workflow de prueba y borrándolo después).

O sea: los archivos de workflow se pueden crear y modificar desde una sesión. Lo que sigue
necesitando manos es cargar los **Secrets**, que no viajan por git a propósito.

## Secrets que hay que cargar (una sola vez)

En **Settings > Secrets and variables > Actions > New repository secret**:

| Secret | Para qué | ¿Hace falta hoy? |
|---|---|---|
| `ELEVENLABS_API_KEY` | voz de ElevenLabs | Solo si se vuelve a esa voz. El motor usa **Kokoro**, que corre local y no necesita clave. |
| `HIGGSFIELD_API_KEY` | clips de gancho | Opcional. Los ganchos salen hoy de mixkit, que es abierto. |

`GITHUB_TOKEN` no se carga: Actions lo inyecta solo, y el workflow ya declara
`permissions: contents: write` para poder commitear el estado de vuelta.

**Si no cargas ninguno, el render diario igual corre**: la voz Kokoro y los clips de mixkit no
piden credenciales. Los Secrets son para las vías alternativas.
