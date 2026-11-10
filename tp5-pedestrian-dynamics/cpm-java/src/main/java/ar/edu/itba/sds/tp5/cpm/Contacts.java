package ar.edu.itba.sds.tp5.cpm;

/**
 * Detección de contactos del CPM con el Cell Index Method (mismo criterio que el TP1), sobre los
 * arreglos de {@link Agents} porque el radio es variable.
 *
 * <p>Contacto entre agentes: {@code |x_i − x_j| < r_i + r_j}. Contacto con una pared:
 * {@code |x_i − p| < r_i}, con {@code p} el punto de la pared más cercano al centro. Por cada
 * contacto se suma el versor de escape {@code e_ij = (x_i − x_j)/|x_i − x_j|} (Ec. 7).</p>
 *
 * <p>La distancia de contacto es a lo sumo {@code 2 r_max}, así que con celdas de lado
 * {@code >= 2 r_max} ({@link CellGrid}) alcanza con revisar las celdas contiguas. Se recorre la
 * mitad de la vecindad (derecha, arriba-derecha, arriba, arriba-izquierda) y cada par se registra en
 * ambos agentes.</p>
 */
public final class Contacts {

    private static final int[][] HALF_NEIGHBORHOOD = {{1, 0}, {1, 1}, {0, 1}, {-1, 1}};

    private final Room room;
    private final CellGrid grid;
    private final int[] head;
    private final int[] next;
    /** Celdas con algún agente del último {@link #compute}, en orden creciente. */
    private final int[] occupied;
    private int occupiedCount;

    public Contacts(final Room room, final CpmParams p, final int n) {
        this.room = room;
        this.grid = new CellGrid(room, p);
        this.head = new int[grid.cells()];
        java.util.Arrays.fill(head, -1);
        this.next = new int[n];
        this.occupied = new int[n];
    }

    /**
     * Marca {@code contact[i]} y acumula {@code (ex, ey)} para los agentes {@code ids[0..count)}
     * (todos los activos en TSDMD puro, los que están en TSDMD en el híbrido). Solo se buscan
     * contactos entre ellos y con las paredes. Recorre solo las celdas ocupadas, en el mismo orden
     * que un barrido de toda la grilla: el costo no depende del tamaño de la habitación.
     */
    public void compute(final Agents a, final int[] ids, final int count) {
        final int mx = grid.mx;
        final int my = grid.my;
        for (int o = 0; o < occupiedCount; o++) {
            head[occupied[o]] = -1;
        }
        occupiedCount = 0;
        for (int k = 0; k < count; k++) {
            final int i = ids[k];
            a.contact[i] = false;
            a.ex[i] = 0;
            a.ey[i] = 0;
            final int c = grid.cellX(a.x[i]) + mx * grid.cellY(a.y[i]);
            if (head[c] < 0) {
                occupied[occupiedCount++] = c;
            }
            next[i] = head[c];
            head[c] = i;
        }
        java.util.Arrays.sort(occupied, 0, occupiedCount);
        for (int o = 0; o < occupiedCount; o++) {
            final int c = occupied[o];
            final int cx = c % mx;
            final int cy = c / mx;
            for (int i = head[c]; i >= 0; i = next[i]) {
                for (int j = next[i]; j >= 0; j = next[j]) {
                    pair(a, i, j);
                }
                for (final int[] off : HALF_NEIGHBORHOOD) {
                    final int nx = cx + off[0];
                    final int ny = cy + off[1];
                    if (nx < 0 || nx >= mx || ny >= my) {
                        continue;
                    }
                    for (int j = head[nx + mx * ny]; j >= 0; j = next[j]) {
                        pair(a, i, j);
                    }
                }
            }
        }
        for (int k = 0; k < count; k++) {
            walls(a, ids[k]);
        }
    }

    private void pair(final Agents a, final int i, final int j) {
        final double dx = a.x[i] - a.x[j];
        final double dy = a.y[i] - a.y[j];
        final double s = a.r[i] + a.r[j];
        final double d2 = dx * dx + dy * dy;
        if (d2 >= s * s) {
            return;
        }
        a.contact[i] = true;
        a.contact[j] = true;
        if (d2 > 0) {
            final double inv = 1 / Math.sqrt(d2);
            a.ex[i] += dx * inv;
            a.ey[i] += dy * inv;
            a.ex[j] -= dx * inv;
            a.ey[j] -= dy * inv;
        }
    }

    private void walls(final Agents a, final int i) {
        final double xi = a.x[i];
        final double yi = a.y[i];
        final double ri = a.r[i];
        for (int w = 0; w < room.wallCount(); w++) {
            final double[] s = room.wall(w);
            final double sx = s[2] - s[0];
            final double sy = s[3] - s[1];
            final double len2 = sx * sx + sy * sy;
            final double u = Math.max(0, Math.min(1, ((xi - s[0]) * sx + (yi - s[1]) * sy) / len2));
            final double dx = xi - (s[0] + u * sx);
            final double dy = yi - (s[1] + u * sy);
            final double d2 = dx * dx + dy * dy;
            if (d2 >= ri * ri) {
                continue;
            }
            a.contact[i] = true;
            if (d2 > 0) {
                final double inv = 1 / Math.sqrt(d2);
                a.ex[i] += dx * inv;
                a.ey[i] += dy * inv;
            }
        }
    }

    /**
     * Agentes activos {@code j ≠ i} con {@code |x_i − x_j| < radius}, usando las celdas armadas en el
     * último {@link #compute}: vale mientras no se muevan las posiciones. Requiere
     * {@code radius <= 2 r_max} (lado mínimo de celda), así alcanza con las 9 celdas alrededor.
     *
     * @param out arreglo de largo {@code >= N − 1} donde se escriben los índices
     * @return cantidad de vecinos escritos en {@code out}
     */
    public int neighbors(final Agents a, final int i, final double radius, final int[] out) {
        final double xi = a.x[i];
        final double yi = a.y[i];
        final double r2 = radius * radius;
        final int cx = grid.cellX(xi);
        final int cy = grid.cellY(yi);
        int count = 0;
        for (int ny = Math.max(0, cy - 1); ny <= Math.min(grid.my - 1, cy + 1); ny++) {
            for (int nx = Math.max(0, cx - 1); nx <= Math.min(grid.mx - 1, cx + 1); nx++) {
                for (int j = head[nx + grid.mx * ny]; j >= 0; j = next[j]) {
                    if (j == i) {
                        continue;
                    }
                    final double dx = xi - a.x[j];
                    final double dy = yi - a.y[j];
                    if (dx * dx + dy * dy < r2) {
                        out[count++] = j;
                    }
                }
            }
        }
        return count;
    }

    public CellGrid grid() {
        return grid;
    }
}
