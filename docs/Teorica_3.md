# Simulación de Sistemas — Teórica 3: Simulaciones dirigidas por eventos

Resumen de `Teorica_3.pdf` (36 diapositivas). Las fórmulas se transcribieron de las diapositivas
(en el PDF están como imágenes).

## 1. Esquemas de simulación

| Esquema | Cuándo se actualiza el estado |
| :--- | :--- |
| **Dirigida por paso temporal** | Cada cierto $\Delta t$ fijo (TP2). |
| **Dirigida por eventos** | Solo cuando sucede un evento; el paso $t_i$ es variable. |

## 2. Dinámica molecular regida por eventos (Event Driven Molecular Dynamics)

Simular $N$ partículas que colisionan sirve para entender gases, difusión, mecánica estadística,
transiciones de fase, medios granulares; las mismas técnicas se usan en cine y videojuegos.

**Definición del sistema**
- $N$ partículas confinadas en movimiento; cada una con posición, velocidad, radio y masa.
- Interacciones **elásticas** entre ellas y con el contorno (si lo hubiera).
- Sin otras fuerzas: **viajan en línea recta a velocidad constante entre colisiones** (MRU). Con
  gravedad: trayectorias balísticas (parabólicas) entre colisiones.

**Cuándo es válido el enfoque dirigido por eventos**
- Choque instantáneo (duración infinitesimal).
- Tiempo de vuelo entre choques $\gg$ duración del choque.
- Densidad media-baja de partículas.

## 3. Algoritmo (diapositivas 6, 9, 11, ...)

- **A1)** Definir posiciones y velocidades iniciales (y radios, tamaño de la caja).
- **A2)** Calcular el tiempo hasta el primer choque (**evento**) $t_c$: mínimo de todos los tiempos
  de choque entre partículas vecinas y con paredes.
- **A3)** Evolucionar **todas** las partículas según sus ecuaciones de movimiento hasta $t_c$.
- **A4)** Guardar el estado del sistema (posiciones y velocidades) en $t = t_c$ (o cada cierto
  número de eventos).
- **A5)** Determinar las nuevas velocidades después del choque, **solo para las partículas que
  chocaron**.
- **A6)** Volver a A2.

### A1: condiciones iniciales
Se generan partículas de a una, con posición y velocidad aleatorias dentro del dominio, tal que la
nueva ($i$) no se superponga con ninguna existente ($j$) ni con las paredes:
$$(x_i - x_j)^2 + (y_i - y_j)^2 > (R_i + R_j)^2 .$$

### A3: vuelo libre (sin gravedad)
$$x_i(t_c) = x_i(0) + v_{x_i} t_c, \qquad y_i(t_c) = y_i(0) + v_{y_i} t_c .$$

### A2: tiempo de choque con paredes (MRU)
Sean $x_{p1} < x_{p2}$ las coordenadas de las paredes verticales:
- si $v_x > 0$: $\;(x_{p2} - R) = x(0) + v_x t \Rightarrow t_c = (x_{p2} - R - x(0)) / v_x$
- si $v_x < 0$: $\;(x_{p1} + R) = x(0) + v_x t \Rightarrow t_c = (x_{p1} + R - x(0)) / v_x$
- ídem para paredes horizontales con la coordenada $y$ (si $v_x = 0$, nunca choca con esa pared).

### A2: tiempo de choque entre partículas (MRU)
Condición de contacto: $(x_i - x_j)^2 + (y_i - y_j)^2 = (R_i + R_j)^2$ con $x_i(t) = x_i(0) + v_x t$,
etc. Reemplazando y simplificando:

$$
t_c = \begin{cases}
\infty & \text{si } \Delta\mathbf{v}\cdot\Delta\mathbf{r} \ge 0 \\
\infty & \text{si } d < 0 \\
-\dfrac{\Delta\mathbf{v}\cdot\Delta\mathbf{r} + \sqrt{d}}{\Delta\mathbf{v}\cdot\Delta\mathbf{v}} & \text{en otro caso}
\end{cases}
\qquad
d = (\Delta\mathbf{v}\cdot\Delta\mathbf{r})^2 - (\Delta\mathbf{v}\cdot\Delta\mathbf{v})\,(\Delta\mathbf{r}\cdot\Delta\mathbf{r} - \sigma^2)
$$

siendo $\sigma = R_i + R_j$, $\Delta\mathbf{r} = (\Delta x, \Delta y) = (x_j - x_i,\; y_j - y_i)$,
$\Delta\mathbf{v} = (\Delta v_x, \Delta v_y) = (v_{x_j} - v_{x_i},\; v_{y_j} - v_{y_i})$,
$\Delta\mathbf{r}\cdot\Delta\mathbf{r} = \Delta x^2 + \Delta y^2$,
$\Delta\mathbf{v}\cdot\Delta\mathbf{v} = \Delta v_x^2 + \Delta v_y^2$,
$\Delta\mathbf{v}\cdot\Delta\mathbf{r} = \Delta v_x \Delta x + \Delta v_y \Delta y$.

- $\Delta\mathbf{v}\cdot\Delta\mathbf{r} \ge 0$: se alejan (o se mueven en paralelo), nunca chocan.
- $d < 0$: se acercan pero pasan de largo (parámetro de impacto mayor que $\sigma$).

### A5: velocidades post-choque

**Partícula–pared** (velocidad $(v_x, v_y)$):
- pared vertical $\rightarrow (-v_x, v_y)$
- pared horizontal $\rightarrow (v_x, -v_y)$

**Partícula–partícula de distinta masa** (choque elástico, sin fricción ni rotación), a partir de
la conservación del impulso $(J_x, J_y)$:
$$J_x = \frac{J\,\Delta x}{\sigma}, \quad J_y = \frac{J\,\Delta y}{\sigma}, \qquad
J = \frac{2\, m_i\, m_j\, (\Delta\mathbf{v}\cdot\Delta\mathbf{r})}{\sigma\,(m_i + m_j)}$$
(símbolos como en la diapositiva 14, evaluados en el instante del choque). Luego:
$$v_{x_i}^d = v_{x_i}^a + J_x/m_i, \quad v_{y_i}^d = v_{y_i}^a + J_y/m_i, \qquad
v_{x_j}^d = v_{x_j}^a - J_x/m_j, \quad v_{y_j}^d = v_{y_j}^a - J_y/m_j .$$

**Caso particular: obstáculos fijos, partícula móvil única** (diapositivas 21–24). Se definen el
versor normal al choque $\hat{e}_n = (e_{nx}, e_{ny})$ (del obstáculo hacia la partícula) y el
tangencial $\hat{e}_t = (-e_{ny}, e_{nx})$; $\alpha$ es el ángulo entre $\hat{e}_n$ y el eje $x$.

**Operador de colisión**:
$$\mathbf{v}^d = \mathbf{R}(-\alpha)\,\mathbf{S}(c_n, c_t)\,\mathbf{R}(\alpha)\,\mathbf{v}^a$$
donde $\mathbf{v}^a$ y $\mathbf{v}^d$ son las velocidades antes ($t_c^-$) y después ($t_c^+$) del
choque, $\mathbf{R}$ es la matriz de rotación y $\mathbf{S}$ la matriz de colisión:
$$\mathbf{R}(\alpha) = \begin{pmatrix} \cos\alpha & \sin\alpha \\ -\sin\alpha & \cos\alpha \end{pmatrix},
\qquad
\mathbf{S}(c_n, c_t) = \begin{pmatrix} -c_n & 0 \\ 0 & c_t \end{pmatrix}.$$
$c_n$ y $c_t$ son los **coeficientes de restitución** normal y tangencial, con valores en $[0, 1)$
que indican la disminución de velocidad por disipación de energía ($c < 1$). **El caso $c = 1$
indica choque elástico.** Desarrollando:
$$\mathbf{v}^d = \begin{pmatrix}
-c_n\cos^2\alpha + c_t\sin^2\alpha & -(c_n + c_t)\sin\alpha\cos\alpha \\
-(c_n + c_t)\sin\alpha\cos\alpha & -c_n\sin^2\alpha + c_t\cos^2\alpha
\end{pmatrix}\mathbf{v}^a .$$
Interpretación: se rota la velocidad al sistema (normal, tangente), se invierte la componente
normal (escalada por $c_n$) y se conserva la tangencial (escalada por $c_t$), y se vuelve a rotar.
Con $c_n = c_t = 1$ equivale a la reflexión especular $\mathbf{v}^d = \mathbf{v}^a - 2(\mathbf{v}^a\cdot\hat{e}_n)\hat{e}_n$,
que coincide con el límite $m_j \to \infty$ de la fórmula del impulso.

## 4. Repaso para el T.P.: movimiento browniano (Einstein)

Desplazamiento cuadrático medio (DCM) y coeficiente de difusión $D$:
$$\langle z^2 \rangle = 2 D t$$
(por cada coordenada; en $d$ dimensiones $\langle |\Delta\mathbf{r}|^2 \rangle = 2 d D t$, ver
Teórica 0). Calcular varios DCM para varios valores de $t$ en la misma corrida y en varias
corridas, para realizar el **ajuste lineal** de los datos (mínimo del error cuadrático, Teórica 0).

## 5. Partículas en presencia de gravedad (no aplica al TP3)

- Trayectorias parabólicas entre choques: $x(t_c) = x(0) + v_x t_c$,
  $y(t_c) = y(0) + v_y(0) t_c - \tfrac{1}{2} g t_c^2$.
- Al reemplazar en la condición de contacto se obtiene un **polinomio de grado 4** en $t$, que se
  resuelve analítica o numéricamente. Los vecinos se seleccionan eficientemente (CIM).
- Las colisiones en sí (partícula–partícula y partícula–pared) se tratan igual que sin gravedad:
  la gravedad solo cambia el vuelo y los tiempos entre choques.
- Ejemplo: **billar de Galton** (arreglo hexagonal de obstáculos circulares por el que caen
  discos; distribución gaussiana a la salida).
