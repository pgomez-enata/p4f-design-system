"""GENERADO por build.py desde tokens/tokens.json — NO EDITAR A MANO."""

COLOR = {
    "azul": "#0595F0",
    "verde": "#83CE00",
    "ink": "#121D30",
    "blanco": "#FFFFFF",
    "ink-2": "#182438",
    "ink-3": "#2B3B57",
    "gris-texto": "#5A6985",
    "gris-borde": "#ACB6C7",
    "gris-velo": "#E1E6F0",
    "hueso": "#EFF3F9",
    "fondo": "#000714",
    "azul-profundo": "#063780",
    "claro-rayo": "#E6F7FE",
}

ROL = {
    "fondo-principal": COLOR["fondo"],
    "fondo-claro": COLOR["blanco"],
    "superficie-oscura-2": COLOR["azul-profundo"],
    "superficie-clara-2": COLOR["claro-rayo"],
    "primario": COLOR["azul"],
    "acento": COLOR["verde"],
    "texto-sobre-oscuro": COLOR["blanco"],
    "texto-sobre-claro": COLOR["ink"],
    "texto-secundario-claro": COLOR["gris-texto"],
    "borde": COLOR["gris-borde"],
}

# qué tinta se puede escribir sobre cada superficie. El núcleo elige
# con esto en vez de con un booleano oscura/clara.
SUPERFICIE = {
    "fondo": {"hex": "#000714", "permitida": ['blanco', 'verde', 'azul', 'gris-borde', 'gris-velo', 'hueso'], "solo_grande": ['gris-texto'], "prohibida": ['ink', 'ink-2', 'ink-3']},
    "azul-profundo": {"hex": "#063780", "permitida": ['blanco', 'verde', 'gris-borde', 'gris-velo', 'hueso'], "solo_grande": ['azul'], "prohibida": ['ink', 'ink-2', 'ink-3', 'gris-texto']},
    "claro-rayo": {"hex": "#E6F7FE", "permitida": ['ink', 'ink-2', 'ink-3', 'gris-texto'], "solo_grande": [], "prohibida": ['azul', 'verde', 'blanco', 'gris-borde', 'gris-velo', 'hueso']},
}

FAMILIA = "Saira"
ITALICA_MODO = "real"
ITALICA_ANGULO = -12.0

PESO = {
    "regular": {"valor": 400, "fichero": "Saira-Regular.ttf", "italica": "Saira-RegularItalic.ttf"},
    "medium": {"valor": 500, "fichero": "Saira-Medium.ttf", "italica": "Saira-MediumItalic.ttf"},
    "semibold": {"valor": 600, "fichero": "Saira-SemiBold.ttf", "italica": "Saira-SemiBoldItalic.ttf"},
    "bold": {"valor": 700, "fichero": "Saira-Bold.ttf", "italica": "Saira-BoldItalic.ttf"},
    "extrabold": {"valor": 800, "fichero": "Saira-ExtraBold.ttf", "italica": "Saira-ExtraBoldItalic.ttf"},
    "black": {"valor": 900, "fichero": "Saira-Black.ttf", "italica": "Saira-BlackItalic.ttf"},
}

ESCALA_PT = {'micro': 7, 'pie': 8.5, 'cuerpo': 10, 'cuerpo-lg': 12, 'h4': 15, 'h3': 19, 'h2': 24, 'h1': 31, 'display': 40, 'display-xl': 54}
ESCALA_PX = {'micro': 20, 'pie': 24, 'cuerpo': 30, 'cuerpo-lg': 36, 'h4': 44, 'h3': 56, 'h2': 70, 'h1': 88, 'display': 112, 'display-xl': 148}
INTERLINEADO = {'display': 0.95, 'titular': 1.02, 'subtitular': 1.15, 'cuerpo': 1.45, 'dato': 1.0, 'pie': 1.3}

HOJA_PT = [612, 792]
MARGEN_PT = {'superior': 60, 'inferior': 60, 'exterior': 54, 'interior': 54}
CAJA_TEXTO_PT = [504, 672]

FORMATOS = {'_nota': 'Los lienzos que generan los 4 módulos del paso 3.', 'editorial': {'revista': {'pt': [612, 792], 'paginas': [16, 24], 'uso': 'revista post-evento'}, 'hoja-interna': {'pt': [612, 792], 'uso': 'informes, checklists, actas, one-pagers'}, 'carta': {'pt': [612, 792], 'uso': 'carta de patrocinio'}, 'dossier': {'pt': [612, 792], 'uso': 'dossier de patrocinio'}}, 'redes': {'_nota': 'Lienzos de redes. La zona segura NO es el margen: es lo que la app tapa con su propia interfaz. Medido sobre las guías públicas de cada plataforma; conservador a propósito.', 'post-cuadrado': {'px': [1080, 1080], 'margen_px': 72, 'uso': 'feed IG/LinkedIn'}, 'post-retrato': {'px': [1080, 1350], 'margen_px': 72, 'uso': 'feed IG — ocupa más pantalla'}, 'historia': {'px': [1080, 1920], 'margen_px': 72, 'zona_segura_px': {'arriba': 250, 'abajo': 250}, '_zona_nota': 'IG tapa arriba con el avatar y la barra, y abajo con el campo de respuesta. Nada legible en esas franjas.'}, 'carrusel': {'px': [1080, 1350], 'margen_px': 72, 'laminas': [3, 10]}, 'portada-yt': {'px': [1280, 720], 'margen_px': 64, 'uso': 'miniatura — 2-4 palabras máximo'}}, 'streaming': {'_nota': '1920×1080 siempre. Un overlay va SOBRE video: su lienzo es RGBA y todo lo que no es placa queda transparente, para poder cargarlo tal cual en OBS o StreamYard.', 'px': [1920, 1080], 'margen_px': {'_nota': 'En broadcast el margen de composición ES la zona segura de título: no tiene sentido un margen propio más generoso que lo que el televisor no recorta. Abajo manda la barra del reproductor (90), que es mayor que los 54 de título.', 'izquierda': 96, 'derecha': 96, 'arriba': 54, 'abajo': 90}, 'zona_segura_px': {'_nota': 'NO es el margen. `titulo` es lo que un televisor puede recortar y donde por tanto no va texto; `accion` es el límite de cualquier gráfico; `barra_reproductor` es la franja de abajo que el reproductor tapa con sus controles cuando el espectador mueve el ratón.', 'titulo': {'x': 96, 'y': 54, 'porcentaje': 5.0}, 'accion': {'x': 67, 'y': 38, 'porcentaje': 3.5}, 'barra_reproductor': 90}, '_zona_origen': 'Título al 5 % y acción al 3.5 % del lienzo, que es el criterio de EBU R95 y SMPTE para 16:9. La franja del reproductor es conservadora a propósito: la barra de YouTube a 1080p ocupa menos, pero el lower-third no debe quedar nunca por debajo de ella.', 'overlay': {'px': [1920, 1080], 'alfa': True, 'uso': 'marco de escena: barra superior con logo, franja inferior con claim, centro libre para la cámara'}, 'lower-third': {'px': [1920, 1080], 'alfa': True, 'zona': 'tercio inferior izquierdo, por encima de la barra del reproductor', 'variantes': ['pitcher', 'experto']}, 'placa-ganador': {'px': [1920, 1080], 'alfa': False, 'uso': 'pantalla completa opaca al cierre'}, 'cuenta-regresiva': {'px': [1920, 1080], 'alfa': False, 'uso': 'pantalla completa opaca antes de empezar. El número lo repone el software de stream sobre el hueco marcado.'}, 'marco-qr': {'px': [1920, 1080], 'alfa': True, 'uso': 'tarjeta en una esquina con el QR de votación o registro. Sin `edicion.registro_url` el QR va como hueco marcado: no se inventa un destino.'}}, 'deck': {'px': [1920, 1080], 'margen_px': {'izquierda': 112, 'derecha': 112, 'arriba': 84, 'abajo': 84}, 'uso': 'deck de patrocinadores, para proyectar o mandar en PDF', '_margen_nota': 'Más holgado que el overlay de streaming porque aquí manda la lectura a distancia, no la interfaz de un reproductor. Un deck no lleva zona segura de broadcast: no va sobre video.'}}
LOGO = {'lockup-color': {'archivo': 'logo/p4f-lockup-color.svg', 'pt': [204.0, 87.88], 'fondo': 'claro'}, 'lockup-ink': {'archivo': 'logo/p4f-lockup-ink.svg', 'pt': [204.04, 87.96], 'fondo': 'claro'}, 'lockup-color-dark': {'archivo': 'logo/p4f-lockup-color-dark.svg', 'pt': [187.17, 81.71], 'fondo': 'oscuro'}, 'lockup-blanco': {'archivo': 'logo/p4f-lockup-blanco.svg', 'pt': [187.17, 81.71], 'fondo': 'oscuro'}, 'isotipo-color': {'archivo': 'logo/p4f-isotipo-color.svg', 'pt': [59.29, 86.75], 'fondo': 'claro'}, 'isotipo-ink': {'archivo': 'logo/p4f-isotipo-ink.svg', 'pt': [59.29, 86.75], 'fondo': 'claro'}, 'isotipo-blanco': {'archivo': 'logo/p4f-isotipo-blanco.svg', 'pt': [59.29, 86.75], 'fondo': 'oscuro'}, 'appicon-azul': {'archivo': 'logo/p4f-appicon-azul.svg', 'pt': [61.29, 61.17], 'fondo': 'cualquiera'}, 'appicon-verde': {'archivo': 'logo/p4f-appicon-verde.svg', 'pt': [61.29, 61.29], 'fondo': 'cualquiera'}, 'appicon-ink': {'archivo': 'logo/p4f-appicon-ink.svg', 'pt': [61.29, 61.29], 'fondo': 'cualquiera'}}
CLEAR_SPACE = {'factor': 0.1, 'referencia': 'ancho del lockup', 'regla': 'X = 10 % del ancho del logo. Nada entra en ese margen, ni texto ni foto ni otro logo.'}
MINIMOS = {'lockup_px': 120, 'isotipo_px': 48, 'watermark_opacidad': [0.7, 0.85]}
RETIRADOS = ['#6FC42E', '#C5F97E', '#1CA0E6', '#121D2F', '#256A8C', '#F97316', '#009DFF', '#9DFF00', '#44B4B8', '#0A1628', '#111827']
EDICION = {'numero': None, 'nombre': None, 'fecha': None, 'hora': None, 'modalidad': None, 'sede': None, 'ciudad': None, 'registro_url': None, 'instagram': '@pitch4fun.latam'}
TONO = {'personalidad': 'startup rebelde: directa, ágil, sin burocracia', 'voz': 'frases cortas, energía alta, foco en ejecución. Cero relleno.', 'claims': ['MENOS SHOW. MÁS EJECUCIÓN.', 'MVP O NADA.', '3 MINUTOS. SIN EXCUSAS.', 'FEEDBACK REAL. CONEXIONES REALES.', 'TU ASK, CLARO Y ACCIONABLE.'], '_claims_origen': 'Pitch4Fun_LineaGrafica_v1/v2.pdf. La paleta de esa guía está retirada, pero sus claims siguen vigentes: son texto, no color.', 'eslogan_hablado': 'No vengas solo a mirar, sino a ejecutar.', 'verbos': ['aplica', 'registra', 'presenta', 'conecta', 'ejecuta', 'decide']}
