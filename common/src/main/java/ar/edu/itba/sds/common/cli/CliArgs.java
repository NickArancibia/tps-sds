package ar.edu.itba.sds.common.cli;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * Parseo de los argumentos de línea de comandos, compartido por los dos ejecutables del proyecto
 * ({@code Main} y {@code BenchmarkRunner}).
 *
 * <p>Formato: {@code --clave valor} para opciones con valor y {@code --flag} para banderas (que
 * quedan mapeadas al string {@code "true"}).</p>
 */
public final class CliArgs {

    private final Map<String, String> options;

    private CliArgs(final Map<String, String> options) {
        this.options = options;
    }

    public static CliArgs parse(final String[] args) {
        final Map<String, String> options = new HashMap<>();
        for (int i = 0; i < args.length; i++) {
            final String arg = args[i];
            if (!arg.startsWith("--")) {
                throw new IllegalArgumentException("Argumento inesperado: " + arg);
            }
            final String key = arg.substring(2);
            if (i + 1 < args.length && !args[i + 1].startsWith("--")) {
                options.put(key, args[++i]);
            } else {
                options.put(key, "true");
            }
        }
        return new CliArgs(options);
    }

    public boolean has(final String key) {
        return options.containsKey(key);
    }

    public String string(final String key, final String fallback) {
        return options.getOrDefault(key, fallback);
    }

    public int integer(final String key, final int fallback) {
        return Integer.parseInt(options.getOrDefault(key, Integer.toString(fallback)));
    }

    public long longValue(final String key, final long fallback) {
        return Long.parseLong(options.getOrDefault(key, Long.toString(fallback)));
    }

    public double number(final String key, final double fallback) {
        return Double.parseDouble(options.getOrDefault(key, Double.toString(fallback)));
    }

    /** Lista de enteros separados por coma, p. ej. {@code --N 100,500,1000}. */
    public List<Integer> integerList(final String key, final List<Integer> fallback) {
        final String raw = options.get(key);
        if (raw == null || raw.isBlank() || "true".equals(raw)) {
            return fallback;
        }
        final List<Integer> values = new ArrayList<>();
        for (final String token : raw.split(",")) {
            values.add(Integer.parseInt(token.trim()));
        }
        return values;
    }

    /** Devuelve el mapa crudo, para casos puntuales que necesitan distinguir "ausente" de default. */
    public Map<String, String> raw() {
        return options;
    }

    public static String format(final double value) {
        return String.format(Locale.US, "%.6f", value);
    }
}
