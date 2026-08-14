package ar.edu.itba.sds;

import ar.edu.itba.sds.cli.CliArgs;
import ar.edu.itba.sds.generator.ParticleGenerator;
import ar.edu.itba.sds.io.DynamicFileIO;
import ar.edu.itba.sds.io.OutputWriter;
import ar.edu.itba.sds.io.StaticFileIO;
import ar.edu.itba.sds.model.NeighborLists;
import ar.edu.itba.sds.model.Particle;
import ar.edu.itba.sds.model.SystemConfig;
import ar.edu.itba.sds.neighbors.BruteForce;
import ar.edu.itba.sds.neighbors.CellIndexMethod;

import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * CLI del punto 1: genera (o carga) un sistema de partículas, calcula sus vecinos con el Cell Index
 * Method, mide el tiempo de ejecución y escribe todos los archivos de la corrida.
 */
public final class Main {

    private static final String USAGE = """
            SdS TP1 - Cell Index Method

            Uso:
              java -jar cim.jar [opciones]

            Opciones:
              --N <int>        Cantidad de partículas                        (default 1000)
              --L <double>     Lado del área de simulación                   (default 20)
              --M <int>        Celdas por lado de la grilla (M x M)          (default: el máximo válido)
              --rc <double>    Radio de interacción                          (default 1.0)
              --rmin <double>  Radio mínimo de partícula                     (default 0.23)
              --rmax <double>  Radio máximo de partícula                     (default 0.26)
              --pbc            Activa condiciones periódicas de contorno     (default: desactivadas)
              --seed <long>    Semilla del generador aleatorio               (default 42)
              --reps <int>     Repeticiones cronometradas de la búsqueda     (default 10)
              --warmup <int>   Repeticiones de calentamiento de la JVM       (default: min(reps, 5))
              --maxAttempts <int>  Intentos máximos por partícula al generar   (default 20000)
              --brute          Usa fuerza bruta en lugar del CIM
              --verify         Compara el resultado del CIM contra fuerza bruta
              --input <dir>    Carga static.txt y dynamic.txt del directorio en lugar de generar
              --out <dir>      Directorio de salida                          (default: output/<auto>)
              --help           Muestra esta ayuda

            Salida (en <out>):
              static.txt     N, L y el radio/color de cada partícula
              dynamic.txt    posiciones y velocidades en t=0
              neighbors.txt  para cada partícula, los ids de sus vecinas a distancia < rc
              run.json       parámetros, tiempos de cada repetición, promedio y desvío
            """;

    public static void main(final String[] args) {
        try {
            run(args);
        } catch (final IllegalArgumentException | IllegalStateException e) {
            System.err.println("ERROR: " + e.getMessage());
            System.exit(1);
        } catch (final IOException e) {
            System.err.println("ERROR de E/S: " + e.getMessage());
            System.exit(1);
        }
    }

    private static void run(final String[] args) throws IOException {
        final Map<String, String> options = CliArgs.parse(args).raw();
        if (options.containsKey("help")) {
            System.out.println(USAGE);
            return;
        }

        final boolean periodic = options.containsKey("pbc");
        final boolean useBruteForce = options.containsKey("brute");
        final boolean verify = options.containsKey("verify");
        final long seed = Long.parseLong(options.getOrDefault("seed", "42"));
        final double rc = Double.parseDouble(options.getOrDefault("rc", "1.0"));
        final double rMin = Double.parseDouble(options.getOrDefault("rmin", "0.23"));
        final int reps = Integer.parseInt(options.getOrDefault("reps", "10"));

        double l = Double.parseDouble(options.getOrDefault("L", "20"));
        double rMax = Double.parseDouble(options.getOrDefault("rmax", "0.26"));
        int n = Integer.parseInt(options.getOrDefault("N", "1000"));

        final List<Particle> particles;
        final long generationTimeNs;

        if (options.containsKey("input")) {
            final Path inputDir = Path.of(options.get("input"));
            final StaticFileIO.StaticData staticData = StaticFileIO.read(inputDir.resolve("static.txt"));
            final List<DynamicFileIO.Snapshot> snapshots =
                    DynamicFileIO.read(inputDir.resolve("dynamic.txt"), staticData.n());
            if (snapshots.isEmpty()) {
                throw new IllegalStateException("El archivo dinámico no contiene ningún tiempo.");
            }
            // El TP1 trabaja sobre un único instante: se usa el primer bloque del archivo dinámico.
            particles = DynamicFileIO.toParticles(staticData, snapshots.get(0));
            n = staticData.n();
            l = staticData.l();
            rMax = particles.stream().mapToDouble(Particle::radius).max().orElse(rMax);
            generationTimeNs = 0;
            System.out.printf("Sistema cargado desde %s (N=%d, L=%.4f)%n", inputDir, n, l);
        } else {
            final int maxAttempts = Integer.parseInt(options.getOrDefault("maxAttempts", "20000"));
            final long start = System.nanoTime();
            particles = new ParticleGenerator(l, rMin, rMax, periodic, maxAttempts).generate(n, seed);
            generationTimeNs = System.nanoTime() - start;
        }

        final int maxM = (int) Math.floor(l / (rc + 2 * rMax));
        if (maxM < 1) {
            throw new IllegalArgumentException(String.format(Locale.US,
                    "Con L=%.4f, rc=%.4f y rMax=%.4f no existe ningún M válido: el área es menor "
                            + "que una celda mínima.", l, rc, rMax));
        }
        final int m = Integer.parseInt(options.getOrDefault("M", Integer.toString(maxM)));

        final SystemConfig config = new SystemConfig(n, l, m, rc, periodic, seed, rMin, rMax);

        // Si M es inválido, el constructor del CIM falla acá con un mensaje explícito (punto 3).
        final CellIndexMethod cim = new CellIndexMethod(l, m, rc, periodic, rMax);
        final BruteForce brute = new BruteForce(l, rc, periodic);
        final var finder = useBruteForce ? brute : cim;

        final int warmup = Integer.parseInt(
                options.getOrDefault("warmup", Integer.toString(Math.min(reps, 5))));

        // Calentamiento: la JVM necesita compilar el bucle caliente antes de dar tiempos estables.
        for (int i = 0; i < warmup; i++) {
            finder.findNeighbors(particles);
        }

        final long[] timesNs = new long[reps];
        NeighborLists neighbors = null;
        for (int i = 0; i < reps; i++) {
            final long start = System.nanoTime();
            neighbors = finder.findNeighbors(particles);
            timesNs[i] = System.nanoTime() - start;
        }

        Boolean verified = null;
        if (verify) {
            final NeighborLists expected = new BruteForce(l, rc, periodic).findNeighbors(particles);
            final int diff = expected.firstDifference(neighbors);
            verified = diff < 0;
            if (verified) {
                System.out.println("Verificación contra fuerza bruta: OK (resultados idénticos)");
            } else {
                System.err.printf("Verificación contra fuerza bruta: FALLÓ en la partícula id=%d%n",
                        particles.get(diff).id());
            }
        }

        final Path outDir = Path.of(options.getOrDefault("out", defaultOutDir(config)));
        StaticFileIO.write(outDir.resolve("static.txt"), l, particles);
        DynamicFileIO.write(outDir.resolve("dynamic.txt"), 0.0, particles);
        OutputWriter.writeNeighbors(outDir.resolve("neighbors.txt"), particles, neighbors);
        OutputWriter.writeRunMetadata(outDir.resolve("run.json"), config, finder.name(), timesNs,
                generationTimeNs, neighbors.totalPairs(), cim.cellSize(), verified);

        printSummary(config, finder.name(), maxM, cim.cellSize(), timesNs, generationTimeNs,
                neighbors, outDir);

        if (verified != null && !verified) {
            System.exit(2);
        }
    }

    private static void printSummary(final SystemConfig config, final String method, final int maxM,
                                     final double cellSize, final long[] timesNs,
                                     final long generationTimeNs, final NeighborLists neighbors,
                                     final Path outDir) {
        final double meanMs = OutputWriter.mean(timesNs) / 1e6;
        final double stdMs = OutputWriter.standardDeviation(timesNs) / 1e6;
        double totalNeighbors = 0;
        for (int i = 0; i < neighbors.size(); i++) {
            totalNeighbors += neighbors.neighborCount(i);
        }

        System.out.printf(Locale.US, """

                ==================== INPUTS ====================
                N                  = %d
                L                  = %.4f
                M                  = %d          (máximo permitido: %d)
                lado de celda L/M  = %.4f      (mínimo requerido rc + 2*rMax = %.4f)
                rc                 = %.4f
                radios             = U[%.4f, %.4f]
                contorno periódico = %s
                semilla            = %d
                método             = %s
                ==================== RESULTADOS ====================
                densidad N/L^2     = %.6f
                pares vecinos      = %d
                vecinos promedio   = %.4f por partícula
                generación         = %.4f ms
                repeticiones       = %d
                tiempo promedio    = %.6f ms
                desvío estándar    = %.6f ms
                ==================== ARCHIVOS ====================
                %s
                %n""",
                config.n(), config.l(), config.m(), maxM, cellSize, config.rc() + 2 * config.rMax(),
                config.rc(), config.rMin(), config.rMax(), config.periodic() ? "sí" : "no",
                config.seed(), method, config.density(), neighbors.totalPairs(),
                totalNeighbors / neighbors.size(), generationTimeNs / 1e6, timesNs.length,
                meanMs, stdMs, outDir.toAbsolutePath());
    }

    private static String defaultOutDir(final SystemConfig config) {
        return "output/N%d_L%s_M%d_rc%s_pbc-%s_seed%d".formatted(
                config.n(), trim(config.l()), config.m(), trim(config.rc()),
                config.periodic(), config.seed());
    }

    private static String trim(final double value) {
        return String.format(Locale.US, "%.2f", value);
    }
}
