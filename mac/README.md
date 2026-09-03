# mac/

Scripts `.command` de doble clic para el Mac. Se usan porque Terminal solo
se puede controlar en modo clic desde Claude y `device_bash` no alcanza
`~/Library`.

Regla: **sin preguntas interactivas**, con la salida a un `.log` en la
carpeta conectada para poder leerla despues.

## Archivos esperados

```
1-LIMPIAR-CLAUDE.command        limpia solo la cache de Claude
2-OPTIMIZAR-MAC.command         diagnostica y pregunta antes de borrar
3-LIMPIAR-AHORA.command         limpia sin preguntar, deja limpieza.log
5-DONDE-ESTA-EL-ESPACIO.command desglose del disco incluyendo ~/Library
6-DETALLE-CLAUDE.command        que pesa dentro de Application Support/Claude
7-LIBERAR-ESPACIO.command       libera lo seguro
1-GENERAR-VOCES.command         voces del sistema para el lote 3 (obsoleto)
```

## Lo que se sabe del disco (02/09/2026)

- `~/Library/Application Support/Claude` = 11 GB, de los cuales 10 GB son
  la VM local de Cowork (rootfs.img). Se regenera si se borra
- `/Library/Caches/com.microsoft.autoupdate.fba` = 3 GB de instaladores
  de Office ya usados. Borrado seguro, pide contrasena de administrador
- Google Chrome duplicado en Aplicaciones (2,2 GB)
- El cuello de botella del Mac es la RAM (8 GB), no el disco
