# INFORME — Qué hace virales los videos de frutas/objetos animados

Encargado por Cristopher el 12/09/2026, antes de rehacer el prototipo del abogado vegetal.
Dos fuentes: (1) medición directa de los dos videos referentes que él aportó, (2) investigación web del formato.

---

## 1. LA MEDICIÓN — sus referentes contra mi prototipo

Medido con OpenCV sobre 30 cuadros repartidos de cada video. Detección de cara con haarcascade.

| | REF 1 (la vela) | REF 2 (las frutas) | MI PROTOTIPO |
|---|---|---|---|
| **Cara en el cuadro (mediana)** | **4,5 %** | **2,5 %** | **1,1 %** ❌ |
| Cara en el cuadro (máximo) | 8,7 % | 10,6 % | 17,1 % |
| Duración | 75 s | 75 s | 39 s ❌ |
| Planos (cambio de ángulo) | 13 | 13 | 9 |
| Plano medio | 5,8 s | 5,8 s | 4,4 s ✅ |
| Escenarios distintos | 8 | 10 | 9 |
| Luminancia media | 93/255 | 56/255 | 66/255 ✅ |
| Contraste (desviación) | 58 | 52 | 51 ✅ |
| Sombra profunda (<45) | 31 % | 58 % | 50 % ✅ |
| Saturación | 104/255 | 118/255 | 116/255 ✅ |

### Lectura

**La luz y el color ya están bien.** Luminancia, contraste, sombra y saturación del prototipo caen dentro del rango de los referentes. Esa parte no hay que tocarla.

**El encuadre está mal por un factor de 2 a 4.** Las caras del prototipo ocupan 1,1 % del cuadro; las de los referentes, 2,5 % y 4,5 %. Se hicieron postales, no primeros planos.

**El ritmo de corte NO es el problema.** Contra la creencia de que hay que cortar cada 2-4 s, los dos referentes cortan cada **5,8 s**, y el prototipo ya va más rápido (4,4 s). Acelerar el montaje habría sido arreglar lo que no estaba roto.

**Falta la mitad del metraje.** 39 s contra 75 s. Sin ese tiempo no hay dónde poner el giro ni dónde construir la humillación.

---

## 2. EL MECANISMO — por qué funciona el híbrido humano/vegetal

Esto viene de un análisis académico publicado en The Conversation, replicado en StudyFinds y RNZ. Es la única explicación con respaldo serio que encontré, y explica el formato entero.

**Primer mecanismo — el borde del valle inquietante.** Los personajes son *"expresivos, pero a menudo no del todo coherentes"*: lo bastante extraños para provocar curiosidad, pero **"no lo bastante incómodos como para que dejes de mirar"**. El diseño no evita el valle inquietante: se queda parado en su borde a propósito.

**Segundo mecanismo — la desconexión moral.** Como los personajes son sintéticos, el espectador tiene distancia psicológica. Tramas de traición, humillación o agresión *"pueden consumirse sin la incomodidad que surgiría si hubiera personas reales involucradas"*.

> **La cabeza de verdura es un permiso emocional.** Deja que el espectador disfrute un melodrama brutal sin sentirse mal. Ese es el motor del formato.

### Consecuencia directa para nuestro prototipo — el error de contenido más grande

En el prototipo, **el trabajador y el jefe son humanos** y solo el abogado es vegetal. Eso rompe el permiso.

- Jefe humano gritándole a un trabajador humano esquelético = **incómodo**. El espectador escapa.
- Ají malvado gritándole a un choclo con esposas = **disfrutable**. El espectador se queda y lo comparte.

La intuición de Cristopher de poner al jefe como "ají malvado" es exactamente la regla del formato. Los tres personajes tienen que ser vegetales.

Fuentes: [StudyFinds](https://studyfinds.com/why-are-millions-watching-ai-fruits-have-affairs-on-tiktok/) · [RNZ](https://www.rnz.co.nz/life/screens/unethical-brain-rot-why-are-millions-watching-ai-fruits-have-affairs-on-tiktok)

---

## 3. LAS REGLAS DE IMAGEN (el componente clave)

### 3.1 El encuadre manda

Es la regla más citada del formato, y la que más nos falta:

> **"La cara tiene que llenar la pantalla. Si el objeto está lejos, el chiste es invisible en un teléfono."** — OpusClip
>
> **"Los primeros 0,5 segundos ya deben mostrar la cara."** · **"El primer fotograma debe mostrar la cara del personaje en su expresión máxima, no un plano general de presentación."**
>
> **"Si tu primer fotograma necesita contexto, es demasiado lento para este formato."** — AICUT

**Progresión de planos observada en videos reales:** abrir en plano medio → cerrar progresivamente → primerísimos primeros planos en el clímax. Nunca plano general de establecimiento.

### 3.2 Composición del personaje

**Regla madre: cabeza absurda, TODO lo demás realista.** El cuerpo, la ropa y la actuación son cien por ciento humanos y creíbles. El absurdo se concentra en un solo punto. Todo lo demás sostiene la inversión emocional.

**Regla de textura — la más accionable.** Hay que pedir los defectos de la verdura real, no la verdura genérica:
- `bruised texture` (magulladuras)
- `seed indentations` (hendiduras de semilla)
- `bumpy organic skin` (piel rugosa)
- `subsurface scattering on vegetable skin`

La textura imperfecta es lo que separa "cine" de "clipart".

**Regla de consistencia:**
1. **Objeto-firma invariable por personaje** (un reloj de oro, unos lentes, un collar). Sobrevive a la deriva del modelo entre generaciones.
2. **En los prompts de animación, describir al personaje por su apariencia, nunca por su nombre.** "El hombre con cabeza de brócoli y traje azul", no "el abogado". El modelo de video no sabe quién es el abogado.

### 3.3 Arquetipos por verdura (convención ya establecida del género)

El espectador los decodifica en menos de un segundo, sin sonido:

| Verdura | Rol |
|---|---|
| Brócoli | Autoridad, matriarca, elegancia |
| Ají / uva / berenjena (oscuro o rojo intenso) | **Villano** |
| Fresa / cereza | Seductora |
| Banana / choclo (claros) | **Inocente, vulnerable, víctima** |
| Palta / pimiento | Joven ambicioso |
| Racimo de uvas | Coro de chismosos |
| Piña | Ostentoso, sospechoso |

El color hace el trabajo de casting que en cine haría un actor. Oscuro = villano, claro = víctima. Legible en mudo, que es como se ve la mitad del tiempo.

### 3.4 Luz

El género **no** es uniformemente oscuro. La constante es el **claroscuro**: una sola fuente de luz motivada con caída pronunciada.

- Confrontación y villano → clave baja: `single overhead spotlight, deep shadow falloff, dark background`
- Resolución emocional → `warm golden hour backlight, long shadows`
- **Nunca** iluminación ambiental plana: lee como render barato.

**No escribir `dark` en el prompt. Escribir la fuente de luz.** El modelo responde a fuentes, no a adjetivos de humor.

### 3.5 Por qué fotorrealismo y no dibujo animado

1. **Habilitador técnico:** el formato existe porque el lip-sync fotorrealista se volvió barato a fines de 2025 (Veo 3). No es una elección estética, es una consecuencia.
2. **Señal de presupuesto:** la alta fidelidad de textura genera la pregunta *"¿cómo hicieron esto?"*, que es en sí misma un motor de comentarios y de re-visionado.
3. **El realismo sostiene la empatía:** *"lo bastante extraño para detener el scroll, pero lo bastante realista para evocar empatía"*. El dibujo plano consigue lo primero y no lo segundo.

---

## 4. ESTRUCTURA NARRATIVA

- **4 a 6 escenas por episodio:** contexto → tensión creciente → **pico dramático (el momento compartible)** → cierre en cliffhanger.
- **El giro va alrededor del 55 % del metraje.** Dos videos medidos de forma independiente lo sitúan en el segundo 45-50 de uno de 75-85 s. Antes, la segunda mitad pierde tensión; después, la retención cae antes de la recompensa.
- **Los primeros 3 segundos son "normalidad → interrupción"**, no caos inmediato. El segundo 0-3 es el absurdo visual presentado como si fuera normal: **la cabeza de verdura ES el gancho**. El conflicto entra en el segundo 3-6.
- **Arcos que más rinden:** infidelidad (el nº 1), embarazo inesperado, identidad secreta, venganza, dinastía familiar.
- **Cierre:** cliffhanger explícito en el último fotograma. La serialización es lo que convierte vistas en seguidores.

### Guion y audio
- **80-90 caracteres de voz por escena** (5-8 s de audio).
- **Música de fondo al 15-20 % del volumen de la voz.**
- **Subtítulos quemados obligatorios** (+12 % de retención; la mitad de la audiencia mira en silencio).
- **Voz con personalidad, nunca neutra.** *"Ligeramente desquiciado. El sarcasmo y el agotamiento funcionan; la narración neutra no."*
- Una voz fija por personaje, nunca se cambia.

---

## 5. NÚMEROS

**Fruit Love Island** (marzo 2026, el caso mejor documentado, con cobertura de prensa):

| Métrica | Valor |
|---|---|
| Seguidores en 4 días | 2,3 millones |
| Vistas totales | ~300 M en 9 días |
| Vistas por episodio | 10-20 M (pico 30 M) |
| **Duración por episodio** | **60 segundos** |
| **Cadencia** | **1 episodio diario** |
| Temporada | 22 episodios |

Otras cuentas: @frutinovelas 30 M de reproducciones en una semana. @ai.cinema021 más de 3 M de seguidores.

**Benchmarks generales de TikTok** (no específicos del formato, orden de magnitud):
- 60 s – 3 min: objetivo >30 % de retención, fuerte >45 %
- Una caída de más del 30 % en los primeros 3 s = la mayoría decidió no verlo
- Hooks de punto de dolor: +23 % de retención media sobre aperturas genéricas
- **Los compartidos valen más que las vistas.** Un video con 50.000 vistas y 8.000 compartidos supera a uno con 500.000 vistas y 200 compartidos.

---

## 6. ⚠️ EL RIESGO QUE HAY QUE SABER ANTES DE APOSTAR AL FORMATO

Fruit Love Island, la cuenta más exitosa del género, **se apagó en 3 semanas**:

- **12 de 22 episodios eliminados** de la plataforma tras reportes masivos
- Comentarios inundados de críticas por el impacto ambiental de la IA generativa
- El creador paró citando *"odio y cero ingresos"*
- Hay además un conflicto de atribución: una creadora sostiene que la serie se inspiró en su contenido sin crédito

Para un estudio jurídico esto importa más que para una cuenta anónima: **el reflujo contra el contenido generado por IA puede salpicar a la marca profesional.** Mitigación razonable: etiquetar el contenido como animación IA, no fingir que es real, y no construir el 100 % de la línea de contenido sobre este formato.

Fuentes: [DesignRush](https://news.designrush.com/tiktok-series-fruit-love-island-ai-format-risk) · [Forbes](https://www.forbes.com/sites/danidiplacido/2026/03/24/tiktoks-viral-fruit-love-island-trend-sparks-online-backlash/)

---

## 7. ERRORES QUE MATAN ESTOS VIDEOS

1. **Encuadre abierto** — el error nº 1 en todas las listas. Es el nuestro.
2. **Enterrar la revelación** — el primer fotograma tiene que ser la cara en expresión máxima.
3. **Voz neutra de narrador.**
4. **Sin subtítulos quemados.**
5. Demasiado setup, demasiados personajes, sin contraste emocional, contar en vez de mostrar.
6. Escribir el diálogo después de generar la imagen. El guion va primero.
7. Fondos estáticos: señalan baja calidad.
8. Usar nombres de personaje en los prompts de video en lugar de descripciones de apariencia.

---

## 8. LO QUE NO SE PUDO VERIFICAR

- **Métricas de @habitosanimados1.** TikTok bloquea el acceso automatizado. Sin vistas ni seguidores verificados.
- **Datos de retención específicos del formato.** Ninguna fuente publica curvas de retención de un fruit drama.
- **Prompts reales de las cuentas grandes.** Ninguna cuenta con millones de seguidores publicó su prompt. Todo lo que circula son reconstrucciones de blogs de herramientas que venden el producto.

---

## 9. LAS 10 REGLAS PARA APLICAR

1. **Los tres personajes principales son vegetales.** El permiso emocional se rompe si el villano es humano.
2. **Cabeza absurda, todo lo demás realista.**
3. **Pedir los defectos de la verdura:** `bruised texture`, `seed indentations`, `subsurface scattering`.
4. **La cara llena el cuadro.** Objetivo: 3-5 % del cuadro de mediana, contra el 1,1 % actual.
5. **El primer fotograma es el personaje en expresión máxima**, no un plano general.
6. **Una sola fuente de luz motivada con caída pronunciada.** Escribir la fuente, no "dark".
7. **Objeto-firma invariable por personaje** + describir por apariencia, nunca por nombre.
8. **75 segundos, no 39.** Corte cada 5-6 s (el ritmo actual ya está bien).
9. **El giro en el segundo 42-45.**
10. **Cliffhanger en el último fotograma + un episodio diario.** La serie es lo que convierte vistas en seguidores.
