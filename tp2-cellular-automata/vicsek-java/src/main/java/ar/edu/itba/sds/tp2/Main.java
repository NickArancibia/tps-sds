package ar.edu.itba.sds.tp2;

import ar.edu.itba.sds.common.cli.CliArgs;
import ar.edu.itba.sds.common.io.DynamicFileIO;
import ar.edu.itba.sds.common.io.StaticFileIO;
import ar.edu.itba.sds.tp2.io.RunWriter;

import java.io.IOException;
import java.nio.file.Path;
import java.util.Locale;

/**
 * CLI del TP2: simula una bandada (modelo de Vicsek estándar o de votante) y escribe todos los
 * archivos de la corrida. La animación y el análisis de observables se hacen offline sobre estos
 * archivos.
 */
public final class Main {

    private static final String USAGE = """
            SdS TP2 - Autómata Off-Lattice: bandadas de agentes autopropulsados

            Uso:
              java -jar vicsek.jar [opciones]

            Opciones:
              --model <s>      Regla de actualización: vicsek | voter        (default vicsek)
              --rho <double>   Densidad N/L^2 (define N si no se pasa --N)   (default 4)
              --N <int>        Cantidad de partículas (pisa a --rho)
              --L <double>     Lado de la caja (PBC siempre activas)         (default 10)
              --rc <double>    Radio de interacción entre centros            (default 1.0)
              --eta <double>   Amplitud del ruido: dθ ~ U[-eta/2, eta/2]     (default 0.5)
              --v <double>     Rapidez de las partículas                     (default 0.03)
              --dt <double>    Paso temporal                                 (default 1.0)
              --steps <int>    Cantidad de pasos a simular                   (default 2000)
              --seed <long>    Semilla del generador aleatorio               (default 42)
              --M <int>        Celdas por lado de la grilla del CIM          (default: el máximo válido)
              --every <int>    Guardar estado cada tantos pasos              (default 1)
              --out <dir>      Directorio de salida                          (default: output/<auto>)
              --help           Muestra esta ayuda

            Salida (en <out>):
              static.txt       N, L y el radio/color de cada partícula (formato de cátedra)
              dynamic.txt      un bloque "t / x y vx vy" cada --every pasos (incluye t=0)
              observables.csv  por paso: tiempo, polarización v_a y fracción del cluster gigante S
              run.json         inputs de la corrida y tiempos de cada llamada al CIM (punto g)
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

        final UpdateModel model = UpdateModel.fromString(cli.string("model", "vicsek"));
        final double l = cli.number("L", 10);
        final double rho = cli.number("rho", 4);
        final int n = cli.integer("N", (int) Math.round(rho * l * l));
        final double rc = cli.number("rc", 1.0);
        final double eta = cli.number("eta", 0.5);
        final double speed = cli.number("v", 0.03);
        final double dt = cli.number("dt", 1.0);
        final int steps = cli.integer("steps", 2000);
        final long seed = cli.longValue("seed", 42);
        final int m = cli.integer("M", SimulationConfig.maxM(l, rc));
        final int every = cli.integer("every", 1);

        final SimulationConfig config = new SimulationConfig(model, n, l, rc, eta, speed, dt,
                steps, seed, m, every);
        final Path outDir = Path.of(cli.string("out", defaultOutDir(config)));

        final long wallStart = System.nanoTime();
        final FlockSimulation sim = new FlockSimulation(config);

        StaticFileIO.write(outDir.resolve("static.txt"), l, sim.particles());
        try (DynamicFileIO.Writer dynamic = new DynamicFileIO.Writer(outDir.resolve("dynamic.txt"));
             RunWriter.ObservablesWriter observables =
                     new RunWriter.ObservablesWriter(outDir.resolve("observables.csv"))) {

            dynamic.writeFrame(sim.time(), sim.particles());
            observables.write(sim.time(), sim.polarization(), sim.largestClusterFraction());

            for (int step = 0; step < steps; step++) {
                sim.step();
                observables.write(sim.time(), sim.polarization(), sim.largestClusterFraction());
                if (sim.currentStep() % every == 0 || sim.currentStep() == steps) {
                    dynamic.writeFrame(sim.time(), sim.particles());
                }
            }
        }
        final long wallTimeNs = System.nanoTime() - wallStart;

        RunWriter.writeRunMetadata(outDir.resolve("run.json"), config, wallTimeNs,
                sim.cimTimesNs());
        printSummary(config, sim, wallTimeNs, outDir);
    }

    private static void printSummary(final SimulationConfig config, final FlockSimulation sim,
                                     final long wallTimeNs, final Path outDir) {
        final long[] cimTimes = sim.cimTimesNs();
        System.out.printf(Locale.US, """

                ==================== INPUTS ====================
                modelo             = %s
                N                  = %d
                L                  = %.4f
                densidad N/L^2     = %.4f
                rc                 = %.4f
                eta (ruido)        = %.4f
                v                  = %.4f
                dt                 = %.4f
                pasos              = %d
                semilla            = %d
                M (CIM)            = %d
                ==================== RESULTADOS ====================
                v_a final          = %.6f
                S final            = %.6f
                tiempo total       = %.2f ms
                CIM por paso       = %.4f ms (desvío %.4f ms, %d llamadas)
                ==================== ARCHIVOS ====================
                %s
                %n""",
                config.model(), config.n(), config.l(), config.density(), config.rc(),
                config.eta(), config.speed(), config.dt(), config.steps(), config.seed(),
                config.m(), sim.polarization(), sim.largestClusterFraction(), wallTimeNs / 1e6,
                RunWriter.mean(cimTimes) / 1e6, RunWriter.standardDeviation(cimTimes) / 1e6,
                cimTimes.length, outDir.toAbsolutePath());
    }

    private static String defaultOutDir(final SimulationConfig config) {
        return "output/%s_rho%s_eta%s_N%d_seed%d".formatted(
                config.model().name().toLowerCase(Locale.US), trim(config.density()),
                trim(config.eta()), config.n(), config.seed());
    }

    private static String trim(final double value) {
        return String.format(Locale.US, "%.2f", value);
    }
}
