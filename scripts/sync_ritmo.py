# -*- coding: utf-8 -*-
"""Sincronizar GPS y video por el "ritmo" del partido (sin horas).

No usa la hora de arranque de los tiempos de Catapult (puede estar
"estipulada") ni la hora del video (en visitante no se sabe). Arma dos
curvas segundo a segundo y busca el corrimiento donde encastran:

  - GPS:   cuantos jugadores estan corriendo fuerte en cada segundo.
  - Video: cuanto cambia la imagen en cada segundo (FFmpeg).

Se mira el partido de a ventanas de 10 minutos. Las ventanas seguidas que
dan el mismo corrimiento forman un "tramo"; si el video tiene un corte
(entretiempo recortado, transmision que se cayo) aparecen dos o mas tramos
con corrimientos distintos. Sirve igual para partidos de corrido, cortados,
de camara VEO o de cualquier link.

Resultado (lo que se guarda en gps/videoSync/{cat}/{fecha}):
  tramos:  [{desde, hasta, offset, ventanas}]  -> segundo_video = hora_unix + offset
           (desde/hasta en hora unix; None = abierto)
  kickoff1 / kickoff2: el mismo dato en el formato viejo, para versiones de
           la app que todavia no leen 'tramos'.
  fuente:  "ritmo"

Validado a ojo el 2026-10-16 con 4TA F29 (sprints de Ordonez en 1T y 2T,
~0.5 s) y 4TA F26 (referencia de Javi). Ver scripts/probar_alineacion.py.
"""
import json
import math
import os
import re
import statistics
import subprocess
import tempfile

try:
    import numpy as np
except ImportError:  # anda sin numpy, mas lento
    np = None

CACHE = os.path.join(tempfile.gettempdir(), "tigre_alineacion")
VENTANA = 600        # segundos de GPS por ventana
PASO = 300           # cada cuanto arranca una ventana nueva
SUAVIZADO = 5        # promedio movil del paso grueso
MARGEN_PICO = 20     # el 2do mejor pico se busca a mas de +-20 s del mejor
CORR_MIN = 0.30      # ventana "buena": correlacion minima...
VENTAJA_MIN = 0.05   # ...y ventaja minima sobre el 2do mejor lugar
TOLERANCIA = 3       # ventanas con corrimientos a +-3 s son el mismo tramo
MIN_VENTANAS = 4     # menos ventanas buenas que esto en total -> no se confia
BANDAS_API = "4,5,6,7,8"   # carreras desde ~15 km/h (Catapult)


# ── Curvas ────────────────────────────────────────────────────────────────
def curva_gps(tramos_carrera):
    """[(inicio_unix, fin_unix)] de todos los jugadores -> (u0, lista con la
    cantidad de jugadores corriendo en cada segundo desde u0)."""
    if not tramos_carrera:
        return None, []
    u0 = int(min(a for a, _ in tramos_carrera))
    u1 = int(max(b for _, b in tramos_carrera)) + 1
    s = [0.0] * (u1 - u0 + 1)
    for a, b in tramos_carrera:
        for t in range(int(a) - u0, max(int(a) + 1, int(math.ceil(b))) - u0):
            s[t] += 1
    return u0, s


def carreras_desde_efforts(dia):
    """Senal liviana (sprints/HSR >=21 km/h ya guardados en catapult_efforts)."""
    out = []
    for efs in (dia.get("jugadores") or {}).values():
        for e in efs or []:
            if e.get("start"):
                out.append((e["start"], e["start"] + max(1.0, e.get("dur") or 0)))
    return out


def carreras_desde_api(st, opener, activity_ids, bandas=BANDAS_API):
    """Senal densa: todas las carreras desde ~15 km/h, pedidas a Catapult."""
    out = []
    for aid in activity_ids:
        for atl in st.catapult_activity_athletes(opener, aid):
            if not atl.get("id"):
                continue
            for e in st._catapult_velocity_merged(opener, aid, atl["id"], bandas):
                if e.get("start_time"):
                    out.append((e["start_time"], e.get("end_time") or e["start_time"] + 1))
    return out


def curva_video(url, yt_dlp, ffmpeg_exe, borrar_video=True):
    """Cambio de imagen por segundo (0..255), con cache por video (json chico).
    El video se baja en la calidad minima y se borra al terminar."""
    os.makedirs(CACHE, exist_ok=True)
    vid = re.sub(r"\W", "_", url.split("/")[-1].split("v=")[-1])[:40]
    ruta_cache = os.path.join(CACHE, vid + ".json")
    if os.path.exists(ruta_cache):
        with open(ruta_cache) as f:
            return json.load(f)
    archivo = os.path.join(CACHE, vid + ".mp4")
    if not os.path.exists(archivo):
        opts = {"format": "160/133/278/worstvideo[ext=mp4]/worst", "outtmpl": archivo,
                "quiet": True, "no_warnings": True, "noprogress": True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            ydl.download([url])
    filtro = ("fps=2,scale=96:-2,format=gray,tblend=all_mode=difference,"
              "signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=-")
    proc = subprocess.run([ffmpeg_exe, "-hide_banner", "-nostats", "-i", archivo, "-an", "-vf", filtro,
                           "-f", "null", "-"], capture_output=True, text=True, errors="replace")
    por_seg, t = {}, None
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
    serie = [statistics.mean(por_seg[i]) if i in por_seg else 0.0 for i in range(max(por_seg) + 1)]
    with open(ruta_cache, "w") as f:
        json.dump(serie, f)
    if borrar_video:
        try:
            os.remove(archivo)
        except OSError:
            pass
    return serie


# ── Encastre ──────────────────────────────────────────────────────────────
def suavizar(s, w):
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
    if len(v) < W or W == 0:
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


def ventanas(u0, g, v):
    """Por cada ventana de GPS: (centro_unix, offset, corr, ventaja)."""
    gs, vs = suavizar(g, SUAVIZADO), suavizar(v, SUAVIZADO)
    res = []
    for a in range(0, max(1, len(gs) - VENTANA + 1), PASO):
        w = gs[a:a + VENTANA]
        if len(w) < VENTANA // 2 or sum(1 for x in w if x > 0) < 30:
            continue  # casi sin actividad (entretiempo, antes/despues del partido)
        c = correlaciones(w, vs)
        if not c:
            continue
        j = max(range(len(c)), key=c.__getitem__)
        resto = [c[k] for k in range(len(c)) if abs(k - j) > MARGEN_PICO]
        res.append((u0 + a + VENTANA // 2, j - (u0 + a), c[j], c[j] - (max(resto) if resto else 0.0)))
    return res


def afinar(u0, g, v, desde, hasta, offset, margen=10, suav=3):
    """Busca el mejor corrimiento a +-margen s, con todo el tramo junto."""
    a, b = max(0, int(desde) - u0), min(len(g), int(hasta) - u0)
    if b - a < 60:
        return offset
    gs, vs = suavizar(g[a:b], suav), suavizar(v, suav)
    mejor, mejor_c = offset, -2.0
    for off in range(int(offset) - margen, int(offset) + margen + 1):
        j = u0 + a + off
        if j < 0 or j + len(gs) > len(vs):
            continue
        c = correlaciones(gs, vs[j:j + len(gs)])
        if c and c[0] > mejor_c:
            mejor, mejor_c = off, c[0]
    return mejor


def buscar_corte(u0, g, v, ini, fin, off_a, off_b, lado=120, paso=5):
    """Entre el ultimo centro del tramo A y el primero del B: el segundo donde
    mejor calza "A antes, B despues" (correlacion a cada lado del corte)."""
    gs, vs = suavizar(g, 3), suavizar(v, 3)
    def corr(a, b, off):
        a, b = max(0, a - u0), min(len(gs), b - u0)
        j = u0 + a + off
        if b - a < 30 or j < 0 or j + (b - a) > len(vs):
            return 0.0
        c = correlaciones(gs[a:b], vs[j:j + (b - a)])
        return c[0] if c else 0.0
    mejor, mejor_s = (ini + fin) // 2, -9.0
    for t in range(int(ini), int(fin) + 1, paso):
        sc = corr(t - lado, t, off_a) + corr(t, t + lado, off_b)
        if sc > mejor_s:
            mejor, mejor_s = t, sc
    return mejor


def tramos_desde_ventanas(u0, g, v, vent):
    """Agrupa las ventanas buenas en tramos de corrimiento parejo."""
    buenas = sorted([x for x in vent if x[2] >= CORR_MIN and x[3] >= VENTAJA_MIN])
    grupos = []
    for x in buenas:
        if grupos and abs(x[1] - statistics.median(y[1] for y in grupos[-1])) <= TOLERANCIA:
            grupos[-1].append(x)
        else:
            grupos.append([x])
    grupos = [gr for gr in grupos if len(gr) >= 2]  # una ventana sola no alcanza
    # dos grupos seguidos con el mismo corrimiento (separados por una ventana rara) -> uno solo
    unidos = []
    for gr in grupos:
        if unidos and abs(statistics.median(y[1] for y in gr) - statistics.median(y[1] for y in unidos[-1])) <= TOLERANCIA:
            unidos[-1].extend(gr)
        else:
            unidos.append(gr)
    if sum(len(gr) for gr in unidos) < MIN_VENTANAS:
        return []
    tramos = []
    for gr in unidos:
        desde, hasta = gr[0][0] - VENTANA // 2, gr[-1][0] + VENTANA // 2
        off = afinar(u0, g, v, desde, hasta, round(statistics.median(y[1] for y in gr)))
        tramos.append({"desde": gr[0][0], "hasta": gr[-1][0], "offset": int(off), "ventanas": len(gr)})
    # bordes: se busca el segundo exacto del corte entre dos tramos; el
    # primero y el ultimo quedan abiertos
    for i in range(len(tramos) - 1):
        corte = buscar_corte(u0, g, v, tramos[i]["hasta"], tramos[i + 1]["desde"],
                             tramos[i]["offset"], tramos[i + 1]["offset"])
        tramos[i]["hasta"], tramos[i + 1]["desde"] = corte, corte
    tramos[0]["desde"], tramos[-1]["hasta"] = None, None
    return tramos


def offset_en(tramos, unix):
    """Corrimiento que corresponde a una hora (el tramo que la contiene)."""
    for t in tramos:
        if (t["desde"] is None or unix >= t["desde"]) and (t["hasta"] is None or unix < t["hasta"]):
            return t["offset"]
    return None


def calcular(u0, g, v, periodos=None):
    """Devuelve el dict listo para gps/videoSync, o None si no encastra firme."""
    tramos = tramos_desde_ventanas(u0, g, v, ventanas(u0, g, v))
    if not tramos:
        return None
    out = {"tramos": tramos, "fuente": "ritmo"}
    for cual, patron in ((1, "rimer"), (2, "egundo")):
        p = next((p for p in (periodos or []) if patron in (p.get("name") or "")), None)
        if p and p.get("start"):
            # +60 s: si Catapult marco el arranque un poco antes del corte real,
            # que el kickoff viejo use el tramo de ese tiempo y no el anterior.
            out[f"kickoff{cual}"] = round(p["start"] + offset_en(tramos, p["start"] + 60), 1)
    return out
