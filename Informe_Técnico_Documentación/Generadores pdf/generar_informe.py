#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generador del informe técnico unificado «Tucumán Respira».

Integra el informe técnico previo, la documentación del equipo y las
correcciones recientes (red/AP, arranque del ESP32 y CO₂ por defecto).
"""
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image as RLImage, KeepTogether, PageBreak,
    PageTemplate, Paragraph, Spacer, Table, TableStyle,
)

BASE = Path(__file__).resolve().parent
SALIDA = str(BASE / "Informe_Tucuman_Respira.pdf")
FIG = BASE / "figuras"
CIRCUITO = BASE.parent / "Diseño_Circuito"
DATOS_PATH = BASE / "datos_resumen.json"
if not DATOS_PATH.exists():
    raise SystemExit("Falta datos_resumen.json; ejecutá actualizar_datos.py.")
DATOS = json.loads(DATOS_PATH.read_text(encoding="utf-8"))

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
pdfmetrics.registerFont(TTFont("DejaVu", FONT_DIR / "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", FONT_DIR / "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Oblique", FONT_DIR / "DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-BoldOblique", FONT_DIR / "DejaVuSans-BoldOblique.ttf"))
pdfmetrics.registerFont(TTFont("DejaVuMono", FONT_DIR / "DejaVuSansMono.ttf"))
pdfmetrics.registerFontFamily(
    "DejaVu", normal="DejaVu", bold="DejaVu-Bold",
    italic="DejaVu-Oblique", boldItalic="DejaVu-BoldOblique",
)

AZUL = colors.HexColor("#0f172a")
VERDE = colors.HexColor("#059669")
GRIS = colors.HexColor("#64748b")
GRIS_CLARO = colors.HexColor("#d7dee8")
FONDO_SUAVE = colors.HexColor("#f8fafc")
FONDO_COD = colors.HexColor("#f1f5f9")
ANCHO = A4[0] - 30 * mm

S = {
    "marca": ParagraphStyle("marca", fontName="DejaVu-Bold", fontSize=10.5,
                            textColor=VERDE, leading=14, spaceAfter=5),
    "escuela": ParagraphStyle("escuela", fontName="DejaVu-Bold", fontSize=13,
                              textColor=AZUL, leading=17, spaceAfter=2),
    "proyecto": ParagraphStyle("proyecto", fontName="DejaVu", fontSize=10.5,
                               textColor=GRIS, leading=14, spaceAfter=12),
    "titulo": ParagraphStyle("titulo", fontName="DejaVu-Bold", fontSize=29,
                             textColor=AZUL, leading=33, spaceAfter=6),
    "subtitulo": ParagraphStyle("subtitulo", fontName="DejaVu", fontSize=12,
                                textColor=GRIS, leading=16, spaceAfter=12),
    "autor": ParagraphStyle("autor", fontName="DejaVu-Bold", fontSize=10.5,
                            textColor=AZUL, leading=14, spaceAfter=5),
    "equipo": ParagraphStyle("equipo", fontName="DejaVu", fontSize=8.8,
                             textColor=AZUL, leading=12, spaceAfter=6),
    "h1": ParagraphStyle("h1", fontName="DejaVu-Bold", fontSize=14.5,
                         textColor=AZUL, leading=18, spaceBefore=11,
                         spaceAfter=6, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="DejaVu-Bold", fontSize=10.5,
                         textColor=VERDE, leading=13.5, spaceBefore=8,
                         spaceAfter=3, keepWithNext=1),
    "body": ParagraphStyle("body", fontName="DejaVu", fontSize=8.9,
                           textColor=colors.HexColor("#1e293b"), leading=12.2,
                           alignment=TA_JUSTIFY, spaceAfter=5),
    "bullet": ParagraphStyle("bullet", fontName="DejaVu", fontSize=8.9,
                             textColor=colors.HexColor("#1e293b"), leading=12.2,
                             leftIndent=12, bulletIndent=2, spaceAfter=2.6),
    "celda": ParagraphStyle("celda", fontName="DejaVu", fontSize=7.7,
                            textColor=colors.HexColor("#1e293b"), leading=9.8),
    "celda_b": ParagraphStyle("celda_b", fontName="DejaVu-Bold", fontSize=7.7,
                              textColor=AZUL, leading=9.8),
    "celda_s": ParagraphStyle("celda_s", fontName="DejaVu", fontSize=7.2,
                              textColor=colors.HexColor("#1e293b"), leading=9.1),
    "celda_bs": ParagraphStyle("celda_bs", fontName="DejaVu-Bold", fontSize=7.2,
                               textColor=AZUL, leading=9.1),
    "th": ParagraphStyle("th", fontName="DejaVu-Bold", fontSize=7.7,
                         textColor=colors.white, leading=9.8),
    "th_s": ParagraphStyle("th_s", fontName="DejaVu-Bold", fontSize=7.2,
                           textColor=colors.white, leading=9.1),
    "small": ParagraphStyle("small", fontName="DejaVu", fontSize=7.2,
                            textColor=GRIS, leading=9.4),
    "code": ParagraphStyle("code", fontName="DejaVuMono", fontSize=6.8,
                           leading=8.5, textColor=colors.HexColor("#0f172a"),
                           backColor=FONDO_COD, borderColor=GRIS_CLARO,
                           borderWidth=0.5, borderPadding=6, spaceBefore=2,
                           spaceAfter=6),
    "quote": ParagraphStyle("quote", fontName="DejaVu", fontSize=8.3,
                            textColor=colors.HexColor("#0f172a"), leading=11.2,
                            leftIndent=12, rightIndent=6,
                            backColor=FONDO_SUAVE, borderColor=GRIS_CLARO,
                            borderWidth=0.5, borderPadding=6, spaceAfter=6),
    "indice": ParagraphStyle("indice", fontName="DejaVu", fontSize=9.2,
                             textColor=AZUL, leading=14.2),
    "figcap": ParagraphStyle("figcap", fontName="DejaVu", fontSize=7.1,
                             textColor=GRIS, leading=9.2, alignment=TA_CENTER),
    "nota": ParagraphStyle("nota", fontName="DejaVu", fontSize=8.0,
                           textColor=colors.HexColor("#1e293b"), leading=11.2,
                           backColor=FONDO_SUAVE, borderColor=GRIS_CLARO,
                           borderWidth=0.5, borderPadding=7, spaceAfter=8),
}

story = []


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;"))


def fmt_int(n):
    return f"{int(n):,}".replace(",", ".")


def fmt_dec(x, dec=2):
    s = f"{float(x):,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")


def fmt_var(clave, x):
    if clave in ("co2", "luz", "presion"):
        return fmt_dec(x, 0)
    if clave in ("temperatura", "humedad", "pm25"):
        return fmt_dec(x, 1)
    return fmt_dec(x, 2)


def fmt_pct(x):
    return f"{float(x):.1f}".replace(".", ",") + " %"


def fmt_fecha_utc(iso):
    dt = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    return dt.strftime("%d/%m/%Y %H:%M UTC")


def fmt_fecha_local(iso):
    dt = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
    return dt.astimezone(timezone(timedelta(hours=-3))).strftime(
        "%d/%m/%Y %H:%M UTC−3")


def fmt_dia(iso):
    return datetime.strptime(str(iso), "%Y-%m-%d").strftime("%d/%m")


def h1(t):
    story.append(Paragraph(esc(t), S["h1"]))


def h2(t):
    story.append(Paragraph(esc(t), S["h2"]))


def p(t):
    story.append(Paragraph(esc(t), S["body"]))


def bullets(items):
    for it in items:
        story.append(Paragraph(esc(it), S["bullet"], bulletText="\u2022"))


def quote(t):
    story.append(Paragraph(esc(t).replace("\n", "<br/>"), S["quote"]))


def code(t):
    story.append(Paragraph(esc(t).replace("\n", "<br/>").replace(" ", "&nbsp;"),
                           S["code"]))


def cols(*fracs):
    return [ANCHO * f for f in fracs]


def tabla(rows, anchos, negrita_primera=False, small=False):
    data = []
    for ri, row in enumerate(rows):
        fila = []
        for ci, cell in enumerate(row):
            if ri == 0:
                est = S["th_s"] if small else S["th"]
            elif negrita_primera and ci == 0:
                est = S["celda_bs"] if small else S["celda_b"]
            else:
                est = S["celda_s"] if small else S["celda"]
            txt = esc(str(cell)).replace("\n", "<br/>")
            fila.append(Paragraph(txt, est))
        data.append(fila)
    t = Table(data, colWidths=anchos, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, FONDO_SUAVE]),
        ("GRID", (0, 0), (-1, -1), 0.4, GRIS_CLARO),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 7))


def fig(path, caption, width_cm=16.5, max_h_mm=115):
    path = Path(path)
    if not path.exists():
        return
    with PILImage.open(path) as im:
        w, h = im.size
    scale = min(width_cm * 10 * mm / w, max_h_mm * mm / h)
    rl = RLImage(str(path), width=w * scale, height=h * scale)
    rl.hAlign = "CENTER"
    story.append(KeepTogether([
        Spacer(1, 4), rl, Spacer(1, 3),
        Paragraph(esc(caption), S["figcap"]), Spacer(1, 7),
    ]))


def fig_grid(items, cols_n=2, captions=True):
    cell_w = ANCHO / cols_n
    rows = []
    for i in range(0, len(items), cols_n):
        row = []
        for j in range(cols_n):
            if i + j >= len(items):
                row.append("")
                continue
            path, caption = items[i + j]
            path = Path(path)
            if not path.exists():
                row.append("")
                continue
            with PILImage.open(path) as im:
                w, h = im.size
            scale = min((cell_w - 9) / w, 70 * mm / h)
            rl = RLImage(str(path), width=w * scale, height=h * scale)
            rl.hAlign = "CENTER"
            if captions:
                row.append([rl, Spacer(1, 3),
                            Paragraph(esc(caption), S["figcap"])])
            else:
                row.append(rl)
        rows.append(row)
    t = Table(rows, colWidths=[cell_w] * cols_n)
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 7))


def pie(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#e2e8f0"))
    canvas.setLineWidth(0.5)
    canvas.line(15 * mm, 14 * mm, A4[0] - 15 * mm, 14 * mm)
    canvas.setFont("DejaVu", 7.1)
    canvas.setFillColor(GRIS)
    canvas.drawString(15 * mm, 10 * mm,
                      "Tucumán Respira — Escuela Técnica N°5 — Equipo 2026")
    canvas.drawRightString(A4[0] - 15 * mm, 10 * mm,
                           "Página %d" % doc.page)
    canvas.restoreState()


# ===================== PORTADA =====================
story.append(Spacer(1, 22))
story.append(Paragraph("INFORME TÉCNICO DEL PROYECTO", S["marca"]))
story.append(Paragraph("Escuela Técnica N°5", S["escuela"]))
story.append(Paragraph("Proyecto: Tucumán Respira 2026", S["proyecto"]))
story.append(Spacer(1, 12))
story.append(Paragraph("Tucumán Respira", S["titulo"]))
story.append(Paragraph(
    "Estación de monitoreo de calidad del aire IoT: panel web, firmwares "
    "Arduino Uno + ESP32 y documentación del equipo.", S["subtitulo"]))
story.append(Spacer(1, 12))
story.append(Paragraph("Equipo de trabajo", S["autor"]))
story.append(Paragraph(
    "Roy Luciano Molina · Maximo Valdez Leguina · Candela Rojas Perassi · "
    "María Pía Olivar · Benicio Gael Pieroni · Joaquín Valdecanto · "
    "Tatiana Maturano · Bautista Argañaraz · Jonás Barreiro", S["equipo"]))
story.append(Paragraph(
    "Documento consolidado por Benicio Gael Pieroni. 29 de octubre de 2026.",
    S["equipo"]))
story.append(Spacer(1, 12))

tabla([
    ["Aspecto", "Detalle"],
    ["Escuela", "Escuela Técnica N°5"],
    ["Proyecto", "Tucumán Respira 2026 — Estación de monitoreo ambiental IoT"],
    ["Entregables",
     "Aplicación web estática (index.html · styles.css · app.js) y dos "
     "firmwares: Arduino Uno (sketch_oct17a) y ESP32 (sketch_oct17b)."],
    ["Fuente de datos",
     "Supabase (PostgreSQL) — tabla «mediciones» — API PostgREST."],
    ["Alcance",
     "Documento único que integra el informe técnico previo, la "
     "documentación del equipo, el hardware, los firmwares, el panel web, "
     "los datos y las correcciones recientes."],
    ["Fecha", "29/10/2026"],
    ["Estado",
     "Implementado, integrado y publicado en GitHub Pages. La versión "
     "corregida del ESP32 fue compilada y cargada."],
    ["Repositorio", "github.com/Benicio54/Tucuman-respira"],
    ["Panel web", "benicio54.github.io/Tucuman-respira"],
], cols(0.19, 0.81), negrita_primera=True)

story.append(Spacer(1, 2))
story.append(Paragraph(
    "Nota de consolidación: este documento reemplaza al informe técnico del "
    "18/10/2026 y reúne la documentación elaborada por el equipo. Las "
    "versiones anteriores se conservan en la carpeta Informes_anteriores/. "
    "La síntesis de 8–10 páginas para el concurso se entrega por separado en "
    "Sintesis_Concurso_Tucuman_Respira.pdf y remite a este informe para el "
    "detalle completo.", S["nota"]))
story.append(PageBreak())

# ===================== ÍNDICE =====================
story.append(Paragraph("Índice de contenidos", S["h1"]))
for t in [
    "1. Resumen ejecutivo",
    "2. Contexto, objetivos y alcance",
    "3. Equipo, roles y metodología",
    "4. Marco de referencia: calidad del aire",
    "5. Arquitectura general y stack tecnológico",
    "6. Hardware: componentes, conexiones y montaje",
    "7. Firmware del Arduino Uno",
    "8. Firmware del ESP32",
    "9. Fuente de datos: Supabase",
    "10. Panel web",
    "11. Métricas, umbrales e ICA",
    "12. Integración y flujo de datos",
    "13. Pruebas, verificaciones y correcciones",
    "14. Resultados y análisis de datos",
    "15. Despliegue y uso",
    "16. Pendientes, recomendaciones y conclusiones",
    "17. Referencias",
    "Anexo A — Configuración y claves",
    "Anexo B — Exportación de datos (CSV / JSON)",
    "Anexo C — Trama de comunicación Uno → ESP32",
    "Anexo D — Registro fotográfico",
    "Anexo E — Material complementario",
    "Anexo F — Esquema de conexiones",
]:
    story.append(Paragraph(esc(t), S["indice"]))
story.append(PageBreak())

# ===================== 1. RESUMEN =====================
h1("1. Resumen ejecutivo")
p("«Tucumán Respira» es una estación de monitoreo ambiental de bajo costo "
  "construida con un Arduino Uno R3 y un ESP32. Mide calidad del aire "
  "(PM2.5, CO y CO₂), variables meteorológicas (temperatura, humedad y "
  "presión), radiación UV y luz ambiental; registra la posición GPS y "
  "publica las lecturas en Supabase. Un panel web estático muestra los "
  "datos en vivo, el histórico, el mapa y el estado de la calidad del aire, "
  "y permite descargar los registros y detener la alarma sonora.")
p("El sistema se organiza en cuatro capas: adquisición (Arduino Uno), "
  "enlace y nube (ESP32), persistencia (Supabase/PostgreSQL) y presentación "
  "(aplicación web). El Uno envía una trama de 9 campos al ESP32 cada 3 s; "
  "el ESP32 la publica en Supabase cada 15 s, calcula el ICA local y "
  "gobierna un zumbador. La web lee Supabase, muestra 8 métricas con "
  "umbrales y fuentes visibles, y para la alarma consulta al ESP32 en la "
  "red local.")
p("Resultados principales")
bullets([
    "Panel público con datos en tiempo real, respaldo por sondeo cada 15 s, "
    "histórico, gráficos de tendencia y mapa con OpenStreetMap.",
    "Ocho métricas con umbrales de referencia (EPA, OSHA/NIOSH, ASHRAE, "
    "OMS y NWS), cada una con su fuente visible.",
    "ICA estilo EPA calculado con PM2.5 y CO; la alarma local replica el "
    "mismo criterio (se activa con ICA > 100 y se corta al bajar de 80).",
    "Descarga pública en CSV y JSON (últimas 100, 500, 1000 o todas las "
    "filas), sin backend propio.",
    "Hardware documentado: sensores, pines, pruebas individuales, "
    "calibración, armado con cables soldados y gabinete impreso en 3D.",
    "Red de configuración temporal: el AP se cierra al conectar y reaparece "
    "si se pierde la red; las credenciales quedan en RAM.",
    "Versión corregida del ESP32 compilada y cargada; se corrigieron el "
    "orden de arranque, la red/AP y el valor por defecto de CO₂.",
    f"Panel publicado en GitHub Pages y base con {fmt_int(DATOS['total'])} "
    f"mediciones reales al {DATOS['fecha_corta']}.",
])
p("El informe integra la documentación del equipo (proceso, componentes, "
  "gabinete y roles), el detalle técnico de los firmwares y del panel, y "
  "las correcciones aplicadas durante la puesta a punto. Los valores de "
  "referencia son orientativos y no constituyen diagnóstico sanitario.")

# ===================== 2. CONTEXTO =====================
h1("2. Contexto, objetivos y alcance")
p("La calidad del aire afecta la salud respiratoria y cardiovascular. La "
  "material particulado fino (PM2.5), el monóxido de carbono (CO) y el "
  "dióxido de carbono (CO₂) son indicadores útiles para evaluar ambientes "
  "interiores y exteriores. Una estación de bajo costo permite observar "
  "tendencias, detectar episodios de ventilación deficiente y acercar los "
  "datos a la comunidad educativa.")
h2("2.1 Problema abordado")
p("El problema abordado es la dificultad de contar con información local, "
  "continua y accesible sobre la calidad del aire y las condiciones "
  "ambientales de la escuela y su entorno. Los datos públicos disponibles "
  "suelen estar dispersos, no tienen resolución local o no resultan fáciles "
  "de interpretar; además, no siempre existe una herramienta propia para "
  "medir, registrar y comparar variables como PM2.5, CO y CO₂. Esa falta de "
  "información dificulta detectar episodios de ventilación deficiente, "
  "relacionar las mediciones con las actividades cotidianas y tomar "
  "decisiones fundamentadas.")
p("El proyecto responde a esa necesidad con una estación de bajo costo, "
  "documentada y replicable, y con un panel que traduce las mediciones en "
  "información comprensible para la comunidad educativa. La estación no "
  "reemplaza una red de monitoreo certificada: busca acercar los datos, "
  "mostrar tendencias y habilitar preguntas concretas sobre el ambiente.")
h2("2.2 Objetivo general")
p("Diseñar, construir y documentar un sistema completo de monitoreo —desde "
  "la adquisición en campo hasta la publicación web— que permita comprender "
  "el estado de la calidad del aire y consultar los datos históricos.")
h2("2.3 Objetivos específicos")
bullets([
    "Medir PM2.5, CO, CO₂, temperatura, humedad, presión, UV y luz.",
    "Registrar la ubicación geográfica de las mediciones con GPS.",
    "Publicar las lecturas en la nube y ofrecer un panel público claro.",
    "Avisar localmente con una alarma sonora y permitir silenciarla desde "
    "la aplicación web.",
    "Permitir la descarga libre de los datos crudos en CSV y JSON.",
    "Documentar el hardware, el proceso de armado, el gabinete y los roles "
    "del equipo.",
])
h2("2.4 Alcance y límites")
p("El informe cubre el hardware, los firmwares, la base de datos, el panel "
  "web, las pruebas y los resultados descriptivos. No incluye calibración "
  "de laboratorio, certificación metrológica, un estudio epidemiológico ni "
  "una campaña prolongada en múltiples puntos. La estación es única y los "
  "datos deben interpretarse como una referencia local.")
h2("2.5 Perfil de usuarios")
p("Público general: docentes, estudiantes y personas técnicas o interesadas "
  "en la calidad del aire. La interfaz prioriza legibilidad, lenguaje claro "
  "y acceso desde cualquier dispositivo.")

# ===================== 3. EQUIPO =====================
h1("3. Equipo, roles y metodología")
p("El proyecto fue realizado por un equipo interdisciplinario. Los roles "
  "surgen de la documentación elaborada por el propio grupo. El equipo contó "
  "con el acompañamiento del docente Tadeo Lobo, de la materia Tecnología de "
  "Control, quien orientó y supervisó el desarrollo del proyecto.")
tabla([
    ["Integrante / docente", "Rol o aporte"],
    ["Roy Luciano Molina", "Diseño del gabinete."],
    ["Maximo Valdez Leguina",
     "Diseño del circuito de conexiones electrónicas."],
    ["Candela Rojas Perassi", "Conexiones físicas del circuito."],
    ["María Pía Olivar", "Armado y presentación del gabinete."],
    ["Benicio Gael Pieroni",
     "Programación de la app web, diseño de la arquitectura y puesta a "
     "punto del proyecto; consolidación de este informe."],
    ["Joaquín Valdecanto", "Colaboración en el proyecto."],
    ["Tatiana Maturano", "Registro fotográfico del proceso."],
    ["Bautista Argañaraz", "Colaboración en el proyecto."],
    ["Jonás Barreiro",
     "Elaboración del informe de sensores, placas y proyecto final."],
    ["Tadeo Lobo (docente)",
     "Tecnología de Control; acompañamiento y supervisión del proyecto."],
], cols(0.28, 0.72), negrita_primera=True)

p("Metodología de trabajo")
p("El equipo se organizó para reunirse en un mismo domicilio y trabajar en "
  "paralelo: una mitad se dedicó al hardware y la otra al software. El "
  "proceso se desarrolló en etapas iterativas:")
bullets([
    "Relevamiento y documentación de todos los componentes, su función y "
    "un diagrama de conexiones.",
    "Prueba individual de cada componente en protoboard, con códigos "
    "separados; soldadura de pines y calibración de los sensores más "
    "sensibles.",
    "Registro de los componentes verificados y conservación de los códigos "
    "individuales para concatenarlos en el producto final.",
    "Integración del circuito y paso del protoboard a un armado con cables "
    "soldados; ajuste progresivo hasta el montaje definitivo.",
    "Desarrollo del código en paralelo al armado y del panel web a mitad "
    "del proceso, hasta conectar la interfaz con los datos reales.",
    "Diseño, medición e impresión 3D del gabinete; distribución de los "
    "componentes, tapa, paredes y agujeros.",
    "Puesta a punto, pruebas de integración, correcciones y documentación.",
])
p("Durante el armado surgieron dos problemas prácticos que quedaron "
  "documentados: no se consiguió el adaptador para conectar el PMS5003 al "
  "protoboard, por lo que se cortaron y soldaron los cables; y los imanes "
  "previstos para la tapa no permitían un cierre adecuado y eran difíciles "
  "de despegar, por lo que se reemplazaron por tornillos.")
fig(FIG / "fig_23.jpeg",
    "Figura 1. Equipo durante el proceso de armado y pruebas.")
fig(FIG / "fig_24.jpeg",
    "Figura 2. Trabajo conjunto en el montaje y la puesta a punto.")

# ===================== 4. MARCO =====================
h1("4. Marco de referencia: calidad del aire")
p("Las métricas se interpretan con estándares de salud y seguridad. El "
  "panel muestra la fuente de cada umbral y el estado general se resume con "
  "un índice tipo ICA (Air Quality Index de la EPA).")
bullets([
    "PM2.5: material particulado fino (≤ 2,5 µm). Se asocia a efectos "
    "respiratorios y cardiovasculares; se evalúa con los tramos del ICA de "
    "la EPA (promedio de 24 h).",
    "CO: monóxido de carbono, gas incoloro e inodoro. Se toma como "
    "referencia el REL de NIOSH (35 ppm, 8 h) y el PEL de OSHA (50 ppm).",
    "CO₂: dióxido de carbono. En interiores es, sobre todo, un indicador de "
    "ventilación; los límites ocupacionales son mucho más altos que los "
    "valores habituales.",
    "UV: radiación ultravioleta medida por el ML8511; se expresa como "
    "irradiancia en mW/cm².",
    "Temperatura, humedad y presión: describen el confort y el contexto "
    "meteorológico; la presión y la luz se muestran como referencia.",
])
p("El ICA se calcula con el subíndice de PM2.5 y el de CO, por "
  "interpolación lineal, y se toma el peor de los dos. Las categorías van "
  "de «Buena» a «Peligrosa». El detalle de los umbrales, los cambios "
  "respecto de versiones anteriores y la tabla del ICA se presentan en la "
  "sección 11.")
p("Los valores son de referencia para interpretar las mediciones y no "
  "constituyen diagnóstico sanitario. El calor real depende también de la "
  "humedad y el viento; la OMS no fija un umbral cuantitativo de humedad, "
  "por lo que los valores altos se rotulan como riesgo de moho.")

# ===================== 5. ARQUITECTURA =====================
h1("5. Arquitectura general y stack tecnológico")
p("La arquitectura es de cuatro capas con comunicación en cascada:")
tabla([
    ["Capa", "Componente", "Función"],
    ["Adquisición", "Arduino Uno R3",
     "Lee los sensores y el GPS; envía una trama de 9 campos por puerto "
     "serie al ESP32 cada 3 s."],
    ["Enlace y nube", "ESP32",
     "Recibe la trama, lee el PMS5003, publica en Supabase por HTTPS, "
     "calcula el ICA local y gobierna el zumbador."],
    ["Persistencia", "Supabase (PostgreSQL)",
     "Almacena la tabla «mediciones» y expone la API PostgREST y Realtime."],
    ["Presentación", "Aplicación web estática",
     "Lee Supabase, renderiza el panel, el histórico, el mapa y las "
     "descargas; consulta al ESP32 para silenciar la alarma."],
], cols(0.16, 0.25, 0.59), negrita_primera=True)
p("Flujo de datos: estación (Arduino Uno → ESP32) → Supabase (PostgreSQL + "
  "Realtime) → navegador (fetch REST + canal Realtime) → interfaz. La alarma "
  "sonora se decide en el ESP32; la web solo envía la orden de silencio al "
  "dispositivo en la red local.")

tabla([
    ["Recurso", "Versión / origen", "Uso en el proyecto"],
    ["HTML5 / CSS3 / JavaScript", "Nativo",
     "Estructura, estilos y lógica del panel."],
    ["Lucide", "unpkg @latest (v1.56.0)", "Iconografía SVG."],
    ["Chart.js", "CDN 4.4.1", "Gráfico de tendencia e históricos."],
    ["Leaflet", "CDN 1.9.4", "Mapa con mosaicos de OpenStreetMap."],
    ["supabase-js", "CDN @supabase/supabase-js@2",
     "Cliente Realtime para nuevas filas."],
    ["Supabase REST", "API PostgREST",
     "Lectura de mediciones y descargas."],
    ["Arduino Uno", "ATmega328P (core AVR 1.8.8)",
     "Adquisición de sensores y GPS; trama serie."],
    ["ESP32", "ESP32 (core 3.3.12)",
     "Wi-Fi/HTTPS, PMS5003, alarma y portal de configuración."],
    ["Supabase", "PostgreSQL / PostgREST", "Almacenamiento y API REST."],
], cols(0.23, 0.29, 0.48), negrita_primera=True)
p("Se optó por librerías livianas cargadas por CDN para mantener la "
  "aplicación en solo tres archivos. Se descartaron frameworks CSS pesados "
  "y Font Awesome; los íconos se resolvieron con Lucide y los estilos con "
  "CSS propio. El mapa pasó de Carto a OpenStreetMap para no depender de "
  "una clave de API. El informe se genera con reportlab 4.1.0 y Pillow "
  "10.2.0.")

# ===================== 6. HARDWARE =====================
h1("6. Hardware: componentes, conexiones y montaje")
p("La estación combina sensores de calidad del aire, clima, UV y luz, un "
  "receptor GPS, dos microcontroladores y un zumbador. La documentación del "
  "equipo relevó cada módulo, sus conexiones y su función.")
h2("6.1 Componentes y función")
tabla([
    ["Componente", "Variable", "Interfaz / pines", "Observaciones"],
    ["BME280 (GY-BME280)", "Temperatura, humedad y presión",
     "I²C: SDA A4, SCL A5; dirección 0x76/0x77",
     "El firmware usa Adafruit_BME280; la documentación del equipo lo "
     "menciona como GY-BMP280."],
    ["MH-Z19C", "CO₂ (ppm)",
     "SoftwareSerial en el Uno: RX 10, TX 11",
     "Sensor NDIR; comando de 9 bytes y respuesta 0xFF 0x86."],
    ["MQ-7", "CO (ppm)",
     "Analógico A0; DO opcional en D9",
     "Calentamiento inicial de 30 s; calibración con R0."],
    ["ML8511 (GY-8511)", "Radiación UV",
     "Salida analógica A2",
     "Se convierte con la referencia real del ADC del Uno (5 V)."],
    ["LDR", "Luz ambiental (lux aprox.)",
     "Analógico A1; DO opcional en D12",
     "Estimación por tramos con map()."],
    ["GPS NEO-6M (GY-GPS6MV2)", "Latitud y longitud",
     "SoftwareSerial en el Uno: RX 7, TX 8",
     "Sentencias GGA/GNGGA; conserva la última coordenada válida."],
    ["PMS5003", "PM2.5 (µg/m³)",
     "ESP32 Serial2: RX 18, TX 5, SET 4",
     "Sensor láser con ventilador; se conecta al ESP32, no al Uno."],
    ["Zumbador pasivo", "Alarma sonora",
     "GPIO 23 del ESP32",
     "Control con tone()/noTone(); 10 minutos de silencio manual."],
    ["Arduino Uno R3 / ESP32", "Control",
     "—",
     "El Uno adquiere; el ESP32 enlaza con la nube y gobierna la alarma."],
], cols(0.20, 0.20, 0.29, 0.31), small=True, negrita_primera=True)

h2("6.2 Conexiones principales")
tabla([
    ["Enlace", "Desde", "Hacia", "Nota"],
    ["Uno ↔ ESP32", "Uno D3 (TX), D2 (RX)",
     "ESP32 GPIO 16 (RX), GPIO 17 (TX)",
     "Trama serie de 9 campos a 9600 baudios."],
    ["GPS", "Módulo TX/RX", "Uno D7 (RX), D8 (TX)",
     "SoftwareSerial; NMEA GGA."],
    ["MH-Z19C", "Módulo TX/RX", "Uno D10 (RX), D11 (TX)",
     "SoftwareSerial; lectura cada 3 s."],
    ["BME280", "SDA/SCL", "Uno A4/A5", "I²C; 3,3 V."],
    ["MQ-7", "AO/DO", "Uno A0 / D9", "Lectura analógica."],
    ["ML8511", "OUT", "Uno A2", "Referencia ADC de 5 V."],
    ["LDR", "AO/DO", "Uno A1 / D12", "Divisor de tensión."],
    ["PMS5003", "TX/RX/SET", "ESP32 GPIO 18 / 5 / 4",
     "Serial2 del ESP32; 5 V."],
    ["Zumbador", "GPIO 23", "Zumbador → GND",
     "Alarma local."],
], cols(0.18, 0.24, 0.28, 0.30), small=True, negrita_primera=True)
p("La conexión completa por pines, con la distribución de alimentación de "
  "5 V, los divisores de nivel y los pines sin conectar, se documenta en el "
  "Anexo F y en las láminas A3 de la carpeta Diseño_Circuito/.")

h2("6.3 Pruebas, calibración y armado")
p("Cada componente se probó por separado en el protoboard con un código "
  "individual. Se soldaron los pines de los módulos que lo necesitaban y se "
  "calibraron los sensores más sensibles. El equipo mantuvo una lista de "
  "componentes verificados y conservó los códigos individuales para "
  "integrarlos después en el firmware final.")
p("En el armado definitivo se reemplazó el protoboard por cables soldados. "
  "El adaptador previsto para el PMS5003 no se consiguió: se cortaron los "
  "cables y se soldaron las puntas. El MQ-7 requiere 30 s de calentamiento "
  "antes de empezar; el ML8511 se corrigió con la referencia de 5 V del "
  "ADC; el BME280 se protege contra valores NaN; y el GPS conserva la "
  "última coordenada válida si pierde el fix.")
p("El gabinete se diseñó después de medir todos los componentes. Se planeó "
  "la distribución interior, la posición de los imanes, la tapa, las paredes "
  "y los agujeros para los sensores y el cableado; luego se imprimió en 3D. "
  "Los imanes no permitían que la tapa cerrara bien y eran difíciles de "
  "despegar, por lo que se optó por tornillos.")
p("El modelo 3D del gabinete se conserva en el repositorio: "
  "Diseño_Hardware/Diseño_Gabinete/Gabinete para tucuman respira.stl "
  "(216 KB). El archivo permite revisar la geometría, reproducir la "
  "impresión y adaptar la distribución interior.")
fig(FIG / "fig_14.jpeg",
    "Figura 3. Gabinete: diseño y terminaciones.")
fig(FIG / "fig_12.jpeg",
    "Figura 4. Gabinete: montaje y distribución interior.")

h2("6.4 Problemas de hardware y soluciones")
tabla([
    ["Problema", "Solución aplicada"],
    ["No se consiguió el adaptador del PMS5003 para el protoboard.",
     "Se cortaron los cables y se soldaron las puntas."],
    ["Los imanes de la tapa no cerraban bien y no se podían despegar.",
     "Se reemplazaron por tornillos."],
    ["El MQ-7 necesita estabilización y calibración.",
     "Calentamiento de 30 s y ajuste con R0; lectura analógica."],
    ["El BME280 puede no detectarse en la dirección esperada.",
     "El firmware prueba 0x76 y 0x77 y avisa por monitor serie."],
    ["El GPS puede perder el fix momentáneamente.",
     "Se conserva y reenvía la última coordenada válida."],
], cols(0.42, 0.58), negrita_primera=True)

# ===================== 7. UNO =====================
h1("7. Firmware del Arduino Uno")
p("El Arduino Uno (sketch_oct17a) lee los sensores ambientales, calcula la "
  "posición GPS y envía una trama de 9 campos al ESP32 cada 3 segundos por "
  "puerto serie a 9600 baudios.")
tabla([
    ["Función", "Sensor / módulo", "Pin o interfaz"],
    ["Clima", "BME280", "I²C A4/A5 (0x76/0x77)"],
    ["CO₂", "MH-Z19C", "SoftwareSerial 10/11"],
    ["CO", "MQ-7", "A0 (DO D9 opcional)"],
    ["UV", "ML8511", "A2"],
    ["Luz", "LDR", "A1 (DO D12 opcional)"],
    ["GPS", "NEO-6M / GY-GPS6MV2", "SoftwareSerial 7/8"],
    ["Enlace", "ESP32", "SoftwareSerial 2/3"],
], cols(0.20, 0.36, 0.44), negrita_primera=True)
p("Funcionamiento")
bullets([
    "El GPS queda como receptor activo; para leer el CO₂ se conmuta "
    "brevemente al puerto del MH-Z19C y se vuelve al GPS.",
    "Se interpretan las sentencias $GPGGA y $GNGGA: se verifica la calidad "
    "del fix y se convierten latitud/longitud de formato NMEA a grados "
    "decimales, con el signo según N/S y E/W.",
    "El MQ-7 espera 30 s de calentamiento. La lectura analógica se convierte "
    "a ppm con Rs/R0 y la curva del sensor.",
    "El ML8511 se convierte con la referencia real de 5 V del ADC: "
    "uv = (V − 0,99) × 15 / (3,3 − 0,99); los valores negativos se llevan a 0.",
    "El BME280 entrega temperatura, humedad y presión; los NaN se "
    "reemplazan por 0 para no enviar valores inválidos.",
    "El LDR se estima por tramos con map() y se envía como lux aproximados.",
    "Cada 3 s se arma la trama de 9 campos y se envía al ESP32.",
])
p("Trama enviada (9 campos separados por coma):")
code("co2,co,temperatura,humedad,presion,uv,lux,latitud,longitud\n"
     "412,3.20,19.9,71,968,0.0,120,-26.83972,-65.29328")
p("Si el MH-Z19C no responde, leerCO2() devuelve 0. El valor inicial de "
  "co2Value es 0: 0 significa «sin lectura», no un valor de 400 ppm. La "
  "última coordenada válida se conserva cuando el GPS pierde el fix; si "
  "nunca hubo fix, se envía 0,0.")
p("El firmware del Uno quedó separado del de la ESP32 en su propia carpeta "
  "(sketch_oct17a). Esto evita el problema que se produjo cuando un archivo "
  "fue reemplazado accidentalmente por el del otro microcontrolador.")

# ===================== 8. ESP32 =====================
h1("8. Firmware del ESP32")
p("El ESP32 (sketch_oct17b) es el enlace con la nube y el controlador de la "
  "alarma. Recibe la trama del Uno, lee el PMS5003, publica el registro en "
  "Supabase, calcula el ICA local y gobierna el zumbador.")
h2("8.1 Conectividad y red de configuración")
p("La conexión se gestiona con una máquina de estados: RED_AP, "
  "RED_CONECTANDO y RED_CONECTADA. Al arrancar, el equipo levanta una red "
  "de configuración temporal (Tucuman-Respira-Config, contraseña "
  "Tucuman2026, IP 192.168.4.1) con portal DNS cautivo. El usuario elige la "
  "red desde el portal; el guardado responde «Conectando…» sin bloquear.")
bullets([
    "Si la conexión se establece, el AP se cierra automáticamente con "
    "detenerAP() y el equipo queda en modo estación (STA).",
    "Si no se conecta en 20 s, se vuelve a levantar el AP para reintentar.",
    "Si la conexión se cae y se confirma la caída durante 5 s, se borran "
    "las credenciales de RAM y se levanta el AP para reconfigurar.",
    "Las credenciales no se guardan en NVS/Preferences: viven en RAM. Al "
    "reiniciar, el equipo vuelve a arrancar en modo AP.",
    "WiFi.persistent(false) y WiFi.setAutoReconnect(false) evitan que la "
    "librería persista credenciales o reconecte por su cuenta; la "
    "reconexión la decide la máquina de estados del firmware.",
    "El orden de arranque es iniciarAP() y luego setupWebServer(), para que "
    "lwIP esté inicializado antes de abrir sockets.",
])
h2("8.2 Publicación en Supabase")
p("Cada 15 s, si hay conexión Wi-Fi, el ESP32 envía un POST HTTPS a la API "
  "REST de Supabase con los encabezados apikey y Authorization (clave "
  "anon). Los campos enviados son co2, co, pm25, temperatura, humedad, "
  "presion, uv, luz, latitud, longitud e ip_dispositivo. La IP local "
  "permite que la web descubra la estación y le envíe la orden de silencio.")
p("El sensor de partículas PMS5003 se lee por Serial2 (RX 18, TX 5, SET 4) "
  "y se publica como PM2.5. El ESP32 calcula el ICA local con los mismos "
  "breakpoints que la web (PM2.5 EPA 2024 y CO con NIOSH REL/OSHA PEL).")
h2("8.3 Alarma y endpoints")
p("El zumbador pasivo está en GPIO 23 y se controla con tone()/noTone(). "
  "La alarma se activa cuando el ICA supera 100 y se corta automáticamente "
  "cuando baja de 80. El silencio manual dura 10 minutos.")
tabla([
    ["Ruta", "Función"],
    ["/", "Portal de configuración (si el AP está activo)."],
    ["/save (POST)", "Guarda SSID y contraseña; responde «Conectando…»."],
    ["/status", "Estado de la estación: Wi-Fi, IP, ICA, alerta, silencio."],
    ["/alarma", "Estado de la alarma y del zumbador (GET/POST/OPTIONS)."],
    ["/silenciar?k=CLAVE", "Silencia el zumbador 10 minutos."],
], cols(0.26, 0.74), negrita_primera=True)
p("Todos los endpoints de control responden con CORS abierto para permitir "
  "el uso desde la aplicación web. El endpoint /silenciar exige la clave "
  "del dispositivo (tucu2026) y está pensado para la red local.")
h2("8.4 Correcciones recientes")
p("Red y AP. La versión anterior mantenía un AP permanente y guardaba las "
  "credenciales en NVS con reconexión automática. La versión corregida usa "
  "un AP temporal, cierra la red al conectar, la reabre si se pierde la "
  "conexión y mantiene las credenciales solo en RAM. El guardado dejó de "
  "bloquear el servidor y el orden de arranque se corrigió.")
p("Reinicio en bucle al iniciar. El equipo se reiniciaba con "
  "rst:0xc (SW_CPU_RESET) antes de imprimir el banner. La causa era abrir "
  "sockets (setupWebServer) antes de inicializar lwIP, que se inicializa "
  "con WiFi.mode()/Network.begin(). La corrección fue llamar a iniciarAP() "
  "antes de setupWebServer(); la versión corregida compila, se cargó y ya "
  "no reproduce el reinicio.")
code("rst:0xc (SW_CPU_RESET)\n"
     "ELF file SHA256: f6d0fd703...\n"
     "Rebooting...")
p("CO₂ por defecto. El firmware usaba currentCO2 = 400 como valor inicial; "
  "si el Uno no estaba conectado, la web mostraba 400 ppm como si fuera una "
  "medición. Ahora currentCO2 = 0 y el 0 significa «sin lectura». En el Uno "
  "también se cambió co2Value = 0; allí el 400 inicial era código muerto "
  "porque se sobrescribía en cada lectura. Un valor real de 400 ppm en aire "
  "limpio es válido y no debe confundirse con el valor por defecto antiguo.")

# ===================== 9. SUPABASE =====================
h1("9. Fuente de datos: Supabase")
p("La información proviene de un proyecto de Supabase (PostgreSQL) con la "
  "API PostgREST habilitada. La tabla utilizada es «mediciones».")
tabla([
    ["Campo", "Tipo", "Significado", "Unidad"],
    ["id", "entero", "Identificador autoincremental.", "—"],
    ["created_at", "timestamp", "Fecha y hora de la lectura (UTC).", "ISO-8601"],
    ["co2", "numérico", "Dióxido de carbono.", "ppm"],
    ["co", "numérico", "Monóxido de carbono.", "ppm"],
    ["pm25", "numérico", "Material particulado fino (PM2.5).", "µg/m³"],
    ["temperatura", "numérico", "Temperatura ambiente.", "°C"],
    ["humedad", "numérico", "Humedad relativa.", "%"],
    ["presion", "numérico", "Presión atmosférica.", "hPa"],
    ["uv", "numérico", "Radiación ultravioleta.", "mW/cm²"],
    ["luz", "numérico", "Luminosidad ambiental.", "lux"],
    ["latitud", "numérico", "Latitud GPS.", "grados"],
    ["longitud", "numérico", "Longitud GPS.", "grados"],
    ["ip_dispositivo", "texto", "IP local actual del ESP32.", "IPv4"],
], cols(0.19, 0.14, 0.49, 0.18), small=True, negrita_primera=True)

p(f"Estado verificado al {fmt_fecha_local(DATOS['generated_at_local'])} "
  "(snapshot; el conteo es dinámico)")
tabla([
    ["Métrica", "Valor"],
    ["Filas totales", fmt_int(DATOS["total"])],
    ["Primera lectura", fmt_fecha_utc(DATOS["first_created_at"])],
    ["Última lectura", f"{fmt_fecha_utc(DATOS['last_created_at'])} "
                      f"({fmt_fecha_local(DATOS['last_created_at'])})"],
    ["Filas válidas para análisis",
     f"{fmt_int(DATOS['valid'])} ({fmt_pct(DATOS['pct']['valid'])})"],
    ["Filas históricas (co2=400, temp=0)",
     f"{fmt_int(DATOS['legacy'])} ({fmt_pct(DATOS['pct']['legacy'])})"],
    ["Filas fuera de rango",
     f"{fmt_int(DATOS['invalid'])} ({fmt_pct(DATOS['pct']['invalid'])})"],
    ["Lecturas con coordenadas",
     f"{fmt_int(DATOS['coords'])} ({fmt_pct(DATOS['pct']['coords'])})"],
    ["Lecturas con ip_dispositivo",
     f"{fmt_int(DATOS['ip'])} ({fmt_pct(DATOS['pct']['ip'])})"],
], cols(0.55, 0.45), negrita_primera=True)
p("La columna ip_dispositivo permite que la aplicación descubra sola la "
  "dirección de la estación en la red local y, con ella, detener el "
  "zumbador. La API Realtime permite que el panel reciba nuevas filas sin "
  "recargar la página; el sondeo cada 15 s funciona como respaldo.")
p("Calidad de datos")
bullets([
    f"Las {fmt_int(DATOS['legacy'])} filas con co2=400 y temperatura=0 "
    "provienen del valor por defecto antiguo, cuando el ESP32 publicaba sin "
    "datos frescos del Uno. No se eliminaron de la base; se conservan como "
    "registro histórico.",
    f"Se excluyeron {fmt_int(DATOS['invalid'])} filas con valores fuera de "
    "rango físico (temperatura de miles de grados negativos, humedad mayor "
    "a 100 %, UV o luz desmesurados) para el análisis descriptivo; no se "
    "borraron de la base.",
    "Las primeras mediciones no tenían GPS; la cobertura de coordenadas fue "
    "mejorando con el firmware que conserva la última posición válida.",
    "La cobertura de ip_dispositivo es parcial porque la columna se agregó "
    "después de las primeras campañas.",
    "Un CO₂ de 400 ppm en aire limpio es un valor real; el problema era el "
    "400 usado como valor inicial cuando no había lectura.",
])
_ult = DATOS["last_valid"]
p(f"Ejemplo de la última fila válida (id {_ult['id']}): CO₂ "
  f"{fmt_dec(_ult['co2'], 0)} ppm; CO {fmt_dec(_ult['co'], 2)} ppm; PM2.5 "
  f"{fmt_dec(_ult['pm25'], 0)} µg/m³; temperatura "
  f"{fmt_dec(_ult['temperatura'], 1)} °C; humedad "
  f"{fmt_dec(_ult['humedad'], 0)} %; presión {fmt_dec(_ult['presion'], 0)} "
  f"hPa; UV {fmt_dec(_ult['uv'], 1)} mW/cm²; luz "
  f"{fmt_dec(_ult['luz'], 0)} lux; latitud "
  f"{fmt_dec(_ult['latitud'], 5)}; longitud "
  f"{fmt_dec(_ult['longitud'], 5)}; IP "
  f"{_ult.get('ip_dispositivo') or '—'}.")

# ===================== 10. PANEL =====================
h1("10. Panel web")
p("La aplicación es estática (HTML + CSS + JavaScript) y se publica en "
  "GitHub Pages. Lee Supabase por REST y Realtime y no tiene backend "
  "propio. El panel está disponible en "
  "https://benicio54.github.io/Tucuman-respira/.")
h2("10.1 Encabezado y estado de conexión")
bullets([
    "Barra superior fija con la identidad «Tucumán Respira»; el logo "
    "recarga la página.",
    "Insignia de conexión con color y tiempo relativo: en vivo, retraso o "
    "sin conexión.",
    "Última actualización con fecha y hora completas.",
    "Botones de descarga, cambio de tema, información y enlace a GitHub.",
])
h2("10.2 Banner de calidad del aire y tarjetas")
bullets([
    "Número ICA grande, categoría, descripción, recomendación sanitaria e "
    "indicador de la alerta del equipo.",
    "Ocho tarjetas (CO₂, CO, PM2.5, temperatura, humedad, presión, UV y "
    "luz) con valor, unidad, etiqueta y barra de nivel.",
    "Las tarjetas se resaltan cuando alcanzan un nivel peligroso; al tocar "
    "una se abre su histórico.",
])
h2("10.3 Resumen, tendencia e histórico")
bullets([
    "Mín./máx. de temperatura, pico de PM2.5, promedio de CO₂ y humedad de "
    "las últimas 100 lecturas.",
    "Pestañas Aire (PM2.5 y CO), Clima (temperatura y humedad), Gases "
    "(CO₂ y CO) y Luz/UV.",
    "El modal de histórico muestra actual, mín., promedio y máx., permite "
    "elegir 20/50/100 puntos y construye el gráfico con el modal abierto "
    "para evitar gráficos colapsados.",
])
h2("10.4 Mapa, descargas y alarma")
bullets([
    "Mapa Leaflet con OpenStreetMap, marcador de la estación y enlace a "
    "Google Maps; usa la última coordenada válida si la lectura reciente "
    "no tiene GPS.",
    "Descarga CSV (BOM UTF-8, separador «;») y JSON; rangos de 100, 500, "
    "1000 o todas las filas, con paginación para el conjunto completo.",
    "El botón «Detener zumbador» obtiene la IP desde ip_dispositivo "
    "(fallback 192.168.4.1) y llama a /silenciar?k=tucu2026; el silencio "
    "dura 10 minutos.",
    "Tema claro/oscuro persistente; gráficos y mapa se recolorean al "
    "cambiar.",
])
h2("10.5 Estados y comportamiento offline")
tabla([
    ["Situación", "Comportamiento de la interfaz"],
    ["Cargando", "Tarjetas «esqueleto» animadas; indicador «Conectando…»."],
    ["En vivo (≤ 120 s)", "Indicador verde con pulso; «En vivo · hace X»."],
    ["Retraso (≤ 300 s)", "Indicador ámbar; «Retraso · hace X»."],
    ["Sin conexión (> 300 s)", "Indicador rojo; aviso con la última lectura."],
    ["Sin datos", "Valores «--» y etiqueta «Sin datos»; ICA «--»."],
    ["Campo nulo", "Se muestra «--» solo en esa métrica."],
    ["Sin GPS", "Última coordenada válida o mapa centrado por defecto."],
], cols(0.28, 0.72), negrita_primera=True)
p("Un watchdog actualiza el estado cada segundo y recalcula el tiempo "
  "transcurrido, de modo que el mensaje refleja la realidad aunque no "
  "lleguen datos nuevos.")
h2("10.6 Responsive y seguridad")
tabla([
    ["Ancho", "Cambios principales"],
    ["≤ 1024 px", "Banner y resumen en una columna; sensores en 2 columnas; "
                  "tendencia y mapa apilados."],
    ["≤ 640 px", "Marca compacta; insignia a ancho completo; una columna; "
                 "tipografías y paddings reducidos; gráficos de 240–260 px."],
    ["≤ 400 px", "Botones, tipografías y pestañas más compactos."],
], cols(0.16, 0.84), negrita_primera=True)
p("La clave de Supabase es pública (anon) y de solo lectura; nunca se "
  "expone la clave de servicio. Las consultas son GET y los datos son "
  "públicos. La descarga se arma en el navegador, sin backend. El endpoint "
  "/silenciar exige la clave del dispositivo y está pensado para la red "
  "local. No se almacenan credenciales de usuario ni datos personales.")

# ===================== 11. UMBRALES =====================
h1("11. Métricas, umbrales e ICA")
p("Cada sensor se clasifica con rangos de referencia de fuentes "
  "reconocidas. Todas las métricas tienen niveles que llegan a «peligro», "
  "con la fuente visible en la interfaz. El estado general se calcula con "
  "PM2.5 y CO; las demás métricas marcan su propia alerta.")
tabla([
    ["Métrica", "Unidad", "Umbrales y etiquetas", "Fuente"],
    ["CO₂", "ppm",
     "Bueno ≤800 · Aceptable ≤1000 · Ventilación pobre ≤1500 · Alta (PEL 8 h) "
     "≤5000 · Muy alta (STEL) ≤30000 · Peligro >30000",
     "OSHA/NIOSH · ASHRAE"],
    ["CO (ICA)", "ppm",
     "Bueno ≤4,4 · Moderado ≤34,9 · Dañino ≤50 · Muy dañino ≤100 · "
     "Peligroso ≤200 · Extremo >200",
     "NIOSH REL 35 ppm · OSHA PEL 50 ppm"],
    ["PM2.5 (ICA)", "µg/m³",
     "Bueno ≤9,0 · Moderado ≤35,4 · Grupos sensibles ≤55,4 · Dañino ≤125,4 · "
     "Muy dañino ≤225,4 · Peligroso >225,4",
     "EPA AQI 2024 (24 h)"],
    ["Temperatura", "°C",
     "Hipotermia ≤0 · Frío ≤10 · Confortable ≤27 · Precaución por calor ≤32 · "
     "Extrema precaución ≤39 · Peligro ≤52 · Peligro extremo >52",
     "NWS/OSHA · NIOSH"],
    ["Humedad", "%",
     "Muy seco ≤20 · Seco ≤30 · Ideal ≤60 · Algo húmedo ≤70 · Riesgo de moho "
     "≤85 · Alto riesgo de moho >85",
     "OMS · ASHRAE"],
    ["Presión", "hPa", "Baja ≤1004,9 · Normal ≤1020 · Alta >1020",
     "Informativo"],
    ["UV", "mW/cm²", "Bajo ≤1 · Moderado ≤3 · Alto ≤6 · Muy alto ≤10 · "
                     "Extremo >10", "Sensor ML8511"],
    ["Luz", "lux", "Oscuridad ≤9,9 · Penumbra ≤99,9 · Interior ≤499 · "
                   "Pleno sol >499", "Informativo"],
], cols(0.14, 0.09, 0.54, 0.23), small=True, negrita_primera=True)

h2("11.1 Cambios respecto de versiones anteriores")
tabla([
    ["Métrica", "Antes", "Ahora"],
    ["CO₂", "Bueno ≤800 · Aceptable ≤1000 · Ventilar ≤2000 · Muy alto ≤5000 · "
            "Riesgo >5000",
     "Bueno ≤800 · Aceptable ≤1000 · Ventilación pobre ≤1500 · Alta (PEL 8 h) "
     "≤5000 · Muy alta (STEL) ≤30000 · Peligro >30000"],
    ["CO (ICA)", "Bueno ≤4,4 · Moderado ≤9,4 · Grupos sensibles ≤12,4 · "
                 "Dañino ≤15,4 · Muy dañino ≤30,4 · Peligroso ≤50,4",
     "Bueno ≤4,4 · Moderado ≤34,9 · Dañino ≤50 · Muy dañino ≤100 · "
     "Peligroso ≤200 · Extremo >200"],
    ["Temperatura", "Frío ≤16,9 · Fresco ≤19,9 · Confortable ≤26 · "
                    "Cálido ≤29,9 · Extremo >29,9",
     "Hipotermia ≤0 · Frío ≤10 · Confortable ≤27 · Precaución por calor ≤32 · "
     "Extrema precaución ≤39 · Peligro ≤52 · Peligro extremo >52"],
    ["Humedad", "Seco ≤29,9 · Ideal ≤60 · Húmedo >60",
     "Muy seco ≤20 · Seco ≤30 · Ideal ≤60 · Algo húmedo ≤70 · Riesgo de moho "
     "≤85 · Alto riesgo de moho >85"],
], cols(0.14, 0.40, 0.46), small=True, negrita_primera=True)
p("PM2.5 no cambió frente a la norma EPA AQI 2024. El UV dejó de expresarse "
  "como índice adimensional y ahora se muestra como irradiancia en mW/cm² "
  "(lectura cruda del ML8511, corregida con la referencia de 5 V del ADC). "
  "En CO se elevó el umbral de «dañino» de 15,4 a 35 ppm (NIOSH REL, 8 h) "
  "para que la alarma no se dispare con valores bajos. Se activó el "
  "resaltado de alerta para CO₂, temperatura y humedad. Presión y luz "
  "quedaron como referencia porque no tienen un umbral de peligro real.")
h2("11.2 Índice de Calidad del Aire (ICA)")
tabla([
    ["Rango ICA", "Categoría", "Descripción"],
    ["0 – 50", "Buena", "Calidad satisfactoria; riesgo bajo."],
    ["51 – 100", "Moderada", "Aceptable; personas muy sensibles podrían "
                              "notar molestias leves."],
    ["101 – 150", "Dañina para grupos sensibles",
     "Los grupos sensibles pueden experimentar efectos."],
    ["151 – 200", "Dañina", "Todos pueden comenzar a sentir efectos."],
    ["201 – 300", "Muy dañina", "Riesgo para toda la población."],
    ["301 – 500", "Peligrosa", "Condiciones de emergencia sanitaria."],
], cols(0.16, 0.30, 0.54), negrita_primera=True)
p("El subíndice se obtiene por interpolación lineal dentro del tramo. Por "
  "ejemplo, PM2.5 = 12 µg/m³ cae en 9,1–35,4 → subíndice 51–100. El índice "
  "global es el peor de PM2.5 y CO. La alarma se activa con ICA > 100 y se "
  "corta al bajar de 80. En CO, el subíndice supera 100 recién a partir de "
  "35 ppm; por debajo de ese valor el CO no activa la alarma por sí solo.")
p("Notas")
bullets([
    "Los valores son de referencia y no constituyen diagnóstico sanitario.",
    "El calor real depende de la humedad y el viento; aquí se evalúa por "
    "temperatura seca.",
    "La OMS no fija un umbral cuantitativo de humedad; los valores altos "
    "indican riesgo de moho.",
    "El CO₂ alto es peligroso en niveles ocupacionales; en interiores es "
    "ante todo un indicador de ventilación.",
    "Presión y luz se muestran como referencia: no existe un umbral de "
    "peligro para la salud en esos rangos.",
])

# ===================== 12. INTEGRACIÓN =====================
h1("12. Integración y flujo de datos")
bullets([
    "El Arduino Uno adquiere los sensores y el GPS y envía la trama de 9 "
    "campos al ESP32 cada 3 s.",
    "El ESP32 recibe la trama, lee el PMS5003, calcula el ICA local y "
    "publica el registro en Supabase cada 15 s, incluida su IP local.",
    "La app web lee Supabase por REST y Realtime, muestra los datos y marca "
    "el nivel de cada métrica y el estado general.",
    "Si el ICA supera 100, el ESP32 activa el zumbador; la app ofrece el "
    "botón «Detener zumbador».",
    "El botón llama a /silenciar con la clave del dispositivo y silencia la "
    "alarma durante 10 minutos.",
])
tabla([
    ["Etapa", "Frecuencia / tiempo"],
    ["Trama Uno → ESP32", "Cada 3 s; 9600 baudios."],
    ["Publicación en Supabase", "Cada 15 s si hay Wi-Fi."],
    ["Sondeo de respaldo de la web", "Cada 15 s; Realtime para nuevas filas."],
    ["Silencio manual de la alarma", "10 minutos."],
    ["Tiempo de intento de conexión Wi-Fi", "20 s; luego vuelve el AP."],
    ["Confirmación de caída de la red", "5 s; luego vuelve el AP."],
], cols(0.52, 0.48), negrita_primera=True)
p("Requisitos de red: el ESP32 y el dispositivo que usa la app deben estar "
  "en la misma red local para el control del zumbador. Si la estación está "
  "en modo AP, la IP por defecto es 192.168.4.1. La app se sirve por HTTP "
  "(Live Server o GitHub Pages), por lo que la llamada al ESP32 por HTTP no "
  "presenta problemas de contenido mixto.")
p("Limitación conocida: el ESP32 publica cada 15 s mientras haya Wi-Fi, "
  "aunque no haya una trama nueva del Uno. Esto puede generar filas "
  "repetidas o con datos no actualizados. Con el cambio de CO₂ a 0, al "
  "menos no se publica un 400 falso; queda pendiente agregar una marca de "
  "frescura antes de subir.")

# ===================== 13. PRUEBAS =====================
h1("13. Pruebas, verificaciones y correcciones")
p("Se realizaron verificaciones estáticas, de compilación, de API y de "
  "renderizado. La versión corregida del ESP32 fue compilada y cargada; la "
  "prueba de alarma en campo queda pendiente.")
tabla([
    ["Verificación", "Resultado"],
    ["Sintaxis del JavaScript (esprima).", "Correcta, sin errores."],
    ["Identificadores usados por app.js presentes en el HTML.", "Todos."],
    ["Respuesta de la API REST de Supabase.", "HTTP 200; columnas esperadas."],
    ["Escritura real en Supabase (POST).", "HTTP 201; registro creado."],
    ["Compilación del firmware del Arduino Uno (avr-g++).", "Sin errores."],
    ["Compilación y carga del ESP32 (xtensa-esp32-elf-g++).",
     "Sin errores; versión corregida compilada y cargada."],
    ["Parser NMEA del GPS (prueba automatizada).",
     "Correcto (N/S/E/W y sin fix)."],
    ["Renderizado del panel (navegador headless).",
     "Sin errores de JavaScript; mapa y tarjetas correctos."],
    ["Columna ip_dispositivo en Supabase.",
     "Operativa; el ESP32 publica su IP."],
    ["Umbral de CO y disparo de la alarma local.",
     "CO «dañino» desde 35 ppm (NIOSH REL)."],
    ["Panel publicado en GitHub Pages.", "HTTP 200."],
    ["Revisión estática de la versión corregida.",
     "Delimitadores balanceados; una sola WiFi.begin(); sin marcadores "
     "prohibidos; CO₂ inicial en 0."],
    ["Prueba de alarma en campo.", "Pendiente."],
], cols(0.56, 0.44), negrita_primera=True)

h2("13.1 Correcciones durante el desarrollo")
tabla([
    ["Problema", "Causa", "Solución"],
    ["Modales encimados o que no se cerraban.",
     "Reglas CSS .modal con display:grid/flex pisaban [hidden].",
     "Se agregó [hidden]{display:none !important}."],
    ["Gráfico del histórico colapsado en móvil.",
     "Se creaba con el modal oculto (sin tamaño).",
     "Abrir modal → crear gráfico → redimensionar."],
    ["Botón de GitHub vacío.",
     "Lucide ya no incluye íconos de marcas.",
     "Se incorporó el logo de GitHub como SVG propio."],
    ["Aviso offline desbordado en el celular.",
     "Caja fuera del contenedor y sin márgenes.",
     "Se envolvió en un .container."],
    ["Logo del encabezado enlazaba a la raíz.",
     "Era un href a «./»; al abrir como archivo mostraba el directorio.",
     "Se convirtió en botón con location.reload()."],
    ["Paneles de Tendencia/GPS fuera de la tarjeta.",
     "El lienzo de Chart.js tiene ancho intrínseco de 300 px.",
     "Grillas minmax(0, …) y min-width:0."],
    ["Umbrales sin respaldo y etiquetas inexactas.",
     "Rangos elegidos a criterio propio.",
     "Se recalibraron con OSHA/NIOSH, EPA, OMS, NWS y ASHRAE."],
    ["Mapa con «API key required».",
     "Los mosaicos de Carto requieren clave.",
     "Se cambió a OpenStreetMap."],
    ["Descarga JSON entrecortada.",
     "Pretty-print con muchos registros y MIME sin charset.",
     "JSON sin indentación y application/json;charset=utf-8."],
    ["Modal de descarga desbordado en Chrome Android.",
     "Grillas 1fr que no podían encogerse.",
     "minmax(0,1fr), min-width:0 y overflow-x:hidden."],
    ["Texto «JSON (datos crudos)» cortado.",
     "Modal demasiado angosto (420 px).",
     "Se ensanchó a 560 px."],
    ["HTTP 400 al publicar.",
     "Se enviaba un campo «aqi» inexistente.",
     "Se eliminó del payload."],
    ["Lecturas desalineadas.",
     "El Uno enviaba 8 campos y el ESP32 interpretaba 7.",
     "Se unificó la trama en 9 campos."],
    ["Coordenadas (0,0) en la base.",
     "El GPS enviaba 0,0 al perder el fix.",
     "El Uno conserva y reenvía la última coordenada válida."],
    ["Sketch del Uno sobrescrito.",
     "Reemplazo accidental por el de la ESP32.",
     "Se restauró y se separaron en carpetas propias."],
    ["Reinicio en bucle del ESP32.",
     "Sockets abiertos antes de inicializar lwIP.",
     "iniciarAP() antes de setupWebServer()."],
    ["AP permanente y credenciales en NVS.",
     "Diseño anterior de red.",
     "AP temporal, credenciales en RAM, sin auto-reconexión de librería."],
    ["CO₂ 400 falso sin datos del Uno.",
     "Valor inicial 400 en el ESP32.",
     "CurrentCO2 = 0; 0 significa «sin lectura»."],
], cols(0.27, 0.33, 0.40), small=True, negrita_primera=True)

# ===================== 14. RESULTADOS =====================
h1("14. Resultados y análisis de datos")
_s = DATOS["stats"]
_e = DATOS["exceed"]
_m = DATOS["max_daily"]
p(f"Al {fmt_fecha_local(DATOS['generated_at_local'])} la base contiene "
  f"{fmt_int(DATOS['total'])} filas. Después de separar "
  f"{fmt_int(DATOS['legacy'])} filas históricas y "
  f"{fmt_int(DATOS['invalid'])} filas con valores fuera de rango, quedan "
  f"{fmt_int(DATOS['valid'])} lecturas válidas para el análisis descriptivo "
  f"({fmt_pct(DATOS['pct']['valid'])} del total). De ellas, "
  f"{fmt_int(DATOS['coords'])} tienen coordenadas GPS y "
  f"{fmt_int(DATOS['ip'])} registran IP del dispositivo.")
p(f"El período analizado va del {fmt_fecha_utc(DATOS['first_created_at'])} "
  f"al {fmt_fecha_utc(DATOS['last_created_at'])}. La tabla siguiente resume "
  "la distribución de las variables en las lecturas válidas.")
h2("14.1 Estadísticas descriptivas")
tabla([
    ["Variable", "Unidad", "Mín.", "Mediana", "P75", "Máx."],
    ["CO₂", "ppm", fmt_var("co2", _s["co2"]["min"]),
     fmt_var("co2", _s["co2"]["median"]), fmt_var("co2", _s["co2"]["p75"]),
     fmt_var("co2", _s["co2"]["max"])],
    ["CO", "ppm", fmt_var("co", _s["co"]["min"]),
     fmt_var("co", _s["co"]["median"]), fmt_var("co", _s["co"]["p75"]),
     fmt_var("co", _s["co"]["max"])],
    ["PM2.5", "µg/m³", fmt_var("pm25", _s["pm25"]["min"]),
     fmt_var("pm25", _s["pm25"]["median"]),
     fmt_var("pm25", _s["pm25"]["p75"]), fmt_var("pm25", _s["pm25"]["max"])],
    ["Temperatura", "°C", fmt_var("temperatura", _s["temperatura"]["min"]),
     fmt_var("temperatura", _s["temperatura"]["median"]),
     fmt_var("temperatura", _s["temperatura"]["p75"]),
     fmt_var("temperatura", _s["temperatura"]["max"])],
    ["Humedad", "%", fmt_var("humedad", _s["humedad"]["min"]),
     fmt_var("humedad", _s["humedad"]["median"]),
     fmt_var("humedad", _s["humedad"]["p75"]),
     fmt_var("humedad", _s["humedad"]["max"])],
    ["Presión", "hPa", fmt_var("presion", _s["presion"]["min"]),
     fmt_var("presion", _s["presion"]["median"]),
     fmt_var("presion", _s["presion"]["p75"]),
     fmt_var("presion", _s["presion"]["max"])],
    ["UV", "mW/cm²", fmt_var("uv", _s["uv"]["min"]),
     fmt_var("uv", _s["uv"]["median"]), fmt_var("uv", _s["uv"]["p75"]),
     fmt_var("uv", _s["uv"]["max"])],
    ["Luz", "lux", fmt_var("luz", _s["luz"]["min"]),
     fmt_var("luz", _s["luz"]["median"]), fmt_var("luz", _s["luz"]["p75"]),
     fmt_var("luz", _s["luz"]["max"])],
], cols(0.24, 0.14, 0.14, 0.16, 0.14, 0.18), small=True,
   negrita_primera=True)
p("Los percentiles resumen las lecturas válidas. La mediana de CO₂ igual a "
  "400 ppm coincide con el valor de referencia del sensor; los valores altos "
  "se asocian a menor renovación de aire. La temperatura, la humedad y la "
  "presión se mantuvieron en rangos compatibles con ambientes interiores y "
  "exteriores de la zona.")

h2("14.2 Interpretación")
bullets([
    f"PM2.5: mediana {fmt_var('pm25', _s['pm25']['median'])} µg/m³ y P75 "
    f"{fmt_var('pm25', _s['pm25']['p75'])} µg/m³. El "
    f"{fmt_pct(_e['pm25']['pct'])} de las lecturas válidas superó "
    "35 µg/m³; el día con mayor mediana diaria fue el "
    f"{fmt_dia(_m['pm25']['date'])} "
    f"({fmt_var('pm25', _m['pm25']['value'])} µg/m³).",
    f"CO: mediana {fmt_var('co', _s['co']['median'])} ppm y P75 "
    f"{fmt_var('co', _s['co']['p75'])} ppm. El "
    f"{fmt_pct(_e['co']['pct'])} superó 35 ppm; la mayor mediana diaria fue "
    f"el {fmt_dia(_m['co']['date'])} "
    f"({fmt_var('co', _m['co']['value'])} ppm).",
    f"CO₂: mediana {fmt_var('co2', _s['co2']['median'])} ppm y P75 "
    f"{fmt_var('co2', _s['co2']['p75'])} ppm. El "
    f"{fmt_pct(_e['co2']['pct'])} superó 1000 ppm; la mayor mediana diaria "
    f"fue el {fmt_dia(_m['co2']['date'])} "
    f"({fmt_var('co2', _m['co2']['value'])} ppm).",
    "Temperatura, humedad y presión: los rangos observados son estables y "
    "sirven como contexto meteorológico; no se usan para diagnosticar "
    "confort ni salud.",
    "UV y luz: el UV máximo fue "
    f"{fmt_var('uv', _s['uv']['max'])} mW/cm² y la luz llegó a "
    f"{fmt_var('luz', _s['luz']['max'])} lux. Son valores de referencia, no "
    "una evaluación de exposición.",
])
fig(FIG / "datos_pm25_co.png",
    "Figura 5. Mediana diaria de PM2.5 y CO en los días con registro. Las "
    "líneas punteadas marcan 35 µg/m³ y 35 ppm.")
fig(FIG / "datos_excedencias.png",
    "Figura 6. Porcentaje de lecturas válidas que superan cada umbral de "
    "referencia.")
p("En conjunto, la mayoría de las lecturas se mantuvo por debajo de los "
  "umbrales, pero aparecen episodios puntuales de PM2.5 y CO que justifican "
  "seguir midiendo y ventilar. El 10/10 y el 20/10 concentraron las medianas "
  "diarias más altas de PM2.5; el 17/10, la de CO. El CO₂ muestra una base "
  "de 400 ppm con picos de hasta 796 ppm de mediana diaria, compatibles con "
  "momentos de menor ventilación.")
p("Ejemplo de ICA: una lectura con PM2.5 40 µg/m³ y CO 16,36 ppm da un ICA "
  "estimado ≈112, dominado por PM2.5. Es un cálculo ilustrativo de una sola "
  "fila; el ICA de la EPA se basa en promedios de 24 h y 8 h, por lo que no "
  "reemplaza una evaluación sanitaria.")

h2("14.3 Calidad y limitaciones")
bullets([
    f"{fmt_int(DATOS['legacy'])} filas ({fmt_pct(DATOS['pct']['legacy'])}) "
    "tienen co2=400 y temperatura=0 por el valor inicial antiguo; se "
    "conservan como registro histórico y no se limpiaron.",
    f"{fmt_int(DATOS['invalid'])} filas ({fmt_pct(DATOS['pct']['invalid'])}) "
    "quedaron fuera de los rangos físicos y se excluyeron del análisis; no "
    "se borraron de la base.",
    "La cobertura de GPS e IP es parcial por el orden de incorporación de "
    "las funciones; no invalida las mediciones, pero limita el mapa y el "
    "control remoto en las filas antiguas.",
    "La estación es única y no tiene calibración de laboratorio; los "
    "sensores de bajo costo tienen deriva y precisión limitada.",
    "El envío cada 15 s sin marca de frescura puede repetir datos; se "
    "recomienda corregirlo.",
    "Los valores de PM2.5 y CO son lecturas instantáneas, mientras que el "
    "ICA de la EPA se basa en promedios (24 h y 8 h).",
])
p(f"El sistema cumplió el objetivo de adquirir, publicar y visualizar datos "
  f"reales de forma continua. La base reúne {fmt_int(DATOS['total'])} filas "
  "y el panel responde en GitHub Pages; la alarma local y el control remoto "
  "quedan verificados a nivel de firmware y endpoints, con la prueba de "
  "campo pendiente.")

# ===================== 15. DESPLIEGUE =====================
h1("15. Despliegue y uso")
h2("15.1 Panel web")
bullets([
    "Publicado en https://benicio54.github.io/Tucuman-respira/.",
    "Repositorio: https://github.com/Benicio54/Tucuman-respira.",
    "Desarrollo local con Live Server (VS Code) o "
    "python3 -m http.server 8000 --bind 0.0.0.0.",
    "Requiere internet para las librerías por CDN y la consulta a Supabase.",
    "Para el control del zumbador, el dispositivo debe estar en la misma red "
    "local que el ESP32.",
])
h2("15.2 Compilación y carga")
bullets([
    "Arduino Uno: placa «Arduino Uno», core AVR 1.8.8; librerías Wire, "
    "SoftwareSerial y Adafruit BME280 (con Adafruit Unified Sensor). Abrir "
    "Código_ArduinoUno/sketch_oct17a/sketch_oct17a.ino y cargar.",
    "ESP32: placa «ESP32 Dev Module», core 3.3.12; librerías WiFi, "
    "HTTPClient, ArduinoJson, DNSServer y WebServer (incluidas en el core). "
    "Abrir Código_ESP32/sketch_oct17b/sketch_oct17b.ino y cargar.",
    "Verificar las conexiones: PMS5003 en el ESP32 (18/5/4), enlace serie "
    "Uno↔ESP32 (2/3 ↔ 16/17), GPS (7/8), CO₂ (10/11), BME280 (A4/A5), "
    "MQ-7 (A0), ML8511 (A2), LDR (A1) y zumbador (GPIO 23).",
])
h2("15.3 Configuración de la red")
bullets([
    "Conectar el celular o la PC a Tucuman-Respira-Config (contraseña "
    "Tucuman2026).",
    "Abrir http://192.168.4.1, ingresar SSID y contraseña de la red local y "
    "guardar.",
    "Si el AP desaparece, la conexión fue exitosa; si reaparece, revisar la "
    "contraseña e intentar de nuevo.",
    "Las credenciales viven en RAM: al reiniciar, el equipo vuelve a abrir "
    "el AP. No hay reconexión automática de la librería; si la red se cae, "
    "el AP se reabre para reconfigurar.",
    "La IP local se publica en Supabase (ip_dispositivo) y la web la usa "
    "para el botón de silencio.",
])
p("Mantenimiento: dejar calentar el MQ-7, revisar la calibración en aire "
  "limpio, mantener limpio el ventilador del PMS5003, verificar la antena "
  "del GPS y ajustar los tornillos del gabinete. El sensor de CO₂ y el de "
  "partículas requieren limpieza y recalibración periódicas.")

# ===================== 16. PENDIENTES =====================
h1("16. Pendientes, recomendaciones y conclusiones")
h2("16.1 Pendientes")
tabla([
    ["Tema", "Recomendación"],
    ["Alarma en campo", "Validar el disparo y el corte del zumbador durante "
                        "una presentación real."],
    ["Calibración del MQ-7", "Verificar la calibración en aire limpio para "
                             "evitar lecturas altas constantes."],
    ["CO₂ sin lectura", "Decidir si el panel muestra 0 o «—» cuando no hay "
                        "datos; documentar el criterio."],
    ["Filas históricas", "Evaluar la limpieza o el etiquetado de las 101 "
                         "filas con co2=400 y temp=0."],
    ["Frescura del envío", "Agregar una marca de tiempo/frescura antes de "
                          "publicar para no repetir datos."],
    ["Energía y gabinete", "Revisar alimentación, ventilación y fijaciones; "
                          "evaluar batería o fuente externa."],
    ["Escalado", "Considerar varias estaciones, backend propio, RLS y HTTPS "
                "en el dispositivo."],
], cols(0.26, 0.74), negrita_primera=True)
h2("16.2 Conclusiones")
p("El proyecto logró un sistema completo y funcional: adquisición con dos "
  "microcontroladores, publicación en la nube, panel público, histórico, "
  "mapa, descargas y alarma local con control remoto. La documentación del "
  "equipo permitió recuperar el proceso de armado, los componentes y las "
  "decisiones de hardware, y este informe los integra con el detalle "
  "técnico del software y los datos.")
p("Las principales enseñanzas fueron la importancia de probar los "
  "componentes por separado, de separar los firmwares en carpetas propias, "
  "de inicializar la red antes de abrir sockets y de distinguir un valor "
  "real de un valor por defecto. Las limitaciones —calibración, estación "
  "única, datos instantáneos y filas históricas— quedan explicitadas para "
  "futuras mejoras.")
p("El panel está publicado y la base sigue creciendo con mediciones reales. "
  "La prueba de campo de la alarma y la calibración fina de los sensores "
  "quedan como próximos pasos.")

# ===================== 17. REFERENCIAS =====================
h1("17. Referencias")
bullets([
    "US EPA. Air Quality Index (AQI) — Technical Assistance Document, 2024.",
    "OSHA. 29 CFR 1910.1000 — Air Contaminants.",
    "NIOSH. Pocket Guide to Chemical Hazards (CO, CO₂).",
    "ASHRAE. Standard 62.1 (ventilación) y Standard 55 (confort térmico).",
    "OMS. Directrices mundiales de calidad del aire, 2021.",
    "Winsen. MH-Z19C CO₂ Module — Datasheet.",
    "Plantower. PMS5003 Particulate Matter Sensor — Datasheet.",
    "Adafruit. BME280 Temperature, Humidity and Pressure Sensor.",
    "ML8511 UV Sensor — Datasheet.",
    "MQ-7 Carbon Monoxide Sensor — Datasheet.",
    "u-blox. NEO-6M GPS Module — Datasheet.",
    "Arduino. Documentación del core AVR y de las placas Uno.",
    "Espressif. ESP32 Arduino Core 3.3.12 — Documentación.",
    "Supabase. PostgREST API y Realtime — Documentación.",
    "Chart.js 4.4.1, Leaflet 1.9.4, Lucide y reportlab 4.1.0 — Documentación.",
    "Equipo Tucumán Respira. Documentación del proyecto, 2026.",
])

# ===================== ANEXO A =====================
h1("Anexo A — Configuración y claves")
p("La configuración se centraliza al inicio de app.js en el bloque CONFIG:")
code('const CONFIG = {\n'
     '  supabaseUrl: "https://lskvyvpjjziuclaatrtu.supabase.co",\n'
     '  supabaseKey: "sb_publishable_O9Havbh6tsAZEDA8VFWQzg_LmTmU4mM",\n'
     '  table: "mediciones",\n'
     '  historyLimit: 100,\n'
     '  pollMs: 15000,\n'
     '  staleWarnSeconds: 120,\n'
     '  staleOfflineSeconds: 300,\n'
     '  defaultLat: -26.82414,\n'
     '  defaultLng: -65.2226,\n'
     '  downloadRanges: { "100": 100, "500": 500, "1000": 1000, all: Infinity },\n'
     '  deviceKey: "tucu2026",\n'
     '  deviceIpDefault: "192.168.4.1",\n'
     '  muteMinutes: 10\n'
     '};')
p("La clave de Supabase es pública (anon) y de solo lectura; no debe "
  "reemplazarse por la clave de servicio. La protección de los datos "
  "depende de las políticas RLS del servidor. La clave deviceKey es la que "
  "exige el ESP32 en /silenciar. El AP usa la contraseña Tucuman2026 y la "
  "IP 192.168.4.1.")

# ===================== ANEXO B =====================
h1("Anexo B — Exportación de datos (CSV / JSON)")
p("CSV")
p("El archivo incluye BOM UTF-8 y separador punto y coma (;). Columnas:")
code("id;fecha_hora;pm25_ug_m3;co2_ppm;co_ppm;temperatura_c;humedad_pct;\n"
     "presion_hpa;uv;luz_lux;latitud;longitud")
p("JSON")
p("El archivo contiene el arreglo de registros tal como lo devuelve la API, "
  "con todos los campos de cada medición (incluidos latitud, longitud e "
  "ip_dispositivo). Se genera sin indentación y con codificación UTF-8 para "
  "evitar cortes en archivos grandes. Los rangos de descarga son 100, 500, "
  "1000 o todas las filas; la descarga completa usa paginación.")

# ===================== ANEXO C =====================
h1("Anexo C — Trama de comunicación Uno → ESP32")
p("Comunicación serie a 9600 baudios, una línea de texto por medición, con "
  "9 campos separados por comas:")
tabla([
    ["Posición", "Campo", "Ejemplo"],
    ["1", "CO₂ (ppm)", "412"],
    ["2", "CO (ppm)", "3.20"],
    ["3", "Temperatura (°C)", "19.9"],
    ["4", "Humedad (%)", "71"],
    ["5", "Presión (hPa)", "968"],
    ["6", "Radiación UV (mW/cm²)", "0.0"],
    ["7", "Luz (lux)", "120"],
    ["8", "Latitud (grados decimales)", "-26.83972"],
    ["9", "Longitud (grados decimales)", "-65.29328"],
], cols(0.16, 0.52, 0.32), negrita_primera=True)
p("El ESP32 procesa la trama con una lectura de formato tipo "
  "sscanf(\"%d,%f,%f,%f,%f,%f,%d,%f,%f\") y descarta las tramas inválidas. "
  "Si el MH-Z19C no responde, el primer campo llega en 0.")

# ===================== ANEXO D =====================
h1("Anexo D — Registro fotográfico")
p("Este anexo reúne todo el material gráfico disponible: 16 diagramas, "
  "esquemas y capturas de la documentación del equipo y las 43 fotografías "
  "del archivo del proyecto (F.01–F.43). Las figuras 1 a 4 del cuerpo son "
  "una selección de este mismo conjunto. Las fotografías fueron tomadas por "
  "Tatiana Maturano y el equipo; el orden reproduce la secuencia de los "
  "archivos originales.")
h2("Diagramas, esquemas y capturas")
_diag = [
    "Pruebas iniciales de los sensores.",
    "Calibración de componentes sensibles.",
    "Montaje en protoboard.",
    "Conexión del circuito.",
    "Armado del prototipo.",
    "Cableado y soldadura.",
    "Pruebas de integración.",
    "Desarrollo del firmware.",
    "Panel web.",
    "Pruebas del panel.",
    "Integración de datos.",
    "Gabinete: vista del conjunto.",
    "Conexiones del módulo de clima.",
    "Conexiones del GPS.",
    "Módulos de medición de gases.",
    "Conexionado de sensores.",
]
fig_grid([
    (FIG / f"fig_{i:02d}.jpeg", "")
    for i in range(1, len(_diag) + 1)
], cols_n=2, captions=False)

h2("Proceso de armado y pruebas — 15/10/2026")
fig_grid([
    (FIG / f"foto_{i:02d}.jpeg", f"F.{i:02d}. Registro fotográfico del proceso.")
    for i in range(1, 41)
], cols_n=2)
h2("Puesta a punto — 17/10/2026")
fig_grid([
    (FIG / f"foto_{i:02d}.jpeg", f"F.{i:02d}. Registro fotográfico del proceso.")
    for i in range(41, 43)
], cols_n=2)
h2("Montaje final — 26/10/2026")
fig_grid([
    (FIG / "foto_43.jpeg", "F.43. Registro fotográfico del proceso."),
], cols_n=2)

# ===================== ANEXO E =====================
h1("Anexo E — Material complementario")
p("Los siguientes materiales se conservan en Informes_anteriores/ o en el "
  "equipo. El video no se incluye en el repositorio por su tamaño; se "
  "adjunta al correo de entrega y se menciona aquí para que el material "
  "quede identificado.")
tabla([
    ["Material", "Ubicación / observación"],
    ["Documentación del equipo (10 pp., 15 MB)",
     "Informes_anteriores/Documentacion_equipo_2026-10-15.pdf. Origen del "
     "proceso, componentes, gabinete y roles."],
    ["Prompt para recrear el proyecto",
     "Informes_anteriores/PROMPT_recrear_proyecto.pdf. Versión conservada "
     "del Anexo D del informe del 18/10/2026."],
    ["Informe técnico anterior (18/10/2026)",
     "Informes_anteriores/Informe_Tucuman_Respira_2026-10-18.pdf."],
    ["Síntesis para el concurso (8–10 pp.)",
     "Sintesis_Concurso_Tucuman_Respira.pdf. Resume este informe y remite a "
     "sus secciones para el detalle completo."],
    ["Video del proyecto (2:49, 35 MB)",
     "WhatsApp Video 2026-10-29 at 11.16.07.mp4. Muestra la estación y las "
     "lecturas de todos los sensores; se adjunta al correo de entrega. No "
     "incluido en el repositorio."],
    ["Modelo 3D del gabinete (216 KB)",
     "Diseño_Hardware/Diseño_Gabinete/Gabinete para tucuman respira.stl."],
    ["Fotografías",
     "43 fotografías en figuras/ (foto_01–foto_43) y 16 diagramas, esquemas "
     "y capturas (fig_01–fig_16); los originales quedan en el equipo."],
    ["Esquema de conexiones (A3 + A4)",
     "Diseño_Circuito/Esquema_Conexiones_Tucuman_Respira.pdf. Diagrama de "
     "interconexión, matriz de pines y notas de protección; se reproduce en "
     "el Anexo F."],
], cols(0.30, 0.70), negrita_primera=True)

story.append(PageBreak())

# ===================== ANEXO F =====================
h1("Anexo F — Esquema de conexiones")
p("El esquema se elaboró a partir de los pines efectivamente usados por los "
  "firmwares y de la alimentación común de 5 V. Se entrega en dos formatos: "
  "A3 con dos hojas (diagrama de interconexión y matriz de pines con notas "
  "de montaje) y A4 con el resumen de conexiones para consulta rápida.")
fig(CIRCUITO / "Esquema_Conexiones_Tucuman_Respira_A4.png",
    "Figura F.1. Resumen A4 del esquema de conexiones: alimentación de 5 V, "
    "entradas analógicas, enlaces UART, I²C y control de la alarma.",
    width_cm=16.5, max_h_mm=232)
p("La versión A3 completa se conserva en "
  "Diseño_Circuito/Esquema_Conexiones_Tucuman_Respira.pdf (dos hojas de "
  "420 × 297 mm), junto con los archivos SVG y PNG de cada hoja y el "
  "generador reproducible. La matriz consigna, para cada conexión, el pin "
  "de origen, el pin de destino y la observación técnica; las hojas 1 y 2 "
  "incluyen además las notas de protección de niveles lógicos, la "
  "desacoplamiento de la fuente y los pines que quedan sin conectar.")
p(f"Fin del informe — «Tucumán Respira», Escuela Técnica N°5, "
  f"{DATOS['fecha_corta']}. Documento consolidado por Benicio Gael Pieroni "
  "para el equipo del proyecto. La síntesis para el concurso se entrega por "
  "separado.")

# ===================== BUILD =====================
def main():
    doc = BaseDocTemplate(
        SALIDA, pagesize=A4,
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=16 * mm, bottomMargin=18 * mm,
        title="Informe técnico unificado — Tucumán Respira 2026",
        author="Equipo Tucumán Respira — Escuela Técnica N°5",
        subject="Estación de monitoreo de calidad del aire IoT: hardware, "
                "firmwares, panel web, datos y documentación del equipo",
        keywords="Tucumán Respira, calidad del aire, Arduino Uno, ESP32, "
                 "Supabase, IoT, Escuela Técnica N°5",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
                  id="cuerpo")
    doc.addPageTemplates([PageTemplate(id="todas", frames=[frame],
                                       onPage=pie)])
    doc.build(story)
    print("Generado:", SALIDA)


if __name__ == "__main__":
    main()
