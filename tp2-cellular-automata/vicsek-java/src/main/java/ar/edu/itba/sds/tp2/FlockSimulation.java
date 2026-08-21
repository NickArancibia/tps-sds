package ar.edu.itba.sds.tp2;

import ar.edu.itba.sds.common.model.NeighborLists;
import ar.edu.itba.sds.common.model.Particle;
import ar.edu.itba.sds.common.neighbors.CellIndexMethod;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * Motor de la simulación de bandadas (autómata off-lattice).
 *
 * <h2>Modelo</h2>
 *
 * <p>N partículas puntuales en una caja de lado L con condiciones periódicas de contorno, todas
 * con rapidez constante v. En cada paso, cada partícula i actualiza su dirección según los vecinos
 * a distancia (entre centros) menor que rc en el tiempo t:</p>
 *
 * <pre>
 *   Vicsek:  θ_i(t+Δt) = atan2( ⟨sin θ⟩_vecinos∪{i} , ⟨cos θ⟩_vecinos∪{i} ) + Δθ
 *   Votante: θ_i(t+Δt) = θ_j(t) + Δθ,   con j elegido al azar entre {i} ∪ vecinos
 * </pre>
 *
 * <p>donde Δθ ~ U[-η/2, η/2]. En ambos modelos, una partícula sin vecinos conserva su propia
 * dirección y se le suma el ruido (en el votante surge naturalmente: se copia a sí misma). La
 * actualización es <b>sincrónica</b>: todas las direcciones nuevas se calculan a partir del estado
 * en t y recién después se aplican.</p>
 *
 * <p>Las posiciones se actualizan con la dirección ya actualizada ("forward update", el estándar
 * actual del algoritmo de Vicsek):</p>
 *
 * <pre>
 *   x_i(t+Δt) = x_i(t) + v·cos(θ_i(t+Δt))·Δt      (mod L)
 * </pre>
 *
 * <h2>Búsqueda de vecinos</h2>
 *
 * <p>Se usa el Cell Index Method de la librería común con partículas de radio 0, de modo que el
 * criterio borde a borde se reduce a distancia entre centros &lt; rc. El tiempo de cada búsqueda se
 * registra para compararlo con el TP1 (punto g del enunciado).</p>
 */
public final class FlockSimulation {

    private final SimulationConfig config;
    private final Random random;
    private final CellIndexMethod cim;
    private final List<Particle> particles;
    private final double[] theta;
    private final double[] newTheta;

    /** Tiempos (ns) de cada llamada al CIM, para el estudio de performance del punto g. */
    private final List<Long> cimTimesNs = new ArrayList<>();

    /** Vecinos calculados con las posiciones del instante actual (se refresca en cada paso). */
    private NeighborLists neighbors;

    private int step = 0;

    public FlockSimulation(final SimulationConfig config) {
        this.config = config;
        this.random = new Random(config.seed());
        // Partículas puntuales (rMax = 0): el CIM exige L/M >= rc.
        this.cim = new CellIndexMethod(config.l(), config.m(), config.rc(), true, 0);
        this.theta = new double[config.n()];
        this.newTheta = new double[config.n()];
        this.particles = new ArrayList<>(config.n());

        // Estado inicial: posiciones uniformes en la caja y direcciones uniformes en [-π, π).
        // Al ser puntuales y sin interacción de volumen, el solapamiento no es un problema.
        for (int i = 0; i < config.n(); i++) {
            final double x = random.nextDouble() * config.l();
            final double y = random.nextDouble() * config.l();
            theta[i] = -Math.PI + random.nextDouble() * 2 * Math.PI;
            final Particle p = new Particle(i + 1, x, y, 0);
            p.setVelocity(config.speed() * Math.cos(theta[i]), config.speed() * Math.sin(theta[i]));
            particles.add(p);
        }
        refreshNeighbors();
    }

    /** Avanza el sistema un paso temporal (actualización sincrónica). */
    public void step() {
        computeNewDirections();

        // Aplicar direcciones y mover: recién acá se pisa el estado en t.
        for (int i = 0; i < config.n(); i++) {
            theta[i] = newTheta[i];
            final Particle p = particles.get(i);
            final double vx = config.speed() * Math.cos(theta[i]);
            final double vy = config.speed() * Math.sin(theta[i]);
            p.setVelocity(vx, vy);
            p.setPosition(wrap(p.x() + vx * config.dt()), wrap(p.y() + vy * config.dt()));
        }
        step++;
        refreshNeighbors();
    }

    private void computeNewDirections() {
        for (int i = 0; i < config.n(); i++) {
            final double noise = config.eta() * (random.nextDouble() - 0.5);
            final int[] around = neighbors.neighborsOf(i);
            final double base;
            if (config.model() == UpdateModel.VICSEK) {
                // Promedio de direcciones de vecinos incluyendo la propia.
                double sinSum = Math.sin(theta[i]);
                double cosSum = Math.cos(theta[i]);
                for (final int j : around) {
                    sinSum += Math.sin(theta[j]);
                    cosSum += Math.cos(theta[j]);
                }
                base = Math.atan2(sinSum, cosSum);
            } else {
                // Votante: copia la dirección de una partícula al azar entre sí misma y sus vecinos.
                final int pick = random.nextInt(around.length + 1);
                base = pick == around.length ? theta[i] : theta[around[pick]];
            }
            newTheta[i] = base + noise;
        }
    }

    private void refreshNeighbors() {
        final long start = System.nanoTime();
        neighbors = cim.findNeighbors(particles);
        cimTimesNs.add(System.nanoTime() - start);
    }

    private double wrap(final double coord) {
        final double l = config.l();
        final double wrapped = coord % l;
        return wrapped < 0 ? wrapped + l : wrapped;
    }

    // ------------------------------------------------------------------ observables

    /**
     * Polarización: v_a = |Σ v_i| / (N·v). Como todas las rapideces son iguales, equivale al módulo
     * del promedio de los versores de dirección.
     */
    public double polarization() {
        double sumSin = 0;
        double sumCos = 0;
        for (final double angle : theta) {
            sumSin += Math.sin(angle);
            sumCos += Math.cos(angle);
        }
        return Math.hypot(sumSin, sumCos) / config.n();
    }

    /** Fracción de partículas en el cluster más grande, sobre el grafo de vecinos actual. */
    public double largestClusterFraction() {
        return Clusters.largestClusterFraction(neighbors);
    }

    // ------------------------------------------------------------------ accessors

    public List<Particle> particles() {
        return particles;
    }

    public double time() {
        return step * config.dt();
    }

    public int currentStep() {
        return step;
    }

    public long[] cimTimesNs() {
        final long[] result = new long[cimTimesNs.size()];
        for (int i = 0; i < result.length; i++) {
            result[i] = cimTimesNs.get(i);
        }
        return result;
    }
}
