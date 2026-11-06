package ar.edu.itba.sds.tp5.cpm;

/**
 * Cuerpo impenetrable de radio {@code r_min} contra paredes y contra otros agentes en TSDMD (agregado
 * propio, no es parte del CPM del paper).
 *
 * <p>El cuerpo de un agente es el disco de radio {@code r_min} (Martin &amp; Parisi, Physica A 633,
 * 2024, Sec. 3.1) y las paredes son rígidas (enunciado). El escape del CPM suma un versor por
 * contacto: si los contactos de un lado dominan, el escape empuja al agente contra una pared o contra
 * otro agente y los cuerpos se superponen.</p>
 *
 * <p>Se aplica a la velocidad ya calculada con las reglas del CPM, antes de mover. Cada vecino
 * cercano (pared o agente) impone una restricción lineal sobre la velocidad del agente:
 * {@code v·n ≥ c}, con {@code n} el versor del vecino al agente y {@code c ≤ 0} lo máximo que el
 * agente puede acercarse por unidad de tiempo:</p>
 *
 * <ul>
 *   <li>Pared, a distancia {@code d} de su punto más cercano: {@code c = −max(0, d − r_min)/Δt}.
 *   La pared no se mueve, así que el agente puede consumir todo el hueco.</li>
 *   <li>Agente {@code j}, a distancia {@code d_ij}: {@code c = −max(0, d_ij − 2 r_min)/(2 Δt)}. Los dos
 *   se mueven en el mismo paso; si cada uno consume a lo sumo la mitad del hueco, la distancia final
 *   es {@code ≥ (x_i' − x_j')·n_ij ≥ d_ij − hueco = 2 r_min} sin importar qué haga el otro. Así cada
 *   agente se corrige solo con las posiciones del comienzo del paso: no depende del orden ni hace
 *   falta iterar.</li>
 * </ul>
 *
 * <p>La velocidad corregida es la más cercana a la original que cumple todas las restricciones
 * ({@link VelocityProjection}). Solo entran los vecinos que el agente puede alcanzar en el paso:
 * paredes con {@code d − |v|Δt < r_min} y agentes con {@code d_ij < 2 r_min + 2|v|Δt}. La proyección
 * no aumenta {@code |v|}, así que los descartados siguen sin ser alcanzables. Si dos cuerpos ya
 * estuvieran superpuestos ({@code c = 0}), la regla solo impide que se sigan acercando.</p>
 */
public final class BodyConstraints {

    private final Room room;
    private final Contacts contacts;
    private final double rMin;
    private final double dt;
    private final int[] neighbors;
    private final VelocityProjection projection = new VelocityProjection();

    public BodyConstraints(final Room room, final Contacts contacts, final CpmParams p, final int n) {
        this.room = room;
        this.contacts = contacts;
        this.rMin = p.rMin();
        this.dt = p.dt();
        this.neighbors = new int[n];
    }

    /**
     * Corrige {@code (vx[i], vy[i])}. Usa las celdas del último {@link Contacts#compute}, así que debe
     * llamarse antes de mover a cualquier agente.
     *
     * @return {@code true} si la velocidad cambió
     */
    public boolean limit(final Agents a, final int i) {
        final double reach = Math.hypot(a.vx[i], a.vy[i]) * dt;
        if (reach == 0) {
            return false;
        }
        projection.clear();
        addWalls(a, i, reach);
        addAgents(a, i, reach);
        if (!projection.project(a.vx[i], a.vy[i])) {
            return false;
        }
        a.vx[i] = projection.vx();
        a.vy[i] = projection.vy();
        return true;
    }

    private void addWalls(final Agents a, final int i, final double reach) {
        final double xi = a.x[i];
        final double yi = a.y[i];
        for (int w = 0; w < room.wallCount(); w++) {
            final double[] s = room.wall(w);
            final double sx = s[2] - s[0];
            final double sy = s[3] - s[1];
            final double u = Math.max(0, Math.min(1, ((xi - s[0]) * sx + (yi - s[1]) * sy) / (sx * sx + sy * sy)));
            final double dx = xi - (s[0] + u * sx);
            final double dy = yi - (s[1] + u * sy);
            final double d = Math.hypot(dx, dy);
            if (d == 0 || d - reach >= rMin) {
                continue;
            }
            projection.add(dx / d, dy / d, -Math.max(0, d - rMin) / dt);
        }
    }

    private void addAgents(final Agents a, final int i, final double reach) {
        final int count = contacts.neighbors(a, i, 2 * rMin + 2 * reach, neighbors);
        for (int k = 0; k < count; k++) {
            final int j = neighbors[k];
            final double dx = a.x[i] - a.x[j];
            final double dy = a.y[i] - a.y[j];
            final double d = Math.hypot(dx, dy);
            if (d == 0) {
                continue;
            }
            projection.add(dx / d, dy / d, -Math.max(0, d - 2 * rMin) / (2 * dt));
        }
    }
}
