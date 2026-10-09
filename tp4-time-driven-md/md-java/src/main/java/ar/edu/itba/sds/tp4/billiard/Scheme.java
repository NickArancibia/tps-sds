package ar.edu.itba.sds.tp4.billiard;

import java.util.Arrays;
import java.util.stream.Collectors;

/** Variantes del esquema de Verlet disponibles para el billar, con su nombre en la CLI. */
public enum Scheme {
    VERLET("verlet", OriginalVerlet::new),
    VELOCITY_VERLET("velocity-verlet", VelocityVerlet::new);

    @FunctionalInterface
    private interface Factory {
        Integrator create(ContactForces forces, double dt, double[] x0, double[] y0, double[] vx0, double[] vy0);
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

    public Integrator create(final ContactForces forces, final double dt, final double[] x0, final double[] y0,
                             final double[] vx0, final double[] vy0) {
        return factory.create(forces, dt, x0, y0, vx0, vy0);
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
