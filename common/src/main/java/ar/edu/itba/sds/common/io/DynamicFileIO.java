package ar.edu.itba.sds.common.io;

import ar.edu.itba.sds.common.model.Particle;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

/**
 * Archivo dinámico: un bloque por instante de tiempo.
 *
 * <pre>
 * t0
 * x1 y1 vx1 vy1
 * x2 y2 vx2 vy2
 * ...
 * xN yN vxN vyN
 * t1
 * ...
 * </pre>
 *
 * <p>El TP1 usa un único tiempo t0 (el método de detección de vecinos se aplica sobre un estado del
 * sistema en un instante dado) y velocidades nulas, pero el formato y este parser soportan varios
 * bloques desde ya porque los TPs siguientes simulan la dinámica.</p>
 */
public final class DynamicFileIO {

    private DynamicFileIO() {
    }

    /** Estado del sistema en un instante. Los arrays están indexados por (id - 1). */
    public record Snapshot(double time, double[] x, double[] y, double[] vx, double[] vy) {
    }

    public static void write(final Path path, final double time, final List<Particle> particles)
            throws IOException {
        writeAll(path, List.of(time), List.of(particles));
    }

    public static void writeAll(final Path path, final List<Double> times,
                                final List<List<Particle>> frames) throws IOException {
        Files.createDirectories(path.toAbsolutePath().getParent());
        try (BufferedWriter writer = Files.newBufferedWriter(path)) {
            for (int t = 0; t < times.size(); t++) {
                writer.write(StaticFileIO.format(times.get(t)));
                writer.newLine();
                for (final Particle p : frames.get(t)) {
                    writer.write("%s %s %s %s".formatted(
                            StaticFileIO.format(p.x()), StaticFileIO.format(p.y()),
                            StaticFileIO.format(p.vx()), StaticFileIO.format(p.vy())));
                    writer.newLine();
                }
            }
        }
    }

    /**
     * Escritor incremental: agrega un bloque por vez sin retener los frames anteriores en memoria.
     * Pensado para simulaciones dinámicas largas, donde acumular todos los estados antes de
     * escribir no escala.
     */
    public static final class Writer implements java.io.Closeable {

        private final BufferedWriter writer;

        public Writer(final Path path) throws IOException {
            Files.createDirectories(path.toAbsolutePath().getParent());
            this.writer = Files.newBufferedWriter(path);
        }

        public void writeFrame(final double time, final List<Particle> particles)
                throws IOException {
            writer.write(StaticFileIO.format(time));
            writer.newLine();
            for (final Particle p : particles) {
                writer.write("%s %s %s %s".formatted(
                        StaticFileIO.format(p.x()), StaticFileIO.format(p.y()),
                        StaticFileIO.format(p.vx()), StaticFileIO.format(p.vy())));
                writer.newLine();
            }
        }

        @Override
        public void close() throws IOException {
            writer.close();
        }
    }

    /**
     * Lee todos los bloques del archivo.
     *
     * @param n cantidad de partículas por bloque (viene del archivo estático).
     */
    public static List<Snapshot> read(final Path path, final int n) throws IOException {
        final List<String> lines = StaticFileIO.readMeaningfulLines(path);
        final List<Snapshot> snapshots = new ArrayList<>();
        int cursor = 0;
        while (cursor < lines.size()) {
            final double time = Double.parseDouble(lines.get(cursor++).trim());
            if (cursor + n > lines.size()) {
                throw new IOException(("Archivo dinámico %s: el bloque t=%s tiene menos de %d "
                        + "partículas.").formatted(path, time, n));
            }
            final double[] x = new double[n];
            final double[] y = new double[n];
            final double[] vx = new double[n];
            final double[] vy = new double[n];
            for (int i = 0; i < n; i++) {
                final String[] tokens = lines.get(cursor++).trim().split("\\s+");
                x[i] = Double.parseDouble(tokens[0]);
                y[i] = Double.parseDouble(tokens[1]);
                vx[i] = tokens.length > 2 ? Double.parseDouble(tokens[2]) : 0;
                vy[i] = tokens.length > 3 ? Double.parseDouble(tokens[3]) : 0;
            }
            snapshots.add(new Snapshot(time, x, y, vx, vy));
        }
        return snapshots;
    }

    /** Reconstruye las partículas de un bloque combinando archivo estático y dinámico. */
    public static List<Particle> toParticles(final StaticFileIO.StaticData staticData,
                                             final Snapshot snapshot) {
        final List<Particle> particles = new ArrayList<>(staticData.n());
        for (int i = 0; i < staticData.n(); i++) {
            particles.add(new Particle(i + 1, snapshot.x()[i], snapshot.y()[i],
                    staticData.radii()[i], snapshot.vx()[i], snapshot.vy()[i]));
        }
        return particles;
    }
}
