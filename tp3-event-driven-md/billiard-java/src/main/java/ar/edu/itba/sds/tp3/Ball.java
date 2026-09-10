package ar.edu.itba.sds.tp3;

/**
 * Partícula móvil (disco rígido). Además de posición, velocidad, radio y masa lleva el estado
 * fresca/usada del enunciado y un contador de colisiones, que es lo que usa la cola de eventos
 * para detectar predicciones obsoletas (bibliografía: Sedgewick & Wayne).
 *
 * <p>El {@code id} es 1-based y coincide con el número de fila en los archivos de salida.</p>
 */
public final class Ball {

    private final int id;
    private final double radius;
    private final double mass;
    private double x;
    private double y;
    private double vx;
    private double vy;
    private boolean used;
    private int collisions;

    public Ball(final int id, final double x, final double y, final double vx, final double vy,
                final double radius, final double mass) {
        this.id = id;
        this.x = x;
        this.y = y;
        this.vx = vx;
        this.vy = vy;
        this.radius = radius;
        this.mass = mass;
    }

    public int id() {
        return id;
    }

    public double x() {
        return x;
    }

    public double y() {
        return y;
    }

    public double vx() {
        return vx;
    }

    public double vy() {
        return vy;
    }

    public double radius() {
        return radius;
    }

    public double mass() {
        return mass;
    }

    public boolean used() {
        return used;
    }

    public int collisions() {
        return collisions;
    }

    /** Vuelo libre (MRU) durante {@code dt}. */
    void move(final double dt) {
        x += vx * dt;
        y += vy * dt;
    }

    void setVelocity(final double vx, final double vy) {
        this.vx = vx;
        this.vy = vy;
    }

    void markUsed() {
        used = true;
    }

    void countCollision() {
        collisions++;
    }

    public double kineticEnergy() {
        return 0.5 * mass * (vx * vx + vy * vy);
    }

    public double speed() {
        return Math.sqrt(vx * vx + vy * vy);
    }
}
