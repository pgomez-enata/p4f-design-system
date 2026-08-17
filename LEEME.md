# Pitch 4 Fun — sistema de diseño

Marca de **Fundación Enlata** e **IAvanza** (HUB de Innovación). Evento de pitch
rápido, **dos ediciones al año**, en formato presencial y virtual.

El sistema se construye para **cualquier edición**, no para una en concreto: lo
que cambia entre ediciones (número, fecha, sede, modalidad) vive en tokens, no
horneado en las plantillas.

**Hoja: 8.5 × 11 pulgadas (612 × 792 pt).** No A4.

---

## Estado

⚠️ **Las cifras de comprobaciones que aparecen en las secciones de cada paso son
las de SU fecha** (68 · 118 · 167 · 194 · 204 · 211 · 223). La corrida de hoy es
la única que cuenta: `python3 build.py doctor`. Una cifra vieja citada en presente
se lee como el estado actual — pasó con «58 comprobaciones» y lo cazó la auditoría.


**`PLAN.html`** es el tablero para Piero: lo cerrado, lo que espera su decisión,
lo que falta y las propuestas nuevas. Este LEEME es el detalle técnico.

| Paso | Qué | Estado |
|---|---|---|
| 0 | Activos vectoriales limpios | ✅ hecho |
| 2 | Tipografía sustituta, elegida por medición | ✅ hecho — **Saira** |
| 1 | Tokens (paleta, edición, retirados) | ✅ hecho |
| 3a | Editorial: retícula y componentes | ✅ hecho |
| 3b | Redes: post, historia, carrusel, portada | ✅ hecho |
| 3c | Streaming: overlays, lower-thirds, placas | ✅ hecho |
| 3d | Patrocinadores: carta, dossier, deck, muro | ✅ hecho |
| 4 | `auditoria.py` — audita las PIEZAS contra los 8 frentes | ✅ hecho |
| 5 | PDF vectorial | ✅ hecho — `pdf.py`, 31 páginas con texto vivo |

### `PLAN.html` — el tablero

Se compone con el propio sistema: Saira incrustada en el fichero y sólo colores
de la paleta. `plan_fuentes.py` mete las 4 caras como data URI, y es idempotente
(se puede volver a correr cada vez que cambie el HTML).

```bash
python3 plan_fuentes.py   # reincrusta Saira en PLAN.html
```

⚠️ **Chrome headless no reproduce el layout estrecho con `--window-size`**: a
320 px renderiza a un ancho mayor y recorta la captura, así que la medida sale
falsa. Lo que sí funciona es **meter la página en un `<iframe width="320">`**
dentro de otro fichero y capturar eso: dentro del iframe el viewport es de
verdad 320 px y las media queries se evalúan contra él.

⚠️ **`--dump-dom` no ejecuta el JavaScript** en esta versión de Chrome: devuelve
el código fuente de la sonda, no su resultado. Para medir hay que hacerlo sobre
el píxel de la captura, o por CDP.

## Arquitectura

```
tokens/tokens.json     fuente de verdad
   └── build.py        genera css/py/yaml · `doctor` comprueba que es cierto
nucleo.py              Lienzo + componentes + instrumentación + el GRABADOR
   pdf.py              reproduce lo grabado en reportlab -> PDF vectorial
   ├── revista.py      Hoja   (8.5x11, unidad = pt)
   ├── redes.py        Pieza  (1080px, unidad = px)
   ├── streaming.py    Escena (1920x1080, unidad = px, lienzo con alfa)
   └── patrocinadores.py
          Pliego  (hereda de Hoja: misma retícula que la revista)
          Lamina  (1920x1080 para el deck)
```

**Los componentes viven en `nucleo.py`, no duplicados.** La píldora, el rayo, las
salpicaduras y las tarjetas son los mismos objetos en la revista y en redes: si
cambian en `tokens/`, cambian en los dos sitios a la vez.

```bash
python3 build.py          # genera tokens.css / tokens.py / tokens.yaml
python3 build.py doctor   # comprueba que lo declarado es CIERTO
```

---

## Paso 0 — de dónde salió cada cosa

La fuente de verdad es **`_fuente/hoja-de-marca-disenador.pdf`** (22-mar-2026),
que estaba enterrada dentro de
`02_P4F_Marketing-20260709T215816Z-2-001.zip` → `web/pitch 4 fun/logo pitch for fun .pdf`.

Es **vector puro**: 294 paths, 262 curvas, 0 imágenes. Los 10 SVG de `logo/`
salen de ahí recortando por región y normalizando el viewBox a la tinta real —
**no** de los PNG, que son rasterizaciones de segunda mano.

### Los 10 activos

| Archivo | pt | Fondo de uso |
|---|---|---|
| `p4f-lockup-color.svg` | 204.00 × 87.88 | claro |
| `p4f-lockup-ink.svg` | 204.04 × 87.96 | claro |
| `p4f-lockup-color-dark.svg` | 187.17 × 81.71 | oscuro |
| `p4f-lockup-blanco.svg` | 187.17 × 81.71 | oscuro |
| `p4f-isotipo-color.svg` | 59.29 × 86.75 | claro |
| `p4f-isotipo-ink.svg` | 59.29 × 86.75 | claro |
| `p4f-isotipo-blanco.svg` | 59.29 × 86.75 | oscuro |
| `p4f-appicon-azul.svg` | 61.29 × 61.17 | cualquiera |
| `p4f-appicon-verde.svg` | 61.29 × 61.29 | cualquiera |
| `p4f-appicon-ink.svg` | 61.29 × 61.29 | cualquiera |

Los 3 del isotipo se derivan del mismo recorte: `blanco` e `ink` son el `color`
recoloreado, así que **comparten geometría exacta**.

### Verificación hecha

- **Fidelidad**: cada SVG se rasterizó y se comparó contra el PDF original
  al mismo tamaño, sin remuestreo. Tras corregir un desplazamiento de 1–2 px a
  288 dpi (origen del viewBox), los píxeles distintos **fuera de bordes** son
  **0.00 – 0.26 %**. Las diferencias son antialiasing entre motores.
- **Color**: los 10 renderizan exactamente los colores del sistema, verificado
  contando píxeles opacos con ≥1 % de presencia.

---

## Trampas ya pagadas en este proyecto

- **`pdftocairo -png` ignora el CropBox** salvo que le pases `-cropbox`. Sin la
  bandera renderiza la página entera y cualquier comparación da 80 % de
  diferencia sin que haya nada roto.
- **`rsvg-convert` sin `-b` deja fondo transparente**; al pasar a RGB se vuelve
  negro y la comparación se dispara.
- **Los degradados no se recolorean tocando `fill`.** El verde del rayo vive en
  `stop-color="rgb(...)"` — con comillas, no con dos puntos. Una variante «mono»
  que solo cambie los `fill` sigue saliendo bicolor.
- **`<defs>` no es solo tipografía.** En los SVG de pdftocairo hay paths del
  dibujo dentro de `<defs>`; borrar el bloque entero para quitar el texto se
  llevó 17 de 23 paths del isotipo. Se quitan solo los `<use>`.
- **Los 4 lockups de la hoja no son la misma geometría escalada**: +8.4 % de
  ancho contra +6.9 % de alto, porque el tagline se compuso a mano en cada uno
  (Obvia 7.1 pt en los de arriba, 6.5 pt en los de la banda oscura).

---

## Paso 2 — la tipografía: **Saira** (SIL OFL)

`fuentes/` — 12 ficheros, 6 pesos × romana/itálica, 661 glifos cada uno,
`OFL-Saira.txt` incluido. Omnibus-Type. Libre: se puede empaquetar y entregar.

### Cómo se eligió

Obvia se extrajo del PDF (`_derivados/_tipo/obvia-subset.cff`) y se midió con
fontTools. Ese es el **objetivo**, no una impresión:

| Métrica | Obvia Bold Italic |
|---|---|
| ItalicAngle | **−12°** |
| cap / em | 0.684 |
| altura de x / cap | 0.782 |
| ancho de tinta H / cap | **0.696** — estrecha |
| ancho/alto de la O | **0.628** — ovalada |
| StdHW / StdVW | **1.099** — contraste **invertido** |

Se midieron con el mismo método las **314 familias del disco** (674 ficheros) y
8 candidatos OFL descargados. Distancia ponderada sobre 7 métricas:

| Fuente | Distancia | Nota |
|---|---|---|
| **Saira ExtraBold** | **0.567** | ✅ elegida |
| IBM Plex Sans Condensed Bold Italic | 0.646 | itálica real −11°, pero más ligera |
| Encode Sans Semi Condensed ExtraBold | 1.025 | |
| Poppins Black | 1.337 | ya instalada, demasiado ancha |
| Archivo ExtraBold | 1.367 | la de IAvanza, demasiado ancha |
| Arial Narrow / DIN Alternate / Avenir Next Condensed | 0.82–0.90 | ⛔ propietarias, descartadas |

**Las itálicas de Saira tienen ItalicAngle −12.0°, exactamente el de Obvia.**

### La sub-decisión que tomé, y se puede revertir

La **itálica real** de Saira queda métricamente más lejos (1.745) que la romana
inclinada 12° por software (0.567), porque la itálica de Saira está dibujada más
ancha. Aun así el sistema usa **la itálica real**: está dibujada y no
distorsionada, su ángulo ya es el correcto, y funciona en cualquier motor sin
transformación. El logo va aparte y en curvas, así que no depende de esto.

Si Piero prefiere que el texto rime más con el logo, se cambia a romana + oblicua
−12° tocando un token. Está medido en `_derivados/_tipo/ranking-final.json`.

---

## Lo que quedó fuera y por qué

- **Obvia no está instalada** y es comercial. El PDF la trae embebida pero **en
  subset** (`WHFMEF+Obvia-BoldItalic`): sirve para que el logo salga en curvas,
  no para componer texto nuevo. Sustituida por Saira — ver paso 2.
- **El sitio web no es fuente de nada.** Está desactualizado y se reconstruirá
  entero después de terminar el sistema (Piero, 15-ago-2026). Su `styles.css`
  (`#C5F97E`, `#111827`, Space Grotesk) y su `logo.svg` (Impact, `#009DFF` /
  `#9DFF00`, paths inventados) **no entran** en el sistema.

## Paso 1 — tokens

`tokens/tokens.json` es la **fuente de verdad**. `build.py` genera `tokens.css`,
`tokens.py` y `tokens.yaml`; los generados no se editan.

### Las reglas duras que salieron de medir, no de opinar

Contraste WCAG 2.1 sobre los hex reales:

| Combinación | Ratio | Veredicto |
|---|---|---|
| blanco / ink | 16.88 | libre |
| verde / ink · ink / verde | 8.68 | libre — es la combinación del acento |
| **ink / azul** | **5.28** | **la forma correcta de poner texto sobre azul** |
| blanco / azul | 3.20 | solo texto grande. Nunca cuerpo. |
| **verde / blanco** | **1.95** | **prohibido — el verde no se lee sobre claro** |
| verde / azul | 1.64 | prohibido |

La guía vieja ya decía «evita texto blanco pequeño sobre Electric Blue». Tenía
razón en eso: **3.20 no pasa AA**. Se equivocaba en la paleta, no en esa regla.

Los 6 neutros se derivan del ink en HSV (h=218°) para que toda la escala comparta
matiz. `gris-texto #5A6985` es el único que pasa AA como texto sobre claro (5.53).

### `edicion` — por qué está lleno de nulos

Van 2 ediciones al año y **ninguna plantilla hornea la fecha, la sede ni el
número**: los leen de `tokens.edicion`. Están en `null` a propósito: un dato de
edición que no tengo no se inventa. La plantilla que reciba un nulo debe marcarlo
visible, no dejarlo en blanco. Para una edición concreta se crea
`tokens/edicion.local.json` con solo las claves que cambian.

### `doctor` — probado en las dos direcciones

`python3 build.py doctor` no cree lo que dice el JSON: recalcula los contrastes,
mide los 10 SVG del logo con `rsvg-convert`, y abre cada `.ttf` para comprobar
peso y ángulo. **58 comprobaciones, 0 fallos.**

Y se comprobó que **sí detecta**: se le inyectaron **11 fallos** (contraste
mentido, AA falseado, medida de logo falsa, hoja A4 con pulgadas de Letter, caja
de texto que no cuadra, rol a color inexistente, fuente ausente, peso y ángulo
mentidos, color retirado revivido) y **cazó los 11**. La regla de colores
retirados se probó además **aislada**, colando `#111827` como neutro con su
contraste correcto para que ninguna otra regla pudiera saltar: la cazó.

---

## Paso 3a — el estilo de las hojas de la revista

`revista.py` — 5 tipos de hoja, ninguno con nada horneado: márgenes, línea base,
columnas, colores y tamaños salen de `tokens/`.

```bash
python3 revista.py muestra     # el pliego en _salida/
python3 revista.py reticula    # el mismo pliego con la retícula encima
```

### La retícula

| | |
|---|---|
| Hoja | 612 × 792 pt (8.5 × 11 in) |
| Márgenes | 60 sup · 60 inf · 54 ext · 54 int |
| Caja de texto | 504 × 672 pt |
| Línea base | 14 pt → **48 líneas exactas** |
| Columnas | **6 de 74 pt**, medianil 12 → 504 exactos |
| Columna de texto | 246 pt (3 columnas + su medianil) ≈ 40 caracteres |

Los márgenes no son redondos por gusto: son los únicos que hacen cuadrar las dos
cuadrículas a la vez. `build.py doctor` falla si alguien los toca.

### Los 5 tipos de hoja

`portada` · `apertura-seccion` · `lectura` · `datos` · `tarjetas`.

El **ritmo de color** alterna ink y blanco: portada, aperturas y datos en oscuro;
lectura y tarjetas en claro. Una revista de 24 pp entera en ink es cara de
imprimir y dura de leer de corrido.

Elementos fijos: kicker verde + sección en la cabecera, **filete que muere en la
columna 4** (no cruza la hoja), folio con barra verde, y marca de agua del
isotipo al 5 % sangrada por el lomo.

### Tres cosas que solo aparecieron al medir

1. **La itálica se sale por la izquierda.** La `A` de Saira Black a 68 pt tiene
   4.32 pt de bearing negativo: alinear el ORIGEN al margen deja la tinta fuera.
   Se arregla alineando la **tinta**, no el origen (`texto(..., optico=True)`).
2. **`anchor="la"` ancla el ascender, no la tinta.** Para `[TBD]` a 54 pt la
   tinta va de +21 a +70 pt del ancla. Calcular el salto con el ALTO de tinta
   (49 pt) daba 4 líneas donde hacían falta 6, y el texto siguiente se montaba
   encima. `lineas_de()` mide del ancla al fondo.
3. **El overflow y el solape son cosas distintas.** Las 5 hojas daban 0 de
   overflow y tenían 7 solapes: un texto encima de otro no se sale de la caja.
   Hay que buscarlo aparte.

### El lenguaje visual, absorbido de la referencia de Piero

Piero entregó una revista de 14 pp ya maquetada como referencia (15-ago-2026).
Está en `_fuente/referencia-revista/`, con su propio LEEME. Entraron al sistema
como **componentes generados**, no como recortes:

`cabecera_seccion()` · `pildora()` · `pie_claims()` · `rayo()` · `salpicadura()`
· `tarjeta()` · `logo_cabecera()`

Tres cosas que conviene saber:

- **La píldora está medida**: −6.17° en la referencia → el sistema usa −6° de
  banda y −12° de corte lateral (el ángulo de la itálica), para que el corte
  rime con el texto.
- **Las texturas no se pudieron extraer**: las páginas son PNG con todo horneado.
  El intento salió contaminado (el «rayo» traía el texto `04 / PROYECTOS`, el
  «splatter azul» era el público de una foto). Se generan.
- **El rayo sale del logo real**: aislado del isotipo por diferencia, 117.114 px.
  Usar el isotipo entero como decorativo se leía como logos gigantes repetidos.

⚠️ **El color de la referencia no es el del sistema.** Son PNG generados por IA y
el color deriva: verde `#A2DE33` (a 61.8 del sistema) y azul `#007FE9` (a 23.6).
Y la referencia es **A4** (0.7075) mientras el sistema es **Letter** (0.7727), así
que la maqueta se readaptó, no se copió página a página.

### Instrumentación

Cada hoja reporta, en pt:
- **overflow de contenido** — tinta fuera de la caja de texto.
- **overflow de página** — cabecera, folio y marca de agua viven en el margen por
  diseño, pero no pueden entrar en el sangrado de 9 pt.
- **solapes** — en dos familias: **texto/texto** y **texto/opaco** (logos e
  imágenes). El rayo y la marca de agua quedan fuera: son fondo y pueden ir
  debajo. La segunda familia se añadió porque en la portada el lockup tapaba la
  palabra «OFICIAL» y el detector de texto/texto no lo veía.

`revista.py muestra` sale con **código 1** si alguna hoja tiene algo. No entrega
en silencio.

Estado: **5 hojas, 0 overflow, 0 solapes**. Y probado en las dos direcciones —
5/5 inyecciones de overflow cazadas, y el detector de solapes verificado contra
el solape geométrico esperado en 5 separaciones distintas, marcando cuando toca y
callando cuando no.

⚠️ **Todavía es raster.** Se genera a 150 dpi con PIL, que es lo que permite medir
la tinta real. Para imprimir hace falta PDF vectorial con la fuente embebida;
`reportlab` no está instalado y Saira no está en el sistema. Se resuelve cuando el
estilo esté aprobado.

---

## Paso 3b — redes

`redes.py` — 8 piezas sobre 5 formatos, con los componentes del núcleo.

```bash
python3 redes.py muestra   # el juego en _salida/redes/
python3 redes.py zonas     # el mismo juego con la zona segura marcada
```

`convocatoria` (1080²) · `historia-anuncio` (1080×1920) · `experto` (1080×1350) ·
`cita` (1080², claro) · `carrusel` 3 láminas (1080×1350) · `portada-yt` (1280×720).

### La zona segura no es el margen

Es la franja que **la app tapa con su propia interfaz**. Instagram cubre unos
250 px arriba (avatar y barra) y 250 px abajo (campo de respuesta). Una historia
puede estar perfectamente maquetada, con 0 de overflow, y aun así tener el
titular debajo del avatar.

`Pieza` la mide aparte y la reporta. Probado en las dos direcciones: texto en la
franja de arriba → 91 px fuera; justo en el límite → 0; en zona útil → 0; en la
franja de abajo → 211 px fuera. **4/4.**

### La migración al núcleo, verificada

Al extraer los componentes de `revista.py` a `nucleo.py` las 5 hojas tenían que
salir **idénticas**. No salieron: 0.29 % de píxeles distintos. Dos causas, las
dos mías:

1. Metí un factor `max(1, U/2)` en el radio de las motas. `radio_px` ya está
   declarado en píxeles y no debe escalar con la unidad del lienzo.
2. Cambié la píldora de leer `alto_pt`/`padding_x_pt` de los tokens a derivarlos
   del tamaño de texto. Desplazaba 1 px y movía toda la banda.

Corregidas las dos, la comparación da **0.0000 % en las 5 hojas**. Si no llego a
comparar píxel a píxel, el sistema se queda con dos píldoras que no encajan.

---

## Paso 3c — streaming

`streaming.py` — 6 piezas, todas 1920×1080.

```bash
python3 streaming.py muestra   # el juego en _salida/streaming/
python3 streaming.py zonas     # previsualización sobre damero, con las 3 zonas
```

`overlay-escena` · `lower-third-pitcher` · `lower-third-experto` ·
`placa-ganador` · `cuenta-regresiva` · `marco-qr`.

### El lienzo tiene alfa

Un overlay va **sobre video**: se arrastra a OBS o a StreamYard tal cual. Lo que
no es placa queda transparente. `Lienzo` acepta `fondo="transparente"` y crea
RGBA en vez de RGB.

⚠️ **Sobre RGBA hay que COMPONER, no pegar.** `paste` con máscara mezcla contra
el RGB del destino, que en un lienzo vacío es negro: los bordes suavizados del
logo salen sucios y una marca de agua al 18 % se ennegrece. Por eso existe
`Lienzo._pegar()`, y lo usan `opaco`, `rayo` y `pildora`.

Medido: el overlay ocupa **19,4 %** del lienzo y el resto es alfa 0; el píxel
central de las cuatro piezas con alfa mide 0. Un overlay que sale opaco tapa el
directo entero y no se nota hasta que está en el aire.

### La zona segura de broadcast son tres, no una

| Zona | Margen | Qué es |
|---|---|---|
| **Título** | 96 × 54 px (5 %) | lo que un televisor puede recortar. Aquí no va texto. |
| **Acción** | 67 × 38 px (3,5 %) | el límite de cualquier gráfico. |
| **Barra del reproductor** | 90 px abajo | lo que YouTube tapa con sus controles al mover el ratón. |

**El margen de composición ES la zona de título**, no un margen aparte: en
broadcast no tiene sentido ser más generoso que lo que no se recorta. Abajo manda
la barra del reproductor, que es mayor. El `doctor` falla si alguien los separa.

Probado en las dos direcciones: texto a y=20 → 9 px fuera (mide la TINTA, no el
ancla); a y=54 justo en el límite → 0; en el centro → 0; a y=1040 → 78 px fuera
de título y 114 bajo la barra; placa desbordando por la derecha → 308 px. **6/6.**

⚠️ **Una barra de 104 px dejaba su propio texto fuera de la zona segura**: el eje
caía en y=52 y el límite de título es 54. La barra subió a 132 px con el
contenido centrado en y=80. Un componente puede sangrar; su texto, no.

⚠️ **El corte diagonal no escala a cualquier altura.** Está calibrado para los
152 px del lower-third (sesgo de 32 px). En la tarjeta del QR, de 322 px, el
mismo ángulo daba 68 px y se comía la esquina: esa pieza usa `tarjeta()`, que es
el componente correcto para un bloque alto.

### El QR no se inventa

`edicion.registro_url` está en nulo y no hay librería de QR instalada. La pieza
lleva el **hueco marcado**, igual que el temporizador de la cuenta regresiva: ese
número lo repone el software de stream, no la plantilla.

### El doctor creció con streaming

De 68 a **213 comprobaciones**. Las nuevas: la zona segura tiene que ser el
porcentaje que declara, todas las piezas miden lo que dice el formato, el margen
coincide con la zona de título y no cabe bajo la barra, y **ningún componente
nombra un rol o un color que no exista** — esa última recorre los 9 componentes
enteros. Probado con 10 fallos inyectados: **10 cazados, 0 escapan**.

---

## Paso 3d — patrocinadores

`patrocinadores.py` — 12 piezas: **carta** (1 hoja) · **dossier** (5 hojas) ·
**deck** (5 láminas 1920×1080) · **muro de aliados** (1 hoja).

```bash
python3 patrocinadores.py muestra    # el juego en _salida/patrocinadores/
python3 patrocinadores.py reticula   # las hojas con la retícula encima
```

Las hojas heredan de `revista.Hoja`: misma retícula de 6 columnas, misma línea
base de 14 pt. Un dossier que no alinea con la revista delata que son dos
sistemas y no uno.

### Aquí no hay ni un número

Este es el módulo que acaba en una mesa ajena. Nombres de nivel, montos, moneda,
cupos y cifras de alcance viven en `tokens.patrocinio` **en nulo** — 12 campos de
12 sin decidir — y salen marcados. El `doctor` falla si alguien rellena un monto
sin que `meta.decisiones_cerradas` registre una decisión de PATROCINIO.

Los **beneficios sí son ciertos**: los siete corresponden a piezas que el sistema
ya produce y que están medidas. El doctor comprueba que el módulo que dice
producir cada uno existe.

### El hallazgo del módulo: el sistema incumplía su propia regla

`tokens.json` declara desde el paso 1 que **el verde sobre blanco da 1.95 y está
PROHIBIDO como texto**. Las plantillas lo usaban igual — en la revista, en redes
y aquí. El `doctor` validaba los tokens; nadie validaba las piezas.

`Lienzo.texto()` mide ahora el contraste de cada texto contra el fondo **real**
bajo su caja, leído del lienzo antes de escribir. No contra `self.bg`: el fondo
puede ser una tarjeta `ink-2` o una píldora verde, y suponerlo es justo el error.

Encontró **50 textos** repartidos por los cuatro módulos:

| Combinación | Ratio | Dónde estaba |
|---|---|---|
| verde sobre blanco | 1.95 | todos los `[TBD]`, números de sección, claims del pie |
| gris-texto sobre ink | 3.05 | etiquetas de la ficha de edición, en 3 módulos |
| azul sobre blanco pequeño | 3.20 | kickers de bloque, «ASK» de las tarjetas |
| blanco sobre azul | 3.20 | el número de las tarjetas de proyecto |
| ink-3 sobre ink | 1.50 | la barra `/` de la cabecera de sección |

Dos piezas nuevas del núcleo lo resuelven **por construcción**, no caso a caso:

- **`Lienzo.color_acento(grande)`** — el acento que sí se lee sobre este fondo.
  Sobre ink es el verde; sobre claro es el azul si el texto es grande y el gris
  de texto si es pequeño.
- **`Lienzo.pendiente()`** — el marcador de dato que falta. Mantiene el código de
  color, pero sobre claro el verde pasa de tinta a **pastilla**, con el texto en
  ink encima (8.68). Es lo que se ve en los `[TBD]` de la carta y del dossier.

⚠️ **«Texto grande» hay que traducirlo a cada lienzo.** En hoja la unidad es el
punto y el umbral de WCAG es directo (18 pt en negrita). En un lienzo de píxeles
no hay puntos: el umbral es el 6 % del ancho, que en 1080 son 65 px. Un primer
umbral por altura de tinta relativa marcaba como «pequeño» un número a 34 pt.

⚠️ **`pendiente()` tuvo que aceptar `optico`.** Al sustituir las llamadas a
`texto(..., optico=True)` se perdió el alineado óptico y la itálica volvió a
salirse 1 px por la izquierda — la trampa del paso 3a, otra vez.

Probado en las dos direcciones: **10 casos, 10 correctos**, incluido un texto
sobre una tarjeta `ink-2` dentro de una hoja blanca, que mide 2.81 contra la
tarjeta y no contra el blanco de la página.

Estado tras el arreglo: **31 piezas, 0 overflow, 0 solapes, 0 contrastes que no
pasan** en los cuatro módulos.

---

## Decisiones de Piero del 15-ago-2026 (segunda tanda)

| Qué | Decisión | Dónde vive |
|---|---|---|
| Formato del pitch | **8 proyectos, 3 minutos**. La 1.ª edición fueron 5 min | `tokens.evento` |
| Nombres | **Muuving · Vixual · Eco Ernesto Visita · MelizAI** | `tokens.proyectos` |
| Cifras | las de la revista de referencia son buenas | `tokens.metricas` |
| Co-marca | los 3 logos NO van siempre; a los ejecutores se los nombra | `tokens.organizadores.regla` |
| Saira | instalada — 12 caras en `~/Library/Fonts` | — |

Ni «3+3 min» ni «10 láminas × 30 s»: **las dos guías anteriores estaban mal**.
El dato sale ahora en la convocatoria, el dossier, el deck y la barra del overlay.

⚠️ Las cifras se marcan en tokens con **su origen real**: vienen de la revista de
referencia y las confirma Piero, no una analítica. Las que él no nombró
—asistentes en vivo y alcance del directo— siguen saliendo marcadas.

Con 4 proyectos por hoja las tarjetas caben sin apretar (medido), lo que responde
de hecho a la duda de 3 contra 4: `tarjeta_proyecto.por_pagina` pasa a 4.

### La píldora: el texto no viajaba con la banda

Piero mandó una captura del claim `MENOS SHOW. MÁS EJECUCIÓN.` porque no se veía
bien. Medido: la banda se inclinaba −6° y **el texto se quedaba horizontal**. En
un claim corto no se nota; en ese, el borde subía 57 px de un extremo a otro y
**130 columnas de tinta —el 28 %— quedaban pegadas al filo o fuera**, con hasta
−21 px de holgura.

Ahora el texto se compone DENTRO de la banda recta y se inclina todo junto.
Medido sobre 6 claims de 191 a 789 columnas: **holgura mínima 14–18 px arriba y
abajo, 0 columnas pegadas**.

⚠️ Ningún control lo veía: no era overflow (cabía en la caja), no era solape (no
había otro texto) y no era contraste (ink sobre verde da 8.68). Lo vio Piero.

---

## Paso 5 — el PDF vectorial

```bash
python3 pdf.py             # los 4 módulos a _salida/pdf/
python3 pdf.py revista     # solo uno
```

**No hay un segundo motor de maquetación.** Cada pieza se construye una sola vez
con PIL —que es lo que permite medir la tinta real, los solapes y el contraste— y
por el camino `_Trazo`, un proxy sobre `ImageDraw`, va **apuntando cada operación
de dibujo**. `pdf.py` reproduce esa lista en reportlab. Un motor, dos salidas.

| Elemento | En el PDF | Por qué |
|---|---|---|
| Texto | **vivo**, Saira embebida | es lo que pide una imprenta |
| Filetes, tarjetas, cajas | **vector** | son formas, no píxeles |
| Píldora inclinada | **vector**, se rota el sistema de coordenadas | el claim sigue siendo texto |
| Logos | **vector**, desde el SVG (svglib) | un logo rasterizado en imprenta, no |
| Rayo y salpicaduras | imagen a 300 dpi | son texturas; vectorizarlas no aporta |
| Marca de agua | imagen | lleva opacidad |

Estado: **31 páginas · 438 textos vivos · 159 formas · 28 SVG · 12 píldoras
vectoriales · 0 caracteres rotos · todas las fuentes embebidas.**

### Cuatro cosas que solo aparecieron al medir

**1. PIL redondea los avances a píxel; un PDF, no.** La diferencia media es del
0,34 %, pero en una palabra corta llega al **6 %** — y eso bastó para que una
línea del dossier que cabía en el PNG se saliera 1 px de la caja en el PDF.
`envolver()` mide ahora con **los dos motores** y manda el más ancho. Antes: 1 de
419 textos se salía solo en el PDF. Después: 0.

**2. Lo que se pinta en una capa temporal no pasa por el grabador.** La placa del
lower-third se componía en un `Image.new` aparte: en el PNG estaba y en el PDF
faltaba entera, con el texto flotando sobre nada. Se dibuja directo sobre el
lienzo.

**3. Los recursos de fuente se COMPARTEN entre páginas.** Al quitar las fuentes
huérfanas —reportlab declara Helvetica y svglib Times-Roman, y ninguna escribe un
carácter, pero quedan listadas y sin embeber— la primera versión borraba según lo
que usaba *una* página y se llevaba por delante las de las demás. Y la detección
fallaba además porque **reportlab escribe con cadenas HEXADECIMALES** (`<0044…>
Tj`) cuando la TrueType va subsetada, no con `(texto) Tj`. Resultado: Saira
Regular desaparecía y el cuerpo de la revista salía en cuadraditos.
La limpieza **se verifica sola**: compara el texto extraíble antes y después y se
deshace si cambia. Esa red es la que cazó el fallo.

**4. Comparar un PNG con alfa contra un PDF da 99 % de diferencia** sin que nada
esté roto: el PNG transparente se vuelve negro al pasar a RGB y el PDF tiene
fondo blanco. Hay que componer los dos sobre el mismo fondo. Ya pasaba con
`rsvg-convert` en el paso 0; es la misma trampa con otra ropa.

Comparado con el PNG, página a página: **media 2,02 %, peor 4,34 %** de píxeles
distintos. Toda la diferencia es tipográfica y va a favor del PDF: sus avances
son los de la fuente, sin redondear.

⚠️ El PDF de **streaming** existe por consistencia, pero los overlays se entregan
en **PNG con alfa**: eso es lo que carga OBS.

---

## Tanda A — superficies y color (16-ago-2026)

Salió de las **15 referencias** que entregó Piero el 15-ago: 8 páginas de revista
y 7 assets. Están en `_fuente/referencia-revista/`.

Lo que se midió sobre ellas:

| hallazgo | número |
|---|---|
| fondos oscuros circulando | **3**: `#0A1628` (declarado), `#121D2F` (assets), `#000714` (páginas) |
| acentos reales | 195° y 75°, que son el azul y el verde de marca — la marca es coherente |
| color sin declarar | familia 210–225° (`#063780`) en las 8 páginas y en 5 de los 7 assets |
| superficie clara | `#E6F7FE` — ahí azul 2.91 y verde 1.77: **ninguno pasa** |

**Decisiones de Piero:** manda `#000714`; `#E6F7FE` entra como superficie
decorativa con el texto siempre en ink; `#063780` entra como superficie
secundaria; y los tres colores de apoyo de la guía v2 se retiran en firme.

### `color.superficies` y las tres listas

Cada superficie clasifica **las 10 tintas** del sistema en `tinta_permitida`
(≥4.5), `tinta_solo_grande` (3.0–4.5) y `tinta_prohibida` (<3.0). Las tres listas
son exhaustivas y el doctor las recalcula una por una, **en las dos direcciones**:
declarar permitida una tinta que no llega es un fallo, y declarar prohibida una
que sí se lee, también. Lo segundo no rompe una pieza, pero hace que la
documentación mienta, que es como vuelven los errores.

### El booleano `oscura` era una bomba de relojería

El núcleo elegía la tinta con `fondo in ("ink","ink-2","ink-3")`. Una lista de
nombres: cada superficie nueva obligaba a acordarse de añadirla en cinco sitios,
y olvidarse **no da error**, da texto ilegible. Ahora `_elegir()` recorre la
prioridad de marca y devuelve el primero que se lee sobre el fondo real. Sobre
`claro-rayo` el sistema cae solo al gris porque ni verde ni azul pasan; nadie
tuvo que escribir esa regla.

### Trampas de esta tanda

- **`self.avisos = []` se inicializaba DESPUÉS de las llamadas a `_elegir`** del
  constructor. Si un fondo no hubiera admitido ninguna tinta, el sistema habría
  lanzado `AttributeError` en vez de decir cuál era el problema.
- **El primer caso de prueba del aviso estaba mal, no el código**: sobre
  `#8A8A8A` el ink llega a 4.86 y `_elegir` acertaba. La banda donde de verdad no
  pasa ninguno es estrecha: `#7E7E7E` (blanco 4.06 · ink 4.16).
- **`ink-3` sobre `azul-profundo` da 1.00** — el mismo valor de luminancia. Una
  tarjeta ahí es invisible sin filete, y nada la marcaría como fallo: no se sale
  de la caja, no pisa nada y su texto se lee. Simplemente no hay tarjeta. Por eso
  `tarjeta()` y `hueco()` eligen el borde midiendo.
- **Colisión de nombres**: `streaming.py` ya tenía un método `suelo()` y el
  atributo nuevo lo tapaba. Ahora es `fondo_real`.

---

## Tanda B — iconografía (16-ago-2026)

**26 iconos**, todos sacados de las 8 páginas de referencia. Ninguno se inventa:
un icono que nadie usa es peso muerto que además hay que mantener coherente.

No son 26 ficheros escritos a mano. Los produce `iconos.py` desde una sola
definición, que es lo que garantiza que compartan caja (24), grosor (2) y remate
(redondo). Con 26 SVG sueltos el grosor se va de uno en uno y nadie lo nota hasta
que hay dos juntos.

### Cómo se tinta

El fichero del sistema lleva `@COLOR@` como marcador y **no se puede pintar tal
cual**. `nucleo.icono()` sustituye el color y cachea el resultado en
`_derivados/iconos/`. La caché va **en disco, no en memoria**: `pdf.py` reproduce
las operaciones apuntadas y necesita abrir el fichero para sacar el vector. Un
icono que solo existiera en RAM llegaría al PDF como imagen.

Verificado: una pieza con los 26 da **396 trazados vectoriales y 0 imágenes**, y
pesa menos de la mitad que su PNG.

### El mínimo son 16 px, y está medido

Se rasterizaron los 26 a 12/14/16/18/20/24/28/32/48 px contando píxeles con alfa
pleno. A 12 px hay **6 iconos sin un solo píxel sólido** y a 14 px quedan 3; a 16
ninguno. Por debajo de 16 el trazo es todo antialias y el icono se lee gris, no
del color que se le pidió. El recomendado es 20 px: a 16 el peor icono tiene el
8 % de su tinta en alfa pleno, a 20 sube al 24 %.

### La trampa de las fuentes huérfanas, segunda parte

Ya estaba en los 4 PDF entregados el 15-ago y **no la vio la verificación que
existía justamente para eso**.

`_limpiar_fuentes()` borra del diccionario las fuentes que reportlab y svglib
declaran sin usar. Lo que no hacía era borrar del flujo el `Tf` que las nombraba.
Resultado: el PDF referenciaba `/F1` y `/F2` sin declararlos, y un preflight lee
«Unknown font tag» y para la producción.

La verificación comparaba **texto extraíble**, que sale idéntico — el texto se
pintaba bien con las fuentes que sí quedaban. Miraba justo lo que no había que
mirar. Ahora comprueba además que **ningún tag nombrado en un `Tf` quede sin
declarar**, y si algo falla revierte el fichero entero.

Dos cosas más que salieron al arreglarlo:

- Tocar el flujo de una página que aún cuelga del *reader* deja el resultado
  **sin comprimir** (la revista pasó de 336 a 491 KB) y pypdf avisa de que ese
  camino no es fiable. Hay que clonar en el writer y comprimir al salir.
- **`pdftocairo` renderiza sobre blanco**: comparar un PDF con piezas de alfa
  contra sus PNG daba 95 % de diferencia sin que nada estuviera roto. Es la
  trampa del alfa otra vez, pero por el otro lado — la primera vez fue el PNG.
  Hace falta `-transp` y componer los dos sobre el mismo suelo.

---

## Tanda C — los 9 componentes de contenido (16-ago-2026)

`metrica` · `ficha_persona` · `chip` · `paso` · `credito` · `celda_logo` ·
`bloque_cita` · `hueco_logo` · `mosaico`. Todos en `nucleo.py`, todos con tokens
y todos con regla en el doctor.

Declaran sus medidas como **proporción de su caja**, nunca en pt ni en px: es lo
que permite que el mismo componente sirva en una hoja de 612 pt y en un lienzo de
1080 px. Duplicar las medidas por formato es cómo se desincronizan.

### El agujero que abrió esta tanda: el desborde de componente

El control de overflow mide contra **el margen de la página**. Un componente
puede reventar su propia caja e invadir al vecino sin que nada chille, porque la
página sigue estando bien. Pasó en la primera lámina y se veía a simple vista:

| componente | texto | se salía |
|---|---|---|
| `metrica «IAVANZA»` | `+1,400` | 23,60 px |
| `ficha «PIERO GÓMEZ»` | `PIERO GÓMEZ` | 12,75 px |
| `ficha «ALICIA TARRAZO»` | `ALICIA TARRAZO` | 69,75 px |

Ahora cada componente abre y cierra su caja (`_abre` / `_cierra`) y el informe
tiene una columna propia, `des`. Y para que no vuelva a pasar:

- **`fuente_que_quepa()`** — una cifra o un nombre no se pueden envolver ni
  cortar: o encogen o se salen. Baja hasta el 55 % del tamaño pedido; por debajo
  de ahí deja de ser el mismo elemento y prefiero que salte el control.
- **`_parrafo()`** — corta con **puntos suspensivos**. Cortar en seco dejaba
  frases a medias («Dos veces al año, sin») y eso se lee como un fallo de datos,
  no como un recorte.

### Solapes: hacía falta el orden de dibujo

El número dentro de la flecha de `paso` salía como solape texto/opaco. No lo es:
es texto **sobre una placa**, igual que la píldora o el lower-third. El detector
no podía distinguirlo porque no sabía qué se pintó antes. Ahora las cajas guardan
su orden y la regla es: *texto entero dentro de una forma anterior* = placa.
Comprobado en los cuatro casos —

| caso | esperado | da |
|---|---|---|
| texto sobre placa dibujada antes | 0 | 0 |
| imagen encima de un texto previo | 1 | 1 |
| texto que se sale de su placa | 1 | 1 |
| texto sobre texto | 1 | 1 |

### Trampas de esta tanda

- **El acento del marco y el del texto no son el mismo.** Un marco es forma y le
  vale 3.0; su etiqueta es texto y exige 4.5. `hueco_logo` usaba el mismo color
  para los dos y dejaba «TU LOGO AQUÍ» en azul sobre blanco a **3.20**. Lo cazó
  el control de contraste, no el ojo.
- **La elipsis borraba con el color equivocado.** Repintar la línea recortada con
  el fondo de la *pieza* deja una barra de otro color cuando el componente está
  dentro de una tarjeta (`ink-2`). Hay que leer el color que hay debajo.
- **Los componentes calculan en proporción y llegan con floats**; `paste` solo
  admite enteros. Se redondea en `svg()`, que es el punto común, no en cada
  llamada.

### Dónde están puestos ya

- `revista.datos()` — seis `metrica`, una por cifra
- `revista.tarjetas()` — tres `chip` de estado por proyecto
- `patrocinadores.muro_aliados()` — nueve `celda_logo` y **tres `hueco_logo`**:
  la celda vacía y el sitio que se está vendiendo son cosas distintas y ahora se
  ven distintas

---

## Tanda D — gráficos y normalización (16-ago-2026)

### Lo primero que apareció: el PDF perdía operaciones en silencio

Antes de dibujar nada hubo que auditar qué sabe reproducir `pdf.py`. El grabador
apunta **10** operaciones de dibujo y el reproductor solo despachaba **6**; las
demás **se ignoraban sin decir nada**.

No era teórico: las 32 piezas usaban **16 `arc`** —las esquinas redondeadas de
los huecos punteados del muro de aliados— y ninguna llegaba al PDF. La pieza no
fallaba; solo le faltaba un trozo, que es peor que reventar.

Arreglado en dos partes: se añadieron `arc`, `pieslice`, `chord` y `point`, y
sobre todo **el reproductor ahora avisa a gritos** de cualquier operación que no
sepa reproducir en vez de saltársela.

Detalle del arco: PIL y reportlab miden los dos desde las 3 en punto, pero con el
eje Y invertido — PIL va horario y reportlab antihorario. Un ángulo θ de PIL es
−θ allí, así que el arranque es `−fin` y la amplitud `fin − inicio`.

### Los 3 gráficos

`grafico_barras` · `grafico_dona` · `mapa`. Reglas duras:

- **El eje de las barras empieza en cero.** Un eje truncado exagera la diferencia
  y es la forma más fácil de publicar un gráfico que miente sin decir una sola
  cifra falsa.
- **Un gráfico no inventa datos.** Un valor a `None` sale como hueco punteado con
  `[TBD]`, igual que cualquier otro dato sin confirmar.
- **La dona se dibuja como sector relleno + hueco**, no como arco grueso: el
  trazo se centra en la elipse en un motor y se mete hacia dentro en el otro, y
  la dona salía de distinto grosor en el PNG y en el PDF.

### El mapa NO se dibujó a mano

Está vectorizado con `potrace` desde `P4F_03_mapa_oscuro.jpg`, que es el asset
que entregó Piero: 12.445 píxeles de trazo verde (el 2,04 % de la imagen) →
45 paths. Un mapa dibujado a ojo sale publicado con la geografía mal.

Sus pines van en coordenadas **relativas al viewBox (0–1)**, no en lat/lon: el
trazo es una referencia, no una proyección declarada, y aceptar coordenadas
geográficas sería mentir sobre su precisión.

### `valor_numerico()` — el «+» es parte del dato

Varias métricas son cadenas y así se imprimen: `+80`, `+1.400`, `+20K`. El «+»
significa «al menos» y el punto es separador de millar. Los gráficos muestran la
cadena tal cual y solo derivan el número para la altura de la barra. Convertirlas
a entero en los tokens perdería el «+».

### La cabecera de sección: 4 formas → 1

En las 8 páginas de referencia conviven cuatro cabeceras distintas. Cuatro
cabeceras en catorce páginas es lo que hace que una revista parezca cuatro
revistas. El código ya usaba una sola en sus 9 sitios; lo que faltaba era
**declararlo**, con las otras cuatro registradas y su motivo:

| variante retirada | por qué |
|---|---|
| `/ 08 / ORGANIZADORES` | dos separadores para un número; el de la izquierda no separa nada |
| `04 / Proyectos — Edición Virtual (2/2)` | mezcla versalitas y caja baja, y mete la paginación dentro del título |
| `01 / RESUMEN DEL EVENTO` | el título al tamaño del subtítulo: se pierde la jerarquía |
| `06 /` + `QUÉ SIGUE` debajo | rompe la línea base y descuadra la retícula |

### Dónde están puestos ya

`revista.datos()` monta los tres gráficos con los datos de `metricas`, incluido
`proyectos_edicion_1/2 = 6/6` — que suman los 12 del total declarado, y esa suma
es lo que comprueba el doctor.

---

## Paso 4 — `auditoria.py`, la auditoría de las PIEZAS (16-ago-2026)

```
python3 auditoria.py          audita las 31 piezas y los 4 PDF
python3 auditoria.py probar   inyecta un fallo por regla y comprueba que salta
```

**Esto NO es `build.py doctor`.** La diferencia es la razón de existir del módulo:

| | comprueba |
|---|---|
| `build.py doctor` | que **tokens.json dice la verdad** — 211 comprobaciones |
| `auditoria.py` | que **las piezas cumplen lo que tokens.json manda** — 26 reglas |

El agujero era exactamente ese hueco. `tokens.json` declaraba desde el paso 1 que
el verde sobre blanco (1.95) está PROHIBIDO como texto, el doctor lo verificaba
tan contento, y las plantillas lo usaban en 50 sitios. **Nadie auditaba las
piezas.**

### Los 8 frentes, y el que no aplica

El frente 5 (estado remoto y despliegue) **no aplica**: el sistema es un
generador local, no publica, no sube y no llama a ninguna API. Se declara en el
informe en vez de callarlo, porque «limpio» y «no revisado» se imprimen igual.

### Cuatro falsos positivos MÍOS, y lo que enseñaron

La primera corrida dio 19 bloqueantes. **Trece eran defectos del auditor, no del
sistema.** Cada uno dejó una regla mejor:

1. **`#121D2F` está a distancia 1.0 del ink vivo** (`#121D30`). Buscar hex
   exactos en píxeles lo encuentra siempre: un píxel de antialias del ink *es*
   ese color. Y un degradado entre dos colores vivos pasa por tonos intermedios
   que coinciden con retirados cercanos — en la portada había **1 píxel** de
   `#0A1628` y **10** de `#121D2F`. Eso no es uso, es azar.
   → La regla ahora exige **área mínima (0,10 %)** y solo se aplica a los
   retirados a más de 20 de distancia de la paleta viva. Los otros cuatro se
   **declaran como no auditables por píxeles**, que es la respuesta honesta.
2. **«3 minutos» daba «3 m»** y no cuadraba con el «3» declarado en
   `evento.formato_vigente`. El regex arrastraba la unidad. Y **«2026» es un año**,
   no una cifra de resultado.
3. **12 métricas «sin origen» que sí lo tienen**: está declarado a nivel de
   sección (`_origen: "revista de referencia de 14 pp, confirmada por Piero"`),
   no métrica por métrica. Exigir nota individual cuando la sección ya lo dice
   era mi error.
4. **El auditor se auditaba a sí mismo.** Con regex, `f.write("open('_fuente/…','w')")`
   se lee como una escritura real: es una **cadena** dentro de una llamada. El
   frente 8 pasó a **AST**, y sus casos de prueba se crean fuera del sistema.
   Además, `os.remove(png)` en `build.py` **sí** es un temporal aunque la
   variable no se llame `tmp`: ahora se rastrea de dónde viene el valor
   (`tempfile.mktemp`), no cómo se llama.

### Los 2 hallazgos reales

**Las plantillas recortaban claims que Piero cerró.** Decían «FEEDBACK REAL.» y
«TU ASK, CLARO.» cuando lo aprobado es «FEEDBACK REAL. **CONEXIONES REALES.**» y
«TU ASK, CLARO **Y ACCIONABLE.**». Medido: los completos **caben de sobra** (651
y 531 px de 936 disponibles), así que el recorte no tenía justificación técnica —
fue una decisión al programar la plantilla, no de Piero. Restaurarlos no es
decidir: es dejar de decidir.

Y restaurarlos destapó **dos fallos más**:

- **La píldora anclada por arriba se sale por abajo.** Al inclinar la banda −6°,
  su alto crece con el ANCHO del texto (`w·sinθ + h·cosθ`): la de «cita» se salió
  34 px y la del carrusel 16. Ahora `pildora()` acepta `ancla="ba"` y se resta la
  altura **real** de la banda rotada — la fórmula analítica se quedaba 1–2 px
  corta, y 2 px es un desborde igual de real.
- **Las 12 píldoras estaban mal colocadas en el PDF desde el paso 5.** PIL pega
  la capa **ya rotada** en (x, y) —ahí queda su techo— y reportlab traslada el
  origen y rota después, así que ahí queda el techo de la banda **sin** rotar. El
  desfase es `rot_h − h` y **crece con el largo del claim**: 19 px con uno corto,
  67 con el completo. Con claims cortos nunca se notó.
  Medido con una banda en posición conocida: el suelo del PDF salía **constante**
  con dos claims de distinto largo, cuando el que debe ser constante es el suelo
  en `y + rot_h`. Corregido, el desfase es de 1 px y ya no depende del texto.
  → Nació de aquí la regla **`pdf-igual-que-png`**: el PDF tiene que *dibujar* lo
  mismo que el PNG, no solo existir. La media bajó de 1,79 % a **1,24 %**.

### Los 14 logos bajo el mínimo — cerrado por Piero (16-ago-2026)

`logo.minimos.lockup_px = 120` estaba declarado desde el paso 1 y **no lo leía
nadie**: era un token decorativo. Medido sobre los 28 lockups que pegan las 31
piezas, **14 estaban por debajo** — deck 101 px, redes 106, streaming 115.

Piero decidió subir los logos, no bajar el mínimo. No se tocaron 14 literales:

- **`nucleo.alto_minimo_logo(ruta)`** deriva el alto que hay que pedirle a rsvg
  desde el ancho mínimo y la proporción real del fichero. Da 53 px para
  `lockup-blanco` y 52 para `lockup-ink`, porque no comparten geometría (el
  tagline se compuso a mano en cada uno, +8,4 % de ancho contra +6,9 % de alto).
- **`Lienzo.logo()` lo respeta por defecto.** Si una llamada quiere bajar del
  mínimo tiene que pedirlo con `permitir_bajo_minimo=True`, y queda en los avisos.
- **El alto de streaming era un token** (`barra_escena.logo_alto_px`), así que se
  corrigió ahí, con su origen declarado.

Dos guardias nuevos, los dos probados con inyección:

| dónde | qué comprueba |
|---|---|
| `build.py` regla 26 | que el mínimo declarado sea **alcanzable**: que exista un alto entero de rasterizado que lo dé. Un mínimo imposible de cumplir haría que las piezas lo incumplieran para siempre |
| `auditoria.py` `logo-sobre-el-minimo` | que **ningún logo pegado** baje del mínimo. Bloqueante |

Resultado: **28 de 28 por encima** (121–498 px), y ninguna pieza gana desborde ni
solape con el logo mayor.

### La prueba en las dos direcciones

`python3 auditoria.py probar` inyecta un fallo por regla: **17 de 17 saltan**, y
sin inyectar nada el sistema queda en silencio. Una regla que nunca se ha visto
fallar no es una regla, es una decoración — y silenciarla se ve exactamente igual
que arreglarla.

---

## Trampas de descarga de fuentes

- La API de Google Fonts sirve **formatos distintos según el User-Agent**. Con UA
  de IE6 devuelve **EOT**; con Safari 5 o Firefox 6, **WOFF**. Solo un UA viejo
  de Android (`Mozilla/5.0 (Linux; U; Android 2.3.7; en-us) AppleWebKit/533.1`)
  devuelve **TTF**.
- Las URLs de `fonts.gstatic.com` **no terminan en `.ttf`** — un grep por
  extensión no encuentra nada aunque la descarga funcione.
- `css2?family=X:ital,wght@1,800` da la itálica; `css?family=X:800italic`
  también, pero conviene comprobar `name` y `OS/2` del fichero: el romano de
  Saira se identifica a sí mismo como «Saira Thin ExtraBold».

---

## Prototipo — la revista de 24 pp con datos simulados (17-ago-2026)

`prototipo.py` compone una revista **completa y llena**, con contenido inventado,
para ver cómo se comporta el sistema cuando hay 24 páginas de corrido. No
sustituye a `revista.py`, que sigue siendo el muestrario honesto que marca en
verde lo que nadie ha confirmado.

    python3 prototipo.py            24 hojas en _salida/prototipo/
    python3 prototipo.py pdf        además el PDF de las 24
    python3 prototipo.py sin-sello  sin la banda de aviso

**Todo lo inventado vive en un solo sitio**, el dict `SIMULADO`. Nada de datos
falsos escondidos dentro de una función: si algún día hay datos reales se
sustituye ese bloque y no se toca nada más.

Cómo se marca que es simulación, en cuatro capas — decidido por Piero el
17-ago-2026 entre tres opciones:

1. Banda **«PROTOTIPO · DATOS SIMULADOS · NO PUBLICABLE»** en las 24 páginas, en
   el aire entre el borde y la cabecera. Una captura de una página interior no se
   puede confundir con material publicable.
2. La **p.02 es un aviso a toda página** con dos listas: lo que sí es real (la
   retícula, la paleta, la tipografía, los componentes, el logo, las medidas) y lo
   que está inventado.
3. Cada nombre ficticio lleva **asterisco** y cada página que lo usa imprime al
   pie qué significa. `verificar()` comprueba que no haya asterisco sin explicar.
4. La **p.24 es el colofón** con la tabla de todo lo simulado y en qué página.

Y dos reglas propias, porque el prototipo **no entra en `auditoria.py`** a
propósito: si entrara, su contenido inventado dispararía el frente 6 en cada
página y el frente 6 dejaría de servir para nada. Así que se audita a sí mismo en
lo que le es propio:

- el aviso tiene que estar en **todas** las páginas;
- **ninguna cifra simulada puede coincidir con una real** de `tokens.metricas`:
  si coincidieran, mañana nadie podría distinguir la maqueta del dato bueno.
  Excepción declarada: `expertos_por_edicion`, `ediciones_celebradas` y
  `proyectos_en_tarima_total` describen el FORMATO, no el resultado de una
  edición — son verdad dentro y fuera de la maqueta, y falsearlas para que no
  coincidan sería inventar al revés. La primera versión de la regla las marcaba
  y me hizo perseguir un fallo que no existía.

La página de patrocinio (p.21) es **la de más riesgo del prototipo**:
`tokens.patrocinio` deja los montos en `null` a propósito, y aquí hay tres
inventados. Por eso el aviso **«MONTO INVENTADO» va dentro de cada tarjeta**, no
solo en la banda de la página: un monto recortado de su contexto es el error más
caro que puede cometer este sistema.

### Lo que la maqueta encontró en el sistema

Llenar 24 páginas activó **6 defectos que las 31 piezas del sistema no tocaban**,
y 5 son la misma raíz: **un color o un tamaño elegido para una FORMA y aplicado a
TEXTO**. Es el tercer sitio donde aparece el mismo patrón, después de `hueco_logo`
en la tanda C.

| Dónde | Qué pasaba | Arreglo |
|---|---|---|
| `revista.Hoja.cabecera()` | el kicker iba en verde fijo: **1.95 sobre blanco** en 6 páginas | el color se mide |
| `nucleo.credito()` | rótulo con el acento de forma: **3.20** en las 8 filas de créditos | color por tamaño del rótulo |
| `nucleo.bloque_cita()` | firma del autor, igual: **3.20** | color por tamaño de la firma |
| `nucleo.hueco()` | la etiqueta no encogía: «ALIADO CUATRO» se salía **97 pt** y pisaba la celda vecina | `fuente_que_quepa` |
| `nucleo.hueco_logo()` | lo mismo | `fuente_que_quepa` |
| `nucleo.grafico_dona()` | con 4 series la última línea de leyenda se salía **6.76 pt** | el radio se despeja del alto real de la leyenda |

Ninguno rompió las 31 piezas: siguen en **0 problemas**.

### Lo que la maqueta encontró de MI parte

- La cabecera con sección a la derecha y `logo_cabecera()` anclado ahí mismo **se
  pisan**. En `revista.py` no se ve porque sus 5 hojas usan una o la otra, nunca
  las dos; aquí hacían falta juntas en 12 páginas. De ahí `cabecera_con_logo()`.
- `ficha_persona` escala **todas** sus medidas por su ALTO. Una caja estrecha y
  muy alta (158 × 420 pt) le pide el nombre a 38 pt en 158 pt de ancho:
  «YAMILA CORCINO*» se salía 60.9 pt y se pisaba con la ficha vecina. El
  componente no estaba roto; la proporción de caja que le di, sí.
- Y una consecuencia de lo anterior que **no se arregla agrandando**: si el
  cuerpo escala con el alto, el número de líneas disponibles no cambia. Barrido
  de 1.05 a 1.60 → 1, 3, 3, 3, 3 y 3 textos recortados con elipsis. **La
  descripción no cabe en una ficha de 1/3 de página con ningún alto**, así que
  sale fuera del componente.
- Un `paso` recibe un alto **nominal** y su texto crece por debajo: 4 escalones a
  74 pt bajaban hasta pisar la cita y la flecha, 9 solapes en una página.
- Anclada por arriba, la píldora de «FUTURO QUE TRANSFORMA.» bajaba hasta la línea
  de organizadores: **155 pt de solape**. Con `ancla="ba"` crece hacia arriba.
- `nota_pie` anclada a una línea base fija se salía 7.7 pt por abajo, y el
  desborde **crecía con lo que dijera la nota**. Ahora se cuentan las líneas y se
  sube desde el borde.
- El tope de columna puesto al alto de la CAJA (y no al del texto) hacía que los
  párrafos nunca llegaran a la segunda columna: la p.07 se leía a media página.

### El fallo silencioso que causó el prototipo

⚠️ Los 24 PNG del prototipo en `_salida/` **rompieron una regla del auditor sin
que nada fallara**. `_pngs()` recorría todo `_salida`, así que
`lote-completo-piezas` pasó a contar 55 PNG frente a 31 esperadas: con 24 de
colchón se podía perder una pieza de verdad y el conteo seguía cuadrando. La
regla se quedó en verde **sin vigilar nada** — el frente 7 en su forma más pura.

No lo vio la auditoría (que seguía dando 0 bloqueantes): lo vio la **prueba de
inyección**, que pasó de 17/17 a 16/17. `_pngs()` ahora filtra por carpeta de
módulo. Es la segunda vez que el arnés de pruebas caza algo que la propia
auditoría no ve.

### Medido

- 24 de 24 páginas: **0 desbordes, 0 solapes, 0 fallos de contraste, 0 desbordes
  de componente, 0 textos recortados**
- PDF de 24 pp, 856 KB, **0 avisos de preflight**; PDF vs PNG **media 2.34 %,
  peor 4.10 %** (umbral 5 %)
- los 15 componentes editoriales del sistema, usados al menos una vez
- el ritmo de color pasó de 15 a **26 tipos de hoja**: hasta ahora cualquier
  página nueva caía en `blanco` por defecto y rompía la alternancia
- doctor **235 comprobaciones / 0 fallos** · auditoría **0 bloqueantes /
  0 importantes** · inyección **17 de 17**

### Y llegaron las fotos (17-ago-2026)

Piero pidió fotos de relleno «aunque sean de otra cosa, solo para dejar como se ve
todo al final». Salen de recortar los **dos collages de la referencia**
(`_fuente/referencia-revista/assets/`), que son de eventos ANTERIORES de la
Fundación: 8 de sala y 4 retratos, en `_derivados/fotos-relleno/`.

Los 4 retratos NO se encuadraron a ojo: se detectó la **caja de cara con Vision**
(`VNDetectFaceRectanglesRequest`, un script Swift de 30 líneas, sin instalar nada)
y el recorte se deriva de ella — aire de 0.65 alturas de cara por arriba, 1.15 por
abajo, y acotado a la foto de origen para no invadir la vecina. A ojo salieron los
cuatro cortados; medidos, los cuatro encuadran.

⚠️ **La atribución es el riesgo, no la foto.** Una cara real junto a
«MARISOL ANDÚJAR* · INVERSIÓN TEMPRANA» le atribuye a una persona real un cargo
que no tiene. Por eso las 4 páginas con foto lo dicen al pie, el colofón lo
recoge y `verificar()` **falla si una página con foto no la declara como de
relleno** o si falta alguna de las 12 (si faltara, el componente pondría su hueco
y la nota seguiría diciendo «las 3 fotos», que sería falso).

**Dos defectos más del sistema, latentes desde el paso 5**, porque los dos únicos
sitios que reciben fotos —`ficha_persona(foto=…)` y `mosaico(fotos=…)`— nunca
habían recibido ninguna:

1. **`opaco()` no grababa la operación.** La foto salía en el PNG y **no en el
   PDF**. Ahora graba `@imagen`. Comprobado en las 4 páginas con foto: si no
   grabara, la comparación PDF-vs-PNG daría 20-40 %; da 0.70–3.91 %.
2. **Ningún componente encajaba la foto en su hueco.** Se pegaba tal cual: una
   foto mayor que su celda tapaba media página y una menor dejaba el hueco a la
   vista. Ahora `Lienzo._encajar()` cubre y recorta al centro — deformar para que
   quepa es peor que perder un borde.

⚠️ Y la limitación de ese encaje, medida: **recorta al CENTRO**, así que si el
sujeto no está centrado en el recorte de origen, se pierde. Pasó con la foto de la
bandera: encajada en una celda apaisada solo se veía el velo verde, porque la
gente estaba en su mitad derecha. Se arregla en el recorte de origen, no en el
componente.

Estado con fotos: 24 de 24 páginas limpias, PDF de **4.7 MB** (las 12 fotos van
embebidas), PDF vs PNG **media 2.20 %, peor 3.91 %**, 0 avisos de preflight.

---

## Acabado limpio y sin sello (17-ago-2026)

    python3 prototipo.py pdf            con la banda de aviso
    python3 prototipo.py sin-sello pdf  el acabado limpio

Las dos versiones salen a `_salida/prototipo/`; la limpia lleva `-sin-sello` en el
nombre. La p.02 de aviso y la p.24 de colofón siguen ahí en las dos, así que el
documento sigue declarando lo que es aunque la banda no esté.

### ⚠️⚠️ SOLAPE DE PLACA CONTRA PLACA — un defecto que llevaba desde la tanda C

Pedir el acabado terminado destapó el fallo más caro de esta tanda, y **no era del
prototipo: era de `revista.py`**, en una pieza entregable del sistema.

Las tarjetas de proyecto miden **124 pt de alto** y se colocaban cada **6.8 líneas
base = 95.2 pt**. Cada tarjeta pisaba **28.8 pt de la anterior**. La de abajo se
dibuja después, así que le tapa el borde inferior a la de arriba y deja sus chips
pegados al filo de la siguiente. En el prototipo era peor: 148 pt de alto cada 8.3
líneas → **31.7 pt**.

**No lo veía ningún control, y no por descuido: no es ninguna de las tres cosas que
se medían.** No es overflow (cabe de sobra en la página). No es desborde de
componente (el texto está dentro de su caja). No es solape de texto, porque el
detector solo mira texto/texto y texto/opaco — y una tarjeta no se registra como
opaca. Es la misma familia que la píldora del paso 5: **una FORMA que se pisa con
otra forma**.

De ahí `Lienzo.solapes_placa()`: `tarjeta()` apunta su caja en `cajas_placa` y el
informe cuenta los cruces. Probado en las dos direcciones —encontró 3 solapes en
`revista.py` y 4 en el prototipo, y tras el arreglo da 0 en las 55 páginas—. El
arreglo es la regla que faltaba escrita: **el salto manda sobre el alto**, nunca
al revés.

### Lo que se llenó para ver la terminación

| Antes | Ahora | De dónde sale |
|---|---|---|
| 9 celdas de logo vacías + 3 huecos punteados | **12 logos** en el muro de la p.20 | los lockups de las comunidades de IAvanza, copiados a `_derivados/logos-relleno/` |
| 2 huecos «QR DE REGISTRO» | **2 QR reales y escaneables** (pp. 18 y 23) | `qrencode -t SVG`, así que van en VECTOR al PDF |
| 6 proyectos + un hueco «07 Y 08 SIN MAQUETAR» | **los 8 del formato**, 4 por página | 2 proyectos inventados más, y la dona agrupada para que sume 8 |

Dos decisiones que no son de gusto:

- **El QR codifica un texto que dice que es una maqueta**, no una URL.
  `edicion.registro_url` está en null y el sistema no inventa destinos: un QR que
  llevara a una dirección falsa sería peor que el hueco marcado que había antes.
  Quien lo escanee lee que esto no es un registro real.
- **Los 12 logos son de la casa.** Poner en un muro de aliados el logo de una
  empresa ajena la presentaría como patrocinadora de un evento que no ha ocurrido,
  y eso no es un detalle de maqueta. Las comunidades de IAvanza son marcas propias.
  La nota al pie de la p.20 lo dice.

---

## Auditoría de terminación (17-ago-2026)

Se lanzó por 6 dimensiones con un refutador por dimensión. **Se cayó a medias por
límite de sesión**: corrieron 3 de las 6 (logos, tipografía, coherencia) y
**ninguno de los refutadores**. El guion devolvió los 29 hallazgos como
«tumbados», que era MENTIRA: cuando el refutador muere, la lista de veredictos
llega vacía y el filtro los manda todos a tumbados. *Sin verificar* no es lo mismo
que *refutado*, y un arnés que no distingue las dos cosas convierte una caída en
un aprobado. Se verificaron a mano, midiendo uno por uno.

### ⚠️⚠️ Los dos lockups oscuros traían una PLACA OPACA horneada

`p4f-lockup-blanco.svg` y `p4f-lockup-color-dark.svg` incluían un
`<rect x="-18.87" y="-8.23" width="226.4" height="98.8" fill="#121D30">` —**más
grande que su propio viewBox**— arrastrado del PDF del diseñador al extraer el
vector. Ocupaba el **74.4 %** de la caja del logo. Como el fondo del sistema es
`#000714` y no `#121D30`, cada logo pegaba un rectángulo más claro alrededor:
**28 apariciones en los 5 módulos**, y cambió **34 de las 79 piezas** al quitarlo
(la portada un 4.06 %, 85.503 px).

Por qué no lo vio nadie en dos semanas:
1. el contraste `#121D30` sobre `#000714` es **1.196** — casi invisible en
   pantalla, pero perfectamente visible impreso y en un proyector;
2. **la verificación del paso 0 comparaba contra el PDF original, que traía el
   mismo fondo**. Comparar contra la fuente no sirve cuando el defecto está en la
   fuente: hay que medir la propiedad que se quiere («el logo es transparente»),
   no la igualdad con el origen.

Y una corrección a lo que escribí primero: **la placa NO tapaba el vídeo** en los
overlays de streaming. Ahí el logo cae sobre la barra de escena, que ya es opaca y
exactamente del mismo `#121D30`: solo cambiaron 14 px de antialiasing en 3 piezas.

De ahí la **regla 27 del doctor**: ninguna variante de logo puede tener esquinas
opacas. Probada en las dos direcciones —con la placa reinyectada canta las 4
esquinas; con los SVG limpios calla—. Los originales quedan en
`_derivados/_logos-con-placa/`, no se borra nada.

### Los 9 defectos de terminación, y su guardia

Todos verificados con medición antes de tocarlos. Cada uno dejó un guardia en
`prototipo.verificar()`, porque **son contradicciones ENTRE páginas** y el
instrumental medía cada página por separado.

| Defecto | Medida | Guardia |
|---|---|---|
| El párrafo 3 de la crónica salía en la p.06 **y** en la p.07 (reparto `[:3]` y `[2:]`) | 1 párrafo en 2 páginas | ningún párrafo puede componerse dos veces |
| La dona anunciaba «Tecnología (3)» y ninguna tarjeta decía Tecnología; 4 etiquetas impresas no salían en la leyenda | 1 sobrante, 4 faltantes | la dona **se cuenta** sobre los verticales impresos |
| La tarima de la 4ª edición repetía la fecha de la 3ª | `14·NOV·2026` en los dos | la próxima no puede caer en la fecha narrada |
| 3 entradas del sumario citaban un titular que no está en su página | 3 de 10 | cada entrada se busca en los TITULARES de su página |
| La sección 05 (patrocinio) no llegaba al índice | 1 de 5 | la página de apertura de cada sección va en el sumario |
| p.02 y p.24 declaraban folio y salían sin pie | 2 páginas | si declara folio, lo imprime |
| La nota al pie caía **dentro** de la 4ª tarjeta de la p.11 y el borde tachaba «maqueta.» | 2 cruces, tarjeta hasta 728.6 pt de 732 | alto 124→112 pt |
| Los 3 montos de la p.21 en 3 cuerpos (44/47/50 px) y **el mayor era el más pequeño** | 3 cuerpos | un cuerpo común, calculado con el monto más largo |
| El cuerpo de la p.06 nunca pasaba a la 2ª columna | 4 textos a la derecha | `dos_columnas()` calcula el corte |

Y **el reparto a dos columnas dejó de adivinarse**: `Pagina.dos_columnas()` envuelve
todo, cuenta las líneas y corta por la mitad. Puesto a ojo, o dejaba media página
en blanco o el texto invadía lo que hubiera debajo — al arreglar lo primero
aparecieron 4 solapes de hasta 218 pt contra la cita.

Inyección de los 6 guardias: **6 de 6 saltan**, y silencio con nada inyectado. El
guardia de secciones necesitó dos intentos: aceptando «la apertura o la página
siguiente», la entrada de otra sección tapaba el hueco y no saltaba.

### El muro de logos: el peso óptico se iguala por ÁREA

Los 12 logos se escalaban solo al ancho de celda, así que todos topaban en 175 px
y su altura quedaba a merced de lo largo que fuera el nombre: **razón 2.83** entre
el más alto y el más bajo. Ahora `celda_logo` iguala el **área de tinta**
(`componentes.celda_logo.logo_area` = 0.055), con los topes de ancho y alto como
límite.

⚠️ Y el límite medido de eso: con lockups de proporción tan dispar (5.4:1 a 9.7:1)
en una celda casi cuadrada, **11 de los 12 siguen topando en el ancho**, así que
escalar no puede igualarlos del todo. El outlier era «JCI», de 3 letras. Cambiado
por otra comunidad: razón de alturas **2.83 → 1.68** y desviación de área
19.5 % → 15.3 %. Un nombre de 3 letras en un muro de lockups no se arregla
escalando; se arregla eligiendo la marca o usando isotipo.

También: `celda_logo` truncaba con `int()` al reescalar y deformaba 3 de los 12
entre 2.4 % y 3.9 %. Ahora redondea. **0 deformados.**

---

## Segunda vuelta de la auditoría de terminación (17-ago-2026)

Se relanzaron las 3 dimensiones que faltaban + un verificador para los 9
hallazgos que quedaron sin comprobar. **Y esta vez el arnés no mintió al
caerse**: el refutador de `fotos` murió por error de conexión y el guion lo
reportó como `REFUTADOR_CAIDO` con sus 10 hallazgos en `sin_verificar`, no en
`tumbados`. El resultado abre con el parte del arnés antes que con los hallazgos.

### ⚠️⚠️ EL BLOQUEANTE: tofu del emoji en 11 de 24 páginas

Las notas al pie abrían con `⚠️` literal. **Saira tiene 661 glifos y ninguno es
U+26A0**; `⚠️` son además DOS codepoints (U+26A0 + U+FE0F), así que PIL imprimía
**dos cajas .notdef —tofu ▯▯— de 16 × 12 px** al principio de la nota, en **11 de
las 24 páginas (46 %)**. Lo escribí yo en cada nota.

Ningún control lo veía, y por una razón que importa: **no es contraste** (el color
es el pedido), **no es desborde** (el tofu ocupa su ancho), **no es solape**, y
**el texto extraíble del PDF sale correcto** — la comprobación de fuentes del paso
5 lo daba por bueno. Es un fallo que solo se ve mirando el píxel o preguntándole a
la fuente.

De ahí `nucleo.cobertura(ttf)` y el control en `Lienzo.texto()`: para cada texto,
todos sus codepoints tienen que estar en el cmap de SU fuente. Barrido de las 55
páginas: **solo el ⚠️**, las 31 del sistema estaban limpias. Probado inyectando
`⚠️` y `✓`: caza U+26A0, U+2713 y U+FE0F.
El arreglo no es cambiar el emoji por otro carácter: `nota_pie(..., aviso=True)`
pinta el **icono `info` del sistema**, en vector, tintado con el acento que se lee
sobre ese fondo — y así llega al PDF como vector, no como glifo prestado.

### Los otros 8 defectos confirmados

| Defecto | Medida | Arreglo |
|---|---|---|
| **«MARISOL ANDÚJAR\*» sale con DOS CARAS distintas** en el pliego 14-15 | p.14 usaba `retrato-2` y la p.15 `retrato-1` para la misma persona | la misma foto en las dos |
| Las dos columnas de la p.06 no comparten línea base | desfase de 8.4 pt en 4 de 8 filas | el aire entre párrafos, en líneas base **enteras** |
| Los 3 nombres de las fichas de la p.14, a cuerpos distintos | 13.44 / 13.44 / 15.36 pt (14 % de diferencia) | `ficha_persona(nombre_pt=…)`, cuerpo común |
| El marco en L del bloque de cita se cerraba por la caja declarada, no por el texto | hasta 31 pt de regla suelta en 5 de 9 bloques | el marco se dibuja al final, con la `y` real |
| Los filetes del sumario pasaban por debajo de la placa de «24 páginas» | filetes a 5 columnas, placa desde la 5ª | filetes a 4 columnas |
| 4 páginas cerraban muy por encima del pie | colas de 227 / 184 / 169 / 151 pt contra una mediana de 47 | contenido y reparto (ver abajo) |

Colas de contenido, antes → después: **p.15** 227→160 · **p.18** 184→125 ·
**p.06** 169→75 · **p.12** 151→fuera del top · **p.22** 132→fuera del top.
La **p.13** (cita a toda página) y la **p.23** (cierre) se quedan con 233 y 162 pt
**a propósito**: son páginas de respiro, no de contenido continuo.

### Fotos: el control que faltaba, y un límite que no se puede arreglar

El refutador de fotos se cayó, así que verifiqué a mano lo medible. **8 de las 12
fotos se amplían por encima de su tamaño nativo**, hasta **1.77×**
(`retrato-4`: nativo 160×200 → 284×214). Y hay un techo del sistema encima: la
composición es a **150 dpi**, así que ninguna imagen embebida puede pasar de
150 ppp, cuando imprenta pide 300.

Esto **no se arregla recortando mejor**: en los collages de origen una cara ocupa
80 × 80 px. Es un límite de la fuente, y por eso las fotos de relleno no sirven
para imprimir — para la revista real hacen falta fotos de verdad.

Lo que sí se puede hacer es no callarlo: `_encajar` ahora apunta cada foto
estirada en `fotos_ampliadas` y el informe la lista con su factor y su ppp real.
Callar esto es exactamente lo que hace que una revista salga de imprenta con las
fotos blandas.

⚠️ **Quedan 9 hallazgos de fotos sin verificar** (el refutador murió): coronillas
cortadas por el borde del recuadro, un brochazo de pintura del collage horneado en
dos fotos, velos de color con borde recto dentro de la foto, una mano ajena
cortada en un retrato, y que los 3 retratos de la p.14 son recortes de fotos que
YA salen más grandes en la crónica y la galería. El último es cierto por
construcción —hay 2 collages para 12 fotos— pero los demás no los he medido.
