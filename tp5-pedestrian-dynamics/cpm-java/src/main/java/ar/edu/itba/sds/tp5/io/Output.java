package ar.edu.itba.sds.tp5.io;

import ar.edu.itba.sds.tp5.cpm.Agents;
import ar.edu.itba.sds.tp5.cpm.CpmParams;
import ar.edu.itba.sds.tp5.cpm.EventLog;

import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

/**
 * Archivos crudos de una corrida (formato de la cátedra extendido con lo propio del CPM).
 *
 * <ul>
 *   <li>{@code static.txt}: {@code N}, {@code L} y una fila {@code r_min r_max} por agente.</li>
 *   <li>{@code dynamic.txt}: por cada estado guardado, una línea con {@code t} y N filas
 *   {@code x y vx vy r tx ty fase contacto esquema} (fila = id). {@code (tx, ty)} es el target
 *   vigente; fase 0 = en la habitación, 1 = cruzó la puerta, 2 = retirado (posición congelada);
 *   contacto 0/1; esquema 0 = TSDMD, 1 = EDMD.</li>
 *   <li>{@code events.csv}: {@code t,id,event} con {@code event} = door | exit.</li>
 * </ul>
 */
public final class Output {

    private static final long[] POW10 = {1, 10, 100, 1_000, 10_000, 100_000, 1_000_000, 10_000_000};
    private static final int POS_DECIMALS = 5;

    private final StringBuilder sb = new StringBuilder(1 << 16);

    public static void writeStatic(final Path path, final int n, final double l, final CpmParams p) throws IOException {
        try (BufferedWriter out = Files.newBufferedWriter(path)) {
            out.write(n + "\n");
            out.write(l + "\n");
            final String row = p.rMin() + " " + p.rMax() + "\n";
            for (int i = 0; i < n; i++) {
                out.write(row);
            }
        }
    }

    public void writeFrame(final BufferedWriter out, final double t, final Agents a) throws IOException {
        sb.setLength(0);
        fixed(t, 6);
        sb.append('\n');
        for (int i = 0; i < a.n(); i++) {
            fixed(a.x[i], POS_DECIMALS);
            sb.append(' ');
            fixed(a.y[i], POS_DECIMALS);
            sb.append(' ');
            fixed(a.vx[i], POS_DECIMALS);
            sb.append(' ');
            fixed(a.vy[i], POS_DECIMALS);
            sb.append(' ');
            fixed(a.r[i], POS_DECIMALS);
            sb.append(' ');
            fixed(a.tx[i], POS_DECIMALS);
            sb.append(' ');
            fixed(a.ty[i], POS_DECIMALS);
            sb.append(' ').append(a.phase[i]).append(' ').append(a.contact[i] ? '1' : '0')
                    .append(' ').append(a.scheme[i]).append('\n');
        }
        out.append(sb);
    }

    public static void writeEvents(final Path path, final EventLog events) throws IOException {
        try (BufferedWriter out = Files.newBufferedWriter(path)) {
            out.write("t,id,event\n");
            for (int k = 0; k < events.size(); k++) {
                out.write(Double.toString(events.time(k)));
                out.write(',');
                out.write(Integer.toString(events.agent(k) + 1));
                out.write(events.type(k) == EventLog.DOOR ? ",door\n" : ",exit\n");
            }
        }
    }

    /** Punto fijo con {@code decimals} decimales sin pasar por {@code String.format}. */
    private void fixed(final double v, final int decimals) {
        final long scale = POW10[decimals];
        long q = Math.round(v * scale);
        if (q < 0) {
            sb.append('-');
            q = -q;
        }
        sb.append(q / scale).append('.');
        final long frac = q % scale;
        for (long d = scale / 10; d > frac && d > 1; d /= 10) {
            sb.append('0');
        }
        sb.append(frac);
    }
}
