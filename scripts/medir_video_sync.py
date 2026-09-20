# -*- coding: utf-8 -*-
"""Mide que tan bien funciona la sincronizacion de video por HORA REAL DEL
STREAM, comparandola contra las fechas que ya estan calibradas (por OCR o a
mano) -- NO escribe nada, ni en Firebase ni en el repo: solo mira e informa.

Para que sirve
--------------
La app salta al segundo exacto de un esfuerzo con la calibracion que hay en
Firebase (gps/videoSync = en que segundo del video arranca cada tiempo). Esa
calibracion se puede deducir sin mirar el video cuando el partido fue una
transmision EN VIVO: YouTube guarda a que hora real arranco el stream y
Catapult da a que hora real arranco cada tiempo, asi que

    kickoff = hora_del_saque_inicial - hora_del_segundo_0_del_video

Este script contesta tres preguntas antes de confiar en esa cuenta:
  1) De todas tus fechas, cuantas son transmision en vivo (se calibran solas
     por esta via) y cuantas son archivos subidos despues (quedan para el
     cartel/OCR o para cargar a mano).
  2) Cuanto se equivoca la cuenta contra lo ya calibrado: si el error es de
     0-3 segundos, la via nueva es mas confiable que el OCR; si el error es
     siempre el mismo numero, se corrige solo con ese numero; si da
     cualquier cosa, conviene dejar el OCR al mando.
  3) Que fechas tienen el video cortado o pausado (el 2T no cierra).

Como correrlo (en la PC del club, desde la carpeta del repo):

    python scripts\\medir_video_sync.py

(si FIREBASE_EMAIL/FIREBASE_PASSWORD no estan en el entorno, las pide por
teclado; son las mismas que ya usa el scraper)

Opcional: un primer argumento limita cuantas fechas mira (ej. "10" para una
prueba rapida, que si no son ~2 segundos por fecha).
"""
import getpass
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scrape_tablas as st  # noqa: E402

RUTA_TABLAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "tablas.json")


def main():
    limite = int(sys.argv[1]) if len(sys.argv) > 1 else 0

    if not st.VIDEO_SYNC_DISPONIBLE:
        print("[ERROR] Falta yt-dlp (pip install yt-dlp) -- sin eso no se puede leer la "
              "hora de arranque de los videos.")
        return 1

    # Las credenciales salen de las mismas variables de entorno que usa el
    # scraper; si no estan puestas (correr el script suelto, a mano), las pide
    # por teclado en vez de fallar -- no se guardan en ningun lado.
    email = os.environ.get("FIREBASE_EMAIL")
    password = os.environ.get("FIREBASE_PASSWORD")
    if not (email and password):
        print("No estan FIREBASE_EMAIL / FIREBASE_PASSWORD en el entorno, asi que van a mano")
        print("(es el mismo usuario de Firebase que usa el scraper; no se guarda nada).")
        try:
            email = email or input("Email de Firebase: ").strip()
            password = password or getpass.getpass("Contrasena: ")
        except (EOFError, KeyboardInterrupt):
            print("\n[ERROR] Sin credenciales no se puede leer la calibracion que ya tenes.")
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

    try:
        token = st._tigre_fb_login(email, password)
    except Exception as e:
        print("[ERROR] No se pudo entrar a Firebase: %s" % e)
        return 1

    print("%-5s %-5s %-10s %10s %10s %8s  %s" %
          ("CAT", "FECHA", "VIDEO", "GUARDADO", "MEDIDO", "DIF", "OBS"))
    print("-" * 78)

    errores, en_vivo, subidos, sin_link, cortados, mirados = [], 0, 0, 0, 0, 0
    for cat in sorted(efforts):
        for fecha_key in sorted(efforts[cat], key=lambda f: int(f.lstrip("F"))):
            if limite and mirados >= limite:
                break
            dia = efforts[cat][fecha_key] or {}
            p1, p2 = st._video_periodos_1y2(dia.get("periodos"))
            if not p1:
                continue
            try:
                link = st._tigre_fb_get("stats/links/%s/%s/par" % (cat, fecha_key.lstrip("F")), token)
            except Exception:
                link = None
            if not link:
                sin_link += 1
                continue
            mirados += 1
            meta = st._video_metadata_yt(link)
            if not meta:
                print("%-5s %-5s %-10s %10s %10s %8s  %s" %
                      (cat, fecha_key, "?", "-", "-", "-", "no se pudo leer el video"))
                continue
            es_vivo = meta.get("live_status") in ("was_live", "is_live") and meta.get("release_timestamp")
            if not es_vivo:
                subidos += 1
                print("%-5s %-5s %-10s %10s %10s %8s  %s" %
                      (cat, fecha_key, meta.get("live_status") or "?", "-", "-", "-",
                       "archivo subido: sin hora de grabacion"))
                continue
            en_vivo += 1
            k1 = p1["start"] - meta["release_timestamp"]
            k2 = p2["start"] - meta["release_timestamp"]
            obs = []
            duracion = meta.get("duration") or 0
            if k1 < 0:
                obs.append("el stream arranco DESPUES del saque inicial")
            if duracion and k2 + (p2["end"] - p2["start"]) > duracion + st._VIDEO_TOLERANCIA_FIN:
                cortados += 1
                obs.append("el video no cubre el 2T (pausado/cortado)")
            try:
                sync = st._tigre_fb_get("gps/videoSync/%s/%s" % (cat, fecha_key), token)
            except Exception:
                sync = None
            guardado = (sync or {}).get("kickoff1")
            if guardado is None:
                obs.append("sin calibrar todavia (esta es la que ganariamos)")
                print("%-5s %-5s %-10s %10s %10.1f %8s  %s" %
                      (cat, fecha_key, "en vivo", "-", k1, "-", "; ".join(obs)))
                continue
            dif = k1 - float(guardado)
            errores.append(dif)
            print("%-5s %-5s %-10s %10.1f %10.1f %+8.1f  %s" %
                  (cat, fecha_key, "en vivo", float(guardado), k1, dif, "; ".join(obs)))

    print("-" * 78)
    print("Videos mirados: %d   |   en vivo: %d   |   subidos como archivo: %d   |   "
          "sin link: %d" % (mirados, en_vivo, subidos, sin_link))
    if cortados:
        print("Videos pausados o cortados (el 2T no cierra): %d" % cortados)
    if not errores:
        print("No hubo ninguna fecha que este calibrada Y sea transmision en vivo, "
              "asi que todavia no se puede medir el error.")
        return 0

    errores.sort()
    mediana = errores[len(errores) // 2]
    print("Comparacion contra %d fecha(s) ya calibradas: "
          "min %+.1fs / mediana %+.1fs / max %+.1fs" % (len(errores), errores[0], mediana, errores[-1]))
    disperso = errores[-1] - errores[0]
    # Ojo: mirar solo la dispersion no alcanza -- un desfasaje PAREJO de varios
    # segundos tiene dispersion 0 y aun asi hay que corregirlo.
    if disperso <= 3 and abs(mediana) <= 3:
        print("=> La hora real del stream coincide con lo ya calibrado. La via automatica "
              "es confiable (y mas precisa que el OCR).")
    elif disperso <= 10:
        print("=> Hay un desfasaje parejo de ~%+.1fs. El scraper ya lo corrige solo "
              "(se mide en cada corrida contra las fechas ya calibradas)." % mediana)
    else:
        print("=> Los errores no se parecen entre si (%.0fs de diferencia entre el mejor y "
              "el peor): revisar esas fechas a ojo antes de confiar en esta via." % disperso)
    return 0


if __name__ == "__main__":
    sys.exit(main())
