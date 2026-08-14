package ar.edu.itba.sds.model;

/**
 * Parámetros de una corrida.
 *
 * @param n        cantidad de partículas
 * @param l        lado del área cuadrada de simulación
 * @param m        cantidad de celdas por lado de la grilla (la grilla es m x m)
 * @param rc       radio de interacción
 * @param periodic true si se usan condiciones periódicas de contorno
 * @param seed     semilla del generador aleatorio (reproducibilidad)
 * @param rMin     radio mínimo de partícula
 * @param rMax     radio máximo de partícula
 */
public record SystemConfig(int n, double l, int m, double rc, boolean periodic, long seed,
                           double rMin, double rMax) {

    public SystemConfig {
        if (n <= 0) {
            throw new IllegalArgumentException("N debe ser positivo, se recibió " + n);
        }
        if (l <= 0) {
            throw new IllegalArgumentException("L debe ser positivo, se recibió " + l);
        }
        if (m <= 0) {
            throw new IllegalArgumentException("M debe ser positivo, se recibió " + m);
        }
        if (rc < 0) {
            throw new IllegalArgumentException("rc no puede ser negativo, se recibió " + rc);
        }
        if (rMin < 0 || rMax < rMin) {
            throw new IllegalArgumentException("Rango de radios inválido: [" + rMin + ", " + rMax + "]");
        }
    }

    /** Densidad de partículas (N / L^2). */
    public double density() {
        return n / (l * l);
    }

    /**
     * Máximo M admisible por el método para este sistema.
     *
     * <p>Ver {@link ar.edu.itba.sds.common.neighbors.CellIndexMethod} para la justificación del criterio
     * {@code L/M > rc + 2*rMax}.</p>
     */
    public int maxM() {
        return (int) Math.floor(l / (rc + 2 * rMax));
    }
}
