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
  el ajuste lineal). **Nunca se usan instantes intermedios** (ni interpolación, ni avance en MRU,
  ni búsqueda de tiempos que no sean eventos): lo prohíbe la cátedra (ver §10).
  - `goals.csv`: `t, id` por cada gol (≤ N líneas). De acá salen `N_g(t)`, `F_g(t)` y `t_90`.
  - `run.json`: inputs, seed, `t_90`, cantidad de eventos por tipo, tiempo de ejecución del lazo
    de eventos (punto 1.1), energía cinética inicial y final (validación: debe ser constante).
  - `static.txt`: N, L, W, d, r, m, obstáculos. `dynamic.txt`: bloques `t` + `x y vx vy estado` por
    partícula (formato de cátedra `../AGENTS.md` §2.2 con **estado/color por bloque**, porque
    cambia en el tiempo). **Solo con `--every`**. Tamaño: ~4 KB por bloque con N = 100.
  - **Regla (2026-09-18)**: los barridos del 1.2 guardan `dynamic.txt` con `--every 25`
    (~8 MB por corrida) para poder calcular cualquier observable nuevo (DCM incluido) sin
    volver a correr. `--every 1` solo para las corridas de animación. Con `--every 0` (como se
    corrió al principio) hubo que re-correr para el 1.3: no repetir.
- **Seeds**: una distinta por realización (regla del repo).
- **Estimación de costo**: con N = 100, v₀ = 1 m/s, r = 0.0175 m, fracción de área ≈ 0.10, el
  camino libre medio es ~0.08 m → ~10 choques/s por partícula → ~10³ eventos/s de simulación.
  30 s ≈ 3·10⁴ eventos; 100 s ≈ 10⁵. Guardar cada evento en `dynamic.txt` es ~400 MB por
  corrida de 30 s: `--every 1` solo para animar.
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


## 5. Estado del post-proceso (2026-09-18)

- **1.1 hecho**: `scripts/run_time_vs_n.sh 20` → `analysis/plot_time_vs_n.py` →
  `time_vs_n.png` (log-log), `time_vs_n_linear.png`, `events_vs_n.png`. Tiempo ~N³ (eventos ~N²
  × O(N) por evento), se empina para N ≥ 300 (fracción de área ≥ 0.35). Barras de error ≤ 9 %,
  menores que el símbolo.
- **Animaciones**: `analysis/animate.py <run_dir> [--fps 60]` (requiere `--every 1`). **Versión
  vieja, reemplazada en §10**: muestreaba a fps fijo avanzando el último bloque en MRU (prohibido).
  Videos hechos con esa versión, a rehacer (60 fps, tiempo real, 30 s, seed
  1, N = 100) en `output/anim/{empty,corr020,corr038,mb_k01,mb_k16,elegida}/anim.mp4`; el
  `dynamic.txt` de cada una (~100–400 MB) se conserva para regenerar fotogramas.
- **1.2 barridos** (`tf = 100`, `--stop-at-t90`, `--every 25`, **20 seeds** 1..20, 8 en
  paralelo; `scripts/run_sweeps.sh` ya tiene esos defaults): `analysis/gen_configs.py` genera
  **solo las familias de la presentación** (hoy 3, ver §9; `corridor` 4 puntos salió después, `single_R` 9,
  `multi_barrier` k = 1..22, `multi_barrier_rows_k` k = 14..17 × n = 1..4) →
  `output/sweeps/<barrido>/<punto>/config.txt` + `index.json`; `analysis/plot_t90.py
  --grid-k 14,15,16,17` → `t90_<barrido>.png`, `analysis/out/t90_<barrido>.csv`. Barra de
  error = desvío entre seeds de `t_90` (ddof=1; el observable es un escalar por realización).
  Decisión 2026-09-18: se bajó de 100 a 20 realizaciones (el enunciado pide ≥ 5; 100 era
  desproporcionado) y se borraron las familias exploratorias (single_x, mirror, grid_K,
  funnel*, bumps, dome*, barrier, corridor_smooth, c_gate) de `output/`, `gen_configs.py` y
  `analysis/{out,figures}`. Sus resultados quedan solo en la lista de hipótesis de abajo.
  El motor es determinista por seed: los `t_90` de las seeds 1..20 son los mismos que antes.
  Total `output/`: ~9 GB (sweeps 7.7 GB, anim 1.5 GB).
- Mesa vacía (20 seeds): **22.2 ± 2.1 s**.
- **Bloque central (`multi_barrier`)**: bloque macizo centrado en `x = L/2` de k columnas
  verticales pegadas (separación entre centros `2R + 10⁻⁴`) de 13 discos R = 0.02 m cada una
  (gap entre superficies < 2r: no pasan partículas). Curva vs k (20 seeds): 21.1 (k = 1,
  ≈ vacía) baja hasta una **meseta k = 13..19 (14.5–15.4 s, diferencias < SE ≈ 0.4 s)** y sube
  (k = 21: 17.7; k = 22: 23.4; k = 23 no deja ubicar las 100 partículas).
- **Configuración elegida: `multi_barrier_rows_k` k = 17, n = 1 → `<t_90>` = 13.6 ± 1.8 s**
  (K = 245, 20 seeds): bloque de 17 columnas más una fila de discos R = 0.02 pegada a cada
  pared larga en cada compartimento. Config =
  `output/sweeps/multi_barrier_rows_k/k17_n01/config.txt` (regenerable con `gen_configs.py`);
  copiada a **`tp3-event-driven-md/Config.txt`** (entrega, 245 líneas; 2026-09-25, verificada:
  la seed 1 con `--obstacles Config.txt` da el mismo t_90 = 16.726222 s que el barrido).
- Ranking por familia (mejor punto de cada una, `<t_90>` en s, 20 seeds salvo indicación):
  - `multi_barrier_rows_k` (k = 14..17): **1 o 2 filas bajan ~1 s** respecto del bloque solo;
    pooling k = 15..17: bloque 15.0 ± 1.6 (60 corridas) vs n ≤ 2 14.0 ± 1.7 (120), diferencia
    1.0 s con SE 0.26. Entre k17_n01 (13.6), k15_n01/n02 (13.7/13.7) no hay diferencia
    resoluble. n = 3 empeora (15.5–16.8), n = 4 supera la vacía. La figura incluye n = 0
    (bloque solo) por k.
  - `single_R` (disco centrado): monótono decreciente con R, 21.6 (R = 0.025) → 16.1 ± 2.0
    (0.33).
  - `corridor` (mesa rellena salvo un corredor central): 22.5 (h = 0.38) → 46 ± 5 (h = 0.20);
    empeora al angostar el corredor.
  - Familias exploradas y descartadas (borradas; valores con 20 seeds de entonces):
    `single_x_R0.30` 16.3 en x = 0.55 ≈ centrado, 49 en x = 0.30; `dome_wall` 17.9; `bumps`
    18.4; `dome` 18.7; `single_x` (R = 0.10) 29.3 en x = 0.15, ≈ vacía desde x ≥ 0.30;
    `mirror_x`/`mirror_R` siempre peor que vacía (R = 0.25 → 79.8; R = 0.30 ninguna alcanza
    0.9); `grid_K` empeora con K (20.8 → 26.1); `funnel*` 24–36; `corridor_smooth`/`c_gate`
    como `corridor` o peor.
- **Hipótesis probadas y descartadas**:
  - "t_90 ∝ área libre" → `corridor` es peor cuanto menos área libre. Falso.
  - "lo que importa es partir la mesa" → `barrier` (una columna, k = 1): 20.3–21.1 ≈ vacía.
    La partición sola no hace nada.
  - "embudos que guíen hacia el arco" → `funnel*`: peor; atrapan partículas lejos del arco.
  - Lectura consistente con todo: lo que ayuda es **quitar área lejana a los arcos** (el
    centro) sin dejar bolsillos, y hay un óptimo: pasado k ≈ 19 la densidad en cada mitad sube
    tanto que `t_90` vuelve a crecer. Hipótesis mecanística **no probada todavía** (no decirla
    como conclusión): `t_90 ~ ℓ²/D` con ℓ la distancia a recorrer hasta el arco y D el
    coeficiente de difusión, que baja con la densidad.
    `analysis/plot_configs.py [--labels ... --cols n]` dibuja configs (con `--labels` sin
    rutas, para diapositivas: `pres_configs_*.png`); `animate.py --snapshot t` guarda un PNG.
- Ninguna realización dejó de alcanzar 0.9 antes de 100 s; `multi_barrier_rows_k` k17_n04
  (15/20) y k16_n04 (1/20) no pudieron ubicar las 100 partículas (`plot_t90` las cuenta en
  `no_generado`).
- **Presentación** (estado del 2026-09-18; la estructura actual del 1.2 está en §9): `../presentaciones/tp3/tp3.tex` (compila, 23 páginas), hilo del 1.2:
  corredor → disco central → bloque de columnas → bloque + filas → elegida. Texto al costado
  de las figuras: solo parámetros que no estén ya en Simulaciones (nada de explicaciones ni
  conclusiones: eso se dice en vivo). Fotogramas en `../presentaciones/tp3/figuras/`
  (`animate.py --snapshot` sobre `output/anim/*`; hechos con la versión vieja, a rehacer: §10).
  Links de YouTube = `PENDIENTE`.
- **1.3 calculado pero NO revisado ni en git (2026-09-18)**: `analysis/dcm.py`, `dcm_*.png`,
  `D_vs_t90.png`, `out/dcm_D.csv` y `out/dcm/` están sin commitear hasta que el grupo lo
  analice; la presentación de momento no tiene diapositivas del 1.3 (ni observable de
  difusión). Lo que hay: `analysis/dcm.py [--t0 0.3 --t1 0.8]` lee
  los `dynamic.txt` (`--every 25`) de **las mismas corridas del 1.2** (52 configuraciones × 20
  seeds) y evalúa el DCM en los instantes de los bloques (sin interpolar; ~10–20 puntos por seed
  en la ventana). Curvas cacheadas en `analysis/out/dcm/*.csv` (t ≤ 3 s; sin cache tarda ~4
  min). DCM(t) tiene tramo balístico hasta ~0.3 s, régimen lineal y saturación por
  confinamiento: ventana de ajuste común [0.3, 0.8] s, marcada en `dcm_vs_t.png`. Ajuste
  `DCM = c·t` por mínimo de E(c) (`dcm_E_c.png`), D = c/4. Resultados (`analysis/out/dcm_D.csv`,
  D en m²/s, 20 seeds): vacía 0.025 ± 0.002; corredor 0.0119 (h = 0.38) → 0.0050 (h = 0.20);
  disco 0.024 (R = 0.025) → 0.0093 (0.33); bloque 0.020 (k = 1) → 0.0074 (k = 16) → 0.0021
  (k = 22); elegida k17_n01 0.0053 ± 0.0005. **No hay correlación global D vs <t_90>**
  (Pearson r = 0.13, Spearman 0.26 sobre 52 configs): todo obstáculo baja D, pero el corredor
  sube t_90 y el disco/bloque lo bajan (`D_vs_t90.png`, un símbolo por familia). Consistente
  con la hipótesis ℓ²/D de arriba, que sigue sin probarse directamente: no afirmarla.
- **Pendiente**: revisar y sumar el 1.3 (observable de difusión en Simulaciones + 3
  diapositivas + conclusión); subir los videos y reemplazar los
  `PENDIENTE`; diapositiva de animación de la elegida (hoy solo config estática); guion con
  tiempos (13 min).

## 6. Cambios del 2026-09-24 (devolución interna de la presentación)

- Diapositivas: "Modelo: esferas duras" → "Modelo: partículas con masa"; nueva diapositiva de
  animación disco central (R = 0.33 m) vs elegida entre "Tiempo de ejecución" y "Disco central:
  <t_90> vs radio"; se quitó "Bloque central: animación" (k = 1 vs 16). Video nuevo:
  `output/anim/disco_R033/` (seed 1, 30 s, `--every 1`); fotogramas t = 8 s en
  `../presentaciones/tp3/figuras/snapshot_{disco,elegida}.png`.
- `analysis/dcm_multi_barrier.py`: 1.3 para el bloque central, k = 1..22, misma lógica que
  `dcm.py` (t_fin a ojo por k en `FIT_END`, k = 18 con la misma ventana que `dcm.py`) →
  `D_vs_t90_multi_barrier.png` (color = k), `D_vs_k_multi_barrier.png`,
  `dcm_multi_barrier.png` (curvas por realización con el tramo ajustado resaltado),
  `out/dcm_D_multi_barrier.csv`. `D_vs_t90_multi_barrier.png` está en la presentación después de D vs <t_90> de las mejores de cada familia).
  Ojo: las curvas DCM son cóncavas casi desde el inicio, así que D depende de t_fin (ventana más
  larga → D menor); los saltos de D entre k con distinto t_fin son en parte efecto de la ventana.
- `time_vs_n_loglog.png`: tiempo vs N con ambos ejes en décadas (no está en la presentación).
  `analysis/out/time_vs_n.csv` viene del modo `--bench` corrido en otra máquina (commit
  1bb0d95); los `run.json` de `output/time_vs_n/` de esta máquina son de la medición vieja (una
  JVM por corrida) y dan otros tiempos. Para rehacer figuras sin pisar el csv:
  `plot_time_vs_n.py --from-csv`.

- `analysis/plot_goals.py <run_dir>... --labels ... --out <png>`: F_g(t) = N_g/N de una o varias
  corridas sin `--stop-at-t90` (una curva por corrida, color de su familia), con F_g = 0.9 y el
  t_90 de cada una marcados sobre los ejes. En la presentación: `fg_empty_disco.png` (mesa vacía
  y disco R = 0.33 m, `output/anim/{empty,disco_R033}`, seed 1, 30 s; t_90 = 22.9 y 16.9 s,
  iguales a la seed 1 de sus barridos), antes de "<t_90> vs radio". Historia: primero era N_g(t)
  (`goals_disco.png`), después F_g en dos diapositivas separadas (`fg_empty.png`,
  `fg_disco.png`); el 2026-09-25 se unieron en una.
- `analysis/dcm_rows_best_k.py`: igual que `D_vs_t90_multi_barrier.png` pero para el bloque con
  filas, un punto por n con su mejor k (n = 0 → k18, 1 → k17, 2 → k15, 3 → k14, 4 → k14; t_fin a
  ojo en `BEST`) → `D_vs_t90_rows_best_k.png`, `out/dcm_D_rows_best_k.csv`. **No está en la
  presentación** (solo para mirar).

## 7. Cambios del 2026-09-25 (segunda devolución interna)

- Diapositivas: Sistema (intro) sin la frase de goles ni "con obstáculos y paredes"; Modelo:
  "Movimiento de partículas" (MRU vectorial, sin texto de definiciones) + "Choques elásticos" con
  la notación de la Teórica 3 pero **con primas** (no superíndices a/d): partícula–partícula con
  J, J_x, J_y y las cuatro componentes v'; obstáculo con v' = R(−α) S(c_n, c_t) R(α) v (c = 1,
  sin desarrollar matrices); pared "se invierte la componente normal". Sin fórmulas de tiempo al
  próximo choque ni nota de definiciones (Δr, σ, masa): el grupo las pidió fuera. En el
  diagrama del motor "Predecir choques de i y j"; Sistema (Simulaciones): esquema a la izquierda
  y todo el texto a la derecha (renglones recortados para que entre); "Observables" (N_g, F_g,
  t_90, tiempo de ejecución, con esquema azul → arco → roja, sin texto de definición de gol) y
  "Observables: difusión" (DCM con esquema de desplazamiento, D); conclusiones recortadas a 3.
- Figuras: el valor destacado va **en el eje**, no al costado. `common.mark_on_axis` agrega un
  tick con color propio y saca los ticks automáticos que se pisarían; `common.mark_point_x`
  marca el mejor punto (recta punteada negra hasta el eje horizontal + tick en negrita; **sin
  anillo/círculo alrededor del punto**: pedido explícito del grupo). `plot_t90.py` lo usa en
  `t90_<barrido>.png` (el mejor punto se calcula, no se
  escribe a mano) y `plot_goals.py` marca t_90 y 0.9 sobre los ejes.
- Eje de <t_90> en todas las figuras = `common.LABEL_T90` ("⟨t₉₀⟩ (s)"), también como eje x de
  `D_vs_t90*.png`. Eje de D en `D_vs_t90*.png` en escala log con rótulos solo en décadas
  (`common.log_yaxis`). **No usar el factor ×10⁻³ arriba del eje** (offset de matplotlib): el
  grupo lo rechazó.
- `t90_<barrido>.png`: la recta de la mesa vacía lleva banda sombreada de ± 1 desvío entre
  realizaciones (es un promedio, igual que los puntos).

## 8. Cambios del 2026-09-25 (tercera devolución interna)

- Choques contra obstáculo: el código (`Collisions.bounceObstacle`) usa `v' = v − 2 (v·ê_n) ê_n`,
  no las matrices; es algebraicamente idéntico a `R(−α) S(1, 1) R(α) v` (chequeado numéricamente,
  diferencia ~10⁻¹⁵). No se cambió el código (cambiaría el redondeo y, por caos, todos los t_90
  por seed). **Decisión del grupo**: la diapositiva "Modelo" muestra **solo la forma del motor**
  (`v − 2 (v·ê_n) ê_n`), sin el operador de matrices de la §7. Partícula–partícula (J) y paredes
  coinciden con el código.
- Error de D revisado: un ajuste `DCM = c·t` por realización, `D = c*/4`, promedio y desvío
  estándar (ddof = 1) entre las 20 realizaciones; sin dividir por √n. Recalculado aparte: coincide.
- `dcm_vs_t.png`: recortado a t ≤ 12 s, figura ancha (8 × 3.9), rectas `c*·t` de la seed 1 en
  [0, t_fin] (negras de trazos) y t_fin con punteada del color de la curva. Diapositiva sin texto.
- Diapositivas: Sistema (Simulaciones) sin dirección ~U, sin "arcos" ni "Parámetros de
  simulación", esquema más grande; Observables dice que el observable es `<t_90>` sobre 20
  realizaciones y el tiempo de ejecución promedio sobre 20 realizaciones de 30 s simulados;
  Difusión explica el ajuste por E(c); F_g(t) mesa vacía vs disco sin texto al costado.
- **Eje de D lineal desde 0** (reemplaza la escala log de la §7) en `D_vs_t90.png`,
  `D_vs_t90_multi_barrier.png`, `D_vs_k_multi_barrier.png` y `D_vs_t90_rows_best_k.png`; rótulo
  `common.LABEL_D` = "⟨D⟩ (m²/s)", igual que ⟨t₉₀⟩. Se borró `common.log_yaxis` (sin uso).

## 9. Cambios del 2026-09-25 (devolución de la cátedra sobre el punto 1.2)

Devolución textual: *"a) NO presentar más de tres configuraciones b) Para cada familia de
configuraciones, seguir el esquema usual de las presentaciones: animación característica,
evolución temporal de número de partículas convertidas, y luego input vs observable (<t90>).
Finalizar mostrando una comparación de los mejores ejemplares de cada familia."*

- **(a)** se leyó como "a lo sumo tres **familias**": disco central (`single_R`), bloque central
  (`multi_barrier`) y bloque con filas (`multi_barrier_rows_k`). El corredor ya no aparece en
  ninguna figura ni diapositiva (`pres_configs_corridor.png` queda en `analysis/figures/` sin uso).
- **Resultados del 1.2**, una tanda por familia, en este orden: animación → F_g(t) → <t_90> vs
  variable. Los esquemas "Configuraciones: …" **se quedan en Simulaciones** (sistema particular,
  raíz §5.3.3 y §8.1). Cierre: "Mejor configuración de cada familia" (`t90_best.png`, con qué
  punto es cada barra al costado: R = 0.33 m, k = 18, k = 17 n = 1) y "Configuración elegida".
  - Disco: animación mesa vacía | R = 0.33 m (absorbe la diapositiva suelta "Mesa vacía"),
    `fg_empty_disco.png`, `t90_single_R.png`.
  - Bloque: animación k = 16 (`snapshot_mb_k16.png`; video en `output/anim/mb_k16` de la máquina
    de Nick, **falta subirlo a YouTube**: `\yt{PENDIENTE}`), `fg_multi_barrier.png` (mesa vacía,
    k = 16, k = 22), `t90_multi_barrier.png`. Se eligió k = 16 porque ya tenía video: está en la
    meseta (14.8 vs 14.5 s del mínimo k = 18, diferencia < SE).
  - Filas: animación de la elegida (k = 17, n = 1), `fg_rows.png` (k = 17, n = 0, 1, 3; "k = 17"
    al costado), `t90_multi_barrier_rows_k.png`.
  - Se sacó "Disco central vs configuración elegida: animación" (cada video pasó a su familia).
    Títulos unificados a "bloque con filas" (como en las figuras). 32 páginas.
- **F_g(t) por familia** (generadas el 2026-09-26 en la máquina de Agustín): seed 1, mismas
  opciones que los barridos (`--tf 100 --stop-at-t90 --every 25`), en `output/fg_seed1/{empty,
  disco_R0.330,mb_k16,mb_k22,mb_k17,rows_k17_n01,rows_k17_n03}` (69 MB). Curvas hasta F_g = 0.9.
  t_90 de esas corridas: vacía 21.6, disco 16.4, k16 14.3, k22 25.9, k17 13.5, k17_n01 13.2,
  k17_n03 17.7 s. **No son las mismas trayectorias que los videos** (hechos en la máquina de Nick,
  vacía seed 1 = 22.9 s): son otra realización del mismo modelo; las tres figuras salen de las
  mismas corridas, así la mesa vacía es la misma curva en todas. `fg_empty_disco.png` se rehízo
  así (antes: corridas de 30 s de `output/anim` de Nick). Colores: rojo mesa vacía, azul disco,
  verde bloque, naranja filas (los de `t90_best`/`D_vs_t90`), negro el extremo "demasiado"
  (k = 22, n = 3). Comandos (desde `analysis/`, `R=../output/fg_seed1`):
  ```
  python3 plot_goals.py $R/empty $R/disco_R0.330 --labels "mesa vacía" "disco central" --out fg_empty_disco.png
  python3 plot_goals.py $R/empty $R/mb_k16 $R/mb_k22 --labels "mesa vacía" "k = 16" "k = 22" \
      --colors tab:red tab:green black --out fg_multi_barrier.png
  python3 plot_goals.py $R/mb_k17 $R/rows_k17_n01 $R/rows_k17_n03 --labels 0 1 3 --legend-title n \
      --colors tab:green tab:orange black --out fg_rows.png
  ```
  `plot_goals.py` ganó `--colors`, `--legend-title` (entradas solo con el valor), escalonado de
  los rótulos de t_90 que se pisan, eje x +5 % y leyenda `best` para corridas cortadas.
- **`t90_multi_barrier.png` en verde** (color de la familia): `plot_t90.py --from-csv single_R
  multi_barrier` rehace las figuras de barridos de una variable desde `analysis/out/t90_*.csv` y la
  mesa vacía de `analysis/out/dcm_D.csv` (datos de Nick, sin leer `output/sweeps`). Validado:
  `t90_single_R.png` sale idéntica salvo antialiasing (se dejó la commiteada).
- **Pendiente**: subir `output/anim/mb_k16/anim.mp4` (máquina de Nick) a YouTube y reemplazar
  `\yt{PENDIENTE}` en "Bloque central: animación".
- Copia de la presentación antes de este cambio (commit 2872b88, tex + pdf + fotogramas) en
  `../presentaciones/tp3_develop/`, para comparar. Si se recompila usa las figuras actuales de
  `analysis/figures/`: la referencia fiel es su `tp3.pdf`.
- **Ojo: los barridos de la máquina de Agustín son de otra muestra** (14–18/9, `--every 0`, 100
  seeds de vacía, `rows_k` solo k = 9..14, sin `single_R`) y no coinciden con los CSV commiteados
  (bloque k = 15: 14.23 vs 15.35 s). **Verificado el 2026-09-26**: con el motor actual, la misma
  seed da otra trayectoria en cada máquina (vacía seed 1: 21.582253 vs 22.9 s; `Config.txt` seed 1:
  13.224576 vs 16.726222 s) y en cada máquina es reproducible (las corridas nuevas repiten los t_90
  de los barridos locales viejos). Causa probable: punto flotante distinto entre plataformas
  (ARM vs x86) amplificado por el caos. **No correr `plot_t90.py` ni `dcm*.py` en esa máquina** (pisan figuras y CSV
  commiteados). `output/anim/multi_barrier_k15` de esa máquina es de la misma generación vieja:
  no usarlo.
- `gen_configs.py` no tiene argparse: `--help` lo ejecuta y reescribe `output/sweeps/*/config.txt`
  e `index.json` (inofensivo, es determinista, pero deja el índice con solo las 3 familias).
- Tiempo (13 min): ~12:15 estimado. Si el ensayo se pasa, en orden: reproducir ~8–10 s de cada
  video; sacar "Bloque central: <D> vs <t_90>".

## 10. Cambios del 2026-09-26 (devolución de la cátedra: interpolación y competencia)

- **Regla de la cátedra (textual)**: "en este TP (Event Driven Simulation) no está permitido
  ningún tipo de interpolación, búsqueda o uso de tiempos que no correspondan a eventos. Ni para
  animar, ni para ningún otro fin." Además, **el zip de código lleva el motor y el código de las
  animaciones**.
- **Auditoría**: violaban la regla `animate.py` (cuadros a fps fijo avanzando en MRU; `--snapshot`
  en un t exacto) y el motor al cortar por `tf` (`advanceTo(tf)` + último bloque de
  `dynamic.txt` y `finalTime` en `t = tf`). Están bien: t_90 (tiempo del gol), F_g(t) (escalones
  en los goles), DCM (solo instantes de bloques; las ventanas de ajuste solo eligen muestras).
- **`animate.py` reescrito**: cada cuadro es exactamente un bloque de `dynamic.txt` (un evento),
  con `t`, número de evento y goles en pantalla. `--stride k` (un cuadro cada k bloques; sin él
  se elige k para que el video dure ≈ (t_fin − t_ini)/speed), `--first/--last` o `--t0/--t1`,
  `--snapshot t` (primer bloque con t_b ≥ t, informa el t_b usado) o `--snapshot-block b`. La
  reproducción **no es en tiempo real** (cada cuadro avanza un número fijo de eventos).
- **Motor**: al cortar por `tf` ya no avanza el estado hasta `tf`; el último bloque y `finalTime`
  son el último evento. No cambia ningún evento ni t_90.
- **Pendiente**: rehacer los videos (`YCpG6rdYMtU`, `OzH415fexjk`, `wTY2R0gUhOo`, y
  `PENDIENTE` de k = 16) y los fotogramas `../presentaciones/tp3/figuras/snapshot_*.png` con el
  `animate.py` nuevo sobre las corridas `--every 1` de `output/anim/*` de la máquina de Nick
  (alcanza con re-renderizar, sin volver a simular); subirlos y reemplazar los IDs en `tp3.tex`.
- **Competencia (punto 1.4)**: la cátedra corre las 5 simulaciones en vivo al comienzo de los
  13 min y el simulador debe imprimir las convertidas en cada nueva conversión y t_90 al final.
  Flag `--live` (campo `live` de `SimulationConfig`, como `every` y `stopAtT90`): cabecera de una
  línea, `convertidas: k / N (t = … s)` por gol y `t_90 = … s` (o "NO ALCANZADO" con las
  convertidas a t_max); sin `--live` la salida es la de siempre. `scripts/competencia.sh gen |
  run | all [dir] [seeds…]`: genera las 5 condiciones iniciales, corre con `Config.txt`,
  `--tf 100 --stop-at-t90 --live` (con `HASTA_TMAX=1` hasta 100 s) y cierra con la tabla de t_90
  y ⟨t_90⟩ ± desvío (ddof = 1). Las 5 corridas tardan ~3 s en total.
- **Zip**: `scripts/build_zip.sh` → `SdS_TP3_2026Q2G02CS2_Codigo.zip` (comisión S2): poms,
  `billiard-java/src`, `CliArgs` de `common` y `analysis/{animate.py, common.py,
  requirements.txt}`; ~32 KB, compila desde el zip. **Rearmarlo justo antes de entregar.**
- Tras la competencia se presenta **solo la sección Simulaciones** (foco en las configuraciones,
  mínimo del resto) y los resultados; los 13 min se reparten entre las 5 corridas y la
  exposición.
