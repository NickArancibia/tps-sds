package ar.edu.itba.sds.tp3;

/**
 * Colisión futura predicha suponiendo que todas las partículas siguen en MRU.
 *
 * <p>Guarda el contador de colisiones de las partículas involucradas en el momento de la
 * predicción: si al desencolarlo alguno cambió, la partícula chocó con otra cosa antes y el
 * evento ya no corresponde a una colisión física (invalidación "lazy").</p>
 *
 * @param time   instante absoluto de la colisión
 * @param type   tipo de colisión
 * @param a      índice (0-based) de la partícula
 * @param b      índice de la otra partícula ({@code PARTICLE}), del obstáculo ({@code OBSTACLE})
 *               o -1 (paredes)
 * @param countA colisiones de {@code a} al predecir
 * @param countB colisiones de {@code b} al predecir (solo {@code PARTICLE})
 */
public record Event(double time, Type type, int a, int b, int countA, int countB)
        implements Comparable<Event> {

    public enum Type {
        /** Choque entre dos partículas móviles. */
        PARTICLE,
        /** Choque de una partícula contra un obstáculo fijo. */
        OBSTACLE,
        /** Choque contra una pared vertical (x = 0 o x = L): acá se decide si hay gol. */
        WALL_X,
        /** Choque contra una pared horizontal (y = 0 o y = W). */
        WALL_Y
    }

    @Override
    public int compareTo(final Event other) {
        return Double.compare(time, other.time);
    }
}
