"use strict";

/* ============================================================
   CONFIGURACIÓN
   La clave usada es la clave pública (anon) del proyecto. En una
   aplicación estática siempre es visible en el cliente; la
   protección real depende de las políticas (RLS) del servidor.
   ============================================================ */
const CONFIG = {
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
};

const COLOR = {
  emerald: "#10b981",
  sky: "#38bdf8",
  amber: "#f59e0b",
  orange: "#fb923c",
  rose: "#f43f5e",
  fuchsia: "#d946ef",
  slate: "#94a3b8"
};

/* Umbrales de referencia. Fuente indicada por métrica y mostrada en la interfaz. */
const METRICS = [
  {
    id: "co2", field: "co2", title: "Dióxido de Carbono (CO₂)", short: "CO₂",
    unit: "ppm", icon: "cloud", decimals: 0, alert: true, meterMax: 2000,
    source: "OSHA/NIOSH (límites de exposición) · ASHRAE (referencia de ventilación)",
    ranges: [
      { max: 800, label: "Bueno", color: "emerald" },
      { max: 1000, label: "Aceptable", color: "sky" },
      { max: 1500, label: "Ventilación pobre", color: "amber" },
      { max: 5000, label: "Alta (PEL 8 h)", color: "orange" },
      { max: 30000, label: "Muy alta (STEL)", color: "rose" },
      { max: Infinity, label: "Peligro (IDLH)", color: "fuchsia" }
    ]
  },
  {
    id: "co", field: "co", title: "Monóxido de Carbono (CO)", short: "CO",
    unit: "ppm", icon: "flame", decimals: 2, alert: true, meterMax: 30,
    source: "EPA AQI (8 h) · OSHA",
    ranges: [
      { max: 4.4, label: "Bueno", color: "emerald" },
      { max: 9.4, label: "Moderado", color: "sky" },
      { max: 12.4, label: "Grupos sensibles", color: "amber" },
      { max: 15.4, label: "Dañino", color: "orange" },
      { max: 30.4, label: "Muy dañino", color: "rose" },
      { max: 50.4, label: "Peligroso", color: "fuchsia" },
      { max: Infinity, label: "Extremo", color: "fuchsia" }
    ]
  },
  {
    id: "pm25", field: "pm25", title: "Material Particulado (PM2.5)", short: "PM2.5",
    unit: "µg/m³", icon: "droplets", decimals: 0, alert: true, meterMax: 150,
    source: "EPA AQI 2024 (24 h)",
    ranges: [
      { max: 9.0, label: "Bueno", color: "emerald" },
      { max: 35.4, label: "Moderado", color: "sky" },
      { max: 55.4, label: "Dañino grupos sensibles", color: "amber" },
      { max: 125.4, label: "Dañino", color: "orange" },
      { max: 225.4, label: "Muy dañino", color: "rose" },
      { max: Infinity, label: "Peligroso", color: "fuchsia" }
    ]
  },
  {
    id: "temp", field: "temperatura", title: "Temperatura", short: "Temperatura",
    unit: "°C", icon: "thermometer", decimals: 1, alert: true, meterMax: 50,
    source: "NWS/OSHA (estrés por calor) · NIOSH (estrés por frío)",
    ranges: [
      { max: 0, label: "Hipotermia", color: "fuchsia" },
      { max: 10, label: "Frío", color: "sky" },
      { max: 27, label: "Confortable", color: "emerald" },
      { max: 32, label: "Precaución por calor", color: "amber" },
      { max: 39, label: "Extrema precaución", color: "orange" },
      { max: 52, label: "Peligro", color: "rose" },
      { max: Infinity, label: "Peligro extremo", color: "fuchsia" }
    ]
  },
  {
    id: "hum", field: "humedad", title: "Humedad Relativa", short: "Humedad",
    unit: "%", icon: "waves", decimals: 0, alert: true, meterMax: 100,
    source: "OMS (humedad y moho) · ASHRAE (recomendación 30–60%)",
    ranges: [
      { max: 20, label: "Muy seco", color: "amber" },
      { max: 30, label: "Seco", color: "sky" },
      { max: 60, label: "Ideal", color: "emerald" },
      { max: 70, label: "Algo húmedo", color: "sky" },
      { max: 85, label: "Riesgo de moho", color: "orange" },
      { max: Infinity, label: "Alto riesgo de moho", color: "rose" }
    ]
  },
  {
    id: "pres", field: "presion", title: "Presión Atmosférica", short: "Presión",
    unit: "hPa", icon: "gauge", decimals: 0, alert: false, meterMax: null,
    source: "Informativo",
    ranges: [
      { max: 1004.9, label: "Baja", color: "sky" },
      { max: 1020, label: "Normal", color: "emerald" },
      { max: Infinity, label: "Alta", color: "sky" }
    ]
  },
  {
    id: "uv", field: "uv", title: "Índice de Radiación UV", short: "UV",
    unit: "", icon: "sun", decimals: 1, alert: true, meterMax: 11,
    source: "OMS / ICNIRP",
    ranges: [
      { max: 2, label: "Bajo", color: "emerald" },
      { max: 5, label: "Moderado", color: "amber" },
      { max: 7, label: "Alto", color: "orange" },
      { max: 10, label: "Muy alto", color: "rose" },
      { max: Infinity, label: "Extremo", color: "fuchsia" }
    ]
  },
  {
    id: "lux", field: "luz", title: "Luz Ambiental", short: "Luz",
    unit: "lux", icon: "sun-medium", decimals: 0, alert: false, meterMax: 1000,
    source: "Informativo",
    ranges: [
      { max: 9.9, label: "Oscuridad", color: "slate" },
      { max: 99.9, label: "Penumbra", color: "sky" },
      { max: 499, label: "Interior", color: "emerald" },
      { max: Infinity, label: "Pleno sol", color: "amber" }
    ]
  }
];

const TREND_TABS = [
  { id: "air", label: "Aire", metrics: ["pm25", "co"], subtitle: "Material particulado (PM2.5) y monóxido de carbono (CO)" },
  { id: "climate", label: "Clima", metrics: ["temp", "hum"], subtitle: "Temperatura y humedad relativa" },
  { id: "gases", label: "Gases", metrics: ["co2", "co"], subtitle: "Dióxido de carbono (CO₂) y monóxido de carbono (CO)" },
  { id: "radiation", label: "Luz / UV", metrics: ["uv", "lux"], subtitle: "Índice UV y luz ambiental" }
];

const AQI_BREAKPOINTS = {
  pm25: [
    [0.0, 9.0, 0, 50], [9.1, 35.4, 51, 100], [35.5, 55.4, 101, 150],
    [55.5, 125.4, 151, 200], [125.5, 225.4, 201, 300], [225.5, 500.4, 301, 500]
  ],
  co: [
    [0.0, 4.4, 0, 50], [4.5, 9.4, 51, 100], [9.5, 12.4, 101, 150],
    [12.5, 15.4, 151, 200], [15.5, 30.4, 201, 300], [30.5, 40.4, 301, 400],
    [40.5, 50.4, 401, 500]
  ]
};

const AQI_CATEGORIES = [
  { max: 50, label: "Buena", color: "emerald", desc: "La calidad del aire es satisfactoria y el riesgo para la salud es bajo.", health: "Ideal para actividades al aire libre. Se recomienda ventilar los ambientes." },
  { max: 100, label: "Moderada", color: "sky", desc: "Calidad aceptable, aunque algunas personas muy sensibles podrían notar molestias leves.", health: "Apto para la mayoría. Personas con asma o afecciones pulmonares deberían vigilar síntomas." },
  { max: 150, label: "Dañina para grupos sensibles", color: "amber", desc: "Grupos sensibles pueden experimentar efectos en la salud.", health: "Niños, adultos mayores y personas con afecciones respiratorias: reducir el esfuerzo intenso al aire libre." },
  { max: 200, label: "Dañina", color: "orange", desc: "Todos pueden comenzar a sentir efectos en la salud.", health: "Limitar la actividad física prolongada al aire libre." },
  { max: 300, label: "Muy dañina", color: "rose", desc: "Riesgo para la salud de toda la población.", health: "Evitar actividades al aire libre. Cerrar ventanas." },
  { max: Infinity, label: "Peligrosa", color: "fuchsia", desc: "Condiciones de emergencia sanitaria.", health: "Permanecer en interiores y evitar la exposición al aire libre." }
];

const state = {
  rows: [],
  latest: null,
  trend: "air",
  modal: null,
  modalRange: 50,
  chart: null,
  sensorChart: null,
  map: null,
  marker: null,
  tile: null,
  client: null,
  lastId: null,
  offlineDismissedId: null
};

const $ = (sel) => document.querySelector(sel);
const byId = (id) => document.getElementById(id);

/* ============================================================
   UTILIDADES
   ============================================================ */
function pad(n) { return String(n).padStart(2, "0"); }

function formatDateTime(value) {
  const d = value instanceof Date ? value : new Date(value);
  if (isNaN(d.getTime())) return "--";
  return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}

function relativeTime(date) {
  const s = Math.max(0, Math.floor((Date.now() - date.getTime()) / 1000));
  if (s < 60) return `hace ${s} s`;
  const m = Math.floor(s / 60);
  if (m < 60) return `hace ${m} min`;
  const h = Math.floor(m / 60);
  if (h < 24) return `hace ${h} h`;
  const d = Math.floor(h / 24);
  return `hace ${d} d`;
}

function metricById(id) { return METRICS.find((m) => m.id === id); }

function findRange(metric, value) {
  if (value === null || value === undefined || value === "" || isNaN(Number(value))) {
    return null;
  }
  const v = Number(value);
  for (const r of metric.ranges) {
    if (v <= r.max) return r;
  }
  return metric.ranges[metric.ranges.length - 1];
}

function formatValue(metric, value) {
  if (value === null || value === undefined || value === "" || isNaN(Number(value))) return "--";
  return Number(value).toFixed(metric.decimals);
}

function classify(metric, value) {
  const range = findRange(metric, value);
  if (!range) return { label: "Sin datos", color: "slate" };
  return range;
}

function setLevel(el, color, base) {
  el.className = `${base} lvl-${color}`;
}

function esc(v) {
  const s = v === null || v === undefined ? "" : String(v);
  return /[;"\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

function url_query(path) {
  return `${CONFIG.supabaseUrl}/rest/v1/${CONFIG.table}${path}`;
}

async function supabaseGet(path) {
  const res = await fetch(url_query(path), {
    headers: { apikey: CONFIG.supabaseKey, Authorization: `Bearer ${CONFIG.supabaseKey}` }
  });
  if (!res.ok) throw new Error(`Supabase HTTP ${res.status}`);
  return res.json();
}

/* ============================================================
   ÍNDICE DE CALIDAD DEL AIRE (EPA)
   ============================================================ */
function subIndex(breakpoints, concentration) {
  const c = Number(concentration);
  if (isNaN(c)) return 0;
  for (const [cLow, cHigh, iLow, iHigh] of breakpoints) {
    if (c >= cLow && c <= cHigh) {
      return Math.round(((iHigh - iLow) / (cHigh - cLow)) * (c - cLow) + iLow);
    }
  }
  return c > breakpoints[breakpoints.length - 1][1] ? 500 : 0;
}

function computeAQI(row) {
  if (!row) return 0;
  const aqiPm = subIndex(AQI_BREAKPOINTS.pm25, row.pm25);
  const aqiCo = subIndex(AQI_BREAKPOINTS.co, row.co);
  return Math.max(aqiPm, aqiCo);
}

function aqiCategory(aqi) {
  for (const cat of AQI_CATEGORIES) {
    if (aqi <= cat.max) return cat;
  }
  return AQI_CATEGORIES[AQI_CATEGORIES.length - 1];
}

/* ============================================================
   CONSTRUCCIÓN DE TARJETAS
   ============================================================ */
function buildSkeletons() {
  const grid = byId("sensors-grid");
  grid.innerHTML = METRICS.map(() => `<div class="skeleton"></div>`).join("");
}

function buildCards() {
  const grid = byId("sensors-grid");
  grid.innerHTML = METRICS.map((m) => `
    <button type="button" class="sensor-card lvl-slate" data-metric="${m.id}" aria-label="Ver histórico de ${m.title}">
      <div class="sensor-top">
        <span class="sensor-name">${m.title}</span>
        <span class="sensor-icon"><i data-lucide="${m.icon}"></i></span>
      </div>
      <div class="sensor-value">
        <strong id="val-${m.id}">--</strong>
        ${m.unit ? `<span>${m.unit}</span>` : ""}
      </div>
      ${m.meterMax ? `<div class="sensor-meter"><i id="meter-${m.id}"></i></div>` : ""}
      <div class="sensor-foot">
        <span class="sensor-status" id="status-${m.id}">Sin datos</span>
        <span class="sensor-hint"><i data-lucide="clock"></i> histórico</span>
      </div>
    </button>
  `).join("");
  grid.querySelectorAll("[data-metric]").forEach((btn) => {
    btn.addEventListener("click", () => openSensorModal(btn.dataset.metric));
  });
  refreshIcons();
}

function renderCards() {
  const row = state.latest;
  METRICS.forEach((m) => {
    const valueEl = byId(`val-${m.id}`);
    const statusEl = byId(`status-${m.id}`);
    const meterEl = byId(`meter-${m.id}`);
    const card = document.querySelector(`.sensor-card[data-metric="${m.id}"]`);
    const raw = row ? row[m.field] : null;
    const cls = classify(m, raw);
    const severe = ["amber", "orange", "rose", "fuchsia"].includes(cls.color);
    const alertClass = m.alert && severe ? " is-alert" : "";

    valueEl.textContent = formatValue(m, raw);
    statusEl.textContent = cls.label;
    card.className = `sensor-card lvl-${cls.color}${alertClass}`;

    if (meterEl) {
      if (raw === null || raw === undefined || isNaN(Number(raw))) {
        meterEl.style.width = "0%";
      } else {
        const pct = Math.max(4, Math.min(100, (Number(raw) / m.meterMax) * 100));
        meterEl.style.width = `${pct}%`;
      }
    }
  });
}

/* ============================================================
   BANNER / RESUMEN
   ============================================================ */
function renderHero() {
  const row = state.latest;
  const banner = byId("air-banner");
  const alarm = byId("alarm-box");
  const aqi = computeAQI(row);
  const cat = aqiCategory(aqi);

  byId("aqi-number").textContent = row ? aqi : "--";
  byId("aqi-category").textContent = row ? cat.label : "Sin datos";
  byId("aqi-status").textContent = row ? `Calidad del aire: ${cat.label}` : "Sin datos disponibles";
  byId("air-description").textContent = row ? cat.desc : "No hay mediciones registradas por el momento.";
  byId("health-text").textContent = row ? cat.health : "Sin información suficiente para dar una recomendación.";
  setLevel(banner, row ? cat.color : "slate", "air-banner");

  const buzzer = !row ? "SIN DATOS" : aqi <= 100 ? "NORMAL" : aqi <= 150 ? "PRECAUCIÓN" : aqi <= 200 ? "ALERTA" : "ALERTA CRÍTICA";
  byId("alarm-text").textContent = buzzer;
  setLevel(alarm, row ? cat.color : "slate", "alarm-box");
}

function renderSummary() {
  const rows = state.rows;
  byId("summary-subtitle").textContent = rows.length
    ? `Últimas ${rows.length} lecturas`
    : "Sin lecturas";
  byId("kpi-total").textContent = rows.length;

  const nums = (field) => rows.map((r) => Number(r[field])).filter((v) => !isNaN(v));
  const temps = nums("temperatura");
  const pm25s = nums("pm25");
  const co2s = nums("co2");
  const hums = nums("humedad");

  byId("kpi-temp-min").textContent = temps.length ? `${Math.min(...temps).toFixed(1)}°C` : "--";
  byId("kpi-temp-max").textContent = temps.length ? `${Math.max(...temps).toFixed(1)}°C` : "--";
  byId("kpi-pm25-max").textContent = pm25s.length ? `${Math.max(...pm25s).toFixed(0)} µg/m³` : "--";
  byId("kpi-co2-avg").textContent = co2s.length ? `${Math.round(co2s.reduce((a, b) => a + b, 0) / co2s.length)} ppm` : "--";
  byId("kpi-hum-avg").textContent = hums.length ? `${Math.round(hums.reduce((a, b) => a + b, 0) / hums.length)} %` : "--";
}

/* ============================================================
   RELOJ / WATCHDOG
   ============================================================ */
function renderClock() {
  const badge = byId("connection-badge");
  const dot = byId("conn-dot");
  const text = byId("last-update");
  const alert = byId("offline-alert");
  const row = state.latest;

  const reading = byId("last-reading");
  if (!row || !row.created_at) {
    dot.className = "conn-dot is-loading";
    text.textContent = "Conectando…";
    badge.title = "Estado de la conexión";
    reading.textContent = "--";
    return;
  }

  const date = new Date(row.created_at);
  const seconds = Math.max(0, Math.floor((Date.now() - date.getTime()) / 1000));
  const absolute = formatDateTime(date);
  const relative = relativeTime(date);

  badge.title = `Última actualización: ${absolute} (${relative})`;
  reading.textContent = `${absolute} (${relative})`;

  if (seconds < CONFIG.staleWarnSeconds) {
    dot.className = "conn-dot ok";
    text.textContent = `En vivo · ${relative}`;
    alert.hidden = true;
  } else if (seconds < CONFIG.staleOfflineSeconds) {
    dot.className = "conn-dot warn";
    text.textContent = `Retraso · ${relative}`;
    alert.hidden = true;
  } else {
    dot.className = "conn-dot off";
    text.textContent = `Sin conexión · ${relative}`;
    byId("offline-text").textContent = `La estación no ha enviado lecturas desde ${absolute} (${relative}). Mostrando los últimos datos registrados.`;
    alert.hidden = state.offlineDismissedId === row.id;
  }
}

/* ============================================================
   MAPA GPS
   ============================================================ */
function initMap() {
  if (typeof L === "undefined") return;
  const dark = document.documentElement.dataset.theme === "dark";
  state.map = L.map("map", { zoomControl: true, attributionControl: false })
    .setView([CONFIG.defaultLat, CONFIG.defaultLng], 12);
  state.tile = makeTile(dark);
  state.tile.addTo(state.map);
}

function makeTile(dark) {
  const url = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png";
  return L.tileLayer(url, {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  });
}

function gpsValido(lat, lng) {
  return !isNaN(lat) && !isNaN(lng) && lat !== 0 && lng !== 0 &&
    lat >= -90 && lat <= 90 && lng >= -180 && lng <= 180;
}

function renderMap() {
  if (!state.map) return;
  let row = state.latest;
  let lat = row ? Number(row.latitud) : NaN;
  let lng = row ? Number(row.longitud) : NaN;
  let hasGps = gpsValido(lat, lng);

  if (!hasGps && Array.isArray(state.rows)) {
    for (let i = state.rows.length - 1; i >= 0; i--) {
      const r = state.rows[i];
      const l = Number(r.latitud);
      const g = Number(r.longitud);
      if (gpsValido(l, g)) {
        row = r;
        lat = l;
        lng = g;
        hasGps = true;
        break;
      }
    }
  }

  const badge = byId("gps-badge");
  const coords = byId("gps-coords");
  const note = byId("gps-note");
  const link = byId("gmaps-link");

  if (!hasGps) {
    badge.textContent = "Sin señal";
    badge.className = "badge badge-muted";
    coords.textContent = "GPS sin señal";
    note.textContent = "";
    link.hidden = true;
    if (state.marker) { state.map.removeLayer(state.marker); state.marker = null; }
    return;
  }

  badge.textContent = "Ubicación por GPS";
  badge.className = "badge badge-good";
  coords.textContent = `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
  note.textContent = row === state.latest
    ? "Coordenadas reportadas por la estación."
    : "Última ubicación conocida reportada por la estación.";
  link.href = `https://www.google.com/maps?q=${lat},${lng}`;
  link.hidden = false;

  const icon = L.divIcon({
    className: "",
    html: '<div style="width:18px;height:18px;border-radius:50%;background:#10b981;border:3px solid #fff;box-shadow:0 0 0 6px rgba(16,185,129,.25)"></div>',
    iconSize: [18, 18],
    iconAnchor: [9, 9]
  });

  if (state.marker) {
    state.marker.setLatLng([lat, lng]);
  } else {
    state.marker = L.marker([lat, lng], { icon }).addTo(state.map);
  }
  state.map.setView([lat, lng], state.map.getZoom() < 12 ? 13 : state.map.getZoom());
}

/* ============================================================
   GRÁFICO DE TENDENCIA
   ============================================================ */
function chartColors() {
  const dark = document.documentElement.dataset.theme === "dark";
  return {
    text: dark ? "#94a3b8" : "#526072",
    grid: dark ? "rgba(51,65,85,.35)" : "rgba(203,213,225,.6)"
  };
}

function buildTrendTabs() {
  const wrap = byId("trend-tabs");
  wrap.innerHTML = TREND_TABS.map((t) =>
    `<button type="button" data-trend="${t.id}" class="${t.id === state.trend ? "is-active" : ""}">${t.label}</button>`
  ).join("");
  wrap.querySelectorAll("[data-trend]").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.trend = btn.dataset.trend;
      wrap.querySelectorAll("[data-trend]").forEach((b) => b.classList.toggle("is-active", b === btn));
      buildTrendChart();
    });
  });
}

function initTrendChart() {
  if (typeof Chart === "undefined") return;
  const c = chartColors();
  state.chart = new Chart(byId("trend-chart").getContext("2d"), {
    type: "line",
    data: { labels: [], datasets: [] },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 400 },
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { labels: { color: c.text, usePointStyle: true, pointStyle: "circle", boxWidth: 8 } },
        tooltip: {
          backgroundColor: "rgba(15,23,42,.92)",
          titleColor: "#f8fafc",
          bodyColor: "#cbd5e1",
          borderColor: "#334155",
          borderWidth: 1,
          padding: 10,
          cornerRadius: 10
        }
      },
      scales: {
        x: { ticks: { color: c.text, maxTicksLimit: 8 }, grid: { color: c.grid } },
        y: { ticks: { color: c.text }, grid: { color: c.grid }, beginAtZero: false }
      }
    }
  });
}

function buildTrendChart() {
  if (!state.chart) return;
  const tab = TREND_TABS.find((t) => t.id === state.trend);
  byId("trend-subtitle").textContent = tab.subtitle;

  const rows = state.rows.slice(-CONFIG.historyLimit);
  const labels = rows.map((r) => formatDateTime(r.created_at).slice(-8));

  state.chart.data.labels = labels;
  state.chart.data.datasets = tab.metrics.map((id) => {
    const m = metricById(id);
    const color = COLOR[m.ranges[0].color];
    return {
      label: m.unit ? `${m.short} (${m.unit})` : m.short,
      data: rows.map((r) => {
        const v = Number(r[m.field]);
        return isNaN(v) ? null : v;
      }),
      borderColor: color,
      backgroundColor: color + "22",
      borderWidth: 2,
      fill: true,
      tension: 0.35,
      pointRadius: 0,
      spanGaps: true
    };
  });
  state.chart.update();
}

/* ============================================================
   MODAL DE HISTÓRICO POR SENSOR
   ============================================================ */
function openModal(el) { el.hidden = false; document.body.style.overflow = "hidden"; }
function closeModal(el) {
  el.hidden = true;
  if (!document.querySelector(".modal:not([hidden])")) document.body.style.overflow = "";
}

function buildModalRanges() {
  const wrap = byId("modal-range");
  wrap.innerHTML = [20, 50, 100].map((n) =>
    `<button type="button" data-range="${n}" class="${n === state.modalRange ? "is-active" : ""}">${n}</button>`
  ).join("");
  wrap.querySelectorAll("[data-range]").forEach((btn) => {
    btn.addEventListener("click", () => {
      state.modalRange = Number(btn.dataset.range);
      wrap.querySelectorAll("[data-range]").forEach((b) => b.classList.toggle("is-active", b === btn));
      buildSensorChart();
    });
  });
}

function openSensorModal(id) {
  state.modal = id;
  byId("modal-sensor").dataset.metric = id;
  openModal(byId("modal-sensor"));
  buildSensorChart();
  if (state.sensorChart) {
    requestAnimationFrame(() => state.sensorChart.resize());
  }
}

function buildSensorChart() {
  const m = metricById(state.modal);
  if (!m) return;

  const rows = state.rows.slice(-state.modalRange);
  byId("sensor-modal-title").textContent = m.title;
  byId("sensor-modal-subtitle").textContent = `Últimas ${state.modalRange} mediciones disponibles`;
  byId("sensor-source").textContent = `Criterio de referencia: ${m.source}`;

  const values = rows
    .map((r) => Number(r[m.field]))
    .filter((v) => !isNaN(v));

  const current = state.latest && !isNaN(Number(state.latest[m.field]))
    ? formatValue(m, state.latest[m.field]) + (m.unit ? " " + m.unit : "")
    : "--";

  byId("stats-current").textContent = current;
  byId("stats-min").textContent = values.length ? formatValue(m, Math.min(...values)) + (m.unit ? " " + m.unit : "") : "--";
  byId("stats-max").textContent = values.length ? formatValue(m, Math.max(...values)) + (m.unit ? " " + m.unit : "") : "--";
  byId("stats-avg").textContent = values.length
    ? formatValue(m, values.reduce((a, b) => a + b, 0) / values.length) + (m.unit ? " " + m.unit : "")
    : "--";

  if (typeof Chart === "undefined") return;
  const c = chartColors();
  const color = COLOR[m.ranges[0].color];
  const labels = rows.map((r) => formatDateTime(r.created_at).slice(-8));
  const data = rows.map((r) => {
    const v = Number(r[m.field]);
    return isNaN(v) ? null : v;
  });

  if (state.sensorChart) {
    state.sensorChart.data.labels = labels;
    state.sensorChart.data.datasets[0].data = data;
    state.sensorChart.data.datasets[0].borderColor = color;
    state.sensorChart.data.datasets[0].backgroundColor = color + "22";
    state.sensorChart.options.scales.x.ticks.color = c.text;
    state.sensorChart.options.scales.x.grid.color = c.grid;
    state.sensorChart.options.scales.y.ticks.color = c.text;
    state.sensorChart.options.scales.y.grid.color = c.grid;
    state.sensorChart.update();
    return;
  }

  state.sensorChart = new Chart(byId("sensor-chart").getContext("2d"), {
    type: "line",
    data: {
      labels,
      datasets: [{
        label: m.unit ? `${m.short} (${m.unit})` : m.short,
        data,
        borderColor: color,
        backgroundColor: color + "22",
        borderWidth: 2,
        fill: true,
        tension: 0.35,
        pointRadius: 2,
        pointBackgroundColor: color,
        spanGaps: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 300 },
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "rgba(15,23,42,.92)",
          titleColor: "#f8fafc",
          bodyColor: "#cbd5e1",
          borderColor: "#334155",
          borderWidth: 1,
          padding: 10,
          cornerRadius: 10
        }
      },
      scales: {
        x: { ticks: { color: c.text, maxTicksLimit: 8 }, grid: { color: c.grid } },
        y: { ticks: { color: c.text }, grid: { color: c.grid }, beginAtZero: false }
      }
    }
  });
}

/* ============================================================
   DESCARGA DE DATOS
   ============================================================ */
async function fetchRows(limit) {
  if (limit === Infinity) return fetchAllRows();
  return supabaseGet(`?select=*&order=id.desc&limit=${limit}`);
}

async function fetchAllRows() {
  const page = 1000;
  let from = 0;
  const all = [];
  while (true) {
    const res = await fetch(url_query("?select=*&order=id.desc"), {
      headers: {
        apikey: CONFIG.supabaseKey,
        Authorization: `Bearer ${CONFIG.supabaseKey}`,
        Range: `${from}-${from + page - 1}`
      }
    });
    if (!res.ok && res.status !== 206) throw new Error(`Supabase HTTP ${res.status}`);
    const batch = await res.json();
    all.push(...batch);
    if (batch.length < page) break;
    from += page;
  }
  return all;
}

function toCSV(rows) {
  const headers = ["id", "fecha_hora", "pm25_ug_m3", "co2_ppm", "co_ppm", "temperatura_c", "humedad_pct", "presion_hpa", "uv", "luz_lux", "latitud", "longitud"];
  const lines = rows.map((r) => [
    r.id, r.created_at, r.pm25, r.co2, r.co, r.temperatura, r.humedad, r.presion, r.uv, r.luz, r.latitud, r.longitud
  ].map(esc).join(";"));
  return "\uFEFF" + [headers.join(";"), ...lines].join("\r\n");
}

function download(filename, content, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

async function handleDownload() {
  const format = byId("dl-format").value;
  const btn = byId("dl-confirm");

  btn.disabled = true;

  try {
    const rows = await fetchRows(resolveDownloadLimit(byId("dl-range").value));
    if (!rows.length) return;

    const stamp = new Date().toISOString().slice(0, 10);
    if (format === "json") {
      download(`tucuman_respira_${stamp}.json`, JSON.stringify(rows), "application/json;charset=utf-8");
    } else {
      download(`tucuman_respira_${stamp}.csv`, toCSV(rows), "text/csv;charset=utf-8;");
    }
  } catch (err) {
    console.error(err);
  } finally {
    btn.disabled = false;
  }
}

function resolveDownloadLimit(rangeKey) {
  if (rangeKey !== "custom") return CONFIG.downloadRanges[rangeKey];

  const custom = parseInt(byId("dl-custom").value, 10);
  return Number.isFinite(custom) && custom > 0 ? custom : CONFIG.downloadRanges["100"];
}

/* ============================================================
   TEMA
   ============================================================ */
function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  byId("theme-icon").setAttribute("data-lucide", theme === "dark" ? "sun" : "moon");
  document.querySelector('meta[name="theme-color"]').setAttribute("content", theme === "dark" ? "#020617" : "#f3f6fb");
  refreshIcons();

  if (state.map) {
    if (state.tile) state.map.removeLayer(state.tile);
    state.tile = makeTile(theme === "dark");
    state.tile.addTo(state.map);
  }
  const c = chartColors();
  [state.chart, state.sensorChart].forEach((ch) => {
    if (!ch) return;
    ch.options.plugins.legend.labels && (ch.options.plugins.legend.labels.color = c.text);
    ch.options.scales.x.ticks.color = c.text;
    ch.options.scales.x.grid.color = c.grid;
    ch.options.scales.y.ticks.color = c.text;
    ch.options.scales.y.grid.color = c.grid;
    ch.update();
  });
}

function toggleTheme() {
  const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
  try { localStorage.setItem("tr_theme", next); } catch (e) {}
  applyTheme(next);
}

/* ============================================================
   ICONOS
   ============================================================ */
function refreshIcons() {
  if (window.lucide && typeof lucide.createIcons === "function") lucide.createIcons();
}

/* ============================================================
   CARGA DE DATOS
   ============================================================ */
function ingest(newRows) {
  if (!newRows || !newRows.length) return false;
  const map = new Map(state.rows.map((r) => [r.id, r]));
  newRows.forEach((r) => map.set(r.id, r));
  state.rows = Array.from(map.values()).sort((a, b) => a.id - b.id).slice(-500);
  const latest = state.rows[state.rows.length - 1] || null;
  const changed = latest && (!state.latest || latest.id !== state.latest.id);
  state.latest = latest;
  state.lastId = latest ? latest.id : null;
  return changed;
}

function renderAll() {
  renderCards();
  renderHero();
  renderSummary();
  renderClock();
  renderMap();
  buildTrendChart();
  if (state.modal && !byId("modal-sensor").hidden) buildSensorChart();
}

async function loadInitial() {
  try {
    const data = await supabaseGet(`?select=*&order=id.desc&limit=${CONFIG.historyLimit}`);
    data.reverse();
    ingest(data);
    renderAll();
    if (!data.length) {
      byId("summary-subtitle").textContent = "Sin lecturas registradas";
    }
  } catch (err) {
    byId("aqi-status").textContent = "No se pudo conectar";
    byId("air-description").textContent = "Verifica la conexión a internet e inténtalo nuevamente.";
    byId("last-update").textContent = "Sin conexión";
    byId("conn-dot").className = "conn-dot off";
  }
}

function initRealtime() {
  if (!window.supabase || typeof window.supabase.createClient !== "function") return;
  try {
    state.client = window.supabase.createClient(CONFIG.supabaseUrl, CONFIG.supabaseKey);
    state.client
      .channel("mediciones-stream")
      .on("postgres_changes", { event: "INSERT", schema: "public", table: CONFIG.table }, (payload) => {
        if (payload && payload.new && ingest([payload.new])) renderAll();
      })
      .subscribe();
  } catch (err) {
    state.client = null;
  }
}

async function poll() {
  try {
    const data = await supabaseGet("?select=*&order=id.desc&limit=1");
    if (data && data.length && data[0].id !== state.lastId) {
      if (ingest(data)) renderAll();
    }
  } catch (err) {
    /* silencioso: el watchdog visual refleja el estado */
  }
}

/* ============================================================
   ALARMA DEL DISPOSITIVO
   ============================================================ */
function ipDispositivo() {
  const row = state.latest || {};
  const ip = normalizarIp(row.ip_dispositivo);
  return ip || CONFIG.deviceIpDefault;
}

function normalizarIp(valor) {
  return String(valor || "")
    .trim()
    .replace(/^https?:\/\//i, "")
    .replace(/\/+$/, "");
}

async function silenciarAlarma() {
  const btn = byId("btn-silenciar");
  const status = byId("silencio-status");
  const ip = ipDispositivo();

  if (!ip) {
    status.textContent = "Todavía no se conoce la IP de la estación.";
    return;
  }

  btn.disabled = true;
  status.textContent = "Enviando…";

  try {
    const url = `http://${ip}/silenciar?k=${encodeURIComponent(CONFIG.deviceKey)}`;
    const res = await fetch(url, { cache: "no-store" });
    const data = await res.json();

    if (!res.ok || !data.ok) {
      status.textContent = data.error ? `Error: ${data.error}` : "La estación rechazó la orden.";
      return;
    }

    status.textContent = `Alarma silenciada ${data.silenciado_minutos} minutos.`;
  } catch (err) {
    status.textContent = "No se pudo contactar la estación. Verificá que estés en la misma red.";
  } finally {
    btn.disabled = false;
  }
}

/* ============================================================
   INICIALIZACIÓN
   ============================================================ */
function bindStatic() {
  byId("btn-theme").addEventListener("click", toggleTheme);
  byId("btn-download").addEventListener("click", () => openModal(byId("modal-download")));
  byId("btn-info").addEventListener("click", () => openModal(byId("modal-info")));
  byId("brand-refresh").addEventListener("click", () => location.reload());
  byId("dl-confirm").addEventListener("click", handleDownload);
  byId("btn-silenciar").addEventListener("click", silenciarAlarma);
  byId("dl-range").addEventListener("change", (e) => {
    byId("dl-custom-field").hidden = e.target.value !== "custom";
  });
  byId("offline-close").addEventListener("click", () => {
    state.offlineDismissedId = state.latest ? state.latest.id : null;
    byId("offline-alert").hidden = true;
  });

  document.querySelectorAll("[data-close]").forEach((el) => {
    el.addEventListener("click", () => closeModal(el.closest(".modal")));
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      document.querySelectorAll(".modal:not([hidden])").forEach((m) => closeModal(m));
    }
  });

  byId("info-sources").innerHTML = METRICS
    .map((m) => `<li><strong>${m.title}:</strong> ${m.source}</li>`)
    .join("");
}

function initDropdowns() {
  const dropdowns = Array.from(document.querySelectorAll("[data-dropdown]"));

  function close(except) {
    dropdowns.forEach((d) => {
      if (d === except) return;
      d.querySelector(".dropdown-menu").hidden = true;
      d.querySelector(".dropdown-toggle").setAttribute("aria-expanded", "false");
    });
  }

  dropdowns.forEach((d) => {
    const toggle = d.querySelector(".dropdown-toggle");
    const menu = d.querySelector(".dropdown-menu");
    const valueEl = d.querySelector(".dropdown-value");
    const input = d.querySelector('input[type="hidden"]');

    toggle.addEventListener("click", (e) => {
      e.stopPropagation();
      const open = menu.hidden;
      close(d);
      menu.hidden = !open;
      toggle.setAttribute("aria-expanded", String(open));
    });

    menu.querySelectorAll(".dropdown-option").forEach((opt) => {
      opt.addEventListener("click", () => {
        input.value = opt.dataset.value;
        valueEl.textContent = opt.textContent;
        menu.querySelectorAll(".dropdown-option").forEach((o) => o.classList.toggle("is-selected", o === opt));
        input.dispatchEvent(new Event("change", { bubbles: true }));
        menu.hidden = true;
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      });
    });
  });

  document.addEventListener("click", () => close(null));
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    const anyOpen = dropdowns.some((d) => !d.querySelector(".dropdown-menu").hidden);
    if (anyOpen) { close(null); e.stopPropagation(); }
  }, true);
}

function init() {
  let savedTheme = "dark";
  try { savedTheme = localStorage.getItem("tr_theme") || "dark"; } catch (e) {}
  document.documentElement.dataset.theme = savedTheme;

  buildSkeletons();
  buildCards();
  buildTrendTabs();
  buildModalRanges();
  initTrendChart();
  initMap();
  bindStatic();
  initDropdowns();
  applyTheme(savedTheme);
  refreshIcons();

  loadInitial();
  initRealtime();
  setInterval(poll, CONFIG.pollMs);
  setInterval(renderClock, 1000);

  window.addEventListener("resize", () => {
    if (state.map) state.map.invalidateSize();
  });
  window.addEventListener("orientationchange", () => {
    if (state.map) setTimeout(() => state.map.invalidateSize(), 250);
  });
}

document.addEventListener("DOMContentLoaded", init);
