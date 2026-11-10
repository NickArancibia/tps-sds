package ar.edu.itba.sds.tp5.hybrid;

import ar.edu.itba.sds.tp5.cpm.Agents;
import ar.edu.itba.sds.tp5.cpm.CellGrid;
import ar.edu.itba.sds.tp5.cpm.CpmParams;
import ar.edu.itba.sds.tp5.cpm.EventLog;
import ar.edu.itba.sds.tp5.cpm.Room;
import ar.edu.itba.sds.tp5.cpm.Targets;
import ar.edu.itba.sds.tp5.cpm.VelocityProjection;
import ar.edu.itba.sds.tp5.edmd.EventQueue;
import ar.edu.itba.sds.tp5.edmd.Recovery;
import ar.edu.itba.sds.tp5.tsdmd.TimeDrivenCpm;

import java.io.IOException;

import static ar.edu.itba.sds.tp5.cpm.Kinematics.INF;
import static ar.edu.itba.sds.tp5.cpm.Kinematics.approachTime;
import static ar.edu.itba.sds.tp5.cpm.Kinematics.retireTime;
import static ar.edu.itba.sds.tp5.cpm.Kinematics.segmentParam;
import static ar.edu.itba.sds.tp5.cpm.Kinematics.wallDistance;
import static ar.edu.itba.sds.tp5.cpm.Kinematics.wallTime;

/**
 * Esquema híbrido: cada agente se resuelve con EDMD o con TSDMD según un área de radio {@code R_h}
 * alrededor de su centro. Con {@code R_h < 2 r_min} ningún agente puede entrar al área de otro y la
 * corrida es EDMD puro; con {@code R_h} mayor que la habitación es TSDMD puro.
 *
 * <p>Agente en EDMD: MRU entre eventos, con los estados y los choques de EDMD puro
 * ({@link ar.edu.itba.sds.tp5.edmd.EventDrivenCpm}): libre, escape de duración {@code Δt} y
 * recuperación en los tramos de {@link Recovery}. El contacto con otro agente en EDMD
 * ({@code |x_i − x_j| = r_i + r_j}) o con una pared ({@code d = r_i}) es un colapso: todos los
 * agentes en EDMD en contacto en ese instante pasan a {@code r_min} y escapan.</p>
 *
 * <p>Criterio de pasaje:</p>
 * <ul>
 *   <li>EDMD → TSDMD: cuando el centro de otro agente en EDMD llega a distancia {@code R_h} del suyo,
 *   o una pared a {@code R_h/2} (evento de entrada al área); o cuando un agente en TSDMD llega a
 *   distancia {@code D = max(R_h, 2 r_max)}. El pasaje se hace en el próximo paso de la grilla, con el
 *   radio que tenga el agente, y arrastra a los agentes en EDMD que queden a menos de {@code D} de
 *   uno recién pasado (cierre transitivo): después de los pasajes ningún agente en EDMD tiene a uno en
 *   TSDMD a menos de {@code D}.</li>
 *   <li>TSDMD → EDMD: en un paso de la grilla, si el agente está libre ({@code r = r_max}, sin
 *   contacto) y no hay ningún agente a menos de {@code D} ni pared a menos de {@code D/2}.</li>
 * </ul>
 *
 * <p>Con {@code R_h ≥ 2 r_max + 2 v Δt} el pasaje llega siempre antes que el contacto: los agentes en
 * EDMD solo caminan libres y todo choque se resuelve por paso temporal. Con {@code R_h} menor, los
 * choques entre agentes en EDMD se resuelven por eventos y solo pasan a TSDMD los que quedan a menos
 * de {@code R_h}. Condición inicial: el mismo criterio en {@code t = 0} (radios en {@code r_min});
 * los agentes que quedan en EDMD empiezan recuperándose, como en EDMD puro.</p>
 *
 * <p>Convivencia: grilla global {@code t_n = nΔt}. Entre dos pasos se procesan en orden los eventos de
 * los agentes en EDMD. Dentro de un paso un agente en TSDMD tiene velocidad constante (regla del CPM),
 * así que su llegada a distancia {@code D} de un agente en EDMD también se predice con la cuadrática
 * {@code |Δx + Δv t| = D}; esas predicciones valen hasta el paso siguiente, cuando el agente TSDMD
 * cambia de velocidad. En cada paso, en orden: se mueven los agentes en TSDMD y se actualizan sus
 * fases (puerta, retiro); se guarda el estado; los agentes marcados pasan a TSDMD; los agentes TSDMD
 * libres y sin nadie cerca pasan a EDMD; paso del CPM solo para los agentes en TSDMD
 * ({@link TimeDrivenCpm#updateVelocities}); se predicen sus llegadas a los agentes en EDMD.</p>
 *
 * <p>Sin contactos perdidos ni cuerpos superpuestos: entre agentes en EDMD todo contacto es un evento;
 * un agente en EDMD no tiene a ninguno en TSDMD a menos de {@code D ≥ 2 r_max}, y entre la llegada a
 * esa distancia y el pasaje (menos de {@code Δt}) se acercan a lo sumo {@code 2 v Δt = r_min}: los
 * cuerpos no se tocan y el paso del CPM detecta el contacto de los espacios personales como en TSDMD
 * puro.</p>
 *
 * <p>Las celdas miden {@code >= D + 2 v Δt}: dos agentes que se acercan a {@code D} dentro de un paso
 * están en celdas contiguas al comienzo del paso.</p>
 */
public final class HybridCpm {

    static final byte CELL = 0;
    static final byte BAND = 1;
    static final byte DOOR = 2;
    static final byte RETIRE = 3;
    static final byte NEAR = 4;
    static final byte NEAR_WALL = 5;
    static final byte CONTACT = 6;
    static final byte WALL = 7;
    static final byte ESCAPE_END = 8;
    static final byte LEVEL_END = 9;
    private static final String[] EVENT_NAMES = {"cell", "band", "door", "retire", "near", "nearWall", "contact",
            "wall", "escapeEnd", "levelEnd"};

    private static final byte FREE = 0;
    private static final byte ESCAPE = 1;
    private static final byte RECOVER = 2;

    /** Tolerancia de contacto (m): a esta distancia dos superficies se consideran en contacto. */
    private static final double TOUCH = 1e-9;

    private final Agents a;
    private final Room room;
    private final CpmParams p;
    private final EventLog log;
    private final Recovery recovery;
    private final TimeDrivenCpm tsdmd;
    private final CellGrid grid;
    private final EventQueue queue = new EventQueue();
    private final VelocityProjection projection = new VelocityProjection();
    private final double rh;
    private final double rhWall;
    /** {@code D = max(R_h, 2 r_max)}: distancia mínima entre un agente en EDMD y uno en TSDMD. */
    private final double mixed;
    /**
     * ¿Puede otro agente entrar al área? Con {@code R_h < 2 r_min} los cuerpos lo impiden: nunca hay
     * agentes en TSDMD, no hace falta predecir entradas al área y alcanzan las celdas de EDMD puro.
     */
    private final boolean areaReachable;
    private final double dt;

    private final double[] t0;
    private final int[] count;
    private final boolean[] pending;
    /** Estado de un agente en EDMD, su tramo de recuperación y el comienzo del escape o la recuperación. */
    private final byte[] mode;
    private final int[] seg;
    private final double[] stateStart;
    private final int[] cx;
    private final int[] cy;
    private final int[] head;
    private final int[] next;
    private final int[] prev;
    private final int[] tsIds;
    private final int[] members;
    private final boolean[] inSet;
    private final double[] savedX;
    private final double[] savedY;

    private long step;
    private double now;
    /** ¿El último evento EDMD cambió algo? (una entrada al área solo si marcó a un agente nuevo) */
    private boolean lastChanged;
    private int lastStepMoved;
    private final long[] processed = new long[EVENT_NAMES.length];
    private long stale;
    private long edToTs;
    private long tsToEd;
    private long tsAgentSteps;
    private long collapses;
    private long collapsedAgents;
    private long jumpCollapses;

    public HybridCpm(final Agents agents, final Room room, final CpmParams params, final double rh,
                     final Recovery recovery, final EventLog log) {
        if (!(rh >= 0)) {
            throw new IllegalArgumentException("--rh debe ser >= 0 (es " + rh + ")");
        }
        this.a = agents;
        this.room = room;
        this.p = params;
        this.log = log;
        this.recovery = recovery;
        this.rh = rh;
        this.rhWall = rh / 2;
        this.mixed = Math.max(rh, 2 * params.rMax());
        this.areaReachable = rh >= 2 * params.rMin();
        this.dt = params.dt();
        this.tsdmd = new TimeDrivenCpm(agents, room, params, log);
        final double vMax = Math.max(params.vdMax(), params.ve());
        this.grid = new CellGrid(room, params, mixed + (areaReachable ? 2 * vMax * dt : 0));
        final int n = agents.n();
        t0 = new double[n];
        count = new int[n];
        pending = new boolean[n];
        mode = new byte[n];
        seg = new int[n];
        stateStart = new double[n];
        cx = new int[n];
        cy = new int[n];
        next = new int[n];
        prev = new int[n];
        tsIds = new int[n];
        members = new int[n];
        inSet = new boolean[n];
        savedX = new double[n];
        savedY = new double[n];
        head = new int[grid.cells()];
        java.util.Arrays.fill(head, -1);
        final int[] active = a.active();
        final int n0 = a.activeCount();
        for (int k = 0; k < n0; k++) {
            final int i = active[k];
            a.scheme[i] = Agents.EDMD;
            mode[i] = recovery.segments() > 0 ? RECOVER : FREE;
            cx[i] = grid.cellX(a.x[i]);
            cy[i] = grid.cellY(a.y[i]);
            link(i);
        }
        // El criterio de pasaje en t = 0 (radios en r_min): quien tiene a alguien en el área empieza en TSDMD.
        for (int k = 0; k < n0; k++) {
            pending[active[k]] = !isClear(active[k], rh, rhWall);
        }
        passPending();
        edToTs = 0;
        for (int k = 0; k < n0; k++) {
            if (a.scheme[active[k]] == Agents.EDMD) {
                beginState(active[k]);
            }
        }
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
                    || ((q.topType == NEAR || q.topType == CONTACT)
                    && (a.phase[q.topB] == Agents.REMOVED || count[q.topB] != q.topCb))) {
                stale++;
                continue;
            }
            now = q.topTime;
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
                case CONTACT -> collapse(i, q.topB);
                case WALL -> collapse(i, -1);
                case ESCAPE_END -> endEscape(i);
                case LEVEL_END -> endLevel(i);
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
        passPending();
        final int[] active = a.active();
        for (int k = 0; k < a.activeCount(); k++) {
            final int i = active[k];
            if (a.scheme[i] == Agents.TSDMD && !a.contact[i] && a.r[i] >= p.rMax() && isClear(i, mixed, mixed / 2)) {
                a.scheme[i] = Agents.EDMD;
                mode[i] = FREE;
                tsToEd++;
                redirect(i);
            }
        }
        updateTsdmd();
    }

    /**
     * Pasa a TSDMD a los agentes marcados y, en cadena, a los agentes en EDMD que queden a menos de
     * {@code D} de uno recién pasado.
     */
    private void passPending() {
        final int[] active = a.active();
        int size = 0;
        for (int k = 0; k < a.activeCount(); k++) {
            if (pending[active[k]]) {
                members[size++] = active[k];
            }
        }
        for (int m = 0; m < size; m++) {
            final int i = members[m];
            sync(i);
            pending[i] = false;
            a.scheme[i] = Agents.TSDMD;
            count[i]++;
            edToTs++;
            for (int ny = Math.max(0, cy[i] - 1); ny <= Math.min(grid.my - 1, cy[i] + 1); ny++) {
                for (int nx = Math.max(0, cx[i] - 1); nx <= Math.min(grid.mx - 1, cx[i] + 1); nx++) {
                    for (int l = head[nx + grid.mx * ny]; l >= 0; l = next[l]) {
                        if (a.scheme[l] == Agents.EDMD && !pending[l]
                                && Math.hypot(a.x[i] - posX(l), a.y[i] - posY(l)) <= mixed) {
                            pending[l] = true;
                            members[size++] = l;
                        }
                    }
                }
            }
        }
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
                            pushNear(i, j, mixed, tNext);
                        }
                    }
                }
            }
        }
    }

    /** ¿No hay ningún agente a {@code reach} o menos de {@code i} ni pared a {@code wallReach} o menos? */
    private boolean isClear(final int i, final double reach, final double wallReach) {
        final double xi = posX(i);
        final double yi = posY(i);
        for (int ny = Math.max(0, cy[i] - 1); ny <= Math.min(grid.my - 1, cy[i] + 1); ny++) {
            for (int nx = Math.max(0, cx[i] - 1); nx <= Math.min(grid.mx - 1, cx[i] + 1); nx++) {
                for (int j = head[nx + grid.mx * ny]; j >= 0; j = next[j]) {
                    if (j != i && Math.hypot(xi - posX(j), yi - posY(j)) <= reach) {
                        return false;
                    }
                }
            }
        }
        for (int w = 0; w < room.wallCount(); w++) {
            if (wallDistance(xi, yi, room.wall(w)) <= wallReach) {
                return false;
            }
        }
        return true;
    }

    // ---------------------------------------------------------------------------------- EDMD

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
        predictNeighbors(i);
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
        pending[i] = false;
        count[i]++;
        log.add(now, i, EventLog.EXIT);
    }

    /**
     * Colapso en el instante actual: {@code i} (y {@code j} si es un contacto entre agentes) más todos
     * los agentes en EDMD que estén en contacto con alguno de ellos. Un agente en TSDMD en contacto suma
     * su versor de escape pero no colapsa acá: lo resuelve su paso del CPM.
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
                        if (!inSet[l] && a.scheme[l] == Agents.EDMD) {
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
            if (wallDistance(xi, yi, room.wall(w)) < a.r[i] - TOUCH) {
                return true;
            }
        }
        return false;
    }

    // ---------------------------------------------------------------------------------- predicción

    /** Todos los eventos futuros del agente en EDMD {@code i} con su trayectoria actual ({@code count[i]} ya incrementado). */
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
            final double tr = retireTime(room, x, y, vx, vy);
            if (tr < INF) {
                queue.push(now + tr, RETIRE, i, -1, ci, 0);
            }
            for (int w = 0; w < room.wallCount(); w++) {
                final double tw = wallTime(x, y, vx, vy, a.r[i], room.wall(w));
                if (tw < INF) {
                    queue.push(now + tw, WALL, i, w, ci, 0);
                }
                if (areaReachable) {
                    final double tn = wallTime(x, y, vx, vy, rhWall, room.wall(w));
                    if (tn < INF) {
                        queue.push(now + tn, NEAR_WALL, i, w, ci, 0);
                    }
                }
            }
        }
        predictNeighbors(i);
    }

    /**
     * Eventos del agente en EDMD {@code i} con sus vecinos: contacto y entrada al área con los que están
     * en EDMD; llegada a distancia {@code D} de los que están en TSDMD (vale hasta el paso siguiente).
     */
    private void predictNeighbors(final int i) {
        final double tNext = (step + 1) * dt;
        final int ci = count[i];
        for (int ny = Math.max(0, cy[i] - 1); ny <= Math.min(grid.my - 1, cy[i] + 1); ny++) {
            for (int nx = Math.max(0, cx[i] - 1); nx <= Math.min(grid.mx - 1, cx[i] + 1); nx++) {
                for (int j = head[nx + grid.mx * ny]; j >= 0; j = next[j]) {
                    if (j == i) {
                        continue;
                    }
                    if (a.scheme[j] == Agents.TSDMD) {
                        pushNear(i, j, mixed, tNext);
                        continue;
                    }
                    final double tc = approachTime(a.x[i] - posX(j), a.y[i] - posY(j), a.vx[i] - a.vx[j],
                            a.vy[i] - a.vy[j], a.r[i] + a.r[j]);
                    if (tc < INF) {
                        queue.push(now + tc, CONTACT, i, j, ci, count[j]);
                    }
                    if (areaReachable) {
                        pushNear(i, j, rh, INF);
                    }
                }
            }
        }
    }

    /** Predice cuándo {@code j} llega a distancia {@code reach} de {@code i} (EDMD); se descarta si cae después de {@code limit}. */
    private void pushNear(final int i, final int j, final double reach, final double limit) {
        final double tc = approachTime(posX(i) - posX(j), posY(i) - posY(j), a.vx[i] - a.vx[j],
                a.vy[i] - a.vy[j], reach);
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

    /** Pasos, pasajes entre esquemas, colapsos por eventos y eventos procesados por tipo, como objeto JSON. */
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
                .append(", \"collapses\": ").append(collapses)
                .append(", \"collapsedAgents\": ").append(collapsedAgents)
                .append(", \"radiusJumpCollapses\": ").append(jumpCollapses)
                .append('}').toString();
    }
}
