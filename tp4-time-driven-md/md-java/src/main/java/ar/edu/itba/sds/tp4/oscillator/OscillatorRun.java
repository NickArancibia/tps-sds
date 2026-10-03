package ar.edu.itba.sds.tp4.oscillator;

import ar.edu.itba.sds.common.cli.CliArgs;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.math.BigDecimal;
import java.util.Locale;

/**
 * Sistema 1: integra el oscilador amortiguado con un esquema y un {@code dt} dados hasta
 * {@code tf}, y escribe el estado {@code t, r, v} cada {@code save-dt}. No calcula observables:
 * la solución analítica y el ECM se evalúan en post-proceso.
 */
public final class OscillatorRun {

    private static final String USAGE = """
            Sistema 1 - Oscilador puntual amortiguado (Teórica 4, diapositiva 37)

            Uso:
              java -jar md.jar oscillator --scheme <esquema> [opciones]

            Integración:
              --scheme <nombre>   %s
              --dt <double>       Paso de integración (s)                         (default 1e-3)
              --tf <double>       Tiempo final (s), múltiplo de dt                 (default 5)
              --save-dt <double>  Intervalo de guardado (s), múltiplo de dt        (default 1e-2)

            Sistema:
              --m <double>        Masa (kg)                                        (default 70)
              --k <double>        Constante elástica (N/m)                         (default 1e4)
              --gamma <double>    Coeficiente de amortiguamiento (kg/s)            (default 100)
              --r0 <double>       Posición inicial r(0) = A (m)                    (default 1)
              --v0 <double>       Velocidad inicial (m/s)                          (default -r0*gamma/(2m))

              --out <dir>         Directorio de salida  (default output/oscillator/<esquema>_dt<dt>)

            Salida (en <out>):
              trajectory.csv      t,r,v cada save-dt, incluyendo t = 0 y t = tf (precisión completa)
              run.json            inputs, cantidad de pasos y tiempo del lazo
            """;

    private OscillatorRun() {
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
        final Scheme scheme = Scheme.fromCli(cli.string("scheme", ""));
        final double dt = cli.number("dt", 1e-3);
        final double tf = cli.number("tf", 5.0);
        final double saveDt = cli.number("save-dt", 1e-2);
        final DampedOscillator oscillator = new DampedOscillator(
                cli.number("m", 70.0), cli.number("k", 1e4), cli.number("gamma", 100.0));
        final double r0 = cli.number("r0", 1.0);
        final double v0 = cli.number("v0", -r0 * oscillator.gamma() / (2 * oscillator.mass()));
        if (dt <= 0 || tf <= 0 || saveDt <= 0) {
            throw new IllegalArgumentException("dt, tf y save-dt tienen que ser positivos");
        }
        final long steps = multipleOf(tf, dt, "tf");
        final long saveEvery = multipleOf(saveDt, dt, "save-dt");
        final Path outDir = Path.of(cli.string("out",
                "output/oscillator/" + scheme.cliName() + "_dt" + compact(dt)));
        Files.createDirectories(outDir);

        final Integrator integrator = scheme.create(oscillator, oscillator.mass(), dt, r0, v0);
        final long start = System.nanoTime();
        try (BufferedWriter out = Files.newBufferedWriter(outDir.resolve("trajectory.csv"))) {
            out.write("t,r,v\n");
            writeRow(out, 0.0, integrator);
            for (long step = 1; step <= steps; step++) {
                integrator.step();
                if (step % saveEvery == 0) {
                    writeRow(out, step * dt, integrator);
                }
            }
        }
        final long loopNs = System.nanoTime() - start;

        writeRunJson(outDir.resolve("run.json"), scheme, oscillator, r0, v0, dt, tf, saveDt,
                steps, saveEvery, loopNs);
        System.out.printf(Locale.US, "%s  dt = %s s  pasos = %d  guardados = %d  lazo = %.1f ms  -> %s%n",
                scheme.cliName(), compact(dt), steps, steps / saveEvery + 1, loopNs / 1e6, outDir);
    }

    /** Cantidad entera de {@code dt} en {@code value}; error si no es un múltiplo exacto. */
    private static long multipleOf(final double value, final double dt, final String name) {
        final long count = Math.round(value / dt);
        if (count < 1 || Math.abs(count * dt - value) > 1e-9 * value) {
            throw new IllegalArgumentException(name + " = " + value + " no es múltiplo entero de dt = " + dt);
        }
        return count;
    }

    private static void writeRow(final BufferedWriter out, final double t, final Integrator integrator)
            throws IOException {
        out.write(Double.toString(t));
        out.write(',');
        out.write(Double.toString(integrator.position()));
        out.write(',');
        out.write(Double.toString(integrator.velocity()));
        out.write('\n');
    }

    private static void writeRunJson(final Path path, final Scheme scheme, final DampedOscillator osc,
                                     final double r0, final double v0, final double dt, final double tf,
                                     final double saveDt, final long steps, final long saveEvery,
                                     final long loopNs) throws IOException {
        final String json = """
                {
                  "system": "oscillator",
                  "scheme": "%s",
                  "m": %s,
                  "k": %s,
                  "gamma": %s,
                  "r0": %s,
                  "v0": %s,
                  "dt": %s,
                  "tf": %s,
                  "saveDt": %s,
                  "steps": %d,
                  "saveEvery": %d,
                  "loopTimeMs": %s
                }
                """.formatted(scheme.cliName(), osc.mass(), osc.k(), osc.gamma(), r0, v0, dt, tf,
                saveDt, steps, saveEvery, loopNs / 1e6);
        Files.writeString(path, json);
    }

    /** {@code 1.0E-3} → {@code 0.001}, {@code 2.5E-4} → {@code 0.00025}: nombre corto sin perder dígitos. */
    private static String compact(final double value) {
        return BigDecimal.valueOf(value).stripTrailingZeros().toString();
    }
}
