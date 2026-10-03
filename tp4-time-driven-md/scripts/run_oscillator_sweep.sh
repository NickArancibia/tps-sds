#!/usr/bin/env bash
# Punto 1.2: barrido de dt para los 4 esquemas del oscilador amortiguado (t_f = 5 s, estado
# guardado cada 10⁻² s). Escribe output/oscillator/sweep/<esquema>_dt<dt>/{trajectory.csv,run.json}.
# Todos los dt dividen exactamente a 10⁻² s y a 5 s (mismos instantes guardados en todas las curvas).
#
# Uso:
#   ./scripts/run_oscillator_sweep.sh
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JAR="$ROOT/md-java/target/md.jar"
OUT="$ROOT/output/oscillator/sweep"
SCHEMES="beeman verlet velocity-verlet euler-pc"
DTS="5e-3 2e-3 1e-3 5e-4 2e-4 1e-4 5e-5 2e-5 1e-5 5e-6 2e-6 1e-6"

if [[ ! -f "$JAR" ]]; then
    echo "No existe $JAR: compilar con 'mvn package' desde la raíz del repo" >&2
    exit 1
fi
rm -rf "$OUT"
for scheme in $SCHEMES; do
    for dt in $DTS; do
        java -jar "$JAR" oscillator --scheme "$scheme" --dt "$dt" --out "$OUT/${scheme}_dt$dt"
    done
done
