package ar.edu.itba.sds.tp5.cpm;

/**
 * Instantes en que cada agente cruza la línea de la puerta ({@link #DOOR}) y en que se retira
 * ({@link #EXIT}). Con estos registros se reconstruyen sin re-simular la curva de población y el
 * tiempo de evacuación.
 */
public final class EventLog {

    public static final byte DOOR = 0;
    public static final byte EXIT = 1;

    private final double[] t;
    private final int[] id;
    private final byte[] type;
    private int size;
    private int exits;

    /** Cada agente genera a lo sumo un evento de cada tipo. */
    public EventLog(final int n) {
        t = new double[2 * n];
        id = new int[2 * n];
        type = new byte[2 * n];
    }

    public void add(final double time, final int agent, final byte kind) {
        t[size] = time;
        id[size] = agent;
        type[size] = kind;
        size++;
        if (kind == EXIT) {
            exits++;
        }
    }

    public int size() {
        return size;
    }

    public double time(final int k) {
        return t[k];
    }

    public int agent(final int k) {
        return id[k];
    }

    public byte type(final int k) {
        return type[k];
    }

    public int exits() {
        return exits;
    }
}
