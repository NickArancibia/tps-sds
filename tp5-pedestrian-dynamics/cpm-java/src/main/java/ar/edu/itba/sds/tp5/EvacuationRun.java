package ar.edu.itba.sds.tp5;

import ar.edu.itba.sds.common.cli.CliArgs;
import ar.edu.itba.sds.tp5.cpm.Agents;
import ar.edu.itba.sds.tp5.cpm.CpmParams;
import ar.edu.itba.sds.tp5.cpm.EventLog;
import ar.edu.itba.sds.tp5.cpm.Room;
import ar.edu.itba.sds.tp5.io.Output;
import ar.edu.itba.sds.tp5.tsdmd.TimeDrivenCpm;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Random;

/**
 * Evacuación de la habitación con el CPM regido por el paso temporal (TSDMD). Corre hasta que se
 * retira el último agente (o hasta {@code t-max}) y escribe outputs crudos: los observables y las
 * animaciones se calculan offline.
 */
public final class EvacuationRun {

    private static final String USAGE = """
            Uso: java -jar cpm.jar tsdmd [opciones]

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
            Corrida:
              --seed <long>        semilla de la condición inicial y de los targets en la franja
                                   de la puerta (default 1)
              --init <archivo>     posiciones iniciales "x y" (una fila por agente) en lugar de
                                   sortearlas; N sale del archivo
              --save-every <int>   guardar un estado cada k pasos de dt (default 3); el último
                                   estado se guarda siempre que caiga en [save-t0, save-t1]
              --save-t0 <s>        guardar solo estados con t >= save-t0 (default 0)
              --save-t1 <s>        guardar solo estados con t <= save-t1 (default sin límite)
              --t-max <s>          corte si no evacuaron todos (default 3000)
              --out <dir>          directorio de salida (default output/tsdmd/N<N>_seed<seed>)
            """;

    private EvacuationRun() {
    }

    public static void run(final String[] args) throws IOException {
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
        final int saveEvery = cli.integer("save-every", 3);
        final double saveT0 = cli.number("save-t0", 0);
        final double saveT1 = cli.number("save-t1", Double.POSITIVE_INFINITY);
        final double tMax = cli.number("t-max", 3000);
        final Path outDir = Path.of(cli.string("out", "output/tsdmd/N" + n + "_seed" + seed));
        if (saveEvery < 1) {
            throw new IllegalArgumentException("--save-every debe ser >= 1");
        }

        final EventLog events = new EventLog(n);
        final TimeDrivenCpm engine = new TimeDrivenCpm(agents, room, p, events);
        final double dt = p.dt();
        final long maxSteps = (long) Math.ceil(tMax / dt);

        Files.createDirectories(outDir);
        Output.writeStatic(outDir.resolve("static.txt"), n, room.l(), p);
        final Output output = new Output();
        long step = 0;
        long saved = 0;
        long lastSaved = -1;
        final long start = System.nanoTime();
        try (BufferedWriter out = Files.newBufferedWriter(outDir.resolve("dynamic.txt"))) {
            if (saveT0 <= 0) {
                output.writeFrame(out, 0.0, agents);
                saved++;
                lastSaved = 0;
            }
            while (agents.activeCount() > 0 && step < maxSteps) {
                step++;
                final double t = step * dt;
                engine.step(t);
                if (step % saveEvery == 0 && t >= saveT0 && t <= saveT1) {
                    output.writeFrame(out, t, agents);
                    saved++;
                    lastSaved = step;
                }
            }
            final double tEnd = step * dt;
            if (lastSaved != step && tEnd >= saveT0 && tEnd <= saveT1) {
                output.writeFrame(out, tEnd, agents);
                saved++;
            }
        }
        final long loopNs = System.nanoTime() - start;
        Output.writeEvents(outDir.resolve("events.csv"), events);

        final boolean evacuated = agents.activeCount() == 0;
        final double finalTime = step * dt;
        final String json = """
                {
                  "scheme": "tsdmd",
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
                  "steps": %d,
                  "finalTime": %s,
                  "evacuated": %s,
                  "evacuationTime": %s,
                  "remaining": %d,
                  "cells": [%d, %d],
                  "rigidWallLimitedEscape": %d,
                  "rigidWallLimitedDesired": %d,
                  "loopTimeMs": %s
                }
                """.formatted(n, seed, initFile == null ? "\"random\"" : "\"" + initFile + "\"", room.l(), room.d(),
                room.exitDistance(), room.xe1(), room.xe2(),
                room.bandMin(), room.bandMax(), p.rMin(), p.rMax(), p.vdMax(), p.ve(), p.beta(), p.tau(), dt,
                p.radiusIncrement(), saveEvery, saveT0, Double.isInfinite(saveT1) ? "null" : saveT1, saved, step,
                finalTime, evacuated, evacuated ? finalTime : "null", agents.activeCount(),
                engine.contacts().cellsX(), engine.contacts().cellsY(), engine.limitedEscape(), engine.limitedDesired(),
                loopNs / 1e6);
        Files.writeString(outDir.resolve("run.json"), json);
        System.out.printf("%s: %d pasos, t = %.2f s, %s, %d estados guardados, %.0f ms%n", outDir, step, finalTime,
                evacuated ? "evacuación completa" : agents.activeCount() + " agentes sin salir", saved, loopNs / 1e6);
    }
}
