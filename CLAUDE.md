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
(actualizado el mismo día tras cerrar Fase 7):

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
  el año actual (`parseFechaLesionDDMM`). Ver Fase 7 más abajo por un ajuste
  posterior a esta misma función (cruce de fin de año).

**Otros dos módulos huérfanos encontrados de paso (sin tocar, quedan para
decidir después):**
- **"CARGA DE ENTRENAMIENTO" / gimnasio** (`buildCargaModule()`, apunta a
  `panel-carga` — no existe en el HTML, mismo patrón que los anteriores).
  Usa `gymData[cat]` para cargar sesiones de gimnasio.
- **"SEMANA" / vista semanal** (`buildSemanaModule()`, apunta a
  `panel-semana` — tampoco existe). Trae un botón "📄 REPORTE"
  (`exportWeeklyReport`) que parece cruzar varias fuentes en un resumen
  semanal.

**Fase 7 — Revisión de código y ajustes (COMPLETA, 2026-08-15):** después de
cerrar la Fase 6, se hizo una revisión completa de todo lo tocado en la
sesión (8 ángulos de revisión en paralelo — correctitud, reuso,
simplificación, eficiencia, altitud, convenciones — con verificación
posterior de cada hallazgo). De 10 hallazgos, 2 se corrigieron ya durante la
revisión misma; los otros 8 se resolvieron después, a pedido explícito del
usuario ("HACE TODO LO QUE PUEDAS"):
1. **Carga de GPS pendiente que se perdía por re-render:** si mientras el
   usuario tenía abierto el panel de confirmación de una carga de GPS
   llegaba una actualización de Firebase (de cualquier cosa, no solo GPS),
   `refreshActiveModule()` volvía a dibujar toda la pantalla y se perdía la
   confirmación a medio hacer. Ahora hay una bandera `gpsPendingUpload` que
   frena ese re-render mientras el panel está abierto.
2. **Fecha editable en la confirmación de carga de GPS:** para una sesión de
   tipo partido, la fecha que trae el PDF ahora se puede corregir a mano
   antes de guardar (`gpsFechaInput-${cat}`) — antes quedaba fija con lo que
   hubiera detectado el parser, sin forma de arreglar un error de lectura.
3. **Fecha de lesión, cruce de fin de año:** `parseFechaLesionDDMM` arma la
   fecha con el año actual, pero si la lesión fue en diciembre y hoy ya es
   enero del año siguiente, esa cuenta daba una fecha "futura" — ahora, si
   la fecha calculada con el año actual queda después de hoy, se usa el año
   anterior.
4. **Módulo GPS viejo eliminado:** el primer intento de módulo GPS (antes de
   esta sesión, ~730 líneas: `renderGpsModule`, `buildGpsUploadSection`,
   `processGpsPdf`, etc.) apuntaba a `panel-gps`, que nunca existió en el
   HTML — quedó completamente inalcanzable en cuanto se armó el sistema
   nuevo (dentro de PLANTEL). Se borró en vez de mantenerlo: ya estaba
   superado del todo, parchearlo hubiera sido esfuerzo tirado.
5. **Nombres en las alertas del header:** los avisos de "🟨 X en alerta" y
   "🩹 X lesionado(s)" en `#alert-pills` solo decían la cantidad — ahora el
   tooltip (mantener el mouse encima) lista los nombres y la categoría de
   cada uno.
6. **Cálculo compartido entre pantalla y PDF exportado:** "Rendimiento por
   bloque de fechas" y la tabla de posiciones LPF tenían el cálculo
   duplicado entre la versión de pantalla y la versión del PDF exportado —
   riesgo de que una corrección futura se aplicara en un lado y no en el
   otro. Ahora `calcBloqueFilas()` y `enriquecerFilasTabla()` calculan el
   dato una sola vez y cada versión (pantalla con `var(--...)`, PDF con
   colores fijos) solo se encarga de pintarlo.
7. **Aviso si el filtro de competencia del scraper deja de matchear:** el
   filtro `"torneo lpf"` agregado para el bug de futdetail (ver más arriba)
   ahora imprime un `[WARN]` si llegaron partidos crudos de futdetail pero
   ninguno pasó el filtro — para enterarse rápido si el día de mañana
   futdetail cambia el nombre de la competencia, en vez de quedarse con
   0 fechas en silencio.
8. **Umbral de columna del parser de GPS, derivado del espaciado real:** el
   mapeo de columnas por cercanía en X (`gpsBuildFieldMap`/
   `gpsAssignNumsToColumns`) usaba una distancia fija (25px/20px) para
   decidir qué tan lejos puede estar un fragmento de texto o un número de su
   columna. Ahora `gpsColThreshold()` agranda ese umbral si el espaciado
   real entre columnas de un PDF puntual es más ancho de lo normal — pero
   **nunca lo achica** por debajo del valor ya probado, así los 19 PDF
   reales usados para calibrar el parser (`C:\Users\Javier\Desktop\GPS\`)
   siguen dando exactamente el mismo resultado (verificado matemáticamente:
   el espaciado mínimo real medido en esos 19 PDF, 21-31px, siempre queda
   por debajo del umbral fijo, así que `gpsColThreshold` elige el valor
   viejo en los 19 casos). Solo entra en juego si en el futuro Catapult
   manda un reporte con menos columnas repartidas en la misma hoja
   (columnas más separadas) — antes ese caso podía perder datos por
   "quedar demasiado lejos" de un umbral pensado para columnas más juntas.

**Backup automático de Firebase (COMPLETO, 2026-08-15):**
`scripts/backup_firebase.py`, corre una vez por día vía
`.github/workflows/backup.yml` (cron 6am UTC / 3am Argentina, más botón
"Run workflow" para forzarlo). Antes no existía ninguna copia de respaldo
de los datos de la temporada — vivían solo en Firebase.
- Guarda un JSON por día en `data/backups/backup-YYYY-MM-DD.json` y borra
  los más viejos que los últimos 30 (`BACKUPS_A_CONSERVAR`), para que el
  repo no crezca sin límite.
- **Probé en vivo los 4 nodos que lee la app** (`stats`, `plantel`,
  `rendimiento`, `gps`, los mismos que lee `loadData()`) pidiéndolos sin
  login: solo `stats` respondió 200 (resultados, goleadores, links,
  aliasJugadores, etc. — todo lo que guarda `saveData()` bajo ese nodo).
  `plantel`, `rendimiento` y `gps` dieron 401 — necesitan sesión. Esto
  coincide con `startPublicListener()` (línea ~4504: "load stats for
  everyone, auth or not") — la lectura pública es a propósito, pero
  **solo para `stats`**, no para los otros tres como decía un comentario
  viejo cerca de `showLoginWall()` que ya no refleja el diseño real.
  Por hoy, el script respalda `stats` sin necesitar nada de vos.
- **Para que también respalde `plantel`/`rendimiento`/`gps`** (roster,
  tarjetas, lesiones, sesiones GPS) hace falta un usuario de Firebase
  dedicado (rol "viewer" alcanza, no necesita poder editar nada) — crealo
  en Firebase Console y cargá su email/contraseña como secrets de GitHub
  `FIREBASE_BACKUP_EMAIL` / `FIREBASE_BACKUP_PASS`. El script ya sabe
  usarlos si están (mismo patrón que `FUTDETAIL_USER`/`PASS`); si no
  están, sigue funcionando igual, solo que respalda menos.

**Reglas de seguridad de Firebase — pendiente de revisar en la consola:**
lo de arriba fue probar desde AFUERA qué se puede leer sin loguearse — no
pude ver las reglas reales (viven en Firebase Console, no en este repo,
y no tengo acceso). Dos cosas que valdría la pena que confirmes ahí vos
mismo cuando tengas un rato:
1. Que la escritura a `stats`/`plantel`/`rendimiento`/`gps` esté
   condicionada al rol del usuario (`admin`/`videoanalista`/
   `videoanalista_reserva`, ver `canEdit` en `index.html`) y no solo a
   "estar logueado" — si cualquier cuenta logueada puede escribir, un rol
   "viewer" mal puesto también podría editar datos.
2. Que `users/{uid}/role` (de donde la app lee qué rol tenés) no sea
   editable desde el navegador por el usuario dueño de esa cuenta — los
   roles se asignan a mano por vos desde la consola; si ese nodo quedara
   escribible, alguien con una cuenta común podría asignarse `admin` a
   sí mismo con una request directa, sin pasar por la app.
No toqué nada de esto porque cambiar reglas de seguridad de un sistema en
producción no es algo que deba hacer sin que lo veas y lo confirmes vos.

**Perfil de posición GPS (COMPLETO, 2026-08-17):** ampliación de las
comparativas de GPS dentro de PLANTEL, inspirada en una app aparte del
usuario ("BL GPS Performance.html", con su propio Firebase — no relacionada
con Tigre) que pidió expresamente usar como referencia de diseño y de
catálogo de métricas, pero **sin conectarse a ese otro Firebase**: todo
sigue guardándose y calculándose con los datos propios de este proyecto.
- **Catálogo ampliado a 16 métricas** (antes 7): `GPS_COMPARE_METRICS`
  (cerca de la línea 3009) ahora define cada métrica como
  `{key, label, unit, get(p)}` en vez de solo `{key, label}` — el `get`
  permite métricas calculadas (HSR/min, Sprints+25/min, Acel/min, dividiendo
  por los minutos jugados) además de las crudas que ya traía el parser de
  PDF de Catapult desde Fase 6 (dist, mpm, m1821, m2125, m25, sprints,
  velmax, acc, dcc, accB2, rhie, totalPL) — **no hizo falta tocar el parser
  de PDF para nada de esto**, ya capturaba casi todo. `gpsCompareRowsHTML`
  se adaptó para recibir el jugador crudo (`getPlayer(item)`) y aplicarle
  `m.get(...)`, en vez de leer `p[key]` directo — así las comparativas que
  ya existían (entre fechas, entre jugadores) ganaron las métricas nuevas
  gratis, sin duplicar código.
- **Nueva comparativa "🧬 JUGADOR VS. PERFIL DE SU POSICIÓN"** dentro de
  cada categoría (mismo bloque colapsable que el resto): elegís una
  posición (sale de `plantelFutdetail[cat].posicion`, que ya carga
  futdetail) y opcionalmente un jugador de esa posición, y se arma una
  tabla con "Prom./Máx. de la posición" vs "Prom./Máx. del jugador" para
  cada una de las 16 métricas, con el mismo criterio visual que el resto
  de la app (mejor valor destacado en dorado, comparando promedio-con-
  promedio y máximo-con-máximo, nunca cruzado).
- **El "perfil de la posición" se calcula en vivo**, no se guarda nada
  nuevo en Firebase: junta todos los registros de jugadores de sesiones
  GPS de tipo **partido** (sin entrenamientos, mismo criterio que usa la
  app de referencia — "máximos y promedios de competencia") cuya posición
  en el plantel coincide, cruzando el alias GPS↔plantel que ya existía
  (`gpsAliasedName`) para que un typo de Catapult no deje a nadie afuera.
  A propósito **no hay pantalla de configuración manual de bandas** — en la
  app de referencia eso es para las zonas de velocidad del sistema GPS
  (18-21, 21-25, +25 km/h), no un benchmark por posición; el perfil real
  por posición ahí también sale calculado, no tipeado a mano.
- La sección solo aparece si la categoría tiene al menos una posición
  cargada en el plantel (si no, no se muestra, no rompe nada) y solo si ya
  hay 2+ sesiones GPS cargadas (mismo gate que las otras comparativas de
  ese bloque).
- Probado con datos falsos inyectados por consola (sin escribir nada en
  Firebase) para confirmar que el cálculo de promedio/máximo y el
  resaltado en dorado dan los números correctos antes de dar esto por
  cerrado.
- **Quedó afuera a propósito** (para no sobrecargar este primer corte): el
  gráfico de tendencia tipo sparkline que tiene la app de referencia por
  cada métrica. Si el resto se usa y gusta, se puede sumar después.

**Carga histórica de GPS 4TA + arreglos del parser (COMPLETO, 2026-08-18):**
se migraron a Firebase los datos reales de Catapult que ya estaban cargados
en "BL GPS Performance.html" (32 jugadores, partidos de competencia de 4ta),
más el informe del partido vs Racing (fecha 21) que se subió a Drive.
- **Bug de Firebase encontrado y corregido por el usuario:** las reglas de
  seguridad de Realtime Database no tenían ninguna entrada para `"gps"`
  (sí para `stats`/`plantel`/`rendimiento`/`reserva`/`users`) — quedó
  afuera cuando se armó Fase 6 y nadie lo notó porque nunca se había
  intentado escribir ahí desde una cuenta real hasta ahora. Sin esa
  entrada, Firebase deniega todo por defecto: ni admin podía guardar una
  sesión GPS. Yo detecté el problema probando escrituras mínimas (`db.ref
  ('gps/__test').set(...)`, comparando contra `stats`/`plantel` que sí
  andaban) pero **no toqué las reglas** — eso lo hizo el usuario en la
  consola de Firebase, agregando a `"gps"` el mismo criterio de
  `.read`/`.write` que ya tenía `"plantel"`/`"rendimiento"`.
- **32 jugadores → 13 fechas de partido (F1, F2, F6, F7, F8, F10-F17)**
  extraídos del `const PLAYERS = {...}` embebido en el HTML de la otra app
  (es JSON real, con métricas ya separadas en `training`/`match`). Se
  cruzaron los rivales de cada fecha contra `RIVALS` (el fixture propio de
  4ta) para confirmar que es la misma data real del equipo, no de otro
  lado.
  - **Fechas sin calendario real:** BL solo guarda "FECHA N", no fecha de
    calendario. Se cruzó contra los PDF ya subidos a Drive (que sí traen
    fecha) y se confirmó que el equipo jugó exactamente cada 7 días entre
    F5 (11/4) y F12 (30/5) — eso da fecha exacta para F6/F7/F8 (quedan
    *entre* dos anclas reales) y una estimación razonable para F1/F2
    (extrapolando hacia atrás). Para F13-F17 no hay ancla real después de
    F12 hasta Racing (F21, 13/8) y la cuenta no cierra prolija (indica un
    parate a mitad de camino que no se puede reconstruir a ciegas) — a
    pedido del usuario se cargaron igual con la misma estimación semanal,
    marcadas `"(fecha estimada)"` en el nombre de la sesión para poder
    corregirlas el día que aparezca la fecha real.
  - **8 nombres de BL sin match directo al plantel** (van a aparecer como
    huérfanos para vincular a mano, mismo mecanismo de siempre): la
    mayoría son typos evidentes (`Alan Luengo`→`Luongo`, `Yair Hillaret`→
    `Hillairet`, etc.); **dos quedaron sin resolver a propósito**
    (`Josue Rojas` y `Cristian Lezcano` no tienen un apellido claro en el
    plantel actual — no se inventó el vínculo).
- **Partido vs Racing:** se bajó el PDF de Drive y se pasó por
  `extractGpsDataFromPdf` (el parser real de la app, no un script aparte),
  lo que destapó dos bugs reales del parser con este informe puntual
  (`index.html`, cerca de la línea 5973 y 6100):
  1. **`gpsFindSummaryPage` exigía ver la palabra "Position" en la página**
     para aceptarla como la página de datos — este informe no trae columna
     de posición y se descartaba entero aunque tuviera 14 filas de jugador
     válidas. Ahora también alcanza con "Datos Generales".
  2. **Duración en formato "01:39:30" (h:mm:ss)** en vez de minutos
     decimales: el separador de dígitos pegados a texto (pensado para
     casos como "Izquierdo109") la partía en 3 números sueltos (1, 39, 30),
     corriendo mal la asignación de columnas de toda la fila. Ahora
     `gpsNumsWithX` reconoce el patrón `h:mm:ss` y lo convierte a un solo
     valor en minutos antes de repartir columnas.
  - Con esos dos arreglos, el mapeo por nombre de encabezado (`gpsBuildFieldMap`)
    igual no reconoció bien "Dist"/"Mts x Min"/"Vel Max"/"Acc"/"Dcc" en este
    informe puntual (encabezados envueltos de forma distinta a los 19 PDF
    ya calibrados) — en vez de tocar esa lógica general (riesgo de romper
    los PDF que ya andan bien), se reconstruyeron esas 5 columnas a mano
    para esta sesión usando el orden de columnas ya confirmado cruzando
    dos jugadores contra el texto crudo del PDF, sin cambiar código del
    parser para esa parte.
- **Bug de fondo encontrado en `gpsAliasedName` (arreglado):** la
  vinculación automática por nombre en otro orden ("Agustin Luna" de
  Catapult == "Luna Agustin" del plantel) solo se usaba para decidir si
  avisar de "huérfano" (`gpsOrphanNames`) — las comparativas individuales
  (comparar fechas, perfil de posición) seguían comparando el nombre crudo
  tal cual contra el jugador elegido y no encontraban nada para ningún
  jugador con el nombre en orden distinto al del plantel. Esto ya afectaba
  a cualquier PDF cargado antes, no es nuevo de esta carga — simplemente
  nunca se había notado porque no había casos de nombre en orden distinto
  hasta ahora. `gpsAliasedName` ahora prueba el mismo match por palabras
  ordenadas alfabéticamente antes de rendirse, así el nombre canónico del
  plantel se usa en forma consistente en todos lados.
- Verificado en la app real (con la carga ya en Firebase, sin datos de
  prueba): "Perfil de posición" para Lateral derecho (DEF) da promedios y
  máximos con sentido, y comparar a Luna Agustín contra su posición ya
  muestra sus propios números en vez de "—".

**Fechas de F1-F17 confirmadas y huérfanos identificados (2026-08-18):**
el usuario acercó el fixture oficial 2026 de la LPF (PDF) y el reglamento del
torneo. Cruzando el fixture contra las 10 sesiones que habían quedado
marcadas "(fecha estimada)" (F1, F2, F6, F7, F8, F13-F17): **las 10 dieron
exactas** — ni un día de diferencia con lo estimado por interpolación
semanal. Se sacó la etiqueta "(fecha estimada)" del nombre de esas 10
sesiones en Firebase, ya no hace falta revisarlas.
- El reglamento también confirma que 4ta juega 90 minutos por partido —
  coincide con la duración real que traían los PDF de Catapult, sin
  sorpresas.
- Sobre los dos huérfanos sin resolver (Josue Rojas / Cristian Lezcano): el
  usuario confirmó que son jugadores reales y distintos de "Rojas Elías" /
  "Lezcano Alan" — sus nombres completos son **Josué Elías Rojas** y
  **Cristian Lionel Lezcano**. Verificado que hoy no figuran en
  `plantelFutdetail['4TA']` (el scrapeo automático de futdetail) — por eso
  la pantalla de "vincular" no los puede ofrecer todavía, no es un bug.
  Quedan guardados en `gps/sessions` con su nombre tal cual vino de BL
  ("Cristian Lezcano" / "Josue Rojas"); en cuanto el plantel los incluya, se
  podrán vincular como cualquier otro huérfano.

**Rediseño de PLANTEL al estilo BL GPS Performance (COMPLETO, 2026-08-18):**
a pedido expreso del usuario ("la idea es hacerlo lo mas parecido o
exactamente igual al index... de BL GPS Performance"), se llevó TODA la
pestaña PLANTEL (no solo GPS) a la estructura/funcionalidad de esa app de
referencia — manteniendo siempre el tema oscuro/dorado propio (nunca el
fondo claro/azul de BL). Dado el tamaño (el módulo "Perfil" de BL solo ya
tiene miles de líneas), se dividió en 5 fases con checkpoint entre cada una,
**todas completas**:
1. Sparkline de tendencia en "Perfil de posición" — **COMPLETA**.
2. "Por fecha" — comparar jugadores de una posición por métrica y fecha
   (bandas +85/60-84/-60 min) — **COMPLETA**.
3. "Informe de partido" — resumen visual de un partido, todo el equipo
   (KPIs + gráficos Chart.js) — **COMPLETA**.
4. Config de métricas (reordenar/ocultar/renombrar) — **COMPLETA** (bandas
   quedaron afuera: nuestras zonas de Catapult son fijas, ver Fase 4).
5. Reorganizar PLANTEL al estilo "Jugadores" de BL — **COMPLETA** (ver
   abajo).

**Fase 1 — Sparkline de tendencia (COMPLETA, 2026-08-18):** dentro de
"🧬 Jugador vs. perfil de su posición" (PLANTEL → GPS), debajo de la tabla
ahora se arma una grilla "📈 EVOLUCIÓN POR FECHA" con un mini-gráfico SVG
propio por cada una de las 16 métricas (sin librerías externas, mismo
patrón visual que BL: área rellena + línea de promedio punteada + puntos
con tooltip al pasar el mouse), pintado con los colores de esta app
(`var(--gold2)`) en vez del azul de BL.
- Si hay un jugador elegido, la evolución es SU propio valor por fecha; si
  no hay jugador (solo posición), es el promedio de todos los que jugaron
  esa posición en cada fecha — mismo criterio que el comportamiento por
  defecto de BL.
- El tooltip de cada punto muestra fecha, rival y valor
  (`gpsRivalLabel(cat, fecha)`, cruzando `RIVALS` para 4TA-9NA o
  `rivalData` para RESERVA — mismo patrón que ya usa
  `renderCompararFechas`).
- Se necesitó separar `gpsPosicionRecords`/`gpsJugadorPartidoRecords` (que
  ya existían, devuelven solo el jugador) de dos nuevas
  `...ConSesion` (devuelven `{session, player}`) para poder agrupar por
  fecha y ordenar cronológicamente — las versiones viejas ahora son un
  simple `.map(r=>r.player)` de las nuevas, sin duplicar lógica ni romper
  a quien ya las usaba.
- Probado en la app real (con los datos ya cargados de 4ta) en los dos
  modos — con Luna Agustín elegido y solo con la posición — sin errores de
  consola ni valores `NaN`.

**Reorganización de RENDIMIENTO en GENERAL y por categoría (COMPLETA,
2026-08-18):** a pedido del usuario, se sacó "Forma reciente (últimos 5)"
del todo y se fusionaron "Local vs Visitante" e "Índice de rendimiento"
dentro de la tabla "Rendimiento por bloque de fechas" (sin su propio
título, solo los datos) — antes eran 3 secciones aparte y LVV/índice se
calculaban sobre toda la temporada; ahora se calculan sobre el ÚLTIMO
bloque jugado (el mismo que la tabla ya resalta en dorado), así que
cambian solos al mover el slider de tamaño de bloque en vez de quedar
fijos en "últimos 5".
- **GENERAL:** la sección pasó a llamarse "RENDIMIENTO GENERAL"; el
  índice ahora es una sola fila "TOTAL" combinando las 6 categorías (antes
  eran 6 filas, una por categoría) y LVV es un solo combinado de las 6 en
  vez de 6 tarjetas separadas. Se sacó también la sección "CITACIONES" de
  GENERAL (a pedido — "eso afuera también"). No se borró la funcionalidad
  (`buildPDFSection`/`renderChecklist`/`generarPDF`, la planilla de
  citaciones con firma), solo el punto de entrada en la pantalla — quedó
  sin usar por ahora, disponible si se decide dónde ponerla después.
- **Por categoría:** la sección pasó a llamarse solo "RENDIMIENTO" y el
  orden de las secciones dentro de RESULTADOS quedó: Resultados →
  Rendimiento → Comparar fechas → Goleadores → Tabla de posiciones (antes
  Forma/LVV/Índice iba justo después de Resultados y el bloque de fechas
  estaba más abajo, después de Comparar fechas — ahora están fusionados en
  un solo lugar). RESERVA sigue mostrando solo la tabla de bloques (sin
  slider, sin LVV/índice) — no tenía Forma/LVV/Índice antes tampoco, no es
  un cambio nuevo para esa categoría.
- Las 4 funciones viejas (`buildFormaHTML`, `buildLVVHTML`,
  `buildIndiceRowsHTML`, `buildRendimientoStatsHTML`) se borraron —
  quedaban sin ningún llamador después del cambio, mismo criterio que el
  módulo GPS viejo en Fase 7 (no dejar código muerto). Las reemplazan
  `buildLVVTotalHTML`, `buildIndiceTotalRowHTML` y
  `buildRendimientoGeneralHTML`. `calcBloqueFilas` ahora también guarda
  `from`/`to` de cada bloque (antes solo el label) — hacía falta para saber
  el rango de fechas exacto del último bloque jugado.
- Probado en la app real: GENERAL con el índice/LVV combinados, 4TA con su
  propio total, RESERVA sin romperse, y el slider de bloque cambiando el
  LVV/índice en vivo (probado moviendo a bloques de 7).

**Fases 2 y 3 del rediseño de PLANTEL — "Por fecha" e "Informe de partido"
(COMPLETAS, 2026-08-18):** se hicieron las dos juntas, a pedido del usuario
("hacelo tal cual lo hace BL"). Antes de codear se leyó a fondo cómo BL
construye esas vistas para reproducir la semántica exacta, no asumirla.
Descubrimiento clave: las "bandas" +85/60-84/-60 min de BL agrupan a los
jugadores de una posición por los minutos que jugó CADA UNO y toman el
máximo de cada grupo (`getBand`/`integrateFecha` en BL) — eso SÍ se puede
reproducir con nuestros datos porque cada registro por jugador ya trae los
minutos. Las dos vistas son solo lectura (no guardan nada), reusan
`GPS_COMPARE_METRICS`, viven dentro de PLANTEL → GPS como secciones
colapsables nuevas, y usan Chart.js (que ya estaba cargado, con el helper
`killChart`).

- **📅 POR FECHA** (`gpsRenderPorFecha` y helpers): posición propia
  (dropdown) + chips de las 16 métricas + pills de fechas (Todas / cada
  partido con su rival). Arranca en "Distancia" (`GPS_DEFAULT_MET_IDX`),
  no en "Minutos" (que sería raro porque las bandas ya son por minutos).
  - 1 fecha elegida → tarjeta con "% del máx histórico" y "Ref. histórica"
    de la posición para la métrica, grilla con TODAS las métricas (mejor
    valor de esa fecha) y desglose de la métrica elegida por banda de
    minutos (+85/60-84/-60, barras animadas con % vs promedio histórico) —
    calcado de `renderOneFecha` de BL.
  - Varias fechas → tabla métrica × (fecha × 3 bandas), como
    `renderMultiFechas` de BL. Default "Todas" (igual que BL); con 14
    fechas la tabla es ancha pero scrollea dentro de `.table-wrap`.
  - `gpsBandasPosFecha` reproduce gt85/r6084/lt60 al vuelo; `gpsHistPos`
    da máx/prom histórico (mejor de cada fecha, solo 60+ min, igual que el
    "summary" de BL).
- **📋 INFORME DE PARTIDO** (`gpsRenderInforme` y helpers): la "foto" de un
  partido para todo el equipo — calcado de `renderInformePartido` de BL.
  Selector de partido (fecha + rival, más reciente primero) + filtro de
  posición + filtro de minutos (Todos/+85/60-84/-60). Tarjetas KPI con
  promedio y rango mín-máx del equipo (calculados solo con los de 60+ min,
  con aviso de a cuántos dejó afuera, igual que BL). Debajo, 7 gráficos de
  barras por jugador (Chart.js, ordenados de mayor a menor por su métrica,
  con línea opcional en eje secundario): Distancia+mts/min, 18-21+mts/min,
  HSR+Sprints+HSR/min, Top speed+sprints, Acel+Desac, Player Load (solo si
  el PDF lo trae — los datos de 4ta que vienen de BL no tienen PL, así que
  hoy no aparece), y Minutos. Se usaron los colores de serie de BL (leen
  bien sobre fondo oscuro) con grilla/ejes en el tono de la app.
- **Detalle técnico — canvas + secciones colapsadas:** los gráficos son
  `<canvas>`; si se dibujan con la sección colapsada quedan a tamaño 0.
  `toggleSeccion` ahora detecta cuando se ABRE la sección del informe
  (`gps-informe-<cat>`) y re-renderiza para que Chart.js los mida bien.
- **Etiquetas de valor siempre visibles (agregadas 2026-08-18 a pedido):**
  `gpsBarLabelsPlugin` porta el plugin `ipValueLabels` de BL pero para fondo
  oscuro (caja `rgba(5,8,15,.85)` + texto claro en vez de caja blanca +
  texto negro). Dibuja el valor sobre cada barra (vertical cuando hay muchas
  barras finas, >8) y sobre cada punto de la línea. Formato con
  `gpsFmtBarNum` (entero con separador de miles; decimal si el valor es
  chico, ej. mts/min o vel máx). Se sumó `layout.padding.top:26` para que
  las etiquetas de la línea no se corten arriba. El tooltip de Chart.js
  (hover → nombre completo + valor) sigue estando además.
- Probado en la app real con los datos de 4ta: Por fecha (tabla multi y
  tarjeta de 1 fecha con bandas y % histórico), Informe (KPIs, 6 gráficos
  con 13-14 barras según el partido, filtros de posición y minutos, cambio
  de fecha) — sin errores de consola ni NaN. Los "GPS save error:
  PERMISSION_DENIED" que aparecen en la consola son historia retenida del
  primer intento de carga masiva (antes de arreglar las reglas), no de este
  código, que es solo lectura.

**Fase 4 — Configuración de métricas (COMPLETA, 2026-08-18):** botón
"⚙️ Configurar métricas" (solo `canEdit`) arriba de las comparativas de GPS,
abre un modal para **reordenar arrastrando + mostrar/ocultar + renombrar** las
16 métricas. Se guarda en Firebase bajo `stats/gpsMetricCfg`
(`{order:[keys], hidden:[keys], labels:{key:"..."}}`) — compartido como el
resto de `stats`, se carga en los 3 puntos donde ya se cargaba
`aliasJugadoresGps` (carga inicial, listener en vivo, listener público) y se
suma al payload de `saveData` + tiene su `guardarGpsMetricCfg()` targeted,
mismo patrón que `aliasJugadoresGps`.
- **`gpsVisibleMetrics()`** es la lista efectiva (orden aplicado, ocultas
  sacadas, label renombrada — devuelve copias con `{...m, label}` que
  conservan la función `get`). Reemplazó a `GPS_COMPARE_METRICS.map(...)` en
  las 4 vistas de "lista de métricas": comparativas
  (`gpsCompareRowsHTML`), perfil de posición, evolución (`gpsEvolucionHTML`)
  y "por fecha" (chips + grilla + tabla multi). **NO** toca los KPIs ni los
  gráficos del Informe de partido — esos usan métricas fijas por diseño
  (`GPS_IP_M`, master list), así que ocultar/renombrar no los cambia (el
  gráfico "Minutos jugados" sigue estando aunque ocultes "Minutos" de la
  lista).
- **Por fecha pasó de guardar índice (`metIdx`) a clave (`metKey`)** — si no,
  reordenar u ocultar métricas movía la selección. Default sigue siendo
  Distancia (`'dist'`); si la métrica elegida se oculta, cae a la primera
  visible.
- **Bandas quedaron afuera a propósito:** BL configura los umbrales de las
  zonas de velocidad (18-21/21-25/+25 km/h) porque cada GPS usa zonas
  distintas, pero nuestros datos vienen de Catapult con esas zonas ya fijas
  y pre-sumadas (columnas `m1821`/`m2125`/`m25`) — no tenemos el trazo crudo
  de velocidad, así que cambiar un umbral no re-agruparía nada. Lo único que
  haría es renombrar etiquetas, que ya lo cubre el renombre de métricas.
- Probado con datos falsos inyectados por consola (sin login, no persiste):
  `gpsVisibleMetrics` aplica orden/ocultar/renombrar y conserva `get`; el
  modal abre 16 filas con drag/checkbox/input; guardar arma el cfg correcto;
  perfil de posición pasa a 15 filas con "dist" renombrado y primero; por
  fecha a 15 chips; el informe sigue con 8 KPIs y 7 gráficos intactos. Sin
  errores de consola.

**Fase 5 — PLANTEL al estilo "Jugadores" de BL (COMPLETA, 2026-08-18):**
`renderPlantelTab` ahora arranca con una sección "👥 JUGADORES"
(`renderJugadoresView`) de dos columnas — a la izquierda, lista de jugadores
agrupados por posición con buscador (`jugadoresListHTML`/`jugadorFiltrar`);
a la derecha, el perfil individual (`renderJugadorPerfil`) al hacer click
(`selJugador`, estado en `gpsJugadorSel[cat]`). Debajo, todo lo que ya estaba
quedó como secciones colapsables (a pedido del usuario, "Jugadores arriba, lo
demás abajo"): la tabla de roster se envolvió en un colapsable "📋 TABLA DE
PLANTEL" (se le sacó su header interno "PLANTEL" para no duplicar), y siguen
tarjetas/lesiones y toda la sección GPS de equipo.
- **El perfil individual combina** (decisión del usuario "Resumen + Evolución
  GPS", sin las sub-pestañas de microciclos de BL que no aplican a nuestros
  datos): *hero* con avatar de iniciales coloreado por línea
  (`jugPosColor`: ARQ dorado / DEF azul / VOL verde / DEL rojo) + máximos GPS
  (dist/vel/+25/sprints) + botón "📄 Exportar ficha" (reusa
  `exportFichaJugador`); tarjetas/lesiones del jugador; tiles de estadísticas
  de temporada de futdetail (convocatorias, titular, minutos, goles,
  asistencias, amarillas, rojas); tabla máx/prom de GPS por métrica
  (respeta `gpsVisibleMetrics`, o sea la config de Fase 4); y la grilla de
  evolución (`gpsEvolucionHTML`, reusada — la misma de Fase 1).
- **`buildMergedRoster(cat)`** extrae el cruce roster+stats (antes vivía
  inline en `renderRosterCat`) para compartirlo entre la lista, el perfil y
  la tabla de roster.
- Layout responsive: `.jug-layout` es grid de 2 columnas en desktop y pasa a
  1 columna en móvil (regla agregada al media query existente).
- Probado en la app real (roster público de 4ta, 38 jugadores, 15 grupos de
  posición) + GPS falso inyectado: la lista agrupa/filtra/resalta bien, el
  perfil arma hero+máximos+stats+tabla GPS (16 métricas)+16 sparklines de
  evolución sin NaN, el buscador filtra por nombre ocultando grupos vacíos,
  la tabla de roster colapsable sigue con sus 38 filas y "comparar
  jugadores", y el layout colapsa a 1 columna en móvil. Sin errores de
  consola.

**Bug de local/visitante corregido + "Resumen por bloque" (COMPLETO, 2026-08-18):**
el usuario notó que en GENERAL, el último bloque daba 8 pts de local y 0 de
visitante, cuando era 6 y 2. Causa: `buildLVVTotalHTML` usaba la condición
cruda de `RIVALS` (que es la de 4ta/5ta/6ta) para las 6 categorías, pero las
menores (7ma/8va/9na) juegan **siempre al revés** — el fixture oficial de la
LPF las pone en la columna espejo (cuando las mayores son local, las menores
son visitante). El usuario lo cruzó contra liga/futdetail/sabadogol y
confirmó el patrón para todo el torneo.
- **`condicionCat(cat, fecha)`** devuelve la condición correcta: mayores =
  `RIVALS[f].c`, menores (`CATS_MENORES` = 7MA/8VA/9NA) = invertida. Corrige
  tanto el LVV combinado de GENERAL como las vistas por categoría de las
  menores (que también estaban invertidas). **Ojo:** la condición cruda de
  `RIVALS` sigue usándose en otros lados (badge de la tabla de RESULTADOS,
  selector de fecha del PDF de citaciones) — ahí muestra la condición de las
  mayores; el usuario solo pidió arreglar el LVV, no se tocó el resto.
- **`lvvSplit(cats, from, to)`** reparte los partidos en local/visitante con
  esa condición correcta, devolviendo pts + G/E/P + goles de cada lado.
- **Se reemplazó** el viejo "Local vs Visitante" (tarjetas, solo último
  bloque) + "Índice de rendimiento" (con columnas MÉTRICAS/bar e ÍNDICE
  compuesto 0-100) por una sola tabla **"RESUMEN POR BLOQUE"**
  (`buildResumenPorBloqueHTML`): una fila por bloque (+ TOTAL) con Pts/PJ,
  % victorias, GF/PJ, GC/PJ, y los puntos de Local y Visitante (con G-E-P
  abajo en chico). A pedido del usuario se sacaron "métricas" e "índice"; se
  sumaron GF/PJ y GC/PJ. Cambia con el slider de tamaño de bloque como el
  resto. RESERVA sigue mostrando solo la tabla de bloques (no usa esto).
- Se borraron `buildLVVTotalHTML` y `buildIndiceTotalRowHTML` (sin
  llamadores) y el CSS muerto asociado (`.lvv-*`, `.indice-*`).
- Verificado con datos reales (públicos): último bloque F21-F25 da 6 pts
  local (2-0-1) / 2 visit (0-2-1); 7MA F21 (3-3) cuenta como visitante, 4TA
  F21 (2-1) como local; el TOTAL de temporada da 93 local / 61 visit (suma
  154, coincide con el total); slider y RESERVA sin romperse; sin errores de
  consola.

**Pendiente / a futuro:**
- **Citaciones** (sacada de GENERAL): el usuario dijo que la retomamos
  después de terminar el rediseño de PLANTEL. El código sigue ahí sin usar
  (`buildPDFSection`/`renderChecklist`/`generarPDF`).
- Si se quiere, revisar si el badge de condición local/visitante de la tabla
  de RESULTADOS y el selector de citaciones deberían mostrar la condición
  correcta por categoría (hoy usan la cruda de RIVALS, o sea la de las
  mayores) — el usuario solo pidió arreglar el LVV por ahora.
- Si futdetail sigue sin traer a Josué Rojas / Cristian Lezcano dentro del
  plantel de 4ta, confirmar con el club si corresponde revisar la carga en
  futdetail (no es algo que se arregle desde acá).
- Si en algún momento aparece un PDF de partido con el mismo problema de
  encabezados que el de Racing (Dist/Mts x Min/Vel Max/Acc/Dcc sin
  reconocer), vale la pena revisar `gpsBuildFieldMap` en serio en vez de
  reconstruir a mano — por ahora fue un caso único.
- Decidir si conviene recuperar CARGA (gimnasio) y/o SEMANA — ver arriba.
- Ya se encontró y arregló el hueco de `"gps"` en las reglas de Firebase;
  igual vale la pena que el usuario chequee alguna vez si hay otro nodo con
  el mismo problema (algo agregado a la app sin agregar su regla).
- Si te interesa respaldar también plantel/rendimiento/gps, crear el
  usuario "viewer" dedicado y cargar los secrets (ver arriba).
