# -*- coding: utf-8 -*-
"""PRUEBA (no guarda nada): saque del 1T, entretiempo, saque del 2T, final y
goles de cada partido con scripts/tiempos.py (GPS de Catapult + la
sincronizacion por ritmo para pasarlo a segundos del video).

Imprime cada momento con su link al video (arranca 5 s antes) para
chequearlo a ojo, lo compara con el arranque de cada tiempo que tiene
Catapult y los goles con los reales (minutos de COMET para los de Tigre y
los minutos del rival cargados en la citacion, si estan).

    python scripts\\probar_tiempos.py 4TA:F26 4TA:F29
    python scripts\\probar_tiempos.py 4TA:F26 --sin-comet       (como un VEO: solo el resultado)
    python scripts\\probar_tiempos.py 4TA:F26 --sin-resultado   (sin COMET ni resultado)

Necesita CATAPULT_USER / CATAPULT_PASS (movimiento y posiciones salen de
ahi; las posiciones quedan en cache). NO baja videos: usa la curva de video
que ya este en cache o, si no, los tramos guardados en el ultimo backup.
"""
import glob
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scrape_tablas as st  # noqa: E402
import sync_ritmo as sr  # noqa: E402
import tiempos as tp  # noqa: E402
from revisar_sync_ritmo import Catapult  # noqa: E402

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def leer(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def item(tabla, cat, n):
    t = (tabla or {}).get(cat)
    if isinstance(t, list):
        return t[n] if n < len(t) else None
    return (t or {}).get(str(n))


def mmss(seg):
    if seg is None:
        return "  -  "
    a = int(abs(seg))
    return f"{'-' if seg < 0 else ''}{a // 60}:{a % 60:02d}"


def main():
    args = sys.argv[1:]
    sin_comet, sin_resultado = "--sin-comet" in args, "--sin-resultado" in args
    casos = [a.split(":") for a in args if ":" in a] or [("4TA", "F26"), ("4TA", "F29")]
    efforts = leer(os.path.join(RAIZ, "data", "catapult_efforts.json"))
    b = leer(sorted(glob.glob(os.path.join(RAIZ, "data", "backups", "backup-*.json")))[-1])
    stats = b["stats"]
    sync_guardado = b.get("gps/videoSync") or (b.get("gps") or {}).get("videoSync") or {}
    cata = Catapult(os.environ["CATAPULT_USER"], os.environ["CATAPULT_PASS"])
    hora = lambda x: time.strftime('%H:%M:%S', time.gmtime(x - 3 * 3600))
    total = {"tig": 0, "tig_ok": 0, "riv": 0, "riv_ok": 0}

    for cat, fk in casos:
        n = int(fk[1:])
        print(f"\n=== {cat} {fk} ===")
        dia = (efforts.get(cat) or {}).get(fk) or {}
        url = (item(stats.get("links"), cat, n) or {}).get("par")
        vid = url.split("/")[-1].split("v=")[-1] if url else None
        aids = cata.actividades(cat, n)
        if not aids:
            print("  sin actividad de Catapult")
            continue
        # tramos: con la curva de video en cache (no se baja nada) o los guardados
        tramos = None
        cache = os.path.join(sr.CACHE, re.sub(r"\W", "_", vid or "")[:40] + ".json")
        if vid and os.path.exists(cache):
            v = sr.curva_video(url, None, None)
            u0, g = sr.curva_gps(sr.carreras_desde_api(st, cata.opener, aids))
            sync = sr.calcular(u0, g, v, dia.get("periodos"))
            tramos = sync and sync["tramos"]
        if not tramos:
            tramos = ((sync_guardado.get(cat) or {}).get(fk) or {}).get("tramos")
        if not tramos:
            print("  sin tramos de sincronizacion: se muestran solo las horas")
        else:
            for t in tramos:
                h = lambda x: "abierto" if x is None else hora(x)
                print(f"  tramo {h(t['desde'])} -> {h(t['hasta'])}  offset {t['offset']}")

        res = item(stats.get("results"), cat, n)
        comet = item(stats.get("partidos"), cat, n) or {}
        min_tigre = sorted(int(g["minuto"]) for g in comet.get("goles") or [] if g.get("minuto") and not g.get("autogol"))
        min_rival = (item(stats.get("matchData"), cat, n) or {}).get("minutosGolesRival") or []
        kw = {}
        if res and not sin_resultado:
            kw.update(resultado=(res[0], res[1]))
        if not sin_comet and not sin_resultado:
            kw["minutos_tigre"] = min_tigre
        ev = tp.eventos_partido(st, cata.opener, aids, tramos, **kw)
        if not ev:
            print("  no se encontro el entretiempo en la curva de movimiento")
            continue

        def link(seg):
            return f"https://youtu.be/{vid}?t={max(0, int(seg) - 5)}" if vid and seg is not None else ""

        p1 = next((p for p in dia.get("periodos") or [] if "rimer" in (p.get("name") or "")), {})
        p2 = next((p for p in dia.get("periodos") or [] if "egundo" in (p.get("name") or "")), {})
        refs = {"saque1": p1.get("start"), "fin1": p1.get("end"), "saque2": p2.get("start"), "final": p2.get("end")}
        nombres = {"saque1": "Saque 1T", "fin1": "Fin 1T (entretiempo)", "saque2": "Saque 2T", "final": "Final"}
        print(f"  fuente: {ev['fuente']} | resultado {res} | COMET Tigre {min_tigre} | rival (citacion) {min_rival or '-'}"
              + (" | SIN COMET" if sin_comet else "") + (" | SIN RESULTADO" if sin_resultado else ""))
        for k in ("saque1", "fin1", "saque2", "final"):
            e = ev[k]
            ref = f"   (Catapult: {e['unix'] - refs[k]:+.0f}s)" if refs[k] else ""
            print(f"  {nombres[k]:24} {hora(e['unix'])}  video {mmss(e['video']):>6}  {link(e['video'])}{ref}")
        for g in ev["goles"]:
            info = f" (informado {g['minutoInformado']}')" if g.get("minutoInformado") else ""
            print(f"  Gol {g['equipo']:5} {g['minuto']:3d}'  {hora(g['unix'])}  video {mmss(g['video']):>6}  "
                  f"conf {g['conf']:5}{info}  {link(g['video'])}")
        # comparacion con los reales: acierto si el minuto da a +-2
        for equipo, reales in (("tigre", min_tigre), ("rival", min_rival)):
            det = [g["minuto"] for g in ev["goles"] if g["equipo"] == equipo]
            usados, ok = set(), 0
            for m in reales:
                cand = [i for i, d in enumerate(det) if i not in usados and abs(d - m) <= 2]
                if cand:
                    usados.add(min(cand, key=lambda i: abs(det[i] - m)))
                    ok += 1
            if reales:
                total["tig" if equipo == "tigre" else "riv"] += len(reales)
                total["tig_ok" if equipo == "tigre" else "riv_ok"] += ok
                print(f"  -> goles de {equipo}: {ok}/{len(reales)} a +-2' (reales {reales}, detectados {det})")
    if total["tig"] or total["riv"]:
        print(f"\nTOTAL: Tigre {total['tig_ok']}/{total['tig']}  rival {total['riv_ok']}/{total['riv']} (a +-2 minutos)")
    print("\nCopia todo este texto y pasaselo a Claude.")


if __name__ == "__main__":
    main()
