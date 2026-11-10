package ar.edu.itba.sds.tp5.cpm;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Random;

/**
 * Estado de los N agentes en arreglos paralelos (índice 0-based; el id de salida es índice + 1).
 *
 * <p>Fase de cada agente: {@link #IN_ROOM} (target en la puerta), {@link #EXITING} (cruzó la línea
 * de la puerta; target afuera) y {@link #REMOVED} (se alejó {@code exitDistance} y salió de la
 * simulación). Los agentes no retirados están en {@link #active()}. Esquema con el que se resuelve
 * cada agente: {@link #TSDMD} (default) o {@link #EDMD}.</p>
 */
public final class Agents {

    public static final byte IN_ROOM = 0;
    public static final byte EXITING = 1;
    public static final byte REMOVED = 2;

    public static final byte TSDMD = 0;
    public static final byte EDMD = 1;

    private final int n;
    public final double[] x;
    public final double[] y;
    public final double[] vx;
    public final double[] vy;
    public final double[] r;
    /** Target vigente (se recalcula en cada paso con la regla de {@link Targets}). */
    public final double[] tx;
    public final double[] ty;
    /** Punto al azar de la franja central de la puerta, sorteado una vez por agente. */
    public final double[] bandX;
    public final byte[] phase;
    public final boolean[] contact;
    /** Esquema vigente de cada agente ({@link #TSDMD} o {@link #EDMD}). */
    public final byte[] scheme;
    /** Suma de los versores de escape {@code Σ_j e_ij} del paso en curso. */
    public final double[] ex;
    public final double[] ey;

    private final int[] active;
    private int activeCount;

    public Agents(final int n) {
        this.n = n;
        x = new double[n];
        y = new double[n];
        vx = new double[n];
        vy = new double[n];
        r = new double[n];
        tx = new double[n];
        ty = new double[n];
        bandX = new double[n];
        phase = new byte[n];
        contact = new boolean[n];
        scheme = new byte[n];
        ex = new double[n];
        ey = new double[n];
        active = new int[n];
        for (int i = 0; i < n; i++) {
            active[i] = i;
        }
        activeCount = n;
    }

    /**
     * Condición inicial: posiciones uniformes en la habitación sin superposición entre agentes ni con
     * las paredes, evaluada con {@code r_max} (no se superponen tampoco cuando el radio crece). Radios
     * en {@code r_min} y velocidad nula, como en el paper.
     */
    public static Agents random(final int n, final Room room, final CpmParams p, final Random random) {
        final Agents a = new Agents(n);
        final double lo = p.rMax();
        final double span = room.l() - 2 * p.rMax();
        final double minDist2 = 4 * p.rMax() * p.rMax();
        final long maxAttempts = 1000L * n;
        long attempts = 0;
        for (int i = 0; i < n; i++) {
            boolean placed = false;
            while (!placed) {
                if (++attempts > maxAttempts) {
                    throw new IllegalStateException("No se pudieron ubicar " + n + " agentes sin superposición en L = "
                            + room.l() + " m");
                }
                final double px = lo + span * random.nextDouble();
                final double py = lo + span * random.nextDouble();
                placed = true;
                for (int j = 0; j < i && placed; j++) {
                    final double dx = px - a.x[j];
                    final double dy = py - a.y[j];
                    placed = dx * dx + dy * dy >= minDist2;
                }
                if (placed) {
                    a.x[i] = px;
                    a.y[i] = py;
                }
            }
            a.r[i] = p.rMin();
            a.bandX[i] = room.bandMin() + (room.bandMax() - room.bandMin()) * random.nextDouble();
        }
        return a;
    }

    /**
     * Condición inicial leída de un archivo con una fila {@code x y} por agente (se ignoran líneas
     * vacías y las que empiezan con {@code #}). Mismas reglas que {@link #random}: dentro de la
     * habitación y sin superposición evaluada con {@code r_max}; radios en {@code r_min}.
     */
    public static Agents fromFile(final Path path, final Room room, final CpmParams p, final Random random)
            throws IOException {
        final List<double[]> rows = Files.readAllLines(path).stream()
                .map(String::strip)
                .filter(line -> !line.isEmpty() && !line.startsWith("#"))
                .map(line -> line.split("\\s+"))
                .map(tokens -> new double[]{Double.parseDouble(tokens[0]), Double.parseDouble(tokens[1])})
                .toList();
        if (rows.isEmpty()) {
            throw new IllegalArgumentException("Sin agentes en " + path);
        }
        final Agents a = new Agents(rows.size());
        final double lo = p.rMax();
        final double hi = room.l() - p.rMax();
        for (int i = 0; i < rows.size(); i++) {
            final double px = rows.get(i)[0];
            final double py = rows.get(i)[1];
            if (px < lo || px > hi || py < lo || py > hi) {
                throw new IllegalArgumentException("Agente " + (i + 1) + " fuera de la habitación o tocando una pared");
            }
            for (int j = 0; j < i; j++) {
                if (Math.hypot(px - a.x[j], py - a.y[j]) < 2 * p.rMax()) {
                    throw new IllegalArgumentException("Agentes " + (j + 1) + " y " + (i + 1) + " superpuestos");
                }
            }
            a.x[i] = px;
            a.y[i] = py;
            a.r[i] = p.rMin();
            a.bandX[i] = room.bandMin() + (room.bandMax() - room.bandMin()) * random.nextDouble();
        }
        return a;
    }

    public int n() {
        return n;
    }

    /** Índices de los agentes no retirados; válidos los primeros {@link #activeCount()}. */
    public int[] active() {
        return active;
    }

    public int activeCount() {
        return activeCount;
    }

    /** Retira el agente que ocupa la posición {@code k} de la lista de activos. */
    public void remove(final int k) {
        final int i = active[k];
        phase[i] = REMOVED;
        vx[i] = 0;
        vy[i] = 0;
        contact[i] = false;
        active[k] = active[--activeCount];
        active[activeCount] = i;
    }

    /** Retira al agente {@code i} (búsqueda lineal en la lista de activos: a lo sumo N veces). */
    public void removeAgent(final int i) {
        for (int k = 0; k < activeCount; k++) {
            if (active[k] == i) {
                remove(k);
                return;
            }
        }
        throw new IllegalStateException("Agente " + i + " no está activo");
    }
}
