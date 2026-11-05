package ar.edu.itba.sds.tp5.cpm;

/**
 * Parámetros del CPM (Baglietto &amp; Parisi, PRE 83, 056117, 2011).
 *
 * <p>{@code rMin}, {@code rMax} y {@code vdMax} los fija el enunciado; {@code beta}, {@code tau} y
 * {@code ve = vdMax} salen del paper. El paso temporal es una regla del modelo (Ec. 2 del paper) y
 * por eso se deriva de los demás parámetros en lugar de ser un input.</p>
 *
 * @param rMin  radio mínimo (m)
 * @param rMax  radio máximo (m)
 * @param vdMax rapidez deseada de un agente libre (m/s)
 * @param ve    rapidez de escape (m/s)
 * @param beta  exponente de la relación rapidez–radio
 * @param tau   tiempo característico de crecimiento del radio (s)
 */
public record CpmParams(double rMin, double rMax, double vdMax, double ve, double beta, double tau) {

    public CpmParams {
        if (!(rMin > 0 && rMax > rMin)) {
            throw new IllegalArgumentException("Se requiere 0 < rmin < rmax (rmin = " + rMin + ", rmax = " + rMax + ")");
        }
        if (!(vdMax > 0 && ve > 0 && beta > 0 && tau > 0)) {
            throw new IllegalArgumentException("vd, ve, beta y tau deben ser positivos");
        }
    }

    /** Ec. (2): {@code Δt = r_min / (2 max(v_dmax, v_e))}. */
    public double dt() {
        return rMin / (2 * Math.max(vdMax, ve));
    }

    /** Ec. (8): crecimiento del radio por paso sin contactos, {@code Δr = r_max Δt / τ}. */
    public double radiusIncrement() {
        return rMax * dt() / tau;
    }

    /** Ec. (1): {@code v_d(r) = v_dmax ((r − r_min)/(r_max − r_min))^β}. */
    public double desiredSpeed(final double r) {
        final double f = (r - rMin) / (rMax - rMin);
        return f <= 0 ? 0 : vdMax * Math.pow(Math.min(f, 1), beta);
    }
}
