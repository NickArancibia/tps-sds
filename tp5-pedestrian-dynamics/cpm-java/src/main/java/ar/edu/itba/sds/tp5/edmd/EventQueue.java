package ar.edu.itba.sds.tp5.edmd;

/**
 * Cola de prioridad de eventos (heap binario sobre arreglos primitivos, sin objetos por evento).
 * Cada evento guarda su tipo, los agentes involucrados ({@code b = -1} si es uno solo, o el índice
 * de la pared para un contacto con pared) y el contador de cambios de cada agente al momento de
 * predecirlo: si alguno cambió después, el evento quedó obsoleto y se descarta al sacarlo.
 */
public final class EventQueue {

    private double[] time = new double[1 << 12];
    private byte[] type = new byte[1 << 12];
    private int[] a = new int[1 << 12];
    private int[] b = new int[1 << 12];
    private int[] ca = new int[1 << 12];
    private int[] cb = new int[1 << 12];
    private int size;
    private long pushed;

    /** Campos del último evento sacado con {@link #pop()}. */
    public double topTime;
    public byte topType;
    public int topA;
    public int topB;
    public int topCa;
    public int topCb;

    public boolean isEmpty() {
        return size == 0;
    }

    /** Instante del próximo evento (infinito si la cola está vacía). */
    public double peekTime() {
        return size == 0 ? Double.POSITIVE_INFINITY : time[0];
    }

    public long pushed() {
        return pushed;
    }

    public void push(final double t, final byte kind, final int i, final int j, final int ci, final int cj) {
        if (size == time.length) {
            final int cap = 2 * size;
            time = java.util.Arrays.copyOf(time, cap);
            type = java.util.Arrays.copyOf(type, cap);
            a = java.util.Arrays.copyOf(a, cap);
            b = java.util.Arrays.copyOf(b, cap);
            ca = java.util.Arrays.copyOf(ca, cap);
            cb = java.util.Arrays.copyOf(cb, cap);
        }
        int k = size++;
        pushed++;
        while (k > 0) {
            final int parent = (k - 1) >>> 1;
            if (time[parent] <= t) {
                break;
            }
            move(parent, k);
            k = parent;
        }
        time[k] = t;
        type[k] = kind;
        a[k] = i;
        b[k] = j;
        ca[k] = ci;
        cb[k] = cj;
    }

    public void pop() {
        topTime = time[0];
        topType = type[0];
        topA = a[0];
        topB = b[0];
        topCa = ca[0];
        topCb = cb[0];
        size--;
        if (size == 0) {
            return;
        }
        final double t = time[size];
        int k = 0;
        while (true) {
            int child = 2 * k + 1;
            if (child >= size) {
                break;
            }
            if (child + 1 < size && time[child + 1] < time[child]) {
                child++;
            }
            if (t <= time[child]) {
                break;
            }
            move(child, k);
            k = child;
        }
        move(size, k);
    }

    private void move(final int from, final int to) {
        time[to] = time[from];
        type[to] = type[from];
        a[to] = a[from];
        b[to] = b[from];
        ca[to] = ca[from];
        cb[to] = cb[from];
    }
}
