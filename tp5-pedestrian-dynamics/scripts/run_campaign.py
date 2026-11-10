#!/usr/bin/env python3
"""Campaña de corridas del TP5: los tres esquemas, barrido de R_h del híbrido y de los radios
intermedios (niveles) de EDMD, y escalamiento con N.

Cada corrida es una ejecución del motor (una JVM por corrida) sin guardar estados (dynamic.txt
vacío): quedan run.json (inputs, tiempo de evacuación, tiempo de ejecución del lazo, contadores),
events.csv (cruce de puerta y retiro de cada agente) y, en el híbrido, schemes.csv. Se guarda en

    output/campaign/N<N>_L<L>/<config>/seed<k>/

con <config> = tsdmd | edmd_lv<niveles> | hybrid_rh<R_h>.

Estudios (--studies, separados por coma; default todos):
    base    N = 500, L = 50 m: tsdmd, edmd (8 niveles), híbrido con R_h en RH
    n200    lo mismo con N = 200 (alternativa opcional de la cátedra)
    levels  edmd con 0..8 niveles, N = 200 y N = 500, L = 50 m
    room    N = 500, L = 150 y 300 m: tsdmd e híbrido con R_h en RH
    scaling punto (d): tsdmd, edmd (8 niveles) e híbrido (R_h = 0.5 m) con N en SCALING_N, a
            L = 50 m y a densidad inicial constante (la del sistema base: L = 50 m √(N/500))

El tiempo de ejecución sale de estas mismas corridas, así que corren en serie y con las
configuraciones intercaladas dentro de cada seed (la deriva de la máquina afecta a todas por igual);
antes se hace una corrida de descarte de ~12 s. NO correr nada pesado en paralelo. Las corridas con run.json se
saltean (para retomar); --fresh borra antes las de los estudios pedidos.

Uso (desde tp5-pedestrian-dynamics/):
    python3 scripts/run_campaign.py
    python3 scripts/run_campaign.py --studies base,levels --seeds 10
"""

from __future__ import annotations

import argparse
import math
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JAR = ROOT / "cpm-java" / "target" / "cpm.jar"
OUT = ROOT / "output" / "campaign"

# 0.1 m < 2 r_min: nadie pasa a TSDMD (EDMD puro; cualquier R_h < 0.2 m da la misma corrida)
RH = (0.1, 0.2, 0.3, 0.5, 0.75, 1, 1.5, 2, 3, 5, 10)
LEVELS = range(0, 9)
SCALING_N = (100, 200, 300, 500, 700, 1000)


def constant_density_length(n: int) -> float:
    """Lado (m, 2 decimales) con la densidad inicial del sistema base, N = 500 en L = 50 m."""
    return round(50 * math.sqrt(n / 500), 2)


def schemes_and_rh() -> list[tuple[str, tuple[str, ...]]]:
    return [("tsdmd", ()), ("edmd_lv8", ("--levels", "8"))] + hybrid_rh()


def hybrid_rh() -> list[tuple[str, tuple[str, ...]]]:
    return [(f"hybrid_rh{rh:g}", ("--rh", f"{rh:g}")) for rh in RH]


def study(name: str) -> list[tuple[int, float, str, tuple[str, ...]]]:
    """→ corridas (N, L, config, opciones del motor) de un estudio."""
    if name == "base":
        return [(500, 50, c, o) for c, o in schemes_and_rh()]
    if name == "n200":
        return [(200, 50, c, o) for c, o in schemes_and_rh()]
    if name == "levels":
        return [(n, 50, f"edmd_lv{k}", ("--levels", str(k))) for n in (200, 500) for k in LEVELS]
    if name == "room":
        return [(500, length, c, o) for length in (150, 300) for c, o in [("tsdmd", ())] + hybrid_rh()]
    if name == "scaling":
        schemes = [("tsdmd", ()), ("edmd_lv8", ("--levels", "8")), ("hybrid_rh0.5", ("--rh", "0.5"))]
        return [(n, length, c, o) for n in SCALING_N for length in (50, constant_density_length(n))
                for c, o in schemes]
    raise SystemExit(f"estudio desconocido: {name}")


def run_dir(n: int, length: float, config: str, seed: int) -> Path:
    return OUT / f"N{n}_L{length:g}" / config / f"seed{seed}"


def launch(n: int, length: float, config: str, options: tuple[str, ...], seed: int, out: Path, t_max: float) -> dict:
    scheme = config.split("_")[0]
    subprocess.run(
        ["java", "-jar", str(JAR), scheme, "--N", str(n), "--L", f"{length:g}", "--seed", str(seed),
         "--save-t0", "1e9", "--t-max", f"{t_max:g}", "--out", str(out), *options],
        check=True, capture_output=True)
    return json.loads((out / "run.json").read_text())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--studies", default="base,n200,levels,room,scaling")
    parser.add_argument("--seeds", type=int, default=10, help="realizaciones: seeds 1..SEEDS (default 10)")
    parser.add_argument("--t-max", type=float, default=3000, help="corte si no evacúan todos (s)")
    parser.add_argument("--fresh", action="store_true", help="borrar las corridas de estos estudios y re-medir")
    args = parser.parse_args()
    if not JAR.is_file():
        raise SystemExit(f"No existe {JAR}: compilar con 'mvn package' desde la raíz del repo")

    runs: list[tuple[int, float, str, tuple[str, ...]]] = []
    for name in args.studies.split(","):
        for run in study(name):
            if run not in runs:  # corridas compartidas entre estudios (edmd_lv8, N = 500 a L = 50 m, ...)
                runs.append(run)
    if args.fresh:
        for n, length, config, _ in runs:
            shutil.rmtree(OUT / f"N{n}_L{length:g}" / config, ignore_errors=True)

    # Descarte de ~12 s: después de un rato sin carga, las primeras corridas tardan hasta 2.7 veces más
    # (medido: paso temporal con N = 500, 2.4 s contra 0.9 s); una corrida corta no alcanza.
    warmup = OUT / "_descarte"
    launch(500, 50, "edmd", (), 1, warmup, args.t_max)
    shutil.rmtree(warmup)

    start = time.time()
    for seed in range(1, args.seeds + 1):
        for n, length, config, options in runs:
            out = run_dir(n, length, config, seed)
            if (out / "run.json").is_file():
                continue
            meta = launch(n, length, config, options, seed, out, args.t_max)
            evacuation = f"{meta['evacuationTime']:.1f} s" if meta["evacuated"] else f"quedan {meta['remaining']}"
            print(f"[{time.time() - start:6.0f} s] seed {seed:2d} N{n}_L{length:g}/{config}: evacuación {evacuation}, "
                  f"lazo {meta['loopTimeMs'] / 1e3:.2f} s", flush=True)
    print("listo", file=sys.stderr)


if __name__ == "__main__":
    main()
