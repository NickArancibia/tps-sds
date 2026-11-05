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
- **Pared rígida sobre el cuerpo (agregado propio, 2026-11-05; no está en el paper)**: después de
  calcular la velocidad con las reglas del CPM y antes de mover, para cada pared con `d` =
  distancia del centro a su punto más cercano `p` y `n = (x − p)/d`: si `v·n < 0` y
  `d + (v·n) Δt < r_min`, la componente normal se reemplaza por `−max(0, d − r_min)/Δt` (el cuerpo
  termina tocando la pared); la tangencial no cambia. Motivo: el escape suma un versor por
  contacto y la pared pesa como un agente, así que con varios agentes empujando el escape podía
  apuntar hacia la pared y meter el cuerpo hasta 5 cm (o atravesarla, porque la pared no tiene
  espesor). Justificación: paredes rígidas (enunciado) y cuerpo `r_min` impenetrable (CPM_AA).
  El paper trata la pared solo como un contacto más; CPM_AA lo evita con un término de elusión
  que no es parte del CPM. Declararlo como agregado propio en la presentación.

### Abiertas

- EDMD: duración del escape (natural: un `Δt`, evento "fin de escape") y mecanismo de
  recuperación (escalones de `Δt`, escalones más gruesos, recuperación instantánea, o trayectoria
  curva con búsqueda de raíces).
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
| `cpm/RigidWalls` | Restricción de pared rígida sobre el cuerpo `r_min` (agregado propio) |
| `io/Output` | `static.txt`, `dynamic.txt`, `events.csv` |
| `EvacuationRun`, `Main` | CLI |

Outputs en `output/tsdmd/<corrida>/` (ignorado por git): `static.txt` (`N`, `L`, `r_min r_max`
por agente), `dynamic.txt` (por estado: `t` y N filas `x y vx vy r tx ty fase contacto`; fase 0 =
en la habitación, 1 = cruzó la puerta, 2 = retirado), `events.csv` (`t,id,event` con door/exit) y
`run.json` (inputs, `Δt`, `Δr`, tiempo de evacuación, tiempo de ejecución del lazo y cuántos
pasos-agente recortó la pared rígida, separados en escape y velocidad deseada). Con la misma
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
  versores y puede empujar a un agente hacia un contacto si los demás contactos dominan.
- Lo mismo pasaba contra las paredes antes de la regla de pared rígida: un agente apretado contra
  la pared inferior podía tener escape hacia la pared (la pared es un solo contacto contra varios
  agentes). El mínimo fue `y = 0.045 m` (cuerpo 5.5 cm adentro con `r = 0.10 m`); ningún agente
  la llegó a cruzar.
- Reingresos: agentes que cruzaron la puerta y el atasco empujó de vuelta adentro. Siguen en fase
  1; `events.csv` registra solo el primer cruce.

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
