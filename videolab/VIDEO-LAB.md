# VIDEO LAB — Sistema autónomo de I+D, producción y optimización audiovisual
Estudio Jurídico San Bernardo · módulo enchufado a la arquitectura general (MASTER_STATE → Video Lab → Fábrica → Metricool → métricas → MASTER_STATE). Encargado por Cristopher el 05/09/2026. No es un proyecto aislado: cada aprendizaje vuelve al cerebro.

## Misión
No producir videos. Producir **atención → audiencia → confianza → contactos → clientes → 400 clientes**. Se optimiza el sistema completo, no la calidad ni las vistas por separado. Métrica reina: **clientes generados**; después consultas, WhatsApp, visitas al perfil, retención, vistas.

## Reglas del laboratorio
1. **Ninguna herramienta es imprescindible.** Prioridad: gratis → open source → free tier suficiente → muy bajo costo → automatizable → premium solo si aporta una diferencia real y medida.
2. **Toda etapa tiene primaria, fallback y premium** (ver pipeline v2 en la auditoría vigente). Si una herramienta desaparece, el sistema sigue.
3. **Probar antes de opinar.** Una herramienta se evalúa corriéndola en el sandbox con el mismo texto/guion de referencia y midiendo (WER, duración, tiempo, loudness, bbox de texto). Lo que no se puede medir se convierte en experimento con retención real.
4. **Un cambio a la vez.** Los experimentos se registran en `registro-experimentos` (Drive) y en la bitácora del Centro de Mando; se corta por número de piezas, no por impresión.
5. **Nada por abuso.** Sin saltarse autenticación, sin cuentas ajenas, sin explotar límites. Ahorrar por ingeniería. Servicios "no oficiales" (edge-tts) solo como fallback y marcados como frágiles.
6. **Ética del contenido** (PROMPT MAESTRO): nada reconocible de un cliente real, nada de resultados prometidos ni testimonios inventados, nada que denigre a jueces, fiscales o colegas por nombre, no presentar ficción como hechos, no afirmaciones jurídicas falsas. Arquetipos (abogados de TV, narradores, comediantes) solo como estudio de ritmo y personalidad: no se copian personajes protegidos.
7. **Cristopher no aparece en cámara** (D-02). Nunca se propone.

## Ficha y ranking de cada herramienta candidata
Nombre · función · costo · free tier · límites · calidad · automatización · API · open source · riesgo de lock-in · utilidad para el pipeline.
Puntaje /10 en: calidad, costo, velocidad, automatización, facilidad, escalabilidad, dependencia, calidad de output → 🟢 recomendada · 🟡 experimentar · 🔴 descartar.
Se mantiene en `videolab/ranking.json` (la tarea de I+D lo actualiza).

## Pipeline modular (cada módulo sustituible)
idea → investigación → hook (10 versiones, filtro) → guion → storyboard → imagen/video → voz → música/SFX → subtítulos karaoke → edición → color/look → vertical 1080×1920 → control de calidad numérico → publicación → métricas → aprendizaje → nueva iteración.
Código: `motor/motor.py` (render), `videolab/voz.py` (voz con fallback), `videolab/karaoke.py` (subtítulos), `motor/ganchos/banco.json` (fotos), `videolab/formatos.json` (formatos-hipótesis).

## Sistema de formatos y experimentación
`videolab/formatos.json` contiene los formatos-hipótesis (historia jurídica, POV, abogado reacciona, caso sorprendente, mito, humor, noticia, "no hagas esto", "si te pasa esto", sketch). Cada semana entran 2 formatos nuevos con 3 piezas; se mata lo que quede bajo la mediana del canal a 7 días; se duplica lo que la supere en 2×. El humor está autorizado y buscado, con conexión a audiencia, marca, recuerdo y conversión. Los primeros 3 segundos son una batalla: sin razón para detener el scroll, el hook se rechaza.

## Costos
Por video se calcula voz + imagen + video + música + edición + upscale = total, y se proyecta a 100 / 500 / 1.000 / 10.000. Objetivo: mínimo costo sin sacrificar calidad medible. Estado 05/09/2026: pipeline v2 ≈ US$0,00-0,02 por video.

## Escalabilidad
Diseñado para 15 piezas diarias, luego 30, luego 50 — **solo si los datos demuestran que el volumen rinde**. Más contenido no es mejor contenido. Hoy: 6 diarias (3 por brazo del experimento de voz).

## Tareas que lo operan (nube)
- **Fábrica** (diaria 06:00): produce con el pipeline v2 y aplica el experimento vigente.
- **Video Lab I+D** (mar/jue/sáb 07:00): busca herramientas nuevas (web, GitHub, benchmarks), prueba UNA en el sandbox con el texto de referencia, actualiza `ranking.json` y la auditoría, propone cambios con datos, escribe en la bitácora.
- **Mejora del sistema** (diaria 22:00): implementa UNA mejora del backlog.
- **Métricas** (lunes 09:00): cierra experimentos, mata/duplica formatos.

## Descubrimiento automático
Cuando aparece una herramienta mejor: ¿tiene API? ¿free tier? ¿se conecta? ¿sustituye o se combina? ¿ahorra? ¿mejora calidad o velocidad? Si sí → se prueba y se propone con datos. Si requiere cuenta, pago o clave → un solo paso para Cristopher, en una frase, con todo lo demás listo. Las claves van a Drive (carpeta Cerebro, archivo `claves.txt`), nunca a GitHub.

## Regla final
Si el problema no es la tecnología sino el contenido, la distribución o la conversión, se dice. Estado 05/09/2026: el problema es la conversión y la medición (MASTER_STATE §4).
