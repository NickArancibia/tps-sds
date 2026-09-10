#!/usr/bin/env bash
# Punto 1.1: tiempo de ejecución en función de N, mesa vacía, t_f = 30 s, varias realizaciones
# (seeds distintas) por N. Escribe output/time_vs_n/N<N>/s<seed>/{run.json,goals.csv,...}.
#
# Usa el modo --bench del motor: UNA sola JVM, calentamiento previo (JIT y frecuencia del CPU)
# y todas las corridas seguidas en orden aleatorio. Medir cada corrida en una JVM nueva no sirve
# para N chico: el lazo dura milisegundos y la medición queda dominada por el JIT y por el gestor
# de energía del CPU (governor powersave: la misma corrida de N = 100 tardaba 125 ms dentro de un
# barrido sostenido y 340 ms suelta). No se escribe dynamic.txt: el tiempo a usar es loopTimeMs de
# run.json (solo el lazo de eventos). No correr nada pesado en paralelo mientras mide.
#
# Uso:
#   ./scripts/run_time_vs_n.sh [seeds]        (default 20; el enunciado pide al menos 10)
set -eu

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
JAR="$ROOT/billiard-java/target/billiard.jar"
OUT="$ROOT/output/time_vs_n"
SEEDS="${1:-20}"
# Fracción de área N·π·r²/(L·W): 0.03 (N=25) … 0.47 (N=400). Más allá la inserción aleatoria
# secuencial deja de converger (límite de empaquetamiento aleatorio en 2D ≈ 0.55).
NS="25,50,100,150,200,300,400"

if [[ ! -f "$JAR" ]]; then
    echo "No existe $JAR: compilar con 'mvn package' desde la raíz del repo" >&2
    exit 1
fi
rm -rf "$OUT"
java -jar "$JAR" --bench "$NS" --seeds "$SEEDS" --tf 30 --out "$OUT"
