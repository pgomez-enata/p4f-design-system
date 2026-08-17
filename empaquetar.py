#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
empaquetar.py — arma el repo público del sistema de diseño Pitch 4 Fun. NO publica nada.

    python3 empaquetar.py                                   # arma en _salida/p4f-publico
    python3 empaquetar.py --repo USUARIO/p4f-design-system  # el repo que irá en el README
    python3 empaquetar.py --sin-muestras                    # sólo el sistema, sin las piezas

El orden importa y no es negociable:

    copiar → SANEAR → regenerar → documentar → muestras → la puerta → contar

⚠️ SANEAR VA ANTES DE REGENERAR. Al revés, los generados (`tokens.yaml`, `tokens.py`,
`tokens.css`) salen del `tokens.json` sucio y el saneo sólo arregla el JSON. En el sistema
hermano esa inversión metió 238 correos, 81 teléfonos y 43 RNC en el paquete.

⚠️ Y LO QUE SE ESCRIBE VA ANTES DEL SANEO. El README que se escribiera después no se limpiaría
nunca — fue una de las tres causas de la fuga del 9-ago-2026.

## Lo que NO viaja, y por qué

Está declarado en `tokens.meta.privado.punteros`, con su motivo. El caso propio de P4F:

**Las fotos.** `_fuente/referencia-revista/` lleva dos collages de eventos reales con 73 caras
de personas a las que nadie preguntó, y los 12 recortes que salen de ellos. Y no basta con
dejar los `.jpg` fuera: van HORNEADOS dentro de los PNG y del PDF del prototipo, así que la
maqueta se publica REGENERADA con `prototipo.py sin-fotos`. Lo que comprueba que funcionó no
es esta lista: es contar caras con Vision sobre los PNG ya escritos, y eso lo hace la puerta.
"""

from pathlib import Path
import argparse
import json
import re
import shutil
import subprocess
import sys

RAIZ = Path(__file__).resolve().parent

NO_VIAJA = {"_derivados", "_salida", "_fuente", "__pycache__", ".git", ".DS_Store",
            ".pytest_cache", ".ipynb_checkpoints"}
# `_fuente` entero se queda fuera por los collages; el PDF del diseñador se copia aparte,
# porque Piero decidió el 17-ago-2026 que sí viaja (es lo que permite verificar que los 10 SVG
# salen del original). Se comprueba con el detector de caras como cualquier otra imagen.
DE_FUENTE = ["hoja-de-marca-disenador.pdf"]

# PLAN.html es el cuaderno de trabajo: 408 KB de notas internas con rutas. No aporta a quien
# clona y sí cuenta cosas de una máquina concreta.
NO_VIAJA_FICHERO = {"PLAN.html", "COMO-PUBLICAR.md", ".DS_Store"}

# Las piezas que se copian a `muestras/`. Se declaran por nombre: un glob sobre `_salida`
# arrastraría los PNG con fotos del prototipo, que es justo lo que no puede salir.
MUESTRAS = [
    ("_salida/prototipo", "muestras/revista-maqueta", "*-sin-fotos.png"),
    ("_salida/prototipo", "muestras/revista-maqueta", "*-sin-fotos.pdf"),
    ("_salida", "muestras/hojas", "revista-0*.png"),
    ("_salida/redes", "muestras/redes", "*.png"),
    ("_salida/streaming", "muestras/streaming", "*.png"),
    ("_salida/patrocinadores", "muestras/patrocinadores", "*.png"),
    ("_salida/pdf", "muestras/pdf", "*.pdf"),
]

GITIGNORE = """# Carpetas de trabajo: se regeneran corriendo el sistema.
_salida/
_derivados/
__pycache__/
*.pyc

# Del sistema operativo
.DS_Store

# Tu edición concreta. `tokens/edicion.local.json` lleva la fecha, la sede y el enlace de
# registro de UNA edición: eso es tuyo, no del sistema.
tokens/edicion.local.json
"""


def log(m):
    print(f"   {m}")


def titulo(t):
    print(f"\n\033[1m▸ {t}\033[0m")


# ────────────────────────────────────────────────────────────────────── 1 · copiar

def copiar(destino):
    """⚠️ ESTE SCRIPT NO BORRA NADA, y el destino se arma en un temporal por eso.

    La primera versión vaciaba la carpeta de destino con `shutil.rmtree`, y el frente 8 del
    propio auditor lo marcó como bloqueante en `empaquetar.py:98`. Tenía razón: `--destino` es
    un argumento, así que apuntarlo por error a una carpeta con cosas dentro se las llevaba.
    «Piero borra, yo nunca» no admite una excepción para mi propia comodidad.

    Ahora el paquete se arma en un temporal y `entregar()` lo intercambia con el destino,
    apartando lo que hubiera en vez de destruirlo.
    """
    titulo("copiar")
    destino.mkdir(parents=True, exist_ok=True)
    n = 0
    for f in sorted(RAIZ.rglob("*")):
        if not f.is_file():
            continue
        rel = f.relative_to(RAIZ)
        if NO_VIAJA & set(rel.parts) or f.name in NO_VIAJA_FICHERO:
            continue
        (destino / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, destino / rel)
        n += 1
    log(f"{n} ficheros del sistema")

    for nombre in DE_FUENTE:
        origen = RAIZ / "_fuente" / nombre
        if origen.exists():
            (destino / "_fuente").mkdir(exist_ok=True)
            shutil.copy2(origen, destino / "_fuente" / nombre)
            n += 1
            log(f"+ _fuente/{nombre} (el vector del diseñador; lo demás de _fuente no viaja)")
        else:
            log(f"⚠ NO ESTÁ: _fuente/{nombre}")
    return n


# ────────────────────────────────────────────────────────────────────── 2 · sanear

RX_RUTA = re.compile(r"~?/(?:Users/[\w.-]+|Downloads|Desktop|Documents|Escritorio|Descargas)"
                     r"[^\s\"'`,;)]*")
# ⚠️ EL NOMBRE DE LA CARPETA NO SE ESCRIBE AQUÍ, y la historia de por qué merece las 6 líneas.
#
# Estaba escrito literal dentro de este patrón, y el saneador lo reescribía a sí mismo: el
# `empaquetar.py` del paquete salía SIN COMPILAR (`EOL while scanning string literal`) y la
# regla `carpeta-de-trabajo` de `prepublicar.py` quedaba convertida en algo que no cazaba nada.
# Le puse el pragma para que el saneo respetara la línea… y entonces el nombre de la carpeta de
# Piero viajó al repo público. Lo cazó `escanear_fuera.py` sobre el repo YA PUBLICADO, no la
# puerta. Con el literal dentro, las dos salidas eran malas.
#
# Se deduce del entorno, con una sola declaración compartida (`prepublicar.carpeta_de_trabajo`)
# porque dos copias del mismo criterio comparten su punto ciego y entonces no son dos capas.
sys.path.insert(0, str(RAIZ))
import prepublicar                                                            # noqa: E402
_CDT = prepublicar.carpeta_de_trabajo()
RX_CARPETA = re.compile(r"[^\s\"'`,;)]*" + re.escape(_CDT) + r"[^\s\"'`,;)]*") if _CDT \
    else re.compile(r"(?!x)x")     # patrón que no casa nunca: no hay nombre que buscar


def sanear(destino):
    """Quita del paquete lo que describe una máquina concreta o identifica a alguien.

    Se hace sobre el paquete, nunca sobre el taller: en el taller esas rutas y ese RNC son
    ciertos y sirven. Lo que no pueden es viajar."""
    titulo("sanear")

    # ── los punteros declarados en `tokens.meta.privado`. Va PRIMERO, porque `regenerar()`
    # rehace el YAML y el .py desde este JSON: al revés, el dato sale horneado en los
    # generados y el saneo sólo arregla el JSON.
    tj = destino / "tokens" / "tokens.json"
    tok = json.loads(tj.read_text(encoding="utf-8"))
    priv = tok.get("meta", {}).get("privado", {})
    vaciados = []
    for clave in ("rnc_organizador",):
        if priv.get(clave):
            priv[clave] = ""
            vaciados.append(clave)
    # y la ruta del disco dentro de las fuentes de verdad
    tok["meta"]["fuentes_de_verdad"] = [RX_RUTA.sub("(fuera del repo)", s)
                                        for s in tok["meta"].get("fuentes_de_verdad", [])]
    tj.write_text(json.dumps(tok, ensure_ascii=False, indent=1), encoding="utf-8")
    log(f"tokens: vaciados {vaciados or '—'}")

    tocados, cambios = 0, 0
    for f in sorted(destino.rglob("*")):
        if not f.is_file() or f.suffix.lower() in {".png", ".jpg", ".jpeg", ".pdf", ".ttf",
                                                   ".zip", ".cff", ".webp"}:
            continue
        try:
            txt = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        # ⚠️ EL SANEO RESPETA EL PRAGMA, línea a línea. Sin esto, el saneador reescribía los
        # FIXTURES de `prepublicar.py --autoprueba` —«(fuera del repo) pasaba
        # a «(fuera del repo)»— y en el repo publicado la autoprueba de la puerta fallaba con
        # 3 de sus reglas SIN PROBAR. Medido desde un clon el 17-ago-2026.
        #
        # Es la forma de fallo de siempre, esta vez fabricada por mí: una comprobación que
        # desaparece se ve igual que una que pasa. Y el matiz que ya costó caro una vez: la
        # exención es POR LÍNEA. Exonerar el fichero entero dejaría sin sanear una ruta real
        # escrita tres líneas más abajo.
        sal, n1, n2 = [], 0, 0
        for linea in txt.split("\n"):
            if "prepublicar: ok" in linea:
                sal.append(linea)
                continue
            linea, a = RX_RUTA.subn("(fuera del repo)", linea)
            linea, b = RX_CARPETA.subn("(la carpeta de trabajo)", linea)
            n1 += a
            n2 += b
            sal.append(linea)
        if n1 + n2:
            f.write_text("\n".join(sal), encoding="utf-8")
            tocados += 1
            cambios += n1 + n2
    log(f"{cambios} rutas de máquina saneadas en {tocados} fichero(s) "
        f"(las líneas con el pragma se respetan: son fixtures de prueba)")
    return cambios


# ─────────────────────────────────────────────────────────── 3 · regenerar dentro del paquete

def regenerar(destino):
    """El build corre DENTRO del paquete, y después del saneo.

    Así los generados salen del `tokens.json` ya limpio. Al revés, `tokens.yaml` y `tokens.py`
    se quedan con el dato sucio y el saneo sólo arregla el JSON: eso es lo que en el sistema
    hermano metió 238 correos en el paquete."""
    titulo("regenerar dentro del paquete")
    r = subprocess.run([sys.executable, "build.py"], cwd=destino, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-1500:], r.stderr[-1500:])
        raise SystemExit("✗ el build falló dentro del paquete")
    log("tokens.css · tokens.py · tokens.yaml regenerados del JSON saneado")

    d = subprocess.run([sys.executable, "build.py", "doctor"], cwd=destino,
                       capture_output=True, text=True)
    m = re.search(r"comprobaciones superadas: (\d+)\s*\n\s*fallos: (\d+)", d.stdout)
    if not m:
        print(d.stdout[-1200:])
        raise SystemExit("✗ el doctor no devolvió cuentas dentro del paquete")
    sup, fal = int(m.group(1)), int(m.group(2))
    log(f"doctor dentro del paquete: {sup} comprobaciones · {fal} fallos")
    if fal:
        raise SystemExit("✗ el paquete no pasa su propio doctor")
    return sup


# ──────────────────────────────────────────────────────────────────── 4 · documentar

def documentos(destino, repo, n_ficheros):
    """README, licencias y .gitignore. Se escriben ANTES del saneo del paso siguiente… no:
    se escriben aquí y el saneo YA pasó, así que no pueden llevar rutas dentro. Por eso este
    texto es fijo y no interpola nada del taller — salvo el nombre del repo, que lo da quien
    empaqueta."""
    titulo("documentos")
    tok = json.loads((destino / "tokens" / "tokens.json").read_text(encoding="utf-8"))
    ver = tok["meta"]["version"]
    # Los tres colores se LEEN de los tokens, no se escriben a mano: un README con el hex
    # copiado se desincroniza en silencio del sistema que documenta. Si algún día el token
    # cambia de sitio, esto revienta el empaquetado — que es lo correcto.
    prim = tok["color"]["primitivos"]
    azul, verde, tinta = (prim["azul"]["hex"], prim["verde"]["hex"], prim["ink"]["hex"])
    retirados = ", ".join(f"`{k}`" for k in tok["color"]["retirados"] if k.startswith("#"))

    (destino / ".gitignore").write_text(GITIGNORE, encoding="utf-8")

    licencia = f"""# Licencias

Este repositorio mezcla tres cosas con licencias distintas. Están separadas a propósito.

## 1 · El código — MIT

Todo lo `.py`, `.json`, `.css` y `.yaml` de este repositorio: el motor de composición
(`nucleo.py`), los cinco generadores de piezas, el auditor, el doctor y los tokens.

```
Copyright (c) 2026 Fundación Enlata · IAvanza

Por la presente se concede permiso, libre de cargo, a cualquier persona que obtenga una copia
de este software y de los archivos de documentación asociados (el "Software"), a utilizar el
Software sin restricción, incluyendo sin limitación los derechos a usar, copiar, modificar,
fusionar, publicar, distribuir, sublicenciar y/o vender copias del Software, y a permitir a
las personas a las que se les proporcione el Software a hacer lo mismo, sujeto a las
siguientes condiciones:

El aviso de copyright anterior y este aviso de permiso se incluirán en todas las copias o
partes sustanciales del Software.

EL SOFTWARE SE PROPORCIONA "COMO ESTÁ", SIN GARANTÍA DE NINGÚN TIPO, EXPRESA O IMPLÍCITA,
INCLUYENDO PERO NO LIMITADO A GARANTÍAS DE COMERCIALIZACIÓN, IDONEIDAD PARA UN PROPÓSITO
PARTICULAR E INCUMPLIMIENTO. EN NINGÚN CASO LOS AUTORES O TITULARES DEL COPYRIGHT SERÁN
RESPONSABLES DE NINGUNA RECLAMACIÓN, DAÑOS U OTRAS RESPONSABILIDADES.
```

## 2 · La marca Pitch 4 Fun — NO es de código abierto

`logo/`, `patrones/`, los colores de marca y el nombre **Pitch 4 Fun** son marca de la
Fundación Enlata e IAvanza. Están aquí para que quien organiza o patrocina una edición pueda
producir sus piezas **correctamente**, no para reutilizarlos en otra cosa.

- ✅ Puedes usarlos para producir materiales **de Pitch 4 Fun**.
- ✅ Puedes leer el código, aprender de él y adaptarlo a **tu propia marca**.
- ❌ No puedes usar el logo, el nombre ni la identidad para otro evento o producto.
- ❌ No puedes modificar el logotipo ni recomponerlo. El sistema ya trae las 10 variantes.

`_fuente/hoja-de-marca-disenador.pdf` es el vector original entregado por el diseñador de la
marca en marzo de 2026. Va incluido para que cualquiera pueda verificar que los 10 SVG de
`logo/` salen de él, y se rige por esta misma sección.

## 3 · La tipografía Saira — SIL Open Font License 1.1

`fuentes/` contiene Saira, de Héctor Gatti / Omnibus-Type, bajo **SIL OFL 1.1**. La licencia
completa viaja en `fuentes/OFL-Saira.txt` y se aplica tal cual.

Saira **no es la tipografía de la marca**: la original es Obvia, que es comercial y no se
distribuye aquí. Saira se eligió midiendo 7 métricas contra Obvia (distancia 0.567, frente a
1.337 de Poppins y 1.367 de Archivo). El logotipo va en curvas y no necesita ninguna de las dos.

## Lo que este repositorio NO contiene, a propósito

- **Fotografías.** Las de la maqueta eran recortes de dos collages de eventos reales, con 73
  caras de personas a las que nadie pidió permiso. La maqueta se publica regenerada con los
  huecos vacíos (`prototipo.py sin-fotos`).
- **Datos de contacto**, rutas de máquina o identidad fiscal. Lo comprueba `prepublicar.py`.
"""
    (destino / "LICENCIAS.md").write_text(licencia, encoding="utf-8")

    readme = f"""# Sistema de diseño · Pitch 4 Fun

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
git clone https://github.com/{repo}.git
cd {repo.split('/')[-1]}
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
| **Azul** | `{azul}` |
| **Verde** | `{verde}` |
| **Tinta** | `{tinta}` |
| **Tipografía** | Saira (SIL OFL). La de marca es Obvia, comercial: el logo va en curvas |
| **Hoja** | 8.5 × 11 in (612 × 792 pt). No A4 |
| **Formato del evento** | 8 proyectos · 3 minutos |

Los tres colores no salen de una guía escrita: salen **medidos del content stream** del vector
original del diseñador, que es lo que está dentro del logo. Una guía anterior declaraba
{retirados}; esos valores están **retirados** y el doctor falla si reaparecen.

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

Sistema v{ver} · {n_ficheros} ficheros · código MIT, marca no · ver [LICENCIAS.md](LICENCIAS.md)
"""
    (destino / "README.md").write_text(readme, encoding="utf-8")
    log("README.md · LICENCIAS.md · .gitignore")


# ──────────────────────────────────────────────────────────────────────── 5 · muestras

def muestras(destino):
    titulo("muestras")
    total = 0
    for origen_rel, destino_rel, patron in MUESTRAS:
        origen = RAIZ / origen_rel
        if not origen.is_dir():
            log(f"⚠ no está: {origen_rel}")
            continue
        salida = destino / destino_rel
        salida.mkdir(parents=True, exist_ok=True)
        n = 0
        for f in sorted(origen.glob(patron)):
            if f.is_file():
                shutil.copy2(f, salida / f.name)
                n += 1
        total += n
        log(f"{n:3d} → {destino_rel}/  ({patron})")
    peso = sum(f.stat().st_size for f in (destino / "muestras").rglob("*") if f.is_file())
    log(f"{total} ficheros · {peso / 1048576:.1f} MB")
    return total


# ──────────────────────────────────────────────── 5b · ¿el paquete está entero y se prueba?

def entero(destino):
    """Dos comprobaciones que nacieron del mismo fallo, y el fallo lo fabricó este script.

    El saneador reescribía el nombre de la carpeta de trabajo DENTRO de los patrones que lo
    buscan. Resultado en el paquete: `empaquetar.py` sin compilar (`EOL while scanning string
    literal`) y la regla `carpeta-de-trabajo` de `prepublicar.py` convertida en
    `r"(la carpeta de trabajo) experiences"`, que no caza nada. Las dos cosas salían del
    empaquetado en verde y sólo se vieron corriendo el sistema desde un clon.

    Así que ahora, antes de la puerta:

    1. **Todo `.py` del paquete tiene que compilar.** Un fichero roto no lanza error al
       copiarlo: sale, y parece que funcionó. Es el frente 7 en su forma más pura.
    2. **La puerta del paquete tiene que probarse a sí misma DENTRO del paquete.** No basta con
       que la del taller pase: la que va a usar quien clone es la otra, y son ficheros
       distintos desde el momento en que hay un saneo por medio. Esto habría cazado solo la
       regla desactivada.
    """
    titulo("¿el paquete está entero?")
    import py_compile
    rotos = []
    for f in sorted(destino.rglob("*.py")):
        try:
            py_compile.compile(str(f), doraise=True, cfile=str(f) + "c")
            Path(str(f) + "c").unlink(missing_ok=True)
        except py_compile.PyCompileError as e:
            rotos.append((f.relative_to(destino).as_posix(), str(e).split("\n")[-1][:90]))
    n_py = len(list(destino.rglob("*.py")))
    if rotos:
        for r, e in rotos:
            log(f"✗ NO COMPILA  {r}  — {e}")
        raise SystemExit(f"\n✗ NO se publica: {len(rotos)} de {n_py} ficheros .py del paquete "
                         f"no compilan.\n")
    log(f"los {n_py} ficheros .py del paquete compilan")

    r = subprocess.run([sys.executable, "prepublicar.py", "--autoprueba"],
                       cwd=destino, capture_output=True, text=True)
    m = re.search(r"RESULTADO: fallos=(\d+) no_probados=(\d+)", r.stdout)
    if not m:
        print(r.stdout[-1200:], r.stderr[-600:])
        raise SystemExit("✗ la autoprueba del paquete no devolvió cuentas")
    fallos, no_probados = int(m.group(1)), int(m.group(2))
    if fallos:
        print(r.stdout[-2000:])
        raise SystemExit(f"\n✗ NO se publica: la puerta DENTRO del paquete falla {fallos} de "
                         f"sus propias comprobaciones. Alguna regla salió desactivada.\n")
    log(f"la puerta se prueba a sí misma dentro del paquete: 0 fallos, "
        f"{no_probados} no probado(s)")
    if no_probados:
        log("  (el detector de caras no se puede probar en el paquete: las fotos con cara no "
            "viajan. Se declara, no se aprueba)")
    return n_py


# ─────────────────────────────────────────────────────────────────────── 6 · la puerta

def puerta(destino):
    """⚠️ La puerta es el primer filtro, NO la verificación.

    En el sistema hermano esta misma puerta dijo «✓ nada que no deba salir» dos veces con
    datos reales publicados detrás. Lo que los encontró fue un escáner escrito aparte, sobre un
    clon del repo YA publicado. Aquí eso es `escanear_fuera.py`, y se corre después de subir.
    """
    titulo("la puerta: ¿se puede publicar esto?")
    r = subprocess.run([sys.executable, str(RAIZ / "prepublicar.py"), str(destino)],
                       capture_output=True, text=True)
    print(r.stdout, end="")
    if r.returncode != 0:
        print(r.stderr, end="")
        raise SystemExit("\n✗ NO se publica. La puerta encontró algo que no debe salir.\n"
                         "  Arréglalo en el taller (o añade el puntero a "
                         "`tokens.meta.privado`) y vuelve a empaquetar.\n")

    # ── y el escáner de FUERA, aquí mismo, sobre el paquete.
    # ⚠️ No sustituye al que se corre sobre el clon de GitHub: ése lee lo que el servidor
    # devuelve de verdad, y es el único que ha encontrado algo dos veces. Pero pasarlo aquí es
    # gratis y habría cazado antes de publicar el nombre de la carpeta de trabajo que se coló
    # el 17-ago-2026 dentro de los patrones a los que yo mismo había puesto el pragma.
    titulo("y el escáner de fuera, sobre el paquete")
    r = subprocess.run([sys.executable, str(RAIZ / "escanear_fuera.py"), str(destino)],
                       capture_output=True, text=True)
    print(r.stdout[-2500:], end="")
    if r.returncode != 0:
        raise SystemExit("\n✗ NO se publica: el escáner independiente encontró algo que la "
                         "puerta no vio.\n")
    return True


# ────────────────────────────────────────────────────────────────────────── 7 · contar

def contar(destino, esperados):
    titulo("cuentas")
    reales = [f for f in destino.rglob("*") if f.is_file()
              and "__pycache__" not in f.parts and ".git" not in f.parts]
    peso = sum(f.stat().st_size for f in reales)
    log(f"{len(reales)} ficheros · {peso / 1048576:.1f} MB")
    if len(reales) < esperados:
        log(f"⚠ ESPERABA AL MENOS {esperados} y hay {len(reales)}. Algo se perdió.")
    return len(reales), peso


def entregar(temporal, destino):
    """Pone el paquete recién armado en su sitio SIN borrar lo que hubiera.

    Si el destino ya existe, se aparta a `<destino>-anterior-N` y se dice en voz alta. Se
    acumulan carpetas, sí: viven en `_salida/`, que es zona de trabajo y está en el
    `.gitignore`. Lo que sobra lo borra Piero.

    ⚠️ El `.git` del destino viejo SE MUEVE al paquete nuevo, no se aparta con él. Si no,
    reempaquetar dejaría el destino sin historial y habría que recrear el repo entero por un
    cambio de una línea.
    """
    titulo("entregar")
    if destino.exists():
        git = destino / ".git"
        if git.exists():
            shutil.move(str(git), str(temporal / ".git"))
            log("el .git del destino anterior se MUEVE al paquete nuevo (conserva historial)")
        n = 1
        while (apartado := destino.parent / f"{destino.name}-anterior-{n}").exists():
            n += 1
        destino.rename(apartado)
        log(f"el destino anterior NO se borra: queda en {apartado.name}/")
    shutil.move(str(temporal), str(destino))
    log(f"paquete en {destino}")


def main():
    import tempfile
    ap = argparse.ArgumentParser(
        description="Arma el repo público del sistema de diseño P4F. NO publica nada.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("--destino", default=str(RAIZ / "_salida" / "p4f-publico"))
    ap.add_argument("--repo", default="TU-USUARIO/p4f-design-system",
                    help="El owner/repo de GitHub. Va en el README")
    ap.add_argument("--sin-muestras", action="store_true", dest="sin_muestras")
    a = ap.parse_args()

    destino = Path(a.destino).resolve()
    print(f"\n\033[1mEmpaquetando el sistema P4F → {destino}\033[0m")

    # se arma aquí y se intercambia al final: ver `copiar()`. El nombre lo da el sistema, así
    # que dos empaquetados a la vez no se pisan.
    temporal = Path(tempfile.mkdtemp(prefix="p4f-paquete-"))
    n = copiar(temporal)
    sanear(temporal)
    regenerar(temporal)
    documentos(temporal, a.repo, n)
    if not a.sin_muestras:
        muestras(temporal)
    entero(temporal)
    puerta(temporal)
    contar(temporal, n)
    entregar(temporal, destino)

    print(f"\n\033[1m✓ paquete armado.\033[0m No se ha publicado nada.")
    print(f"  Revísalo: {destino}")
    print(f"  Y después de publicar, el escáner de fuera:  "
          f"python3 escanear_fuera.py <clon-del-repo-publicado>\n")


if __name__ == "__main__":
    main()
