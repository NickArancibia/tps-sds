package ar.edu.itba.sds.common.model;

/**
 * Una partícula del sistema.
 *
 * <p>El TP1 trabaja sobre una "foto estática" (un único tiempo t0) y las velocidades son cero,
 * pero se modelan desde ya porque los TPs siguientes simulan la dinámica del sistema.</p>
 *
 * <p>El {@code id} es 1-based: coincide con el número de fila en los archivos estático y dinámico,
 * que es la identidad de la partícula según el formato de la cátedra.</p>
 */
public final class Particle {

    private final int id;
    private final double radius;
    private double x;
    private double y;
    private double vx;
    private double vy;

    public Particle(final int id, final double x, final double y, final double radius) {
        this(id, x, y, radius, 0, 0);
    }

    public Particle(final int id, final double x, final double y, final double radius,
                    final double vx, final double vy) {
        this.id = id;
        this.x = x;
        this.y = y;
        this.radius = radius;
        this.vx = vx;
        this.vy = vy;
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

    public double radius() {
        return radius;
    }

    public double vx() {
        return vx;
    }

    public double vy() {
        return vy;
    }

    public void setPosition(final double x, final double y) {
        this.x = x;
        this.y = y;
    }

    public void setVelocity(final double vx, final double vy) {
        this.vx = vx;
        this.vy = vy;
    }

    @Override
    public String toString() {
        return "Particle[id=%d, x=%.4f, y=%.4f, r=%.4f]".formatted(id, x, y, radius);
    }
}
