# -*- coding: utf-8 -*-
"""Carga tiempos y goles (scripts/tiempos.py) en gps/videoSync/{cat}/{fecha}/eventos
para las fechas ya calibradas que todavia no los tienen.

Escribe SOLO el campo 'eventos' (no toca tramos ni kickoffs). Los goles de
confianza baja no se guardan. Las fechas que ya tienen 'eventos' se saltean
(--forzar las recalcula).

Uso (con FIREBASE_EMAIL/PASSWORD y CATAPULT_USER/PASS en el entorno):
    python scripts\\cargar_eventos.py                (todas las categorias)
    python scripts\\cargar_eventos.py 4TA 5TA        (solo esas)
    python scripts\\cargar_eventos.py --solo-ver     (calcula y muestra, no guarda)
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scrape_tablas as st  # noqa: E402
import tiempos as tp  # noqa: E402
from revisar_sync_ritmo import Catapult  # noqa: E402


def item(tabla, cat, n):
    t = (tabla or {}).get(cat)
    if isinstance(t, list):
        return t[n] if n < len(t) else None
    return (t or {}).get(str(n))


def main():
    args = sys.argv[1:]
    forzar, solo_ver = "--forzar" in args, "--solo-ver" in args
    cats = [a.upper() for a in args if not a.startswith("--")]
    login = lambda: st._tigre_fb_login(os.environ["FIREBASE_EMAIL"], os.environ["FIREBASE_PASSWORD"])
    tok, t_tok = login(), time.time()
    vs = st._tigre_fb_get("gps/videoSync", tok) or {}
    stats = {k: st._tigre_fb_get(f"stats/{k}", tok) for k in ("results", "partidos", "matchData")}
    cata = Catapult(os.environ["CATAPULT_USER"], os.environ["CATAPULT_PASS"])
    hechas = 0
    for cat in sorted(vs):
        if cats and cat not in cats:
            continue
        for fk in sorted(vs[cat], key=lambda f: int(f[1:])):
            d = vs[cat][fk] or {}
            n = int(fk[1:])
            if not d.get("tramos") or (d.get("eventos") and not forzar):
                continue
            print(f"{cat} {fk}: calculando ...", flush=True)
            try:
                # Firebase no guarda los null: el primer tramo llega sin 'desde' y el ultimo sin 'hasta'
                tramos = [{"desde": None, "hasta": None, **t} for t in d["tramos"]]
                aids = cata.actividades(cat, n)
                if not aids:
                    print("   sin actividad de Catapult")
                    continue
                res = item(stats["results"], cat, n)
                com = item(stats["partidos"], cat, n) or {}
                riv = (item(stats["matchData"], cat, n) or {}).get("minutosGolesRival") or []
                mins = [int(g["minuto"]) for g in com.get("goles") or [] if g and g.get("minuto") and not g.get("autogol")]
                ev = tp.eventos_partido(st, cata.opener, aids, tramos,
                                        resultado=tuple(res[:2]) if isinstance(res, list) and len(res) >= 2 else None,
                                        minutos_tigre=mins or None, minutos_rival=riv or None)
                if not ev:
                    print("   no se encontro el entretiempo en la curva de movimiento")
                    continue
                ev["goles"] = [g for g in ev.get("goles") or [] if g.get("conf") != "baja"]
                if time.time() - t_tok > 2400:
                    tok, t_tok = login(), time.time()
                if not solo_ver:
                    try:
                        st._tigre_fb_put(f"gps/videoSync/{cat}/{fk}/eventos", ev, tok)
                    except Exception:  # noqa -- token vencido: un reintento
                        tok, t_tok = login(), time.time()
                        st._tigre_fb_put(f"gps/videoSync/{cat}/{fk}/eventos", ev, tok)
                hechas += 1
                print(f"   [{'CALCULADO' if solo_ver else 'GUARDADO'}] {cat}:{fk} ({len(ev['goles'])} gol(es))", flush=True)
            except Exception as e:  # noqa -- una fecha mala no frena el resto
                print(f"   [ERROR] {cat}:{fk}: {str(e)[:150]}", flush=True)
    print(f"\nListo: {hechas} fecha(s).")


if __name__ == "__main__":
    main()
