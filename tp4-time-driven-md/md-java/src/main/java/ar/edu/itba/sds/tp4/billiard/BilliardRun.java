package ar.edu.itba.sds.tp4.billiard;

import ar.edu.itba.sds.common.cli.CliArgs;

import java.io.BufferedWriter;
import java.io.IOException;
import java.math.BigDecimal;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.Random;

/**
 * Sistema 2: billar circular con contactos elásticos (resorte lineal normal) integrado con paso
 * fijo {@code dt} hasta {@code tf}. Escribe el estado cada {@code save-dt} y los instantes de
 * conversión fresca → usada. No calcula observables: energía, F_u, t_90, f(v) van en post-proceso.
 */
public final class BilliardRun {

    private static final String USAGE = """
            Sistema 2 - Billar circular

            Uso:
              java -jar md.jar billiard --scheme <esquema> [opciones]

            Integración:
              --scheme <nombre>   %s
              --dt <double>       Paso de integración (s)                          (default 1e-5)
              --tf <double>       Tiempo final (s), múltiplo de dt                  (default 10)
              --save-dt <double>  Intervalo de guardado (s), múltiplo de dt         (default 5e-2)

            Sistema:
              --n <int>           Cantidad de partículas                            (default 300)
              --xo <double>       Obstáculos en (±xo, 0), r <= xo <= R - r          (default: sin obstáculos)
              --seed <long>       Semilla de la condición inicial                   (default 1)
              --init <nombre>     random: inserción secuencial al azar (hasta N ≈ 465)
                                  hex: N sitios al azar de una red triangular de lado 2r
                                  (hasta ~720)                                      (default random)
              --R <double>        Radio del dominio (m)                             (default 0.51)
              --r <double>        Radio de partículas y obstáculos (m)              (default 0.0175)
              --m <double>        Masa (kg)                                         (default 0.025)
              --k <double>        Constante elástica normal (N/m)                   (default 1e4)
              --v0 <double>       Módulo de la velocidad inicial (m/s)              (default 1)

              --out <dir>         Directorio de salida
                                  (default output/billiard/<esquema>_N<n>_dt<dt>_s<seed>)

            Benchmark (punto 2.1b: una sola JVM, calentamiento previo y orden aleatorio):
              --bench N1,N2,...   Lista de N a medir (reemplaza a --n)
              --seeds <int>       Realizaciones (seeds 1..seeds) por N              (default 10)
              --warmup-s <double> Segundos de calentamiento previo                  (default 30)
                                  Escribe <out>/N<N>/s<seed>/ sin dynamic.txt (default out:
                                  output/billiard/time_vs_n)

            Salida (en <out>):
              static.txt          N; R; "r m" por partícula; K; "x y r" por obstáculo
              dynamic.txt         por bloque: t y "x y vx vy estado" por partícula (estado 0 = fresca,
                                  1 = usada), cada save-dt incluyendo t = 0 y t = tf (precisión completa)
              conversions.csv     t,id del primer contacto de cada partícula con un obstáculo (id desde 1)
              run.json            inputs, pasos y tiempo del lazo (loopTimeMs: solo la integración)
            """;

    private static final int WARMUP_N = 150;
    private static final double WARMUP_TF = 1.0;
    private static final long BENCH_SHUFFLE_SEED = 20261008L;

    /** Inputs de una corrida. */
    private record Config(Scheme scheme, Table table, int n, long seed, String init, double v0, double dt,
                          double tf, double saveDt) {

        Config withNAndSeed(final int newN, final long newSeed, final double newTf) {
            return new Config(scheme, table, newN, newSeed, init, v0, dt, newTf, saveDt);
        }
    }

    private BilliardRun() {
    }

    public static void run(final String[] args) throws IOException {
        final CliArgs cli = CliArgs.parse(args);
        if (cli.has("help")) {
            System.out.printf(USAGE, Scheme.names());
            return;
        }
        if (!cli.has("scheme")) {
            throw new IllegalArgumentException("Falta --scheme (" + Scheme.names() + ")");
        }
        final double bigR = cli.number("R", 0.51);
        final double r = cli.number("r", 0.0175);
        final double m = cli.number("m", 0.025);
        final double k = cli.number("k", 1e4);
        final Table table = cli.has("xo")
                ? Table.withObstacles(bigR, r, m, k, cli.number("xo", 0))
                : Table.empty(bigR, r, m, k);
        final Config config = new Config(Scheme.fromCli(cli.string("scheme", "")), table, cli.integer("n", 300),
                cli.longValue("seed", 1), cli.string("init", "random"), cli.number("v0", 1.0),
                cli.number("dt", 1e-5), cli.number("tf", 10.0), cli.number("save-dt", 5e-2));
        if (config.dt() <= 0 || config.tf() <= 0 || config.saveDt() <= 0 || config.n() < 1) {
            throw new IllegalArgumentException("dt, tf, save-dt y n tienen que ser positivos");
        }

        if (cli.has("bench")) {
            bench(config, cli.integerList("bench", List.of()), cli.integer("seeds", 10),
                    cli.number("warmup-s", 30), Path.of(cli.string("out", "output/billiard/time_vs_n")));
            return;
        }
        final Path outDir = Path.of(cli.string("out", "output/billiard/%s_N%d_dt%s_s%d"
                .formatted(config.scheme().cliName(), config.n(), compact(config.dt()), config.seed())));
        final Result result = simulate(config, outDir, true);
        System.out.printf(Locale.US, "%s  N = %d  dt = %s s  pasos = %d  usadas = %d  lazo = %.1f s  -> %s%n",
                config.scheme().cliName(), config.n(), compact(config.dt()), result.steps(), result.conversions(),
                result.loopNs() / 1e9, outDir);
    }

    private record Result(long steps, int conversions, long loopNs) {
    }

    /**
     * Punto 2.1b: tiempo de ejecución vs N en una sola JVM (como el {@code --bench} del TP3).
     * Primero corridas descartables para calentar el JIT y la frecuencia del CPU; después todas las
     * corridas (N × seeds) seguidas en orden aleatorio, para que una deriva residual se reparta
     * entre los N como ruido. Sin dynamic.txt: el tiempo a usar es {@code loopTimeMs}.
     */
    private static void bench(final Config base, final List<Integer> ns, final int seeds, final double warmupSeconds,
                              final Path outDir) throws IOException {
        if (ns.isEmpty() || seeds < 1) {
            throw new IllegalArgumentException("--bench necesita una lista de N y --seeds >= 1");
        }
        System.out.printf(Locale.US, "Calentando %.0f s con corridas descartables (N = %d, tf = %s s)...%n",
                warmupSeconds, WARMUP_N, WARMUP_TF);
        final long warmupStart = System.nanoTime();
        for (int w = 1; (System.nanoTime() - warmupStart) / 1e9 < warmupSeconds; w++) {
            simulate(base.withNAndSeed(WARMUP_N, -w, WARMUP_TF), outDir.resolve("warmup"), false);
        }

        final List<long[]> jobs = new ArrayList<>();
        for (final int n : ns) {
            for (long seed = 1; seed <= seeds; seed++) {
                jobs.add(new long[]{n, seed});
            }
        }
        Collections.shuffle(jobs, new Random(BENCH_SHUFFLE_SEED));
        System.out.printf(Locale.US, "Midiendo %d corridas en orden aleatorio...%n", jobs.size());
        int done = 0;
        for (final long[] job : jobs) {
            final Config config = base.withNAndSeed((int) job[0], job[1], base.tf());
            final Result result = simulate(config, outDir.resolve("N" + job[0]).resolve("s" + job[1]), false);
            done++;
            System.out.printf(Locale.US, "[%3d/%3d] N=%-4d seed=%-3d usadas=%-4d lazo %9.3f s%n", done,
                    jobs.size(), job[0], job[1], result.conversions(), result.loopNs() / 1e9);
        }
        System.out.println("Benchmark terminado: " + outDir.toAbsolutePath());
    }

    /** Corre una simulación y escribe sus archivos en {@code outDir}; el tiempo medido es solo el lazo. */
    private static Result simulate(final Config c, final Path outDir, final boolean writeDynamic) throws IOException {
        final long steps = multipleOf(c.tf(), c.dt(), "tf");
        final long saveEvery = multipleOf(c.saveDt(), c.dt(), "save-dt");
        final Random random = new Random(c.seed());
        final InitialState init = switch (c.init()) {
            case "random" -> InitialState.random(c.table(), c.n(), c.v0(), random);
            case "hex" -> InitialState.hexagonal(c.table(), c.n(), c.v0(), random);
            default -> throw new IllegalArgumentException("--init desconocido: " + c.init() + " (random, hex)");
        };
        Files.createDirectories(outDir);
        writeStatic(outDir.resolve("static.txt"), c.table(), c.n());

        final ContactForces forces = new ContactForces(c.table(), c.n());
        final Integrator integrator = c.scheme().create(forces, c.dt(), init.x, init.y, init.vx, init.vy);
        final long loopNs;
        if (writeDynamic) {
            final long start = System.nanoTime();
            try (BufferedWriter out = Files.newBufferedWriter(outDir.resolve("dynamic.txt"))) {
                writeFrame(out, 0.0, integrator, forces);
                for (long step = 1; step <= steps; step++) {
                    integrator.step(step * c.dt());
                    if (step % saveEvery == 0) {
                        writeFrame(out, step * c.dt(), integrator, forces);
                    }
                }
            }
            loopNs = System.nanoTime() - start;
        } else {
            final long start = System.nanoTime();
            for (long step = 1; step <= steps; step++) {
                integrator.step(step * c.dt());
            }
            loopNs = System.nanoTime() - start;
        }

        writeConversions(outDir.resolve("conversions.csv"), forces);
        writeRunJson(outDir.resolve("run.json"), c, steps, saveEvery, writeDynamic, forces, loopNs);
        return new Result(steps, forces.conversions(), loopNs);
    }

    /** Cantidad entera de {@code dt} en {@code value}; error si no es un múltiplo exacto. */
    private static long multipleOf(final double value, final double dt, final String name) {
        final long count = Math.round(value / dt);
        if (count < 1 || Math.abs(count * dt - value) > 1e-9 * value) {
            throw new IllegalArgumentException(name + " = " + value + " no es múltiplo entero de dt = " + dt);
        }
        return count;
    }

    private static void writeStatic(final Path path, final Table table, final int n) throws IOException {
        try (BufferedWriter out = Files.newBufferedWriter(path)) {
            out.write(n + "\n");
            out.write(table.bigR() + "\n");
            final String particle = table.r() + " " + table.m() + "\n";
            for (int i = 0; i < n; i++) {
                out.write(particle);
            }
            out.write(table.obstacleX().length + "\n");
            for (final double ox : table.obstacleX()) {
                out.write(ox + " 0.0 " + table.r() + "\n");
            }
        }
    }

    private static void writeFrame(final BufferedWriter out, final double t, final Integrator integrator,
                                   final ContactForces forces) throws IOException {
        final double[] x = integrator.x();
        final double[] y = integrator.y();
        final double[] vx = integrator.vx();
        final double[] vy = integrator.vy();
        out.write(Double.toString(t));
        out.write('\n');
        for (int i = 0; i < x.length; i++) {
            out.write(Double.toString(x[i]));
            out.write(' ');
            out.write(Double.toString(y[i]));
            out.write(' ');
            out.write(Double.toString(vx[i]));
            out.write(' ');
            out.write(Double.toString(vy[i]));
            out.write(forces.used(i) ? " 1\n" : " 0\n");
        }
    }

    private static void writeConversions(final Path path, final ContactForces forces) throws IOException {
        try (BufferedWriter out = Files.newBufferedWriter(path)) {
            out.write("t,id\n");
            for (int c = 0; c < forces.conversions(); c++) {
                out.write(Double.toString(forces.conversionTime(c)));
                out.write(',');
                out.write(Integer.toString(forces.conversionId(c) + 1));
                out.write('\n');
            }
        }
    }

    private static void writeRunJson(final Path path, final Config c, final long steps, final long saveEvery,
                                     final boolean dynamic, final ContactForces forces, final long loopNs)
            throws IOException {
        final Table table = c.table();
        final String xo = table.hasObstacles() ? Double.toString(table.obstacleX()[1]) : "null";
        final String json = """
                {
                  "system": "billiard",
                  "scheme": "%s",
                  "N": %d,
                  "seed": %d,
                  "init": "%s",
                  "R": %s,
                  "r": %s,
                  "m": %s,
                  "k": %s,
                  "v0": %s,
                  "xo": %s,
                  "dt": %s,
                  "tf": %s,
                  "saveDt": %s,
                  "steps": %d,
                  "saveEvery": %d,
                  "dynamicWritten": %s,
                  "cellsPerSide": %d,
                  "conversions": %d,
                  "loopTimeMs": %s
                }
                """.formatted(c.scheme().cliName(), c.n(), c.seed(), c.init(), table.bigR(), table.r(), table.m(),
                table.k(), c.v0(), xo, c.dt(), c.tf(), c.saveDt(), steps, saveEvery, dynamic,
                forces.cellsPerSide(), forces.conversions(), loopNs / 1e6);
        Files.writeString(path, json);
    }

    /** {@code 1.0E-3} → {@code 0.001}: nombre corto sin perder dígitos. */
    private static String compact(final double value) {
        return BigDecimal.valueOf(value).stripTrailingZeros().toPlainString();
    }
}
