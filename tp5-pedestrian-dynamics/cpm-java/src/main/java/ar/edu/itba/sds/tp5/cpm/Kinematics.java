package ar.edu.itba.sds.tp5.cpm;

/**
 * Tiempos de eventos para trayectorias rectilíneas uniformes (EDMD puro e híbrido).
 */
public final class Kinematics {

    /** Umbral de acercamiento {@code Δx·Δv} (m²/s) para predecir un evento. */
    private static final double APPROACH = 1e-12;
    public static final double INF = Double.POSITIVE_INFINITY;

    private Kinematics() {
    }

    /**
     * Tiempo hasta que dos puntos que se acercan quedan a distancia {@code reach} (suma de radios,
     * radio contra un punto fijo o radio del área del híbrido). {@code 0} si ya están a esa distancia o
     * menos y acercándose; infinito si no se acercan o no llegan.
     */
    public static double approachTime(final double dx, final double dy, final double dvx, final double dvy,
                                      final double reach) {
        final double b = dx * dvx + dy * dvy;
        if (b >= -APPROACH) {
            return INF;
        }
        final double c = dx * dx + dy * dy - reach * reach;
        if (c <= 0) {
            return 0;
        }
        final double vv = dvx * dvx + dvy * dvy;
        final double disc = b * b - vv * c;
        if (disc < 0) {
            return INF;
        }
        return c / (-b + Math.sqrt(disc));
    }

    /** Tiempo hasta que el centro queda a distancia {@code r} del segmento de pared {@code s}. */
    public static double wallTime(final double x, final double y, final double vx, final double vy, final double r,
                                  final double[] s) {
        final double sx = s[2] - s[0];
        final double sy = s[3] - s[1];
        final double len = Math.hypot(sx, sy);
        final double ux = sx / len;
        final double uy = sy / len;
        final double rx = x - s[0];
        final double ry = y - s[1];
        final double side = -rx * uy + ry * ux;
        final double rate = -vx * uy + vy * ux;
        double best = INF;
        if (side * rate < 0) {
            final double gap = Math.abs(side) - r;
            final double t = gap <= 0 ? 0 : gap / Math.abs(rate);
            final double u = (rx + vx * t) * ux + (ry + vy * t) * uy;
            if (u >= 0 && u <= len) {
                best = t;
            }
        }
        best = Math.min(best, approachTime(rx, ry, vx, vy, r));
        return Math.min(best, approachTime(x - s[2], y - s[3], vx, vy, r));
    }

    /** Tiempo hasta salir del círculo de retiro de {@code room} con {@code y < 0}. */
    public static double retireTime(final Room room, final double x, final double y, final double vx,
                                    final double vy) {
        final double e = room.exitDistance();
        final double dx = x - room.doorCenterX();
        final double b = dx * vx + y * vy;
        final double c = dx * dx + y * y - e * e;
        final double vv = vx * vx + vy * vy;
        if (c >= 0) {
            if (y < 0) {
                return 0;
            }
            if (b >= 0) {
                return INF;
            }
        }
        final double disc = b * b - vv * c;
        if (disc < 0) {
            return INF;
        }
        final double t = (-b + Math.sqrt(disc)) / vv;
        return y + vy * t < 0 ? t : INF;
    }

    /** Parámetro {@code u ∈ [0, 1]} del punto del segmento {@code s} más cercano a {@code (x, y)}. */
    public static double segmentParam(final double x, final double y, final double[] s) {
        final double sx = s[2] - s[0];
        final double sy = s[3] - s[1];
        return Math.max(0, Math.min(1, ((x - s[0]) * sx + (y - s[1]) * sy) / (sx * sx + sy * sy)));
    }

    /** Distancia de {@code (x, y)} al segmento {@code s}. */
    public static double wallDistance(final double x, final double y, final double[] s) {
        final double u = segmentParam(x, y, s);
        return Math.hypot(x - (s[0] + u * (s[2] - s[0])), y - (s[1] + u * (s[3] - s[1])));
    }
}
