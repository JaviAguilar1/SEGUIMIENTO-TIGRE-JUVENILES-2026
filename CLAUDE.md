# Reglas de trabajo

- Responder siempre en español (Argentina), tratando de "vos".
- Explicar los pasos de forma simple: el usuario está aprendiendo, así que evitar jerga sin explicarla.
- Antes de tocar código, mostrar el plan de lo que se va a hacer y pedir confirmación antes de aplicarlo.
- Usar la skill `superpowers` para features grandes o con varias partes (planificar,
  detectar riesgos y definir criterios antes de construir) — formaliza la regla de
  arriba, no la reemplaza.

# Estado del proyecto

App de una sola página (`index.html`) para seguimiento de las inferiores de
Tigre. Se viene mejorando en fases (ver los archivos de "Pegada" en
`C:\Users\Javier\Desktop\files\` para el plan completo). Progreso al 2026-08-15
(actualizado el mismo día tras cerrar Fase 6):

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
FECHAS, RENDIMIENTO POR BLOQUE, GOLEADORES y TABLA DE POSICIONES LPF (y,
desde Fase 6, las de PLANTEL/GPS) se colapsan tocando el título
(`seccionTitulo`/`toggleSeccion`). **Arrancan cerradas por defecto**
(`seccionColapsada`, agregado 2026-08-15) — el estado se guarda por
sección y sobrevive a los re-renders (mover el slider de bloque, cambiar
de semestre, etc. no las vuelve a cerrar si ya las abriste).

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
  - **Bug corregido (2026-08-15):** futdetail numera "fecha_nro" por
    separado dentro de cada competencia — la fecha 1 de "Torneo LPF" y la
    fecha 1 de "Amistosos" son partidos distintos que comparten número, y
    `parse_futdetail_partidos` no filtraba por competencia, así que los
    amistosos pisaban las fechas reales del torneo (confirmado con datos
    reales: 4TA F1-F5 traían rivales que ni juegan la LPF —
    "Excursionistas", "San Martín de Burzaco" — eran amistosos). Se
    inspeccionó la respuesta cruda del endpoint (con el usuario, vía
    DevTools) y se confirmó el campo `competencia_descripcion` — ahora se
    descarta cualquier fila que no diga exactamente `"Torneo LPF"`. Esto
    **no se corrige solo en la app**: hace falta que corra el scraper de
    nuevo (automático cada 30 min, o "🔄 Actualizar datos" → "Run workflow"
    en GitHub Actions) para que `data/tablas.json` se regenere con el
    filtro nuevo.
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

**Fase 5 — Export PDF (COMPLETA):** reusa el patrón de `generarPDF()`
(ventana nueva con HTML propio, escudo vía `ESCUDO_B64`, `window.print()` en
el `onload`, sin librerías externas) en tres modos nuevos, todos enganchados
en el panel de ESTADÍSTICAS que sí está vivo hoy (`buildStatsCatSelect` /
`renderStatsCat` / `renderRosterTable`):
1. **Exportar por categoría** — botón "⬇ EXPORTAR PDF" al lado del selector
   (cuando hay una categoría elegida, no en GENERAL). Abre un modal
   (`abrirExportCategoria`) con checkboxes para tildar qué secciones entran:
   Resultados por fecha, Tabla de posiciones LPF, Goleadores, Rendimiento
   por bloque de fechas, Datos de jugadores. Genera con
   `generarPDFCategoria()`; soporta RESERVA (semestres, tabla LPF con las
   dos zonas Clausura/Apertura) igual que el resto de la app.
2. **Ficha individual de jugador** — botón "📄" en cada fila de la tabla de
   PLANTEL (ahora es una pestaña propia, ver Fase 6), `exportFichaJugador()`:
   ficha fija con categoría, posición, edad, convocatorias, titular,
   minutos, goles, asistencias y tarjetas.
3. **Exportar GENERAL** — botón "⬇ EXPORTAR GENERAL" al lado del selector
   cuando está en GENERAL, `generarPDFGeneral()`: resumen general (tabla
   comparativa de las 6 categorías) + rendimiento por bloque acumulado,
   secciones fijas sin checkbox (revierte a propósito la decisión anterior
   de "no exportar GENERAL" — el usuario lo pidió después de ver el resto
   del plan armado).

Todas las secciones (`pdfSection*` + `pdfTablaLPFHtml` + `abrirVentanaPDF`,
cerca de la línea 4915) están escritas con estilos en línea propios (sin
`var(--...)`, porque la ventana del PDF es un documento HTML aparte que no
hereda el CSS de la app) — mismo criterio que ya usaba `generarPDF()`.

**Descubrimiento durante Fase 5, recuperado el 2026-08-15 (ver más abajo):**
el módulo "RENDIMIENTO" apuntaba a `panel-rendimiento`, que no existía en
el HTML — estaba huérfano igual que el módulo GPS. Ya no: se repartió su
contenido dentro de la navegación que sí está viva (ver más abajo).

**Fase 6 — Rendimiento físico / Catapult (COMPLETA):** PLANTEL dejó de estar
escondido detrás del botón "VER DATOS DE JUGADORES" y pasó a ser una
sub-pestaña propia dentro de cada categoría, junto a RESULTADOS
(`catActiveTab`, `buildCatTabsHTML()`, `renderPlantelTab()` — la elección de
pestaña es compartida entre categorías, no por categoría). PLANTEL reúne:
roster + "⚖️ Comparar jugadores" (ya existían, se mudaron ahí sin cambios) +
todo lo nuevo de rendimiento físico:

- **Parser de PDF de Catapult OpenField, rehecho de cero**
  (`extractGpsDataFromPdf` y sus helpers `gpsFindSummaryPage`/
  `gpsBuildFieldMap`/`gpsAssignNumsToColumns`/`gpsDetectCategoria`/etc.,
  buscar "GPS MODULE" en `index.html`). Reemplaza al parser viejo que mapeaba
  columnas por posición fija (rompía apenas cambiaba el set de columnas del
  export). Detecta por **contenido**, no por nombre de archivo, entre 3
  formatos reales de Catapult:
  1. Entrenamiento ("Datos"): varios bloques por ejercicio + página resumen
     final con una fila por jugador — se guardan los números de la página
     resumen y, si están, los nombres de ejercicio como lista de contexto
     (`session.ejercicios`).
  2. Partido: página "DATOS GENERALES" con una fila por jugador.
  3. Solo gráficos (sin tabla de datos, sin importar el nombre del archivo)
     → se rechaza con un mensaje claro en vez de guardar basura.
  El mapeo de columnas es por **nombre de encabezado** (agrupando texto por
  cercanía en X a cada columna numérica), confirmado necesario con 19 PDF
  reales del club: las columnas exportadas no son siempre las mismas (un
  informe de partido puede traer Max Acc/Max Decel/Player Load y otro no).
  La categoría se detecta por el texto del PDF y se valida cruzando nombres
  de jugadores contra el plantel ya cargado — ojo que Catapult exporta
  "Nombre Apellido" y el plantel guarda "Apellido Nombre" (`gpsDetectCategoria`
  compara con las palabras ordenadas alfabéticamente, no el string tal cual).
  Si la categoría detectada no coincide bien, se avisa en el panel de carga
  pero nunca se cambia sola — lo confirma el usuario.
- **Guardado en Firebase:** pasó de `gps.set({sessions:[...]})` (reescribía
  TODO en cada carga, riesgo de pisarse entre dos personas) a
  `gps/sessions/{id}` con `push()` — `saveGpsSession()`/`deleteGpsSession()`.
  Compatible con datos viejos si los hubiera (`Object.values()` funciona
  igual con el array viejo o el objeto nuevo).
- **Carga desde la app:** zona de upload dentro de PLANTEL (solo si
  `canEdit`), con panel de confirmación antes de guardar (nombre de sesión
  editable, aviso de categoría dudosa como se explicó arriba).
- **Comparativas de rendimiento físico:** por un jugador entre 2-3 fechas, y
  entre 2-3 jugadores de una misma sesión — mismo patrón visual (selectores
  + tabla con el máximo destacado en dorado) que ya usan "comparar fechas" y
  "comparar jugadores" en el resto de la app.
- **Recordatorio de GPS sin cargar en Confiabilidad:** mismo mecanismo que
  los recordatorios de links (Fase 3, punto 5) — mismo `dismissKey`, mismo
  botón "👍 OMITIR" — para "partido ya jugado sin sesión GPS de tipo partido
  cargada". Solo 4TA/5TA/6TA (mismo alcance que el resto de Confiabilidad),
  solo partidos (no entrenamientos).

**Vinculación de nombres GPS ↔ plantel (COMPLETA, agregada 2026-08-15):**
mismo mecanismo que `aliasJugadores` de Confiabilidad, pero para la tercera
fuente de nombres (`aliasJugadoresGps[cat]`, `db.ref('stats/aliasJugadoresGps')`).
Antes de mostrar un jugador de GPS como "sin vincular" ya se prueba el
match por palabras ordenadas alfabéticamente (`normNombreOrdenIndependiente`
— así "Santiago Ruiz" de Catapult ya empareja solo con "Ruiz Santiago" del
plantel, sin hacer falta vincular nada a mano); el aviso de "🔗 Vincular"
(dentro de PLANTEL, dentro de la sección GPS) solo aparece para nombres que
de verdad no matchean con nadie del plantel. Una vez vinculado,
`gpsAliasedName(cat, nombre)` se usa en toda la UI de comparativas para
que las dos fuentes se traten como la misma persona.

**Módulo RENDIMIENTO recuperado (COMPLETA, 2026-08-15):** en vez de darle
un panel propio (que hubiera significado un sistema de navegación paralelo
al que ya existe), su contenido se repartió en la navegación actual, según
qué es cada cosa:
- **Forma reciente (últimos 5), Local vs Visitante, Índice de rendimiento**
  (`buildFormaHTML`/`buildLVVHTML`/`buildIndiceRowsHTML`, combinadas en
  `buildRendimientoStatsHTML(idPrefix, cats)`) — son estadísticas de
  **equipo**, derivadas de `results[cat]` (no hace falta cargar nada nuevo):
  aparecen en GENERAL (las 6 categorías juntas) y dentro de RESULTADOS de
  cada categoría (solo la suya). No se muestran para RESERVA — el cálculo
  original siempre usa el fixture de 4TA-9NA (`RIVALS`, 35 fechas), nunca
  `RIVALS_RESERVA`, así que para Reserva daría fechas y rivales mal; eso ya
  venía así en el módulo original, no es algo nuevo.
- **Tarjetas y Lesiones** (`buildTarjetasHTML`/`buildLesionesHTML`, más
  formulario para cargar) — son de **jugador**, así que se movieron a
  PLANTEL de cada categoría, junto al resto de lo individual. Siguen
  guardándose en `rendimiento` (`saveRendimiento()`/`loadRendimiento()`, ya
  estaba bien conectado, no hizo falta tocar el guardado).
- **Citaciones** (`generarPDF()`, planilla de convocados con firma) — no es
  ni de equipo ni de una categoría en particular (tiene su propio selector
  de categoría adentro), así que quedó como herramienta única dentro de
  GENERAL. Se adaptó `renderChecklist()` para leer nombres de
  `plantelFutdetail[cat]` en vez de `players[cat]` — esa era la lista de
  jugadores del módulo PLANTEL viejo con fichas manuales (foto, DNI,
  domicilio) que se sacó a propósito en Fase 1 y no tiene forma de
  cargarse hoy; sin este cambio, Citaciones iba a mostrar siempre "sin
  jugadores".
- Las alertas de tarjetas (3+ amarillas) ya se ven en el header
  (`#alert-pills`/`refreshAlerts()`, que además de tarjetas ya avisaba de
  lesiones activas y sobrecarga de GPS) — no se repitió ese banner adentro
  de PLANTEL para no duplicar la misma info dos veces.
- Bug de cálculo encontrado y corregido de paso: la fecha de una lesión se
  carga como "DD/MM" sin año, y dársela cruda a `new Date(...)` daba
  resultados absurdos (miles de días) — ahora se arma la fecha a mano con
  el año actual (`parseFechaLesionDDMM`).

**Otros dos módulos huérfanos encontrados de paso (sin tocar, quedan para
decidir después):**
- **"CARGA DE ENTRENAMIENTO" / gimnasio** (`buildCargaModule()`, apunta a
  `panel-carga` — no existe en el HTML, mismo patrón que los anteriores).
  Usa `gymData[cat]` para cargar sesiones de gimnasio.
- **"SEMANA" / vista semanal** (`buildSemanaModule()`, apunta a
  `panel-semana` — tampoco existe). Trae un botón "📄 REPORTE"
  (`exportWeeklyReport`) que parece cruzar varias fuentes en un resumen
  semanal.

**Pendiente / a futuro:**
- Decidir si conviene recuperar CARGA (gimnasio) y/o SEMANA — ver arriba.
