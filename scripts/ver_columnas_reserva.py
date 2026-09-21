# -*- coding: utf-8 -*-
"""Diagnostico de una sola vez: imprime las columnas que trae la pagina de
planteles de RESERVA en statfutbol, para confirmar si ahi estan los partidos
jugados y los minutos de cada jugador (en las juveniles si estan; el parser de
Reserva nunca las leyo).

    python scripts\\ver_columnas_reserva.py

No escribe nada en ningun lado, solo mira e imprime.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scrape_tablas as st  # noqa: E402


def main():
    base = "afaplantelesCALP2026"      # Proyeccion Apertura (ver FUENTES_RESERVA)
    equipos = st.fetch_statfutbol_reserva_equipos(base)
    m = st.statfutbol_match_equipo("TIGRE", equipos)
    if not m:
        print("[ERROR] No se encontro a Tigre en el listado de planteles de Reserva.")
        return 1
    team_id, nombre = m
    print("Equipo: %s (id %s)\n" % (nombre, team_id))

    html = st.fetch_post("%s%sResolucion.php" % (st.STATFUTBOL_BASE, base), {"player": team_id})

    # Encabezados de la tabla, para ver que columna es cada una
    heads = re.findall(r"<th[^>]*>(.*?)</th>", html, re.DOTALL)
    heads = [re.sub(r"<[^>]+>", "", h).strip() for h in heads]
    print("ENCABEZADOS: %s\n" % (heads or "(no se encontraron)"))

    filas = re.findall(r'<tr class="trConsultParaJugadores">(.*?)</tr>', html, re.DOTALL)
    print("Filas de jugador: %d\n" % len(filas))
    for fila in filas[:5]:
        celdas = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", c)).strip()
                  for c in re.findall(r"<td[^>]*>(.*?)</td>", fila, re.DOTALL)]
        print("  " + " | ".join("[%d] %s" % (i, c) for i, c in enumerate(celdas[:8])))
    print("\n=> En las juveniles la celda [1] es PARTIDOS JUGADOS y la [2] MINUTOS.")
    print("   Si aca pasa lo mismo, con leer esas dos celdas Reserva tiene minutos.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
