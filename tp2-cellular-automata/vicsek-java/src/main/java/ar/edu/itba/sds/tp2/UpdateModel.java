package ar.edu.itba.sds.tp2;

/**
 * Regla de actualización de la dirección de cada partícula.
 *
 * <ul>
 *   <li>{@link #VICSEK}: promedia las direcciones de todos los vecinos <b>incluyéndose a sí
 *       misma</b> y le suma el ruido.</li>
 *   <li>{@link #VOTER}: elige <b>un solo vecino al azar</b> (nunca a sí misma), copia su dirección
 *       y le suma el ruido. Sin vecinos, conserva su propia dirección más el ruido.</li>
 * </ul>
 */
public enum UpdateModel {
    VICSEK,
    VOTER;

    public static UpdateModel fromString(final String value) {
        return switch (value.toLowerCase(java.util.Locale.US)) {
            case "vicsek", "standard" -> VICSEK;
            case "voter", "votante" -> VOTER;
            default -> throw new IllegalArgumentException(
                    "Modelo desconocido: '" + value + "'. Usar vicsek o voter.");
        };
    }
}
