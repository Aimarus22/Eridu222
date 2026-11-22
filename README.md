# Tablilla de los 222 Me — Teogonía FAIR de $B_4$

* **Autor:** Aimar Rollán-González | Unafiliated Tinkerer & Transmedia Artist
* **GitHub:** https://github.com/Aimarus22
* **Disponibilidad:** https://github.com/Aimarus22/Eridu222
* **Fecha:** Nov 2026

**Abstract:**
*Dub-nam-tar-ra* determinista de las 65.536 formas booleanas de 4 variables ($B_4$), ordenadas según la cosmogonía sumeria arcaica del *Abzu*. Atlas FAIR en Python puro (cero dependencias): Quine-McCluskey exacto, 402 *Ĝiš-ḫur* (NP), 222 *Me* (NPN), ANF, Walsh-Hadamard y cálamo Unicode (`dubsar.py`) para Termux.

**Keywords:** Boolean Algebra, Quine-McCluskey Algorithm, Walsh-Hadamard, Sumerian Cosmology, Code Poetry, Human in the Loop Creation, New Media Art, Oddities

> *La arcilla de Eridu y un procesador lógico comparten el mismo elemento: un silicio sin edad.  
> Cuatro puertas. Dieciséis cuñas. Sesenta y cinco mil quinientos treinta y seis destinos cocidos en un cosmos de barro primordial.*

Este repositorio es una **tablilla cuneiforme digital** y, al mismo tiempo, una pieza de ingeniería de datos: un generador en Python con cero dependencias externas que cartografía, disecciona y audita la totalidad del *Abzu* booleano de 4 variables ($2^{2^4} = 65.536$ funciones) en **~4 segundos desde un teléfono Android con Termux**.

Este horno térmicux cuece el barro para que nada se pierda. No hay ruido analógico, ni heurísticas aproximadas, ni valores imputados. Todo es determinista, exacto y verificable bit a bit mediante `SHA-256`.

---

## Por qué existe esta tablilla de 5.674 KB

Cualquiera puede contar del `0` al `65.535` en binario en seis líneas de código. Es un ejercicio simple y un prompt aun más simple.

Esta tablilla de arcilla binaria se cuece sin instalar `numpy`, `pandas`, `sympy`, *SageMath* ni *toolchains* de C++:

1. **Síntesis de circuitos digitales:** Algoritmo exacto de Quine-McCluskey + *branch-and-bound* para hallar el mínimo irreductible de términos producto y literales (`min_sop_terms`, `min_sop_literals`).
2. **Teoría de grupos y simetrías:** Colapso completo del *Abzu* en sus **402 *Ĝiš-ḫur* (clases NP)** y **222 *Me* (clases NPN)** mediante tablas de búsqueda (LUTs) por byte.
3. **Criptografía y análisis espectral:** Transformada rápida de Möbius (Forma Normal Algebraica de Zhegalkin), Transformada rápida de Walsh-Hadamard (no-linealidad y detección de funciones *bent*) y sensibilidad media sobre el hipercubo de 4 dimensiones.

---

## Teogonía del *Abzu*: jerarquías de $B_4$

Aunque el *Abzu* contiene 65.536 tablillas binarias, casi todas son ecos simétricos de un mismo decreto. En los márgenes del CSV habitan los linajes primordiales:

* **Los dos *Me* solitarios (órbitas NPN de tamaño 2):** Mientras una forma corriente se refleja en cientos de espejos (hasta `768`), solo dos decretos permanecen casi solos:
  * **`0x0000` (*Nammu*) y `0xFFFF` (*An*):** El mar primordial mudo sin una sola cuña encendida y la bóveda celeste íntegra sin sombra. Grado `0`, sensibilidad `0.0`, cero puertas activas.
  * **`0x6996` y `0x9669` (*Enlil*, el Aliento que separa):** Como el dios del viento que apartó a *An* (Cielo) de *Ki* (Tierra), su paridad (`A ⊕ B ⊕ C ⊕ D`) divide el tablero en ajedrez: sensibilidad máxima (`4.0000`), no-linealidad `0`, y la peor pesadilla de Quine-McCluskey (`8` términos y `32` literales irreductibles).
* **Los *Abgal* (`896` funciones *bent*):** Los sabios primordiales surgidos del *Abzu*. Alcanzan la máxima no-linealidad criptográfica (`6`), espectro de Walsh plano (`walsh_max_abs = 4`) y grado algebraico exactamente `2`, bajo una maldición estructural: **jamás pueden estar equilibrados** (peso de Hamming siempre `6` o `10`, nunca `8`).
* **La Obra de *Kulla* (`168` funciones monótonas):** *Kulla*, dios sumerio del molde de ladrillos y la piqueta, corresponde al número de Dedekind $M(4) = 168$. Ladrillo sobre ladrillo: una vez encendida una cuña, jamás retrocede de `1` a `0`.
* **El Paso de *Utu* por el *Kur* (`256` funciones autoduales):** Como el sol recorriendo el cielo diurno y su reverso exacto en el inframundo de *Ereškigal* ($f(\neg x) = \neg f(x)$).
* **Las Cañas de *Nisaba* (`32` funciones simétricas):** La señora de la escritura y las cuentas solo pesa cuántas espigas arden, indiferente y ciega al orden de las puertas.
* **La Cuerda de *Eridu* (`32` funciones afines):** Geometría recta de agrimensor, grado $\le 1$ y no-linealidad `0`.
* **Los *Gidim* (`942` funciones con variables vacuas):** Espectros del *Kur* que ocupan una casa de cuatro muros pero ignoran en secreto al menos una puerta (`essential_vars < 4`). Solo `64.594` formas escuchan las cuatro entradas.
* **Arcilla de *Ninmaḫ* (el resto del *Abzu*):** La multitud ordinaria moldeada con barro primordial para sostener el peso del cosmos.

---

## Codebook (`boolean4_atlas.csv`)

`65.536` filas × `21` columnas, sin valores nulos. Convención de entrada: `idx = 8A + 4B + 2C + D`; `truth_table_bin` debe leerse como texto para preservar ceros a la izquierda; el grado de `0x0000` se codifica como `0`.

| Columna | Tipo | Descripción |
| :--- | :---: | :--- |
| `func_id_dec` | `int` | Identificador entero contiguo (`0`–`65535`). |
| `func_id_hex` | `str` | Identificador hexadecimal normalizado (`0x0000`–`0xFFFF`). |
| `truth_table_bin` | `str` | Tabla de verdad de longitud fija 16 (`f(15)...f(0)`). |
| `hamming_weight` | `int` | Cantidad de unos en la tabla de verdad (`0`–`16`). |
| `essential_vars` | `int` | Número de variables de entrada de las que depende realmente (`0`–`4`). |
| `avg_sensitivity` | `float` | Influencia total / sensibilidad media al voltear un bit (`0.0000`–`4.0000`). |
| `algebraic_degree` | `int` | Grado del polinomio en Forma Normal Algebraica (`0`–`4`). |
| `anf_hex` | `str` | Máscara hexadecimal de los coeficientes de la ANF (Zhegalkin). |
| `walsh_max_abs` | `int` | Máximo valor absoluto del espectro de Walsh-Hadamard (`4`–`16`). |
| `nonlinearity` | `int` | Distancia mínima a las funciones afines: $8 - \text{walsh\_max\_abs}/2$ (`0`–`6`). |
| `min_sop_terms` | `int` | Número mínimo exacto de términos producto en Suma de Productos (`0`–`8`). |
| `min_sop_literals` | `int` | Número mínimo exacto de literales en Suma de Productos (`0`–`32`). |
| `np_canonical_hex` | `str` | Representante mínimo de su *Ĝiš-ḫur* / clase NP (`402` clases). |
| `npn_class_id` | `int` | Índice correlativo de su *Me* / linaje NPN (`1`–`222`). |
| `npn_canonical_hex` | `str` | Representante mínimo de su *Me* / linaje NPN (`222` clases). |
| `is_balanced` | `0/1` | `1` si `hamming_weight == 8` (`12.870` funciones). |
| `is_monotone` | `0/1` | `1` si es monótona creciente en el retículo booleano (`168` funciones). |
| `is_self_dual` | `0/1` | `1` si $f(\neg x) = \neg f(x)$ para todo $x$ (`256` funciones). |
| `is_symmetric` | `0/1` | `1` si la salida depende solo del peso de Hamming de la entrada (`32` funciones). |
| `is_affine` | `0/1` | `1` si `algebraic_degree <= 1` y `nonlinearity == 0` (`32` funciones). |
| `is_bent` | `0/1` | `1` si alcanza la no-linealidad máxima `6` (`896` funciones). |

---

## Reproducción y sello criptográfico

Requiere únicamente **Python 3.10+** (biblioteca estándar, cero paquetes externos). Probado en Linux y Android/Termux.

```bash
python3 build_boolean4_atlas.py
sha256sum boolean4_atlas.csv
```

**Huella esperada (`SHA-256`):**
`58bef4cb85b27cf47e7dcceacbd2630ce5dcf922e1579b8af6fa67817c39cf29`

---

## El cálamo de bolsillo (`dubsar.py`)

Para estampar cualquier tablilla del CSV en la terminal con su mapa de Karnaugh 4×4 en cuñas Unicode, polinomio ANF decodificado y colofón determinista:

```bash
python3 dubsar.py 0x6996
python3 dubsar.py --random --order abgal
```

Linajes filtrables con `--order`: `abgal`, `kulla`, `utu_kur`, `nisaba`, `eridu`, `gidim`, `balanced`, `enlil` y `solitary`.

---

## CRediT (Contributor Roles Taxonomy)

* **Aimar Rollán-González:** Idea original, arquitectura conceptual, financiación (pago de tarifa de datos y de Gemini Pro), dirección, validación, pulido estético y haiku final.

## Agradecimientos

* A una LLM: por la asistencia en la redacción, amplificación cognitiva en ausencia de cafeína y picar el código ejecutable en una noche de insomnio.
* A un editor de texto plano: por su soporte digital de la redacción (después de pasado el insomnio).
* A Termux: por servir de horno portátil donde cocer la tablilla csv.
* Al lenguaje natural vehículo de mi pensamiento (castellano) y a los escribas anónimos de Eridu, por prestar la arcilla y el mito.
* Al lenguaje de programación (Python): por ser vínculo entre el concepto abstracto y el silicio.
* A George Boole: por sentar las bases lógicas.
* A mi padre: por haberme convencido en su día para apuntarme a un FP de Electrónica en vez de a uno de Navegación marítima. Allí oi hablar por primera vez de tablas de verdad y de puertas lógicas, aunque perdí la libertad de navegar por la mar océana.

## Licencias

* `CC-BY-NC-ND 4.0`, para el haiku.
* `CC-BY 4.0`, para el `README.md`.
* `CC0 1.0`, para el dataset CSV (`boolean4_atlas.csv`).
* `MIT`, para el código en Python (`build_boolean4_atlas.py`, `dubsar.py`).

## Haiku: Cálamo electrónico Bifourcado

> Barro binario  
> y dioses ordenados;  
> canto de otoño.