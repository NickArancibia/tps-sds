#!/usr/bin/env bash
# Barrido completo del TP2: modelos {vicsek, voter} × ρ {2,4,8} × grilla de η × 50 seeds,
# más corridas "de animación" (bloques dinámicos cada 5 pasos) para casos característicos.
#
# Es reanudable: si una corrida ya tiene observables.csv se saltea. Uso:
#   ./scripts/run_sweeps.sh [jobs_paralelos]   (default 12)
set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JAR="$ROOT/vicsek-java/target/vicsek.jar"
OUT="$ROOT/output"
JOBS="${1:-12}"

MODELS="vicsek voter"
# Densidades: enteras (N = 200, 400, 800) + bajas 1/pi, 1/(2pi), 1/(3pi) (N = 32, 16, 11),
# elegidas para dar ~1, 0.5 y 0.33 vecinos promedio dentro de rc (debajo de la percolación).
RHOS="2 4 8 0.3183 0.1592 0.1061"
ETAS="0.0 0.25 0.5 0.75 1.0 1.5 2.0 2.5 3.0 3.5 4.0 4.5 5.0 5.5 6.28"
SEEDS=$(seq 1 50)
STEPS=2000
# Corridas más largas donde la última mitad (que promedia el post-proceso) no alcanza a
# ser estacionaria en 2000 pasos:
#  - densidades bajas (N chico): se ordenan mucho más lento con η bajo → 5000 pasos;
#  - votante con η = 0: único caso con estado absorbente (consenso, v_a = 1) y su tiempo
#    de consenso crece con N (a ρ = 8, 13/50 seeds no absorbían en 2000) → 10000 pasos.
steps_for() {
    local model="$1" rho="$2" eta="$3"
    if [[ "$model" == voter && "$eta" == "0.0" ]]; then echo 10000
    elif [[ "$rho" == 0.* ]]; then echo 5000
    else echo "$STEPS"
    fi
}
export -f steps_for

# Etas características para animaciones (ordenado / transición / desordenado).
ANIM_ETAS="0.5 2.0 4.0"

run_one() {
    local model="$1" rho="$2" eta="$3" seed="$4" every="$5" dir="$6"
    local steps; steps="$(steps_for "$model" "$rho" "$eta")"
    if [[ -s "$dir/observables.csv" ]]; then
        return 0
    fi
    mkdir -p "$dir"
    if java -jar "$JAR" --model "$model" --rho "$rho" --eta "$eta" --steps "$steps" \
            --seed "$seed" --every "$every" --out "$dir" > "$dir/stdout.log" 2>&1; then
        echo "OK   $model rho=$rho eta=$eta seed=$seed"
    else
        echo "FAIL $model rho=$rho eta=$eta seed=$seed (ver $dir/stdout.log)"
    fi
}
export -f run_one
export JAR STEPS

jobs_file="$(mktemp)"
trap 'rm -f "$jobs_file"' EXIT

# Corridas de animación primero (pocas y se usan para elegir el estacionario).
for model in $MODELS; do
    for rho in $RHOS; do
        for eta in $ANIM_ETAS; do
            dir="$OUT/anim/$model/rho${rho}_eta${eta}"
            echo "run_one $model $rho $eta 42 5 $dir" >> "$jobs_file"
        done
    done
done

# Barrido principal: solo observables (bloques dinámicos únicamente en t=0 y final).
for model in $MODELS; do
    for rho in $RHOS; do
        for eta in $ETAS; do
            for seed in $SEEDS; do
                dir="$OUT/sweep/$model/rho${rho}/eta${eta}/s${seed}"
                echo "run_one $model $rho $eta $seed 1000000 $dir" >> "$jobs_file"
            done
        done
    done
done

total=$(wc -l < "$jobs_file")
echo "Lanzando $total corridas con $JOBS jobs en paralelo..."
xargs -a "$jobs_file" -P "$JOBS" -I CMD bash -c CMD
echo "Barrido terminado: $(find "$OUT/sweep" -name observables.csv | wc -l) corridas con observables."
