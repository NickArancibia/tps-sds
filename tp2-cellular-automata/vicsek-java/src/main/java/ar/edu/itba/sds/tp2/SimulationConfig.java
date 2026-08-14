package ar.edu.itba.sds.tp2;

/**
 * Parámetros de una simulación de bandadas.
 *
 * <p>El sistema es una caja cuadrada de lado {@code l} con condiciones periódicas de contorno
 * (siempre: el enunciado no contempla el caso sin PBC). Las partículas son puntuales
 * (radio 0) y se mueven todas con la misma rapidez {@code speed}.</p>
 *
 * @param model       regla de actualización de direcciones (Vicsek estándar o votante)
 * @param n           cantidad de partículas
 * @param l           lado de la caja
 * @param rc          radio de interacción (distancia entre centros)
 * @param eta         amplitud del ruido: Δθ ~ U[-eta/2, eta/2]
 * @param speed       módulo de la velocidad de las partículas
 * @param dt          paso temporal
 * @param steps       cantidad de pasos a simular
 * @param seed        semilla del generador aleatorio
 * @param m           celdas por lado de la grilla del CIM
 * @param outputEvery cada cuántos pasos se guarda un bloque en el archivo dinámico
 */
public record SimulationConfig(UpdateModel model, int n, double l, double rc, double eta,
                               double speed, double dt, int steps, long seed, int m,
                               int outputEvery) {

    public SimulationConfig {
        if (n <= 0) {
            throw new IllegalArgumentException("N debe ser positivo, se recibió " + n);
        }
        if (l <= 0 || rc <= 0) {
            throw new IllegalArgumentException("L y rc deben ser positivos");
        }
        if (eta < 0) {
            throw new IllegalArgumentException("eta no puede ser negativo, se recibió " + eta);
        }
        if (speed < 0 || dt <= 0) {
            throw new IllegalArgumentException("v debe ser >= 0 y dt > 0");
        }
        if (steps <= 0 || outputEvery <= 0) {
            throw new IllegalArgumentException("steps y outputEvery deben ser positivos");
        }
        if (m <= 0) {
            throw new IllegalArgumentException("M debe ser positivo, se recibió " + m);
        }
    }

    /** Densidad de partículas rho = N / L^2. */
    public double density() {
        return n / (l * l);
    }

    /** Máximo M admisible por el CIM con partículas puntuales: L/M >= rc. */
    public static int maxM(final double l, final double rc) {
        return Math.max(1, (int) Math.floor(l / rc));
    }
}
