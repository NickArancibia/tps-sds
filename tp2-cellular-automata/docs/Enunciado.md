# Simulación de Sistemas
## Trabajo Práctico Nro. 2: Autómatas Celulares
*(Enunciado publicado en CAMPUS el 13/08/2026)*

---

### General

Los entregables del T.P. son:

* **a-** Presentación oral de 13 minutos de duración con las secciones indicadas en el documento `".../Formato_Presentaciones.pdf"`.
* **b-** El documento de la presentación en formato pdf (sin animaciones embebidas, solo links explícitos).
* **c-** El código fuente implementado en un archivo `*.zip`. Solo versión final del motor de simulación (Tamaño del archivo del orden de los kb. No adjuntar historial, documentos, output de simulaciones, etc.).
* **d-** Un informe con las mismas secciones que la presentación y teniendo en cuenta el formato indicado en `".../Formato_Informes.pdf"`.

#### Fecha y Forma de Entrega:
La presentación en pdf (**b**), el código fuente (**c**) y el informe (**d**) deberán ser presentados a través de campus, antes del día **04/09/2026 a las 13 hs**. 

Los archivos deben nombrarse de la siguiente manera:
* `SdS_TP2_2026Q2GXXCSS_Presentación`
* `SdS_TP2_2026Q2GXXCSS_Codigo`
* `SdS_TP2_2026Q2GXXCSS_Informe`

*(donde `XX` es el número de grupo y `SS` es la comisión [“S” o “S2”])*. Las presentaciones orales (**a**) se realizarán durante la clase del mismo día.

Se recuerda que la simulación debe generar un output en formato de archivo de texto. Luego el módulo de animación se ejecuta en forma independiente tomando estos archivos de texto como input. De esta forma, la velocidad de la animación no queda supeditada a la velocidad de la simulación.

Para cada uno de los estudios que se realicen, se debe mostrar animación característica, evolución temporal del observable primario, para explicitar cómo se calcula el observable escalar (promedios o derivadas) que se usará luego al mostrar input vs observable escalar.

---

### Ejercicio: Autómata Off-Lattice: Bandadas de agentes autopropulsados

Implementar el algoritmo de bandadas descripto en la clase teórica 1 [1]. El sistema se simulará en una caja cuadrada de lado $L = 10$ con condiciones periódicas de contorno.

El estudio deberá realizarse para tres densidades: $\rho = 2, 4, 8$. Además del modelo estándar, se estudiará otro tipo de interacción entre las partículas: el modelo de votante (ver al final del TP para detalle de cómo funciona).

Se deberán considerar dos escenarios:
- Modelo estándar [1].
- Modelo de votante [2].

Estudiar el comportamiento del sistema como función del parámetro de ruido $\eta$ para las tres densidades propuestas. Para cada caso presentar:

* **a) Animaciones:**
  A partir de las posiciones y velocidades generadas por las simulaciones hacer animaciones que muestren la dinámica del sistema para pocas situaciones características. Representar cada partícula con un vector (velocidad) cuyo origen estará ubicado en la posición de la partícula para cada tiempo de simulación $t$. Colorear los vectores según el ángulo de la velocidad. Las animaciones características deben estar al inicio de cada estudio (ver `.../GuiaPresentaciones.pdf`).

* **b) Evolución temporal del observable:**
  Para la polarización ($v_a$) determinar en qué tiempos se deben tomar los promedios para calcular el valor escalar (válido) del observable. Mostrar evoluciones temporales características para indicar los criterios usados para medir en el estado estacionario. En estos ejemplos mostrar con líneas verticales el inicio del mismo.

* **c) Curva Input vs Observable:**
  Graficar curvas del observable $v_a$ en función de $\eta$, con las barras de error correspondientes para las distintas densidades.

* **d) Clusters:**
  Definimos un cluster como un conjunto de partículas donde todo par de partículas está conectado por una cadena de saltos entre vecino y vecino (partículas dentro del radio de interacción $r_c$). Considere el tamaño del cluster más grande de la red, y la fracción de nodos que comprende (que notamos $S$) como observable. Para las tres densidades consideradas, graficar la evolución de $S$ en función del tiempo. Graficar el valor medio de $S$ en el estacionario con su desvío en función de $\eta$ para las densidades consideradas, siguiendo un procedimiento equivalente al realizado en (c) para la polarización.

* **e)** Grafique el valor de la polarización $v_a$ en función de la fracción de partículas en la componente gigante $S$, distinguiendo las distintas densidades.

* **f)** Repetir los puntos (**a**, **b**, **c**, **d** y **e**) para el modelo del votante y comparar con el modelo estándar en las figuras construidas en los puntos (**b**, **c**, **d** y **e**).

* **g) Tiempos de ejecución del CIM:**
  Tomar algunas simulaciones que tengan un número de partículas similar a las estudiadas en el TP1 y registrar los tiempos de ejecución del CIM. Luego compararlas con los tiempos obtenidos en el TP1.

---

### Modelo de votante:
En el modelo estándar de Vicsek, cada partícula calcula el promedio de las direcciones de todos sus vecinos y toma esa dirección promedio (más el ruido $\eta$). En el modelo de votante, en cambio, cada partícula no promedia: elige al azar a uno solo de sus vecinos y copia directamente su dirección (más el ruido $\eta$) [2]. La diferencia fundamental es esa: Vicsek promedia entre todos los vecinos, el votante copia a uno solo elegido al azar.

---

### Referencias
* **[1]** Vicsek, T., Czirók, A., Ben-Jacob, E., Cohen, I., & Shochet, O. (1995). Novel type of phase transition in a system of self-driven particles. *Physical review letters*, 75(6), 1226.
* **[2]** Loscar, E. S., Baglietto, G., & Vazquez, F. (2021). Noisy multistate voter model for flocking in finite dimensions. *Physical Review E*, 104(3), 034111.