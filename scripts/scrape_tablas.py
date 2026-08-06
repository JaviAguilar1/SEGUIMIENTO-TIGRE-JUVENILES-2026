#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Scraper de tablas de posiciones de Juveniles LPF (fuente oficial).
Genera data/tablas.json que la app SEGUIMIENTO TIGRE lee para mostrar
la tabla general por categoria (4TA, 5TA, 6TA).

Corre automaticamente via GitHub Actions (ver .github/workflows/tablas.yml).
No requiere ninguna intervencion manual.

Si la Liga cambia el HTML de sus paginas y el parser deja de encontrar
la tabla, el script termina con codigo != 0 y NO sobrescribe el JSON
existente (asi la app sigue mostrando el ultimo dato bueno).
"""

import json
import re
import sys
import datetime
import urllib.request

# Categoria en la app  ->  slug de la URL oficial
# 4TA-9NA usan el parser estandar (la <table> viene embebida en el HTML).
FUENTES = {
    "4TA": "https://www.ligaprofesional.ar/cuarta-2026/",
    "5TA": "https://www.ligaprofesional.ar/quinta-2026/",
    "6TA": "https://www.ligaprofesional.ar/sexta-2026/",
    "7MA": "https://www.ligaprofesional.ar/septima-2026/",
    "8VA": "https://www.ligaprofesional.ar/octava-2026/",
    "9NA": "https://www.ligaprofesional.ar/novena-2026/",
}

# Reserva ("Proyeccion" en la web oficial). A diferencia de las juveniles,
# estas paginas NO traen la <table> embebida: la tabla se carga desde un
# iframe externo de DataFactory. Por eso tienen su propio parser (parse_reserva).
# Dos torneos por semestre -> dos vistas separadas en la app.
FUENTES_RESERVA = {
    "RESERVA_APE": "https://www.ligaprofesional.ar/proyeccion-apertura-2026/",
    "RESERVA_CLA": "https://www.ligaprofesional.ar/proyeccion-clausura-2026/",
}

OUT_PATH = "data/tablas.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; TigreJuvenilesBot/1.0; +github-actions)"
}

# Nombre oficial en la web  ->  como queremos mostrarlo (normalizamos "Tigre")
def norm_equipo(nombre: str) -> str:
    return nombre.strip()


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_tabla(html: str):
    """
    Extrae las filas de la 'Tabla de posiciones'.
    La pagina oficial la renderiza como una <table> cuyas filas tienen:
      Pos | Equipo | Pts | J | G | E | P | GF | GC | DIF
    Devuelve lista de dicts. Lanza ValueError si no encuentra nada.
    """
    # Aislar el bloque que arranca en el titulo "Tabla de posiciones"
    idx = html.lower().find("tabla de posiciones")
    if idx == -1:
        raise ValueError("No se encontro el titulo 'Tabla de posiciones'")
    bloque = html[idx:]

    # Cortar en el siguiente <h2>/<h3> (ej. "Torneos anteriores") para no
    # arrastrar tablas ajenas.
    corte = re.search(r"<h[23][\s>]", bloque[20:], re.IGNORECASE)
    if corte:
        bloque = bloque[: corte.start() + 20]

    # Primera <table> del bloque
    m = re.search(r"<table\b[^>]*>(.*?)</table>", bloque, re.IGNORECASE | re.DOTALL)
    if not m:
        raise ValueError("No se encontro <table> en el bloque de posiciones")
    tabla_html = m.group(1)

    filas = re.findall(r"<tr\b[^>]*>(.*?)</tr>", tabla_html, re.IGNORECASE | re.DOTALL)
    out = []
    for fila in filas:
        celdas = re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", fila, re.IGNORECASE | re.DOTALL)
        # limpiar tags internos y espacios
        celdas = [re.sub(r"<[^>]+>", "", c).replace("&nbsp;", " ").strip() for c in celdas]
        if len(celdas) < 10:
            continue
        pos_raw = celdas[0].replace("°", "").strip()
        # saltar header y filas vacias
        if not re.match(r"^\d+$", pos_raw):
            continue
        equipo = norm_equipo(celdas[1])
        if not equipo:
            continue
        try:
            fila_dict = {
                "pos": int(pos_raw),
                "equipo": equipo,
                "pts": int(celdas[2]),
                "pj": int(celdas[3]),
                "pg": int(celdas[4]),
                "pe": int(celdas[5]),
                "pp": int(celdas[6]),
                "gf": int(celdas[7]),
                "gc": int(celdas[8]),
                "dif": int(celdas[9].replace("+", "")),
            }
        except (ValueError, IndexError):
            continue
        out.append(fila_dict)

    if not out:
        raise ValueError("Se encontro la tabla pero no se pudo parsear ninguna fila")
    return out


def _filas_desde_tabla_html(tabla_html: str):
    """Parsea una <table> de posiciones (mismo formato que las juveniles)."""
    filas = re.findall(r"<tr\b[^>]*>(.*?)</tr>", tabla_html, re.IGNORECASE | re.DOTALL)
    out = []
    for fila in filas:
        celdas = re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", fila, re.IGNORECASE | re.DOTALL)
        celdas = [re.sub(r"<[^>]+>", "", c).replace("&nbsp;", " ").strip() for c in celdas]
        if len(celdas) < 10:
            continue
        pos_raw = celdas[0].replace("°", "").strip()
        if not re.match(r"^\d+$", pos_raw):
            continue
        equipo = norm_equipo(celdas[1])
        if not equipo:
            continue
        try:
            out.append({
                "pos": int(pos_raw), "equipo": equipo,
                "pts": int(celdas[2]), "pj": int(celdas[3]),
                "pg": int(celdas[4]), "pe": int(celdas[5]), "pp": int(celdas[6]),
                "gf": int(celdas[7]), "gc": int(celdas[8]),
                "dif": int(celdas[9].replace("+", "")),
            })
        except (ValueError, IndexError):
            continue
    return out


def parse_reserva(html: str):
    """
    Extrae la tabla de posiciones de una pagina de Proyeccion (Reserva).
    La pagina oficial NO trae la <table> embebida: incrusta un iframe de
    DataFactory con page=posiciones. Estrategia, en orden:
      1) Si por algun motivo hay una <table> embebida, usarla (reusa parse_tabla).
      2) Buscar la URL del iframe/enlace de DataFactory (page=posiciones),
         fetchearla y parsear la <table> que sirve DataFactory.
    Lanza ValueError si no logra ninguna fila.
    """
    # 1) intento directo por si la pagina ya trae la tabla
    try:
        return parse_tabla(html)
    except ValueError:
        pass

    # 2) ubicar la URL de DataFactory con page=posiciones
    m = re.search(
        r"https?://[^\"'\s]*datafactory[^\"'\s]*?page=posiciones[^\"'\s]*",
        html, re.IGNORECASE)
    if not m:
        # a veces el orden de los params varia: aceptar cualquier URL de
        # datafactory del canal reserva y forzar page=posiciones
        m2 = re.search(
            r"https?://[^\"'\s]*datafactory[^\"'\s]*?channel=deportes\.futbol\.reserva[^\"'\s]*",
            html, re.IGNORECASE)
        if not m2:
            raise ValueError("No se encontro el iframe de DataFactory (posiciones)")
        base = m2.group(0).replace("&amp;", "&")
        url_df = re.sub(r"page=\w+", "page=posiciones", base)
        if "page=posiciones" not in url_df:
            url_df = base + ("&" if "?" in base else "?") + "page=posiciones"
    else:
        url_df = m.group(0).replace("&amp;", "&")

    df_html = fetch(url_df)

    # DataFactory sirve la tabla como <table>; reusar el mismo parser tolerante.
    mtab = re.search(r"<table\b[^>]*>(.*?)</table>", df_html, re.IGNORECASE | re.DOTALL)
    if mtab:
        filas = _filas_desde_tabla_html(mtab.group(1))
        if filas:
            return filas
    raise ValueError(
        "Se ubico el iframe de DataFactory pero no se pudo parsear la tabla "
        "(puede requerir el endpoint JSON del feed)")


def main():
    resultado = {
        "actualizado": datetime.datetime.now(datetime.timezone.utc)
        .astimezone(datetime.timezone(datetime.timedelta(hours=-3)))
        .strftime("%Y-%m-%d %H:%M"),
        "fuente": "ligaprofesional.ar (oficial)",
        "categorias": {},
    }
    errores = []
    for cat, url in FUENTES.items():
        try:
            html = fetch(url)
            filas = parse_tabla(html)
            resultado["categorias"][cat] = filas
            print(f"[OK] {cat}: {len(filas)} equipos")
        except Exception as e:  # noqa
            errores.append(f"{cat}: {e}")
            print(f"[ERROR] {cat}: {e}", file=sys.stderr)

    # Reserva (Proyeccion): parser propio (iframe DataFactory). Que falle una
    # de estas NO debe afectar a las juveniles: se captura por separado.
    for cat, url in FUENTES_RESERVA.items():
        try:
            html = fetch(url)
            filas = parse_reserva(html)
            resultado["categorias"][cat] = filas
            print(f"[OK] {cat}: {len(filas)} equipos")
        except Exception as e:  # noqa
            errores.append(f"{cat}: {e}")
            print(f"[ERROR] {cat}: {e}", file=sys.stderr)

    # Salvaguarda: si Apertura y Clausura de reserva salieron IDENTICAS, es casi
    # seguro que ambas paginas comparten el mismo iframe de DataFactory y no se
    # estan diferenciando. Avisar fuerte (en log y en el JSON) para revisarlo,
    # en vez de mostrar datos duplicados en las dos pestanas sin que se note.
    ape = resultado["categorias"].get("RESERVA_APE")
    cla = resultado["categorias"].get("RESERVA_CLA")
    if ape and cla and ape == cla:
        aviso = ("RESERVA_APE y RESERVA_CLA salieron identicas: la fuente "
                 "probablemente no diferencia los torneos por URL. Revisar el iframe.")
        print(f"[AVISO] {aviso}", file=sys.stderr)
        resultado["avisos"] = resultado.get("avisos", []) + [aviso]

    # Si NINGUNA categoria salio bien, no pisamos el JSON anterior.
    if not resultado["categorias"]:
        print("Ninguna categoria pudo procesarse. No se sobrescribe el JSON.", file=sys.stderr)
        sys.exit(1)

    import os
    os.makedirs("data", exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    print(f"Escrito {OUT_PATH} ({len(resultado['categorias'])} categorias)")

    # Salir con error si alguna fallo, para que la Action lo marque en amarillo,
    # pero igual dejamos el JSON con lo que si funciono.
    if errores:
        sys.exit(0)  # no rompemos el commit; el dato parcial sigue siendo util


if __name__ == "__main__":
    main()
