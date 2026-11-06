# Texto oculto en Teorica_5.pdf

## Página 3 (736 caracteres recortados)

```text
flujo en masa
flujo restringido
zona estancas
Figura I.1: Tipos de flujos gravitatorios en silos (Schulze, 1998).
Los tipos de flujo que se encuentran durante el vaciado dependerán de la
geometría del silo y de las propiedades mecánicas de las paredes y del material ensilado.
Los diferentes autores coinciden en distinguir cinco zonas distintas dentro del flujo
esquematizado en la figura I.2.
Figura I.2: Zonas dentro de un flujos gravitatorio en silos
Estas cinco zonas son:
-La zona de flujo en masa situada en la parte superior del silo donde las partículas
descienden en bloque. Los esfuerzos de corte se encuentran cerca de las paredes y a la
entrada de la zona de transición (Khati y Shahrour 1997, Yacoub y Roth 1997). El
[fórmula] a) b) c)
```

## Página 4 (452 caracteres recortados)

```text
[fórmula] 8 rr zz K σ σ =
(I.4)
donde K es conocida como la constante de Janssen. Substituyendo las ecs. (I.3) y (I.4)
en la ec. (I.2), se obtiene que
[fórmula] 4 p zz zz m K d g dz D µ σ σ ρ + =
(I.5)
Teniendo en cuenta que a z=0 la tensión es nula (superficie libre), la solución
para esta ecuación diferencial ordinaria de primer orden es
[fórmula] 4 m zz p g D K ρ σ µ =
(I.6)
Lo cual evidencia que la componente del tensor σzz tiende a un valor asintótico a
```

## Página 5 (1379 caracteres recortados)

```text
[fórmula] ( )
dN t
[fórmula] Q dt =
(I.14)
A diferencia de lo que ocurre en el caso de los líquidos, en sistemas granulares el
caudal es independiente de la altura de la columna. Esto ocurre cuando la presión en la
boca del silo ha alcanzado su valor asintótico, según se explicó en I.1.2. Otra posible
causa puede ser que las paredes inclinadas de la zona cónica del silo soporten el peso
del material a través de arcos dinámicos que transmiten las presiones a dichas paredes,
manteniendo la presión en el orificio de salida constante.
La ec. (I.14) define el caudal en la zona donde Q es constante.
Se ha verificado experimentalmente (Beverloo et al., 1961), que el caudal en un
silo 3-D es proporcional a
(I.15)
donde np es el nro. partículas por unidad de volumen, d el diámetro del orificio de salida
del silo, r el radio medio de las partículas y c un factor adimensional que permite
considerar que una fracción del orificio de salida no es utilizada, corrigiendo al diámetro
real del mismo por uno efectivo (d-cr). En el caso 2-D el exponente 2.5 debe ser
reemplazado por 1.5. Cabe notar que la funcionalidad de la expresión de Beverloo surge
simplemente de consideraciones dimensionales del sistema.
I. 1. 5 Simulaciones DEM
La dinámica de un medio granular está dominada por el tipo de colisiones y por
el tiempo que las partículas están en contacto. Si la densidad de partículas es baja, los
```

## Página 8 (1356 caracteres recortados)

```text
vecinas en contacto
[fórmula] i i ij j = ∑
donde m es la masa, r&& el vector aceleración, F la fuerza y los subíndices i y j indican la
identidad de las partículas. El término de la fuerza puede depender de las posiciones y
velocidades de cada partícula del sistema. Su forma particular se describirá en los
parágrafos siguientes, sin embargo adelantamos que esta fuerza actúa solamente sobre
vecinos en contacto. Además de la ec. (I.16), en el caso general, la formulación
considera también la ecuación del torque, como se verá en I.1.5.2.
Las partículas son consideradas blandas, deformándose durante la interacción
con otras partículas o las paredes del contenedor. La forma de considerar esta
deformación, para discos bidimensionales, es evaluar el solapamiento entre partículas en
contacto definido como
[fórmula] ( )
( )t
[fórmula] r R R t ij j i ij − + = ξ
(I.17)
donde Ri y Rj son los radios de cada partícula y rij la distancia entre sus centros, como se
muestra en la figura I.5.
Figura I.5: Definiciones de variables geométricas entre dos partículas en contacto
La evolución del sistema de N partículas resultará de integrar numéricamente el
sistema de ecuaciones expresado en (I.16). Para hacer esto existen diversos métodos
como por ejemplo diferencias finitas, el algoritmo de Verlet o el corrector predictor de
Gear de distintos ordenes (Allen y Tildesley, 1982).
```

## Página 9 (1356 caracteres recortados)

```text
vecinas en contacto
[fórmula] i i ij j = ∑
donde m es la masa, r&& el vector aceleración, F la fuerza y los subíndices i y j indican la
identidad de las partículas. El término de la fuerza puede depender de las posiciones y
velocidades de cada partícula del sistema. Su forma particular se describirá en los
parágrafos siguientes, sin embargo adelantamos que esta fuerza actúa solamente sobre
vecinos en contacto. Además de la ec. (I.16), en el caso general, la formulación
considera también la ecuación del torque, como se verá en I.1.5.2.
Las partículas son consideradas blandas, deformándose durante la interacción
con otras partículas o las paredes del contenedor. La forma de considerar esta
deformación, para discos bidimensionales, es evaluar el solapamiento entre partículas en
contacto definido como
[fórmula] ( )
( )t
[fórmula] r R R t ij j i ij − + = ξ
(I.17)
donde Ri y Rj son los radios de cada partícula y rij la distancia entre sus centros, como se
muestra en la figura I.5.
Figura I.5: Definiciones de variables geométricas entre dos partículas en contacto
La evolución del sistema de N partículas resultará de integrar numéricamente el
sistema de ecuaciones expresado en (I.16). Para hacer esto existen diversos métodos
como por ejemplo diferencias finitas, el algoritmo de Verlet o el corrector predictor de
Gear de distintos ordenes (Allen y Tildesley, 1982).
```

## Página 10 (4105 caracteres recortados)

```text
El método consiste en integrar numéricamente las ecuaciones de movimiento
para un sistema de N partículas discretizando al tiempo en pasos fijos ∆t,
i  =1,...,N
(I.16)
donde m es la masa, r&& el vector aceleración, F la fuerza y los subíndices i y j indican la
identidad de las partículas. El término de la fuerza puede depender de las posiciones y
velocidades de cada partícula del sistema. Su forma particular se describirá en los
parágrafos siguientes, sin embargo adelantamos que esta fuerza actúa solamente sobre
vecinos en contacto. Además de la ec. (I.16), en el caso general, la formulación
considera también la ecuación del torque, como se verá en I.1.5.2.
Las partículas son consideradas blandas, deformándose durante la interacción
con otras partículas o las paredes del contenedor. La forma de considerar esta
deformación, para discos bidimensionales, es evaluar el solapamiento entre partículas en
contacto definido como
[fórmula] ( )
( )t
[fórmula] r R R t ij j i ij − + = ξ
(I.17)
donde R y R son los radios de cada partícula y r la distancia entre sus centros, como se
El método consiste en integrar numéricamente las ecuaciones de movimiento
para un sistema de N partículas discretizando al tiempo en pasos fijos ∆t,
vecinas en contacto
[fórmula] i i ij j m = = ∑ r F &&
(I.16)
donde m es la masa, r&& el vector aceleración, F la fuerza y los subíndices i y j indican la
identidad de las partículas. El término de la fuerza puede depender de las posiciones y
velocidades de cada partícula del sistema. Su forma particular se describirá en los
parágrafos siguientes, sin embargo adelantamos que esta fuerza actúa solamente sobre
vecinos en contacto. Además de la ec. (I.16), en el caso general, la formulación
considera también la ecuación del torque, como se verá en I.1.5.2.
Las partículas son consideradas blandas, deformándose durante la interacción
con otras partículas o las paredes del contenedor. La forma de considerar esta
deformación, para discos bidimensionales, es evaluar el solapamiento entre partículas en
contacto definido como
[fórmula] ( )
( )t
[fórmula] r R R t ij j i ij − + = ξ
(I.17)
a movido lo suficiente como para salirse de su celda, se vuelve a testear por nuevos
bles vecinos y por nueva ubicación en una nueva celda. De esta forma, la detección
contactos en cada paso temporal se realiza entre menos partículas. Además, los
bles nuevos vecinos están limitados a las celdas vecinas, de modo que no se
ulan las distancias entre todas las partículas cada vez.
Ahora se presenta la formulación del problema incluyendo, además de las
ciones y velocidades de traslación, las rotaciones y velocidades angulares de cada
cula.
A la ec.(I.16) se la debe acompañar con su equivalente para los torques (I.25)
[fórmula] 1 N i i ij j m = =∑ r F &&
(I.16)
(I.25)
de Ii es el momento de inercia, θ&& i es la aceleración angular y Mij es el torque
cado sobre la partícula i debido a la j.
.2.1 Ciclo de Cálculo
El esquema de discretización, en este caso, es como sigue: Para cada partícula se
ideran las aceleraciones (traslacional y angular) constantes en el intervalo [-∆t/2,
Las expresiones para las fuerzas normal y tangencial, sin tener
amortiguamiento, son
[fórmula] N ˆ n
nk ξ
[fórmula] = − F ( ) N T T T ˆ sgn t min ˆ t rel c k µ ξ −  =  −  F r F &
donde
[fórmula] rel
cr& es la velocidad relativa de las superficies de las partículas en
contacto, la cual tiene en cuenta las velocidades de los centros de
velocidades angulares. ξT es el desplazamiento del punto de contacto en
tangencial durante el tiempo que dura el contacto y se lo define como
[fórmula] T ( ) rel c t t t ξ = ∆ ∑ r&
La ec. (I.33), a diferencia de la ec. (I.23), muestra una interacción
dirección tangencial al contacto. Esta interacción es válida mientras la m
misma no supere a la fuerza de rozamiento coulombiano. Si alcanzara ese
de allí vale la fuerza de rozamiento, permitiendo un deslizamiento fricciona
La expresión para el torque (M) resulta
donde R es el vector que va desde el centro de la partícula al punto de
figura I.5) y F la fuerza total (F=FN+FT).
Tanto la fuerza total como el torque sufren un amortiguamient
regulado por el parámetro adimensional a
```

## Página 14 (1178 caracteres recortados)

```text
Existen varias posibles formas de elegir la interacción entre partículas. En este
código se usó una interacción elástica amortiguada para la componente normal de la
fuerza (FN) y una de rozamiento coulombiano para la componente tangencial de la
misma (FT), definidas para ξ > 0 (cuando hay solapamiento entre partículas) de la
siguiente manera
[fórmula] N ˆ n
nk ξ
[fórmula] γξ   = − −   F &
(I.22)
[fórmula] ( ) T N ˆ sgn t rel µ = − F F r&
(I.23)
donde
[fórmula] rel . r
es la velocidad relativa entre los centros de masa de las partículas, kn y γ son
las constantes elástica y de amortiguamiento, µ  es el coeficiente de rozamiento, nˆ es el
versor en la dirección normal y tˆ de la tangencial. Estas interacciones están
esquematizadas en las figuras I.6 (a) y (b).
Figura I.6: Modelos de interacciones entre partículas
Si bien, en general, se consideran otras expresiones para la fuerza tangencial,
agregando interacciones elásticas (Wolf, 1996; PFC2D) o considerando distinciones
entre rozamiento estático y dinámico (Herrmann, 1993), hay varias razones para elegir
la expresión dada en las ecs. (I.22) y (I.23):
a) Tanto esta como las otras expresiones son empíricas y sin sustento teórico,
```

## Página 15 (2993 caracteres recortados)

Fuente LaTeX de fórmulas (texto invisible):

- `\bold F_{\text{T}} = - \mu ~|\bold F_{N}|~ \mathrm{sgn} (\dot{\bold r}_{rel}~ . ~\hat{\mathrm t}~)~ \hat{ \mathrm t}`
- `- \mu ~|\bold F_{N}|~ \mathrm{sgn} (\dot{\bold r}_{rel}~ . ~\hat{\mathrm t}~)~ \hat{ \mathrm t}`

```text
. En las simulaciones hay que detectar cuales son las partículas que se
s conocida como "detección de contactos". En el presente código la
ctos se realiza calculando las distancias ξij entre todas todos los pares
y luego se eligen los pares que tienen ξij positivo. Si ξ < 0 no hay
n este caso, las fuerzas de interacción son nulas.
rias posibles formas de elegir la interacción entre partículas. En este
a interacción elástica amortiguada para la componente normal de la
a de rozamiento coulombiano para la componente tangencial de la
idas para ξ > 0 (cuando hay solapamiento entre partículas) de la
(I.22)
[fórmula] ( ) T N ˆ sgn t rel µ = − F F r&
(I.23)
locidad relativa entre los centros de masa de las partículas, kn y γ son
tica y de amortiguamiento, µ  es el coeficiente de rozamiento, nˆ es el
ección normal y tˆ de la tangencial. Estas interacciones están
las figuras I.6 (a) y (b).
valores de las fuerzas y torques en (t+∆t/2) se obtienen de las leyes de inte
partículas.
I.1.5.2.2 Interacciones Partícula – Partícula
Las expresiones para las fuerzas normal y tangencial, sin tener
amortiguamiento, son
[fórmula] N ˆ n
nk ξ
[fórmula] = − F
donde
[fórmula] rel
cr& es la velocidad relativa de las superficies de las partículas en
contacto, la cual tiene en cuenta las velocidades de los centros de
velocidades angulares. ξT es el desplazamiento del punto de contacto en
tangencial durante el tiempo que dura el contacto y se lo define como
[fórmula] T ( ) rel c t t t ξ = ∆ ∑ r&
La ec. (I.33), a diferencia de la ec. (I.23), muestra una interacción
dirección tangencial al contacto. Esta interacción es válida mientras la m
misma no supere a la fuerza de rozamiento coulombiano. Si alcanzara ese v
[fórmula] N ˆ n
nk ξ
[fórmula] = − F ( N T T T sgn min ˆ t k µ ξ −  =  −  F r F &
donde
[fórmula] rel
cr& es la velocidad relativa de las super
contacto, la cual tiene en cuenta las veloci
velocidades angulares. ξT es el desplazamiento
tangencial durante el tiempo que dura el contacto
La ec. (I.33), a diferencia de la ec. (I.23)
dirección tangencial al contacto. Esta interacció
misma no supere a la fuerza de rozamiento coulo
de allí vale la fuerza de rozamiento, permitiendo
La expresión para el torque (M) resulta
[fórmula] = × M R F
donde R es el vector que va desde el centro de
figura I.5) y F la fuerza total (F=FN+FT).
Tanto la fuerza total como el torque s
regulado por el parámetro adimensional a
[fórmula] / 2 t t t t t t θ θ θ +∆ +∆ = + ∆ &
(I.31)
el ciclo de cálculo es el siguiente: Dados los valores de las
ante (t-∆t/2) y las posiciones, fuerzas y torques en el instante (t), se
y (I.29) para obtener las velocidades en el instante (t+∆t/2). Los
y torques en (t+∆t/2) se obtienen de las leyes de interacción entre
es Partícula – Partícula
nes para las fuerzas normal y tangencial, sin tener en cuenta el
[fórmula] n
(I.32)
[fórmula] ( ) N T T T ˆ sgn t min ˆ t rel c k µ ξ −  =  −  F r F &
(I.33)
ocidad relativa de las superficies de las partículas en el punto de
ene en cuenta las velocidades de los centros de masa y las
```

## Página 19 (994 caracteres recortados)

```text
partículas se hace un desarrollo de Taylor de orden dos para las posiciones en el instante
t +∆t, en función de la las variables dinámicas en el paso anterior t
[fórmula] ( ) ( ) ( ) ( ) 2 1 2 i i i i t t t t t t t + ∆ = + ∆+ ∆ r r r r & &&
(I.18)
[fórmula] ( ) ( ) ( ) i i i t t t t t + ∆ = + ∆ r r r & & &&
(I.19)
[fórmula] ( ) ( ) 1 1 N i ij j i t t m = = ∑ r F &&
(I.20)
donde r y r& son los vectores posición y velocidad, respectivamente.
Para la elección del paso temporal se utilizó el criterio propuesto por Thompson
y Grest (1991).
(I.21)
donde kn es la constante de restitución elástica normal (ver Interacciones partícula –
partícula).
El paso temporal debe ser mucho menor que el tiempo que permanecen en
contacto dos partículas (tiempo de choque). Si el paso temporal fuera muy alto, el
método numérico generaría fuerzas enormes y el sistema explotaría.
Para simular interacciones entre partículas más rígidas (de mayor constante
elástica k) se requieren pasos ∆t menores y, por ende, es más costoso
```

## Página 24 (1236 caracteres recortados)

```text
Marroqu´ın
separately. Both approaches are also extremely
extend to 3D, because the calculation of
p between two polyhedra is computationally
nsive. This is the main reason why most of
ercial codes for particulate systems are still
imulations with spheres, or clumps of spheres
g complex-shaped objects [9].
tter I present a solution to this problem in 2D,
oncept of spheropolygons. They are generated
Minkowski sum of a polygon with a disk, which
more than the object resulting from sweeping
nd a polygon. This simple concept can be used
e very complex shapes, including non-convex
hout the need to decompose them into spherical
parts. The interaction between spheropoly-
odeled by considering all possible vertex-edge
s. The result is a simple and elegant model,
erent interaction laws can be implemented
wardly. I anticipate that this model will be the
oint to the development of a new generation
Fig. 1: (a) Minkowski cow obtained by sweeping a disk around
a polygon of 62 edges. The disk has radius 10 cm and the length
of the polygon is 3 m. (b) The cow as represented by a clump
of disks using 726 disks.
sum approach is that it removes the unwanted roughness
of the surface in the clump-of-disks method.
The point-inside-spheropolygon test combined with a
```

## Página 25 (1335 caracteres recortados)

```text
ite stiﬀness is
s are not truly
s method [10].
customizable,
points P and
sum is given
operation
[fórmula] is
g of one set
changing the
m of a polygon
heropolygons.
e the sphero-
[fórmula] the
sphero-
eropolyhedron
in simulations
Minkowski cow
m is compared
rt (b) of ﬁg. 1.
ent a complex
ower than the
lumpy object.
inner disks of
mpy cow, the
between the polygons. Let us take two spheropolygons SPi
and SPj with their respective polygons Pi and Pj and the
radii of the disks ri and rj. Each polygon is deﬁned by the
set of vertices {Vi} and edges {Ei}. The overlapping length
between each pair of vertex-edge (V, E) is deﬁned as
δ(V, E) = ⟨ri + rj −d(V, E)⟩,
[fórmula] (1)
where d(X, E) =∥⃗Y −⃗X ∥is the Euclidean distance from
the vertex V to the segment E. Here⃗X is the position of
the vertex V and⃗Y is its closest point on the edge E. The
ramp function ⟨x⟩returns x if x > 0 and zero otherwise.
The force⃗Fij acting on particle i by the particle j is
deﬁned by
[fórmula] (2)
where⃗F(V, E) represents the force between the vertex
V and the edge E. If the vertex-edge overlapping length
is zero, we take⃗F(V, E) = 0. Diﬀerent vertex-edge forces
can be included in the model: linear dashpots, non-linear
Hertzian laws, Lennard-Jones forces, dissipative viscous
forces, sliding friction, etc.
The torque on particle i given by j is
τij =
[fórmula] !
(⃗R(Vi, Ej) −⃗ri) ×⃗F(Vi, Ej)
```

## Página 26 (1235 caracteres recortados)

```text
[fórmula] aws
eral
ero-
[fórmula] ody and
s is
ruly
10].
ble,
[fórmula] and ven is set the gon
ons.
ero-
ero-
[fórmula] ron ons cow red
of inertia. This numerical integration, whose details are
explained elsewhere [14], does not represent much compu-
tational eﬀort, because the mass properties are calculated
only once and they are assumed to be constant throughout
the simulation.
Interaction force.
To solve the interaction between
spheropolygons, we consider all vertex-edge distances
between the polygons. Let us take two spheropolygons SPi
and SPj with their respective polygons Pi and Pj and the
radii of the disks ri and rj. Each polygon is deﬁned by the
set of vertices {Vi} and edges {Ei}. The overlapping length
between each pair of vertex-edge (V, E) is deﬁned as
[fórmula] (1)
where d(X, E) =∥⃗Y −⃗X ∥is the Euclidean distance from
the vertex V to the segment E. Here⃗X is the position of
the vertex V and⃗Y is its closest point on the edge E. The
ramp function ⟨x⟩returns x if x > 0 and zero otherwise.
The force⃗Fij acting on particle i by the particle j is
deﬁned by
Fij = −⃗Fji =
[fórmula] !
ViEj
F(Vi, Ej) +
[fórmula] !
VjEi
F(Vj, Ei),
[fórmula] (2)
where⃗F(V, E) represents the force between the vertex
V and the edge E. If the vertex-edge overlapping length
```

## Página 27 (1225 caracteres recortados)

```text
a of the
with this
or along
y of the
method
es, each
contact
me very
mber of
ions, we
likely to
eighbor
h are in
d as the
en them
nce [14].
t list is
s whose
d when
particles
]. A link
n of the
iﬁcation
calculate contact forces between neighbor particles;
apply contact forces to the particles;
apply gravity forces to the particles;
correct positions and its derivatives using forces and
torques.
need to be calculated during the time integration, which
is, along with the neighborhood identiﬁcation, one of the
main reasons of the eﬃciency of the code.
Benchmark tests. – Simulations will be perform
using Minkowski cows interacting via repulsive, frictional
forces
[fórmula] (6)
where⃗N = (⃗Y −⃗X)/ ∥⃗Y −⃗X ∥is the normal unit vector.
The tangential vector⃗T is taken perpendicular to⃗n.
δn is the overlapping length deﬁned in eq. (1). The
elastic displacement δt accounts frictional forces, and it
must satisfy the sliding condition |Ft| < µFn, where µ
is the coeﬃcient of friction [16]. The parameters of the
simulations are the normal stiﬀness k = 107 N/m, the
tangential stiﬀness kt = 0.1kn, friction coeﬃcient µ = 0.5
gravity
g = 10 m/s2,
density
σ = 1 kg/m2,
time
step
∆t = 10−5 s and the Verlet distance α = 1 m.
We perform three series of simulations. The ﬁrst one
```

## Página 28 (746 caracteres recortados)

```text
[fórmula] et he on s. o- o- on ns w ed 1. ex he t. of he ry of ki
∥ − ∥
the vertex V to the segment E. Here⃗X is the position of
the vertex V and⃗Y is its closest point on the edge E. The
ramp function ⟨x⟩returns x if x > 0 and zero otherwise.
The force⃗Fij acting on particle i by the particle j is
deﬁned by
Fij = −⃗Fji =
[fórmula] !
ViEj
F(Vi, Ej) +
[fórmula] !
VjEi
F(Vj, Ei),
[fórmula] (2)
where⃗F(V, E) represents the force between the vertex
V and the edge E. If the vertex-edge overlapping length
is zero, we take⃗F(V, E) = 0. Diﬀerent vertex-edge forces
can be included in the model: linear dashpots, non-linear
Hertzian laws, Lennard-Jones forces, dissipative viscous
forces, sliding friction, etc.
The torque on particle i given by j is
[fórmula] (3)
4001-p2
```

## Página 29 (1009 caracteres recortados)

```text
where⃗ri is the center of mass of particle i, and⃗R is the
point of application of the force, which is taken as the
middle point of the overlap region between the vertex and
the edge:
R(V, E) =⃗X +
[fórmula] !
ri + 1
2δ(V, E)
[fórmula] "
X −⃗Y
∥⃗Y −⃗X ∥
[fórmula] , (4)
The evolution of⃗ri and the orientation ϕi of the particle
is governed by the equations of motion:
[fórmula] (5)
Here mi and Ii are the mass and moment of inertia of the
particle. The sum is over all particles interacting with this
particle; g is the gravity; and ˆy is the unit vector along
the vertical direction.
Eﬃcient calculation of forces.
The eﬃciency of the
dynamics simulation is mainly determined by the method
of contact detection. In a system of N particles, each
one with M edges, the number of calculations for contact
Algorithm 1
scheme.
Input: state
Output: sta
predict posit
using a Tayl
update verti
if neighbor u
calculate
update n
update c
[fórmula] end
calculate con
apply contac
apply gravit
correct posit
torques.
need to be cal
is, along with
main reasons o
```

## Página 30 (996 caracteres recortados)

```text
F. Alonso-Marroqu´ın
Fig. 6: Simulations of granular ﬂow using disks (left) and
Minkowski cows (right). Two diﬀerent apertures are chosen:
20 m (top) and 30 m (bottom). The snapshots are taken eight
seconds after discharge.
respect to other existing particle-based models: i) The
as in avalanches (snow, d
astrophysics as the dyna
of planets or the icy part
This work is the ﬁrst ste
of conservative and dissipa
plenty of potential applicat
This work is supported
Council (project number D
REFERENCES
[1] Carlson H. and Mcca
(2000) 213.
[2] Pelzl G., Diele S. an
11 (1999) 707.
[3] Alonso-Marroquin F
Vardoulakis I., Phys.
[4] Mirtich B., ACM Tran
[5] Ruspini D. and Khatib
[6] Baraff D., Algorithmic
[7] Hasegawa S. and Sat
23 (2004) 529.
[8] Poeschel
[fórmula] T. and
Granular Dynamics (Sp
[9] Lu M. and McDowell
[fórmula] 69.
[10] Moreau J., Unilateral
freedom dynamics, in In
cal Sciences, Courses a
Vienna) 1988.
[11] Pournin L., Weber
J.-A., Ramaioli M. a
Matter, 7 (2005) 119.
[12] Pournin L. and Lieblin
element method to tridi
```
