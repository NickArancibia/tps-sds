package ar.edu.itba.sds.tp2.io;

import ar.edu.itba.sds.tp2.SimulationConfig;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Locale;

/**
 * Escritura de los archivos propios del TP2 (además de los static/dynamic del formato de cátedra).
 *
 * <p>La simulación corre offline: se persiste todo lo necesario (inputs, observables por paso,
 * tiempos del CIM) para que el post-proceso pueda generar cualquier gráfico o animación sin volver
 * a correr nada.</p>
 */
public final class RunWriter {

    private RunWriter() {
    }

    /**
     * CSV de observables por paso: tiempo, polarización v_a y fracción del cluster más grande S.
     *
     * <p>Se escribe una fila por paso (no promedios): el criterio de estacionario y los promedios
     * se deciden en el post-proceso.</p>
     */
    public static final class ObservablesWriter implements java.io.Closeable {

        private final BufferedWriter writer;

        public ObservablesWriter(final Path path) throws IOException {
            Files.createDirectories(path.toAbsolutePath().getParent());
            this.writer = Files.newBufferedWriter(path);
            writer.write("time,polarization,largest_cluster_fraction");
            writer.newLine();
        }

        public void write(final double time, final double polarization, final double s)
                throws IOException {
            writer.write(String.format(Locale.US, "%.6f,%.6f,%.6f", time, polarization, s));
            writer.newLine();
        }

        @Override
        public void close() throws IOException {
            writer.close();
        }
    }

    /**
     * Metadatos de la corrida: todos los inputs y los tiempos de cada llamada al CIM (punto g:
     * comparación de performance contra el TP1).
     */
    public static void writeRunMetadata(final Path path, final SimulationConfig config,
                                        final long wallTimeNs, final long[] cimTimesNs)
            throws IOException {
        Files.createDirectories(path.toAbsolutePath().getParent());
        final double mean = mean(cimTimesNs);
        final double std = standardDeviation(cimTimesNs);
        final StringBuilder json = new StringBuilder();
        json.append("{\n");
        json.append("  \"model\": \"").append(config.model()).append("\",\n");
        json.append("  \"N\": ").append(config.n()).append(",\n");
        json.append("  \"L\": ").append(num(config.l())).append(",\n");
        json.append("  \"density\": ").append(num(config.density())).append(",\n");
        json.append("  \"rc\": ").append(num(config.rc())).append(",\n");
        json.append("  \"eta\": ").append(num(config.eta())).append(",\n");
        json.append("  \"speed\": ").append(num(config.speed())).append(",\n");
        json.append("  \"dt\": ").append(num(config.dt())).append(",\n");
        json.append("  \"steps\": ").append(config.steps()).append(",\n");
        json.append("  \"seed\": ").append(config.seed()).append(",\n");
        json.append("  \"M\": ").append(config.m()).append(",\n");
        json.append("  \"outputEvery\": ").append(config.outputEvery()).append(",\n");
        json.append("  \"periodic\": true,\n");
        json.append("  \"wallTimeMs\": ").append(num(wallTimeNs / 1e6)).append(",\n");
        json.append("  \"cimCalls\": ").append(cimTimesNs.length).append(",\n");
        json.append("  \"cimMeanTimeMs\": ").append(num(mean / 1e6)).append(",\n");
        json.append("  \"cimStdTimeMs\": ").append(num(std / 1e6)).append(",\n");
        json.append("  \"cimTimesNs\": [");
        for (int i = 0; i < cimTimesNs.length; i++) {
            json.append(i == 0 ? "" : ", ").append(cimTimesNs[i]);
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

    /** Desvío estándar muestral (denominador n-1). */
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
