# Simulación de Sistemas — Teórica 0

## 1. Dictado de la Materia
- Las clases teóricas son guías que deben complementarse con la bibliografía recomendada.
- Flexibilidad para profundizar según el método científico.
- **Trabajo Práctico Final:** Tema a elección entre los vistos en la materia o propuestas relevantes de los alumnos.
- **Lenguaje de programación:** A elección.
- **Modalidad:** Grupos de 2 o 3 personas (identificador `AAAAQQGG` en campus). Usar el identificador de grupo para toda comunicación.
- **Asistencia obligatoria** a las presentaciones de T.P.
- **Entregas:** Vía Campus Virtual (presentación PDF con enlaces explícitos a animaciones, código fuente e informe cuando corresponda). Control automático de plagio y uso responsable de IA.
- Lectura obligatoria de Cronograma, Reglamento y Guías de Formato.

---

## 2. Sistemas y Modelos

### Definición de Sistema
- Conjunto de componentes interrelacionadas que interactúan y funcionan como un todo.
- Pueden ser físicos o conceptuales. Poseen límites, componentes, entradas (inputs), salidas (outputs) y procesos internos.
- Presentan **observables medibles y cuantificables**.
- Pueden interactuar con subsistemas, otros sistemas y el entorno.

### Definición de Modelo
- **Abstracción y simplificación** de un Sistema Real (no es único).
- Relaciona variables de entrada $u(t)$ (estímulo) y salida $y(t)$ (respuesta):
  $$y(t) = g(u(t))$$
- **Objetivo central:** Comprender y predecir el comportamiento del sistema.

### Objetivos de la Teoría de Sistemas
1. **Modelado y Análisis:** Entender el funcionamiento interno.
2. **Diseño:** Crear sistemas derivados bajo las mismas leyes.
3. **Control:** Seleccionar inputs para alcanzar un output específico.
4. **Evaluación de Funcionamiento:** Caracterización exhaustiva bajo diversas condiciones operativas.
5. **Optimización:** Determinar variables y parámetros para maximizar/minimizar una función objetivo.

---

## 3. Dinámica y Espacio de Estados

- **Datos de un sistema:** Medición y registro temporal de variables de entrada y salida.
- **Estado $x(t)$:** Información mínima necesaria tal que $y(t)$ queda unívocamente determinada para $t \ge t_0$ a partir de $x(t_0)$ y $u(t)$. Sus componentes son las *variables de estado*.
- **Dinámica del sistema:** Relaciones matemáticas entre $u(t)$, $y(t)$ y $x(t)$.
- **Espacio de Estados:** Conjunto de todos los posibles valores que puede tomar el vector de estado.
- **Ecuaciones de Estado (generales en tiempo continuo):**
  $$\dot{\mathbf{x}}(t) = \mathbf{f}(\mathbf{x}(t), \mathbf{u}(t), t), \quad \mathbf{x}(t_0) = \mathbf{x}_0$$
  $$\mathbf{y}(t) = \mathbf{g}(\mathbf{x}(t), \mathbf{u}(t), t)$$

### Espacio de Fases
- Representación geométrica de las variables de estado (por ejemplo, posición vs. velocidad: $(x, \dot{x})$).
- **Ejemplos clásicos:**
  - *Oscilador armónico amortiguado:* $m\ddot{x} = -kx - \gamma \dot{x}$ (espiral convergente al origen).
  - *Oscilador de Duffing (no lineal forzado):* $m\ddot{x} = x - x^3 - \gamma \dot{x} + \Gamma \cos(\omega t)$ (comportamiento caótico / atractores extraños).

---

## 4. Clasificación de Modelos

| Criterio | Tipo | Características |
| :--- | :--- | :--- |
| **Memoria** | **Estáticos** | $y(t)$ no depende de $u(\tau < t)$. Ecuaciones algebraicas (ej.: circuito CC). |
| | **Dinámicos** | $y(t)$ depende de la historia previa $u(\tau \le t)$ y del estado inicial. Ecuaciones diferenciales (ej.: oscilador armónico). |
| **Linealidad** | **Lineales** | Cumplen el principio de superposición: $g(a_1 u_1 + a_2 u_2) = a_1 g(u_1) + a_2 g(u_2)$.<br>Forma matricial: $\dot{\mathbf{x}} = \mathbf{A}\mathbf{x} + \mathbf{B}\mathbf{u}$, $\mathbf{y} = \mathbf{C}\mathbf{x} + \mathbf{D}\mathbf{u}$. |
| | **No Lineales** | No cumplen superposición. Pueden presentar caos determinista (sensibilidad a condiciones iniciales con exponente de Lyapunov > 0, transitividad topológica, órbitas periódicas densas, ej.: Atractor de Lorenz). |
| **Naturaleza de Estados** | **Continuos** | Variables de estado continuas en $\mathbb{R}$ (ecuaciones diferenciales). |
| | **Discretos** | Variables toman valores en conjuntos discretos (enteros, ON/OFF, estados lógicos). |
| **Incertidumbre** | **Deterministas** | Comportamiento totalmente fijado por condiciones iniciales y leyes deterministas (Demonio de Laplace). |
| | **Estocásticos** | Entradas o transiciones probabilísticas/aleatorias (Monte Carlo). |
| **Avance Temporal** | **Tiempo Discreto** | El sistema progresa en intervalos regulares $\Delta t$ fijos (ej.: integración numérica). |
| | **Eventos Discretos** | El sistema evoluciona mediante saltos instantáneos al ocurrir eventos específicos (ej.: teoría de colas / servidores). |

---

## 5. Simulación Estocástica y Monte Carlo
- Empleo de secuencias de números pseudoaleatorios para aproximar soluciones numéricas o modelar incertidumbre.
- **Ejemplos:**
  - Estimación geométrica de $\pi$.
  - Transporte y dispersión de neutrones en materia.
  - *Random Walk (Caminata Aleatoria) y Difusión:*
    $$\langle z^2 \rangle \propto 2 d D t$$
    donde $d$ es la dimensión ($2Dt$ en 1D, $4Dt$ en 2D, $6Dt$ en 3D) y $D$ es el coeficiente de difusión (requiere promediar múltiples realizaciones).

---

## 6. Simulación vs. Animación
- **Animación:** Técnica visual para representar ilusión de movimiento (cuadros por segundo basados en persistencia retiniana ~1/10 s).
- **Simulación:** Motor computacional basado en modelos matemáticos (física, ecuaciones diferenciales, agentes) que genera la serie de datos temporales.
- La animación es el **post-procesamiento visual** de los datos calculados por la simulación.

---

## 7. Conceptos de Estadística y Regresiones

- **Herramientas de análisis:** Python, Matlab, R, Octave (evitar planillas de cálculo como Excel para análisis masivo).
- **Métricas estadísticas:**
  - Histograma, Distribución de probabilidad discreta ($y_i = N_i/N$), Función de Densidad de Probabilidad continua PDF ($y_i = N_i / (\Delta x_i N)$ con $\int \text{PDF} = 1$).
- **Reporte de resultados y barras de error:**
  - Reportar observables como promedio y desvío estándar: $\mu \pm \sigma$.
  - Ajustar cifras significativas al error: si $\sigma = 0.3\text{ cm}$, escribir $L = 45.4 \pm 0.3\text{ cm}$ (es incorrecto $45.423457 \pm 0.323428\text{ cm}$).
- **Regresiones y Ajustes:**
  - Ajustar datos **exclusivamente con modelos teóricos fundamentados**, nunca mediante polinomios arbitrarios o splines sin sustento físico.
  - Minimización del error cuadrático:
    $$E(c) = \sum_i \left[ y_i - f(x_i, c) \right]^2$$
    El valor óptimo $c^*$ minimiza $E(c)$.
