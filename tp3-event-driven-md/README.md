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
| `--live` | modo competencia: una línea por cada nueva conversión y al final `t_90` (en lugar del resumen completo, que queda en `run.json`) | — |
| `--out` | directorio de salida | `output/N<N>_K<K>_seed<seed>` |

## Competencia (punto 1.4)

5 realizaciones de `Config.txt` con los parámetros fijos del enunciado (N = 100, v0 = 1 m/s,
r = 0.0175 m, m = 0.025 kg, L = 1.20 m, W = 0.68 m, d = 0.20 m, t_max = 100 s), sin `dynamic.txt`.
Compila el jar si falta.

```bash
# 1) Antes de empezar: generar las 5 condiciones iniciales (seeds distintas; sin seeds usa la hora)
./scripts/competencia.sh gen output/competencia [s1 s2 s3 s4 s5]   # -> ci1..ci5/initial.txt, seeds.txt

# 2) Cuando lo indiquen los docentes: correr las 5
./scripts/competencia.sh run output/competencia                   # o: run ini1.txt ... ini5.txt
```

Cada corrida imprime `convertidas: k / 100  (t = ... s)` en cada nueva conversión y al final
`t_90 = ... s` (o `t_90 NO ALCANZADO: k / 100 convertidas a t_max`). Al terminar, tabla de los 5
`t_90` y `<t_90> ± desvío` (ddof = 1). Por defecto cada corrida corta en `t_90`
(`--stop-at-t90`); con `HASTA_TMAX=1` sigue hasta t_max. `./scripts/competencia.sh all <dir>
[seeds]` hace los dos pasos seguidos (para ensayar). Las 5 corridas tardan ~3 s en total.

A mano, una corrida: `java -jar billiard-java/target/billiard.jar --obstacles Config.txt --tf 100
--initial ci1/initial.txt --stop-at-t90 --live --out run1`.

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
  1 usada) por partícula, en el instante de cada evento (o cada k), más `t = 0` y el último evento antes de `tf` (no se escribe ningún estado en tiempos que no sean eventos).
- `run.json` — inputs, `t_90`, conteo de eventos por tipo, energía cinética inicial y final,
  tiempo del lazo de eventos y total.
