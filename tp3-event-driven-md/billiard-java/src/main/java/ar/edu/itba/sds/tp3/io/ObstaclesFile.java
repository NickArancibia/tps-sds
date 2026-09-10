package ar.edu.itba.sds.tp3.io;

import ar.edu.itba.sds.tp3.Obstacle;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

/**
 * Archivo de configuración de obstáculos, con el formato exacto de la competencia: una línea por
 * obstáculo, {@code x y R} en metros separados por espacios. Se ignoran líneas vacías y las que
 * empiezan con {@code #}.
 */
public final class ObstaclesFile {

    private ObstaclesFile() {
    }

    public static List<Obstacle> read(final Path path) throws IOException {
        final List<Obstacle> obstacles = new ArrayList<>();
        int lineNumber = 0;
        for (final String raw : Files.readAllLines(path)) {
            lineNumber++;
            final String line = raw.strip();
            if (line.isEmpty() || line.startsWith("#")) {
                continue;
            }
            final String[] parts = line.split("\\s+");
            if (parts.length != 3) {
                throw new IOException("%s:%d: se esperaba 'x y R' y se leyó '%s'"
                        .formatted(path, lineNumber, line));
            }
            obstacles.add(new Obstacle(Double.parseDouble(parts[0]), Double.parseDouble(parts[1]),
                    Double.parseDouble(parts[2])));
        }
        return obstacles;
    }
}
