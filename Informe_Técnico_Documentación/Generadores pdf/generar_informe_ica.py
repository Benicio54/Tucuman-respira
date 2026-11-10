#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genera «Informe_ICA_EPA_Tucuman_Respira.pdf» en esta misma carpeta.

Fuente de datos: datos_resumen.json del 29/10/2026 del proyecto
Estación_Climática. Si no se encuentra, usa una copia embebida.
"""

import json
import tempfile
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, HRFlowable, Image as RLImage, KeepTogether,
    PageBreak, PageTemplate, Paragraph, Preformatted, Spacer, Table,
    TableStyle,
)
from reportlab.platypus.flowables import Flowable

BASE = Path(__file__).resolve().parent
SALIDA = BASE / "Informe_ICA_EPA_Tucuman_Respira.pdf"
DATOS_PATH = Path(
    "/home/benicio/Proyectos_Informática/Estación_Climática/"
    "Informe_Técnico_Documentación/Generadores pdf/datos_resumen.json"
)

# Datos

DATOS_FALLBACK = {
    "total": 3197, "valid": 2977, "legacy": 101, "invalid": 119,
    "first_created_at": "2026-10-05T00:45:18+00:00",
    "last_created_at": "2026-10-29T15:14:11+00:00",
    "stats": {
        "co2": {"min": 400, "median": 400, "p75": 476, "max": 5000},
        "co": {"min": 0.1, "median": 21.16, "p75": 25.41, "max": 905.18},
        "pm25": {"min": 0, "median": 20, "p75": 29, "max": 139},
        "temperatura": {"min": 18.5, "median": 20.8, "p75": 23.6, "max": 26.9},
        "humedad": {"min": 45, "median": 66, "p75": 69, "max": 78},
        "presion": {"min": 959, "median": 968, "p75": 969, "max": 1014},
        "uv": {"min": 0, "median": 0.5, "p75": 1.5, "max": 4.4},
        "luz": {"min": 0, "median": 84, "p75": 954, "max": 4035},
    },
    "exceed": {
        "pm25": {"count": 447, "pct": 15.0},
        "co": {"count": 366, "pct": 12.3},
        "co2": {"count": 146, "pct": 4.9},
    },
    "daily": [
        {"date": "2026-10-05", "count": 291, "pm25": 10.0, "co": 0.5, "co2": 454.0},
        {"date": "2026-10-07", "count": 134, "pm25": 9.0, "co": 0.83, "co2": 455.0},
        {"date": "2026-10-10", "count": 99, "pm25": 49.0, "co": 0.69, "co2": 450.0},
        {"date": "2026-10-17", "count": 371, "pm25": 7.0, "co": 35.23, "co2": 400.0},
        {"date": "2026-10-18", "count": 1096, "pm25": 23.0, "co": 24.04, "co2": 400.0},
        {"date": "2026-10-19", "count": 68, "pm25": 17.0, "co": 21.16, "co2": 570.0},
        {"date": "2026-10-20", "count": 146, "pm25": 45.5, "co": 19.63, "co2": 578.0},
        {"date": "2026-10-21", "count": 192, "pm25": 25.0, "co": 18.04, "co2": 796.0},
        {"date": "2026-10-29", "count": 580, "pm25": 18.0, "co": 16.36, "co2": 400.0},
    ],
    "max_daily": {
        "pm25": {"date": "2026-10-10", "value": 49.0},
        "co": {"date": "2026-10-17", "value": 35.23},
        "co2": {"date": "2026-10-21", "value": 796.0},
    },
    "pct": {"valid": 93.1, "legacy": 3.2, "invalid": 3.7, "coords": 75.3, "ip": 62.2},
}


def cargar_datos():
    try:
        return json.loads(DATOS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return DATOS_FALLBACK


DATOS = cargar_datos()

# Tablas EPA

PM25 = [(0.0, 9.0, 0, 50), (9.1, 35.4, 51, 100), (35.5, 55.4, 101, 150),
        (55.5, 125.4, 151, 200), (125.5, 225.4, 201, 300),
        (225.5, 325.4, 301, 500)]
PM10 = [(0, 54, 0, 50), (55, 154, 51, 100), (155, 254, 101, 150),
        (255, 354, 151, 200), (355, 424, 201, 300), (425, 604, 301, 500)]
CO_EPA = [(0.0, 4.4, 0, 50), (4.5, 9.4, 51, 100), (9.5, 12.4, 101, 150),
          (12.5, 15.4, 151, 200), (15.5, 30.4, 201, 300),
          (30.5, 50.4, 301, 500)]
CO_PROY = [(0.0, 4.4, 0, 50), (4.5, 34.9, 51, 100), (35.0, 50.0, 101, 150),
           (50.1, 100.0, 151, 200), (100.1, 200.0, 201, 300),
           (200.1, 500.0, 301, 500)]

CATS = [
    (50, "Buena", "#00E400", "Verde"),
    (100, "Moderada", "#FFFF00", "Amarillo"),
    (150, "Dañina para grupos sensibles", "#FF7E00", "Naranja"),
    (200, "Dañina", "#FF0000", "Rojo"),
    (300, "Muy dañina", "#8F3F97", "Púrpura"),
    (500, "Peligrosa", "#7E0023", "Granate"),
]

PALETA_ACTUAL = [
    ("Buena", "emerald", "#10b981"),
    ("Moderada", "sky", "#38bdf8"),
    ("Dañina grupos sensibles", "amber", "#f59e0b"),
    ("Dañina", "orange", "#fb923c"),
    ("Muy dañina", "rose", "#f43f5e"),
    ("Peligrosa", "fuchsia", "#d946ef"),
]


def subindice(bp, c):
    c = float(c)
    if c <= bp[0][0]:
        return 0
    if c > bp[-1][1]:
        return 500
    for lo, hi, il, ih in bp:
        if lo <= c <= hi:
            return int(round((ih - il) / (hi - lo) * (c - lo) + il))
    return 0


def categoria(aqi):
    for maximo, nombre, hexs, color in CATS:
        if aqi <= maximo:
            return nombre, hexs, color
    return CATS[-1][1], CATS[-1][2], CATS[-1][3]


def fmt(v):
    s = f"{float(v):.2f}".rstrip("0").rstrip(".")
    ent, _, dec = s.partition(".")
    if abs(int(ent)) >= 1000:
        ent = f"{int(ent):,}".replace(",", ".")
    return ent + ("," + dec if dec else "")


def _lin(c):
    c = c / 255.0
    return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4


def luminancia(hexs):
    h = hexs.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contraste(a, b):
    la, lb = luminancia(a), luminancia(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


# Estilos y utilidades

AZUL = colors.HexColor("#0f172a")
VERDE = colors.HexColor("#059669")
GRIS = colors.HexColor("#64748b")
GRIS_CLARO = colors.HexColor("#d7dee8")
FONDO_SUAVE = colors.HexColor("#f8fafc")
FONDO_COD = colors.HexColor("#0f172a")
FONDO_NOTA = colors.HexColor("#ecfdf5")
ROJO_SUAVE = colors.HexColor("#fef2f2")

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
for nombre, archivo in [
    ("DejaVu", "DejaVuSans.ttf"),
    ("DejaVu-Bold", "DejaVuSans-Bold.ttf"),
    ("DejaVu-Oblique", "DejaVuSans-Oblique.ttf"),
    ("DejaVu-BoldOblique", "DejaVuSans-BoldOblique.ttf"),
    ("DejaVuMono", "DejaVuSansMono.ttf"),
    ("DejaVuMono-Bold", "DejaVuSansMono-Bold.ttf"),
]:
    pdfmetrics.registerFont(TTFont(nombre, FONT_DIR / archivo))
pdfmetrics.registerFontFamily(
    "DejaVu", normal="DejaVu", bold="DejaVu-Bold",
    italic="DejaVu-Oblique", boldItalic="DejaVu-BoldOblique",
)
pdfmetrics.registerFontFamily(
    "DejaVuMono", normal="DejaVuMono", bold="DejaVuMono-Bold",
    italic="DejaVuMono", boldItalic="DejaVuMono-Bold",
)

ANCHO = A4[0] - 30 * mm
S = {
    "tag": ParagraphStyle(
        "tag", fontName="DejaVu-Bold", fontSize=8, leading=10,
        textColor=VERDE, spaceAfter=8),
    "title": ParagraphStyle(
        "title", fontName="DejaVu-Bold", fontSize=25, leading=30,
        textColor=AZUL, spaceAfter=8),
    "subtitle": ParagraphStyle(
        "subtitle", fontName="DejaVu", fontSize=11.5, leading=16,
        textColor=GRIS, spaceAfter=14),
    "h1": ParagraphStyle(
        "h1", fontName="DejaVu-Bold", fontSize=14.5, leading=18,
        textColor=AZUL, spaceBefore=12, spaceAfter=6, keepWithNext=1),
    "h2": ParagraphStyle(
        "h2", fontName="DejaVu-Bold", fontSize=10.5, leading=13.5,
        textColor=VERDE, spaceBefore=9, spaceAfter=3, keepWithNext=1),
    "body": ParagraphStyle(
        "body", fontName="DejaVu", fontSize=9.2, leading=13.4,
        textColor=colors.HexColor("#1e293b"), alignment=TA_JUSTIFY,
        spaceAfter=5, splitLongWords=1),
    "small": ParagraphStyle(
        "small", fontName="DejaVu", fontSize=8, leading=11.2,
        textColor=GRIS, alignment=TA_JUSTIFY, spaceAfter=4),
    "bullet": ParagraphStyle(
        "bullet", fontName="DejaVu", fontSize=9.2, leading=13,
        textColor=colors.HexColor("#1e293b"), leftIndent=11,
        bulletIndent=3, spaceAfter=2.5),
    "th": ParagraphStyle(
        "th", fontName="DejaVu-Bold", fontSize=7.6, leading=9.4,
        textColor=colors.white),
    "td": ParagraphStyle(
        "td", fontName="DejaVu", fontSize=8, leading=10.4,
        textColor=colors.HexColor("#1e293b")),
    "td_small": ParagraphStyle(
        "td_small", fontName="DejaVu", fontSize=7.3, leading=9.3,
        textColor=colors.HexColor("#1e293b")),
    "figcap": ParagraphStyle(
        "figcap", fontName="DejaVu-Oblique", fontSize=7.6, leading=10,
        textColor=GRIS, alignment=TA_CENTER, spaceBefore=3, spaceAfter=8),
    "code": ParagraphStyle(
        "code", fontName="DejaVuMono", fontSize=7, leading=9.4,
        textColor=colors.HexColor("#e2e8f0"), backColor=FONDO_COD,
        borderPadding=5, spaceBefore=2, spaceAfter=7),
    "nota": ParagraphStyle(
        "nota", fontName="DejaVu", fontSize=8.6, leading=12,
        textColor=colors.HexColor("#064e3b")),
    "cover_meta": ParagraphStyle(
        "cover_meta", fontName="DejaVu", fontSize=8.4, leading=11.6,
        textColor=colors.HexColor("#1e293b")),
}

story = []


def p(texto, estilo="body"):
    story.append(Paragraph(texto, S[estilo]))


def h1(texto):
    story.append(Paragraph(texto, S["h1"]))


def h2(texto):
    story.append(Paragraph(texto, S["h2"]))


def bullets(items):
    for it in items:
        story.append(Paragraph(it, S["bullet"], bulletText="•"))
    story.append(Spacer(1, 3))


def tabla(data, anchos, small=True, negrita_primera=False, bg=True):
    filas = []
    for i, fila in enumerate(data):
        celdas = []
        for j, celda in enumerate(fila):
            if i == 0:
                celdas.append(Paragraph(str(celda), S["th"]))
            else:
                txt = str(celda)
                if negrita_primera and j == 0:
                    txt = f"<b>{txt}</b>"
                celdas.append(
                    Paragraph(txt, S["td_small"] if small else S["td"]))
        filas.append(celdas)
    t = Table(filas, colWidths=[a * ANCHO for a in anchos], repeatRows=1)
    estilos = [
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("GRID", (0, 0), (-1, -1), 0.4, GRIS_CLARO),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
    ]
    if bg:
        estilos.append(
            ("ROWBACKGROUNDS", (0, 1), (-1, -1),
             [colors.white, FONDO_SUAVE]))
    t.setStyle(TableStyle(estilos))
    story.append(t)
    story.append(Spacer(1, 7))


def nota(titulo, texto):
    contenido = [[Paragraph(f"<b>{titulo}</b> {texto}", S["nota"])]]
    t = Table(contenido, colWidths=[ANCHO])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), FONDO_NOTA),
        ("LINEBEFORE", (0, 0), (0, -1), 2.5, VERDE),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(t)
    story.append(Spacer(1, 8))


def codigo(texto):
    story.append(Preformatted(texto, S["code"]))


def figura(path, caption, width_cm=16.4):
    if not path:
        return
    path = Path(path)
    if not path.is_file():
        return
    with PILImage.open(path) as im:
        w, h = im.size
    escala = min(width_cm * 10 * mm / w, 105 * mm / h)
    img = RLImage(str(path), width=w * escala, height=h * escala)
    img.hAlign = "CENTER"
    story.append(KeepTogether([
        Spacer(1, 5), img, Paragraph(caption, S["figcap"]),
    ]))


class Linea(Flowable):
    def __init__(self, grosor=1.6, color=VERDE, ancho=None):
        super().__init__()
        self.grosor = grosor
        self.color = color
        self.ancho = ancho

    def wrap(self, av_w, av_h):
        self._w = self.ancho or av_w
        return self._w, self.grosor + 4

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.grosor)
        self.canv.line(0, 2, self._w, 2)


# Figuras

def figuras(tmp):
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 8.5,
        "axes.edgecolor": "#cbd5e1",
        "axes.linewidth": 0.6,
    })
    st = DATOS["stats"]

    casos = [
        ("PM2.5\nmediana", st["pm25"]["median"]),
        ("PM2.5\np75", st["pm25"]["p75"]),
        ("PM2.5\nmáx", st["pm25"]["max"]),
        ("CO\nmediana", st["co"]["median"]),
        ("CO\np75", st["co"]["p75"]),
        ("CO\nmáx diario", DATOS["max_daily"]["co"]["value"]),
    ]
    actual = [subindice(PM25, c) if "PM2.5" in n else subindice(CO_PROY, c)
              for n, c in casos]
    epa = [subindice(PM25, c) if "PM2.5" in n else subindice(CO_EPA, c)
           for n, c in casos]

    fig, ax = plt.subplots(figsize=(9.4, 3.7), dpi=200)
    for maximo, _n, hexs, _c in CATS:
        ini = 0 if maximo == 50 else CATS[CATS.index(
            (maximo, _n, hexs, _c)) - 1][0]
        ax.axhspan(ini, maximo, color=hexs, alpha=0.13, zorder=0)

    x = range(len(casos))
    ancho = 0.36
    b1 = ax.bar([i - ancho / 2 for i in x], actual, ancho,
                color="#cbd5e1", edgecolor="#94a3b8", linewidth=0.6,
                label="Criterio actual del proyecto", zorder=3)
    b2 = ax.bar([i + ancho / 2 for i in x], epa, ancho,
                color=[categoria(v)[1] for v in epa],
                edgecolor="#475569", linewidth=0.6,
                label="EPA 2024 (oficial)", zorder=3)

    for barras, vals in ((b1, actual), (b2, epa)):
        for barra, v in zip(barras, vals):
            ax.annotate(str(v), (barra.get_x() + barra.get_width() / 2, v),
                        ha="center", va="bottom", fontsize=7.5,
                        color="#0f172a", xytext=(0, 2),
                        textcoords="offset points")

    ax.axhline(100, color="#334155", linestyle=(0, (4, 3)), linewidth=0.8)
    ax.text(len(casos) - 0.45, 104, "umbral de alerta (100)", fontsize=7,
            ha="right", color="#334155")
    ax.set_xticks(list(x))
    ax.set_xticklabels([n for n, _ in casos], fontsize=7.6)
    ax.set_ylabel("Subíndice ICA")
    ax.set_ylim(0, 520)
    ax.set_xlim(-0.6, len(casos) - 0.4)
    ax.grid(axis="y", color="#e2e8f0", linewidth=0.5, zorder=1)
    ax.set_axisbelow(True)
    ax.legend(loc="upper left", fontsize=7.4, frameon=False)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    fig.tight_layout()
    ruta1 = Path(tmp) / "comparacion.png"
    fig.savefig(ruta1, dpi=200, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(9.4, 1.55), dpi=200)
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 1)
    ax.axis("off")
    for i, (maximo, nombre, hexs, color) in enumerate(CATS):
        ini = 0 if i == 0 else CATS[i - 1][0] + 1
        ax.add_patch(Rectangle((i, 0), 1, 1, facecolor=hexs,
                               edgecolor="white", linewidth=2))
        texto = "#0f172a" if contraste(hexs, "#ffffff") < 4.5 else "#ffffff"
        ax.text(i + 0.5, 0.62, f"{ini}–{maximo}", ha="center", va="center",
                fontsize=8.6, color=texto, fontweight="bold")
        ax.text(i + 0.5, 0.33, color, ha="center", va="center",
                fontsize=7.4, color=texto)
        ax.text(i + 0.5, 0.13, hexs, ha="center", va="center",
                fontsize=6.4, color=texto)
    fig.tight_layout(pad=0.2)
    ruta2 = Path(tmp) / "colores.png"
    fig.savefig(ruta2, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return ruta1, ruta2


# Página

def pie(canvas, doc):
    canvas.saveState()
    canvas.setFont("DejaVu", 7.4)
    canvas.setFillColor(GRIS)
    alto = A4[1] - 11 * mm
    canvas.drawString(15 * mm, alto, "Informe ICA · Tucumán Respira 2026")
    canvas.drawRightString(A4[0] - 15 * mm, alto, "Noviembre 2026")
    canvas.setStrokeColor(GRIS_CLARO)
    canvas.setLineWidth(0.4)
    canvas.line(15 * mm, alto - 3.5 * mm, A4[0] - 15 * mm, alto - 3.5 * mm)
    canvas.drawString(15 * mm, 10 * mm,
                      "Datos del 29/10/2026 · Análisis, sin cambios implementados")
    canvas.drawRightString(A4[0] - 15 * mm, 10 * mm, f"Página {doc.page}")
    canvas.restoreState()


# Contenido

def portada():
    story.append(Spacer(1, 28 * mm))
    p("ESCUELA TÉCNICA N°5 · TUCUMÁN RESPIRA 2026", "tag")
    p("El Índice de Calidad del Aire (ICA)<br/>y su implementación en Tucumán Respira",
      "title")
    p("Cómo se calcula según la EPA, qué mide realmente el PMS5003, "
      "qué falta para un ICA completo y qué colores corresponden a cada umbral.",
      "subtitle")
    story.append(Linea(1.8, VERDE, ANCHO))
    story.append(Spacer(1, 12 * mm))

    meta = [
        ["Proyecto", "Tucumán Respira — estación de monitoreo ambiental IoT"],
        ["Documento", "Informe de análisis del ICA (documento nuevo e independiente)"],
        ["Fecha", "7 de noviembre de 2026"],
        ["Base de datos", f"{DATOS['total']:,} mediciones al 29/10/2026 · "
                          f"{DATOS['valid']:,} válidas".replace(",", ".")],
        ["Criterio", "U.S. EPA — Air Quality Index, revisión 2024"],
        ["Cobertura", "PM2.5 (24 h), PM10 (24 h) y CO (8 h) disponibles; "
                      "O₃, NO₂ y SO₂ ausentes"],
        ["Autoría", "Equipo Tucumán Respira · consolidado por Benicio Gael Pieroni"],
        ["Estado", "Análisis. No modifica el informe técnico, los firmwares "
                   "ni la aplicación."],
    ]
    tabla([["Campo", "Detalle"]] + meta, [0.20, 0.80],
          small=False, negrita_primera=True)

    nota("Alcance.",
         "Este documento responde tres preguntas: cómo se calcula el ICA, "
         "si los sensores del proyecto alcanzan para calcularlo y qué colores "
         "corresponden a cada umbral. Las propuestas de código del Anexo A "
         "son orientativas y no fueron aplicadas.")
    story.append(PageBreak())


def indice():
    h1("Contenido")
    items = [
        ("1", "Resumen ejecutivo"),
        ("2", "Qué es el ICA y por qué no es climático"),
        ("3", "Cálculo oficial EPA 2024"),
        ("4", "El PMS5003: qué mide y qué entrega"),
        ("5", "Auditoría del proyecto y de los datos medidos"),
        ("6", "¿Alcanzan los sensores para calcular el ICA?"),
        ("7", "Colores de referencia y cómo se asignan"),
        ("8", "Hallazgos y recomendaciones"),
        ("9", "Anexo A — Cambios de código propuestos"),
        ("10", "Referencias"),
    ]
    for num, titulo in items:
        story.append(Paragraph(
            f"<b>{num}.</b>&nbsp;&nbsp;{titulo}",
            ParagraphStyle("toc", parent=S["body"], fontSize=10,
                           leading=17, alignment=0)))
    story.append(Spacer(1, 8))
    p("Convenciones: ICA y AQI se usan como sinónimos; «subíndice» es el ICA "
      "calculado para un contaminante; el ICA final es el mayor de los "
      "subíndices. Las concentraciones se expresan en µg/m³ salvo el CO, en ppm.",
      "small")
    story.append(PageBreak())


def seccion_1():
    h1("1. Resumen ejecutivo")
    p("El Índice de Calidad del Aire (ICA) es una escala de comunicación de "
      "riesgo sanitario, no una variable meteorológica. Se calcula a partir de "
      "las concentraciones de contaminantes criterio promediadas en ventanas "
      "de tiempo fijas y se expresa como el peor de sus subíndices. La EPA "
      "define seis categorías con colores normalizados, de verde a granate.")
    p("El proyecto Tucumán Respira calcula un ICA con dos contaminantes: "
      "PM2.5 y CO. La fórmula de interpolación es correcta, pero el tramo de "
      "CO no es el de la EPA —se reemplazó por umbrales de NIOSH/OSHA— y el "
      "panel usa lecturas instantáneas en lugar de promedios de 24 h y 8 h. "
      "El resultado es un indicador útil para comunicar tendencias, pero no "
      "comparable con un ICA oficial.")
    p("El sensor PMS5003 entrega PM1.0, PM2.5 y PM10, además de seis conteos "
      "de partículas. El firmware lee únicamente PM2.5: PM10 está disponible "
      "y se desperdicia. Para un ICA EPA completo faltan O₃, NO₂ y SO₂, que "
      "el PMS5003 no puede medir porque es un sensor óptico de partículas. "
      "El CO₂ del MH-Z19C no forma parte del ICA.")
    p("Los colores del panel tampoco son los oficiales: usa una paleta de "
      "diseño (esmeralda, celeste, ámbar, naranja, rosa, fucsia) en lugar de "
      "verde, amarillo, naranja, rojo, púrpura y granate. La lógica dinámica "
      "—calcular, clasificar y aplicar la clase— está bien resuelta; lo que "
      "no coincide es la paleta ni el criterio numérico del CO.")
    p("Con los datos del 29/10/2026 el contraste es concreto: la mediana de "
      f"PM2.5 ({fmt(DATOS['stats']['pm25']['median'])} µg/m³) da un subíndice de "
      f"{subindice(PM25, DATOS['stats']['pm25']['median'])} en ambos criterios; "
      f"la mediana de CO ({fmt(DATOS['stats']['co']['median'])} ppm) da "
      f"{subindice(CO_PROY, DATOS['stats']['co']['median'])} con el criterio "
      f"actual y {subindice(CO_EPA, DATOS['stats']['co']['median'])} con EPA. "
      "Esa diferencia explica por qué el panel casi nunca sale de «amarillo» "
      "mientras que el criterio oficial llevaría el CO a «púrpura».")

    h2("Veredicto en una tabla")
    tabla([
        ["Pregunta", "Respuesta"],
        ["¿Se puede calcular un ICA EPA completo?", "No. Faltan O₃, NO₂ y SO₂."],
        ["¿Se puede calcular un ICA parcial?", "Sí: PM2.5 + CO (hoy) y "
         "PM2.5 + PM10 + CO (con un cambio menor)."],
        ["¿El ICA actual es comparable con el oficial?", "No: el tramo de CO "
         "no es EPA y no se usan promedios de 24 h / 8 h."],
        ["¿Los colores son los de referencia?", "No: la paleta es de diseño, "
         "no la normalizada por la EPA."],
        ["¿La fórmula de interpolación es correcta?", "Sí, y coincide en "
         "firmware y aplicación."],
        ["¿El PMS5003 alcanza para PM2.5 y PM10?", "Sí, aunque no es un "
         "instrumento de referencia."],
    ], [0.38, 0.62], small=False, negrita_primera=True)

    h2("Cinco acciones de mayor impacto")
    bullets([
        "<b>Rotular el índice.</b> Llamarlo «ICA parcial PM2.5 + CO (EPA)» y "
        "aclarar que es estimado e instantáneo.",
        "<b>Corregir el CO.</b> Volver a los tramos EPA 2024 o documentar que "
        "se usa un índice local basado en NIOSH.",
        "<b>Exponer PM10.</b> El PMS5003 ya lo entrega: solo hay que leerlo y "
        "publicarlo.",
        "<b>Calcular promedios.</b> 24 h para PM y 8 h para CO, en la app o en "
        "una vista de Supabase.",
        "<b>Adoptar la paleta oficial.</b> Seis colores EPA, con texto oscuro "
        "sobre amarillo y claro sobre rojo, púrpura y granate.",
    ])
    story.append(PageBreak())


def seccion_2():
    h1("2. Qué es el ICA y por qué no es climático")
    p("El ICA es un número adimensional entre 0 y 500 que traduce la "
      "concentración de uno o más contaminantes a una categoría de riesgo. "
      "No mide el clima: mide exposición a contaminantes. La temperatura, la "
      "humedad y la presión describen el contexto meteorológico y afectan la "
      "dispersión de los contaminantes, pero no entran en la fórmula del ICA.")
    p("La confusión es frecuente porque el panel muestra juntos el estado del "
      "aire, las variables climáticas y la radiación UV. Son tres capas "
      "distintas: el ICA resume contaminantes criterio; el confort térmico se "
      "evalúa con índices como humidex o sensación térmica; la UV tiene su "
      "propia escala. El CO₂, por su parte, es un indicador de ventilación de "
      "interiores y no es un contaminante criterio del ICA de la EPA.")
    h2("Las seis categorías")
    p("Cada categoría tiene un color y un mensaje sanitario. El color no es "
      "decorativo: la EPA lo normaliza para que cualquier persona reconozca "
      "el nivel sin leer el número. La categoría se obtiene del peor "
      "subíndice, es decir, del contaminante que en ese momento domina el "
      "riesgo.")
    tabla([
        ["ICA", "Categoría EPA", "Mensaje general"],
        ["0–50", "Buena", "Calidad satisfactoria; riesgo bajo."],
        ["51–100", "Moderada", "Aceptable; personas muy sensibles podrían "
         "notar molestias leves."],
        ["101–150", "Dañina para grupos sensibles", "Niños, adultos mayores y "
         "personas con afecciones respiratorias deben reducir el esfuerzo."],
        ["151–200", "Dañina", "Todos pueden comenzar a sentir efectos."],
        ["201–300", "Muy dañina", "Alerta sanitaria para toda la población."],
        ["301–500", "Peligrosa", "Condiciones de emergencia."],
    ], [0.13, 0.30, 0.57], small=False, negrita_primera=True)
    nota("Para qué no sirve.",
         "El ICA no diagnostica enfermedades, no reemplaza una estación de "
         "referencia y no debería compararse entre países sin verificar el "
         "criterio usado. Un ICA calculado con dos contaminantes no es "
         "equivalente al ICA de una red que mide los seis.")


def seccion_3():
    h1("3. Cálculo oficial EPA 2024")
    p("La EPA calcula un subíndice por contaminante con una interpolación "
      "lineal entre los puntos de corte de su tabla. Luego reporta el mayor "
      "de los subíndices. La fórmula es:")
    codigo(
        "I = (I_hi − I_lo) / (C_hi − C_lo) · (C − C_lo) + I_lo\n\n"
        "C      concentración medida (promedio del período)\n"
        "C_lo   punto de corte inferior de concentración\n"
        "C_hi   punto de corte superior de concentración\n"
        "I_lo   índice inferior del tramo\n"
        "I_hi   índice superior del tramo\n\n"
        "ICA = max(I_PM2.5, I_PM10, I_O3, I_CO, I_SO2, I_NO2)"
    )
    p("Antes de interpolar, la EPA trunca la concentración según el "
      "contaminante (por ejemplo, PM2.5 a 0,1 µg/m³ y CO a 0,1 ppm) para que "
      "los valores límite caigan siempre dentro de un tramo. Los promedios "
      "exigidos no son los mismos para todos: PM2.5 y PM10 usan 24 h; CO y "
      "O₃ usan 8 h; NO₂ y SO₂ usan 1 h o 24 h según el nivel.")
    h2("Tabla de puntos de corte (EPA 2024)")
    tabla([
        ["ICA", "PM2.5<br/>24 h", "PM10<br/>24 h", "O₃<br/>8 h", "CO<br/>8 h",
         "SO₂<br/>24 h", "NO₂<br/>1 h", "Categoría"],
        ["0–50", "0,0–9,0", "0–54", "0–54", "0,0–4,4", "0–35", "0–53", "Buena"],
        ["51–100", "9,1–35,4", "55–154", "55–70", "4,5–9,4", "36–75",
         "54–100", "Moderada"],
        ["101–150", "35,5–55,4", "155–254", "71–85", "9,5–12,4", "76–185",
         "101–360", "Dañina grupos sensibles"],
        ["151–200", "55,5–125,4", "255–354", "86–105", "12,5–15,4",
         "186–304", "361–649", "Dañina"],
        ["201–300", "125,5–225,4", "355–424", "106–200", "15,5–30,4",
         "305–604", "650–1.249", "Muy dañina"],
        ["301–500", "225,5–325,4", "425–604", "405–604*", "30,5–50,4",
         "605–1.004", "1.250–2.049", "Peligrosa"],
    ], [0.085, 0.115, 0.105, 0.12, 0.105, 0.115, 0.115, 0.24], small=True)
    p("* Por encima de 300, el O₃ se calcula con el promedio de 1 h; el SO₂ "
      "usa 24 h por encima de 200. Unidades: µg/m³ salvo CO, en ppm.", "small")
    h2("Ejemplo con los datos del proyecto")
    pm = DATOS["stats"]["pm25"]["median"]
    co = DATOS["stats"]["co"]["median"]
    a_pm = subindice(PM25, pm)
    a_co = subindice(CO_EPA, co)
    a_co_proy = subindice(CO_PROY, co)
    tabla([
        ["Paso", "PM2.5", "CO (EPA)", "CO (criterio del proyecto)"],
        ["Concentración", f"{fmt(pm)} µg/m³", f"{fmt(co)} ppm", f"{fmt(co)} ppm"],
        ["Tramo", "9,1–35,4 → 51–100", "15,5–30,4 → 201–300",
         "4,5–34,9 → 51–100"],
        ["Subíndice", str(a_pm), str(a_co), str(a_co_proy)],
        ["Categoría", categoria(a_pm)[2], categoria(a_co)[2],
         categoria(a_co_proy)[2]],
        ["ICA final (peor)", f"{max(a_pm, a_co)} → {categoria(max(a_pm, a_co))[2]}",
         "", ""],
    ], [0.28, 0.24, 0.24, 0.24], small=True, negrita_primera=True)
    p("El cálculo del CO con EPA es: (300 − 201) / (30,4 − 15,5) · "
      f"({fmt(co)} − 15,5) + 201 = {a_co}. El criterio del proyecto, en cambio, "
      f"extiende el tramo «moderado» hasta 34,9 ppm y devuelve {a_co_proy}. "
      "La diferencia de categoría no es cosmética: cambia el mensaje sanitario "
      "y el color que ve el público.")
    nota("Sobre los promedios.",
         "Un ICA de 24 h no se calcula con la lectura del momento. El panel "
         "muestra el valor instantáneo cada 15 s; para hablar de ICA EPA hay "
         "que promediar PM2.5 y PM10 en 24 h y CO en 8 h. Mientras eso no "
         "ocurra, corresponde rotularlo como «estimación instantánea».")


def seccion_4():
    h1("4. El PMS5003: qué mide y qué entrega")
    p("El PMS5003 es un sensor óptico de partículas: un ventilador hace pasar "
      "aire por un haz láser y un fotodiodo mide la luz dispersada. Clasifica "
      "las partículas por tamaño y estima concentraciones másicas. No mide "
      "gases: no puede aportar CO, O₃, NO₂ ni SO₂.")
    p("Cada trama tiene 32 bytes, comienza con 0x42 0x4D y termina con un "
      "checksum. El firmware del ESP32 ya valida longitud y checksum. La "
      "trama contiene dos juegos de valores —«CF=1» y «atmosférico»— y seis "
      "conteos por tamaño:")
    tabla([
        ["Bytes", "Campo", "Unidad", "Uso en el proyecto"],
        ["0–1", "Cabecera 0x42 0x4D", "—", "Sincronización"],
        ["2–3", "Longitud de trama (28)", "bytes", "Validación"],
        ["4–5", "PM1.0 (CF=1)", "µg/m³", "No se usa"],
        ["6–7", "PM2.5 (CF=1)", "µg/m³", "No se usa"],
        ["8–9", "PM10 (CF=1)", "µg/m³", "No se usa"],
        ["10–11", "PM1.0 atmosférico", "µg/m³", "No se usa"],
        ["12–13", "PM2.5 atmosférico", "µg/m³", "<b>Se publica como pm25</b>"],
        ["14–15", "PM10 atmosférico", "µg/m³",
         "<b>Disponible, no se publica</b>"],
        ["16–27", "Conteos >0,3 / 0,5 / 1,0 / 2,5 / 5,0 / 10 µm", "partículas/0,1 L",
         "No se usan"],
        ["28–29", "Versión", "—", "No se usa"],
        ["30–31", "Checksum", "—", "Validación"],
    ], [0.11, 0.39, 0.20, 0.30], small=True)
    p("El firmware lee el valor atmosférico de PM2.5 (bytes 12–13), que es una "
      "estimación corregida para aire ambiente. PM10 está en los bytes 14–15 "
      "y se descarta. Con una línea adicional se podría publicar y usar en el "
      "ICA, sin hardware nuevo.")
    h2("Límites que conviene declarar")
    bullets([
        "No es un instrumento de referencia: su exactitud depende de la "
        "humedad, la temperatura y la composición del aerosol.",
        "La calibración de fábrica es genérica; para comparar con una estación "
        "oficial se requiere co-ubicación y un factor de corrección.",
        "El ventilador y la óptica se ensucian: sin mantenimiento, la lectura "
        "deriva con el tiempo.",
        "Entrega concentraciones másicas estimadas, no masa filtrada; no "
        "sirve para cumplir normativa.",
    ])


def seccion_5():
    h1("5. Auditoría del proyecto y de los datos medidos")
    p("El cálculo está implementado tres veces: en la aplicación "
      "(<font face='DejaVuMono' size='8'>App-Web/app.js</font>), en la copia "
      "publicada (<font face='DejaVuMono' size='8'>docs/app.js</font>) y en el "
      "firmware del ESP32 (<font face='DejaVuMono' size='8'>sketch_oct17b.ino</font>). "
      "Las tres usan la misma fórmula y las mismas tablas. El Arduino Uno no "
      "calcula ICA: solo envía la concentración de CO.")
    h2("5.1 Dónde está cada pieza")
    tabla([
        ["Archivo", "Líneas", "Función"],
        ["App-Web/app.js", "145–155", "AQI_BREAKPOINTS (PM2.5 y CO)"],
        ["App-Web/app.js", "156–164", "AQI_CATEGORIES (categoría y color)"],
        ["App-Web/app.js", "266–271", "computeAQI: máximo de subíndices"],
        ["App-Web/app.js", "346–356", "renderHero: aplica clase de color"],
        ["App-Web/styles.css", "9–15", "Variables de la paleta actual"],
        ["docs/app.js", "145–164", "Copia publicada (duplicada)"],
        ["sketch_oct17b.ino", "113–129", "Tablas BR_PM25 y BR_CO"],
        ["sketch_oct17b.ino", "131–147", "subIndice y calcularAQI"],
        ["sketch_oct17b.ino", "210–212", "Lectura de PM2.5 de la trama"],
        ["sketch_oct17b.ino", "327–337", "Publicación en Supabase"],
        ["sketch_oct17a.ino", "118–125", "Cálculo de CO con MQ-7"],
    ], [0.31, 0.16, 0.53], small=True)
    h2("5.2 El tramo de CO no es EPA")
    p("El informe técnico lo reconoce: «En CO se elevó el umbral de dañino de "
      "15,4 a 35 ppm (NIOSH REL, 8 h) para que la alarma no se dispare con "
      "valores bajos». El efecto es que el subíndice de CO crece mucho más "
      "lento que el oficial. La tabla siguiente compara ambos criterios en "
      "los puntos de corte:")
    tabla([
        ["CO (ppm)", "Subíndice actual", "Categoría actual", "Subíndice EPA",
         "Categoría EPA"],
        ["4,4", "50", "Buena", "50", "Buena"],
        ["9,4", "59", "Moderada", "100", "Moderada"],
        ["12,4", "64", "Moderada", "150", "Dañina grupos sensibles"],
        ["15,4", "69", "Moderada", "200", "Dañina"],
        ["30,4", "93", "Moderada", "300", "Muy dañina"],
        ["35,0", "101", "Dañina grupos sensibles", "346", "Peligrosa"],
        ["50,0", "150", "Dañina grupos sensibles", "496", "Peligrosa"],
    ], [0.16, 0.20, 0.25, 0.18, 0.21], small=True, negrita_primera=True)
    p("Con el criterio actual, 50 ppm de CO —el PEL de OSHA— todavía cae en "
      "«dañina para grupos sensibles» (150). Con EPA, 50 ppm está al borde de "
      "«peligrosa» (496). No son dos formas de decir lo mismo: son dos "
      "índices distintos.")
    h2("5.3 Los datos medidos")
    st = DATOS["stats"]
    tabla([
        ["Variable", "Unidad", "Mín.", "Mediana", "P75", "Máx."],
        ["CO₂", "ppm", fmt(st["co2"]["min"]), fmt(st["co2"]["median"]),
         fmt(st["co2"]["p75"]), fmt(st["co2"]["max"])],
        ["CO", "ppm", fmt(st["co"]["min"]), fmt(st["co"]["median"]),
         fmt(st["co"]["p75"]), fmt(st["co"]["max"])],
        ["PM2.5", "µg/m³", fmt(st["pm25"]["min"]), fmt(st["pm25"]["median"]),
         fmt(st["pm25"]["p75"]), fmt(st["pm25"]["max"])],
        ["Temperatura", "°C", fmt(st["temperatura"]["min"]),
         fmt(st["temperatura"]["median"]), fmt(st["temperatura"]["p75"]),
         fmt(st["temperatura"]["max"])],
        ["Humedad", "%", fmt(st["humedad"]["min"]), fmt(st["humedad"]["median"]),
         fmt(st["humedad"]["p75"]), fmt(st["humedad"]["max"])],
        ["Presión", "hPa", fmt(st["presion"]["min"]), fmt(st["presion"]["median"]),
         fmt(st["presion"]["p75"]), fmt(st["presion"]["max"])],
        ["UV", "mW/cm²", fmt(st["uv"]["min"]), fmt(st["uv"]["median"]),
         fmt(st["uv"]["p75"]), fmt(st["uv"]["max"])],
        ["Luz", "lux", fmt(st["luz"]["min"]), fmt(st["luz"]["median"]),
         fmt(st["luz"]["p75"]), fmt(st["luz"]["max"])],
    ], [0.20, 0.12, 0.12, 0.18, 0.18, 0.20], small=True,
        negrita_primera=True)
    p(f"El resumen cubre {fmt(DATOS['total'])} filas, de las cuales "
      f"{fmt(DATOS['valid'])} son válidas ({fmt(DATOS['pct']['valid'])} %). Las "
      "excedencias que reporta el informe son PM2.5 &gt; 35 µg/m³ "
      f"({fmt(DATOS['exceed']['pm25']['count'])} filas, "
      f"{fmt(DATOS['exceed']['pm25']['pct'])} %), CO &gt; 35 ppm "
      f"({fmt(DATOS['exceed']['co']['count'])}, {fmt(DATOS['exceed']['co']['pct'])} %) "
      "y CO₂ &gt; 1.000 ppm "
      f"({fmt(DATOS['exceed']['co2']['count'])}, {fmt(DATOS['exceed']['co2']['pct'])} %). "
      "Esos cortes no coinciden con los límites de categoría del ICA: sirven "
      "para describir el conjunto, no para clasificarlo.")
    h2("5.4 Qué implica en el índice")
    filas = [["Fecha", "n", "PM2.5", "CO", "ICA actual", "ICA EPA"]]
    for d in DATOS["daily"]:
        a = max(subindice(PM25, d["pm25"]), subindice(CO_PROY, d["co"]))
        e = max(subindice(PM25, d["pm25"]), subindice(CO_EPA, d["co"]))
        filas.append([
            f"{d['date'][8:10]}/{d['date'][5:7]}", str(d["count"]),
            fmt(d["pm25"]), fmt(d["co"]), str(a), str(e),
        ])
    tabla(filas, [0.16, 0.12, 0.14, 0.14, 0.22, 0.22], small=True)
    p("El 17/10 la mediana diaria de CO fue 35,23 ppm: el criterio actual "
      "marca 102 (apenas por encima del umbral de alarma) y el criterio EPA "
      "marca 348 (peligrosa). El 10/10, con PM2.5 de 49 µg/m³, la mediana ya "
      "era 134 (dañina para grupos sensibles).", "small")


def seccion_6():
    h1("6. ¿Alcanzan los sensores para calcular el ICA?")
    p("No para un ICA EPA completo. El ICA oficial requiere seis "
      "contaminantes criterio y la estación mide dos, o tres si se aprovecha "
      "PM10. La respuesta corta es: alcanza para un ICA parcial, no para "
      "replicar el índice oficial.")
    tabla([
        ["Contaminante", "Promedio", "Sensor del proyecto", "Estado"],
        ["PM2.5", "24 h", "PMS5003 (bytes 12–13)", "Disponible y en uso"],
        ["PM10", "24 h", "PMS5003 (bytes 14–15)", "Disponible, no publicado"],
        ["CO", "8 h", "MQ-7 (Arduino Uno)", "Disponible, sin calibrar"],
        ["O₃", "8 h", "—", "<b>Ausente</b>"],
        ["NO₂", "1 h", "—", "<b>Ausente</b>"],
        ["SO₂", "24 h / 1 h", "—", "<b>Ausente</b>"],
        ["CO₂", "No aplica", "MH-Z19C", "No es contaminante del ICA"],
    ], [0.19, 0.14, 0.34, 0.33], small=True, negrita_primera=True)
    h2("6.1 Cobertura real")
    p("Con lo que hay hoy el panel puede calcular un ICA de dos contaminantes "
      "(PM2.5 y CO). Si se publica PM10, pasa a tres. Para llegar a seis "
      "faltan sensores de gases: O₃, NO₂ y SO₂. El CO₂ no suma al ICA, pero "
      "sí aporta una lectura de ventilación que el panel ya muestra.")
    p("Agregar esos sensores no es solo comprar módulos. Los sensores de gases "
      "de bajo costo (MQ-131 para O₃, MQ-136 para SO₂, MICS-6814 para NO₂/CO) "
      "tienen deriva, sensibilidad cruzada y requieren calibración con gas "
      "patrón. Sin ese proceso, un ICA de seis contaminantes daría una "
      "falsa sensación de completitud.")
    nota("Cómo declararlo.",
         "La forma honesta es rotular el índice como «ICA parcial PM2.5 + CO "
         "(EPA)» o «ICA parcial PM2.5 + PM10 + CO (EPA)», indicar que es una "
         "estimación y enlazar esta nota metodológica desde el panel.")
    h2("6.2 Qué haría falta para completarlo")
    tabla([
        ["Faltante", "Alternativa de bajo costo", "Requisito para usarla"],
        ["O₃", "MQ-131 / sensor electroquímico", "Calibración y corrección "
         "por temperatura/humedad"],
        ["NO₂", "MICS-6814 / electroquímico", "Co-ubicación y factores de "
         "corrección"],
        ["SO₂", "MQ-136 / electroquímico", "Calibración con gas patrón"],
        ["PM10", "Ya disponible en el PMS5003", "Leer bytes 14–15 y publicar"],
        ["Promedios", "Vista SQL o cálculo en la app", "Ventanas móviles de "
         "24 h y 8 h"],
    ], [0.16, 0.44, 0.40], small=True, negrita_primera=True)


def seccion_7():
    h1("7. Colores de referencia y cómo se asignan")
    p("La EPA asigna un color fijo a cada categoría. No se elige según el "
      "contaminante ni según el mensaje: se deriva del número de ICA. Ese es "
      "el punto que hay que respetar si se quiere que el panel sea legible "
      "para cualquiera que conozca la escala.")
    filas = [["ICA", "Color", "Categoría", "Hex", "Contraste vs blanco",
              "Texto recomendado"]]
    for maximo, nombre, hexs, color in CATS:
        ini = 0 if maximo == 50 else [c[0] for c in CATS][
            [c[0] for c in CATS].index(maximo) - 1] + 1
        ratio = contraste(hexs, "#ffffff")
        texto = "Oscuro (#0f172a)" if ratio < 4.5 else "Claro (#ffffff)"
        filas.append([f"{ini}–{maximo}", color, nombre, hexs,
                      f"{ratio:.1f}".replace(".", ",") + ":1", texto])
    tabla(filas, [0.11, 0.12, 0.28, 0.13, 0.17, 0.19], small=True)
    p("El contraste se mide contra blanco. Amarillo y verde necesitan texto "
      "oscuro; rojo queda en el límite para texto normal y conviene usarlo "
      "en negrita o con texto oscuro; púrpura y granate admiten texto claro.",
      "small")


def seccion_7b(fig_colores):
    figura(fig_colores,
           "Figura 2. Escala oficial de colores del ICA (EPA). El color se "
           "asigna por rango de índice, no por contaminante.")


def seccion_8(fig_comp):
    h1("7.1 Comparación con la paleta actual")
    p("El panel usa seis colores de diseño que no coinciden con los de la "
      "EPA. La diferencia más visible es el azul («sky») en la categoría "
      "moderada, donde la referencia es amarillo; y el fucsia en la categoría "
      "peligrosa, donde la referencia es granate.")
    tabla([["Categoría", "Clase actual", "Hex actual", "Hex EPA", "Diferencia"]]
          + [[c[0], c[1], c[2], CATS[i][2],
              "Coincide en tono" if c[2].lower() == CATS[i][2].lower()
              else "Distinto"] for i, c in enumerate(PALETA_ACTUAL)],
          [0.30, 0.16, 0.16, 0.16, 0.22], small=True, negrita_primera=True)
    p("La lógica actual —<font face='DejaVuMono' size='8'>computeAQI → "
      "aqiCategory → setLevel</font>— es correcta: calcula el número, busca la "
      "categoría y aplica la clase. El cambio necesario es de datos, no de "
      "arquitectura: reemplazar los hex y los nombres de clase, y decidir si "
      "los colores del ICA se separan de los colores de las tarjetas de "
      "sensores.")
    h2("7.2 Cómo se modifica según el dato medido")
    p("El color no se actualiza a mano. Cada vez que llega una fila, el panel "
      "recalcula el ICA y aplica la categoría que corresponde. El flujo "
      "completo es:")
    codigo(
        "1. leer pm25, pm10 y co de la fila\n"
        "2. truncar cada concentración al decimal que exige la EPA\n"
        "3. calcular el subíndice de cada contaminante\n"
        "4. ICA = max(sublndices)\n"
        "5. buscar la categoría: aqi <= 50, 100, 150, 200, 300, 500\n"
        "6. aplicar la clase de color y el texto de la categoría\n"
        "7. si ICA > 100, activar la alarma; si baja de 80, cortarla"
    )
    p("La alarma del ESP32 usa exactamente ese criterio: se enciende por "
      "encima de 100 y se apaga por debajo de 80. Es una histéresis razonable "
      "para evitar parpadeos, pero depende de que las tablas del firmware y "
      "de la app sean iguales. Hoy no lo serían si se cambia solo un lado.")
    h2("7.3 Qué color corresponde a los datos medidos")
    st = DATOS["stats"]
    casos = [
        ("PM2.5 mediana", st["pm25"]["median"], "µg/m³", PM25),
        ("PM2.5 p75", st["pm25"]["p75"], "µg/m³", PM25),
        ("PM2.5 máx", st["pm25"]["max"], "µg/m³", PM25),
    ]
    filas = [["Indicador", "Valor", "ICA", "Categoría", "Color"]]
    for nombre, crudo, unidad, bp in casos:
        v = subindice(bp, crudo)
        filas.append([nombre, f"{fmt(crudo)} {unidad}", str(v),
                      categoria(v)[0], categoria(v)[2]])
    for clave, etiqueta in (("median", "mediana"), ("p75", "p75")):
        crudo = st["co"][clave]
        v = subindice(CO_EPA, crudo)
        filas.append([f"CO {etiqueta}", f"{fmt(crudo)} ppm", str(v),
                      categoria(v)[0], categoria(v)[2]])
    crudo = DATOS["max_daily"]["co"]["value"]
    v = subindice(CO_EPA, crudo)
    filas.append(["CO máx diario", f"{fmt(crudo)} ppm",
                  str(v), categoria(v)[0], categoria(v)[2]])
    tabla(filas, [0.24, 0.19, 0.10, 0.28, 0.19], small=True,
          negrita_primera=True)
    p("Con el criterio oficial, el CO domina el índice casi todos los días y "
      "lo lleva a púrpura o granate. Con el criterio actual, el mismo CO queda "
      "en amarillo. La diferencia no está en el sensor: está en la tabla.")
    figura(fig_comp,
           "Figura 1. Subíndice ICA con el criterio actual y con EPA 2024 "
           "para los valores del resumen del 29/10/2026. En PM2.5 ambos "
           "coinciden; en CO el criterio actual subestima el subíndice.")
    h2("7.4 Accesibilidad y uso del color")
    bullets([
        "No usar el color como única señal: acompañar con el número, la "
        "categoría en texto y un ícono.",
        "Amarillo y verde exigen texto oscuro; nunca texto claro sobre "
        "amarillo.",
        "En modo claro, un borde o una insignia rellena funciona mejor que "
        "texto coloreado sobre blanco.",
        "Verde y rojo son la combinación más difícil para daltonismo; la "
        "etiqueta textual resuelve la ambigüedad.",
        "Mantener una leyenda visible con los seis rangos y sus colores.",
    ])


def seccion_9(fig_comp):
    h1("8. Hallazgos y recomendaciones")
    p("Los hallazgos se ordenan por impacto sobre la interpretación pública "
      "del índice. Ninguno requiere hardware nuevo salvo la cobertura de "
      "gases, que se propone como etapa separada.")
    tabla([
        ["#", "Hallazgo", "Evidencia", "Efecto", "Prioridad"],
        ["1", "Tramos de CO distintos de EPA", "app.js 149–153; "
         "sketch 122–129", "Subestima el riesgo por CO", "Alta"],
        ["2", "Sin promedios 24 h / 8 h", "Uso de la última fila",
         "ICA instantáneo, no comparable", "Alta"],
        ["3", "Solo 2 contaminantes de 6", "PMS5003 + MQ-7",
         "ICA parcial", "Alta"],
        ["4", "PM10 disponible sin usar", "bytes 14–15 de la trama",
         "Se pierde un contaminante gratis", "Media"],
        ["5", "Paleta no oficial", "styles.css 9–15", "Confusión de colores",
         "Media"],
        ["6", "Tope PM2.5 en 500,4", "app.js 146; sketch 119",
         "Pendiente distinta en el tramo alto", "Baja"],
        ["7", "MQ-7 sin calibrar", "R0 fijo en 9.800 Ω", "CO dominante y "
         "sesgado", "Alta"],
        ["8", "Tablas duplicadas", "App-Web y docs",
         "Riesgo de divergencia", "Media"],
    ], [0.05, 0.24, 0.25, 0.31, 0.15], small=True)
    h2("8.1 Recomendaciones")
    tabla([
        ["Prioridad", "Acción", "Dónde"],
        ["Alta", "Corregir los tramos de CO a EPA o rotular el índice como "
         "local", "app.js, docs/app.js, sketch ESP32"],
        ["Alta", "Calcular promedios móviles de 24 h y 8 h", "App o vista SQL"],
        ["Alta", "Calibrar el MQ-7 en aire limpio y documentar R0",
         "sketch Arduino Uno"],
        ["Alta", "Rotular «ICA parcial (EPA)» y «estimado»", "Panel y notas"],
        ["Media", "Publicar PM10 y sumarlo al máximo", "Firmware ESP32"],
        ["Media", "Adoptar la paleta EPA y una leyenda", "styles.css, index.html"],
        ["Media", "Eliminar la duplicación entre App-Web y docs",
         "Build o copia automática"],
        ["Baja", "Corregir el tope de PM2.5 a 325,4", "app.js y firmware"],
    ], [0.12, 0.55, 0.33], small=True, negrita_primera=True)


def seccion_10():
    h1("9. Anexo A — Cambios de código propuestos")
    p("Este anexo describe qué habría que tocar para que la implementación "
      "refleje el criterio EPA. No se aplicó ningún cambio. El orden sugerido "
      "es: base de datos, firmware del ESP32, aplicación, y por último la "
      "calibración del Arduino Uno.")
    nota("Advertencia.",
         "El panel no consume el campo «ica» que publica el ESP32: lo "
         "recalcula en el navegador con sus propias tablas. Si se cambia solo "
         "el firmware, el panel seguirá mostrando el criterio anterior.")

    h2("9.1 Arduino Uno — sketch_oct17a.ino")
    p("El Uno no calcula ICA. Su única incidencia es la calidad del CO que "
      "envía. Los cambios son de calibración, no de estructura:")
    tabla([
        ["Línea", "Actual", "Cambio"],
        ["122", "float R0 = 9800.0;", "Usar R0 medido en aire limpio, no una "
         "constante arbitraria."],
        ["118–125", "Rs, ratio y curva 98,539·ratio^−0,63", "Verificar la "
         "ecuación contra el datasheet del MQ-7 y documentarla."],
        ["—", "Sin ciclo de calentador", "El MQ-7 pide alternar 5 V y 1,4 V "
         "(≈60 s / 90 s). Implementarlo obliga a rediseñar el lazo de 3 s."],
        ["162", "Trama de 9 campos", "No cambiar, salvo que se agregue un "
         "campo nuevo; en ese caso actualizar el sscanf del ESP32."],
    ], [0.10, 0.36, 0.54], small=True, negrita_primera=True)
    codigo(
        "int mq7Analog = analogRead(MQ7_AO);\n"
        "float VRL = mq7Analog * (5.0 / 1023.0);\n"
        "if (VRL == 0) VRL = 0.001;\n"
        "float Rs = ((5.0 - VRL) / VRL) * 1000.0;\n"
        "// R0 debe provenir de una calibración, no de una constante\n"
        "float ratio = Rs / R0;\n"
        "ppmCO = 98.539 * pow(ratio, -0.63);"
    )

    h2("9.2 ESP32 — sketch_oct17b.ino")
    p("Es el cambio central: corregir los puntos de corte, leer PM10 y sumarlo "
      "al máximo.")
    codigo(
        "// 113-120: corregir el último tramo de PM2.5\n"
        "const float BR_PM25[][4] = {\n"
        "  {0.0,   9.0,   0,  50}, {9.1,  35.4,  51, 100},\n"
        "  {35.5,  55.4,  101, 150}, {55.5, 125.4, 151, 200},\n"
        "  {125.5, 225.4, 201, 300}, {225.5, 325.4, 301, 500}\n"
        "};\n\n"
        "// 122-129: reemplazar los tramos NIOSH por los de EPA (8 h)\n"
        "const float BR_CO[][4] = {\n"
        "  {0.0,  4.4,  0,  50}, {4.5,  9.4,  51, 100},\n"
        "  {9.5,  12.4, 101, 150}, {12.5, 15.4, 151, 200},\n"
        "  {15.5, 30.4, 201, 300}, {30.5, 50.4, 301, 500}\n"
        "};\n\n"
        "// nueva tabla para PM10\n"
        "const float BR_PM10[][4] = {\n"
        "  {0,   54,  0,  50}, {55,  154, 51, 100},\n"
        "  {155, 254, 101, 150}, {255, 354, 151, 200},\n"
        "  {355, 424, 201, 300}, {425, 604, 301, 500}\n"
        "};\n\n"
        "// 210-212: leer también PM10 (bytes 14-15)\n"
        "currentPM25 = ((uint16_t)buffer[12] << 8) | buffer[13];\n"
        "currentPM10 = ((uint16_t)buffer[14] << 8) | buffer[15];\n\n"
        "// 143-147: máximo de los tres subíndices\n"
        "float aqiPm   = subIndice(BR_PM25, 6, (float)currentPM25);\n"
        "float aqiPm10 = subIndice(BR_PM10, 6, (float)currentPM10);\n"
        "float aqiCo   = subIndice(BR_CO, 6, currentCO);\n"
        "return (int)round(max(aqiPm, max(aqiPm10, aqiCo)));\n\n"
        "// 327-337: publicar el campo nuevo\n"
        "doc[\"pm10\"] = currentPM10;\n"
        "doc[\"ica_metodo\"] = \"EPA-2024\";"
    )
    p("Requiere declarar <font face='DejaVuMono' size='8'>uint16_t "
      "currentPM10 = 0;</font> junto a las demás variables y agregar la "
      "columna <font face='DejaVuMono' size='8'>pm10</font> en la tabla "
      "<font face='DejaVuMono' size='8'>mediciones</font> de Supabase. Las "
      "filas históricas quedarán con PM10 nulo; el cálculo debe ignorar los "
      "nulos en lugar de tratarlos como cero.")

    h2("9.3 Aplicación web — App-Web/app.js")
    codigo(
        "// 145-155: breakpoints EPA\n"
        "const AQI_BREAKPOINTS = {\n"
        "  pm25: [[0.0,9.0,0,50],[9.1,35.4,51,100],[35.5,55.4,101,150],\n"
        "         [55.5,125.4,151,200],[125.5,225.4,201,300],\n"
        "         [225.5,325.4,301,500]],\n"
        "  pm10: [[0,54,0,50],[55,154,51,100],[155,254,101,150],\n"
        "         [255,354,151,200],[355,424,201,300],[425,604,301,500]],\n"
        "  co:   [[0.0,4.4,0,50],[4.5,9.4,51,100],[9.5,12.4,101,150],\n"
        "         [12.5,15.4,151,200],[15.5,30.4,201,300],\n"
        "         [30.5,50.4,301,500]]\n"
        "};\n\n"
        "// 156-164: categorías con los colores oficiales\n"
        "const AQI_CATEGORIES = [\n"
        "  { max: 50,  key: \"aqi-green\",  label: \"Buena\" },\n"
        "  { max: 100, key: \"aqi-yellow\", label: \"Moderada\" },\n"
        "  { max: 150, key: \"aqi-orange\", label: \"Dañina para grupos sensibles\" },\n"
        "  { max: 200, key: \"aqi-red\",    label: \"Dañina\" },\n"
        "  { max: 300, key: \"aqi-purple\", label: \"Muy dañina\" },\n"
        "  { max: 500, key: \"aqi-maroon\", label: \"Peligrosa\" }\n"
        "];\n\n"
        "// 266-271: sumar PM10 al máximo\n"
        "function computeAQI(row) {\n"
        "  if (!row) return 0;\n"
        "  return Math.max(\n"
        "    subIndex(AQI_BREAKPOINTS.pm25, row.pm25),\n"
        "    subIndex(AQI_BREAKPOINTS.pm10, row.pm10),\n"
        "    subIndex(AQI_BREAKPOINTS.co, row.co)\n"
        "  );\n"
        "}"
    )
    p("Para los promedios, agregar una función que filtre las filas por "
      "ventana temporal y promedie antes de calcular:")
    codigo(
        "function promedioVentana(rows, campo, horas) {\n"
        "  const desde = Date.now() - horas * 3600 * 1000;\n"
        "  const vals = rows\n"
        "    .filter(r => new Date(r.created_at).getTime() >= desde)\n"
        "    .map(r => Number(r[campo]))\n"
        "    .filter(v => Number.isFinite(v));\n"
        "  if (!vals.length) return null;\n"
        "  return vals.reduce((a, b) => a + b, 0) / vals.length;\n"
        "}"
    )
    p("Con 100 filas de historial (el límite actual) no se cubren 24 h a "
      "15 s: hacen falta 5.760 filas. O se sube el límite, o se calcula en "
      "Supabase con una vista que devuelva los promedios ya listos.")

    h2("9.4 Hoja de estilos — App-Web/styles.css")
    codigo(
        ":root {\n"
        "  --aqi-green:  #00E400;\n"
        "  --aqi-yellow: #FFFF00;\n"
        "  --aqi-orange: #FF7E00;\n"
        "  --aqi-red:    #FF0000;\n"
        "  --aqi-purple: #8F3F97;\n"
        "  --aqi-maroon: #7E0023;\n"
        "}\n\n"
        ".lvl-aqi-green  { --level: var(--aqi-green); }\n"
        ".lvl-aqi-yellow { --level: var(--aqi-yellow); }\n"
        ".lvl-aqi-orange { --level: var(--aqi-orange); }\n"
        ".lvl-aqi-red    { --level: var(--aqi-red); }\n"
        ".lvl-aqi-purple { --level: var(--aqi-purple); }\n"
        ".lvl-aqi-maroon { --level: var(--aqi-maroon); }\n\n"
        "/* texto oscuro sobre los colores claros */\n"
        ".air-banner.lvl-aqi-green .air-number,\n"
        ".air-banner.lvl-aqi-yellow .air-number,\n"
        ".air-banner.lvl-aqi-orange .air-number { color: #0f172a; }"
    )
    p("Se propone un prefijo <font face='DejaVuMono' size='8'>aqi-</font> para "
      "no mezclar la escala del ICA con la paleta de las tarjetas de sensores, "
      "que hoy usa esmeralda, celeste, ámbar, naranja, rosa y fucsia. Si se "
      "prefiere unificar, hay que aceptar que las tarjetas cambien de color.")

    h2("9.5 Copia publicada y nota del panel")
    bullets([
        "<font face='DejaVuMono' size='8'>docs/app.js</font>, "
        "<font face='DejaVuMono' size='8'>docs/styles.css</font> y "
        "<font face='DejaVuMono' size='8'>docs/index.html</font> son la copia "
        "que sirve GitHub Pages: hay que replicar los cambios o generar docs/ "
        "automáticamente desde App-Web/.",
        "La nota de <font face='DejaVuMono' size='8'>index.html</font> "
        "(l. 276) dice que el CO usa 35 ppm de NIOSH y 50 ppm de OSHA: debe "
        "actualizarse al criterio EPA o a la decisión que se tome.",
        "Agregar una leyenda de seis colores y el texto «ICA parcial (EPA) · "
        "estimado» junto al número.",
        "Actualizar el mapa <font face='DejaVuMono' size='8'>COLOR</font> de "
        "gráficos si se reutilizan los mismos nombres.",
    ])

    h2("9.6 Validación")
    p("Antes de publicar, verificar los puntos de corte contra la tabla EPA. "
      "Cada fila debe devolver exactamente el índice indicado:")
    tabla([
        ["Concentración", "Contaminante", "ICA esperado"],
        ["9,0 µg/m³", "PM2.5", "50"],
        ["35,4 µg/m³", "PM2.5", "100"],
        ["55,4 µg/m³", "PM2.5", "150"],
        ["125,4 µg/m³", "PM2.5", "200"],
        ["225,4 µg/m³", "PM2.5", "300"],
        ["325,4 µg/m³", "PM2.5", "500"],
        ["4,4 ppm", "CO", "50"],
        ["9,4 ppm", "CO", "100"],
        ["12,4 ppm", "CO", "150"],
        ["15,4 ppm", "CO", "200"],
        ["30,4 ppm", "CO", "300"],
        ["50,4 ppm", "CO", "500"],
    ], [0.30, 0.35, 0.35], small=True, negrita_primera=True)
    p("Si el panel y el firmware devuelven valores distintos para la misma "
      "concentración, las tablas se desincronizaron.")


def referencias():
    h1("10. Referencias")
    refs = [
        "US EPA / AirNow. <i>Air Quality Index (AQI) Basics</i>. "
        "https://www.airnow.gov/aqi/aqi-basics/",
        "US EPA. <i>Technical Assistance Document for the Reporting of Daily "
        "Air Quality — the Air Quality Index (AQI)</i>, 2018 (tablas y reglas "
        "de promediado).",
        "US EPA. <i>Final Reconsideration of the National Ambient Air Quality "
        "Standards for Particulate Matter</i> y hoja de actualización del AQI, "
        "2024 (PM2.5: 0–9,0 · 9,1–35,4 · … · 225,5–325,4 µg/m³).",
        "Plantower. <i>PMS5003 Particulate Matter Sensor — Datasheet</i> "
        "(trama de 32 bytes, campos PM1.0/PM2.5/PM10 y conteos).",
        "Winsen. <i>MQ-7 Carbon Monoxide Sensor — Datasheet</i> (ciclo de "
        "calentador y curva de calibración).",
        "NIOSH. <i>Pocket Guide to Chemical Hazards</i> (CO: REL 35 ppm, "
        "8 h). OSHA. 29 CFR 1910.1000 (PEL 50 ppm).",
        "ASHRAE. <i>Standard 62.1</i> (ventilación) y <i>Standard 55</i> "
        "(confort térmico).",
        "OMS. <i>Directrices mundiales de calidad del aire</i>, 2021 "
        "(PM2.5: 15 µg/m³ en 24 h; PM10: 45 µg/m³ en 24 h).",
        "Proyecto Tucumán Respira. <i>Informe técnico unificado</i>, secciones "
        "6.3, 11 y 16.1; y código en Software_Código_Fuente/ (app.js, "
        "sketch_oct17a.ino, sketch_oct17b.ino).",
    ]
    for i, r in enumerate(refs, 1):
        story.append(Paragraph(f"{i}. {r}", S["small"]))
    story.append(Spacer(1, 10))
    story.append(Linea(0.6, GRIS_CLARO, ANCHO))
    story.append(Spacer(1, 6))
    p("Documento elaborado el 7 de noviembre de 2026 a partir de los datos "
      "del 29 de octubre de 2026. Las tablas EPA se reproducen con fines de "
      "referencia; la fuente normativa es la documentación oficial citada.",
      "small")


# Armado

def main():
    tmp = tempfile.mkdtemp(prefix="ica_fig_")
    fig_comp, fig_col = figuras(tmp)

    portada()
    indice()
    seccion_1()
    seccion_2()
    story.append(PageBreak())
    seccion_3()
    story.append(PageBreak())
    seccion_4()
    story.append(PageBreak())
    seccion_5()
    story.append(PageBreak())
    seccion_6()
    story.append(PageBreak())
    seccion_7()
    seccion_7b(fig_col)
    story.append(PageBreak())
    seccion_8(fig_comp)
    story.append(PageBreak())
    seccion_9(fig_comp)
    story.append(PageBreak())
    seccion_10()
    story.append(PageBreak())
    referencias()

    doc = BaseDocTemplate(
        str(SALIDA), pagesize=A4,
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=19 * mm, bottomMargin=18 * mm,
        title="El ICA en Tucumán Respira — cálculo EPA, sensores y colores",
        author="Equipo Tucumán Respira — Escuela Técnica N°5",
        subject="Análisis del Índice de Calidad del Aire: cálculo EPA 2024, "
                "PMS5003, cobertura de sensores y colores de referencia",
        keywords="ICA, AQI, EPA, PM2.5, PM10, CO, PMS5003, Tucumán Respira",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
                  id="cuerpo")
    doc.addPageTemplates([PageTemplate(id="todas", frames=[frame], onPage=pie)])
    doc.build(story)
    print("Generado:", SALIDA)


if __name__ == "__main__":
    main()
