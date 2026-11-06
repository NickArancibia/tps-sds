# AGENTS.md — SdS TP5: Dinámica Peatonal (Evacuación con esquema híbrido EDMD + TSDMD)

> Leer y respetar siempre los lineamientos de `../AGENTS.md` (raíz del repo). El enunciado
> completo está en `docs/Enunciado.md` (PDF original en `docs/enunciado/`) y tiene máxima
> prioridad. Modelo: paper del CPM en `docs/papers/Biblio_6_7/CPM.pdf`; resto de la bibliografía
> de la cátedra en `docs/papers/` (resumen en la sección 8).

---

## 1. De qué se trata

TP5 de Simulación de Sistemas (ITBA). El grupo eligió el **Problema 2**: evacuación de una
habitación resuelta con tres esquemas, **TSDMD puro, EDMD puro e híbrido** (EDMD en la zona
diluida, TSDMD en el bottleneck de la puerta), con el **CPM** como modelo peatonal.

- Habitación cuadrada de lado **L = 50 m**, una puerta de ancho **d = 0.8 m** en el centro de una
  pared. **N = 500** agentes al azar en toda la habitación, sin superponerse entre sí ni con las
  paredes.
- Target: la puerta; al alcanzarla, segundo target afuera. El agente se retira al alejarse
  **1 m** de la puerta.
- CPM: **r_min = 0.10 m**, **r_max = 0.25 m**, **v_d = 1.5 m/s**; el resto del paper (sección 2).
- Paredes rígidas que interactúan con los agentes que las tocan.
- **Entrega: 13/11/2026 13 hs** por campus: `SdS_TP5_2026Q2GXXCSS_Presentación` (pdf) y
  `SdS_TP5_2026Q2GXXCSS_Codigo` (zip de pocos kB, solo la versión final del motor). Presentación
  oral de **13 min**; la descripción matemático-computacional del esquema híbrido lleva más
  tiempo que una introducción habitual.

### Puntos del enunciado (Problema 2)

| Punto | Qué pide | Parámetros |
| :--- | :--- | :--- |
| Diseño | Describir matemáticamente: criterios de pasaje EDMD ↔ TSDMD; convivencia (sincronización eventos/`dt`, eventos EDMD–TSDMD, sin contactos perdidos ni superposiciones al pasar de esquema); colisión agente–agente y agente–pared en EDMD puro e híbrido y mecanismo de recuperación de la velocidad deseada | — |
| a | Implementar los tres esquemas; animación característica de cada uno (híbrido coloreado por esquema); fracción de partículas en cada esquema vs t | N = 500, L = 50 m |
| b | Curvas de población N_in(t) y tiempo de evacuación (sale el último agente), ≥ 10 realizaciones, promedio ± error; discutir contra TSDMD puro como referencia | ídem |
| c | Wall-clock de la simulación completa de los tres esquemas (misma PC, barra de error); híbrido: wall-clock y tiempo de evacuación vs parámetro principal del criterio de pasaje, con TSDMD y EDMD puros como referencia | ídem |
| d | Escalamiento del wall-clock con N ∈ [100, 1000] para los tres esquemas: (a) densidad inicial constante (L crece), (b) L constante (densidad crece). Escalamiento → log-log (§8.3 raíz) | — |

## 2. Modelo: CPM (Baglietto & Parisi, PRE 83, 056117, 2011)

Parámetros: `r_min = 0.10 m`, `r_max = 0.25 m` y `v_dmax = 1.5 m/s` (enunciado); `β = 0.9`,
`τ = 0.5 s`, `v_e = v_dmax` (paper, Ec. 9).

- Paso temporal, **regla del modelo** (el enunciado prohíbe cambiarlo arbitrariamente):
  `Δt = r_min / (2 max(v_dmax, v_e)) = 0.10 / 3 ≈ 0.0333 s`.
- Rapidez deseada: `v_d(r) = v_dmax ((r − r_min)/(r_max − r_min))^β`, con `v_d(r_min) = 0`.
- Velocidad deseada: `v_d = v_d(r) e_target`.
- Contacto: entre agentes si `|x_i − x_j| < r_i + r_j`; con pared si la distancia al punto más
  cercano de la pared es `< r_i` (en ese caso `x_j` es ese punto).
- Escape: `v_e = v_e Σ_j e_ij / |Σ_j e_ij|`, con `e_ij = (x_i − x_j)/|x_i − x_j|` sobre todos los
  contactos j (agentes y paredes).
- Radio: con contacto, `r_i → r_min` instantáneamente; sin contacto, `Δr = r_max Δt / τ` por paso,
  hasta `r_max`.
- Algoritmo de un paso, en cuatro iteraciones separadas sobre todas las partículas (actualización
  sincrónica):
  1. Detectar contactos y calcular `v_e`.
  2. Ajustar radios.
  3. Calcular la dirección de `v_d` (posición actual y target) y su módulo con `v_d(r)`.
  4. `v = v_d` si `r > r_min`, `v = v_e` si `r = r_min`; luego `x(t) = x(t − Δt) + v Δt`.
- Targets en la salida del paper (Sec. III B; puerta en `y = 0` entre `x_e1` y `x_e2`, ancho
  `L_d`): si `x_i` cae fuera de `[x_e1 + 0.2 L_d, x_e1 + 0.8 L_d]`, el target es un punto al azar
  de ese intervalo; si cae dentro, el target está justo enfrente (`x_target = x_i`). Al alcanzar
  la puerta se coloca un nuevo target afuera.
- Condición inicial del paper: radios en `r_min` (velocidad deseada inicial nula).
- Interpretación del radio (paper, Sec. II): es un radio efectivo, no el cuerpo. `r_min` es el
  radio equivalente que fija la densidad máxima (el cuerpo apretado en la multitud); un radio cerca
  de `r_max` funciona como sensor del espacio personal (la distancia mínima a la que el movimiento
  empieza a verse afectado; `r_max` ≈ medio paso completo). "Contacto" en el CPM es que se toquen
  los espacios personales vigentes, no los cuerpos: dos agentes libres chocan a `0.50 m` entre
  centros, con los cuerpos a `0.30 m` de distancia. La superposición de cuerpos (centros a menos de
  `2 r_min`) sí es un artefacto del modelo.

## 3. Decisiones

### Tomadas (conversación 2026-11-05)

- Problema 2 con CPM.
- Orden: **primero TSDMD puro**. Es el CPM tal cual lo define el paper, la referencia del punto
  (b), y sirve para mirar la dinámica real (animaciones y diagnósticos) antes de diseñar EDMD e
  híbrido.
- La recuperación de la velocidad deseada después de un choque no es un problema en TSDMD (es la
  regla de crecimiento del radio). Aparece solo en EDMD, porque entre eventos la velocidad debe ser
  constante y durante la recuperación no lo es.
- El motor separa las reglas del CPM (rapidez en función del radio, crecimiento del radio, regla
  de contacto y escape, targets) del esquema que avanza el tiempo, para que los tres esquemas
  compartan el mismo núcleo.
- Búsqueda de vecinos con el Cell Index Method (mismo criterio que el TP1, celdas de lado
  `>= 2 r_max`) en todos los esquemas: si no, el punto (d) mide la búsqueda de vecinos y no el
  esquema. Está reimplementado sobre arreglos en `cpm/Contacts.java` porque el `Particle` de
  `common/` tiene radio fijo.
- Datos del paper para todo lo que el enunciado no fija: `β = 0.9`, `τ = 0.5 s`, `v_e = v_dmax`,
  `Δt` de la Ec. (2), target en la puerta con la regla del paper (franja central del 60 %; el punto
  al azar se sortea una vez por agente) y radios iniciales en `r_min`.
- Segundo target en `(x_i, −1 m)`: al cruzar la línea de la puerta cada agente sale derecho, como
  en CPM_AA (Sec. 4.3). Reemplazó a un target común en `(L/2, −1 m)`, que hacía converger y chocar
  a los agentes después de la puerta (sección 7). El target se elige por posición: con `y > 0`
  vale la regla de la puerta, también para un agente que el atasco empujó de vuelta adentro. El
  agente pasa a la fase "cruzó la puerta" cuando su centro cruza `y = 0` y se retira cuando
  `|x − (L/2, 0)| >= 1 m` con `y < 0`.
- Condición inicial: posiciones uniformes sin superposición evaluada con `r_max` (entre agentes y
  con paredes), así tampoco se superponen al crecer el radio.
- **Cuerpo impenetrable contra paredes y agentes (agregado propio; no está en el paper)**. Pedido
  de la cátedra: los cuerpos (disco de `r_min`) nunca se superponen. Se aplica después de calcular
  la velocidad con las reglas del CPM y antes de mover (`cpm/BodyConstraints`). Cada vecino que el
  agente puede alcanzar en el paso impone `v·n ≥ c`, con `n` el versor del vecino al agente:
  - pared a distancia `d` de su punto más cercano: `c = −max(0, d − r_min)/Δt` (consume todo el
    hueco; la pared no se mueve);
  - agente `j` a distancia `d_ij`: `c = −max(0, d_ij − 2 r_min)/(2Δt)` (cada uno consume a lo sumo
    la mitad del hueco, así la distancia final es `≥ 2 r_min` haga lo que haga el otro; cada
    agente se corrige solo con las posiciones del comienzo del paso, sin depender del orden ni
    iterar).
  La velocidad corregida es la más cercana a la del CPM que cumple todas las restricciones
  (proyección sobre la intersección de semiplanos, que contiene a `v = 0`): en 2D se prueban la
  velocidad original, su proyección sobre cada recta violada y la intersección de cada par de
  rectas, y se elige el candidato factible más cercano. Con una sola restricción equivale a
  recortar la componente normal (la regla de pared rígida anterior, 2026-11-05, que solo miraba
  paredes y quedó reemplazada). Motivo: el escape suma un versor por contacto; si los contactos de
  un lado dominan, empuja al agente contra una pared o contra otro agente (sección 6). Declararlo
  como agregado propio en la presentación; CPM_AA dice que en el CPM las superposiciones entre
  partículas se deshacen al paso siguiente y no las impide.

### Tomadas (conversación 2026-11-06): EDMD puro

- Escape de duración `Δt` desde el contacto (evento "fin de escape"), con `r = r_min` y velocidad
  constante. Un contacto en medio del escape o de la recuperación es un colapso nuevo: el escape
  reinicia desde ese instante y los eventos pendientes del agente se descartan (contador de cambios
  por agente). Cada escape dura `Δt > 0`, así que no hay cadenas de colapsos en tiempo cero.
- Colapso: todos los agentes en contacto en ese instante (cierre transitivo, tolerancia 10⁻⁹ m)
  pasan a `r_min` y escapan con `v_e Σe/|Σe|` sumando sus contactos vigentes (Ec. 6), con los radios
  de antes del colapso. Si dos cuerpos quedan tocándose (solo pasa si ya estaban en `r_min`), la
  velocidad se proyecta con `v·n ≥ 0` para que no se acerquen. Los cuerpos y los espacios
  personales nunca se superponen: el contacto salta cuando se tocan.
- Recuperación en tramos de radio y rapidez constantes (propuesta del grupo); parámetro `levels` =
  radios intermedios que se recorren (máximo 8 = `K − 1`, con `K = 9` pasos de `Δr` hasta `r_max`;
  la recuperación dura `8Δt` y el agente queda libre `9Δt` después del contacto): los primeros
  `levels` radios de TSDMD desde `r_min + Δr`, un `Δt` cada uno con rapidez `v_d(r_k)`, y el último
  sostenido hasta el final; con 0 el agente queda quieto en `r_min` toda la recuperación; con 8 es
  TSDMD. No hace falta que los tramos estén equiespaciados (decisión del grupo, 2026-11-06). El
  tiempo de recuperación no es `τ`: es `8Δt = 0.27 s`. Se probó y descartó una variante propia
  (`mean`: tramos iguales que recorren la misma distancia que TSDMD, sección 6.2).
- Al empezar un tramo el radio salta; si pisa a un vecino o una pared, el colapso es en ese mismo
  instante (deficiencia del esquema a declarar: con menos niveles los saltos son más grandes).
- Otros eventos: contacto con pared, cruce del borde de la franja y de `y = 0` (cambio de target;
  el de la puerta registra el evento), retiro, y cruce de celda del CIM (misma grilla que TSDMD:
  dos agentes solo pueden tocarse desde celdas contiguas).
- Estados guardados en eventos, como en el TP3: uno cada `save-every` eventos que cambian el
  estado (los cruces de celda no cuentan; default 1000, `--save-every 1` = todos), con todas las
  posiciones en el instante de ese evento (sin modificar el estado del motor). La animación avanza
  un número fijo de eventos por cuadro (`--stride`): no es en tiempo real. Una primera versión
  guardaba el primer evento después de cada `Δt`, lo que equivale a muestrear en tiempo y daba
  una reproducción casi en tiempo real; se descartó.

### Abiertas

- Híbrido: criterio de pasaje y su parámetro principal (candidato: distancia a la puerta);
  TSDMD → EDMD solo con la partícula libre (`r = r_max`, sin contactos); resolución de un contacto
  EDMD–TSDMD. Dentro de un paso del CPM, `v` y `r` son constantes; tomar ese tramo como MRU
  permite predecir contactos EDMD–TSDMD con la cuadrática del TP3 (decisión a declarar).

## 4. Diagnósticos previstos sobre TSDMD (para diseñar EDMD e híbrido)

No son observables de entrega; guían las decisiones abiertas. La simulación guarda radio y estado
de contacto de cada agente para poder calcularlos en el post-proceso.

- Choques por unidad de tiempo en función de la distancia a la puerta.
- Distancia a la puerta de los agentes con `r < r_max` (tamaño del bottleneck).
- Duración real de la recuperación y fracción de agentes que vuelven a chocar antes de terminarla.
- Fracción de agentes libres vs t.

## 5. Implementación

Motor en `cpm-java/` (módulo Maven `cpm`, paquete `ar.edu.itba.sds.tp5`):

| Clase | Rol |
| :--- | :--- |
| `cpm/CpmParams` | Parámetros, `Δt` (Ec. 2), `Δr` (Ec. 8), `v_d(r)` (Ec. 1) |
| `cpm/Room` | Paredes como segmentos (la inferior partida por la puerta), franja de targets, criterio de retiro |
| `cpm/Agents` | Estado en arreglos paralelos, lista de activos, condición inicial |
| `cpm/Targets` | Regla de targets (paper + segundo target) |
| `cpm/Contacts` | Contactos agente–agente (CIM) y agente–pared; suma de versores de escape |
| `cpm/EventLog` | Instantes de cruce de puerta y de retiro |
| `tsdmd/TimeDrivenCpm` | Un paso del CPM en cuatro iteraciones sincrónicas |
| `cpm/BodyConstraints` | Cuerpo `r_min` impenetrable contra paredes y agentes en TSDMD (agregado propio) |
| `cpm/VelocityProjection` | Velocidad más cercana que cumple restricciones `v·n ≥ c` (TSDMD y colapsos de EDMD) |
| `cpm/CellGrid` | Grilla del CIM común a los dos esquemas |
| `edmd/EventDrivenCpm` | EDMD puro: eventos, predicción con la cuadrática, colapsos |
| `edmd/Recovery` | Tramos de recuperación (`levels` radios intermedios desde `r_min + Δr`) |
| `edmd/EventQueue` | Heap de eventos sobre arreglos primitivos, con invalidación por contadores |
| `io/Output` | `static.txt`, `dynamic.txt`, `events.csv` |
| `EvacuationRun`, `Main` | CLI (`tsdmd` y `edmd`) |

Outputs en `output/<esquema>/<corrida>/` (ignorado por git): `static.txt` (`N`, `L`, `r_min r_max`
por agente), `dynamic.txt` (por estado: `t` y N filas `x y vx vy r tx ty fase contacto`; fase 0 =
en la habitación, 1 = cruzó la puerta, 2 = retirado; en EDMD `contacto` = escapando), `events.csv`
(`t,id,event` con door/exit) y `run.json` (inputs, `Δt`, `Δr`, tiempo de evacuación, tiempo de
ejecución del lazo; TSDMD: pasos y en cuántos pasos-agente la restricción de cuerpo cambió la
velocidad, `bodyLimitedEscape` y `bodyLimitedDesired`; EDMD: `recovery`, `levels` y `events` con
los eventos procesados por tipo, descartados, colapsos y colapsos por salto de radio). Con la misma
seed la corrida es idéntica: para ver un intervalo paso a paso se re-corre con `--save-every 1
--save-t0 --save-t1` (verificado: posiciones idénticas a la corrida completa en los estados
comunes).

Condición inicial alternativa: `--init <archivo>` con una fila `x y` por agente (mismas validaciones
que la sorteada). Escenario de prueba: `scenarios/dos_agentes.txt`, dos agentes simétricos respecto
del eje de la puerta.

Post-proceso en `analysis/`: `cpm_common.py` (carga) y `animate_evacuation.py` (animación o PNG).
Colores: azul libre, negro recuperando, rojo en contacto. En la habitación completa cada agente es
un punto de tamaño fijo; en el zoom (`--zoom`, o panel derecho con `--panel-zoom`) se dibuja el
cuerpo (disco sólido de `r_min`) y el espacio personal (círculo de radio `r` vigente). Opciones del
zoom: `--arrows` velocidad, `--desired` dirección deseada de los agentes en contacto, `--trails`
trayectorias, `--info` r, rapidez y estado de cada agente (hasta 6 agentes).

Cómo leer un choque cuadro a cuadro: el estado guardado en el paso k tiene posiciones y radios
después del paso. Los espacios personales superpuestos se ven en el cuadro k − 1; en el cuadro k
los dos agentes ya están en rojo, con `r = r_min` y velocidad de escape.

## 6. Primera corrida de prueba (TSDMD, N = 500, seed 1, 2026-11-05)

Exploratoria, una sola realización: no son resultados de entrega. La tabla compara el segundo
target anterior, común en `(L/2, −1 m)`, con el actual `(x_i, −1 m)`, y este último con la regla
de pared rígida (configuración vigente); las viñetas sin aclaración son de la primera corrida.

| | Target común `(L/2, −1 m)` | Target `(x_i, −1 m)` | + pared rígida |
| :--- | ---: | ---: | ---: |
| Tiempo de evacuación (s) | 222.6 | 196.0 | 193.5 |
| Cruces de puerta entre 50 y 100 s (agentes/s) | 2.30 | 2.62 | 2.66 |
| Reingresos (cruzaron y volvieron a entrar) | 54 | 19 | 15 |
| Mínima distancia del centro a la pared inferior, lejos de la puerta (m) | 0.045 | 0.050 | 0.100 |

- Con pared rígida: superposición cuerpo–pared nula en todos los estados guardados (máximo
  2·10⁻⁶ m, la resolución de la salida). La regla actuó en 14111 pasos-agente sobre escapes y en
  11018 sobre velocidades deseadas, de unos 1.46·10⁶ pasos-agente (1.7 %). Las de velocidad
  deseada son recortes de a lo sumo `v_d(r_min + Δr) Δt` = 7 mm: el contacto se detecta con el
  radio del comienzo del paso y la velocidad usa el radio ya crecido, así que un agente que acaba
  de colapsar contra la pared puede acercarse hasta 7 mm de más.

- Lazo de 2.2 s, 1.6 s y 0.8 s (columnas de la tabla) con escritura cada 3 pasos; los tiempos
  de ejecución todavía no se midieron con cuidado (punto c).
- Flujo específico: 2.9 agentes/(m s) con el target común y 3.3 con el actual. Los dos superan el
  rango experimental citado en el paper (1.25–2) y lo que obtiene el paper con sus parámetros
  (`r_max` = 0.32 y 0.37 m). Acá `r_max` = 0.25 m lo fija el enunciado.
- El atasco es un semicírculo de unos 4 m de radio frente a la puerta (t = 60 s). En los estados
  muestreados cada 30 s entre 30 s y 150 s, más del 60 % de los agentes activos está en contacto.
- Superposiciones profundas en el atasco: hasta 167 pares con centros a menos de `2 r_min`, con
  distancia mínima entre centros de 0.10 m. El CPM no impide superposiciones: el escape suma
  versores y puede empujar a un agente hacia un contacto si los demás contactos dominan. Con la
  configuración vigente, guardando todos los pasos: superposición de cuerpos en el 90 % de los
  estados (de t ≈ 6 s a t ≈ 187 s), hasta 157 pares a la vez (t = 42 s), profundidad
  `2 r_min − d_ij` con mediana 1.4 cm, p99 6.1 cm y máximo 9.7 cm, todas a menos de 4.9 m de la
  puerta. Cada episodio dura 1 paso (máximo 5): el par se separa con el escape y vuelve a
  superponerse. La regla de pared rígida de entonces era solo contra paredes (ver sección 6.1).
- Lo mismo pasaba contra las paredes antes de la regla de pared rígida: un agente apretado contra
  la pared inferior podía tener escape hacia la pared (la pared es un solo contacto contra varios
  agentes). El mínimo fue `y = 0.045 m` (cuerpo 5.5 cm adentro con `r = 0.10 m`); ningún agente
  la llegó a cruzar.
- Reingresos: agentes que cruzaron la puerta y el atasco empujó de vuelta adentro. Siguen en fase
  1; `events.csv` registra solo el primer cruce.

### 6.1 Restricción de cuerpo contra agentes (2026-11-06)

Comparación entre la regla de pared rígida sola (anterior) y la restricción de cuerpo contra
paredes y agentes (vigente), 10 realizaciones (seeds 1–10) de cada una; tiempo de evacuación como
media ± desvío entre realizaciones:

| | Pared rígida sola | Cuerpo contra paredes y agentes |
| :--- | ---: | ---: |
| Tiempo de evacuación, N = 100 (s) | 49.9 ± 1.1 | 49.3 ± 1.6 |
| Tiempo de evacuación, N = 500 (s) | 194.6 ± 1.7 | 166.1 ± 1.4 |
| Seed 1, N = 500: cruces de puerta entre 50 y 100 s (agentes/s) | 2.66 | 3.32 |
| Seed 1, N = 500: agentes a < 4 m de la puerta en contacto (50–100 s) | 70 % | 54 % |
| Seed 1, N = 500: rapidez media de los agentes en contacto a < 4 m (m/s) | 1.49 | 0.71 |
| Seed 1, N = 500: pasos-agente con velocidad modificada | 1.7 % | 45 % |

- Superposición de cuerpos: verificada en doble precisión dentro del motor (seed 1, N = 100 y
  500, todos los pasos): mínimo de `|x_i − x_j| − 2 r_min` y de `d_pared − r_min` del orden de
  `−2·10⁻¹⁵ m` (redondeo). En `dynamic.txt` (5 decimales) aparecen pares a 0.199994 m: es el
  redondeo de la salida, no superposición.
- Sin la restricción, N = 100 ya muestra superposiciones: 27 % de los estados, hasta 5 pares a la
  vez, máximo 7.2 cm (t = 32.03 s, agentes 48 y 50).
- La restricción acelera la evacuación con N = 500 (−15 %) y sube el flujo específico a
  4.2 agentes/(m s), todavía más lejos del rango experimental (1.25–2). No se verificó el
  mecanismo: la componente media de la velocidad hacia la puerta de los agentes en contacto es
  negativa en las dos versiones (−0.09 y −0.12 m/s), así que no es que la restricción deje pasar
  solo los escapes hacia la puerta.
- Corridas y animaciones de N = 100 (seed 1, todos los pasos) en
  `output/tsdmd/restriccion_cuerpos/`.

### 6.2 EDMD puro: primeras corridas (2026-11-06)

Exploratorias: 3 realizaciones (seeds 1–3) por configuración, media ± desvío entre realizaciones;
tiempo de ejecución del lazo sin escritura de estados. TSDMD con la restricción de cuerpo vigente.

| Esquema | Evacuación N = 100 (s) | Lazo N = 100 (s) | Evacuación N = 500 (s) | Lazo N = 500 (s) |
| :--- | ---: | ---: | ---: | ---: |
| TSDMD | 47.8 ± 0.7 | 0.19 | 166 ± 2 | 0.96 |
| EDMD hold, 0 niveles | 346 ± 11 | 0.53 | 1650 y 1725 (seed 3 sin evacuar a 3000 s) | 7.8 |
| EDMD hold, 1 nivel | 76.9 ± 0.8 | 0.29 | 314 ± 3 | 10.8 |
| EDMD hold, 2 niveles | 64 ± 1 | 0.31 | 273 ± 5 | 10.9 |
| EDMD hold, 4 niveles | 59 ± 2 | 0.31 | 257 ± 2 | 10.4 |
| EDMD hold, 8 niveles (= TSDMD) | 60 ± 2 | 0.32 | 255 ± 3 | 10.5 |
| EDMD mean, 1 tramo (descartado) | 57 ± 2 | 0.24 | 246 ± 1 | 7.5 |
| EDMD mean, 2 tramos (descartado) | 56 ± 2 | 0.22 | 243 ± 4 | 8.0 |
| EDMD mean, 4 tramos (descartado) | 59.4 ± 0.4 | 0.25 | 248 ± 2 | 8.7 |

- Invariantes verificados en doble precisión después de cada evento (seed 1, N = 100; hold 8,
  hold 0 y mean 2): mínimo de `d_ij − (r_i + r_j)`, de `d_ij − 2 r_min` y de `d_pared − r` del
  orden de `−10⁻¹⁴ m`. La trayectoria no depende de cuántos estados se guardan (misma evacuación
  con `--save-every 1` y sin guardar).
- Con 8 niveles EDMD reproduce un choque aislado de TSDMD (escenario de dos agentes: primer
  contacto en 2.220 s contra 2.233 s detectado por TSDMD al comienzo del paso; retiros 4.01 y
  4.02 s contra 3.90 y 3.93 s), pero en el atasco evacua más lento: seed 1, N = 500, entre 50 y
  100 s, 1.98 cruces/s contra 3.32, y a menos de 4 m de la puerta el 75 % de los agentes está
  escapando contra 54 % en TSDMD (N = 100, 15–35 s, a < 2.5 m: 44 % contra 33 %). En EDMD un
  agente que escapa a 1.5 m/s dentro del atasco toca cuerpos ajenos durante el escape y cada toque
  es un colapso nuevo de los dos; no se aisló cuánto aporta cada diferencia con TSDMD.
- Hold con 0 niveles: el agente queda quieto `8Δt` después de cada escape y vuelve de golpe a
  `r_max`. Seed 3, N = 500: los dos últimos agentes quedaron trabados frente a la puerta hasta
  `t-max` (cada vez que uno vuelve a `r_max` toca al otro o al marco y los dos colapsan).
- Costo: con N = 500, EDMD tarda 8–11 veces más que TSDMD (1.3–1.6·10⁶ eventos procesados contra
  5·10³ pasos). Con N = 100 la diferencia es 1.2–2.8 veces.
- Animaciones de N = 100, seed 1 (estados cada 5 o 10 eventos): `output/edmd/N100_seed1_hold8/`
  (20 eventos por cuadro), `N100_seed1_hold1/` (15) y `N100_seed1_hold0/` (50), cada una con su
  `evacuacion.mp4`. Con 1 nivel (r₁ = 0.117 m, 0.21 m/s) la evacuación de la seed 1 tarda 76.3 s:
  55 % de los colapsos son por salto de radio (75 % con 0 niveles), y a menos de 4 m de la puerta,
  entre 15 y 60 s, 62 % de los agentes se está recuperando y 35 % escapando.

## 7. Escenario de dos agentes (`scenarios/dos_agentes.txt`, seed 1)

Agentes en `(22.5, 2.5)` y `(27.5, 2.5)` m, convergiendo a la puerta. Valores de `dynamic.txt`
guardando todos los pasos:

- Libres a `r_max` y 1.50 m/s desde `t ≈ 0.3 s`. Primer contacto en el paso 68 (`t = 2.267 s`):
  centros a 0.463 m (< `r1 + r2 = 0.50 m`) con los cuerpos separados.
- Paso del contacto: los dos colapsan a `r_min`, escapan a 1.50 m/s casi en horizontal (opuesto
  al otro) y se separan 0.10 m. El paso siguiente ya no hay contacto: `r = 0.117 m` y 0.21 m/s
  hacia el target. El contacto dura un solo paso.
- Con el segundo target común en `(L/2, −1 m)` volvían a tocarse cada 0.17–0.43 s: pasaban la
  puerta lado a lado (0.8 m alcanzan para dos agentes con `r` chico) y afuera convergían al mismo
  punto, así que chocaban hasta retirarse (11 contactos entre los dos; salida del último a los
  5.30 s). Con el target actual `(x_i, −1 m)` salen en paralelo: 4 contactos entre los dos (2
  antes de la puerta y 2 en los primeros 0.3 m afuera) y el último se retira a los 3.93 s.

## 8. Bibliografía de la cátedra (`docs/papers/`)

| Archivo | Trabajo | Para qué sirve acá |
| :--- | :--- | :--- |
| `Biblio_6_7/CPM.pdf` | Baglietto & Parisi, PRE 83, 056117 (2011) | El modelo (secciones 2 y 3) |
| `Biblio_6_7/CPM_AA.pdf` | Martin & Parisi, Physica A 633, 129414 (2024): CPM anisotrópico con elusión (A-CPM, AA-CPM) | Interpretación del radio, regla de targets en una evacuación, superposición con paredes |
| `Biblio_6_7/CPM_Z.pdf` | Oriana, Patterson & Parisi, PRE (2024): juego humano-zombie con CPM | Choques repetidos de agentes que van al mismo target; ruido angular contra simetrías |
| `BiblioGranulares/TehoryAndSimulation...Luding.pdf` | S. Luding, "Theory and simulation of granular materials with hard spheres" (2003, escaneado) | EDMD: algoritmo eficiente y colapso inelástico (modelo TC) |
| `BiblioGranulares/DrivenGranularGases.pdf`, `Experiments and Simulations on Granular Gases.pdf` (tesis, H.-Q. Wang 2011), `AlonsoMarroquinEsferoPoligonos/` | Gases granulares forzados; partículas esfero-poligonales | Sin uso directo por ahora |
| `Biblio_6_7/SFM_2000.pdf`, `SFM_2010.pdf`, `PCA.pdf`, `A new collision avoidance model...pdf` | Helbing et al. Nature 2000 (SFM); Moussaïd et al. PNAS 2011; Karamouzas et al. 2009 (elusión predictiva); Wang et al. Chin. Phys. B 2015 (elusión por velocidad deseada) | SFM y capas de elusión: Problema 1, no elegido |

Datos relevantes:

- **Radio (CPM_AA, Sec. 3.1)**: "el radio de la partícula solo debe interpretarse como un radio
  físico duro cuando está en su valor mínimo (`r_min`); para radios mayores representa el espacio
  personal necesario para caminar". Al chocar, el radio pasa a ser "el radio físico e
  impenetrable". Respalda dibujar el cuerpo como disco de `r_min`.
- **Paredes (CPM_AA, Sec. 4.2)**: afirma que el CPM original no permite superposición con las
  paredes. Sin la regla de pared rígida, en nuestra corrida un cuerpo llegó a meterse 5.5 cm en la
  pared inferior (sección 6). CPM_AA evita la superposición con un término de elusión de paredes
  propio de su modelo; nosotros, con la restricción de la sección 3.
- **Targets en evacuación (CPM_AA, Sec. 4.3)**: target `(x, −3 m)` si `y <= 0.5 m` y `x` está en
  el 80 % central de la puerta; si no, un punto al azar de ese 80 % sobre la línea de la puerta.
  El segundo target conserva la `x` del agente (sale derecho). Lo adoptamos para el segundo target
  (sección 3); para el de la puerta seguimos con la regla del paper original (60 % central).
- **Choques repetidos (CPM_Z, Sec. IV A)**: dos agentes que persiguen el mismo target chocan una y
  otra vez y se frenan ("convergent pursuit"); es el mismo efecto del escenario de la sección 7.
  Agregan ruido angular uniforme en `[−μ/2, μ/2]` (`μ` = 3°) a la dirección deseada para romper
  configuraciones simétricas.
- **Parámetros usados en otros trabajos**: CPM_AA usa `Δt = 1/33 s` (para coincidir con la
  frecuencia de las cámaras); CPM_Z usa `Δt = 0.05 s`, `r_min = 0.15 m`, `r_max = 0.35 m`. Acá el
  enunciado fija `r_min`, `r_max` y que `Δt` es regla del modelo (Ec. 2).
- **EDMD (Luding, Secs. 2.3 y 2.4)**: con choques instantáneos, si el tiempo entre eventos tiende
  a cero aparece el "colapso inelástico" (la tasa de choques diverge). El modelo TC lo evita
  reintroduciendo una duración de contacto `t_c`: si el último choque de la partícula fue hace
  menos de `t_c`, el choque se trata distinto. Análogo directo para el EDMD con CPM, donde el
  escape dura `Δt`. Algoritmo eficiente: actualizar solo las partículas del último evento,
  próximos eventos en un heap (`O(log N)` por cambio), celdas como eventos de cruce para buscar
  compañeros de choque; costo total `O(N log N)`.
