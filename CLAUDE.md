# SEGUIMIENTO TIGRE JUVENILES 2026

App de una sola página (`index.html`) para seguir las inferiores de Tigre:
Reserva y 4ta a 9na. Se publica con GitHub Pages desde `main`.

Este archivo tiene SOLO lo vigente. El detalle histórico (cómo y por qué se
hizo cada cosa) está en `HISTORIAL.md`: consultalo cuando necesites el
contexto de una función puntual, pero si contradice este archivo o el
código, manda el código.

## Reglas de trabajo

- Responder en español (Argentina), de "vos", simple y sin jerga sin explicar.
- Antes de tocar código: mostrar el plan y pedir confirmación.
- Cambios chicos y quirúrgicos (Edit, nunca reescribir `index.html` entero).
- No borrar ni "limpiar" funciones que no tienen que ver con el pedido.
- Después de cada cambio: chequear sintaxis y pasar el checklist de abajo.
- Cerrar cada cambio con una línea de "cómo probarlo".

## Datos

**Firebase Realtime Database** (`tigre-2026`, SDK compat 9.23.0, NO Firestore).
Todo pide login desde el 2026-08-27 (muro de login).
- `stats`: resultados, goleadores, citaciones (`matchData`), informes COMET
  (`partidos`), plantel, alias de jugadores.
- `gps`: sesiones, `videoSync`, `reservaManual`, `catapultReservaAuth`.
- `users` / `profile_taken`: usuarios y roles.
- `citacionesImg`, `temporadas_cerradas`, `temporadaActiva`.

Ojo: Firebase devuelve arrays con huecos `null` cuando las fechas son
correlativas. Todo recorrido de `matchData`/`partidos`/`results` tiene que
saltear los `null`.

**`data/tablas.json`** (lo genera `scripts/scrape_tablas.py`):
- ligaprofesional.ar: tablas y fixture de 4ta a 9na.
- statfutbol.com.ar: resultados, jugadores, eventos por fecha, Reserva,
  alertas del rival.
- futdetail (con login): fixture, jugadores (acumulado, incluye amistosos),
  plantel con foto/edad/altura/peso/pie.
- BL GPS y Catapult OpenField (con login): GPS por partido.
- `data/catapult_efforts.json`: esfuerzos de sprint/HSR con hora real.

Fuentes que YA NO se usan: sabadogol y Paren la Pelota. No volver a agregarlas.

**Prioridad (por fecha, no por total de temporada):**
1. Lo cargado a mano (planilla, PDF de COMET, PDF de citación).
2. statfutbol.
3. LPF oficial.

## Automatización

- **PC del club** (tarea programada cada 4 hs,
  `Documents\futdetail_scraper\actualizar_liga.ps1`): corre el scraper con
  todas las credenciales y sube a Firebase y al repo. Es el único lugar que
  tiene las credenciales de Catapult: si la PC está apagada, no se actualiza.
- **GitHub Actions**:
  - `backup.yml`: backup diario de Firebase a `data/backups/`. Necesita los
    secrets `FIREBASE_BACKUP_EMAIL` / `FIREBASE_BACKUP_PASS`. Si falla, el
    motivo aparece como anotación del run.
  - `tablas.yml`: solo manual ("Run workflow"). No tiene creds de Catapult.
- El repo es PÚBLICO: no subir mails, contraseñas ni el nodo `users`.

## Roles

- `admin`: todo.
- `videoanalista_reserva` / `videoanalista_menores`: editan solo su grupo
  (`EDIT_SCOPES`).
- `cat_XXX` (DT/PF/AC de una categoría), `ea_mayores` / `ea_menores`: solo
  ven su grupo (`VIEW_SCOPES`).
- Coordinador, director y `viewer`: solo miran.

**Alta de cuentas (desde 2026-10-16):** la persona elige su perfil en "Crear
cuenta" y queda PENDIENTE (`users/uid/rolSolicitado` + `perfil`, sin `role`).
No ve nada hasta que el admin la aprueba en el panel 👥 (✓ asigna el rol, ✕
rechaza y libera el perfil). Solo el admin escribe `role`.

**Reglas de Firebase:** copia en `firebase.rules.json` (lo que manda es lo
pegado en la consola: Realtime Database → Reglas). Leer datos exige tener rol.
Si se cambian, actualizar los dos lados.

## Esfuerzos en video (sincronización)

`gps/videoSync/{cat}/{fecha}`: `tramos` [{desde, hasta, offset}] → segundo
del video = hora unix + offset (método por "ritmo", `scripts/sync_ritmo.py`,
no depende de la hora de arranque de Catapult ni de la del video). Si no hay
`tramos`, vale la fórmula vieja con `kickoff1/kickoff2`. Lo calibrado a mano
(`fuente: 'manual'`) manda y borra los tramos. Revisión sin guardar:
`scripts/revisar_sync_ritmo.py`.

## Ficha del jugador

`calcularFichaJugador` → `renderFichaCardHTML` (modal y Comparar) y
`exportFichaJugador` (PDF, mismos números). Muestra datos personales,
totales (convocado, jugó, titular, minutos, goles, asistencias, amarillas,
rojas) y la tabla fecha por fecha con estado (Titular / Entró / No ingresó /
Suplente / No citado / Sin citación / Revisar citación / Por jugar), minutos
y eventos, más las fechas en otras categorías.

## Checklist antes de dar un cambio por terminado

1. Sintaxis: extraer los `<script>` de `index.html` y correr `node --check`.
2. La app carga y loguea sin errores en la consola.
3. Abrir la ficha de un jugador de 4ta, uno de Reserva y uno que haya
   jugado en dos categorías.
4. Ver que la tabla general y los resultados de la categoría tocada no
   cambiaron si no tenían que cambiar.
5. Commit chico con mensaje claro de qué cambió y por qué.
