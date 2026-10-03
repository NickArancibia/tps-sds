# Simulación de Sistemas
## Trabajo Práctico Nro. 4: Dinámica Molecular Regida por el Paso Temporal
*(Enunciado publicado en CAMPUS el 2/10/2026. Transcripción de
`enunciado/TP4_Enunciado_2026Q2.pdf`.)*

---

### General

El sistema a simular, analizar y presentar se describe más abajo.

Se recuerda que la simulación debe generar un *output* en formato de archivo de texto. Luego el
módulo de animación se ejecuta en forma independiente tomando estos archivos de texto como
*input*. De esta forma la velocidad de la animación no queda supeditada a la velocidad de la
simulación.

Los entregables del T.P. son:

* **a-** Presentación oral de 13 minutos de duración con las secciones indicadas en el documento
  `".../Formato_Presentaciones.pdf"`.
* **b-** El documento de la presentación en formato pdf. En las diapositivas con animaciones debe
  verse un fotograma representativo de la misma con su respectivo link explícito a youtube o
  vimeo (NO enviar archivos de animaciones, ni por medio de links, ni subirlos a campus, ni a
  drive, ni embebidos en el pdf).
* **c-** Archivo `.zip` con el código fuente implementado. Únicamente incluir la versión final del
  motor de simulación (no incluir versiones previas, ni código de postprocesamiento, ni outputs,
  ni figuras, ni resultados, ni ninguna documentación extra). **Este archivo debe ser menor a
  100 KB.**

**Al preparar los entregables, seguir los lineamientos establecidos en las Guías de Formato.**

#### Fecha y Forma de Entrega

La presentación en pdf (b) y el código fuente (c) deberán ser presentados **a través de campus**,
antes del día **23/10/2026 a las 13 hs**. Los archivos deben nombrarse de la siguiente manera:

**`SdS_TP4_2026Q2GXXCSS_Presentación.pdf`** y **`SdS_TP4_2026Q2GXXCSS_Codigo.zip`**, donde XX es
el número de grupo y SS es la comisión ("S" or "S2").

---

### Sistema 1) Oscilador Puntual Amortiguado (solución analítica)

Con la finalidad de comparar los errores de los distintos esquemas de integración se estudiará un
sistema con sólo una partícula puntual: el oscilador amortiguado, cuya solución se conoce
analíticamente.

Considerar la solución, los parámetros y las condiciones iniciales dadas en la diapositiva 36 de
la teórica.

**1.1)** Integrar la ecuación de movimiento del oscilador utilizando por lo menos los esquemas:
- Beeman
- Verlet original
- Velocity Verlet
- Euler predictor-corrector

**1.2)** Para cada método y para un dado paso de integración $dt$, se define el error cuadrático
medio (ECM($dt$)) sumando las diferencias al cuadrado entre la solución numérica y la analítica
para todos los pasos temporales y normalizando por el número total de pasos.

Estudiar como disminuye dicho ECM al disminuir el paso de integración ($dt < 10^{-2}$ s) para los
4 métodos (1.1). Usar ejes logarítmicos para poder apreciar las diferencias de error a escalas
pequeñas. ¿Cuál de los esquemas de integración resulta mejor **para este sistema**?

En la presentación, solo se debe mostrar una diapositiva referida al sistema 1: con esta última
figura de ECM vs $dt$ para los 4 métodos de integración solicitados. No mostrar animaciones, ni
introducción, ni ninguna otra información.

---

### Sistema 2) *Billar Circular*

Utilizar dinámica molecular regida por el paso temporal: integrar numéricamente las ecuaciones de
movimiento de Newton, $m\,\ddot{\mathbf{r}}_i = \mathbf{F}_i$, de cada partícula con un paso
temporal fijo $dt$. Utilizar el esquema de Verlet. Imprimir el estado del sistema (posiciones,
velocidades y *color* de las partículas) cada un número entero de pasos, $dt_2 = n\,dt$, para no
llenar el disco rígido, y luego realizar animaciones y los correspondientes análisis a partir de
los estados guardados (*output* primario).

Considerar un dominio de simulación circular con centro en el origen y radio $R = 0.51$ m. Su
área, $\pi R^2 \approx 0.817$ m², es prácticamente igual a la de la mesa de metegol del TP3, de
modo que para un mismo $N$ la densidad es la misma en ambos trabajos. La pared es fija e
indeformable. Dentro del dominio se ubican 2 obstáculos circulares fijos (de masa infinita) del
mismo radio $r$ que las partículas, con centros en $(-x_o, 0)$ y $(+x_o, 0)$, simétricos respecto
del eje $y$, tal como se ilustra en la Fig. 1(a).

> **Figura 1** (en el PDF): (a) Esquema del sistema a simular, a escala: círculo de radio
> $R = 0.51$ m centrado en $O$, obstáculos negros en $\pm x_o$ sobre el eje $x$. Las partículas
> frescas (azules) se convierten en usadas (rojas) al tocar por primera vez uno de los obstáculos
> (negros). (b) Construcción de la partícula imagen para el contacto partícula-pared (esquema no a
> escala): partícula en $\mathbf{r}_i$, punto de contacto $C$ sobre la pared, normal
> $\hat{\mathbf{n}}$, partícula imagen (punteada) en $\mathbf{r}_{img}$ y superposición
> $\xi_{iw}$.

Considerar $N$ partículas de radio $r = 0.0175$ m y masa $m = 0.025$ kg, ubicadas aleatoriamente
dentro del dominio sin solaparse entre sí, ni con los obstáculos, ni con la pared, con velocidades
iniciales de módulo $v_0 = 1$ m/s y ángulo de las direcciones distribuidos uniformemente en el
intervalo $[0, 2\pi)$.

Las partículas interactúan sólo por contacto, mediante un resorte lineal en la dirección normal,
sin fricción ni disipación. La fuerza total sobre la partícula $i$ es:

$$\mathbf{F}_i = \sum_j -k\,\xi_{ij}\,\hat{\mathbf{e}}_{ij}, \qquad
\xi_{ij} = r_i + r_j - |\mathbf{r}_j - \mathbf{r}_i| > 0, \qquad
\hat{\mathbf{e}}_{ij} = \frac{\mathbf{r}_j - \mathbf{r}_i}{|\mathbf{r}_j - \mathbf{r}_i|}$$

donde la suma se extiende sólo a los $j$ en contacto con $i$ ($\xi_{ij} > 0$). Los $j$ pueden ser
otras partículas, los obstáculos (fijos, de radio $r$) o la partícula imagen de la pared descripta
más abajo. Utilizar $k = 10^4$ N/m.

**Contacto con la pared: partícula imagen.** En un billar circular, la normal saliente a la pared
en el punto de contacto $C$ es radial, $\hat{\mathbf{n}} = \mathbf{r}_i/|\mathbf{r}_i|$, y la
partícula $i$ está en contacto con la pared si $|\mathbf{r}_i| > R - r$. El contacto se trata como
un choque contra una partícula virtual fija de radio $r$, cuyo centro se ubica fuera del círculo,
sobre la normal, a una distancia tal que su borde toca justo la pared en $C = R\,\hat{\mathbf{n}}$
(Fig. 1(b)):

$$\mathbf{r}_{img} = (R + r)\,\hat{\mathbf{n}}, \qquad
\xi_{iw} = 2r - |\mathbf{r}_{img} - \mathbf{r}_i| = |\mathbf{r}_i| + r - R$$

Si $\xi_{iw} > 0$ se aplica la misma fuerza de resorte que en el choque partícula-partícula. Como
$\mathbf{r}_i$, $C$ y $\mathbf{r}_{img}$ están alineados sobre la normal, $\xi_{iw}$ coincide con
la superposición de la partícula en la pared y la fuerza resulta puramente normal. Dado que
durante el choque la partícula puede desplazarse tangencialmente, la posición de la partícula
imagen debe recalcularse todos los $dt$.

**Conversión de partículas.** Todas las partículas comienzan en estado "**fresca**" (azul). Cuando
una partícula fresca toca por primera vez cualquiera de los dos obstáculos, pasa al estado
"**usada**" (roja). Sólo se cuenta el primer contacto: una partícula usada nunca vuelve a ser
fresca, pero sigue moviéndose e interactuando normalmente, de manera que $N$ y la densidad del
sistema permanecen constantes.

Definimos $N_u(t)$ como el número acumulado de partículas usadas, $F_u(t) = N_u(t)/N$ como la
fracción de partículas usadas, y $t_{90}$ como el tiempo en el cual $F_u$ alcanza el valor 0.9.

#### 2.1) Paso temporal y tiempo de ejecución en función de N.

**a)** Para el sistema sin obstáculos y $N = 300$, graficar la energía total del sistema en
función del tiempo para distintos valores de $dt < 10^{-2}$ s. Proponer un observable escalar que
caracterice dicha evolución y graficarlo en función de $dt$ para elegir y justificar, a partir de
la conservación de la energía, el $dt$ a utilizar en el resto del trabajo.

**b)** Para el sistema con obstáculos en contacto (a distancia $r$ del centro), simular durante un
tiempo absoluto fijo $t_f = 30$ s para distintos números de partículas $N$ (llegar por lo menos
hasta $N > 600$), realizando al menos 10 realizaciones para cada $N$. Graficar el tiempo de
ejecución promedio en función de $N$ incluyendo su desvío estándar. En el mismo gráfico incluir
los resultados del punto 1.1 del TP3 (dinámica molecular regida por eventos), ejecutados en la
misma computadora. Comparar y discutir cómo escala el costo computacional de cada método con $N$.

#### 2.2) Posición de los obstáculos.

Para el punto 2.2 considerar $N = 100$ partículas y un tiempo máximo de simulación
$t_{max} = 100$ s.

Variar la posición $x_o$ de los obstáculos en forma simétrica, desde la posición más cercana al
centro que permiten sus radios, $x_o = r$ (obstáculos en contacto entre sí), hasta el borde,
$x_o = R - r$ (obstáculos en contacto con la pared). Para cada $x_o$ simular al menos 5
realizaciones. Graficar $F_u(t)$ para pocos valores típicos de $x_o$ y los correspondientes
$\langle t_{90} \rangle$ con su barra de error en función de $x_o$. Si alguna realización no
alcanza $F_u = 0.9$ antes de $t_{max}$, reportarlo e informar $F_u(t_{max})$.

¿Existe una posición de los obstáculos que minimice $\langle t_{90} \rangle$? Justificar con los
resultados obtenidos.

Comparar el resultado final con una densidad menor (por ejemplo, $N = 20$) y discutir si la
respuesta anterior depende de la frecuencia de choques entre partículas.

#### 2.3) Distribución de velocidades.

Para el sistema sin obstáculos y $N = 100$, todas las partículas comienzan con el mismo módulo de
velocidad $v_0$. Calcular, promediando sobre varias realizaciones, la distribución de probabilidad
del módulo de la velocidad, $f(v)$ con $v = |\mathbf{v}|$, para distintos instantes de tiempo,
desde $t = 0$ hasta alcanzar el estado estacionario.

La distribución de Maxwell-Boltzmann para el módulo de la velocidad en 2D es:

$$f(v) = \frac{m\,v}{k_B T}\,\exp\!\left(-\frac{m\,v^2}{2\,k_B T}\right)$$

Ajustar la distribución estacionaria obtenida con esta expresión, tomando como único parámetro
libre la energía térmica efectiva $k_B T$ del sistema, siguiendo las indicaciones del método de
ajuste mostrado en la clase Teórica 0. Comparar el valor ajustado con
$m\langle v^2 \rangle/2 = m v_0^2/2$ y discutir.

#### 2.4) Efecto de la densidad.

**2.4 a)** Tomar los outputs de las simulaciones realizadas en 2.1.b) y reportar
$\langle t_{90} \rangle$ y $\langle t_{100} \rangle$ en función de la densidad. ¿Existe una
densidad óptima? ¿Por qué?

**2.4 b)** (Opcional) Hallar la posición óptima $x_0$ de los obstáculos para distintas densidades
($N$). Para ello hacer un mapa de calor donde para cada punto $(x_0, N)$ se representa
$\langle t_{90} \rangle$ o $\langle t_{100} \rangle$ en la escala de colores.

#### 2.5) Declaración sobre de uso de agentes IA

Se recuerda que el uso de agentes de IA está permitido para ser usado como herramienta/asistente
en la programación de código. Pero no para hacer presentaciones o reportes de forma independiente.
Los agentes de IA no pueden reemplazar al proceso de aprendizaje.

Al finalizar las presentaciones orales, exponer una diapositiva extra que sirva de base para
explicitar que agente y modelo se utilizó y de qué manera.
