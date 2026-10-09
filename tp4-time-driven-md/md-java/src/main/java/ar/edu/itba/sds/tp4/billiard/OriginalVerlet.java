package ar.edu.itba.sds.tp4.billiard;

/**
 * Verlet original (Teórica 4), {@code r(t+dt) = 2 r(t) − r(t−dt) + a(t) dt²}, en forma sumada:
 * se acumula el desplazamiento {@code d(t) = r(t+dt) − r(t) = d(t−dt) + a(t) dt²}, lo que evita
 * restar posiciones casi iguales. La velocidad sale de la diferencia centrada
 * {@code v(t) = [r(t+dt) − r(t−dt)] / (2 dt) = [d(t−dt) + d(t)] / (2 dt)}, que recién se conoce
 * con {@code r(t+dt)}: el esquema va un paso adelantado para informar {@code r(t)} y {@code v(t)}
 * juntas.
 *
 * <p>Arranque: {@code r(−dt)} por Euler en {@code −dt}, {@code d(−dt) = v(0) dt − a(0) dt²/2}. En
 * la condición inicial no hay contactos ({@code a(0) = 0}), así que coincide con la exacta.</p>
 */
public final class OriginalVerlet implements Integrator {

    private final ContactForces forces;
    private final int n;
    private final double dt;
    private final double dtSq;
    private final double[] x;
    private final double[] y;
    private final double[] vx;
    private final double[] vy;
    /** {@code r(t+dt) − r(t)}. */
    private final double[] dx;
    private final double[] dy;
    private final double[] ax;
    private final double[] ay;

    public OriginalVerlet(final ContactForces forces, final double dt, final double[] x0, final double[] y0,
                          final double[] vx0, final double[] vy0) {
        this.forces = forces;
        this.n = x0.length;
        this.dt = dt;
        this.dtSq = dt * dt;
        this.x = x0.clone();
        this.y = y0.clone();
        this.vx = vx0.clone();
        this.vy = vy0.clone();
        this.dx = new double[n];
        this.dy = new double[n];
        this.ax = new double[n];
        this.ay = new double[n];
        forces.accelerations(0.0, x, y, ax, ay);
        for (int i = 0; i < n; i++) {
            dx[i] = vx0[i] * dt + 0.5 * ax[i] * dtSq;
            dy[i] = vy0[i] * dt + 0.5 * ay[i] * dtSq;
        }
    }

    @Override
    public void step(final double tNext) {
        for (int i = 0; i < n; i++) {
            x[i] += dx[i];
            y[i] += dy[i];
        }
        forces.accelerations(tNext, x, y, ax, ay);
        final double inv2dt = 0.5 / dt;
        for (int i = 0; i < n; i++) {
            final double dxNext = dx[i] + ax[i] * dtSq;
            final double dyNext = dy[i] + ay[i] * dtSq;
            vx[i] = (dx[i] + dxNext) * inv2dt;
            vy[i] = (dy[i] + dyNext) * inv2dt;
            dx[i] = dxNext;
            dy[i] = dyNext;
        }
    }

    @Override
    public double[] x() {
        return x;
    }

    @Override
    public double[] y() {
        return y;
    }

    @Override
    public double[] vx() {
        return vx;
    }

    @Override
    public double[] vy() {
        return vy;
    }
}
