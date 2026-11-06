package ar.edu.itba.sds.tp5.cpm;

/**
 * Velocidad más cercana a una dada que cumple un conjunto de restricciones lineales
 * {@code v·n_k ≥ c_k} con {@code c_k ≤ 0} (proyección sobre una intersección de semiplanos que
 * contiene a {@code v = 0}).
 *
 * <p>En 2D el óptimo es la velocidad original, su proyección sobre la recta de una restricción
 * violada o la intersección de dos rectas: se prueban todos los candidatos y se elige el factible
 * más cercano ({@code v = 0} siempre es factible). Con una sola restricción activa equivale a
 * recortar la componente normal y dejar la tangencial.</p>
 */
public final class VelocityProjection {

    /** Tolerancia de factibilidad (m/s). */
    private static final double EPS = 1e-12;

    private double[] nx = new double[16];
    private double[] ny = new double[16];
    private double[] c = new double[16];
    private int m;
    private double outX;
    private double outY;

    public void clear() {
        m = 0;
    }

    /** Agrega {@code v·(ux, uy) ≥ ck}, con {@code (ux, uy)} unitario y {@code ck ≤ 0}. */
    public void add(final double ux, final double uy, final double ck) {
        if (m == c.length) {
            nx = java.util.Arrays.copyOf(nx, 2 * m);
            ny = java.util.Arrays.copyOf(ny, 2 * m);
            c = java.util.Arrays.copyOf(c, 2 * m);
        }
        nx[m] = ux;
        ny[m] = uy;
        c[m] = ck;
        m++;
    }

    /**
     * Proyecta {@code (vx, vy)}; el resultado queda en {@link #vx()} y {@link #vy()}.
     *
     * @return {@code true} si la velocidad cambió
     */
    public boolean project(final double vx, final double vy) {
        outX = vx;
        outY = vy;
        if (feasible(vx, vy)) {
            return false;
        }
        double bestX = 0;
        double bestY = 0;
        double best = vx * vx + vy * vy;
        for (int k = 0; k < m; k++) {
            final double s = c[k] - (vx * nx[k] + vy * ny[k]);
            if (s <= 0) {
                continue; // no violada: proyectar sobre su recta no puede ser el óptimo
            }
            final double px = vx + s * nx[k];
            final double py = vy + s * ny[k];
            final double dist = s * s;
            if (dist < best && feasible(px, py)) {
                best = dist;
                bestX = px;
                bestY = py;
            }
        }
        for (int k = 0; k < m; k++) {
            for (int l = k + 1; l < m; l++) {
                final double det = nx[k] * ny[l] - ny[k] * nx[l];
                if (Math.abs(det) < 1e-12) {
                    continue;
                }
                final double px = (c[k] * ny[l] - ny[k] * c[l]) / det;
                final double py = (nx[k] * c[l] - c[k] * nx[l]) / det;
                final double dist = (px - vx) * (px - vx) + (py - vy) * (py - vy);
                if (dist < best && feasible(px, py)) {
                    best = dist;
                    bestX = px;
                    bestY = py;
                }
            }
        }
        outX = bestX;
        outY = bestY;
        return true;
    }

    public double vx() {
        return outX;
    }

    public double vy() {
        return outY;
    }

    private boolean feasible(final double vx, final double vy) {
        for (int k = 0; k < m; k++) {
            if (vx * nx[k] + vy * ny[k] < c[k] - EPS) {
                return false;
            }
        }
        return true;
    }
}
