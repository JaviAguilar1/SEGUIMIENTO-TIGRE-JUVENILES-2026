---
name: firebase-tigre
description: >-
  Trabajar con el Firebase del proyecto SEGUIMIENTO-TIGRE-JUVENILES (la app
  index.html de seguimiento de las inferiores de Tigre). Usá esta skill SIEMPRE
  que toques algo que lea o escriba en Firebase en este proyecto: leer o guardar
  resultados, goleadores, links, plantel, tarjetas, lesiones o sesiones de GPS;
  agregar un nodo nuevo a la base; tocar el login, los roles o los permisos
  (canEdit/isAdmin); revisar o cambiar las reglas de seguridad; o trabajar con
  el backup en Python (backup_firebase.py). Activala aunque el usuario no diga
  la palabra "Firebase" — frases como "que se guarde en la nube", "no me guarda
  los datos", "quiero respaldar la temporada", "agregá un campo nuevo que
  persista", "por qué cualquiera puede editar", "sumá el login para tal cosa" o
  "se pisan los datos entre dos personas" caen todas acá. Esta app usa Realtime
  Database (NO Firestore) y el SDK compat 9.23.0; la skill trae el modelo de
  datos real y los patrones ya usados para no romper lo que anda.
---

# Firebase del proyecto Tigre

Esta app (`index.html`, una sola página) guarda TODA la temporada en **Firebase
Realtime Database**. No hay backend propio: el navegador habla directo con
Firebase. Por eso, cualquier cambio que toque datos hay que hacerlo respetando
los patrones que ya existen, o se corre el riesgo de pisar o perder información
real del club.

Antes de tocar código, seguí las reglas del `CLAUDE.md` del repo: responder en
español (Argentina, de "vos"), explicar los pasos simple (el usuario está
aprendiendo), y **mostrar el plan y pedir confirmación antes de aplicar
cambios**. Nunca cambies reglas de seguridad ni borres nodos sin confirmación
explícita.

## Lo que NO hay que confundir

- Es **Realtime Database**, no Firestore. No hay `collection()`, `doc()`,
  `getDocs()`, `where()`. Se usa `db.ref('ruta')` con `.set()`, `.push()`,
  `.update()`, `.remove()`, `.on('value')`, `.once('value')`.
- Es el **SDK compat 9.23.0** cargado por `<script>` desde gstatic (no módulos
  ES, no `import`). Existe un objeto global `firebase`. Se usa
  `firebase.database()`, `firebase.auth()`. No mezcles con la sintaxis modular
  v9 (`getDatabase`, `ref(db, ...)`, `onValue(...)`) — rompería todo.
- La `apiKey` que aparece en el código (`AIzaSyC...`) es **pública a propósito**
  (así funcionan las apps web de Firebase); no es un secreto ni un bug. Lo que
  protege los datos son las **reglas de seguridad** de la consola, no ocultar la
  key. No la borres ni la "escondas".

## Modelo de datos y patrones (leé esto antes de escribir código)

El detalle completo de nodos, roles y funciones está en
`references/modelo-datos.md`. **Leelo antes de tocar cualquier lectura o
escritura** — tiene la estructura exacta de `stats`, `plantel`, `rendimiento`,
`gps`, `users`, y qué función usar en cada caso. Acá va lo esencial:

- **Cuatro nodos de datos**: `stats` (lectura **pública**, alimenta el modo
  COMPARTIR), y `plantel`, `rendimiento`, `gps` (requieren login). Más
  `users/{uid}/role` para los permisos.
- **Guardar en `stats`**: NO escribas a mano con `db.ref('stats').set(...)`.
  Usá la función `saveData()` que ya existe: arma el `payload` completo con todo
  el estado en memoria y lo guarda con **debounce** (espera con `saveTimeout`
  para no pegarle a Firebase en cada tecla). Si agregás un dato nuevo que tiene
  que persistir en `stats`, sumalo al `payload` de `saveData()` y a la lectura
  de `startPublicListener()` — en los dos lados, o se guarda pero no se lee (o
  al revés).
- **GPS**: `saveGpsSession()` / `deleteGpsSession()` escriben una sesión por ID
  (`gps/sessions/{id}`), NO todo el nodo de una. Esto es a propósito: evita que
  dos personas cargando a la vez se pisen. No vuelvas al patrón viejo de
  reescribir todo `gps` con un `.set({sessions:[...]})`.
- **Toda escritura va detrás de `canEdit`**: las funciones de guardado arrancan
  con `if(!fbReady||!db||!canEdit) return;`. Respetalo. Si agregás una escritura
  nueva, ponele el mismo candado, o un usuario "viewer" podría escribir desde la
  consola del navegador.
- **Lecturas en tiempo real con `.on('value')`**: los datos se sincronizan
  solos entre pestañas/usuarios. Si agregás un nodo nuevo que la app tiene que
  ver actualizado, sumale su listener (mirá `startPublicListener` /
  `setupGpsListener` como molde), y ojo con no re-renderizar encima de algo que
  el usuario está editando (existe la bandera `gpsPendingUpload` justo para eso).

## Auth y roles

Login por **email/contraseña** (`firebase.auth().signInWithEmailAndPassword`).
El rol se lee en vivo de `users/{uid}/role` dentro de `onAuthStateChanged`, y de
ahí salen `currentRole`, `isAdmin` y `canEdit`. Roles que pueden editar:
`admin`, `videoanalista`, `videoanalista_reserva`. `viewer` (y cualquier cosa
sin rol) solo mira. Hay roles por categoría tipo `cat_4TA`. Los roles se asignan
**a mano desde Firebase Console**, nunca desde la app.

Si el usuario pide "que tal persona pueda hacer tal cosa", casi siempre es tocar
`canEdit` / el chequeo de rol en la app, **no** las reglas de seguridad — pero
acordate de que la app y las reglas tienen que decir lo mismo: la app decide qué
se ve, las reglas son las que de verdad frenan una escritura maliciosa.

## Reglas de seguridad (mucho cuidado)

Las reglas viven en **Firebase Console → Realtime Database → Reglas**, NO en
este repo. Están marcadas como pendientes de revisar en el `CLAUDE.md`. Dos
riesgos concretos a confirmar/cerrar cuando el usuario lo pida:

1. Que escribir en `stats`/`plantel`/`rendimiento`/`gps` dependa del **rol**
   (`admin`/`videoanalista`/...), no solo de "estar logueado". Si alcanza con
   estar logueado, un `viewer` mal configurado podría editar.
2. Que `users/{uid}/role` **no** sea escribible por el dueño de esa cuenta desde
   el navegador — si no, cualquiera con una cuenta común podría hacerse `admin`
   con una request directa.

Nunca apliques cambios de reglas por tu cuenta: son un sistema en producción.
Proponé las reglas, explicá qué hace cada línea, y que el usuario las pegue y
confirme en la consola. Si necesitás la sintaxis exacta de las reglas de RTDB,
buscala en la doc oficial antes de escribirla de memoria.

## Backup en Python

`scripts/backup_firebase.py` respalda los datos a `data/backups/` una vez por
día (GitHub Actions, `.github/workflows/backup.yml`). Lee por **API REST**
(`{DB_URL}/{nodo}.json`), no por el SDK. `stats` se baja sin login; para
`plantel`/`rendimiento`/`gps` se loguea con `FIREBASE_BACKUP_EMAIL/PASS`
(GitHub Secrets) vía `identitytoolkit ... signInWithPassword`. Si querés que el
backup cubra esos tres nodos hace falta crear un usuario "viewer" dedicado en la
consola y cargar esos secrets. El mismo `apiKey` público de la app sirve para el
login REST.

## Checklist antes de dar por hecho un cambio de Firebase

- ¿Respeté compat 9.23.0 (`db.ref(...)`, `firebase.auth()`), sin sintaxis
  modular?
- Si es una escritura nueva: ¿está detrás de `canEdit`? ¿Va por la función
  correcta (`saveData` para `stats`, `saveGpsSession` para GPS)?
- Si es un dato nuevo que persiste: ¿lo sumé al `payload` **y** al listener de
  lectura?
- ¿Toqué reglas de seguridad? Si sí: NO las apliqué solo — se las mostré al
  usuario para que las confirme en la consola.
- ¿Probé o expliqué cómo se ve el efecto (login como admin, otra pestaña que
  recibe el cambio en vivo)?
