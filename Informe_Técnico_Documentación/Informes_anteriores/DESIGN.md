# Dirección de diseño: Tucumán Respira

## Producto y audiencia

Panel público de una estación de monitoreo ambiental IoT. Lo consultan vecinos, docentes y estudiantes de Tucumán para entender en segundos el estado del aire y el clima. La prioridad es el dato, no la decoración.

## Identidad

El panel representa aire que se mueve sobre una ciudad de noche. La marca es verde esmeralda y el fondo profundo es azul noche. Esa combinación separa la lectura de los sensores del ruido del entorno y hace que los colores EPA funcionen como señales, no como adornos.

No se usa una estética de producto SaaS genérico: no hay gradientes de marca, ni glassmorphism en tarjetas, ni grillas de fondo. El único recurso decorativo es el borde lateral del ICA, que repite el color de la categoría como una marca de estado.

## Diales

- **ENERGY 1**: lectura calmada y densa en datos. Un solo foco por pantalla: el número del ICA.
- **RHYTHM 2**: hero con banner y resumen, grilla de sensores y dos paneles distintos. Hay variación, no una plantilla repetida.
- **MOTION 1**: solo transiciones de hover, pulso del estado de conexión y shimmer del esqueleto de carga. Nada de animaciones de entrada.

## Paleta

- **Base**: `#020617` (fondo oscuro) y `#f8fafc` (fondo claro).
- **Superficies**: `#0b0f19` y `#111827` en oscuro; `#ffffff` y `#f1f5f9` en claro.
- **Marca**: `#10b981`. El texto que necesita contraste usa `#047857` en claro y `#10b981` en oscuro.
- **Acento funcional**: escala oficial EPA. No es decoración: codifica la categoría del ICA. Se usa en bordes, puntos y medidores. Para texto existe una variante AA por tema (`--lvl-*-text`).

La paleta efectiva son dos colores base más un acento de marca. La escala EPA es un segundo sistema, justificado por el dato.

## Tipografía

Pila de fuentes del sistema (`-apple-system`, `Segoe UI`, `Roboto`, `Arial`). Motivo: cero dependencias de red, render nativo en celulares de gama baja y lectura estable en ambos temas. No se usa una tipografía decorativa porque el panel no vende una marca, publica mediciones.

## Componentes

- Radios de 16 px en superficies y 10 px en controles. Solo los badges de estado son píldoras, porque representan una etiqueta corta.
- Objetivos táctiles de 44 px como mínimo en botones, tabs, opciones de lista y cierre de avisos.
- Sombras solo en tarjetas al pasar el mouse y en modales. Sirven para indicar elevación, no para hacer flotar toda la página.
- Iconografía Lucide. Se elige por el trazo de línea, que acompaña la lectura de datos, y porque cada icono tiene relación directa con su métrica: viento, gotas, termómetro, sol, reloj.

## Tema oscuro por defecto

El panel se consulta al aire libre y de noche tanto como de día. El fondo azul noche mantiene la lectura estable en pantallas OLED y hace que los colores EPA conserven su función de alarma. El tema claro está disponible y comparte los mismos tokens de contraste.

## Marca y activos

El favicon y la marca textual son parte del proyecto existente. Si el equipo define un logo formal, se reemplaza el SVG inline por ese archivo y se elimina el actual.

## Reglas de mantenimiento

- Ningún color EPA puro se usa como texto. Siempre se usa su variante `--lvl-*-text`.
- Cualquier texto nuevo debe cumplir 4.5:1 en ambos temas. Los tokens `--muted` y `--muted-2` ya están calibrados.
- Los estados vacío, de carga y de error son parte del componente, no un agregado.
- El modo oscuro y el claro se prueban juntos. Un cambio de paleta se valida en los dos.
