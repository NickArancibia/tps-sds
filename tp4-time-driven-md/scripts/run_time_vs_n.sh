#!/usr/bin/env bash
# Punto 2.1b: tiempo de ejecución vs N, en esta máquina, para los dos motores:
#   1. TP3 (dinámica molecular por eventos), su punto 1.1: mesa rectangular vacía, t_f = 30 s,
#      red hexagonal (--init hex) para todos los N → output/tp3_time_vs_n/N<N>/s<seed>/
#   2. TP4 (paso temporal): obstáculos en contacto (x_o = r), red hexagonal para todos los N,
#      dt = 10⁻⁵ s (2.1a), t_f = 30 s → output/billiard/time_vs_n/N<N>/s<seed>/
# Cada motor usa su modo --bench: una sola JVM, calentamiento previo, corridas en orden aleatorio,
# sin dynamic.txt; el tiempo es loopTimeMs de run.json. Las corridas del TP4 guardan
# conversions.csv; scripts/run_t100_vs_n.sh las extiende (mismas semillas) para el 2.4a.
#
# Solo se borran y re-miden los N de las listas NS3 / NS4; los demás N ya medidos quedan. Lista
# vacía = no correr ese motor. Con RESUME=1 no se borra nada: los dos --bench saltean las
# corridas que ya tienen run.json (retomar una sesión cortada). Corre secuencial: NO correr nada
# pesado en paralelo mientras mide.
#
# Uso:
#   ./scripts/run_time_vs_n.sh                        # los dos motores, todos los N, SEEDS = 10
#   NS4= ./scripts/run_time_vs_n.sh                   # solo el TP3
#   NS4=625,650 ./scripts/run_time_vs_n.sh            # TP3 completo + esos N del TP4
#   RESUME=1 NS4=625,650 ./scripts/run_time_vs_n.sh   # retomar lo anterior donde quedó
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JAR4="$ROOT/md-java/target/md.jar"
JAR3="$ROOT/../tp3-event-driven-md/billiard-java/target/billiard.jar"
OUT3="$ROOT/output/tp3_time_vs_n"
OUT4="$ROOT/output/billiard/time_vs_n"
SEEDS="${SEEDS:-10}"
NS3="${NS3-25,50,100,150,200,300,400,500,600,625,650,675}"
NS4="${NS4-25,50,100,150,200,300,400,500,600,625,650,675}"

for jar in "$JAR3" "$JAR4"; do
    if [[ ! -f "$jar" ]]; then
        echo "No existe $jar: compilar con 'mvn package' desde la raíz del repo" >&2
        exit 1
    fi
done
if [[ "${RESUME:-0}" != 1 ]]; then
    for n in ${NS3//,/ }; do rm -rf "$OUT3/N$n"; done
    for n in ${NS4//,/ }; do rm -rf "$OUT4/N$n"; done
fi
if [[ -n "$NS3" ]]; then
    java -jar "$JAR3" --bench "$NS3" --seeds "$SEEDS" --init hex --tf 30 --out "$OUT3"
fi
if [[ -n "$NS4" ]]; then
    java -jar "$JAR4" billiard --scheme velocity-verlet --bench "$NS4" --seeds "$SEEDS" --xo 0.0175 \
        --init hex --dt 1e-5 --tf 30 --out "$OUT4"
fi
