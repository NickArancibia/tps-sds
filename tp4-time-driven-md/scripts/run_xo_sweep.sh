#!/usr/bin/env bash
# Punto 2.2: posición de los obstáculos. Obstáculos en (±x_o, 0) desde x_o = r (en contacto entre
# sí) hasta x_o = R − r (en contacto con la pared), N = 100 y N = 20 (densidad menor), t_max = 100 s
# o hasta F_u = 1 (--stop-at-t100). Red hexagonal (mismo método que 2.1b y 2.4a), dt = 10⁻⁵ s,
# Velocity Verlet, estado cada 0.5 s. Semillas 1–5 (el enunciado pide al menos 5).
# Escribe output/billiard/xo_sweep/N<N>/xo<x_o>/s<seed>/. Corre en paralelo (JOBS) y saltea las
# corridas que ya tienen run.json (se pueden sumar semillas o x_o sin repetir).
#
# Uso:
#   ./scripts/run_xo_sweep.sh                 # JOBS = nproc - 2
#   JOBS=11 SEEDS="6 7 8 9 10" ./scripts/run_xo_sweep.sh
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JAR="$ROOT/md-java/target/md.jar"
OUT="$ROOT/output/billiard/xo_sweep"
NS="${NS:-100 20}"
XOS="${XOS:-0.0175 0.05 0.1 0.15 0.2 0.25 0.3 0.35 0.4 0.45 0.4925}"
SEEDS="${SEEDS:-1 2 3 4 5}"
TMAX="${TMAX:-100}"
JOBS="${JOBS:-$(( $(nproc) > 2 ? $(nproc) - 2 : 1 ))}"

if [[ ! -f "$JAR" ]]; then
    echo "No existe $JAR: compilar con 'mvn package' desde la raíz del repo" >&2
    exit 1
fi
mkdir -p "$OUT"
for n in $NS; do
    for xo in $XOS; do
        for seed in $SEEDS; do
            [[ -f "$OUT/N$n/xo$xo/s$seed/run.json" ]] || echo "$n $xo $seed"
        done
    done
done | xargs -P "$JOBS" -L 1 sh -c \
    'java -jar "$0" billiard --scheme velocity-verlet --n "$3" --xo "$4" --seed "$5" --init hex \
        --dt 1e-5 --tf "$2" --save-dt 0.5 --stop-at-t100 --out "$1/N$3/xo$4/s$5"' "$JAR" "$OUT" "$TMAX"
