package ar.edu.itba.sds.tp5.tsdmd;

import ar.edu.itba.sds.tp5.cpm.Agents;
import ar.edu.itba.sds.tp5.cpm.BodyConstraints;
import ar.edu.itba.sds.tp5.cpm.Contacts;
import ar.edu.itba.sds.tp5.cpm.CpmParams;
import ar.edu.itba.sds.tp5.cpm.EventLog;
import ar.edu.itba.sds.tp5.cpm.Room;
import ar.edu.itba.sds.tp5.cpm.Targets;

/**
 * CPM regido por el paso temporal, tal cual el pseudocódigo del paper. Cada paso recorre todos los
 * agentes activos en iteraciones separadas (actualización sincrónica):
 *
 * <ol>
 *   <li>Contactos y suma de versores de escape ({@link Contacts}).</li>
 *   <li>Radios: con contacto {@code r = r_min}; sin contacto {@code r = min(r + Δr, r_max)}.</li>
 *   <li>Target y velocidad deseada {@code v_d(r) e_target}.</li>
 *   <li>Velocidad: con contacto {@code v_e Σe/|Σe|} (nula si la suma se anula); sin contacto
 *   {@code v_d}. Luego la restricción de cuerpo impenetrable contra paredes y agentes
 *   ({@link BodyConstraints}, agregado propio), con las posiciones del comienzo del paso.
 *   Posición: {@code x(t) = x(t − Δt) + v(t) Δt}.</li>
 * </ol>
 *
 * <p>Después de mover se actualizan las fases: cruzar {@code y <= 0} pasa el agente a
 * {@link Agents#EXITING} y alejarse {@code exitDistance} del centro de la puerta lo retira.</p>
 */
public final class TimeDrivenCpm {

    private final Agents a;
    private final Room room;
    private final CpmParams p;
    private final Contacts contacts;
    private final BodyConstraints bodies;
    private final EventLog events;
    private final double dt;
    private final double dr;
    /** Pasos-agente en que la restricción de cuerpo cambió una velocidad de escape o una deseada. */
    private long limitedEscape;
    private long limitedDesired;

    public TimeDrivenCpm(final Agents agents, final Room room, final CpmParams params, final EventLog events) {
        this.a = agents;
        this.room = room;
        this.p = params;
        this.events = events;
        this.contacts = new Contacts(room, params, agents.n());
        this.bodies = new BodyConstraints(room, contacts, params, agents.n());
        this.dt = params.dt();
        this.dr = params.radiusIncrement();
        final int[] active = a.active();
        for (int k = 0; k < a.activeCount(); k++) {
            Targets.update(a, active[k], room);
        }
    }

    /** Avanza un paso; {@code t} es el instante al final del paso (para registrar eventos). */
    public void step(final double t) {
        final int[] active = a.active();
        final int count = a.activeCount();

        updateVelocities(active, count);

        for (int k = 0; k < count; k++) {
            final int i = active[k];
            a.x[i] += a.vx[i] * dt;
            a.y[i] += a.vy[i] * dt;
        }

        // De atrás hacia adelante: remove(k) trae a la posición k el último activo, ya revisado.
        for (int k = count - 1; k >= 0; k--) {
            final int i = active[k];
            if (a.phase[i] == Agents.IN_ROOM && a.y[i] <= 0) {
                a.phase[i] = Agents.EXITING;
                events.add(t, i, EventLog.DOOR);
            }
            if (a.phase[i] == Agents.EXITING && room.hasLeft(a.x[i], a.y[i])) {
                a.remove(k);
                events.add(t, i, EventLog.EXIT);
            }
        }
    }

    /**
     * Iteraciones 1–4 del paso del CPM (contactos, radios, targets y velocidades, restricción de
     * cuerpo) para los agentes {@code ids[0..count)}, con sus posiciones actuales. No mueve.
     */
    public void updateVelocities(final int[] ids, final int count) {
        contacts.compute(a, ids, count);

        for (int k = 0; k < count; k++) {
            final int i = ids[k];
            a.r[i] = a.contact[i] ? p.rMin() : Math.min(a.r[i] + dr, p.rMax());
        }

        for (int k = 0; k < count; k++) {
            final int i = ids[k];
            Targets.update(a, i, room);
            if (a.contact[i]) {
                final double norm = Math.hypot(a.ex[i], a.ey[i]);
                if (norm > 0) {
                    a.vx[i] = p.ve() * a.ex[i] / norm;
                    a.vy[i] = p.ve() * a.ey[i] / norm;
                } else {
                    a.vx[i] = 0;
                    a.vy[i] = 0;
                }
            } else {
                final double dx = a.tx[i] - a.x[i];
                final double dy = a.ty[i] - a.y[i];
                final double dist = Math.hypot(dx, dy);
                final double speed = dist > 0 ? p.desiredSpeed(a.r[i]) / dist : 0;
                a.vx[i] = speed * dx;
                a.vy[i] = speed * dy;
            }
            if (bodies.limit(a, i)) {
                if (a.contact[i]) {
                    limitedEscape++;
                } else {
                    limitedDesired++;
                }
            }
        }
    }

    public Contacts contacts() {
        return contacts;
    }

    public long limitedEscape() {
        return limitedEscape;
    }

    public long limitedDesired() {
        return limitedDesired;
    }
}
