# Guía para Realizar Presentaciones con Diapositivas

## 1. Consideraciones Generales

1.1 **Autocontenido:** Los informes y las presentaciones sobre un mismo trabajo son documentos independientes y cada uno es autocontenido. No se pueden dejar ítems sin especificar en uno de ellos porque estarán en el otro.  
1.2 **Numeración:** Numerar las diapositivas para facilitar la discusión posterior al hacer referencia a una diapositiva identificada por su número.  
1.3 **Tiempos:** Respetar los tiempos designados ensayando previamente. En cada T.P. se indicará el tiempo correspondiente. Para el T.P. final el tiempo de la presentación oral debe ser de **10 a 15 minutos** según se indique en los enunciados.  
1.4 **Prioridad del Enunciado:** Responder a todos los puntos pedidos en el enunciado del T.P. y leerlo completo. Este documento tiene **máxima prioridad** respecto de otros documentos como teóricas o guías genéricas.  
1.5 **Formato de Entrega:** Respetar el formato solicitado para la entrega de los archivos y los nombres de los mismos.  
1.6 **Texto Reducido:** Las diapositivas no deben contener mucho texto (no redactar párrafos enteros o partes de bibliografía).  
1.7 **Figuras y Captions:** Las figuras **no** llevan títulos dentro de las mismas ni leyendas explicativas debajo (*captions*, que sí van en los informes escritos). La información correspondiente a la configuración del sistema (parámetros fijos / condiciones particulares bajo las cuales se obtuvieron los resultados) debe estar descripta **al costado de la figura**.  
1.8 **Ejes de Figuras:** Las figuras **sí** llevan leyendas/títulos en los ejes vertical y horizontal, preferentemente en palabras (no símbolos) y cuando corresponda con las unidades entre paréntesis con las abreviaturas del sistema MKS (ej.: segundos (s), metros (m)). El tamaño de fuente dentro de las figuras debe ser similar al del resto de la diapositiva (por lo menos tamaño 20).  
1.9 **Notación Científica:** Tanto en figuras como en tablas se debe usar notación científica con potencias de 10 como superíndice ($10^{-1}, 10^0, 10^1, 10^2, \dots$) con sus unidades correspondientes. **No** utilizar notación tipo `1E2` ni `10^2`.  
1.10 **Cifras Significativas:** En tablas de resultados de observables promedio se deben utilizar las cifras significativas correspondientes al error asociado (según Teórica 0), evitando excesos de dígitos que dificulten la lectura.  
1.11 **Bibliografía:** La presentación **no** lleva sección final de bibliografía/referencias. De ser necesario, se incluye la cita abreviada directamente en la diapositiva correspondiente (*Autor, revista y año de publicación*).  
1.12 **Estructura Visual:** Estructurar de forma coherente títulos y subtítulos.  
  *Sugerencia:* Se puede usar LaTeX Beamer (`\documentclass{beamer}`) con `\useoutertheme{miniframes}` o `\usetheme{Warsaw}`.  
1.13 **Separadores de Sección:** Separar secciones con diapositivas que contengan únicamente el título de la sección que comienza. **No numerar las secciones en la presentación.**

---

## 2. Secciones

Las presentaciones deben estructurarse de acuerdo con el flujo *Sistema Real $\rightarrow$ Modelo Matemático $\rightarrow$ Modelo Computacional $\rightarrow$ Simulación*:

### 2.1 Introducción / Sistema Real / Fundamentos (Máximo 3 diapositivas)
- Somera descripción del sistema real a simular.
- Rápida pero completa descripción de las ecuaciones del modelo matemático general (sin especificar sistemas particulares ni métodos de resolución).

### 2.2 Implementación
- Detalle de la traducción del modelo matemático al modelo computacional: arquitectura del código, pseudocódigo, diagramas UML, etc.
- **Solo considerar el motor de simulación propiamente dicho**, omitiendo post-proceso o formatos de archivo I/O.

### 2.3 Simulaciones
- Descripción del sistema particular a simular: geometría, rango de parámetros fijos y variables, inputs y outputs a estudiar (ilustrar con un esquema del sistema).
- Definición matemática rigurosa de los observables calculados a partir del output directo (ej.: fórmulas de promedios, qué se suma y sobre qué se divide).
- Detallar número de repeticiones y tiempos de simulación.

### 2.4 Resultados
Estructurar la sección de resultados siguiendo este orden:
1. **Animación característica:** Para cada input/parámetro, mostrar primero una animación representativa (o dos con valores extremos) para ilustrar la dinámica del sistema.
2. **Evolución temporal del observable:** Mostrar el observable en función del tiempo y definir el escalar que caracteriza el proceso (ej.: promedio temporal en estado estacionario, tasa de crecimiento). Mostrar solo evoluciones típicas para validar la métrica sin extenderse.
3. **Gráfico Input vs. Observable:** Presentar la curva con los promedios y barras de error correspondientes.
4. Repetir los pasos 1 a 3 para los demás parámetros evaluados.
5. **Ajustes teóricos:** Mostrar cómo se halló el mejor ajuste según lo explicado en la Teórica 0.
6. **Puntos y líneas:** Identificar claramente los puntos promedio con símbolos o barras de error. No unir puntos con líneas continuas sin destacar los datos muestreados. Opcionalmente usar líneas rectas como guía visual. **Prohibido interpolar con funciones arbitrarias (splines, polinomios) sin sustento teórico.**
7. **Escalas:** Usar escalas semilogarítmicas o doble logarítmicas cuando los datos varíen en órdenes de magnitud.
8. **Animaciones en la entrega:** En vivo deben estar embebidas en la presentación. En el PDF a entregar **no** debe haber videos embebidos ni archivos adjuntos: incluir una imagen fija representativa y el enlace explícito a YouTube o similar debajo.

### 2.5 Conclusiones (1 diapositiva)
- Basadas estrictamente en los resultados mostrados.
- No incluir resultados no mostrados, ni hipótesis no comprobadas, ni tareas pendientes o descartadas.

### 2.6 Diapositiva de Cierre
- Puede incluir "Muchas Gracias" o "Gracias por su Atención". No se estila escribir "¿Preguntas?".

---

## 3. Otras Consideraciones

3.1 **Distribución de Exposición:** La charla debe repartirse equitativamente entre los integrantes. Todos deben dominar la totalidad del contenido.  
3.2 **Equilibrio y Respeto:** Tiempos balanceados sin superposiciones ni interrupciones entre compañeros. Responder las preguntas del público en orden.  
3.3 **Revisión Grupal:** Revisar el trabajo antes de entregar para evitar reiterar observaciones de entregas previas (las reiteraciones conllevan penalizaciones).  
3.4 **Consultas:** Evacuar dudas oportunamente con los docentes.  
3.5 **Notación Matemática:**
- **Vectores:** Negrita sin itálica ($\mathbf{x}$).
- **Escalares:** Itálica sin negrita ($t$).
- **Unidades:** Sin negrita ni itálica ($8\text{ m}$, $\text{s}$, $\text{kg}$).
