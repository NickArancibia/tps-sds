package ar.edu.itba.sds.tp4.billiard;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Random;

/**
 * Condiciones iniciales sin superposiciones (entre partículas, con los obstáculos ni con la pared)
 * y velocidad de módulo {@code v0} con ángulo uniforme en [0, 2π).
 * <ul>
 *   <li>{@link #random}: inserción secuencial al azar, centro uniforme en {@code |r| <= R − r}.
 *   Se traba cerca de la fracción de área de saturación (~0.55 en 2D, N ≈ 465 acá).</li>
 *   <li>{@link #hexagonal}: N sitios elegidos al azar de una red triangular de lado
 *   {@code 2r} (contacto sin superposición). Llega a ~720 partículas.</li>
 * </ul>
 */
public final class InitialState {

    private static final int MAX_ATTEMPTS = 1_000_000;
    /** Margen relativo sobre {@code 2r} en la red: los vecinos quedan con {@code ξ < 0} pese al redondeo. */
    private static final double LATTICE_MARGIN = 1e-9;

    public final double[] x;
    public final double[] y;
    public final double[] vx;
    public final double[] vy;

    private InitialState(final int n) {
        x = new double[n];
        y = new double[n];
        vx = new double[n];
        vy = new double[n];
    }

    public static InitialState random(final Table table, final int n, final double v0, final Random random) {
        final InitialState s = new InitialState(n);
        final double maxRadius = table.bigR() - table.r();
        final double minDistSq = 4 * table.r() * table.r();
        for (int i = 0; i < n; i++) {
            boolean placed = false;
            for (int attempt = 0; attempt < MAX_ATTEMPTS && !placed; attempt++) {
                final double px = (2 * random.nextDouble() - 1) * maxRadius;
                final double py = (2 * random.nextDouble() - 1) * maxRadius;
                if (px * px + py * py <= maxRadius * maxRadius && fits(s, i, px, py, table, minDistSq)) {
                    s.x[i] = px;
                    s.y[i] = py;
                    placed = true;
                }
            }
            if (!placed) {
                throw new IllegalStateException(
                        "No se pudo ubicar la partícula %d de %d sin superposición (fracción de área %.3f)"
                                .formatted(i + 1, n, n * table.r() * table.r() / (table.bigR() * table.bigR())));
            }
            final double theta = random.nextDouble() * 2 * Math.PI;
            s.vx[i] = v0 * Math.cos(theta);
            s.vy[i] = v0 * Math.sin(theta);
        }
        return s;
    }

    /**
     * Red triangular de lado {@code a = 2r(1 + 1e-9)} con la fila {@code y = 0} en
     * {@code x = (i + 1/2) a}: con los obstáculos en contacto ({@code x_o = r}) cada obstáculo
     * ocupa un sitio. Se descartan los sitios fuera de {@code |r| <= R − r} o a menos de
     * {@code 2r} de un obstáculo, y se eligen N al azar.
     */
    public static InitialState hexagonal(final Table table, final int n, final double v0, final Random random) {
        final double a = 2 * table.r() * (1 + LATTICE_MARGIN);
        final double rowHeight = a * Math.sqrt(3) / 2;
        final double maxRadius = table.bigR() - table.r();
        final double minDistSq = 4 * table.r() * table.r();
        final int rows = (int) Math.ceil(maxRadius / rowHeight);
        final int cols = (int) Math.ceil(maxRadius / a) + 1;
        final List<double[]> sites = new ArrayList<>();
        for (int j = -rows; j <= rows; j++) {
            final double py = j * rowHeight;
            final double shift = (Math.floorMod(j, 2) == 0) ? 0.5 * a : 0.0;
            for (int i = -cols; i <= cols; i++) {
                final double px = i * a + shift;
                if (px * px + py * py > maxRadius * maxRadius) {
                    continue;
                }
                boolean free = true;
                for (final double ox : table.obstacleX()) {
                    free &= (px - ox) * (px - ox) + py * py >= minDistSq;
                }
                if (free) {
                    sites.add(new double[]{px, py});
                }
            }
        }
        if (sites.size() < n) {
            throw new IllegalArgumentException(
                    "La red hexagonal tiene %d sitios libres; no entran %d partículas".formatted(sites.size(), n));
        }
        Collections.shuffle(sites, random);
        final InitialState s = new InitialState(n);
        for (int i = 0; i < n; i++) {
            s.x[i] = sites.get(i)[0];
            s.y[i] = sites.get(i)[1];
            final double theta = random.nextDouble() * 2 * Math.PI;
            s.vx[i] = v0 * Math.cos(theta);
            s.vy[i] = v0 * Math.sin(theta);
        }
        return s;
    }

    private static boolean fits(final InitialState s, final int placed, final double px, final double py,
                                final Table table, final double minDistSq) {
        for (final double ox : table.obstacleX()) {
            if ((px - ox) * (px - ox) + py * py <= minDistSq) {
                return false;
            }
        }
        for (int j = 0; j < placed; j++) {
            final double dx = px - s.x[j];
            final double dy = py - s.y[j];
            if (dx * dx + dy * dy <= minDistSq) {
                return false;
            }
        }
        return true;
    }
}
