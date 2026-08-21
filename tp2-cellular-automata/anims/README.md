# `anims/` — Animaciones GPU de corridas de simulación

Post-proceso que convierte una corrida ya simulada (`static.txt`, `dynamic.txt`,
`observables.csv`, `run.json`) en un MP4, **sin re-simular**. El render lo hace la GPU vía
[VisPy](https://vispy.org) y el encode ffmpeg (binario que viene en el wheel de `imageio-ffmpeg`,
así que en Windows no hace falta tener ffmpeg en el PATH).

El paquete es **agnóstico del TP**: `run.py`, `canvas.py` y `writer.py` solo conocen el formato de
cátedra, común a todos los TPs. Lo específico del TP2 vive en `anims/scenes/flock.py`; una
animación para el TP3 es un archivo nuevo en `anims/scenes/`.

## Instalación

```bash
cd tp2-cellular-automata/anims
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # Linux/Mac: .venv/bin/python
```

## Uso

```bash
python -m anims output/demo
```

| Flag | Descripción | Default |
|---|---|---|
| `--out` | archivo de salida | `<run_dir>/anim.mp4` |
| `--fps` | cuadros por segundo | 30 |
| `--every` | usar 1 de cada N frames guardados | 1 |
| `--size` | resolución `WxH` | `1280x720` |
| `--scene` | escena a usar | `flock` |
| `--no-hud` | video limpio, sin overlay | — |
| `--no-cache` | ignora y no escribe el caché `state.npz` | — |
| `--preview` | abre una ventana interactiva en vez de renderizar | — |

Ejemplo típico para la presentación (una corrida larga, acelerada):

```bash
python -m anims output/eta0.5_rho4 --every 4 --fps 30 --out ../docs/vicsek_eta05.mp4
```

## Qué se ve

Cada partícula es un segmento con la punta en su dirección de movimiento, coloreado con un mapa
cíclico en el ángulo: cuando la bandada se ordena el campo vira a un color uniforme, y el orden se
lee de un vistazo. El HUD muestra `t`, `η`, `N`/`ρ`, y `v_a` y `S` leídos de `observables.csv`
(indexados por tiempo, así que respeta el `--every` con el que se guardó la corrida). Si la corrida
no tiene `observables.csv` o `run.json`, esas líneas simplemente no aparecen.

## Rendimiento

Todo es vectorizado con numpy: no hay ningún bucle por partícula en Python. El parseo de
`dynamic.txt` se cachea en `<run_dir>/state.npz` (invalidado por el mtime del archivo), así que la
segunda pasada sobre la misma corrida arranca instantánea. Para N=400 y 200 frames a 1280×720 el
render completo tarda ~4 s.

## Tests

Los tests del parser y del encoder no necesitan GPU:

```bash
.venv/Scripts/python -m pytest tests -q
```

El render en sí se valida a ojo sobre una corrida real (no se testea el contenido de los píxeles).
