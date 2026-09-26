#!/usr/bin/env bash
# Entregable (c) del TP3: zip con el código fuente (< 100 KB, ver docs/Enunciado.md).
#
# Contenido (con la misma estructura de directorios del repo, para que compile con
# `mvn package` desde la raíz del zip):
#   - pom.xml raíz recortado: solo los módulos common y tp3-event-driven-md/billiard-java
#     (el del repo lista también TP1 y TP2, que no van).
#   - common/pom.xml + las clases de common que usa el motor (hoy solo cli/CliArgs.java).
#   - tp3-event-driven-md/billiard-java/{pom.xml,src/}: motor de simulación.
#   - tp3-event-driven-md/analysis/{animate.py,common.py,requirements.txt}: código de las
#     animaciones a partir de los outputs primarios (pedido de la cátedra: sin interpolar ni usar
#     tiempos que no sean eventos).
# Nada de outputs, figuras, target/, documentación ni el resto del post-proceso.
#
# Nombre pedido: SdS_TP3_2026Q2GXXCSS_Codigo.zip (XX = grupo, SS = comisión "S" o "S2").
#
# Uso:
#   ./scripts/build_zip.sh [salida.zip]      (default: SdS_TP3_2026Q2G${GRUPO}C${COMISION}_Codigo.zip
#                                             en el directorio actual; GRUPO=02, COMISION=S)
set -euo pipefail

TP="$(cd "$(dirname "$0")/.." && pwd)"
REPO="$(cd "$TP/.." && pwd)"
GRUPO="${GRUPO:-02}"
COMISION="${COMISION:-S}"
OUT="${1:-$PWD/SdS_TP3_2026Q2G${GRUPO}C${COMISION}_Codigo.zip}"
case "$OUT" in /*) ;; *) OUT="$PWD/$OUT" ;; esac
LIMIT=102400

# Clases de common que importa el motor (se detectan de los imports, así no queda nada de más).
COMMON_CLASSES=$(grep -rhoE '^import ar\.edu\.itba\.sds\.common\.[A-Za-z0-9_.]+;' \
    "$TP/billiard-java/src" | sed -E 's/^import (.*);/\1/' | sort -u)

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

# pom raíz sin los módulos de otros TPs (se sacan todos los tp* y se vuelve a agregar el del TP3).
grep -vE '<module>tp[0-9]+-[^<]*</module>' "$REPO/pom.xml" | awk '
    /<\/modules>/ { print "        <module>tp3-event-driven-md/billiard-java</module>" }
    { print }' > "$STAGE/pom.xml"

mkdir -p "$STAGE/common"
cp "$REPO/common/pom.xml" "$STAGE/common/"
for cls in $COMMON_CLASSES; do
    src="common/src/main/java/$(echo "$cls" | tr . /).java"
    mkdir -p "$STAGE/$(dirname "$src")"
    cp "$REPO/$src" "$STAGE/$src"
done

mkdir -p "$STAGE/tp3-event-driven-md/billiard-java" "$STAGE/tp3-event-driven-md/analysis"
cp "$TP/billiard-java/pom.xml" "$STAGE/tp3-event-driven-md/billiard-java/"
cp -R "$TP/billiard-java/src" "$STAGE/tp3-event-driven-md/billiard-java/"
cp "$TP/analysis/animate.py" "$TP/analysis/common.py" "$TP/analysis/requirements.txt" \
    "$STAGE/tp3-event-driven-md/analysis/"
find "$STAGE" -name '.DS_Store' -delete

rm -f "$OUT"
(cd "$STAGE" && zip -q -r -9 -X "$OUT" .)

SIZE=$(wc -c < "$OUT" | tr -d ' ')
unzip -l "$OUT"
echo "$OUT: $SIZE bytes ($(( SIZE / 1024 )) KB)"
if (( SIZE >= LIMIT )); then
    echo "ATENCIÓN: supera los 100 KB pedidos" >&2
    exit 1
fi
