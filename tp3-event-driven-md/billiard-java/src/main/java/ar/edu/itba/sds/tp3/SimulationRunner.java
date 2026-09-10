package ar.edu.itba.sds.tp3;

import ar.edu.itba.sds.tp3.io.InitialStateFile;
import ar.edu.itba.sds.tp3.io.RunWriter;

import java.io.IOException;
import java.nio.file.Path;
import java.util.List;

/**
 * Ejecuta una corrida completa (lazo de eventos + escritura de todos los archivos) en un
 * directorio de salida. Lo usan el CLI ({@link Main}) y el modo benchmark ({@link Benchmark}).
 */
public final class SimulationRunner {

    /** Resumen de una corrida ya ejecutada. */
    public record Result(BilliardSimulation sim, double energyInitial, long loopTimeNs) {
    }

    private SimulationRunner() {
    }

    public static Result run(final SimulationConfig config, final List<Ball> balls, final Path outDir,
                             final String obstaclesFile, final String initialFile,
                             final boolean verify, final long wallStartNs) throws IOException {
        RunWriter.writeStatic(outDir.resolve("static.txt"), config, balls);
        InitialStateFile.write(outDir.resolve("initial.txt"), balls);

        final BilliardSimulation sim = new BilliardSimulation(config, balls);
        final double energyInitial = sim.kineticEnergy();
        long ioTimeNs = 0;
        final long loopStart;
        try (RunWriter.GoalsWriter goalsWriter = new RunWriter.GoalsWriter(outDir.resolve("goals.csv"));
             RunWriter.DynamicWriter dynamic = config.every() > 0
                     ? new RunWriter.DynamicWriter(outDir.resolve("dynamic.txt")) : null) {

            if (dynamic != null) {
                dynamic.writeFrame(0, sim.balls());
            }
            long events = 0;
            loopStart = System.nanoTime();
            while (true) {
                final double nextEvent = sim.nextEventTime();
                if (nextEvent >= config.tf()) {
                    sim.advanceTo(config.tf());
                    break;
                }
                final BilliardSimulation.Step step = sim.processNextEvent();
                events++;
                if (step.goal() || (dynamic != null && events % config.every() == 0)) {
                    final long ioStart = System.nanoTime();
                    if (step.goal()) {
                        goalsWriter.write(step.event().time(), sim.balls().get(step.event().a()).id());
                    }
                    if (dynamic != null && events % config.every() == 0) {
                        dynamic.writeFrame(sim.time(), sim.balls());
                    }
                    ioTimeNs += System.nanoTime() - ioStart;
                }
                if (verify) {
                    sim.verifyNoOverlaps(1e-9);
                }
                if (config.stopAtT90() && sim.reachedT90()) {
                    break;
                }
            }
            if (dynamic != null && events % config.every() != 0) {
                dynamic.writeFrame(sim.time(), sim.balls());
            }
        }
        final long loopTimeNs = System.nanoTime() - loopStart - ioTimeNs;
        final long wallTimeNs = System.nanoTime() - wallStartNs;

        RunWriter.writeRunMetadata(outDir.resolve("run.json"), config, obstaclesFile, initialFile,
                sim, energyInitial, loopTimeNs, wallTimeNs);
        return new Result(sim, energyInitial, loopTimeNs);
    }
}
