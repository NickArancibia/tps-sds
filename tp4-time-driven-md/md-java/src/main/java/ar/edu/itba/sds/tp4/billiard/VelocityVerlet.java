package ar.edu.itba.sds.tp4.billiard;

/**
 * Velocity Verlet (Teórica 4): la fuerza depende solo de las posiciones, así que es explícito.
 * <pre>
 * r(t+dt) = r(t) + v(t) dt + a(t) dt²/2
 * v(t+dt) = v(t) + [a(t) + a(t+dt)] dt/2
 * </pre>
 */
public final class VelocityVerlet implements Integrator {

    private final ContactForces forces;
    private final int n;
    private final double dt;
    private final double[] x;
    private final double[] y;
    private final double[] vx;
    private final double[] vy;
    private final double[] ax;
    private final double[] ay;

    public VelocityVerlet(final ContactForces forces, final double dt, final double[] x0, final double[] y0,
                          final double[] vx0, final double[] vy0) {
        this.forces = forces;
        this.n = x0.length;
        this.dt = dt;
        this.x = x0.clone();
        this.y = y0.clone();
        this.vx = vx0.clone();
        this.vy = vy0.clone();
        this.ax = new double[n];
        this.ay = new double[n];
        forces.accelerations(0.0, x, y, ax, ay);
    }

    @Override
    public void step(final double tNext) {
        final double half = 0.5 * dt;
        for (int i = 0; i < n; i++) {
            vx[i] += half * ax[i];
            vy[i] += half * ay[i];
            x[i] += dt * vx[i];
            y[i] += dt * vy[i];
        }
        forces.accelerations(tNext, x, y, ax, ay);
        for (int i = 0; i < n; i++) {
            vx[i] += half * ax[i];
            vy[i] += half * ay[i];
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
