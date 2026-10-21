package ar.edu.itba.sds.tp4.oscillator;

/**
 * Verlet original: {@code r(t+dt) = 2 r(t) - r(t-dt) + dt²/m f(t)}, con velocidad centrada
 * {@code v(t) = (r(t+dt) - r(t-dt)) / (2 dt)}.
 *
 * <p>Como {@code v(t)} recién se conoce después de calcular {@code r(t+dt)}, el integrador va un
 * paso adelantado: guarda {@code r(t+dt)} para poder informar {@code r(t)} y {@code v(t)} juntas.
 * La {@code v(t)} que pide {@code f(t)} se predice con Euler desde {@code v(t-dt)}, se avanza, y
 * se corrige con la velocidad centrada que da esa {@code r(t+dt)}. En el primer paso {@code v(0)}
 * es dato y no se predice.</p>
 *
 * <p>Se implementa en la forma sumada, algebraicamente idéntica: en lugar de recalcular
 * {@code 2 r(t) - r(t-dt)} se acumula el desplazamiento {@code d(t) = r(t) - r(t-dt)},
 * {@code d(t+dt) = d(t) + dt²/m f(t)}, {@code r(t+dt) = r(t) + d(t+dt)}, y la velocidad centrada es
 * {@code (d(t+dt) + d(t)) / (2 dt)}. En la forma directa el redondeo de {@code r} (~10⁻¹⁶ m) entra
 * en cada paso al desplazamiento como un error de velocidad ~10⁻¹⁶/dt, y el ECM del oscilador
 * se aplanaba en ~10⁻¹⁹ m² para dt ≤ 2·10⁻⁶ s.</p>
 *
 * <p>Arranque: {@code r(-dt)} por Euler en {@code -dt} (Teórica 4),
 * {@code r(0) - dt v(0) + dt²/2 a(0)}, es decir {@code d(0) = dt v(0) - dt²/2 a(0)}.</p>
 */
public final class OriginalVerlet implements Integrator {

    private final Force force;
    private final double mass;
    private final double dt;
    private double position;
    private double velocity;
    /** {@code r(t) - r(t-dt)}. */
    private double displacement;
    /** {@code r(t+dt) - r(t)}. */
    private double nextDisplacement;

    public OriginalVerlet(final Force force, final double mass, final double dt,
                          final double position0, final double velocity0) {
        this.force = force;
        this.mass = mass;
        this.dt = dt;
        this.position = position0;
        this.velocity = velocity0;
        final double acceleration0 = force.at(position0, velocity0) / mass;
        this.displacement = dt * velocity0 - dt * dt / 2 * acceleration0;
        this.nextDisplacement = advance(velocity0);
    }

    @Override
    public void step() {
        final double velocityBack = velocity;           // v(t-dt), ya conocida
        final double accelerationBack = force.at(position, velocityBack) / mass;
        position += nextDisplacement;                   // ahora estamos en t
        displacement = nextDisplacement;
        final double predicted = velocityBack + accelerationBack * dt;
        final double corrected = (advance(predicted) + displacement) / (2 * dt);
        nextDisplacement = advance(corrected);
        velocity = (nextDisplacement + displacement) / (2 * dt);
    }

    /** {@code r(t+dt) - r(t)} evaluando {@code f(t)} con la velocidad dada. */
    private double advance(final double velocityAtT) {
        return displacement + dt * dt / mass * force.at(position, velocityAtT);
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
