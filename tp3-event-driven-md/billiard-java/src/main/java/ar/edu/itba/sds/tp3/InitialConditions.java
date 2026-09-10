package ar.edu.itba.sds.tp3;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * A1: generación de la condición inicial. Se insertan partículas de a una, con posición uniforme
 * en el rectángulo interior {@code [r, L-r] × [r, W-r]} y dirección uniforme en [0, 2π), rechazando
 * las que se superponen con una partícula ya insertada o con un obstáculo (diapositiva 10).
 */
public final class InitialConditions {

    /** Intentos por partícula antes de declarar que la configuración no permite generar N. */
    private static final int MAX_ATTEMPTS = 100_000;

    private InitialConditions() {
    }

    public static List<Ball> generate(final SimulationConfig config, final Random random) {
        final List<Ball> balls = new ArrayList<>(config.n());
        final double r = config.radius();
        for (int id = 1; id <= config.n(); id++) {
            boolean placed = false;
            for (int attempt = 0; attempt < MAX_ATTEMPTS && !placed; attempt++) {
                final double x = r + random.nextDouble() * (config.l() - 2 * r);
                final double y = r + random.nextDouble() * (config.w() - 2 * r);
                if (fits(x, y, r, balls, config.obstacles())) {
                    final double theta = random.nextDouble() * 2 * Math.PI;
                    balls.add(new Ball(id, x, y, config.v0() * Math.cos(theta),
                            config.v0() * Math.sin(theta), r, config.mass()));
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
