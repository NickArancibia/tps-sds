package ar.edu.itba.sds.common.model;

import java.util.Arrays;

/**
 * Resultado de una búsqueda de vecinos: para cada partícula, la lista de índices de sus vecinas.
 *
 * <p>Usa arrays primitivos que crecen por demanda en lugar de {@code List<List<Integer>>} para
 * evitar el boxing dentro del bucle cronometrado, que distorsionaría las mediciones de tiempo.</p>
 *
 * <p>Los índices son 0-based (posición en la lista de partículas). Para obtener el id 1-based que
 * va a los archivos, sumar 1 o consultar la partícula correspondiente.</p>
 *
 * <p>La instancia es reutilizable entre corridas mediante {@link #clear()}: eso permite repetir la
 * búsqueda muchas veces sin pagar el costo de alocar memoria en cada repetición.</p>
 */
public final class NeighborLists {

    private static final int INITIAL_CAPACITY = 8;

    private final int[][] data;
    private final int[] sizes;

    public NeighborLists(final int n) {
        this.data = new int[n][];
        this.sizes = new int[n];
    }

    /** Registra el par (i, j) en ambas direcciones: la relación de vecindad es simétrica. */
    public void addPair(final int i, final int j) {
        add(i, j);
        add(j, i);
    }

    private void add(final int i, final int j) {
        int[] row = data[i];
        if (row == null) {
            row = new int[INITIAL_CAPACITY];
            data[i] = row;
        } else if (sizes[i] == row.length) {
            row = Arrays.copyOf(row, row.length * 2);
            data[i] = row;
        }
        row[sizes[i]++] = j;
    }

    public int size() {
        return sizes.length;
    }

    public int neighborCount(final int i) {
        return sizes[i];
    }

    /** Devuelve los vecinos de {@code i} en un array del tamaño exacto (copia). */
    public int[] neighborsOf(final int i) {
        return data[i] == null ? new int[0] : Arrays.copyOf(data[i], sizes[i]);
    }

    /** Cantidad total de pares vecinos distintos. */
    public int totalPairs() {
        int total = 0;
        for (final int size : sizes) {
            total += size;
        }
        return total / 2;
    }

    /** Vacía las listas conservando la memoria ya alocada, para reutilizar la instancia. */
    public void clear() {
        Arrays.fill(sizes, 0);
    }

    /**
     * Compara dos resultados sin importar el orden en que se listan los vecinos.
     *
     * @return el índice de la primera partícula cuyos vecinos difieren, o -1 si son idénticos.
     */
    public int firstDifference(final NeighborLists other) {
        if (other.size() != size()) {
            return 0;
        }
        for (int i = 0; i < size(); i++) {
            final int[] mine = neighborsOf(i);
            final int[] theirs = other.neighborsOf(i);
            Arrays.sort(mine);
            Arrays.sort(theirs);
            if (!Arrays.equals(mine, theirs)) {
                return i;
            }
        }
        return -1;
    }
}
