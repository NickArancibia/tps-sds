# Diseño — `anims/`: animaciones GPU de corridas de simulación

**Fecha:** 2026-08-21
**Ubicación del proyecto:** `tp2-cellular-automata/anims/`

## 1. Problema

El motor del TP2 corre offline y persiste todo (`static.txt`, `dynamic.txt`,
`observables.csv`, `run.json`). Falta la pieza de post-proceso que convierta una corrida en una
animación MP4 para la presentación, sin re-simular y sin tiempos de render largos.

El proyecto tiene que servir también para los TPs siguientes: el formato estático/dinámico es el
mismo de cátedra en todos, así que lo único que cambia entre TPs es *qué se dibuja*.

## 2. Decisión de tecnología: VisPy

**Elegido: VisPy** (scene graph sobre OpenGL) + `imageio-ffmpeg` para el encode.

Presupuesto de tiempo estimado para el caso más grande del enunciado (N=800, 2000 frames, 720p):

| Etapa | Ejecutor | Tiempo |
|---|---|---|
| Parseo de `dynamic.txt` | numpy (C) | ~1 s |
| Update por frame | numpy sobre arrays de 800 | ~0,2 s total |
| Draw call + readback | GPU / driver | ~3 s |
| Encode H.264 | ffmpeg (C) | ~15 s |

Total ~20 s, de los cuales el intérprete de Python aporta menos de 1 s. El diseño no tiene ningún
bucle por partícula en Python: todo son operaciones vectorizadas sobre arrays.

Alternativas descartadas y por qué:

- **matplotlib + pipe a ffmpeg**: CPU puro, ~2–4 min para el mismo caso. Anda hoy, no escala a los
  TPs siguientes si crecen N o los pasos.
- **pygfx (WGPU)**: rendimiento comparable, pero API menos estable y menos difundida.
- **Java2D escribiendo PNGs durante la simulación**: cero parseo y cero lenguaje nuevo, pero acopla
  el render a la simulación — cambiar un color obliga a re-simular. Rompe la separación
  motor/post-proceso que el repo ya estableció.
- **Java + LWJGL**: mismo rendimiento (mismo hardware, mismo trabajo), a cambio de shaders, VAOs y
  contexto a mano más bindings de ffmpeg vía JavaCV. Varios cientos de líneas para llegar donde
  VisPy llega en ~80, y sin visor interactivo.

El cuello de botella es la GPU y el encoder, que son código nativo en todas las opciones. Cambiar
de lenguaje mueve la parte que no cuesta.

`imageio-ffmpeg` trae el binario de ffmpeg en el wheel: en Windows evita depender de que ffmpeg
esté instalado y en el PATH.

## 3. Estructura

```
tp2-cellular-automata/anims/
├── requirements.txt        # vispy, imageio-ffmpeg, numpy, PyQt5
├── README.md
└── anims/
    ├── __init__.py
    ├── run.py       # loader del formato de cátedra → Run
    ├── canvas.py    # SceneCanvas offscreen/interactivo, caja PBC, HUD
    ├── scene.py     # Protocol Scene (punto de extensión)
    ├── scenes/
    │   ├── __init__.py
    │   └── flock.py # escena del TP2
    ├── writer.py    # frames uint8 → ffmpeg → mp4
    └── cli.py       # `python -m anims`
```

**Frontera clave:** `run.py`, `canvas.py` y `writer.py` no saben nada de Vicsek. Hablan del formato
`static.txt`/`dynamic.txt`, común a todos los TPs. Lo específico del TP2 vive solo en
`scenes/flock.py`. Una animación para el TP3 es un archivo nuevo en `scenes/`.

## 4. Componentes

### `run.py`

Qué hace: carga un directorio de corrida a memoria.
Cómo se usa: `run = load_run(path)`.
De qué depende: numpy.

```python
@dataclass
class Run:
    path: Path
    n: int
    l: float
    times: np.ndarray        # (T,)
    state: np.ndarray        # (T, N, 4) float32 — x, y, vx, vy
    meta: dict               # run.json, {} si no existe
    observables: dict[str, np.ndarray] | None   # columnas de observables.csv
```

Parseo: el bloque del archivo dinámico tiene tamaño fijo `1 + 4N` tokens, así que se lee el archivo
entero y se convierte con un split vectorizado en una sola pasada
(`np.array(text.split(), dtype=np.float32)`), luego `reshape`. Sin bucle por línea. No se usa
`np.fromstring`, deprecado para texto.

Para el caso grande el array ocupa ~25 MB. Se cachea a `<run>/state.npz` (estado más vector de
tiempos), invalidado por mtime de `dynamic.txt`, así la segunda pasada arranca instantánea.

Degradación: si falta `observables.csv`, `observables` queda en `None` (corridas de otros TPs que no
lo escriben). Si falta `run.json`, `meta` queda vacío.

### `scene.py`

El punto de extensión. Un `Protocol` de dos métodos:

```python
class Scene(Protocol):
    def build(self, view: ViewBox, run: Run) -> None: ...
    def update(self, i: int) -> list[str]: ...
```

`build` crea los visuals una sola vez; `update` solo reescribe buffers existentes — nunca recrea
visuals, que es lo que mataría el rendimiento — y devuelve las líneas de texto del HUD para ese
frame.

### `canvas.py`

Arma el `SceneCanvas` (offscreen con `show=False`, o visible en modo preview), el `ViewBox` con
cámara `PanZoom` fijada al dominio `[0, L]²`, el borde de la caja PBC y el visual de texto del HUD.
Expone `render() -> np.ndarray` (uint8, H×W×3).

El HUD lo dibuja el canvas a partir de las líneas que devuelve `scene.update`, así el formato del
HUD no se duplica en cada escena futura.

Si no hay contexto OpenGL disponible, falla con un mensaje que dice qué instalar, en vez de un
traceback de GL.

### `scenes/flock.py`

Escena del TP2. Cada partícula es un segmento con la punta en la dirección de movimiento, dibujado
con un único `Line` visual con `connect='segments'` (2 vértices por partícula) — una sola llamada de
dibujo para todas las partículas.

Color por ángulo con un mapa cíclico HSV: cuando la bandada se ordena, el campo vira a un color
uniforme, y eso se lee de un vistazo.

Los segmentos que cruzan el borde no se dibujan hacia la imagen periódica: cada partícula se dibuja
en su posición dentro del dominio (el largo de la flecha es de escala de `rc`, no del dominio, así
que el artefacto en el borde es despreciable).

HUD: `t`, `η` (de `run.json`), `v_a` y `S` (de `observables.csv`, indexados por el paso
correspondiente al frame, respetando `outputEvery`). Si no hay observables, solo `t`.

### `writer.py`

Envuelve `imageio_ffmpeg.write_frames`: abre el pipe con tamaño y fps, recibe frames uint8 y cierra.
Codec H.264, `yuv420p` para que reproduzca en cualquier lado (incluido PowerPoint).

### `cli.py`

```
python -m anims <run_dir> [opciones]

  --out <path>     Archivo de salida            (default: <run_dir>/anim.mp4)
  --fps <int>      Cuadros por segundo          (default 30)
  --every <int>    Usar 1 de cada N frames      (default 1)
  --size <WxH>     Resolución                   (default 1280x720)
  --scene <name>   Escena a usar                (default flock)
  --no-hud         Video limpio, sin overlay
  --preview        Abre ventana interactiva en vez de renderizar
```

## 5. Flujo

1. `cli` carga el `Run`.
2. Construye el canvas (offscreen o visible) y la escena; `scene.build(view, run)`.
3. Por cada frame: `scene.update(i)` → `canvas.render()` → `writer.append(frame)`.
4. Cierra el pipe.

En `--preview`, el paso 3 lo maneja un timer de VisPy sobre el mismo canvas y la misma escena; no
hay una segunda ruta de código de dibujo.

Nada de re-simular ni recalcular vecindades en Python, igual que la regla ya vigente en
`tp1-cell-index-method/analysis/`.

## 6. Tests

Sin GPU (corren en cualquier lado):

- `run.py`: parser contra un run chico escrito a mano en un tmpdir — verifica shape, tiempos,
  valores, y las dos degradaciones (sin `observables.csv`, sin `run.json`). Round-trip del caché e
  invalidación por mtime.
- `writer.py`: frames sintéticos → mp4 → releer y verificar cantidad de frames y resolución.

Con GPU: el render se valida a ojo sobre una corrida real. No se testea el contenido de los píxeles.

## 7. Fuera de alcance

- Gráficos de observables (`v_a(η)`, `S(η)`, etc.): son del post-proceso de análisis, no de este
  proyecto.
- GIF: si hace falta, sale de convertir el mp4.
- Mover esto a una librería compartida en la raíz del repo. El paquete se diseña TP-agnóstico, así
  que el día que lo necesite el TP3 se mueve sin reescribirlo.
