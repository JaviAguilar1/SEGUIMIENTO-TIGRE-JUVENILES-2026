# Modelo de datos y patrones — Firebase del proyecto Tigre

Referencia detallada. La app es `index.html` (una sola página). Toda la
persistencia es **Realtime Database**. Los números de línea son orientativos
(el archivo cambia); ubicá las funciones por nombre con una búsqueda.

## Índice

- Configuración e inicialización
- Los cuatro nodos de datos (+ `users`)
- Cómo se GUARDA (write) cada cosa
- Cómo se LEE (listeners) cada cosa
- Auth y roles
- Reglas de seguridad (estado y riesgos)
- Backup por REST (Python)

## Configuración e inicialización

SDK **compat 9.23.0**, cargado por `<script>` desde gstatic:

```
firebase-app-compat.js
firebase-auth-compat.js
firebase-database-compat.js
```

Config (`FB_CONFIG`, ~línea 1491). `apiKey` pública a propósito:

```js
const FB_CONFIG = {
  apiKey:            "AIzaSyCw7zfTu06EfT9PNvwcUQq5yGZiy5AGDPE",
  authDomain:        "tigre-2026.firebaseapp.com",
  databaseURL:       "https://tigre-2026-default-rtdb.firebaseio.com",
  projectId:         "tigre-2026",
  storageBucket:     "tigre-2026.firebasestorage.app",
  messagingSenderId: "213836128045",
  appId:             "1:213836128045:web:6ea572a1090e118f4fbda4"
};
```

Init (~1748):

```js
if(!firebase.apps.length) firebase.initializeApp(FB_CONFIG);
db = firebase.database();
fbReady = true;
firebase.auth().onAuthStateChanged(user => { ... });
```

`db` es global. Todas las rutas se arman con `db.ref('...')`.

## Los cuatro nodos de datos (+ users)

| Nodo           | Lectura      | Escritura           | Qué contiene |
|----------------|--------------|---------------------|--------------|
| `stats`        | **pública**  | roles con `canEdit` | resultados, links, goleadores, plantel (futdetail), jugadores, matchData, gymData, rivalData, chequeoSemanal, aliasJugadores, aliasJugadoresGps, recordatoriosOmitidos |
| `plantel`      | requiere login | `canEdit`         | roster real de jugadores |
| `rendimiento`  | requiere login | `canEdit`         | tarjetas y lesiones por jugador |
| `gps`          | requiere login | `canEdit`         | sesiones de Catapult en `gps/sessions/{id}` |
| `users/{uid}/role` | login    | solo consola (a mano) | rol de cada usuario |

`stats` es de lectura pública **a propósito**: la vista COMPARTIR muestra
resultados/goleadores sin login (`startPublicListener`). Los otros tres nodos
devuelven 401 sin sesión (confirmado probando el REST). Un comentario viejo
cerca de `showLoginWall()` decía que los cuatro eran públicos — no es cierto,
solo `stats`.

### Sub-claves de `stats` (el `payload` de `saveData`)

`results`, `links`, `goleadores`, `jugadores`, `plantel`, `matchData`,
`gymData`, `rivalData`, `chequeoSemanal`, `aliasJugadores`, `aliasJugadoresGps`,
`recordatoriosOmitidos`. Cada uno indexado por categoría (`4TA`, `5TA`, `6TA`,
`7MA`, `8VA`, `9NA`, `RESERVA`, y aparte `RESERVA_S2`). `results[cat][fecha]` y
`links[cat][fecha]` se recorren por el fixture (`RIVALS` / `RIVALS_RESERVA` /
`RIVALS_RESERVA_S2`).

## Cómo se GUARDA cada cosa

**Regla de oro:** toda función de escritura arranca con
`if(!fbReady||!db||!canEdit) return;`. Copiá ese candado en cualquier escritura
nueva.

### `stats` → `saveData()` (~1855)

No escribas `db.ref('stats').set(...)` a mano. `saveData()`:

1. Chequea `canEdit`.
2. `clearTimeout(saveTimeout)` + `setTimeout(...)` → **debounce**, para no
   escribir en cada tecla.
3. Arma `payload` con TODO el estado en memoria (todas las sub-claves de
   arriba).
4. `db.ref('stats').set(payload)`.

Como reescribe `stats` entero, cualquier dato nuevo que quieras persistir ahí
**tenés que agregarlo al `payload`** o se pierde al próximo guardado.

### GPS → `saveGpsSession()` / `deleteGpsSession()` (~5650)

Por sesión, no todo el nodo:

```js
db.ref('gps/sessions/'+session.id).set(session)   // guardar/actualizar una
db.ref('gps/sessions/'+id).remove()               // borrar una
```

Antes se hacía `gps.set({sessions:[...]})` (reescribía todo, dos personas se
pisaban). Ya no: quedó por ID. `Object.values()` al leer funciona igual con el
formato viejo (array) o el nuevo (objeto), así que no hay que migrar nada.
Maneja errores de permisos mostrando un toast claro (regla de `/gps`).

### plantel / rendimiento

`plantel` y `rendimiento` tienen sus propios `db.ref('plantel')...` /
`db.ref('rendimiento')...` (tarjetas y lesiones vía `saveRendimiento()` ~4915).
Mismo candado `canEdit`.

## Cómo se LEE cada cosa (listeners en tiempo real)

Todo se sincroniza en vivo con `.on('value', ...)`. Los cambios de un usuario
aparecen solos en las otras pestañas/dispositivos.

- **`startPublicListener()` (~4504)**: `db.ref('stats').on('value', ...)` —
  corre para todos, con o sin login. Vuelca cada sub-clave del snapshot al
  estado en memoria (`results`, `links`, `goleadores`, ...). Si agregás un dato
  nuevo a `stats`, agregá acá su línea de lectura además de sumarlo al `payload`.
- **`onAuthStateChanged` (~1751)**: al loguearse, engancha
  `db.ref('users/'+uid+'/role').on('value', ...)` (rol en vivo) y otro
  `db.ref('stats').on('value', ...)`.
- **`setupGpsListener()` (~5675)**: `db.ref('gps/sessions').on('value', ...)` →
  `gpsSessions = Object.values(snap.val())`. Refresca la sección de PLANTEL si
  es lo que se está mirando, **salvo** que haya una carga a medio confirmar
  (bandera `gpsPendingUpload`) — para no borrar de pantalla algo que el usuario
  está por guardar.
- `.once('value')` se usa donde alcanza una lectura puntual (sin quedar
  escuchando).

**Trampa a evitar:** un `.on('value')` que re-renderiza toda la pantalla puede
pisar un formulario abierto. Antes de re-render, fijate si hay una edición en
curso (patrón `gpsPendingUpload`).

## Auth y roles

```js
firebase.auth().signInWithEmailAndPassword(email, pass)   // doLogin() ~1969
firebase.auth().signOut()                                  // doLogout() ~1984
firebase.auth().onAuthStateChanged(user => { ... })        // ~1751
```

Al loguear, se lee el rol en vivo:

```js
db.ref('users/'+user.uid+'/role').on('value', snap=>{
  currentRole = snap.val() || 'viewer';
  isAdmin     = currentRole === 'admin';
  canEdit     = ['admin','videoanalista','videoanalista_reserva'].includes(currentRole);
  catRole     = currentRole;   // roles por categoría tipo 'cat_4TA'
});
```

- Editan: `admin`, `videoanalista`, `videoanalista_reserva`.
- Solo miran: `viewer` y cualquier cuenta sin rol.
- Al salir, se resetea a `viewer` y la app queda en **modo vista** (no hay muro
  bloqueante; el sitio se ve igual, sin permisos de edición).
- Los roles se asignan **a mano en Firebase Console**. La app nunca escribe
  `users/{uid}/role`.

## Reglas de seguridad — estado y riesgos

Viven en **Firebase Console → Realtime Database → Reglas** (no en el repo).
Marcadas como pendientes de revisar. Lo único confirmado (probando el REST desde
afuera) es qué se puede **leer** sin login: solo `stats`. No se pudieron ver las
reglas reales. Al proponer o revisar reglas, cuidar:

1. **Escritura por rol, no por "logueado".** `stats`/`plantel`/`rendimiento`/
   `gps` deberían exigir rol editor, no solo sesión iniciada.
2. **`users/{uid}/role` no escribible por el dueño.** Si no, alguien se
   autoasigna `admin` con una request directa.

Nunca aplicar cambios de reglas sin que el usuario los confirme en la consola
(sistema en producción). Buscar la sintaxis exacta de reglas de RTDB en la doc
oficial antes de escribirla.

## Backup por REST (Python)

`scripts/backup_firebase.py` (+ `.github/workflows/backup.yml`, cron diario 6am
UTC). No usa el SDK; usa la **API REST**:

```py
DB_URL = "https://tigre-2026-default-rtdb.firebaseio.com"
fetch:  GET {DB_URL}/{nodo}.json           # + ?auth={idToken} si hace falta login
login:  POST https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={apiKey}
        body {email, password, returnSecureToken:true} -> idToken
```

- `stats` se baja sin login. `plantel`/`rendimiento`/`gps` necesitan
  `FIREBASE_BACKUP_EMAIL` / `FIREBASE_BACKUP_PASS` (GitHub Secrets). Sin esos
  secrets, el script respalda solo `stats` y no rompe (mismo patrón que
  `FUTDETAIL_USER/PASS` en `scrape_tablas.py`).
- Guarda `data/backups/backup-YYYY-MM-DD.json` y poda a los últimos 30
  (`BACKUPS_A_CONSERVAR`).
- El `apiKey` público de la app sirve para el login REST — no hace falta otro.
