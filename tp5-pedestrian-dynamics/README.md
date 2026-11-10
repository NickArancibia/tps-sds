# TP5 — Dinámica peatonal: evacuación con el CPM

Problema 2 del enunciado (`docs/Enunciado.md`): evacuación de N = 500 agentes de una habitación de
50 m × 50 m por una puerta de 0.8 m, con el Contractile Particle Model (Baglietto & Parisi, 2011).
Implementados los tres esquemas del enunciado: regido por el paso temporal (TSDMD), regido por
eventos (EDMD puro) e híbrido, con dos agregados propios declarados en `AGENTS.md` (sección 3):
segundo target `(x_i, −1 m)` y cuerpo impenetrable de radio `r_min` contra paredes y contra otros
agentes.

## Compilar

Desde la raíz del repo:

```bash
mvn -q -pl tp5-pedestrian-dynamics/cpm-java -am package -DskipTests
```

## Simular

Desde `tp5-pedestrian-dynamics/`:

```bash
# Evacuación completa, un estado cada 3 pasos (0.1 s)
java -jar cpm-java/target/cpm.jar tsdmd --N 500 --seed 1 --out output/tsdmd/N500_seed1

# Misma corrida (misma seed), guardando todos los pasos entre 3 s y 9 s
java -jar cpm-java/target/cpm.jar tsdmd --N 500 --seed 1 --save-every 1 --save-t0 3 --save-t1 9 \
    --out output/tsdmd/N500_seed1_t3-9

# Condición inicial desde archivo (una fila "x y" por agente): escenario de dos agentes
java -jar cpm-java/target/cpm.jar tsdmd --init scenarios/dos_agentes.txt --save-every 1 \
    --out output/tsdmd/dos_agentes

# EDMD puro: recuperación con los 8 radios intermedios de TSDMD (default) o con menos (--levels).
# En EDMD --save-every cuenta eventos (sin los cruces de celda): un estado cada 5 eventos
java -jar cpm-java/target/cpm.jar edmd --N 100 --seed 1 --save-every 5 --out output/edmd/N100_seed1_hold8
java -jar cpm-java/target/cpm.jar edmd --N 100 --seed 1 --levels 1 --save-every 5 \
    --out output/edmd/N100_seed1_hold1

# Híbrido: área de radio rh (m) alrededor de cada agente. rh < 2 rmin (0.2 m): EDMD puro; rh >= 0.6 m:
# todos los choques por paso temporal; rh mayor que la habitación: TSDMD puro. --levels vale para los
# choques que se resuelven por eventos. --save-every cuenta eventos (EDMD sin cruces de celda, y pasos
# con agentes en TSDMD); además de los archivos de siempre escribe schemes.csv (agentes en cada
# esquema en cada paso)
java -jar cpm-java/target/cpm.jar hybrid --N 100 --seed 1 --rh 1 --save-every 1 \
    --out output/hybrid/N100_seed1_rh1

java -jar cpm-java/target/cpm.jar tsdmd --help   # todas las opciones
```

Cada corrida escribe `static.txt`, `dynamic.txt`, `events.csv` y `run.json` (y `schemes.csv` en el
híbrido; formato en `AGENTS.md`, sección 5).

## Campaña de mediciones y figuras

```bash
# Los tres esquemas (N = 500 y 200), barrido de R_h del híbrido (L = 50, 150 y 300 m), de los radios
# intermedios de EDMD y escalamiento con N de 100 a 1000 (a L = 50 m y a densidad constante); 10 seeds
# por configuración, sin guardar estados. Corre en serie (mide el tiempo de ejecución): no correr nada
# pesado en paralelo. Retoma donde quedó; --fresh re-mide
python3 scripts/run_campaign.py                       # → output/campaign/N<N>_L<L>/<config>/seed<k>/
python3 scripts/run_campaign.py --studies base,levels # solo algunos (base, n200, levels, room, scaling)

# Figuras (analysis/figures/campaign/) y, por stdout, la tabla de cada una
python3 analysis/plot_campaign.py
```

## Animar

```bash
# Habitación completa (puntos) + zoom en la puerta (cuerpo r_min y espacio personal r), 0.5 s por cuadro
python3 analysis/animate_evacuation.py output/tsdmd/N500_seed1 --stride 5 --fps 30 --panel-zoom 25 3.5 4.5 \
    --out output/tsdmd/N500_seed1/evacuacion_general.mp4

# Zoom en la puerta, un cuadro por paso (1/3 de la velocidad real), con velocidades y dirección deseada
python3 analysis/animate_evacuation.py output/tsdmd/N500_seed1_t3-9 --zoom 25 1.5 2.0 --arrows --desired \
    --fps 10 --out output/tsdmd/N500_seed1_t3-9/choques_lento.mp4

# Dos agentes: 1/6 de la velocidad real, con trayectorias y r, |v| y distancia de cada agente
python3 analysis/animate_evacuation.py output/tsdmd/dos_agentes --t0 1.8 --zoom 25 0 1.2 --arrows --desired \
    --trails --info --fps 5 --out output/tsdmd/dos_agentes/choque_dos_agentes.mp4

# Híbrido: coloreado solo por esquema (azul EDMD, rojo TSDMD)
python3 analysis/animate_evacuation.py output/hybrid/N100_seed1_rh1 --panel-zoom 25 1.2 2 \
    --out output/hybrid/N100_seed1_rh1/evacuacion.mp4

# PNG de un instante
python3 analysis/animate_evacuation.py output/tsdmd/N500_seed1 --snapshot 60
```
