# BACKLOG del sistema — ordenado por impacto sobre el objetivo (400 clientes)

Una mejora por noche (tarea "Mejora del sistema 22:00"). Marcar con fecha lo hecho. Cada mejora se anota también en la bitácora del Centro de Mando (Artifact write_db, url https://claude.ai/code/artifact/150db229-8dca-4b72-ba6d-df5130030d53, collection bitacora).

## Pendiente
1. **Instrumentar el embudo** — link rastreable en la bio de TikTok (parámetro utm o acortador propio), conteo diario de mensajes de WhatsApp entrantes, campo "origen" en cada cita de Google Calendar. Sin esto no hay atribución. Al lograrlo: update sistema/estado con embudo:{instrumentado:true}.
2. **Consultas en el Centro de Mando** — la tarea de las 08:00 no puede escribir en la bitácora (bloqueo del clasificador). La tarea nocturna debe leer el correo "Consultas de hoy" del día en Gmail y escribir una entrada tipo "consulta" con consultas:<M>, y actualizar sistema/estado.consultas_respondidas. Nunca nombres ni datos de casos.
3. **Créditos de Eleven** — reusar la imagen de gancho por materia (una nueva por día) para bajar de ~1.320 a ~600 créditos por pieza. Probar seedream-5-lite o gemini-3.1-flash-image y comparar calidad.
4. **Karaoke** — subtítulos palabra por palabra con faster-whisper (ya instalado en el sandbox) sincronizados con la voz.
5. **Variantes de formato** — chat de WhatsApp simulado, mito vs realidad con veredicto en el segundo 2, noticia judicial de la semana en placa propia. Cada formato nuevo recibe 10 piezas y se mide.
6. **Corte de atención cada 2 s** — el detalle de cada punto aparece a los 0,85 s con fundido.
7. **Registro de experimentos automático** — la fábrica deja cada pieza también como doc en la colección `experimentos` del Centro de Mando (id, materia, gancho, formato, hora, post_id) y la tarea de métricas le agrega vistas/retención; la página puede mostrar la tabla.
8. **Centro de Mando: vistas en vivo** — añadir al manifiesto mcp la herramienta getAnalyticsDataByMetrics (TKEV02 vistas, TKEV07 seguidores) cuando Metricool ya entregue datos, y mostrar seguidores y vistas de 7 días en las tarjetas.

## Hecho
- 05/09/2026 — Motor 100% nube validado (lote 09, 8 piezas), receta en motor/RECETA-MOTOR-NUBE.md, 4 tareas programadas creadas.
- 05/09/2026 — Centro de Mando vivo: cola de Metricool en vivo (mcp) y bitácora + capacidad del sistema (db). Las tareas escriben al terminar.
