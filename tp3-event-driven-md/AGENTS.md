# AGENTS.md — SdS TP3: Simulación Dirigida por Eventos (Billar-Metegol)

> Leer y respetar siempre los lineamientos de `../AGENTS.md` (raíz del repo). El enunciado
> completo está en `docs/Enunciado.md` (capturas originales en `docs/enunciado/`) y tiene máxima
> prioridad. Teoría: `../docs/Teorica_3.md` (resumen con fórmulas) y `../docs/Teorica_3.pdf`.
> Bibliografía: `docs/bibliografia/Sedgewick_Wayne_MD_Hard_Spheres.pdf` (assignment COS 226,
> Princeton: cola de prioridad de eventos + invalidación por contador de colisiones).

---

## 1. De qué se trata

TP3 de Simulación de Sistemas (ITBA): **dinámica molecular regida por eventos** (esferas duras
en 2D) sobre una "mesa de metegol". Entre colisiones las partículas hacen MRU; los eventos son
las colisiones (partícula–partícula, partícula–obstáculo, partícula–pared), todas **elásticas**.

- Dominio rectangular **L = 1.20 m × W = 0.68 m**, paredes fijas.
- **Arcos**: segmento de longitud **d = 0.20 m** centrado en cada pared corta (`x = 0` y `x = L`),
  o sea `|y − W/2| ≤ d/2`.
- **K obstáculos** circulares fijos (masa infinita), `(x_k, y_k, R_k)`: parámetros libres, con
  `R_k ≥ r`, íntegramente dentro del dominio, sin solaparse entre sí, y que permitan generar las
  N partículas.
- **N partículas** de radio **r = 0.0175 m**, masa **m = 0.025 kg**, velocidad inicial de módulo
  **v₀ = 1 m/s** con ángulo ~ U[0, 2π), posiciones iniciales al azar sin solapamiento.
- Estado **fresca** (azul) → **usada** (roja) al **primer** contacto con un arco (= choque con
  pared corta con `|y − W/2| ≤ d/2`). Cuenta un **gol**; la partícula rebota normalmente y sigue
  en el sistema (N y densidad constantes). Una usada nunca vuelve a sumar goles.
- Observables: `N_g(t)` goles acumulados, `F_g(t) = N_g/N`, **`t_90`** = primer t con
  `F_g ≥ 0.9`. **Objetivo del TP: encontrar y justificar la configuración de obstáculos que
  minimiza `<t_90>`.**
- Entrega: **28/09/2026 13 hs** (presentación pdf + código zip **< 100 KB** + `Config.txt`).
  Ese mismo día hay **competencia en vivo** entre grupos.

### Puntos del enunciado

| Punto | Qué pide | Parámetros |
| :--- | :--- | :--- |
| 1.1 | Tiempo de ejecución (wall-clock) promedio ± desvío vs. N, mesa vacía | `t_f = 30 s`, ≥ 10 realizaciones por N |
| 1.2 | Explorar configuraciones de obstáculos; `<t_90>` ± error vs. variable estudiada; comparar contra mesa vacía; justificar cómo se encontró la mejor | N = 100, ≥ 5 realizaciones |
| 1.3 | DCM promediado sobre **todas** las partículas móviles (frescas + usadas) de una realización; ajuste lineal (método Teórica 0) → `D`. Reportar `D` para mesa vacía y demás configuraciones; ver si hay correlación `D` vs `<t_90>` | N = 100 |
| 1.4 | Competencia: 5 realizaciones de la mejor configuración con el propio motor | N = 100, `t_max = 100 s`, parámetros fijos del enunciado |

Formato de `Config.txt`: una línea por obstáculo, `x_k y_k R_k` en metros separados por espacio.

## 2. Modelo (para presentación e informe)

Todo está en `../docs/Teorica_3.md`; lo esencial:

- **Vuelo libre**: `r_i(t) = r_i(t₀) + v_i (t − t₀)`.
- **Tiempo a pared**: `t = (x_p − R − x)/v_x` (según signo de `v_x`); ídem en y.
- **Tiempo entre partículas**: `t_c = −(Δv·Δr + √d)/(Δv·Δv)` con
  `d = (Δv·Δr)² − (Δv·Δv)(Δr·Δr − σ²)`, `σ = R_i + R_j`; sin choque si `Δv·Δr ≥ 0` o `d < 0`.
  Para un obstáculo fijo se usa la misma fórmula con `v_j = 0`, `R_j = R_k`.
- **Post-choque pared**: se invierte la componente normal (`−v_x` o `−v_y`).
- **Post-choque partícula–partícula**: impulso `J = 2 m_i m_j (Δv·Δr) / (σ (m_i + m_j))`,
  `J_x = J Δx/σ`, `J_y = J Δy/σ`; `v_i += J/m_i`, `v_j −= J/m_j`.
- **Post-choque partícula–obstáculo**: límite `m_j → ∞` de lo anterior ≡ operador de colisión
  `R(−α) S(c_n, c_t) R(α)` con `c_n = c_t = 1` (elástico) ≡ reflexión especular
  `v' = v − 2 (v·ê_n) ê_n` con `ê_n` el versor centro-obstáculo → centro-partícula.
- **Difusión**: `<|r(t) − r(0)|²>` vs `t`; en 2D `DCM = 4 D t` (Teórica 0: `2 d D t`). La
  Teórica 3 escribe `<z²> = 2 D t` por coordenada. **Decisión (2026-09-10)**: DCM = distancia
  total al cuadrado en el plano, ajuste `DCM = c·t` por mínimo de `E(c)` (método Teórica 0,
  mostrar la curva `E(c)` con su mínimo) y `D = c*/4`. Dejar la definición explícita en la
  presentación.

## 3. Decisiones de diseño (propuesta; ajustar al implementar)

- **Motor en Java**, módulo Maven `billiard-java/` colgado del `pom.xml` raíz, reutilizando
  `common/` (`Particle`, IO, `CliArgs`) donde encaje. El zip de entrega debe ser < 100 KB: solo
  `src/` del motor (+ lo mínimo de `common` que use).
- **Algoritmo**: cola de prioridad de eventos (bibliografía) con **invalidación lazy** por
  contador de colisiones de cada partícula. Al procesar un evento válido: avanzar todas las
  partículas a `t`, aplicar choque, y re-predecir solo los eventos de las partículas involucradas
  (contra todas las demás, obstáculos y paredes). Alternativa más simple para validar: recomputar
  el mínimo global O(N²) tras cada evento.
- **Gol**: el evento "choque con pared vertical" ya da `y` en el instante de contacto; si la
  partícula es fresca y `|y − W/2| ≤ d/2` → gol + cambio de estado. El rebote es el normal.
- **Precisión**: tras avanzar, las partículas quedan exactamente en contacto; cuidar que
  `Δv·Δr ≥ 0` descarte el re-choque inmediato y que errores de redondeo no generen `t_c` negativos
  (clamp a 0 / tolerancia).
- **Output** (decisión 2026-09-10, corregida): el estado se imprime **en los instantes de los
  eventos**, cada `--every k` eventos, como pide textualmente el enunciado ("imprimir el estado
  en cada uno de estos t_i, o mejor cada un número entero de eventos"). No hay salida a intervalo
  fijo: para el DCM se usan los propios instantes de los bloques (el espaciado irregular no afecta
  el ajuste lineal) y, si hiciera falta un instante intermedio, con `--every 1` la interpolación
  lineal es exacta.
  - `goals.csv`: `t, id` por cada gol (≤ N líneas). De acá salen `N_g(t)`, `F_g(t)` y `t_90`.
  - `run.json`: inputs, seed, `t_90`, cantidad de eventos por tipo, tiempo de ejecución del lazo
    de eventos (punto 1.1), energía cinética inicial y final (validación: debe ser constante).
  - `static.txt`: N, L, W, d, r, m, obstáculos. `dynamic.txt`: bloques `t` + `x y vx vy estado` por
    partícula (formato de cátedra `../AGENTS.md` §2.2 con **estado/color por bloque**, porque
    cambia en el tiempo). **Solo con `--every`**: los barridos de 1.1 y 1.2 no lo escriben.
    Tamaño: 30 s con N = 100 y `--every 1` ≈ 10 MB (2.5·10⁴ bloques).
- **Seeds**: una distinta por realización (regla del repo).
- **Estimación de costo**: con N = 100, v₀ = 1 m/s, r = 0.0175 m, fracción de área ≈ 0.10, el
  camino libre medio es ~0.08 m → ~10 choques/s por partícula → ~10³ eventos/s de simulación.
  30 s ≈ 3·10⁴ eventos; 100 s ≈ 10⁵. Guardar cada evento en `dynamic.txt` sería ~60 MB por
  corrida: usar `--every k` con k > 1 salvo para la corrida del DCM/animación.
- **Punto 1.1**: elegir un rango de N (ej. 25 … 400) acotado por la densidad: la fracción de
  área `N π r² / (L W)` debe quedar bien por debajo de ~0.5 para que la inserción aleatoria
  converja.

### Decisiones tomadas el 2026-09-10 (antes de implementar el motor)

- **Lenguaje y módulo**: Java, módulo `billiard-java/` que depende de `common/`. Para el zip de
  entrega (< 100 KB) alcanza con `billiard-java/src` + `common/src` + poms.
- **Obstáculos como input**: el motor lee un archivo con el **mismo formato que `Config.txt`**
  (`x_k y_k R_k` por línea). Mesa vacía = sin flag. Así la configuración que se entrega es
  exactamente la que corre el motor.
- **Condición inicial**: inserción secuencial por rechazo (posición uniforme en `[r, L−r] ×
  [r, W−r]`, rechazar si solapa con partícula u obstáculo), con tope de intentos → error claro si
  la configuración no permite generar N partículas (restricción ii).
- **Fin de la corrida**: `--tf` (tiempo simulado). Flag opcional `--stop-at-t90` para cortar
  apenas `F_g ≥ 0.9` (acelera los barridos del punto 1.2; no usar cuando se necesita el DCM).
- **Tiempo de ejecución (1.1)**: se cronometra **solo el lazo de eventos** (sin generación de
  condición inicial ni escritura de archivos). Se mide con el modo `--bench`: **una sola JVM**,
  calentamiento de 30 s y todas las corridas (N × seeds) seguidas en **orden aleatorio**.
  Motivo (medido el 2026-09-10): con una JVM por corrida, N chico queda dominado por el JIT y
  por el governor `powersave` del CPU (la misma corrida de N = 100 tardó 125 ms en un barrido
  sostenido y 340 ms suelta; N = 25 pasó de 25 ms a 4 ms con JIT caliente). Esto va dicho en
  la presentación como "parámetros de medición".
- **Eventos simultáneos**: se procesan en orden de cola, uno por vez; el segundo se re-predice
  después del primero. No se tratan choques múltiples (igual que la bibliografía).
- **Modo competencia**: dos pasos en el CLI: `--gen-initial` (escribe `initial.txt` con
  posiciones y velocidades) y `--initial initial.txt` para correr desde ese estado. Permite
  generar las condiciones iniciales cuando lo indiquen los docentes y correr después.
- **Realizaciones**: el enunciado pide ≥ 10 (1.1) y ≥ 5 (1.2). Se decide **después de medir** el
  costo real de una corrida; objetivo 20 por punto si una corrida de 100 s tarda del orden de
  1 s. La cantidad va como "parámetro de simulación", no como input barrido.

## 4. Arquitectura (implementada el 2026-09-10)

Módulo Maven `billiard-java/` (depende de `common/` solo por `CliArgs`). Compilar desde la raíz:
`mvn package` → `billiard-java/target/billiard.jar`.

```
billiard-java/src/main/java/ar/edu/itba/sds/tp3/
├── Main.java                # CLI: parsea args, arma la config, imprime el resumen
├── SimulationRunner.java    # una corrida completa: lazo de eventos + escritura de archivos
├── Benchmark.java           # modo --bench (punto 1.1): una JVM, calentamiento, orden aleatorio
├── SimulationConfig.java    # record con todos los parámetros; valida obstáculos (i, ii)
├── Ball.java                # partícula: x y vx vy r m, estado usada, contador de colisiones
├── Obstacle.java            # record (x, y, R)
├── Event.java               # colisión predicha: t, tipo, índices, contadores al predecir
├── Collisions.java          # física: tiempos de choque (pared/partícula/obstáculo) y rebotes
├── BilliardSimulation.java  # motor: PriorityQueue<Event>, invalidación lazy, goles, t_90
├── InitialConditions.java   # A1: inserción por rechazo
└── io/                      # ObstaclesFile (formato Config.txt), InitialStateFile, RunWriter
```

Lazo de `Main`: mientras el próximo evento válido caiga antes de `tf`, procesarlo; cada `--every`
eventos se escribe un bloque en `dynamic.txt` y los goles se escriben en `goals.csv` al ocurrir.
El tiempo "lazo de eventos" descuenta el tiempo de escritura (medido: escribir 10 MB tarda 2 s
contra 0.3 s de lazo, por eso 1.1 corre sin `--every`).

Outputs en `--out` (default `output/N<N>_K<K>_seed<seed>/`): `initial.txt`, `static.txt`,
`goals.csv`, `run.json` y, con `--every`, `dynamic.txt` (bloques `t` + `x y vx vy estado`).
`output/` está ignorado por git (regla global del `.gitignore`).

### Validaciones hechas

- `--verify` (chequeo O(N²) de solapamientos tras cada evento) pasa en mesa vacía (N = 100,
  30 s) y con 3 obstáculos (N = 100, 100 s).
- Energía cinética conservada con variación relativa ~10⁻¹² en corridas de 10⁵ eventos.
- Test determinista con `--initial`: partícula hacia el arco hace gol en `(0.6 − r)/v0 = 0.5825 s`
  exacto; tras un choque de masas iguales la otra intercambia velocidad y llega al arco en el
  instante esperado.
- Costo medido (mesa vacía, 30 s, sin verify, sin `--every`): N = 100 → 0.34 s y 2.5·10⁴
  eventos; N = 300 → 6.8 s y 3.3·10⁵ eventos (los eventos crecen ~N²). Con 3 obstáculos y
  100 s: 10⁵ eventos. La cola queda acotada (8·10³ entradas con N = 100). Con estos números,
  **20 realizaciones por configuración son baratas**; el punto 1.1 con N ≥ 400 es lo único lento.

