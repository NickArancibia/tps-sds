# Simulación de Sistemas — Teórica 4: Simulaciones dirigidas por el paso temporal

Resumen de `Teorica_4.pdf` (47 diapositivas). Las fórmulas se transcribieron de las diapositivas
(en el PDF están como imágenes). Las notas marcadas **[nota]** no están en las diapositivas: son
aclaraciones propias para la implementación.

## 1. Dinámica molecular dirigida por el paso temporal (diapositivas 2–4)

- $N$ partículas interactúan mediante fuerzas que en general dependen de la distancia entre ellas.
- Se integran numéricamente las ecuaciones de movimiento; el tiempo avanza en cantidades discretas
  $\Delta t$ (el **paso temporal**).
- Las interacciones pueden ser de largo o de corto alcance. Los "choques" **no son instantáneos**:
  duran varios pasos temporales.

**Cuándo conviene** (frente a la dirigida por eventos, Teórica 3):
- Partículas en contacto la mayor parte del tiempo, o bien
- interacciones de largo alcance, o bien
- interacciones de corto alcance pero con alta densidad.
- Tiempo de vuelo entre choques $\ll$ duración del choque.

**Interacciones de a pares**: la fuerza total sobre $i$ es la suma de las fuerzas de cada
partícula con la que interactúa,
$$\mathbf{F}_i = \sum_{j \ne i} \mathbf{F}_{ij} \qquad (\text{ej.: } \mathbf{F}_i = \mathbf{F}_{ij} + \mathbf{F}_{ik}).$$

Notación de las diapositivas: $\mathbf{f}_i(t)$ es la fuerza sobre $i$, $m_i$ su masa,
$\mathbf{a}_i = \mathbf{f}_i/m_i$, y $\mathbf{r}_q = d^q\mathbf{r}/dt^q$ (así
$\mathbf{r}_1 = \mathbf{v}$, $\mathbf{r}_2 = \mathbf{a}$).

## 2. Base: desarrollo de Taylor (diapositivas 5–7, 12)

$$\mathbf{r}_i(t+\Delta t) = \mathbf{r}_i(t) + \Delta t\,\mathbf{v}_i(t) + \frac{\Delta t^2}{2 m_i}\mathbf{f}_i(t)
+ \frac{\Delta t^3}{3!}\dddot{\mathbf{r}}_i(t) + O(\Delta t^4)$$
$$\mathbf{v}_i(t+\Delta t) = \mathbf{v}_i(t) + \frac{\Delta t}{m_i}\mathbf{f}_i(t)
+ \frac{\Delta t^2}{2}\ddot{\mathbf{v}}_i(t) + \frac{\Delta t^3}{3!}\dddot{\mathbf{v}}_i(t) + O(\Delta t^4)$$

Cuantos más términos se conservan, mejor aproxima la serie a la función en un entorno de $t$
(diapositiva 7: ejemplo gráfico con órdenes 1, 2, ...).

## 3. Algoritmos tipo Euler (diapositivas 8–10)

### Euler (el más simple y menos preciso)
$$\mathbf{r}_i(t+\Delta t) = \mathbf{r}_i(t) + \Delta t\,\mathbf{v}_i(t) + \frac{\Delta t^2}{2 m_i}\mathbf{f}_i(t) + O(\Delta t^3)$$
$$\mathbf{v}_i(t+\Delta t) = \mathbf{v}_i(t) + \frac{\Delta t}{m_i}\mathbf{f}_i(t) + O(\Delta t^2)$$
No es reversible en el tiempo ni preserva el volumen en el espacio de fases.

### Euler modificado
Usa la velocidad **actualizada** en vez de la del paso anterior:
$$\mathbf{v}_i(t+\Delta t) = \mathbf{v}_i(t) + \frac{\Delta t}{m_i}\mathbf{f}_i(t)$$
$$\mathbf{r}_i(t+\Delta t) = \mathbf{r}_i(t) + \Delta t\,\mathbf{v}_i(t+\Delta t) + \frac{\Delta t^2}{2 m_i}\mathbf{f}_i(t)$$
**[nota]** Así figura en la diapositiva 10 (con el término $\Delta t^2 \mathbf{f}/2m$). El Euler
semi-implícito (simpléctico) habitual en la literatura no lleva ese término.

## 4. Algoritmos tipo Verlet (diapositivas 11–20)

### Verlet original
Sumando los desarrollos de Taylor en $+\Delta t$ y $-\Delta t$:
$$\mathbf{r}_i(t+\Delta t) = 2\mathbf{r}_i(t) - \mathbf{r}_i(t-\Delta t) + \frac{\Delta t^2}{m_i}\mathbf{f}_i(t) + O(\Delta t^4)$$
Restándolos:
$$\mathbf{v}_i(t) = \frac{\mathbf{r}_i(t+\Delta t) - \mathbf{r}_i(t-\Delta t)}{2\Delta t} + O(\Delta t^3)$$
**[nota]** La diapositiva 15 escribe $O(\Delta t^3)$: es el error del numerador; al dividir por
$2\Delta t$ el error de la velocidad es $O(\Delta t^2)$.

- No hace falta calcular velocidades para obtener las trayectorias; sí para observables como la
  energía cinética.
- **Primer paso**: hace falta $\mathbf{r}(t-\Delta t)$; se estima con Euler evaluado en $-\Delta t$:
  $\mathbf{r}(-\Delta t) = \mathbf{r}(0) - \Delta t\,\mathbf{v}(0) + \frac{\Delta t^2}{2m}\mathbf{f}(0)$.
- **[nota]** Si la fuerza depende de la velocidad, $\mathbf{f}(t)$ necesita $\mathbf{v}(t)$, que
  en Verlet recién se conoce después de calcular $\mathbf{r}(t+\Delta t)$. Hay que decidir y
  documentar cómo se aproxima $\mathbf{v}(t)$ dentro de la fuerza.

### Leap-frog
$$\mathbf{v}_i\!\left(t+\tfrac{\Delta t}{2}\right) = \mathbf{v}_i\!\left(t-\tfrac{\Delta t}{2}\right) + \frac{\Delta t}{m_i}\mathbf{f}_i(t),
\qquad
\mathbf{r}_i(t+\Delta t) = \mathbf{r}_i(t) + \Delta t\,\mathbf{v}_i\!\left(t+\tfrac{\Delta t}{2}\right)$$
Velocidad en el tiempo entero:
$\mathbf{v}_i(t) = \left[\mathbf{v}_i(t-\tfrac{\Delta t}{2}) + \mathbf{v}_i(t+\tfrac{\Delta t}{2})\right]/2$.

### Velocity-Verlet
Provee posiciones y velocidades en el mismo paso temporal:
$$\mathbf{r}_i(t+\Delta t) = \mathbf{r}_i(t) + \Delta t\,\mathbf{v}_i(t) + \frac{\Delta t^2}{2 m_i}\mathbf{f}_i(t) + O(\Delta t^3)$$
$$\mathbf{v}_i(t+\Delta t) = \mathbf{v}_i(t) + \frac{\Delta t}{2 m_i}\left[\mathbf{f}_i(t) + \mathbf{f}_i(t+\Delta t)\right] + O(\Delta t^2)$$
En dos medios pasos: (1) $\mathbf{v}(t+\Delta t/2) = \mathbf{v}(t) + \mathbf{a}(t)\,\Delta t/2$;
se calcula $\mathbf{r}(t+\Delta t)$ y con ella $\mathbf{a}(t+\Delta t)$;
(2) $\mathbf{v}(t+\Delta t) = \mathbf{v}(t+\Delta t/2) + \mathbf{a}(t+\Delta t)\,\Delta t/2$.
Muy estable y preserva volúmenes en el espacio de fases (**integrador simpléctico**).

Diapositiva 18: esquema (tabla $\mathbf{r}, \mathbf{v}, \mathbf{a}$ × $t-\delta t, t, t+\delta t$)
de qué variables usa cada variante en cada sub-paso.

### Beeman
$$\mathbf{r}(t+\Delta t) = \mathbf{r}(t) + \mathbf{v}(t)\Delta t + \frac{2}{3}\mathbf{a}(t)\Delta t^2 - \frac{1}{6}\mathbf{a}(t-\Delta t)\Delta t^2$$
$$\mathbf{v}(t+\Delta t) = \mathbf{v}(t) + \frac{1}{3}\mathbf{a}(t+\Delta t)\Delta t + \frac{5}{6}\mathbf{a}(t)\Delta t - \frac{1}{6}\mathbf{a}(t-\Delta t)\Delta t$$

### Beeman para fuerzas que dependen de la velocidad (variante predictor-corrector)
1. $\mathbf{r}(t+\Delta t) = \mathbf{r}(t) + \mathbf{v}(t)\Delta t + \frac{2}{3}\mathbf{a}(t)\Delta t^2 - \frac{1}{6}\mathbf{a}(t-\Delta t)\Delta t^2 + O(\Delta t^4)$
2. Velocidad predicha:
   $\mathbf{v}^{p}(t+\Delta t) = \mathbf{v}(t) + \frac{3}{2}\mathbf{a}(t)\Delta t - \frac{1}{2}\mathbf{a}(t-\Delta t)\Delta t + O(\Delta t^3)$
3. Con $\mathbf{r}(t+\Delta t)$ y $\mathbf{v}^{p}(t+\Delta t)$ se calcula $\mathbf{a}(t+\Delta t)$.
4. Velocidad corregida:
   $\mathbf{v}^{c}(t+\Delta t) = \mathbf{v}(t) + \frac{1}{3}\mathbf{a}(t+\Delta t)\Delta t + \frac{5}{6}\mathbf{a}(t)\Delta t - \frac{1}{6}\mathbf{a}(t-\Delta t)\Delta t + O(\Delta t^3)$

**[nota]** Beeman necesita $\mathbf{a}(t-\Delta t)$ en el primer paso; las diapositivas no dicen
cómo obtenerla. Opción análoga a Verlet: estimar $\mathbf{r}(-\Delta t), \mathbf{v}(-\Delta t)$
con Euler en $-\Delta t$ y evaluar la fuerza ahí.

## 5. Algoritmos predictor-corrector (diapositivas 21–30)

Tres pasos, partiendo de $\mathbf{r}_i(t)$ y $\mathbf{v}_i(t)$:
1. **Predecir** $\mathbf{r}_i(t+\Delta t)$ y $\mathbf{v}_i(t+\Delta t)$.
2. **Evaluar** las fuerzas $\mathbf{f}_i(t+\Delta t)$ con las predicciones.
3. **Corregir** las predicciones combinando valores previos y predichos.

### Euler predictor-corrector
1. $\mathbf{v}_i^p(t+\Delta t) = \mathbf{v}_i(t) + \mathbf{a}_i(t)\Delta t$, $\;\mathbf{r}_i^p(t+\Delta t) = \mathbf{r}_i(t) + \mathbf{v}_i(t)\Delta t$
2. $\mathbf{f}_i(\mathbf{r}_i^p, \mathbf{v}_i^p) \Rightarrow \mathbf{a}_i(t+\Delta t)$
3. $\mathbf{v}_i(t+\Delta t) = \mathbf{v}_i(t) + \mathbf{a}_i(t+\Delta t)\Delta t$, $\;\mathbf{r}_i(t+\Delta t) = \mathbf{r}_i(t) + \mathbf{v}_i(t+\Delta t)\Delta t$

### Gear predictor-corrector (orden 5)
**1) Predecir** (Taylor de cada derivada, $q = 0..5$):
$$\mathbf{r}^p_q(t+\Delta t) = \sum_{k=q}^{5} \mathbf{r}_k(t)\,\frac{\Delta t^{\,k-q}}{(k-q)!}$$
es decir:
- $\mathbf{r}^p = \mathbf{r} + \mathbf{r}_1\Delta t + \mathbf{r}_2\frac{\Delta t^2}{2!} + \mathbf{r}_3\frac{\Delta t^3}{3!} + \mathbf{r}_4\frac{\Delta t^4}{4!} + \mathbf{r}_5\frac{\Delta t^5}{5!}$
- $\mathbf{r}^p_1 = \mathbf{r}_1 + \mathbf{r}_2\Delta t + \mathbf{r}_3\frac{\Delta t^2}{2!} + \mathbf{r}_4\frac{\Delta t^3}{3!} + \mathbf{r}_5\frac{\Delta t^4}{4!}$
- $\mathbf{r}^p_2 = \mathbf{r}_2 + \mathbf{r}_3\Delta t + \mathbf{r}_4\frac{\Delta t^2}{2!} + \mathbf{r}_5\frac{\Delta t^3}{3!}$
- $\mathbf{r}^p_3 = \mathbf{r}_3 + \mathbf{r}_4\Delta t + \mathbf{r}_5\frac{\Delta t^2}{2!}$
- $\mathbf{r}^p_4 = \mathbf{r}_4 + \mathbf{r}_5\Delta t$
- $\mathbf{r}^p_5 = \mathbf{r}_5$

**2) Evaluar**: con las variables predichas se calcula la fuerza y la aceleración
$\mathbf{a}(t+\Delta t)$; se define
$$\Delta\mathbf{a} = \mathbf{a}(t+\Delta t) - \mathbf{a}^p(t+\Delta t) = \mathbf{r}_2(t+\Delta t) - \mathbf{r}^p_2(t+\Delta t),
\qquad \Delta\mathbf{R2} = \frac{\Delta\mathbf{a}\,(\Delta t)^2}{2!}.$$

**3) Corregir**:
$$\mathbf{r}^c_q = \mathbf{r}^p_q + \alpha_q\,\Delta\mathbf{R2}\,\frac{q!}{(\Delta t)^q}$$
($\mathbf{r}^c = \mathbf{r}^p + \alpha_0\Delta\mathbf{R2}$, $\;\mathbf{r}^c_1 = \mathbf{r}^p_1 + \alpha_1\Delta\mathbf{R2}/\Delta t$, ...).

**Coeficientes $\alpha_q$** — fuerzas que dependen **solo de las posiciones**, $\mathbf{r}_2 = f(\mathbf{r})$:

| Orden | $\alpha_0$ | $\alpha_1$ | $\alpha_2$ | $\alpha_3$ | $\alpha_4$ | $\alpha_5$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 2 | 0 | 1 | 1 | | | |
| 3 | 1/6 | 5/6 | 1 | 1/3 | | |
| 4 | 19/120 | 3/4 | 1 | 1/2 | 1/12 | |
| 5 | 3/20 | 251/360 | 1 | 11/18 | 1/6 | 1/60 |

Fuerzas que dependen de **posiciones y velocidades**, $\mathbf{r}_2 = f(\mathbf{r}, \mathbf{r}_1)$:
igual a la anterior salvo $\alpha_0$ de orden 4 y 5.

| Orden | $\alpha_0$ | $\alpha_1$ | $\alpha_2$ | $\alpha_3$ | $\alpha_4$ | $\alpha_5$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 2 | 0 | 1 | 1 | | | |
| 3 | 1/6 | 5/6 | 1 | 1/3 | | |
| 4 | **19/90** | 3/4 | 1 | 1/2 | 1/12 | |
| 5 | **3/16** | 251/360 | 1 | 11/18 | 1/6 | 1/60 |

**Primer paso**: las derivadas de orden mayor a 2 se obtienen derivando la expresión de la fuerza.
Ejemplo, una partícula con fuerza elástica $\mathbf{F} = m\mathbf{r}_2 = -k(\mathbf{r} - \mathbf{r}^0)$:
$$\mathbf{r}_2 = -\tfrac{k}{m}(\mathbf{r} - \mathbf{r}^0),\quad
\mathbf{r}_3 = -\tfrac{k}{m}\mathbf{r}_1,\quad
\mathbf{r}_4 = -\tfrac{k}{m}\mathbf{r}_2 = \left(\tfrac{k}{m}\right)^2(\mathbf{r} - \mathbf{r}^0),\quad
\mathbf{r}_5 = -\tfrac{k}{m}\mathbf{r}_3 = \left(\tfrac{k}{m}\right)^2\mathbf{r}_1 .$$
Con fuerzas más complejas se pueden inicializar las derivadas superiores en cero.

**[nota]** Con fuerza amortiguada $m\mathbf{r}_2 = -k\mathbf{r} - \gamma\mathbf{r}_1$ el mismo
procedimiento da la recurrencia $\mathbf{r}_{q+2} = -\tfrac{k}{m}\mathbf{r}_q - \tfrac{\gamma}{m}\mathbf{r}_{q+1}$.

## 6. Paso temporal (diapositivas 31–33)

- **Demasiado corto**: simulación innecesariamente lenta. **Demasiado largo**: errores por las
  aproximaciones, "explosiones". **Justo**: errores aceptables y máxima velocidad.
- Diferenciar el **paso de integración** $\Delta t$ del **paso de guardado** del estado
  $\Delta t_2 = k\,\Delta t$, con $k \in \mathbb{N}$. Se guarda cuando
  $t/\Delta t_2 = \mathrm{round}(t/\Delta t_2)$ (con $t = \sum \Delta t$).
- **[nota]** En el código conviene un contador entero de pasos (`paso % k == 0`) en vez de
  comparar flotantes acumulados.

## 7. Verificación del error (diapositivas 34–35)

- **Caso simple**: comparar con la solución analítica.
- **Caso realista conservativo**: conservación de la energía del sistema,
  $E_\text{cinética} + E_\text{potencial} = \text{cte}$.
- **Sistemas no conservativos**: repetir con $\Delta t$ cada vez menores hasta que los resultados
  cambien menos que un error dado.

## 8. Casos de estudio (diapositivas 36–42)

### 8.1 Oscilador amortiguado (una partícula, comparar con la solución analítica)
$$f = m a = m r_2 = -k r - \gamma r_1$$
- Parámetros: $m = 70$ kg, $k = 10^4$ N/m, $\gamma = 100$ kg/s, $t_f = 5$ s.
- Condiciones iniciales: $r(0) = 1$ m, $v(0) = -A\gamma/(2m)$ m/s.
- Solución analítica:
$$r(t) = A\,\exp\!\left(-\frac{\gamma}{2m}t\right)\cos\!\left(\sqrt{\frac{k}{m} - \frac{\gamma^2}{4m^2}}\;t\right)$$
  con $A = 1$ m (de $r(0) = 1$ m).
- Diapositiva 38: posición (m) vs. tiempo (s) para analítica, Euler predictor-corrector
  modificado, Verlet y Gear predictor-corrector; a escala global se superponen, con zoom
  (alrededor de $t \approx 3.15$ s) se distinguen las diferencias entre métodos.
- **[nota]** Con estos parámetros: $\omega = \sqrt{k/m - \gamma^2/4m^2} \approx 11.93$ rad/s
  (período $\approx 0.527$ s), tiempo de decaimiento $2m/\gamma = 1.4$ s; subamortiguado. La fuerza
  depende de la velocidad: Gear con la tabla de $\mathbf{r}_2 = f(\mathbf{r}, \mathbf{r}_1)$ y
  Beeman en su variante predictor-corrector.

### 8.2 Gas de Lennard-Jones (potencial 12-6)
$$V_{LJ}(r) = 4\varepsilon\left[\left(\frac{\sigma}{r}\right)^{12} - \left(\frac{\sigma}{r}\right)^{6}\right]
= \varepsilon\left[\left(\frac{r_m}{r}\right)^{12} - 2\left(\frac{r_m}{r}\right)^{6}\right]$$
$\varepsilon$: profundidad del pozo; $r$: distancia entre partículas; $\sigma$: distancia a la
que el potencial se anula; $r_m = 2^{1/6}\sigma$: posición del mínimo.
$$F(r) = -V'(r) = \frac{12\varepsilon}{r_m}\left[\left(\frac{r_m}{r}\right)^{13} - \left(\frac{r_m}{r}\right)^{7}\right]$$
$F(r_m) = 0$: $r_m$ es un punto de equilibrio. ($F > 0$ repulsiva para $r < r_m$.)

### 8.3 Sistema gravitatorio
$$\mathbf{F}_{ij} = G\,\frac{m_i m_j}{r_{ij}^2}\,\mathbf{e}_{ij}, \qquad E^{pot}_{ij} = -G\,\frac{m_i m_j}{r_{ij}}$$
$m$: masa de cada partícula; $r_{ij}$: distancia entre $i$ y $j$; $G$: constante de gravitación
universal, $G = 6.693 \cdot 10^{-11}\ \mathrm{m^3/(kg\,s^2)}$ (valor de la diapositiva; CODATA:
$6.674 \cdot 10^{-11}$).

### 8.4 Restitución normal (contacto elástico entre discos)
$$\mathbf{F}_N = -k_n\,\xi\,\hat{\mathbf{e}}^n, \qquad \xi_{ij} = R_i + R_j - |\mathbf{r}_j - \mathbf{r}_i|, \qquad
E^{pot} = \tfrac{1}{2}k_n\xi^2$$
$$e^n_x = \frac{x_j - x_i}{|\mathbf{r}_j - \mathbf{r}_i|}, \qquad e^n_y = \frac{y_j - y_i}{|\mathbf{r}_j - \mathbf{r}_i|}$$
$\xi_{ij}$ es la superposición (solo hay fuerza si $\xi_{ij} > 0$); $\hat{\mathbf{e}}^n$ apunta de
$i$ hacia $j$, así que $\mathbf{F}_N$ sobre $i$ lo empuja en sentido opuesto a $j$.

## 9. Suma de fuerzas (diapositivas 43–46)

Antes de sumar, para cada partícula se proyectan las fuerzas normal y tangencial generadas por
cada partícula en contacto sobre las componentes cartesianas:
$$F_x = F_N e^n_x, \quad F_y = F_N e^n_y, \qquad e^t_x = -e^n_y, \quad e^t_y = e^n_x .$$
Finalmente, la fuerza total sobre cada partícula $i$ debido a la interacción con las demás
partículas $j$ resulta (diapositiva 46):
$$\mathbf{F}^{Tot}_i = \sum_j \mathbf{F}_{N\,ij}, \qquad
F^{Tot}_{i\,x} = \sum_j F_{N\,ij}\,e^n_{x\,ij}, \qquad
F^{Tot}_{i\,y} = \sum_j F_{N\,ij}\,e^n_{y\,ij}$$
