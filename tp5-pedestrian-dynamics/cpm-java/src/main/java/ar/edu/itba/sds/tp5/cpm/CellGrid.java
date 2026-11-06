package ar.edu.itba.sds.tp5.cpm;

/**
 * Grilla del Cell Index Method, común a todos los esquemas: celdas de lado {@code >= 2 r_max} (la
 * máxima distancia de contacto) sobre {@code [0, L] × [yMin, L]}, con {@code yMin} por debajo del
 * radio de retiro afuera de la puerta. Con ese lado, dos agentes en contacto están en la misma
 * celda o en celdas contiguas.
 */
public final class CellGrid {

    public final int mx;
    public final int my;
    public final double cellW;
    public final double cellH;
    public final double yMin;

    public CellGrid(final Room room, final CpmParams p) {
        this.yMin = -(room.exitDistance() + 2 * p.rMax());
        final double minCell = 2 * p.rMax();
        this.mx = Math.max(1, (int) Math.floor(room.l() / minCell));
        this.my = Math.max(1, (int) Math.floor((room.l() - yMin) / minCell));
        this.cellW = room.l() / mx;
        this.cellH = (room.l() - yMin) / my;
    }

    public int cellX(final double x) {
        return Math.max(0, Math.min(mx - 1, (int) (x / cellW)));
    }

    public int cellY(final double y) {
        return Math.max(0, Math.min(my - 1, (int) ((y - yMin) / cellH)));
    }

    public int cells() {
        return mx * my;
    }
}
