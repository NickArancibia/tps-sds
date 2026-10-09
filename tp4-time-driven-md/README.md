# SdS TP4 — Dinámica Molecular Regida por el Paso Temporal

Motor en **Java** (módulo `md-java`). El contexto completo del TP está en [AGENTS.md](AGENTS.md)
y el enunciado en [docs/Enunciado.md](docs/Enunciado.md).

## Requisitos

- Java 21 y Maven
- Post-proceso: Python 3 con `numpy` y `matplotlib`; `ffmpeg` para las animaciones

## Compilar

```bash
# Desde la raíz del repositorio (compila common + todos los TPs)
mvn package          # genera tp4-time-driven-md/md-java/target/md.jar
```

## Sistema 1: oscilador puntual amortiguado

```bash
# Desde tp4-time-driven-md/
java -jar md-java/target/md.jar oscillator --scheme verlet --dt 1e-3
java -jar md-java/target/md.jar oscillator --help
```

| Flag | Descripción | Default |
|---|---|---|
| `--scheme` | `beeman`, `verlet`, `velocity-verlet`, `euler-pc` | (obligatorio) |
| `--dt` | paso de integración (s) | 1e-3 |
| `--tf` | tiempo final (s), múltiplo de `dt` | 5 |
| `--save-dt` | intervalo de guardado (s), múltiplo de `dt` | 1e-2 |
| `--m`, `--k`, `--gamma` | masa (kg), constante elástica (N/m), amortiguamiento (kg/s) | 70, 1e4, 100 |
| `--r0`, `--v0` | condiciones iniciales (m, m/s) | 1, −r0·γ/(2m) |
| `--out` | directorio de salida | `output/oscillator/<esquema>_dt<dt>` |

Salida en `--out`: `trajectory.csv` (`t,r,v` cada `save-dt`, incluyendo `t = 0` y `t = tf`, con
precisión completa de `double`) y `run.json` (inputs, pasos, tiempo del lazo).

Animación (masa-resorte y `r(t)` contra la analítica; un cuadro por estado guardado):

```bash
python3 analysis/animate_oscillator.py output/oscillator/verlet_dt0.001   # → <corrida>/animation.mp4
```

Punto 1.2 (ECM vs dt de los 4 esquemas, ~5 s en total):

```bash
./scripts/run_oscillator_sweep.sh     # → output/oscillator/sweep/<esquema>_dt<dt>/
python3 analysis/plot_ecm.py          # → analysis/figures/ej1/ecm_vs_dt.png + tabla por stdout
```

## Sistema 2: billar circular

```bash
# Desde tp4-time-driven-md/
java -jar md-java/target/md.jar billiard --scheme velocity-verlet --n 300 --dt 1e-5 --tf 10
java -jar md-java/target/md.jar billiard --scheme velocity-verlet --n 100 --xo 0.0175 --tf 100
java -jar md-java/target/md.jar billiard --help
```

| Flag | Descripción | Default |
|---|---|---|
| `--scheme` | `verlet`, `velocity-verlet` | (obligatorio) |
| `--dt` | paso de integración (s) | 1e-5 |
| `--tf` | tiempo final (s), múltiplo de `dt` | 10 |
| `--save-dt` | intervalo de guardado (s), múltiplo de `dt` | 5e-2 |
| `--n` | cantidad de partículas | 300 |
| `--xo` | obstáculos en `(±xo, 0)`, `r ≤ xo ≤ R − r`; sin el flag no hay obstáculos | — |
| `--seed` | semilla de la condición inicial | 1 |
| `--init` | `random` (inserción al azar, hasta N ≈ 465) o `hex` (sitios al azar de una red triangular de lado 2r, hasta 714–716) | `random` |
| `--R`, `--r`, `--m`, `--k`, `--v0` | radio del dominio (m), radio de partículas (m), masa (kg), constante elástica (N/m), módulo de la velocidad inicial (m/s) | 0.51, 0.0175, 0.025, 1e4, 1 |
| `--out` | directorio de salida | `output/billiard/<esquema>_N<n>_dt<dt>_s<seed>` |

Salida en `--out`: `static.txt` (N; R; `r m` por partícula; K; `x y r` por obstáculo),
`dynamic.txt` (por bloque: `t` y `x y vx vy estado` por partícula, estado 0 = fresca, 1 = usada,
precisión completa), `conversions.csv` (`t,id` del primer contacto con un obstáculo) y `run.json`.

Punto 2.1a (energía vs dt, N = 300 sin obstáculos, 10 semillas × 12 dt × 2 esquemas; ~20 min
con 14 núcleos; saltea las corridas ya hechas):

```bash
./scripts/run_energy_sweep.sh      # → output/billiard/energy_dt/<esquema>_dt<dt>_s<seed>/
python3 analysis/plot_energy_dt.py # → analysis/figures/ej2/energia_*.png + tabla por stdout
```

Punto 2.1b (tiempo de ejecución vs N, TP3 y TP4 en esta máquina, 10 realizaciones por N; ~1.5 h
secuencial, sin otra carga pesada mientras mide):

```bash
./scripts/run_time_vs_n.sh         # → output/tp3_time_vs_n/ y output/billiard/time_vs_n/
python3 analysis/plot_time_vs_n.py # → analysis/figures/ej2/tiempo_vs_n.png + tabla por stdout
```

`--bench N1,N2,... --seeds k` corre todas las realizaciones en una sola JVM (calentamiento previo,
orden aleatorio, sin `dynamic.txt`); el tiempo es `loopTimeMs` de cada `run.json`.

Animación (un cuadro por estado guardado, sin interpolar; la superposición de los contactos se ve
más oscura):

```bash
python3 analysis/animate_billiard.py <corrida> --stride 2                 # → <corrida>/animation.mp4
python3 analysis/animate_billiard.py <corrida> --zoom 0 0 0.15            # cuadrado de 0.3 m centrado en (0, 0)
python3 analysis/animate_billiard.py <corrida> --snapshot 5 --out f.png   # fotograma para el PDF
```
