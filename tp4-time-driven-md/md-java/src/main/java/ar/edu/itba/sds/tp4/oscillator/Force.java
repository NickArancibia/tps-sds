package ar.edu.itba.sds.tp4.oscillator;

/** Fuerza sobre una partícula en 1D, que puede depender de la posición y de la velocidad. */
public interface Force {

    double at(double position, double velocity);

    /**
     * Derivada temporal de la fuerza a lo largo de la trayectoria,
     * {@code df/dt = ∂f/∂r · v + ∂f/∂v · a}. La usa el arranque de Verlet original (término de
     * tercer orden de {@code r(-dt)}).
     */
    double rate(double position, double velocity, double acceleration);
}
