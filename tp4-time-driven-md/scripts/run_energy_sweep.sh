#!/usr/bin/env bash
# Punto 2.1a: barrido de dt sin obstáculos, N = 300, t_f = 10 s, estado cada 5·10⁻² s, para las
# dos variantes de Verlet y varias semillas (una condición inicial distinta por semilla; la misma
# condición inicial para todos los dt y esquemas de una semilla).
# Escribe output/billiard/energy_dt/<esquema>_dt<dt>_s<seed>/. Corre en paralelo (JOBS) y saltea
# las corridas que ya tienen run.json (se pueden agregar semillas sin repetir las anteriores).
#
# Uso:
#   ./scripts/run_energy_sweep.sh            # JOBS = nproc - 2
#   JOBS=4 SEEDS="1 2" ./scripts/run_energy_sweep.sh
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JAR="$ROOT/md-java/target/md.jar"
OUT="$ROOT/output/billiard/energy_dt"
SCHEMES="${SCHEMES:-verlet velocity-verlet}"
DTS="${DTS:-5e-3 2e-3 1e-3 5e-4 2e-4 1e-4 5e-5 2e-5 1e-5 5e-6 2e-6 1e-6}"
SEEDS="${SEEDS:-1 2 3 4 5 6 7 8 9 10}"
JOBS="${JOBS:-$(( $(nproc) > 2 ? $(nproc) - 2 : 1 ))}"

if [[ ! -f "$JAR" ]]; then
    echo "No existe $JAR: compilar con 'mvn package' desde la raíz del repo" >&2
    exit 1
fi
mkdir -p "$OUT"
# Los dt más chicos primero: son los más largos y así el paralelismo se aprovecha mejor.
for dt in $(echo $DTS | tr ' ' '\n' | sort -g); do
    for scheme in $SCHEMES; do
        for seed in $SEEDS; do
            [[ -f "$OUT/${scheme}_dt${dt}_s${seed}/run.json" ]] || echo "$scheme $dt $seed"
        done
    done
done | xargs -P "$JOBS" -L 1 sh -c \
    'java -jar "$0" billiard --scheme "$2" --dt "$3" --seed "$4" --n 300 --tf 10 --save-dt 5e-2 \
        --out "$1/$2_dt$3_s$4"' "$JAR" "$OUT"
