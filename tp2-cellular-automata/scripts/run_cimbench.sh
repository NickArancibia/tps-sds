#!/usr/bin/env bash
# Corridas mínimas para la comparación de tiempos del CIM (punto g del enunciado).
#
# El tiempo por llamada al CIM depende de N, no de η ni de la seed, así que para esta
# figura no hace falta el barrido completo de run_sweeps.sh: alcanzan 5 seeds por
# (modelo, ρ) con un η cualquiera. Con 1000 pasos se cronometran 500 llamadas por corrida
# en la mitad que promedia el post-proceso, las mismas 500 repeticiones que mide el bench
# del TP1.
#
# La serie del TP1 tiene que medirse en la misma máquina, si no la comparación es entre
# hardwares y no entre implementaciones:
#   cd ../tp1-cell-index-method
#   java -cp <classes> ar.edu.itba.sds.bench.BenchmarkRunner --sweep N --N 200,400,800 \
#        --L 10 --M 10 --rc 1.0 --rmin 0 --rmax 0 --pbc --reps 500 --seeds 1 \
#        --out output/bench/bench_tp2_geometry_pbc.csv
#
# Uso:  ./scripts/run_cimbench.sh
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JAR="$ROOT/vicsek-java/target/vicsek.jar"
OUT="$ROOT/output/cimbench"

MODELS="vicsek voter"
# N = 200, 400, 800 con L = 10: los mismos N que barre el bench del TP1.
RHOS="2 4 8"
SEEDS="1 2 3 4 5"
ETA=0.5
STEPS=1000

for model in $MODELS; do
    for rho in $RHOS; do
        for seed in $SEEDS; do
            dir="$OUT/$model/rho${rho}/s${seed}"
            [[ -s "$dir/run.json" ]] && continue
            mkdir -p "$dir"
            java -jar "$JAR" --model "$model" --rho "$rho" --eta "$ETA" --steps "$STEPS" \
                 --seed "$seed" --out "$dir" > "$dir/stdout.log" 2>&1 \
                && echo "OK   $model rho=$rho seed=$seed" \
                || echo "FAIL $model rho=$rho seed=$seed (ver $dir/stdout.log)"
        done
    done
done

echo "Listo: $(find "$OUT" -name run.json | wc -l) corridas."
