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
 * {@code >= 2 r_max} alcanza con revisar las celdas contiguas. Se recorre la mitad de la vecindad
 * (derecha, arriba-derecha, arriba, arriba-izquierda) y cada par se registra en ambos agentes.</p>
 */
public final class Contacts {

    private static final int[][] HALF_NEIGHBORHOOD = {{1, 0}, {1, 1}, {0, 1}, {-1, 1}};

    private final Room room;
    private final double yMin;
    private final int mx;
    private final int my;
    /** Lado de las celdas en cada eje (ambos {@code >= 2 r_max}); cubren {@code [0, L] × [yMin, L]}. */
    private final double cellW;
    private final double cellH;
    private final int[] head;
    private final int[] next;

    public Contacts(final Room room, final CpmParams p, final int n) {
        this.room = room;
        // Afuera los agentes se retiran a exitDistance del centro de la puerta.
        this.yMin = -(room.exitDistance() + 2 * p.rMax());
        final double minCell = 2 * p.rMax();
        this.mx = Math.max(1, (int) Math.floor(room.l() / minCell));
        this.my = Math.max(1, (int) Math.floor((room.l() - yMin) / minCell));
        this.cellW = room.l() / mx;
        this.cellH = (room.l() - yMin) / my;
        this.head = new int[mx * my];
        this.next = new int[n];
    }

    /** Marca {@code contact[i]} y acumula {@code (ex, ey)} para todos los agentes activos. */
    public void compute(final Agents a) {
        final int[] active = a.active();
        final int count = a.activeCount();
        java.util.Arrays.fill(head, -1);
        for (int k = 0; k < count; k++) {
            final int i = active[k];
            a.contact[i] = false;
            a.ex[i] = 0;
            a.ey[i] = 0;
            final int c = cellX(a.x[i]) + mx * cellY(a.y[i]);
            next[i] = head[c];
            head[c] = i;
        }
        for (int cy = 0; cy < my; cy++) {
            for (int cx = 0; cx < mx; cx++) {
                final int c = cx + mx * cy;
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
        }
        for (int k = 0; k < count; k++) {
            walls(a, active[k]);
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

    private int cellX(final double x) {
        return Math.max(0, Math.min(mx - 1, (int) (x / cellW)));
    }

    private int cellY(final double y) {
        return Math.max(0, Math.min(my - 1, (int) ((y - yMin) / cellH)));
    }

    public int cellsX() {
        return mx;
    }

    public int cellsY() {
        return my;
    }
}
