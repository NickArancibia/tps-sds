package ar.edu.itba.sds.bench;

import ar.edu.itba.sds.common.cli.CliArgs;
import ar.edu.itba.sds.generator.ParticleGenerator;
import ar.edu.itba.sds.common.model.NeighborLists;
import ar.edu.itba.sds.common.model.Particle;
import ar.edu.itba.sds.common.neighbors.CellIndexMethod;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Locale;

/**
 * Barridos de parámetros de los puntos 3 y 4: mide el tiempo de la búsqueda de vecinos variando
 * {@code M} (punto 3) o {@code N} (punto 4) y escribe un CSV con los resultados.
 *
 * <h2>Qué se cronometra</h2>
 *
 * <p>Únicamente {@link ar.edu.itba.sds.common.neighbors.NeighborFinder#findNeighbors(List)}: la generación
 * de partículas queda fuera, y la escritura del CSV ocurre después de todas las mediciones. La
 * construcción de la grilla sí está incluida, porque es parte inseparable del método (en una
 * simulación dinámica hay que rehacerla en cada paso).</p>
 *
 * <p>Antes de cronometrar se hacen repeticiones de calentamiento para que el JIT ya haya compilado
 * el bucle caliente; sin eso los primeros valores son hasta un orden de magnitud más lentos y
 * ensucian el promedio.</p>
 *
 * <h2>Formato del CSV</h2>
 *
 * <pre>
 * experiment,N,L,M,rc,pbc,seed,repetition,time_ns,neighbor_pairs
 * </pre>
 *
 * <p>Se escribe una fila por repetición individual (no el promedio) para que el análisis en Python
 * pueda recalcular cualquier estadístico sin volver a correr nada.</p>
 */
public final class BenchmarkRunner {

    /** L de referencia del enunciado: los N por defecto y el M óptimo se expresan respecto de él. */
    private static final double REFERENCE_L = 20.0;

    /** Tiempo mínimo de calentamiento por punto, además del conteo de {@code --warmup}. */
    private static final long MIN_WARMUP_NANOS = 200_000_000L;

    private static final String USAGE = """
            SdS TP1 - Barridos de tiempo de cómputo (puntos 3 y 4)

            Uso:
              java -cp cim.jar ar.edu.itba.sds.bench.BenchmarkRunner --sweep <tipo> [opciones]

            Tipos de barrido (--sweep):
              M         Punto 3: para cada N de --N, recorre M = 1 .. Mmax con L fijo.
              N         Punto 4.1 (densidad libre): L fijo, N variable, M fijo.
              density   Punto 4.2 (densidad fija): N variable y L = sqrt(N/rho), rho constante.

            Opciones comunes:
              --L <double>     Lado del área                                  (default 20)
              --rc <double>    Radio de interacción                           (default 1.0)
              --rmin <double>  Radio mínimo de partícula                      (default 0.23)
              --rmax <double>  Radio máximo de partícula                      (default 0.26)
              --pbc            Activa condiciones periódicas de contorno      (default: desactivadas)
              --seed <long>    Semilla base del generador                     (default 42)
              --seeds <int>    Configuraciones distintas por punto            (default 1)
              --reps <int>     Repeticiones cronometradas por configuración   (default 100)
              --warmup <int>   Repeticiones de calentamiento de la JVM        (default: min(reps, 20))
              --maxAttempts <int>  Intentos máximos por partícula al generar  (default 20000)
              --out <archivo>  CSV de salida                                  (default output/bench_<sweep>.csv)

            Opciones de --sweep M:
              --N <lista>      Valores de N separados por coma                (default 500,1000)

            Opciones de --sweep N y --sweep density:
              --N <lista>      Valores de N separados por coma                (default: 10 valores log-espaciados)
              --Nmin <int>     Primer N cuando no se pasa --N                 (default 10)
              --Nmax <int>     Último N cuando no se pasa --N                 (default: el máximo de la geometría)
              --points <int>   Cantidad de valores de N cuando no se pasa --N (default 12)
              --M <int>        M óptimo hallado en el punto 3                 (default: el máximo válido)

            Opciones de --sweep density:
              --rho <double>   Densidad N/L^2 a mantener constante            (default 1.25, o sea N=500 con L=20)
              --fixedM         Mantiene M constante en vez de mantener constante el lado de celda
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
        if (cli.has("help") || args.length == 0) {
            System.out.println(USAGE);
            return;
        }

        final String sweep = cli.string("sweep", "M");
        final double l = cli.number("L", REFERENCE_L);
        final double rc = cli.number("rc", 1.0);
        final double rMin = cli.number("rmin", 0.23);
        final double rMax = cli.number("rmax", 0.26);
        final boolean periodic = cli.has("pbc");
        final long seed = cli.longValue("seed", 42);
        final int seeds = cli.integer("seeds", 1);
        final int reps = cli.integer("reps", 100);
        final int warmup = cli.integer("warmup", Math.min(reps, 20));
        final int maxAttempts = cli.integer("maxAttempts", 20_000);

        final Path out = Path.of(cli.string("out", "output/bench_" + sweep + ".csv"));
        Files.createDirectories(out.toAbsolutePath().getParent());

        final Params params = new Params(rc, rMin, rMax, periodic, seed, seeds, reps, warmup,
                maxAttempts);

        try (BufferedWriter writer = Files.newBufferedWriter(out)) {
            writer.write("experiment,N,L,M,rc,pbc,seed,repetition,time_ns,neighbor_pairs");
            writer.newLine();

            switch (sweep) {
                case "M" -> sweepM(writer, cli, l, params);
                case "N" -> sweepN(writer, cli, l, params);
                case "density" -> sweepDensity(writer, cli, params);
                default -> throw new IllegalArgumentException(
                        "Barrido desconocido: '" + sweep + "'. Usar M, N o density.");
            }
        }

        System.err.println("CSV escrito en " + out.toAbsolutePath());
    }

    // ------------------------------------------------------------------ punto 3: barrido de M

    /**
     * Para cada N, recorre todos los M válidos (1 hasta Mmax) sobre <b>la misma</b> configuración de
     * partículas: así la única variable es el tamaño de la grilla. {@code M = 1} es exactamente
     * fuerza bruta (una sola celda que contiene a todas las partículas).
     */
    private static void sweepM(final BufferedWriter writer, final CliArgs cli, final double l,
                               final Params params) throws IOException {
        final List<Integer> ns = cli.integerList("N", List.of(500, 1000));
        final int maxM = maxM(l, params);
        System.err.printf(Locale.US, "Barrido de M: N=%s, M=1..%d, L=%.2f%n", ns, maxM, l);

        for (final int n : ns) {
            for (int s = 0; s < params.seeds(); s++) {
                final long seed = params.seed() + s;
                final List<Particle> particles = generate(n, l, seed, params);
                for (int m = 1; m <= maxM; m++) {
                    measure(writer, "M", particles, n, l, m, seed, params);
                }
                System.err.printf(Locale.US, "  N=%d seed=%d listo%n", n, seed);
            }
        }
    }

    // ------------------------------------------------------------------ punto 4: barridos de N

    /** Punto 4.1: L fijo, N creciente, M constante. La densidad crece con N. */
    private static void sweepN(final BufferedWriter writer, final CliArgs cli, final double l,
                               final Params params) throws IOException {
        final int maxM = maxM(l, params);
        final int m = cli.integer("M", maxM);
        final List<Integer> ns = nValues(cli, l, params);
        System.err.printf(Locale.US, "Barrido de N (densidad libre): N=%s, L=%.2f, M=%d%n", ns, l, m);

        for (final int n : ns) {
            for (int s = 0; s < params.seeds(); s++) {
                final long seed = params.seed() + s;
                final List<Particle> particles = generate(n, l, seed, params);
                measure(writer, "N_free", particles, n, l, m, seed, params);
            }
            System.err.printf(Locale.US, "  N=%d listo (densidad %.4f)%n", n, n / (l * l));
        }
    }

    /**
     * Punto 4.2: la densidad {@code rho = N/L^2} se mantiene constante haciendo crecer
     * {@code L = sqrt(N/rho)} junto con N.
     *
     * <p>El enunciado pide usar "el M óptimo del punto 3", pero ese óptimo es en realidad un
     * <b>tamaño de celda</b> óptimo: como acá L cambia, mantener M constante cambiaría el lado de
     * celda {@code L/M} y con él la cantidad de partículas por celda, que es lo que determina el
     * costo. Por eso, por defecto, se escala {@code M} con {@code L} para conservar el lado de celda
     * del punto 3. Con {@code --fixedM} se fuerza el M constante.</p>
     */
    private static void sweepDensity(final BufferedWriter writer, final CliArgs cli,
                                     final Params params) throws IOException {
        final double referenceL = cli.number("L", REFERENCE_L);
        final int referenceM = cli.integer("M", maxM(referenceL, params));
        final boolean fixedM = cli.has("fixedM");
        final double rho = cli.number("rho", 500 / (REFERENCE_L * REFERENCE_L));
        final List<Integer> ns = nValues(cli, referenceL, params);

        System.err.printf(Locale.US, "Barrido de N (densidad fija rho=%.4f): N=%s, M %s%n",
                rho, ns, fixedM ? "constante" : "escalado con L");

        for (final int n : ns) {
            final double l = Math.sqrt(n / rho);
            final int maxM = maxM(l, params);
            // Escalar M con L conserva el lado de celda L/M del punto 3.
            final int scaled = (int) Math.round(referenceM * l / referenceL);
            final int m = Math.min(maxM, Math.max(1, fixedM ? referenceM : scaled));

            for (int s = 0; s < params.seeds(); s++) {
                final long seed = params.seed() + s;
                final List<Particle> particles = generate(n, l, seed, params);
                measure(writer, "N_fixed_density", particles, n, l, m, seed, params);
            }
            System.err.printf(Locale.US, "  N=%d listo (L=%.4f, M=%d, celda=%.4f)%n", n, l, m, l / m);
        }
    }

    // ------------------------------------------------------------------ núcleo de la medición

    /**
     * Cronometra {@code reps} búsquedas de vecinos sobre una configuración ya generada y escribe una
     * fila por repetición.
     */
    private static void measure(final BufferedWriter writer, final String experiment,
                                final List<Particle> particles, final int n, final double l,
                                final int m, final long seed, final Params params)
            throws IOException {
        final CellIndexMethod cim = new CellIndexMethod(l, m, params.rc(), params.periodic(),
                params.rMax());

        // Calentamiento: descartado, sólo sirve para que el JIT compile el bucle caliente.
        //
        // El corte es por cantidad de repeticiones *y* por tiempo mínimo: con N chico cada búsqueda
        // dura microsegundos y unas pocas decenas de repeticiones no alcanzan para que el JIT
        // compile, con lo que las primeras mediciones salen un orden de magnitud más lentas y
        // arruinan el promedio de justo los puntos más baratos del barrido.
        final long warmupDeadline = System.nanoTime() + MIN_WARMUP_NANOS;
        for (int i = 0; i < params.warmup() || System.nanoTime() < warmupDeadline; i++) {
            cim.findNeighbors(particles);
        }

        final long[] timesNs = new long[params.reps()];
        int pairs = 0;
        for (int i = 0; i < params.reps(); i++) {
            final long start = System.nanoTime();
            final NeighborLists neighbors = cim.findNeighbors(particles);
            timesNs[i] = System.nanoTime() - start;
            pairs = neighbors.totalPairs();
        }

        final String prefix = String.format(Locale.US, "%s,%d,%.6f,%d,%.6f,%b,%d,",
                experiment, n, l, m, params.rc(), params.periodic(), seed);
        for (int i = 0; i < timesNs.length; i++) {
            writer.write(prefix);
            writer.write(Integer.toString(i));
            writer.write(',');
            writer.write(Long.toString(timesNs[i]));
            writer.write(',');
            writer.write(Integer.toString(pairs));
            writer.newLine();
        }
    }

    private static List<Particle> generate(final int n, final double l, final long seed,
                                           final Params params) {
        return new ParticleGenerator(l, params.rMin(), params.rMax(), params.periodic(),
                params.maxAttempts()).generate(n, seed);
    }

    private static int maxM(final double l, final Params params) {
        final int maxM = (int) Math.floor(l / (params.rc() + 2 * params.rMax()));
        if (maxM < 1) {
            throw new IllegalArgumentException(String.format(Locale.US,
                    "Con L=%.4f, rc=%.4f y rMax=%.4f no existe ningún M válido.",
                    l, params.rc(), params.rMax()));
        }
        return maxM;
    }

    /**
     * Valores de N del punto 4: los explícitos de {@code --N}, o si no una progresión geométrica
     * entre {@code --Nmin} y {@code --Nmax}.
     *
     * <p>El espaciado es logarítmico porque el gráfico de tiempo vs N se lee en escala log-log: con
     * espaciado lineal la mitad de los puntos se amontonaría en la última década.</p>
     */
    private static List<Integer> nValues(final CliArgs cli, final double l, final Params params) {
        final int nMax = cli.integer("Nmax",
                ParticleGenerator.estimateMaxParticles(l, params.rMin(), params.rMax()));
        final int nMin = cli.integer("Nmin", 10);
        final int points = cli.integer("points", 12);
        if (nMin < 1 || nMax < nMin) {
            throw new IllegalArgumentException(
                    "Rango de N inválido: [" + nMin + ", " + nMax + "]");
        }

        final List<Integer> fallback = new ArrayList<>();
        if (points == 1) {
            fallback.add(nMax);
        } else {
            // LinkedHashSet: con N chicos el redondeo puede repetir valores consecutivos.
            final LinkedHashSet<Integer> unique = new LinkedHashSet<>();
            final double ratio = Math.log((double) nMax / nMin) / (points - 1);
            for (int i = 0; i < points; i++) {
                unique.add((int) Math.round(nMin * Math.exp(ratio * i)));
            }
            fallback.addAll(unique);
        }
        return cli.integerList("N", fallback);
    }

    /** Parámetros que no cambian dentro de un barrido. */
    private record Params(double rc, double rMin, double rMax, boolean periodic, long seed,
                          int seeds, int reps, int warmup, int maxAttempts) {
    }

    private BenchmarkRunner() {
    }
}
