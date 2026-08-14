package ar.edu.itba.sds.generator;

import ar.edu.itba.sds.common.model.Particle;
import ar.edu.itba.sds.model.SystemConfig;

import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * Genera N partículas con posiciones aleatorias y radios uniformes en [rMin, rMax],
 * <b>sin solapamiento</b>.
 *
 * <p>Estrategia de rechazo: se sortea una posición candidata y, si se solapa con alguna partícula
 * ya colocada ({@code dist(centros) < r_i + r_j}), se descarta y se sortea otra. No se relaja ni se
 * "empuja" a las partículas.</p>
 *
 * <p>El chequeo de solapamiento usa una grilla auxiliar de celdas de lado {@code 2*rMax}: alcanza
 * con mirar las 9 celdas alrededor de la candidata en lugar de las N partículas ya colocadas, lo
 * que hace viable generar sistemas densos.</p>
 *
 * <p>Si se supera el límite de intentos, la densidad pedida es (en la práctica) irrealizable y se
 * lanza una excepción indicando cuántas partículas se llegaron a colocar. Eso es lo que define el
 * "máximo N generable en la geometría" que pide el enunciado.</p>
 */
public final class ParticleGenerator {

    private static final int DEFAULT_MAX_ATTEMPTS_PER_PARTICLE = 20_000;

    private final double l;
    private final double rMin;
    private final double rMax;
    private final boolean periodic;
    private final int maxAttemptsPerParticle;

    private final int cells;
    private final double cellSize;
    private final List<List<Integer>> grid;

    public ParticleGenerator(final SystemConfig config) {
        this(config.l(), config.rMin(), config.rMax(), config.periodic(),
                DEFAULT_MAX_ATTEMPTS_PER_PARTICLE);
    }

    public ParticleGenerator(final double l, final double rMin, final double rMax,
                             final boolean periodic, final int maxAttemptsPerParticle) {
        this.l = l;
        this.rMin = rMin;
        this.rMax = rMax;
        this.periodic = periodic;
        this.maxAttemptsPerParticle = maxAttemptsPerParticle;
        this.cells = Math.max(1, (int) Math.floor(l / (2 * rMax)));
        this.cellSize = l / cells;
        this.grid = new ArrayList<>(cells * cells);
        for (int i = 0; i < cells * cells; i++) {
            grid.add(new ArrayList<>());
        }
    }

    public List<Particle> generate(final int n, final long seed) {
        final Random random = new Random(seed);
        final List<Particle> particles = new ArrayList<>(n);
        for (final List<Integer> cell : grid) {
            cell.clear();
        }

        final double[] xs = new double[n];
        final double[] ys = new double[n];
        final double[] rs = new double[n];

        for (int i = 0; i < n; i++) {
            final double radius = rMin + random.nextDouble() * (rMax - rMin);
            boolean placed = false;

            for (int attempt = 0; attempt < maxAttemptsPerParticle && !placed; attempt++) {
                final double x;
                final double y;
                if (periodic) {
                    // Con contorno periódico no hay paredes: el centro puede estar en cualquier lado.
                    x = random.nextDouble() * l;
                    y = random.nextDouble() * l;
                } else {
                    // Sin contorno periódico la partícula entera debe caber dentro del área.
                    x = radius + random.nextDouble() * (l - 2 * radius);
                    y = radius + random.nextDouble() * (l - 2 * radius);
                }
                if (!overlaps(x, y, radius, xs, ys, rs)) {
                    xs[i] = x;
                    ys[i] = y;
                    rs[i] = radius;
                    particles.add(new Particle(i + 1, x, y, radius));
                    grid.get(cellOf(x, y)).add(i);
                    placed = true;
                }
            }

            if (!placed) {
                throw new IllegalStateException(String.format(java.util.Locale.US,
                        "No se pudo colocar la partícula %d de %d sin solapamiento tras %d intentos "
                                + "(L=%.4f, radios en [%.4f, %.4f]). La densidad pedida no es "
                                + "alcanzable por muestreo por rechazo: reducir N o aumentar L.",
                        i + 1, n, maxAttemptsPerParticle, l, rMin, rMax));
            }
        }
        return particles;
    }

    private boolean overlaps(final double x, final double y, final double radius,
                             final double[] xs, final double[] ys, final double[] rs) {
        final int cx = coordToCell(x);
        final int cy = coordToCell(y);
        for (int dy = -1; dy <= 1; dy++) {
            for (int dx = -1; dx <= 1; dx++) {
                int nx = cx + dx;
                int ny = cy + dy;
                if (periodic) {
                    nx = Math.floorMod(nx, cells);
                    ny = Math.floorMod(ny, cells);
                } else if (nx < 0 || nx >= cells || ny < 0 || ny >= cells) {
                    continue;
                }
                for (final int other : grid.get(ny * cells + nx)) {
                    double ddx = x - xs[other];
                    double ddy = y - ys[other];
                    if (periodic) {
                        ddx -= l * Math.round(ddx / l);
                        ddy -= l * Math.round(ddy / l);
                    }
                    final double minDistance = radius + rs[other];
                    if (ddx * ddx + ddy * ddy < minDistance * minDistance) {
                        return true;
                    }
                }
            }
        }
        return false;
    }

    private int cellOf(final double x, final double y) {
        return coordToCell(y) * cells + coordToCell(x);
    }

    private int coordToCell(final double coord) {
        final int index = (int) Math.floor(coord / cellSize);
        return Math.min(Math.max(index, 0), cells - 1);
    }

    /**
     * Cota superior grosera de partículas para una geometría, útil para elegir el "N máximo" de los
     * estudios: fracción de empaquetamiento del 50% con el radio medio.
     */
    public static int estimateMaxParticles(final double l, final double rMin, final double rMax) {
        final double meanRadius = (rMin + rMax) / 2;
        return (int) Math.floor(0.5 * l * l / (Math.PI * meanRadius * meanRadius));
    }
}
