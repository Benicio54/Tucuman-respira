#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Actualiza el snapshot de datos y los gráficos del informe.

Consulta Supabase, separa filas históricas y valores fuera de rango, calcula
estadísticas descriptivas y escribe datos_resumen.json + dos gráficos en
figuras/. Los generadores de informes leen ese JSON para mantener las cifras
y los gráficos sincronizados.
"""
from __future__ import annotations

import json
import statistics
from datetime import datetime, timedelta, timezone
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import requests
from matplotlib.ticker import FuncFormatter

BASE = Path(__file__).resolve().parent
FIG = BASE / "figuras"
SALIDA = BASE / "datos_resumen.json"

SUPABASE_URL = "https://lskvyvpjjziuclaatrtu.supabase.co/rest/v1/mediciones"
SUPABASE_KEY = "sb_publishable_O9Havbh6tsAZEDA8VFWQzg_LmTmU4mM"
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
}

CAMPOS = (
    "id,created_at,co2,co,pm25,temperatura,humedad,presion,uv,luz,"
    "latitud,longitud,ip_dispositivo"
)
VARIABLES = [
    ("co2", "CO₂", "ppm"),
    ("co", "CO", "ppm"),
    ("pm25", "PM2.5", "µg/m³"),
    ("temperatura", "Temperatura", "°C"),
    ("humedad", "Humedad", "%"),
    ("presion", "Presión", "hPa"),
    ("uv", "UV", "mW/cm²"),
    ("luz", "Luz", "lux"),
]
MESES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def fetch_rows() -> list[dict]:
    session = requests.Session()
    filas: list[dict] = []
    offset = 0
    while True:
        r = session.get(
            SUPABASE_URL,
            headers=HEADERS,
            params={
                "select": CAMPOS,
                "order": "id.asc",
                "limit": 1000,
                "offset": offset,
            },
            timeout=40,
        )
        r.raise_for_status()
        lote = r.json()
        filas.extend(lote)
        if len(lote) < 1000:
            break
        offset += 1000
    if not filas:
        raise RuntimeError("Supabase devolvió una lista vacía.")
    return filas


def num(valor) -> float | None:
    try:
        return float(valor)
    except (TypeError, ValueError):
        return None


def es_historica(fila: dict) -> bool:
    return num(fila.get("co2")) == 400 and num(fila.get("temperatura")) == 0


def es_valida(fila: dict) -> bool:
    if es_historica(fila):
        return False
    v = {k: num(fila.get(k)) for k, _, _ in VARIABLES}
    if any(x is None for x in v.values()):
        return False
    return (
        0 <= v["co2"] <= 10000
        and 0 <= v["co"] <= 2000
        and 0 <= v["pm25"] <= 1000
        and -10 <= v["temperatura"] <= 60
        and 0 <= v["humedad"] <= 100
        and 900 <= v["presion"] <= 1100
        and 0 <= v["uv"] <= 20
        and 0 <= v["luz"] <= 200000
    )


def percentil(ordenados: list[float], p: float) -> float:
    if not ordenados:
        return 0.0
    return ordenados[min(len(ordenados) - 1, int(p * (len(ordenados) - 1)))]


def pct(n: int, d: int) -> float:
    return round(n / d * 100, 1) if d else 0.0


def resumen_stats(validas: list[dict]) -> dict:
    out = {}
    for clave, _, _ in VARIABLES:
        valores = sorted(v[clave] for v in validas)
        out[clave] = {
            "min": round(valores[0], 2),
            "median": round(statistics.median(valores), 2),
            "p75": round(percentil(valores, 0.75), 2),
            "max": round(valores[-1], 2),
        }
    return out


def resumen_diario(validas: list[dict]) -> list[dict]:
    dias: dict[str, dict[str, list[float]]] = {}
    for fila in validas:
        fecha = str(fila["created_at"])[:10]
        dias.setdefault(fecha, {k: [] for k, _, _ in VARIABLES})
        for clave, _, _ in VARIABLES:
            dias[fecha][clave].append(float(fila[clave]))
    salida = []
    for fecha in sorted(dias):
        d = dias[fecha]
        salida.append({
            "date": fecha,
            "count": len(d["pm25"]),
            "pm25": round(statistics.median(d["pm25"]), 1),
            "co": round(statistics.median(d["co"]), 2),
            "co2": round(statistics.median(d["co2"]), 0),
        })
    return salida


def max_diario(diario: list[dict], clave: str) -> dict:
    item = max(diario, key=lambda d: d[clave])
    return {"date": item["date"], "value": item[clave]}


def graficar(diario: list[dict], exceed: dict) -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 8.5,
        "axes.edgecolor": "#cbd5e1",
        "axes.labelcolor": "#0f172a",
        "xtick.color": "#475569",
        "ytick.color": "#475569",
        "axes.titlecolor": "#0f172a",
    })
    fechas = [datetime.strptime(d["date"], "%Y-%m-%d") for d in diario]
    pm = [d["pm25"] for d in diario]
    co = [d["co"] for d in diario]

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(6.5, 3.1), sharex=True,
        gridspec_kw={"hspace": 0.18},
    )
    ax1.plot(fechas, pm, color="#059669", marker="o", linewidth=1.6,
             markersize=4.5, label="PM2.5")
    ax1.axhline(35, color="#dc2626", linestyle="--", linewidth=1.0)
    ax1.set_ylabel("PM2.5 (µg/m³)")
    ax1.set_title("Mediana diaria de PM2.5 y CO — días con registro", loc="left")
    ax1.grid(axis="y", color="#e2e8f0", linewidth=0.8)
    ax1.set_ylim(0, max(pm + [40]) * 1.22)
    ax2.plot(fechas, co, color="#d97706", marker="o", linewidth=1.6,
             markersize=4.5, label="CO")
    ax2.axhline(35, color="#dc2626", linestyle="--", linewidth=1.0)
    ax2.set_ylabel("CO (ppm)")
    ax2.set_xlabel("Fecha (2026)")
    ax2.grid(axis="y", color="#e2e8f0", linewidth=0.8)
    ax2.set_ylim(0, max(co + [40]) * 1.22)
    ax2.xaxis.set_major_locator(mdates.DayLocator(interval=2))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    for ax in (ax1, ax2):
        ax.spines[["top", "right"]].set_visible(False)
    fig.savefig(FIG / "datos_pm25_co.png", dpi=200, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)

    etiquetas = ["PM2.5 > 35\nµg/m³", "CO > 35\nppm", "CO₂ > 1000\nppm"]
    valores = [exceed["pm25"]["pct"], exceed["co"]["pct"], exceed["co2"]["pct"]]
    colores = ["#059669", "#d97706", "#2563eb"]
    fig, ax = plt.subplots(figsize=(6.5, 2.7))
    barras = ax.bar(etiquetas, valores, color=colores, width=0.55)
    ax.set_ylabel("Lecturas válidas (%)")
    ax.set_title("Excedencias sobre el total de lecturas válidas", loc="left")
    ax.set_ylim(0, max(valores + [1]) * 1.3)
    ax.grid(axis="y", color="#e2e8f0", linewidth=0.8)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda y, _: f"{y:.0f}%"))
    ax.spines[["top", "right"]].set_visible(False)
    for barra, valor in zip(barras, valores):
        ax.text(barra.get_x() + barra.get_width() / 2, valor + 0.4,
                f"{valor:.1f}%".replace(".", ","), ha="center",
                va="bottom", fontsize=9, color="#0f172a")
    fig.savefig(FIG / "datos_excedencias.png", dpi=200, bbox_inches="tight",
                facecolor="white")
    plt.close(fig)


def main() -> None:
    filas = fetch_rows()
    validas = [f for f in filas if es_valida(f)]
    historicas = [f for f in filas if es_historica(f)]
    invalidas = [f for f in filas if not es_historica(f) and not es_valida(f)]
    if not validas:
        raise RuntimeError("No hay filas válidas para analizar.")

    stats = resumen_stats(validas)
    diario = resumen_diario(validas)
    exceed = {
        "pm25": {
            "count": sum(1 for f in validas if float(f["pm25"]) > 35),
            "pct": pct(sum(1 for f in validas if float(f["pm25"]) > 35),
                       len(validas)),
        },
        "co": {
            "count": sum(1 for f in validas if float(f["co"]) > 35),
            "pct": pct(sum(1 for f in validas if float(f["co"]) > 35),
                       len(validas)),
        },
        "co2": {
            "count": sum(1 for f in validas if float(f["co2"]) > 1000),
            "pct": pct(sum(1 for f in validas if float(f["co2"]) > 1000),
                       len(validas)),
        },
    }
    ahora_utc = datetime.now(timezone.utc)
    ahora_local = ahora_utc.astimezone(timezone(timedelta(hours=-3)))
    ultima = filas[-1]
    ultima_valida = validas[-1]

    datos = {
        "generated_at_utc": ahora_utc.isoformat(),
        "generated_at_local": ahora_local.isoformat(),
        "fecha_corta": ahora_local.strftime("%d/%m/%Y"),
        "fecha_larga": (
            f"{ahora_local.day} de {MESES[ahora_local.month - 1]} de "
            f"{ahora_local.year}"
        ),
        "total": len(filas),
        "valid": len(validas),
        "legacy": len(historicas),
        "invalid": len(invalidas),
        "coords": sum(
            1 for f in filas
            if f.get("latitud") is not None and f.get("longitud") is not None
        ),
        "ip": sum(1 for f in filas if f.get("ip_dispositivo")),
        "first_created_at": filas[0]["created_at"],
        "last_created_at": ultima["created_at"],
        "last_raw": ultima,
        "last_valid": ultima_valida,
        "stats": stats,
        "exceed": exceed,
        "daily": diario,
        "max_daily": {
            "pm25": max_diario(diario, "pm25"),
            "co": max_diario(diario, "co"),
            "co2": max_diario(diario, "co2"),
        },
        "pct": {
            "valid": pct(len(validas), len(filas)),
            "legacy": pct(len(historicas), len(filas)),
            "invalid": pct(len(invalidas), len(filas)),
            "coords": pct(
                sum(1 for f in filas
                    if f.get("latitud") is not None
                    and f.get("longitud") is not None),
                len(filas),
            ),
            "ip": pct(sum(1 for f in filas if f.get("ip_dispositivo")),
                      len(filas)),
        },
    }
    SALIDA.write_text(json.dumps(datos, ensure_ascii=False, indent=2),
                      encoding="utf-8")
    graficar(diario, exceed)

    print(f"Snapshot: {SALIDA}")
    print(f"Total: {datos['total']} | válidas: {datos['valid']} | "
          f"históricas: {datos['legacy']} | inválidas: {datos['invalid']}")
    print(f"PM2.5 > 35: {exceed['pm25']['count']} "
          f"({exceed['pm25']['pct']}%)")
    print(f"CO > 35: {exceed['co']['count']} ({exceed['co']['pct']}%)")
    print(f"CO₂ > 1000: {exceed['co2']['count']} "
          f"({exceed['co2']['pct']}%)")
    print("Gráficos: figuras/datos_pm25_co.png, "
          "figuras/datos_excedencias.png")


if __name__ == "__main__":
    main()
