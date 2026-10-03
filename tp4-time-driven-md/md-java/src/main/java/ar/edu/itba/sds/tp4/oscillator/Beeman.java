package ar.edu.itba.sds.tp4.oscillator;

/**
 * Beeman en su variante predictor-corrector para fuerzas que dependen de la velocidad (Teórica 4,
 * diapositiva 20):
 * <pre>
 * r(t+dt)   = r(t) + v(t) dt + 2/3 a(t) dt² - 1/6 a(t-dt) dt²
 * v_p(t+dt) = v(t) + 3/2 a(t) dt - 1/2 a(t-dt) dt
 * a(t+dt)   = f(r(t+dt), v_p(t+dt)) / m
 * v(t+dt)   = v(t) + 1/3 a(t+dt) dt + 5/6 a(t) dt - 1/6 a(t-dt) dt
 * </pre>
 * La aceleración que pasa al paso siguiente se recalcula con la velocidad corregida (mismo
 * criterio que Velocity Verlet). Arranque: {@code a(-dt)} evaluada en {@code r(-dt), v(-dt)}
 * estimadas con Euler en {@code -dt}.
 */
public final class Beeman implements Integrator {

    private final Force force;
    private final double mass;
    private final double dt;
    private double position;
    private double velocity;
    private double acceleration;
    private double previousAcceleration;

    public Beeman(final Force force, final double mass, final double dt,
                  final double position0, final double velocity0) {
        this.force = force;
        this.mass = mass;
        this.dt = dt;
        this.position = position0;
        this.velocity = velocity0;
        this.acceleration = force.at(position0, velocity0) / mass;
        final double positionBack = position0 - dt * velocity0 + dt * dt / 2 * acceleration;
        final double velocityBack = velocity0 - dt * acceleration;
        this.previousAcceleration = force.at(positionBack, velocityBack) / mass;
    }

    @Override
    public void step() {
        final double nextPosition = position + velocity * dt
                + (2.0 / 3.0 * acceleration - 1.0 / 6.0 * previousAcceleration) * dt * dt;
        final double predicted = velocity + (1.5 * acceleration - 0.5 * previousAcceleration) * dt;
        final double nextAcceleration = force.at(nextPosition, predicted) / mass;
        final double nextVelocity = velocity + (1.0 / 3.0 * nextAcceleration
                + 5.0 / 6.0 * acceleration - 1.0 / 6.0 * previousAcceleration) * dt;
        previousAcceleration = acceleration;
        position = nextPosition;
        velocity = nextVelocity;
        acceleration = force.at(position, velocity) / mass;
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
