package ar.edu.itba.sds.tp4.billiard;

import java.util.Arrays;

/**
 * Aceleraciones por contacto (resorte lineal normal, {@code F_i = Σ_j −k ξ_ij ê_ij}) contra otras
 * partículas, los obstáculos fijos y la partícula imagen de la pared. También registra la
 * conversión fresca → usada en el paso en que una partícula toca un obstáculo por primera vez.
 *
 * <p>Búsqueda de pares con una grilla de celdas sobre {@code [−R, R]²} de lado {@code ≥ 2r} (el
 * alcance del contacto entre centros), sin periodicidad: cada par se revisa una vez recorriendo
 * la celda propia y la mitad de la vecindad (derecha, arriba-derecha, arriba, arriba-izquierda),
 * como el CIM de {@code common}. Se reimplementa acá sobre arreglos primitivos y sumando la fuerza
 * en el mismo recorrido para no alocar ni armar listas de vecinos en cada paso.</p>
 */
public final class ContactForces {

    private final Table table;
    private final int n;
    private final double contact;
    private final double contactSq;
    private final double wallStart;
    private final double kOverM;

    private final int cells;
    private final double cellSize;
    private final int[] head;
    private final int[] next;

    private final boolean[] used;
    private final double[] conversionTime;
    private final int[] conversionId;
    private int conversions;

    public ContactForces(final Table table, final int n) {
        this.table = table;
        this.n = n;
        this.contact = 2 * table.r();
        this.contactSq = contact * contact;
        this.wallStart = table.bigR() - table.r();
        this.kOverM = table.k() / table.m();
        this.cells = Math.max(1, (int) Math.floor(2 * table.bigR() / contact));
        this.cellSize = 2 * table.bigR() / cells;
        this.head = new int[cells * cells];
        this.next = new int[n];
        this.used = new boolean[n];
        this.conversionTime = new double[n];
        this.conversionId = new int[n];
    }

    /**
     * Escribe en {@code ax, ay} la aceleración de cada partícula en las posiciones {@code x, y},
     * correspondientes al instante {@code t} (que solo se usa para registrar conversiones).
     */
    public void accelerations(final double t, final double[] x, final double[] y,
                              final double[] ax, final double[] ay) {
        Arrays.fill(ax, 0, n, 0.0);
        Arrays.fill(ay, 0, n, 0.0);
        fillGrid(x, y);
        for (int cy = 0; cy < cells; cy++) {
            for (int cx = 0; cx < cells; cx++) {
                final int cell = cy * cells + cx;
                for (int i = head[cell]; i != -1; i = next[i]) {
                    for (int j = next[i]; j != -1; j = next[j]) {
                        pair(i, j, x, y, ax, ay);
                    }
                }
                neighborCell(cell, cx + 1, cy, x, y, ax, ay);
                neighborCell(cell, cx + 1, cy + 1, x, y, ax, ay);
                neighborCell(cell, cx, cy + 1, x, y, ax, ay);
                neighborCell(cell, cx - 1, cy + 1, x, y, ax, ay);
            }
        }
        for (int i = 0; i < n; i++) {
            wall(i, x, y, ax, ay);
            for (final double ox : table.obstacleX()) {
                obstacle(t, i, ox, x, y, ax, ay);
            }
        }
    }

    private void neighborCell(final int cell, final int nx, final int ny, final double[] x, final double[] y,
                              final double[] ax, final double[] ay) {
        if (nx < 0 || nx >= cells || ny >= cells) {
            return;
        }
        final int other = ny * cells + nx;
        for (int i = head[cell]; i != -1; i = next[i]) {
            for (int j = head[other]; j != -1; j = next[j]) {
                pair(i, j, x, y, ax, ay);
            }
        }
    }

    /** Par i–j: {@code F_i = −k ξ ê_ij}, {@code F_j = −F_i}. */
    private void pair(final int i, final int j, final double[] x, final double[] y,
                      final double[] ax, final double[] ay) {
        final double dx = x[j] - x[i];
        final double dy = y[j] - y[i];
        final double distSq = dx * dx + dy * dy;
        if (distSq >= contactSq) {
            return;
        }
        final double dist = Math.sqrt(distSq);
        final double scale = kOverM * (contact - dist) / dist;
        final double fx = scale * dx;
        final double fy = scale * dy;
        ax[i] -= fx;
        ay[i] -= fy;
        ax[j] += fx;
        ay[j] += fy;
    }

    /**
     * Pared: imagen fija de radio r en {@code (R + r) n̂}, {@code ξ = |r_i| + r − R}. La fuerza
     * {@code −k ξ n̂} apunta hacia el centro.
     */
    private void wall(final int i, final double[] x, final double[] y, final double[] ax, final double[] ay) {
        final double distSq = x[i] * x[i] + y[i] * y[i];
        if (distSq <= wallStart * wallStart) {
            return;
        }
        final double dist = Math.sqrt(distSq);
        final double scale = kOverM * (dist - wallStart) / dist;
        ax[i] -= scale * x[i];
        ay[i] -= scale * y[i];
    }

    /** Obstáculo fijo de radio r en {@code (ox, 0)}; el primer contacto convierte a la partícula. */
    private void obstacle(final double t, final int i, final double ox, final double[] x, final double[] y,
                          final double[] ax, final double[] ay) {
        final double dx = ox - x[i];
        final double dy = -y[i];
        final double distSq = dx * dx + dy * dy;
        if (distSq >= contactSq) {
            return;
        }
        final double dist = Math.sqrt(distSq);
        final double scale = kOverM * (contact - dist) / dist;
        ax[i] -= scale * dx;
        ay[i] -= scale * dy;
        if (!used[i]) {
            used[i] = true;
            conversionTime[conversions] = t;
            conversionId[conversions] = i;
            conversions++;
        }
    }

    private void fillGrid(final double[] x, final double[] y) {
        Arrays.fill(head, -1);
        for (int i = 0; i < n; i++) {
            final int cell = cellIndex(y[i]) * cells + cellIndex(x[i]);
            next[i] = head[cell];
            head[cell] = i;
        }
    }

    /** Índice de celda acotado: una partícula que penetra la pared puede quedar apenas fuera de [−R, R]. */
    private int cellIndex(final double coord) {
        final int index = (int) Math.floor((coord + table.bigR()) / cellSize);
        return Math.min(cells - 1, Math.max(0, index));
    }

    public boolean used(final int i) {
        return used[i];
    }

    public int conversions() {
        return conversions;
    }

    public double conversionTime(final int index) {
        return conversionTime[index];
    }

    public int conversionId(final int index) {
        return conversionId[index];
    }

    public int cellsPerSide() {
        return cells;
    }
}
