# TP5 — Dinámica peatonal: evacuación con el CPM

Problema 2 del enunciado (`docs/Enunciado.md`): evacuación de N = 500 agentes de una habitación de
50 m × 50 m por una puerta de 0.8 m, con el Contractile Particle Model (Baglietto & Parisi, 2011).
Por ahora está implementado el esquema regido por el paso temporal (TSDMD), con dos agregados
propios declarados en `AGENTS.md` (sección 3): segundo target `(x_i, −1 m)` y pared rígida sobre
el cuerpo de radio `r_min`.

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

java -jar cpm-java/target/cpm.jar tsdmd --help   # todas las opciones
```

Cada corrida escribe `static.txt`, `dynamic.txt`, `events.csv` y `run.json` (formato en
`AGENTS.md`, sección 5).

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

# PNG de un instante
python3 analysis/animate_evacuation.py output/tsdmd/N500_seed1 --snapshot 60
```
