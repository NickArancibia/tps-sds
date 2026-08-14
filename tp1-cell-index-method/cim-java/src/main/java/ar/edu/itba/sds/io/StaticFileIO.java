package ar.edu.itba.sds.io;

import ar.edu.itba.sds.model.Particle;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Archivo estático: la información que no cambia en el tiempo.
 *
 * <pre>
 * N              (cantidad total de partículas)
 * L              (lado del área de simulación)
 * r1 c1          (radio y propiedad/color de la partícula 1)
 * r2 c2
 * ...
 * rN cN
 * </pre>
 *
 * <p>El número de fila es la identidad de la partícula (1, 2, ..., N).</p>
 */
public final class StaticFileIO {

    /** Color por defecto de las partículas ("propiedad" en el formato de la cátedra). */
    public static final String DEFAULT_COLOR = "#1f77b4";

    private StaticFileIO() {
    }

    /** Datos del archivo estático. Los radios están indexados por (id - 1). */
    public record StaticData(int n, double l, double[] radii, String[] colors) {
    }

    public static void write(final Path path, final double l, final List<Particle> particles)
            throws IOException {
        Files.createDirectories(path.toAbsolutePath().getParent());
        try (BufferedWriter writer = Files.newBufferedWriter(path)) {
            writer.write(Integer.toString(particles.size()));
            writer.newLine();
            writer.write(format(l));
            writer.newLine();
            for (final Particle p : particles) {
                writer.write(format(p.radius()) + " " + DEFAULT_COLOR);
                writer.newLine();
            }
        }
    }

    public static StaticData read(final Path path) throws IOException {
        final List<String> lines = readMeaningfulLines(path);
        if (lines.size() < 2) {
            throw new IOException("Archivo estático incompleto: " + path);
        }
        final int n = Integer.parseInt(lines.get(0).trim());
        final double l = Double.parseDouble(lines.get(1).trim());
        if (lines.size() < 2 + n) {
            throw new IOException(("Archivo estático %s declara N=%d pero sólo tiene %d filas de "
                    + "partículas.").formatted(path, n, lines.size() - 2));
        }
        final double[] radii = new double[n];
        final String[] colors = new String[n];
        for (int i = 0; i < n; i++) {
            final String[] tokens = lines.get(2 + i).trim().split("\\s+");
            radii[i] = Double.parseDouble(tokens[0]);
            colors[i] = tokens.length > 1 ? tokens[1] : DEFAULT_COLOR;
        }
        return new StaticData(n, l, radii, colors);
    }

    static List<String> readMeaningfulLines(final Path path) throws IOException {
        final List<String> result = new ArrayList<>();
        for (final String line : Files.readAllLines(path)) {
            if (!line.isBlank() && !line.trim().startsWith("#")) {
                result.add(line);
            }
        }
        return result;
    }

    static String format(final double value) {
        return String.format(Locale.US, "%.6f", value);
    }
}
