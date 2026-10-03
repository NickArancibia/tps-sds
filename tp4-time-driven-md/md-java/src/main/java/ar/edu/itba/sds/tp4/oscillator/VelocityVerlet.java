package ar.edu.itba.sds.tp4.oscillator;

/**
 * Velocity Verlet: {@code r(t+dt) = r(t) + dt v(t) + dt²/(2m) f(t)} y
 * {@code v(t+dt) = v(t) + dt/(2m) (f(t) + f(t+dt))}.
 *
 * <p>{@code f(t+dt)} necesita {@code v(t+dt)}: se predice con Euler
 * {@code v(t) + f(t)/m dt}, se evalúa la fuerza y se corrige la velocidad. La fuerza que pasa al
 * paso siguiente se recalcula con la velocidad corregida.</p>
 */
public final class VelocityVerlet implements Integrator {

    private final Force force;
    private final double mass;
    private final double dt;
    private double position;
    private double velocity;
    private double currentForce;

    public VelocityVerlet(final Force force, final double mass, final double dt,
                          final double position0, final double velocity0) {
        this.force = force;
        this.mass = mass;
        this.dt = dt;
        this.position = position0;
        this.velocity = velocity0;
        this.currentForce = force.at(position0, velocity0);
    }

    @Override
    public void step() {
        final double nextPosition = position + dt * velocity + dt * dt / (2 * mass) * currentForce;
        final double predicted = velocity + currentForce / mass * dt;
        final double predictedForce = force.at(nextPosition, predicted);
        final double nextVelocity = velocity + dt / (2 * mass) * (currentForce + predictedForce);
        position = nextPosition;
        velocity = nextVelocity;
        currentForce = force.at(position, velocity);
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
