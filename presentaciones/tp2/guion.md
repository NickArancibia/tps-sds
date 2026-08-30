# Guión de la presentación — TP2

Documento interno, **no se entrega**. Contiene lo que se dice en voz alta sobre
cada diapositiva. Las diapositivas llevan solo figura + parámetros fijos y
variables al costado (GuiaPresentaciones §1.6 y §1.7): la interpretación es
oral, no escrita.

Numeración según el PDF compilado.

---

## Resultados — Vicsek

### Vicsek: animación

Dos casos extremos a la misma densidad, ρ = 2. A la izquierda, ruido bajo: las
flechas apuntan casi todas para el mismo lado. A la derecha, ruido alto: cada
partícula apunta a cualquier parte.

Los valores de v_a que están al costado son de ese fotograma solo, no promedios
del estacionario. Si alguien los compara con las curvas de más adelante, van a
dar distinto, y está bien: con N = 200 un instante fluctúa bastante alrededor de
la media.

### Vicsek: v_a(t)

Menos ruido ordena antes y satura más alto. Las tres curvas llegan a un
estacionario; el trazo punteado marca dónde lo ubicamos.

De acá sale el escalar que usamos en todas las curvas siguientes: promedio
temporal sobre la última mitad de la corrida.

### Vicsek: v_a vs η

Es la curva central del trabajo. Va de orden total sin ruido a desorden con
ruido alto.

Lo que hay que hacer notar: subir la densidad corre la caída hacia ruidos
mayores. Con más vecinos dentro del radio, el promedio de direcciones filtra más
ruido, así que hace falta más η para romper el orden.

### Vicsek: S(t)

S ≈ 1 para los tres ruidos. Con ρ ≥ 2 y r_c = 1 el grafo de vecinos percola: el
cluster más grande se come casi todas las partículas, independientemente del
ruido.

Aclarar que el eje vertical está acotado a los datos — arranca en 0,86, no en 0.
En escala completa sería una recta plana.

### Vicsek: S vs η

Para las tres densidades exigidas, S ≈ 1 con todo ruido. Por eso agregamos
densidades más bajas: ahí S sí cae con η, y se aplana a partir de η ≈ 4 rad.

Si preguntan por qué esas densidades: son las que dan menos de un vecino
promedio dentro de r_c, o sea el régimen donde el sistema deja de percolar.

### Vicsek: v_a vs S

Los dos paneles tienen distinta escala en S, por eso están separados.

A la izquierda (densidades bajas) v_a crece con S: el orden necesita
conectividad, si el sistema está fragmentado no puede alinearse globalmente.

A la derecha (densidades exigidas) S no se mueve mientras v_a recorre todo su
rango. Son observables independientes en ese régimen.

---

## Resultados — Votante

### Votante: animación

Misma densidad, mismos ruidos, mismo instante y misma representación que Vicsek,
para que la comparación sea directa.

El punto: a η = 0,5 rad Vicsek está en 0,98 y el votante ya recorre todo el
círculo. Con el mismo ruido, una regla mantiene el orden y la otra no.

### Votante: v_a(t)

Sin ruido satura en 1. Con 0,5 rad fluctúa sin llegar a estacionarse — por eso
esa curva no lleva trazo punteado. Con 2 rad queda cerca de cero.

### Votante: v_a vs η

Todas las densidades pierden el orden dentro del primer radián.

La diferencia clave con Vicsek: acá subir ρ **no** corre la caída. Copiar el
ángulo de un solo vecino no promedia nada, así que tener más vecinos no ayuda.

### Vicsek vs votante: v_a vs η

Ambos alcanzan v_a = 1 sin ruido, pero el votante pierde el orden con ruidos
mucho menores.

La explicación es la regla: promediar sobre los vecinos filtra el ruido, copiar
a uno solo lo propaga. Es el resultado central de la comparación.

Misma forma en ρ = 2 y 8; mostramos ρ = 4 como caso típico.

### Votante: S(t)

Mismo comportamiento que Vicsek: S ≈ 1 para los tres ruidos. Eje acotado a los
datos, igual que antes.

### Votante: S vs η

Igual que en Vicsek: ρ ≥ 2 percola, y las densidades bajas caen con η.

Conclusión: la conectividad depende de la densidad, no de la regla de
alineación.

### Vicsek vs votante: S vs η

Ojo con el eje, está acotado a los datos: los mínimos son 0,9982 y 0,9991, o sea
que toda la variación entra en menos del 0,2 %.

Dicho de otro modo: la regla de alineación separa v_a en un factor tres, pero no
deja huella en la conectividad.

### Vicsek vs votante: v_a vs S

Cada panel junta las tres densidades de su grupo.

A la izquierda las dos nubes se solapan: con menos de un vecino por partícula,
promediar y copiar dejan de distinguirse. A la derecha ambos modelos se apilan
en S ≈ 1.

En ningún régimen S separa una regla de la otra. El observable que discrimina es
v_a.

### Tiempos del CIM

Vicsek y votante dan tiempos casi idénticos: el CIM no depende de la regla de
alineación, solo de la geometría de vecinos.

El TP2 queda por encima del microbenchmark del TP1 porque acá el CIM se mide
dentro de la simulación, con el resto del paso alrededor.
