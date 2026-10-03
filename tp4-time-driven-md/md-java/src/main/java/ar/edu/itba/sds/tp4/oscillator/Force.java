package ar.edu.itba.sds.tp4.oscillator;

/** Fuerza sobre una partícula en 1D, que puede depender de la posición y de la velocidad. */
@FunctionalInterface
public interface Force {

    double at(double position, double velocity);
}
