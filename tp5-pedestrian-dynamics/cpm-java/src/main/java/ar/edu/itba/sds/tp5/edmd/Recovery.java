package ar.edu.itba.sds.tp5.edmd;

import ar.edu.itba.sds.tp5.cpm.CpmParams;

/**
 * Recuperación del radio y de la velocidad deseada en EDMD, como tramos de radio y rapidez
 * constantes (MRU) que empiezan cuando termina el escape.
 *
 * <p>En TSDMD, después del paso de escape el radio vale {@code r_k = r_min + k Δr} en el paso
 * {@code k = 1, …, K − 1} y llega a {@code r_max} en el paso {@code K} ({@code K = 9}: la
 * recuperación dura {@code (K − 1) Δt = 8 Δt} y el agente queda libre {@code 9 Δt} después del
 * contacto).</p>
 *
 * <p>{@code levels} es la cantidad de radios intermedios que se recorren: los primeros
 * {@code levels} radios de TSDMD, un {@code Δt} cada uno, con rapidez {@code v_d(r_k)} (Ec. 1); el
 * último se sostiene hasta el final de la recuperación. Con {@code levels = 0} el agente se queda en
 * {@code r_min} (rapidez nula) toda la recuperación; con {@code levels = K − 1} reproduce TSDMD.</p>
 */
public final class Recovery {

    private final int levels;
    /** Fin de cada tramo, medido desde el comienzo de la recuperación (s). */
    private final double[] end;
    private final double[] radius;
    private final double[] speed;

    public Recovery(final CpmParams p, final int levels) {
        final int max = maxLevels(p);
        if (levels < 0 || levels > max) {
            throw new IllegalArgumentException("--levels debe estar en [0, " + max + "] (es " + levels + ")");
        }
        this.levels = levels;
        final int segments = max == 0 ? 0 : Math.max(1, levels);
        end = new double[segments];
        radius = new double[segments];
        speed = new double[segments];
        final double dt = p.dt();
        for (int s = 0; s < segments; s++) {
            end[s] = s == segments - 1 ? max * dt : (s + 1) * dt;
            radius[s] = levels == 0 ? p.rMin() : p.rMin() + (s + 1) * p.radiusIncrement();
            speed[s] = p.desiredSpeed(radius[s]);
        }
    }

    /** {@code K − 1}: radios intermedios de TSDMD entre {@code r_min} y {@code r_max}. */
    public static int maxLevels(final CpmParams p) {
        final int k = (int) Math.ceil((p.rMax() - p.rMin()) / p.radiusIncrement() - 1e-9);
        return Math.max(0, k - 1);
    }

    public int segments() {
        return end.length;
    }

    public double end(final int s) {
        return end[s];
    }

    public double radius(final int s) {
        return radius[s];
    }

    public double speed(final int s) {
        return speed[s];
    }

    public int levels() {
        return levels;
    }
}
