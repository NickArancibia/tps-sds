# AGENTS.md — SdS TP4: Dinámica Molecular Regida por el Paso Temporal (Billar Circular)

> Leer y respetar siempre los lineamientos de `../AGENTS.md` (raíz del repo). El enunciado
> completo está en `docs/Enunciado.md` (PDF original en `docs/enunciado/`) y tiene máxima
> prioridad. Teoría: `../docs/Teorica_4.md` (resumen con fórmulas) y `../docs/Teorica_4.pdf`.

---

## 1. De qué se trata

TP4 de Simulación de Sistemas (ITBA): **dinámica molecular dirigida por el paso temporal**. El
tiempo avanza en pasos fijos `dt`, las fuerzas se recalculan en cada paso y las ecuaciones de
movimiento se integran numéricamente; los contactos duran varios pasos (no hay eventos).

- **Sistema 1 — oscilador puntual amortiguado**: comparar integradores contra la solución
  analítica. Parámetros de la Teórica 4 (el enunciado dice "diapositiva 36"; en
  `Teorica_4.pdf` es la **37**, la 36 es la carátula de "Casos de estudio"): `m = 70 kg`,
  `k = 10⁴ N/m`, `γ = 100 kg/s`, `t_f = 5 s`, `r(0) = 1 m`, `v(0) = −Aγ/(2m)` con `A = 1 m`.
- **Sistema 2 — billar circular**: dominio circular de radio **R = 0.51 m** centrado en el
  origen (área ≈ 0.817 m², misma densidad que la mesa del TP3 a igual N), pared fija.
  **2 obstáculos fijos** de radio `r` en `(±x_o, 0)`. **N partículas** de radio
  **r = 0.0175 m**, masa **m = 0.025 kg**, `|v₀| = 1 m/s` con ángulo ~ U[0, 2π), posiciones al
  azar sin solapamiento (entre sí, con obstáculos ni con la pared). Integrador: **Verlet**.
  Estado (x, y, vx, vy, color) cada `dt₂ = n·dt`.
- Estado **fresca** (azul) → **usada** (roja) al **primer** contacto con un obstáculo. Las usadas
  siguen interactuando (N constante).
- **Entrega: 23/10/2026 13 hs** por campus: `SdS_TP4_2026Q2GXXCSS_Presentación.pdf` y
  `SdS_TP4_2026Q2GXXCSS_Codigo.zip` (**< 100 KB**, solo la versión final del motor). Presentación
  oral de **13 min**.
- Presentación: del sistema 1 **una sola diapositiva** (la figura ECM vs dt de los 4 métodos;
  sin intro ni animaciones). Al final, **diapositiva extra declarando qué agente/modelo de IA se
  usó y cómo** (punto 2.5).

### Puntos del enunciado

| Punto | Qué pide | Parámetros |
| :--- | :--- | :--- |
| 1.1 | Integrar el oscilador con Beeman, Verlet original, Velocity Verlet, Euler predictor-corrector ("por lo menos") | Teórica 4 diap. 37 |
| 1.2 | ECM(dt) vs dt en ejes log para los 4 métodos; ¿cuál es mejor **para este sistema**? | `dt < 10⁻² s` |
| 2.1a | Energía total vs t para varios dt; proponer un **observable escalar** de esa evolución, graficarlo vs dt y elegir el dt del resto del TP | sin obstáculos, N = 300, `dt < 10⁻² s` |
| 2.1b | Tiempo de ejecución promedio ± desvío vs N, en el mismo gráfico que el 1.1 del TP3 **corrido en la misma computadora**; discutir escalamiento | obstáculos en contacto (`x_o = r`), `t_f = 30 s`, N hasta **> 600**, ≥ 10 realizaciones por N |
| 2.2 | `F_u(t)` para pocos `x_o` típicos y `<t_90>` ± error vs `x_o`; reportar realizaciones que no lleguen a 0.9 con su `F_u(t_max)`; ¿hay `x_o` óptimo?; repetir con densidad menor y discutir dependencia con la frecuencia de choques | N = 100 (y p. ej. N = 20), `t_max = 100 s`, `x_o ∈ [r, R − r]`, ≥ 5 realizaciones por `x_o` |
| 2.3 | `f(v)` del módulo de la velocidad a varios t desde 0 hasta el estacionario, promediando realizaciones; ajustar Maxwell-Boltzmann 2D con `k_B T` libre (método Teórica 0); comparar con `m<v²>/2 = m v₀²/2` | sin obstáculos, N = 100 |
| 2.4a | `<t_90>` y `<t_100>` vs densidad **con los outputs del 2.1b**; ¿densidad óptima? ¿por qué? | ídem 2.1b |
| 2.4b | (Opcional) mapa de calor de `<t_90>` o `<t_100>` en `(x_o, N)` | — |
| 2.5 | Diapositiva de declaración de uso de IA | — |

## 2. Modelo

- **Sistema 1**: `m r₂ = −k r − γ r₁`, solución
  `r(t) = A exp(−γt/2m) cos(√(k/m − γ²/4m²) t)`.
- **Sistema 2**, fuerza sobre i (solo normal, sin fricción ni disipación, `k = 10⁴ N/m`):
  `F_i = Σ_j −k ξ_ij ê_ij`, `ξ_ij = r_i + r_j − |r_j − r_i| > 0`,
  `ê_ij = (r_j − r_i)/|r_j − r_i|`. Los j son otras partículas, los obstáculos o la imagen de la
  pared.
- **Pared (partícula imagen)**: `n̂ = r_i/|r_i|`, contacto si `|r_i| > R − r`;
  `r_img = (R + r) n̂`, `ξ_iw = |r_i| + r − R`. La imagen se recalcula en cada dt.
- **Observables** (post-proceso):
  - `ECM(dt) = (1/N_pasos) Σ_k (r_num(t_k) − r_an(t_k))²` sobre todos los pasos.
  - `E(t) = Σ_i ½ m |v_i|² + Σ_{pares en contacto} ½ k ξ_ij² + Σ_{contactos con pared/obstáculo} ½ k ξ²`.
  - `N_u(t)` acumulado de usadas, `F_u(t) = N_u/N`, `t_90` = primer t con `F_u ≥ 0.9`,
    `t_100` = primer t con `F_u = 1`.
  - `f(v)` densidad de probabilidad de `|v|`; MB 2D `f(v) = (m v/k_B T) exp(−m v²/(2 k_B T))`.

## 3. Escalas del sistema (cálculos propios, no del enunciado)

- **Fracción de área** `φ = N r²/R² = 1.18·10⁻³ N`: N = 20 → 0.024, 100 → 0.118, 300 → 0.35,
  400 → 0.47, 600 → **0.71**, 700 → 0.82.
- **Duración de un contacto** (medio período del resorte): par de partículas
  `π√(μ/k)` con `μ = m/2` → **3.5·10⁻³ s**; contra pared u obstáculo `π√(m/k)` →
  **5.0·10⁻³ s**. El rango `dt < 10⁻²` incluye dt mayores que el contacto: ahí el integrador
  no resuelve el choque (sobre-penetración, energía que explota). El dt útil queda del orden de
  10⁻⁵–10⁻⁴ s; lo decide el 2.1a.
- **Superposición máxima** frontal (`ξ = v_rel √(μ/k)`): con `v_rel = 2 m/s`, 2.2 mm (13 % de r);
  contra pared a 1 m/s, 1.6 mm.
- **Energía**: al inicio todo es cinética, `E₀ = N m v₀²/2`; si se conserva y en el estacionario
  la potencial es chica, MB 2D da `m<v²>/2 = k_B T = m v₀²/2 = 0.0125 J`.
- **Oscilador**: `ω ≈ 11.93 rad/s` (período ≈ 0.527 s), decaimiento `2m/γ = 1.4 s`,
  `v(0) = −0.714 m/s`; con `dt = 10⁻²` hay ~53 pasos por período.

## 4. Riesgos y puntos de atención

- **Inicialización a N > 600 (2.1b)**: la inserción aleatoria secuencial (la del TP3) se traba
  cerca de `φ ≈ 0.55` en 2D (N ≈ 465 acá; el TP3 1.1 llegó solo a N = 400 por eso, ver
  `../tp3-event-driven-md/scripts/run_time_vs_n.sh`). A N = 600–700 (`φ` 0.71–0.82) hace falta
  otro método (ej.: red hexagonal con sitios elegidos al azar, o crecer radios). El empaquetado
  hexagonal admite ~720 centros dentro de `R − r`.
- **Comparación con TP3 (2.1b)**: el TP3 1.1 fue mesa rectangular vacía; hay que **re-correr su
  benchmark en la misma máquina** que el del TP4. Para N > 400 el TP3 tampoco puede inicializar
  con su método actual.
- **2.4a reusa los outputs del 2.1b**: esas corridas deben guardar los tiempos de conversión
  (equivalente a `goals.csv` del TP3) aunque sean de benchmark; si no, hay que re-correr (error
  del TP3, no repetir). Con `t_f = 30 s` puede que `t_100` (o `t_90`) no se alcance para algún N:
  reportarlo.
- **Verlet original y velocidades**: `v(t)` recién se conoce después de `r(t+dt)`, con error
  `O(dt²)`. Afecta la energía cinética del 2.1a, la `f(v)` del 2.3 y las velocidades impresas.
- **Sistema 1 con fuerza dependiente de la velocidad**: Verlet original y Velocity Verlet
  necesitan `v` donde todavía no la tienen; Beeman usa la variante predictor-corrector
  (Teórica 4 §4). Como la fuerza es lineal en `v`, también se puede despejar exacto. Documentar la
  elección; afecta el ECM.
- **Tiempos de conversión**: el primer `ξ > 0` con un obstáculo se detecta en el paso en que
  ocurre; registrar el `t` de ese paso (no esperar al `dt₂` de guardado).
- **Barras de error**: `t_90` y el tiempo de ejecución son un escalar por realización → desvío
  estándar (ddof = 1) entre realizaciones. `f(v)` y la energía: definir explícitamente al
  implementar.
- **Benchmark**: medir solo el lazo de integración, sin escribir `dynamic.txt`, una JVM con
  calentamiento (lección del TP3, ver su `run_time_vs_n.sh`).

## 5. Decisiones

### Tomadas (2026-10-02)

- **Sistema 1, motor sin observables**: cada corrida = un esquema + un `dt` + `t_f = 5 s` fijo;
  escribe `t, r, v` cada `n` pasos. La analítica y el ECM se calculan en post-proceso.
- **ECM sobre los estados guardados**, no sobre todos los pasos: con `t_k` los instantes
  guardados y `K` su cantidad, `ECM(dt) = (1/K) Σ_k (r_num(t_k) − r_an(t_k))²`. Difiere de
  la letra del enunciado ("todos los pasos temporales"): escribir esta definición explícita en
  la diapositiva. Condiciones: el intervalo de guardado tiene que ser chico frente al período
  (≈ 0.527 s) para muestrear bien la oscilación del error, y conviene que sea el mismo
  intervalo absoluto para todos los `dt` (mismos `t_k` en todas las curvas), lo que obliga a
  elegir `dt` que lo dividan exactamente.
- **Indicación de la cátedra (consulta 2026-10-02)**: los valores de `r` o `v` que un esquema
  necesita y no tiene (incluidos `r(−dt)`, `v(−dt)`, `a(−dt)` en `t = 0`) se infieren a
  criterio del grupo: desde repetir el valor actual o el anterior hasta estimarlos con Euler.
  Recomendaron Euler o Euler modificado como predictor, evaluar la fuerza y corregir.
- **Velocidad faltante: predictor-corrector en todos los esquemas (2026-10-03)**. Predecir con
  Euler, evaluar la fuerza, corregir una vez; la fuerza/aceleración que pasa al paso siguiente
  se recalcula con la velocidad corregida. Mismo ECM que el despeje (ver chequeos abajo), pero
  no depende de que la fuerza sea lineal en `v` y sigue el patrón de la teórica (Beeman diap.
  20, Euler PC diap. 23). Detalle por esquema en el javadoc de cada clase del motor.
  - Verlet original: `v(t)` predicha desde `v(t−dt)` (centrada, ya conocida) con `a(t−dt)`;
    corrección con la centrada que da la `r(t+dt)` predicha. En el primer paso `v(0)` es dato.
  - Velocity Verlet: `v(t+dt)` predicha como `v(t) + a(t) dt`.
  - Beeman: variante PC de la teórica; `a(t+dt)` se recalcula con la `v` corregida (la
    diapositiva no lo dice; mismo criterio que Velocity Verlet).
  - Arranques: `r(−dt)` (Verlet) y `a(−dt)` (Beeman) por Euler en `−dt`.
- **`t_f = 5 s` (sistema 1)**: es parámetro de la teórica (diap. 37) y ya es significativo:
  ~9.5 períodos, amplitud final 2.8 % de la inicial (`e^{−t/1.4}`); con un error que crece como
  `t e^{−t/τ}`, el 97 % de la integral del error cuadrático cae antes de 5 s. Alargarlo solo
  diluye el promedio del ECM. Configurable con `--tf`.

### Abiertas (charlar antes de implementar)

1. Sistema 2: "esquema de Verlet" = **Verlet original** o **Velocity Verlet** (el 1.1 los
   distingue; la teórica llama "Algoritmo de Verlet" al original).
2. ~~Sistema 1: cómo evaluar la fuerza amortiguada~~ → decidido (predictor-corrector, arriba).
   Registro de las alternativas evaluadas:
   Opciones: diferencia hacia atrás / medio paso, predictor Euler, predictor-corrector, o
   despeje exacto (fuerza lineal en `v`), con `c = γ dt/(2m)`:
   - Verlet: `r(t+dt) = [(2 − k dt²/m) r(t) − (1 − c) r(t−dt)] / (1 + c)`. Implementarlo como
     incremento, `r(t+dt) = r(t) + [(1 − c)(r(t) − r(t−dt)) − (k dt²/m) r(t)] / (1 + c)`: la
     forma directa pierde precisión por redondeo (ECM 1.7·10⁻¹⁶ en dt = 10⁻⁵ y 7·10⁻¹⁵ en
     5·10⁻⁶, contra 3.8·10⁻¹⁸ y 1.9·10⁻¹⁹ con el incremento).
   - Velocity Verlet: `v(t+dt) = [v(t) + dt/(2m) (f(t) − k r(t+dt))] / (1 + c)`.

   Chequeo descartable (script fuera del repo, 2026-10-02, ECM sobre todos los pasos,
   dt = 10⁻³, 5·10⁻⁴, 2.5·10⁻⁴): diferencia hacia atrás (Verlet) y medio paso (Velocity
   Verlet) dan pendiente log-log ≈ 2 (orden 1); predictor Euler, predictor-corrector y despeje
   dan ≈ 4 (orden 2). No es resultado para presentar: hay que rehacerlo con el motor. Comparar
   variantes de Verlet sirve para elegir, pero el enunciado limita el sistema 1 a **una**
   diapositiva con los 4 métodos: la comparación no entra (salvo que la cátedra acepte un anexo).

   Beeman tiene el mismo problema (`a(t+dt)` necesita `v(t+dt)`), pero la teórica ya lo
   resuelve con su variante predictor-corrector (diap. 20); Euler predictor-corrector no
   necesita ajuste (su predicción ya da `v^p`). Segundo chequeo descartable (ECM guardando cada
   10⁻² s, dt de 10⁻² a 10⁻⁵): Verlet, Velocity Verlet (ambos con despeje) y Beeman (PC o
   despeje, casi idénticos) dan pendiente 4, Beeman con ECM ~13 % menor; Euler PC pendiente
   ≈ 2, con 3·10³ (dt = 10⁻²) a 10¹⁰ (dt = 10⁻⁵) veces más ECM.

   Tercer chequeo descartable, Verlet con predictor-corrector: predecir `v(t)` con Euler desde
   `v(t−dt) = (r(t) − r(t−2dt))/(2dt)` (en el primer paso, `v(0)` es dato), evaluar `f(t)`,
   avanzar y corregir con la `v(t)` centrada que da la `r(t+dt)` predicha. Con 1 corrección da
   el mismo ECM que el despeje (2 correcciones no cambian nada); solo predictor da ~20 % más,
   misma pendiente 4. Velocity Verlet PC (predecir `v(t+dt) = v(t) + a(t) dt`) da ~5 % menos
   que el despeje si `f(t+dt)` se recalcula con la `v` corregida, ~20 % más si no.
3. ¿Se agrega Gear de orden 5 al sistema 1? El enunciado dice "por lo menos" los 4, pero la
   diapositiva pide la figura "para los 4 métodos solicitados".
4. Método de inicialización para N alto, y si se usa el mismo para todos los N.
5. Observable escalar del 2.1a (ej.: `max_t |E(t) − E₀|/E₀`, promedio temporal de
   `|E(t) − E₀|/E₀`, o pendiente de deriva) y criterio de tolerancia para elegir dt.
6. Valores de N del 2.1b/2.4a y de `x_o` del 2.2; cantidad de realizaciones.
7. Criterio de estacionario para `f(v)` en el 2.3 (ej.: `<v⁴>/<v²>²`, que vale 1 al inicio y 2
   para MB en 2D) y ancho de bins del histograma.
8. Búsqueda de vecinos: CIM de `../common/` (grilla sobre `[−R, R]²`, sin periodicidad) vs.
   fuerza bruta; impacta directo en el escalamiento del 2.1b.

## 6. Arquitectura

### Implementado (2026-10-03): sistema 1

Módulo Maven `md-java/` (depende de `common/` solo por `CliArgs`). Compilar desde la raíz:
`mvn package` → `md-java/target/md.jar`. Uso: `java -jar md.jar oscillator --scheme <esq>
--dt <dt>` (ver `README.md`).

```
md-java/src/main/java/ar/edu/itba/sds/tp4/
├── Main.java                       # CLI: primer argumento = sistema (oscillator; billar después)
└── oscillator/
    ├── OscillatorRun.java          # CLI del sistema 1, lazo de pasos, trajectory.csv + run.json
    ├── Force.java                  # f(r, v) en 1D
    ├── DampedOscillator.java       # f = −k r − γ v
    ├── Integrator.java             # step(), position(), velocity() en el mismo instante
    ├── Scheme.java                 # enum CLI → integrador
    ├── Beeman.java, OriginalVerlet.java, VelocityVerlet.java, EulerPredictorCorrector.java
```

- `tf` y `save-dt` tienen que ser múltiplos enteros de `dt` (si no, error): el guardado usa
  contador entero de pasos y los mismos `t_k` para todos los `dt`.
- `trajectory.csv` con `Double.toString` (precisión completa: el ECM llega a 10⁻¹⁸).
- Verlet original va un paso adelantado internamente para informar `r(t)` y `v(t)` juntas.
- Post-proceso: `analysis/oscillator_common.py` (carga + analítica),
  `analysis/animate_oscillator.py` (masa-resorte + `r(t)` vs analítica, un cuadro por estado
  guardado).
- Verificado 2026-10-03 (corridas de prueba en `output/oscillator/prueba/`, ECM guardando cada
  10⁻² s, dt = 10⁻², 10⁻³, 10⁻⁴, 10⁻⁵): Beeman 3.4·10⁻⁶ … 3.3·10⁻¹⁸, Verlet 3.8·10⁻⁶ …
  3.8·10⁻¹⁸, Velocity Verlet 3.8·10⁻⁶ … 3.6·10⁻¹⁸ (pendiente 4); Euler PC 1.2·10⁻² … 3.4·10⁻⁸.
  Coincide con los chequeos de `exploracion/`.
- **Punto 1.2 (2026-10-03)**: `scripts/run_oscillator_sweep.sh` (4 esquemas × dt = 5·10⁻³ …
  10⁻⁶ en secuencia 1-2-5; dt < 10⁻² como pide el enunciado) → `output/oscillator/sweep/`;
  `analysis/plot_ecm.py` → `analysis/figures/ecm_vs_dt.png` + tabla y pendientes por stdout.
  Resultado: Beeman < Velocity Verlet < Verlet original por ~8 % y ~13 % (indistinguibles en
  la figura log-log), las tres con pendiente 4.00 (orden 2); Euler PC pendiente 1.86 en
  10⁻⁴–5·10⁻³ y 2.0 para dt chicos (orden 1), 10⁴–10¹² veces más ECM. Verlet original se
  aplana en ~10⁻¹⁹ para dt ≤ 5·10⁻⁶ mientras las otras siguen bajando hasta 3·10⁻²²:
  probablemente redondeo de `2r(t) − r(t−dt)` (sin verificar; la forma "sumada" de Verlet, que
  acumula `r(t) − r(t−dt)`, lo evitaría). Pendiente decidir: explicarlo o cortar el barrido.

### Convenciones del repo

- Motor en **Java**, módulo Maven propio dentro de este directorio, agregado a `<modules>` del
  `pom.xml` raíz; reutilizar `../common/` (`Particle`, `CliArgs`, IO estático/dinámico, CIM)
  donde encaje. El zip < 100 KB lleva solo el `src/` del motor (+ lo usado de `common`).
- Post-proceso en Python en `analysis/` (figuras en `analysis/figures/`), scripts de barridos
  en `scripts/`, outputs crudos en `output/`.
- `exploracion/`: prototipos en Python para decidir antes de implementar (no van al zip ni a
  la presentación). `verlet_variantes.py` compara formas de inferir `v(t)` en Verlet original
  para el oscilador → `verlet_variantes_ecm.png` (ECM vs dt) y `verlet_variantes_cociente.png`
  (ECM relativo al despeje).
- Cada corrida escribe `static.txt` / `dynamic.txt` (formato de cátedra, `../AGENTS.md` §2.2,
  más el estado fresca/usada), los tiempos de conversión, y `run.json` con todos los inputs
  (integrador, `dt`, `dt₂`, seed, `t_f`, `x_o`, N) y tiempos del lazo.
- Guardado con contador entero de pasos (`paso % n == 0`), incluyendo `t = 0`.
