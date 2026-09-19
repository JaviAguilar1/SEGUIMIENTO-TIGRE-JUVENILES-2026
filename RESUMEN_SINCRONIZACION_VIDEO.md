# Resumen: sincronización de esfuerzos en video

> **Estado: COMPLETO (2026-09-19).** Este archivo es un resumen histórico.
> La descripción vigente y detallada vive en `CLAUDE.md` (bloque
> "Esfuerzos en video") — si hay una diferencia, gana `CLAUDE.md`.

## Objetivo
En la solapa GPS, cada esfuerzo de un jugador (sprint ≥25 km/h o carrera
21-25 km/h) abre el video del partido en el momento exacto. Para eso hay que
saber en qué segundo del video arranca el 1T y el 2T de cada partido.

## Cómo funciona (implementado)
- Fórmula: `segundo_video = kickoff(1T o 2T) + (inicio_esfuerzo − inicio_periodo)`,
  con `gps/videoSync/{cat}/F{n} = {kickoff1, kickoff2}` en Firebase.
- **Calibración automática** en `scripts/scrape_tablas.py`: lee el cartel del
  video con OCR. Reconoce los dos formatos — VEO (reciente, "1T/2T" explícito,
  `detectar_kickoffs_video`) y LPF (viejo, reloj corrido, `detectar_kickoffs_lpf`
  con clustering RANSAC). `detectar_kickoffs_auto` clasifica y despacha.
- **Partidos de visitante** (video sin cartel) → calibración manual con el
  formulario del modo VIDEO. El detector no reintenta una fecha tras 3 fallos
  con el mismo link (`gps/videoSyncFallos`).
- **Recorte a los tiempos del partido (2026-09-19):** los esfuerzos se filtran
  a las ventanas "Primer/Segundo tiempo" (en el scraper, en la app y con una
  limpieza única del `tablas.json`), así no entra calentamiento u otra sesión
  del día que caía mal en el video.
- **Se corre solo en la PC del club** cada 4hs (tarea programada), con el
  archivo de credenciales de Firebase ya creado. El video se frena solo al
  terminar el esfuerzo; hay pre-roll de 4s y botones ◀5s/5s▶.

## Cobertura
- GPS/Catapult solo existe en 4TA, 5TA y 6TA (los chalecos no se usan en
  7MA-9NA). Se sincronizan esas tres categorías, con manejo de errores por
  fecha.
- Fechas de local con cartel: calibradas automáticamente. Fechas de visitante:
  a mano cuando haga falta.
