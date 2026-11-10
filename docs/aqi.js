/* ICA EPA parcial: la estación no mide O3, NO2 ni SO2, y PM1.0 queda fuera.
   Se carga antes de app.js y también se requiere desde Node (module.exports). */
(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) {
    module.exports = api;
  } else {
    root.AQI = api;
  }
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  /* Paleta oficial EPA (AQI 2024). */
  const COLORS = {
    good: "#00E400",
    moderate: "#FFFF00",
    sensitive: "#FF7E00",
    unhealthy: "#FF0000",
    "very-unhealthy": "#8F3F97",
    hazardous: "#7E0023",
    neutral: "#94A3B8"
  };

  /* Cortes EPA. decimals = precisión con la que la EPA trunca
     antes de interpolar (PM2.5 y CO 0.1; PM10 entero). */
  const BREAKPOINTS = {
    pm25: {
      decimals: 1,
      ranges: [
        [0.0, 9.0, 0, 50],
        [9.1, 35.4, 51, 100],
        [35.5, 55.4, 101, 150],
        [55.5, 125.4, 151, 200],
        [125.5, 225.4, 201, 300],
        [225.5, 325.4, 301, 500]
      ]
    },
    pm10: {
      decimals: 0,
      ranges: [
        [0, 54, 0, 50],
        [55, 154, 51, 100],
        [155, 254, 101, 150],
        [255, 354, 151, 200],
        [355, 424, 201, 300],
        [425, 604, 301, 500]
      ]
    },
    co: {
      decimals: 1,
      ranges: [
        [0.0, 4.4, 0, 50],
        [4.5, 9.4, 51, 100],
        [9.5, 12.4, 101, 150],
        [12.5, 15.4, 151, 200],
        [15.5, 30.4, 201, 300],
        [30.5, 50.4, 301, 500]
      ]
    }
  };

  const CATEGORIES = [
    {
      max: 50,
      label: "Buena",
      color: "good",
      desc: "La calidad del aire es satisfactoria y el riesgo para la salud es bajo.",
      health: "Ideal para actividades al aire libre. Se recomienda ventilar los ambientes."
    },
    {
      max: 100,
      label: "Moderada",
      color: "moderate",
      desc: "Calidad aceptable, aunque algunas personas muy sensibles podrían notar molestias leves.",
      health: "Apto para la mayoría. Personas con asma o afecciones pulmonares deberían vigilar síntomas."
    },
    {
      max: 150,
      label: "Dañina para grupos sensibles",
      color: "sensitive",
      desc: "Grupos sensibles pueden experimentar efectos en la salud.",
      health: "Niños, adultos mayores y personas con afecciones respiratorias: reducir el esfuerzo intenso al aire libre."
    },
    {
      max: 200,
      label: "Dañina",
      color: "unhealthy",
      desc: "Todos pueden comenzar a sentir efectos en la salud.",
      health: "Limitar la actividad física prolongada al aire libre."
    },
    {
      max: 300,
      label: "Muy dañina",
      color: "very-unhealthy",
      desc: "Riesgo para la salud de toda la población.",
      health: "Evitar actividades al aire libre. Cerrar ventanas."
    },
    {
      max: Infinity,
      label: "Peligrosa",
      color: "hazardous",
      desc: "Condiciones de emergencia sanitaria.",
      health: "Permanecer en interiores y evitar la exposición al aire libre."
    }
  ];

  function esNumeroValido(value) {
    return value !== null && value !== undefined && value !== "" && isFinite(Number(value));
  }

  /* Trunca (no redondea), como pide la EPA. */
  function truncate(value, decimals) {
    if (!esNumeroValido(value)) return null;
    const n = Number(value);
    if (n <= 0) return 0;
    const factor = Math.pow(10, decimals);
    return Math.floor(n * factor + 1e-9) / factor;
  }

  /* Subíndice de un contaminante. Devuelve null si no hay dato. */
  function subIndex(pollutant, concentration) {
    const spec = BREAKPOINTS[pollutant];
    if (!spec) return null;

    const c = truncate(concentration, spec.decimals);
    if (c === null) return null;
    if (c <= 0) return 0;

    const ranges = spec.ranges;
    for (let i = 0; i < ranges.length; i++) {
      const [cLow, cHigh, iLow, iHigh] = ranges[i];
      if (c >= cLow && c <= cHigh) {
        return Math.round(((iHigh - iLow) / (cHigh - cLow)) * (c - cLow) + iLow);
      }
    }

    return c > ranges[ranges.length - 1][1] ? 500 : 0;
  }

  function subIndices(row) {
    return {
      pm25: row ? subIndex("pm25", row.pm25) : null,
      pm10: row ? subIndex("pm10", row.pm10) : null,
      co: row ? subIndex("co", row.co) : null
    };
  }

  /* ICA = máximo de los subíndices disponibles. null si no hay ninguno. */
  function computeAQI(row) {
    if (!row) return null;
    const values = Object.values(subIndices(row)).filter((v) => v !== null);
    if (!values.length) return null;
    return Math.max(...values);
  }

  function dominantPollutant(row) {
    if (!row) return null;
    const subs = subIndices(row);
    let best = null;

    Object.entries(subs).forEach(([pollutant, value]) => {
      if (value === null) return;
      if (!best || value > best.value) best = { pollutant, value };
    });

    return best;
  }

  function category(aqi) {
    if (!esNumeroValido(aqi)) return null;
    const n = Number(aqi);
    for (const cat of CATEGORIES) {
      if (n <= cat.max) return cat;
    }
    return CATEGORIES[CATEGORIES.length - 1];
  }

  function colorFor(aqi) {
    const cat = category(aqi);
    return cat ? COLORS[cat.color] : COLORS.neutral;
  }

  return {
    COLORS,
    BREAKPOINTS,
    CATEGORIES,
    truncate,
    subIndex,
    subIndices,
    computeAQI,
    dominantPollutant,
    category,
    colorFor
  };
});
