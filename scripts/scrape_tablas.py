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
import os
import re
import sys
import datetime
import urllib.request
import urllib.parse
import http.cookiejar

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

# Resultado por fecha de Tigre (partido por partido): fuente sabadogol.com.ar.
# La LPF oficial no sirve esto en HTML plano (lo carga con JS via un widget de
# terceros que no se puede scrapear simple), pero sabadogol.com.ar muestra el
# mismo fixture en una tabla comun. FIXTURE_URL recibe por POST el anio (a),
# la categoria (c=6 es "Juveniles LPF") y el torneo puntual (t), que ya viene
# separado por division (a diferencia de "d", que es redundante con "t" pero
# lo mandamos igual porque el form original lo espera).
FIXTURE_URL = "https://sabadogol.com.ar/fixture.php"
FIXTURE_ANIO = "3"     # 2026
FIXTURE_CAT = "6"      # Juveniles LPF
FIXTURE_TORNEOS = {
    "4TA": ("3", "5"),
    "5TA": ("4", "9"),
    "6TA": ("5", "10"),
    "7MA": ("6", "11"),
    "8VA": ("7", "12"),
    "9NA": ("8", "13"),
}

# Nombre oficial en la web  ->  como queremos mostrarlo (normalizamos "Tigre")
def norm_equipo(nombre: str) -> str:
    return nombre.strip()


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def fetch_post(url: str, data: dict) -> str:
    body = urllib.parse.urlencode(data).encode()
    headers = dict(HEADERS)
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _quitar_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s).strip()


def parse_fixture_cat(html: str):
    """
    Extrae, de una respuesta de sabadogol.com.ar/fixture.php, los partidos de
    TIGRE fecha por fecha. La pagina trae las 35 fechas en una sola respuesta
    (pestanas que ya vienen todas armadas en el HTML), cada una precedida por
    un comentario "<!-- N -->" con el numero de fecha.
    Devuelve dict {fecha:int -> {"gf":int,"gc":int,"rival":str}}.
    Partidos todavia no jugados (sin marcador "N - N") se omiten.
    """
    partes = re.split(r"<!--\s*(\d+)\s*-->", html)
    out = {}
    # partes[0] es lo anterior a la primera fecha; despues alterna numero/bloque
    for i in range(1, len(partes), 2):
        try:
            fecha = int(partes[i])
        except ValueError:
            continue
        bloque = partes[i + 1]
        m = re.search(r'<table class="table">(.*?)</table>', bloque, re.DOTALL)
        if not m:
            continue
        filas = re.findall(
            r'<tr>\s*<td class="text-end[^"]*"[^>]*>(.*?)</td>\s*'
            r'<td[^>]*><div[^>]*>([^<]*)</div></td>\s*'
            r'<td class="text-start[^"]*"[^>]*>(.*?)</td>\s*</tr>',
            m.group(1), re.DOTALL)
        for local_raw, marcador, visitante_raw in filas:
            local = _quitar_tags(local_raw)
            visitante = _quitar_tags(visitante_raw)
            es_local = "TIGRE" in local.upper()
            es_visitante = "TIGRE" in visitante.upper()
            if not (es_local or es_visitante):
                continue
            gm = re.match(r"^\s*(\d+)\s*-\s*(\d+)\s*$", marcador.strip())
            if not gm:
                continue  # todavia no jugado
            g1, g2 = int(gm.group(1)), int(gm.group(2))
            if es_local:
                out[fecha] = {"gf": g1, "gc": g2, "rival": visitante}
            else:
                out[fecha] = {"gf": g2, "gc": g1, "rival": local}
    return out


# ── futdetail (panel privado del club) ──────────────────────────────────
# Login clasico por formulario (usuario/password -> cookie de sesion PHP).
# Las credenciales viven en GitHub Secrets (FUTDETAIL_USER, FUTDETAIL_PASS)
# y llegan aca como variables de entorno; nunca se escriben en el codigo.
# El listado de partidos (con goles_local/goles_visitante ya incluidos) se
# pide a "partidos_consulta_procesos.php" por POST, autenticado con esa
# misma sesion. Si faltan las credenciales, esta parte simplemente se
# saltea (no rompe el resto del scraper).
FUTDETAIL_BASE = "https://futdetail.com.ar/futdetail_web_tigre/"
FUTDETAIL_LOGIN_URL = FUTDETAIL_BASE + "login.php"
FUTDETAIL_PARTIDOS_URL = FUTDETAIL_BASE + "partidos_consulta_procesos.php"
FUTDETAIL_TEMPORADA_ID = "3"  # 2026, mismo criterio que el desplegable del panel
FUTDETAIL_DIVISIONES = {
    "4TA": "3",
    "5TA": "4",
    "6TA": "5",
    "7MA": "6",
    "8VA": "7",
    "9NA": "8",
}


def futdetail_login(usuario: str, password: str):
    """Inicia sesion en futdetail y devuelve un opener con la cookie ya
    seteada. Lanza RuntimeError si el usuario/password son invalidos."""
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.open(urllib.request.Request(FUTDETAIL_LOGIN_URL, headers=HEADERS), timeout=30)
    body = urllib.parse.urlencode({
        "usuario": usuario, "password": password, "password_nueva": "",
    }).encode()
    headers = dict(HEADERS)
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    resp = opener.open(urllib.request.Request(FUTDETAIL_LOGIN_URL, data=body, headers=headers), timeout=30)
    texto = resp.read().decode("utf-8", errors="replace")
    if "invalido" in texto.lower():
        raise RuntimeError("usuario/password de futdetail invalidos")
    return opener


def fetch_futdetail_partidos(opener, id_division: str):
    """Pide el listado de partidos de una division ya logueado. Devuelve
    la lista cruda tal cual la sirve el endpoint (lista de dicts)."""
    body = urllib.parse.urlencode({
        "opcion": "4", "id_division": id_division, "temporada_id": FUTDETAIL_TEMPORADA_ID,
    }).encode()
    headers = dict(HEADERS)
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    resp = opener.open(urllib.request.Request(FUTDETAIL_PARTIDOS_URL, data=body, headers=headers), timeout=30)
    return json.loads(resp.read().decode("utf-8", errors="replace"))


def parse_futdetail_partidos(filas):
    """
    Convierte la lista cruda de partidos_consulta_procesos.php en
    {fecha:int -> {"gf":int,"gc":int,"rival":str, ...links...}}. "localia"
    dice si Tigre jugo de local (L) o visitante (V), y con eso se sabe cual
    gol es cual. Partidos sin resultado cargado (todavia no jugados) se
    omiten. De paso se traen los links que ya haya cargados (video del
    partido, resumen, analisis propio, informe, pelota parada, gps, charla
    DT, arenga) para no tener que cargarlos a mano dos veces.

    IMPORTANTE: futdetail numera "fecha_nro" por separado dentro de CADA
    competencia -- la fecha 1 de "Torneo LPF" y la fecha 1 de "Amistosos"
    son partidos distintos que comparten numero. Sin filtrar por
    competencia, los amistosos pisaban las fechas reales del torneo
    (confirmado con datos reales: fechas 1-5 de 4TA traian rivales que ni
    juegan la LPF, ej. "Excursionistas", "San Martin de Burzaco" -- eran
    amistosos, no el torneo). El campo crudo se llama
    "competencia_descripcion" (confirmado inspeccionando la respuesta real
    del endpoint).
    """
    out = {}
    for f in filas:
        competencia = str(f.get("competencia_descripcion", "")).strip().lower()
        if competencia != "torneo lpf":
            continue  # amistosos u otra competencia -- no es el torneo que seguimos
        try:
            fecha = int(str(f.get("fecha_nro", "")).strip())
        except (TypeError, ValueError):
            continue
        gl, gv = f.get("goles_local"), f.get("goles_visitante")
        if gl in (None, "", "None") or gv in (None, "", "None"):
            continue  # sin resultado cargado todavia
        try:
            gl, gv = int(gl), int(gv)
        except (TypeError, ValueError):
            continue
        localia = str(f.get("localia", "")).strip().upper()
        # "equipo_rival" es el id numerico del club (la web lo usa para el
        # <select>); "nombre" es el nombre legible. Nos quedamos con el
        # nombre, y si por algun motivo viene vacio usamos el id como ultimo
        # recurso (mejor un numero que nada).
        rival = (f.get("nombre") or f.get("equipo_rival") or "").strip()
        links = {
            "partido_url": (f.get("partido_url") or "").strip(),
            "momentos_destacados_url": (f.get("momentos_detacados_url") or "").strip(),
            "analisis_url": (f.get("analisis_url") or "").strip(),
            "rival_url": (f.get("rival_url") or "").strip(),
            "informe_partido": (f.get("informe_partido") or "").strip(),
            "pelota_parada_url": (f.get("pelota_parada_url") or "").strip(),
            "gps_url": (f.get("gps_url") or "").strip(),
            "charla_dt": (f.get("charla_dt") or "").strip(),
            "arenga_jugadores_url": (f.get("arenga_jugadores_url") or "").strip(),
        }
        if localia == "L":
            out[fecha] = {"gf": gl, "gc": gv, "rival": rival, **links}
        elif localia == "V":
            out[fecha] = {"gf": gv, "gc": gl, "rival": rival, **links}
        # localia distinto de L/V: no deberia pasar, se ignora la fila
    return out


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
        "fuente_fixture": "sabadogol.com.ar",
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

    # Resultados de Tigre partido por partido (4TA-9NA), fuente sabadogol.com.ar.
    # Independiente de la tabla de posiciones: si esto falla, no afecta lo de arriba.
    resultado["fixture"] = {}
    for cat, (d, t) in FIXTURE_TORNEOS.items():
        try:
            html = fetch_post(FIXTURE_URL, {"a": FIXTURE_ANIO, "c": FIXTURE_CAT, "d": d, "t": t})
            partidos = parse_fixture_cat(html)
            if not partidos:
                raise ValueError("no se encontro ningun partido de Tigre")
            resultado["fixture"][cat] = partidos
            print(f"[OK] fixture {cat}: {len(partidos)} fechas")
        except Exception as e:  # noqa
            errores.append(f"fixture {cat}: {e}")
            print(f"[ERROR] fixture {cat}: {e}", file=sys.stderr)

    # Resultados de Tigre partido por partido segun futdetail (panel privado).
    # Necesita FUTDETAIL_USER / FUTDETAIL_PASS como variables de entorno (las
    # pone la GitHub Action desde los secrets del repo). Si no estan seteadas
    # -todavia no se configuraron, o se corre local sin ellas- se saltea
    # entero sin marcar error: es una fuente opcional, no bloquea nada.
    usuario_fd = os.environ.get("FUTDETAIL_USER")
    password_fd = os.environ.get("FUTDETAIL_PASS")
    if usuario_fd and password_fd:
        resultado["fixture_futdetail"] = {}
        try:
            opener_fd = futdetail_login(usuario_fd, password_fd)
            print("[OK] futdetail: login correcto")
            for cat, id_division in FUTDETAIL_DIVISIONES.items():
                try:
                    filas = fetch_futdetail_partidos(opener_fd, id_division)
                    partidos = parse_futdetail_partidos(filas)
                    resultado["fixture_futdetail"][cat] = partidos
                    print(f"[OK] futdetail {cat}: {len(partidos)} fechas")
                except Exception as e:  # noqa
                    errores.append(f"futdetail {cat}: {e}")
                    print(f"[ERROR] futdetail {cat}: {e}", file=sys.stderr)
        except Exception as e:  # noqa
            errores.append(f"futdetail login: {e}")
            print(f"[ERROR] futdetail login: {e}", file=sys.stderr)
    else:
        print("[AVISO] FUTDETAIL_USER/FUTDETAIL_PASS no configurados, se omite futdetail")

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
