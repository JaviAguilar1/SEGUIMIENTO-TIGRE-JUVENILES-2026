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
import urllib.error
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
# estas paginas ya NO traen ninguna <table> embebida (confirmado 2026-08-18,
# re-chequeado 2026-08-31: sigue igual): todo se dibuja con un <opta-widget>
# por JS. Por eso la tabla de posiciones de Reserva sale de statfutbol.com.ar
# (fetch_statfutbol_reserva_zona), que tiene una pagina estatica por zona y
# por torneo (confirmado con datos reales: Tigre en Zona A en los dos
# torneos). A diferencia de sabadogol (fuente vieja, sacada por poca
# confiabilidad -- se quedaba atras varios dias con los resultados), acá no
# hace falta detectar la zona por proximidad de texto: cada URL es una zona.
RESERVA_ZONA_URLS = {
    "RESERVA_APE": {
        "Zona A": "afaposicionescopaapA2026Resolucion.php",
        "Zona B": "afaposicionescopaapB2026Resolucion.php",
    },
    "RESERVA_CLA": {
        "Zona A": "afaposicionescopaclA2026Resolucion.php",
        "Zona B": "afaposicionescopaclB2026Resolucion.php",
    },
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


def fetch_post(url: str, data: dict) -> str:
    body = urllib.parse.urlencode(data).encode()
    headers = dict(HEADERS)
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    req = urllib.request.Request(url, data=body, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def _quitar_tags(s: str) -> str:
    return re.sub(r"<[^>]+>", "", s).strip()


def parse_lpf_fixture_completo(html: str):
    """
    Extrae TODOS los partidos ya jugados de cada fecha (los de Tigre y los de
    los demas equipos) de la misma pagina de ligaprofesional.ar que ya usa
    parse_tabla para la tabla de posiciones -- no hace falta un pedido HTTP
    aparte. Reemplaza a la vieja fuente sabadogol.com.ar (sacada por poca
    confiabilidad: se quedaba atras varios dias con los resultados reales,
    confirmado comparando contra la LPF oficial y statfutbol.com.ar el
    2026-08-31).

    La pagina arma el fixture con pestañas "Fecha 1".."Fecha 35" (widget
    Elementor/ElementsKit): un <table class="...tablepress-fixture"> por
    fecha, dentro de un <div class="tab-pane" id="content-XXXX"> propio. El
    numero de fecha no viaja en las filas de la tabla, asi que se arma
    cruzando cada pestaña (data-ekit-handler-id="fecha-N", con
    data-target="#content-XXXX" apuntando a su panel) contra el panel que
    tiene ese mismo id -- NO por orden de aparicion: confirmado con un caso
    real (2026-08-31, 9NA) que el pedido HTTP a veces devuelve un panel de
    menos que otras (probable variacion de cache del lado de la Liga, no
    algo que dependa de nuestro request) -- matchear por id evita asignarle
    a una fecha la tabla de otra cuando eso pasa; esa fecha simplemente
    queda afuera de este pedido puntual (se completa sola en el proximo).

    Devuelve {fecha:int -> [{"local":str,"visitante":str,"gl":int,"gv":int}, ...]}.
    Partidos sin marcador (todavia no jugados, celda de gol vacia) se omiten.
    """
    nav_pairs = re.findall(
        r'data-ekit-handler-id="fecha-(\d+)"[^>]*data-target="#(content-[0-9a-f]+)"', html)
    panel_ids = re.split(r'id="(content-[0-9a-f]+)" role="tabpanel"', html)
    paneles = dict(zip(panel_ids[1::2], panel_ids[2::2]))  # content_id -> html despues del panel
    if not nav_pairs or not paneles:
        raise ValueError("no se encontraron pestañas ni paneles de fixture")

    out = {}
    for fecha_str, content_id in nav_pairs:
        panel_html = paneles.get(content_id)
        if not panel_html:
            continue  # panel de esta fecha no vino en esta respuesta puntual
        m = re.search(
            r'<table id="tablepress-\d+" class="tablepress tablepress-id-\d+ tablepress-fixture">(.*?)</table>',
            panel_html, re.DOTALL)
        if not m:
            continue
        fecha = int(fecha_str)
        tabla_html = m.group(1)
        filas = re.findall(
            r'<td class="column-1">.*?</td>\s*<td class="column-2">(.*?)</td>\s*'
            r'<td class="column-3">.*?</td>\s*<td class="column-4">(.*?)</td>\s*'
            r'<td class="column-5">.*?</td>\s*<td class="column-6">(.*?)</td>\s*'
            r'<td class="column-7">.*?</td>\s*<td class="column-8">(.*?)</td>',
            tabla_html, re.DOTALL)
        partidos = []
        for local_raw, gl_raw, gv_raw, visitante_raw in filas:
            gl_raw, gv_raw = _quitar_tags(gl_raw), _quitar_tags(gv_raw)
            if not (gl_raw.isdigit() and gv_raw.isdigit()):
                continue  # todavia no jugado
            partidos.append({
                "local": norm_equipo(_quitar_tags(local_raw)),
                "visitante": norm_equipo(_quitar_tags(visitante_raw)),
                "gl": int(gl_raw),
                "gv": int(gv_raw),
            })
        if partidos:
            out[fecha] = partidos
    if not out:
        raise ValueError("no se pudo parsear ningun partido jugado")
    return out


def fixture_tigre_desde_completo(fixture_completo: dict):
    """Aisla los partidos de TIGRE de un fixture_completo (parse_lpf_fixture_
    completo) en el shape que espera resultado["fixture"]:
    {fecha:int -> {"gf":int,"gc":int,"rival":str}}."""
    out = {}
    for fecha, partidos in fixture_completo.items():
        for p in partidos:
            es_local = p["local"].upper() == "TIGRE"
            es_visitante = p["visitante"].upper() == "TIGRE"
            if es_local:
                out[fecha] = {"gf": p["gl"], "gc": p["gv"], "rival": p["visitante"]}
            elif es_visitante:
                out[fecha] = {"gf": p["gv"], "gc": p["gl"], "rival": p["local"]}
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
FUTDETAIL_ESTADISTICAS_URL = FUTDETAIL_BASE + "division_estadisticas.php"
# El JSON real de estadisticas por jugador sale de este endpoint, no de la
# pagina de arriba (confirmado con el Network tab de un navegador real
# logueado: la pagina la pide con un POST aparte a esto). El bug de fondo
# de "Expecting value ... <!doctype html>" que venia fallando desde que se
# agrego esta parte era justamente pedir el JSON a la URL de la pagina en
# vez de a esta -- FUTDETAIL_ESTADISTICAS_URL solo sirve para la visita
# previa que deja estado de sesion/referer (ver fetch_futdetail_estadisticas).
FUTDETAIL_ESTADISTICAS_PROCESO_URL = FUTDETAIL_BASE + "division_estadisticas_proceso.php"
# Plantel (roster) por division: posicion, nombre, edad, altura, peso, pie,
# valoracion, foto. Confirmado con el usuario via DevTools -- GET con estos
# parametros (el "_" es un cache-buster de jQuery, no hace falta mandarlo).
FUTDETAIL_JUGADORES_URL = FUTDETAIL_BASE + "jugadores_consulta_lista_procesos.php"
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
            "sistema_tactico": (f.get("sistema_tactico") or "").strip(),
        }
        if localia == "L":
            out[fecha] = {"gf": gl, "gc": gv, "rival": rival, **links}
        elif localia == "V":
            out[fecha] = {"gf": gv, "gc": gl, "rival": rival, **links}
        # localia distinto de L/V: no deberia pasar, se ignora la fila
    return out


def fetch_futdetail_estadisticas(opener, id_division: str):
    """Pide las estadisticas por jugador de una division ya logueado.
    Al principio se penso que division_estadisticas.php devolvia la tabla
    ya renderizada en HTML (por eso el primer intento la parseaba asi), pero
    esa pagina en realidad la arma con JavaScript: los datos reales salen de
    un POST aparte a division_estadisticas_proceso.php, que SI devuelve JSON
    -- confirmado inspeccionando el pedido real con el usuario (DevTools ->
    Network -> Fetch/XHR). Primero se visita division_estadisticas.php (deja
    estado de sesion / referer, como con el login) y recien despues se hace
    el POST -- pero el POST tiene que ir a division_estadisticas_proceso.php
    (FUTDETAIL_ESTADISTICAS_PROCESO_URL), NO a la url de la pagina: ese era
    el bug real detras del "Expecting value ... <!doctype html>" que
    persistia en varios intentos anteriores (headers, Referer, GET previo)
    -- nunca era la sesion, era la URL equivocada. Confirmado re-mirando el
    Network tab con un navegador logueado: la pagina pide el JSON a
    division_estadisticas_proceso.php, y ESA respuesta matchea exacto lo que
    parse_futdetail_estadisticas espera.
    """
    pagina_url = f"{FUTDETAIL_ESTADISTICAS_URL}?id_division={id_division}"
    opener.open(urllib.request.Request(pagina_url, headers=HEADERS), timeout=30)

    body = urllib.parse.urlencode({
        "id_division": id_division, "temporada_id": FUTDETAIL_TEMPORADA_ID,
    }).encode()
    headers = dict(HEADERS)
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    # El backend distingue pedidos AJAX reales por este header (asi lo manda
    # el JS de la pagina) -- sin el, la respuesta viene distinta.
    headers["X-Requested-With"] = "XMLHttpRequest"
    headers["Referer"] = pagina_url
    resp = opener.open(urllib.request.Request(FUTDETAIL_ESTADISTICAS_PROCESO_URL, data=body, headers=headers), timeout=30)
    texto = resp.read().decode("utf-8", errors="replace")
    try:
        return json.loads(texto)
    except ValueError as e:
        # Si esto vuelve a fallar, el mensaje ya trae un pedazo de lo que
        # realmente contesto el servidor (login vencido, HTML de error,
        # etc.) en vez de un simple "Expecting value" sin contexto.
        raise ValueError(f"{e} -- respuesta cruda: {texto[:200]!r}") from e


def parse_futdetail_estadisticas(filas):
    """
    Convierte la lista cruda de division_estadisticas_proceso.php (todos los
    campos vienen como string) en dicts con los numeros ya convertidos:
    convocatorias, partidos titular, minutos, goles, asistencias, amarillas,
    rojas -- acumulado de toda la temporada. Ignora "entrenamiento_ausencia"
    (viene en la respuesta pero no se usa en la app).
    """
    CAMPOS_NUM = [
        "convocatorias", "partidos_titular", "minutos_jugados",
        "goles", "asistencias", "tarjeta_amarilla", "tarjeta_roja",
    ]
    out = []
    for f in filas:
        jugador = str(f.get("jugador") or "").strip()
        if not jugador:
            continue
        fila_dict = {"jugador": jugador}
        for campo in CAMPOS_NUM:
            try:
                fila_dict[campo] = int(f.get(campo) or 0)
            except (TypeError, ValueError):
                fila_dict[campo] = 0
        out.append(fila_dict)

    if not out:
        raise ValueError("Se recibio la respuesta pero no se pudo parsear ningun jugador")
    return out


def fetch_futdetail_plantel(opener, id_division: str):
    """Pide el roster (plantel propio) de una division ya logueado --
    posicion, nombre, edad, altura, peso, pie, valoracion, foto. Confirmado
    con el usuario via DevTools (Network -> Fetch/XHR) sobre la pantalla
    "Jugadores Propios" (scoutdetail.php?jugadores_propios=S): al filtrar
    por division, la tabla pide este GET y devuelve JSON directo (no hace
    falta parsear HTML). El resto de los parametros son los que manda el
    formulario "sin filtrar" (posicion/nombre/edad/valoracion vacios,
    ver_baja=N para no traer jugadores dados de baja).
    """
    params = {
        "division": id_division, "jugadores_propios": "S", "id_jugador": "0",
        "opcion": "1", "posicion": "", "edad": "0", "nombre": "",
        "valoracion": "0", "ver_baja": "N", "id_categoria": "0",
        "nacionalidad": "0", "id_equipo": "0", "ver_a_prestamo": "N",
    }
    url = f"{FUTDETAIL_JUGADORES_URL}?{urllib.parse.urlencode(params)}"
    resp = opener.open(urllib.request.Request(url, headers=HEADERS), timeout=30)
    return json.loads(resp.read().decode("utf-8", errors="replace"))


def parse_futdetail_plantel(filas):
    """Convierte la lista cruda de jugadores_consulta_lista_procesos.php en
    el shape que espera plantelFutdetail en index.html: {nombre, posicion,
    edad, altura, peso, pie, valoracion, foto}. El id lo calcula la app
    sola a partir del nombre (assignPlayerIds), no hace falta mandarlo.

    Altura viene inconsistente desde futdetail: a veces en cm ("187.00") y
    a veces en metros ("1.85") segun quien haya cargado a cada jugador --
    se normaliza a cm siempre que el valor sea menor a 10 (nadie mide menos
    de 10 metros).
    """
    def _num(v):
        try:
            n = float(v)
            return n if n else None
        except (TypeError, ValueError):
            return None

    out = []
    for f in filas:
        nombre = str(f.get("Nombre") or "").strip()
        if not nombre:
            continue
        altura = _num(f.get("Altura"))
        if altura is not None and altura < 10:
            altura *= 100
        foto = f.get("imagen_jugador")
        out.append({
            "nombre": nombre,
            "posicion": str(f.get("Posicion") or "").strip(),
            "edad": int(f["edad"]) if str(f.get("edad") or "").isdigit() else None,
            "altura": round(altura) if altura is not None else None,
            "peso": _num(f.get("Peso")),
            "pie": {"D": "Derecho", "I": "Izquierdo"}.get(f.get("pie"), ""),
            "valoracion": f.get("valoracion") or "",
            "foto": (FUTDETAIL_BASE + foto) if foto else None,
        })
    return out


# ── BL GPS Performance (app aparte de Brian, preparador fisico) ─────────
# Firebase distinto al de Tigre, SOLO LECTURA. No tiene un nodo compartido:
# cada usuario guarda todo su estado como un JSON serializado en
# usuarios/{uid}/blob (confirmado leyendo como su propia app guarda/carga
# los datos) -- hay que loguearse con un usuario real de esa app para leer
# algo. Credenciales en GitHub Secrets (BL_USER, BL_PASS), igual que
# futdetail; si no estan configuradas esta parte se saltea sola.
BL_FB_API_KEY = "AIzaSyAE6tdPK5rUDlE5YABF31M5gKkug6HMdl8"
BL_FB_DB_URL = "https://bl-gps-performance-default-rtdb.firebaseio.com"


def fetch_bl_players(email: str, password: str):
    """
    Login con email/password contra Firebase Auth (API REST, sin SDK) y
    lectura de usuarios/{uid}/blob. Devuelve
    {nombre: {"pos":..., "match":[{"fecha","opp","min","metrics":[...]},...]}}
    -- se descarta todo lo demas del blob (entrenamientos, ejercicios,
    planificacion de fuerza, etc.) porque la app de Tigre solo cruza datos
    de partido.
    """
    auth_url = (
        "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
        f"?key={BL_FB_API_KEY}"
    )
    body = json.dumps({"email": email, "password": password, "returnSecureToken": True}).encode()
    req = urllib.request.Request(auth_url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            auth_data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detalle = e.read().decode("utf-8", errors="replace")[:200]
        raise RuntimeError(f"login BL invalido: {detalle}") from e
    uid = auth_data["localId"]
    id_token = auth_data["idToken"]

    blob_url = f"{BL_FB_DB_URL}/usuarios/{uid}/blob.json?auth={id_token}"
    with urllib.request.urlopen(blob_url, timeout=30) as resp:
        raw = json.loads(resp.read().decode("utf-8"))  # el valor guardado ES un string JSON
    if not raw:
        return {}
    data = json.loads(raw)
    players = data.get("PLAYERS") or {}

    out = {}
    for nombre, p in players.items():
        matches = p.get("match") or []
        if not matches:
            continue
        out[nombre] = {"pos": p.get("pos", ""), "match": matches}
    return out


# ── parenlapelota.com.ar (segunda fuente publica para 4TA-9NA) ──────────
# Next.js con render en el servidor -- la tabla de posiciones ya viene
# armada en el HTML de la respuesta, sin JS ni login (confirmado con un
# curl plano). Se usa solo como cruce extra para la fila de Tigre en
# Confiabilidad (equipoMismatches en index.html) -- no reemplaza a la LPF
# oficial, asi que solo se guarda la fila de Tigre de cada categoria, no
# la tabla completa (36 equipos no aportan nada mas por ahora).
PARENLAPELOTA_SLUGS = {
    "4TA": "cuarta", "5TA": "quinta", "6TA": "sexta",
    "7MA": "septima", "8VA": "octava", "9NA": "novena",
}


def fetch_parenlapelota_tigre(slug: str):
    html = fetch(f"https://parenlapelota.com.ar/lpf/{slug}")
    idx = html.find(">Tigre<")
    if idx == -1:
        raise ValueError("No se encontro la fila de Tigre en la tabla")
    # La celda del equipo trae escudo (img) + nombre en markup anidado, asi
    # que se busca por el texto "Tigre" y se aisla el <tr> que lo contiene,
    # en vez de asumir una estructura fija de columnas de entrada.
    tr_start = html.rfind("<tr", 0, idx)
    tr_end = html.find("</tr>", idx)
    if tr_start == -1 or tr_end == -1:
        raise ValueError("No se pudo aislar la fila de Tigre")
    celdas = re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", html[tr_start:tr_end], re.IGNORECASE | re.DOTALL)
    celdas = [re.sub(r"<[^>]+>", "", c).replace("&nbsp;", " ").strip() for c in celdas]
    if len(celdas) < 10:
        raise ValueError(f"Fila de Tigre con menos celdas de las esperadas: {celdas}")
    # Orden real de columnas en parenlapelota (distinto al de la LPF oficial):
    # Pos | Equipo | PJ | G | E | P | GF | GC | DG | PTS -- confirmado con
    # una fila real (Cuarta 2026: 18 Tigre 22 10 4 8 33 23 +10 34).
    return {
        "pj": int(celdas[2]), "pg": int(celdas[3]), "pe": int(celdas[4]), "pp": int(celdas[5]),
        "gf": int(celdas[6]), "gc": int(celdas[7]),
    }


# ── statfutbol.com.ar (alertas del proximo rival) ────────────────────────
# Fuente publica, HTML servido plano (confirmado con curl, sin JS). Se usa
# SOLO para el proximo partido de cada categoria (no toda la temporada):
# 1) quien es el goleador del plantel del rival, y 2) si alguien del rival
# se amonesto en su ULTIMO partido jugado y ese cartel lo dejo justo en un
# multiplo de 5 amarillas de la temporada (nuestra regla de suspension:
# cada 5ta amarilla = 1 partido afuera).
STATFUTBOL_BASE = "https://statfutbol.com.ar/"
STATFUTBOL_CATNUM = {"4TA": "4", "5TA": "5", "6TA": "6", "7MA": "7", "8VA": "8", "9NA": "9"}

# Los nombres de equipo no se escriben igual en las distintas paginas del
# propio statfutbol (el fixture abrevia mas que el selector de planteles:
# "DEF Y JUSTICIA" vs "DEFENSA Y JUSTICIA", "C.CORDOBA(SDE)" vs "CENTRAL
# CORDOBA (SANTIAGO DEL ESTERO)", etc). _statfutbol_match_equipo empareja
# por nombre base + codigo de ciudad (cuando hay parentesis en los dos
# lados), probado a mano contra los 35 rivales reales de Cuarta 2026 antes
# de escribir esto (34/35 automatico, 1 con el parche de C.CORDOBA de abajo).
STATFUTBOL_CITY_CODES = {
    "LP": "LP", "LA PLATA": "LP",
    "RC": "RC", "RIO CUARTO": "RC", "RIO CUARTO - CORDOBA": "RC",
    "SDE": "SDE", "SANTIAGO DEL ESTERO": "SDE",
    "SJ": "SJ", "SAN JUAN": "SJ",
    "SF": "SF", "SANTA FE": "SF",
    "C": "CBA", "CORDOBA": "CBA",
    "M": "MZA", "MZA": "MZA", "MENDOZA": "MZA",
    "MDP": "MDP", "MAR DEL PLATA": "MDP",
    "J": "JUNIN", "JUNIN": "JUNIN",
}
# Alias palabra-por-palabra (nunca substring suelto, para no pisar nombres
# reales como "Colon" o "San Martin").
STATFUTBOL_PALABRA_ALIAS = {
    "IND": "INDEPENDIENTE", "JRS": "JUNIORS", "CTRAL": "CENTRAL", "DEF": "DEFENSA",
}
# Nombres coloquiales cortos que en el futbol argentino todos entienden a
# que club se refieren, pero que por substring solo son ambiguos (matchean
# con mas de un club real).
STATFUTBOL_ALIAS_EXACTOS = {"CENTRAL": "ROSARIO CENTRAL"}


def _statfutbol_norm_palabras(s):
    s = s.upper().replace(".", " ")
    s = re.sub(r"\s+", " ", s).strip()
    # Caso puntual: "C.CORDOBA" (ya con el punto convertido a espacio arriba)
    # es Central Cordoba, no "Cordoba" a secas -- sin esto, la "C" sola no
    # significa nada y el match falla.
    s = re.sub(r"^C CORDOBA\b", "CENTRAL CORDOBA", s)
    return " ".join(STATFUTBOL_PALABRA_ALIAS.get(w, w) for w in s.split(" "))


def _statfutbol_partes(s):
    s = _statfutbol_norm_palabras(s)
    m = re.match(r"^(.*?)\s*\(([^)]*)\)\s*$", s)
    if m:
        base, city = m.group(1).strip(), m.group(2).strip()
    else:
        base, city = s, ""
    return base, STATFUTBOL_CITY_CODES.get(city, city)


def statfutbol_match_equipo(nombre_fixture, equipos):
    """equipos: lista de (id, nombre) del selector de planteles. Devuelve
    (id, nombre) del que mejor matchea, o None si no hay un match unico."""
    alias = STATFUTBOL_ALIAS_EXACTOS.get(nombre_fixture.upper().strip())
    if alias:
        for eid, en in equipos:
            if _statfutbol_partes(en)[0] == alias:
                return (eid, en)
    fbase, fcity = _statfutbol_partes(nombre_fixture)
    cands = []
    for eid, en in equipos:
        ebase, ecity = _statfutbol_partes(en)
        if fbase in ebase or ebase in fbase:
            if not fcity or not ecity or fcity == ecity:
                cands.append((eid, en, ebase == fbase))
    if len(cands) > 1:
        exactos = [c for c in cands if c[2]]
        if len(exactos) == 1:
            cands = exactos
    return (cands[0][0], cands[0][1]) if len(cands) == 1 else None


def fetch_statfutbol_fixture(catnum):
    """Fixture completo de la categoria (35 fechas, todos los equipos).
    Partidos no jugados traen score ".-." (confirmado con datos reales)."""
    html = fetch(f"{STATFUTBOL_BASE}afafixtureliga{catnum}2026Resolucion.php")
    filas = re.findall(r'<tr class="trConsult[^"]*">(.*?)</tr>', html, re.DOTALL)
    out = []
    for fila in filas:
        celdas = re.findall(r"<td[^>]*>(.*?)</td>", fila, re.DOTALL)
        if len(celdas) < 9:
            continue
        def equipo_de(c):
            m = re.search(r'class="pc">([^<]*)</span>', c)
            return m.group(1).strip() if m else ""
        jm = re.match(r"\s*(\d+)", re.sub(r"<[^>]+>", "", celdas[1]))
        local, visita = equipo_de(celdas[2]), equipo_de(celdas[4])
        score = re.sub(r"<[^>]+>", "", celdas[3]).strip()
        fm = re.search(r"(\d{4}-\d{2}-\d{2})", celdas[6])
        idm = re.search(r'name="idPartido" value="(\d+)"', celdas[8])
        if not (jm and local and visita and fm and idm):
            continue
        out.append({
            "jornada": int(jm.group(1)), "local": local, "visita": visita,
            "jugado": score not in ("", ".-."), "fecha_iso": fm.group(1), "id_partido": idm.group(1),
        })
    return out


def fetch_statfutbol_equipos(catnum):
    """Lista (id, nombre) del selector 'Elija un equipo' de PLANTELES."""
    html = fetch(f"{STATFUTBOL_BASE}afaplanteles{catnum}2026.php")
    opts = re.findall(r'<option value="(\d+)">\s*([^<]+?)\s*</option>', html)
    return [(v, n.strip()) for v, n in opts]


def fetch_statfutbol_plantel(catnum, team_id):
    """Plantel del equipo con acumulado de temporada por jugador (ya viene
    calculado por statfutbol, no hay que sumar partido a partido)."""
    html = fetch_post(f"{STATFUTBOL_BASE}afaplanteles{catnum}2026Resolucion.php", {"player": team_id})
    filas = re.findall(r'<tr class="trConsultParaJugadores">(.*?)</tr>', html, re.DOTALL)
    out = []
    for fila in filas:
        nombre_m = re.search(r'jugador-pc">([^<]*)</span>', fila)
        celdas = re.findall(r"<td[^>]*>(.*?)</td>", fila, re.DOTALL)
        # celdas: [0]=nombre, [1]=PJ, [2]=MIN, [3]=GOL, [4]=AM, [5]=EXP, [6]=OUT, [7]=IN, [8]=boton
        if not nombre_m or len(celdas) < 5:
            continue
        try:
            gol = int(re.sub(r"<[^>]+>", "", celdas[3]).strip())
            am = int(re.sub(r"<[^>]+>", "", celdas[4]).strip())
        except (ValueError, IndexError):
            continue
        out.append({"nombre": nombre_m.group(1).strip(), "gol": gol, "am": am})
    return out


def fetch_statfutbol_sintesis_amarillas(catnum, id_partido, team_id_objetivo, equipos):
    """Devuelve los nombres de jugadores del equipo team_id_objetivo que se
    amonestaron (amarilla) en ese partido puntual."""
    html = fetch_post(f"{STATFUTBOL_BASE}sintesispartido{catnum}2026.php",
                       {"idPartido": id_partido, "fixGL": "0", "fixGV": "0"})
    # ojo: "encabezado-equipo" tambien aparece en el <style> inline mas
    # arriba en la pagina -- hay que buscar el <th>, no el string suelto.
    idx = html.find('<th class="encabezado-equipo"')
    idx2 = html.find("</table>", idx)
    if idx < 0 or idx2 < 0:
        raise ValueError("No se encontro la tabla de sintesis")
    bloque = html[idx:idx2]
    # "1 gol" (singular) vs "2 goles" (plural) -- statfutbol usa las dos. El
    # nombre del equipo puede traer su propio parentesis (ej. "GODOY CRUZ
    # A.T. (MENDOZA)"), asi que no se puede cortar en el primer "(" -- se
    # captura todo sin exigir nada mas que terminar justo antes de
    # "(N gol/es)</th>" (ese es siempre el ultimo parentesis de la celda).
    nombres_equipo = re.findall(r'encabezado-equipo">.*?;(.+?)\s*\(\d+ gol(?:es)?\)\s*</th>', bloque)
    tds = re.findall(r'<td class="jugadores-equipo"[^>]*>(.*?)</td>', bloque, re.DOTALL)
    if len(nombres_equipo) != 2 or len(tds) != 2:
        raise ValueError("Formato de sintesis inesperado (equipos/columnas)")
    nombre_objetivo = next((n for eid, n in equipos if eid == team_id_objetivo), None)
    lado = None
    for i, ne in enumerate(nombres_equipo):
        m = statfutbol_match_equipo(ne, equipos)
        if m and m[0] == team_id_objetivo:
            lado = i
    if lado is None:
        raise ValueError(f"No pude identificar de que lado esta el equipo {nombre_objetivo!r} en la sintesis")
    spans = re.findall(r'<span class="linea-jugador">(.*?)</span>', tds[lado], re.DOTALL)
    amonestados = []
    for sp in spans:
        iconos = re.findall(r'<i class="([^"]+)"[^>]*?style="color:([^;"]+)', sp)
        if not any("fa-square" in cls and color == "yellow" for cls, color in iconos):
            continue
        texto = re.sub(r"<form.*?</form>", "", sp, flags=re.DOTALL)
        texto = re.sub(r"<i.*?</i>|<i[^>]*/?>", "", texto, flags=re.DOTALL)
        nombre = re.sub(r"^\s*\d+\.\s*", "", texto).strip()
        if nombre:
            amonestados.append(nombre)
    return amonestados


def calcular_alerta_rival(cat, catnum):
    """Para el PROXIMO partido de la categoria (el primero sin jugar en el
    fixture de statfutbol): goleador del plantel rival + jugadores que se
    amonestaron en el ultimo partido del rival y quedaron en multiplo de 5
    amarillas de la temporada (posible suspension para jugar contra
    nosotros). Devuelve None si no hay proximo partido o algo no matchea
    (fuente opcional, no debe romper el resto del scraping)."""
    fixture = fetch_statfutbol_fixture(catnum)
    proximo = next((p for p in fixture if not p["jugado"] and (p["local"] == "TIGRE" or p["visita"] == "TIGRE")), None)
    if not proximo:
        return None
    rival_nombre_fx = proximo["visita"] if proximo["local"] == "TIGRE" else proximo["local"]

    equipos = fetch_statfutbol_equipos(catnum)
    match = statfutbol_match_equipo(rival_nombre_fx, equipos)
    if not match:
        raise ValueError(f"No pude identificar al equipo rival {rival_nombre_fx!r} en el listado de planteles")
    team_id, team_nombre = match

    plantel = fetch_statfutbol_plantel(catnum, team_id)
    if not plantel:
        raise ValueError(f"Plantel vacio para {team_nombre!r}")
    goleador = max(plantel, key=lambda j: j["gol"])
    am_por_nombre = {j["nombre"]: j["am"] for j in plantel}

    # Ultimo partido JUGADO del rival antes de enfrentarnos (no necesariamente
    # la fecha anterior a la nuestra -- el rival puede tener fechas libres/
    # reprogramadas distintas a las nuestras).
    partidos_rival = [p for p in fixture if p["jugado"] and (p["local"] == team_nombre.split(" (")[0]
                       or p["visita"] == team_nombre.split(" (")[0]
                       or statfutbol_match_equipo(p["local"], equipos) == match
                       or statfutbol_match_equipo(p["visita"], equipos) == match)]
    partidos_rival.sort(key=lambda p: p["fecha_iso"])
    ultimo = partidos_rival[-1] if partidos_rival else None

    riesgo = []
    if ultimo:
        # El partido puede ya figurar como jugado en el fixture pero todavia
        # no tener su sintesis cargada del lado de statfutbol (confirmado
        # 2026-09-01: la tabla viene vacia, sin nombre de equipo ni
        # jugadores, no es un cambio de formato) -- en ese caso no hay
        # amonestados que avisar todavia, no es un error real.
        try:
            amonestados = fetch_statfutbol_sintesis_amarillas(catnum, ultimo["id_partido"], team_id, equipos)
        except ValueError:
            amonestados = []
        for nombre in amonestados:
            am_total = am_por_nombre.get(nombre)
            if am_total is not None and am_total > 0 and am_total % 5 == 0:
                riesgo.append({"nombre": nombre, "amarillas": am_total})

    return {
        "fecha": proximo["jornada"],
        "rival": team_nombre,
        "goleador": {"nombre": goleador["nombre"], "goles": goleador["gol"]} if goleador["gol"] > 0 else None,
        "amarillas_riesgo": riesgo,
    }


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
        celdas_raw = re.findall(r"<t[dh]\b[^>]*>(.*?)</t[dh]>", fila, re.IGNORECASE | re.DOTALL)
        if len(celdas_raw) < 10:
            continue
        def _limpiar(c):
            return re.sub(r"<[^>]+>", "", c).replace("&nbsp;", " ").strip()
        pos_raw = _limpiar(celdas_raw[0]).replace("°", "").strip()
        if not re.match(r"^\d+$", pos_raw):
            continue
        # La celda de equipo a veces trae dos versiones pegadas (ej.
        # statfutbol: <span class="pc">RIVER PLATE</span><span
        # class="celu">RIV</span>, una para PC y otra abreviada para
        # celular -- CSS oculta una segun el viewport, pero las dos quedan
        # en el HTML crudo). Si esta la version "pc" se usa esa; si no, el
        # texto entero de la celda (formato de la LPF, sin este split).
        m_pc = re.search(r'class="pc">([^<]*)</span>', celdas_raw[1])
        equipo = norm_equipo(m_pc.group(1) if m_pc else _limpiar(celdas_raw[1]))
        if not equipo:
            continue
        celdas = [_limpiar(c) for c in celdas_raw]
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


def fetch_statfutbol_reserva_zona(path: str):
    """
    Tabla de posiciones de una zona de Reserva (Proyeccion), desde
    statfutbol.com.ar (reemplaza a sabadogol.com.ar, sacada por poca
    confiabilidad: se quedaba atras varios dias con los resultados reales).
    A diferencia de la LPF oficial (que para Proyeccion sigue siendo un
    widget de Opta por JS, sin tabla en el HTML -- re-chequeado 2026-08-31),
    statfutbol tiene una pagina estatica POR ZONA (no hace falta detectar la
    zona por texto cercano como con sabadogol: cada URL ya es una sola
    zona), con las mismas 10 primeras columnas que el resto de las tablas de
    posiciones de la app (POS/EQUIPO/PTS/PJ/G/E/P/GF/GC/Dif, mas PG/VI al
    final que no usamos) -- confirmado con datos reales, Tigre en Zona A en
    los dos torneos.
    """
    html = fetch(STATFUTBOL_BASE + path)
    m = re.search(r"<table\b[^>]*>(.*?)</table>", html, re.IGNORECASE | re.DOTALL)
    if not m:
        raise ValueError("no se encontro ninguna <table> en la pagina")
    filas = _filas_desde_tabla_html(m.group(1))
    if not filas:
        raise ValueError("se encontro la tabla pero no se pudo parsear ninguna fila")
    return filas


def main():
    resultado = {
        "actualizado": datetime.datetime.now(datetime.timezone.utc)
        .astimezone(datetime.timezone(datetime.timedelta(hours=-3)))
        .strftime("%Y-%m-%d %H:%M"),
        "fuente": "ligaprofesional.ar (oficial)",
        "fuente_fixture": "ligaprofesional.ar (oficial)",
        "fuente_reserva": "statfutbol.com.ar",
        "categorias": {},
    }
    errores = []
    # De paso que se pide cada pagina de la LPF para la tabla de posiciones,
    # se saca tambien el fixture completo (mismo HTML, sin pedido aparte) --
    # ver parse_lpf_fixture_completo. Reemplaza a la vieja fuente sabadogol.
    resultado["fixture"] = {}
    resultado["fixture_completo"] = {}
    for cat, url in FUENTES.items():
        try:
            html = fetch(url)
            filas = parse_tabla(html)
            resultado["categorias"][cat] = filas
            print(f"[OK] {cat}: {len(filas)} equipos")
        except Exception as e:  # noqa
            errores.append(f"{cat}: {e}")
            print(f"[ERROR] {cat}: {e}", file=sys.stderr)
            continue  # sin el HTML no se puede sacar el fixture tampoco

        try:
            fc = parse_lpf_fixture_completo(html)
            resultado["fixture_completo"][cat] = fc
            print(f"[OK] fixture_completo {cat}: {len(fc)} fechas")
            partidos_tigre = fixture_tigre_desde_completo(fc)
            if not partidos_tigre:
                raise ValueError("no se encontro ningun partido de Tigre")
            resultado["fixture"][cat] = partidos_tigre
            print(f"[OK] fixture {cat}: {len(partidos_tigre)} fechas")
        except Exception as e:  # noqa
            errores.append(f"fixture {cat}: {e}")
            print(f"[ERROR] fixture {cat}: {e}", file=sys.stderr)

    # Reserva (Proyeccion): tabla de posiciones desde statfutbol.com.ar (ver
    # fetch_statfutbol_reserva_zona). Cada zona es una URL separada, asi que
    # puede faltar una sola sin perder la otra ni afectar a las juveniles.
    for cat, zonas_urls in RESERVA_ZONA_URLS.items():
        zonas = {}
        for zona, path in zonas_urls.items():
            try:
                zonas[zona] = fetch_statfutbol_reserva_zona(path)
            except Exception as e:  # noqa
                errores.append(f"{cat} {zona}: {e}")
                print(f"[ERROR] {cat} {zona}: {e}", file=sys.stderr)
        if zonas:
            resultado["categorias"][cat] = {"zonas": zonas}
            print(f"[OK] {cat}: {', '.join(f'{z} ({len(f)} equipos)' for z, f in zonas.items())}")

    # Segunda fuente publica para el cruce de Confiabilidad (fila de Tigre:
    # PJ/PG/PE/PP/GF/GC). No necesita credenciales, siempre se intenta.
    resultado["tigre_parenlapelota"] = {}
    for cat, slug in PARENLAPELOTA_SLUGS.items():
        try:
            fila = fetch_parenlapelota_tigre(slug)
            resultado["tigre_parenlapelota"][cat] = fila
            print(f"[OK] parenlapelota {cat}: PJ {fila['pj']}")
        except Exception as e:  # noqa
            errores.append(f"parenlapelota {cat}: {e}")
            print(f"[ERROR] parenlapelota {cat}: {e}", file=sys.stderr)

    # Alertas del proximo rival (statfutbol.com.ar): goleador del plantel +
    # jugadores en riesgo de suspension por 5ta amarilla. Fuente publica, no
    # necesita credenciales. Si calcular_alerta_rival no encuentra proximo
    # partido (temporada terminada) devuelve None y esa categoria se omite
    # sin marcar error.
    resultado["rival_alertas"] = {}
    for cat, catnum in STATFUTBOL_CATNUM.items():
        try:
            alerta = calcular_alerta_rival(cat, catnum)
            if alerta:
                resultado["rival_alertas"][cat] = alerta
                print(f"[OK] statfutbol {cat}: rival {alerta['rival']}, "
                      f"{len(alerta['amarillas_riesgo'])} en riesgo de suspension")
            else:
                print(f"[OK] statfutbol {cat}: sin proximo partido pendiente")
        except Exception as e:  # noqa
            errores.append(f"statfutbol {cat}: {e}")
            print(f"[ERROR] statfutbol {cat}: {e}", file=sys.stderr)

    # Goles y amarillas de TIGRE (no del rival) segun statfutbol -- 4ta
    # fuente para comparar contra mi carga/COMET/futdetail (a pedido del
    # usuario 2026-09-01, prioridad mas baja de las 4: COMET > Liga oficial >
    # futdetail > statfutbol). Reusa fetch_statfutbol_plantel, que ya trae el
    # acumulado de temporada por jugador (gol/am) calculado por el sitio.
    resultado["statfutbol_jugadores"] = {}
    for cat, catnum in STATFUTBOL_CATNUM.items():
        try:
            equipos = fetch_statfutbol_equipos(catnum)
            match = statfutbol_match_equipo("TIGRE", equipos)
            if not match:
                raise ValueError("No se encontro a Tigre en el listado de planteles")
            team_id, _ = match
            plantel = fetch_statfutbol_plantel(catnum, team_id)
            resultado["statfutbol_jugadores"][cat] = plantel
            print(f"[OK] statfutbol jugadores {cat}: {len(plantel)} jugadores")
        except Exception as e:  # noqa
            errores.append(f"statfutbol jugadores {cat}: {e}")
            print(f"[ERROR] statfutbol jugadores {cat}: {e}", file=sys.stderr)

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
                    if filas and not partidos:
                        # Filas si vino, pero el filtro de competencia (ver
                        # parse_futdetail_partidos) descarto todo -- probable
                        # que futdetail haya renombrado "Torneo LPF". Aviso
                        # fuerte para no fallar en silencio como paso antes.
                        print(
                            f"[WARN] futdetail {cat}: {len(filas)} partidos recibidos pero "
                            "0 pasaron el filtro de competencia 'Torneo LPF' -- revisar si "
                            "futdetail cambio el campo competencia_descripcion",
                            file=sys.stderr,
                        )
                except Exception as e:  # noqa
                    errores.append(f"futdetail {cat}: {e}")
                    print(f"[ERROR] futdetail {cat}: {e}", file=sys.stderr)

            # Estadisticas de jugadores (convocatorias/titular/minutos/goles/
            # asist./amarillas/rojas, acumulado de temporada) -- reusa la
            # misma sesion ya logueada arriba. La app las sincroniza sola a
            # Firebase cuando abre un editor (ver sincronizarJugadoresDesde
            # Futdetail en index.html); antes de esto quedaban estaticas.
            resultado["jugadores_futdetail"] = {}
            for cat, id_division in FUTDETAIL_DIVISIONES.items():
                try:
                    filas_raw = fetch_futdetail_estadisticas(opener_fd, id_division)
                    jugadores = parse_futdetail_estadisticas(filas_raw)
                    resultado["jugadores_futdetail"][cat] = jugadores
                    print(f"[OK] futdetail estadisticas {cat}: {len(jugadores)} jugadores")
                except Exception as e:  # noqa
                    errores.append(f"futdetail estadisticas {cat}: {e}")
                    print(f"[ERROR] futdetail estadisticas {cat}: {e}", file=sys.stderr)

            # Plantel (roster: posicion/edad/altura/peso/pie/foto) -- misma
            # sesion. La app lo sincroniza sola a Firebase (ver
            # sincronizarPlantelDesdeFutdetail en index.html), asi que un
            # jugador nuevo dado de alta en futdetail (o un dato corregido)
            # llega solo, sin carga manual.
            resultado["plantel_futdetail"] = {}
            for cat, id_division in FUTDETAIL_DIVISIONES.items():
                try:
                    filas_raw = fetch_futdetail_plantel(opener_fd, id_division)
                    plantel = parse_futdetail_plantel(filas_raw)
                    resultado["plantel_futdetail"][cat] = plantel
                    print(f"[OK] futdetail plantel {cat}: {len(plantel)} jugadores")
                except Exception as e:  # noqa
                    errores.append(f"futdetail plantel {cat}: {e}")
                    print(f"[ERROR] futdetail plantel {cat}: {e}", file=sys.stderr)
        except Exception as e:  # noqa
            errores.append(f"futdetail login: {e}")
            print(f"[ERROR] futdetail login: {e}", file=sys.stderr)
    else:
        print("[AVISO] FUTDETAIL_USER/FUTDETAIL_PASS no configurados, se omite futdetail")

    # Datos de rendimiento fisico (GPS) de "BL GPS Performance" -- Firebase
    # de Brian, el preparador fisico. Fuente opcional: si no estan las
    # credenciales configuradas se saltea sin romper el resto.
    usuario_bl = os.environ.get("BL_USER")
    password_bl = os.environ.get("BL_PASS")
    if usuario_bl and password_bl:
        try:
            jugadores_bl = fetch_bl_players(usuario_bl, password_bl)
            resultado["bl_gps"] = {"players": jugadores_bl}
            print(f"[OK] BL GPS Performance: {len(jugadores_bl)} jugadores")
        except Exception as e:  # noqa
            errores.append(f"BL GPS Performance: {e}")
            print(f"[ERROR] BL GPS Performance: {e}", file=sys.stderr)
    else:
        print("[AVISO] BL_USER/BL_PASS no configurados, se omite BL GPS Performance")

    # Salvaguarda: Zona A y Zona B de un mismo torneo de reserva salen de dos
    # URLs distintas de statfutbol (fetch_statfutbol_reserva_zona), asi que
    # no deberian coincidir nunca -- si salen IDENTICAS es señal de que
    # statfutbol sirvio el mismo contenido para las dos (ej. un redirect o un
    # cambio de URL). Avisar fuerte en vez de mostrar datos duplicados sin
    # que se note.
    for cat in ("RESERVA_APE", "RESERVA_CLA"):
        zonas = (resultado["categorias"].get(cat) or {}).get("zonas", {})
        za, zb = zonas.get("Zona A"), zonas.get("Zona B")
        if za and zb and za == zb:
            aviso = (f"{cat}: Zona A y Zona B salieron identicas -- revisar si "
                      "statfutbol cambio esas URLs.")
            print(f"[AVISO] {aviso}", file=sys.stderr)
            resultado["avisos"] = resultado.get("avisos", []) + [aviso]

    # Si NINGUNA categoria salio bien, no pisamos el JSON anterior.
    if not resultado["categorias"]:
        print("Ninguna categoria pudo procesarse. No se sobrescribe el JSON.", file=sys.stderr)
        sys.exit(1)

    # Se guardan los errores en el JSON (aunque el resto haya salido bien)
    # para que la propia app pueda avisar "hubo un problema en la ultima
    # actualizacion" en vez de mostrar datos parciales como si estuviera
    # todo perfecto.
    if errores:
        resultado["errores"] = errores

    os.makedirs("data", exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)
    print(f"Escrito {OUT_PATH} ({len(resultado['categorias'])} categorias)")

    # Salir con error si alguna fuente fallo -- el commit del dato parcial
    # ya se hace en un paso aparte de la Action (con continue-on-error en
    # este paso), asi que salir con error ac no lo bloquea: solo hace que
    # el run quede marcado como fallido y GitHub mande el aviso por mail.
    # (Antes esto hacia exit(0) pese al comentario que decia lo contrario
    # -- el run siempre quedaba en verde aunque hubiera fuentes rotas.)
    if errores:
        sys.exit(1)


if __name__ == "__main__":
    main()
