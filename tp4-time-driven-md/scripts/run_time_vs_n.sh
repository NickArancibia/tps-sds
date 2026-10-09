#!/usr/bin/env bash
# Punto 2.1b: tiempo de ejecución vs N, en esta máquina, para los dos motores:
#   1. TP3 (dinámica molecular por eventos), su punto 1.1: mesa rectangular vacía, t_f = 30 s,
#      N = 25 … 400 (su inserción al azar no pasa de ~400) → output/tp3_time_vs_n/N<N>/s<seed>/
#   2. TP4 (paso temporal): obstáculos en contacto (x_o = r), red hexagonal para todos los N,
#      dt = 10⁻⁵ s (2.1a), t_f = 30 s, N = 25 … 700 → output/billiard/time_vs_n/N<N>/s<seed>/
# Cada motor usa su modo --bench: una sola JVM, calentamiento previo, corridas en orden aleatorio,
# sin dynamic.txt; el tiempo es loopTimeMs de run.json. Las corridas del TP4 guardan
# conversions.csv, que el 2.4a usa para t_90 y t_100.
#
# Corre secuencial y tarda ~1.5 h con SEEDS = 10: NO correr nada pesado en paralelo mientras mide.
#
# Uso:
#   ./scripts/run_time_vs_n.sh             # SEEDS = 10 (el enunciado pide al menos 10)
#   SEEDS=2 ./scripts/run_time_vs_n.sh
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JAR4="$ROOT/md-java/target/md.jar"
JAR3="$ROOT/../tp3-event-driven-md/billiard-java/target/billiard.jar"
SEEDS="${SEEDS:-10}"
NS3="25,50,100,150,200,300,400"
NS4="25,50,100,150,200,300,400,500,600,700"

for jar in "$JAR3" "$JAR4"; do
    if [[ ! -f "$jar" ]]; then
        echo "No existe $jar: compilar con 'mvn package' desde la raíz del repo" >&2
        exit 1
    fi
done
rm -rf "$ROOT/output/tp3_time_vs_n" "$ROOT/output/billiard/time_vs_n"
java -jar "$JAR3" --bench "$NS3" --seeds "$SEEDS" --tf 30 --out "$ROOT/output/tp3_time_vs_n"
java -jar "$JAR4" billiard --scheme velocity-verlet --bench "$NS4" --seeds "$SEEDS" --xo 0.0175 \
    --init hex --dt 1e-5 --tf 30 --out "$ROOT/output/billiard/time_vs_n"
