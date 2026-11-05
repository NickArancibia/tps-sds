package ar.edu.itba.sds.tp5.cpm;

/**
 * Targets de la evacuación, según la posición del agente.
 *
 * <ul>
 *   <li>Dentro de la habitación ({@code y > 0}; regla del paper, Sec. III B): si el agente está
 *   frente a la franja central de la puerta ({@code [xe1 + 0.2 d, xe1 + 0.8 d]}), el target está
 *   justo enfrente, {@code (x_i, 0)}; si no, es su punto al azar de esa franja,
 *   {@code (bandX_i, 0)}. Vale también para un agente que cruzó y el atasco empujó de vuelta.</li>
 *   <li>Afuera ({@code y <= 0}): {@code (x_i, −exitDistance)}, justo enfrente; cada agente sale
 *   derecho, como en Martin &amp; Parisi, Physica A 633 (2024), Sec. 4.3. Un target común a todos
 *   los hacía converger y chocar una y otra vez después de la puerta.</li>
 * </ul>
 */
public final class Targets {

    private Targets() {
    }

    public static void update(final Agents a, final int i, final Room room) {
        final double xi = a.x[i];
        if (a.y[i] > 0) {
            a.tx[i] = xi >= room.bandMin() && xi <= room.bandMax() ? xi : a.bandX[i];
            a.ty[i] = 0;
        } else {
            a.tx[i] = xi;
            a.ty[i] = room.exitTargetY();
        }
    }
}
