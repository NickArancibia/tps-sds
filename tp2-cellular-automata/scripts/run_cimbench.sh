#!/usr/bin/env bash
# Comparación de tiempos del CIM (punto g del enunciado): las tres series de
# `analysis/figures/cim_tp1_vs_tp2.png`, medidas en la misma máquina y en la misma sesión.
#
#   1. TP1: bench del TP1 con --fresh: 50 configuraciones uniformes con semillas distintas,
#      una llamada cronometrada sobre cada una, así ninguna llamada repite una configuración
#      ya vista (como en la simulación, donde las partículas se mueven entre llamadas).
#   2-3. TP2 Vicsek y votante: 5 seeds por ρ, η = 0.5, 1000 pasos; el post-proceso promedia
#      las 500 llamadas de la segunda mitad.
#
# El tiempo por llamada depende de N y de la configuración espacial (η), no de la seed, así
# que no hace falta el barrido completo de run_sweeps.sh.
#
# Un tiempo de ejecución solo es comparable contra otro medido en el mismo equipo y en las
# mismas condiciones: correr con el equipo enchufado y sin otras cargas (navegador, IDE).
# En una notebook a batería las mediciones varían hasta 3x entre ejecuciones.
#
# Requiere los jars compilados desde la raíz del repo (`mvn -q -DskipTests package`).
# Vuelve a correr todo desde cero (borra output/cimbench y el CSV del TP1) para que las
# series salgan de la misma sesión.
#
# Uso:  ./scripts/run_cimbench.sh
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JAR="$ROOT/vicsek-java/target/vicsek.jar"
TP1_JAR="$ROOT/../tp1-cell-index-method/cim-java/target/cim.jar"
TP1_BENCH="$ROOT/../tp1-cell-index-method/output/bench"
OUT="$ROOT/output/cimbench"

[[ -s "$JAR" && -s "$TP1_JAR" ]] || { echo "Faltan los jars: correr 'mvn -q -DskipTests package' en la raíz."; exit 1; }

MODELS="vicsek voter"
# N = 200, 400, 800 con L = 10: los mismos N que barre el bench del TP1.
RHOS="2 4 8"
SEEDS="1 2 3 4 5"
ETA=0.5
STEPS=1000

TP1_COMMON=(--sweep N --N 200,400,800 --L 10 --M 10 --rc 1.0 --rmin 0 --rmax 0 --pbc)

rm -rf "$OUT"
mkdir -p "$TP1_BENCH"

echo "== TP1 (50 configuraciones x 1 llamada)"
java -cp "$TP1_JAR" ar.edu.itba.sds.bench.BenchmarkRunner "${TP1_COMMON[@]}" \
     --seeds 50 --fresh --out "$TP1_BENCH/bench_tp2_geometry_pbc.csv"

echo "== TP2 (5 seeds x 3 rho x 2 modelos)"
for model in $MODELS; do
    for rho in $RHOS; do
        for seed in $SEEDS; do
            dir="$OUT/$model/rho${rho}/s${seed}"
            mkdir -p "$dir"
            java -jar "$JAR" --model "$model" --rho "$rho" --eta "$ETA" --steps "$STEPS" \
                 --seed "$seed" --out "$dir" > "$dir/stdout.log" 2>&1 \
                && echo "OK   $model rho=$rho seed=$seed" \
                || echo "FAIL $model rho=$rho seed=$seed (ver $dir/stdout.log)"
        done
    done
done

echo "Listo: $(find "$OUT" -name run.json | wc -l) corridas del TP2."
(cd "$ROOT/analysis" && python3 plot_cim_times.py)
