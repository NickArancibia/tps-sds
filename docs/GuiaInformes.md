# Guía para Redacción de Informe

- Los informes y las presentaciones sobre un mismo trabajo son documentos independientes y cada uno es autocontenido. No se pueden dejar ítems sin especificar en uno de ellos porque estarán en el otro.
- **Numerar Secciones y sub-secciones.**
  Las secciones habituales son similares a las de las presentaciones: *Introducción*, *Modelo*, *Implementación*, *Simulaciones*, *Resultados* y *Conclusiones*. Para más detalle ver "GuiaPresentaciones.pdf".
- **Lenguaje técnico escrito:** no usar lenguaje coloquial ni descripciones "literarias". Usar el mismo idioma en todo el informe.
- Establecer conclusiones basadas en los resultados mostrados.
- Todas las secciones llevan texto analizando y llevando un hilo lógico del estudio. En ningún caso puede haber una sección con figuras sueltas.
- **Figuras y ecuaciones:** deben estar numeradas y referenciadas en el texto, de la siguiente manera:
  - *En el texto:* "En la Fig. 1..."
    > **Figura 1:** Descripción .... parámetros, etc.  
    > *(en general, observable vs input/parámetro, promedios y barras de error)*
  - *En el texto:* "En la Ec. (1)..."
    $$E = m c^2 \quad (1)$$
    > donde $E$ es la energía, $m$ la masa de la partícula y $c$ la velocidad de la luz.

---

### Convención para símbolos matemáticos (tanto en informe como presentaciones):
- **Escalares:** *Times New Roman*, Itálicas, Sin Negrita (ej.: $t$, ec. (1)).
- **Vectores:** **Times New Roman**, Negrita, Sin Itálicas (ej.: $\mathbf{r}_i(t)$, $\mathbf{x}$).
- **Unidades y números:** Sin negritas ni itálicas (ej.: $m = 4\text{ kg}$, $8\text{ m}$).
  - Metros: $\text{m}$
  - Segundos: $\text{s}$
  - Kilogramos: $\text{kg}$, etc.

---

### Referencias
Los informes llevan una sección extra sin número, denominada **"Referencias"**, donde se lista la bibliografía citada en el trabajo. Si no está citado en el texto, entonces no se debe agregar en Referencias ni en ninguna otra parte.

- *En el texto:* "Se ha demostrado [1] que ..."
- *Sección Referencias al final:*
  > **Referencias:**  
  > [1] Nombre Apellido, "Título trabajo", *Nombre publicación*, vol., nro., pp. (año).

*Tip:* Consultar [Google Scholar](https://scholar.google.com.ar); debajo de la publicación, haciendo clic en el símbolo de comillas (`""`), aparecen las citas en el formato indicado.

---

### Sugerencia General
- Utilizar **LaTeX** como procesador de texto (y ecuaciones).
