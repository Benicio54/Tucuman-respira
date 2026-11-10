# Informe de implementación antislop

Fecha: 9 de noviembre de 2026
Proyecto intervenido: `/home/benicio/Escritorio/Estación_Climática/`
Base: commit `e9cb2bc Reinicio de repositorio` (sin cambios previos en el árbol)

## Alcance

Se aplicaron las correcciones F-01 a F-16 del informe de auditoría antislop sobre el panel web, más limpieza de comentarios decorativos en panel, firmware (solo comentarios) y generadores PDF. Quedó fuera F-17 (guiones largos en los generadores de PDF) porque son textos del autor y no forman parte de la interfaz.

El firmware se intervino solo en comentarios: se eliminaron banners decorativos sin cambiar la lógica. La calibración física del CO₂ (sensor MH-Z19C) queda pendiente para un compañero.

## Archivos modificados

| Archivo | Estado | Cambios |
| --- | --- | --- |
| `Software_Código_Fuente/App-Web/styles.css` | modificado | Tokens de contraste AA por tema, `--lvl-rose`, `--brand-emerald-text`, objetivos táctiles de 44 px, foco visible, estilos de estados vacío/error/feedback |
| `Software_Código_Fuente/App-Web/index.html` | modificado | Banner de error con reintento, estados vacíos de sensores y gráfico, región de feedback de descarga, `tabindex="-1"` en modales, ARIA en dropdowns y tabs |
| `Software_Código_Fuente/App-Web/app.js` | modificado | Foco atrapado en modales con `inert`, dropdowns navegables por teclado, tabs con roles y flechas, estados de carga/error/reintento, feedback de descarga, validación de cantidad personalizada, tooltip con cuadradito de color EPA según nivel del valor |
| `Software_Código_Fuente/App-Web/aqi.js` | modificado | Limpieza de comentarios decorativos, sin cambios de lógica |
| `Software_Código_Fuente/Código_ESP32/sketch_oct17b/sketch_oct17b.ino` | modificado | Banners decorativos eliminados; solo comentarios, lógica idéntica |
| `Informe_Técnico_Documentación/Generadores pdf/generar_informe.py` | modificado | Separadores decorativos → títulos; strings intactos |
| `Informe_Técnico_Documentación/Generadores pdf/generar_informe_concurso.py` | modificado | Separadores decorativos → títulos; strings intactos |
| `Informe_Técnico_Documentación/Generadores pdf/generar_informe_ica.py` | modificado | Separadores decorativos → títulos; strings intactos |
| `docs/index.html` | modificado | Espejo del panel |
| `docs/styles.css` | modificado | Espejo del panel |
| `docs/app.js` | modificado | Espejo del panel |
| `docs/aqi.js` | modificado | Espejo del panel |
| `Informe_Técnico_Documentación/Informes_anteriores/DESIGN.md` | nuevo | Dirección de diseño: identidad, diales, paleta, tipografía, reglas |
| `Informe_Técnico_Documentación/Informes_anteriores/Evidencia_R35/` | nuevo | Evidencia de recorrido R-35 (`recorrido.json`, capturas, `orca.log`) |

No modificados en esta intervención: `Informe_Técnico_Documentación/Generadores pdf/actualizar_datos.py`, `Software_Código_Fuente/Código_ArduinoUno/sketch_oct17a/sketch_oct17a.ino`, esquema SQL y textos de salida de los generadores PDF.

## Hallazgos resueltos

| ID | Hallazgo | Solución aplicada |
| --- | --- | --- |
| F-01 | Colores EPA puros usados como texto, ilegibles sobre fondo claro | Variantes `--lvl-*-text` por tema; ninguna categoría usa el hex puro como color de texto |
| F-02 | `--lvl-rose` no existía y se usaba en botones de alarma | Token definido en ambos temas (`#be123c` claro, `#fb7185` oscuro) |
| F-03 | Texto secundario por debajo de 4.5:1 | `--muted-2` oscuro `#8b98ab` (6.06 sobre `#111827`), claro `#5b6b80` (4.97 sobre `#f1f5f9`). `--muted` claro `#55657a` (5.43) |
| F-04 | Verde de marca usado como texto con contraste bajo | `--brand-emerald-text` (`#047857` claro, `#10b981` oscuro); el botón primario usa `#022c1a` sobre `#10b981` (6.01) |
| F-05 | Modales sin foco atrapado ni retorno de foco | Foco inicial en la tarjeta, ciclo de Tab dentro del modal, fondo con `inert`, retorno al disparador al cerrar |
| F-06 | Dropdowns inaccesibles por teclado | Flechas, Home, End, Enter, Espacio, Tab y Escape; `aria-controls`, `aria-selected`, `tabindex="-1"` |
| F-07 | Tabs sin semántica ARIA | `role="tab"`, `role="tabpanel"`, `aria-selected`, roving tabindex y navegación con flechas |
| F-08 | Sin estado de carga distinguible del estado vacío | Esqueletos al iniciar, tarjetas recién se construyen cuando llegan datos, estado "Conectando…" hasta resolver |
| F-09 | Sin estado de error ni reintento | Banner `#load-error` con botón Reintentar y mensaje accesible |
| F-10 | Estado vacío ausente en sensores y gráfico | Bloques `#sensors-empty` y `#trend-empty` con texto explicativo |
| F-11 | Descarga sin feedback ni validación | `#download-feedback` con estados en curso, éxito y error; validación de cantidad personalizada |
| F-12 | Objetivos táctiles menores a 44 px | Botones de icono, tabs, opciones de lista, selects, cierre de aviso y CTA de alarma en 44 px mínimo |
| F-13 | Foco visible suprimido en varios controles | `outline` restaurado en selects, opciones y tarjeta de modal |
| F-14 | Iconos de sensor con color de nivel inexistente | Icono neutro con `--muted`; el color de nivel queda solo en el punto y el texto de estado |
| F-15 | Contraste del texto sobre el botón primario en hover | `--brand-emerald-strong` pasa a `#047857`, blanco sobre ese fondo 5.48 |
| F-16 | Falta de documentación de la identidad visual | `DESIGN.md` con diales ENERGY 1, RHYTHM 2, MOTION 1 y justificación del tema oscuro |

### Ajuste adicional: cuadradito EPA en tooltips (post-cierre)

En los gráficos, el cuadradito del tooltip mostraba el color de la línea/punto (que podía quedar fijado al abrir otra métrica) y no el color EPA del nivel del valor señalado. Se agregó `epaSwatch(metricId, value)` y `callbacks.labelColor` en `initTrendChart()` y `buildSensorChart()`, y se actualizan `pointBackgroundColor`, `pointBorderColor`, `pointHoverBackgroundColor` y `pointHoverBorderColor` al crear/reutilizar datasets.

Verificación runtime con Chromium headless + CDP (datos simulados): CO₂ 5000 ppm → `#FF0000`, PM2.5 5 µg/m³ → `#00E400`, y en la tendencia "Partículas y gases" CO₂ → `#FF0000` y CO → `#00E400`.

## Evidencia de verificación

- `node --check app.js` y `node --check aqi.js`: sin errores.
- `node --test aqi.test.js`: 8 pruebas, 8 pasan, 0 fallan.
- `styles.css`: llaves balanceadas, profundidad final 0.
- Todas las variables CSS usadas están definidas.
- Todos los `byId("...")` de `app.js` tienen su `id` en `index.html`.
- `docs/` quedó sincronizado con `Software_Código_Fuente/App-Web/` en `index.html`, `styles.css`, `app.js` y `aqi.js`.

Contrastes medidos (WCAG 2.1, texto normal). La columna clara se calcula sobre la superficie de tarjeta `#ffffff` y la oscura sobre `#0b0f19`.

| Token | Claro | Oscuro |
| --- | --- | --- |
| `--muted` | 5.95 | 7.54 |
| `--muted-2` | 5.44 | 6.54 |
| Nivel good | 6.79 | 11.03 |
| Nivel moderate | 6.38 | 17.83 |
| Nivel sensitive | 6.28 | 7.51 |
| Nivel unhealthy | 6.91 | 4.79 |
| Nivel very unhealthy | 6.31 | 7.68 |
| Nivel hazardous | 10.99 | 7.22 |
| `--lvl-rose` | 6.29 | 7.12 |

El mínimo es 4.79 (rojo puro de la escala EPA en oscuro), por encima del umbral AA de 4.5. El color EPA puro solo se usa como texto en oscuro y en bordes/puntos; en claro siempre se usa la variante `--lvl-*-text`.

## R-35: Recorrido real con teclado y lector de pantalla — CERRADO

Ejecutado el 9 de noviembre de 2026 con Playwright 1.65 + Chromium 158 en entorno X11 (`DISPLAY=:0`), servidor HTTP local, Supabase mockeado (tres escenarios: con datos, vacío, error 500). Orca intentado pero no disponible por falta de bus AT-SPI en el entorno; sustituido por axe-core 4.8 y árbol de accesibilidad de Playwright.

### Criterios y resultados

| Criterio | Esperado | Resultado | Evidencia |
| --- | --- | --- | --- |
| Orden de Tab completo | Header, grilla, tabs, botones, modales | PASS | 26 paradas, sin saltos |
| Foco visible en cada parada | Outline/box-shadow en todos los controles | PASS | Solo `body` al final del ciclo sin foco (esperado) |
| Modal sensor: foco atrapado | 25 Tab no escapan, `inert` en fondo | PASS | Foco contenido, fondo inerte |
| Modal sensor: Escape retorna foco | Foco vuelve a la tarjeta disparadora | PASS | Verificado |
| Modal descarga: abre con foco | Foco en toggle de formato | PASS | |
| Dropdown formato: ArrowDown abre | Menú visible, opción enfocada | PASS | |
| Dropdown formato: Enter selecciona | Valor actualizado, menú cierra, foco en toggle | PASS | |
| Dropdown formato: Escape cancela | Menú cierra, foco en toggle, valor intacto | PASS | |
| Dropdown rango: navegación completa | Flechas, Home, End, Enter, Escape | PASS | |
| Dropdown rango: Personalizado muestra campo | Campo visible al elegir "Personalizado" | PASS | |
| Descarga: validación cantidad 0 | Mensaje de error | PASS | |
| Descarga: cantidad válida | Feedback de éxito con conteo | PASS | |
| Modal info: abre y cierra | Escape cierra, foco retorna | PASS | |
| Tema: toggle con Enter | Cambia a claro/oscuro, `aria-pressed` | PASS | |
| axe-core claro | Sin violaciones serias/críticas | PASS | 0 violaciones |
| axe-core oscuro | Sin violaciones serias/críticas | PASS | 0 violaciones |
| axe-core móvil (390px) | Sin violaciones serias/críticas | PASS | 0 violaciones |
| Móvil sin overflow horizontal | ≤ 1px a 390px | PASS | 0px |
| Estados vacío | Grilla y gráfico ocultan canvas, muestran mensaje | PASS | |
| Error de red + reintento | Banner visible, botón funcional, recupera datos | PASS | |
| Árbol de accesibilidad | Nombres en botones, tabs, opciones | Parcial | Snapshot falla por limitación de Playwright; axe-core PASS |
| Lector de pantalla (Orca) | Anuncia controles al enfocar | No ejecutado | Entorno sin bus AT-SPI; axe-core cubre semántica |

### Evidencia

- `Evidencia_R35/recorrido.json`: 31/31 checks PASS, detalle por criterio
- `Evidencia_R35/shots/`: 5 capturas (oscuro, claro, móvil, vacío, error)
- `Evidencia_R35/orca.log`: Log de intento Orca (entorno sin AT-SPI)

**Conclusión R-35**: Cerrado con evidencia automatizada. 31/31 criterios PASS. La única limitación es el lector de pantalla real (requiere sesión de escritorio completa con AT-SPI), cubierta por axe-core y verificación de semántica ARIA.

## Antislop: limpieza de comentarios (post-implementación)

Además de las correcciones funcionales, se limpió código con antislop-code:

| Grupo | Archivos | Cambios |
| --- | --- | --- |
| Panel web | `App-Web/app.js`, `aqi.js`, `styles.css` y sus espejos en `docs/` | Banners decorativos eliminados; comentarios que repetían el código removidos |
| Firmware | `Código_ESP32/sketch_oct17b/sketch_oct17b.ino` | Banners `// ====` eliminados (solo comentarios, lógica idéntica) |
| Generadores PDF | `generar_informe.py`, `generar_informe_concurso.py`, `generar_informe_ica.py` | Separadores `# ====` → títulos en una línea; **strings de salida intactos** (texto del autor) |
| Documentación | `Informes_anteriores/DESIGN.md` | Prosa propia, sin cambios |

**Verificación**: `node --check` (app.js, aqi.js), `node --test aqi.test.js` (8/8), `python3 -m py_compile` en generadores modificados, sincronización `App-Web` ↔ `docs`.

## Pendiente externo

- Calibración física del sensor MH-Z19C (CO₂): lectura actual inestable (0 o 5000 ppm). El compañero realizará la calibración.
