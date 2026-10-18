#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generador del informe técnico unificado «Tucumán Respira».

Regenera Informe_Tucuman_Respira.pdf a partir del contenido del informe.
Umbral de CO actualizado: «dañino» a partir de 35 ppm (NIOSH REL 8 h).
"""
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
    TableStyle, PageBreak,
)

BASE = os.path.dirname(os.path.abspath(__file__))
SALIDA = os.path.join(BASE, "Informe_Tucuman_Respira.pdf")

AZUL = colors.HexColor("#0f172a")
VERDE = colors.HexColor("#059669")
GRIS = colors.HexColor("#64748b")
GRIS_CLARO = colors.HexColor("#d7dee8")
FONDO_SUAVE = colors.HexColor("#f8fafc")
FONDO_COD = colors.HexColor("#f1f5f9")

ANCHO = A4[0] - 30 * mm

S = {
    "marca": ParagraphStyle("marca", fontName="Helvetica-Bold", fontSize=11,
                            textColor=VERDE, leading=15, spaceAfter=4),
    "titulo": ParagraphStyle("titulo", fontName="Helvetica-Bold", fontSize=30,
                             textColor=AZUL, leading=34, spaceAfter=6),
    "subtitulo": ParagraphStyle("titulo2", fontName="Helvetica", fontSize=13,
                                textColor=GRIS, leading=17, spaceAfter=10),
    "autor": ParagraphStyle("autor", fontName="Helvetica-Bold", fontSize=11,
                            textColor=AZUL, leading=15, spaceAfter=10),
    "h1": ParagraphStyle("h1", fontName="Helvetica-Bold", fontSize=15,
                         textColor=AZUL, leading=19, spaceBefore=12,
                         spaceAfter=6, keepWithNext=1),
    "h2": ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=10.5,
                         textColor=VERDE, leading=14, spaceBefore=9,
                         spaceAfter=3, keepWithNext=1),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9,
                           textColor=colors.HexColor("#1e293b"), leading=12.6,
                           alignment=TA_JUSTIFY, spaceAfter=5),
    "bullet": ParagraphStyle("bullet", fontName="Helvetica", fontSize=9,
                             textColor=colors.HexColor("#1e293b"), leading=12.5,
                             leftIndent=13, bulletIndent=3, spaceAfter=2.5),
    "celda": ParagraphStyle("celda", fontName="Helvetica", fontSize=8,
                            textColor=colors.HexColor("#1e293b"), leading=10.5),
    "celda_b": ParagraphStyle("celda_b", fontName="Helvetica-Bold", fontSize=8,
                              textColor=AZUL, leading=10.5),
    "th": ParagraphStyle("th", fontName="Helvetica-Bold", fontSize=8,
                         textColor=colors.white, leading=10.5),
    "small": ParagraphStyle("small", fontName="Helvetica", fontSize=7.5,
                            textColor=GRIS, leading=10),
    "code": ParagraphStyle("code", fontName="Courier", fontSize=7, leading=8.8,
                           textColor=colors.HexColor("#0f172a"),
                           backColor=FONDO_COD, borderColor=GRIS_CLARO,
                           borderWidth=0.5, borderPadding=6, spaceBefore=2,
                           spaceAfter=6),
    "quote": ParagraphStyle("quote", fontName="Helvetica", fontSize=8.5,
                            textColor=colors.HexColor("#0f172a"), leading=11.5,
                            leftIndent=14, rightIndent=6,
                            backColor=FONDO_SUAVE, borderColor=GRIS_CLARO,
                            borderWidth=0.5, borderPadding=6, spaceAfter=6),
    "indice": ParagraphStyle("indice", fontName="Helvetica", fontSize=9.5,
                             textColor=AZUL, leading=15),
}

story = []


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


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


def tabla(rows, anchos, negrita_primera=False):
    data = []
    for ri, row in enumerate(rows):
        fila = []
        for ci, cell in enumerate(row):
            est = S["th"] if ri == 0 else (
                S["celda_b"] if (negrita_primera and ci == 0) else S["celda"])
            fila.append(Paragraph(esc(cell), est))
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


def pie(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#e2e8f0"))
    canvas.setLineWidth(0.5)
    canvas.line(15 * mm, 14 * mm, A4[0] - 15 * mm, 14 * mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(GRIS)
    canvas.drawString(15 * mm, 10 * mm,
                      "Tucumán Respira — Encargado: Benicio Gael Pieroni")
    canvas.drawRightString(A4[0] - 15 * mm, 10 * mm, "Página %d" % doc.page)
    canvas.restoreState()


# ===================== PORTADA =====================
story.append(Spacer(1, 12))
story.append(Paragraph("INFORME TÉCNICO DEL PROYECTO", S["marca"]))
story.append(Spacer(1, 4))
story.append(Paragraph("Tucumán Respira", S["titulo"]))
story.append(Paragraph(
    "Panel web de monitoreo de calidad del aire IoT y firmwares de la "
    "estación (Arduino Uno + ESP32)", S["body"]))
story.append(Spacer(1, 8))
story.append(Paragraph("Encargado del trabajo: Benicio Gael Pieroni",
                       S["body"]))
story.append(Spacer(1, 12))

tabla([
    ["Aspecto", "Detalle"],
    ["Encargado", "Benicio Gael Pieroni"],
    ["Proyecto", "Tucumán Respira — Estación de monitoreo ambiental IoT"],
    ["Entregables",
     "Aplicación web estática (index.html · styles.css · app.js) y dos "
     "firmwares: Arduino Uno (sketch_oct17a) y ESP32 (sketch_oct17b)"],
    ["Fuente de datos",
     "Supabase (PostgreSQL) — tabla «mediciones» (API PostgREST)"],
    ["Alcance de este informe",
     "Documento único que consolida el informe del panel web, el detalle de "
     "los cambios de umbrales realistas y los firmwares con su integración y "
     "el control del zumbador."],
    ["Fecha del informe", "18/10/2026"],
    ["Estado",
     "Implementado, integrado y verificado (pendiente de publicación online)"],
], [95, 410], negrita_primera=True)

p("Este documento reemplaza y unifica los informes anteriores («Informe "
  "técnico del panel web» y «Cambios de umbrales realistas») y agrega los "
  "firmwares del Arduino Uno y del ESP32, la integración entre ambos, la base "
  "de datos y el control remoto del zumbador desde la web. Describe el diseño, "
  "la arquitectura, las funcionalidades, los umbrales de referencia, las "
  "correcciones aplicadas y las verificaciones realizadas durante el "
  "desarrollo del sistema «Tucumán Respira».")
story.append(PageBreak())

# ===================== ÍNDICE =====================
story.append(Paragraph("Índice de contenidos", S["h1"]))
for t in [
    "1. Resumen ejecutivo", "2. Contexto y objetivos del proyecto",
    "3. Decisiones de diseño acordadas", "4. Arquitectura y stack tecnológico",
    "5. Estructura de archivos y métricas de código",
    "6. Fuente de datos: Supabase", "7. Métricas y umbrales de referencia",
    "8. Cambios de umbrales realistas (antes / después)",
    "9. Índice de Calidad del Aire (ICA / EPA)",
    "10. Funcionalidades del panel web",
    "11. Estados del sistema y comportamiento «offline»",
    "12. Adaptación responsive (móviles y tablets)", "13. Seguridad",
    "14. Firmware del Arduino Uno (adquisición y GPS)",
    "15. Firmware del ESP32 (WiFi, Supabase y alarma)",
    "16. Integración del sistema y control del zumbador",
    "17. Correcciones de errores durante el desarrollo",
    "18. Verificaciones y pruebas realizadas",
    "19. Cómo ejecutar y visualizar el sistema",
    "20. Pendientes y recomendaciones", "Anexo A — Configuración y claves",
    "Anexo B — Exportación de datos (CSV / JSON)",
    "Anexo C — Trama de comunicación Uno → ESP32",
    "Anexo D — Prompt para recrear el proyecto con opencode",
]:
    story.append(Paragraph(esc(t), S["indice"]))
story.append(PageBreak())

# ===================== 1. RESUMEN =====================
h1("1. Resumen ejecutivo")
p("«Tucumán Respira» es una estación de monitoreo ambiental que mide la "
  "calidad del aire y variables meteorológicas y publica sus lecturas en la "
  "nube. El sistema se compone de cuatro piezas: un Arduino Uno que adquiere "
  "los sensores y calcula la posición GPS; un ESP32 que se conecta a Wi-Fi, "
  "envía las mediciones a Supabase y gobierna una alarma sonora con zumbador; "
  "una base de datos PostgreSQL en Supabase; y una aplicación web estática "
  "que rediseñada por completo muestra los datos en vivo y permite "
  "descargarlos y detener la alarma de forma remota.")
p("Este informe único documenta el panel web, los umbrales realistas, los dos "
  "firmwares y su integración. Entre los resultados se destacan: un panel "
  "claro con datos en tiempo real y respaldo por sondeo, 8 métricas con "
  "umbrales por estándar, un panel claro con datos en tiempo real y respaldo "
  "por sondeo, 8 métricas con umbrales por estándar (EPA, OMS/ICNIRP, "
  "OSHA/NIOSH, NIOSH y ASHRAE) con su fuente visible, el ICA (EPA) con PM2.5 y "
  "CO, histórico y gráficos, descarga pública en CSV y JSON, mapa con "
  "OpenStreetMap y botón para detener la alarma.")
story.append(Spacer(1, 2))
h2("Resultados")
bullets([
    "Panel con datos en tiempo real, respaldo por sondeo cada 15 s y 8 "
    "métricas con umbrales por estándar, cada una con su fuente visible.",
    "Índice de calidad del aire (ICA/EPA) calculado con PM2.5 y CO.",
    "Histórico y gráfico de tendencia; descarga pública en CSV y JSON "
    "(últimas 100, 500, 1000 o todas las filas).",
    "Mapa de ubicación con OpenStreetMap y marcador de la estación; usa la "
    "última coordenada GPS válida.",
    "Firmware del Arduino Uno: 8 sensores, GPS NMEA y trama de 9 campos hacia "
    "el ESP32.",
    "Firmware del ESP32: Wi-Fi (modo estación + punto de acceso de "
    "configuración), carga a Supabase, alarma por zumbador y endpoints de "
    "control (/status, /alarma, /silenciar).",
    "Diseño responsive con puntos de quiebre en 1024, 640 y 400 píxeles, sin "
    "scroll horizontal en celulares.",
])
story.append(PageBreak())

# ===================== 2. CONTEXTO =====================
h1("2. Contexto y objetivos del proyecto")
p("«Tucumán Respira» es una estación de monitoreo ambiental de bajo costo "
  "construida con microcontroladores (Arduino Uno R3 y ESP32) y sensores de "
  "calidad del aire y clima. Las mediciones se envían de forma periódica a "
  "Supabase y quedan disponibles para consulta pública.")
h2("Objetivo general")
p("Ofrecer un sistema completo de monitoreo —desde la adquisición en campo "
  "hasta la publicación web— que permita al público comprender el estado de "
  "la calidad del aire y consultar los datos históricos.")
h2("Objetivos específicos")
bullets([
    "Medir en forma continua variables de calidad del aire (PM2.5, CO₂, CO), "
    "meteorológicas (temperatura, humedad, presión), radiación UV y luz "
    "ambiental.",
    "Registrar la ubicación geográfica (GPS) de las mediciones.",
    "Publicar los datos en la nube y ofrecer un panel público que los muestre "
    "de forma clara.",
    "Avisar localmente (alarma sonora) cuando la calidad del aire supera "
    "umbrales peligrosos, y permitir silenciar esa alarma desde la aplicación "
    "web.",
    "Permitir la descarga libre de los datos crudos (CSV/JSON).",
    "Garantizar una correcta visualización en celulares y aplicar "
    "correcciones de seguridad.",
])
h2("Perfil de usuarios")
p("Público general: docentes, estudiantes y personas técnicas o interesadas "
  "en la calidad del aire. La interfaz prioriza la legibilidad, el lenguaje "
  "claro y la accesibilidad desde cualquier dispositivo.")

# ===================== 3. DECISIONES =====================
h1("3. Decisiones de diseño acordadas")
p("Las siguientes decisiones fueron acordadas con el responsable del proyecto "
  "antes y durante la implementación, y definen el comportamiento actual del "
  "sistema.")
tabla([
    ["Tema", "Decisión adoptada"],
    ["Base de partida", "Versión simple existente del panel (se rediseñó sobre ella)."],
    ["Tipo de proyecto", "Proyecto real, conectado a la base de datos real de la estación."],
    ["Datos simulados", "No se muestran datos simulados. Solo se presentan mediciones reales."],
    ["Formato de entrega", "Aplicación estática de 3 archivos (HTML + CSS + JS) más dos firmwares."],
    ["Identidad visual", "Nombre «Tucumán Respira», tema oscuro/claro con verde esmeralda."],
    ["Público objetivo", "General: docentes, estudiantes y técnicos."],
    ["Prioridad", "Estado de la calidad del aire + valor de cada sensor."],
    ["Interacción", "Clic en un sensor abre su histórico (panel modal)."],
    ["Descarga", "Botón público, formatos CSV y JSON, últimas 100 por defecto."],
    ["Alertas y peligro",
     "Cada métrica tiene niveles de peligro con su fuente; el estado general "
     "(ICA) se calcula con PM2.5 y CO."],
    ["Fuente del umbral", "Se muestra en la interfaz la fuente de cada umbral."],
    ["Actualización", "Tiempo real + marca de última actualización (fecha y hora + relativa)."],
    ["Mapa", "Ubicación GPS de la estación sobre mosaicos de OpenStreetMap (sin clave)."],
    ["Zumbador", "Ubicado y gobernado por el ESP32 (GPIO 23); la alarma la decide la propia ESP32."],
    ["GPS", "Conectado al Arduino Uno en los pines 7 (RX) y 8 (TX) por SoftwareSerial."],
    ["Detener alarma", "Botón directo en la app que consulta a la ESP32; la IP se obtiene sola desde Supabase."],
    ["Base de datos", "No se cambian los campos existentes; solo se agrega «ip_dispositivo»."],
    ["Control de versiones", "No se modificó el repositorio Git durante el desarrollo."],
    ["Seguridad", "Se aplicaron las correcciones de seguridad indicadas."],
], [105, 400], negrita_primera=True)
story.append(PageBreak())

# ===================== 4. ARQUITECTURA =====================
h1("4. Arquitectura y stack tecnológico")
p("La arquitectura es de cuatro capas con comunicación en cascada:")
bullets([
    "Adquisición (Arduino Uno): lee los sensores y el GPS y envía una trama "
    "de 9 campos por puerto serie al ESP32.",
    "Enlace y nube (ESP32): se conecta al Wi-Fi del lugar, expone un punto de "
    "acceso de configuración y realiza peticiones HTTPS a la API REST de "
    "Supabase (PostgREST).",
    "Persistencia (Supabase): base PostgreSQL con la tabla «mediciones».",
    "Presentación (app web): aplicación estática que lee Supabase y, para la "
    "alarma, consulta directamente al ESP32 en la red local.",
])
p("Flujo de datos: Estación (Arduino Uno → ESP32) → Supabase (PostgreSQL + "
  "Realtime) → navegador (fetch REST + canal Realtime) → render de la "
  "interfaz.")
h2("Tecnologías y librerías utilizadas")
tabla([
    ["Recurso", "Versión / origen", "Uso en el proyecto"],
    ["HTML5 / CSS3 / JavaScript", "Nativo", "Estructura, estilos y lógica de la aplicación."],
    ["Lucide", "unpkg @latest (v1.56.0)", "Iconografía de la interfaz (SVG)."],
    ["Chart.js", "CDN 4.4.1", "Gráfico de tendencia y gráficos de histórico por sensor."],
    ["Leaflet", "CDN 1.9.4", "Mapa de ubicación de la estación."],
    ["supabase-js", "CDN @supabase/supabase-js@2", "Cliente Realtime (suscripción a nuevas filas)."],
    ["Supabase REST", "API PostgREST", "Lectura de mediciones y descargas."],
    ["Arduino Uno", "ATmega328P (core avr 1.8.8)", "Lectura de sensores y GPS; trama serie."],
    ["ESP32", "ESP32 (core 3.3.12)", "Wi-Fi + HTTPS, alarma y portal de configuración."],
    ["Supabase", "PostgreSQL / PostgREST", "Almacenamiento y API REST."],
], [130, 145, 230], negrita_primera=True)
h2("Justificación de las librerías")
p("Se optó por librerías livianas y ampliamente utilizadas, cargadas por CDN "
  "para mantener la aplicación en solo 3 archivos. Se descartó el uso de "
  "frameworks CSS pesados (por ejemplo, Tailwind) y de Font Awesome, "
  "reemplazando los íconos por Lucide (SVG) y los estilos por CSS propio, con "
  "el objetivo de reducir el peso y mantener el control total del diseño. "
  "Para el mapa se pasó de Carto a OpenStreetMap para no depender de una "
  "clave de API.")

# ===================== 5. ESTRUCTURA =====================
h1("5. Estructura de archivos y métricas de código")
p("El proyecto se organiza en la aplicación web y los dos firmwares.")
tabla([
    ["Archivo", "Rol", "Líneas aprox."],
    ["index.html", "Estructura y semántica de la interfaz; carga de librerías y de app.js.", "271"],
    ["styles.css", "Sistema de diseño: tokens de tema, componentes y reglas responsive.", "678"],
    ["app.js", "Configuración, datos, clasificación, gráficos, mapa, modales y descargas.", "1010"],
    ["sketch_oct17a.ino", "Firmware del Arduino Uno (adquisición, GPS y trama serie).", "274"],
    ["sketch_oct17b.ino", "Firmware del ESP32 (WiFi, Supabase, alarma y portal).", "841"],
    ["Total", "—", "≈ 3.074"],
], [95, 340, 75], negrita_primera=True)
h2("Organización interna de app.js")
bullets([
    "CONFIG: parámetros centrales (URL y clave de Supabase, tabla, límites, "
    "tiempos, coordenadas por defecto, clave del dispositivo y minutos de "
    "silencio).",
    "METRICS: definición de los 8 sensores, unidades, decimales, umbrales y "
    "fuentes.",
    "TREND_TABS y AQI_*: pestañas del gráfico de tendencia y tablas del índice "
    "de calidad del aire.",
    "Utilidades: formato de fecha/hora, tiempo relativo, formateo, escapado de "
    "CSV y validación de GPS.",
    "ICA (EPA): cálculo del subíndice y del índice global.",
    "Render: construcción de tarjetas, banner, resumen, reloj de estado, mapa, "
    "gráficos, modales y descargas.",
    "Carga de datos: lectura inicial, Realtime y sondeo de respaldo; e "
    "inicialización.",
])
story.append(PageBreak())

# ===================== 6. SUPABASE =====================
h1("6. Fuente de datos: Supabase")
p("La información proviene de un proyecto de Supabase (PostgreSQL) con la API "
  "PostgREST habilitada. La tabla utilizada es «mediciones».")
tabla([
    ["Campo", "Tipo", "Significado", "Unidad"],
    ["id", "entero", "Identificador autoincremental de la fila.", "—"],
    ["created_at", "timestamp", "Fecha y hora de la lectura (UTC).", "ISO-8601"],
    ["co2", "numérico", "Dióxido de carbono.", "ppm"],
    ["co", "numérico", "Monóxido de carbono.", "ppm"],
    ["pm25", "numérico", "Material particulado fino (PM2.5).", "µg/m³"],
    ["temperatura", "numérico", "Temperatura ambiente.", "°C"],
    ["humedad", "numérico", "Humedad relativa.", "%"],
    ["presion", "numérico", "Presión atmosférica.", "hPa"],
    ["uv", "numérico", "Radiación ultravioleta (irradiancia).", "mW/cm²"],
    ["luz", "numérico", "Luminosidad ambiental.", "lux"],
    ["latitud", "numérico", "Latitud GPS de la estación.", "grados"],
    ["longitud", "numérico", "Longitud GPS de la estación.", "grados"],
    ["ip_dispositivo", "texto", "IP local actual del ESP32 (nueva columna).", "IPv4"],
], [85, 70, 275, 70], negrita_primera=True)
h2("Estado verificado de la base de datos (al 18/10/2026)")
tabla([
    ["Métrica", "Valor"],
    ["Filas totales", "1.284"],
    ["Primera lectura", "05/10/2026 00:45:18 UTC"],
    ["Última lectura", "18/10/2026 15:50:53 UTC"],
    ["Lecturas con coordenadas", "533"],
    ["Lecturas sin coordenadas (firmware previo sin GPS)", "751"],
    ["Lecturas con «ip_dispositivo»", "117 (desde que se activó la publicación de la IP)"],
], [330, 175], negrita_primera=True)
p("La columna «ip_dispositivo» permite que la aplicación descubra sola la "
  "dirección de la estación en la red local y, con ella, detener el zumbador "
  "sin que el usuario tenga que escribir ninguna IP.")
story.append(PageBreak())

# ===================== 7. UMBRALES =====================
h1("7. Métricas y umbrales de referencia")
p("Cada sensor se clasifica según rangos de referencia tomados de fuentes "
  "reconocidas de salud y seguridad. Todas las métricas cuentan con niveles "
  "que llegan a «peligro», cada uno con su fuente visible en la interfaz. El "
  "estado general (índice de calidad del aire) se calcula con PM2.5 y CO; el "
  "resto de las métricas marcan su propio nivel de alerta en su tarjeta.")
tabla([
    ["Métrica", "Unidad", "Umbrales y etiquetas", "Fuente"],
    ["CO₂", "ppm",
     "Bueno ≤800 · Aceptable ≤1000 · Ventilación pobre ≤1500 · Alta (PEL 8 h) "
     "≤5000 · Muy alta (STEL) ≤30000 · Peligro >30000",
     "OSHA/NIOSH · ASHRAE (ventilación)"],
    ["CO (ICA)", "ppm",
     "Bueno ≤4,4 · Moderado ≤34,9 · Dañino ≤50 · Muy dañino ≤100 · Peligroso "
     "≤200 · Extremo >200",
     "NIOSH REL (35 ppm) · OSHA PEL (50 ppm)"],
    ["PM2.5 (ICA)", "µg/m³",
     "Bueno ≤9,0 · Moderado ≤35,4 · Grupos sensibles ≤55,4 · Dañino ≤125,4 · "
     "Muy dañino ≤225,4 · Peligroso >225,4",
     "EPA AQI 2024 (24 h)"],
    ["Temperatura", "°C",
     "Hipotermia ≤0 · Frío ≤10 · Confortable ≤27 · Precaución por calor ≤32 · "
     "Extrema precaución ≤39 · Peligro ≤52 · Peligro extremo >52",
     "NWS/OSHA (calor) · NIOSH (frío)"],
    ["Humedad", "%",
     "Muy seco ≤20 · Seco ≤30 · Ideal ≤60 · Algo húmedo ≤70 · Riesgo de moho "
     "≤85 · Alto riesgo de moho >85",
     "OMS (humedad y moho) · ASHRAE"],
    ["Presión", "hPa", "Baja ≤1004,9 · Normal ≤1020 · Alta >1020",
     "Informativo (sin umbral de salud)"],
    ["UV", "mW/cm²", "Bajo ≤1 · Moderado ≤3 · Alto ≤6 · Muy alto ≤10 · "
     "Extremo >10", "Sensor ML8511 (irradiancia)"],
    ["Luz", "lux", "Oscuridad ≤9,9 · Penumbra ≤99,9 · Interior ≤499 · Pleno "
     "sol >499", "Informativo (sin umbral de salud)"],
], [75, 45, 275, 110], negrita_primera=True)
h2("Notas")
bullets([
    "Los valores son de referencia para interpretar las mediciones y no "
    "constituyen diagnóstico sanitario.",
    "El calor y el frío se evalúan por temperatura seca; el índice de calor "
    "real depende además de la humedad y el viento.",
    "La OMS no fija un umbral cuantitativo de humedad: los niveles altos "
    "indican riesgo de moho, no peligro agudo.",
    "Presión y luz se muestran como referencia: no existe un umbral de peligro "
    "para la salud humana en esos rangos.",
    "El CO₂ alto es peligroso solo en niveles ocupacionales (OSHA/NIOSH); en "
    "interiores es ante todo un indicador de ventilación.",
    "El CO se clasifica con el límite de referencia de 35 ppm (REL de NIOSH, "
    "8 h); su nivel «dañino» comienza en ese valor.",
    "El estado general (ICA) se calcula con PM2.5 y CO; cada métrica, además, "
    "marca su propia alerta en la tarjeta.",
])
story.append(PageBreak())

# ===================== 8. CAMBIOS =====================
h1("8. Cambios de umbrales realistas (antes / después)")
p("Como parte del proyecto se revisaron y recalibraron los umbrales de todas "
  "las métricas contra fuentes de salud y seguridad pública, se corrigieron "
  "las etiquetas que sugerían una norma inexistente y se fijó la fuente "
  "visible de cada umbral. El objetivo fue que cada sensor clasifique con "
  "niveles de peligro realistas y honestos, sin rangos inventados.")
h2("3.1 Valores que cambiaron")
tabla([
    ["Métrica", "Antes", "Ahora", "Fuente"],
    ["CO₂",
     "Bueno ≤800 · Aceptable ≤1000 · Ventilar ≤2000 · Muy alto ≤5000 · Riesgo "
     ">5000 (fuente «ASHRAE»).",
     "Bueno ≤800 · Aceptable ≤1000 · Ventilación pobre ≤1500 · Alta (PEL 8 h) "
     "≤5000 · Muy alta (STEL) ≤30000 · Peligro >30000.",
     "OSHA/NIOSH · ASHRAE"],
    ["CO (ICA)",
     "Bueno ≤4,4 · Moderado ≤9,4 · Grupos sensibles ≤12,4 · Dañino ≤15,4 · Muy "
     "dañino ≤30,4 · Peligroso ≤50,4 · Extremo >50,4 (fuente «EPA AQI 8 h»).",
     "Bueno ≤4,4 · Moderado ≤34,9 · Dañino ≤50 · Muy dañino ≤100 · Peligroso "
     "≤200 · Extremo >200.",
     "NIOSH REL (35 ppm) · OSHA PEL (50 ppm)"],
    ["Temperatura",
     "Frío ≤16,9 · Fresco ≤19,9 · Confortable ≤26 · Cálido ≤29,9 · Extremo "
     ">29,9 (fuente «ASHRAE 55»).",
     "Hipotermia ≤0 · Frío ≤10 · Confortable ≤27 · Precaución por calor ≤32 · "
     "Extrema precaución ≤39 · Peligro ≤52 · Peligro extremo >52.",
     "NWS/OSHA (calor) · NIOSH (frío)"],
    ["Humedad",
     "Seco ≤29,9 · Ideal ≤60 · Húmedo >60 (fuente «ASHRAE 62.1»).",
     "Muy seco ≤20 · Seco ≤30 · Ideal ≤60 · Algo húmedo ≤70 · Riesgo de moho "
     "≤85 · Alto riesgo de moho >85.",
     "OMS (humedad y moho) · ASHRAE"],
], [70, 150, 165, 115], negrita_primera=True)
p("Frente a su norma, PM2.5 (EPA AQI 2024) no cambió. El UV dejó de "
  "expresarse como índice adimensional y ahora se muestra como irradiancia en "
  "mW/cm² (lectura cruda del ML8511), corregida con la referencia real del ADC "
  "del Uno (5 V). En el CO se elevó el umbral de «dañino» de 15,4 a 35 ppm "
  "(REL de NIOSH, 8 h) para que la alarma no se dispare con valores bajos ni "
  "en ausencia de riesgo real. Se activó el resaltado de alerta para CO₂, "
  "temperatura y humedad, de modo que cuando alcanzan un nivel marcado en rojo "
  "su tarjeta se destaca. Presión y luz quedaron como referencia, porque no "
  "tienen umbral de peligro real.")
h2("3.2 Texto del panel «Acerca del sistema» (index.html)")
p("El texto anterior decía que solo PM2.5, CO y UV generaban alertas y "
  "mencionaba el UV como parte del estado general, lo que no era exacto. Se "
  "reemplazó por:")
quote("El estado general (índice de calidad del aire) se calcula con PM2.5 "
      "(EPA) y CO, tomando para el CO el umbral de referencia de 35 ppm (NIOSH "
      "REL) y 50 ppm (OSHA PEL). Los demás parámetros usan umbrales propios "
      "basados en fuentes de salud pública (OSHA/NIOSH, OMS y NWS) para "
      "indicar su nivel; cuando alcanzan un valor dañino, su tarjeta se "
      "resalta como alerta.")
h2("3.3 Criterio de umbrales y fuentes")
tabla([
    ["Métrica", "Fuente y criterio"],
    ["PM2.5 (ICA)", "EPA AQI 2024. Valores oficiales de subíndice (24 h)."],
    ["CO (ICA)",
     "NIOSH REL (35 ppm, 8 h) y OSHA PEL (50 ppm). El umbral de «dañino» del "
     "CO se fija en 35 ppm."],
    ["UV", "Sensor ML8511 (GY-8511). Irradiancia en mW/cm². Bajo, Moderado, "
     "Alto, Muy alto, Extremo."],
    ["CO₂", "OSHA/NIOSH (PEL 5000 ppm 8 h; STEL 30000 ppm; IDLH 40000 ppm) y "
     "ASHRAE como referencia de ventilación."],
    ["Temperatura", "NWS/OSHA (estrés por calor) y NIOSH (estrés por frío), "
     "sobre temperatura seca."],
    ["Humedad", "OMS (humedad y moho) y ASHRAE (recomendación 30–60 %). Los "
     "niveles altos indican riesgo de moho."],
    ["Presión / Luz", "Referencia. No existe un umbral de peligro para la "
     "salud en esos rangos."],
], [110, 395], negrita_primera=True)
h2("3.4 Aclaraciones honestas")
bullets([
    "El calor real depende también de la humedad y el viento (índice de "
    "calor); aquí se evalúa por temperatura seca.",
    "La OMS no fija un umbral cuantitativo de humedad; por eso los valores "
    "altos se rotulan como «riesgo de moho».",
    "El CO₂ solo es tóxico en concentraciones ocupacionales; en interiores es, "
    "sobre todo, un indicador de ventilación.",
    "El índice ICA de la EPA se basa en promedios (PM2.5 24 h, CO 8 h); la app "
    "usa la lectura del momento, tal como se acordó.",
    "Para el CO se adopta el límite de referencia de NIOSH (35 ppm, 8 h): por "
    "debajo de ese valor el CO no se marca como «dañino».",
    "Presión y luz se dejan como referencia para no inventar un peligro que la "
    "ciencia no respalda.",
])
story.append(PageBreak())

# ===================== 9. ICA =====================
h1("9. Índice de Calidad del Aire (ICA / EPA)")
p("El estado general de la calidad del aire se resume con un índice estilo "
  "ICA (Air Quality Index de la EPA). Se calcula el subíndice de PM2.5 y el de "
  "CO y se toma el peor de los dos como índice global del momento. La alarma "
  "sonora del ESP32 replica este cálculo.")
tabla([
    ["Rango ICA", "Categoría", "Descripción"],
    ["0 – 50", "Buena",
     "La calidad del aire es satisfactoria y el riesgo para la salud es bajo."],
    ["51 – 100", "Moderada",
     "Calidad aceptable; personas muy sensibles podrían notar molestias leves."],
    ["101 – 150", "Dañina para grupos sensibles",
     "Los grupos sensibles pueden experimentar efectos en la salud."],
    ["151 – 200", "Dañina", "Todos pueden comenzar a sentir efectos en la salud."],
    ["201 – 300", "Muy dañina", "Riesgo para la salud de toda la población."],
    ["301 – 500", "Peligrosa", "Condiciones de emergencia sanitaria."],
], [90, 150, 265], negrita_primera=True)
p("Además del número y la categoría, el panel muestra la descripción, una "
  "recomendación sanitaria acorde y un indicador del estado de la alerta del "
  "equipo (NORMAL, PRECAUCIÓN, ALERTA o ALERTA CRÍTICA).")
h2("Interpolación lineal")
p("El subíndice se obtiene por interpolación lineal dentro del rango "
  "correspondiente (por ejemplo, para PM2.5 con concentración 12 µg/m³ "
  "corresponde al tramo 9,1–35,4 → subíndice 51–100). El método replica el "
  "empleado por la EPA. La alarma sonora se activa cuando el ICA supera 100 y "
  "se corta automáticamente cuando baja de 80.")
p("En el caso del CO, el subíndice supera 100 recién a partir de 35 ppm (REL "
  "de NIOSH, 8 h); por debajo de ese valor el CO no activa la alarma por sí "
  "solo. El resto de la escala del CO se extiende hacia arriba (peligroso "
  ">200 ppm) siguiendo el mismo criterio de referencia.")

# ===================== 10. FUNCIONALIDADES =====================
h1("10. Funcionalidades del panel web")
h2("10.1 Encabezado y estado de conexión")
bullets([
    "Barra superior fija («sticky») con la identidad «Tucumán Respira»; el "
    "logo recarga la página.",
    "Insignia de conexión con indicador de color: en vivo, retraso o sin "
    "conexión, con tiempo relativo.",
    "Marca de última actualización con fecha y hora completas (dd/mm/aaaa "
    "hh:mm:ss).",
    "Botones de acción: descargar, cambiar tema, información y enlace a GitHub.",
])
h2("10.2 Banner de calidad del aire y tarjetas de sensores")
bullets([
    "Número ICA grande, categoría, descripción, recomendación sanitaria e "
    "indicador de la alerta del equipo.",
    "Ocho tarjetas (CO₂, CO, PM2.5, temperatura, humedad, presión, UV y luz) "
    "con valor, unidad, etiqueta de clasificación y barra de nivel; se "
    "resaltan en nivel peligroso.",
    "Al tocar una tarjeta se abre su histórico.",
])
h2("10.3 Resumen reciente y gráfico de tendencia")
bullets([
    "Mín./máx. de temperatura, pico de PM2.5, promedio de CO₂ y de humedad de "
    "las últimas 100 lecturas.",
    "Pestañas Aire (PM2.5 y CO), Clima (temperatura y humedad), Gases (CO₂ y "
    "CO) y Luz/UV.",
])
h2("10.4 Histórico por sensor (modal)")
bullets([
    "Estadísticas (actual, mín., promedio, máx.), selector de 20/50/100 puntos "
    "y gráfico del sensor.",
    "Se construye con el modal ya abierto y se redimensiona para evitar "
    "gráficos colapsados.",
])
h2("10.5 Mapa de ubicación")
bullets([
    "Mapa construido con Leaflet y mosaicos de OpenStreetMap (sin clave de "
    "API), con marcador de la estación.",
    "Muestra la insignia «Ubicación por GPS» y las coordenadas; si la lectura "
    "más reciente no tiene posición válida, se usa la última coordenada GPS "
    "válida y se indica «Última ubicación conocida».",
    "Incluye un enlace «Ver en Google Maps» cuando hay coordenadas y recalcula "
    "su tamaño al girar el dispositivo.",
])
h2("10.6 Descarga pública de datos")
bullets([
    "Formatos CSV (planilla) y JSON (datos crudos); rangos: últimas 100 (por "
    "defecto), 500, 1000 o todas.",
    "La descarga de «todas» usa paginación por rangos para traer el conjunto "
    "completo.",
])
h2("10.7 Control del zumbador desde la app")
bullets([
    "Botón «Detener zumbador» en el panel de alerta.",
    "La aplicación obtiene la IP de la estación automáticamente desde el "
    "último registro de Supabase (campo «ip_dispositivo»); si aún no hay "
    "ninguno, usa 192.168.4.1 (punto de acceso de la ESP32).",
    "El botón envía la orden al endpoint /silenciar del ESP32; la respuesta "
    "indica los minutos de silencio.",
])
h2("10.7b Tema y detalles")
bullets([
    "Tema claro/oscuro persistente en el navegador; gráficos y mapa se "
    "recolorean al cambiar.",
    "Aviso automático de estación desconectada, descartable, y actualización "
    "Realtime + sondeo cada 15 s.",
])
story.append(PageBreak())

# ===================== 11. ESTADOS OFFLINE =====================
h1("11. Estados del sistema y comportamiento «offline»")
p("La aplicación contempla y comunica con claridad los distintos estados de "
  "los datos, un aspecto clave cuando la estación no transmite.")
tabla([
    ["Situación", "Comportamiento de la interfaz"],
    ["Cargando", "Tarjetas «esqueleto» animadas; indicador «Conectando…»."],
    ["En vivo (≤120 s)", "Indicador verde con pulso; texto «En vivo · hace X»."],
    ["Retraso (≤300 s)", "Indicador ámbar; texto «Retraso · hace X»."],
    ["Sin conexión (>300 s)", "Indicador rojo; aviso con la fecha y hora de la última lectura."],
    ["Sin datos", "Valores «--» y etiqueta «Sin datos»; ICA mostrado como «--»."],
    ["Campo puntual nulo", "Se muestra «--» solo en esa métrica, sin afectar al resto."],
    ["Sin GPS", "Se usa la última coordenada válida; si no hay ninguna, el mapa se centra por defecto."],
], [150, 355], negrita_primera=True)
p("Un vigilante («watchdog») actualiza el estado cada segundo y recalcula el "
  "tiempo transcurrido respecto de la última lectura, de modo que el mensaje "
  "siempre refleja la realidad, incluso si no llegan datos nuevos.")

# ===================== 12. RESPONSIVE =====================
h1("12. Adaptación responsive (móviles y tablets)")
tabla([
    ["Ancho", "Cambios principales"],
    ["≤ 1024 px", "El banner y el resumen pasan a una columna; sensores en 2 "
     "columnas; tendencia y mapa se apilan."],
    ["≤ 640 px", "Marca compacta; insignia de conexión a ancho completo; una "
     "columna de sensores; tipografías y paddings reducidos; gráficos y mapa "
     "de 240–260 px; campos de descarga en una columna; modales con menos "
     "margen."],
    ["≤ 400 px", "Botones, tipografías y pestañas aún más compactos."],
], [75, 430], negrita_primera=True)
bullets([
    "El gráfico del histórico se construye con el modal ya abierto para evitar "
    "gráficos colapsados.",
    "El mapa recalcula su tamaño al girar el dispositivo o redimensionar la "
    "ventana.",
    "El aviso «offline» se envuelve en un contenedor con el ancho y los "
    "márgenes del resto; no desborda.",
    "El modal de descarga usa columnas minmax(0,1fr) y min-width:0 para no "
    "desbordar al abrir los desplegables.",
])
story.append(PageBreak())

# ===================== 13. SEGURIDAD =====================
h1("13. Seguridad")
p("La aplicación es de solo lectura sobre los datos públicos y aplica "
  "correcciones de seguridad en el cliente y en el dispositivo.")
bullets([
    "La clave de Supabase usada es pública (anon) y de solo lectura; nunca se "
    "expone la clave de servicio.",
    "Todas las consultas a Supabase son de lectura (GET) y los datos son "
    "públicos.",
    "El botón de descarga arma el archivo en el navegador, sin backend propio.",
    "El endpoint «/silenciar» del ESP32 exige una clave compartida (deviceKey) "
    "y solo acepta peticiones desde la red local.",
    "No se almacenan credenciales de usuario ni se envían datos personales.",
])

# ===================== 14. FIRMWARE UNO =====================
h1("14. Firmware del Arduino Uno (adquisición y GPS)")
p("El Arduino Uno (sketch_oct17a) lee los sensores ambientales, calcula la "
  "posición GPS y envía una trama de 9 campos al ESP32 cada 3 segundos por "
  "puerto serie a 9600 baudios.")
h2("Sensores y pines")
tabla([
    ["Sensor", "Variable", "Conexión"],
    ["PMS5003 (partículas)", "PM2.5 (µg/m³)", "SoftwareSerial RX=2, TX=3 (hacia el ESP32)"],
    ["DHT/BME280 (clima)", "Temperatura, humedad, presión", "I²C (A4/A5)"],
    ["MH-Z19C", "CO₂ (ppm)", "SoftwareSerial RX=10, TX=11"],
    ["MQ-7", "Monóxido de carbono (CO)", "Analógico A0"],
    ["ML8511 (GY-8511)", "Radiación UV", "Analógico A2"],
    ["LDR", "Luz ambiental (lux aprox.)", "Analógico A1 · digital D12"],
    ["GPS NEO-6M (GY-GPS6MV2)", "Latitud y longitud", "SoftwareSerial RX=7, TX=8"],
], [150, 170, 185], negrita_primera=True)
h2("Funcionamiento")
bullets([
    "El GPS se deja como receptor activo por defecto (gpsSerial.listen()); se "
    "conmuta brevemente al puerto del sensor de CO₂ para leerlo y se vuelve al "
    "GPS.",
    "Se interpretan las sentencias $GPGGA y $GNGGA: se verifica la calidad del "
    "fix y se convierten latitud/longitud de formato NMEA (ggmm.mmmm) a grados "
    "decimales, aplicando el signo según N/S y E/W.",
    "El MQ-7 requiere un calentamiento inicial; el sistema espera 30 segundos "
    "antes de empezar.",
    "El ML8511 se convierte con la referencia real del ADC del Uno (5 V, no "
    "3,3 V), de modo que la irradiancia UV deja de recortarse a cero.",
    "Las lecturas del BME280 se protegen contra valores inválidos (NaN).",
    "Cada 3 segundos se envía al ESP32 una trama de 9 campos.",
])
h2("Conservación de la última coordenada válida")
p("Si el GPS pierde el fix momentáneamente, el firmware no envía (0,0): "
  "conserva la última posición válida y la reutiliza hasta recuperar la señal. "
  "Esto evita filas sin coordenadas originadas por cortes transitorios del "
  "GPS.")
story.append(PageBreak())

# ===================== 15. FIRMWARE ESP32 =====================
h1("15. Firmware del ESP32 (WiFi, Supabase y alarma)")
p("El ESP32 es el enlace con la nube y el controlador de la alarma. Recibe la "
  "trama del Arduino Uno, arma el registro y lo publica en Supabase; además, "
  "mide el ICA (con PM2.5 y CO) y gobierna el zumbador.")
h2("Conectividad")
bullets([
    "Conexión al Wi-Fi del lugar en modo estación (STA), con reconexión "
    "automática.",
    "Punto de acceso permanente Tucuman-Respira-Config (contraseña Tucuman2026, "
    "IP 192.168.4.1) con portal DNS cautivo, para configurar la red sin "
    "flashear.",
    "Las credenciales se guardan en memoria no volátil (NVS) con Preferences.",
])
h2("Publicación en Supabase")
bullets([
    "Petición HTTPS POST a la API REST de Supabase con encabezados apikey y "
    "Authorization (clave anon).",
    "Campos enviados: co2, co, pm25, temperatura, humedad, presion, uv, luz, "
    "latitud, longitud e ip_dispositivo (IP local del ESP32, para el "
    "descubrimiento automático desde la app).",
    "Se eliminó el envío de un campo inexistente («aqi») que provocaba un "
    "error HTTP 400.",
    "El sensor de partículas (PMS5003) se lee por Serial2 (RX 18 / TX 5, "
    "SET 4).",
])
h2("Alarma sonora")
bullets([
    "Zumbador pasivo en GPIO 23, controlado con tone()/noTone().",
    "El ICA se calcula localmente con los mismos breakpoints que la web "
    "(PM2.5 EPA 2024 y CO con umbral NIOSH REL / OSHA PEL).",
    "Se activa el sonido al superar ICA > 100 y se corta al bajar de 80; el "
    "silencio manual dura 10 minutos.",
])
h2("Endpoints HTTP")
tabla([
    ["Ruta", "Función"],
    ["/silenciar?k=CLAVE", "Silencia el zumbador (10 minutos)."],
    ["/status", "Estado de la estación: AQI actual, alerta y silencio."],
    ["/alarma", "Estado de la alarma y del zumbador."],
    ["/save (POST)", "Guarda credenciales Wi-Fi y confirma el estado."],
    ["/", "Punto de acceso de configuración (portal cautivo)."],
], [150, 355], negrita_primera=True)
p("Todos los endpoints responden con CORS abierto (Access-Control-Allow-"
  "Origin: *) para permitir el control desde la web.")
story.append(PageBreak())

# ===================== 16. INTEGRACIÓN =====================
h1("16. Integración del sistema y control del zumbador")
p("El flujo completo del sistema es:")
bullets([
    "El Arduino Uno adquiere los sensores y el GPS y envía la trama de 9 "
    "campos al ESP32 cada 3 segundos.",
    "El ESP32 recibe la trama, calcula el ICA local y publica el registro en "
    "Supabase (incluida su IP local).",
    "La app web lee Supabase, muestra los datos, marca el nivel de cada "
    "métrica y el estado general.",
    "Si el ICA supera 100, el ESP32 activa el zumbador; la app ofrece el botón "
    "«Detener zumbador».",
    "El botón llama al endpoint /silenciar del ESP32 (con la clave del "
    "dispositivo) y silencia la alarma 10 minutos.",
])
h2("Requisitos de red")
bullets([
    "El ESP32 y el dispositivo que usa la app deben estar en la misma red "
    "local para el control del zumbador.",
    "Si la estación está únicamente en modo punto de acceso, la IP de la app "
    "es 192.168.4.1 (valor por defecto).",
])
p("Nota: la app se sirve por HTTP (por ejemplo con Live Server), por lo que "
  "la llamada al ESP32 por HTTP no presenta problemas de contenido mixto.")

# ===================== 17. ERRORES =====================
h1("17. Correcciones de errores durante el desarrollo")
tabla([
    ["Problema detectado", "Causa", "Solución aplicada"],
    ["Los modales no se cerraban y aparecían encimados.",
     "Reglas CSS .modal con display:grid/flex pisaban el atributo «hidden».",
     "Se agregó [hidden]{display:none !important}."],
    ["El gráfico del histórico se veía colapsado en móvil.",
     "Se creaba con el modal oculto (sin tamaño).",
     "Se reordenó: abrir modal → crear gráfico → redimensionar."],
    ["El botón de GitHub aparecía vacío.",
     "Las versiones nuevas de Lucide ya no incluyen íconos de marcas "
     "(«github»).",
     "Se incorporó el logotipo de GitHub como SVG propio en el botón."],
    ["El aviso «offline» desbordaba el borde en el celular.",
     "Caja fuera del contenedor y sin márgenes.",
     "Se envolvió el aviso en un .container, compartiendo el ancho del resto."],
    ["El logo del encabezado enlazaba a la raíz del sitio.",
     "Era un enlace href a «./»; al abrir la app como archivo, el navegador "
     "mostraba el listado de la carpeta (exponía el directorio).",
     "Se convirtió el logo en un botón que recarga la página "
     "(location.reload())."],
    ["Los paneles de Tendencia/GPS se salían de la tarjeta en móviles "
     "angostos.",
     "El lienzo de Chart.js tiene ancho intrínseco de 300 px.",
     "Grillas con minmax(0, …) y min-width:0 en .panel y .chart-wrap."],
    ["Umbrales sin respaldo normativo y con etiquetas inexactas.",
     "Rangos elegidos a criterio propio.",
     "Se recalibraron con fuentes (OSHA/NIOSH, EPA, OMS/ICNIRP, NWS, ASHRAE) y "
     "se corrigieron los textos."],
    ["El mapa mostraba «API key required» sobre fondo negro.",
     "Los mosaicos de Carto requieren clave.",
     "Se cambió a mosaicos de OpenStreetMap (sin clave)."],
    ["La descarga JSON salía «entrecortada».",
     "Pretty-print con muchos registros y MIME sin charset.",
     "JSON sin indentación y MIME application/json;charset=utf-8."],
    ["El modal de descarga se desbordaba en Chrome Android al abrir los "
     "desplegables.",
     "Grillas 1fr que no podían encogerse por el ancho intrínseco del "
     "desplegable.",
     "minmax(0,1fr), min-width:0, overflow-x:hidden y ancho del modal "
     "limitado al viewport."],
    ["El texto «JSON (datos crudos)» se cortaba en PC.",
     "Modal demasiado angosto (420 px).",
     "Se ensanchó el modal de descarga a 560 px."],
    ["La app enviaba datos a Supabase y recibía HTTP 400.",
     "Se enviaba un campo «aqi» inexistente.",
     "Se eliminó el campo del payload."],
    ["Las lecturas quedaban desalineadas (valores cruzados).",
     "El Uno enviaba 8 campos y el ESP32 interpretaba 7.",
     "Se unificó la trama en 9 campos y el parser correspondiente."],
    ["Llegaban coordenadas (0,0) a la base.",
     "El GPS enviaba 0,0 al perder el fix.",
     "El Uno conserva y reenvía la última coordenada válida."],
    ["El sketch del Arduino Uno quedó sobrescrito con el de la ESP32.",
     "Reemplazo accidental del archivo.",
     "Se restauró el firmware del Uno y se separaron ambos en carpetas "
     "propias."],
], [150, 165, 190], negrita_primera=True)
story.append(PageBreak())

# ===================== 18. VERIFICACIONES =====================
h1("18. Verificaciones y pruebas realizadas")
tabla([
    ["Verificación", "Resultado"],
    ["Sintaxis del JavaScript (análisis con esprima).", "Correcta (sin errores de análisis)."],
    ["Coincidencia de los identificadores usados por app.js con el HTML.", "Todos presentes."],
    ["Respuesta de la API REST de Supabase.", "HTTP 200; columnas con los nombres esperados."],
    ["Escritura real a Supabase (POST desde el flujo).", "HTTP 201 (registro creado correctamente)."],
    ["Compilación del firmware del Arduino Uno (avr-g++).", "Sin errores."],
    ["Compilación del firmware del ESP32 (xtensa-esp32-elf-g++).", "Sin errores."],
    ["Parser NMEA del GPS (prueba automatizada).", "Correcto (sentencias N/S/E/W y sin fix)."],
    ["Renderizado del panel (navegador headless).", "Sin errores de JavaScript; mapa y tarjetas correctos."],
    ["Columna «ip_dispositivo» en Supabase.", "Operativa; el ESP32 publica su IP en cada envío."],
    ["Umbral de CO y disparo de la alarma local (revisión de firmware).",
     "El CO solo marca «dañino» y dispara la alarma desde 35 ppm (NIOSH REL)."],
], [300, 205], negrita_primera=True)
p("Prueba pendiente en campo: validar la alarma sonora y el corte del "
  "zumbador durante una presentación real con la estación conectada a la red "
  "del lugar.")

# ===================== 19. EJECUCIÓN =====================
h1("19. Cómo ejecutar y visualizar el sistema")
h2("Aplicación web con Live Server (Visual Studio Code)")
bullets([
    "Abrir la carpeta de la app web en Visual Studio Code.",
    "Instalar la extensión «Live Server» y pulsar «Go Live».",
    "Se abrirá el panel en http://127.0.0.1:5500/.",
    "Desde un celular de la misma red: http://<IP-de-la-PC>:5500/ (la IP se "
    "obtiene con hostname -I).",
])
h2("Opción alternativa — servidor local con Python")
code("python3 -m http.server 8000 --bind 0.0.0.0")
bullets([
    "En la misma PC: http://127.0.0.1:8000/",
    "En un celular de la misma red Wi-Fi: http://<IP-de-la-PC>:8000/",
    "Requiere conexión a internet (librerías por CDN y consulta a Supabase).",
    "Para el control del zumbador, estar en la misma red local que el ESP32.",
    "Detener el servidor con Ctrl + C.",
])

# ===================== 20. PENDIENTES =====================
h1("20. Pendientes y recomendaciones")
tabla([
    ["Tema", "Recomendación"],
    ["Publicación online", "Hostear los 3 archivos (GitHub Pages, Netlify, "
     "Vercel o Cloudflare Pages) para que el público acceda."],
    ["Clave de Supabase", "Mantener solo la clave pública (anon) de lectura en "
     "el cliente."],
    ["Umbral de CO", "Re-flashear el ESP32 para que el nuevo umbral (35 ppm) "
     "quede activo en la estación."],
    ["Calibración del MQ-7", "Verificar la calibración del sensor de CO en "
     "aire limpio para evitar lecturas altas constantes."],
    ["Alarma en campo", "Validar en campo el disparo y el corte del zumbador."],
    ["Escalado del ICA del CO", "Revisar los tramos superiores del CO (>50 "
     "ppm) frente a nuevas fuentes si se necesita más detalle."],
], [120, 385], negrita_primera=True)
story.append(PageBreak())

# ===================== ANEXOS =====================
h1("Anexo A — Configuración y claves")
p("La configuración se centraliza al inicio de app.js en el bloque CONFIG:")
code("""const CONFIG = {
  supabaseUrl: "https://lskvyvpjjziuclaatrtu.supabase.co",
  supabaseKey: "sb_publishable_O9Havbh6tsAZEDA8VFWQzg_LmTmU4mM",
  table: "mediciones",
  historyLimit: 100,
  pollMs: 15000,
  staleWarnSeconds: 120,
  staleOfflineSeconds: 300,
  defaultLat: -26.82414,
  defaultLng: -65.2226,
  downloadRanges: { "100": 100, "500": 500, "1000": 1000, all: Infinity },
  deviceKey: "tucu2026",
  deviceIpDefault: "192.168.4.1",
  muteMinutes: 10
};""")
p("Nota de seguridad: «supabaseKey» es una clave pública (anon) pensada para "
  "usarse en el cliente; no debe reemplazarse por la clave de servicio. La "
  "protección de los datos depende de las políticas RLS del servidor. La "
  "clave «deviceKey» es la que exige el ESP32 en el endpoint «/silenciar».")

h1("Anexo B — Exportación de datos (CSV / JSON)")
h2("CSV")
p("El archivo incluye una marca de orden de bytes (BOM) UTF-8 y separador "
  "punto y coma (;). Columnas:")
code("id;fecha_hora;pm25_ug_m3;co2_ppm;co_ppm;temperatura_c;humedad_pct;\n"
     "presion_hpa;uv;luz_lux;latitud;longitud")
h2("JSON")
p("El archivo JSON contiene el arreglo de registros tal como los devuelve la "
  "API, con todos los campos de cada medición (incluidos latitud, longitud e "
  "ip_dispositivo). Se genera sin indentación y con codificación UTF-8 para "
  "evitar cortes en archivos grandes.")
story.append(PageBreak())

# ===================== ANEXO C =====================
h1("Anexo C — Trama de comunicación Uno → ESP32")
p("Comunicación serie a 9600 baudios, una línea de texto por medición, con 9 "
  "campos separados por comas:")
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
], [70, 250, 185], negrita_primera=True)
p("El ESP32 procesa la trama con una lectura de formato tipo "
  "sscanf(\"%d,%f,%f,%f,%f,%f,%d,%f,%f\") y descarta las tramas inválidas.")

# ===================== ANEXO D =====================
h1("Anexo D — Prompt para recrear el proyecto con opencode")
p("A continuación se incluye un prompt ampliado para recrear el sistema "
  "completo (panel web y firmwares) con sus umbrales actualizados.")
code(
    'Recrea el proyecto "Tucuman Respira": panel web estatico (index.html +\n'
    'styles.css + app.js) que lee Supabase y dos firmwares (Arduino Uno +\n'
    'ESP32) que cargan las mediciones.\n\n'
    'DATOS (Supabase, solo lectura):\n'
    '- URL: https://lskvyvpjjziuclaatrtu.supabase.co\n'
    '- Clave publica (anon): sb_publishable_O9Havbh6tsAZEDA8VFWQzg_LmTmU4mM\n'
    '- Tabla: mediciones (id, created_at, co2, co, pm25, temperatura,\n'
    '  humedad, presion, uv, luz, latitud, longitud, ip_dispositivo)\n'
    '- GET {URL}/rest/v1/mediciones?select=*&order=id.desc&limit=100\n\n'
    'METRICAS Y UMBRALES (mostrar la fuente):\n'
    '- CO2 [ppm] OSHA/NIOSH + ASHRAE: Bueno<=800, Aceptable<=1000,\n'
    '  Ventilacion pobre<=1500, Alta (PEL 8h)<=5000, Muy alta (STEL)<=30000.\n'
    '- CO [ppm] NIOSH REL (35 ppm)/OSHA PEL (50 ppm): Bueno<=4.4,\n'
    '  Moderado<=34.9, Danino<=50, Muy danino<=100, Peligroso<=200.\n'
    '- PM2.5 [ug/m3] EPA AQI 2024: Bueno<=9, Moderado<=35.4,\n'
    '  Danino grupos sensibles<=55.4, Danino<=125.4, Muy danino<=225.4.\n'
    '- Temperatura [C], Humedad [%], Presion [hPa], UV [mW/cm2] y Luz [lux]\n'
    '  con sus umbrales de salud habituales.\n\n'
    'ICA: subindice de PM2.5 y CO por interpolacion lineal; tomar el PEOR.\n'
    '- pm25: [0,9.0]->[0,50] [9.1,35.4]->[51,100] [35.5,55.4]->[101,150]\n'
    '  [55.5,125.4]->[151,200] [125.5,225.4]->[201,300]\n'
    '- co: [0,4.4]->[0,50] [4.5,34.9]->[51,100] [35,50]->[101,150]\n'
    '  [50.1,100]->[151,200] [100.1,200]->[201,300] [200.1,500]->[301,500]\n'
    '- Categorias: 0-50 Buena; 51-100 Moderada; 101-150 Danina para grupos\n'
    '  sensibles; 151-200 Danina; 201-300 Muy danina; 301-500 Peligrosa.\n\n'
    'FIRMWARE ESP32: WiFi STA + AP "Tucuman-Respira-Config" (clave\n'
    'Tucuman2026, IP 192.168.4.1), POST a Supabase, zumbador GPIO 23 (tone/\n'
    'noTone) que suena si ICA>100 y se corta si <80, y endpoints /silenciar,\n'
    '/status, /alarma, /save.\n\n'
    'Control del zumbador: la web obtiene la IP desde ip_dispositivo\n'
    '(fallback 192.168.4.1) y llama a http://<ip>/silenciar?k=tucu2026.\n'
    'Entrega los archivos completos y funcionales, sin backend propio.')

p("Fin del informe — «Tucumán Respira», sistema de monitoreo de calidad del "
  "aire IoT (panel web, umbrales y firmwares). Encargado del trabajo: Benicio "
  "Gael Pieroni. Documento generado el 18/10/2026.")
story.append(Spacer(1, 24))
story.append(Paragraph(
    "Tucumán Respira — Encargado: Benicio Gael Pieroni", S["small"]))


def main():
    doc = BaseDocTemplate(
        SALIDA, pagesize=A4,
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=16 * mm, bottomMargin=18 * mm,
        title="Informe técnico unificado — Tucumán Respira",
        author="Benicio Gael Pieroni",
        subject="Panel web, umbrales y firmwares — Estación de monitoreo IoT",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
                  id="cuerpo")
    doc.addPageTemplates([PageTemplate(id="todas", frames=[frame],
                                       onPage=pie)])
    doc.build(story)
    print("Generado:", SALIDA)


if __name__ == "__main__":
    main()
