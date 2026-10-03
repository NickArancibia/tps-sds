package ar.edu.itba.sds.tp4.oscillator;

/**
 * Euler predictor-corrector (Teórica 4, diapositiva 23):
 * <pre>
 * predecir:  v_p = v(t) + a(t) dt,          r_p = r(t) + v(t) dt
 * evaluar:   a(t+dt) = f(r_p, v_p) / m
 * corregir:  v(t+dt) = v(t) + a(t+dt) dt,  r(t+dt) = r(t) + v(t+dt) dt
 * </pre>
 */
public final class EulerPredictorCorrector implements Integrator {

    private final Force force;
    private final double mass;
    private final double dt;
    private double position;
    private double velocity;

    public EulerPredictorCorrector(final Force force, final double mass, final double dt,
                                   final double position0, final double velocity0) {
        this.force = force;
        this.mass = mass;
        this.dt = dt;
        this.position = position0;
        this.velocity = velocity0;
    }

    @Override
    public void step() {
        final double acceleration = force.at(position, velocity) / mass;
        final double predictedVelocity = velocity + acceleration * dt;
        final double predictedPosition = position + velocity * dt;
        final double nextAcceleration = force.at(predictedPosition, predictedVelocity) / mass;
        velocity = velocity + nextAcceleration * dt;
        position = position + velocity * dt;
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
