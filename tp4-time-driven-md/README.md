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
python3 analysis/plot_ecm.py          # → analysis/figures/ecm_vs_dt.png + tabla por stdout
```
