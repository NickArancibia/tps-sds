package ar.edu.itba.sds.tp4.billiard;

import java.util.Arrays;

/**
 * Detecta el comienzo de cada choque: un contacto (par de partículas, partícula–pared o
 * partícula–obstáculo) cuenta como choque nuevo solo en la primera evaluación de fuerzas en que
 * tiene {@code ξ > 0} después de una evaluación sin superposición. Mientras el contacto siga con
 * {@code ξ > 0} en evaluaciones consecutivas (el choque se está resolviendo durante varios
 * {@code dt}) no se vuelve a contar; si se separa ({@code ξ ≤ 0}) y vuelve a tocarse, es otro choque.
 *
 * <p>Por cada contacto se guarda la última evaluación en que tuvo {@code ξ > 0}; el choque empieza
 * si esa marca es anterior a la evaluación previa (tampoco cuenta dos veces un contacto informado
 * dos veces en la misma evaluación). Arreglos primitivos fijos (pares en {@code N × N}): sin
 * alocación por paso. Un contacto presente en la primera evaluación ({@code t = 0}) cuenta como
 * choque en {@code t = 0}.</p>
 */
public final class CollisionTracker {

    /** Tipo de contacto; {@code cli} es el nombre que va en {@code collisions.csv}. */
    public enum Kind {
        PARTICLE("particle"), WALL("wall"), OBSTACLE("obstacle");

        private final String cli;

        Kind(final String cli) {
            this.cli = cli;
        }

        public String cli() {
            return cli;
        }
    }

    /** Recibe cada choque nuevo, en la evaluación en que empieza. */
    @FunctionalInterface
    public interface Listener {
        /**
         * @param i     partícula (índice desde 0; en un par, la de menor índice)
         * @param other otra partícula u obstáculo (índice desde 0, obstáculos en el orden de
         *              {@link Table#obstacleX()}), o −1 si es la pared
         */
        void collision(double t, Kind kind, int i, int other);
    }

    private static final int NEVER = Integer.MIN_VALUE;

    private final int n;
    private final int obstacles;
    private final Listener listener;
    private final int[] pairSeen;
    private final int[] wallSeen;
    private final int[] obstacleSeen;
    private final long[] counts = new long[Kind.values().length];
    private int evaluation = -1;
    private double t;

    public CollisionTracker(final int n, final int obstacles, final Listener listener) {
        this.n = n;
        this.obstacles = obstacles;
        this.listener = listener;
        this.pairSeen = new int[n * n];
        this.wallSeen = new int[n];
        this.obstacleSeen = new int[n * obstacles];
        Arrays.fill(pairSeen, NEVER);
        Arrays.fill(wallSeen, NEVER);
        Arrays.fill(obstacleSeen, NEVER);
    }

    /** Llamar una vez por evaluación de fuerzas, antes de informar sus contactos. */
    void beginEvaluation(final double time) {
        evaluation++;
        t = time;
    }

    /** Par i–j con {@code ξ > 0} en esta evaluación. */
    void particle(final int i, final int j) {
        final int key = i < j ? i * n + j : j * n + i;
        if (starts(pairSeen, key)) {
            report(Kind.PARTICLE, Math.min(i, j), Math.max(i, j));
        }
    }

    /** Partícula i contra la pared con {@code ξ > 0} en esta evaluación. */
    void wall(final int i) {
        if (starts(wallSeen, i)) {
            report(Kind.WALL, i, -1);
        }
    }

    /** Partícula i contra el obstáculo {@code o} con {@code ξ > 0} en esta evaluación. */
    void obstacle(final int i, final int o) {
        if (starts(obstacleSeen, i * obstacles + o)) {
            report(Kind.OBSTACLE, i, o);
        }
    }

    /** Choques contados de un tipo. */
    public long count(final Kind kind) {
        return counts[kind.ordinal()];
    }

    private boolean starts(final int[] seen, final int key) {
        final boolean starts = seen[key] < evaluation - 1;
        seen[key] = evaluation;
        return starts;
    }

    private void report(final Kind kind, final int i, final int other) {
        counts[kind.ordinal()]++;
        listener.collision(t, kind, i, other);
    }
}
