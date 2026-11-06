package ar.edu.itba.sds.tp5.edmd;

import ar.edu.itba.sds.tp5.cpm.Agents;
import ar.edu.itba.sds.tp5.cpm.CellGrid;
import ar.edu.itba.sds.tp5.cpm.CpmParams;
import ar.edu.itba.sds.tp5.cpm.EventLog;
import ar.edu.itba.sds.tp5.cpm.Room;
import ar.edu.itba.sds.tp5.cpm.Targets;
import ar.edu.itba.sds.tp5.cpm.VelocityProjection;

import java.io.IOException;

/**
 * CPM regido por eventos (EDMD puro). Entre eventos cada agente hace MRU con radio constante, así que
 * los contactos se predicen con la cuadrática {@code |Δx + Δv t| = r_i + r_j}.
 *
 * <p>Estados de un agente: {@link #FREE} ({@code r = r_max}, rapidez {@code v_dmax} hacia el
 * target), {@link #ESCAPE} ({@code r = r_min}, velocidad de escape durante {@code Δt}) y
 * {@link #RECOVER} (tramos de {@link Recovery}, con la velocidad deseada del tramo hacia el
 * target). Condición inicial: todos recuperándose desde {@code t = 0} con radio {@code r_min}, como
 * el primer paso de TSDMD.</p>
 *
 * <p>Eventos:</p>
 * <ul>
 *   <li>contacto agente–agente ({@code |x_i − x_j| = r_i + r_j}) y agente–pared ({@code d = r_i}):
 *   colapso. Todos los agentes en contacto en ese instante (cierre transitivo) pasan a {@code r_min}
 *   y escapan con {@code v_e Σe/|Σe|} (Ec. 6), sumando los contactos vigentes con los radios de antes
 *   del colapso. Si dos cuerpos quedan tocándose (solo pasa si ya estaban en {@code r_min}), la
 *   velocidad se proyecta para que no se acerquen ({@link VelocityProjection} con {@code c = 0}):
 *   los cuerpos nunca se superponen;</li>
 *   <li>fin de escape ({@code Δt} después del colapso) y fin de cada tramo de recuperación. Al
 *   empezar un tramo el radio salta: si queda superpuesto con un vecino o una pared, hay contacto en
 *   ese mismo instante;</li>
 *   <li>cruce del borde de la franja central de la puerta y de la línea de la puerta ({@code y = 0}):
 *   cambio de target ({@link Targets}); el cruce de la puerta registra el evento de puerta;</li>
 *   <li>retiro: a {@code exitDistance} del centro de la puerta, del lado de afuera;</li>
 *   <li>cruce de celda del Cell Index Method ({@link CellGrid}): dos agentes solo pueden tocarse si
 *   están en celdas contiguas, así que al cambiar de celda se predicen los contactos con los nuevos
 *   vecinos.</li>
 * </ul>
 *
 * <p>Cada agente lleva un contador de cambios de trayectoria; un evento predicho con contadores
 * viejos se descarta al sacarlo de la cola. Las posiciones se guardan en el instante {@code t0[i]}
 * del último cambio del agente; {@link #writeState} las muestra en el instante del evento actual sin
 * modificar el estado, así la trayectoria no depende de cuántos estados se guardan.</p>
 */
public final class EventDrivenCpm {

    static final byte CONTACT = 0;
    static final byte WALL = 1;
    static final byte ESCAPE_END = 2;
    static final byte LEVEL_END = 3;
    static final byte CELL = 4;
    static final byte BAND = 5;
    static final byte DOOR = 6;
    static final byte RETIRE = 7;
    private static final String[] EVENT_NAMES = {"contact", "wall", "escapeEnd", "levelEnd", "cell", "band", "door",
            "retire"};

    public static final byte FREE = 0;
    public static final byte ESCAPE = 1;
    public static final byte RECOVER = 2;

    /** Tolerancia de contacto (m): a esta distancia dos superficies se consideran en contacto. */
    private static final double TOUCH = 1e-9;
    /** Umbral de acercamiento {@code Δx·Δv} (m²/s) para predecir un contacto. */
    private static final double APPROACH = 1e-12;
    private static final double INF = Double.POSITIVE_INFINITY;

    private final Agents a;
    private final Room room;
    private final CpmParams p;
    private final EventLog log;
    private final Recovery recovery;
    private final CellGrid grid;
    private final EventQueue queue = new EventQueue();
    private final VelocityProjection projection = new VelocityProjection();

    private final double dt;
    private final double[] t0;
    private final byte[] mode;
    private final int[] seg;
    /** Comienzo del escape o de la recuperación en curso. */
    private final double[] stateStart;
    private final int[] count;
    private final int[] cx;
    private final int[] cy;
    private final int[] head;
    private final int[] next;
    private final int[] prev;
    private final int[] members;
    private final boolean[] inSet;
    private final double[] savedX;
    private final double[] savedY;

    private double now;
    private byte lastType = -1;
    private final long[] processed = new long[EVENT_NAMES.length];
    private long stale;
    private long collapses;
    private long collapsedAgents;
    private long jumpCollapses;

    public EventDrivenCpm(final Agents agents, final Room room, final CpmParams params, final Recovery recovery,
                          final EventLog log) {
        this.a = agents;
        this.room = room;
        this.p = params;
        this.log = log;
        this.recovery = recovery;
        this.grid = new CellGrid(room, params);
        this.dt = params.dt();
        final int n = agents.n();
        t0 = new double[n];
        mode = new byte[n];
        seg = new int[n];
        stateStart = new double[n];
        count = new int[n];
        cx = new int[n];
        cy = new int[n];
        next = new int[n];
        prev = new int[n];
        members = new int[n];
        inSet = new boolean[n];
        savedX = new double[n];
        savedY = new double[n];
        head = new int[grid.cells()];
        java.util.Arrays.fill(head, -1);

        final int[] active = a.active();
        for (int k = 0; k < a.activeCount(); k++) {
            final int i = active[k];
            cx[i] = grid.cellX(a.x[i]);
            cy[i] = grid.cellY(a.y[i]);
            link(i);
            a.r[i] = params.rMin();
            mode[i] = recovery.segments() > 0 ? RECOVER : FREE;
        }
        for (int k = 0; k < a.activeCount(); k++) {
            beginState(active[k]);
        }
    }

    /**
     * Procesa el próximo evento válido.
     *
     * @return {@code false} si la cola quedó vacía
     */
    public boolean processNext() {
        final EventQueue q = queue;
        while (!q.isEmpty()) {
            q.pop();
            final int i = q.topA;
            if (a.phase[i] == Agents.REMOVED || count[i] != q.topCa
                    || (q.topType == CONTACT && (a.phase[q.topB] == Agents.REMOVED || count[q.topB] != q.topCb))) {
                stale++;
                continue;
            }
            now = q.topTime;
            lastType = q.topType;
            processed[q.topType]++;
            switch (q.topType) {
                case CONTACT -> collapse(i, q.topB);
                case WALL -> collapse(i, -1);
                case ESCAPE_END -> endEscape(i);
                case LEVEL_END -> endLevel(i);
                case CELL -> crossCell(i, q.topB);
                case BAND -> crossBand(i, q.topB);
                case DOOR -> crossDoor(i);
                case RETIRE -> retire(i);
                default -> throw new IllegalStateException("Evento desconocido " + q.topType);
            }
            return true;
        }
        return false;
    }

    /**
     * ¿El último evento procesado cambió el estado de algún agente? Los cruces de celda son solo de la
     * búsqueda de vecinos: no cambian ni velocidades ni radios.
     */
    public boolean lastEventChangedState() {
        return lastType != CELL;
    }

    /** Escritura de un estado; puede tirar {@link IOException}. */
    @FunctionalInterface
    public interface StateWriter {
        void write() throws IOException;
    }

    /**
     * Llama a {@code writer} con las posiciones de todos los agentes en el instante del último evento
     * y después restaura las posiciones de referencia (el estado del motor no cambia).
     */
    public void writeState(final StateWriter writer) throws IOException {
        final int[] active = a.active();
        final int n = a.activeCount();
        for (int k = 0; k < n; k++) {
            final int i = active[k];
            savedX[i] = a.x[i];
            savedY[i] = a.y[i];
            a.x[i] = posX(i);
            a.y[i] = posY(i);
        }
        try {
            writer.write();
        } finally {
            for (int k = 0; k < n; k++) {
                final int i = active[k];
                a.x[i] = savedX[i];
                a.y[i] = savedY[i];
            }
        }
    }

    public double time() {
        return now;
    }

    // ---------------------------------------------------------------------------------- eventos

    private void endEscape(final int i) {
        sync(i);
        if (recovery.segments() == 0) {
            mode[i] = FREE;
        } else {
            mode[i] = RECOVER;
            seg[i] = 0;
            stateStart[i] = now;
        }
        beginState(i);
    }

    private void endLevel(final int i) {
        sync(i);
        if (++seg[i] == recovery.segments()) {
            mode[i] = FREE;
        }
        beginState(i);
    }

    /** Fija radio y velocidad de un agente libre o recuperándose; si el radio nuevo pisa a alguien, colapso. */
    private void beginState(final int i) {
        sync(i);
        a.contact[i] = false;
        a.r[i] = mode[i] == FREE ? p.rMax() : recovery.radius(seg[i]);
        if (overlaps(i)) {
            jumpCollapses++;
            collapse(i, -1);
            return;
        }
        redirect(i);
    }

    /** Velocidad deseada hacia el target vigente (radio sin cambios) y nuevas predicciones. */
    private void redirect(final int i) {
        Targets.update(a, i, room);
        final double speed = mode[i] == FREE ? p.vdMax() : recovery.speed(seg[i]);
        final double dx = a.tx[i] - a.x[i];
        final double dy = a.ty[i] - a.y[i];
        final double dist = Math.hypot(dx, dy);
        a.vx[i] = dist > 0 ? speed * dx / dist : 0;
        a.vy[i] = dist > 0 ? speed * dy / dist : 0;
        count[i]++;
        predict(i);
    }

    private void crossCell(final int i, final int dir) {
        sync(i);
        unlink(i);
        switch (dir) {
            case 0 -> cx[i]++;
            case 1 -> cx[i]--;
            case 2 -> cy[i]++;
            default -> cy[i]--;
        }
        link(i);
        pushCell(i);
        predictContacts(i);
    }

    private void crossBand(final int i, final int side) {
        sync(i);
        a.x[i] = side == 0 ? room.bandMin() : room.bandMax();
        redirect(i);
    }

    private void crossDoor(final int i) {
        sync(i);
        if (a.phase[i] == Agents.IN_ROOM) {
            a.phase[i] = Agents.EXITING;
            log.add(now, i, EventLog.DOOR);
        }
        if (mode[i] != ESCAPE) {
            a.y[i] = 0;
            redirect(i);
        }
    }

    private void retire(final int i) {
        sync(i);
        if (a.phase[i] == Agents.IN_ROOM) {
            a.phase[i] = Agents.EXITING;
            log.add(now, i, EventLog.DOOR);
        }
        unlink(i);
        a.removeAgent(i);
        count[i]++;
        log.add(now, i, EventLog.EXIT);
    }

    // ---------------------------------------------------------------------------------- colapso

    /**
     * Colapso en el instante actual: {@code i} (y {@code j} si es un contacto entre agentes) más todos
     * los agentes que estén en contacto con alguno de ellos.
     */
    private void collapse(final int i, final int j) {
        collapses++;
        int size = 0;
        members[size++] = i;
        inSet[i] = true;
        if (j >= 0) {
            members[size++] = j;
            inSet[j] = true;
        }
        // Cierre de los contactos vigentes con los radios de antes del colapso, sumando versores (Ec. 6).
        for (int m = 0; m < size; m++) {
            final int k = members[m];
            sync(k);
            a.ex[k] = 0;
            a.ey[k] = 0;
            final double xk = a.x[k];
            final double yk = a.y[k];
            for (int ny = Math.max(0, cy[k] - 1); ny <= Math.min(grid.my - 1, cy[k] + 1); ny++) {
                for (int nx = Math.max(0, cx[k] - 1); nx <= Math.min(grid.mx - 1, cx[k] + 1); nx++) {
                    for (int l = head[nx + grid.mx * ny]; l >= 0; l = next[l]) {
                        if (l == k) {
                            continue;
                        }
                        final double dx = xk - posX(l);
                        final double dy = yk - posY(l);
                        final double d = Math.hypot(dx, dy);
                        if (d > a.r[k] + a.r[l] + TOUCH || d == 0) {
                            continue;
                        }
                        a.ex[k] += dx / d;
                        a.ey[k] += dy / d;
                        if (!inSet[l]) {
                            inSet[l] = true;
                            members[size++] = l;
                        }
                    }
                }
            }
            for (int w = 0; w < room.wallCount(); w++) {
                final double[] s = room.wall(w);
                final double u = segmentParam(xk, yk, s);
                final double dx = xk - (s[0] + u * (s[2] - s[0]));
                final double dy = yk - (s[1] + u * (s[3] - s[1]));
                final double d = Math.hypot(dx, dy);
                if (d <= a.r[k] + TOUCH && d > 0) {
                    a.ex[k] += dx / d;
                    a.ey[k] += dy / d;
                }
            }
        }
        collapsedAgents += size;
        for (int m = 0; m < size; m++) {
            final int k = members[m];
            a.r[k] = p.rMin();
            mode[k] = ESCAPE;
            stateStart[k] = now;
            a.contact[k] = true;
            Targets.update(a, k, room);
            final double norm = Math.hypot(a.ex[k], a.ey[k]);
            a.vx[k] = norm > 0 ? p.ve() * a.ex[k] / norm : 0;
            a.vy[k] = norm > 0 ? p.ve() * a.ey[k] / norm : 0;
        }
        // Cuerpos que quedaron tocándose: que no se acerquen (cada uno por su lado, c = 0).
        for (int m = 0; m < size; m++) {
            keepBodiesApart(members[m]);
        }
        for (int m = 0; m < size; m++) {
            final int k = members[m];
            inSet[k] = false;
            count[k]++;
            predict(k);
        }
    }

    private void keepBodiesApart(final int k) {
        projection.clear();
        final double xk = a.x[k];
        final double yk = a.y[k];
        final double rMin = p.rMin();
        for (int ny = Math.max(0, cy[k] - 1); ny <= Math.min(grid.my - 1, cy[k] + 1); ny++) {
            for (int nx = Math.max(0, cx[k] - 1); nx <= Math.min(grid.mx - 1, cx[k] + 1); nx++) {
                for (int l = head[nx + grid.mx * ny]; l >= 0; l = next[l]) {
                    if (l == k) {
                        continue;
                    }
                    final double dx = xk - posX(l);
                    final double dy = yk - posY(l);
                    final double d = Math.hypot(dx, dy);
                    if (d > 0 && d <= 2 * rMin + TOUCH) {
                        projection.add(dx / d, dy / d, 0);
                    }
                }
            }
        }
        for (int w = 0; w < room.wallCount(); w++) {
            final double[] s = room.wall(w);
            final double u = segmentParam(xk, yk, s);
            final double dx = xk - (s[0] + u * (s[2] - s[0]));
            final double dy = yk - (s[1] + u * (s[3] - s[1]));
            final double d = Math.hypot(dx, dy);
            if (d > 0 && d <= rMin + TOUCH) {
                projection.add(dx / d, dy / d, 0);
            }
        }
        if (projection.project(a.vx[k], a.vy[k])) {
            a.vx[k] = projection.vx();
            a.vy[k] = projection.vy();
        }
    }

    /** ¿El espacio personal de {@code i} (ya sincronizado) pisa el de un vecino o una pared? */
    private boolean overlaps(final int i) {
        final double xi = a.x[i];
        final double yi = a.y[i];
        for (int ny = Math.max(0, cy[i] - 1); ny <= Math.min(grid.my - 1, cy[i] + 1); ny++) {
            for (int nx = Math.max(0, cx[i] - 1); nx <= Math.min(grid.mx - 1, cx[i] + 1); nx++) {
                for (int l = head[nx + grid.mx * ny]; l >= 0; l = next[l]) {
                    if (l != i && Math.hypot(xi - posX(l), yi - posY(l)) < a.r[i] + a.r[l] - TOUCH) {
                        return true;
                    }
                }
            }
        }
        for (int w = 0; w < room.wallCount(); w++) {
            final double[] s = room.wall(w);
            final double u = segmentParam(xi, yi, s);
            if (Math.hypot(xi - (s[0] + u * (s[2] - s[0])), yi - (s[1] + u * (s[3] - s[1]))) < a.r[i] - TOUCH) {
                return true;
            }
        }
        return false;
    }

    // ---------------------------------------------------------------------------------- predicción

    /** Todos los eventos futuros de {@code i} con su trayectoria actual ({@code count[i]} ya incrementado). */
    private void predict(final int i) {
        final int ci = count[i];
        if (mode[i] == ESCAPE) {
            queue.push(stateStart[i] + dt, ESCAPE_END, i, -1, ci, 0);
        } else if (mode[i] == RECOVER) {
            queue.push(stateStart[i] + recovery.end(seg[i]), LEVEL_END, i, -1, ci, 0);
        }
        final double x = a.x[i];
        final double y = a.y[i];
        final double vx = a.vx[i];
        final double vy = a.vy[i];
        if (vx != 0 || vy != 0) {
            pushCell(i);
            if (mode[i] != ESCAPE && y > 0) {
                if (x < room.bandMin() && vx > 0) {
                    queue.push(now + (room.bandMin() - x) / vx, BAND, i, 0, ci, 0);
                } else if (x > room.bandMax() && vx < 0) {
                    queue.push(now + (room.bandMax() - x) / vx, BAND, i, 1, ci, 0);
                }
            }
            if (y > 0 && vy < 0) {
                queue.push(now - y / vy, DOOR, i, -1, ci, 0);
            }
            final double tr = retireTime(x, y, vx, vy);
            if (tr < INF) {
                queue.push(now + tr, RETIRE, i, -1, ci, 0);
            }
            for (int w = 0; w < room.wallCount(); w++) {
                final double tw = wallTime(x, y, vx, vy, a.r[i], room.wall(w));
                if (tw < INF) {
                    queue.push(now + tw, WALL, i, w, ci, 0);
                }
            }
        }
        predictContacts(i);
    }

    private void predictContacts(final int i) {
        final int ci = count[i];
        for (int ny = Math.max(0, cy[i] - 1); ny <= Math.min(grid.my - 1, cy[i] + 1); ny++) {
            for (int nx = Math.max(0, cx[i] - 1); nx <= Math.min(grid.mx - 1, cx[i] + 1); nx++) {
                for (int j = head[nx + grid.mx * ny]; j >= 0; j = next[j]) {
                    if (j == i) {
                        continue;
                    }
                    final double tc = approachTime(a.x[i] - posX(j), a.y[i] - posY(j), a.vx[i] - a.vx[j],
                            a.vy[i] - a.vy[j], a.r[i] + a.r[j]);
                    if (tc < INF) {
                        queue.push(now + tc, CONTACT, i, j, ci, count[j]);
                    }
                }
            }
        }
    }

    private void pushCell(final int i) {
        final double vx = a.vx[i];
        final double vy = a.vy[i];
        double best = INF;
        int dir = -1;
        if (vx > 0 && cx[i] < grid.mx - 1) {
            best = ((cx[i] + 1) * grid.cellW - a.x[i]) / vx;
            dir = 0;
        } else if (vx < 0 && cx[i] > 0) {
            best = (cx[i] * grid.cellW - a.x[i]) / vx;
            dir = 1;
        }
        if (vy > 0 && cy[i] < grid.my - 1) {
            final double t = (grid.yMin + (cy[i] + 1) * grid.cellH - a.y[i]) / vy;
            if (t < best) {
                best = t;
                dir = 2;
            }
        } else if (vy < 0 && cy[i] > 0) {
            final double t = (grid.yMin + cy[i] * grid.cellH - a.y[i]) / vy;
            if (t < best) {
                best = t;
                dir = 3;
            }
        }
        if (dir >= 0) {
            queue.push(now + Math.max(0, best), CELL, i, dir, count[i], 0);
        }
    }

    /**
     * Tiempo hasta que dos superficies que se acercan quedan a distancia {@code reach} entre centros
     * ({@code reach} = suma de radios, o radio contra un punto fijo). {@code 0} si ya están a esa
     * distancia o menos y acercándose.
     */
    private static double approachTime(final double dx, final double dy, final double dvx, final double dvy,
                                       final double reach) {
        final double b = dx * dvx + dy * dvy;
        if (b >= -APPROACH) {
            return INF;
        }
        final double c = dx * dx + dy * dy - reach * reach;
        if (c <= 0) {
            return 0;
        }
        final double vv = dvx * dvx + dvy * dvy;
        final double disc = b * b - vv * c;
        if (disc < 0) {
            return INF;
        }
        return c / (-b + Math.sqrt(disc));
    }

    /** Tiempo hasta que el centro queda a distancia {@code r} del segmento de pared {@code s}. */
    private static double wallTime(final double x, final double y, final double vx, final double vy, final double r,
                                   final double[] s) {
        final double sx = s[2] - s[0];
        final double sy = s[3] - s[1];
        final double len = Math.hypot(sx, sy);
        final double ux = sx / len;
        final double uy = sy / len;
        final double rx = x - s[0];
        final double ry = y - s[1];
        final double side = -rx * uy + ry * ux;
        final double rate = -vx * uy + vy * ux;
        double best = INF;
        if (side * rate < 0) {
            final double gap = Math.abs(side) - r;
            final double t = gap <= 0 ? 0 : gap / Math.abs(rate);
            final double u = (rx + vx * t) * ux + (ry + vy * t) * uy;
            if (u >= 0 && u <= len) {
                best = t;
            }
        }
        best = Math.min(best, approachTime(rx, ry, vx, vy, r));
        return Math.min(best, approachTime(x - s[2], y - s[3], vx, vy, r));
    }

    /** Tiempo hasta salir del círculo de retiro con {@code y < 0}. */
    private double retireTime(final double x, final double y, final double vx, final double vy) {
        final double e = room.exitDistance();
        final double dx = x - room.doorCenterX();
        final double b = dx * vx + y * vy;
        final double c = dx * dx + y * y - e * e;
        final double vv = vx * vx + vy * vy;
        if (c >= 0) {
            if (y < 0) {
                return 0;
            }
            if (b >= 0) {
                return INF;
            }
        }
        final double disc = b * b - vv * c;
        if (disc < 0) {
            return INF;
        }
        final double t = (-b + Math.sqrt(disc)) / vv;
        return y + vy * t < 0 ? t : INF;
    }

    private static double segmentParam(final double x, final double y, final double[] s) {
        final double sx = s[2] - s[0];
        final double sy = s[3] - s[1];
        return Math.max(0, Math.min(1, ((x - s[0]) * sx + (y - s[1]) * sy) / (sx * sx + sy * sy)));
    }

    // ---------------------------------------------------------------------------------- estado

    private void sync(final int i) {
        final double elapsed = now - t0[i];
        if (elapsed != 0) {
            a.x[i] += a.vx[i] * elapsed;
            a.y[i] += a.vy[i] * elapsed;
            t0[i] = now;
        }
    }

    private double posX(final int j) {
        return a.x[j] + a.vx[j] * (now - t0[j]);
    }

    private double posY(final int j) {
        return a.y[j] + a.vy[j] * (now - t0[j]);
    }

    private void link(final int i) {
        final int c = cx[i] + grid.mx * cy[i];
        prev[i] = -1;
        next[i] = head[c];
        if (head[c] >= 0) {
            prev[head[c]] = i;
        }
        head[c] = i;
    }

    private void unlink(final int i) {
        if (prev[i] >= 0) {
            next[prev[i]] = next[i];
        } else {
            head[cx[i] + grid.mx * cy[i]] = next[i];
        }
        if (next[i] >= 0) {
            prev[next[i]] = prev[i];
        }
    }

    // ---------------------------------------------------------------------------------- estadísticas

    public CellGrid grid() {
        return grid;
    }

    public Recovery recovery() {
        return recovery;
    }

    /** Eventos procesados por tipo, descartados, colapsos y agentes colapsados, como objeto JSON. */
    public String statsJson() {
        final StringBuilder sb = new StringBuilder("{");
        long total = 0;
        for (int k = 0; k < EVENT_NAMES.length; k++) {
            sb.append('"').append(EVENT_NAMES[k]).append("\": ").append(processed[k]).append(", ");
            total += processed[k];
        }
        return sb.append("\"processed\": ").append(total)
                .append(", \"stale\": ").append(stale)
                .append(", \"pushed\": ").append(queue.pushed())
                .append(", \"collapses\": ").append(collapses)
                .append(", \"collapsedAgents\": ").append(collapsedAgents)
                .append(", \"radiusJumpCollapses\": ").append(jumpCollapses)
                .append('}').toString();
    }

    public long processedEvents() {
        long total = 0;
        for (final long k : processed) {
            total += k;
        }
        return total;
    }
}
