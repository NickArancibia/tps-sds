package ar.edu.itba.sds.tp3;

import java.io.IOException;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.Random;

/**
 * Punto 1.1: tiempo de ejecución en función de N, mesa vacía, dentro de una única JVM.
 *
 * <p>Medir cada corrida en una JVM nueva no sirve para N chico: el lazo dura milisegundos y la
 * medición queda dominada por el JIT y por el gestor de frecuencia del CPU (que solo sube con
 * carga sostenida: la misma corrida de N = 100 tardaba 125 ms dentro de un barrido y 340 ms
 * suelta). Por eso: (1) se calienta el JIT y el CPU con corridas descartables, (2) todas las
 * corridas (N × seeds) se hacen seguidas, sin pausas, en <b>orden aleatorio</b> para que
 * cualquier deriva residual se reparta entre todos los N como ruido y no sesgue la curva.</p>
 *
 * <p>Cada corrida escribe sus archivos normales en {@code <out>/N<N>/s<seed>/}; el tiempo a usar
 * es {@code loopTimeMs} de {@code run.json} (solo el lazo de eventos).</p>
 */
public final class Benchmark {

    private static final int WARMUP_N = 150;

    private Benchmark() {
    }

    public static void run(final List<Integer> ns, final int seeds, final SimulationConfig base,
                           final double warmupSeconds, final Path outDir) throws IOException {
        System.out.printf(Locale.US, "Calentando JIT y CPU durante %.0f s con corridas descartables (N = %d)...%n",
                warmupSeconds, WARMUP_N);
        final long warmupStart = System.nanoTime();
        int warmups = 0;
        while ((System.nanoTime() - warmupStart) / 1e9 < warmupSeconds) {
            final SimulationConfig cfg = withNAndSeed(base, WARMUP_N, -1 - warmups++);
            SimulationRunner.run(cfg, InitialConditions.generate(cfg, new Random(cfg.seed())),
                    outDir.resolve("warmup"), null, null, false, System.nanoTime());
        }

        final List<int[]> jobs = new ArrayList<>();
        for (final int n : ns) {
            for (int seed = 1; seed <= seeds; seed++) {
                jobs.add(new int[]{n, seed});
            }
        }
        Collections.shuffle(jobs, new Random(20260910));
        System.out.printf(Locale.US, "Midiendo %d corridas en orden aleatorio...%n", jobs.size());
        int done = 0;
        for (final int[] job : jobs) {
            final SimulationConfig cfg = withNAndSeed(base, job[0], job[1]);
            final Path dir = outDir.resolve("N" + job[0]).resolve("s" + job[1]);
            final long wallStart = System.nanoTime();
            final List<Ball> balls = InitialConditions.generate(cfg, new Random(cfg.seed()));
            final SimulationRunner.Result result = SimulationRunner.run(cfg, balls, dir, null, null,
                    false, wallStart);
            done++;
            System.out.printf(Locale.US, "[%3d/%3d] N=%-4d seed=%-3d lazo %10.3f ms%n", done,
                    jobs.size(), job[0], job[1], result.loopTimeNs() / 1e6);
        }
        System.out.println("Benchmark terminado: " + outDir.toAbsolutePath());
    }

    private static SimulationConfig withNAndSeed(final SimulationConfig b, final int n, final long seed) {
        return new SimulationConfig(n, b.l(), b.w(), b.d(), b.radius(), b.mass(), b.v0(), b.tf(),
                seed, 0, false, List.of());
    }
}
