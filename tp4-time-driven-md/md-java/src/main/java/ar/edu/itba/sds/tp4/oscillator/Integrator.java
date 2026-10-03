package ar.edu.itba.sds.tp4.oscillator;

/**
 * Esquema de integración de una partícula en 1D con paso fijo {@code dt}. Recién construido
 * representa el instante t = 0; cada {@link #step()} avanza un {@code dt}. Después de cada
 * llamada, {@link #position()} y {@link #velocity()} corresponden al mismo instante.
 *
 * <p>Cuando la fuerza depende de una velocidad que el esquema todavía no conoce, se usa en todos
 * los esquemas el mismo criterio: predecirla con Euler, evaluar la fuerza y corregir.</p>
 */
public interface Integrator {

    void step();

    double position();

    double velocity();
}
