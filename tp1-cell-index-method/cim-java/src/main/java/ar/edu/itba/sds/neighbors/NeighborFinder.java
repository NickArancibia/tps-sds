package ar.edu.itba.sds.neighbors;

import ar.edu.itba.sds.model.NeighborLists;
import ar.edu.itba.sds.model.Particle;

import java.util.List;

/**
 * Estrategia de búsqueda de partículas vecinas.
 *
 * <p>La búsqueda es una función pura sobre el estado {@code (posiciones, radios)}: no guarda
 * estado del sistema entre llamadas. Eso permite invocarla en cada paso temporal de una simulación
 * dinámica (TPs siguientes) reutilizando la misma instancia.</p>
 */
public interface NeighborFinder {

    /**
     * Calcula, para cada partícula, las vecinas cuya distancia <b>borde a borde</b> es menor que rc.
     *
     * @param particles partículas del sistema; el índice en la lista identifica a la partícula
     *                  dentro del resultado.
     */
    NeighborLists findNeighbors(List<Particle> particles);

    /** Nombre del método, para reportes y CSVs. */
    String name();
}
