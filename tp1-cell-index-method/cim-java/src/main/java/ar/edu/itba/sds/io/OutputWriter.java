package ar.edu.itba.sds.io;

import ar.edu.itba.sds.common.model.NeighborLists;
import ar.edu.itba.sds.common.model.Particle;
import ar.edu.itba.sds.model.SystemConfig;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;

/**
 * Escritura de los resultados de una corrida.
 *
 * <p>La simulación se corre offline: la animación y los observables surgen de estos archivos. Por
 * eso se persiste <b>todo</b> lo necesario para analizar la corrida después (inputs, tiempos de
 * cada repetición, resultados) y no hace falta volver a ejecutar nada para graficar otra cosa.</p>
 */
public final class OutputWriter {

    private OutputWriter() {
    }

    /**
     * Archivo de vecinos: una fila por partícula con su id seguido de los ids de sus vecinas
     * (distancia borde a borde menor que rc).
     *
     * <pre>
     * 1 5 12 40
     * 2 7
     * 3
     * </pre>
     */
    public static void writeNeighbors(final Path path, final List<Particle> particles,
                                      final NeighborLists neighbors) throws IOException {
        Files.createDirectories(path.toAbsolutePath().getParent());
        try (BufferedWriter writer = Files.newBufferedWriter(path)) {
            for (int i = 0; i < particles.size(); i++) {
                final int[] ids = neighbors.neighborsOf(i);
                for (int k = 0; k < ids.length; k++) {
                    ids[k] = particles.get(ids[k]).id();
                }
                Arrays.sort(ids);
                final StringBuilder line = new StringBuilder().append(particles.get(i).id());
                for (final int id : ids) {
                    line.append(' ').append(id);
                }
                writer.write(line.toString());
                writer.newLine();
            }
        }
    }

    /**
     * Metadatos de la corrida: todo lo necesario para reproducirla e interpretarla sin volver a
     * ejecutarla, incluyendo los tiempos de cada repetición individual.
     */
    public static void writeRunMetadata(final Path path, final SystemConfig config,
                                        final String method, final long[] timesNs,
                                        final long generationTimeNs, final int totalPairs,
                                        final double cellSize, final Boolean verified)
            throws IOException {
        Files.createDirectories(path.toAbsolutePath().getParent());
        final double meanNs = mean(timesNs);
        final double stdNs = standardDeviation(timesNs);
        final StringBuilder json = new StringBuilder();
        json.append("{\n");
        json.append("  \"method\": \"").append(method).append("\",\n");
        json.append("  \"N\": ").append(config.n()).append(",\n");
        json.append("  \"L\": ").append(num(config.l())).append(",\n");
        json.append("  \"M\": ").append(config.m()).append(",\n");
        json.append("  \"rc\": ").append(num(config.rc())).append(",\n");
        json.append("  \"periodic\": ").append(config.periodic()).append(",\n");
        json.append("  \"seed\": ").append(config.seed()).append(",\n");
        json.append("  \"rMin\": ").append(num(config.rMin())).append(",\n");
        json.append("  \"rMax\": ").append(num(config.rMax())).append(",\n");
        json.append("  \"maxM\": ").append(config.maxM()).append(",\n");
        json.append("  \"cellSize\": ").append(num(cellSize)).append(",\n");
        json.append("  \"density\": ").append(num(config.density())).append(",\n");
        json.append("  \"repetitions\": ").append(timesNs.length).append(",\n");
        json.append("  \"generationTimeNs\": ").append(generationTimeNs).append(",\n");
        json.append("  \"meanTimeNs\": ").append(num(meanNs)).append(",\n");
        json.append("  \"stdTimeNs\": ").append(num(stdNs)).append(",\n");
        json.append("  \"meanTimeMs\": ").append(num(meanNs / 1e6)).append(",\n");
        json.append("  \"stdTimeMs\": ").append(num(stdNs / 1e6)).append(",\n");
        json.append("  \"neighborPairs\": ").append(totalPairs).append(",\n");
        json.append("  \"verifiedAgainstBruteForce\": ")
                .append(verified == null ? "null" : verified.toString()).append(",\n");
        json.append("  \"timesNs\": [");
        for (int i = 0; i < timesNs.length; i++) {
            json.append(i == 0 ? "" : ", ").append(timesNs[i]);
        }
        json.append("]\n}\n");
        Files.writeString(path, json.toString());
    }

    public static double mean(final long[] values) {
        double sum = 0;
        for (final long value : values) {
            sum += value;
        }
        return values.length == 0 ? 0 : sum / values.length;
    }

    /** Desvío estándar muestral (denominador n-1), que es lo que va en la barra de error. */
    public static double standardDeviation(final long[] values) {
        if (values.length < 2) {
            return 0;
        }
        final double mean = mean(values);
        double sum = 0;
        for (final long value : values) {
            final double diff = value - mean;
            sum += diff * diff;
        }
        return Math.sqrt(sum / (values.length - 1));
    }

    private static String num(final double value) {
        return String.format(Locale.US, "%.6f", value);
    }
}
