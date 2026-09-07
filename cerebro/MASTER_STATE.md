# MASTER_STATE — Estudio Jurídico San Bernardo

> Archivo cerebro. Se ACTUALIZA, no se reescribe. La fuente de verdad es la copia de Google Drive (carpeta Cerebro); esta copia de GitHub lista los cambios de cada revisión.
> Revisión vigente: **rev. 10**, 7 de septiembre de 2026, 09:00 Chile — PRIMERA LECTURA REAL DE MÉTRICAS.

## Cambios de la rev. 10 respecto de la rev. 9

### BLOQUEO ACTIVO — tope de cuenta en Metricool
- §2 La publicación del 07/09 09:00 (id 371688560, jornada de 42 horas) volvió con **ERROR: "You have reached your Metricool account limit."** Las otras siete piezas del lunes quedan PENDING y pueden caer por lo mismo. Sin resolver el tope, la Fábrica no publica aunque el pipeline funcione. Es el problema nº 1 de la semana.
- §5 El límite real de publicaciones ya no es el de TikTok (~25/24 h) sino el del plan de Metricool. Respaldo: publicación directa por Higgsfield (E-06), que no consume cuota.

### §3 MÉTRICAS — primera lectura real (semana 01–07/09/2026, hora de Chile)
- 90 videos con datos · **21.308 vistas** · 304 likes · 26 comentarios · 17 compartidos · seguidores 43.261 → 43.260 (neto −1).
- Vistas por día: mar 01 1.657 (10 videos) · mié 02 3.399 (24) · jue 03 2.944 (25) · vie 04 1.080 (11) · sáb 05 1.601 (10) · **dom 06 10.614 (9)** · lun 07 parcial 13 (1).
- Los días de 24 y 25 piezas rindieron **menos por video** (142 y 118) que los de 9 y 10 (1.179 y 160). Más volumen no compró vistas.
- **Mejor pieza: "Un taxi sin chofer que cobra la mitad que Uber. Y si te choca, ¿quién responde?"** — 06/09 01:21, 50 s, **5.469 vistas**, 100 likes, 15 comentarios, 11 compartidos. Actualidad (robotaxi) con ángulo de responsabilidad civil.
- **Segunda: video-respuesta a un comentario** (@Al Ca9391, licencia de conducir) — 06/09 13:02, 41 s, **3.657 vistas**, 70 likes. Formato no planificado, no estaba en `formatos.json`.
- Entre las dos: 9.126 vistas = 86% del domingo, 43% de la semana y 20 de los 26 comentarios de los siete días.
- **Peor:** los evergreen cortos del sistema anterior (22–24 s, publicados por hora los días 02–04), mínimo 66 vistas con 0 likes y 0 comentarios. Dentro de la grilla nueva, el peor fue "¿Te despidieron y la carta no dice nada?" (05/09 13:00, laboral, 128 vistas).
- **Conversión: 0 consultas atribuibles a TikTok.** Calendar sin reservas nuevas entre el 01 y el 07/09 (las dos existentes las crearon Cristopher y Natali). Gmail sin consultas de clientes en 8 días. 21.308 vistas → 0 consultas.

### §3 y §7 Lo que NO se puede medir (hallazgo duro)
- `fullVideoWatchedRate` (retención), tiempo medio visto, alcance, visitas al perfil y fuentes de tráfico (forYou / hashtag / sonido / búsqueda / perfil) vuelven **null en las 90 piezas**. Metricool entrega para esta cuenta solo vistas, likes, comentarios y compartidos.
- Consecuencia: **la regla "mata el formato con menor retención" no se puede ejecutar como está escrita.** Esta semana se aplicó sobre vistas por pieza, declarándolo (D-20).
- Los timestamps de `getAnalyticsDataByMetrics` para posts vienen en **UTC**: restar 3 h para leer hora de Chile (4 h antes del cambio de hora del 05/09).
- Corolario del 07/09 sobre publicación: tampoco un PENDING es publicado. El estado ERROR de Metricool solo aparece al consultar `getScheduledPosts`; no llega por correo.

### §2 GRILLA DE HORAS recalculada (fuente: getBestTimeToPostByNetwork, ventana 08/08–07/09)
- Tres picos los siete días: 10:00, 12:00 y 18:00. Valle de 00:00 a 07:00 y caída sostenida desde las 21:00.
- **Lunes a viernes: 10:00 · 12:00 · 16:00 · 17:00 · 18:00 · 19:00**
- **Sábado y domingo: 10:00 · 12:00 · 15:00 · 16:00 · 18:00 · 20:00**
- Salen 09:00 (−40% frente a las 10:00), 13:00 (valle entre los dos picos del mediodía) y 20:00 entre semana.
- Salvedad: el mejor video de la semana salió a la **01:21**, la peor franja de toda la tabla, y sacó 5.469 vistas. La grilla fija el piso, no es la palanca.

### §6 Decisiones
- **D-10 DEROGADA** (grilla 09:00 12:00 13:00 16:00 18:00 20:00). La reemplaza la grilla nueva.
- **D-18 el TEMA DE ACTUALIDAD manda sobre la grilla.** La pieza de actualidad con ángulo jurídico es la primera del día y se produce aunque desplace a un evergreen. El evergreen es relleno, no es el producto.
- **D-19 el VIDEO-RESPUESTA A COMENTARIO entra como formato fijo (F13):** una pieza diaria respondiendo un comentario real de la cuenta, con el @ visible y la precisión legal como cuerpo. Se agrega a `formatos.json`.
- **D-20 mientras TikTok no devuelva retención, el criterio de matar/duplicar es vistas por pieza contra la mediana de la semana**, y así se declara en cada informe. No se inventan lecturas de retención.

### §8 Veredictos de hipótesis
- **H-01** (voz IA no retiene) → **sin veredicto posible**: no hay dato de retención. Con vistas como sustituto, F01 tiene mediana de 159 vistas y ~0 comentarios: se degrada a relleno de grilla, no es el producto.
- **H-03** (penal vs civil) → **sin veredicto**: la dispersión dentro de cada materia (128 a 433) supera la diferencia entre materias, y con 0 consultas la mitad de la hipótesis no se puede probar. Congelada hasta tener embudo.
- **H-04** (el horario importa menos que el gancho) → **CONFIRMADA**: 5.469 vistas en la peor franja del día, 34× la mediana.
- **H-06** (F11 ensayo largo) → **provisional negativo**: parte 1, 189 vistas, 4 likes, 0 comentarios, con 3× el costo y 3× la duración de una pieza de grilla. Si las partes 2 y 3 no despegan, la serie se cierra y no se abre una parte 4.
- **H-07** (quiz F12) → sin datos; publica el 07/09 20:00, se mide el 10/09, y se juzgará por comentarios porque el "% completado" es inmedible.
- **H-08 y H-09** (actualidad + estructura viral) → **a favor, fuerte**: las dos piezas fuera de grilla hicieron 9.126 vistas contra 1.488 de las siete piezas de grilla del mismo domingo, 6× por pieza. H-09 se eleva a decisión (D-18).
- **E-01** (Kokoro vs Eleven) → **no se puede cerrar**: Metricool no marca el brazo. Hay que escribir A/B en registro-experimentos al programar cada pieza.
- **H-10 (nueva)** el video-respuesta (F13) rinde sobre la grilla porque hereda la audiencia del video original. Prueba: 1 pieza diaria por 7 días.
- **H-11 (nueva)** el gancho "objeto/servicio nuevo + ¿quién responde si te pasa algo?" es replicable fuera del tema del taxi. Prueba: las 3 variantes de las próximas 48 h.

### §9 Qué se mata y qué se duplica
- **MATA:** las tres franjas de valle (09:00, 13:00 y 20:00 entre semana) y el evergreen abstracto de 22–28 s como producto principal. La serie F11 de ensayo largo queda congelada tras la parte 3.
- **DUPLICA:** actualidad con ángulo jurídico y video-respuesta a comentario. Los dos superaron las 2.000 vistas, así que **regla de las 48 horas: 3 variantes de cada gancho antes del 09/09**.
- Prioridad 1 sigue siendo instrumentar el embudo: 21.308 vistas y 0 consultas es el único número que importa esta semana.

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
