# Reglas de trabajo

- Responder siempre en español (Argentina), tratando de "vos".
- Explicar los pasos de forma simple: el usuario está aprendiendo, así que evitar jerga sin explicarla.
- Antes de tocar código, mostrar el plan de lo que se va a hacer y pedir confirmación antes de aplicarlo.

# Estado del proyecto

App de una sola página (`index.html`) para seguimiento de las inferiores de
Tigre. Se viene mejorando en fases (ver los archivos de "Pegada" en
`C:\Users\Javier\Desktop\files\` para el plan completo). Progreso al 2026-08-15
(actualizado el mismo día tras cerrar Fase 4 y arrancar Fase 5):

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
GENERAL, con 5 cruces automáticos (solo 4TA/5TA/6TA — 7MA/8VA/9NA quedan
afuera a pedido):
1. Resultados por partido: mi planilla (`results`) vs LIGA vs futdetail.
2. Equipo: PJ/PG/GF de mi planilla vs tabla oficial LPF.
3. Goles por jugador: mi carga (`goleadores`) vs futdetail (`jugadoresStats`).
4. Links: mi carga (`links`) vs futdetail, para Partido/Resumen Goles/
   Análisis Propio/Próximo Rival (los 4 tipos que futdetail también tiene —
   ver `LINK_KEYS_DESDE_FUTDETAIL`; "Citaciones" no tiene equivalente ahí).
5. Recordatorios: partido ya jugado (con otra fecha posterior también
   jugada, así no hace falta fecha de calendario) sin ningún link cargado
   en ningún lado → recordatorio con botón "👍 OMITIR" que lo descarta para
   siempre en Firebase (`recordatoriosOmitidos`) — a propósito no se
   recalcula solo como el resto, porque a veces no cargar un link es
   intencional.
Los primeros 4 tienen un botón "🔄 REVISAR" que recalcula en vivo (no hay
sistema de "marcar como resuelto" persistente salvo para recordatorios).
Además hay una corrección manual para un error conocido de la LPF que nunca
va a corregirse (`CORRECCIONES_TABLA_LPF`, 6TA/GF) — se aplica sobre el
espejo crudo de la LPF (`TABLA_DATA.categorias`) apenas se descarga, así
se ve bien en todos lados (tabla por categoría, combinada, Confiabilidad).

**Auto-completado de links desde futdetail:** si un link (Partido/Resumen/
Análisis Propio/Próximo Rival) está vacío en tu carga manual, se completa
solo con lo que ya haya en futdetail (`completarLinksDesdeFutdetail`); si
ya cargaste algo, no se toca.

**Secciones desplegables:** dentro de cada categoría, RESULTADOS, COMPARAR
FECHAS, RENDIMIENTO POR BLOQUE, GOLEADORES y TABLA DE POSICIONES LPF se
colapsan tocando el título (`seccionTitulo`/`toggleSeccion`).

**Tabla de equivalencias de jugadores (dentro de Confiabilidad, COMPLETA):**
cuando un jugador aparece "huérfano" (nombre distinto en mi carga vs
futdetail — errores de tipeo, apellidos compuestos), se puede vincular a
mano con un botón "🔗 Vincular" al lado de la diferencia. Queda guardado en
Firebase (`aliasJugadores`, por categoría) para siempre. Adelanta la regla
de emparejamiento de jugadores pensada para Catapult (Pegada 1) — cuando
llegue esa fase, revisar si conviene reusar este mismo mecanismo.

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
  listado de partidos (con goles y links ya incluidos — partido, resumen,
  análisis propio, análisis rival, informe PDF, pelota parada, gps, charla
  DT, arenga) sale de `partidos_consulta_procesos.php` por POST, autenticado
  con la sesión. Si los secrets no están configurados, esta parte se
  saltea sola sin romper el resto.
- Todo lo de arriba se junta en un solo `data/tablas.json` con las claves
  `categorias` (tabla LPF), `fixture` (LIGA) y `fixture_futdetail`.

**Botón "🔄 Actualizar datos" (COMPLETO):** al lado del selector de
categoría/botón de plantel. Al tocarlo: (1) descarta `TABLA_DATA` en memoria
y vuelve a pedir `data/tablas.json` con cache-buster, así se ve ya mismo lo
último que haya en el servidor, y (2) abre en pestaña nueva la página de
GitHub Actions del workflow (`tablas.yml`) para que, si hace falta, se pueda
forzar un scrapeo nuevo ahí mismo con "Run workflow". No dispara la Action
directamente desde la app: eso requeriría guardar un token de GitHub en el
código público de la página, algo inseguro (cualquiera podría copiarlo desde
el navegador) — se descartó a propósito por ese motivo.

**Fase 4 — Auto-refresh (COMPLETA, solo la mitad servidor):** el cron de
`.github/workflows/tablas.yml` pasó de una vez por hora a cada 30 minutos
(`*/30 * * * *`). La mitad navegador (timer interno para refrescar solo sin
que el usuario haga nada) se evaluó y se descartó a pedido expreso: cada
carga/recarga de página ya trae el archivo fresco, y el botón manual cubre
el caso "lo quiero ya" — un timer solo suma valor si alguien deja la pestaña
abierta muchísimas horas sin tocarla, que no es el uso real de la app. Si
eso cambia en el futuro, retomarlo (quedó diseñado: refresco targeted de
`gen-tabla-general`/`gen-posicion`/`gen-confiabilidad`/`tabla-lpf-CAT` +
`sincronizarLinksVaciosEnPantalla`, sin tocar RESULTADOS/GOLEADORES, y
saltando el ciclo si hay un input enfocado).

**Fase 5 — Export PDF (EN CURSO, pausada 2026-08-15 antes de definir
secciones):** ya existe en el código un generador de PDF reutilizable para
"Citaciones" (planilla de convocados a un partido, botón "⬇ GENERAR PDF",
función `generarPDF()` ~línea 4848): arma una ventana nueva con HTML
formateado (escudo vía `ESCUDO_B64`, header rojo/azul del club, tablas) y
llama a `window.print()` en el `onload`, para que el usuario elija "Guardar
como PDF" desde el diálogo de impresión — sin librerías externas. La idea es
reusar el mismo patrón para exportar datos de ESTADÍSTICAS (no solo
Citaciones). Ya definido con el usuario:
- Alcance: **por categoría** (como Citaciones — elegís una categoría y
  exportás sus secciones), no un export combinado de GENERAL.
- Falta definir: qué secciones exactas entran (candidatas charladas:
  Resultados por fecha, Tabla de posiciones LPF, Goleadores, Rendimiento por
  bloque de fechas) — quedó sin cerrar, retomar preguntando eso antes de
  tocar código.

**Descubrimiento relevante para Fase 6:** el código ya tiene un módulo GPS
arrancado (no expuesto en la navegación actual): `gpsSessions`,
`saveGpsData()`, `db.ref('gps')`, etc. (~línea 4916 en adelante). Es
anterior a las fases de esta sesión y no está integrado a la UI de hoy —
antes de "empezar de cero" la Fase 6, revisar ese módulo para ver qué ya
sirve y qué hay que rehacer.

**Pendiente:**
- Fase 5 — Export PDF (ver arriba, falta cerrar qué secciones exportar).
- Fase 6 — Catapult (datos físicos/GPS). Capa aparte, nunca se cruza con
  resultados. Ver regla de emparejamiento de jugadores en la Pegada 1, y el
  módulo GPS ya existente mencionado arriba.
