package ar.edu.itba.sds.tp4;

import ar.edu.itba.sds.tp4.billiard.BilliardRun;
import ar.edu.itba.sds.tp4.oscillator.OscillatorRun;

import java.io.IOException;
import java.util.Arrays;

/**
 * CLI del TP4. El primer argumento elige el sistema; el resto son las opciones de ese sistema.
 * La simulación solo escribe outputs crudos: observables y animaciones se calculan offline.
 */
public final class Main {

    private static final String USAGE = """
            SdS TP4 - Dinámica molecular regida por el paso temporal

            Uso:
              java -jar md.jar oscillator [opciones]   Sistema 1: oscilador puntual amortiguado
              java -jar md.jar billiard [opciones]     Sistema 2: billar circular
              java -jar md.jar <sistema> --help        Opciones de cada sistema
            """;

    private Main() {
    }

    public static void main(final String[] args) {
        if (args.length == 0 || "--help".equals(args[0])) {
            System.out.print(USAGE);
            return;
        }
        final String[] rest = Arrays.copyOfRange(args, 1, args.length);
        try {
            switch (args[0]) {
                case "oscillator" -> OscillatorRun.run(rest);
                case "billiard" -> BilliardRun.run(rest);
                default -> throw new IllegalArgumentException("Sistema desconocido: " + args[0] + "\n" + USAGE);
            }
        } catch (final IllegalArgumentException | IllegalStateException e) {
            System.err.println("ERROR: " + e.getMessage());
            System.exit(1);
        } catch (final IOException e) {
            System.err.println("ERROR de E/S: " + e.getMessage());
            System.exit(1);
        }
    }
}
