# Guión de la presentación — TP2

Documento interno, **no se entrega**. Contiene lo que se dice en voz alta sobre
cada diapositiva. Las diapositivas llevan solo figura + parámetros fijos y
variables al costado (GuiaPresentaciones §1.6 y §1.7): la interpretación es
oral, no escrita.

Numeración según el PDF compilado.

---

## Simulaciones

### Observables

Las dos fórmulas son sobre el estado en un paso: v_a normaliza la suma vectorial
de velocidades por N·v, así que vale 1 si todas apuntan igual y 0 si se cancelan.
S es la fracción de partículas que entran en la componente conexa más grande.

El escalar de cada corrida es el promedio temporal sobre la segunda mitad. La
elección no es arbitraria: elegimos T mirando las evoluciones temporales para
que el transitorio termine mucho antes de T/2, y por eso las densidades bajas
corren 5000 pasos en vez de 2000. Lo verificamos promediando en cambio el último
10 % de cada corrida: la diferencia es de 0,14 desvíos en mediana, o sea que
dónde se corta la ventana no cambia el resultado.

Sobre la barra de error, por si preguntan: es el desvío muestral de 50 números
independientes, uno por repetición, no un promedio de desvíos ni el desvío de
los pasos temporales apilados. Los pasos dentro de una corrida están
autocorrelacionados (tau ≈ 40–90 pasos), así que tratarlos como independientes
subestimaría el error entre 8 y 14 veces. Cada repetición ya es un promedio
temporal, y el error que ese promedio arrastra por ser una ventana finita
aparece solo como dispersión extra entre repeticiones: no hay nada que propagar.

---

## Resultados — Vicsek

### Vicsek: animación

Dos casos extremos a la misma densidad, ρ = 2. A la izquierda, ruido bajo: las
flechas apuntan casi todas para el mismo lado. A la derecha, ruido alto: cada
partícula apunta a cualquier parte.

Aclarar en voz alta cómo leer la figura: cada flecha es el vector velocidad de
una partícula y el color codifica su ángulo. Con ruido bajo el campo es casi de
un solo color; con ruido alto están todos los colores mezclados.

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

Misma lectura que antes: flecha = velocidad, color = ángulo.

El punto: con el mismo η = 0,5 Vicsek queda casi monocromático y el votante ya
recorre todo el círculo de colores. Con el mismo ruido, una regla mantiene el
orden y la otra no.

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

Mostramos una sola densidad, ρ = 1/π, por el mismo criterio que en las
comparaciones anteriores: es la que recorre el rango más amplio de S. Con ρ ≥ 2
los dos modelos quedan clavados en S > 0,99 y el gráfico no dice nada; el
detalle por densidad está en las dos figuras por modelo.

Las dos curvas se superponen dentro de las barras de error. O sea: la regla de
alineación no cambia la relación entre polarización y conectividad. Recorren el
mismo camino, lo que cambia es a qué η llega cada uno a cada punto del camino.

En ningún régimen S separa una regla de la otra. El observable que discrimina es
v_a.

### Tiempos del CIM

Es el mismo código de CIM y en los dos casos el cronómetro envuelve únicamente
la llamada a findNeighbors. Lo que cambia son las condiciones de medición, y por
eso el TP2 queda por encima del microbenchmark del TP1. Tres causas, medidas:

1. **La configuración no es uniforme.** El bench del TP1 mide sobre partículas
   distribuidas al azar; en el TP2 Vicsek forma bandadas, las celdas quedan
   desbalanceadas y el CIM hace más comparaciones. Midiendo la misma simulación
   con η = 6,28 (desordenada, casi uniforme) contra η = 0,5 (v_a = 0,98): 0,101
   contra 0,148 ms a N = 200, o sea 1,5 veces solo por la distribución
   espacial. Es también la razón por la que Vicsek queda apenas arriba del
   votante en la figura: con η = 0,5 Vicsek se agrupa y el votante no.
2. **JIT sin calentar.** El bench del TP1 calienta la JVM al menos 200 ms antes
   de cronometrar; el TP2 mide dentro de una corrida de 1000 pasos, o sea que el
   método se ejecuta 1000 veces en total y nunca llega al umbral de compilación
   C2. Extendiendo la corrida a 20000 pasos el tiempo por llamada baja de 0,184
   a 0,148 ms: otro factor 1,24.
3. **Caché fría y GC.** Entre dos llamadas al CIM corre el resto del paso (los
   senos y cosenos de las N partículas, el recorrido de clusters, la escritura
   de observables), que desaloja de caché los datos del CIM; y las listas de
   vecinos se asignan con objetos vivos alrededor, así que alguna pausa de GC
   cae adentro de la ventana cronometrada. Es lo que queda: 1,4 veces a
   N = 200.

El cierre: **el efecto se desvanece con N**. Corriendo las dos series en la misma
máquina, a N = 800 y con configuración uniforme el TP2 da 1,29 ms contra 1,32 ms
del TP1: idénticos. El sobrecosto por llamada es aproximadamente constante, así
que pesa cuando la llamada es corta (N = 200) y desaparece cuando es larga.
