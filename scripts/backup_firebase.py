#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backup diario de los datos de Firebase (resultados, goleadores, tarjetas,
lesiones, sesiones GPS, etc.) a un archivo JSON versionado en el repo.

Por que hace falta: toda la info de la temporada vive UNICAMENTE en
Firebase Realtime Database. Si alguien borra algo por error, o hay un
problema con la cuenta de Firebase, no hay ninguna copia de respaldo aparte
-- este script la crea sin intervencion manual.

Que respalda hoy, sin configurar nada: el nodo "stats" (resultados,
goleadores, links, rendimiento por bloque) es de lectura publica a
proposito -- la app lo lee sin login para que funcione el boton
"COMPARTIR" (vista publica, ver startPublicListener() en index.html).
Por eso este script lo puede pedir por HTTPS simple, sin credenciales.

Que falta para respaldar tambien plantel/rendimiento/gps (roster, tarjetas,
lesiones, sesiones GPS): esos tres nodos SI piden login (lo confirme
probando cada uno -- devuelven 401 sin sesion, a diferencia de "stats").
Si en Firebase Console creas un usuario dedicado para esto (rol "viewer"
alcanza, no hace falta que pueda editar) y cargas su email/password como
secrets de GitHub `FIREBASE_BACKUP_EMAIL` / `FIREBASE_BACKUP_PASS`, este
script se loguea solo (via la API REST de Firebase Auth, con el mismo
apiKey publico que ya usa la app) y los suma al backup. Sin esos secrets,
el script sigue andando igual y respalda nada mas que "stats" -- mismo
patron que ya usa scripts/scrape_tablas.py con FUTDETAIL_USER/PASS.

Corre automaticamente via GitHub Actions (ver .github/workflows/backup.yml).
Guarda un archivo por dia en data/backups/ y borra los mas viejos que
BACKUPS_A_CONSERVAR, para que el repo no crezca sin limite.
"""

import json
import os
import sys
import datetime
import urllib.request
import urllib.error

DB_URL = "https://tigre-2026-default-rtdb.firebaseio.com"
FB_API_KEY = "AIzaSyCw7zfTu06EfT9PNvwcUQq5yGZiy5AGDPE"  # publico, ver FB_CONFIG en index.html
NODO_PUBLICO = "stats"
NODOS_CON_LOGIN = ["plantel", "rendimiento", "gps"]
CARPETA_BACKUPS = os.path.join(os.path.dirname(__file__), "..", "data", "backups")
BACKUPS_A_CONSERVAR = 30


def fetch_nodo(nodo, id_token=None):
    url = f"{DB_URL}/{nodo}.json"
    if id_token:
        url += f"?auth={id_token}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def login(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FB_API_KEY}"
    body = json.dumps({"email": email, "password": password, "returnSecureToken": True}).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))["idToken"]


def main():
    os.makedirs(CARPETA_BACKUPS, exist_ok=True)

    backup = {"generado": datetime.datetime.now(datetime.timezone.utc).isoformat()}

    try:
        backup[NODO_PUBLICO] = fetch_nodo(NODO_PUBLICO)
    except Exception as e:  # noqa
        print(f"[ERROR] no se pudo leer '{NODO_PUBLICO}' (publico): {e}", file=sys.stderr)
        sys.exit(1)

    email = os.environ.get("FIREBASE_BACKUP_EMAIL")
    password = os.environ.get("FIREBASE_BACKUP_PASS")
    if not email or not password:
        print("[OK] FIREBASE_BACKUP_EMAIL/PASS no configurados -- se respalda solo 'stats'.")
    else:
        try:
            id_token = login(email, password)
            for nodo in NODOS_CON_LOGIN:
                backup[nodo] = fetch_nodo(nodo, id_token)
            print(f"[OK] login de backup correcto: se sumaron {', '.join(NODOS_CON_LOGIN)}")
        except Exception as e:  # noqa
            print(f"[WARN] no se pudo respaldar plantel/rendimiento/gps: {e}", file=sys.stderr)

    hoy = datetime.date.today().isoformat()
    destino = os.path.join(CARPETA_BACKUPS, f"backup-{hoy}.json")
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(backup, f, ensure_ascii=False, indent=2, sort_keys=True)
    print(f"[OK] backup guardado en {destino}")

    # Podar backups viejos -- nos quedamos con los ultimos BACKUPS_A_CONSERVAR.
    archivos = sorted(
        f for f in os.listdir(CARPETA_BACKUPS)
        if f.startswith("backup-") and f.endswith(".json")
    )
    for viejo in archivos[:-BACKUPS_A_CONSERVAR]:
        os.remove(os.path.join(CARPETA_BACKUPS, viejo))
        print(f"[OK] backup viejo eliminado: {viejo}")


if __name__ == "__main__":
    main()
