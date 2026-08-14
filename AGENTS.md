# AGENTS.md — Lineamientos generales del repositorio

Este repositorio contiene los trabajos prácticos (TPs) de la materia **Simulación de Sistemas (ITBA)**: implementaciones de motores de simulación, post-procesamiento, animaciones, presentaciones e informes.

> **REGLA FUNDAMENTAL**: cada TP vive en su propio directorio y puede tener su propio archivo de contexto (`AGENTS.md` / `CLAUDE.md` local). Todo contexto local **debe comenzar referenciando este archivo raíz** (por ejemplo: *"Leer y respetar siempre los lineamientos de `../AGENTS.md`"*). Los lineamientos de este documento aplican a **todos** los trabajos; el contexto local solo agrega o especializa, nunca contradice.
>
> **Prioridad de documentos**: el **enunciado del TP** tiene máxima prioridad por sobre cualquier guía genérica (incluido este documento). Siempre leer el enunciado completo y responder a todos los puntos pedidos.

---

## 1. Estructura del repositorio

- Un directorio por TP en la raíz (ej.: `tp1/`, `tp2/`, ...).
- Dentro de cada TP, separar claramente:
  - **Motor de simulación**: el núcleo que resuelve el modelo computacional.
  - **Post-procesamiento**: cálculo de observables, generación de gráficos y animaciones a partir de los outputs de la simulación.
  - **Entrega**: presentación (PDF), informe si corresponde, y archivos con el formato y nombres exactos solicitados en el enunciado.
- El motor de simulación **no** debe mezclarse con el post-proceso: la simulación escribe outputs crudos (estado del sistema en ciertos instantes) y el post-proceso los consume.
- Respetar el formato y nombres de archivos solicitados en cada enunciado para la entrega.

## 2. Modelado y simulación

Respetar la cadena conceptual de la materia: **Sistema Real → Modelo Matemático → Modelo Computacional → Simulación**.

- El **modelo matemático** se expresa en forma general (ecuaciones), sin atarse a un sistema particular ni al método numérico de resolución.
- El **modelo computacional** es la traducción del modelo matemático a código: documentar arquitectura, pseudocódigo o diagramas (UML) del motor de simulación.
- Las **simulaciones** se definen sobre un sistema particular: geometría, parámetros fijos, parámetros variables (inputs), outputs a estudiar.
- Los **observables** se calculan a partir del output directo de la simulación y deben estar **definidos matemáticamente** de forma explícita: si se promedia, aclarar qué se suma y sobre qué se divide.
- Registrar siempre el **número de repeticiones** (realizaciones) y los **tiempos de simulación** utilizados.
- **Seeds distintas para promediar**: cuando se realizan varias ejecuciones para promediar resultados, cada una debe usar una **seed distinta**. Si se hacen 10000 ejecuciones con la misma seed se está testeando la potencia de la PC y no la simulación ni lo que se busca mostrar. Por ejemplo: 50 o 100 ejecuciones, cada una con su propia seed.
- Los observables promedio se reportan con **barras de error** (con su cálculo de desvío), y con las **cifras significativas** correspondientes al error asociado. Si aparece un **outlier** muy grande (por ej., un desvío mucho mayor que el resto), **avisar** antes de seguir.

### 2.1 Simulación offline y outputs

La simulación se realiza **OFFLINE**: las animaciones y los observables **surgen** de la simulación y de los resultados que esta arroja, como etapa posterior y separada (post-proceso).

- **SUPER importante**: cada simulación debe imprimir/guardar **toda la información verdaderamente necesaria** (inputs, resultados parciales, outputs) para poder realizar y analizar **cualquier cosa** (videos, animaciones, gráficos, nuevos observables) sobre esos mismos parámetros **sin tener que volver a correr toda la simulación**.
- Ante la duda, guardar de más: re-correr una simulación completa por un dato faltante es el peor escenario.

### 2.2 Formato de archivos de salida

Formato de referencia para guardar simulaciones de partículas y su posterior visualización. El número de fila identifica a la partícula (1, 2, ..., N).

**Info estática** (constante en el tiempo):

```
N           (heading: número total de partículas)
L           (longitud del lado del área de simulación)
r1 c1       (radio y color de la partícula 1)
r2 c2       (radio y color de la partícula 2)
...
rN cN       (radio y color de la partícula N)
```

**Info dinámica** (un bloque por instante de tiempo guardado):

```
t1
x1 y1 vx1 vy1     (partícula 1)
x2 y2 vx2 vy2     (partícula 2)
...
xN yN vxN vyN     (partícula N)
t2
x1 y1 vx1 vy1
...
xN yN vxN vyN
```

### 2.3 Herramientas de visualización y animación

Recomendaciones de la cátedra: **Matlab/Octave**, **Matplotlib** (Python), **Ovito**, u otras equivalentes.

## 3. Gráficos y figuras

Estas reglas aplican a toda figura, esté en una presentación o en un informe:

- **Ejes**: siempre con leyenda/título en ambos ejes, preferentemente en **palabras** (no símbolos), con **unidades entre paréntesis** usando abreviaturas del sistema MKS: (s), (m), (kg), etc.
- **Tipografía**: el tamaño de fuente de letras y números dentro de las figuras debe ser similar al del texto que las rodea (en presentaciones, mínimo 20).
- **Notación científica**: potencias de 10 con supraíndice (10⁻¹, 10⁰, 10¹, 10²). **Prohibido** usar `1E2`, `10^2` o similares. Toda cantidad lleva sus unidades.
- **Datos promedio**: identificar claramente cada punto con un símbolo y/o barra de error. Nunca unir puntos con líneas sin que se distingan los puntos. Se permite unirlos con **rectas** como "guía para el ojo".
- **Prohibido interpolar** datos con funciones arbitrarias (polinomios, splines) que no provengan de una teoría sobre el sistema estudiado.
- **Escalas**: si los datos varían en varios órdenes de magnitud, usar escala **log-log o semilogarítmica** en el eje que corresponda; una escala lineal que aplasta las diferencias no es aceptable.
- **Escala logarítmica**: usar notación científica en los labels y asegurarse de que los labels de los ejes estén **equiespaciados**. No incluir rayitas (ticks) intermedias que no vayan a tener label.
- **Barras de error**: todo gráfico de promedios lleva barras de error con su cálculo de desvío. Si un punto presenta un desvío mucho mayor que el resto (outlier), **avisar** en lugar de graficarlo sin más.
- **Ajustes**: cuando se ajusta una función teórica a los resultados, mostrar cómo se halló el mejor ajuste (según lo explicado en la Teórica 0, ej.: mínimo del error cuadrático en función del parámetro de ajuste).
- **Estado estacionario**: en gráficos de evolución temporal, identificar cuándo se pasa del estado inicial (transitorio) al estado estacionario. El criterio es **a ojo**: dibujar una **recta vertical** que pase por el punto a partir del cual empieza el régimen estacionario, para que quede claramente marcado.

## 4. Notación matemática y unidades

Convención para símbolos matemáticos, tanto en informes como en presentaciones (tipografía Times New Roman):

- **Vectores**: negrita, sin itálica (**x**, **r**ᵢ(*t*)).
- **Escalares**: itálica, sin negrita (*t*).
- **Unidades y números**: sin negrita y sin itálica, separados (*m* = 4 kg). Abreviaturas MKS: m, s, kg, etc.
- Cifras significativas acordes al error asociado; no reportar dígitos de más que dificulten la lectura.

## 5. Presentaciones (diapositivas)

Basado en la "Guía para realizar presentaciones con diapositivas" de la cátedra.

### 5.1 Consideraciones generales

- Informe y presentación de un mismo TP son documentos **independientes y autocontenidos**: no dejar ítems sin especificar en uno porque están en el otro.
- **Numerar las diapositivas** (facilita la discusión posterior).
- **Respetar los tiempos** designados en cada enunciado; ensayar antes. Para el TP final: 10 a 15 minutos según se indique.
- Poco texto en las diapositivas: no redactar párrafos enteros ni pegar bibliografía. Usar un **mínimo de ecuaciones**.
- **SUPER importante — no inventar resultados**: no agregar a la presentación (ni al informe) nada que salga de cálculos que **no se hayan realizado**. Si hay algo interesante que se podría agregar pero requiere cálculos nuevos, **explicarlo y esperar confirmación** antes de hacerlo.
- **Sin sección de bibliografía**: si hace falta una cita, va abreviada en la diapositiva correspondiente (autor, revista, año).
- Títulos y subtítulos coherentes. Sugerencia de la cátedra: LaTeX Beamer (`\documentclass{beamer}`) con `\useoutertheme{miniframes}` o `\usetheme{Warsaw}`.
- Separar secciones con diapositivas que solo tengan el título de la sección. **No numerar las secciones** en la presentación.

### 5.2 Figuras en presentaciones

- Las figuras **no llevan título dentro ni caption debajo** (a diferencia de los informes, que sí llevan captions).
- Los **parámetros fijos** (configuración del sistema con la que se obtuvo el resultado) se describen **al costado de la figura**.
- Aplican además todas las reglas de la sección 3 (ejes, unidades, notación científica, fuente ≥ 20).

### 5.3 Estructura obligatoria de la presentación

Distribución orientativa de tiempos (para una presentación de ~15 min):

1. **Introducción / Sistema Real / Fundamentos** (< 1 min, máx. 3 diapositivas): descripción somera del sistema real y descripción rápida pero completa de las ecuaciones del modelo matemático general (sin sistema particular ni métodos de resolución).
2. **Implementación** (~3 min): cómo se traduce el modelo matemático al computacional (arquitectura, pseudocódigo, UML). **Solo el motor de simulación**: no describir post-proceso ni formato de archivos input/output.
3. **Simulaciones** (~2 min): configuración del sistema particular a simular (geometría, rango de parámetros fijos y variables, inputs y outputs), con un **esquema ilustrativo**. Definición matemática de los observables. Número de repeticiones y tiempos simulados.
4. **Resultados** (~8 min; animaciones + estudio paramétrico/estadístico), estructurados así para **cada input/parámetro estudiado**:
   1. Animación característica del sistema (puede haber dos, con valores extremos del input) para ilustrar la dinámica.
   2. Figura del observable en función del tiempo (solo evoluciones típicas, de valores extremos, para validar la definición del observable) y explicación del escalar que caracteriza el proceso (ej.: promedio en el estado estacionario, tasa de crecimiento). No extenderse: las evoluciones no son los resultados definitivos.
   3. Figura de **input vs. observable**, con promedio y barras de error.
   4. Repetir 1–3 para cada parámetro estudiado.
   - Si hay ajuste de función teórica: mostrar cómo se halló el mejor ajuste.
5. **Conclusiones** (< 1 min, 1 diapositiva): basadas **solo en los resultados mostrados**. No son conclusiones: resultados no mostrados, hipótesis no probadas explícitamente, cosas que quedaron por hacer o que se descartaron. Toda hipótesis explicativa debe haber sido probada y mostrada en resultados.
6. Opcional: diapositiva de cierre ("Muchas Gracias" / "Gracias por su atención"), **sin** escribir "¿preguntas?".

### 5.4 Animaciones

- El propósito de las animaciones es **situar al espectador en qué se está estudiando**, complementando a las figuras (animaciones + figuras). Ejemplo: si se estudia el nivel de polarización en función del ruido, mostrar una película con mucho ruido y otra con poco.
- **Ojo**: las animaciones y su tiempo de reproducción **consumen tiempo de presentación**; elegir duraciones acordes al tiempo total designado.
- En la presentación **en vivo**: animaciones **embebidas** en la diapositiva (no salir de la presentación para mostrarlas).
- En el **PDF que se entrega**: **sin** animaciones embebidas ni archivos de animación adjuntos. En su lugar: una imagen fija de un fotograma representativo y, debajo, un **link explícito a YouTube o similar**.

### 5.5 Trabajo en grupo

- La presentación se distribuye previamente entre los presentadores, en partes **balanceadas** en tiempo, contenido y participación.
- Todos los integrantes deben poder exponer **cualquier** parte.
- No superponerse ni agregar a lo que recién explicó un compañero; las preguntas se responden en orden.
- Antes de entregar, **todos** revisan el documento contra esta guía y contra las correcciones de TPs anteriores: los errores reiterados de un TP al siguiente penalizan la nota.

## 6. Informes

Basado en la "Guía para Redacción de Informe" de la cátedra. Los informes son documentos redactados, **independientes y autocontenidos** respecto de la presentación: no dejar ítems sin especificar en uno porque están en el otro.

### 6.1 Estructura

- **Numerar secciones y sub-secciones**.
- Las secciones habituales son similares a las de las presentaciones: **Introducción; Modelo; Implementación; Simulaciones; Resultados; Conclusiones** (para el detalle del contenido de cada una, ver la sección 5.3 de este documento).
- Al final va una sección extra **sin número** denominada **"Referencias"**.

### 6.2 Redacción

- **Lenguaje técnico escrito**: no usar lenguaje coloquial ni descripciones "literarias".
- Usar **el mismo idioma en todo el informe**.
- **Todas** las secciones llevan texto que analiza y mantiene el hilo lógico del estudio. En ningún caso puede haber una sección con figuras sueltas.
- Conclusiones basadas **solo en los resultados mostrados** (mismo criterio que en presentaciones).
- Sugerencia de la cátedra: usar **LaTeX** como procesador de texto y ecuaciones.

### 6.3 Figuras y ecuaciones

- Las figuras **sí llevan caption** debajo (a diferencia de las presentaciones): "**Figura 1**: Descripción..., parámetros, etc." — en general observable vs. input/parámetro, con promedios y barras de error.
- Figuras y ecuaciones deben estar **numeradas y referenciadas en el texto**: "En la Fig. 1...", "En la Ec. (1)...".
- Las ecuaciones llevan su número entre paréntesis a la derecha, y debajo se definen todos los símbolos: *E* = *m c*² (1), "donde *E* es la energía, *m* la masa de la partícula y *c* la velocidad de la luz".
- Aplican además todas las reglas de gráficos (sección 3) y de notación matemática (sección 4).

### 6.4 Referencias

- La sección "Referencias" lista **solo** la bibliografía citada en el texto: si no está citada, no va en Referencias ni en ninguna otra parte.
- Cita en el texto con corchetes: "Se ha demostrado [1] que ...".
- Formato de la lista: `[1] Nombre Apellido, "Título trabajo", Nombre publicación, vol., nro., pp. (año).`
- Tip: en Google Scholar (https://scholar.google.com.ar), el símbolo de doble comilla debajo de cada publicación da la cita en el formato indicado.

## 7. Checklist antes de entregar

- [ ] ¿Se leyó el enunciado completo y se respondieron **todos** los puntos pedidos?
- [ ] ¿Se respetan formato y nombres de archivos solicitados?
- [ ] ¿Diapositivas numeradas y tiempos ensayados?
- [ ] ¿Figuras con ejes en palabras + unidades MKS, fuente adecuada, notación científica con supraíndices?
- [ ] ¿Puntos de datos identificados con símbolos/barras de error, sin interpolaciones arbitrarias?
- [ ] ¿Observables definidos matemáticamente, con repeticiones y tiempos de simulación explicitados?
- [ ] ¿Cifras significativas acordes al error?
- [ ] ¿PDF de presentación sin animaciones embebidas, con fotograma + link?
- [ ] ¿Conclusiones basadas solo en resultados mostrados?
- [ ] ¿Se verificó no repetir errores corregidos en TPs anteriores?
