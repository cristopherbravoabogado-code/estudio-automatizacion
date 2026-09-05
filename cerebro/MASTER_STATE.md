# MASTER_STATE — Estudio Jurídico San Bernardo

> Archivo cerebro. Se ACTUALIZA, no se reescribe. La fuente de verdad es la copia de Google Drive (carpeta Cerebro); esta copia de GitHub lista los cambios de cada revisión.
> Revisión vigente: **rev. 9**, 5 de septiembre de 2026, 17:30 Chile — RADAR GLOBAL de tendencias del día.

## Cambios de la rev. 9 respecto de la rev. 8
- §2 NUEVO MÓDULO **RADAR GLOBAL** (`videolab/viral/radar.py` + `videolab/viral/RADAR-GLOBAL.md`): trae en 3 s ~230 temas del día de Google Trends RSS, Google News RSS, Wikipedia pageviews y X/trends24 (CL, MX, ES, AR, US), cada uno con puntaje de ángulo jurídico (7 materias + palabras de conflicto) y peso por país (Chile ×3). Con `--video` busca en YouTube Shorts el viral real de ese tema (vistas y duración). Medido el 05/09: 230 temas, 24 con ángulo legal, 2,8 s.
- **REGLA MADRE**: video del día = TEMA del radar × ESTRUCTURA radiografiada. No se copia el tema de un viral de fútbol o farándula; se toma el tema de actualidad con ángulo jurídico y se cuenta con la estructura que retiene.
- §2 Tareas: "Tendencia del día" (trig_012g4GgzsCQusrCuQPD439w3) ahora arranca con `radar.py --video` y guarda la foto del día en `videolab/viral/radar/<fecha>.json` (serie histórica para anticipar en vez de reaccionar).
- §5 TikTok del estudio conectado en Higgsfield (connector f23f2205-1ae6-4259-8240-e6f4165bbe79, activo 05/09): sonidos del día de Chile + vía alterna de publicación directa (DIRECT_POST con música) si Metricool falla, y experimento E-06 los martes y jueves.
- §6 + **D-17** (05/09) el descubrimiento de tendencias se hace con el RADAR GLOBAL (4 fuentes públicas), no con rankings de TikTok: están cerrados. El tema lo manda el radar; la estructura, el viral radiografiado.
- §7 PUERTAS CERRADAS probadas el 05/09 (no volver a intentarlas): **Reddit** bloquea la IP del datacenter ("Blocked - network policy"); **TikTok Creative Center** responde `40101 no permission` porque su API pide firma calculada en el navegador; **YouTube /feed/trending** ya no existe (YouTube retiró la página). Además: el contenedor de Claude no alcanza trends.google.com ni news.google.com (proxy) — el radar corre en el sandbox de Higgsfield, no en el contenedor; y trends24 sí se parsea con `trend-name[^>]*>\s*<a[^>]*>([^<]{2,40})`.
- §8 + **H-09** (05/09) un tema de actualidad contado con una estructura viral rinde más que un tema evergreen → comparar las piezas de "tendencia" contra la mediana del canal a 72 h; si una materia del radar rinde sistemáticamente mejor, se le sube el peso en el diccionario de radar.py.

## Cambios de la rev. 8 respecto de la rev. 7
- §0 Doctrina: siempre "en San Bernardo" EXCEPTO dentro de los quiz (la comuna va en la descripción, D-15).
- §2 VIRAL LAB: piloto vigente `videolab/piloto-quiz-02.json` (v2: sin intro, la pregunta 1 es el gancho desde el segundo 0; sin comuna en pantalla; preguntas de la vida diaria; 100 s; cada respuesta con artículo verificado). Nueva tarea secundaria TENDENCIA DEL DÍA (10:00, publica la misma mañana).
- §2 Publicaciones: lun 07/09 20:00 = 371533524 F12 quiz v2 'renuncia y te pago el finiquito al tiro' (reemplazó al 371526566). Verificaciones programadas 06/09 07:40 y 11:30 Chile.
- §5 Límites: Fábrica (6) + Viral Lab (1) + Tendencia (1) = 8 publicaciones/día, dentro del tope ~25/24 h.
- §6 + D-15 (criterio del quiz) y D-16 (Tendencia del día).
- §7 Metricool (conector) para TikTok solo entrega métricas propias y mejor hora; NO hay competidores ni tendencias. updateScheduledPost cambia el id del post (conserva el uuid): registrar el id nuevo.
- §8 + H-08 (replicar el mismo día la estructura de un viral en tendencia rinde más que la grilla fija).
