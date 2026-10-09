package ar.edu.itba.sds.tp4.billiard;

/**
 * Esquema de integración del billar. Después de construirlo y después de cada {@link #step()},
 * {@link #x()}, {@link #y()}, {@link #vx()}, {@link #vy()} tienen posiciones y velocidades en el
 * mismo instante {@code t = pasos · dt}. Los arreglos son el estado interno: solo lectura.
 */
public interface Integrator {

    /** Avanza el estado de {@code t} a {@code t + dt}; {@code tNext = t + dt}. */
    void step(double tNext);

    double[] x();

    double[] y();

    double[] vx();

    double[] vy();
}
