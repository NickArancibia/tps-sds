package ar.edu.itba.sds.tp3;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Random;

/**
 * A1: generación de la condición inicial, con dirección de la velocidad uniforme en [0, 2π).
 * <ul>
 *   <li>{@code random}: se insertan partículas de a una, con posición uniforme en el rectángulo
 *   interior {@code [r, L-r] × [r, W-r]}, rechazando las que se superponen con una partícula ya
 *   insertada o con un obstáculo (diapositiva 10). Se traba cerca de N ≈ 400 en la mesa del TP.</li>
 *   <li>{@code hex}: N sitios elegidos al azar de una red triangular de lado {@code 2r} centrada
 *   en el rectángulo interior (737 sitios en la mesa vacía del TP). La agregó el TP4 para llegar a
 *   N &gt; 600 en el benchmark de tiempo de ejecución.</li>
 * </ul>
 */
public final class InitialConditions {

    /** Intentos por partícula antes de declarar que la configuración no permite generar N. */
    private static final int MAX_ATTEMPTS = 100_000;
    /** Margen relativo sobre {@code 2r} en la red: los vecinos quedan separados pese al redondeo. */
    private static final double LATTICE_MARGIN = 1e-9;

    private InitialConditions() {
    }

    public static List<Ball> generate(final SimulationConfig config, final Random random) {
        return switch (config.init()) {
            case "random" -> randomInsertion(config, random);
            case "hex" -> hexagonal(config, random);
            default -> throw new IllegalArgumentException("--init desconocido: " + config.init());
        };
    }

    private static List<Ball> randomInsertion(final SimulationConfig config, final Random random) {
        final List<Ball> balls = new ArrayList<>(config.n());
        final double r = config.radius();
        for (int id = 1; id <= config.n(); id++) {
            boolean placed = false;
            for (int attempt = 0; attempt < MAX_ATTEMPTS && !placed; attempt++) {
                final double x = r + random.nextDouble() * (config.l() - 2 * r);
                final double y = r + random.nextDouble() * (config.w() - 2 * r);
                if (fits(x, y, r, balls, config.obstacles())) {
                    balls.add(newBall(id, x, y, config, random));
                    placed = true;
                }
            }
            if (!placed) {
                throw new IllegalStateException(
                        "No se pudo ubicar la partícula %d de %d sin solapamientos (fracción de área %.3f)"
                                .formatted(id, config.n(), config.areaFraction()));
            }
        }
        return balls;
    }

    /**
     * Red triangular de lado {@code a = 2r(1 + 1e-9)}, filas horizontales separadas
     * {@code a√3/2}, filas impares corridas {@code a/2}. La red se centra en el rectángulo interior
     * {@code [r, L-r] × [r, W-r]}; se descartan los sitios que se superponen con un obstáculo y se
     * eligen N al azar.
     */
    private static List<Ball> hexagonal(final SimulationConfig config, final Random random) {
        final double r = config.radius();
        final double a = 2 * r * (1 + LATTICE_MARGIN);
        final double rowHeight = a * Math.sqrt(3) / 2;
        final double innerL = config.l() - 2 * r;
        final double innerW = config.w() - 2 * r;
        final int rows = (int) Math.floor(innerW / rowHeight) + 1;
        final int cols = (int) Math.floor(innerL / a) + 1;
        final double x0 = r + (innerL - (cols - 1) * a) / 2;
        final double y0 = r + (innerW - (rows - 1) * rowHeight) / 2;
        final List<double[]> sites = new ArrayList<>();
        for (int j = 0; j < rows; j++) {
            final double y = y0 + j * rowHeight;
            final double shift = (j % 2 == 0) ? 0 : 0.5 * a;
            for (int i = 0; i < cols; i++) {
                final double x = x0 + shift + i * a;
                if (x <= config.l() - r && fits(x, y, r, List.of(), config.obstacles())) {
                    sites.add(new double[]{x, y});
                }
            }
        }
        if (sites.size() < config.n()) {
            throw new IllegalArgumentException("La red hexagonal tiene %d sitios libres; no entran %d partículas"
                    .formatted(sites.size(), config.n()));
        }
        Collections.shuffle(sites, random);
        final List<Ball> balls = new ArrayList<>(config.n());
        for (int id = 1; id <= config.n(); id++) {
            final double[] site = sites.get(id - 1);
            balls.add(newBall(id, site[0], site[1], config, random));
        }
        return balls;
    }

    private static Ball newBall(final int id, final double x, final double y, final SimulationConfig config,
                                final Random random) {
        final double theta = random.nextDouble() * 2 * Math.PI;
        return new Ball(id, x, y, config.v0() * Math.cos(theta), config.v0() * Math.sin(theta),
                config.radius(), config.mass());
    }

    private static boolean fits(final double x, final double y, final double r,
                                final List<Ball> balls, final List<Obstacle> obstacles) {
        for (final Ball b : balls) {
            if (overlap(x - b.x(), y - b.y(), r + b.radius())) {
                return false;
            }
        }
        for (final Obstacle o : obstacles) {
            if (overlap(x - o.x(), y - o.y(), r + o.radius())) {
                return false;
            }
        }
        return true;
    }

    private static boolean overlap(final double dx, final double dy, final double sigma) {
        return dx * dx + dy * dy <= sigma * sigma;
    }
}
