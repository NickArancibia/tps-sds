package ar.edu.itba.sds.tp5.hybrid;

import ar.edu.itba.sds.tp5.cpm.Agents;
import ar.edu.itba.sds.tp5.cpm.CellGrid;
import ar.edu.itba.sds.tp5.cpm.CpmParams;
import ar.edu.itba.sds.tp5.cpm.EventLog;
import ar.edu.itba.sds.tp5.cpm.Room;
import ar.edu.itba.sds.tp5.cpm.Targets;
import ar.edu.itba.sds.tp5.edmd.EventQueue;
import ar.edu.itba.sds.tp5.tsdmd.TimeDrivenCpm;

import java.io.IOException;

import static ar.edu.itba.sds.tp5.cpm.Kinematics.INF;
import static ar.edu.itba.sds.tp5.cpm.Kinematics.approachTime;
import static ar.edu.itba.sds.tp5.cpm.Kinematics.retireTime;
import static ar.edu.itba.sds.tp5.cpm.Kinematics.wallDistance;
import static ar.edu.itba.sds.tp5.cpm.Kinematics.wallTime;

/**
 * Esquema híbrido: cada agente se resuelve con EDMD o con TSDMD según un área de radio {@code R_h}
 * alrededor de su centro.
 *
 * <p>Criterio de pasaje:</p>
 * <ul>
 *   <li>EDMD → TSDMD: cuando el centro de otro agente llega a distancia {@code R_h} del suyo, o una
 *   pared a distancia {@code R_h/2} (evento de entrada al área). El pasaje se hace en el próximo
 *   paso de la grilla.</li>
 *   <li>TSDMD → EDMD: en un paso de la grilla, si el agente está libre ({@code r = r_max}, sin
 *   contacto) y no hay ningún agente a menos de {@code R_h} ni pared a menos de {@code R_h/2}. Choque,
 *   escape y recuperación son siempre por paso temporal.</li>
 * </ul>
 *
 * <p>Convivencia: grilla global {@code t_n = nΔt}. Entre dos pasos se procesan en orden los eventos de
 * los agentes en EDMD (cambio de target en el borde de la franja y en la línea de la puerta, retiro,
 * cruce de celda, entrada al área). Dentro de un paso un agente en TSDMD tiene velocidad constante
 * (regla del CPM), así que su entrada al área de un agente en EDMD también se predice con la
 * cuadrática {@code |Δx + Δv t| = R_h}; esas predicciones valen hasta el paso siguiente, cuando el
 * agente TSDMD cambia de velocidad. En cada paso, en orden: se mueven los agentes en TSDMD y se
 * actualizan sus fases (puerta, retiro); se guarda el estado; los agentes marcados pasan a TSDMD; los
 * agentes TSDMD libres y sin nadie en el área pasan a EDMD; paso del CPM solo para los agentes en
 * TSDMD ({@link TimeDrivenCpm#updateVelocities}); se predicen sus entradas al área de los agentes en
 * EDMD.</p>
 *
 * <p>Sin contactos perdidos: un agente en EDMD camina libre y no tiene a nadie a menos de
 * {@code R_h ≥ 2 r_max} (ni pared a menos de {@code R_h/2 ≥ r_max}), así que no puede tocar a nadie;
 * entre la entrada al área y el pasaje (menos de {@code Δt}) se acerca a lo sumo {@code 2 v Δt}
 * {@code = r_min}: los cuerpos no se tocan y el paso del CPM detecta el contacto de los espacios
 * personales como en TSDMD puro.</p>
 *
 * <p>Las celdas del área miden {@code >= R_h + 2 v Δt}: dos agentes que se acercan a {@code R_h}
 * dentro de un paso están en celdas contiguas al comienzo del paso.</p>
 */
public final class HybridCpm {

    static final byte CELL = 0;
    static final byte BAND = 1;
    static final byte DOOR = 2;
    static final byte RETIRE = 3;
    static final byte NEAR = 4;
    static final byte NEAR_WALL = 5;
    private static final String[] EVENT_NAMES = {"cell", "band", "door", "retire", "near", "nearWall"};

    private final Agents a;
    private final Room room;
    private final CpmParams p;
    private final EventLog log;
    private final TimeDrivenCpm tsdmd;
    private final CellGrid grid;
    private final EventQueue queue = new EventQueue();
    private final double rh;
    private final double rhWall;
    private final double dt;

    private final double[] t0;
    private final int[] count;
    private final boolean[] pending;
    private final int[] cx;
    private final int[] cy;
    private final int[] head;
    private final int[] next;
    private final int[] prev;
    private final int[] tsIds;
    private final double[] savedX;
    private final double[] savedY;

    private long step;
    private double now;
    private byte lastType = -1;
    /** ¿El último evento EDMD cambió algo? (una entrada al área solo si marcó a un agente nuevo) */
    private boolean lastChanged;
    private int lastStepMoved;
    private final long[] processed = new long[EVENT_NAMES.length];
    private long stale;
    private long edToTs;
    private long tsToEd;
    private long tsAgentSteps;

    public HybridCpm(final Agents agents, final Room room, final CpmParams params, final double rh,
                     final EventLog log) {
        if (!(rh >= 2 * params.rMax())) {
            throw new IllegalArgumentException("--rh debe ser >= 2 r_max = " + 2 * params.rMax() + " m (es " + rh + ")");
        }
        this.a = agents;
        this.room = room;
        this.p = params;
        this.log = log;
        this.rh = rh;
        this.rhWall = rh / 2;
        this.dt = params.dt();
        this.tsdmd = new TimeDrivenCpm(agents, room, params, log);
        final double vMax = Math.max(params.vdMax(), params.ve());
        this.grid = new CellGrid(room, params, rh + 2 * vMax * dt);
        final int n = agents.n();
        t0 = new double[n];
        count = new int[n];
        pending = new boolean[n];
        cx = new int[n];
        cy = new int[n];
        next = new int[n];
        prev = new int[n];
        tsIds = new int[n];
        savedX = new double[n];
        savedY = new double[n];
        head = new int[grid.cells()];
        java.util.Arrays.fill(head, -1);
        final int[] active = a.active();
        for (int k = 0; k < a.activeCount(); k++) {
            final int i = active[k];
            a.scheme[i] = Agents.TSDMD;
            cx[i] = grid.cellX(a.x[i]);
            cy[i] = grid.cellY(a.y[i]);
            link(i);
        }
        // Condición inicial con radios en r_min: todos empiezan en TSDMD.
        updateTsdmd();
    }

    /**
     * Procesa el próximo evento: un evento EDMD, si hay alguno antes del próximo paso de la grilla, o
     * ese paso (mueve los agentes en TSDMD y actualiza sus fases; después hay que llamar a
     * {@link #prepareNextStep()}).
     *
     * @return {@code true} si procesó un paso de la grilla
     */
    public boolean processNext() {
        final double tNext = (step + 1) * dt;
        final EventQueue q = queue;
        while (q.peekTime() <= tNext) {
            q.pop();
            final int i = q.topA;
            if (a.phase[i] == Agents.REMOVED || count[i] != q.topCa
                    || (q.topType == NEAR && (a.phase[q.topB] == Agents.REMOVED || count[q.topB] != q.topCb))) {
                stale++;
                continue;
            }
            now = q.topTime;
            lastType = q.topType;
            lastChanged = q.topType != CELL;
            processed[q.topType]++;
            switch (q.topType) {
                case CELL -> crossCell(i, q.topB);
                case BAND -> crossBand(i, q.topB);
                case DOOR -> crossDoor(i);
                case RETIRE -> retire(i);
                case NEAR -> {
                    final int j = q.topB;
                    final boolean markI = a.scheme[i] == Agents.EDMD && !pending[i];
                    final boolean markJ = a.scheme[j] == Agents.EDMD && !pending[j];
                    pending[i] |= markI;
                    pending[j] |= markJ;
                    lastChanged = markI || markJ;
                }
                case NEAR_WALL -> {
                    lastChanged = !pending[i];
                    pending[i] = true;
                }
                default -> throw new IllegalStateException("Evento desconocido " + q.topType);
            }
            return false;
        }
        step++;
        now = tNext;
        lastStepMoved = moveTsdmd();
        return true;
    }

    /**
     * ¿El último evento procesado es un evento del sistema? Un evento EDMD lo es si cambió algo (no
     * los cruces de celda, que son solo de la búsqueda de vecinos, ni una entrada al área de un agente
     * ya marcado); un paso de la grilla, solo si había agentes en TSDMD.
     */
    public boolean lastWasSystemEvent(final boolean gridStep) {
        return gridStep ? lastStepMoved > 0 : lastChanged;
    }

    /** Pasajes entre esquemas, paso del CPM de los agentes en TSDMD y sus predicciones. */
    public void prepareNextStep() {
        final int[] active = a.active();
        for (int k = 0; k < a.activeCount(); k++) {
            final int i = active[k];
            if (pending[i]) {
                sync(i);
                pending[i] = false;
                a.scheme[i] = Agents.TSDMD;
                count[i]++;
                edToTs++;
            }
        }
        for (int k = 0; k < a.activeCount(); k++) {
            final int i = active[k];
            if (a.scheme[i] == Agents.TSDMD && !a.contact[i] && a.r[i] >= p.rMax() && areaIsEmpty(i)) {
                a.scheme[i] = Agents.EDMD;
                tsToEd++;
                redirect(i);
            }
        }
        updateTsdmd();
    }

    // ---------------------------------------------------------------------------------- TSDMD

    /**
     * Mueve un paso a los agentes en TSDMD y actualiza sus fases, como {@link TimeDrivenCpm#step}.
     *
     * @return agentes en TSDMD que se movieron
     */
    private int moveTsdmd() {
        final int[] active = a.active();
        final int count0 = a.activeCount();
        int moved = 0;
        for (int k = 0; k < count0; k++) {
            final int i = active[k];
            if (a.scheme[i] != Agents.TSDMD) {
                continue;
            }
            a.x[i] += a.vx[i] * dt;
            a.y[i] += a.vy[i] * dt;
            t0[i] = now;
            relink(i);
            moved++;
        }
        // De atrás hacia adelante: remove(k) trae a la posición k el último activo, ya revisado.
        for (int k = count0 - 1; k >= 0; k--) {
            final int i = active[k];
            if (a.scheme[i] != Agents.TSDMD) {
                continue;
            }
            if (a.phase[i] == Agents.IN_ROOM && a.y[i] <= 0) {
                a.phase[i] = Agents.EXITING;
                log.add(now, i, EventLog.DOOR);
            }
            if (a.phase[i] == Agents.EXITING && room.hasLeft(a.x[i], a.y[i])) {
                unlink(i);
                a.remove(k);
                count[i]++;
                log.add(now, i, EventLog.EXIT);
            }
        }
        return moved;
    }

    /** Paso del CPM para los agentes en TSDMD (en el orden de la lista de activos) y sus predicciones. */
    private void updateTsdmd() {
        final int[] active = a.active();
        int m = 0;
        for (int k = 0; k < a.activeCount(); k++) {
            if (a.scheme[active[k]] == Agents.TSDMD) {
                tsIds[m++] = active[k];
            }
        }
        if (m == 0) {
            return;
        }
        tsdmd.updateVelocities(tsIds, m);
        tsAgentSteps += m;
        final double tNext = (step + 1) * dt;
        for (int k = 0; k < m; k++) {
            count[tsIds[k]]++;
        }
        // Mismos pares TSDMD–EDMD en celdas contiguas, recorridos desde los agentes en EDMD: en el atasco
        // casi no hay agentes EDMD, y recorrer los vecinos de cada agente TSDMD costaría más que el paso.
        for (int k = 0; k < a.activeCount(); k++) {
            final int i = active[k];
            if (a.scheme[i] != Agents.EDMD) {
                continue;
            }
            for (int ny = Math.max(0, cy[i] - 1); ny <= Math.min(grid.my - 1, cy[i] + 1); ny++) {
                for (int nx = Math.max(0, cx[i] - 1); nx <= Math.min(grid.mx - 1, cx[i] + 1); nx++) {
                    for (int j = head[nx + grid.mx * ny]; j >= 0; j = next[j]) {
                        if (a.scheme[j] == Agents.TSDMD) {
                            pushNear(i, j, tNext);
                        }
                    }
                }
            }
        }
    }

    /** ¿No hay ningún agente a menos de {@code R_h} ni pared a menos de {@code R_h/2}? */
    private boolean areaIsEmpty(final int i) {
        final double xi = posX(i);
        final double yi = posY(i);
        for (int ny = Math.max(0, cy[i] - 1); ny <= Math.min(grid.my - 1, cy[i] + 1); ny++) {
            for (int nx = Math.max(0, cx[i] - 1); nx <= Math.min(grid.mx - 1, cx[i] + 1); nx++) {
                for (int j = head[nx + grid.mx * ny]; j >= 0; j = next[j]) {
                    if (j != i && Math.hypot(xi - posX(j), yi - posY(j)) <= rh) {
                        return false;
                    }
                }
            }
        }
        for (int w = 0; w < room.wallCount(); w++) {
            if (wallDistance(xi, yi, room.wall(w)) <= rhWall) {
                return false;
            }
        }
        return true;
    }

    // ---------------------------------------------------------------------------------- EDMD

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
        predictNear(i);
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
        a.y[i] = 0;
        redirect(i);
    }

    private void retire(final int i) {
        sync(i);
        if (a.phase[i] == Agents.IN_ROOM) {
            a.phase[i] = Agents.EXITING;
            log.add(now, i, EventLog.DOOR);
        }
        unlink(i);
        a.removeAgent(i);
        pending[i] = false;
        count[i]++;
        log.add(now, i, EventLog.EXIT);
    }

    /** Agente en EDMD: velocidad libre hacia el target vigente y todas sus predicciones. */
    private void redirect(final int i) {
        sync(i);
        Targets.update(a, i, room);
        final double dx = a.tx[i] - a.x[i];
        final double dy = a.ty[i] - a.y[i];
        final double dist = Math.hypot(dx, dy);
        final double speed = p.vdMax();
        a.vx[i] = dist > 0 ? speed * dx / dist : 0;
        a.vy[i] = dist > 0 ? speed * dy / dist : 0;
        count[i]++;
        final int ci = count[i];
        final double x = a.x[i];
        final double y = a.y[i];
        final double vx = a.vx[i];
        final double vy = a.vy[i];
        if (vx == 0 && vy == 0) {
            return;
        }
        pushCell(i);
        if (y > 0) {
            if (x < room.bandMin() && vx > 0) {
                queue.push(now + (room.bandMin() - x) / vx, BAND, i, 0, ci, 0);
            } else if (x > room.bandMax() && vx < 0) {
                queue.push(now + (room.bandMax() - x) / vx, BAND, i, 1, ci, 0);
            }
            if (vy < 0) {
                queue.push(now - y / vy, DOOR, i, -1, ci, 0);
            }
        }
        final double tr = retireTime(room, x, y, vx, vy);
        if (tr < INF) {
            queue.push(now + tr, RETIRE, i, -1, ci, 0);
        }
        for (int w = 0; w < room.wallCount(); w++) {
            final double tw = wallTime(x, y, vx, vy, rhWall, room.wall(w));
            if (tw < INF) {
                queue.push(now + tw, NEAR_WALL, i, w, ci, 0);
            }
        }
        predictNear(i);
    }

    /** Entradas al área entre el agente EDMD {@code i} y sus vecinos. */
    private void predictNear(final int i) {
        final double tNext = (step + 1) * dt;
        for (int ny = Math.max(0, cy[i] - 1); ny <= Math.min(grid.my - 1, cy[i] + 1); ny++) {
            for (int nx = Math.max(0, cx[i] - 1); nx <= Math.min(grid.mx - 1, cx[i] + 1); nx++) {
                for (int j = head[nx + grid.mx * ny]; j >= 0; j = next[j]) {
                    if (j != i) {
                        pushNear(i, j, a.scheme[j] == Agents.TSDMD ? tNext : INF);
                    }
                }
            }
        }
    }

    /** Predice cuándo {@code j} entra al área de {@code i} (EDMD); se descarta si cae después de {@code limit}. */
    private void pushNear(final int i, final int j, final double limit) {
        final double tc = approachTime(posX(i) - posX(j), posY(i) - posY(j), a.vx[i] - a.vx[j],
                a.vy[i] - a.vy[j], rh);
        if (tc < INF && now + tc <= limit) {
            queue.push(now + tc, NEAR, i, j, count[i], count[j]);
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

    // ---------------------------------------------------------------------------------- estado

    /**
     * Llama a {@code writer} con las posiciones de todos los agentes en el instante actual y después
     * restaura las posiciones de referencia (el estado del motor no cambia).
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

    /** Escritura de un estado; puede tirar {@link IOException}. */
    @FunctionalInterface
    public interface StateWriter {
        void write() throws IOException;
    }

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

    private void relink(final int i) {
        final int nx = grid.cellX(a.x[i]);
        final int ny = grid.cellY(a.y[i]);
        if (nx != cx[i] || ny != cy[i]) {
            unlink(i);
            cx[i] = nx;
            cy[i] = ny;
            link(i);
        }
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

    public double time() {
        return now;
    }

    public long steps() {
        return step;
    }

    /** Agentes activos en TSDMD. */
    public int tsdmdCount() {
        final int[] active = a.active();
        int m = 0;
        for (int k = 0; k < a.activeCount(); k++) {
            if (a.scheme[active[k]] == Agents.TSDMD) {
                m++;
            }
        }
        return m;
    }

    public CellGrid grid() {
        return grid;
    }

    public TimeDrivenCpm tsdmd() {
        return tsdmd;
    }

    /** Pasos, pasajes entre esquemas y eventos procesados por tipo, como objeto JSON. */
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
                .append(", \"steps\": ").append(step)
                .append(", \"tsdmdAgentSteps\": ").append(tsAgentSteps)
                .append(", \"edmdToTsdmd\": ").append(edToTs)
                .append(", \"tsdmdToEdmd\": ").append(tsToEd)
                .append('}').toString();
    }
}
