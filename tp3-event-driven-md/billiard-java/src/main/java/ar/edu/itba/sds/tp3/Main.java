package ar.edu.itba.sds.tp3;

import ar.edu.itba.sds.common.cli.CliArgs;
import ar.edu.itba.sds.tp3.io.InitialStateFile;
import ar.edu.itba.sds.tp3.io.ObstaclesFile;
import ar.edu.itba.sds.tp3.io.RunWriter;

import java.io.IOException;
import java.nio.file.Path;
import java.util.List;
import java.util.Locale;
import java.util.Random;

/**
 * CLI del TP3: simula el billar-metegol con dinámica molecular regida por eventos y escribe los
 * archivos de la corrida. Animaciones y observables se calculan offline sobre esos archivos.
 */
public final class Main {

    private static final String USAGE = """
            SdS TP3 - Dinámica molecular regida por eventos: Billar-Metegol

            Uso:
              java -jar billiard.jar [opciones]

            Sistema:
              --N <int>           Cantidad de partículas                        (default 100)
              --L <double>        Largo de la mesa (m)                          (default 1.20)
              --W <double>        Ancho de la mesa (m)                          (default 0.68)
              --d <double>        Longitud del arco (m)                         (default 0.20)
              --r <double>        Radio de las partículas (m)                   (default 0.0175)
              --m <double>        Masa de las partículas (kg)                   (default 0.025)
              --v0 <double>       Módulo de la velocidad inicial (m/s)          (default 1.0)
              --obstacles <file>  Archivo de obstáculos, una línea "x y R" por obstáculo
                                  (mismo formato que Config.txt; sin flag = mesa vacía)

            Corrida:
              --tf <double>       Tiempo simulado máximo (s)                    (default 30)
              --seed <long>       Semilla del generador aleatorio               (default 42)
              --stop-at-t90       Cortar apenas F_g >= 0.9
              --every <k>         Escribir dynamic.txt cada k eventos (1 = todos) (default 0 = no escribir)
              --initial <file>    Correr desde una condición inicial dada (líneas "x y vx vy";
                                  N se toma del archivo)
              --gen-initial       Solo generar la condición inicial en <out>/initial.txt y salir
              --verify            Chequear solapamientos tras cada evento (lento, para depurar)

            Benchmark (punto 1.1, mesa vacía, una sola JVM con calentamiento y orden aleatorio):
              --bench [N1,N2,...] Lista de N a medir                          (default 25,...,400)
              --seeds <int>       Realizaciones (seeds 1..seeds) por N        (default 20)
              --warmup-s <double> Segundos de calentamiento previo            (default 30)
                                  Escribe <out>/N<N>/s<seed>/ (default out: output/time_vs_n)
              --out <dir>         Directorio de salida                          (default: output/<auto>)
              --help              Muestra esta ayuda

            Salida (en <out>):
              initial.txt         condición inicial usada (x y vx vy por partícula)
              static.txt          N, L W d, radio y masa por partícula, obstáculos
              goals.csv           un renglón por gol: tiempo e id de la partícula
              dynamic.txt         (con --every) bloques "t / x y vx vy estado" en los instantes de los
                                  eventos, incluyendo t = 0 y t = tf
              run.json            inputs, t_90, conteo de eventos, energía inicial/final, tiempos
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
        final CliArgs cli = CliArgs.parse(args);
        if (cli.has("help")) {
            System.out.println(USAGE);
            return;
        }
        final long wallStart = System.nanoTime();

        if (cli.has("bench")) {
            final SimulationConfig base = new SimulationConfig(100, cli.number("L", 1.20),
                    cli.number("W", 0.68), cli.number("d", 0.20), cli.number("r", 0.0175),
                    cli.number("m", 0.025), cli.number("v0", 1.0), cli.number("tf", 30), 0, 0,
                    false, List.of());
            Benchmark.run(cli.integerList("bench", List.of(25, 50, 100, 150, 200, 300, 400)),
                    cli.integer("seeds", 20), base, cli.number("warmup-s", 30),
                    Path.of(cli.string("out", "output/time_vs_n")));
            return;
        }

        final String obstaclesFile = cli.string("obstacles", null);
        final List<Obstacle> obstacles = obstaclesFile == null ? List.of()
                : ObstaclesFile.read(Path.of(obstaclesFile));
        final String initialFile = cli.string("initial", null);
        final double radius = cli.number("r", 0.0175);
        final double mass = cli.number("m", 0.025);

        List<Ball> balls = null;
        int n = cli.integer("N", 100);
        if (initialFile != null) {
            balls = InitialStateFile.read(Path.of(initialFile), radius, mass);
            n = balls.size();
        }
        final SimulationConfig config = new SimulationConfig(n, cli.number("L", 1.20),
                cli.number("W", 0.68), cli.number("d", 0.20), radius, mass, cli.number("v0", 1.0),
                cli.number("tf", 30), cli.longValue("seed", 42), cli.integer("every", 0),
                cli.has("stop-at-t90"), obstacles);
        final Path outDir = Path.of(cli.string("out", defaultOutDir(config)));

        if (balls == null) {
            balls = InitialConditions.generate(config, new Random(config.seed()));
        }
        if (cli.has("gen-initial")) {
            RunWriter.writeStatic(outDir.resolve("static.txt"), config, balls);
            InitialStateFile.write(outDir.resolve("initial.txt"), balls);
            System.out.printf(Locale.US, "Condición inicial (N = %d, seed = %d) escrita en %s%n",
                    config.n(), config.seed(), outDir.resolve("initial.txt").toAbsolutePath());
            return;
        }

        final SimulationRunner.Result result = SimulationRunner.run(config, balls, outDir,
                obstaclesFile, initialFile, cli.has("verify"), wallStart);
        printSummary(config, result.sim(), result.energyInitial(), result.loopTimeNs(),
                System.nanoTime() - wallStart, outDir);
    }

    private static void printSummary(final SimulationConfig config, final BilliardSimulation sim,
                                     final double energyInitial, final long loopTimeNs,
                                     final long wallTimeNs, final Path outDir) {
        long total = 0;
        for (final long count : sim.processedEvents().values()) {
            total += count;
        }
        System.out.printf(Locale.US, """

                ==================== INPUTS ====================
                N                  = %d
                L x W, d           = %.3f x %.3f, %.3f
                r, m, v0           = %.4f, %.4f, %.3f
                obstáculos         = %d
                fracción de área   = %.4f
                tf                 = %.3f
                semilla            = %d
                ==================== RESULTADOS ====================
                goles              = %d / %d  (t_90 con %d)
                t_90               = %s
                tiempo final       = %.6f
                eventos            = %d (partícula %d, obstáculo %d, pared x %d, pared y %d; obsoletos %d; en cola al final %d)
                energía cinética   = %.12e -> %.12e (variación relativa %.2e)
                lazo de eventos    = %.2f ms
                tiempo total       = %.2f ms
                ==================== ARCHIVOS ====================
                %s
                %n""",
                config.n(), config.l(), config.w(), config.d(), config.radius(), config.mass(),
                config.v0(), config.obstacles().size(), config.areaFraction(), config.tf(),
                config.seed(), sim.goals(), config.n(), config.goalsForT90(),
                sim.reachedT90() ? String.format(Locale.US, "%.6f", sim.t90()) : "no alcanzado",
                sim.time(), total,
                sim.processedEvents().get(Event.Type.PARTICLE),
                sim.processedEvents().get(Event.Type.OBSTACLE),
                sim.processedEvents().get(Event.Type.WALL_X),
                sim.processedEvents().get(Event.Type.WALL_Y), sim.staleEvents(), sim.queueSize(),
                energyInitial, sim.kineticEnergy(),
                Math.abs(sim.kineticEnergy() - energyInitial) / energyInitial,
                loopTimeNs / 1e6, wallTimeNs / 1e6, outDir.toAbsolutePath());
    }

    private static String defaultOutDir(final SimulationConfig config) {
        return "output/N%d_K%d_seed%d".formatted(config.n(), config.obstacles().size(),
                config.seed());
    }
}
