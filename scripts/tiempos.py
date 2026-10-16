# -*- coding: utf-8 -*-
"""Tiempos y goles de un partido, solo con el GPS de Catapult (no necesita
marcador en pantalla ni COMET: anda tambien con videos VEO).

Detecta saque del 1T, fin del 1T, saque del 2T, final y los goles, y los
pasa a segundo de video con los tramos de la sincronizacion por ritmo
(sync_ritmo.py). detectar() devuelve el dict que va en
gps/videoSync/{cat}/{fecha}/eventos. NO guarda nada.

Como se detecta:
  - Tiempos, con la curva de "jugadores en movimiento" (trote o mas)
    segundo a segundo: entretiempo = la pausa larga del medio; saque = el
    arranque despues de la pausa; final = la primera pausa larga despues
    del 2T. Si el "arranque" es el trote corto del equipo yendo a sus
    puestos (y despues se quedan quietos esperando), el saque es el
    arranque siguiente. Con posiciones, ademas: si antes del "saque" el
    equipo estaba amontonado (charla), se espera a que se abra en la cancha.
  - Goles, con las posiciones de Catapult (lat/long, 1 por segundo). La
    linea del medio y que arco defiende Tigre en cada tiempo salen de la
    formacion de los saques del 1T y 2T.
      * Gol de Tigre: el festejo, 4 o mas jugadores abrazados (a menos de
        2 m) fuera de su mitad. El gol es el primer corte del juego en el
        minuto anterior al abrazo.
      * Gol del rival: Tigre vuelve CAMINANDO (nadie trota) desde su area
        hasta la formacion de saque del medio (todos en su mitad, los de
        adelante sobre la linea) y espera ahi a sacar.
    Solo con el GPS de Tigre no alcanza para encontrarlos todos (ver la
    validacion en probar_tiempos.py), por eso se apoya en lo que se sepa:
  - Con el resultado y los minutos de COMET: los goles con minuto se buscan
    cerca de ese minuto (si no hay candidato, queda el minuto, conf media);
    los que no traen minuto (casi siempre los del rival) se reparten entre
    los mejores candidatos de ese lado (conf baja/media).
  - Sin resultado: solo los festejos clarisimos de Tigre.
  - Sin posiciones: solo las pausas de juego (conf baja).

Uso:
    ev = eventos_partido(st, opener, activity_ids, tramos,
                         resultado=(goles_tigre, goles_rival),
                         minutos_tigre=[21, 65], minutos_rival=None)
"""
import json
import math
import os
import statistics
import time
import urllib.request

import sync_ritmo as sr

BANDAS_MOVIMIENTO = "3,4,5,6,7,8"   # trotando o mas rapido
VERSION = 1


# ── Datos de Catapult ────────────────────────────────────────────────────
def curva_movimiento(st, opener, activity_ids):
    """(u0, lista): cuantos jugadores se mueven (trote o mas) en cada segundo."""
    return sr.curva_gps(sr.carreras_desde_api(st, opener, activity_ids, BANDAS_MOVIMIENTO))


def _sensor(st, opener, activity_id, athlete_id):
    req = urllib.request.Request(
        f"{st.CATAPULT_API_BASE}/activities/{activity_id}/athletes/{athlete_id}/sensor",
        headers=st.CATAPULT_HEADERS)
    data = json.loads(opener.open(req, timeout=180).read().decode("utf-8", errors="replace"))
    for s in data or []:
        if s.get("stream_type") == "gps":
            return s.get("data") or []
    return (data[0].get("data") or []) if data else []


def posiciones_desde_api(st, opener, activity_ids):
    """{atleta: {segundo_unix: (lat, long)}} promediando las muestras de 10 Hz
    de cada segundo. Pesa ~8 MB por jugador, asi que queda en cache (un json
    chico por actividad) en la misma carpeta que las curvas de video."""
    out = {}
    for aid in activity_ids:
        ruta = os.path.join(sr.CACHE, f"pos_{aid}.json")
        if os.path.exists(ruta):
            with open(ruta) as f:
                guardado = json.load(f)
        else:
            guardado = {}
            for atl in st.catapult_activity_athletes(opener, aid):
                if not atl.get("id"):
                    continue
                acc = {}
                for r in _sensor(st, opener, aid, atl["id"]):
                    la, lo, ts = r.get("lat"), r.get("long"), r.get("ts")
                    if ts is None or not la or not lo or abs(la) > 90 or abs(lo) > 180:
                        continue
                    a = acc.setdefault(int(ts), [0.0, 0.0, 0])
                    a[0] += la
                    a[1] += lo
                    a[2] += 1
                if acc:
                    guardado[atl["id"]] = {str(t): [round(a[0] / a[2], 7), round(a[1] / a[2], 7)]
                                           for t, a in acc.items()}
            os.makedirs(sr.CACHE, exist_ok=True)
            with open(ruta, "w") as f:
                json.dump(guardado, f)
        for atl, filas in guardado.items():
            out.setdefault(atl, {}).update({int(t): tuple(p) for t, p in filas.items()})
    return out


# ── Tiempos (curva de movimiento) ────────────────────────────────────────
def _corridas(serie, cond):
    """[(inicio, fin)] de los tramos consecutivos donde cond(x) es True."""
    out, ini = [], None
    for i, x in enumerate(serie):
        if cond(x) and ini is None:
            ini = i
        elif not cond(x) and ini is not None:
            out.append((ini, i))
            ini = None
    if ini is not None:
        out.append((ini, len(serie)))
    return out


def _arranque(mov, desde):
    """Primer segundo con 3+ jugadores en movimiento desde 'desde'."""
    for i in range(desde, len(mov)):
        if mov[i] >= 3:
            return i
    return desde


def detectar_tiempos(u0, mov):
    """Saques, entretiempo y final con la curva de movimiento (indices)."""
    s0 = sr.suavizar(mov, 20)
    s = [s0[min(len(s0) - 1, i + 10)] for i in range(len(s0))]  # centrado: sin retraso
    p90 = sorted(s)[int(len(s) * 0.9)] or 1.0
    quieto = _corridas(s, lambda x: x < 0.15 * p90)
    activos = [i for i, x in enumerate(s) if x >= 0.15 * p90]
    if not activos:
        return None
    a0, a1 = activos[0], activos[-1]
    largo = a1 - a0
    cand = [(i, f) for i, f in quieto if 360 <= f - i <= 1800 and a0 + 0.3 * largo <= i <= a0 + 0.75 * largo]
    if not cand:
        return None
    ht = max(cand, key=lambda r: r[1] - r[0])
    previas = [r for r in quieto if r[1] <= ht[0] - 40 * 60 and r[1] - r[0] >= 90]
    saque1 = _arranque(mov, previas[-1][1] if previas else a0)
    saque2 = _arranque(mov, ht[1])
    finales = [r for r in quieto if r[0] > saque2 + 40 * 60 and r[1] - r[0] >= 180]
    final = finales[0][0] if finales else a1
    semi = _corridas(s, lambda x: x < 0.35 * p90)
    pausas = [(i, f) for i, f in semi if 40 <= f - i <= 150 and
              ((saque1 < i < ht[0]) or (saque2 < i < final))]
    return {"saque1": saque1, "fin1": ht[0], "ht_fin": ht[1], "saque2": saque2, "final": final,
            "pausas": pausas}


def _refinar_saque(mov, i, cancha=None, u0=0):
    """El 'arranque' puede ser el trote corto del equipo yendo a sus puestos
    (o saliendo de la charla). Si despues de un trote de hasta 25 s se
    quedan quietos 20 s o mas, el saque es el arranque siguiente (dentro de
    los 2 minutos). Con posiciones: si justo antes estaban amontonados, se
    espera a que el equipo se abra y se quede quieto, y el saque es el
    arranque que sigue."""
    fin = next((j for j in range(i + 3, i + 26) if j + 20 <= len(mov) and max(mov[j:j + 20]) <= 1), None)
    if fin is not None:
        b = next((k for k in range(fin, min(len(mov), i + 120)) if mov[k] >= 3), None)
        if b is not None:
            i = b
    if cancha is None:
        return i
    for _ in range(2):
        abierto = cancha.apertura(u0 + i - 5, u0 + i)
        if abierto is None or abierto >= 6:
            break
        listo = None
        for t in range(u0 + i, u0 + i + 240):
            if all((cancha.apertura(k, k + 1) or 0) >= 8 and (cancha.vmed(k) or 9) <= 1.2 for k in range(t, t + 5)):
                listo = t + 5
                break
        if listo is None:
            break
        b = next((k for k in range(listo - u0, min(len(mov), listo - u0 + 180)) if mov[k] >= 3), None)
        if b is None:
            break
        i = b
    return i


# ── Posiciones ───────────────────────────────────────────────────────────
class Cancha:
    """Posiciones de Tigre segundo a segundo, en metros, con el eje de la
    cancha y la linea del medio de cada tiempo (ver marco())."""

    EN_CANCHA = 45.0     # m de la mediana del equipo: mas lejos es suplente/banco

    def __init__(self, posiciones, t0, t1):
        self.t0, self.T = t0, t1 - t0
        lats = sorted(p[0] for f in posiciones.values() for t, p in f.items() if t0 <= t < t1)
        lons = sorted(p[1] for f in posiciones.values() for t, p in f.items() if t0 <= t < t1)
        if len(lats) < 3000:
            raise ValueError("pocas posiciones")
        lat0, lon0 = lats[len(lats) // 2], lons[len(lons) // 2]
        kx = 111320 * math.cos(math.radians(lat0))
        self.P = []
        for f in posiciones.values():
            fila = [None] * self.T
            for t, p in f.items():
                k = t - t0
                if 0 <= k < self.T:
                    fila[k] = ((p[1] - lon0) * kx, (p[0] - lat0) * 110540)
            self.P.append(fila)
        self._foto, self._st = {}, {}
        self.ok = False

    # -- por segundo --
    def foto(self, t):
        """[(e, n, velocidad)] de los jugadores en cancha en el segundo t."""
        if t in self._foto:
            return self._foto[t]
        k = t - self.t0
        out = []
        if 2 <= k < self.T:
            pts = [(f[k], f[k - 2]) for f in self.P if f[k] is not None]
            if pts:
                me = statistics.median(p[0][0] for p in pts)
                mn = statistics.median(p[0][1] for p in pts)
                for p, q in pts:
                    if math.hypot(p[0] - me, p[1] - mn) < self.EN_CANCHA:
                        out.append((p[0], p[1], math.hypot(p[0] - q[0], p[1] - q[1]) / 2 if q else None))
        self._foto[t] = out
        return out

    def vmed(self, t):
        v = [x[2] for x in self.foto(t) if x[2] is not None]
        return statistics.median(v) if v else None

    def apertura(self, t0, t1):
        """Desvio (m) del equipo en su direccion mas abierta, promedio t0..t1."""
        vals = []
        for t in range(t0, t1):
            f = self.foto(t)
            if len(f) < 6:
                continue
            me = sum(p[0] for p in f) / len(f)
            mn = sum(p[1] for p in f) / len(f)
            sxx = sum((p[0] - me) ** 2 for p in f) / len(f)
            syy = sum((p[1] - mn) ** 2 for p in f) / len(f)
            sxy = sum((p[0] - me) * (p[1] - mn) for p in f) / len(f)
            tr, det = sxx + syy, sxx * syy - sxy * sxy
            vals.append(math.sqrt(max(0.0, tr / 2 + math.sqrt(max(0.0, tr * tr / 4 - det)))))
        return sum(vals) / len(vals) if vals else None

    def abrazo(self, t, radio=2.0):
        """(cuantos jugadores hay, como maximo, a menos de 'radio' m de uno;
        donde, en metros hacia el arco propio desde la linea del medio)."""
        k = t - self.t0
        if not 0 <= k < self.T:
            return 0, None
        pts = [f[k] for f in self.P if f[k] is not None]
        n, p = max(((sum(1 for q in pts if math.hypot(p[0] - q[0], p[1] - q[1]) < radio), p) for p in pts),
                   default=(0, None))
        if p is None or not self.ok:
            return n, None
        u = p[0] * self.ax[0] + p[1] * self.ax[1]
        return n, (self.s * u - self.h1 if t < self.ht_fin else -self.s * u - self.h2)

    # -- marco de la cancha --
    def marco(self, saque1, saque2, fin1, ht_fin, final):
        """Eje largo de la cancha (por donde se mueve el centro del equipo),
        que arco defiende Tigre en cada tiempo y donde esta la linea del
        medio (el frente de la formacion de cada saque)."""
        self.ht_fin = ht_fin
        cs = []
        for t in list(range(saque1, fin1)) + list(range(saque2, final)):
            f = self.foto(t)
            if len(f) >= 7:
                cs.append((sum(p[0] for p in f) / len(f), sum(p[1] for p in f) / len(f)))
        if len(cs) < 600:
            return False
        me = sum(c[0] for c in cs) / len(cs)
        mn = sum(c[1] for c in cs) / len(cs)
        sxx = sum((c[0] - me) ** 2 for c in cs)
        syy = sum((c[1] - mn) ** 2 for c in cs)
        sxy = sum((c[0] - me) * (c[1] - mn) for c in cs)
        th = 0.5 * math.atan2(2 * sxy, sxx - syy)
        self.ax = (math.cos(th), math.sin(th))
        U = lambda p: p[0] * self.ax[0] + p[1] * self.ax[1]
        V = lambda p: -p[0] * self.ax[1] + p[1] * self.ax[0]

        def formacion(t):
            """Ultimo momento (hasta 1 min antes del saque) con 7+ jugadores
            quietos, abiertos a lo ancho (25 m o mas) y con 8-45 m de fondo."""
            for t0 in range(t - 4, t - 60, -1):
                f = self.foto(t0)
                if len(f) < 7 or (self.vmed(t0) or 9) > 1.5:
                    continue
                u, v = [U(p) for p in f], [V(p) for p in f]
                if max(v) - min(v) >= 25 and 8 <= max(u) - min(u) <= 45:
                    return u
            return None

        p1, p2 = formacion(saque1), formacion(saque2)
        if p1 and p2:
            s = -1 if statistics.mean(p1) < statistics.mean(p2) else 1
        elif p1 or p2:
            medio = statistics.mean(c[0] * self.ax[0] + c[1] * self.ax[1] for c in cs)
            if p1:
                s = -1 if statistics.mean(p1) < medio else 1
            else:
                s = 1 if statistics.mean(p2) < medio else -1
        else:
            return False
        # s*U crece hacia el arco propio del 1T; la linea del medio es el
        # 2do jugador mas adelantado de la formacion del saque
        h1 = sorted(s * u for u in p1)[1] if p1 else None
        h2 = sorted(-s * u for u in p2)[1] if p2 else None
        self.s = s
        self.h1 = h1 if h1 is not None else -h2
        self.h2 = h2 if h2 is not None else -h1
        self.dos_saques = bool(p1 and p2)
        self.ok = True
        return True

    def estado(self, t):
        """Del equipo en t, en metros hacia el arco propio desde la linea del
        medio (positivo = mitad propia): n, centro, 2do mas adelantado, el
        mas atrasado, cuantos en su mitad (con 10 m de tolerancia) y la
        velocidad mediana. None si hay menos de 7 jugadores."""
        if t in self._st:
            return self._st[t]
        f = self.foto(t)
        out = None
        if len(f) >= 7:
            if t < self.ht_fin:
                su = sorted(self.s * (p[0] * self.ax[0] + p[1] * self.ax[1]) - self.h1 for p in f)
            else:
                su = sorted(-self.s * (p[0] * self.ax[0] + p[1] * self.ax[1]) - self.h2 for p in f)
            out = {"n": len(su), "centro": sum(su) / len(su), "frente": su[1], "fondo": su[-1],
                   "propia": sum(1 for x in su if x > -10), "vmed": self.vmed(t)}
        self._st[t] = out
        return out


# ── Goles ────────────────────────────────────────────────────────────────
def _formacion_saque(e):
    """El equipo parado como para sacar del medio: todos en su mitad, los de
    adelante sobre la linea, los de atras a no mas de ~38 m y quietos."""
    return (e is not None and -10 <= e["frente"] <= 10 and 8 <= e["fondo"] <= 38
            and 2 <= e["centro"] <= 24 and e["propia"] >= e["n"] - 1 and (e["vmed"] or 9) <= 1.4)


def _jugando(t, margen_ini=90, margen_fin=0):
    return (list(range(t["saque1"] + margen_ini, t["fin1"] + margen_fin)) +
            list(range(t["saque2"] + margen_ini, t["final"] + margen_fin)))


def _formaciones(cancha, t):
    """[(desde, hasta)] de los ratos (3 s o mas) con el equipo en formacion de saque."""
    runs = []
    for x in _jugando(t, 60, 30):
        if _formacion_saque(cancha.estado(x)):
            if runs and x - runs[-1][1] <= 4:
                runs[-1][1] = x
            else:
                runs.append([x, x])
    return [(a, b) for a, b in runs if b - a >= 3]


def _fin_de_juego(mov, u0, desde, hasta, primero=False):
    """Ultimo (o primer) segundo en [desde, hasta) donde se pasa de jugar
    (8 s con 4+ jugadores en movimiento en promedio) a quieto (12 s con 2 o
    menos)."""
    movat = lambda x: mov[x - u0] if 0 <= x - u0 < len(mov) else 0
    for x in (range(desde, hasta) if primero else range(hasta - 1, desde - 1, -1)):
        if sum(movat(k) for k in range(x - 8, x)) / 8 >= 4 and sum(movat(k) for k in range(x, x + 12)) / 12 <= 2:
            return x
    return None


def _goles_tigre(cancha, mov, u0, t, forms):
    """Festejos: 4 o mas jugadores de Tigre abrazados (a menos de 2 m entre
    si) durante el juego. Lejos de los saques y del final (ahi se juntan a
    charlar) y descartando las charlas largas con el juego parado (pausa de
    hidratacion)."""
    movat = lambda x: mov[x - u0] if 0 <= x - u0 < len(mov) else 0
    hits = []
    for x in _jugando(t, 90, -90):
        n, donde = cancha.abrazo(x)
        # en su propia mitad suele ser la barrera de un tiro libre
        if n >= 4 and (donde is None or donde <= 15):
            hits.append((x, n))
    grupos = []
    for h in hits:
        if grupos and h[0] - grupos[-1][-1][0] <= 30:
            grupos[-1].append(h)
        else:
            grupos.append([h])
    out = []
    for g in grupos:
        a, b = g[0][0], g[-1][0]
        maximo, seg = max(h[1] for h in g), len(g)
        antes = sum(movat(k) for k in range(a - 40, a - 10)) / 30
        if seg >= 30 and antes < 1.5:
            continue   # charla larga con el juego parado
        # el abrazo llega despues de la corrida del festejo: el gol es el
        # primer corte del juego en el minuto anterior
        gol = _fin_de_juego(mov, u0, a - 50, a + 1, primero=True) or a - 20
        sig = next((f for f in forms if b <= f[0] <= b + 240), None)
        p = min(2, maximo - 4) + (2 if seg >= 5 else 1 if seg >= 2 else 0) + (1 if sig else 0)
        out.append({"lado": "tigre", "gol": gol, "reinicio": sig[1] + 1 if sig else None,
                    "puntos": p, "abrazo": maximo, "abrazo_seg": seg})
    return out


def _goles_rival(cancha, mov, u0, t, forms):
    """Despues del gol rival, Tigre vuelve CAMINANDO (nadie trota) desde su
    area a la formacion del saque y espera ahi a que saque."""
    movat = lambda x: mov[x - u0] if 0 <= x - u0 < len(mov) else 0
    out = []
    for f0, f1 in forms:
        ta = None
        for k in range(f0 - 1, f0 - 150, -1):
            e = cancha.estado(k)
            if e and e["centro"] >= 28 and e["frente"] >= 5:
                ta = k
                break
        if ta is None:
            continue
        a0 = ta
        for k in range(ta, ta - 150, -1):
            e = cancha.estado(k)
            if not e or e["centro"] < 22:
                break
            a0 = k
        vuelta = [movat(k) for k in range(ta, f0)] or [0]
        mv = sum(vuelta) / len(vuelta)
        fondos = [cancha.estado(k)["fondo"] for k in range(a0, f0) if cancha.estado(k)]
        p = 0
        p += 3 if mv <= 1.2 else 1 if mv <= 2.5 else 0
        p += 1 if max(sr.suavizar(vuelta, 10)) <= 3 else 0
        p += 1 if f1 - f0 + 1 >= 15 else 0
        p += 1 if ta - a0 >= 20 else 0
        p += 1 if min(fondos, default=0) >= 30 else 0
        gol = _fin_de_juego(mov, u0, a0 - 30, ta + 1) or a0
        out.append({"lado": "rival", "gol": gol, "reinicio": f1 + 1, "puntos": p})
    # varias formaciones despues de la misma vuelta: queda la primera
    out.sort(key=lambda c: c["reinicio"])
    unicos = []
    for c in out:
        if unicos and c["gol"] == unicos[-1]["gol"]:
            continue
        unicos.append(c)
    return unicos


# ── Todo junto ───────────────────────────────────────────────────────────
def detectar(u0, mov, tramos=None, posiciones=None, goles_tigre=None, goles_rival=None,
             minutos_tigre=None, minutos_rival=None):
    """Tiempos y goles de un partido. Devuelve el dict para
    gps/videoSync/{cat}/{fecha}/eventos (None si no se encuentra el
    entretiempo). 'video' = segundo del video (puede ser negativo si el
    video arranca despues); None si no hay tramos."""
    t = detectar_tiempos(u0, mov)
    if not t:
        return None
    cancha = None
    if posiciones:
        try:
            cancha = Cancha(posiciones, u0 + t["saque1"] - 400, u0 + t["final"] + 400)
        except ValueError:
            cancha = None
    t["saque1"] = _refinar_saque(mov, t["saque1"], cancha, u0)
    t["saque2"] = _refinar_saque(mov, t["saque2"], cancha, u0)
    T = {k: u0 + v for k, v in t.items() if k != "pausas"}
    if cancha is not None and not cancha.marco(T["saque1"], T["saque2"], T["fin1"], T["ht_fin"], T["final"]):
        cancha = None

    def video(unix, dentro=0):
        if not tramos:
            return None
        off = sr.offset_en(tramos, unix + dentro)
        return None if off is None else int(round(unix + off))

    def minuto(unix):
        if unix < T["ht_fin"]:
            return max(1, int((unix - T["saque1"]) // 60) + 1)
        return 45 + max(1, int((unix - T["saque2"]) // 60) + 1)

    def inicio_min(m):
        return T["saque1"] + (m - 1) * 60 if m <= 45 else T["saque2"] + (m - 46) * 60

    ev = {"version": VERSION, "fuente": "gps+posiciones" if cancha else "gps",
          "generado": time.strftime("%Y-%m-%d %H:%M")}
    # el corte entre tramos puede caer segundos despues del saque: el saque
    # se busca dentro de su tiempo (+60 s) y los finales (-60 s)
    for clave, dentro in (("saque1", 60), ("fin1", -60), ("saque2", 60), ("final", -60)):
        ev[clave] = {"unix": T[clave], "video": video(T[clave], dentro),
                     "conf": "alta" if cancha else "media"}

    # candidatos
    if cancha:
        forms = _formaciones(cancha, T)
        cands = _goles_tigre(cancha, mov, u0, T, forms) + _goles_rival(cancha, mov, u0, T, forms)
    else:
        cands = [{"gol": u0 + i, "reinicio": u0 + f, "lado": None, "puntos": 0}
                 for i, f in t["pausas"]]

    goles, usados = [], set()

    def libre(c):
        # un mismo gol no se cuenta dos veces (festejo de Tigre y vuelta del rival)
        return id(c) not in usados and all(abs(c["gol"] - g["unix"]) > 60 for g in goles)

    def tomar(c, equipo, conf, minuto_info=None):
        usados.add(id(c))
        g = {"unix": int(c["gol"]), "reinicio": int(c["reinicio"]) if c.get("reinicio") else None,
             "video": video(c["gol"]),
             "equipo": equipo, "minuto": minuto(c["gol"]), "conf": conf}
        if minuto_info:
            g["minutoInformado"] = minuto_info
        goles.append(g)

    # 1) goles con minuto informado: el mejor candidato cerca de ese minuto
    for equipo, mins in (("tigre", minutos_tigre or []), ("rival", minutos_rival or [])):
        for m in sorted(mins):
            ini = inicio_min(m)
            mismo = [c for c in cands if libre(c) and c["lado"] in (equipo, None) and ini - 90 <= c["gol"] <= ini + 150]
            if mismo:
                c = max(mismo, key=lambda c: (c["puntos"], -abs(c["gol"] - ini - 30)))
                tomar(c, equipo, "alta" if c["lado"] == equipo and c["puntos"] >= 2 else "media", m)
            else:   # solo el minuto informado: el momento queda a +-1 minuto
                goles.append({"unix": ini + 30, "reinicio": None, "video": video(ini + 30), "equipo": equipo,
                              "minuto": m, "minutoInformado": m, "conf": "media"})
    # 2) los que faltan (sin minuto): los mejores candidatos de ese lado. Sin
    # el resultado, solo los festejos clarisimos de Tigre (la vuelta del
    # rival sola da demasiadas falsas).
    for equipo, total, mins in (("tigre", goles_tigre, minutos_tigre), ("rival", goles_rival, minutos_rival)):
        faltan = None if total is None else max(0, total - len(mins or []))
        libres = sorted((c for c in cands if c["lado"] in (equipo, None)), key=lambda c: -c["puntos"])
        if faltan is None:
            libres = [c for c in libres if c["puntos"] >= 5 and c["lado"] == equipo == "tigre"]
            faltan = len(libres)
        for c in libres:
            if faltan <= 0:
                break
            if libre(c):
                tomar(c, equipo, "media" if c["lado"] == equipo and c["puntos"] >= 5 else "baja")
                faltan -= 1
    ev["goles"] = sorted(goles, key=lambda g: g["unix"])
    return ev


def eventos_partido(st, opener, activity_ids, tramos, resultado=None, minutos_tigre=None,
                    minutos_rival=None, con_posiciones=True):
    """Pide a Catapult lo que hace falta y devuelve detectar(...).
    resultado = (goles_tigre, goles_rival) o None si no se sabe."""
    u0, mov = curva_movimiento(st, opener, activity_ids)
    if not mov:
        return None
    pos = posiciones_desde_api(st, opener, activity_ids) if con_posiciones else None
    gt, gr = resultado if resultado else (None, None)
    return detectar(u0, mov, tramos, pos, gt, gr, minutos_tigre, minutos_rival)
