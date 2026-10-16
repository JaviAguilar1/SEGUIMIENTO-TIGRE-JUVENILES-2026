# -*- coding: utf-8 -*-
"""PRUEBA (no guarda nada): detectar saque del 1T, entretiempo, saque del 2T,
final y posibles goles, solo con el GPS de Catapult + la sincronizacion por
ritmo (sync_ritmo.py) para pasarlo a segundos del video.

Como se detecta (curva de "jugadores en movimiento" segundo a segundo):
  - Entretiempo: la pausa larga (6 a 30 min) en el medio de la actividad.
  - Saque 1T / 2T: el arranque de la actividad despues de la ultima pausa
    de al menos 90 s antes del 1T, y al final del entretiempo.
  - Final: la primera pausa larga (3 min o mas) despues del 2T.
  - Posibles goles: pausas de 40 a 150 s durante el juego. Si COMET tiene el
    minuto del gol de Tigre, se marca la pausa mas cercana a ese minuto.

Imprime cada momento con su link al video (arranca 5 s antes) para
chequearlo a ojo, y lo compara con lo que tiene Catapult como arranque de
cada tiempo.

    python scripts\\probar_tiempos.py 4TA:F26 4TA:F29

Necesita CATAPULT_USER / CATAPULT_PASS (la curva de movimiento sale de ahi).
"""
import glob
import json
import os
import statistics
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scrape_tablas as st  # noqa: E402
import sync_ritmo as sr  # noqa: E402
from revisar_sync_ritmo import Catapult  # noqa: E402

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
BANDAS_MOVIMIENTO = "3,4,5,6,7,8"   # trotando o mas rapido


def leer(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def corridas(serie, cond):
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


def detectar(u0, mov):
    """Devuelve dict con saque1, entretiempo (ini, fin), saque2, final y pausas (unix)."""
    s0 = sr.suavizar(mov, 20)
    s = [s0[min(len(s0) - 1, i + 10)] for i in range(len(s0))]  # centrado: sin retraso
    p90 = sorted(s)[int(len(s) * 0.9)] or 1.0
    quieto = corridas(s, lambda x: x < 0.15 * p90)
    activos = [i for i, x in enumerate(s) if x >= 0.15 * p90]
    if not activos:
        return None
    a0, a1 = activos[0], activos[-1]
    largo = a1 - a0
    cand = [(i, f) for i, f in quieto if 360 <= f - i <= 1800 and a0 + 0.3 * largo <= i <= a0 + 0.75 * largo]
    if not cand:
        return None
    ht = max(cand, key=lambda r: r[1] - r[0])

    def arranque(desde):
        """Primer segundo con 3+ jugadores en movimiento desde 'desde'."""
        for i in range(desde, len(mov)):
            if mov[i] >= 3:
                return i
        return desde

    previas = [r for r in quieto if r[1] <= ht[0] - 40 * 60 and r[1] - r[0] >= 90]
    saque1 = arranque(previas[-1][1] if previas else a0)
    saque2 = arranque(ht[1])
    finales = [r for r in quieto if r[0] > saque2 + 40 * 60 and r[1] - r[0] >= 180]
    final = finales[0][0] if finales else a1
    semi = corridas(s, lambda x: x < 0.35 * p90)
    pausas = [(i, f) for i, f in semi if 40 <= f - i <= 150 and
              ((saque1 < i < ht[0]) or (saque2 < i < final))]
    return {"saque1": u0 + saque1, "ht": (u0 + ht[0], u0 + ht[1]), "saque2": u0 + saque2,
            "final": u0 + final, "pausas": [(u0 + i, f - i) for i, f in pausas]}


def main():
    casos = [a.split(":") for a in sys.argv[1:] if ":" in a] or [("4TA", "F26"), ("4TA", "F29")]
    efforts = leer(os.path.join(RAIZ, "data", "catapult_efforts.json"))
    b = leer(sorted(glob.glob(os.path.join(RAIZ, "data", "backups", "backup-*.json")))[-1])
    links, partidos = b["stats"].get("links") or {}, b["stats"].get("partidos") or {}
    cata = Catapult(os.environ["CATAPULT_USER"], os.environ["CATAPULT_PASS"])
    ffmpeg = st.imageio_ffmpeg.get_ffmpeg_exe()

    def item(tabla, cat, n):
        t = tabla.get(cat)
        if isinstance(t, list):
            return t[n] if n < len(t) else None
        return (t or {}).get(str(n))

    for cat, fk in casos:
        n = int(fk[1:])
        print(f"\n=== {cat} {fk} ===")
        dia = (efforts.get(cat) or {}).get(fk) or {}
        url = (item(links, cat, n) or {}).get("par")
        if not url:
            print("  sin link de video")
            continue
        vid = url.split("/")[-1].split("v=")[-1]
        aids = cata.actividades(cat, n)
        v = sr.curva_video(url, st.yt_dlp, ffmpeg)
        u0, g = sr.curva_gps(sr.carreras_desde_api(st, cata.opener, aids))
        sync = sr.calcular(u0, g, v, dia.get("periodos"))
        if not sync:
            print("  no encastra el video, no se puede pasar a segundos de video")
            continue
        for t in sync["tramos"]:
            hora = lambda x: "abierto" if x is None else time.strftime('%H:%M:%S', time.gmtime(x - 3 * 3600))
            print(f"  tramo {hora(t['desde'])} -> {hora(t['hasta'])}  offset {t['offset']}  ({t['ventanas']} ventanas)")
        m0, mov = sr.curva_gps(sr.carreras_desde_api(st, cata.opener, aids, BANDAS_MOVIMIENTO))
        d = detectar(m0, mov)
        if not d:
            print("  no se encontro el entretiempo en la curva de movimiento")
            continue

        def linea(nombre, unix, ref=None):
            # el corte entre tramos puede caer segundos despues del saque:
            # el saque se busca dentro de su tiempo (+60 s), los finales -60 s
            dentro = 60 if nombre.startswith("Saque") else -60 if nombre.startswith(("Fin", "Final")) else 0
            seg = unix + sr.offset_en(sync["tramos"], unix + dentro)
            sg, a = ("-" if seg < 0 else ""), int(abs(seg))
            txt = (f"  {nombre:24} {time.strftime('%H:%M:%S', time.gmtime(unix - 3 * 3600))}  video "
                   f"{sg}{a // 60}:{a % 60:02d}  https://youtu.be/{vid}?t={max(0, int(seg) - 5)}")
            if ref:
                txt += f"   (Catapult: {unix - ref:+.0f}s)"
            print(txt)

        p1 = next((p for p in dia.get("periodos") or [] if "rimer" in (p.get("name") or "")), {})
        p2 = next((p for p in dia.get("periodos") or [] if "egundo" in (p.get("name") or "")), {})
        linea("Saque 1T", d["saque1"], p1.get("start"))
        linea("Fin 1T (entretiempo)", d["ht"][0], p1.get("end"))
        linea("Saque 2T", d["saque2"], p2.get("start"))
        linea("Final", d["final"], p2.get("end"))
        comet = item(partidos, cat, n) or {}
        goles = [g for g in comet.get("goles") or [] if g.get("minuto") and not g.get("autogol")]
        esperados = []
        for gl in goles:
            mnt = int(gl["minuto"])
            base = d["saque1"] + (mnt - 0.5) * 60 if mnt <= 45 else d["saque2"] + (mnt - 45.5) * 60
            esperados.append((base, f"gol {gl.get('nombre', '')} min {mnt}"))
        print(f"  Pausas de 40-150 s (posibles goles): {len(d['pausas'])}  | COMET: {len(goles)} gol(es) de Tigre con minuto, rival {comet.get('golesRival', '?')}")
        usadas = set()
        for base, nombre in esperados:
            if not d["pausas"]:
                break
            mejor = min(d["pausas"], key=lambda p: abs(p[0] - base))
            usadas.add(mejor)
            linea(f"{nombre[:22]}", mejor[0])
            print(f"      -> pausa de {mejor[1]} s, a {mejor[0] - base:+.0f} s del minuto informado")
        for p in sorted(d["pausas"], key=lambda p: -p[1])[:6]:
            if p not in usadas:
                linea(f"pausa {p[1]} s", p[0])
    print("\nCopia todo este texto y pasaselo a Claude.")


if __name__ == "__main__":
    main()
