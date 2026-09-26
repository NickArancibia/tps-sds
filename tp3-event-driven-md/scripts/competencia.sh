#!/usr/bin/env bash
# Punto 1.4: competencia en vivo. 5 realizaciones de la configuración entregada (Config.txt) con
# los parámetros fijos del enunciado: N = 100, v0 = 1 m/s, r = 0.0175 m, m = 0.025 kg,
# L = 1.20 m, W = 0.68 m, d = 0.20 m, t_max = 100 s.
#
# Dos pasos, como pide el enunciado (las condiciones iniciales se generan antes y se corre
# cuando lo indiquen los docentes):
#   gen  -> una condición inicial por realización (seed distinta) en <dir>/ci<i>/initial.txt
#   run  -> corre cada una con --live: imprime las convertidas en cada nueva conversión y al
#           final t_90; después, tabla con los t_90 y <t_90> ± desvío (ddof = 1).
# Sin dynamic.txt (no se pasa --every). Por defecto cada corrida corta en t_90 (--stop-at-t90):
# t_90 ya quedó determinado y ahorra tiempo de exposición; si no se alcanza, corre hasta t_max y
# reporta las convertidas a t_max (criterio de desempate del ranking). Con HASTA_TMAX=1 corre
# siempre hasta t_max.
#
# Uso:
#   ./scripts/competencia.sh gen [dir] [seed1 ... seedK]   (default: output/competencia, 5 seeds
#                                                           distintas a partir de la hora actual)
#   ./scripts/competencia.sh run [dir]                     (corre <dir>/ci*/initial.txt)
#   ./scripts/competencia.sh run <ini1> ... <iniK>         (corre archivos x y vx vy dados; salida
#                                                           en $OUT, default output/competencia)
#   ./scripts/competencia.sh all [dir] [seed1 ... seedK]   (gen + run, para ensayar)
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(cd "$ROOT/.." && pwd)"
JAR="$ROOT/billiard-java/target/billiard.jar"
CONFIG="$ROOT/Config.txt"
N_RUNS=5
PARAMS=(--N 100 --v0 1.0 --r 0.0175 --m 0.025 --L 1.20 --W 0.68 --d 0.20 --tf 100
        --obstacles "$CONFIG")

usage() {
    sed -n '2,/^set -eu/p' "$0" | sed '$d; s/^# \{0,1\}//'
    exit 1
}

# Hora actual en segundos con milisegundos (perl está en macOS y Linux; si no, segundos enteros).
now() {
    perl -MTime::HiRes=time -e 'printf "%.3f", time' 2>/dev/null || date +%s
}

ensure_jar() {
    if [[ ! -f "$JAR" ]]; then
        echo "No existe $JAR: compilando con Maven..."
        (cd "$REPO" && mvn -q package -pl tp3-event-driven-md/billiard-java -am)
    fi
}

gen() {
    local dir="$1"; shift
    local seeds=("$@")
    if (( ${#seeds[@]} == 0 )); then
        local base
        base="$(date +%s)"
        for i in $(seq 1 "$N_RUNS"); do
            seeds+=("$((base + i))")
        done
    fi
    mkdir -p "$dir"
    : >"$dir/seeds.txt"
    local i=0
    for seed in "${seeds[@]}"; do
        i=$((i + 1))
        java -jar "$JAR" "${PARAMS[@]}" --seed "$seed" --gen-initial --out "$dir/ci$i"
        echo "ci$i $seed" >>"$dir/seeds.txt"
    done
    echo "Seeds usadas en $dir/seeds.txt"
}

run() {
    local out="$1"; shift
    local inits=("$@")
    local extra=(--live)
    [[ "${HASTA_TMAX:-0}" == "1" ]] || extra+=(--stop-at-t90)
    local k=${#inits[@]}
    (( k == N_RUNS )) || echo "AVISO: se pidieron $N_RUNS realizaciones y hay $k" >&2

    local start end i=0
    local runs=()
    start="$(now)"
    for ini in "${inits[@]}"; do
        i=$((i + 1))
        echo
        echo "==================== Realización $i / $k ===================="
        java -jar "$JAR" "${PARAMS[@]}" "${extra[@]}" --initial "$ini" --out "$out/run$i"
        runs+=("$out/run$i/run.json")
    done
    end="$(now)"

    echo
    echo "==================== Resultados ===================="
    printf '%-6s %-14s %-12s %s\n' "real." "t_90 (s)" "convertidas" "condición inicial"
    local values="" t90 goals ini
    i=0
    for json in "${runs[@]}"; do
        i=$((i + 1))
        t90="$(sed -n 's/^  "t90": \(.*\),$/\1/p' "$json")"
        goals="$(sed -n 's/^  "goals": \(.*\),$/\1/p' "$json")"
        values+="$t90 $goals"$'\n'
        [[ "$t90" == "null" ]] && t90="NO ALCANZADO"
        ini="${inits[$((i - 1))]}"
        printf '%-6s %-14s %-12s %s\n' "$i" "$t90" "$goals" "$(basename "$(dirname "$ini")")/$(basename "$ini")"
    done
    printf '%s' "$values" | awk -v runs="$k" '
        { if ($1 != "null") { n++; s += $1; ss += $1 * $1 } else { miss++ }; g += $2 }
        END {
            if (miss > 0) {
                printf "\n%d de %d realizaciones NO alcanzaron F_g = 0.9 antes de t_max.\n", miss, runs
                printf "Convertidas promedio a t_max (desempate del ranking): %.1f\n", g / runs
            }
            if (n >= 2) {
                mean = s / n; var = (ss - n * mean * mean) / (n - 1); if (var < 0) var = 0
                sd = sqrt(var)
                # error a 1 cifra significativa (2 si empieza en 1), valor al mismo decimal
                dec = 0
                if (sd > 0) {
                    l = log(sd) / log(10); e = int(l); if (l < 0 && l != e) e--
                    lead = int(sd / 10 ^ e + 1e-9); dec = -e + (lead == 1 ? 1 : 0); if (dec < 0) dec = 0
                }
                printf "\n<t_90> = %.*f ± %.*f s   (n = %d, desvío ddof = 1; sin redondear: %.6f ± %.6f)\n",
                       dec, mean, dec, sd, n, mean, sd
            } else if (n == 1) {
                printf "\n<t_90> = %.6f s (una sola realización, sin desvío)\n", s
            }
        }'
    awk -v a="$start" -v b="$end" -v k="$k" -v o="$out" \
        'BEGIN { printf "Tiempo total de las %d corridas: %.1f s   (archivos en %s)\n", k, b - a, o }'
}

cmd="${1:-}"
[[ -n "$cmd" ]] || usage
shift
case "$cmd" in
    gen|all)
        ensure_jar
        dir="${1:-$ROOT/output/competencia}"
        if [[ $# -gt 0 ]]; then shift; fi
        gen "$dir" "$@"
        if [[ "$cmd" == "all" ]]; then
            inits=()
            for f in "$dir"/ci*/initial.txt; do inits+=("$f"); done
            run "$dir" "${inits[@]}"
        fi
        ;;
    run)
        ensure_jar
        dir="${1:-$ROOT/output/competencia}"
        if [[ $# -le 1 && -d "$dir" ]]; then
            inits=()
            for f in "$dir"/ci*/initial.txt; do
                [[ -f "$f" ]] && inits+=("$f")
            done
            if (( ${#inits[@]} == 0 )); then
                echo "No hay condiciones iniciales en $dir/ci*/initial.txt: correr 'gen' primero" >&2
                exit 1
            fi
            run "$dir" "${inits[@]}"
        else
            for f in "$@"; do
                [[ -f "$f" ]] || { echo "No existe $f" >&2; exit 1; }
            done
            run "${OUT:-$ROOT/output/competencia}" "$@"
        fi
        ;;
    *)
        usage
        ;;
esac
