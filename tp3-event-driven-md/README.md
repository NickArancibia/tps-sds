# SdS TP3 — Simulación Dirigida por Eventos: Billar-Metegol

Dinámica molecular de esferas duras regida por eventos sobre una mesa rectangular con arcos y
obstáculos fijos. Motor en **Java** (módulo `billiard-java`). El contexto completo del TP está en
[AGENTS.md](AGENTS.md) y el enunciado en [docs/Enunciado.md](docs/Enunciado.md).

## Requisitos

- Java 21 y Maven

## Compilar

```bash
# Desde la raíz del repositorio (compila common + todos los TPs)
mvn package          # genera tp3-event-driven-md/billiard-java/target/billiard.jar
```

## Correr una simulación

```bash
# Mesa vacía, 30 s, guardando el estado cada 5 eventos para animar
java -jar billiard-java/target/billiard.jar --N 100 --tf 30 --seed 1 --every 5 --out output/demo

# Con obstáculos (archivo con una línea "x y R" por obstáculo, mismo formato que Config.txt)
java -jar billiard-java/target/billiard.jar --obstacles config.txt --tf 100 --seed 7 --stop-at-t90
```

Opciones principales (`--help` lista todas):

| Flag | Descripción | Default |
|---|---|---|
| `--N` | cantidad de partículas | 100 |
| `--L`, `--W`, `--d` | largo y ancho de la mesa, longitud del arco (m) | 1.20, 0.68, 0.20 |
| `--r`, `--m`, `--v0` | radio (m), masa (kg) y rapidez inicial (m/s) | 0.0175, 0.025, 1.0 |
| `--obstacles` | archivo de obstáculos `x y R` (sin flag: mesa vacía) | — |
| `--tf` | tiempo simulado máximo (s) | 30 |
| `--seed` | semilla (usar seeds distintas para promediar) | 42 |
| `--stop-at-t90` | cortar apenas la fracción de usadas llega a 0.9 | — |
| `--every` | escribir `dynamic.txt` cada k eventos, 1 = todos (0 = no escribir) | 0 |
| `--gen-initial` | solo generar `initial.txt` y salir (competencia) | — |
| `--initial` | correr desde un `initial.txt` dado | — |
| `--verify` | chequear solapamientos tras cada evento (lento, depuración) | — |
| `--out` | directorio de salida | `output/N<N>_K<K>_seed<seed>` |

## Benchmark del punto 1.1

```bash
./scripts/run_time_vs_n.sh 20          # una JVM, calentamiento, N × seeds en orden aleatorio
python3 analysis/plot_time_vs_n.py     # analysis/out/time_vs_n.csv + analysis/figures/time_vs_n.png
```

## Salida

En `--out`:

- `initial.txt` — condición inicial usada (`x y vx vy` por partícula).
- `static.txt` — `N`, `L W d`, `r m` por partícula, `K` y `x y R` por obstáculo.
- `goals.csv` — `time,id`, un renglón por gol (de acá salen `N_g(t)`, `F_g(t)` y `t_90`).
- `dynamic.txt` — solo con `--every`: bloques `t` seguidos de `x y vx vy estado` (0 fresca,
  1 usada) por partícula, en el instante de cada evento (o cada k), más `t = 0` y `t = tf`.
- `run.json` — inputs, `t_90`, conteo de eventos por tipo, energía cinética inicial y final,
  tiempo del lazo de eventos y total.
