# AGENTS.md — SdS TP2: Autómata Off-Lattice (Bandadas)

> Leer y respetar siempre los lineamientos de `../AGENTS.md` (raíz del repo). El enunciado
> completo está en `docs/Enunciado.md` y tiene máxima prioridad.

---

## 1. De qué se trata

TP2 de Simulación de Sistemas (ITBA): **bandadas de agentes autopropulsados** (modelo de
Vicsek [1]) como autómata celular off-lattice, más una variante: el **modelo de votante** [2].

- Caja cuadrada de lado **L = 10** con **condiciones periódicas de contorno** (siempre).
- Partículas **puntuales** con rapidez constante `v` (default 0.03) y radio de interacción
  `r_c` (default 1, distancia **entre centros**).
- Densidades a estudiar: **ρ = N/L² = 2, 4, 8** (N = 200, 400, 800) más las bajas
  **ρ = 1/(3π), 1/(2π), 1/π** (N = round(ρ·L²) = 11, 16, 32; ~0.33, 0.5 y 1 vecino promedio
  dentro de r_c, debajo de la percolación).
- Input principal: el **ruido η** (Δθ ~ U[-η/2, η/2]).
- Observables: **polarización** `v_a = |Σv_i|/(N·v)` y **fracción del cluster más grande** `S`
  (clusters = componentes conexas del grafo de vecindad con `r_c`).
- Entrega: **04/09/2026 13hs** (presentación pdf + código zip + informe).

### Reglas de actualización (sincrónicas, siempre desde el estado en t)

- **Vicsek estándar**: θ nuevo = dirección promedio de los vecinos **incluyéndose a sí misma**
  (vía `atan2(⟨sin⟩, ⟨cos⟩)`) + ruido.
- **Votante**: copia la dirección de **una partícula elegida al azar entre sí misma y sus
  vecinos** + ruido. *Decisión del grupo*: el PDF no prohíbe la auto-copia; aclararlo en
  presentación e informe.
- **Sin vecinos** (ambos modelos): conserva su propia dirección + ruido (en el votante surge
  naturalmente al copiarse a sí misma).
- Posición: `x(t+Δt) = x(t) + v·cos(θ(t+Δt))·Δt` mod L ("forward update").

## 2. Arquitectura

Módulo Maven `vicsek-java/` que depende de la librería compartida **`common/`** de la raíz
(paquetes `ar.edu.itba.sds.common.*`: CIM, `Particle`, `NeighborLists`, IO estático/dinámico,
`CliArgs`). La búsqueda de vecinos por paso usa el **CIM del TP1** con radio de partícula 0
(criterio borde a borde ≡ entre centros) y PBC; cada llamada se cronometra para el punto g.

```
vicsek-java/src/main/java/ar/edu/itba/sds/tp2/
├── Main.java             # CLI: parsea args, orquesta, escribe outputs
├── SimulationConfig.java # record con todos los parámetros de la corrida
├── UpdateModel.java      # enum VICSEK | VOTER
├── FlockSimulation.java  # motor: init aleatorio, paso sincrónico, observables
├── Clusters.java         # union-find sobre NeighborLists → fracción del cluster gigante
└── io/RunWriter.java     # observables.csv + run.json (inputs y tiempos del CIM)
```

Outputs por corrida (en `output/<auto>/` o `--out`):

- `static.txt` / `dynamic.txt`: formato de cátedra (ver `../AGENTS.md` §2.2); un bloque cada
  `--every` pasos, incluyendo t=0 y el final.
- `observables.csv`: `time,polarization,largest_cluster_fraction`, **una fila por paso** (el
  criterio de estacionario y los promedios se deciden en post-proceso).
- `run.json`: todos los inputs + tiempos de cada llamada al CIM (punto g: comparar con TP1).

Compilar desde la raíz del repo: `mvn package` → `vicsek-java/target/vicsek.jar`.

## 3. Estado y pendientes

- [x] Motor de simulación (Vicsek + votante) con CIM de `common`, validado: η bajo → v_a≈1,
      η alto → v_a≈0, S<1 con densidades bajas.
- [x] Barridos completos en `output/` (2 modelos × 6 ρ × 15 η × 50 seeds) + corridas de
      animación (`output/anim/`, bloques cada 5 pasos) vía `scripts/run_sweeps.sh`.
      Las densidades bajas corren 5000 pasos (se ordenan más lento); el resto 2000.
- [x] Post-proceso Python (`analysis/`): `aggregate.py` reduce el barrido a `out/summary.csv`
      (promedio estacionario t ≥ 1000 por seed; media ± desvío muestral sobre 50 seeds);
      `plot_evolution.py` y `plot_curves.py` generan las figuras en `analysis/figures/`.
      Hallazgo: con ρ ≥ 2 y r_c = 1 el sistema percola y S ≈ 1 siempre (única variación:
      mínimo S ≈ 0.96 en ρ = 2 cerca de la transición); las figuras de S van con eje acotado.
- [x] Animaciones (`anims/`): paquete Python TP-agnóstico (VisPy + ffmpeg) que rinde una corrida
      a MP4 sin re-simular, con vectores coloreados por ángulo y HUD con t, η, v_a y S. Se usa
      sobre `output/anim/`; ver `anims/README.md`.
- [ ] Punto g: comparar tiempos del CIM con los del TP1 (mismos N).
- [ ] Presentación + informe.

## Referencias

- [1] Vicsek et al., PRL 75, 1226 (1995).
- [2] Loscar, Baglietto & Vazquez, PRE 104, 034111 (2021).
