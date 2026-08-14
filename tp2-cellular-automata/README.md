# SdS TP2 — Autómata Off-Lattice: Bandadas (Vicsek / Votante)

Motor de simulación en **Java** (módulo `vicsek-java`, usa el CIM de la librería `common/` de la
raíz). El contexto completo del TP está en [AGENTS.md](AGENTS.md) y el enunciado en
[docs/Enunciado.md](docs/Enunciado.md).

## Requisitos

- Java 21 y Maven

## Compilar

```bash
# Desde la raíz del repositorio (compila common + todos los TPs)
mvn package          # genera tp2-cellular-automata/vicsek-java/target/vicsek.jar
```

## Correr una simulación

```bash
java -jar vicsek-java/target/vicsek.jar --model vicsek --rho 4 --eta 0.5 --steps 2000 \
     --seed 42 --out output/demo
```

Opciones principales (`--help` lista todas):

| Flag | Descripción | Default |
|---|---|---|
| `--model` | `vicsek` (promedia vecinos + sí misma) o `voter` (copia un vecino al azar) | `vicsek` |
| `--rho` | densidad N/L² (define N si no se pasa `--N`) | 4 |
| `--N` | cantidad de partículas (pisa a `--rho`) | — |
| `--L` | lado de la caja (PBC siempre activas) | 10 |
| `--rc` | radio de interacción entre centros | 1.0 |
| `--eta` | amplitud del ruido: Δθ ~ U[-η/2, η/2] | 0.5 |
| `--v` | rapidez de las partículas | 0.03 |
| `--dt` | paso temporal | 1.0 |
| `--steps` | pasos a simular | 2000 |
| `--seed` | semilla (usar seeds distintas para promediar) | 42 |
| `--every` | cada cuántos pasos se guarda un bloque dinámico | 1 |

## Salida

En `--out` (o `output/<auto>/`):

- `static.txt` y `dynamic.txt` — formato de cátedra, para animaciones.
- `observables.csv` — `time,polarization,largest_cluster_fraction`, una fila por paso.
- `run.json` — inputs de la corrida + tiempos de cada llamada al CIM (punto g).
