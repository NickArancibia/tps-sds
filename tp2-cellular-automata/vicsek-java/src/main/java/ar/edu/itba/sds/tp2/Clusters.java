package ar.edu.itba.sds.tp2;

import ar.edu.itba.sds.common.model.NeighborLists;

/**
 * Detección de clusters sobre el grafo de vecindad: un cluster es un conjunto de partículas donde
 * todo par está conectado por una cadena de saltos entre vecinos (distancia &lt; rc).
 *
 * <p>Se resuelve con union-find (compresión de caminos + unión por tamaño): O(E·α(N)) sobre los
 * pares de vecinos que ya calculó el CIM, sin volver a mirar posiciones.</p>
 */
public final class Clusters {

    private Clusters() {
    }

    /** Fracción de partículas que pertenecen al cluster más grande (el observable S). */
    public static double largestClusterFraction(final NeighborLists neighbors) {
        final int n = neighbors.size();
        final int[] parent = new int[n];
        final int[] size = new int[n];
        for (int i = 0; i < n; i++) {
            parent[i] = i;
            size[i] = 1;
        }

        for (int i = 0; i < n; i++) {
            for (final int j : neighbors.neighborsOf(i)) {
                if (j > i) {
                    union(parent, size, i, j);
                }
            }
        }

        int largest = 0;
        for (int i = 0; i < n; i++) {
            if (find(parent, i) == i) {
                largest = Math.max(largest, size[i]);
            }
        }
        return (double) largest / n;
    }

    private static int find(final int[] parent, final int i) {
        int root = i;
        while (parent[root] != root) {
            root = parent[root];
        }
        int cursor = i;
        while (parent[cursor] != root) {
            final int next = parent[cursor];
            parent[cursor] = root;
            cursor = next;
        }
        return root;
    }

    private static void union(final int[] parent, final int[] size, final int i, final int j) {
        final int rootI = find(parent, i);
        final int rootJ = find(parent, j);
        if (rootI == rootJ) {
            return;
        }
        if (size[rootI] < size[rootJ]) {
            parent[rootI] = rootJ;
            size[rootJ] += size[rootI];
        } else {
            parent[rootJ] = rootI;
            size[rootI] += size[rootJ];
        }
    }
}
