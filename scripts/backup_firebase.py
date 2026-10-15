#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backup diario de los datos de Firebase (resultados, goleadores, tarjetas,
lesiones, sesiones GPS, etc.) a un archivo JSON versionado en el repo.

Por que hace falta: toda la info de la temporada vive UNICAMENTE en
Firebase Realtime Database. Si alguien borra algo por error, o hay un
problema con la cuenta de Firebase, no hay ninguna copia de respaldo aparte
-- este script la crea sin intervencion manual.

Que respalda: "stats", "temporadaActiva" y cada hijo legible de "gps".
Desde el muro de login (2026-08-27) NINGUN nodo se puede leer sin sesion,
asi que el script se loguea con los secrets FIREBASE_BACKUP_EMAIL /
FIREBASE_BACKUP_PASS (API REST de Firebase Auth, mismo apiKey publico de la
app). Sin esos secrets falla a proposito: un backup vacio no sirve.
"stats" es obligatorio; si otro nodo falla, avisa y sigue.
No respalda "users" (mails y roles) porque el repo es publico.

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
# Desde el muro de login (27/8) todo pide sesion. "stats" es obligatorio;
# el resto se intenta y, si falla, avisa pero no corta el backup.
NODO_OBLIGATORIO = "stats"
# "gps" no tiene regla de lectura en la raiz (solo en cada hijo), asi que
# se lee hijo por hijo. "credenciales" de Catapult nunca se lee (regla false).
NODOS_EXTRA = [
    "temporadaActiva",
    "gps/sessions", "gps/videoSync", "gps/videoSyncFallos",
    "gps/reservaManual", "gps/catapultReservaAuth/estado",
]
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

    email = os.environ.get("FIREBASE_BACKUP_EMAIL")
    password = os.environ.get("FIREBASE_BACKUP_PASS")
    if not email or not password:
        print("::error::Backup: faltan FIREBASE_BACKUP_EMAIL/PASS en los secrets del repo.")
        sys.exit(1)
    try:
        id_token = login(email, password)
        backup[NODO_OBLIGATORIO] = fetch_nodo(NODO_OBLIGATORIO, id_token)
    except Exception as e:  # noqa
        detalle = " ".join(e.read().decode("utf-8", errors="replace").split())[:300] if hasattr(e, "read") else ""
        # "::error::" lo muestra GitHub como anotacion del run (visible sin abrir el log).
        print(f"::error::Backup: login o lectura de '{NODO_OBLIGATORIO}' fallo: {e} {detalle}")
        sys.exit(1)
    for nodo in NODOS_EXTRA:
        try:
            backup[nodo] = fetch_nodo(nodo, id_token)
        except Exception as e:  # noqa
            detalle = " ".join(e.read().decode("utf-8", errors="replace").split())[:200] if hasattr(e, "read") else ""
            print(f"::warning::Backup: no se pudo respaldar '{nodo}': {e} {detalle}")

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
