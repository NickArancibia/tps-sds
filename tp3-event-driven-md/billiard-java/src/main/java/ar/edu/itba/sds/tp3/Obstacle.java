package ar.edu.itba.sds.tp3;

/**
 * Obstáculo circular fijo (masa infinita) con centro {@code (x, y)} y radio {@code radius}.
 * Mismo formato que el archivo de configuración de la competencia: una línea {@code x y R}.
 */
public record Obstacle(double x, double y, double radius) {

    public Obstacle {
        if (radius <= 0) {
            throw new IllegalArgumentException("El radio de un obstáculo debe ser positivo");
        }
    }

    public boolean overlaps(final Obstacle other) {
        final double dx = x - other.x;
        final double dy = y - other.y;
        final double sigma = radius + other.radius;
        return dx * dx + dy * dy < sigma * sigma;
    }
}
