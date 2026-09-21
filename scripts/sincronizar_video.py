# -*- coding: utf-8 -*-
"""Corre SOLO la sincronizacion de video (gps/videoSync) a mano, sin esperar a
la tarea programada de la PC y sin tocar nada del resto del scraper.

Para que sirve
--------------
La calibracion de "esfuerzos en video" la hace `scrape_tablas.py` como parte de
su corrida completa, cada 4 horas. Este arranque hace solo esa parte: no
necesita las credenciales de Catapult ni de futdetail (los esfuerzos ya estan
en data/tablas.json, que el scraper deja actualizado en el repo), solo las de
Firebase, que son las mismas de siempre.

Como correrlo (en la PC del club, desde la carpeta del repo, con main al dia):

    git checkout main
    git pull
    python scripts\\sincronizar_video.py

Escribe en Firebase (gps/videoSync y gps/videoSyncFallos) exactamente lo mismo
que escribiria la corrida automatica. Las fechas que no se pueden detectar
quedan como estan, para calibrar a mano.

Ojo con el tiempo: cada fecha que el detector intenta tarda entre medio minuto
(via del corte) y varios minutos (barrido del cartel, cuando todavia no se
rindio con esa fecha). Con muchas fechas pendientes puede ser media hora o mas.
"""
import getpass
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scrape_tablas as st  # noqa: E402

RUTA_TABLAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "tablas.json")


def main():
    email = os.environ.get("FIREBASE_EMAIL")
    password = os.environ.get("FIREBASE_PASSWORD")
    if not (email and password):
        print("No estan FIREBASE_EMAIL / FIREBASE_PASSWORD en el entorno, asi que van a mano")
        print("(es el mismo usuario de Firebase que usa el scraper; no se guarda nada).")
        try:
            email = email or input("Email de Firebase: ").strip()
            password = password or getpass.getpass("Contrasena: ")
        except (EOFError, KeyboardInterrupt):
            print("\n[ERROR] Sin credenciales no se puede guardar la calibracion.")
            return 1
    if not (email and password):
        print("[ERROR] Faltan las credenciales de Firebase.")
        return 1

    try:
        with open(RUTA_TABLAS, encoding="utf-8") as f:
            efforts = json.load(f).get("catapult_efforts") or {}
    except Exception as e:
        print("[ERROR] No se pudo leer data/tablas.json: %s" % e)
        return 1
    if not efforts:
        print("[ERROR] data/tablas.json no tiene catapult_efforts todavia.")
        return 1

    fechas = sum(len(v or {}) for v in efforts.values())
    print("Fechas con esfuerzos de Catapult: %d (las que ya estan calibradas se saltean solas)\n"
          % fechas)
    st.sincronizar_video_kickoffs(email, password, efforts)
    return 0


if __name__ == "__main__":
    sys.exit(main())
