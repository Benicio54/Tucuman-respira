const test = require("node:test");
const assert = require("node:assert/strict");
const AQI = require("./aqi.js");

test("trunca como la EPA (no redondea)", () => {
  assert.equal(AQI.truncate(9.09, 1), 9.0);
  assert.equal(AQI.truncate(9.19, 1), 9.1);
  assert.equal(AQI.truncate(54.9, 0), 54);
  assert.equal(AQI.truncate(-3, 1), 0);
  assert.equal(AQI.truncate(null, 1), null);
});

test("PM2.5 no deja huecos entre tramos", () => {
  assert.equal(AQI.subIndex("pm25", 9.0), 50);
  assert.equal(AQI.subIndex("pm25", 9.1), 51);
  assert.equal(AQI.subIndex("pm25", 35.4), 100);
  assert.equal(AQI.subIndex("pm25", 35.5), 101);
  assert.equal(AQI.subIndex("pm25", 325.4), 500);
  assert.equal(AQI.subIndex("pm25", 400), 500);
});

test("PM10 no deja huecos entre tramos", () => {
  assert.equal(AQI.subIndex("pm10", 54), 50);
  assert.equal(AQI.subIndex("pm10", 55), 51);
  assert.equal(AQI.subIndex("pm10", 154), 100);
  assert.equal(AQI.subIndex("pm10", 155), 101);
  assert.equal(AQI.subIndex("pm10", 604), 500);
});

test("CO no deja huecos entre tramos", () => {
  assert.equal(AQI.subIndex("co", 4.4), 50);
  assert.equal(AQI.subIndex("co", 4.5), 51);
  assert.equal(AQI.subIndex("co", 9.4), 100);
  assert.equal(AQI.subIndex("co", 9.5), 101);
  assert.equal(AQI.subIndex("co", 50.4), 500);
});

test("el ICA es el máximo de los subíndices disponibles", () => {
  assert.equal(AQI.computeAQI({ pm25: 12, pm10: 60, co: 2 }), 56);
  assert.equal(AQI.computeAQI({ pm25: null, pm10: 80, co: null }), 63);
  assert.equal(AQI.computeAQI({ pm25: null, pm10: null, co: null }), null);
  assert.equal(AQI.computeAQI(null), null);
});

test("identifica el contaminante dominante", () => {
  assert.deepEqual(AQI.dominantPollutant({ pm25: 12, pm10: 60, co: 2 }), {
    pollutant: "pm25",
    value: 56
  });
  assert.equal(AQI.dominantPollutant({}), null);
});

test("categorías y colores en los bordes", () => {
  assert.equal(AQI.category(50).label, "Buena");
  assert.equal(AQI.category(51).label, "Moderada");
  assert.equal(AQI.category(100).label, "Moderada");
  assert.equal(AQI.category(101).label, "Dañina para grupos sensibles");
  assert.equal(AQI.category(301).label, "Peligrosa");
  assert.equal(AQI.colorFor(75), "#FFFF00");
  assert.equal(AQI.colorFor(null), "#94A3B8");
});

test("PM1.0 no entra al ICA", () => {
  assert.equal(AQI.computeAQI({ pm1: 500 }), null);
});
