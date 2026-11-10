package ar.edu.itba.sds.tp5;

import java.io.IOException;
import java.util.Arrays;

/**
 * CLI del TP5. El primer argumento elige el esquema; el resto son las opciones de la corrida.
 * La simulación solo escribe outputs crudos: observables y animaciones se calculan offline.
 */
public final class Main {

    private static final String USAGE = """
            SdS TP5 - Evacuación con el CPM

            Uso:
              java -jar cpm.jar tsdmd [opciones]    CPM regido por el paso temporal
              java -jar cpm.jar edmd [opciones]     CPM regido por eventos
              java -jar cpm.jar hybrid [opciones]   esquema híbrido (EDMD + TSDMD)
              java -jar cpm.jar tsdmd --help        Opciones (comunes a los tres esquemas)
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
                case "tsdmd", "edmd", "hybrid" -> EvacuationRun.run(args[0], rest);
                default -> throw new IllegalArgumentException("Esquema desconocido: " + args[0] + "\n" + USAGE);
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
