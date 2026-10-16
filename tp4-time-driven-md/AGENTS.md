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
  `../tp3-event-driven-md/scripts/run_time_vs_n.sh`). Resuelto en el TP4 con `--init hex`
  (2026-10-08, §6): red triangular de lado `2r`, 716 sitios sin obstáculos y 714 con `x_o = r`.
- **Comparación con TP3 (2.1b)**: el TP3 1.1 fue mesa rectangular vacía; hay que **re-correr su
  benchmark en la misma máquina** que el del TP4. Resuelto (2026-10-12): el TP3 ganó
  `--init hex` (red triangular centrada en la mesa, 737 sitios) y se re-corre con red hexagonal
  para todos los N, hasta 675 (§6).
- **2.4a reusa los outputs del 2.1b**: con `t_f = 30 s` no se llega a `t_90` desde N = 200 ni a
  `t_100` casi nunca. Resuelto (2026-10-12): el motor es determinista, así que una corrida con la
  misma semilla reproduce bit a bit la del benchmark (verificado: `conversions.csv` idéntico en
  N = 25 y 50, semilla 1) y se extiende con `--stop-at-t100` hasta `t_max = 1500 s` (§6). Las
  realizaciones que no llegan se reportan con `F_u(t_max)`.
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
  - Arranques: `a(−dt)` (Beeman) por Euler en `−dt` (con la exacta da el mismo ECM).
    `r(−dt)` (Verlet) por **Taylor hasta tercer orden** (2026-10-05):
    `r(0) − dt v(0) + dt²/2 a(0) − dt³/6 j(0)`, `j = (df/dt)/m` (`Force.rate`; en el oscilador
    `df/dt = −k v − γ a`). Con Euler en `−dt` (solo hasta dt², lo de la teórica) el ECM era ~9 %
    mayor (C = 379 vs 348 m² s⁻⁴), mismo orden.
- **`t_f = 5 s` (sistema 1)**: es parámetro de la teórica (diap. 37) y ya es significativo:
  ~9.5 períodos, amplitud final 2.8 % de la inicial (`e^{−t/1.4}`); con un error que crece como
  `t e^{−t/τ}`, el 97 % de la integral del error cuadrático cae antes de 5 s. Alargarlo solo
  diluye el promedio del ECM. Configurable con `--tf`.

### Abiertas (charlar antes de implementar)

1. Sistema 2: "esquema de Verlet" = **Verlet original** o **Velocity Verlet** (el 1.1 los
   distingue; la teórica llama "Algoritmo de Verlet" al original). El motor tiene los dos
   (`--scheme`). Con fuerza que depende solo de posiciones son **el mismo algoritmo**: además de
   las mismas posiciones, `r(t+dt) − r(t−dt) = 2 dt v_VV(t)`, así que la velocidad centrada de
   Verlet coincide con la de Velocity Verlet. Lo único que cambia es el redondeo (ver §6,
   sistema 2). Velocity Verlet es más simple (sin arranque `r(−dt)` ni paso adelantado).
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
4. ~~Método de inicialización para N alto~~ → red hexagonal (`--init hex`, §6), usada para
   **todos** los N del 2.1b (mismo método en toda la curva; elegido 2026-10-08).
5. ~~Observable escalar del 2.1a y dt~~ → error medio ε y **dt = 10⁻⁵ s** (2026-10-08, §6).
6. ~~Valores de N del 2.1b/2.4a~~ → N = 25, 50, 100, 150, 200, 300, 400, 500, 600, 625, 650,
   675, 10 realizaciones, en los dos motores (2026-10-12; 700 se sacó por costo del TP3, §6).
   ~~`x_o` del 2.2~~ → r, 0.05, 0.10, …, 0.45, R − r (11 valores), N = 100 y 20, 5 realizaciones,
   red hexagonal (2026-10-14, §6).
7. Criterio de estacionario para `f(v)` en el 2.3 y ancho de bins del histograma. Decidido
   (2026-10-14): inicio del estacionario **a ojo** con recta vertical sobre la evolución de un
   escalar (propuesto `<v⁴>/<v²>²`, 1 en t = 0 y 2 para MB 2D), como en TP2/TP3; `t_f` = 10 s,
   estado cada 0.01 s, **10 realizaciones**, red hexagonal, sin obstáculos, N = 100. Pendiente:
   bins.
8. ~~Búsqueda de vecinos~~ → implementado con grilla de celdas propia (§6, sistema 2); costo por
   paso O(N), relevante para el escalamiento del 2.1b.

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
- **Punto 1.2 (2026-10-03, re-corrido 2026-10-05 con el arranque nuevo de Verlet)**:
  `scripts/run_oscillator_sweep.sh` (4 esquemas × dt = 5·10⁻³ … 10⁻⁶ en secuencia 1-2-5;
  dt < 10⁻² como pide el enunciado) → `output/oscillator/sweep/`; `analysis/plot_ecm.py` →
  `analysis/figures/ej1/ecm_vs_dt.png` + tabla y pendientes por stdout. Resultado: Beeman < Verlet
  original < Velocity Verlet por ~6 % y ~10 % (indistinguibles en la figura log-log), las tres
  con pendiente 4.00 (orden 2); Euler PC pendiente 1.86 en 10⁻⁴–5·10⁻³ y 2.0 para dt chicos
  (orden 1), 10⁴–10¹² veces más ECM. Verlet original se aplana en ~10⁻¹⁹ para dt ≤ 5·10⁻⁶
  mientras las otras siguen bajando hasta 3·10⁻²²: probablemente redondeo de
  `2r(t) − r(t−dt)` (sin verificar; la forma "sumada" de Verlet, que acumula `r(t) − r(t−dt)`,
  lo evitaría). Pendiente decidir: explicarlo o cortar el barrido.
  `plot_ecm.py` también escribe `analysis/figures/ej1/ecm_dt4_vs_dt.png` (2026-10-05, **solo para
  análisis, no va a la diapositiva**): ECM/dt⁴ vs dt de los tres esquemas de orden 2 en eje y
  lineal, solo dt ≥ 10⁻⁵ (debajo, el piso de Verlet lo saca de escala). Constantes
  `C = ECM/dt⁴`: Beeman 330, Verlet original 348 (×1.06), Velocity Verlet 364 (×1.10) m² s⁻⁴,
  planas en todo el rango (VV y Beeman suben ~2 % en dt = 5·10⁻³ por términos de orden
  superior). Descartado: lupa en dt = 10⁻³ dentro de `ecm_vs_dt.png` (no gustó).
  También `analysis/figures/ej1/ecm_vs_dt_tramo.png` (solo análisis): el log-log de `ecm_vs_dt.png`
  recortado a dt ∈ [10⁻³/1.04, 10⁻³·1.04] y a los tres esquemas de orden 2 (rectas paralelas;
  un solo punto medido, el resto son los segmentos guía hacia 5·10⁻⁴ y 2·10⁻³).
  Los chequeos de abajo (2026-10-05) son con el arranque de Euler de Verlet (C = 379).
  Verlet con despeje vs predictor-corrector (2026-10-05, `exploracion/verlet_variantes.py`,
  mismo ECM): C = 379.7 / 379.5 / 379.4 (despeje) contra 380.1 / 379.5 / 379.5 (PC) en
  dt = 5·10⁻³ / 10⁻³ / 10⁻⁴; cociente PC/despeje 1.001 → 1.00003. El despeje (forma
  incremental) también se aplana en ~10⁻¹⁹ para dt ≤ 5·10⁻⁶ (1.9·10⁻¹⁹, 1.1·10⁻¹⁹, 1.8·10⁻¹⁹,
  idénticos al PC): el piso no viene del predictor-corrector.
  Equivalencia (motor, 2026-10-05): con `--gamma 0` Verlet y Velocity Verlet dan las mismas
  posiciones (máx. 3·10⁻¹² m) y los tres el mismo ECM; con γ = 1000 kg/s se separan (Verlet/
  Beeman 6.2, VV/Beeman 0.80). Las diferencias vienen solo de la v dentro de −γv.
  Chequeo descartable de arranque y velocidad (Python fuera del repo, C = ECM/dt⁴ en dt = 10⁻³ /
  10⁻⁴, m² s⁻⁴): Beeman 330 (a(−dt) exacta: igual); Verlet PC 379 = despeje 379; **Verlet con
  r(−dt) por Taylor de 3er orden (jerk = (−k v − γ a)/m) o exacta: 348** (−8 %, sigue arriba de
  Beeman); Verlet con v(t) de 3 puntos hacia atrás 436; VV PC 363 (motor); VV implícito (despeje
  o PC iterado a convergencia) 379, igual a Verlet con arranque de Euler; VV sin recalcular f
  con la v corregida 436; VV con predictor Adams-Bashforth 2 377–379. Ninguna variante bajó de
  Beeman con γ = 100. Beeman sin recalcular a(t+dt) con la v corregida (pasa la de la v
  predicha, literal de la teórica): C = 327.0 / 328.7 contra 329.6 / 329.0 del motor (< 1 %).

### Implementado (2026-10-08): sistema 2, motor + barrido de dt del 2.1a

```
md-java/src/main/java/ar/edu/itba/sds/tp4/billiard/
├── BilliardRun.java      # CLI (java -jar md.jar billiard ...), lazo, static/dynamic/conversions/run.json
├── Table.java            # R, r, m, k, obstáculos en (±x_o, 0)
├── ContactForces.java    # resortes partícula-partícula (grilla de celdas), pared (imagen), obstáculos;
│                         # registra la conversión fresca → usada en el paso del primer ξ > 0
├── Integrator.java, Scheme.java
├── VelocityVerlet.java, OriginalVerlet.java   # Verlet en forma sumada, v centrada, paso adelantado
└── InitialState.java     # random: inserción secuencial al azar en |r| <= R − r (se traba en N ≈ 465)
                          # hex: N sitios al azar de una red triangular de lado 2r(1 + 10⁻⁹)
```

- Grilla propia (no el CIM de `common`): 29 × 29 celdas de lado `2R/29 ≥ 2r` sobre `[−R, R]²`,
  sin listas de vecinos ni alocación por paso; la fuerza se suma en el mismo recorrido.
- `dynamic.txt` con precisión completa (`Double.toString`): la energía potencial se calcula en
  post-proceso con `ξ ~ 10⁻³ m` y hace falta resolver desvíos relativos de 10⁻⁸.
- Post-proceso: `analysis/billiard_common.py` (carga, `E = Σ ½ m v² + Σ_contactos ½ k ξ²`).
- **Barrido 2.1a** (`scripts/run_energy_sweep.sh` → `output/billiard/energy_dt/`;
  `analysis/plot_energy_dt.py` → `analysis/figures/ej2/`): N = 300 sin obstáculos,
  `t_f = 10 s`, estado cada 5·10⁻² s, **semillas 1–10**, dt = 5·10⁻³ … 10⁻⁶ (1-2-5), ambos
  esquemas. El sistema es conservativo: todo cambio de E es error de integración (criterio de la
  Teórica 4, diap. 34–35, para casos sin solución analítica). Error relativo
  `ΔE(t) = (E(t) − E₀)/E₀` (antes llamado "desvío relativo"; se renombró para no confundirlo
  con el desvío estándar de las barras).
  - **Observable elegido (2026-10-08): error medio** `ε = (1/K) Σ_{t_k>0} |ΔE(t_k)|` sobre los
    K = 200 estados guardados; un escalar por realización, barra = desvío estándar entre las 10
    semillas (ddof = 1). Descartados: `|ΔE(t_f)|` (desvío entre semillas del orden de su
    promedio) y `max|ΔE|` (paralelo a ε, factor ~2-3).
  - Figuras: `energia_vs_t.png` (E(t) con dt = 5·10⁻⁴, 10⁻⁴, 5·10⁻⁵, 10⁻⁵, semilla 1; 10⁻³ se
    sacó: diverge y aplasta la escala), `energia_error_medio_dt.png` (ε vs dt, Velocity Verlet,
    10 semillas por punto), `energia_esquemas_dt.png` (ε vs dt, ambas variantes),
    `energia_costo_dt.png`. Las figuras de ε excluyen los dt que divergen (ε ≥ 1: 10⁻³, 2·10⁻³,
    5·10⁻³), que se informan al costado.
  - **dt elegido (2026-10-08): 10⁻⁵ s**, recta vertical en `energia_error_medio_dt.png`.
    Criterio: mayor dt redondo con ε < 10⁻⁴ (ε = 5·10⁻⁶; 2·10⁻⁵ también cumple, 5·10⁻⁵ no).
    ~350 pasos por contacto partícula-partícula; dt ≥ 10⁻³ diverge.
  - ε (Velocity Verlet, promedio ± desvío): 2.3·10⁻² ± 9·10⁻³ (5·10⁻⁴), 4.7·10⁻⁴ ± 2·10⁻⁴
    (10⁻⁴), 5.0·10⁻⁶ ± 2·10⁻⁶ (10⁻⁵), 7·10⁻⁸ ± 4·10⁻⁸ (10⁻⁶); pendiente log-log 2.03 en
    10⁻⁶–5·10⁻⁴ (orden 2). dt = 10⁻³: 9·10³ (diverge; `|ΔE| = 1` entre 1.55 y 2.05 s);
    2·10⁻³: 4·10⁵; 5·10⁻³: E no finita en las 10 semillas.
  - Verlet original y Velocity Verlet: mismo ε dentro de las barras en todo el rango.
    Partiendo de la misma condición inicial, las trayectorias se separan por redondeo
    amplificado por el caos: 2.5·10⁻¹⁰ m a 0.2 s, 2.6·10⁻⁵ m a 0.4 s, 0.09 m a 0.6 s
    (exponente ~58 s⁻¹, dt = 10⁻⁴). Ninguna trayectoria individual es reproducible a más de
    ~0.5 s: solo valen las estadísticas sobre semillas.
  - Costo (14 corridas en paralelo, no es benchmark): ~4 µs por paso por cada 100 partículas;
    10⁻⁵ s → 41 s por cada 10 s simulados con N = 300.
- **Punto 2.1b** (2026-10-08): `scripts/run_time_vs_n.sh` corre, secuencial y en esta máquina,
  el `--bench` del TP3 (su 1.1: mesa vacía, N = 25 … 400, `output/tp3_time_vs_n/`) y el
  `--bench` del TP4 (`billiard --bench`, `output/billiard/time_vs_n/N<N>/s<seed>/`): `x_o = r`,
  `--init hex` para **todos** los N (mismo método en toda la curva), dt = 10⁻⁵ s, t_f = 30 s,
  N = 25, 50, 100, 150, 200, 300, 400, 500, 600, 700, 10 seeds. Una JVM, 30 s de calentamiento,
  orden aleatorio, sin `dynamic.txt`; guarda `conversions.csv` (para el 2.4a) y `run.json`
  (`loopTimeMs`). `analysis/plot_time_vs_n.py` → `ej2/tiempo_vs_n.png` (log-log, promedio ±
  desvío entre realizaciones) y exponentes locales por stdout. Prueba previa (0.5 s simulados):
  N = 50 → 0.22 s, N = 700 → 1.84 s, o sea ~13 s y ~110 s por corrida de 30 s.
  **Corrido 2026-10-08** (80 min en total; log en `output/time_vs_n.log`). Tiempo del lazo,
  promedio ± desvío (10 realizaciones):
  - TP3 (eventos): 0.0020 s (N = 25), 0.096 (100), 1.07 (200), 6.1 (300), 25.0 (400);
    exponente local 2.6 → 4.9 (crece con N).
  - TP4 (paso temporal): 12.5 s (25), 17.0 (100), 25.4 (200), 36.0 (300), 49.8 (400), 66 (500),
    86 (600), 115 (700); exponente local 0.14 → 1.87. A N chico domina el costo fijo por paso
    (recorrer las 29 × 29 celdas, 3·10⁶ pasos); a N grande crece más que lineal porque con área
    fija los pares a revisar por celda crecen con la densidad [inferencia, no medido aparte].
  - TP3 más rápido en todo el rango medido (×6400 en N = 25, ×2 en N = 400). Cruce no medido:
    el TP3 no inicializa arriba de N ≈ 400.
  - Para el 2.4a (mismos outputs): F_u(30 s) = 0.93 (25), 0.95 (100), 0.89 (150), 0.86 (200),
    0.71 (300), 0.55 (400), 0.34 (500), 0.14 (600), 0.01 (700). t_90 alcanzado en 7, 10, 9, 4
    de 10 realizaciones para N = 25, 50, 100, 150 y en ninguna desde N = 200.
- **Actualización 2.1b (2026-10-12)**: se agregan N = 625 y 650 (los dos motores) y el TP3 se
  re-corre con `--init hex` en todos los N (25 … 700, mismo método que el TP4). El benchmark del
  TP4 existente (2026-10-08) no se re-corre: solo se miden 625 y 650 (otra sesión, misma
  máquina). `run_time_vs_n.sh` re-mide solo los N de `NS3`/`NS4`. Comando lanzado:
  `NS4=625,650 ./scripts/run_time_vs_n.sh && ./scripts/run_t100_vs_n.sh`, log en
  `output/corridas_2026-10-12.log`.
  Pruebas previas del TP3 con red hexagonal: 737 sitios (738 falla); `--verify` sin
  superposiciones a N = 700 y 737 (0.01 s, ~17–19 mil eventos); con `--init random` reproduce el
  benchmark viejo (N = 100, semilla 1: 25481 eventos, igual). Costo a N = 700, semilla 1: 4.36·10⁶
  eventos en 6 s simulados, 439 s de lazo (el primer segundo, ~10⁶ eventos, es el más caro:
  arranca con vecinas a 3.5·10⁻¹¹ m); estimado ~20 min por corrida de 30 s. Cola de eventos
  1.35·10⁷ a 3 s y 1.43·10⁷ a 6 s (se satura), RSS 3.5 GB. 1 s simulado (4 en paralelo):
  N = 500 4.2 s, 600 13.4 s, 650 26.7 s, 700 123 s.
  **Cambio (2026-10-12, 23:40): N = 700 → 675** en los dos motores (2.1b y 2.4a). El TP3 a
  N = 700 tardó 35 min por corrida (1 hecha, borrada); quedan tres N > 600 y el cruce de costos
  ya se ve entre 400 y 500. El benchmark del TP4 a N = 700 (2026-10-08) se movió a
  `output/billiard/time_vs_n_N700/` (fuera de la figura, por si sirve en otro punto). Se cortó
  la cadena y se reanudó con `RESUME=1 NS4=625,650,675 ./scripts/run_time_vs_n.sh &&
  ./scripts/run_t100_vs_n.sh` (los `--bench` saltean las corridas con `run.json`; 50 de 120
  ya hechas). Medido en esta sesión antes del corte (TP3, lazo por corrida): N = 500 83 s,
  600 4.1 min, 625 5.7 min, 650 8.5 min, 700 35 min.
  **ESTADO (2026-10-13 13:20; si se corta, los `run.json` del disco mandan sobre esta nota)**:
  - Benchmark TP3 (`output/tp3_time_vs_n/`): **completo, 120 de 120** (sesiones 10-12 noche y
    10-13 mañana). Lazo promedio ± desvío (s): 0.0019 (25), 0.092 (100), 1.09 (200), 5.6 (300),
    24 ± 2 (400), 87 ± 10 (500), 246 ± 17 (600), 351 ± 36 (625), 512 ± 32 (650), 850 ± 70
    (675). Exponente local 2.6 → 13 (crece sin parar). Cruce con el TP4 entre N = 400 y 500.
  - Benchmark TP4: medir solo 625/650/675 hoy contra el resto del 10-08 daba un escalón
    (N = 625 84.7 s < N = 600 86.4 s, desvíos ~0.5 s: deriva entre sesiones). Decidido
    2026-10-13: **re-correr el benchmark TP4 completo (12 N × 10) en una sola sesión**, antes del
    2.4a. El del 10-08 quedó en `output/billiard/time_vs_n_2026-10-08/` (respaldo; N = 700 sigue
    en `time_vs_n_N700/`). Lanzado 13:20, ~1.7 h.
  - Corridas largas 2.4a (`output/billiard/t100_vs_n/`): arrancan solas después del benchmark
    TP4. ~6 h, en paralelo; no miden tiempo.
  - Comando en curso (desde `tp4-time-driven-md/`, log al final de
    `output/corridas_2026-10-12.log`): `NS3= ./scripts/run_time_vs_n.sh &&
    ./scripts/run_t100_vs_n.sh`. Si se corta, retomar con
    `RESUME=1 NS3= ./scripts/run_time_vs_n.sh && ./scripts/run_t100_vs_n.sh` (sin `RESUME=1`
    borraría lo ya medido del TP4). Sin carga pesada en la PC hasta que termine el benchmark.
  - Después: `python3 analysis/plot_time_vs_n.py` y `python3 analysis/plot_t100_vs_n.py`;
    decidir qué hacer con los N que no completan las 10 realizaciones en el 2.4a.
  - **Benchmark TP4 completo (2026-10-13, 13:20–15:00, una sesión)**: lazo promedio ± desvío
    (s): 11.54 ± 0.12 (25), 15.85 (100), 23.7 (200), 33.5 (300), 46.1 (400), 61.5 (500),
    80.5 ± 0.4 (600), 86.7 ± 0.8 (625), 92.2 ± 0.1 (650), 100 ± 3 (675); ~7–8 % más rápido que
    el del 10-08. Exponente local 0.15 → ~2. `tiempo_vs_n.png` regenerada con TP3 y TP4
    completos. Corridas largas del 2.4a arrancaron ~15:00 (N grandes primero).
  - **2.4a cortado a mano (2026-10-13 16:54)**: 0 corridas completas. Las 14 en curso (10 de
    N = 675 a ~1000 s simulados, 4 de 650 a ~1050 s) se borraron (no hay checkpoint). Vistazo
    antes de cortar (último estado de `dynamic.txt`): N = 675 `F_u` ≈ 0.01 a ~920 s (casi igual
    que a 30 s), N = 650 0.06–0.08 a ~970 s (0.02 a 30 s). Con 14 en paralelo cada corrida va ~2×
    más lenta que en el benchmark (N = 675: ~9 s simulados por minuto, ~2.8 h hasta 1500 s).
    Estimado para todo el 2.4a: ~8 h. Retomar desde `tp4-time-driven-md/` con
    `./scripts/run_t100_vs_n.sh` (saltea las que tienen `run.json`; no mide tiempos).
  - **Relanzado 2026-10-13 18:41 solo N ≤ 600** (decisión: ver primero los N que llegan a
    `t_90`; 625, 650 y 675 se deciden después): `NS="25 50 100 150 200 300 400 500 600"
    ./scripts/run_t100_vs_n.sh`, mismo `t_max = 1500 s`. Estimado ~2.5 h (lo dominan las 10 de
    N = 600). Si se corta, mismo comando (saltea las completas).
  - **Cortado 2026-10-13 21:00 (RETOMAR DESDE ACÁ)**: completas N = 400 (8/10: faltan s9, s10),
    500 (10/10), 600 (10/10). Faltan todas las de N = 25, 50, 100, 150, 200, 300 (cortas, cortan
    en `t_100`) y luego decidir 625/650/675. Retomar con el mismo comando
    `NS="25 50 100 150 200 300 400 500 600" ./scripts/run_t100_vs_n.sh` (~30–40 min estimado).
    Parcial (promedio ± desvío entre realizaciones): `<t_90>` 87 ± 5 s (400), 172 ± 9 (500),
    571 ± 26 (600); `<t_100>` 258 ± 30 (400), 560 ± 100 (500); N = 600 llega a `t_100` en 1 de
    10 (1433 s), las otras 9 con `F_u(1500 s)` = 0.997 ± 0.002.
    **Ojo**: leer `F_u` del último bloque de un `dynamic.txt` en escritura subestima (bloque
    truncado por el buffer); los vistazos de N = 600 (0.78 a ~1060 s) y de 650/675 de la tarde
    eran subestimaciones. Usar `conversions.csv` solo de corridas terminadas.
  - **Completo N ≤ 600 (2026-10-14, 09:39–09:56)**, 90/90. Promedio ± desvío entre las 10
    realizaciones, `<t_90>` (s): 27 ± 7 (25), 23 ± 4 (50), 23 ± 3 (100), 31 ± 4 (150), 35 ± 3
    (200), 55 ± 3 (300), 89 ± 6 (400), 172 ± 9 (500), 571 ± 26 (600). `<t_100>` (s): 44 ± 17,
    40 ± 10, 53 ± 16, 68 ± 14, 91 ± 20, 168 ± 26, 263 ± 37, 557 ± 96; N = 600 llega a `t_100`
    en 1 de 10 (sin punto; `F_u(1500 s)` = 0.997 ± 0.002). Mínimo en N = 50–100 (ρ ≈ 60–120
    m⁻²), indistinguible de N = 25 dentro de las barras; desde N = 150 crece monótono.
    Figuras generadas: `ej2/t90_vs_densidad.png`, `t100_vs_densidad.png`, `*_vs_n.png`,
    `fu_vs_t_densidad.png`. Pendiente: decidir N = 625/650/675.
- **Punto 2.2** (2026-10-14): `scripts/run_xo_sweep.sh` → `output/billiard/xo_sweep/N<N>/xo<x_o>/s<seed>/`.
  `x_o` = 0.0175 (r), 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.4925 (R − r);
  N = 100 y N = 20; semillas 1–5; red hexagonal (mismo método que 2.1b/2.4a), dt = 10⁻⁵ s,
  Velocity Verlet, `t_max = 100 s` con `--stop-at-t100`, estado cada 0.5 s. Determinismo
  verificado: N = 100, `x_o = r`, semillas 1, 3, 4, 5 dan `conversions.csv` idéntico al 2.4a.
  `analysis/plot_xo.py`: `<t_90>` ± desvío entre realizaciones (ddof = 1) vs `x_o` solo si
  llegan las 5 (mismo criterio que el 2.4a), las dos densidades en `ej2/t90_vs_xo.png`;
  `<F_u(t)>` ± desvío para `x_o` = r, 0.25, R − r en `ej2/fu_vs_t_xo_N<N>.png` (`--fu-xo` para
  cambiarlos). Lanzado 2026-10-14 13:50 con `JOBS=11` (en paralelo con la semilla 1 de
  N = 625/650/675 del 2.4a, que no mide tiempos).
  **Resultados (2026-10-14, 13:50–13:58, 110/110, todas llegan a `t_90` antes de 100 s)**,
  `<t_90>` (s) promedio ± desvío entre 5 realizaciones:
  - N = 100: 21 ± 2 (r), 19 ± 3 (0.05), 16.2 ± 0.8 (0.10), 14.5 ± 1.7 (0.15), 15.7 ± 1.5 (0.20),
    15 ± 2 (0.25), 16.5 ± 1.5 (0.30), 14.9 ± 1.6 (0.35), 18 ± 2 (0.40), 22 ± 2 (0.45),
    35 ± 4 (R − r). Meseta ~15 s en 0.10–0.35; peor en los dos extremos.
  - N = 20: 18 ± 2, 23 ± 9, 13 ± 4, 15 ± 4, 15 ± 4, 12 ± 2, 10.6 ± 2.4 (0.30), 14 ± 3, 15 ± 3,
    15 ± 2, 25 ± 7 (R − r). Más ruidoso; mínimo nominal en 0.25–0.30, indistinguible dentro
    de las barras de casi toda la meseta; también peor en los extremos.
  - Con 5 realizaciones no se puede elegir un único `x_o` óptimo dentro de la meseta.
  - Esquemas (2026-10-16, para Simulaciones): `analysis/plot_xo_scheme.py` →
    `ej2/esquema_xo.png` (una mesa por `x_o`, a escala, leída de las corridas; los tres `x_o` de
    `fu_vs_t_xo_N<N>.png` con sus colores, el resto gris; panel con R, r, `x_o`) y
    `ej2/esquema_densidad.png` (t = 0 de N = 100 y N = 20 en `x_o` = 0.25, semilla 1, con
    velocidades; 122 y 24 m⁻²).
- **2.4a, semilla 1 de N = 625/650/675 (2026-10-14, 13:39–14:48, hasta 1500 s)**: `F_u` a
  30 / 100 / 300 / 600 / 1000 / 1500 s: 625 → 0.09 / 0.22 / 0.45 / 0.70 / 0.83 / 0.94 (`t_90`
  = 1234 s, sin `t_100`); 650 → 0.02 / 0.03 / 0.04 / 0.06 / 0.09 / 0.11; 675 → 0.01 constante.
  (N = 600 semilla 1, comparación: `t_90` = 558 s, `F_u(1500)` = 1.00.)
  Mecanismo (animaciones 2026-10-14, `output/billiard/anim/`): `larga_N{600,650,675}_s1.mp4`
  (los estados cada 5 s de las corridas de 1500 s, 15 fps, ~20 s de video) y
  `corta_N{650,675}_s1.mp4` (re-corrida de 5 s guardando cada 0.01 s; reproduce las conversiones
  de la larga). N = 675: 9 conversiones, 8 en t ≈ 0 (sitios de la red pegados a los
  obstáculos) y la última en 1.2 s; esas 9 forman un anillo de usadas alrededor de los
  obstáculos que no se mueve en 1500 s: el sistema está atascado (sólido) y ninguna fresca
  llega a los obstáculos. N = 650: el anillo se reacomoda lentamente, las usadas se difunden
  hacia afuera (73 a 1500 s, repartidas por todo el círculo) y dejan entrar frescas.
  Semillas 2–10 de N = 625 (2026-10-14 15:18–17:02, `NS=625 SEEDS="2 … 10" JOBS=9
  ./scripts/run_t100_vs_n.sh`): **las 10 llegan a `t_90`**, `<t_90>` = 1270 ± 70 s; ninguna llega
  a `t_100` (`F_u(1500 s)` = 0.933 ± 0.010). N = 625 entra a `t90_vs_densidad.png`; 650 y 675
  (solo semilla 1) quedan fuera, informados con `F_u(1500 s)` = 0.11 y 0.01.
- **Punto 2.3** (2026-10-14): `scripts/run_speed_dist.sh` → `output/billiard/speed_dist/s<seed>/`
  (sin obstáculos, N = 100, red hexagonal, dt = 10⁻⁵ s, `t_f` = 20 s (re-corrido desde 10 s
  para confirmar el estacionario), estado cada 0.01 s, semillas 1–10; 157 MB).
  `analysis/plot_speed_dist.py` → `ej2/fv_evolucion.png`: f(v) = cuentas en el bin / (N Δv) por
  realización, promedio ± desvío entre las 10 (ddof = 1), un panel por instante, Δv = 0.05 m/s;
  y `ej2/rapidez_media_vs_t.png`: `<|v|>(t)` = (1/N) Σ_i |v_i| por realización, promedio ±
  desvío entre realizaciones, eje t log. Escalar elegido para marcar el estacionario a ojo:
  **rapidez media** (descartado `<v⁴>/<v²>²`, 2026-10-14). Cae de 1 a ~0.88 m/s hasta ~0.6–1 s
  y queda plana: promedio 0.880 (1–5 s), 0.880 (5–10), 0.881 (10–15), 0.881 (15–20), fluctuación
  instantánea ±0.015; MB 2D con `k_B T` = 0.0125 J predice 0.886. **Estacionario: t_est = 1 s**
  (marcado a ojo por el grupo, recta vertical punteada; 2026-10-14). Figuras finales:
  `rapidez_media_vs_t.png` (con la recta), `fv_evolucion.png` (f(v) a 0.05, 0.1, 0.2, 0.5 y
  1 s, cada una en ese instante, promedio ± desvío entre las 10 realizaciones, Δv = 0.1 m/s,
  superpuestas, leyenda "t (s)"; la curva "≥ 1" promediada sobre t ≥ 1 s se sacó el 2026-10-16:
  ese promedio queda solo en `fv_estacionaria_mb.png`), `fv_estacionaria_mb.png` (f(v)
  estacionaria con Δv = 0.05 m/s promediando todos los estados t ≥ 1 s de las 10 realizaciones;
  barra = desvío de los f instantáneos, criterio §8.3, por eso es grande: ~5 partículas por bin
  y estado) y `error_ajuste_mb.png` (E vs k_BT en mJ, recta en el mínimo). **Resultado**: k_BT
  ajustado = 12.41 mJ; m<v²>/2 estacionario = 12.32 mJ; m v0²/2 = 12.50 mJ (−0.7 % y −1.4 %).
  La diferencia de m<v²>/2 sería la energía guardada en los resortes de los contactos
  [inferencia: no se midió E_p en estas corridas]. El ajuste no tiene incerteza calculada.
- **Punto 2.4a** (2026-10-12): `scripts/run_t100_vs_n.sh` → `output/billiard/t100_vs_n/N<N>/s<seed>/`.
  Mismo sistema y semillas que el benchmark del TP4 (`x_o = r`, red hexagonal, dt = 10⁻⁵ s,
  Velocity Verlet), `--stop-at-t100` (corta en el primer paso con `F_u = 1`; `finalTime` en
  `run.json`, último estado en `dynamic.txt`), `t_max = 1500 s`, estado cada 5 s (~1 GB como
  máximo). En paralelo (nproc − 2), N grandes primero; nunca mientras mide el 2.1b.
  `analysis/plot_t100_vs_n.py`: `t_90` = tiempo de la conversión ⌈0.9 N⌉, `t_100` = de la N-ésima;
  `<t_90>`, `<t_100>` ± desvío entre realizaciones (ddof = 1) **solo para los N en que llegan las
  10** (decidido 2026-10-12; qué hacer con los incompletos se decide con los resultados); por
  stdout cuántas llegan y `F_u(t_final)` de las que no. Figuras `ej2/t90_vs_densidad.png`,
  `t100_vs_densidad.png` (densidad numérica `N/(πR²)`, m⁻², la de la presentación), las mismas
  vs N (`*_vs_n.png`, respaldo) y `fu_vs_t_densidad.png` (`<F_u(t)>` ± desvío, N = 25, 300, 600,
  675; el promedio de un N llega hasta el `t_final` más chico de sus corridas incompletas).
  Estimación previa (extrapolando `1 − F_u ∝ e^{−t/τ}` desde 30 s, optimista en las colas):
  `t_100` ~250 s (400), ~490 s (500), ~1400 s (600); N = 700 casi congelado (`φ = 0.82`, arriba
  de la solidificación de discos duros en 2D, φ ≈ 0.72): sin conversiones entre 20 y 30 s.
  Animaciones de los extremos (decidido): N = 600 como alto (N = 25 propuesto como bajo),
  re-corriendo una semilla ~20 s con estado fino.
- **Red hexagonal** (`--init hex`): fila `y = 0` en `x = (i + ½) a`, así con `x_o = r` cada
  obstáculo ocupa un sitio. Sitios: 716 (sin obstáculos), 714 (`x_o = r`), 708 (`x_o = 0.2`).
  Chequeo (2026-10-08, dt = 10⁻⁵, 3 s, `x_o = r`): `E_p(0) = 0` (sin superposición inicial);
  N = 300 `<|ΔE|>` 2.7·10⁻⁶, N = 700 6.9·10⁻⁶. A N = 700 la energía potencial es el 38 % de E
  (contactos casi permanentes; 5 % a N = 300). Lazo de 3·10⁵ pasos sin carga: 5.8 s (N = 300),
  8.2 s (N = 700).
  Esquema: `analysis/plot_hex_init.py <corrida>` → `ej2/red_hexagonal.png` (red completa, sitios
  elegidos, velocidades, ampliación en los obstáculos); reconstruye la red en Python y verifica
  que cada partícula de t = 0 cae en un sitio (distancia 0). Corrida de ejemplo:
  `output/billiard/hex_demo_N300_s1`. Consecuencia: las vecinas arrancan a 2r + ~10⁻¹¹ m (en
  contacto), así que las que ocupan los sitios pegados a un obstáculo pueden convertirse en el
  primer paso (2 de 300 en esa corrida).
- **Animación**: `analysis/animate_billiard.py` (un cuadro por estado guardado, `--stride` elige
  uno de cada k, `--zoom X Y HALF`, `--snapshot T` para el PNG del PDF). Partículas
  semitransparentes: la superposición se ve más oscura. Corridas de ejemplo en
  `output/billiard/anim/` (N = 300, `x_o = r`, seed 7, dt = 10⁻⁵): `panorama.mp4` (t_f = 20 s,
  estado cada 10⁻² s) y `lenta_zoom.mp4` (t_f = 0.3 s, estado cada 2·10⁻⁴ s, zoom 0.3 m × 0.3 m
  sobre los obstáculos). Mismo seed y dt: la lenta son los primeros 0.3 s de la misma trayectoria.
  Superposición máxima vista en la lenta: 5.1 mm (29 % de r).

### Convenciones del repo

- Motor en **Java**, módulo Maven propio dentro de este directorio, agregado a `<modules>` del
  `pom.xml` raíz; reutilizar `../common/` (`Particle`, `CliArgs`, IO estático/dinámico, CIM)
  donde encaje. El zip < 100 KB lleva solo el `src/` del motor (+ lo usado de `common`).
- Post-proceso en Python en `analysis/` (figuras en `analysis/figures/ej1/` y `ej2/`, según el
  sistema; `save_figure(fig, "ej1" | "ej2", nombre)`), scripts de barridos
  en `scripts/`, outputs crudos en `output/`.
- `exploracion/`: prototipos en Python para decidir antes de implementar (no van al zip ni a
  la presentación). `verlet_variantes.py` compara formas de inferir `v(t)` en Verlet original
  para el oscilador → `verlet_variantes_ecm.png` (ECM vs dt) y `verlet_variantes_cociente.png`
  (ECM relativo al despeje).
- Cada corrida escribe `static.txt` / `dynamic.txt` (formato de cátedra, `../AGENTS.md` §2.2,
  más el estado fresca/usada), los tiempos de conversión, y `run.json` con todos los inputs
  (integrador, `dt`, `dt₂`, seed, `t_f`, `x_o`, N) y tiempos del lazo.
- Guardado con contador entero de pasos (`paso % n == 0`), incluyendo `t = 0`.
