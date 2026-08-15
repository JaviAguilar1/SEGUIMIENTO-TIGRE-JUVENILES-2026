# Reglas de trabajo

- Responder siempre en español (Argentina), tratando de "vos".
- Explicar los pasos de forma simple: el usuario está aprendiendo, así que evitar jerga sin explicarla.
- Antes de tocar código, mostrar el plan de lo que se va a hacer y pedir confirmación antes de aplicarlo.

# Estado del proyecto

App de una sola página (`index.html`) para seguimiento de las inferiores de
Tigre. Se viene mejorando en fases (ver los archivos de "Pegada" en
`C:\Users\Javier\Desktop\files\` para el plan completo). Progreso al 2026-08-15:

**Fase 1 — Estructura (COMPLETA):** se sacó la pantalla de Inicio y la solapa
PLANTEL. La app arranca directo en ESTADÍSTICAS → GENERAL. Selector de
categoría (desplegable) arriba, con el botón "ver datos de jugadores" al
lado cuando hay una categoría elegida (no en GENERAL).

**Fase 2 — Comparativas (COMPLETA):** tamaño de bloque de fechas
configurable (slider 2-17, `bloqueSize`), con tabla "RENDIMIENTO POR BLOQUE
DE FECHAS" tanto en GENERAL (acumulado) como por categoría. Comparar 2-3
fechas sueltas de una categoría. Comparar 2-3 jugadores de una categoría en
tabla (no se hizo comparativa entre categorías, se descartó a pedido
expreso — "puede generar malestar").

**Fase 3 — Confiabilidad (COMPLETA):** sección "🔎 CONFIABILIDAD" al final de
GENERAL, con 3 cruces automáticos (solo 4TA/5TA/6TA — 7MA/8VA/9NA quedan
afuera a pedido):
1. Resultados por partido: mi planilla (`results`) vs LIGA vs futdetail.
2. Equipo: PJ/PG/GF de mi planilla vs tabla oficial LPF.
3. Goles por jugador: mi carga (`goleadores`) vs futdetail (`jugadoresStats`).
Cada diferencia tiene un botón "🔄 REVISAR" que recalcula en vivo (no hay
sistema de "marcar como resuelto" persistente, se reemplazó por esto).

**Fuentes de datos automatizadas** (`scripts/scrape_tablas.py`, corre cada
hora vía `.github/workflows/tablas.yml`, sin intervención manual):
- **Tabla de posiciones LPF:** scrape simple de `ligaprofesional.ar` (HTML
  estático). Funciona desde antes de esta fase.
- **Fixture partido por partido (LIGA):** la LPF oficial carga esto con JS
  (widget de Opta, no se puede scrapear simple). En cambio
  `sabadogol.com.ar/fixture.php` muestra el mismo fixture en HTML plano
  (POST con params `a`/`c`/`d`/`t`, ver `FIXTURE_TORNEOS` en el script) — de
  ahí sale.
- **futdetail:** panel privado (`futdetail.com.ar/futdetail_web_tigre/`).
  Login clásico por formulario + cookie de sesión PHP (nada de navegador
  headless, mucho más simple que LPF). Las credenciales viven en GitHub
  Secrets (`FUTDETAIL_USER`, `FUTDETAIL_PASS`) — nunca en el código. El
  listado de partidos (con goles ya incluidos) sale de
  `partidos_consulta_procesos.php` por POST, autenticado con la sesión.
  Si los secrets no están configurados, esta parte se saltea sola sin
  romper el resto.
- Todo lo de arriba se junta en un solo `data/tablas.json` con las claves
  `categorias` (tabla LPF), `fixture` (LIGA) y `fixture_futdetail`.

**Pendiente:**
- Fase 4 — Auto-refresh cada 30 min (tablas + futdetail). La más delicada,
  tiene dos mitades (servidor y navegador), avisar antes de tocar nada.
- Fase 5 — Export PDF con el escudo del club, eligiendo qué exportar.
- Fase 6 — Catapult (datos físicos/GPS). Capa aparte, nunca se cruza con
  resultados. Ver regla de emparejamiento de jugadores en la Pegada 1.
