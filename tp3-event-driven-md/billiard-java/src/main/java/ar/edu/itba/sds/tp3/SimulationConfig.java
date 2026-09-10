package ar.edu.itba.sds.tp3;

import java.util.List;

/**
 * Parámetros de una simulación del billar-metegol.
 *
 * @param n          cantidad de partículas móviles
 * @param l          largo de la mesa (paredes cortas en x = 0 y x = L)
 * @param w          ancho de la mesa (paredes largas en y = 0 y y = W)
 * @param d          longitud del arco, centrado en cada pared corta: |y - W/2| ≤ d/2
 * @param radius     radio de las partículas
 * @param mass       masa de las partículas
 * @param v0         módulo de la velocidad inicial (dirección uniforme en [0, 2π))
 * @param tf         tiempo simulado máximo
 * @param seed       semilla del generador aleatorio
 * @param every      escribir el estado en dynamic.txt cada tantos eventos (0 = no escribir)
 * @param stopAtT90  cortar la corrida apenas F_g ≥ 0.9
 * @param obstacles  obstáculos fijos (vacío = mesa vacía)
 */
public record SimulationConfig(int n, double l, double w, double d, double radius, double mass,
                               double v0, double tf, long seed, int every, boolean stopAtT90,
                               List<Obstacle> obstacles) {

    public SimulationConfig {
        if (n <= 0) {
            throw new IllegalArgumentException("N debe ser positivo, se recibió " + n);
        }
        if (l <= 0 || w <= 0) {
            throw new IllegalArgumentException("L y W deben ser positivos");
        }
        if (d <= 0 || d > w) {
            throw new IllegalArgumentException("d debe estar en (0, W]");
        }
        if (radius <= 0 || mass <= 0 || v0 <= 0) {
            throw new IllegalArgumentException("r, m y v0 deben ser positivos");
        }
        if (2 * radius >= l || 2 * radius >= w) {
            throw new IllegalArgumentException("Las partículas no entran en la mesa");
        }
        if (tf <= 0) {
            throw new IllegalArgumentException("tf debe ser positivo");
        }
        if (every < 0) {
            throw new IllegalArgumentException("every no puede ser negativo");
        }
        obstacles = List.copyOf(obstacles);
        validateObstacles(obstacles, l, w, radius);
    }

    /** Restricciones (i) y (ii) del punto 1.2 (menos la de "permitir generar N partículas"). */
    private static void validateObstacles(final List<Obstacle> obstacles, final double l,
                                          final double w, final double radius) {
        for (int k = 0; k < obstacles.size(); k++) {
            final Obstacle o = obstacles.get(k);
            if (o.radius() < radius) {
                throw new IllegalArgumentException(
                        "Obstáculo %d: R = %s < r = %s".formatted(k + 1, o.radius(), radius));
            }
            if (o.x() - o.radius() < 0 || o.x() + o.radius() > l
                    || o.y() - o.radius() < 0 || o.y() + o.radius() > w) {
                throw new IllegalArgumentException(
                        "Obstáculo %d no está íntegramente dentro del dominio".formatted(k + 1));
            }
            for (int m = 0; m < k; m++) {
                if (o.overlaps(obstacles.get(m))) {
                    throw new IllegalArgumentException(
                            "Los obstáculos %d y %d se solapan".formatted(m + 1, k + 1));
                }
            }
        }
    }

    /** Cantidad de goles a partir de la cual F_g = N_g / N ≥ 0.9. */
    public int goalsForT90() {
        return (int) Math.ceil(0.9 * n - 1e-9);
    }

    /** Fracción del área de la mesa ocupada por partículas y obstáculos. */
    public double areaFraction() {
        double occupied = n * Math.PI * radius * radius;
        for (final Obstacle o : obstacles) {
            occupied += Math.PI * o.radius() * o.radius();
        }
        return occupied / (l * w);
    }
}
