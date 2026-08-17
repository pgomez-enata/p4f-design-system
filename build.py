#!/usr/bin/env python3
"""Build del sistema de diseño Pitch 4 Fun.

    python3 build.py            genera tokens.css / tokens.py / tokens.yaml
    python3 build.py doctor     comprueba que lo declarado en tokens.json es CIERTO

`doctor` no cree lo que dice el JSON: vuelve a medir contrastes, mide los SVG del
logo y comprueba que cada fichero de fuente existe y tiene el peso y el ángulo
que declara. Si algo no cuadra, sale con código 1.
"""
import json, os, re, subprocess, sys, tempfile

RAIZ = os.path.dirname(os.path.abspath(__file__))
TOK = os.path.join(RAIZ, "tokens", "tokens.json")


# ---------------------------------------------------------------- utilidades

def cargar():
    with open(TOK, encoding="utf-8") as f:
        return json.load(f)


def _lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminancia(hexa):
    r, g, b = (int(hexa[i:i + 2], 16) for i in (1, 3, 5))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contraste(a, b):
    l1, l2 = luminancia(a), luminancia(b)
    if l1 < l2:
        l1, l2 = l2, l1
    return (l1 + 0.05) / (l2 + 0.05)


def tintas(t):
    """Los colores que pueden ser TINTA: primitivos y neutros."""
    d = {k: v["hex"] for k, v in t["color"]["primitivos"].items()}
    d.update({k: v["hex"] for k, v in t["color"]["neutros"].items() if not k.startswith("_")})
    return d


def superficies(t):
    """Los colores que solo pueden ser FONDO."""
    return {k: v["hex"] for k, v in t["color"].get("superficies", {}).items()
            if not k.startswith("_")}


def hexes(t):
    """Todos los hex del sistema, por nombre. Tintas y superficies."""
    d = tintas(t)
    d.update(superficies(t))
    return d


# ------------------------------------------------------------------ genera

def gen_css(t):
    h = hexes(t)
    L = ["/* GENERADO por build.py desde tokens/tokens.json — NO EDITAR A MANO */",
         f"/* {t['meta']['marca']} v{t['meta']['version']} — {t['meta']['actualizado']} */", "", ":root {"]
    L.append("  /* color */")
    for k, v in h.items():
        L.append(f"  --p4f-{k}: {v};")
    L.append("")
    L.append("  /* roles */")
    for k, v in t["color"]["roles"].items():
        if k.startswith("_"):
            continue
        L.append(f"  --p4f-rol-{k}: var(--p4f-{v});")
    L.append("")
    L.append("  /* tipografia */")
    L.append(f"  --p4f-familia: '{t['tipografia']['familia']['nombre']}', system-ui, sans-serif;")
    for k, v in t["tipografia"]["pesos"].items():
        L.append(f"  --p4f-peso-{k}: {v['valor']};")
    L.append("")
    L.append("  /* escala pt (impresion 8.5x11) */")
    for k, v in t["tipografia"]["escala_pt"].items():
        if not k.startswith("_"):
            L.append(f"  --p4f-pt-{k}: {v}pt;")
    L.append("")
    L.append("  /* escala px (lienzos 1080) */")
    for k, v in t["tipografia"]["escala_px"].items():
        if not k.startswith("_"):
            L.append(f"  --p4f-px-{k}: {v}px;")
    L.append("")
    L.append("  /* hoja */")
    hp = t["hoja"]
    L.append(f"  --p4f-hoja-ancho: {hp['pt'][0]}pt;")
    L.append(f"  --p4f-hoja-alto: {hp['pt'][1]}pt;")
    for k, v in hp["margen_pt"].items():
        L.append(f"  --p4f-margen-{k}: {v}pt;")
    L.append("}")
    L.append("")
    L.append("/* @font-face — los .ttf viven en fuentes/ */")
    for k, v in t["tipografia"]["pesos"].items():
        for est, campo in (("normal", "fichero"), ("italic", "italica")):
            L.append("@font-face {")
            L.append(f"  font-family: '{t['tipografia']['familia']['nombre']}';")
            L.append(f"  font-weight: {v['valor']};")
            L.append(f"  font-style: {est};")
            L.append(f"  src: url('../fuentes/{v[campo]}') format('truetype');")
            L.append("}")
    return "\n".join(L) + "\n"


def gen_py(t):
    h = hexes(t)
    L = ['"""GENERADO por build.py desde tokens/tokens.json — NO EDITAR A MANO."""', ""]
    L.append("COLOR = {")
    for k, v in h.items():
        L.append(f'    "{k}": "{v}",')
    L.append("}")
    L.append("")
    L.append("ROL = {")
    for k, v in t["color"]["roles"].items():
        if not k.startswith("_"):
            L.append(f'    "{k}": COLOR["{v}"],')
    L.append("}")
    L.append("")
    L.append("# qué tinta se puede escribir sobre cada superficie. El núcleo elige")
    L.append("# con esto en vez de con un booleano oscura/clara.")
    L.append("SUPERFICIE = {")
    for k, v in t["color"].get("superficies", {}).items():
        if k.startswith("_"):
            continue
        L.append(f'    "{k}": {{"hex": "{v["hex"]}", '
                 f'"permitida": {v.get("tinta_permitida", [])!r}, '
                 f'"solo_grande": {v.get("tinta_solo_grande", [])!r}, '
                 f'"prohibida": {v.get("tinta_prohibida", [])!r}}},')
    L.append("}")
    L.append("")
    L.append(f'FAMILIA = "{t["tipografia"]["familia"]["nombre"]}"')
    L.append(f'ITALICA_MODO = "{t["tipografia"]["italica"]["modo"]}"')
    L.append(f'ITALICA_ANGULO = {t["tipografia"]["italica"]["angulo"]}')
    L.append("")
    L.append("PESO = {")
    for k, v in t["tipografia"]["pesos"].items():
        L.append(f'    "{k}": {{"valor": {v["valor"]}, "fichero": "{v["fichero"]}", "italica": "{v["italica"]}"}},')
    L.append("}")
    L.append("")
    L.append("ESCALA_PT = " + repr({k: v for k, v in t["tipografia"]["escala_pt"].items() if not k.startswith("_")}))
    L.append("ESCALA_PX = " + repr({k: v for k, v in t["tipografia"]["escala_px"].items() if not k.startswith("_")}))
    L.append("INTERLINEADO = " + repr(t["tipografia"]["interlineado"]))
    L.append("")
    L.append("HOJA_PT = " + repr(t["hoja"]["pt"]))
    L.append("MARGEN_PT = " + repr(t["hoja"]["margen_pt"]))
    L.append("CAJA_TEXTO_PT = " + repr(t["hoja"]["caja_texto_pt"]))
    L.append("")
    L.append("FORMATOS = " + repr(t["formatos"]))
    L.append("LOGO = " + repr(t["logo"]["variantes"]))
    L.append("CLEAR_SPACE = " + repr(t["logo"]["clear_space"]))
    L.append("MINIMOS = " + repr({k: v for k, v in t["logo"]["minimos"].items() if not k.startswith("_")}))
    L.append("RETIRADOS = " + repr(list(t["color"]["retirados"].keys() - {"_nota"})))
    L.append("EDICION = " + repr({k: v for k, v in t["edicion"].items() if not k.startswith("_")}))
    L.append("TONO = " + repr(t["tono"]))
    return "\n".join(L) + "\n"


def gen_yaml(t):
    def vol(o, ind=0):
        p = "  " * ind
        if isinstance(o, dict):
            out = []
            for k, v in o.items():
                if isinstance(v, (dict, list)) and v:
                    out.append(f"{p}{k}:")
                    out.append(vol(v, ind + 1))
                else:
                    out.append(f"{p}{k}: {json.dumps(v, ensure_ascii=False)}")
            return "\n".join(out)
        if isinstance(o, list):
            return "\n".join(f"{p}- {json.dumps(x, ensure_ascii=False)}" if not isinstance(x, dict)
                             else f"{p}-\n" + vol(x, ind + 1) for x in o)
        return f"{p}{json.dumps(o, ensure_ascii=False)}"
    return ("# GENERADO por build.py desde tokens/tokens.json — NO EDITAR A MANO\n" + vol(t) + "\n")


# ------------------------------------------------------------------ doctor

def _tinta_svg(path):
    """Caja de tinta real del SVG, en pt. Devuelve (ancho, alto)."""
    with open(path, encoding="utf-8") as f:
        s = f.read()
    m = re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"', s)
    if not m:
        return None
    W = float(m.group(1))
    png = tempfile.mktemp(suffix=".png")
    try:
        subprocess.run(["rsvg-convert", "-z", "6", "-o", png, path],
                       check=True, capture_output=True)
        from PIL import Image
        import numpy as np
        im = Image.open(png).convert("RGBA")
        a = np.asarray(im)
        ys, xs = np.where(a[:, :, 3] > 10)
        sc = im.width / W
        return ((xs.max() - xs.min() + 1) / sc, (ys.max() - ys.min() + 1) / sc)
    finally:
        if os.path.exists(png):
            os.remove(png)


def doctor(t):
    fallos, avisos, ok = [], [], 0

    # 1. contrastes declarados vs recalculados
    h = hexes(t)
    for nombre, d in t["color"]["contraste"]["medido"].items():
        a, b = nombre.split("_sobre_")
        if a not in h or b not in h:
            fallos.append(f"contraste '{nombre}': color desconocido")
            continue
        real = contraste(h[a], h[b])
        if abs(real - d["ratio"]) > 0.02:
            fallos.append(f"contraste {nombre}: declara {d['ratio']}, mide {real:.2f}")
        elif d["AA_normal"] != (real >= 4.5):
            fallos.append(f"contraste {nombre}: AA_normal declara {d['AA_normal']}, mide {real >= 4.5}")
        else:
            ok += 1

    # 2. contrastes de los neutros
    for k, v in t["color"]["neutros"].items():
        if k.startswith("_"):
            continue
        real = contraste(v["hex"], "#FFFFFF")
        if abs(real - v["contraste_sobre_blanco"]) > 0.02:
            fallos.append(f"neutro {k}: declara {v['contraste_sobre_blanco']}, mide {real:.2f}")
        else:
            ok += 1

    # 3. ficheros de fuente: existen, peso y angulo correctos
    try:
        from fontTools.ttLib import TTFont
        tiene_ft = True
    except ImportError:
        tiene_ft = False
        avisos.append("fontTools no disponible: no se comprobaron los pesos ni el ángulo de las fuentes")
    for k, v in t["tipografia"]["pesos"].items():
        for campo, ital in (("fichero", False), ("italica", True)):
            p = os.path.join(RAIZ, "fuentes", v[campo])
            if not os.path.exists(p):
                fallos.append(f"fuente ausente: fuentes/{v[campo]}")
                continue
            if not tiene_ft:
                ok += 1
                continue
            f = TTFont(p, lazy=True)
            w = f["OS/2"].usWeightClass
            ang = f["post"].italicAngle
            f.close()
            if w != v["valor"]:
                fallos.append(f"{v[campo]}: peso {w}, declara {v['valor']}")
            elif ital and abs(ang - t["tipografia"]["italica"]["angulo"]) > 0.5:
                fallos.append(f"{v[campo]}: ángulo {ang}, declara {t['tipografia']['italica']['angulo']}")
            elif not ital and abs(ang) > 0.5:
                fallos.append(f"{v[campo]}: es romana pero tiene ángulo {ang}")
            else:
                ok += 1

    # 4. SVG del logo: existen y miden lo declarado
    hay_rsvg = subprocess.run(["which", "rsvg-convert"], capture_output=True).returncode == 0
    for k, v in t["logo"]["variantes"].items():
        p = os.path.join(RAIZ, v["archivo"])
        if not os.path.exists(p):
            fallos.append(f"logo ausente: {v['archivo']}")
            continue
        if not hay_rsvg:
            avisos.append(f"sin rsvg-convert: no se midió {v['archivo']}")
            continue
        m = _tinta_svg(p)
        if m is None:
            fallos.append(f"{v['archivo']}: sin viewBox legible")
            continue
        dw, dh = v["pt"]
        if abs(m[0] - dw) > 0.5 or abs(m[1] - dh) > 0.5:
            fallos.append(f"{v['archivo']}: mide {m[0]:.2f}x{m[1]:.2f} pt, declara {dw}x{dh}")
        else:
            ok += 1

    # 5. ningun color retirado se cuela como color vivo
    vivos = {x.upper() for x in h.values()}
    for r in t["color"]["retirados"]:
        if r.startswith("_"):
            continue
        if r.upper() in vivos:
            fallos.append(f"el color {r} está retirado Y en uso a la vez")
        else:
            ok += 1

    # 6. coherencia de la hoja
    hp = t["hoja"]
    esp = [round(hp["pulgadas"][0] * 72), round(hp["pulgadas"][1] * 72)]
    if hp["pt"] != esp:
        fallos.append(f"hoja: {hp['pulgadas']} in son {esp} pt, declara {hp['pt']}")
    else:
        ok += 1
    cx = hp["pt"][0] - hp["margen_pt"]["exterior"] - hp["margen_pt"]["interior"]
    cy = hp["pt"][1] - hp["margen_pt"]["superior"] - hp["margen_pt"]["inferior"]
    if hp["caja_texto_pt"] != [cx, cy]:
        fallos.append(f"caja de texto: los márgenes dan {[cx, cy]}, declara {hp['caja_texto_pt']}")
    else:
        ok += 1

    # 7. roles apuntan a colores que existen
    for k, v in t["color"]["roles"].items():
        if k.startswith("_"):
            continue
        if v not in h:
            fallos.append(f"rol '{k}' apunta a '{v}', que no existe")
        else:
            ok += 1

    # 8. la reticula tiene que CUADRAR, no aproximarse
    r = hp["reticula"]
    lineas = hp["caja_texto_pt"][1] / r["linea_base_pt"]
    if abs(lineas - round(lineas)) > 1e-9:
        fallos.append(f"retícula: caja de {hp['caja_texto_pt'][1]} pt / base {r['linea_base_pt']} pt "
                      f"= {lineas:.4f} líneas, no es entero")
    elif round(lineas) != r["lineas_por_caja"]:
        fallos.append(f"retícula: la caja da {round(lineas)} líneas, declara {r['lineas_por_caja']}")
    else:
        ok += 1

    ancho = r["columnas"] * r["ancho_columna_pt"] + (r["columnas"] - 1) * r["medianil_pt"]
    if ancho != hp["caja_texto_pt"][0]:
        fallos.append(f"retícula: {r['columnas']} col de {r['ancho_columna_pt']} + medianiles "
                      f"= {ancho} pt, la caja mide {hp['caja_texto_pt'][0]} pt")
    else:
        ok += 1

    mitad = 3 * r["ancho_columna_pt"] + 2 * r["medianil_pt"]
    if mitad != r["ancho_columna_texto_pt"]:
        fallos.append(f"retícula: la columna de texto debería medir {mitad} pt, declara {r['ancho_columna_texto_pt']}")
    elif 2 * mitad + r["medianil_pt"] != hp["caja_texto_pt"][0]:
        fallos.append(f"retícula: 2 columnas de texto + medianil = {2*mitad+r['medianil_pt']} pt, "
                      f"la caja mide {hp['caja_texto_pt'][0]} pt")
    else:
        ok += 1

    # 9. el ritmo de color solo nombra fondos que existen
    for k, v in t["editorial"]["ritmo_de_color"].items():
        if k.startswith("_"):
            continue
        if v not in h:
            fallos.append(f"ritmo_de_color['{k}'] usa '{v}', que no es un color del sistema")
        else:
            ok += 1

    # 10. streaming: la zona segura tiene que SER el porcentaje que declara
    s = t["formatos"]["streaming"]
    W, H = s["px"]
    for k in ("titulo", "accion"):
        z = s["zona_segura_px"][k]
        ex, ey = round(W * z["porcentaje"] / 100), round(H * z["porcentaje"] / 100)
        if [z["x"], z["y"]] != [ex, ey]:
            fallos.append(f"zona segura '{k}': {z['porcentaje']} % de {W}x{H} son "
                          f"{ex}x{ey} px, declara {z['x']}x{z['y']}")
        else:
            ok += 1

    # 11. todas las piezas de streaming son del tamaño del formato
    for k, v in s.items():
        if k.startswith("_") or not isinstance(v, dict) or "px" not in v:
            continue
        if v["px"] != s["px"]:
            fallos.append(f"streaming['{k}']: mide {v['px']}, el formato es {s['px']}")
        else:
            ok += 1

    # 12. el margen de streaming ES la zona segura, no un margen aparte
    mg, zt = s["margen_px"], s["zona_segura_px"]
    if [mg["izquierda"], mg["derecha"], mg["arriba"]] != [zt["titulo"]["x"], zt["titulo"]["x"],
                                                          zt["titulo"]["y"]]:
        fallos.append(f"streaming: el margen {mg} no coincide con la zona de título "
                      f"{zt['titulo']}")
    elif mg["abajo"] < zt["barra_reproductor"]:
        fallos.append(f"streaming: el margen inferior ({mg['abajo']}) es menor que la barra "
                      f"del reproductor ({zt['barra_reproductor']}): la pieza cabría debajo "
                      f"de los controles")
    else:
        ok += 1

    # 13. los componentes solo nombran roles y colores que existen
    CLAVES_COLOR = {"fondo", "color", "filete_color", "borde_color",
                    "relleno_sobre_ink", "relleno_sobre_claro"}
    roles = t["tipografia"]["roles"]

    def revisar(nodo, ruta):
        nonlocal ok
        if not isinstance(nodo, dict):
            return
        for k, v in nodo.items():
            if k.startswith("_"):
                continue
            sub = f"{ruta}.{k}"
            if k == "rol" and isinstance(v, str):
                if v not in roles:
                    fallos.append(f"{sub} usa el rol '{v}', que no existe en tipografia.roles")
                else:
                    ok += 1
            elif k in CLAVES_COLOR:
                vals = list(v.values()) if isinstance(v, dict) else (
                    v if isinstance(v, list) else [v])
                for c in vals:
                    if not isinstance(c, str):
                        continue
                    if c not in h:
                        fallos.append(f"{sub} usa el color '{c}', que no es del sistema")
                    else:
                        ok += 1
            elif k == "colores" and isinstance(v, list):
                for c in v:
                    if c not in h:
                        fallos.append(f"{sub} usa el color '{c}', que no es del sistema")
                    else:
                        ok += 1
            else:
                revisar(v, sub)

    revisar(t["componentes"], "componentes")

    # 14. patrocinio: la estructura cuadra y NADIE ha colado un precio
    pt_ = t["patrocinio"]
    if len(pt_["nivel"]) != pt_["niveles"]:
        fallos.append(f"patrocinio: declara {pt_['niveles']} niveles y trae "
                      f"{len(pt_['nivel'])} entradas")
    else:
        ok += 1
    cerrado = any("PATROCINIO" in d.upper() for d in t["meta"]["decisiones_cerradas"])
    for i, n in enumerate(pt_["nivel"]):
        relleno = [k for k in ("nombre", "monto", "moneda", "cupos") if n.get(k) is not None]
        if relleno and not cerrado:
            fallos.append(f"patrocinio.nivel[{i}] trae {relleno} y meta.decisiones_cerradas "
                          f"no registra ninguna decisión de PATROCINIO. Un precio sin decisión "
                          f"detrás no sale del sistema.")
        else:
            ok += 1
    modulos = set(t["formatos"]) | {"patrocinadores"}
    for b in pt_["beneficios"]:
        if b["lo_produce"] not in modulos:
            fallos.append(f"beneficio «{b['que'][:40]}» dice producirlo '{b['lo_produce']}', "
                          f"que no es un módulo del sistema")
        else:
            ok += 1

    # 15. el patrón del rayo existe de verdad
    pat = os.path.join(RAIZ, t["componentes"]["rayo_decorativo"]["archivo"])
    if not os.path.exists(pat):
        fallos.append(f"falta el patrón del rayo: {t['componentes']['rayo_decorativo']['archivo']}")
    else:
        ok += 1

    # 16. cada superficie clasifica LAS 10 TINTAS y las tres listas se recalculan
    #     una por una. Va en las dos direcciones a propósito: declarar permitida
    #     una tinta que no llega es un fallo, y declarar prohibida una que sí se
    #     lee también lo es — lo segundo no rompe una pieza, pero hace que la
    #     documentación mienta, que es cómo vuelven los errores.
    tin = tintas(t)
    for ns, s in t["color"].get("superficies", {}).items():
        if ns.startswith("_"):
            continue
        listas = {"tinta_permitida": (4.5, None), "tinta_solo_grande": (3.0, 4.5),
                  "tinta_prohibida": (None, 3.0)}
        clasificadas = set()
        for nombre, (lo, hi) in listas.items():
            for nt in s.get(nombre, []):
                if nt not in tin:
                    fallos.append(f"superficies.{ns}.{nombre} nombra '{nt}', que no es una tinta")
                    continue
                if nt in clasificadas:
                    fallos.append(f"superficies.{ns}: '{nt}' está en dos listas a la vez")
                    continue
                clasificadas.add(nt)
                r = contraste(s["hex"], tin[nt])
                if (lo is not None and r < lo) or (hi is not None and r >= hi):
                    lim = (f"≥{lo}" if hi is None else
                           (f"<{hi}" if lo is None else f"{lo}–{hi}"))
                    fallos.append(f"superficies.{ns}.{nombre} incluye '{nt}', pero "
                                  f"{nt} sobre {ns} mide {r:.2f} y la lista exige {lim}")
                else:
                    ok += 1
        faltan = set(tin) - clasificadas - {ns}
        if faltan:
            fallos.append(f"superficies.{ns}: sin clasificar {sorted(faltan)}. Las tres "
                          f"listas tienen que cubrir las {len(tin)} tintas del sistema.")
        else:
            ok += 1

    # 18. iconografía: los 26 SVG existen, comparten caja y grosor, y llevan el
    #     marcador de color. Se comprueba el FICHERO, no la definición: el que
    #     acaba en el PDF es el fichero, y un `iconos.py` sin correr deja el
    #     catálogo declarado y el disco vacío sin que nada chille.
    ico = t.get("iconografia")
    if ico:
        d_ico = os.path.join(RAIZ, "iconos")
        en_disco = (sorted(f[4:-4] for f in os.listdir(d_ico) if f.endswith(".svg"))
                    if os.path.isdir(d_ico) else [])
        if en_disco != ico["catalogo"]:
            sobran = set(en_disco) - set(ico["catalogo"])
            faltan = set(ico["catalogo"]) - set(en_disco)
            fallos.append(f"iconografía: el catálogo declara {len(ico['catalogo'])} y en "
                          f"disco hay {len(en_disco)}. Faltan {sorted(faltan)}, "
                          f"sobran {sorted(sobran)}. Corre `python3 iconos.py`.")
        else:
            ok += 1
        vb = f'viewBox="0 0 {ico["caja"]} {ico["caja"]}"'
        for n in en_disco:
            with open(os.path.join(d_ico, f"p4f-{n}.svg"), encoding="utf-8") as f:
                s = f.read()
            mal = []
            if vb not in s:
                mal.append(f"caja distinta de {ico['caja']}")
            if f'stroke-width="{ico["trazo"]}"' not in s:
                mal.append(f"trazo distinto de {ico['trazo']}")
            if f'stroke-linecap="{ico["remate"]}"' not in s:
                mal.append(f"remate distinto de {ico['remate']}")
            if "@COLOR@" not in s:
                mal.append("sin el marcador @COLOR@: no se puede tintar")
            if mal:
                fallos.append(f"icono '{n}': {', '.join(mal)}")
            else:
                ok += 1

    # 19. los componentes de proporciones tienen que CABER en su caja.
    #     Un componente cuyas proporciones verticales suman más de 1 se sale de
    #     sí mismo por construcción, y eso no lo ve el control de overflow de la
    #     página: la página sigue estando bien mientras el componente invade al
    #     vecino. Medido: pasaba en la primera lámina.
    ALTOS = {
        "metrica": ["icono_alto", "cifra_alto", "etiqueta_alto", "nota_alto",
                    "aire_icono", "aire_cifra"],
        "ficha_persona": ["retrato_alto", "nombre_alto", "rol_alto", "desc_alto"],
        "bloque_cita": ["comilla", "texto_alto", "autor_alto", "nota_alto"],
    }
    for nombre, campos in ALTOS.items():
        comp = t["componentes"].get(nombre)
        if not comp:
            fallos.append(f"falta el componente '{nombre}'")
            continue
        suma = sum(comp[k] for k in campos) + comp["padding"] * 2
        if suma >= 1.0:
            fallos.append(f"componentes.{nombre}: sus proporciones verticales suman "
                          f"{suma:.3f} ≥ 1.0 — no cabe en su propia caja")
        else:
            ok += 1

    # 20. el mosaico: cada reparto tiene que sumar el número de fotos que dice
    mos = t["componentes"].get("mosaico", {})
    for n, filas in mos.get("repartos", {}).items():
        if sum(filas) != int(n):
            fallos.append(f"mosaico.repartos['{n}']: {filas} suma {sum(filas)}, no {n}")
        else:
            ok += 1
    if abs(sum(mos.get("pesos_fila_alta", [1])) - 1.0) > 1e-9:
        fallos.append(f"mosaico.pesos_fila_alta suma {sum(mos['pesos_fila_alta'])}, no 1.0")
    else:
        ok += 1

    # 21. todo icono que nombre un componente tiene que existir
    if ico:
        def buscar_iconos(nodo, ruta):
            nonlocal ok
            if isinstance(nodo, dict):
                for k, v in nodo.items():
                    if k in ("icono", "iconos") and isinstance(v, (str, list)):
                        for n in ([v] if isinstance(v, str) else v):
                            if n not in ico["catalogo"]:
                                fallos.append(f"{ruta}.{k} nombra el icono '{n}', "
                                              f"que no está en el catálogo")
                            else:
                                ok += 1
                    else:
                        buscar_iconos(v, f"{ruta}.{k}")
        buscar_iconos(t["componentes"], "componentes")

    # 22. los gráficos: existen, y el fichero del mapa está donde dice
    gr = t.get("graficos")
    if gr:
        for k in ("barras", "dona", "mapa"):
            if k not in gr:
                fallos.append(f"falta el gráfico '{k}'")
            else:
                ok += 1
        arch = os.path.join(RAIZ, gr["mapa"]["archivo"])
        if not os.path.exists(arch):
            fallos.append(f"falta el mapa vectorial: {gr['mapa']['archivo']}")
        else:
            with open(arch, encoding="utf-8") as f:
                s = f.read()
            vb = f'viewBox="0 0 {gr["mapa"]["viewbox"][0]} {gr["mapa"]["viewbox"][1]}"'
            if vb not in s:
                fallos.append(f"el mapa declara viewBox {gr['mapa']['viewbox']} y el "
                              f"fichero no lo trae")
            elif "@COLOR@" not in s:
                fallos.append("el mapa no lleva el marcador @COLOR@: no se puede tintar")
            else:
                ok += 1
        # el eje en cero no es una opción: la zona de barras tiene que dejar sitio
        # al eje y a las etiquetas dentro de la caja.
        b = gr["barras"]
        if b["zona_barras"] + b["etiqueta_alto"] * 1.6 >= 1.0:
            fallos.append(f"graficos.barras: la zona de barras ({b['zona_barras']}) más "
                          f"la etiqueta no cabe en la caja")
        else:
            ok += 1
        if gr["dona"]["grosor"] * 2 >= 1.0:
            fallos.append("graficos.dona: el grosor del anillo se come el hueco")
        else:
            ok += 1

    # 23. la cabecera de sección tiene UNA forma canónica y las demás, retiradas
    cab = t["componentes"].get("cabecera_seccion", {})
    if "_canonica" not in cab:
        fallos.append("cabecera_seccion no declara cuál es su forma canónica")
    elif len([k for k in cab.get("variantes_retiradas", {}) if not k.startswith("_")]) < 1:
        fallos.append("cabecera_seccion no registra ninguna variante retirada: si en la "
                      "referencia había 4 formas, tienen que quedar por escrito")
    else:
        ok += 1

    # 24. las cifras de `metricas` que se derivan unas de otras tienen que CUADRAR.
    #     LEEME.md y tokens.json declaraban esta comprobación desde la tanda D
    #     («esa suma es lo que comprueba el doctor») y NO existía: con
    #     proyectos_edicion_1 = 99 el doctor seguía diciendo 211/0. Lo cazó la
    #     auditoría por frentes, no el propio doctor.
    M = t["metricas"]
    for expr in [M[k] for k in M if k.endswith("_suma_declarada")]:
        izq, der = expr.split("==")
        try:
            a = sum(float(M[x.strip()]) for x in izq.split("+"))
            b_ = float(M[der.strip()])
        except (KeyError, ValueError) as e:
            fallos.append(f"metricas: la suma declarada «{expr}» no se puede evaluar ({e})")
            continue
        if abs(a - b_) > 1e-9:
            fallos.append(f"metricas: «{expr}» da {a:g} y el total declara {b_:g}")
        else:
            ok += 1

    # 25. una contradicción declarada tiene que seguir siendo cierta: si alguien
    #     la «arregla» a medias, el aviso se queda mintiendo en el fichero.
    prj = t.get("proyectos", {})
    if "_hueco_declarado" in prj:
        n_nom = len(prj.get("edicion_1", []))
        n_cif = t["metricas"].get("proyectos_edicion_1")
        if n_cif is not None and n_nom == n_cif:
            fallos.append(f"proyectos._hueco_declarado sigue avisando de una "
                          f"contradicción que ya no existe ({n_nom} = {n_cif}): "
                          f"un aviso obsoleto es peor que ninguno")
        else:
            ok += 1

    # 26. el mínimo del logo tiene que ser ALCANZABLE: existe un alto entero de
    #     rasterizado que da ese ancho. Si no, es un número que nadie puede
    #     cumplir y las piezas lo incumplirían para siempre.
    import math as _m
    for k, v in t["logo"]["variantes"].items():
        w, h = v["pt"]
        lim = t["logo"]["minimos"]["lockup_px" if "lockup" in k else "isotipo_px"]
        alto = _m.ceil(lim * h / w)
        if round(alto * w / h) < lim:
            fallos.append(f"logo.minimos: {k} necesita {alto} px de alto para "
                          f"{lim} de ancho y a ese alto mide "
                          f"{round(alto * w / h)}: el mínimo no es alcanzable")
        else:
            ok += 1

    # 27. NINGÚN SVG DE LOGO PUEDE TRAER FONDO OPACO.
    #     Los dos lockups para fondo oscuro venían con un `<rect fill="#121D30">`
    #     de 226×99 pt —más grande que su propio viewBox— arrastrado del PDF del
    #     diseñador al extraer el vector. Ocupaba el 74.4 % de su caja, y como el
    #     fondo del sistema es #000714 y no #121D30, cada logo pegaba un
    #     rectángulo más claro alrededor: 28 apariciones en los 5 módulos, y 3 de
    #     ellas en overlays de streaming, que van SOBRE VÍDEO y ahí la placa tapa
    #     el fotograma.
    #     Por qué no lo vio nadie: el contraste #121D30 sobre #000714 es 1.196,
    #     casi invisible en pantalla, y la verificación del paso 0 comparaba
    #     contra el PDF original, QUE TRAÍA EL MISMO FONDO. Comparar contra la
    #     fuente no sirve cuando el defecto está en la fuente: hay que medir la
    #     propiedad que se quiere («el logo es transparente»), no la igualdad.
    for k, v in t["logo"]["variantes"].items():
        ruta = os.path.join(RAIZ, v["archivo"])
        if not os.path.exists(ruta):
            fallos.append(f"logo.variantes['{k}']: no existe {v['archivo']}")
            continue
        png = tempfile.mktemp(suffix=".png")
        try:
            subprocess.run(["rsvg-convert", "-h", "120", "-o", png, ruta],
                           check=True, capture_output=True)
            from PIL import Image
            im = Image.open(png).convert("RGBA")
            w, h = im.size
            esquinas = [im.getpixel(p) for p in
                        ((1, 1), (w - 2, 1), (1, h - 2), (w - 2, h - 2))]
            opacas = [e for e in esquinas if e[3] > 200]
            if opacas:
                fallos.append(
                    f"logo.variantes['{k}']: {len(opacas)} de 4 esquinas OPACAS "
                    f"(RGBA{opacas[0]}). Un logo con fondo horneado pega una placa "
                    f"sobre la pieza y tapa el vídeo en los overlays con alfa")
            else:
                ok += 1
        finally:
            if os.path.exists(png):
                os.remove(png)

    # 17. el rol de fondo apunta a una superficie, no a una tinta
    sup = superficies(t)
    if sup:
        fp = t["color"]["roles"].get("fondo-principal")
        if fp not in sup:
            fallos.append(f"roles.fondo-principal es '{fp}', que no es una superficie. "
                          f"El fondo de las piezas sale de color.superficies.")
        else:
            ok += 1

    return fallos, avisos, ok


# -------------------------------------------------------------------- main

def main():
    t = cargar()
    if len(sys.argv) > 1 and sys.argv[1] == "doctor":
        fallos, avisos, ok = doctor(t)
        print(f"{t['meta']['marca']} v{t['meta']['version']} — doctor\n")
        for a in avisos:
            print(f"  aviso  {a}")
        for f in fallos:
            print(f"  FALLO  {f}")
        print(f"\n  comprobaciones superadas: {ok}")
        print(f"  fallos: {len(fallos)}")
        if fallos:
            print("\nEl sistema NO está sano.")
            sys.exit(1)
        print("\nTodo lo que tokens.json declara es cierto.")
        return

    d = os.path.join(RAIZ, "tokens")
    salidas = [("tokens.css", gen_css(t)), ("tokens.py", gen_py(t)), ("tokens.yaml", gen_yaml(t))]
    for nombre, contenido in salidas:
        with open(os.path.join(d, nombre), "w", encoding="utf-8") as f:
            f.write(contenido)
        print(f"  tokens/{nombre:12s} {len(contenido):7d} B")
    print(f"\nGenerado desde tokens.json. Corre `python3 build.py doctor` para comprobarlo.")


if __name__ == "__main__":
    main()
