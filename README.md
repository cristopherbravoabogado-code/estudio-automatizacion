# Estudio Automatizacion

Repositorio del **Estudio Juridico San Bernardo**. Guarda el codigo, la
documentacion y los calendarios de la fabrica de contenido. No guarda videos
ni audio: eso se regenera.

## ⚠️ ESTE REPOSITORIO ES PUBLICO (verificado el 19/09/2026)

Hasta el 19/09 este archivo decia "repositorio privado". **Es falso**: la API
de GitHub responde `"private": false` y el sandbox de Higgsfield, que no tiene
credenciales de GitHub, baja cualquier archivo con HTTP 200.

Revisado ese mismo dia, **no hay datos de clientes, ni RUT, ni numeros de
causa, ni claves**: las reglas de abajo funcionaron. Lo que si esta expuesto es
la estrategia -el banco de ganchos, los analisis de que funciona, los
procedimientos-, que es la ventaja competitiva del estudio.

**No se puede hacer privado sin romper la fabrica**, porque dos cosas dependen
de que se lea sin credenciales:

1. `produce.py` baja su propio codigo desde `raw.githubusercontent.com` cuando
   corre en el sandbox (en Actions ya no: usa `PRODUCE_LOCAL`).
2. Las piezas se alojan como assets de una Release y TikTok las importa desde
   esa url publica.

El camino para cerrarlo, pendiente: un repositorio aparte y publico solo con
los mp4 -que van a TikTok de todos modos- y este privado.

## Por que existe este repo

El motor de video vivia en un contenedor efimero. Cada vez que moria la
sesion habia que reconstruirlo desde cero. Aca el codigo es permanente,
tiene historial y se puede volver atras cuando una version sale peor que
la anterior.

## Estructura

```
motor/         Generacion de video: render, ilustracion, musica, voz
publicacion/   Publicacion y programacion en TikTok
contenido/     Descripciones, guiones y calendarios (texto, no media)
mac/           Scripts .command de mantencion del Mac
docs/          Documentacion tecnica y procedimientos validados
.github/       Workflows de GitHub Actions
```

## Documentacion

| Archivo | Contenido |
|---|---|
| docs/ARQUITECTURA.md | Motores de render, musica y voz |
| docs/TIKTOK-STUDIO.md | Procedimiento validado de carga y programacion |
| docs/VOZ.md | Decisiones de voz y costos de ElevenLabs |
| docs/RESCATE-ARCHIVOS.md | Como bajar archivos de CDN bloqueados |
| docs/RED-Y-BLOQUEOS.md | Que alcanza y que no cada entorno |

## Reglas del repo

1. **Nada de media.** El `.gitignore` bloquea mp4, mp3, wav y modelos pesados.
2. **Nada de claves.** Zernio, ElevenLabs, Higgsfield y Artlist van en
   GitHub Secrets, nunca en un archivo.
3. **Nada de datos de clientes.** Secreto profesional. Los modelos de
   escritos que se suban van sin nombres, RUT ni numeros de causa.
4. **Un commit por cambio real**, con mensaje que diga que se cambio y por que.
