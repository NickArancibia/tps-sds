# Texto oculto en Teorica_7.pdf

## Página 5 (8 caracteres recortados)

Fuente LaTeX de fórmulas (texto invisible):

- `m_i ~ \bold{a}_i ~ = ~ \bold{F}_g + \bold{F}_e`

```text
latexit>
```

## Página 6 (647 caracteres recortados)

```text
t al.
simulation the pedestrian Pi is trying to reach its desired
hus, a goal force Fg is applied that attracts the pedestrian
prefers to move toward its destination with a certain speed
each this speed gradually within a certain time τ. Along
mption, the goal force Fg can be deﬁned as:
[fórmula] (1)
∥. Note that Fg is similar to the force described in Equa-
s social force model [7].
ward its goal, it also has to avoid collisions with the envi-
ing walls). Let W denote the set of walls that are present
onment. Then, a repulsive force Fw is exerted from each
the pedestrian. This force can be deﬁned as:
[fórmula]    n
ds + ri −diw
[fórmula] ,
if d −r < d
```

## Página 7 (2207 caracteres recortados)

```text
the wall, diw deﬁnes the shortest distance between
denotes the safe distance that the pedestrian prefers
ngs.
ps a certain psychophysical distance ρi from other
feel comfortable. This distance deﬁnes the so-called
edestrian. For eﬃciency reasons, we model this space
tered at the current position of the pedestrian and
n all of our simulations, this led to realistic behaviour
n elliptical personal space was not necessary.
eives the environment to detect imminent and future
destrians. A collision at some time tc ≥0 occurs when
invades into the personal space of Pi, that is:
[fórmula] (3)
denotes the distance between the pedestrians’ centers.
pation time tα, the pedestrian Pi resolves potential
me in advance by adjusting its trajectory. As a result,
ard its goal, evading other pedestrians with minimal
behaviour, an evasive force Fe is applied on Pi. Note
me tα can vary between pedestrians.
[fórmula] 
where the constant κ indicates the steepness of the repulsive potential, nw
is the normal vector of the wall, diw deﬁnes the shortest distance between
Pi and the wall and ds denotes the safe distance that the pedestrian prefers
to keep from the buildings.
The pedestrian Pi keeps a certain psychophysical distance ρi from other
pedestrians in order to feel comfortable. This distance deﬁnes the so-called
personal space of the pedestrian. For eﬃciency reasons, we model this space
as a disc B(xi, ρi) centered at the current position of the pedestrian and
having radius ρi > ri. In all of our simulations, this led to realistic behaviour
and hence, the use of an elliptical personal space was not necessary.
The pedestrian Pi perceives the environment to detect imminent and future
collisions with other pedestrians. A collision at some time tc ≥0 occurs when
another pedestrian Pj invades into the personal space of Pi, that is:
∃tc ≥0 | dij ≤ρi + rj,
[fórmula] (3)
where denotes the distance between the pedestrians’ centers.
Given a certain anticipation time tα, the pedestrian Pi resolves potential
collisions within this time in advance by adjusting its trajectory. As a result,
it safely navigates toward its goal, evading other pedestrians with minimal
eﬀort. To simulate this behaviour, an evasive force F is applied on P. Note
```

## Página 11 (2081 caracteres recortados)

```text
[fórmula] 46
I. Karamouzas et al.
aur approac
[fórmula] (
Fig. 1. Example of the force used to avoid a f
the force depends on the relative positions a
on the current positions of the pedestrians. T
space of the pedestrian Pi.
[fórmula] 4.2
Selecting Pedestrians
Having computed the set CP tα
i , we sort it
keep the ﬁrst N pedestrians. Preliminary e
that this number can be kept small (betwee
avoidance behaviour. This not only reduc
but also reﬂects natural human behavio
A Predictive Collision Avoidance Model for Pedestrian Simulation
[fórmula] 47
Fig. 2. The magnitude of the avoidance force as a function of the distance D
ition xi of pedestrian Pi and its future position ci plus the distance between
two pedestrians at their time of collision. As can be inferred from Fig. 2, the
but also reﬂects natural human behaviour. In real-life, an individual tr
avoid a limited number of other pedestrians, usually those that are on co
course with him in the coming short time. Similarly, the virtual pedestr
tries to evade the N pedestrians with which it will collide ﬁrst.
[fórmula] 4.3
Avoidance Maneuvers
We now show how the pedestrian Pi can avoid a potential collision with an
pedestrian Pj that belongs to the set CP tα
i . Let tcij be the time of co
between the two pedestrians. Let also ci = xi + tcijvdes
[fórmula] i
and cj = xj +
denote the locations of pedestrians Pi and Pj at time tcij; ci and cj derive
(5) and (6) respectively.
Based on these future locations, we select an evasive force Fij for the p
trian Pi, so that it can smoothly avoid the pedestrian Pj. The direction
force is given by the unit vector ncicj =
ci−cj
∥ci−cj∥pointing from cj to ci.
example, consider Fig. 1(a). The blue pedestrian will hit the red pedestr
the back. Therefore, it makes a slight move toward the latter and eventual
pass behind it. In contrast, in a typical particle-based system the red pede
would have forced the blue one to move in the opposite direction, leadin
new collision in the near future (Fig. 1(b)).
The magnitude of the evasive force Fi is approximated by a piecewise fu
f(D), where  is the distance between the c
```

## Página 12 (1091 caracteres recortados)

```text
[fórmula] 4.4
Computing the Evasive Force
In the last step of our algorithm, we compute the total evasive forc
is applied on the pedestrian Pi given its set CP tα
i . Two approach
distinguished. The ﬁrst is to take into account each one of the N p
independently and compute a corresponding force Fij as described abo
the evasive force can be deﬁned as the weighted sum of those N force
where the weighting factor wij gives a higher priority to the most
collisions.
The second approach, which diﬀers from existing solutions, is to
forces sequentially (iterative approach). The idea here is as follows. L
pedestrian in the set CP tα
[fórmula] i
and let Fij be the evasive force that is exer
Let us also, for notational convenience, name this force Fv. Then, we
whether the pedestrian Pi still collides with each one of the remaini
pedestrians in the set, after (virtually) applying the force Fv. In other
ﬁrst estimate the desired velocity of Pi by including Fv into the (4).
iterate over the N −2 pedestrians in the set and compute the time o
tc between Pi and each one of the selected N −2 pedestrians. If a col
```

## Página 13 (437 caracteres recortados)

```text
[fórmula] 46
I. Karamouzas et al.
Fig. 1. Example of the force used to avoid a future collision. Note that the direction of
the force depends on the relative positions at the moment of the impact, rather than
on the current positions of the pedestrians. The light blue disc represents the personal
space of the pedestrian Pi.
[fórmula] 4.2
Selecting Pedestrians
Having computed the set CP tα
, we sort it in order of increasing collision time and
```

## Página 14 (1469 caracteres recortados)

```text
A Predictive Collision Avoidance Model for Pedestrian Simulation
[fórmula] 51
Table 1. Statistics for the hallway scenario derived from the simulation of 100 agents
interactive applications, we simulated 1, 000 fully animated characters in a vir-
tual park environment. Each character enters the park through a random gate
and has to advance toward a randomly selected exit. To increase the realism of
the simulation, we varied the preferred and maximum speeds among the charac-
ters, as well as the anticipation time of each character and the size of its personal
space. The simulation was updated at 10 fps, whereas a parallel thread was used
to render the characters and the scene at 30 fps. Our model led to smooth mo-
tions and thus, we did not have to decouple the simulation from the rendering.
Since, on average, the cpu was busy for only 25% of each time step, we conclude
that our model can be used for real-time simulation of thousands of characters.
Finally, we also simulated the interactions of pedestrians at the crosswalks of an
outdoor virtual city environment. Our approach resulted in a smooth avoidance
behaviour and a visually pleasing simulation.
[fórmula] 50
I. Karamouzas et al.
Fig. 4. Example paths for the hallway scenario
we ﬁrst optimised the two models following an approach similar to the one de-
scribed above. In all test-cases, we noted that pedestrians using Helbing’s model
tend to adapt their motions rather late in order to avoid a potential collision.
```

## Página 20 (2050 caracteres recortados)

```text
ral mechanisms at the retina and brain levels (18, 19).
y, we represent the pedestrian’s visual information as
r all possible directions α in [−ϕ, ϕ] (with a reason-
r resolution), we compute the distance to the ﬁrst
α), if pedestrian i moved in direction α at speed v0
[fórmula] i ,
account the other pedestrians’ walking speeds and
If no collision is expected to occur in direction α, f(α)
default maximum value dmax, which represents the
stance” of pedestrian i (Fig. 1).
of the Cognitive Heuristics. The ﬁrst movement heu-
rns the relative angle αdes of the chosen walking di-
mpared with the line of sight. Empirical evidence
t pedestrians seek an unobstructed walking direction,
deviating too much from the direct path to their
[fórmula] !
¼ ð!
[fórmula] ! Þ
Effect of Body Collisions. In cases of overcrowding, physical
interactions between bodies may occur, causing unintentional
movements that are not determined by the above heuristics.
Indeed, at extreme densities, it is necessary to distinguish be-
tween the intentional avoidance behavior of pedestrians adapting
their motion according to perceived visual cues and unintentional
movements resulting from interaction forces caused by collision
with other bodies. We have therefore extended the above de-
scription by considering physical contact forces
[fórmula] f!
ij ¼ kgðri þ rj −dijÞ n!
[fórmula] ij;
ustration of a pedestrian p1 facing three other subjects and trying to reach the destination point O1 marked in red. The blue dashed line
o the line of sight. (B) Illustration of the same situation, as seen by pedestrian p1. (C) Abstraction of the scene by a black and white visual ﬁeld.
areas represent a shorter collision distance. (D) Graphical representation of the function f(α) reﬂecting the distance to collision in direction α. The
of the vision ﬁeld is limited by a wall. Pedestrian p4 is hidden by pedestrian p2 and, therefore, not visible. Pedestrian p3 is moving away, so
uld occur in position p′3, but only if p1 moved toward the right-hand side.
w.pnas.org/cgi/doi/10.1073/pnas.1016507108
Moussaïd et al.
```

## Página 21 (1354 caracteres recortados)

```text
is the main
ol their mo-
ation of the
econd ques-
nformation,
and desired
ssume that
walking be-
on time τ of
under con-
each pedes-
d speed v!
[fórmula] i.
trian’s body
=320, where
buted in the
ally charac-
d his or her
nment he or
r the end of
anges to the
destination (16, 17). A trade-off therefore has to be found be-
tween avoiding obstacles and minimizing detours from the most
direct route. Accordingly, our ﬁrst heuristic is “A pedestrian
chooses the direction αdes that allows the most direct path to des-
tination point Oi, taking into account the presence of obstacles.”
The chosen direction αdes(t) is computed through the minimi-
zation of the distance d(α) to the destination:
Here, α0 is the direction of the destination point.
The second heuristic determines the desired walking speed
vdes(t). Because a time period τ is required for the pedestrian to
stop in the case of an unexpected obstacle, pedestrians should
compensate for this delay by keeping a safe distance (20).
Therefore, we formulate the second heuristic as follows: “A pe-
destrian maintains a distance from the ﬁrst obstacle in the chosen
walking direction that ensures a time to collision of at least τ.” In
other words, the speed vdes(t) is given by vdesðtÞ ¼ minðv0
i ; dh=τÞ,
where dh is the distance between pedestrian i and the ﬁrst ob-
stacle in the desired direction αdes at time t. The vector v!
des of
```

## Página 22 (879 caracteres recortados)

```text
istance d(α) to the destination:
¼ d2
max þ fðαÞ2 −2dmaxfðαÞcosðα0 −αÞ:
direction of the destination point.
heuristic determines the desired walking speed
e a time period τ is required for the pedestrian to
e of an unexpected obstacle, pedestrians should
or this delay by keeping a safe distance (20).
formulate the second heuristic as follows: “A pe-
ains a distance from the ﬁrst obstacle in the chosen
on that ensures a time to collision o at least τ.” In
he speed vdes(t) is given by
[fórmula] ,
e distance between pedestran i ante rst o-
esired direction αdes at time t. The vector v!
des of
elocity points in direction αdes has the norm
The change in the actual velocity v!
i at time t
walking conditions is given by the acceleration
dt ¼ ð v!
des −v!
iÞ=τ.
Collisions. In cases of overcrowding, physical
etween bodies may occur, causing unintentional
at are not determined by the above heuristics.
```

## Página 23 (1218 caracteres recortados)

```text
[fórmula] v! i. ody ere the ac- her or of the i. the pe- 9). as on-
ﬁrst
[fórmula] v0 i , and (α) the
stop in the case of an unexpected obstacle, pedestrians shoul
compensate for this delay by keeping a safe distance (20
Therefore, we formulate the second heuristic as follows: “A pe
destrian maintains a distance from the ﬁrst obstacle in the chose
walking direction that ensures a time to collision of at least τ.” I
other words, the speed vdes(t) is given by vdesðtÞ ¼ minðv0
i ; dh=τ
where dh is the distance between pedestrian i and the ﬁrst ob
stacle in the desired direction αdes at time t. The vector v!
des o
the desired velocity points in direction αdes has the norm
k v!
desk ¼ vdes. The change in the actual velocity v!
i at time
under normal walkin conditions is given by the acceleratio
equation
Effect of Body Collisions. In cases of overcrowding, physica
interactions between bodies may occur, causing unintentiona
movements that are not determined by the above heuristic
Indeed, at extreme densities, it is necessary to distinguish be
tween the intentional avoidance behavior of pedestrians adaptin
their motion according to perceived visual cues and unintentiona
movements resulting from interaction forces caused by collisio
```

## Página 24 (1521 caracteres recortados)

```text
where g(x) = 0 if the pedestrians i and j do not touch ea
and otherwise equals the argument x. n!
ij is the normali
tor pointing from pedestrian j to i, and dij is the distance
the pedestrians’ centers of mass (1). The physical int
with a wall W is represented analogously by a conta
[fórmula] f!
iW ¼ kgðri −diWÞ n!
iW, where diW is the distance to the
and n!
iW is the direction perpendicular to it.
[fórmula] The
resultin
acceleration
euation
reads
[fórmula] d
and is sol
gether with the usual equation of motion d x!
i=dt ¼ v!
[fórmula] x!
iðtÞ denotes the location of pedestrian i at time t. In co
social force models, however, the interaction terms f!
ij a
are nonzero only in extremely crowded situations, but n
normal walking conditions.
Results
uch each other
normalized vec-
stance between
cal interaction
contact force
e to the wall W
[fórmula] ads
is sove to-
dt ¼ v!
i, where
t. In contrast to
ms f!
ij and f!
[fórmula] iW
, but not under
shows transitions from smooth ﬂows to stop
“crowd turbulence,” as has been observed bef
(4). Fig. 3C depicts typical space–time diagra
at various density levels, displaying a smooth,
density (regime 1), but stop-and-go waves
(regimes 2 and 3). These waves result from t
small local perturbations in the ﬂow due to
lems when competing for scarce gaps (22): W
pedestrians is high enough, such perturbatio
reaction of braking maneuvers, resulting in
waves. This result is illustrated by the sign
between the local speed at positions x1 and
a certain time lag T (Fig. 3B). In particular
us to estimate the backward propagation s
```

## Página 25 (3364 caracteres recortados)

```text
erved trajectories under both conditions (Fig. 2).
e Patterns of Motion. Next, we explored the model pre-
in a collective context. For bidirectional trafﬁc in a
ssuming random initial positions of pedestrians, we ﬁnd
w directions separate spontaneously after a short time, as
ally observed (Fig. S2). This collective organization re-
e well-known lane formation phenomenon (2), which is
teristic property of crowd dynamics.
lso investigated the inﬂuence of pedestrian density on
tional ﬂows. The velocity–density relation predicted by
el agrees well with empirical data (21) (Fig. 3A). Fur-
e, when the density exceeds critical values, our model
by a power law with exponent 1.95 ± 0.09. This result is in excellen
agreement with detailed evaluations of crowd turbulence durin
a crowd disaster that happened to be recorded by a surveillanc
camera (4).
Discussion
The greater explanatory power of our heuristics-based modeling
demonstrated through comparison with different empirical an
experimental data (overview in Fig. S5 and Table S1), sugges
a paradigm shift from physics-inspired binary interaction mode
to an integrated treatment of multiple interactions, which ar
typical for social interactions in human crowds or animal swarm
(23–28). Without requiring additional assumptions, our approac
overcomes various issues related to the combination of multipl
binary interactions (6, 11). Our model treats a pedestrian’s re
action to his or her visually perceived environment in an in
tegrated way rather than reducing it to a superposition of pa
interactions. Instead of being repelled by their neighbors, as wa
assumed in previous particle models, individuals actively seek
free path through the crowd. The combined effect of neighborin
individuals is implicitly included in the representation of
pedestrian’s visual ﬁeld. Our model therefore correctly handle
situations in which pedestrians are hidden or outside the ﬁeld o
view. Finally, high-density and life-threatening situations can b
studied by combining heuristics-based movement resulting from
visual perception of the environment with unintentional di
placements due to physical forces resulting from unavoidabl
collisions with other bodies. In doing so, the emergence of crow
turbulence in panic situations can be reproduced as well.
Understanding pedestrian heuristics and the emergence o
complex crowd behavior is a crucial step toward a more reliabl
description and prediction of pedestrian ﬂows in real-life si
uations. Our heuristics-based model therefore has importan
practical applications, such as the improvement of architecture
and exit routes, as well as the organization of mass events. I
addition, the vision-based treatment of the pedestrian heuristic
esults of computer simulations for the heuristic pedestrian model
s) compared with experimental results (shaded lines) during simple
maneuvers in a corridor of 7.88 m length and 1.75 m width (data
10). (A) Average trajectory of a pedestrian passing a static in-
tanding in the middle of the corridor (n = 148 replications). (B)
rajectory of a pedestrian passing another individual moving in the
direction (n = 123 replications). Dashed shaded lines indicate the SD
erage trajectory. Pedestrians are moving from left to right. The
simulations were conducted in a way that reﬂected the experi-
[fórmula] A B 1 2 3 C ) s ( e m i T 30 60 90 0 t n
eiciffe
[fórmula] o C n oit ale rr o C 0.6 0.3 0
```

## Página 26 (1831 caracteres recortados)

```text
her evidence for our cognitive, heuristics-
be collected by using eye-tracking systems
e visual cues followed by pedestrians. Our
perspectives in other research areas. In the
robotics, for example, the model may serve
n in complex dynamic environments, which
nt for swarms of mobile robots (31). In fact,
ion-avoidance concepts of multirobot sys-
n inspired by human behavior (32, 33). The
support resource-efﬁcient designs. We also expect t
heuristics-based approach will inspire new models of c
human behavior such as group decision making (34) and
social activity patterns (35, 36), where the occurrence o
taneous interactions between multiple individuals matte
Materials and Methods
Experimental Setup. The controlled experiments shown in Fig. 2
ducted in 2006 in Bordeaux (France). The experimental corridor
length and 1.75 m width was equipped with a 3D tracking syste
consisted of three digital cameras (SONY DCR-TRV950E) mount
of turbulent ﬂows in front of a bottleneck for an occupancy value of 0.98. (For the analysis of a turning corridor as in
urg in 2010, see Fig. S4). (A) The local body compression Cð x!Þ reveals two critical areas of strong compression in front o
B) Analyzing the “crowd pressure” (deﬁned as local density times the local velocity variance) (Materials and Methods) rev
g (in red), indicating the likelihood of a crowd disaster (4). (C) Distribution of displacements (i.e., location changes bet
d by speeds with k v!
ik < 0:05m=s). The double logarithmic representation reveals a power law with slope k = −1.95 ± 0.0
al ﬁndings (see ﬁgure 3e in ref. 4, where the slope is k = −2.01 ± 0.15). The local speed, local pressure, and local co
n Materials and Methods. The above results are based on simulations of 360 pedestrians during 240 s in a corridor of lengt
a bottleneck of width 4 m, assuming periodic boundary conditions.
```

## Página 28 (396 caracteres recortados)

```text
agent velocity (Eq. 2) by considering a simple avoidance mecha
The general idea is that the self-propelled particle will produce a
vi(t) as stated in Ref. [9]. In this case, the new mechanism w
depending on the neighbor particles and obstacles. First, the coll
[fórmula] eik
where j indicates the nearest visible neighbor, k the nearest point
term for breaking possible symmetric situations.
[fórmula] 3
```

## Página 29 (0 caracteres recortados)

Fuente LaTeX de fórmulas (texto invisible):

- `\bold{v}_d ~ = ~ v_d~\bold{e}^i_a`
- `\bold e_{a}^{i} = \frac{\bold n_{c} + \bold e_{t}^{i}}{| \bold n_{c} + \bold e_{t}^{i} |}`

## Página 42 (44 caracteres recortados)

```text
www.urbix.com.ar
1- Aspectos Geométricos
FILAS
```
