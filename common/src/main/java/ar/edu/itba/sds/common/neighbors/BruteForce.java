package ar.edu.itba.sds.common.neighbors;

import ar.edu.itba.sds.common.model.NeighborLists;
import ar.edu.itba.sds.common.model.Particle;

import java.util.List;

/**
 * Búsqueda de vecinos comparando todos contra todos: O(N^2).
 *
 * <p>Existe como <b>baseline de validación</b>: el CIM debe devolver exactamente el mismo conjunto
 * de vecinos que esta implementación, con y sin condiciones periódicas. Cualquier cambio en el CIM
 * tiene que seguir pasando esa comparación (ver {@code --verify} en la CLI).</p>
 */
public final class BruteForce implements NeighborFinder {

    private final double l;
    private final double rc;
    private final boolean periodic;
    private NeighborLists result;

    public BruteForce(final double l, final double rc, final boolean periodic) {
        this.l = l;
        this.rc = rc;
        this.periodic = periodic;
    }

    @Override
    public NeighborLists findNeighbors(final List<Particle> particles) {
        final int n = particles.size();
        if (result == null || result.size() != n) {
            result = new NeighborLists(n);
        } else {
            result.clear();
        }

        final double[] x = new double[n];
        final double[] y = new double[n];
        final double[] r = new double[n];
        for (int i = 0; i < n; i++) {
            final Particle p = particles.get(i);
            x[i] = p.x();
            y[i] = p.y();
            r[i] = p.radius();
        }

        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                double dx = x[i] - x[j];
                double dy = y[i] - y[j];
                if (periodic) {
                    dx -= l * Math.round(dx / l);
                    dy -= l * Math.round(dy / l);
                }
                final double limit = rc + r[i] + r[j];
                if (dx * dx + dy * dy < limit * limit) {
                    result.addPair(i, j);
                }
            }
        }
        return result;
    }

    @Override
    public String name() {
        return "BruteForce%s".formatted(periodic ? "(PBC)" : "");
    }
}
