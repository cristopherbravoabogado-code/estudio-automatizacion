# publicacion/

Scripts de publicacion y programacion en TikTok.
Procedimiento manual validado en `docs/TIKTOK-STUDIO.md`.

## Archivos esperados

```
publicar.ps1       cliente de la API de Zernio (Windows). Modo -Automatico
                   programa solo huecos futuros, nunca publica inmediato
```

## Estado de las vias de publicacion (03/09/2026)

| Via | Estado |
|---|---|
| TikTok Studio carga masiva + extension Chrome | **La que funciona.** Cristopher arrastra, Claude llena descripcion y hora |
| Zernio plan gratis (Direct Post) | Falla con "at capacity" en inmediato Y programado. `draft:true` si funciona |
| Upload-Post Basic | Alternativa de pago (13 EUR/mes anual). No probada |
| Higgsfield tiktok_publish | Existe, no probada |

TikTok bloquea la carga automatizada de archivos. El llenado de formularios
si funciona.
