package ar.edu.itba.sds.tp5.cpm;

/**
 * Restricción de pared rígida sobre el cuerpo (agregado propio, no es parte del CPM del paper).
 *
 * <p>El cuerpo de un agente es el disco de radio {@code r_min} (Martin &amp; Parisi, Physica A 633,
 * 2024, Sec. 3.1) y las paredes son rígidas (enunciado). El escape del CPM suma un versor por
 * contacto y la pared pesa como un agente: si varios agentes empujan contra uno que toca la pared,
 * el escape puede apuntar hacia ella y meter el cuerpo adentro, o incluso atravesarla.</p>
 *
 * <p>Regla, aplicada a la velocidad ya calculada con las reglas del CPM y antes de mover: para cada
 * pared con {@code d} = distancia del centro a su punto más cercano {@code p} y
 * {@code n = (x − p)/d}, si la componente normal {@code v_n = v·n} es entrante ({@code v_n < 0}) y el
 * paso dejaría el centro a menos de {@code r_min} de la pared ({@code d + v_n Δt < r_min}), se la
 * reemplaza por {@code v_n' = −max(0, d − r_min)/Δt}: el cuerpo termina tocando la pared. La
 * componente tangencial no cambia, y si la velocidad se aleja de la pared tampoco se toca.</p>
 */
public final class RigidWalls {

    private RigidWalls() {
    }

    /**
     * Ajusta {@code (vx[i], vy[i])} contra todas las paredes de {@code room}.
     *
     * @return {@code true} si alguna pared recortó la velocidad
     */
    public static boolean limit(final Agents a, final int i, final Room room, final double rMin, final double dt) {
        final double xi = a.x[i];
        final double yi = a.y[i];
        boolean limited = false;
        for (int w = 0; w < room.wallCount(); w++) {
            final double reach = Math.hypot(a.vx[i], a.vy[i]) * dt;
            final double[] s = room.wall(w);
            final double sx = s[2] - s[0];
            final double sy = s[3] - s[1];
            final double u = Math.max(0, Math.min(1, ((xi - s[0]) * sx + (yi - s[1]) * sy) / (sx * sx + sy * sy)));
            final double dx = xi - (s[0] + u * sx);
            final double dy = yi - (s[1] + u * sy);
            final double d = Math.hypot(dx, dy);
            if (d == 0 || d - reach >= rMin) {
                continue;
            }
            final double nx = dx / d;
            final double ny = dy / d;
            final double vn = a.vx[i] * nx + a.vy[i] * ny;
            final double vnMin = -Math.max(0, d - rMin) / dt;
            if (vn < vnMin) {
                a.vx[i] += (vnMin - vn) * nx;
                a.vy[i] += (vnMin - vn) * ny;
                limited = true;
            }
        }
        return limited;
    }
}
