# -*- coding: utf-8 -*-
"""PRUEBA (no guarda nada): sincronizar GPS y video por el "ritmo" del partido.

Idea
----
No usa la hora de arranque de los tiempos de Catapult (puede estar
"estipulada") ni la hora del video (en visitante no se sabe). Compara dos
senales segundo a segundo y busca el corrimiento donde encastran:

  - GPS:   cuantos jugadores estan corriendo fuerte en cada segundo
           (sale de los esfuerzos de Catapult; la hora ENTRE esfuerzos es
           exacta porque viene del GPS).
  - Video: cuanto cambia la imagen en cada segundo (FFmpeg). La camara se
           mueve con la jugada y se queda quieta en las pelotas paradas.

El resultado es el "offset": segundo_del_video = hora_unix_del_esfuerzo + offset.
Se calcula por ventanas de 10 minutos, asi un corte en el video se nota
porque el offset cambia de una ventana a otra.

Para medir si sirve, se compara contra las fechas YA calibradas (a mano o
por esfuerzo conocido): esa es la respuesta correcta conocida.

Como correrlo (en la PC del club, desde la carpeta del repo, con main al dia):

    python scripts\\probar_alineacion.py                 (elige solo 5 fechas calibradas)
    python scripts\\probar_alineacion.py 4TA:F29 5TA:F14 (fechas puntuales)

Opcional, senal de GPS mas densa (pide la velocidad a Catapult, tarda mas):
    con CATAPULT_USER / CATAPULT_PASS en el entorno se agrega solo.

Necesita lo mismo que ya usa el scraper para el video: yt-dlp e
imageio-ffmpeg. Si esta numpy lo usa (mas rapido); si no, anda igual.
"""
import glob
import json
import math
import os
import re
import statistics
import subprocess
import sys
import tempfile
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scrape_tablas as st  # noqa: E402

try:
    import numpy as np
except ImportError:  # anda sin numpy, mas lento
    np = None

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CACHE = os.path.join(tempfile.gettempdir(), "tigre_alineacion")
VENTANA = 600       # segundos de GPS por ventana
PASO = 300          # cada cuanto arranca una ventana nueva
SUAVIZADO = 5       # promedio movil, en segundos
CORR_MIN = 0.20     # correlacion minima para confiar en una ventana
MARGEN_PICO = 20    # el 2do mejor pico se busca a mas de +-20 s del mejor


# ── Datos del repo ────────────────────────────────────────────────────────
def cargar_json(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def ultimo_backup():
    archivos = sorted(glob.glob(os.path.join(RAIZ, "data", "backups", "backup-*.json")))
    if not archivos:
        raise SystemExit("[ERROR] No hay backups en data/backups (hace git pull).")
    return cargar_json(archivos[-1])


def link_video(stats, cat, fecha_num):
    links = (stats.get("links") or {}).get(cat)
    if isinstance(links, list):
        item = links[fecha_num] if fecha_num < len(links) else None
    else:
        item = (links or {}).get(str(fecha_num))
    return (item or {}).get("par") or ""


def periodo(periodos, cual):
    patron = "rimer" if cual == 1 else "egundo"
    return next((p for p in periodos if patron in (p.get("name") or "")), None)


def offset_verdad(dia, sync, unix):
    """Offset de la calibracion guardada para el tiempo que contiene 'unix'."""
    p1, p2 = periodo(dia["periodos"], 1), periodo(dia["periodos"], 2)
    if p2 and unix >= p2["start"] and sync.get("kickoff2") is not None:
        return float(sync["kickoff2"]) - p2["start"], 2
    if p1 and sync.get("kickoff1") is not None:
        return float(sync["kickoff1"]) - p1["start"], 1
    return None, None


# ── Senal del GPS ─────────────────────────────────────────────────────────
def senal_gps(tramos):
    """tramos = [(inicio_unix, fin_unix)] de todos los jugadores ->
    (u0, lista) con la cantidad de jugadores corriendo en cada segundo."""
    if not tramos:
        return None, []
    u0 = int(min(a for a, _ in tramos))
    u1 = int(max(b for _, b in tramos)) + 1
    s = [0.0] * (u1 - u0 + 1)
    for a, b in tramos:
        for t in range(int(a) - u0, max(int(a) + 1, int(math.ceil(b))) - u0):
            s[t] += 1
    return u0, s


def tramos_desde_json(dia):
    out = []
    for efs in (dia.get("jugadores") or {}).values():
        for e in efs or []:
            if e.get("start"):
                out.append((e["start"], e["start"] + max(1.0, e.get("dur") or 0)))
    return out


def tramos_desde_api(cat, fecha_num, usuario, clave, bandas="4,5,6,7,8"):
    opener, _cj = st.catapult_login(usuario, clave)
    teams = st.catapult_get(opener, f"{st.CATAPULT_API_BASE}/teams")
    team_id = next((t["id"] for t in teams if st.CATAPULT_TEAMS.get(t.get("name")) == cat), None)
    if not team_id:
        return []
    acts = st.catapult_get(opener, f"{st.CATAPULT_API_BASE}/activities?page=1&page_size=100"
                                   f"&sort=-start_time&deleted=0&team_ids={team_id}")
    aids = [aid for aid, f in st._catapult_actividades_partido(acts, cat).items() if f == fecha_num]
    out = []
    for aid in aids:
        for atl in st.catapult_activity_athletes(opener, aid):
            if not atl.get("id"):
                continue
            for e in st._catapult_velocity_merged(opener, aid, atl["id"], bandas):
                if e.get("start_time"):
                    out.append((e["start_time"], e.get("end_time") or e["start_time"] + 1))
    return out


# ── Senal del video ───────────────────────────────────────────────────────
def senal_video(url):
    """Cambio de imagen por segundo (0..255). Se guarda en cache por video."""
    os.makedirs(CACHE, exist_ok=True)
    vid = re.sub(r"\W", "_", url.split("/")[-1].split("v=")[-1])[:40]
    ruta_cache = os.path.join(CACHE, vid + ".json")
    if os.path.exists(ruta_cache):
        return cargar_json(ruta_cache)
    archivo = os.path.join(CACHE, vid + ".mp4")
    if not os.path.exists(archivo):
        print(f"    bajando video en calidad minima ({url}) ...")
        opts = {"format": "160/133/278/worstvideo[ext=mp4]/worst", "outtmpl": archivo,
                "quiet": True, "no_warnings": True, "noprogress": True}
        with st.yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
    print("    midiendo movimiento de la imagen (FFmpeg) ...")
    ffmpeg = st.imageio_ffmpeg.get_ffmpeg_exe()
    filtro = ("fps=2,scale=96:-2,format=gray,tblend=all_mode=difference,"
              "signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-")
    proc = subprocess.run([ffmpeg, "-hide_banner", "-nostats", "-i", archivo, "-an", "-vf", filtro,
                           "-f", "null", "-"], capture_output=True, text=True, errors="replace")
    por_seg = {}
    t = None
    for linea in proc.stdout.splitlines():
        m = re.search(r"pts_time:([\d.]+)", linea)
        if m:
            t = int(float(m.group(1)))
            continue
        m = re.search(r"YAVG=([\d.]+)", linea)
        if m and t is not None:
            por_seg.setdefault(t, []).append(float(m.group(1)))
    if not por_seg:
        raise RuntimeError("FFmpeg no devolvio datos de movimiento: " + proc.stderr[-300:])
    n = max(por_seg) + 1
    serie = [statistics.mean(por_seg[i]) if i in por_seg else 0.0 for i in range(n)]
    with open(ruta_cache, "w") as f:
        json.dump(serie, f)
    return serie


# ── Encastre ──────────────────────────────────────────────────────────────
def suavizar(s, w=SUAVIZADO):
    if w <= 1:
        return list(s)
    acc, out = 0.0, []
    for i, x in enumerate(s):
        acc += x
        if i >= w:
            acc -= s[i - w]
        out.append(acc / min(i + 1, w))
    return out


def correlaciones(g, v):
    """Correlacion de Pearson de la ventana g contra cada posicion de v."""
    W = len(g)
    if len(v) < W:
        return []
    mg = sum(g) / W
    gz = [x - mg for x in g]
    ng = math.sqrt(sum(x * x for x in gz)) or 1e-9
    if np is not None:
        va, ga = np.asarray(v, dtype=float), np.asarray(gz, dtype=float)
        num = np.correlate(va, ga, mode="valid")
        cs, cs2 = np.cumsum(np.r_[0, va]), np.cumsum(np.r_[0, va * va])
        s, s2 = cs[W:] - cs[:-W], cs2[W:] - cs2[:-W]
        den = np.sqrt(np.maximum(s2 - s * s / W, 1e-9)) * ng
        return list(num / den)
    cs, cs2 = [0.0], [0.0]
    for x in v:
        cs.append(cs[-1] + x)
        cs2.append(cs2[-1] + x * x)
    out = []
    for j in range(len(v) - W + 1):
        num = sum(gz[i] * v[j + i] for i in range(W))
        s, s2 = cs[j + W] - cs[j], cs2[j + W] - cs2[j]
        out.append(num / (math.sqrt(max(s2 - s * s / W, 1e-9)) * ng))
    return out


def alinear(u0, g, v):
    """Por cada ventana de GPS: (centro_unix, offset, corr, ventaja_sobre_2do_pico)."""
    g, v = suavizar(g), suavizar(v)
    res = []
    for a in range(0, max(1, len(g) - VENTANA + 1), PASO):
        w = g[a:a + VENTANA]
        if len(w) < VENTANA // 2 or sum(1 for x in w if x > 0) < 30:
            continue  # ventana casi sin actividad (entretiempo, antes/despues)
        c = correlaciones(w, v)
        if not c:
            continue
        j = max(range(len(c)), key=c.__getitem__)
        resto = [c[k] for k in range(len(c)) if abs(k - j) > MARGEN_PICO]
        segundo = max(resto) if resto else 0.0
        offset = j - (u0 + a)  # segundo_video = unix + offset
        res.append((u0 + a + VENTANA // 2, offset, c[j], c[j] - segundo))
    return res


def consenso(ventanas):
    buenas = [x for x in ventanas if x[2] >= CORR_MIN and x[3] > 0.03]
    if not buenas:
        return None, 0
    offs = sorted(x[1] for x in buenas)
    # el grupo mas grande de offsets que caen a +-8 s entre si
    mejor = max(offs, key=lambda o: sum(1 for p in offs if abs(p - o) <= 8))
    grupo = [p for p in offs if abs(p - mejor) <= 8]
    return statistics.median(grupo), len(grupo)


# ── Main ──────────────────────────────────────────────────────────────────
def main():
    efforts = cargar_json(os.path.join(RAIZ, "data", "catapult_efforts.json"))
    backup = ultimo_backup()
    stats, vsync = backup.get("stats") or {}, backup.get("gps/videoSync") or {}
    usuario, clave = os.environ.get("CATAPULT_USER"), os.environ.get("CATAPULT_PASS")

    casos = [a.split(":") for a in sys.argv[1:] if ":" in a]
    if not casos:  # 5 fechas calibradas, con video
        for cat, fechas in vsync.items():
            for fk, s in fechas.items():
                if fk in (efforts.get(cat) or {}) and link_video(stats, cat, int(fk[1:])):
                    casos.append((cat, fk))
        casos = casos[:5]

    resumen = []
    for cat, fk in casos:
        print(f"\n=== {cat} {fk} ===")
        dia = (efforts.get(cat) or {}).get(fk)
        url = link_video(stats, cat, int(fk[1:]))
        sync = (vsync.get(cat) or {}).get(fk) or {}
        if not dia or not url:
            print("  sin esfuerzos o sin link de video, se saltea")
            continue
        try:
            v = senal_video(url)
        except Exception as e:  # noqa
            print(f"  [ERROR] video: {e}")
            continue
        fuentes = [("esfuerzos >=21 km/h (json)", tramos_desde_json(dia))]
        if usuario and clave:
            try:
                fuentes.append(("velocidad Catapult (API)", tramos_desde_api(cat, int(fk[1:]), usuario, clave)))
            except Exception as e:  # noqa
                print(f"  [AVISO] Catapult API: {e}")
        for nombre, tramos in fuentes:
            u0, g = senal_gps(tramos)
            if not g:
                continue
            t0 = time.time()
            vent = alinear(u0, g, v)
            print(f"  GPS: {nombre} -- {len(tramos)} tramos, {len(vent)} ventanas ({time.time() - t0:.0f}s)")
            errores = []
            for centro, off, corr, ventaja in vent:
                verdad, tiempo = offset_verdad(dia, sync, centro) if sync else (None, None)
                err = f"{off - verdad:+7.1f}s" if verdad is not None else "   s/d"
                if verdad is not None and corr >= CORR_MIN:
                    errores.append(abs(off - verdad))
                print(f"    ventana {time.strftime('%H:%M', time.localtime(centro))}"
                      f"  offset {off:9.0f}  corr {corr:4.2f}  ventaja {ventaja:4.2f}"
                      f"  {('T' + str(tiempo)) if tiempo else '  '} error {err}")
            est, n = consenso(vent)
            verdad1, _ = offset_verdad(dia, sync, periodo(dia["periodos"], 1)["start"]) if sync and periodo(dia["periodos"], 1) else (None, None)
            linea = f"  => consenso: offset {est} ({n} ventanas)"
            if est is not None and verdad1 is not None:
                linea += f"  | calibracion guardada 1T: {verdad1:.1f}  -> diferencia {est - verdad1:+.1f}s"
            print(linea)
            resumen.append((cat, fk, nombre, est, verdad1, n))

    print("\n=========== RESUMEN ===========")
    for cat, fk, nombre, est, verdad, n in resumen:
        dif = f"{est - verdad:+.1f}s" if (est is not None and verdad is not None) else "s/d"
        print(f"{cat} {fk:4} | {nombre:28} | diferencia vs calibracion: {dif:>8} | ventanas de acuerdo: {n}")
    print("\nCopia todo este texto y pasaselo a Claude.")


if __name__ == "__main__":
    main()
