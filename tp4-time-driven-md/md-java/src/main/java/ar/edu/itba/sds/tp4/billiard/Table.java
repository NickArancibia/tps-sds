package ar.edu.itba.sds.tp4.billiard;

/**
 * Parámetros fijos del billar circular: dominio de radio {@code bigR} centrado en el origen,
 * partículas de radio {@code r} y masa {@code m}, resorte normal {@code k} y obstáculos fijos de
 * radio {@code r} centrados en {@code (obstacleX[o], 0)} (vacío = sin obstáculos).
 */
public record Table(double bigR, double r, double m, double k, double[] obstacleX) {

    public Table {
        if (bigR <= 0 || r <= 0 || m <= 0 || k <= 0) {
            throw new IllegalArgumentException("R, r, m y k tienen que ser positivos");
        }
        if (2 * r >= bigR) {
            throw new IllegalArgumentException("El diámetro de las partículas no entra en el dominio");
        }
        for (final double x : obstacleX) {
            if (Math.abs(x) > bigR - r + 1e-12) {
                throw new IllegalArgumentException("Obstáculo en x = " + x + " fuera del dominio (|x| <= R - r)");
            }
        }
    }

    /** Dos obstáculos simétricos en {@code (±xo, 0)}, con {@code r <= xo <= R - r}. */
    public static Table withObstacles(final double bigR, final double r, final double m, final double k,
                                      final double xo) {
        if (xo < r - 1e-12 || xo > bigR - r + 1e-12) {
            throw new IllegalArgumentException("x_o = %s fuera de [r, R - r] = [%s, %s]".formatted(xo, r, bigR - r));
        }
        return new Table(bigR, r, m, k, new double[]{-xo, xo});
    }

    public static Table empty(final double bigR, final double r, final double m, final double k) {
        return new Table(bigR, r, m, k, new double[0]);
    }

    public boolean hasObstacles() {
        return obstacleX.length > 0;
    }
}
