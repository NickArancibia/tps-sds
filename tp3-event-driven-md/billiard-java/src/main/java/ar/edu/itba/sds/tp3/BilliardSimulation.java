package ar.edu.itba.sds.tp3;

import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import java.util.PriorityQueue;

/**
 * Motor de dinámica molecular regida por eventos (Teórica 3, diapositiva 6):
 * <ol>
 *   <li>A1: condición inicial (recibida ya generada).</li>
 *   <li>A2: el próximo evento es el mínimo de la cola de prioridad de colisiones predichas.</li>
 *   <li>A3: se avanzan todas las partículas en MRU hasta ese instante.</li>
 *   <li>A4: el estado se guarda desde afuera, en el instante de cada evento (o cada k).</li>
 *   <li>A5: se actualizan las velocidades solo de las partículas que chocaron y se re-predicen
 *       únicamente sus colisiones futuras.</li>
 * </ol>
 * Las predicciones obsoletas quedan en la cola y se descartan al desencolarlas comparando los
 * contadores de colisiones (bibliografía: Sedgewick &amp; Wayne, COS 226).
 */
public final class BilliardSimulation {

    /** Resultado de procesar un evento. {@code goal} indica si fue el primer contacto con un arco. */
    public record Step(Event event, boolean goal) {
    }

    private final SimulationConfig config;
    private final Ball[] balls;
    private final List<Obstacle> obstacles;
    private final PriorityQueue<Event> queue = new PriorityQueue<>();
    private final Map<Event.Type, Long> processed = new EnumMap<>(Event.Type.class);
    private long stale;
    private double time;
    private int goals;
    private double t90 = Double.NaN;

    public BilliardSimulation(final SimulationConfig config, final List<Ball> initial) {
        if (initial.size() != config.n()) {
            throw new IllegalArgumentException("Se esperaban %d partículas y se recibieron %d"
                    .formatted(config.n(), initial.size()));
        }
        this.config = config;
        this.balls = initial.toArray(new Ball[0]);
        this.obstacles = config.obstacles();
        for (final Event.Type type : Event.Type.values()) {
            processed.put(type, 0L);
        }
        for (int i = 0; i < balls.length; i++) {
            predictWalls(i);
            predictObstacles(i);
            for (int j = i + 1; j < balls.length; j++) {
                predictPair(i, j);
            }
        }
    }

    public double time() {
        return time;
    }

    public int goals() {
        return goals;
    }

    /** Instante en que F_g alcanzó 0.9, o NaN si todavía no ocurrió. */
    public double t90() {
        return t90;
    }

    public boolean reachedT90() {
        return !Double.isNaN(t90);
    }

    public List<Ball> balls() {
        return List.of(balls);
    }

    public Map<Event.Type, Long> processedEvents() {
        return processed;
    }

    public long staleEvents() {
        return stale;
    }

    /** Eventos (válidos u obsoletos) que quedan en la cola. */
    public int queueSize() {
        return queue.size();
    }

    public double kineticEnergy() {
        double e = 0;
        for (final Ball b : balls) {
            e += b.kineticEnergy();
        }
        return e;
    }

    /** Instante del próximo evento válido (∞ si no hay más colisiones posibles). */
    public double nextEventTime() {
        final Event next = peekValid();
        return next == null ? Double.POSITIVE_INFINITY : next.time();
    }

    /** A3: vuelo libre de todas las partículas hasta {@code t} (no invalida ningún evento). */
    public void advanceTo(final double t) {
        if (t < time) {
            throw new IllegalArgumentException("No se puede retroceder el tiempo");
        }
        final double dt = t - time;
        if (dt > 0) {
            for (final Ball b : balls) {
                b.move(dt);
            }
        }
        time = t;
    }

    /** A2 + A3 + A5 para el próximo evento válido. */
    public Step processNextEvent() {
        final Event event = peekValid();
        if (event == null) {
            throw new IllegalStateException("No quedan eventos");
        }
        queue.poll();
        advanceTo(event.time());
        processed.merge(event.type(), 1L, Long::sum);

        final Ball a = balls[event.a()];
        boolean goal = false;
        switch (event.type()) {
            case WALL_X -> {
                goal = !a.used() && Math.abs(a.y() - config.w() / 2) <= config.d() / 2;
                if (goal) {
                    a.markUsed();
                    goals++;
                    if (Double.isNaN(t90) && goals >= config.goalsForT90()) {
                        t90 = time;
                    }
                }
                Collisions.bounceVerticalWall(a);
                repredict(event.a());
            }
            case WALL_Y -> {
                Collisions.bounceHorizontalWall(a);
                repredict(event.a());
            }
            case OBSTACLE -> {
                Collisions.bounceObstacle(a, obstacles.get(event.b()));
                repredict(event.a());
            }
            case PARTICLE -> {
                Collisions.bounceBalls(a, balls[event.b()]);
                repredict(event.a());
                repredict(event.b());
            }
            default -> throw new IllegalStateException("Tipo de evento desconocido");
        }
        return new Step(event, goal);
    }

    private Event peekValid() {
        while (!queue.isEmpty()) {
            final Event e = queue.peek();
            if (isValid(e)) {
                return e;
            }
            queue.poll();
            stale++;
        }
        return null;
    }

    private boolean isValid(final Event e) {
        if (balls[e.a()].collisions() != e.countA()) {
            return false;
        }
        return e.type() != Event.Type.PARTICLE || balls[e.b()].collisions() == e.countB();
    }

    private void repredict(final int i) {
        predictWalls(i);
        predictObstacles(i);
        for (int j = 0; j < balls.length; j++) {
            if (j != i) {
                predictPair(i, j);
            }
        }
    }

    private void predictWalls(final int i) {
        final Ball b = balls[i];
        final double tx = Collisions.timeToVerticalWall(b, config.l());
        if (tx != Collisions.NEVER) {
            queue.add(new Event(time + tx, Event.Type.WALL_X, i, -1, b.collisions(), 0));
        }
        final double ty = Collisions.timeToHorizontalWall(b, config.w());
        if (ty != Collisions.NEVER) {
            queue.add(new Event(time + ty, Event.Type.WALL_Y, i, -1, b.collisions(), 0));
        }
    }

    private void predictObstacles(final int i) {
        final Ball b = balls[i];
        for (int k = 0; k < obstacles.size(); k++) {
            final double t = Collisions.timeToObstacle(b, obstacles.get(k));
            if (t != Collisions.NEVER) {
                queue.add(new Event(time + t, Event.Type.OBSTACLE, i, k, b.collisions(), 0));
            }
        }
    }

    private void predictPair(final int i, final int j) {
        final double t = Collisions.timeToBall(balls[i], balls[j]);
        if (t != Collisions.NEVER) {
            queue.add(new Event(time + t, Event.Type.PARTICLE, i, j, balls[i].collisions(),
                    balls[j].collisions()));
        }
    }

    /**
     * Chequeo de consistencia (solo para depurar, O(N²)): ninguna partícula se superpone con otra,
     * con un obstáculo ni con las paredes más allá de {@code tolerance}.
     */
    public void verifyNoOverlaps(final double tolerance) {
        for (int i = 0; i < balls.length; i++) {
            final Ball a = balls[i];
            if (a.x() < a.radius() - tolerance || a.x() > config.l() - a.radius() + tolerance
                    || a.y() < a.radius() - tolerance || a.y() > config.w() - a.radius() + tolerance) {
                throw new IllegalStateException("t=%.6f: partícula %d fuera de la mesa (%.6f, %.6f)"
                        .formatted(time, a.id(), a.x(), a.y()));
            }
            for (final Obstacle o : obstacles) {
                final double dist = Math.hypot(a.x() - o.x(), a.y() - o.y());
                if (dist < a.radius() + o.radius() - tolerance) {
                    throw new IllegalStateException("t=%.6f: partícula %d dentro de un obstáculo"
                            .formatted(time, a.id()));
                }
            }
            for (int j = i + 1; j < balls.length; j++) {
                final Ball b = balls[j];
                final double dist = Math.hypot(a.x() - b.x(), a.y() - b.y());
                if (dist < a.radius() + b.radius() - tolerance) {
                    throw new IllegalStateException("t=%.6f: partículas %d y %d solapadas (dist %.3e)"
                            .formatted(time, a.id(), b.id(), dist));
                }
            }
        }
    }
}
