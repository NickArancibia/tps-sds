package ar.edu.itba.sds.common.neighbors;

import ar.edu.itba.sds.common.model.NeighborLists;
import ar.edu.itba.sds.common.model.Particle;

import java.util.List;

/**
 * Cell Index Method: divide el área LxL en una grilla de MxM celdas y busca vecinos únicamente
 * entre partículas de celdas contiguas.
 *
 * <h2>Criterio sobre el tamaño de celda</h2>
 *
 * <p>Para partículas puntuales el método exige {@code L/M > rc}. Con partículas de radio no nulo
 * el criterio de vecindad es sobre la distancia borde a borde:</p>
 *
 * <pre>
 *     dist(centros) &lt; rc + r_i + r_j  &le;  rc + 2*rMax
 * </pre>
 *
 * <p>Es decir, el <b>borde</b> de una vecina puede caer en una celda contigua sin que lo haga su
 * <b>centro</b>. Para que alcance con revisar las celdas adyacentes, el criterio se corrige a:</p>
 *
 * <pre>
 *     L/M &gt; rc + 2*rMax        →        Mmax = floor(L / (rc + 2*rMax))
 * </pre>
 *
 * <p>Con L=20, rc=1 y rMax=0.26 queda {@code L/M > 1.52} y por lo tanto {@code Mmax = 13}. Pedir
 * un M mayor es un error: el método dejaría de encontrar vecinos legítimos.</p>
 *
 * <h2>Recorrido de celdas</h2>
 *
 * <p>Se recorre sólo la mitad de la vecindad de cada celda (derecha, arriba-derecha, arriba,
 * arriba-izquierda) más la celda propia, registrando cada par en ambas direcciones. La relación de
 * vecindad es simétrica, así que esto evita comparar cada par dos veces.</p>
 *
 * <p>Con condiciones periódicas y {@code M < 3} ese esquema colapsaría (una misma celda sería
 * vecina de otra por dos direcciones distintas y los pares se contarían dos veces), por lo que en
 * ese caso se recorren todos los pares directamente. El resultado es idéntico; sólo cambia el
 * costo, que para M=1 o M=2 es de por sí el de fuerza bruta.</p>
 */
public final class CellIndexMethod implements NeighborFinder {

    /** Mitad de la vecindad de una celda: derecha, arriba-derecha, arriba, arriba-izquierda. */
    private static final int[][] HALF_NEIGHBORHOOD = {{1, 0}, {1, 1}, {0, 1}, {-1, 1}};

    private final double l;
    private final int m;
    private final double rc;
    private final boolean periodic;
    private final double rMax;
    private final double cellSize;

    /** Cabeza de la lista enlazada de partículas de cada celda (-1 = celda vacía). */
    private final int[] head;
    /** Siguiente partícula dentro de la misma celda (-1 = fin de lista). Se realoca si crece N. */
    private int[] next;
    private NeighborLists result;

    public CellIndexMethod(final double l, final int m, final double rc, final boolean periodic,
                           final double rMax) {
        final double cell = l / m;
        final double minCellSize = rc + 2 * rMax;
        if (cell + 1e-12 < minCellSize) {
            final int maxM = (int) Math.floor(l / minCellSize);
            throw new IllegalArgumentException(String.format(java.util.Locale.US,
                    "M=%d es inválido para L=%.4f, rc=%.4f y rMax=%.4f: el lado de celda L/M=%.4f "
                            + "es menor que rc + 2*rMax = %.4f. El máximo M permitido es %d.",
                    m, l, rc, rMax, cell, minCellSize, maxM));
        }
        this.l = l;
        this.m = m;
        this.rc = rc;
        this.periodic = periodic;
        this.rMax = rMax;
        this.cellSize = cell;
        this.head = new int[m * m];
    }

    @Override
    public NeighborLists findNeighbors(final List<Particle> particles) {
        final int n = particles.size();
        if (next == null || next.length < n) {
            next = new int[n];
        }
        if (result == null || result.size() != n) {
            result = new NeighborLists(n);
        } else {
            result.clear();
        }

        // Copia a arrays primitivos: mejora la localidad de memoria del bucle caliente.
        final double[] x = new double[n];
        final double[] y = new double[n];
        final double[] r = new double[n];
        for (int i = 0; i < n; i++) {
            final Particle p = particles.get(i);
            x[i] = p.x();
            y[i] = p.y();
            r[i] = p.radius();
            if (r[i] > rMax + 1e-12) {
                throw new IllegalArgumentException(String.format(java.util.Locale.US,
                        "La partícula %d tiene radio %.4f, mayor que el rMax=%.4f declarado.",
                        p.id(), r[i], rMax));
            }
        }

        if (periodic && m < 3) {
            allPairs(n, x, y, r);
            return result;
        }

        fillGrid(n, x, y);

        for (int cy = 0; cy < m; cy++) {
            for (int cx = 0; cx < m; cx++) {
                final int cell = cy * m + cx;

                // Pares dentro de la propia celda.
                for (int i = head[cell]; i != -1; i = next[i]) {
                    for (int j = next[i]; j != -1; j = next[j]) {
                        checkPair(i, j, x, y, r);
                    }
                }

                // Pares contra la mitad de la vecindad.
                for (final int[] offset : HALF_NEIGHBORHOOD) {
                    int nx = cx + offset[0];
                    int ny = cy + offset[1];
                    if (periodic) {
                        nx = Math.floorMod(nx, m);
                        ny = Math.floorMod(ny, m);
                    } else if (nx < 0 || nx >= m || ny < 0 || ny >= m) {
                        continue;
                    }
                    final int neighborCell = ny * m + nx;
                    for (int i = head[cell]; i != -1; i = next[i]) {
                        for (int j = head[neighborCell]; j != -1; j = next[j]) {
                            checkPair(i, j, x, y, r);
                        }
                    }
                }
            }
        }
        return result;
    }

    /** Asigna cada partícula a su celda mediante listas enlazadas (sin alocar por celda). */
    private void fillGrid(final int n, final double[] x, final double[] y) {
        java.util.Arrays.fill(head, -1);
        for (int i = 0; i < n; i++) {
            final int cx = cellIndex(x[i]);
            final int cy = cellIndex(y[i]);
            final int cell = cy * m + cx;
            next[i] = head[cell];
            head[cell] = i;
        }
    }

    /** Índice de celda de una coordenada, acotado para tolerar errores de punto flotante. */
    private int cellIndex(final double coord) {
        final int index = (int) Math.floor(coord / cellSize);
        if (index < 0) {
            return periodic ? Math.floorMod(index, m) : 0;
        }
        if (index >= m) {
            return periodic ? Math.floorMod(index, m) : m - 1;
        }
        return index;
    }

    /** Camino equivalente para PBC con M &lt; 3, donde el recorrido por celdas se degenera. */
    private void allPairs(final int n, final double[] x, final double[] y, final double[] r) {
        for (int i = 0; i < n; i++) {
            for (int j = i + 1; j < n; j++) {
                checkPair(i, j, x, y, r);
            }
        }
    }

    private void checkPair(final int i, final int j, final double[] x, final double[] y,
                           final double[] r) {
        double dx = x[i] - x[j];
        double dy = y[i] - y[j];
        if (periodic) {
            dx -= l * Math.round(dx / l);
            dy -= l * Math.round(dy / l);
        }
        final double limit = rc + r[i] + r[j];
        if (dx * dx + dy * dy < limit * limit) {
            result.addPair(i, j);
        }
    }

    public int m() {
        return m;
    }

    public double cellSize() {
        return cellSize;
    }

    @Override
    public String name() {
        return "CIM(M=%d%s)".formatted(m, periodic ? ", PBC" : "");
    }
}
