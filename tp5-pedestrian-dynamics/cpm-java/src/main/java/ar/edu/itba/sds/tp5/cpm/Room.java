package ar.edu.itba.sds.tp5.cpm;

/**
 * Habitación cuadrada {@code [0, L] × [0, L]} con una única puerta de ancho {@code d} centrada en la
 * pared inferior ({@code y = 0}, entre {@code xe1} y {@code xe2}). Afuera ({@code y < 0}) no hay
 * paredes.
 *
 * <p>Las paredes son segmentos de espesor nulo: el contacto con una pared se evalúa contra su punto
 * más cercano al centro del agente, así que los bordes de la puerta (extremos de los segmentos
 * inferiores) no necesitan un caso especial.</p>
 */
public final class Room {

    /** Fracción de la puerta, desde cada borde, excluida como target (regla del paper, Sec. III B). */
    private static final double DOOR_MARGIN = 0.2;

    private final double l;
    private final double d;
    private final double exitDistance;
    /** Segmentos de pared: {x1, y1, x2, y2}. */
    private final double[][] walls;

    /**
     * @param l            lado de la habitación (m)
     * @param d            ancho de la puerta (m)
     * @param exitDistance distancia al centro de la puerta, del lado de afuera, a la que el agente se
     *                     retira (m); el segundo target está a esa distancia de la línea de la puerta
     */
    public Room(final double l, final double d, final double exitDistance) {
        if (!(l > 0 && d > 0 && d < l && exitDistance > 0)) {
            throw new IllegalArgumentException("Geometría inválida: L = " + l + ", d = " + d);
        }
        this.l = l;
        this.d = d;
        this.exitDistance = exitDistance;
        final double xe1 = xe1();
        final double xe2 = xe2();
        this.walls = new double[][]{
                {0, 0, 0, l},      // izquierda
                {l, 0, l, l},      // derecha
                {0, l, l, l},      // superior
                {0, 0, xe1, 0},    // inferior, a la izquierda de la puerta
                {xe2, 0, l, 0},    // inferior, a la derecha de la puerta
        };
    }

    public double l() {
        return l;
    }

    public double d() {
        return d;
    }

    public double exitDistance() {
        return exitDistance;
    }

    public double xe1() {
        return 0.5 * (l - d);
    }

    public double xe2() {
        return 0.5 * (l + d);
    }

    public double doorCenterX() {
        return 0.5 * l;
    }

    /** Extremo izquierdo de la franja de la puerta usada como target. */
    public double bandMin() {
        return xe1() + DOOR_MARGIN * d;
    }

    /** Extremo derecho de la franja de la puerta usada como target. */
    public double bandMax() {
        return xe1() + (1 - DOOR_MARGIN) * d;
    }

    /** Ordenada del segundo target {@code (x_i, −exitDistance)}, del lado de afuera. */
    public double exitTargetY() {
        return -exitDistance;
    }

    /** ¿El agente ya se alejó {@code exitDistance} del centro de la puerta (del lado de afuera)? */
    public boolean hasLeft(final double x, final double y) {
        final double dx = x - doorCenterX();
        return y < 0 && dx * dx + y * y >= exitDistance * exitDistance;
    }

    public int wallCount() {
        return walls.length;
    }

    /** Segmento {@code w} como {x1, y1, x2, y2}. No modificar. */
    public double[] wall(final int w) {
        return walls[w];
    }
}
