# -*- coding: utf-8 -*-
"""Revision de la sincronizacion de video por "ritmo" (ver sync_ritmo.py).

Por defecto NO GUARDA NADA: arma una tabla con todas las fechas que tienen
esfuerzos de Catapult y link de video, comparando la calibracion actual con
la que da el metodo nuevo.

Como correrlo (en la PC del club, desde la carpeta del repo, con main al dia):

    python scripts\\revisar_sync_ritmo.py                 (todas las categorias)
    python scripts\\revisar_sync_ritmo.py 4TA 5TA         (solo esas)

Para guardar (pide el usuario de Firebase del scraper):

    python scripts\\revisar_sync_ritmo.py --guardar pendientes
        -> solo las fechas SIN calibrar.
    python scripts\\revisar_sync_ritmo.py --guardar 4TA:F10,4TA:F11
        -> reemplaza esas fechas puntuales. La calibracion anterior queda
           guardada adentro, en "anterior", para poder volver atras.

Con CATAPULT_USER / CATAPULT_PASS en el entorno usa la senal densa (carreras
desde ~15 km/h, la validada). Sin eso usa los esfuerzos guardados (>=21 km/h),
que encastra peor.
"""
import getpass
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scrape_tablas as st  # noqa: E402
import sync_ritmo as sr  # noqa: E402

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def leer_json(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def periodo(periodos, patron):
    return next((p for p in periodos or [] if patron in (p.get("name") or "")), None)


class Firebase:
    def __init__(self, email, clave):
        self.email, self.clave, self.tok = email, clave, st._tigre_fb_login(email, clave)

    def get(self, path):
        return st._tigre_fb_get(path, self.tok)

    def put(self, path, valor):
        try:
            return st._tigre_fb_put(path, valor, self.tok)
        except Exception:
            self.tok = st._tigre_fb_login(self.email, self.clave)
            return st._tigre_fb_put(path, valor, self.tok)


class Catapult:
    """Login una vez y cache de actividades por categoria."""
    def __init__(self, usuario, clave):
        self.opener, _ = st.catapult_login(usuario, clave)
        teams = st.catapult_get(self.opener, f"{st.CATAPULT_API_BASE}/teams")
        self.team = {st.CATAPULT_TEAMS.get(t.get("name")): t["id"] for t in teams}
        self.acts = {}

    def actividades(self, cat, fecha_num):
        if cat not in self.acts:
            tid = self.team.get(cat)
            lista = st.catapult_get(self.opener, f"{st.CATAPULT_API_BASE}/activities?page=1&page_size=100"
                                                 f"&sort=-start_time&deleted=0&team_ids={tid}") if tid else []
            self.acts[cat] = st._catapult_actividades_partido(lista, cat)
        return [aid for aid, f in self.acts[cat].items() if f == fecha_num]


def main():
    args = sys.argv[1:]
    guardar = None
    if "--guardar" in args:
        i = args.index("--guardar")
        guardar = args[i + 1] if i + 1 < len(args) else ""
        args = args[:i] + args[i + 2:]
    cats_pedidas = [a.upper() for a in args]

    efforts = leer_json(os.path.join(RAIZ, "data", "catapult_efforts.json"))
    fb = None
    if guardar is not None:
        email = os.environ.get("FIREBASE_EMAIL") or input("Email de Firebase (el del scraper): ").strip()
        clave = os.environ.get("FIREBASE_PASSWORD") or getpass.getpass("Contrasena: ")
        fb = Firebase(email, clave)
        vsync = fb.get("gps/videoSync") or {}
        links = (fb.get("stats/links") or {})
    else:
        backups = sorted(glob.glob(os.path.join(RAIZ, "data", "backups", "backup-*.json")))
        if not backups:
            raise SystemExit("[ERROR] No hay backups en data/backups (hace git pull).")
        b = leer_json(backups[-1])
        vsync, links = b.get("gps/videoSync") or {}, (b.get("stats") or {}).get("links") or {}
        print(f"(solo lectura, datos del backup {os.path.basename(backups[-1])})")

    cata = None
    if os.environ.get("CATAPULT_USER") and os.environ.get("CATAPULT_PASS"):
        try:
            cata = Catapult(os.environ["CATAPULT_USER"], os.environ["CATAPULT_PASS"])
            print("Senal de GPS: carreras desde ~15 km/h (Catapult)")
        except Exception as e:  # noqa
            print(f"[AVISO] Catapult: {e} -- se usan los esfuerzos guardados")
    if not cata:
        print("Senal de GPS: esfuerzos guardados >=21 km/h (menos precisa)")

    a_guardar = set()
    if guardar and guardar != "pendientes":
        a_guardar = {x.strip().upper() for x in guardar.split(",") if ":" in x}

    ffmpeg = st.imageio_ffmpeg.get_ffmpeg_exe()
    filas = []
    for cat in sorted(efforts):
        if cats_pedidas and cat not in cats_pedidas:
            continue
        for fk in sorted(efforts[cat], key=lambda f: int(f[1:])):
            dia = efforts[cat][fk]
            lk = links.get(cat)
            item = (lk[int(fk[1:])] if isinstance(lk, list) and int(fk[1:]) < len(lk) else (lk or {}).get(fk[1:])) if lk else None
            url = (item or {}).get("par") if isinstance(item, dict) else None
            if not url:
                continue
            actual = (vsync.get(cat) or {}).get(fk)
            print(f"{cat} {fk}: calculando ...", flush=True)
            try:
                v = sr.curva_video(url, st.yt_dlp, ffmpeg)
                carreras = []
                if cata:
                    carreras = sr.carreras_desde_api(st, cata.opener, cata.actividades(cat, int(fk[1:])))
                if not carreras:
                    carreras = sr.carreras_desde_efforts(dia)
                u0, g = sr.curva_gps(carreras)
                nuevo = sr.calcular(u0, g, v, dia.get("periodos")) if g else None
            except Exception as e:  # noqa
                filas.append((cat, fk, actual, None, f"error: {str(e)[:60]}"))
                continue
            difs = []
            for cual, patron in ((1, "rimer"), (2, "egundo")):
                p = periodo(dia.get("periodos"), patron)
                k = (actual or {}).get(f"kickoff{cual}")
                if nuevo and p and p.get("start") and k is not None:
                    off_nuevo = sr.offset_en(nuevo["tramos"], p["start"] + 120)
                    difs.append(off_nuevo - (float(k) - p["start"]))
            if not nuevo:
                propuesta = "no encastra (queda como esta)"
            elif not actual:
                propuesta = "GUARDAR: estaba sin calibrar"
            elif difs and max(abs(d) for d in difs) <= 5:
                propuesta = "coincide"
            else:
                propuesta = "DIFIERE: revisar a ojo"
            filas.append((cat, fk, actual, nuevo, propuesta, difs))

            clave = f"{cat}:{fk}"
            if fb and nuevo and ((guardar == "pendientes" and not actual) or clave in a_guardar):
                valor = dict(nuevo)
                if actual:
                    valor["anterior"] = actual
                fb.put(f"gps/videoSync/{cat}/{fk}", valor)
                print(f"   [GUARDADO] {clave}")

    print("\n================= REVISION =================")
    for f in filas:
        cat, fk, actual, nuevo, propuesta = f[:5]
        difs = f[5] if len(f) > 5 else []
        act = f"{(actual or {}).get('fuente') or ('manual/ocr' if actual else 'sin calibrar')}"
        tr = " | ".join(f"{t['offset'] - (nuevo['tramos'][0]['offset'])}s x{t['ventanas']}" for t in nuevo["tramos"]) if nuevo else "-"
        dif = " / ".join(f"{d:+.0f}s" for d in difs) if difs else "-"
        print(f"{cat} {fk:4} | actual: {act:12} | tramos: {len(nuevo['tramos']) if nuevo else 0} ({tr}) "
              f"| dif 1T/2T: {dif:14} | {propuesta}")
    print("\nCopia todo este texto y pasaselo a Claude.")


if __name__ == "__main__":
    main()
