package ar.edu.itba.sds.tp4.oscillator;

import java.util.Arrays;
import java.util.stream.Collectors;

/** Esquemas de integración disponibles para el oscilador, con su nombre en la CLI. */
public enum Scheme {
    BEEMAN("beeman", Beeman::new),
    VERLET("verlet", OriginalVerlet::new),
    VELOCITY_VERLET("velocity-verlet", VelocityVerlet::new),
    EULER_PC("euler-pc", EulerPredictorCorrector::new);

    @FunctionalInterface
    private interface Factory {
        Integrator create(Force force, double mass, double dt, double position0, double velocity0);
    }

    private final String cliName;
    private final Factory factory;

    Scheme(final String cliName, final Factory factory) {
        this.cliName = cliName;
        this.factory = factory;
    }

    public String cliName() {
        return cliName;
    }

    public Integrator create(final Force force, final double mass, final double dt,
                             final double position0, final double velocity0) {
        return factory.create(force, mass, dt, position0, velocity0);
    }

    public static Scheme fromCli(final String name) {
        for (final Scheme scheme : values()) {
            if (scheme.cliName.equals(name)) {
                return scheme;
            }
        }
        throw new IllegalArgumentException("Esquema desconocido: " + name + " (opciones: " + names() + ")");
    }

    public static String names() {
        return Arrays.stream(values()).map(Scheme::cliName).collect(Collectors.joining(", "));
    }
}
