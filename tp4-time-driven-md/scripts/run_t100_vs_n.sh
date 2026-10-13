#!/usr/bin/env bash
# Punto 2.4a: t_90 y t_100 vs densidad. Mismo sistema y mismas semillas que el benchmark del 2.1b
# (x_o = r, red hexagonal, dt = 10⁻⁵ s, Velocity Verlet): el motor es determinista, así que los
# primeros 30 s de cada corrida son bit a bit la corrida del 2.1b, extendida hasta F_u = 1
# (--stop-at-t100) o hasta t_max = 1500 s. Estado cada 5 s (~1 GB en total como máximo).
# Escribe output/billiard/t100_vs_n/N<N>/s<seed>/. Corre en paralelo (JOBS), N grandes primero
# (son las más largas), y saltea las corridas que ya tienen run.json.
#
# NO correr mientras mide scripts/run_time_vs_n.sh.
#
# Uso:
#   ./scripts/run_t100_vs_n.sh               # JOBS = nproc - 2
#   JOBS=4 NS="25 50" SEEDS="1 2" ./scripts/run_t100_vs_n.sh
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JAR="$ROOT/md-java/target/md.jar"
OUT="$ROOT/output/billiard/t100_vs_n"
NS="${NS:-25 50 100 150 200 300 400 500 600 625 650 675}"
SEEDS="${SEEDS:-1 2 3 4 5 6 7 8 9 10}"
TMAX="${TMAX:-1500}"
JOBS="${JOBS:-$(( $(nproc) > 2 ? $(nproc) - 2 : 1 ))}"

if [[ ! -f "$JAR" ]]; then
    echo "No existe $JAR: compilar con 'mvn package' desde la raíz del repo" >&2
    exit 1
fi
mkdir -p "$OUT"
for n in $(echo $NS | tr ' ' '\n' | sort -gr); do
    for seed in $SEEDS; do
        [[ -f "$OUT/N$n/s$seed/run.json" ]] || echo "$n $seed"
    done
done | xargs -P "$JOBS" -L 1 sh -c \
    'java -jar "$0" billiard --scheme velocity-verlet --n "$3" --seed "$4" --xo 0.0175 --init hex \
        --dt 1e-5 --tf "$2" --save-dt 5 --stop-at-t100 --out "$1/N$3/s$4"' "$JAR" "$OUT" "$TMAX"
