# Sistema de diseño · Pitch 4 Fun

[![doctor](https://img.shields.io/badge/doctor-245%20comprobaciones-0595F0)](#comprobarlo)
[![auditoría](https://img.shields.io/badge/auditor%C3%ADa-0%20bloqueantes-83CE00)](#comprobarlo)
[![licencia](https://img.shields.io/badge/c%C3%B3digo-MIT-121D30)](LICENCIAS.md)

**Pitch 4 Fun** es un evento de pitch de la **Fundación Enlata** e **IAvanza**: 8 proyectos,
3 minutos cada uno, dos ediciones al año. Esto es el sistema que produce todas sus piezas.

No es una guía de estilo en PDF que alguien tiene que leer y obedecer. **Es un programa que
compone las piezas y se niega a sacar una que incumpla.** Los tokens son la fuente de verdad,
las piezas se generan desde ellos, y dos herramientas comprueban cosas distintas: el `doctor`
verifica que *los tokens dicen la verdad*, y la `auditoría` verifica que *las piezas cumplen*.

```bash
git clone https://github.com/pgomez-enata/p4f-design-system.git
cd p4f-design-system
python3 -m pip install pillow reportlab svglib fonttools pypdf
python3 build.py doctor        # ¿los tokens dicen la verdad?
python3 revista.py             # produce las hojas editoriales
python3 auditoria.py           # ¿las piezas cumplen?
```

## Qué produce

| Módulo | Qué saca | Formato |
|---|---|---|
| `revista.py` | Hojas editoriales: portada, apertura de sección, lectura, datos, tarjetas | 8.5 × 11 in |
| `redes.py` | Piezas de Instagram y LinkedIn | 1080 × 1080 · 1080 × 1350 · 1080 × 1920 |
| `streaming.py` | Overlays de directo, lower-thirds y placa de cierre | 1920 × 1080 |
| `patrocinadores.py` | Muro de aliados, carta y dossier de patrocinio | 8.5 × 11 in |
| `prototipo.py` | Maqueta de 24 páginas de la revista post-evento | 8.5 × 11 in |
| `pdf.py` | Cualquiera de las anteriores, en PDF vectorial | texto seleccionable |

Todas salen a `_salida/`, que no está en el repositorio: se regenera corriendo el sistema.
En [`muestras/`](muestras) hay una copia de lo que produce, para verlo sin ejecutar nada.

## Cómo está hecho

**Un solo motor.** `nucleo.py` compone sobre un lienzo y, a la vez, **graba cada operación de
dibujo**. `pdf.py` reproduce esa grabación en reportlab. Un único motor de maquetación, dos
salidas: el PNG y el PDF no pueden divergir porque salen de la misma lista de operaciones.
Medido: 2.15 % de diferencia media entre las dos salidas, 4.52 % en el peor caso.

**Los tokens mandan.** `tokens/tokens.json` es lo único que se edita a mano. De ahí se generan
`tokens.css`, `tokens.py` y `tokens.yaml` con `python3 build.py`. Un valor que no esté en los
tokens no se puede usar: la auditoría lo marca.

**Nada se mide a ojo.** Los solapes se detectan sobre la tinta real de cada glifo
(`actualBoundingBoxAscent/Descent`), no sobre la caja de la fuente — medir con la caja inventa
solapes que no existen y tapa los que sí. El contraste se mide por tamaño de texto. Y si una
fuente no tiene un carácter, se detecta antes de dibujarlo: un glifo que falta **no da error**,
imprime un cuadrito vacío y el texto extraíble del PDF sigue saliendo correcto.

## La marca, en corto

| | |
|---|---|
| **Azul** | `#0595F0` |
| **Verde** | `#83CE00` |
| **Tinta** | `#121D30` |
| **Tipografía** | Saira (SIL OFL). La de marca es Obvia, comercial: el logo va en curvas |
| **Hoja** | 8.5 × 11 in (612 × 792 pt). No A4 |
| **Formato del evento** | 8 proyectos · 3 minutos |

Los tres colores no salen de una guía escrita: salen **medidos del content stream** del vector
original del diseñador, que es lo que está dentro del logo. Una guía anterior declaraba
`#C5F97E`, `#111827`, `#009DFF`, `#9DFF00`, `#256A8C`, `#44B4B8`, `#F97316`, `#1CA0E6`, `#6FC42E`, `#0A1628`, `#121D2F`; esos valores están **retirados** y el doctor falla si reaparecen.

## Comprobarlo

```bash
python3 build.py doctor        # 245 comprobaciones sobre los tokens
python3 auditoria.py           # las piezas contra las reglas del sistema
python3 auditoria.py probar    # inyecta 17 defectos y comprueba que el auditor los caza
python3 prepublicar.py --autoprueba   # la puerta de publicación se prueba a sí misma
```

`auditoria.py probar` es la prueba que importa: **una regla que no salta se ve exactamente
igual que un sistema limpio**. Inyecta un defecto de cada familia y verifica que el auditor lo
encuentra. Si el auditor deja de cazar uno, esa prueba falla.

## La maqueta

`prototipo.py` produce una revista post-evento completa de 24 páginas. **Todo su contenido está
inventado**: los 8 proyectos, las 6 personas, todas las cifras y todas las citas. Cada página
lo lleva escrito en una banda, y `verificar()` comprueba que ninguna cifra simulada coincide
con una real, que el sumario cita titulares que existen, y que ningún párrafo se compone dos
veces.

Los huecos de foto van **vacíos a propósito**. Las fotos de relleno con las que se probó eran
recortes de eventos reales, con caras de personas a las que nadie preguntó, y no salen del
taller. Lo que la maqueta enseña es la retícula, que es lo que aporta el sistema.

## Estructura

```
tokens/          la fuente de verdad · lo único que se edita a mano
logo/            10 variantes del logotipo, en curvas
iconos/          26 iconos del sistema
patrones/        el rayo y el mapa
fuentes/         Saira (SIL OFL 1.1)
nucleo.py        el motor: compone y graba las operaciones
pdf.py           reproduce la grabación en PDF vectorial
build.py         genera los tokens derivados · `doctor`
auditoria.py     audita las piezas · `probar` inyecta defectos
prepublicar.py   la puerta antes de publicar · `--autoprueba`
muestras/        una copia de lo que produce el sistema
```

---

Sistema v1.0.0 · 73 ficheros · código MIT, marca no · ver [LICENCIAS.md](LICENCIAS.md)
