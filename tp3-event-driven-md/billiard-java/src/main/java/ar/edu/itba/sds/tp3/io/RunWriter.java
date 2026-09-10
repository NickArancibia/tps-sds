package ar.edu.itba.sds.tp3.io;

import ar.edu.itba.sds.tp3.Ball;
import ar.edu.itba.sds.tp3.BilliardSimulation;
import ar.edu.itba.sds.tp3.Event;
import ar.edu.itba.sds.tp3.Obstacle;
import ar.edu.itba.sds.tp3.SimulationConfig;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * Escritura de los archivos de una corrida. La simulación corre offline: se persiste todo lo
 * necesario (inputs, goles, estado a intervalos fijos, energía, tiempos) para que el post-proceso
 * pueda calcular cualquier observable o animación sin volver a simular.
 */
public final class RunWriter {

    private RunWriter() {
    }

    /**
     * Archivo estático (lo que no cambia en el tiempo):
     * <pre>
     * N
     * L W d
     * r1 m1
     * ...
     * rN mN
     * K
     * x1 y1 R1        (obstáculos)
     * ...
     * </pre>
     */
    public static void writeStatic(final Path path, final SimulationConfig config,
                                   final List<Ball> balls) throws IOException {
        Files.createDirectories(path.toAbsolutePath().getParent());
        try (BufferedWriter writer = Files.newBufferedWriter(path)) {
            writer.write(Integer.toString(balls.size()));
            writer.newLine();
            writer.write("%s %s %s".formatted(num(config.l()), num(config.w()), num(config.d())));
            writer.newLine();
            for (final Ball b : balls) {
                writer.write("%s %s".formatted(num(b.radius()), num(b.mass())));
                writer.newLine();
            }
            writer.write(Integer.toString(config.obstacles().size()));
            writer.newLine();
            for (final Obstacle o : config.obstacles()) {
                writer.write("%s %s %s".formatted(num(o.x()), num(o.y()), num(o.radius())));
                writer.newLine();
            }
        }
    }

    /**
     * Bloques de estado del sistema: {@code t} y luego una línea {@code x y vx vy estado} por
     * partícula (estado 0 = fresca, 1 = usada; va por bloque porque cambia en el tiempo). Un
     * bloque cada {@code every} eventos, en el instante del evento, como pide el enunciado.
     */
    public static final class DynamicWriter implements java.io.Closeable {

        private final BufferedWriter writer;

        public DynamicWriter(final Path path) throws IOException {
            Files.createDirectories(path.toAbsolutePath().getParent());
            this.writer = Files.newBufferedWriter(path);
        }

        public void writeFrame(final double time, final List<Ball> balls) throws IOException {
            writer.write(num(time));
            writer.newLine();
            for (final Ball b : balls) {
                writer.write("%s %s %s %s %d".formatted(num(b.x()), num(b.y()), num(b.vx()),
                        num(b.vy()), b.used() ? 1 : 0));
                writer.newLine();
            }
        }

        @Override
        public void close() throws IOException {
            writer.close();
        }
    }

    /** CSV con una fila por gol: instante e id de la partícula. De acá salen N_g(t), F_g(t) y t_90. */
    public static final class GoalsWriter implements java.io.Closeable {

        private final BufferedWriter writer;

        public GoalsWriter(final Path path) throws IOException {
            Files.createDirectories(path.toAbsolutePath().getParent());
            this.writer = Files.newBufferedWriter(path);
            writer.write("time,id");
            writer.newLine();
        }

        public void write(final double time, final int id) throws IOException {
            writer.write(String.format(Locale.US, "%.9f,%d", time, id));
            writer.newLine();
        }

        @Override
        public void close() throws IOException {
            writer.close();
        }
    }

    /** Metadatos de la corrida: inputs, resultados escalares, conteos de eventos y tiempos. */
    public static void writeRunMetadata(final Path path, final SimulationConfig config,
                                        final String obstaclesFile, final String initialFile,
                                        final BilliardSimulation sim, final double energyInitial,
                                        final long loopTimeNs, final long wallTimeNs)
            throws IOException {
        Files.createDirectories(path.toAbsolutePath().getParent());
        final Map<Event.Type, Long> events = sim.processedEvents();
        long total = 0;
        for (final long count : events.values()) {
            total += count;
        }
        final StringBuilder json = new StringBuilder();
        json.append("{\n");
        json.append("  \"N\": ").append(config.n()).append(",\n");
        json.append("  \"L\": ").append(num(config.l())).append(",\n");
        json.append("  \"W\": ").append(num(config.w())).append(",\n");
        json.append("  \"d\": ").append(num(config.d())).append(",\n");
        json.append("  \"r\": ").append(num(config.radius())).append(",\n");
        json.append("  \"m\": ").append(num(config.mass())).append(",\n");
        json.append("  \"v0\": ").append(num(config.v0())).append(",\n");
        json.append("  \"tf\": ").append(num(config.tf())).append(",\n");
        json.append("  \"seed\": ").append(config.seed()).append(",\n");
        json.append("  \"every\": ").append(config.every()).append(",\n");
        json.append("  \"stopAtT90\": ").append(config.stopAtT90()).append(",\n");
        json.append("  \"areaFraction\": ").append(num(config.areaFraction())).append(",\n");
        json.append("  \"obstaclesFile\": ").append(str(obstaclesFile)).append(",\n");
        json.append("  \"initialFile\": ").append(str(initialFile)).append(",\n");
        json.append("  \"obstacles\": [");
        for (int k = 0; k < config.obstacles().size(); k++) {
            final Obstacle o = config.obstacles().get(k);
            json.append(k == 0 ? "" : ", ").append("[%s, %s, %s]".formatted(num(o.x()),
                    num(o.y()), num(o.radius())));
        }
        json.append("],\n");
        json.append("  \"goals\": ").append(sim.goals()).append(",\n");
        json.append("  \"goalsForT90\": ").append(config.goalsForT90()).append(",\n");
        json.append("  \"t90\": ").append(sim.reachedT90() ? num(sim.t90()) : "null").append(",\n");
        json.append("  \"finalTime\": ").append(num(sim.time())).append(",\n");
        json.append("  \"events\": {\n");
        json.append("    \"total\": ").append(total).append(",\n");
        json.append("    \"particle\": ").append(events.get(Event.Type.PARTICLE)).append(",\n");
        json.append("    \"obstacle\": ").append(events.get(Event.Type.OBSTACLE)).append(",\n");
        json.append("    \"wallX\": ").append(events.get(Event.Type.WALL_X)).append(",\n");
        json.append("    \"wallY\": ").append(events.get(Event.Type.WALL_Y)).append(",\n");
        json.append("    \"stale\": ").append(sim.staleEvents()).append(",\n");
        json.append("    \"queueSizeAtEnd\": ").append(sim.queueSize()).append("\n");
        json.append("  },\n");
        json.append("  \"kineticEnergyInitial\": ").append(sci(energyInitial)).append(",\n");
        json.append("  \"kineticEnergyFinal\": ").append(sci(sim.kineticEnergy())).append(",\n");
        json.append("  \"loopTimeMs\": ").append(num(loopTimeNs / 1e6)).append(",\n");
        json.append("  \"wallTimeMs\": ").append(num(wallTimeNs / 1e6)).append("\n");
        json.append("}\n");
        Files.writeString(path, json.toString());
    }

    public static String num(final double value) {
        return String.format(Locale.US, "%.6f", value);
    }

    private static String sci(final double value) {
        return String.format(Locale.US, "%.12e", value);
    }

    private static String str(final String value) {
        return value == null ? "null" : "\"" + value.replace("\\", "\\\\").replace("\"", "\\\"") + "\"";
    }
}
