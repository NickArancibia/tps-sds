# Simulación de Sistemas
## Trabajo Práctico Nro. 5: Dinámica Peatonal
*(Enunciado publicado en CAMPUS el 30/10/2026. Transcripción de
`enunciado/TP5_Enunciado_2026Q2.pdf`.)*

---

### General

Elegir entre los dos problemas detallados más abajo para implementar, estudiar y presentar. Ambos
problemas utilizan alguno de los siguientes modelos de dinámica peatonal vistos en las clases
teóricas: SFM [1] sin fuerza social o CPM [2].

Las simulaciones tendrán un *dt* fijo e intrínseco de la simulación (en el caso de dinámica
molecular regida por el paso temporal). En caso de ser necesario (según sea el modelo elegido,
número de partículas, tamaño de archivos de output, etc.) considerar un *dt₂* para imprimir el
estado del sistema (posiciones, velocidades, radio en caso de CPM, de las partículas) para luego
realizar análisis y animaciones con una velocidad adecuada. **Notar que en el caso de CPM el *dt*
forma parte de las reglas del modelo y por lo tanto no se lo debe cambiar arbitrariamente.** Se
recuerda que la simulación debe generar un output en formato de archivo de texto. Luego el módulo
de animación se ejecuta en forma independiente tomando estos archivos de texto como input. De esta
forma la velocidad del análisis y de la animación no quedan supeditados a la velocidad de la
simulación.

Para cada uno de los estudios que se realicen, se debe mostrar una animación característica, la
evolución temporal del observable primario, y explicitar cómo se calcula el observable escalar que
se usará luego al mostrar input vs. observable escalar.

Los entregables del T.P. son:

* **a-** Presentación oral tipo Powerpoint o similar de **13 minutos** de duración con las
  secciones indicadas en el documento `".../Formato_Presentaciones.pdf"`.
* **b-** El documento de la presentación en formato pdf (sin animaciones embebidas, solo links
  explícitos a youtube o vimeo, por favor no a google drive).
* **c-** El código fuente implementado en un archivo `.zip`. Solo versión final del motor de
  simulación (tamaño del archivo del orden de unos pocos kB). No adjuntar en este archivo código de
  postprocesamiento, ni historial de versiones, ni output de simulaciones, ni figuras, ni
  resultados, ni otros documentos.

#### Fecha y Forma de Entrega

La presentación en pdf (b) y el código fuente (c) deberán ser presentados a través de campus,
**antes del día 13/11/2026 a las 13 hs**. Los archivos deben nombrarse de la siguiente manera:
`SdS_TP5_2026Q2GXXCSS_Presentación` y `SdS_TP5_2026Q2GXXCSS_Codigo`, donde XX es el número de
grupo y SS es la comisión ("S" o "S2"). Las presentaciones orales (a) se realizarán durante la
clase del mismo día.

---

### Problema 1: Calibración de una capa de elusión con trayectorias experimentales

*(No elegido por el grupo; se transcribe completo por referencia.)*

La cátedra proveerá un conjunto de *M* eventos experimentales, cada uno con las trayectorias reales
de 2 peatones que caminan en curso de colisión con intervalo de muestreo *Δt*<sub>exp</sub>. Para
cada peatón *i* de cada evento *m* se dispone de su trayectoria experimental
**r**<sub>i,exp</sub>(*t<sub>k</sub>*) = (*x*<sub>i,exp</sub>(*t<sub>k</sub>*),
*y*<sub>i,exp</sub>(*t<sub>k</sub>*)), con *t<sub>k</sub>* = *k Δt*<sub>exp</sub>.

Elegir entre SFM sin fuerza social [1] o CPM [2]. Estos modelos, por sí solos, no anticipan
colisiones. Proponer una capa de elusión que dependa de exactamente **2 parámetros a ajustar
(*p₁*, *p₂*)** y que actúe **únicamente modificando la velocidad deseada** de la partícula, a
través de un target temporal. Es decir, ante la detección de una colisión futura con otro agente,
la capa de elusión reemplaza transitoriamente el target final por un target temporal (lo que cambia
la dirección de la velocidad deseada), y una vez resuelto el conflicto la partícula vuelve a
dirigirse a su target final. La capa de elusión no puede agregar fuerzas ni modificar las reglas
propias del modelo elegido. Ésta debe estar explicada en forma matemática en la introducción de la
presentación, y calibrada/ajustada en base a los datos experimentales provistos.

**Condiciones de cada simulación:** cada uno de los 2 agentes se inicializa con la posición y la
velocidad experimentales en el instante inicial del evento. Su target final es la última posición
de su trayectoria experimental y el módulo de su velocidad deseada *v<sub>d</sub>* es la rapidez
media de dicha trayectoria. Se simula hasta el último instante experimental del evento. Para SFM
usar como radio de las partículas *r* = 0.25 m; para CPM usar *r*<sub>min</sub> = 0.10 m y
*r*<sub>max</sub> = 0.25 m. Tomar los parámetros no especificados aquí de los *papers*
correspondientes.

Para cuantificar la diferencia entre trayectorias experimentales y simuladas se utilizarán dos
métricas de error cuadrático medio (ECM), definidas para cada peatón *i* del evento *m*, con
*N<sub>m</sub>* instantes experimentales:

**Métrica 1** (a iguales tiempos): compara las posiciones experimental y simulada en el mismo
instante *t<sub>k</sub>*,

E<sup>(1)</sup><sub>i</sub> = (1/*N<sub>m</sub>*) Σ<sub>k</sub> [ (*x*<sub>i,exp</sub>(*t<sub>k</sub>*) − *x*<sub>i,sim</sub>(*t<sub>k</sub>*))² + (*y*<sub>i,exp</sub>(*t<sub>k</sub>*) − *y*<sub>i,sim</sub>(*t<sub>k</sub>*))² ]  (1)

**Métrica 2** (punto más cercano): para cada punto (*x*, *y*) de la trayectoria experimental se
toma el punto (*x*', *y*') más cercano de la trayectoria simulada, aunque éste no corresponda al
mismo tiempo,

E<sup>(2)</sup><sub>i</sub> = (1/*N<sub>m</sub>*) Σ<sub>k</sub> min<sub>j</sub> [ (*x*<sub>i,exp</sub>(*t<sub>k</sub>*) − *x*<sub>i,sim</sub>(*t<sub>j</sub>*))² + (*y*<sub>i,exp</sub>(*t<sub>k</sub>*) − *y*<sub>i,sim</sub>(*t<sub>j</sub>*))² ]  (2)

Notar que la **Métrica 1** penaliza diferencias de forma y de tiempo de paso, mientras que la
**Métrica 2** compara solo la forma geométrica de la trayectoria. Para cada métrica por separado,
el error de un evento es el promedio sobre sus 2 peatones (*E<sub>m</sub>*), y el error
poblacional es el promedio sobre todos los eventos:

⟨E⟩(*p₁*, *p₂*) = (1/M) Σ<sub>m</sub> *E<sub>m</sub>*(*p₁*, *p₂*)  (3)

#### Puntos a resolver

* **a)** Implementar el modelo elegido con la capa de elusión propuesta. Mostrar animaciones
  características que superpongan las trayectorias experimentales y las simuladas para algunos
  eventos. Durante la presentación, dedicarle a la descripción matemática de la capa de elusión
  más tiempo del habitualmente destinado a la introducción matemática de las presentaciones.
* **b)** Calibración poblacional: encontrar el par (*p₁*, *p₂*) que minimiza ⟨E⟩ usando los
  mismos parámetros para todos los eventos. Describir el proceso empleado para encontrar el
  conjunto óptimo de parámetros. Hacerlo para cada una de las dos métricas por separado. Mostrar
  ⟨E⟩ en función de (*p₁*, *p₂*) (por ejemplo, gráfico de superficie sobre una grilla de
  parámetros, y/o cortes unidimensionales con sus barras de error), indicando el óptimo. Comparar
  los óptimos obtenidos con cada métrica.
* **c)** Calibración individual: para cada evento *m* encontrar el par (*p*<sub>1,m</sub>,
  *p*<sub>2,m</sub>) que minimiza *E<sub>m</sub>*, para cada métrica. Mostrar la distribución de
  los parámetros óptimos individuales, junto con los valores poblacionales obtenidos en (b).
  Comparar la distribución de errores *E<sub>m</sub>* obtenidos con los parámetros poblacionales y
  con los individuales, y discutir cuánto se gana al individualizar los parámetros.
* **d)** Validación cruzada. Separar los eventos al azar en un conjunto de entrenamiento y otro de
  validación. Calibrar los parámetros poblacionales con el primero y reportar el error sobre el
  segundo. Repetir para distintas particiones y comparar con los errores de (b).

---

### Problema 2: Evacuación con esquema híbrido Event Driven + Time Step Driven

***(Problema elegido por el grupo.)***

Elegir entre SFM sin fuerza social [1] o CPM [2].

Simular la evacuación de ***N* = 500 agentes** desde una habitación cuadrada de lado
***L* = 50 m** con una única puerta de ancho ***d* = 0.8 m** ubicada en el centro de una de sus
paredes, como se muestra en la Fig. 1. Inicialmente los agentes se generan al azar, sin
superponerse entre ellos ni con las paredes, en toda la habitación (densidad baja). El target de
todos los agentes es la puerta y el módulo de la velocidad deseada es ***v<sub>d</sub>* =
1.5 m/s**. Las paredes son rígidas y deben interactuar con las partículas si alguna la choca. Los
agentes que atraviesan la puerta se retiran de la simulación una vez que se alejan de ella una
distancia de **1 m** (esto requiere un segundo target una vez alcanzada la puerta). Para SFM usar
como radio de las partículas una distribución uniforme *r* ∊ [0.18 m, 0.25 m]; para CPM usar
***r*<sub>min</sub> = 0.10 m** y ***r*<sub>max</sub> = 0.25 m**. Tomar los parámetros no
especificados aquí de los *papers* correspondientes.

> **Figura 1** (en el PDF): esquema del sistema a simular en un momento arbitrario: habitación
> cuadrada de lado *L* con la puerta de ancho *d* en el centro de una pared. Las partículas azules
> están en la zona diluida (candidatas a Event Driven) y las rojas en el bottleneck cerca de la
> puerta (candidatas a Time Step Driven). Las flechas indican las velocidades.

Mientras los agentes están dispersos, se mueven en línea recta hacia la puerta con velocidad
constante y prácticamente no interactúan, por lo que su dinámica puede resolverse con dinámica
molecular regida por eventos (EDMD), avanzando el sistema directamente hasta el próximo evento
(contacto entre agentes, contacto con paredes, llegada a la puerta, etc.). A medida que se forma el
bottleneck cerca de la puerta, las interacciones se vuelven continuas y esas partículas requieren
dinámica molecular regida por el paso temporal (TSDMD).

Proponer un esquema híbrido que permita separar, tanto por etapas de la simulación como por cada
partícula, la utilización de uno u otro esquema. Describir matemáticamente:

* Los criterios de pasaje de una partícula de EDMD a TSDMD y viceversa (por ejemplo, en base a
  densidad local, número de vecinos, tiempo al próximo contacto, distancia a la puerta, etc.).
* Cómo se resuelve la convivencia de ambos esquemas: sincronización entre los eventos y los pasos
  *dt*, cómo se calculan los eventos de una partícula EDMD con una partícula TSDMD, y cómo se
  garantiza que no se pierdan contactos ni haya superposiciones en el pasaje de un esquema a otro.
* En los casos EDMD puro e híbrido, explicar cómo será considerada la colisión entre agentes y
  entre agentes y paredes, y el mecanismo para recuperar la velocidad deseada después de dicha
  colisión.

#### Puntos a resolver

* **a)** Implementar los tres esquemas: TSDMD puro, EDMD puro e híbrido. Mostrar animaciones
  características de cada uno; en el caso híbrido colorear las partículas según el esquema con el
  que se resuelve en cada instante. Graficar la evolución temporal de la fracción de partículas en
  cada esquema. Durante la presentación dedicarle a la descripción matemática-computacional del
  esquema híbrido más tiempo del que usualmente se dedica a la introducción matemática del TP.
* **b)** Para los tres esquemas, medir las curvas de población (número de agentes dentro de la
  habitación en función del tiempo) y el tiempo de evacuación (tiempo en que sale el último
  agente). Realizar al menos 10 realizaciones y reportar los tiempos de evacuación promedio con sus
  barras de error. Tomando TSDMD puro como referencia, discutir las diferencias de los otros dos
  esquemas.
* **c)** Medir el tiempo de ejecución (*wall-clock*) de la simulación completa para los tres
  esquemas, en la misma computadora y con su barra de error sobre las realizaciones. Para el
  esquema híbrido, variar el parámetro principal del criterio de pasaje entre esquemas y graficar
  el tiempo de ejecución y el tiempo de evacuación en función de dicho parámetro, indicando los
  valores de los casos TSDMD puro y EDMD puro como referencia.
* **d)** Estudiar cómo escalan los tiempos de ejecución de los tres esquemas con el número de
  agentes, variando *N* (por ejemplo *N* ∊ [100, 1000]) y en dos variantes: a) aumentando *L* de
  forma tal que la densidad inicial se mantenga constante; y b) a *L* constante, aumentando la
  densidad.

---

### Referencias

[1] Helbing, D., Farkas, I., & Vicsek, T. (2000). Simulating dynamical features of escape panic.
*Nature*, 407(6803), 487-490.

[2] Baglietto, G., & Parisi, D. R. (2011). Continuous-space automaton model for pedestrian
dynamics. *Physical Review E*, 83(5), 056117. (PDF en `papers/Biblio_6_7/CPM.pdf`.)
