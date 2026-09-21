# Resumen: sincronización de esfuerzos en video

> **Estado: COMPLETO (2026-09-19), ampliado el 2026-09-20 con la calibración
> por hora real del stream.** Este archivo es un resumen histórico.
> La descripción vigente y detallada vive en `CLAUDE.md` (bloque
> "Esfuerzos en video") — si hay una diferencia, gana `CLAUDE.md`.

## Objetivo
En la solapa GPS, cada esfuerzo de un jugador (sprint ≥25 km/h o carrera
21-25 km/h) abre el video del partido en el momento exacto. Para eso hay que
saber en qué segundo del video arranca el 1T y el 2T de cada partido.

## Cómo funciona (implementado)
- Fórmula: `segundo_video = kickoff(1T o 2T) + (inicio_esfuerzo − inicio_periodo)`,
  con `gps/videoSync/{cat}/F{n} = {kickoff1, kickoff2}` en Firebase.
- **Calibración automática, vía 1 — hora real del stream (2026-09-20):** si el
  video de YouTube fue una transmisión en vivo, YouTube guarda a qué hora real
  arrancó (`release_timestamp` en yt-dlp) y Catapult a qué hora real arrancó
  cada tiempo, así que el kickoff sale de una resta, sin mirar ningún cuadro
  (`detectar_kickoffs_metadata`). Es más barato y más preciso que el OCR
  —cancela los errores de marcado de período— y se auto-calibra contra las
  fechas ya calibradas. Valida tres cosas antes de guardar (arranque antes del
  saque inicial, duración que cubra los dos tiempos, y un cuadro de control en
  el 2T); si algo no cierra, sigue por OCR.
- **Calibración automática, vía 2 — el cartel** en `scripts/scrape_tablas.py`:
  lee el cartel del video con OCR. Reconoce los dos formatos — VEO (reciente, "1T/2T" explícito,
  `detectar_kickoffs_video`) y LPF (viejo, reloj corrido, `detectar_kickoffs_lpf`
  con clustering RANSAC). `detectar_kickoffs_auto` clasifica y despacha.
- **Partidos de visitante** (archivo subido, sin hora real y muchas veces sin
  cartel) → calibración manual con el formulario del modo VIDEO, que ahora pide
  un solo dato: el botón "▶ BUSCARLO EN EL VIDEO" abre el reproductor y un clic
  en "📍 ACÁ ARRANCA EL 1T" copia el segundo exacto; el 2T lo calcula solo con
  el hueco entre tiempos que da Catapult. El detector no reintenta una fecha tras 3 fallos
  con el mismo link (`gps/videoSyncFallos`).
- **Recorte a los tiempos del partido (2026-09-19):** los esfuerzos se filtran
  a las ventanas "Primer/Segundo tiempo" (en el scraper, en la app y con una
  limpieza única del `tablas.json`), así no entra calentamiento u otra sesión
  del día que caía mal en el video.
- **Se corre solo en la PC del club** cada 4hs (tarea programada), con el
  archivo de credenciales de Firebase ya creado. El video se frena solo al
  terminar el esfuerzo; hay pre-roll de 4s y botones ◀5s/5s▶.

## Cobertura
- Las 6 juveniles usan chalecos (confirmado en OpenField el 2026-09-20), así
  que se sincronizan 4TA a 9NA, con manejo de errores por fecha.
- Fechas de local (transmisión propia): automáticas, por hora real del stream o
  por cartel. Fechas de visitante: a mano, de un clic.
- Para medir cuánto cubre cada vía sobre los datos reales:
  `python scripts/medir_video_sync.py` (solo lee, pide las credenciales de
  Firebase por teclado si no están en el entorno).
