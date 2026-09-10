package ar.edu.itba.sds.tp3.io;

import ar.edu.itba.sds.tp3.Ball;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

/**
 * Condición inicial de las partículas: una línea {@code x y vx vy} por partícula (radio y masa
 * vienen de la configuración). Permite generar las condiciones iniciales de la competencia con
 * anticipación y correr después desde ese estado exacto.
 */
public final class InitialStateFile {

    private InitialStateFile() {
    }

    public static void write(final Path path, final List<Ball> balls) throws IOException {
        Files.createDirectories(path.toAbsolutePath().getParent());
        try (BufferedWriter writer = Files.newBufferedWriter(path)) {
            for (final Ball b : balls) {
                writer.write(String.format(Locale.US, "%.17g %.17g %.17g %.17g",
                        b.x(), b.y(), b.vx(), b.vy()));
                writer.newLine();
            }
        }
    }

    public static List<Ball> read(final Path path, final double radius, final double mass)
            throws IOException {
        final List<Ball> balls = new ArrayList<>();
        for (final String raw : Files.readAllLines(path)) {
            final String line = raw.strip();
            if (line.isEmpty() || line.startsWith("#")) {
                continue;
            }
            final String[] p = line.split("\\s+");
            if (p.length != 4) {
                throw new IOException("%s: se esperaba 'x y vx vy' y se leyó '%s'".formatted(path, line));
            }
            balls.add(new Ball(balls.size() + 1, Double.parseDouble(p[0]), Double.parseDouble(p[1]),
                    Double.parseDouble(p[2]), Double.parseDouble(p[3]), radius, mass));
        }
        if (balls.isEmpty()) {
            throw new IOException("Condición inicial vacía: " + path);
        }
        return balls;
    }
}
