package ar.edu.itba.sds.tp4.oscillator;

/**
 * Verlet original: {@code r(t+dt) = 2 r(t) - r(t-dt) + dt²/m f(t)}, con velocidad centrada
 * {@code v(t) = (r(t+dt) - r(t-dt)) / (2 dt)}.
 *
 * <p>Como {@code v(t)} recién se conoce después de calcular {@code r(t+dt)}, el integrador va un
 * paso adelantado: guarda {@code r(t+dt)} para poder informar {@code r(t)} y {@code v(t)} juntas.
 * La {@code v(t)} que pide {@code f(t)} se predice con Euler desde {@code v(t-dt)}, se avanza, y
 * se corrige con la velocidad centrada que da esa {@code r(t+dt)}. Arranque: {@code r(-dt)} por
 * Euler en {@code -dt}; en el primer paso {@code v(0)} es dato y no se predice.</p>
 */
public final class OriginalVerlet implements Integrator {

    private final Force force;
    private final double mass;
    private final double dt;
    private double previousPosition;
    private double position;
    private double nextPosition;
    private double velocity;

    public OriginalVerlet(final Force force, final double mass, final double dt,
                          final double position0, final double velocity0) {
        this.force = force;
        this.mass = mass;
        this.dt = dt;
        this.position = position0;
        this.velocity = velocity0;
        this.previousPosition = position0 - dt * velocity0
                + dt * dt / (2 * mass) * force.at(position0, velocity0);
        this.nextPosition = advance(velocity0);
    }

    @Override
    public void step() {
        final double velocityBack = velocity;           // v(t-dt), ya conocida
        final double accelerationBack = force.at(position, velocityBack) / mass;
        previousPosition = position;
        position = nextPosition;                        // ahora estamos en t
        final double predicted = velocityBack + accelerationBack * dt;
        final double corrected = (advance(predicted) - previousPosition) / (2 * dt);
        nextPosition = advance(corrected);
        velocity = (nextPosition - previousPosition) / (2 * dt);
    }

    /** {@code r(t+dt)} evaluando {@code f(t)} con la velocidad dada. */
    private double advance(final double velocityAtT) {
        return 2 * position - previousPosition + dt * dt / mass * force.at(position, velocityAtT);
    }

    @Override
    public double position() {
        return position;
    }

    @Override
    public double velocity() {
        return velocity;
    }
}
