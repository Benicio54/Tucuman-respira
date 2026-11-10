"use strict";

/* La clave es la pública (anon) del proyecto. En una aplicación estática
   siempre es visible en el cliente; la protección real depende de las políticas RLS. */
const CONFIG = {
  supabaseUrl: "https://lskvyvpjjziuclaatrtu.supabase.co",
  supabaseKey: "sb_publishable_O9Havbh6tsAZEDA8VFWQzg_LmTmU4mM",
  table: "mediciones",
  averagesView: "ica_promedios",
  historyLimit: 100,
  pollMs: 15000,
  staleWarnSeconds: 120,
  staleOfflineSeconds: 300,
  defaultLat: -26.82414,
  defaultLng: -65.2226,
  downloadRanges: { "100": 100, "500": 500, "1000": 1000, all: Infinity },
  deviceKey: "tucu2026",
  deviceIpDefault: "192.168.4.1",
  muteMinutes: 10,
  pmHours: 24,
  coHours: 8,
  minCoverage: 0.75
};

/* Umbrales de referencia, con la fuente indicada por métrica en la interfaz.
   PM1.0 tiene escala propia y no entra al ICA; PM2.5, PM10 y CO sí. */
const METRICS = [
  {
    id: "co2", field: "co2", title: "Dióxido de Carbono (CO₂)", short: "CO₂",
    unit: "ppm", icon: "cloud", decimals: 0, alert: true, meterMax: 2000,
    chartColor: "#38bdf8",
    source: "OSHA/NIOSH (límites de exposición) · ASHRAE (referencia de ventilación)",
    ranges: [
      { max: 800, label: "Bueno", color: "good" },
      { max: 1000, label: "Aceptable", color: "moderate" },
      { max: 1500, label: "Ventilación pobre", color: "sensitive" },
      { max: 5000, label: "Alta (PEL 8 h)", color: "unhealthy" },
      { max: 30000, label: "Muy alta (STEL)", color: "very-unhealthy" },
      { max: Infinity, label: "Peligro (IDLH)", color: "hazardous" }
    ]
  },
  {
    id: "co", field: "co", title: "Monóxido de Carbono (CO)", short: "CO",
    unit: "ppm", icon: "flame", decimals: 2, alert: true, meterMax: 50,
    chartColor: "#FF0000",
    source: "EPA AQI 2024 (8 h) · MQ-7 con curva corregida y calibración estimada",
    ranges: [
      { max: 4.4, label: "Buena", color: "good" },
      { max: 9.4, label: "Moderada", color: "moderate" },
      { max: 12.4, label: "Dañina grupos sensibles", color: "sensitive" },
      { max: 15.4, label: "Dañina", color: "unhealthy" },
      { max: 30.4, label: "Muy dañina", color: "very-unhealthy" },
      { max: Infinity, label: "Peligrosa", color: "hazardous" }
    ]
  },
  {
    id: "pm1", field: "pm1", title: "Material Particulado (PM1.0)", short: "PM1.0",
    unit: "µg/m³", icon: "wind", decimals: 0, alert: false, meterMax: 100,
    chartColor: "#00E400",
    source: "Escala propia · informativa, sin ICA oficial (referencia: ~2/3 del PM2.5)",
    note: "No entra al ICA",
    ranges: [
      { max: 10, label: "Bajo", color: "good" },
      { max: 20, label: "Moderado", color: "moderate" },
      { max: 30, label: "Alto", color: "sensitive" },
      { max: 50, label: "Muy alto", color: "unhealthy" },
      { max: 75, label: "Extremo", color: "very-unhealthy" },
      { max: Infinity, label: "Peligroso", color: "hazardous" }
    ]
  },
  {
    id: "pm25", field: "pm25", title: "Material Particulado (PM2.5)", short: "PM2.5",
    unit: "µg/m³", icon: "wind", decimals: 0, alert: true, meterMax: 325.4,
    chartColor: "#FF7E00",
    source: "EPA AQI 2024 (24 h)",
    ranges: [
      { max: 9.0, label: "Buena", color: "good" },
      { max: 35.4, label: "Moderada", color: "moderate" },
      { max: 55.4, label: "Dañina grupos sensibles", color: "sensitive" },
      { max: 125.4, label: "Dañina", color: "unhealthy" },
      { max: 225.4, label: "Muy dañina", color: "very-unhealthy" },
      { max: Infinity, label: "Peligrosa", color: "hazardous" }
    ]
  },
  {
    id: "pm10", field: "pm10", title: "Material Particulado (PM10)", short: "PM10",
    unit: "µg/m³", icon: "wind", decimals: 0, alert: true, meterMax: 604,
    chartColor: "#8F3F97",
    source: "EPA AQI 2024 (24 h)",
    ranges: [
      { max: 54, label: "Buena", color: "good" },
      { max: 154, label: "Moderada", color: "moderate" },
      { max: 254, label: "Dañina grupos sensibles", color: "sensitive" },
      { max: 354, label: "Dañina", color: "unhealthy" },
      { max: 424, label: "Muy dañina", color: "very-unhealthy" },
      { max: Infinity, label: "Peligrosa", color: "hazardous" }
    ]
  },
  {
    id: "temp", field: "temperatura", title: "Temperatura", short: "Temperatura",
    unit: "°C", icon: "thermometer", decimals: 1, alert: true, meterMax: 50,
    chartColor: "#fb923c",
    source: "NWS/OSHA (estrés por calor) · NIOSH (estrés por frío)",
    ranges: [
      { max: 0, label: "Hipotermia", color: "hazardous" },
      { max: 10, label: "Frío", color: "moderate" },
      { max: 27, label: "Confortable", color: "good" },
      { max: 32, label: "Precaución por calor", color: "sensitive" },
      { max: 39, label: "Extrema precaución", color: "unhealthy" },
      { max: 52, label: "Peligro", color: "very-unhealthy" },
      { max: Infinity, label: "Peligro extremo", color: "hazardous" }
    ]
  },
  {
    id: "hum", field: "humedad", title: "Humedad Relativa", short: "Humedad",
    unit: "%", icon: "droplets", decimals: 0, alert: true, meterMax: 100,
    chartColor: "#22d3ee",
    source: "OMS (humedad y moho) · ASHRAE (recomendación 30–60%)",
    ranges: [
      { max: 20, label: "Muy seco", color: "sensitive" },
      { max: 30, label: "Seco", color: "moderate" },
      { max: 60, label: "Ideal", color: "good" },
      { max: 70, label: "Algo húmedo", color: "moderate" },
      { max: 85, label: "Riesgo de moho", color: "unhealthy" },
      { max: Infinity, label: "Alto riesgo de moho", color: "very-unhealthy" }
    ]
  },
  {
    id: "pres", field: "presion", title: "Presión Atmosférica", short: "Presión",
    unit: "hPa", icon: "gauge", decimals: 0, alert: false, meterMax: null,
    chartColor: "#94a3b8",
    source: "Informativo",
    ranges: [
      { max: 1004.9, label: "Baja", color: "moderate" },
      { max: 1020, label: "Normal", color: "good" },
      { max: Infinity, label: "Alta", color: "moderate" }
    ]
  },
  {
    id: "uv", field: "uv", title: "Radiación UV", short: "UV",
    unit: "mW/cm²", icon: "sun", decimals: 2, alert: true, meterMax: 15,
    chartColor: "#f59e0b",
    source: "Sensor ML8511",
    ranges: [
      { max: 1, label: "Bajo", color: "good" },
      { max: 3, label: "Moderado", color: "sensitive" },
      { max: 6, label: "Alto", color: "unhealthy" },
      { max: 10, label: "Muy alto", color: "very-unhealthy" },
      { max: Infinity, label: "Extremo", color: "hazardous" }
    ]
  },
  {
    id: "lux", field: "luz", title: "Luz Ambiental", short: "Luz",
    unit: "lux", icon: "sun-medium", decimals: 0, alert: false, meterMax: 1000,
    chartColor: "#a3e635",
    source: "Informativo",
    ranges: [
      { max: 9.9, label: "Oscuridad", color: "neutral" },
      { max: 99.9, label: "Penumbra", color: "moderate" },
      { max: 499, label: "Interior", color: "good" },
      { max: Infinity, label: "Pleno sol", color: "sensitive" }
    ]
  }
];

const TREND_TABS = [
  { id: "particles", label: "Partículas", metrics: ["pm1", "pm25", "pm10"], subtitle: "PM1.0, PM2.5 y PM10 (µg/m³)" },
  { id: "gases", label: "Gases", metrics: ["co2", "co"], subtitle: "Dióxido de carbono (CO₂) y monóxido de carbono (CO)" },
  { id: "climate", label: "Clima", metrics: ["temp", "hum"], subtitle: "Temperatura y humedad relativa" },
  { id: "radiation", label: "Luz / UV", metrics: ["uv", "lux"], subtitle: "Radiación UV y luz ambiental" }
];

const state = {
  rows: [],
  latest: null,
  averages: null,
  trend: "particles",
  modal: null,
  modalRange: 50,
  chart: null,
  sensorChart: null,
  map: null,
  marker: null,
  station: null,
  tile: null,
  client: null,
  lastId: null,
  offlineDismissedId: null,
  modalTrigger: null,
  cardsBuilt: false,
  loaded: false,
  loadFailed: false
};

const $ = (sel) => document.querySelector(sel);
const byId = (id) => document.getElementById(id);

/* Utilidades */
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
  if (!range) return { label: "Sin datos", color: "neutral" };
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

function isValidNumber(value) {
  return value !== null && value !== undefined && value !== "" && !isNaN(Number(value));
}

function formatNumber(value, decimals = 0) {
  return isValidNumber(value) ? Number(value).toFixed(decimals) : "--";
}

/* ICA EPA parcial: tablas y truncado en aqi.js; una hora cuenta con 15 min de muestras. */
const SEVERE_COLORS = ["sensitive", "unhealthy", "very-unhealthy", "hazardous"];

function coverageOk(hours, windowHours) {
  return isValidNumber(hours) && Number(hours) >= Math.ceil(windowHours * CONFIG.minCoverage);
}

function averagesForAQI() {
  const avg = state.averages;
  if (!avg) return null;

  const row = {};
  if (coverageOk(avg.horas_pm25, CONFIG.pmHours) && isValidNumber(avg.pm25_24h)) row.pm25 = Number(avg.pm25_24h);
  if (coverageOk(avg.horas_pm10, CONFIG.pmHours) && isValidNumber(avg.pm10_24h)) row.pm10 = Number(avg.pm10_24h);
  if (coverageOk(avg.horas_co, CONFIG.coHours) && isValidNumber(avg.co_8h)) row.co = Number(avg.co_8h);

  return Object.keys(row).length ? row : null;
}

function aqiInput() {
  const averaged = averagesForAQI();
  if (averaged) return { mode: "average", row: averaged };
  return { mode: "instant", row: state.latest };
}

async function fetchAverages() {
  const url = `${CONFIG.supabaseUrl}/rest/v1/${CONFIG.averagesView}?select=*`;
  const res = await fetch(url, {
    headers: { apikey: CONFIG.supabaseKey, Authorization: `Bearer ${CONFIG.supabaseKey}` }
  });
  if (!res.ok) throw new Error(`Supabase HTTP ${res.status}`);
  const data = await res.json();
  return Array.isArray(data) && data.length ? data[0] : null;
}

async function refreshAverages() {
  try {
    state.averages = await fetchAverages();
  } catch (err) {
    state.averages = null;
  }
}

function describeMethod(input) {
  if (input.mode === "average") {
    return "Promedios móviles con cobertura mínima del 75 % (PM 18/24 h · CO 6/8 h).";
  }
  if (!state.latest) return "Esperando mediciones de la estación.";
  return "Lectura instantánea: todavía no hay cobertura suficiente para el promedio (PM 18/24 h · CO 6/8 h).";
}

function renderBreakdown(input) {
  const wrap = byId("aqi-breakdown");
  if (!wrap) return;

  const avg = state.averages || {};
  const specs = [
    { key: "pm25", label: "PM2.5", unit: "µg/m³", decimals: 1, hours: avg.horas_pm25, window: CONFIG.pmHours },
    { key: "pm10", label: "PM10", unit: "µg/m³", decimals: 1, hours: avg.horas_pm10, window: CONFIG.pmHours },
    { key: "co", label: "CO", unit: "ppm", decimals: 2, hours: avg.horas_co, window: CONFIG.coHours }
  ];

  wrap.innerHTML = specs.map((s) => {
    const value = input.row ? input.row[s.key] : null;

    if (!isValidNumber(value)) {
      const reason = input.mode === "average" && isValidNumber(s.hours) ? "sin cobertura" : "sin dato";
      return `<span class="aqi-chip is-missing lvl-neutral"><i class="aqi-chip-dot"></i><b>${s.label}</b> ${reason}</span>`;
    }

    const sub = AQI.subIndex(s.key, value);
    const cat = AQI.category(sub);
    const color = cat ? cat.color : "neutral";
    const coverage = input.mode === "average" ? ` · ${s.hours}/${s.window} h` : "";

    return `<span class="aqi-chip lvl-${color}"><i class="aqi-chip-dot"></i><b>${s.label}</b> ${formatNumber(value, s.decimals)} ${s.unit} <em>ICA ${sub}${coverage}</em></span>`;
  }).join("");
}

function renderLegend() {
  const wrap = byId("aqi-legend");
  if (!wrap) return;

  wrap.innerHTML = AQI.CATEGORIES.map((cat) => {
    const range = cat.max === Infinity ? "> 300" : `≤ ${cat.max}`;
    return `<span class="lvl-${cat.color}"><i></i>${cat.label} ${range}</span>`;
  }).join("");
}

/* Construcción de tarjetas */
function buildSkeletons() {
  const grid = byId("sensors-grid");
  grid.innerHTML = METRICS.map(() => `<div class="skeleton"></div>`).join("");
}

function ensureCards() {
  if (state.cardsBuilt) return;
  buildCards();
  state.cardsBuilt = true;
}

function buildCards() {
  const grid = byId("sensors-grid");
  grid.innerHTML = METRICS.map((m) => `
    <button type="button" class="sensor-card lvl-neutral" data-metric="${m.id}">
      <div class="sensor-top">
        <span class="sensor-name">${m.title}${m.note ? ` <em class="sensor-tag">${m.note}</em>` : ""}</span>
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
    if (!valueEl || !statusEl || !card) return;
    const cls = classify(m, raw);
    const alertClass = m.alert && SEVERE_COLORS.includes(cls.color) ? " is-alert" : "";

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

/* Banner y resumen */
function renderHero() {
  const input = aqiInput();
  const aqi = AQI.computeAQI(input.row);
  const cat = AQI.category(aqi);
  const banner = byId("air-banner");
  const alarm = byId("alarm-box");

  byId("aqi-number").textContent = aqi === null ? "--" : aqi;
  byId("aqi-category").textContent = cat ? cat.label : "Sin datos";
  byId("aqi-status").textContent = cat ? `Calidad del aire: ${cat.label}` : "Sin datos disponibles";
  byId("air-description").textContent = cat ? cat.desc : "No hay mediciones registradas por el momento.";
  byId("health-text").textContent = cat ? cat.health : "Sin información suficiente para dar una recomendación.";
  byId("aqi-method").textContent = describeMethod(input);
  setLevel(banner, cat ? cat.color : "neutral", "air-banner");

  renderBreakdown(input);
  renderLegend();

  /* El zumbador del equipo usa la lectura instantánea, no el promedio. */
  const instantAqi = AQI.computeAQI(state.latest);
  const instantCat = AQI.category(instantAqi);
  const buzzer = instantAqi === null ? "SIN DATOS"
    : instantAqi <= 100 ? "NORMAL"
    : instantAqi <= 150 ? "PRECAUCIÓN"
    : instantAqi <= 200 ? "ALERTA"
    : "ALERTA CRÍTICA";

  byId("alarm-text").textContent = buzzer;
  setLevel(alarm, instantCat ? instantCat.color : "neutral", "alarm-box");
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

/* Reloj y watchdog */
function renderClock() {
  const badge = byId("connection-badge");
  const dot = byId("conn-dot");
  const text = byId("last-update");
  const alert = byId("offline-alert");
  const row = state.latest;

  const reading = byId("last-reading");
  if (!row || !row.created_at) {
    if (state.loadFailed) {
      dot.className = "conn-dot off";
      text.textContent = "Sin conexión";
    } else if (state.loaded) {
      dot.className = "conn-dot off";
      text.textContent = "Sin lecturas";
    } else {
      dot.className = "conn-dot is-loading";
      text.textContent = "Conectando…";
    }
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

/* Mapa GPS */
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
    state.station = null;
    byId("map-center").disabled = true;
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
    html: '<div style="width:18px;height:18px;border-radius:50%;background:#10b981;border:3px solid #fff;box-shadow:0 0 0 6px rgba(16,185,129,.25)" title="Ubicación de la estación" role="img" aria-label="Ubicación de la estación"></div>',
    iconSize: [18, 18],
    iconAnchor: [9, 9]
  });

  if (state.marker) {
    state.marker.setLatLng([lat, lng]);
  } else {
    state.marker = L.marker([lat, lng], { icon }).addTo(state.map);
    state.marker.on("add", () => {
      const el = state.marker.getElement();
      if (el) el.setAttribute("aria-label", "Ubicación de la estación");
    });
  }
  state.map.setView([lat, lng], state.map.getZoom() < 12 ? 13 : state.map.getZoom());
  state.station = { lat, lng };
  byId("map-center").disabled = false;
}

function centerOnStation() {
  if (!state.map || !state.station) return;
  state.map.flyTo([state.station.lat, state.station.lng],
    Math.max(state.map.getZoom(), 13), { duration: 0.7 });
}

/* Gráfico de tendencia */
function chartColors() {
  const dark = document.documentElement.dataset.theme === "dark";
  return {
    text: dark ? "#94a3b8" : "#526072",
    grid: dark ? "rgba(51,65,85,.35)" : "rgba(203,213,225,.6)"
  };
}

/* Color EPA del nivel del valor, para el cuadradito del tooltip. */
function epaSwatch(metricId, value) {
  const metric = metricById(metricId);
  const range = metric ? findRange(metric, value) : null;
  const hex = AQI.COLORS[range ? range.color : "neutral"] || AQI.COLORS.neutral;
  return { borderColor: hex, backgroundColor: hex, borderWidth: 0 };
}

function buildTrendTabs() {
  const wrap = byId("trend-tabs");
  wrap.innerHTML = TREND_TABS.map((t) =>
    `<button type="button" role="tab" id="trend-tab-${t.id}" data-trend="${t.id}" aria-selected="${t.id === state.trend}" aria-controls="trend-panel" tabindex="${t.id === state.trend ? "0" : "-1"}" class="${t.id === state.trend ? "is-active" : ""}">${t.label}</button>`
  ).join("");
  const tabs = Array.from(wrap.querySelectorAll("[data-trend]"));

  function select(btn, focus) {
    state.trend = btn.dataset.trend;
    tabs.forEach((b) => {
      const on = b === btn;
      b.classList.toggle("is-active", on);
      b.setAttribute("aria-selected", String(on));
      b.tabIndex = on ? 0 : -1;
    });
    const panel = byId("trend-panel");
    if (panel) panel.setAttribute("aria-labelledby", btn.id);
    if (focus) btn.focus();
    buildTrendChart();
  }

  tabs.forEach((btn) => btn.addEventListener("click", () => select(btn, false)));
  wrap.addEventListener("keydown", (e) => {
    const i = tabs.indexOf(document.activeElement);
    if (i < 0) return;
    let target = null;
    if (e.key === "ArrowRight") target = tabs[(i + 1) % tabs.length];
    else if (e.key === "ArrowLeft") target = tabs[(i - 1 + tabs.length) % tabs.length];
    else if (e.key === "Home") target = tabs[0];
    else if (e.key === "End") target = tabs[tabs.length - 1];
    if (target) { e.preventDefault(); select(target, true); }
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
          cornerRadius: 10,
          callbacks: {
            labelColor: (item) => {
              const tab = TREND_TABS.find((t) => t.id === state.trend);
              return epaSwatch(tab ? tab.metrics[item.datasetIndex] : null, item.raw);
            }
          }
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
    const color = m.chartColor;
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

/* Histórico por sensor */
function openModal(el) {
  state.modalTrigger = document.activeElement instanceof HTMLElement ? document.activeElement : null;
  el.hidden = false;
  const barra = window.innerWidth - document.documentElement.clientWidth;
  document.documentElement.style.overflow = "hidden";
  document.body.style.overflow = "hidden";
  if (barra > 0) document.body.style.paddingRight = `${barra}px`;
  document.querySelectorAll(MODAL_BACKGROUND).forEach((node) => { node.inert = true; });
  const card = el.querySelector(".modal-card");
  if (card) requestAnimationFrame(() => card.focus());
}
function closeModal(el) {
  el.hidden = true;
  if (!document.querySelector(".modal:not([hidden])")) {
    document.documentElement.style.overflow = "";
    document.body.style.overflow = "";
    document.body.style.paddingRight = "";
    document.querySelectorAll(MODAL_BACKGROUND).forEach((node) => { node.inert = false; });
    if (state.modalTrigger && document.contains(state.modalTrigger)) state.modalTrigger.focus();
    state.modalTrigger = null;
  }
}

const MODAL_BACKGROUND = "header.site-header, main.main, footer.site-footer, body > .container";

function trapModalFocus(e) {
  if (e.key !== "Tab") return;
  const modal = document.querySelector(".modal:not([hidden])");
  if (!modal) return;
  const focusables = Array.from(modal.querySelectorAll(
    'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
  ));
  if (!focusables.length) { e.preventDefault(); return; }
  const first = focusables[0];
  const last = focusables[focusables.length - 1];
  const active = document.activeElement;
  const isTabStop = focusables.includes(active);
  if (!isTabStop) {
    e.preventDefault();
    (e.shiftKey ? last : first).focus();
    return;
  }
  if (e.shiftKey && active === first) { e.preventDefault(); last.focus(); }
  else if (!e.shiftKey && active === last) { e.preventDefault(); first.focus(); }
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
  const color = m.chartColor;
  const labels = rows.map((r) => formatDateTime(r.created_at).slice(-8));
  const data = rows.map((r) => {
    const v = Number(r[m.field]);
    return isNaN(v) ? null : v;
  });

  if (state.sensorChart) {
    state.sensorChart.data.labels = labels;
    state.sensorChart.data.datasets[0].data = data;
    state.sensorChart.data.datasets[0].label = m.unit ? `${m.short} (${m.unit})` : m.short;
    state.sensorChart.data.datasets[0].borderColor = color;
    state.sensorChart.data.datasets[0].backgroundColor = color + "22";
    state.sensorChart.data.datasets[0].pointBackgroundColor = color;
    state.sensorChart.data.datasets[0].pointBorderColor = color;
    state.sensorChart.data.datasets[0].pointHoverBackgroundColor = color;
    state.sensorChart.data.datasets[0].pointHoverBorderColor = color;
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
        pointBorderColor: color,
        pointHoverBackgroundColor: color,
        pointHoverBorderColor: color,
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
          cornerRadius: 10,
          callbacks: {
            labelColor: (item) => epaSwatch(state.modal, item.raw)
          }
        }
      },
      scales: {
        x: { ticks: { color: c.text, maxTicksLimit: 8 }, grid: { color: c.grid } },
        y: { ticks: { color: c.text }, grid: { color: c.grid }, beginAtZero: false }
      }
    }
  });
}

/* Descarga de datos */
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
  const headers = ["id", "fecha_hora", "pm1_ug_m3", "pm25_ug_m3", "pm10_ug_m3", "co2_ppm", "co_ppm", "temperatura_c", "humedad_pct", "presion_hpa", "uv", "luz_lux", "latitud", "longitud"];
  const lines = rows.map((r) => [
    r.id, r.created_at, r.pm1, r.pm25, r.pm10, r.co2, r.co, r.temperatura, r.humedad, r.presion, r.uv, r.luz, r.latitud, r.longitud
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

function setDownloadFeedback(text, kind) {
  const el = byId("download-feedback");
  if (!el) return;
  el.textContent = text;
  el.classList.toggle("is-error", kind === "error");
  el.classList.toggle("is-ok", kind === "ok");
}

async function handleDownload() {
  const format = byId("dl-format").value;
  const rangeKey = byId("dl-range").value;
  const btn = byId("dl-confirm");
  const customField = byId("dl-custom");

  if (rangeKey === "custom") {
    const custom = parseInt(customField.value, 10);
    if (!Number.isFinite(custom) || custom < 1) {
      setDownloadFeedback("Escribí una cantidad mayor a 0.", "error");
      customField.focus();
      return;
    }
  }

  btn.disabled = true;
  setDownloadFeedback("Preparando la descarga…");

  try {
    const rows = await fetchRows(resolveDownloadLimit(rangeKey));
    if (!rows.length) {
      setDownloadFeedback("No hay registros para descargar en ese rango.", "error");
      return;
    }

    const stamp = new Date().toISOString().slice(0, 10);
    if (format === "json") {
      download(`tucuman_respira_${stamp}.json`, JSON.stringify(rows), "application/json;charset=utf-8");
    } else {
      download(`tucuman_respira_${stamp}.csv`, toCSV(rows), "text/csv;charset=utf-8;");
    }
    const count = rows.length === 1 ? "1 registro" : `${rows.length} registros`;
    setDownloadFeedback(`Descarga iniciada: ${count}.`, "ok");
  } catch (err) {
    console.error(err);
    setDownloadFeedback("No se pudo descargar. Revisá la conexión y reintentá.", "error");
  } finally {
    btn.disabled = false;
  }
}

function resolveDownloadLimit(rangeKey) {
  if (rangeKey !== "custom") return CONFIG.downloadRanges[rangeKey];

  const custom = parseInt(byId("dl-custom").value, 10);
  return Number.isFinite(custom) && custom > 0 ? custom : CONFIG.downloadRanges["100"];
}

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  byId("theme-icon").setAttribute("data-lucide", theme === "dark" ? "sun" : "moon");
  byId("btn-theme").setAttribute("aria-pressed", theme === "light");
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

function refreshIcons() {
  if (window.lucide && typeof lucide.createIcons === "function") lucide.createIcons();
}

/* Carga de datos */
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
  const hasRows = state.rows.length > 0;
  const grid = byId("sensors-grid");
  const empty = byId("sensors-empty");
  const trendEmpty = byId("trend-empty");
  const trendCanvas = byId("trend-chart");
  if (grid) grid.hidden = !hasRows;
  if (empty) empty.hidden = hasRows;
  if (trendEmpty) trendEmpty.hidden = hasRows;
  if (trendCanvas) trendCanvas.hidden = !hasRows;

  renderCards();
  renderHero();
  renderSummary();
  renderClock();
  renderMap();
  buildTrendChart();
  if (state.chart && hasRows) state.chart.resize();
  if (state.modal && !byId("modal-sensor").hidden) buildSensorChart();
}

function showLoadError(message) {
  byId("load-error-text").textContent = message;
  byId("load-error").hidden = false;
}

function hideLoadError() {
  byId("load-error").hidden = true;
}

async function loadInitial() {
  hideLoadError();
  try {
    const data = await supabaseGet(`?select=*&order=id.desc&limit=${CONFIG.historyLimit}`);
    data.reverse();
    ingest(data);
    ensureCards();
    state.loadFailed = false;
    state.loaded = true;
    await refreshAverages();
    renderAll();
    if (!data.length) {
      byId("summary-subtitle").textContent = "Sin lecturas registradas";
    }
  } catch (err) {
    showLoadError("No se pudieron cargar las mediciones. Revisá la conexión y reintentá.");
    state.loadFailed = true;
    state.loaded = true;
    byId("aqi-status").textContent = "No se pudo conectar";
    byId("air-description").textContent = "Verifica la conexión a internet e inténtalo nuevamente.";
    byId("last-update").textContent = "Sin conexión";
    byId("conn-dot").className = "conn-dot off";
    byId("summary-subtitle").textContent = "Sin lecturas";
    byId("sensors-grid").hidden = true;
    byId("sensors-empty").hidden = false;
    byId("trend-empty").hidden = false;
    byId("trend-chart").hidden = true;
  }
}

async function retryLoad() {
  const btn = byId("load-error-retry");
  btn.disabled = true;
  btn.textContent = "Reintentando…";
  await loadInitial();
  btn.disabled = false;
  btn.textContent = "Reintentar";
}

function initRealtime() {
  if (!window.supabase || typeof window.supabase.createClient !== "function") return;
  try {
    state.client = window.supabase.createClient(CONFIG.supabaseUrl, CONFIG.supabaseKey);
    state.client
      .channel("mediciones-stream")
      .on("postgres_changes", { event: "INSERT", schema: "public", table: CONFIG.table }, (payload) => {
        if (!payload || !payload.new || !ingest([payload.new])) return;
        ensureCards();
        state.loadFailed = false;
        state.loaded = true;
        hideLoadError();
        refreshAverages().finally(renderAll);
      })
      .subscribe();
  } catch (err) {
    state.client = null;
  }
}

async function poll() {
  try {
    const data = await supabaseGet("?select=*&order=id.desc&limit=1");
    if (data && data.length) {
      ensureCards();
      state.loadFailed = false;
      state.loaded = true;
      hideLoadError();
      if (data[0].id !== state.lastId && ingest(data)) {
        await refreshAverages();
        renderAll();
      }
    }
  } catch (err) {
    /* Silencioso: el watchdog visual refleja el estado. */
  }
}

/* Alarma del dispositivo */
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

/* Inicialización */
function bindStatic() {
  byId("btn-theme").addEventListener("click", toggleTheme);
  byId("btn-download").addEventListener("click", () => {
    setDownloadFeedback("");
    openModal(byId("modal-download"));
  });
  byId("btn-info").addEventListener("click", () => openModal(byId("modal-info")));
  byId("brand-refresh").addEventListener("click", () => location.reload());
  byId("map-center").addEventListener("click", centerOnStation);
  byId("dl-confirm").addEventListener("click", handleDownload);
  byId("load-error-retry").addEventListener("click", retryLoad);
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
  document.addEventListener("keydown", trapModalFocus);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      document.querySelectorAll(".modal:not([hidden])").forEach((m) => closeModal(m));
    }
  });

  byId("info-sources").innerHTML = [
    `<li><strong>ICA EPA parcial:</strong> PM2.5 y PM10 (24 h) · CO (8 h) · colores oficiales EPA 2024.</li>`,
    ...METRICS.map((m) => `<li><strong>${m.title}:</strong> ${m.source}</li>`)
  ].join("");
}

function initDropdowns() {
  const dropdowns = Array.from(document.querySelectorAll("[data-dropdown]"));

  const optionsOf = (d) => Array.from(d.querySelectorAll(".dropdown-option"));

  function close(except, returnFocus) {
    dropdowns.forEach((d) => {
      if (d === except) return;
      const menu = d.querySelector(".dropdown-menu");
      if (menu.hidden) return;
      menu.hidden = true;
      d.querySelector(".dropdown-toggle").setAttribute("aria-expanded", "false");
      if (returnFocus) d.querySelector(".dropdown-toggle").focus();
    });
  }

  function open(d) {
    const menu = d.querySelector(".dropdown-menu");
    const toggle = d.querySelector(".dropdown-toggle");
    close(d, false);
    menu.hidden = false;
    toggle.setAttribute("aria-expanded", "true");
    const selected = menu.querySelector(".dropdown-option.is-selected") || optionsOf(d)[0];
    if (selected) selected.focus();
  }

  function select(d, opt) {
    const toggle = d.querySelector(".dropdown-toggle");
    const valueEl = d.querySelector(".dropdown-value");
    const input = d.querySelector('input[type="hidden"]');
    input.value = opt.dataset.value;
    valueEl.textContent = opt.textContent;
    optionsOf(d).forEach((o) => {
      const on = o === opt;
      o.classList.toggle("is-selected", on);
      o.setAttribute("aria-selected", String(on));
    });
    input.dispatchEvent(new Event("change", { bubbles: true }));
    d.querySelector(".dropdown-menu").hidden = true;
    toggle.setAttribute("aria-expanded", "false");
    toggle.focus();
  }

  dropdowns.forEach((d) => {
    const toggle = d.querySelector(".dropdown-toggle");
    const menu = d.querySelector(".dropdown-menu");
    const opts = optionsOf(d);

    toggle.addEventListener("click", (e) => {
      e.stopPropagation();
      if (menu.hidden) open(d);
      else {
        menu.hidden = true;
        toggle.setAttribute("aria-expanded", "false");
      }
    });

    toggle.addEventListener("keydown", (e) => {
      if (e.key === "ArrowDown" || e.key === "ArrowUp") {
        e.preventDefault();
        open(d);
      }
    });

    opts.forEach((opt) => {
      opt.addEventListener("click", () => select(d, opt));
      opt.addEventListener("keydown", (e) => {
        const index = opts.indexOf(opt);
        let next = null;
        if (e.key === "ArrowDown") next = opts[(index + 1) % opts.length];
        else if (e.key === "ArrowUp") next = opts[(index - 1 + opts.length) % opts.length];
        else if (e.key === "Home") next = opts[0];
        else if (e.key === "End") next = opts[opts.length - 1];
        else if (e.key === "Enter" || e.key === " ") { e.preventDefault(); select(d, opt); return; }
        else if (e.key === "Tab") {
          menu.hidden = true;
          toggle.setAttribute("aria-expanded", "false");
          return;
        }
        if (next) { e.preventDefault(); next.focus(); }
      });
    });
  });

  document.addEventListener("click", () => close(null, false));
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    const openDropdown = dropdowns.find((d) => !d.querySelector(".dropdown-menu").hidden);
    if (!openDropdown) return;
    openDropdown.querySelector(".dropdown-menu").hidden = true;
    const toggle = openDropdown.querySelector(".dropdown-toggle");
    toggle.setAttribute("aria-expanded", "false");
    toggle.focus();
    e.stopPropagation();
  }, true);
}

function init() {
  let savedTheme = "dark";
  try { savedTheme = localStorage.getItem("tr_theme") || "dark"; } catch (e) {}
  document.documentElement.dataset.theme = savedTheme;

  buildSkeletons();
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
