package ar.edu.itba.sds.tp4.oscillator;

/** Oscilador amortiguado: {@code f = -k r - gamma v} (Teórica 4, diapositiva 37). */
public record DampedOscillator(double mass, double k, double gamma) implements Force {

    @Override
    public double at(final double position, final double velocity) {
        return -k * position - gamma * velocity;
    }

    @Override
    public double rate(final double position, final double velocity, final double acceleration) {
        return -k * velocity - gamma * acceleration;
    }
}
