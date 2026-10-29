#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generador de la síntesis para el concurso «Tucumán Respira».

El documento resume el Informe_Tucuman_Respira.pdf y reutiliza su snapshot de
datos y sus gráficos. Las referencias § remiten al informe técnico completo.
"""
from __future__ import annotations

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
SALIDA = str(BASE / "Sintesis_Concurso_Tucuman_Respira.pdf")
FIG = BASE / "figuras"
DATOS_PATH = BASE / "datos_resumen.json"
if not DATOS_PATH.exists():
    raise SystemExit("Falta datos_resumen.json; ejecutá actualizar_datos.py.")
DATOS = json.loads(DATOS_PATH.read_text(encoding="utf-8"))

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
pdfmetrics.registerFont(TTFont("DejaVu", FONT_DIR / "DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", FONT_DIR / "DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Oblique", FONT_DIR / "DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-BoldOblique", FONT_DIR / "DejaVuSans-BoldOblique.ttf"))
pdfmetrics.registerFontFamily(
    "DejaVu", normal="DejaVu", bold="DejaVu-Bold",
    italic="DejaVu-Oblique", boldItalic="DejaVu-BoldOblique",
)

AZUL = colors.HexColor("#0f172a")
VERDE = colors.HexColor("#059669")
GRIS = colors.HexColor("#64748b")
GRIS_CLARO = colors.HexColor("#d7dee8")
FONDO_SUAVE = colors.HexColor("#f8fafc")
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
                         textColor=AZUL, leading=18, spaceBefore=10,
                         spaceAfter=5, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="DejaVu-Bold", fontSize=10.5,
                         textColor=VERDE, leading=13.5, spaceBefore=7,
                         spaceAfter=3, keepWithNext=1),
    "body": ParagraphStyle("body", fontName="DejaVu", fontSize=9.1,
                           textColor=colors.HexColor("#1e293b"), leading=12.6,
                           alignment=TA_JUSTIFY, spaceAfter=5),
    "bullet": ParagraphStyle("bullet", fontName="DejaVu", fontSize=9.0,
                             textColor=colors.HexColor("#1e293b"), leading=12.4,
                             leftIndent=12, bulletIndent=2, spaceAfter=2.4),
    "celda": ParagraphStyle("celda", fontName="DejaVu", fontSize=7.6,
                            textColor=colors.HexColor("#1e293b"), leading=9.7),
    "celda_b": ParagraphStyle("celda_b", fontName="DejaVu-Bold", fontSize=7.6,
                              textColor=AZUL, leading=9.7),
    "celda_s": ParagraphStyle("celda_s", fontName="DejaVu", fontSize=7.1,
                              textColor=colors.HexColor("#1e293b"), leading=9.0),
    "celda_bs": ParagraphStyle("celda_bs", fontName="DejaVu-Bold", fontSize=7.1,
                               textColor=AZUL, leading=9.0),
    "th": ParagraphStyle("th", fontName="DejaVu-Bold", fontSize=7.6,
                         textColor=colors.white, leading=9.7),
    "th_s": ParagraphStyle("th_s", fontName="DejaVu-Bold", fontSize=7.1,
                           textColor=colors.white, leading=9.0),
    "small": ParagraphStyle("small", fontName="DejaVu", fontSize=7.4,
                            textColor=GRIS, leading=9.9),
    "quote": ParagraphStyle("quote", fontName="DejaVu", fontSize=8.6,
                            textColor=colors.HexColor("#0f172a"), leading=11.6,
                            leftIndent=12, rightIndent=6,
                            backColor=FONDO_SUAVE, borderColor=GRIS_CLARO,
                            borderWidth=0.5, borderPadding=7, spaceAfter=7),
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


def fig(path, caption, width_cm=16.5, max_h_mm=105):
    path = Path(path)
    if not path.exists():
        return
    with PILImage.open(path) as im:
        w, h = im.size
    scale = min(width_cm * mm / w, max_h_mm * mm / h)
    rl = RLImage(str(path), width=w * scale, height=h * scale)
    rl.hAlign = "CENTER"
    story.append(KeepTogether([
        Spacer(1, 4), rl, Spacer(1, 3),
        Paragraph(esc(caption), S["figcap"]), Spacer(1, 7),
    ]))


def fig_grid(items, cols_n=2):
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
            row.append([rl, Spacer(1, 3),
                        Paragraph(esc(caption), S["figcap"])])
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
                      "Síntesis para el concurso — Tucumán Respira 2026")
    canvas.drawRightString(A4[0] - 15 * mm, 10 * mm,
                           "Página %d" % doc.page)
    canvas.restoreState()


# ===================== PORTADA =====================
story.append(Spacer(1, 20))
story.append(Paragraph("SÍNTESIS PARA EL CONCURSO", S["marca"]))
story.append(Paragraph("Escuela Técnica N°5", S["escuela"]))
story.append(Paragraph("Proyecto: Tucumán Respira 2026", S["proyecto"]))
story.append(Spacer(1, 12))
story.append(Paragraph("Tucumán Respira", S["titulo"]))
story.append(Paragraph(
    "Estación de monitoreo de calidad del aire IoT: síntesis del informe "
    "técnico para la entrega del concurso.", S["subtitulo"]))
story.append(Spacer(1, 10))
story.append(Paragraph("Equipo de trabajo", S["autor"]))
story.append(Paragraph(
    "Roy Luciano Molina · Maximo Valdez Leguina · Candela Rojas Perassi · "
    "María Pía Olivar · Benicio Gael Pieroni · Joaquín Valdecanto · "
    "Tatiana Maturano · Bautista Argañaraz · Jonás Barreiro", S["equipo"]))
story.append(Paragraph(
    "Docente: Tadeo Lobo — Tecnología de Control.", S["equipo"]))
story.append(Paragraph(
    "Síntesis preparada por Benicio Gael Pieroni. 29 de octubre de 2026.",
    S["equipo"]))
story.append(Spacer(1, 12))

tabla([
    ["Aspecto", "Detalle"],
    ["Concurso", "Tucumán Respira 2026 — Etapa 1"],
    ["Escuela", "Escuela Técnica N°5"],
    ["Proyecto", "Estación de monitoreo ambiental IoT"],
    ["Docente", "Tadeo Lobo — Tecnología de Control"],
    ["Video", "2:49, MP4; muestra todos los sensores"],
    ["Entrega", "30/10/2026 — direcciontecnicayfp.tuc@gmail.com"],
    ["Documento base", "Informe_Tucuman_Respira.pdf (informe técnico completo)"],
], cols(0.20, 0.80), negrita_primera=True)

story.append(Spacer(1, 2))
story.append(Paragraph(
    "Esta síntesis resume el Informe Técnico completo. Las referencias § "
    "remiten a ese documento, donde se encuentra el detalle de hardware, "
    "firmware, pruebas, datos y registro fotográfico. El informe técnico se "
    "conserva como respaldo y puede adjuntarse como anexo.", S["nota"]))
story.append(PageBreak())

# ===================== 1. PROBLEMA =====================
h1("1. Problema abordado y objetivo")
p("El problema abordado es la dificultad de contar con información local, "
  "continua y accesible sobre la calidad del aire y las condiciones "
  "ambientales de la escuela y su entorno. Los datos públicos suelen estar "
  "dispersos, no tienen resolución local o no resultan fáciles de "
  "interpretar; además, no siempre existe una herramienta propia para medir, "
  "registrar y comparar variables como PM2.5, CO y CO₂. Esa falta de "
  "información dificulta detectar episodios de ventilación deficiente, "
  "relacionar las mediciones con las actividades cotidianas y tomar "
  "decisiones fundamentadas.")
p("El proyecto responde con una estación de bajo costo, documentada y "
  "replicable, y con un panel que traduce las mediciones en información "
  "comprensible para la comunidad educativa. No reemplaza una red de "
  "monitoreo certificada: acerca los datos, muestra tendencias y habilita "
  "preguntas concretas sobre el ambiente.")
p("Objetivo general: diseñar, construir y documentar un sistema completo de "
  "monitoreo —desde la adquisición en campo hasta la publicación web— que "
  "permita comprender el estado de la calidad del aire y consultar los datos "
  "históricos.")
bullets([
    "Medir PM2.5, CO, CO₂, temperatura, humedad, presión, UV y luz.",
    "Registrar la ubicación de cada medición con GPS.",
    "Publicar las lecturas en la nube y ofrecer un panel público claro.",
    "Avisar localmente con una alarma y permitir silenciarla desde la web.",
    "Permitir la descarga libre de los datos en CSV y JSON.",
    "Documentar el hardware, el armado, el gabinete y los roles del equipo.",
])
quote("La estación es una herramienta educativa y de observación local; sus "
      "datos no constituyen un diagnóstico sanitario ni una certificación "
      "metrológica.")

# ===================== 2. DISEÑO =====================
h1("2. Diseño y construcción de la estación")
p("El sistema se organiza en cuatro capas: adquisición (Arduino Uno), "
  "enlace y nube (ESP32), persistencia (Supabase/PostgreSQL) y presentación "
  "(aplicación web). El Uno lee los sensores y envía una trama de 9 campos "
  "al ESP32 cada 3 s; el ESP32 publica en Supabase cada 15 s, calcula el ICA "
  "local y gobierna un zumbador. La web lee Supabase por REST y Realtime.")
tabla([
    ["Componente", "Función"],
    ["Arduino Uno R3", "Adquisición y lectura de los sensores."],
    ["ESP32", "Wi-Fi, publicación en Supabase, ICA y alarma."],
    ["MH-Z19C", "CO₂ por UART."],
    ["MQ-7", "CO por entrada analógica."],
    ["PMS5003", "PM2.5 por Serial2; ventilador y láser."],
    ["BME280", "Temperatura, humedad y presión por I²C."],
    ["ML8511 + LDR", "Radiación UV y luz ambiental."],
    ["NEO-6M", "Posición GPS."],
], cols(0.28, 0.72), negrita_primera=True)
p("El gabinete se diseñó después de medir todos los componentes: distribución "
  "interior, tapa, paredes y agujeros para sensores y cableado. Se imprimió "
  "en 3D; los imanes previstos para la tapa no cerraban bien y se "
  "reemplazaron por tornillos. El modelo se conserva en "
  "Diseño_Hardware/Diseño_Gabinete/Gabinete para tucuman respira.stl "
  "(216 KB). El armado definitivo reemplazó el protoboard por cables "
  "soldados; como no se consiguió el adaptador del PMS5003, se cortaron y "
  "soldaron los cables.")
fig_grid([
    (FIG / "fig_14.jpeg", "Figura 3. Gabinete: diseño y terminaciones."),
    (FIG / "fig_12.jpeg", "Figura 4. Gabinete: montaje y distribución interior."),
])
h2("2.1 Flujo de datos")
tabla([
    ["Capa", "Qué ocurre"],
    ["Adquisición", "El Uno lee los sensores y el GPS y arma una trama de 9 "
     "campos cada 3 s."],
    ["Enlace", "El ESP32 recibe la trama, publica cada 15 s, calcula el ICA "
     "local y gobierna el zumbador."],
    ["Persistencia", "Supabase/PostgreSQL guarda la tabla mediciones; REST y "
     "Realtime alimentan el panel."],
    ["Presentación", "La web muestra 8 métricas, histórico, mapa, descargas "
     "CSV/JSON y control de la alarma."],
], cols(0.22, 0.78), small=True, negrita_primera=True)
h2("2.2 Cronología del proyecto")
tabla([
    ["Fecha", "Hito"],
    ["05/10–10/10", "Primeras mediciones y pruebas de sensores."],
    ["15/10", "Armado del prototipo y registro fotográfico."],
    ["17/10", "Puesta a punto, correcciones de firmware y pruebas de "
     "integración."],
    ["26/10", "Montaje final y terminación del gabinete."],
    ["29/10", "Cierre del snapshot de datos y documentación."],
], cols(0.22, 0.78), small=True, negrita_primera=True)

# ===================== 3. PROGRAMACIÓN =====================
h1("3. Programación y puesta a punto")
p("El desarrollo se hizo en etapas: primero se probó cada componente por "
  "separado en protoboard y con códigos independientes; después se integró "
  "el circuito con cables soldados y se concatenaron los firmwares. El "
  "panel web se desarrolló en paralelo y se conectó a los datos reales "
  "antes de la puesta a punto final.")
tabla([
    ["Etapa", "Qué se hizo", "Resultado"],
    ["Pruebas individuales", "Sensores y módulos por separado, con códigos "
     "propios.", "Cada componente verificado antes de integrarlo."],
    ["Calibración", "MQ-7 con 30 s de calentamiento y ajuste de R0; ML8511 "
     "con referencia de 5 V; BME280 con 0x76/0x77 y protección ante NaN.",
     "Lecturas más estables y diagnóstico por monitor serie."],
    ["Integración", "Cables soldados, trama de 9 campos y GPS con última "
     "coordenada válida.", "Circuito definitivo sin protoboard."],
    ["Firmware ESP32", "AP temporal, credenciales en RAM, currentCO2=0 y "
     "arranque de red antes de abrir sockets.", "Sin reinicio en bucle y sin "
     "CO₂ falso."],
    ["Panel web", "Supabase REST/Realtime, ICA, alarma, histórico y descargas "
     "CSV/JSON.", "Panel público en GitHub Pages."],
], cols(0.20, 0.43, 0.37), small=True, negrita_primera=True)
p("Las correcciones clave surgieron de las pruebas: el ESP32 se reiniciaba "
  "porque abría sockets antes de inicializar la red; el CO₂ mostraba 400 ppm "
  "cuando no había datos del Uno; el BME280 podía no detectarse en la "
  "dirección esperada; y el GPS podía perder el fix. Todas quedaron "
  "documentadas y corregidas en el firmware.")
h2("3.1 Pruebas y verificaciones")
tabla([
    ["Prueba", "Resultado"],
    ["Sensores individuales", "Cada módulo respondió en protoboard antes de "
     "la integración."],
    ["Trama Uno → ESP32", "9 campos cada 3 s; las tramas inválidas se "
     "descartan."],
    ["Wi-Fi y AP", "AP temporal; credenciales en RAM; reapertura si se "
     "pierde la red."],
    ["Supabase", "Publicación cada 15 s; REST y Realtime disponibles."],
    ["Panel web", "8 métricas, histórico, mapa, descargas y control de la "
     "alarma."],
    ["Alarma", "Verificada a nivel de firmware y endpoints; falta la prueba "
     "de campo."],
], cols(0.28, 0.72), small=True, negrita_primera=True)
fig_grid([
    (FIG / "fig_06.jpeg", "Figura 5. Cableado y soldadura."),
    (FIG / "fig_09.jpeg", "Figura 6. Panel web."),
])

# ===================== 4. DATOS =====================
h1("4. Datos obtenidos e interpretación")
_s = DATOS["stats"]
_e = DATOS["exceed"]
_m = DATOS["max_daily"]
p(f"Al {fmt_fecha_local(DATOS['generated_at_local'])} la base contiene "
  f"{fmt_int(DATOS['total'])} filas. Después de separar "
  f"{fmt_int(DATOS['legacy'])} filas históricas y "
  f"{fmt_int(DATOS['invalid'])} filas con valores fuera de rango, quedan "
  f"{fmt_int(DATOS['valid'])} lecturas válidas ({fmt_pct(DATOS['pct']['valid'])} "
  f"del total). {fmt_int(DATOS['coords'])} tienen coordenadas GPS y "
  f"{fmt_int(DATOS['ip'])} registran IP del dispositivo.")
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
fig(FIG / "datos_pm25_co.png",
    "Figura 1. Mediana diaria de PM2.5 y CO en los días con registro. Las "
    "líneas punteadas marcan 35 µg/m³ y 35 ppm.")
fig(FIG / "datos_excedencias.png",
    "Figura 2. Porcentaje de lecturas válidas que superan cada umbral.")
bullets([
    f"PM2.5: mediana {fmt_var('pm25', _s['pm25']['median'])} µg/m³ y P75 "
    f"{fmt_var('pm25', _s['pm25']['p75'])} µg/m³. El "
    f"{fmt_pct(_e['pm25']['pct'])} superó 35 µg/m³; la mayor mediana diaria "
    f"fue el {fmt_dia(_m['pm25']['date'])} "
    f"({fmt_var('pm25', _m['pm25']['value'])} µg/m³).",
    f"CO: mediana {fmt_var('co', _s['co']['median'])} ppm y P75 "
    f"{fmt_var('co', _s['co']['p75'])} ppm. El "
    f"{fmt_pct(_e['co']['pct'])} superó 35 ppm; la mayor mediana diaria fue "
    f"el {fmt_dia(_m['co']['date'])} "
    f"({fmt_var('co', _m['co']['value'])} ppm).",
    f"CO₂: mediana {fmt_var('co2', _s['co2']['median'])} ppm y P75 "
    f"{fmt_var('co2', _s['co2']['p75'])} ppm. El "
    f"{fmt_pct(_e['co2']['pct'])} superó 1000 ppm; los picos son "
    "compatibles con momentos de menor ventilación.",
])
p("La mayoría de las lecturas se mantuvo por debajo de los umbrales, pero "
  "aparecen episodios puntuales de PM2.5 y CO que justifican seguir midiendo "
  "y ventilar. Las medianas diarias más altas de PM2.5 se registraron el "
  "10/10 y el 20/10; la de CO, el 17/10. El CO₂ muestra una base de 400 ppm "
  "con picos de hasta 796 ppm de mediana diaria.")
p("Calidad y limitaciones: las 101 filas históricas con co2=400 y "
  "temperatura=0 se conservan como registro; las 119 filas fuera de rango se "
  "excluyeron del análisis. La estación es única, no tiene calibración de "
  "laboratorio y PM2.5/CO son lecturas instantáneas; el ICA de la EPA se "
  "basa en promedios de 24 h y 8 h. Los resultados describen el período y "
  "no reemplazan una evaluación sanitaria.")
h2("4.1 Umbrales de referencia")
tabla([
    ["Variable", "Referencia utilizada", "Lectura"],
    ["PM2.5", "35 µg/m³ (EPA AQI, 24 h)", "Sobre 35: grupos sensibles."],
    ["CO", "35 ppm (NIOSH REL, 8 h); 50 ppm (OSHA PEL)",
     "Sobre 35: atención."],
    ["CO₂", "1000 ppm (ventilación); 5000 ppm (ocupacional)",
     "Sobre 1000: ventilar."],
    ["Temp. / humedad", "18–26 °C; 30–60 % (ASHRAE, referencia)",
     "Confort orientativo."],
    ["UV / luz", "Valores de referencia local", "No evalúan exposición."],
], cols(0.18, 0.47, 0.35), small=True, negrita_primera=True)
p("Los umbrales permiten leer las mediciones y compararlas, pero no son "
  "límites legales para este contexto ni reemplazan una evaluación "
  "profesional. La estación prioriza la observación de tendencias y la "
  "detección de episodios.")

# ===================== 5. DIFICULTADES =====================
h1("5. Dificultades y soluciones")
tabla([
    ["Dificultad", "Solución aplicada"],
    ["No se consiguió el adaptador del PMS5003 para el protoboard.",
     "Se cortaron los cables y se soldaron las puntas."],
    ["Los imanes de la tapa no cerraban bien y eran difíciles de despegar.",
     "Se reemplazaron por tornillos."],
    ["El MQ-7 necesita estabilización y calibración.",
     "Calentamiento de 30 s y ajuste con R0; lectura analógica."],
    ["El BME280 puede no detectarse en la dirección esperada.",
     "El firmware prueba 0x76 y 0x77 y avisa por monitor serie."],
    ["El GPS puede perder el fix momentáneamente.",
     "Se conserva y reenvía la última coordenada válida."],
    ["El ESP32 se reiniciaba en bucle al iniciar.",
     "Se inicializa la red/AP antes de abrir los sockets."],
    ["El CO₂ mostraba 400 ppm sin datos frescos del Uno.",
     "currentCO2 = 0; el 0 significa «sin lectura»."],
], cols(0.42, 0.58), small=True, negrita_primera=True)
p("Las dificultades se resolvieron con pruebas aisladas, registro de los "
  "códigos que funcionaban y correcciones sucesivas. Ese proceso quedó "
  "documentado en el informe técnico y permitió que el armado final fuera "
  "reproducible.")

# ===================== 6. EQUIPO =====================
h1("6. Equipo y roles")
p("El proyecto fue realizado por un equipo interdisciplinario y contó con el "
  "acompañamiento del docente Tadeo Lobo, de la materia Tecnología de "
  "Control, quien orientó y supervisó el desarrollo.")
tabla([
    ["Integrante / docente", "Rol o aporte"],
    ["Roy Luciano Molina", "Diseño del gabinete."],
    ["Maximo Valdez Leguina", "Diseño del circuito de conexiones electrónicas."],
    ["Candela Rojas Perassi", "Conexiones físicas del circuito."],
    ["María Pía Olivar", "Armado y presentación del gabinete."],
    ["Benicio Gael Pieroni", "Programación web, arquitectura y puesta a punto; "
     "consolidación del informe."],
    ["Joaquín Valdecanto", "Colaboración en el proyecto."],
    ["Tatiana Maturano", "Registro fotográfico del proceso."],
    ["Bautista Argañaraz", "Colaboración en el proyecto."],
    ["Jonás Barreiro", "Informe de sensores, placas y proyecto final."],
    ["Tadeo Lobo (docente)", "Tecnología de Control; acompañamiento y "
     "supervisión."],
], cols(0.28, 0.72), small=True, negrita_primera=True)

# ===================== 7. FOTOS =====================
h1("7. Registro fotográfico")
p("Selección de 8 fotografías del proceso. El informe técnico reúne las 43 "
  "fotografías y los 16 diagramas, esquemas y capturas del Anexo D.")
fig(FIG / "fig_23.jpeg",
    "Figura 7. Equipo durante el proceso de armado y pruebas.", max_h_mm=105)
fig_grid([
    (FIG / "foto_41.jpeg", "Figura 8. Puesta a punto."),
    (FIG / "foto_43.jpeg", "Figura 9. Montaje final."),
    (FIG / "fig_24.jpeg", "Figura 10. Trabajo conjunto en el montaje."),
])

# ===================== 8. VIDEO =====================
h1("8. Video del proyecto")
quote("Archivo: WhatsApp Video 2026-10-29 at 11.16.07.mp4\n"
      "Duración: 2:49 · Formato: MP4 · Tamaño: 35 MB\n"
      "Contenido: estación funcionando y lecturas de todos los sensores "
      "(CO₂, CO, PM2.5, temperatura, humedad, presión, UV, luz y GPS).\n"
      "Entrega: se adjunta al correo, no se copia al repositorio.")
p("El video cumple el máximo de 3 minutos. La síntesis y el video son los "
  "dos entregables principales de la Etapa 1; el informe técnico completo "
  "queda como respaldo.")
h2("8.1 Contenido verificado del video")
tabla([
    ["Contenido", "Verificado"],
    ["Estación funcionando y equipo", "Sí"],
    ["Calidad del aire: CO₂, CO y PM2.5", "Sí"],
    ["Temperatura, humedad, presión, UV y luz", "Sí"],
    ["Ubicación GPS", "Sí"],
], cols(0.72, 0.28), small=True, negrita_primera=True)
h2("Materiales de la entrega")
tabla([
    ["Material", "Ubicación / observación"],
    ["Síntesis para el concurso", "Este PDF, 8–10 páginas."],
    ["Video del proyecto", "WhatsApp Video 2026-10-29 at 11.16.07.mp4; "
     "2:49; se adjunta al correo."],
    ["Informe técnico completo", "Informe_Tucuman_Respira.pdf; respaldo "
     "metodológico y anexo."],
    ["Modelo 3D del gabinete", "Diseño_Hardware/Diseño_Gabinete/Gabinete "
     "para tucuman respira.stl (216 KB)."],
    ["Registro fotográfico", "43 fotos y 16 diagramas en el Anexo D del "
     "informe técnico."],
], cols(0.30, 0.70), small=True, negrita_primera=True)
story.append(PageBreak())

# ===================== 9. CIERRE =====================
h1("9. Conclusiones y trazabilidad")
p("El proyecto logró un sistema completo y funcional: adquisición con dos "
  "microcontroladores, publicación en la nube, panel público, histórico, "
  "mapa, descargas y alarma local con control remoto. La documentación "
  "permitió recuperar el proceso de armado, los componentes y las decisiones "
  "de hardware, y este informe los integra con el detalle técnico del "
  "software y los datos.")
p("Las principales enseñanzas fueron probar los componentes por separado, "
  "separar los firmwares, inicializar la red antes de abrir sockets y "
  "distinguir un valor real de un valor por defecto. Las limitaciones "
  "—calibración, estación única, datos instantáneos y filas históricas— "
  "quedan explicitadas para futuras mejoras.")
tabla([
    ["Sección de la síntesis", "Sección del informe técnico"],
    ["Problema y objetivo", "§2"],
    ["Diseño y construcción", "§5–6"],
    ["Programación y puesta a punto", "§7–8 y §13"],
    ["Datos e interpretación", "§9 y §14"],
    ["Dificultades y soluciones", "§6.4 y §13"],
    ["Equipo y roles", "§3"],
    ["Registro fotográfico", "Anexo D"],
    ["Video y materiales", "Anexo E"],
], cols(0.55, 0.45), small=True, negrita_primera=True)
h2("Checklist de entrega")
tabla([
    ["Ítem", "Estado"],
    ["Síntesis en PDF (8–10 pp.)", "Incluida"],
    ["Video MP4 de 2:49", "Adjuntar al correo"],
    ["Asunto", "Tucumán Respira - Entrega - Escuela Técnica N°5"],
    ["Destinatario", "direcciontecnicayfp.tuc@gmail.com"],
    ["Fecha límite", "30/10/2026"],
], cols(0.38, 0.62), small=True, negrita_primera=True)
p("Fin de la síntesis — «Tucumán Respira», Escuela Técnica N°5, 29/10/2026.")


def main():
    doc = BaseDocTemplate(
        SALIDA, pagesize=A4,
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=16 * mm, bottomMargin=18 * mm,
        title="Síntesis para el concurso — Tucumán Respira 2026",
        author="Equipo Tucumán Respira — Escuela Técnica N°5",
        subject="Síntesis del informe técnico para la Etapa 1 del concurso "
                "Tucumán Respira 2026",
        keywords="Tucumán Respira, concurso, calidad del aire, Arduino Uno, "
                 "ESP32, Supabase, IoT, Escuela Técnica N°5",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
                  id="cuerpo")
    doc.addPageTemplates([PageTemplate(id="todas", frames=[frame],
                                       onPage=pie)])
    doc.build(story)
    print("Generado:", SALIDA)


if __name__ == "__main__":
    main()
