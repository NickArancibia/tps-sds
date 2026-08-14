# Simulación de Sistemas — Teórica 1: Sistemas Físicos y Cell Index Method

## 1. Sistemas de Muchas Partículas

- **Problema de 1 y 2 cuerpos:** Integrables analíticamente.
- **Problema de 3 o más cuerpos ($N$ cuerpos):** No integrables analíticamente; requieren integración numérica mediante técnicas de **Dinámica Molecular**.
- **Sistemas macroscópicos con $N \gg 1$:** Mecánica Estadística y Teoría Cinética.

### Ejemplos en la Naturaleza e Ingeniería:
- **Interacción Gravitatoria:** Galaxias (ej.: Galaxia M101 con $\sim 10^{12}$ estrellas).
- **Flujos Granulares:** Descarga de silos, relojes de arena.
- **Materia Activa:**
  - Sistemas formados por unidades auto-propulsadas capaces de consumir energía interna o del entorno para generar movimiento sistemático.
  - Inyección de energía local/microscópica a nivel de agente.
  - Propiedades fuera del equilibrio: comportamientos colectivos emergentes, transiciones orden-desorden, formación de patrones.
  - *Ejemplos biológicos:* Turbulencia bacteriana, cardúmenes, bandadas de estorninos (*murmurations*).
  - *Dinámica peatonal / Evacuaciones:*
    - **Social Force Model (Helbing):**
      $$m_i \ddot{\mathbf{r}}_i = \mathbf{F}_{\text{GRANULAR}} + \mathbf{F}_{\text{SOCIAL}} + \mathbf{F}_{\text{DRIVING}} + \mathbf{F}_{\text{FLUCTUATION}}$$
    - Fenómeno *Freezing by Heating* (bloqueo por pánico/fluctuaciones térmicas).
    - Efecto *Faster is Slower* (en agentes egoístas, intentar salir más rápido congestiona la salida y aumenta el tiempo total).
    - Efecto *Faster is Faster* (en insectos sociales como hormigas, con comportamiento no egoísta).

---

## 2. Detección de Vecinos y "Cell Index Method" (CIM)

En sistemas de partículas interactuantes de corto alcance, solo se requiere calcular distancias entre partículas vecinas ($r_{ij} < r_c$).

### Comparación Algorítmica:
- **Fuerza Bruta:** Calcula distancias de todos los pares. Complejidad $O(N^2)$.
- **Cell Index Method (CIM):** Divide el espacio de simulación (caja de lado $L$) en una grilla de $M \times M$ celdas. Complejidad $O(N)$ a densidad constante.

### Criterio de Selección de Grilla:
- Longitud de lado de celda: $L / M$.
- Condición fundamental para buscar vecinos solo en celdas adyacentes e inmediata:
  $$\frac{L}{M} \ge r_c + 2 r_{\max}$$
  *(o $L/M \ge r_c$ para partículas puntuales).*
  Si $L/M < r_c$, las partículas podrían interactuar a través de celdas no contiguas, invalidando la búsqueda de vecindad local.

### Optimizaciones del CIM:
1. **Simetría ($d_{ij} = d_{ji}$):** Para cada celda central, basta con revisar la celda propia y 4 celdas vecinas (ej.: Este, Noreste, Norte, Noroeste). Esto reduce los cálculos a la mitad.
2. **Condiciones Periódicas de Contorno (PBC):** Aplicar periodicidad modular en los bordes de la grilla.

### Estructura de Salida (Lista de Vecinos):
Para cada partícula $i$, almacenar los identificadores de sus vecinos a distancia $d \le r_c$:
```text
[id_i] -> [vecino_1, vecino_2, ...]
1      -> 5, 17, 32
2      -> (sin vecinos)
3      -> 8, 12
...
```

---

## 3. Trabajo Práctico: Implementación CIM

- Implementar el Cell Index Method y contrastar tiempos de ejecución frente a Fuerza Bruta.
- Evaluar la variación del tiempo de cómputo en función de $N$ y del número de celdas $M$.
- Considerar partículas con radio finito con distancia borde a borde:
  $$d_{\text{borde}}(i, j) = \|\mathbf{r}_i - \mathbf{r}_j\| - (r_i + r_j) < r_c$$
- Desarrollar un visualizador de vecinos interactivo.

---

## 4. Arquitectura de Simulación y Formato de Archivos

Separar estrictamente el **motor de simulación** del **post-procesamiento/visualización**.

### Formato de Archivo Estático (Propiedades fijas):
```text
N        (Número total de partículas)
L        (Lado del área cuadrada)
r_1 c_1  (radio y color de partícula 1)
r_2 c_2  (radio y color de partícula 2)
...
r_N c_N
```

### Formato de Archivo Dinámico (Evolución temporal):
```text
t_0
x_1 y_1 vx_1 vy_1
x_2 y_2 vx_2 vy_2
...
x_N y_N vx_N vy_N
t_1
x_1 y_1 vx_1 vy_1
...
```

---

## 5. Pautas para las Presentaciones Orales (TP2 en adelante)

- **Estructura de la Presentación:**
  1. *Introducción / Sistema Real* (< 1 min)
  2. *Implementación* (~3 min): Diagramas UML, arquitectura, algoritmos.
  3. *Simulaciones* (~2 min): Parámetros, variables y formulación de observables.
  4. *Resultados* (~8 min): Animaciones, análisis paramétrico, curvas con barras de error y ajustes teóricos.
  5. *Conclusiones* (< 1 min).
- **Tiempo total:** $\le 15$ minutos.
- **Exposición:** Todos los integrantes exponen partes balanceadas.
- **Consejos de oratoria científica:** Hablar con voz firme, mantener contacto visual con el público, ensayar en voz alta, no sobrecargar las diapositivas de texto y responder preguntas en forma concisa y ordenada.
