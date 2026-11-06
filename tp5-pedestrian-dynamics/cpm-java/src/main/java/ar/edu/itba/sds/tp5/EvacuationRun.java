package ar.edu.itba.sds.tp5;

import ar.edu.itba.sds.common.cli.CliArgs;
import ar.edu.itba.sds.tp5.cpm.Agents;
import ar.edu.itba.sds.tp5.cpm.CellGrid;
import ar.edu.itba.sds.tp5.cpm.CpmParams;
import ar.edu.itba.sds.tp5.cpm.EventLog;
import ar.edu.itba.sds.tp5.cpm.Room;
import ar.edu.itba.sds.tp5.edmd.EventDrivenCpm;
import ar.edu.itba.sds.tp5.edmd.Recovery;
import ar.edu.itba.sds.tp5.io.Output;
import ar.edu.itba.sds.tp5.tsdmd.TimeDrivenCpm;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Random;

/**
 * Evacuación de la habitación con el CPM, regida por el paso temporal (TSDMD) o por eventos (EDMD).
 * Corre hasta que se retira el último agente (o hasta {@code t-max}) y escribe outputs crudos: los
 * observables y las animaciones se calculan offline.
 */
public final class EvacuationRun {

    private static final String USAGE = """
            Uso: java -jar cpm.jar tsdmd|edmd [opciones]

            Sistema (enunciado):
              --N <int>            agentes (default 500)
              --L <m>              lado de la habitación (default 50)
              --d <m>              ancho de la puerta (default 0.8)
              --exit <m>           distancia de retiro (al centro de la puerta) y ordenada del
                                   segundo target (x_i, -exit) (default 1)
            CPM (enunciado y paper):
              --rmin <m>           default 0.10
              --rmax <m>           default 0.25
              --vd <m/s>           rapidez deseada máxima (default 1.5)
              --ve <m/s>           rapidez de escape (default = vd)
              --beta <num>         default 0.9
              --tau <s>            default 0.5
            Recuperación en EDMD:
              --levels <int>       radios intermedios de TSDMD que se recorren, un dt cada uno desde
                                   r_min + dr; el último se sostiene hasta el final de la
                                   recuperación (0: quieto en r_min; 8 = TSDMD) (default 8)
            Corrida:
              --seed <long>        semilla de la condición inicial y de los targets en la franja
                                   de la puerta (default 1)
              --init <archivo>     posiciones iniciales "x y" (una fila por agente) en lugar de
                                   sortearlas; N sale del archivo
              --save-every <int>   TSDMD: guardar un estado cada k pasos de dt (default 3). EDMD:
                                   guardar el estado cada k eventos, sin contar los cruces de celda
                                   (default 1000; 1 = todos, para animar). El último estado se
                                   guarda siempre que caiga en [save-t0, save-t1]
              --save-t0 <s>        guardar solo estados con t >= save-t0 (default 0)
              --save-t1 <s>        guardar solo estados con t <= save-t1 (default sin límite)
              --t-max <s>          corte si no evacuaron todos (default 3000)
              --out <dir>          directorio de salida (default output/<esquema>/N<N>_seed<seed>)
            """;

    private EvacuationRun() {
    }

    public static void run(final String scheme, final String[] args) throws IOException {
        final CliArgs cli = CliArgs.parse(args);
        if (cli.has("help")) {
            System.out.print(USAGE);
            return;
        }
        final String initFile = cli.string("init", null);
        final Room room = new Room(cli.number("L", 50), cli.number("d", 0.8), cli.number("exit", 1));
        final double vd = cli.number("vd", 1.5);
        final CpmParams p = new CpmParams(cli.number("rmin", 0.10), cli.number("rmax", 0.25), vd,
                cli.number("ve", vd), cli.number("beta", 0.9), cli.number("tau", 0.5));
        final long seed = cli.longValue("seed", 1);
        final Random random = new Random(seed);
        final Agents agents = initFile == null
                ? Agents.random(cli.integer("N", 500), room, p, random)
                : Agents.fromFile(Path.of(initFile), room, p, random);
        final int n = agents.n();
        final int saveEvery = cli.integer("save-every", "edmd".equals(scheme) ? 1000 : 3);
        final double saveT0 = cli.number("save-t0", 0);
        final double saveT1 = cli.number("save-t1", Double.POSITIVE_INFINITY);
        final double tMax = cli.number("t-max", 3000);
        final Path outDir = Path.of(cli.string("out", "output/" + scheme + "/N" + n + "_seed" + seed));
        if (saveEvery < 1) {
            throw new IllegalArgumentException("--save-every debe ser >= 1");
        }
        final Recovery recovery = "edmd".equals(scheme)
                ? new Recovery(p, cli.integer("levels", Recovery.maxLevels(p)))
                : null;

        final EventLog events = new EventLog(n);
        Files.createDirectories(outDir);
        Output.writeStatic(outDir.resolve("static.txt"), n, room.l(), p);
        final Output output = new Output();
        final double dt = p.dt();
        final Window window = new Window(saveT0, saveT1);
        final double finalTime;
        final String schemeJson;
        final String summary;
        final long start = System.nanoTime();
        try (BufferedWriter out = Files.newBufferedWriter(outDir.resolve("dynamic.txt"))) {
            if (window.contains(0)) {
                output.writeFrame(out, 0.0, agents);
                window.saved(0);
            }
            if (recovery == null) {
                final TimeDrivenCpm engine = new TimeDrivenCpm(agents, room, p, events);
                final long maxSteps = (long) Math.ceil(tMax / dt);
                long step = 0;
                while (agents.activeCount() > 0 && step < maxSteps) {
                    step++;
                    final double t = step * dt;
                    engine.step(t);
                    if (step % saveEvery == 0 && window.contains(t)) {
                        output.writeFrame(out, t, agents);
                        window.saved(t);
                    }
                }
                finalTime = step * dt;
                if (window.lastSaved != finalTime && window.contains(finalTime)) {
                    output.writeFrame(out, finalTime, agents);
                    window.saved(finalTime);
                }
                schemeJson = """
                          "steps": %d,
                          "cells": [%d, %d],
                          "bodyLimitedEscape": %d,
                          "bodyLimitedDesired": %d,
                        """.formatted(step, engine.contacts().grid().mx, engine.contacts().grid().my,
                        engine.limitedEscape(), engine.limitedDesired());
                summary = step + " pasos";
            } else {
                final EventDrivenCpm engine = new EventDrivenCpm(agents, room, p, recovery, events);
                long changes = 0;
                while (agents.activeCount() > 0 && engine.processNext()) {
                    final double t = engine.time();
                    if (t > tMax) {
                        break;
                    }
                    if (engine.lastEventChangedState() && ++changes % saveEvery == 0 && window.contains(t)) {
                        engine.writeState(() -> output.writeFrame(out, t, agents));
                        window.saved(t);
                    }
                }
                finalTime = engine.time();
                if (window.lastSaved != finalTime && window.contains(finalTime)) {
                    engine.writeState(() -> output.writeFrame(out, finalTime, agents));
                    window.saved(finalTime);
                }
                final CellGrid grid = engine.grid();
                schemeJson = """
                          "levels": %d,
                          "cells": [%d, %d],
                          "events": %s,
                        """.formatted(recovery.levels(), grid.mx, grid.my, engine.statsJson());
                summary = engine.processedEvents() + " eventos";
            }
        }
        final long loopNs = System.nanoTime() - start;
        Output.writeEvents(outDir.resolve("events.csv"), events);

        final boolean evacuated = agents.activeCount() == 0;
        final String json = """
                {
                  "scheme": "%s",
                  "N": %d,
                  "seed": %d,
                  "init": %s,
                  "L": %s,
                  "d": %s,
                  "exitDistance": %s,
                  "doorX1": %s,
                  "doorX2": %s,
                  "targetBand": [%s, %s],
                  "rMin": %s,
                  "rMax": %s,
                  "vdMax": %s,
                  "ve": %s,
                  "beta": %s,
                  "tau": %s,
                  "dt": %s,
                  "dr": %s,
                  "saveEvery": %d,
                  "saveT0": %s,
                  "saveT1": %s,
                  "savedFrames": %d,
                  "finalTime": %s,
                  "evacuated": %s,
                  "evacuationTime": %s,
                  "remaining": %d,
                %s  "loopTimeMs": %s
                }
                """.formatted(scheme, n, seed, initFile == null ? "\"random\"" : "\"" + initFile + "\"", room.l(),
                room.d(), room.exitDistance(), room.xe1(), room.xe2(), room.bandMin(), room.bandMax(), p.rMin(),
                p.rMax(), p.vdMax(), p.ve(), p.beta(), p.tau(), dt, p.radiusIncrement(), saveEvery, saveT0,
                Double.isInfinite(saveT1) ? "null" : saveT1, window.count, finalTime, evacuated,
                evacuated ? finalTime : "null", agents.activeCount(), schemeJson, loopNs / 1e6);
        Files.writeString(outDir.resolve("run.json"), json);
        System.out.printf("%s: %s, t = %.2f s, %s, %d estados guardados, %.0f ms%n", outDir, summary, finalTime,
                evacuated ? "evacuación completa" : agents.activeCount() + " agentes sin salir", window.count,
                loopNs / 1e6);
    }

    /** Ventana de guardado {@code [t0, t1]} y estados escritos. */
    private static final class Window {
        private final double t0;
        private final double t1;
        private long count;
        private double lastSaved = Double.NaN;

        private Window(final double t0, final double t1) {
            this.t0 = t0;
            this.t1 = t1;
        }

        private boolean contains(final double t) {
            return t >= t0 && t <= t1;
        }

        private void saved(final double t) {
            count++;
            lastSaved = t;
        }
    }
}
