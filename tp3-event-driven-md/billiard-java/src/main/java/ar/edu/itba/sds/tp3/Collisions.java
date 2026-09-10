package ar.edu.itba.sds.tp3;

/**
 * Física de las colisiones (Teórica 3): tiempos de choque en MRU y velocidades post-choque para
 * choques elásticos (coeficientes de restitución c_n = c_t = 1).
 */
public final class Collisions {

    public static final double NEVER = Double.POSITIVE_INFINITY;

    private Collisions() {
    }

    /** Tiempo hasta tocar una pared vertical (x = 0 o x = L). */
    public static double timeToVerticalWall(final Ball p, final double l) {
        if (p.vx() > 0) {
            return clamp((l - p.radius() - p.x()) / p.vx());
        }
        if (p.vx() < 0) {
            return clamp((p.radius() - p.x()) / p.vx());
        }
        return NEVER;
    }

    /** Tiempo hasta tocar una pared horizontal (y = 0 o y = W). */
    public static double timeToHorizontalWall(final Ball p, final double w) {
        if (p.vy() > 0) {
            return clamp((w - p.radius() - p.y()) / p.vy());
        }
        if (p.vy() < 0) {
            return clamp((p.radius() - p.y()) / p.vy());
        }
        return NEVER;
    }

    public static double timeToBall(final Ball i, final Ball j) {
        return timeToContact(j.x() - i.x(), j.y() - i.y(), j.vx() - i.vx(), j.vy() - i.vy(),
                i.radius() + j.radius());
    }

    public static double timeToObstacle(final Ball p, final Obstacle o) {
        return timeToContact(o.x() - p.x(), o.y() - p.y(), -p.vx(), -p.vy(),
                p.radius() + o.radius());
    }

    /**
     * Tiempo hasta que la distancia entre centros sea {@code sigma}, con {@code Δr = r_j - r_i} y
     * {@code Δv = v_j - v_i} (diapositiva 14):
     * <pre>
     *   t_c = ∞                                   si Δv·Δr ≥ 0 (se alejan)
     *   t_c = ∞                                   si d < 0     (pasan de largo)
     *   t_c = -(Δv·Δr + √d) / (Δv·Δv)             en otro caso
     *   d   = (Δv·Δr)² - (Δv·Δv) (Δr·Δr - σ²)
     * </pre>
     */
    public static double timeToContact(final double dx, final double dy, final double dvx,
                                       final double dvy, final double sigma) {
        final double dvdr = dvx * dx + dvy * dy;
        if (dvdr >= 0) {
            return NEVER;
        }
        final double dvdv = dvx * dvx + dvy * dvy;
        final double drdr = dx * dx + dy * dy;
        final double d = dvdr * dvdr - dvdv * (drdr - sigma * sigma);
        if (d < 0) {
            return NEVER;
        }
        return clamp(-(dvdr + Math.sqrt(d)) / dvdv);
    }

    /** Pared vertical: se invierte la componente x. */
    public static void bounceVerticalWall(final Ball p) {
        p.setVelocity(-p.vx(), p.vy());
        p.countCollision();
    }

    /** Pared horizontal: se invierte la componente y. */
    public static void bounceHorizontalWall(final Ball p) {
        p.setVelocity(p.vx(), -p.vy());
        p.countCollision();
    }

    /**
     * Choque elástico entre dos discos (diapositiva 20), a partir del impulso
     * {@code J = 2 m_i m_j (Δv·Δr) / (σ (m_i + m_j))}, {@code J_x = J Δx/σ}, {@code J_y = J Δy/σ}.
     */
    public static void bounceBalls(final Ball i, final Ball j) {
        final double dx = j.x() - i.x();
        final double dy = j.y() - i.y();
        final double dvx = j.vx() - i.vx();
        final double dvy = j.vy() - i.vy();
        final double dvdr = dvx * dx + dvy * dy;
        final double sigma = i.radius() + j.radius();
        final double impulse = 2 * i.mass() * j.mass() * dvdr / (sigma * (i.mass() + j.mass()));
        final double jx = impulse * dx / sigma;
        final double jy = impulse * dy / sigma;
        i.setVelocity(i.vx() + jx / i.mass(), i.vy() + jy / i.mass());
        j.setVelocity(j.vx() - jx / j.mass(), j.vy() - jy / j.mass());
        i.countCollision();
        j.countCollision();
    }

    /**
     * Choque elástico contra un obstáculo fijo: límite m_j → ∞ del anterior, equivalente al
     * operador de colisión R(-α) S(1, 1) R(α) (diapositivas 22-24): se invierte la componente
     * normal y se conserva la tangencial, {@code v' = v - 2 (v·ê_n) ê_n}.
     */
    public static void bounceObstacle(final Ball p, final Obstacle o) {
        double nx = p.x() - o.x();
        double ny = p.y() - o.y();
        final double norm = Math.sqrt(nx * nx + ny * ny);
        nx /= norm;
        ny /= norm;
        final double vn = p.vx() * nx + p.vy() * ny;
        p.setVelocity(p.vx() - 2 * vn * nx, p.vy() - 2 * vn * ny);
        p.countCollision();
    }

    /**
     * Por redondeo una partícula puede quedar una fracción de epsilon "del lado equivocado" del
     * contacto y dar un tiempo levemente negativo: se trata como colisión inmediata.
     */
    private static double clamp(final double t) {
        return t < 0 ? 0 : t;
    }
}
