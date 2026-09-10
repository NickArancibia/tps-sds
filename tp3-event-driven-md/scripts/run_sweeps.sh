#!/usr/bin/env bash
# Punto 1.2: <t_90> por configuración de obstáculos. Corre cada config de output/sweeps/*/*/config.txt
# (generadas por analysis/gen_configs.py) más la mesa vacía, con N = 100, t_f = 100 s (el t_max de
# la competencia) y --stop-at-t90, una seed distinta por realización. Escribe
# output/sweeps/<barrido>/<punto>/s<seed>/{goals.csv,run.json,...} y output/sweeps/empty/s<seed>/.
# Sin dynamic.txt (para el DCM del punto 1.3 se corre aparte con --every 1).
#
# Las corridas van en paralelo (acá no se mide tiempo de ejecución).
#
# Uso:
#   ./scripts/run_sweeps.sh [seeds] [jobs]      (default 20 seeds, 8 en paralelo)
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JAR="$ROOT/billiard-java/target/billiard.jar"
SWEEPS="$ROOT/output/sweeps"
SEEDS="${1:-20}"
JOBS="${2:-8}"
TF=100

if [[ ! -f "$JAR" ]]; then
    echo "No existe $JAR: compilar con 'mvn package' desde la raíz del repo" >&2
    exit 1
fi
if ! ls "$SWEEPS"/*/*/config.txt >/dev/null 2>&1; then
    echo "No hay configuraciones en $SWEEPS: correr analysis/gen_configs.py" >&2
    exit 1
fi

run_one() {
    local out="$1" seed="$2" cfg="$3"
    local args=(--N 100 --tf "$TF" --seed "$seed" --stop-at-t90 --out "$out")
    [[ "$cfg" != "-" ]] && args+=(--obstacles "$cfg")
    mkdir -p "$(dirname "$out")"
    if ! java -jar "$JAR" "${args[@]}" >"$out.log" 2>&1; then
        echo "FALLÓ: $out (ver $out.log)" >&2
        return 1
    fi
    rm -f "$out.log"
}
export -f run_one
export JAR TF

{
    for seed in $(seq 1 "$SEEDS"); do
        echo "$SWEEPS/empty/s$seed" "$seed" "-"
    done
    for cfg in "$SWEEPS"/*/*/config.txt; do
        dir="$(dirname "$cfg")"
        for seed in $(seq 1 "$SEEDS"); do
            echo "$dir/s$seed" "$seed" "$cfg"
        done
    done
} | xargs -P "$JOBS" -L 1 bash -c 'run_one "$0" "$1" "$2"'
echo "Barridos terminados: $SWEEPS"
