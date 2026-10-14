#!/usr/bin/env bash
# Punto 2.3: distribución del módulo de la velocidad. Sin obstáculos, N = 100, todas con |v| = v0 =
# 1 m/s al inicio, red hexagonal (mismo método que el resto del TP), dt = 10⁻⁵ s, Velocity Verlet,
# t_f = 20 s, estado cada 0.01 s (las velocidades salen de dynamic.txt). Semillas 1–10.
# Escribe output/billiard/speed_dist/s<seed>/. Corre en paralelo (JOBS) y saltea las corridas que
# ya tienen run.json.
#
# Uso:
#   ./scripts/run_speed_dist.sh               # JOBS = nproc - 2
#   SEEDS="11 12" TF=20 ./scripts/run_speed_dist.sh
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JAR="$ROOT/md-java/target/md.jar"
OUT="$ROOT/output/billiard/speed_dist"
SEEDS="${SEEDS:-1 2 3 4 5 6 7 8 9 10}"
TF="${TF:-20}"
JOBS="${JOBS:-$(( $(nproc) > 2 ? $(nproc) - 2 : 1 ))}"

if [[ ! -f "$JAR" ]]; then
    echo "No existe $JAR: compilar con 'mvn package' desde la raíz del repo" >&2
    exit 1
fi
mkdir -p "$OUT"
for seed in $SEEDS; do
    [[ -f "$OUT/s$seed/run.json" ]] || echo "$seed"
done | xargs -P "$JOBS" -L 1 sh -c \
    'java -jar "$0" billiard --scheme velocity-verlet --n 100 --seed "$3" --init hex \
        --dt 1e-5 --tf "$2" --save-dt 0.01 --out "$1/s$3"' "$JAR" "$OUT" "$TF"
