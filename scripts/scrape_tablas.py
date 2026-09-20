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
import time
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

# Fixture/planteles/sintesis de Reserva (Apertura y Clausura) -- mismo tipo
# de dato que ya se saca de statfutbol para las juveniles (STATFUTBOL_CATNUM),
# pero con URLs literales por torneo en vez de un "catnum" que se pueda
# interpolar (confirmado navegando el sitio, 2026-09-02; Javi pidio traer
# "todos los datos que se puedan automatizar" para Reserva). RESERVA_APE
# mapea al 1er semestre de la app (results['RESERVA']), RESERVA_CLA al 2do
# (results['RESERVA_S2']), mismo criterio que reservaSemestre en index.html.
RESERVA_TORNEOS = {
    "RESERVA_APE": {
        "fixture": "afafixturecopaape2026Resolucion.php",
        "planteles_base": "afaplantelesCALP2026",
        "sintesis": "sintesispartidocopaape2026.php",
    },
    "RESERVA_CLA": {
        "fixture": "afafixturecopacla2026Resolucion.php",
        "planteles_base": "afaplantelesCCLP2026",
        "sintesis": "sintesispartidocopacla2026.php",
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


# ── Catapult OpenField directo ───────────────────────────────────────────
# Alternativa a BL GPS Performance: en vez de depender de que alguien suba
# el CSV a la app de Brian, se loguea directo en Catapult y se baja la
# metrica del propio partido. Salida en catapult_gps.players, separado por
# categoria (a diferencia de bl_gps.players, que es plano -- ver el porque
# en fetch_catapult_players) A PROPOSITO -- Javi pidio un modulo aparte en
# la app para poder comparar los dos antes de decidir con cual quedarse
# (2026-09-02), asi que ninguno de los dos se toca ni se fusiona todavia.
CATAPULT_API_BASE = "https://backend-us.openfield.catapultsports.com/api/v6"
# El login NO es en us.openfield.catapultsports.com pese a que el <form> de
# esa pagina apunte ahi -- ese host es solo el static hosting de la SPA
# (confirmado: un POST ahi da 405 "MethodNotAllowed" de CloudFront/S3). El
# JS de la pagina en realidad manda el login al dominio de la API.
CATAPULT_LOGIN_URL = "https://backend-us.openfield.catapultsports.com/login"
# Sanctum exige que la request "parezca" venir de la SPA -- sin Referer/
# Origin, hasta con la cookie de sesion bien mandada, el middleware
# EnsureFrontendRequestsAreStateful no la reconoce como pedido stateful y
# cae a 401 "Unauthenticated." (confirmado en vivo con credenciales
# reales: agregar estos dos headers fue lo que lo resolvio).
CATAPULT_HEADERS = dict(HEADERS)
CATAPULT_HEADERS.update({
    "Referer": "https://us.openfield.catapultsports.com/",
    "Origin": "https://us.openfield.catapultsports.com",
})

# Nombre del equipo en Catapult -> categoria en la app (confirmado con
# GET /api/v6/teams en una sesion real).
CATAPULT_TEAMS = {
    "Tigre 4ta División": "4TA",
    "Tigre 5ta División": "5TA",
    "Tigre 6ta División": "6TA",
    "Tigre 7ma División": "7MA",
    "Tigre 8va División": "8VA",
    "Tigre 9na División": "9NA",
    "Tigre Reserva": "RESERVA",
}

# Catapult arma sus PROPIOS "equipos" (team_id) con un roster que le
# pertenece a Catapult, no al club -- queda desactualizado (jugadores que
# cambiaron de categoria durante la temporada, o que ya ni siquiera estan
# en el club) y NO hay que confiar en el para decidir la categoria de cada
# jugador (confirmado con datos reales, Javi 2026-09-02: Catapult tenia a
# Agustin Luna, Axel Wirz, Feversani y Adamovsky -- todos de otra
# categoria real -- adentro del equipo "6ta", y a Iriart/Dalessandro
# Davalos, que ya no estan en el club). La categoria real de cada jugador
# sale del plantel de futdetail (mismo criterio que ya usa el resto de la
# app, ver plantelFutdetail en index.html) -- si un jugador no aparece en
# NINGUN plantel real, se descarta (no se muestra su GPS).
#
# Snapshot de emergencia (2026-09-02) por si en esta corrida no se pudo
# scrapear futdetail (FUTDETAIL_USER/PASS no configurados) -- fetch_catapult_players
# usa el plantel recien scrapeado en esta misma corrida si esta disponible,
# y cae a este snapshot fijo si no. Conviene refrescarlo de vez en cuando.
CATAPULT_PLANTEL_SNAPSHOT = json.loads(r'''
{"4TA":["Ruiz Santiago","Leguizamon Maximo","Ramos Bautista","Rojas Josue","Luongo Alan","Aguirre Iñaki","Saravia Roman","Medina Tiziano","González Kevin","López Facundo","Luna Agustin","Molas Lucas","González Alex","Benitez Lautaro","Fredes Felipe","Perez Gaston","Alvaro Navoni","Cáceres Thomas","Copes Tomas","González Tobías","Benítez Cristian","Mansilla Nehemias","Fares Hamdan","Ordoñez Ignacio","Pannoni Lautaro","Zalazar Benjamín","Afonso Nicolas","Pesolilla Roman","Leszczuk  Brandon","Medina Alejandro","Lezcano Cristian Leonel","Hillairet Yair","Figueredo Benjamin","Gonzalez Santino","Andrusisen Lautaro","Gómez Luka","Mayer Tomas","Lezcano Alan","Ferreyra Rodrigo"],"5TA":["Pereyra Manuel","Zerda Santiago Lionel","Petry Uriel","Cordoba Santiago","Feversani Bautista","Moyano Jerónimo","Samper Joaquin","Wirz Axel","Demonte Tomas","Luque Gonzalo","Adamovsky Felipe ","Canullo Juan","Rodriguez Agustín","Ledesma Gonzalo","Juarez Nahuel","Llera Mariano","Rodriguez Thiago","Poblete Matias","Barrios Cristian ","Crotto Ivo","Crotto Nicolas","Clauser Ramiro","Vargas Thiago","Perez Joaquin","Gonzalez Tomas","Gonzalez Lautaro","Ricaldi Ian","Hernandez Emanuel","Vera Conrado","Miño Roman","Galesio Santino","Rivas Marco","Letizia Ignacio","Villanueva Román"],"6TA":["Sosena Fausto","Camba Rocco","Bruno Lautaro","Sotelo Benjamín ","Scungio Sebastian","Ortiz Ignacio","Moralejo Santiago","Luna Alejo","Muchiutti Valentino","Umeres Agustin","Torres David","Fernandez Jerónimo","Marchetti Ivan","Belmonte Agustín","Gomez Santiago","Mauriño Octavio","Romero Benicio","Nuñez Jonathan","Delgado Francisco","Cortes Adrian maximiliano","Calderon Roman","Schenone Elias","Serapio Ignacio","Brandy German","Pomar Santino","Collado Lautaro","Acosta Jonathan","Parra Matias","Mallmann Félix","Ibañez Tiziano","Zarza Quimey","Lizardia Bautista","Dechiara Francesco","Ambiela Emilio","Sigel Bruno"],"7MA":["Martinez Giuliano","Maturano Benjamin","Montoya Francisco","Castro Matias","Conte Maximiliano","Pucill Mateo","Insaurralde Ihan","Marini Tomas","Dominguez Bautista","Gonzalez Santino","Levy Thiago","Soberon Isaias","Lopez Sebastian","Burela Santino","Lovisi Luciano","Gaitan Valentin","Mancuello Tobias","Lamanna Fabrizio","Almiron Sebastian","Omann Juan Ignacio","Jara Juan","Molina Ramiro","Core Valentino","Di Sipio Agustin","Puchi Santino","Mena Sebastian","Herrera Thiago","Lopez Dionel","Fredes Tiago","Barrios Bautista","Trejo Nicolas","Gagliardo Pedro Tomas","Sodero Santino","Baltazar Alejandro Emanuel","Sala Valentino","Cazal Fernandez Gustavo Alberto","Gallardo Dylan","Godoy Gonzalo","Prieto Alexander","Astesana Valentino"],"8VA":["Arias Nicolas","Reinoso Patricio","Mosqueda Ernesto Jesús ","Monzon Tiziano","Garcia Bautista","Inostroza Bastian","Sanchez Mathias","Tobler Bautista","Meza Luca ","Fino Amadeo","Merlos Galeano Lautaro Benjamin ","Simone  Pedro ","De Olivera Elias","Reinoso Martiniano","Rodríguez  Josué Francisco","Zelaya Franco","Navarro Valentin","Reyes Jose","Noriega Mateo","Rios Mateo","Fernández leis Gabriel ","Cabrera Luca","Radaelli Manuel","Gonzalia Bautista","Gonzalez Leonardo Fabian","Reynoso Tomas","Maguna Pedro","Blanco Dylan Alex","Celiz Teo","Martinuccio Bautista","Punos Tiziano","Galeano Joaquin","Beron Santiago","Aquilue Santiago","Guglielmo Lisandro","Conte Ian","Ruiz Ullua David ","Saragoza Ramiro ","Bin Justin","Lagos Benjamin","Cuba Gio","Bustamante Alan","Chmea Roque","Cocozza Maximo"],"9NA":["Echevarrieta Bautista ","Torrecilla Enzo Francisco","Vargas Valentino","Baccaro Santino","Peludero Mateo","Ibañez Bastian","Vargas Felipe","Mora Bautista","Duarte Gaston ","Cubilla Jonathan","Gomez Zaracho Octavio","Alvarenga Martin Adriano","Lopez Tomas","Soto Mateo","Sanchez Benjamin","Tulis Federico ","Becerra Lionel","Diaz Oliva Santiago","Baigorria Nicolás Nahuel","Enrique Ian","Agorreca Ignacio","Prado Lautaro","Arce Miño  Axel ","Villalba Bogado Gustavo","Diaz Francisco Roman","Dominic Tomassi Benjamin","Pesolilla Ian","Gomez Joaquin","Capozucca Benjamin","Duarte Gonzalo Isaias ","Holm Ian","Bojorge Benjamin","Zapata Alejo","Maidana Lautaro","Dos Santos  Bayron ","Ortiz Leonardo","Monzon Ian ","Marquez  Marcos Bautista","Denis Galli Sebastian","Nuñez Tiziano ","Olocco Mikeas"]}
''')

# Citaciones reales (titulares+suplentes) por categoria/fecha -- exportado
# desde matchData en Firebase (2026-09-02). Es la fuente MAS confiable para
# saber en que categoria jugo un jugador una fecha puntual (a diferencia
# del plantel general, que solo dice de que categoria es "normalmente" --
# no alcanza para detectar a alguien que jugo prestado en otra categoria
# ESE partido, ej. Adamovsky en la F23 de 4TA). Archivo aparte (no un
# string en este .py) por el tamaño; se refresca a mano de vez en cuando.
_CITACIONES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "catapult_citaciones_snapshot.json")
try:
    with open(_CITACIONES_PATH, "r", encoding="utf-8") as _f:
        CATAPULT_CITACIONES_SNAPSHOT = json.load(_f)
except FileNotFoundError:
    CATAPULT_CITACIONES_SNAPSHOT = {}

# Nombres de Catapult que en realidad son la MISMA persona que otro nombre
# ya en el plantel real, pero con una diferencia real de letras (no
# alcanza con reordenar palabras) -- confirmado a mano (Javi, 2026-09-02):
# "Panonni" en Catapult es un typo de "Pannoni". Clave = nombre normalizado
# tal cual sale de Catapult, valor = nombre "canonico" a usar en su lugar
# (se renormaliza igual despues).
CATAPULT_ALIAS_NOMBRE = {
    "lautaro panonni": "Lautaro Pannoni",
    # "Gio" (apodo) vs "Giovanni" (nombre completo en Catapult) -- muy
    # distintos en longitud para que el parecido de texto los matchee solo.
    "cuba giovanni": "Cuba Gio",
}

# Excepciones puntuales a mano (ultimo recurso): partidos donde un jugador
# jugo "prestado" en OTRA categoria, para casos donde la citacion real no
# esta cargada o no alcanza a resolverlo sola. El caso conocido (Adamovsky
# F23 con 4TA) ya lo resuelve solo _catapult_categoria_por_citacion() cruzando
# contra catapult_citaciones_snapshot.json, asi que por ahora queda vacio --
# clave = (nombre normalizado, "F<numero>"), valor = categoria real.
CATAPULT_CATEGORIA_EXCEPCION = {}


def _catapult_norm_nombre(s):
    """Igual que normNombreOrdenIndependiente en index.html: minuscula, sin
    acentos, solo letras, palabras ordenadas alfabeticamente -- asi el
    orden de nombre/apellido no importa al comparar dos fuentes distintas."""
    import unicodedata
    s = unicodedata.normalize("NFD", (s or "").lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z\s]", " ", s)
    return " ".join(sorted(w for w in s.split() if w))


def _catapult_categoria_por_nombre(plantel_por_cat):
    """{nombre_normalizado: categoria} a partir del plantel real (el
    scrapeado en esta misma corrida si esta disponible, sino el snapshot)."""
    fuente = plantel_por_cat or CATAPULT_PLANTEL_SNAPSHOT
    out = {}
    for cat, jugadores in fuente.items():
        for j in jugadores:
            nombre = j.get("nombre") if isinstance(j, dict) else j
            n = _catapult_norm_nombre(nombre)
            if n:
                out[n] = cat
    return out


def _catapult_resolver_categoria(nombre_norm, categoria_por_nombre):
    """
    Busca la categoria real de un nombre ya normalizado, con 3 niveles de
    tolerancia (se prueban en orden, se usa el primero que matchee).
    Encontrado revisando los descartes reales: la comparacion EXACTA sola
    dejaba afuera a la mayoria de los jugadores actuales, no solo a los que
    se fueron del club -- Catapult casi nunca escribe el nombre completo
    (le faltan segundos nombres/apellidos que si estan en el plantel real)
    y a veces tiene una letra distinta (typos ya conocidos del proyecto:
    "Luengo"/"Luongo", "Hillaret"/"Hillairet", ademas de otros nuevos como
    "Cáceres Tomás"/"Cáceres Thomas", "Gio Cuba"/"Cuba Gio") (Javi,
    2026-09-02).

    1. Exacto (ya viene resuelto antes de llamar a esto).
    2. Subconjunto de palabras: si TODAS las palabras del nombre de
       Catapult aparecen en el nombre del plantel (o al reves), es la
       misma persona con nombre incompleto de un lado -- solo se acepta
       si da una UNICA coincidencia en todo el plantel (si hay mas de una,
       queda ambiguo y no se resuelve, mejor no adivinar).
    3. Parecido de texto (typos de una letra): SequenceMatcher sobre el
       string normalizado completo, umbral alto (0.84) y tambien exige
       coincidencia unica.
    """
    palabras = set(nombre_norm.split())
    if not palabras:
        return None

    candidatos_subset = []
    for cand_norm, cat in categoria_por_nombre.items():
        cand_palabras = set(cand_norm.split())
        if palabras <= cand_palabras or cand_palabras <= palabras:
            candidatos_subset.append(cat)
    if len(set(candidatos_subset)) == 1:
        return candidatos_subset[0]
    if len(set(candidatos_subset)) > 1:
        return None  # ambiguo -- mas de un jugador real matchea por subconjunto

    import difflib
    mejor_score, mejor_cats = 0.0, set()
    for cand_norm, cat in categoria_por_nombre.items():
        score = difflib.SequenceMatcher(None, nombre_norm, cand_norm).ratio()
        if score > mejor_score:
            mejor_score, mejor_cats = score, {cat}
        elif score == mejor_score:
            mejor_cats.add(cat)
    if mejor_score >= 0.84 and len(mejor_cats) == 1:
        return next(iter(mejor_cats))
    return None


def _catapult_citaciones_por_cat_fecha():
    """{(categoria, fecha_num): set(nombres normalizados)} a partir de
    CATAPULT_CITACIONES_SNAPSHOT -- se arma una sola vez por corrida."""
    out = {}
    for cat, fechas in CATAPULT_CITACIONES_SNAPSHOT.items():
        for fecha_str, nombres in fechas.items():
            try:
                fecha_num = int(fecha_str)
            except ValueError:
                continue
            out[(cat, fecha_num)] = {_catapult_norm_nombre(n) for n in nombres if n}
    return out


def _catapult_categoria_por_citacion(nombre_norm, fecha_num, citaciones_por_cat_fecha):
    """
    La fuente MAS confiable para la categoria de UN registro puntual: se
    fija quien jugo esa fecha exacta (todas las categorias, no solo la
    "normal" del jugador) segun la citacion real. Resuelve automaticamente
    casos de "jugo prestado" (ej. Adamovsky en la F23 de 4TA) sin necesitar
    una excepcion a mano por cada caso. Solo devuelve algo si hay una
    UNICA categoria cuya citacion de esa fecha lo tiene (exacto o por
    subconjunto de palabras, mismo criterio de tolerancia que el resto);
    si es ambiguo o no aparece en ninguna, no resuelve nada (se cae al
    resto de las reglas)."""
    palabras = set(nombre_norm.split())
    if not palabras:
        return None
    candidatos = set()
    for (cat, f), nombres_norm in citaciones_por_cat_fecha.items():
        if f != fecha_num:
            continue
        if nombre_norm in nombres_norm:
            candidatos.add(cat)
            continue
        for cn in nombres_norm:
            cn_palabras = set(cn.split())
            if palabras <= cn_palabras or cn_palabras <= palabras:
                candidatos.add(cat)
                break
    return next(iter(candidatos)) if len(candidatos) == 1 else None


# Las 16 metricas del CSV/PDF de Catapult, en el mismo orden que
# BL_METRICAS en index.html (indice a indice, para que el frontend no
# necesite ningun mapeo propio) -- el NOMBRE de campo real de
# /api/v6/stats se confirmo a mano cruzando los numeros contra la tabla
# "Reporte detallado" real de un partido (Tomas Caceres, F23 vs Godoy
# Cruz, PDF oficial del 29/8/2026: 60min/5495m/94.47mpm/241-173-45m/
# 2 sprints/28.1kmh/13-17 acc-dcc/4.9/-4.9 max), asi que estan
# verificados contra el reporte oficial, no adivinados (2026-09-03).
#
# "rhie_total_bouts" se saco de esta lista (2026-09-03): la doc oficial
# de Catapult confirma que los bouts de RHIE NO se pueden pedir por API
# ("Because RHIE bouts are not available in the API...", ver
# https://vision-projects.catapultsports.com/focus-openfield/index.html)
# -- se calculan agrupando esfuerzos individuales de alta intensidad que
# caen dentro de una ventana de recuperacion configurable (en Catapult,
# esta ventana esta en 21s para este club -- ver "ESFUERZOS DE ALTA
# INTENSIDAD DENTRO DE 21" en los PDF exportados), y esa agrupacion
# requiere el detalle esfuerzo-por-esfuerzo con su horario exacto, que
# la API de stats no expone (solo totales agregados por partido). Pedir
# este campo igual no rompia nada -- la API contestaba 0 siempre, sin
# error -- pero ese 0 es enganoso (parece un dato real, "no tuvo ningun
# esfuerzo repetido", cuando en realidad nunca se pudo medir). Ahora
# metrics[10] queda directamente en None (ver mas abajo) y el frontend
# lo muestra como "no disponible" en vez de "0".
CATAPULT_STATS_PARAMS = [
    "athlete_id", "athlete_name", "activity_id", "activity_name",
    "total_duration", "average_distance_session", "meterage_per_minute",
    "velocity_band6_total_distance", "velocity_band7_total_distance", "velocity_band8_total_distance",
    "gen2_velocity_band8_total_effort_count", "max_vel",
    "gen2_acceleration_band8_total_effort_count", "gen2_acceleration_band1_total_effort_count",
    "gen2_acceleration_band2_total_effort_count",
    "max_effort_acceleration", "max_effort_deceleration",
    "high_speed_distance_per_minute", "total_player_load",
]


# Fecha de calendario real de cada fecha del Torneo Juveniles 2026 -- copia
# de FECHA_CALENDARIO en index.html (mismo fixture oficial de la LPF). Solo
# vale para 4TA-9NA -- RESERVA juega otro torneo (Copa Proyeccion), por eso
# no se procesa GPS para RESERVA (ver fetch_catapult_players).
CATAPULT_FECHA_CALENDARIO = {
    1: (2026, 3, 14), 2: (2026, 3, 21), 3: (2026, 3, 28),
    4: (2026, 4, 2), 5: (2026, 4, 11), 6: (2026, 4, 18), 7: (2026, 4, 25),
    8: (2026, 5, 2), 9: (2026, 5, 9), 10: (2026, 5, 16), 11: (2026, 5, 23), 12: (2026, 5, 30),
    13: (2026, 6, 6), 14: (2026, 6, 13), 15: (2026, 6, 20), 16: (2026, 6, 27),
    17: (2026, 7, 4), 18: (2026, 7, 11),
    19: (2026, 8, 1), 20: (2026, 8, 8), 21: (2026, 8, 15), 22: (2026, 8, 22), 23: (2026, 8, 29),
    24: (2026, 9, 5), 25: (2026, 9, 12), 26: (2026, 9, 19), 27: (2026, 9, 26),
    28: (2026, 10, 3), 29: (2026, 10, 10), 30: (2026, 10, 24), 31: (2026, 10, 31),
    32: (2026, 11, 7), 33: (2026, 11, 14), 34: (2026, 11, 21),
    35: (2026, 12, 5),
}
# Invertido (dia -> fecha) para buscar por dia real jugado, no por lo que
# diga el nombre en Catapult -- a pedido de Javi (2026-09-02): en vez de
# confiar en "F<numero>" del nombre (poco confiable: hay partidos viejos
# sin ese prefijo, y actividades de la temporada 2025 que quedaron con el
# mismo nombre "F24".."F31" que esta), se recorre el fixture fecha por
# fecha, se calcula que dia de calendario le toca, y se busca en Catapult
# que actividad se jugo ESE dia (o el siguiente -- ver mas abajo). Si
# ninguna actividad coincide, esa fecha simplemente no tiene GPS cargado
# todavia -- no se inventa nada.
#
# Cada fecha acepta tambien el DIA SIGUIENTE al oficial: confirmado con
# datos reales que la descarga/creacion de la sesion en Catapult a veces
# queda fechada un dia despues del partido en si (F2 vs Ferro aparecia
# fechada 22/3 en 4TA/6TA/7MA en vez del 21/3 oficial, mismo patron en
# varias categorias a la vez) -- "no importa que se hayan subido los
# datos al dia siguiente" (Javi, 2026-09-02).
CATAPULT_DIA_A_FECHA = {}
for _fecha, _ymd in CATAPULT_FECHA_CALENDARIO.items():
    for _offset in (0, 1):
        _d = datetime.date(*_ymd) + datetime.timedelta(days=_offset)
        CATAPULT_DIA_A_FECHA[(_d.year, _d.month, _d.day)] = _fecha
# Excepcion aparte (no es "un dia despues", es una fecha que se jugo en
# serio en DOS dias bien distintos): la F3 vs Lanús se suspendio por
# lluvia el 28/3 en Rincon a mitad del primer tiempo de 4TA (nunca
# arrancaron 5TA/6TA) -- el 15/4 se completo el 2do tiempo de 4TA en
# Hacoaj Y se jugaron completos los partidos de 5TA y 6TA de esa misma
# fecha 3 (6TA quedo registrada en Catapult el 16/4, un dia despues, mismo
# patron de arriba). Mismo criterio para cualquier tipo de registro, no
# solo GPS -- ver también parseCitacionPdf/segundoTiempoDe en index.html,
# que ya resolvía este mismo caso para las citaciones.
CATAPULT_DIA_A_FECHA[(2026, 4, 15)] = 3
CATAPULT_DIA_A_FECHA[(2026, 4, 16)] = 3
AR_TZ = datetime.timezone(datetime.timedelta(hours=-3))
# Cualquier actividad de antes de esta fecha es de una temporada vieja que
# quedo en Catapult -- se descarta sin mirar nada mas (Javi, 2026-09-02).
CATAPULT_TEMPORADA_DESDE = datetime.date(2026, 1, 14)


def _catapult_xsrf(cj):
    for c in cj:
        if c.name == "XSRF-TOKEN":
            return urllib.parse.unquote(c.value)
    return None


def catapult_login(email: str, password: str):
    """Inicia sesion en Catapult OpenField (cookie) y devuelve un opener
    listo para pegarle a la API. Catapult usa Laravel Sanctum (SPA auth):
    primero hay que pedir GET /sanctum/csrf-cookie (en el dominio de la
    API, backend-us...) para que el servidor mande la cookie XSRF-TOKEN
    (domain=.openfield.catapultsports.com, por eso sirve tambien para
    us.openfield...) -- la pagina de login normal NO la manda por si sola,
    la pide via JS al cargar (confirmado en vivo con curl plano: sin este
    paso, el POST a /login siempre da 419 "CSRF token mismatch"). Despues
    se manda esa cookie de vuelta como header X-XSRF-TOKEN en el POST."""
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.open(urllib.request.Request(f"{CATAPULT_API_BASE.rsplit('/api', 1)[0]}/sanctum/csrf-cookie",
                                        headers=CATAPULT_HEADERS), timeout=30)

    xsrf = _catapult_xsrf(cj)
    if not xsrf:
        raise RuntimeError("no se pudo obtener la cookie XSRF-TOKEN de Catapult")

    body = json.dumps({"name": email, "password": password}).encode()
    headers = dict(CATAPULT_HEADERS)
    headers.update({"Content-Type": "application/json", "Accept": "application/json", "X-XSRF-TOKEN": xsrf})
    try:
        opener.open(urllib.request.Request(CATAPULT_LOGIN_URL, data=body, headers=headers), timeout=30)
    except urllib.error.HTTPError as e:
        detalle = e.read().decode("utf-8", errors="replace")[:200]
        raise RuntimeError(f"login Catapult invalido: {detalle}") from e
    return opener, cj


def catapult_get(opener, url):
    req = urllib.request.Request(url, headers=CATAPULT_HEADERS)
    return json.loads(opener.open(req, timeout=30).read().decode("utf-8", errors="replace"))


def catapult_stats_post(opener, cj, activity_ids):
    """POST /api/v6/stats agrupado por atleta+actividad -- una fila por
    jugador que jugo alguna de las actividades pedidas."""
    body = json.dumps({
        "filters": [{"name": "activity_id", "comparison": "=", "values": activity_ids}],
        "group_by": ["athlete", "activity"],
        "parameters": CATAPULT_STATS_PARAMS,
        "sorting": ["athlete_name"],
        "source": "cached_stats",
    }).encode()
    headers = dict(CATAPULT_HEADERS)
    headers.update({"Content-Type": "application/json", "Accept": "application/json",
                     "X-XSRF-TOKEN": _catapult_xsrf(cj)})
    resp = opener.open(urllib.request.Request(f"{CATAPULT_API_BASE}/stats", data=body, headers=headers), timeout=30)
    return json.loads(resp.read().decode("utf-8", errors="replace"))


def _catapult_actividades_partido(actividades, cat):
    """Filtra la lista de actividades (de /activities) a los partidos reales
    del Torneo LPF, devolviendo {activity_id: fecha_num}. Extraido de
    fetch_catapult_players para reusarlo en scripts de exportacion (ver
    export_catapult_csv.py) sin duplicar la logica de filtro.

    Por cada actividad-partido, se busca a que fecha del fixture le
    corresponde el dia real en que se jugo (no lo que diga el nombre).
    Actividades de antes del arranque de temporada se descartan derecho
    (quedaron de un año anterior); actividades cuyo dia no coincide con
    NINGUNA fecha del fixture tambien se descartan (amistosos, partidos
    internos, etc.).
    """
    fecha_por_activity_id = {}
    for a in actividades:
        nombre_act = a.get("name") or ""
        # Normalmente es " vs Rival" en el nombre, pero se confirmo un
        # caso real ("F 22- 4ta division", el partido real de la fecha
        # 22 vs Rosario Central) sin "vs" -- caia afuera del filtro
        # aunque tuviera datos reales de jugadores. "division" sirve
        # como señal alternativa, PERO tambien aparece en nombres de
        # entrenamiento tipo "4ta division md -4" ("md" = "match day",
        # notacion estandar para dias relativos a un partido) -- se
        # excluyen esos explicitamente (Javi, 2026-09-02).
        es_partido = " vs " in nombre_act or (
            re.search(r"divisi[oó]n", nombre_act, re.IGNORECASE)
            and not re.search(r"\bmd\b", nombre_act, re.IGNORECASE)
        )
        if not es_partido:
            continue
        # Partidos de otro torneo (Liga Metro, no el Torneo LPF que
        # seguimos) quedan cargados en Catapult con "Liga" en el nombre
        # del rival -- sin este filtro, si caen el mismo dia (o el
        # siguiente) que una fecha real del fixture LPF, su GPS pisaba
        # el de la fecha del torneo (caso real: 7MA F6 "AAAJ Rojo Liga"
        # y F15 "San Lorenzo Liga", 2026-09-03).
        if re.search(r"\bliga\b", nombre_act, re.IGNORECASE):
            print(f"[AVISO] Catapult {cat}: '{a.get('name')}' parece ser de otro torneo "
                  f"(Liga Metro) -- se descarta, no es Torneo LPF.", file=sys.stderr)
            continue
        ts = a.get("start_time")
        if not ts:
            continue
        dia = datetime.datetime.fromtimestamp(ts, AR_TZ).date()
        if dia < CATAPULT_TEMPORADA_DESDE:
            continue
        fecha_num = CATAPULT_DIA_A_FECHA.get((dia.year, dia.month, dia.day))
        if fecha_num is None:
            print(f"[AVISO] Catapult {cat}: '{a.get('name')}' se jugo el {dia.strftime('%d/%m/%Y')}, "
                  f"un dia que no coincide con ninguna fecha del fixture -- se descarta (amistoso, "
                  f"partido interno, etc.).", file=sys.stderr)
            continue
        fecha_por_activity_id[a["id"]] = fecha_num
    return fecha_por_activity_id


def fetch_catapult_players(email: str, password: str, plantel_por_cat=None):
    """
    Devuelve {categoria: {nombre: {"pos":..., "match":[{"fecha","opp",
    "min","metrics":[...]},...]}}} -- una capa mas que fetch_bl_players
    (que es plano, sin categoria) A PROPOSITO: BL trackea un solo equipo,
    pero Catapult trae las 7 categorias de Tigre juntas, y hay apellidos
    repetidos de una categoria a otra (confirmado con datos reales) --
    sin esta separacion, dos jugadores DISTINTOS con el mismo nombre en
    categorias distintas terminarian compartiendo (mal) los partidos de
    los dos. Solo partidos, mismo alcance que BL ("la app de Tigre solo
    cruza datos de partido").

    Un partido se distingue de un entrenamiento por el NOMBRE de la
    actividad (" vs " en el medio, ej. "F 23- 4ta vs Godoy Cruz" -- los
    entrenamientos se llaman "4ta md -4", "5ta Recuperacion
    Compensatoria", etc., nunca con " vs "). Se probo primero mirando la
    etiqueta DayCode="MD" de cada actividad (mas preciso en teoria), pero
    esa etiqueta no viene en el listado de /activities -- hacia falta un
    GET /activities/{id}?include=all por cada una para leerla, y con
    cientos de entrenamientos de por medio (7 categorias x hasta 100 cada
    una) el scraper tardaba mas de 20 minutos. El nombre SI viene en el
    listado, sin pedidos extra.

    RESERVA no se procesa (a pedido de Javi): juega otro torneo, sin
    fixture confiable acá para cruzar. El numero de fecha de cada partido
    NO sale de leer el nombre (poco confiable, ver CATAPULT_DIA_A_FECHA
    mas arriba) -- se calcula el dia de calendario real de cada fecha del
    fixture y se busca que actividad de Catapult se jugo justo ESE dia.
    """
    opener, cj = catapult_login(email, password)
    categoria_por_nombre = _catapult_categoria_por_nombre(plantel_por_cat)
    citaciones_por_cat_fecha = _catapult_citaciones_por_cat_fecha()
    avisados_sin_plantel = set()

    teams = catapult_get(opener, f"{CATAPULT_API_BASE}/teams")
    team_ids_por_cat = {}
    for t in teams:
        cat = CATAPULT_TEAMS.get(t.get("name"))
        if cat and cat != "RESERVA":
            team_ids_por_cat[cat] = t["id"]

    out = {}
    for cat, team_id in team_ids_por_cat.items():
        actividades = catapult_get(opener, f"{CATAPULT_API_BASE}/activities"
                                    f"?page=1&page_size=100&sort=-start_time&deleted=0&team_ids={team_id}")
        fecha_por_activity_id = _catapult_actividades_partido(actividades, cat)

        partidos = list(fecha_por_activity_id.keys())
        if not partidos:
            continue

        # Posiciones: se sacan del roster del partido mas reciente (el
        # primero de la lista, ya viene ordenada -start_time) -- no cambian
        # de un partido a otro dentro de la misma temporada.
        roster = catapult_get(opener, f"{CATAPULT_API_BASE}/activities/{partidos[0]}/athletes")
        posiciones = {
            f"{r.get('first_name', '')} {r.get('last_name', '')}".strip(): r.get("position_name", "")
            for r in roster
        }

        filas = catapult_stats_post(opener, cj, partidos)
        for fila in filas:
            nombre = fila.get("athlete_name")
            if not nombre:
                continue
            fecha_num = fecha_por_activity_id.get(fila.get("activity_id"))
            if fecha_num is None:
                continue

            # La categoria NUNCA sale del equipo de Catapult (cat) -- sale
            # del plantel real. Se aplica primero el alias de nombre mal
            # escrito (typo real, no solo orden de palabras), despues la
            # excepcion puntual (jugador que jugo prestado en otra
            # categoria ESA fecha), y si no aparece en NINGUN plantel real
            # se descarta entero (ya no esta en el club).
            nombre_norm = _catapult_norm_nombre(nombre)
            if nombre_norm in CATAPULT_ALIAS_NOMBRE:
                nombre = CATAPULT_ALIAS_NOMBRE[nombre_norm]
                nombre_norm = _catapult_norm_nombre(nombre)
            # Orden de confianza: excepcion a mano > citacion real de ESA
            # fecha (sabe si jugo prestado en otra categoria puntual) >
            # plantel general exacto > plantel general con tolerancia.
            cat_real = CATAPULT_CATEGORIA_EXCEPCION.get((nombre_norm, f"F{fecha_num}"))
            if cat_real is None:
                cat_real = _catapult_categoria_por_citacion(nombre_norm, fecha_num, citaciones_por_cat_fecha)
            if cat_real is None:
                cat_real = categoria_por_nombre.get(nombre_norm)
            if cat_real is None:
                cat_real = _catapult_resolver_categoria(nombre_norm, categoria_por_nombre)
            if cat_real is None:
                if nombre not in avisados_sin_plantel:
                    avisados_sin_plantel.add(nombre)
                    print(f"[AVISO] Catapult: '{nombre}' (equipo '{cat}' en Catapult) no aparece en "
                          f"ningun plantel real -- se descarta su GPS (ya no esta en el club, o el "
                          f"nombre no matchea).", file=sys.stderr)
                continue

            minutos = round((fila.get("total_duration") or 0) / 60)
            act_nombre = fila.get("activity_name") or ""
            rival = act_nombre.split(" vs ")[-1].strip() if " vs " in act_nombre else ""
            acel_mas3 = fila.get("gen2_acceleration_band8_total_effort_count") or 0
            m25 = fila.get("velocity_band8_total_distance") or 0
            metrics = [
                fila.get("average_distance_session"), fila.get("meterage_per_minute"),
                fila.get("velocity_band6_total_distance"), fila.get("velocity_band7_total_distance"),
                m25, fila.get("gen2_velocity_band8_total_effort_count"),
                fila.get("max_vel"), acel_mas3,
                fila.get("gen2_acceleration_band1_total_effort_count"),
                fila.get("gen2_acceleration_band2_total_effort_count"), None,  # RHIE: no disponible por API, ver comentario de CATAPULT_STATS_PARAMS
                fila.get("max_effort_acceleration"), fila.get("max_effort_deceleration"),
                round(acel_mas3 / minutos, 2) if minutos else 0,
                fila.get("high_speed_distance_per_minute"),
                round(m25 / minutos, 2) if minutos else 0,
                fila.get("total_player_load"),
            ]
            cat_out = out.setdefault(cat_real, {})
            cat_out.setdefault(nombre, {"pos": posiciones.get(nombre, ""), "match": []})
            registro = {"fecha": f"F{fecha_num}", "opp": rival, "min": minutos, "metrics": metrics}
            # A veces hay DOS actividades distintas en Catapult para el
            # mismo partido real (confirmado: "F9 - 4ta vs Talleres Cba" y
            # "F9- 4ta vs talleres" el mismo dia, cargas duplicadas del
            # lado de Catapult) -- si un jugador ya tiene un registro de
            # esa misma fecha, se queda con el que tenga mas minutos (mas
            # completo) en vez de guardar los dos (Javi, 2026-09-02).
            previos = cat_out[nombre]["match"]
            existente = next((r for r in previos if r["fecha"] == registro["fecha"]), None)
            if existente is None:
                previos.append(registro)
            elif registro["min"] > existente["min"]:
                previos[previos.index(existente)] = registro

    return out


def catapult_activity_athletes(opener, activity_id):
    """GET /activities/{id}/athletes -- el roster REAL de quienes jugaron
    esa actividad (con dispositivo puesto), sacado de los datos crudos.

    A proposito NO se usa /stats (source=cached_stats, lo que usa
    catapult_stats_post/fetch_catapult_players de arriba) para esto: esa
    cache puede estar incompleta si Catapult todavia no "horneo" del todo
    la actividad -- confirmado en vivo (2026-09-05): la F23 de 4TA vs
    Godoy Cruz tiene process_status=unprocessed, y /stats solo devolvia 2
    de los 15 jugadores reales, mientras que este endpoint (y /efforts
    por atleta) ya tienen los datos crudos completos igual. NO se toca
    fetch_catapult_players con este hallazgo todavia -- es un cambio mas
    grande (afecta a las 6 categorias en produccion) que se evalua aparte."""
    return catapult_get(opener, f"{CATAPULT_API_BASE}/activities/{activity_id}/athletes")


def catapult_activity_periods(opener, activity_id):
    """GET /activities/{id} -- trae 'periods' (nombre + start_time/end_time
    en Unix de cada tiempo del partido). Es el mismo dato que hasta ahora
    se calibraba a mano mirando el reloj quemado en el video (ver sesion
    Focus/OpenField del 2026-09-05) -- de aca sale automatico."""
    data = catapult_get(opener, f"{CATAPULT_API_BASE}/activities/{activity_id}")
    return data.get("periods") or []


def _catapult_velocity_merged(opener, activity_id, athlete_id, bands):
    """Baja los velocity_efforts de un atleta para las bandas pedidas y funde
    los solapados: la API los da en METROS POR SEGUNDO y separados por banda,
    asi que un mismo tramo que cruza varias bandas aparece como varias filas
    con tiempos superpuestos. Devuelve una lista de tramos unicos
    {start_time,end_time,max_velocity,distance} (velocidad en m/s todavia)."""
    qs = urllib.parse.urlencode({"effort_types": "velocity", "velocity_bands": bands})
    url = f"{CATAPULT_API_BASE}/activities/{activity_id}/athletes/{athlete_id}/efforts?{qs}"
    data = catapult_get(opener, url)
    raw = sorted((data[0].get("data") or {}).get("velocity_efforts") or [] if data else [],
                 key=lambda e: e.get("start_time") or 0)
    merged = []
    for e in raw:
        last = merged[-1] if merged else None
        if last is not None and (e.get("start_time") or 0) <= (last["end_time"] or 0) + 0.5:
            last["end_time"] = max(last["end_time"], e.get("end_time") or 0)
            last["max_velocity"] = max(last["max_velocity"], e.get("max_velocity") or 0)
            last["distance"] = max(last["distance"], e.get("distance") or 0)
        else:
            merged.append({
                "start_time": e.get("start_time"), "end_time": e.get("end_time") or e.get("start_time"),
                "max_velocity": e.get("max_velocity") or 0, "distance": e.get("distance") or 0,
            })
    return merged


def _catapult_effort_dict(e, tipo):
    return {
        "start": e["start_time"],
        "dur": round((e["end_time"] or 0) - (e["start_time"] or 0), 2),
        "vel": round((e["max_velocity"] or 0) * 3.6, 2),
        "dist": round(e["distance"] or 0, 2),
        "tipo": tipo,
    }


def catapult_efforts_por_atleta(opener, cj, activity_id, athlete_id, min_kmh=25):
    """Sprints (>=min_kmh) de un atleta en una actividad, ya limpios en km/h y
    con los tramos solapados fundidos. Validado en vivo contra los 11 sprints
    de Pannoni en la F23 que ya se habian sacado a mano de OpenField Cloud:
    coincide exacto (misma hora, duracion, velocidad y distancia en los 11).
    cj se mantiene por compatibilidad de firma (el GET usa la cookie del
    opener, no hace falta XSRF para leer)."""
    merged = _catapult_velocity_merged(opener, activity_id, athlete_id, "7,8")
    return [_catapult_effort_dict(e, "sprint") for e in merged
            if round((e["max_velocity"] or 0) * 3.6, 2) >= min_kmh]


def catapult_hsr_por_atleta(opener, cj, activity_id, athlete_id, lo_kmh=21, hi_kmh=25):
    """Carreras de alta velocidad (lo_kmh <= pico < hi_kmh, tipo "hsr"), la
    HSR que ya define el club (21-25 km/h). Banda 6 (>=~18 km/h) para no
    perder nada del piso de 21 y despues se filtra el rango; el corte <hi_kmh
    deja los sprints (>=25) afuera, asi no se cuenta dos veces el mismo
    tramo (confirmado: 0 colisiones de start_time con los sprints)."""
    merged = _catapult_velocity_merged(opener, activity_id, athlete_id, "6")
    return [_catapult_effort_dict(e, "hsr") for e in merged
            if lo_kmh <= round((e["max_velocity"] or 0) * 3.6, 2) < hi_kmh]


def fetch_catapult_efforts(email: str, password: str, cats, existentes=None, min_kmh=25):
    """Esfuerzos individuales (sprints, >=min_kmh) por jugador y fecha, mas
    los horarios reales de cada periodo (para calibrar despues el salto a
    video) -- pensado para "clic en la metrica destacada -> ver el
    momento en video", complementario a fetch_catapult_players (que solo
    trae totales de sesion, sin hora de cada esfuerzo puntual).

    Solo procesa las categorias en `cats` (hoy: ["4TA"], a proposito --
    cada partido son muchos pedidos de a un jugador por vez, mas caro que
    el resto del scraper). INCREMENTAL: si `existentes` (el
    catapult_efforts de la corrida anterior) ya tiene una fecha resuelta
    para una categoria, se la saltea entera -- así las corridas de rutina
    (cada 4hs) no vuelven a pedir partidos viejos, solo el que sea nuevo.

    No toca fetch_catapult_players ni catapult_gps -- pipeline separado a
    proposito (mismo criterio que bl_gps vs catapult_gps, ver comentario
    de fetch_catapult_players)."""
    opener, cj = catapult_login(email, password)
    existentes = existentes or {}

    teams = catapult_get(opener, f"{CATAPULT_API_BASE}/teams")
    team_ids_por_cat = {CATAPULT_TEAMS.get(t.get("name")): t["id"] for t in teams
                         if CATAPULT_TEAMS.get(t.get("name")) in cats}

    out = {}
    for cat, team_id in team_ids_por_cat.items():
        actividades = catapult_get(opener, f"{CATAPULT_API_BASE}/activities"
                                    f"?page=1&page_size=100&sort=-start_time&deleted=0&team_ids={team_id}")
        fecha_por_activity_id = _catapult_actividades_partido(actividades, cat)
        nombre_por_activity_id = {a["id"]: a.get("name") or "" for a in actividades}

        activities_por_fecha = {}
        for activity_id, fecha_num in fecha_por_activity_id.items():
            activities_por_fecha.setdefault(fecha_num, []).append(activity_id)

        cat_prev = (existentes.get(cat) or {})
        cat_out = dict(cat_prev)  # arranca con lo viejo, solo se pisan las fechas nuevas
        nuevas = 0
        for fecha_num, activity_ids in activities_por_fecha.items():
            fecha_key = f"F{fecha_num}"
            if fecha_key in cat_prev:
                continue  # ya resuelta en una corrida anterior, no se vuelve a pedir

            # Una fecha puntual con una actividad rota en Catapult (404,
            # id borrado, lo que sea) no debe tirar abajo el resto de las
            # fechas de esta categoria NI las otras categorias pedidas en
            # la misma corrida -- confirmado en vivo (2026-09-18): al
            # sumar 5TA/6TA, un 404 puntual abortaba tambien 4TA aunque ya
            # estuviera resuelto. Mismo criterio que el resto del scraper
            # ("un partido puntual con la pagina rota no debe tirar abajo
            # toda la temporada").
            try:
                rival = ""
                for aid in activity_ids:
                    nombre_act = nombre_por_activity_id.get(aid, "")
                    if " vs " in nombre_act:
                        rival = nombre_act.split(" vs ")[-1].strip()
                        break

                jugadores_roster = {}  # nombre -> (activity_id, athlete_id)
                periodos = []
                for aid in activity_ids:
                    for atl in catapult_activity_athletes(opener, aid):
                        nombre = f"{atl.get('first_name', '')} {atl.get('last_name', '')}".strip()
                        if nombre and atl.get("id"):
                            jugadores_roster.setdefault(nombre, (aid, atl["id"]))
                    for p in catapult_activity_periods(opener, aid):
                        periodos.append({"name": p.get("name"), "start": p.get("start_time"), "end": p.get("end_time")})

                # Ventanas de los dos tiempos del partido (Catapult marca
                # "Primer/Segundo tiempo"). Se recortan los esfuerzos a esas
                # ventanas para no traer calentamiento u otra sesion del dia,
                # que despues caian mal en el video (segundo negativo). Mismo
                # criterio que la app (gpsVideoFormHTML/gpsVideoSeg). Si no hay
                # periodos con nombre de tiempo, no se filtra (fallback).
                def _es_tiempo(nm):
                    nm = (nm or "").lower()
                    return "primer" in nm or "segundo" in nm
                ventanas = [(p["start"], p["end"]) for p in periodos
                            if p.get("start") and p.get("end") and _es_tiempo(p.get("name"))]
                def _en_partido(e):
                    s = e.get("start")
                    return s is not None and (not ventanas or any(a <= s <= b for a, b in ventanas))
                jugadores_out = {}
                for nombre, (aid, athlete_id) in jugadores_roster.items():
                    nombre_norm = _catapult_norm_nombre(nombre)
                    if nombre_norm in CATAPULT_ALIAS_NOMBRE:
                        nombre = CATAPULT_ALIAS_NOMBRE[nombre_norm]
                    # No se descarta si no matchea el plantel (a diferencia de
                    # fetch_catapult_players) -- acá alcanza con haber jugado
                    # esa actividad, el filtro de categoria real ya lo hizo
                    # _catapult_actividades_partido/team_id al elegir la
                    # actividad. Igual se deja constancia en el nombre tal cual
                    # vino de Catapult para que el matcheo en la app (mismo
                    # criterio que gpsAliasedName) lo pueda resolver despues.
                    esf = catapult_efforts_por_atleta(opener, cj, aid, athlete_id, min_kmh)
                    esf += catapult_hsr_por_atleta(opener, cj, aid, athlete_id)
                    esf = [e for e in esf if _en_partido(e)]
                    jugadores_out[nombre] = sorted(esf, key=lambda e: e.get("start") or 0)
            except Exception as e:  # noqa
                print(f"[AVISO] Catapult efforts {cat} {fecha_key}: {e} -- se saltea esta fecha.", file=sys.stderr)
                continue

            cat_out[fecha_key] = {"opp": rival, "periodos": periodos, "jugadores": jugadores_out}
            nuevas += 1

        if nuevas:
            print(f"[OK] Catapult efforts {cat}: {nuevas} fecha(s) nueva(s) procesada(s)")
        out[cat] = cat_out

    return out


# ── VIDEO — deteccion automatica de arranque de cada tiempo ─────────────
# "Esfuerzos en video" (ver gpsVideoSeg en index.html) necesita, por cada
# fecha, el segundo exacto del video de YouTube donde arranca cada tiempo
# (gps/videoSync en Firebase) para poder saltar al momento justo de un
# esfuerzo puntual (que ya trae fetch_catapult_efforts de arriba, con
# hora real). Hasta ahora eso se cargaba siempre a mano, mirando el video.
#
# Esto lo automatiza para los partidos que traen quemado en la esquina un
# cartel con el tiempo (1T/2T) y el reloj del partido (cámara "VEO",
# 2026-09-18): se lee con OCR y se ubica el segundo exacto por búsqueda,
# igual que se haría mirando el video a mano. Confirmado que NO todos los
# videos tienen ese cartel (uno viejo de marzo no lo trae) -- si no se
# encuentra, la fecha simplemente queda sin tocar para calibrar a mano
# como siempre, nunca se inventa nada.
#
# Requiere paquetes de Python que NO son parte del resto de este script
# a propósito (para que el resto del scraper siga corriendo en cualquier
# PC sin ningún pip install): yt-dlp, imageio-ffmpeg, pytesseract, Pillow
# -- más Tesseract OCR instalado en la PC (el programa en sí, aparte del
# paquete de Python). Si algo de esto falta, esta sección entera se
# saltea sola, mismo criterio que FUTDETAIL_USER/CATAPULT_USER.
try:
    import io as _video_io
    import shutil as _video_shutil
    import subprocess as _video_subprocess
    import yt_dlp
    import imageio_ffmpeg
    import pytesseract
    from PIL import Image as _VideoImage
    VIDEO_SYNC_DISPONIBLE = True
except ImportError:
    VIDEO_SYNC_DISPONIBLE = False

_TESSERACT_CANDIDATOS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
]


def _video_configurar_tesseract():
    """pytesseract busca 'tesseract' en el PATH -- recien instalado, en
    Windows a veces no aparece todavia ahi (hace falta abrir una terminal
    nueva). Si no lo encuentra, prueba las rutas tipicas del instalador."""
    if _video_shutil.which("tesseract"):
        return True
    for candidato in _TESSERACT_CANDIDATOS:
        if os.path.exists(candidato):
            pytesseract.pytesseract.tesseract_cmd = candidato
            return True
    return False


# Lee "1T 0:00" / "2T 15:07", etc. Tesseract confunde la T del cartel con
# un 7 (fuente estilizada) de forma consistente -- confirmado con datos
# reales, "1T" sale como "17" y "2T" como "27" -- por eso el regex acepta
# T o 7 como segundo caracter en vez de pelear con eso.
# Tolerante con la lectura del "1T"/"2T" (el OCR a veces lo lee "17", "11",
# "1 1"): el periodo tiene que estar separado del reloj por espacio o "_".
VIDEO_PERIODO_CLOCK_RE = re.compile(r"([12])\s*[T7I1l|][\s_]+(\d{1,3}):(\d{2})")


def _video_leer_marcador(frame_bytes):
    """Recorta la esquina donde va el cartel quemado (1T/2T + reloj) y lo
    lee con OCR. Devuelve (periodo, segundos_de_reloj) o None si no hay
    cartel reconocible en este frame (video sin ese overlay, tapado por
    algo, o mitad de una transicion).

    El recorte es en PROPORCION del ancho/alto del frame (no en pixeles
    fijos) para que sirva sin importar la resolucion real del video --
    calibrado a ojo con el cartel de la camara VEO (esquina superior
    izquierda), confirmado 2026-09-18 con la F24 de 4TA vs Platense."""
    im = _VideoImage.open(_video_io.BytesIO(frame_bytes))
    w, h = im.size
    # Primero el recorte angosto (solo periodo + reloj, camara VEO con
    # cartel corto); si no lee, uno mas ancho que incluye los nombres de
    # equipo (cartel largo, ej. "TIG 0 0 GDC 1T 4:57" en 5TA, 2026-09-19).
    m = None
    for x0, x1 in ((0.19, 0.34), (0.0, 0.30)):
        crop = im.crop((int(w*x0), 0, int(w*x1), int(h*0.10)))
        if crop.width < 10 or crop.height < 10:
            continue
        factor = max(1, 300 // max(crop.width, 1))
        crop = crop.resize((crop.width*factor, crop.height*factor))
        texto = pytesseract.image_to_string(crop, config="--psm 8")
        m = VIDEO_PERIODO_CLOCK_RE.search(texto)
        if m:
            break
    if not m:
        return None
    periodo = int(m.group(1))
    segundos = int(m.group(2))*60 + int(m.group(3))
    return periodo, segundos


def _video_frame_en(stream_url, segundo, ffmpeg_exe):
    """Un solo frame (bytes JPEG) del video en el segundo pedido, via seek
    rapido de ffmpeg directo sobre la URL (sin descargar el video entero --
    YouTube soporta range requests). None si el segundo esta fuera de rango o
    el stream se corto."""
    cmd = [ffmpeg_exe, "-ss", str(max(0, segundo)), "-i", stream_url,
           "-vframes", "1", "-q:v", "4", "-f", "image2pipe", "-vcodec", "mjpeg", "-"]
    try:
        proc = _video_subprocess.run(cmd, capture_output=True, timeout=25)
    except Exception:
        return None
    return proc.stdout or None


def _video_leer_en(stream_url, segundo, ffmpeg_exe):
    """Lee el cartel VEO (1T/2T + reloj) en el segundo pedido. None si no hay
    cartel legible ahi."""
    frame = _video_frame_en(stream_url, segundo, ffmpeg_exe)
    if not frame:
        return None
    try:
        return _video_leer_marcador(frame)
    except Exception:
        return None


def detectar_kickoffs_video(youtube_url, duracion_minima_1t=15*60):
    """Encuentra el segundo exacto de arranque de 1er y 2do tiempo en un
    video de YouTube con el cartel quemado de la camara VEO. Devuelve
    {"kickoff1":seg, "kickoff2":seg} o None si no se pudo (sin ese
    cartel, formato distinto, algo salio mal) -- la fecha queda para
    calibrar a mano en ese caso.

    Algoritmo (el mismo que se haria a mano mirando el video):
    1) Busca el arranque del 1er tiempo probando los primeros segundos
       del video (los partidos filmados asi arrancan grabando ya con el
       cartel puesto, siempre dentro del primer minuto y medio).
    2) Busca por biseccion el momento exacto donde el cartel pasa de "1T"
       a "2T" -- sin asumir nada de cuanto dura el entretiempo EN EL
       VIDEO (a veces esta editado/recortado: confirmado con la F24 de
       4TA, calcular el segundo tiempo a partir del horario que da
       Catapult a secas daba un resultado ~16 minutos mal).
    3) Una vez ubicado el cambio de tiempo, ajusta fino para encontrar el
       primer frame que diga exactamente "0:00" en cada tiempo.
    """
    if not VIDEO_SYNC_DISPONIBLE or not _video_configurar_tesseract():
        return None

    # 720p si esta disponible -- el cartel es chico, mas resolucion ayuda
    # al OCR en videos con mas compresion/ruido. Cae a resoluciones mas
    # chicas si el video no tiene 720p (formatos "https" directos, no
    # m3u8, para poder hacer seek rapido sin descargar todo el video).
    ydl_opts = {"quiet": True, "no_warnings": True, "format": "136/135/134/160/243"}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            stream_url = info["url"]
            duracion = info.get("duration") or 6*3600
    except Exception:
        return None

    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    leer = lambda seg: _video_leer_en(stream_url, seg, ffmpeg_exe)  # noqa: E731

    # Primero fino (cada 4s) en el primer minuto y medio -- el caso mas
    # comun, la camara ya arranca grabando con el cartel puesto. Si no
    # aparece ahi, un segundo barrido mas grueso hasta los 10 minutos, por
    # las dudas de que haya un poco de previa/entrada en cancha antes de
    # que se vea el cartel (confirmado que hace falta con algunos partidos
    # cargados a mano por Javi, 2026-09-18).
    kickoff1 = None
    candidatos_1t = list(range(0, 90, 4)) + list(range(90, 600, 15))
    for candidato in candidatos_1t:
        r = leer(candidato)
        if r and r[0] == 1:
            estimado = candidato - r[1]
            for ajuste in range(max(0, estimado-3), estimado+4):
                if leer(ajuste) == (1, 0):
                    kickoff1 = ajuste
                    break
            if kickoff1 is None:
                kickoff1 = max(0, estimado)
            break
    if kickoff1 is None:
        return None  # sin cartel reconocible -- video sin overlay, o formato distinto

    # Barrido grueso buscando CUALQUIER lectura valida de 2T (el reloj del
    # 2T es continuo, asi que kickoff2 = segundo_del_video - reloj). Una
    # lectura "2T" solo vale si t - reloj queda bien despues del arranque
    # del 1T (descarta lecturas confundidas). Reemplaza a la biseccion: en
    # 5TA el video termina sin cartel (no hay lectura cerca del final) y el
    # OCR a veces lee "2T" como "1T", lo que rompia la biseccion.
    estimado2 = None
    for t in range(kickoff1 + duracion_minima_1t, int(duracion) - 10, 90):
        r = leer(t)
        if r and r[0] == 2 and t - r[1] >= kickoff1 + duracion_minima_1t - 60:
            estimado2 = t - r[1]
            break
    if estimado2 is None:
        return None
    kickoff2 = None
    for ajuste in range(max(0, estimado2-5), estimado2+6):
        if leer(ajuste) == (2, 0):
            kickoff2 = ajuste
            break
    if kickoff2 is None:
        kickoff2 = max(0, estimado2)

    return {"kickoff1": float(kickoff1), "kickoff2": float(kickoff2)}


# ── Cartel LPF (partidos de local, transmision oficial) ─────────────────
# A diferencia del cartel VEO, NO trae "1T/2T": solo un reloj corrido de
# partido en una caja arriba al centro-izquierda (~x 0.33-0.44). Cuenta
# 0:00 -> 45:00 en el 1T y sigue 45:00 -> 90:00 en el 2T (se congela en el
# entretiempo). Se calibra por el "offset" (segundo_de_video - reloj) de
# cada tiempo: kickoff1 = offset del 1T; kickoff2 = 45:00 + offset del 2T.
# Validado contra F13 (3/2791) y F5 (3/2730) de 4TA, 2026-09-19.
_VIDEO_RELOJ_LPF_RE = re.compile(r"(\d{1,3}):(\d{2})")


def _video_leer_reloj_lpf(frame_bytes):
    """Lee el reloj del cartel LPF. Devuelve segundos de reloj (int) o None
    si no hay reloj legible ahi (video sin ese overlay)."""
    im = _VideoImage.open(_video_io.BytesIO(frame_bytes))
    w, h = im.size
    # x 0.30-0.44: el reloj se corre horizontalmente segun el ancho del cuadro
    # de equipos/marcador (en 6TA queda mas a la izquierda que en 4TA), asi que
    # el recorte es ancho para cubrir las dos posiciones. El whitelist de
    # digitos + el RANSAC descartan cualquier texto del marcador que se cuele.
    crop = im.crop((int(w*0.30), int(h*0.02), int(w*0.44), int(h*0.11))).convert("L")
    crop = crop.resize((crop.width*4, crop.height*4))
    # Primero binarizado (texto blanco sobre caja); si no, el gris directo.
    for img in (crop.point(lambda p: 255 if p > 170 else 0), crop):
        txt = pytesseract.image_to_string(img, config="--psm 7 -c tessedit_char_whitelist=0123456789:")
        m = _VIDEO_RELOJ_LPF_RE.search(txt)
        if m and int(m.group(2)) < 60:
            return int(m.group(1)) * 60 + int(m.group(2))
    return None


def _video_offset_ransac(pares, tol=6):
    """De una lista de (segundo_video, reloj_segundos) devuelve (offset, n):
    el offset = segundo_video - reloj que MAS puntos comparten (tipo RANSAC),
    robusto a lecturas sueltas que el OCR lee mal (un digito fantasma agranda
    el reloj -> offset negativo, imposible: se descarta). None si no hay
    consenso."""
    cands = sorted({t - c for t, c in pares if (t - c) >= -3})
    mejor_off, mejor_n = None, 0
    for cand in cands:
        n = sum(1 for t, c in pares if abs((t - c) - cand) <= tol)
        if n > mejor_n:
            mejor_off, mejor_n = cand, n
    if mejor_off is None:
        return None, 0
    inliers = sorted(t - c for t, c in pares if abs((t - c) - mejor_off) <= tol)
    return inliers[len(inliers) // 2], len(inliers)


def detectar_kickoffs_lpf(youtube_url):
    """Como detectar_kickoffs_video pero para el cartel LPF (reloj corrido).
    Muestrea el reloj en la 1a parte del video (1T) y en la 2a mitad (2T),
    saca el offset robusto de cada tiempo y calcula los kickoffs. None si no
    hay reloj legible (video sin cartel, tipico de partidos de visitante)."""
    if not VIDEO_SYNC_DISPONIBLE or not _video_configurar_tesseract():
        return None
    ydl_opts = {"quiet": True, "no_warnings": True, "format": "136/135/134/160/243"}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            stream_url = info["url"]
            duracion = int(info.get("duration") or 6 * 3600)
    except Exception:
        return None
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    def leer(t):
        f = _video_frame_en(stream_url, t, ffmpeg_exe)
        return _video_leer_reloj_lpf(f) if f else None

    # 1T: primeros ~34 min de video (reloj < 40:00, seguro en 1er tiempo).
    # Muestreo denso (cada 120s) para juntar suficientes lecturas limpias: el
    # OCR del reloj es ruidoso y el clustering RANSAC necesita volumen.
    pts1 = [(t, leer(t)) for t in range(60, 2100, 120)]
    pts1 = [(t, c) for t, c in pts1 if c is not None and c < 2400]
    off1, n1 = _video_offset_ransac(pts1)
    if off1 is None or n1 < 3:
        return None
    # 2T: segunda mitad del video (reloj > 47:00), evitando el borde de 45:00
    # del entretiempo. ~14 muestras entre el 55% y el 92% del video.
    paso2 = max(120, (int(duracion*0.92) - int(duracion*0.55)) // 13)
    pts2 = [(t, leer(t)) for t in range(int(duracion*0.55), int(duracion*0.92), paso2)]
    pts2 = [(t, c) for t, c in pts2 if c is not None and 2820 < c < 5400]
    off2, n2 = _video_offset_ransac(pts2)
    if off2 is None or n2 < 3:
        return None
    kickoff1 = max(0, off1)
    kickoff2 = 2700 + off2  # el 2T arranca en 45:00 del reloj de partido
    if not (0 <= kickoff1 <= 600 and kickoff1 + 2100 <= kickoff2 <= kickoff1 + 4200):
        return None
    return {"kickoff1": float(kickoff1), "kickoff2": float(kickoff2)}


# -- Hora real del video: la via mas barata y exacta (2026-09-20) -------
# Los dos detectores de arriba miran el video (bajan cuadros y los pasan por
# OCR) para saber en que segundo arranca cada tiempo. Ese dato se puede
# deducir SIN mirar un solo cuadro cuando el video fue una TRANSMISION EN
# VIVO: YouTube guarda la hora real en que arranco el stream
# (liveBroadcastDetails.startTimestamp, que yt-dlp expone como
# release_timestamp) y Catapult ya nos da la hora real de arranque de cada
# tiempo (periodos[].start, epoch). Con las dos:
#
#     kickoff_N = periodo_N.start - hora_real_del_segundo_0_del_video
#
# Ademas de ser ~100 veces mas barato que el OCR, es MAS preciso: la app
# despues calcula kickoff + (hora_esfuerzo - periodo.start), asi que si el
# staff marco el periodo corrido en OpenField -- o si el que opera el reloj
# del cartel lo arranco tarde -- el error entra y sale por el mismo lado y
# se cancela solo. El OCR, en cambio, calibra contra el cartel y se come
# ese desfasaje entero.
#
# Solo vale si el video es la transmision entera y sin cortes: si pausaron
# el stream (tipico en el entretiempo) el 2T queda corrido, asi que se
# valida que el video sea lo bastante largo como para contener los dos
# tiempos completos. Si no da, devuelve None y sigue el camino del OCR.
_VIDEO_TOLERANCIA_FIN = 600   # seg que puede faltarle al video al final (cortaron el stream antes de que el staff cerrara el periodo)
_VIDEO_PREVIA_MAX = 3600      # seg de previa del stream antes del saque inicial que se consideran creibles
_VIDEO_VIA_ACTUAL = "metadata+ocr"  # cambiar si se suma una via nueva -> reintenta los fallos viejos una vez
_VIDEO_SONDEOS_MAX = 8        # cuantos videos se consultan buscando transmisiones en vivo antes de rendirse
# Medido el 2026-09-20 sobre las 55 fechas con link: NINGUNA es transmision en
# vivo (el club transmite, pero a YouTube sube el archivo despues, y ahi YouTube
# borra la hora de grabacion). O sea que hoy esta via no entra nunca. Se deja
# igual porque no cuesta casi nada y es la mas precisa el dia que suba un vivo,
# pero se corta sola: si los primeros videos de la corrida no son en vivo, no se
# pregunta por el resto.
_video_vivos = {"vistos": 0, "encontrados": 0}


def _video_vale_la_pena_metadata():
    """False cuando ya se consultaron varios videos en esta corrida y ninguno
    era transmision en vivo -- evita gastar una consulta por fecha al pedo."""
    return _video_vivos["encontrados"] > 0 or _video_vivos["vistos"] < _VIDEO_SONDEOS_MAX


def _video_periodos_1y2(periodos):
    """Los dos tiempos del partido de la actividad de Catapult, con el mismo
    criterio de nombres que usa la app (gpsVideoSeg en index.html). Devuelve
    (None, None) si falta alguno o si les falta la hora."""
    p1 = p2 = None
    for p in periodos or []:
        nombre = p.get("name") or ""
        if p1 is None and re.search("rimer", nombre, re.I):
            p1 = p
        elif p2 is None and re.search("egundo", nombre, re.I):
            p2 = p
    if not (p1 and p2 and p1.get("start") and p2.get("start") and p2.get("end")):
        return None, None
    return p1, p2


def _video_metadata_yt(youtube_url):
    """Metadata del video sin bajar nada (~2s): si fue transmision en vivo, a
    que hora real arranco y cuanto dura. None si no se pudo."""
    if not VIDEO_SYNC_DISPONIBLE:
        return None
    try:
        with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "skip_download": True}) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
    except Exception:
        return None
    meta = {"live_status": info.get("live_status"),
            "release_timestamp": info.get("release_timestamp"),
            "duration": info.get("duration")}
    _video_vivos["vistos"] += 1
    if meta["live_status"] in ("was_live", "is_live") and meta["release_timestamp"]:
        _video_vivos["encontrados"] += 1
    return meta


# Formatos de YouTube en orden de preferencia: 'https' directo (no m3u8) para
# poder saltar a un segundo puntual sin bajar el video entero. El liviano
# arranca por la calidad mas baja -- alcanza de sobra para ver si la imagen
# cambia de golpe, y baja y decodifica mucho mas rapido.
_VIDEO_FORMATO = "136/135/134/160/243"
_VIDEO_FORMATO_LIVIANO = "160/134/135/136/243"


def _video_stream_url(youtube_url, formato=_VIDEO_FORMATO):
    """URL directa del video para sacarle cuadros con ffmpeg."""
    try:
        with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True,
                               "format": formato}) as ydl:
            return ydl.extract_info(youtube_url, download=False)["url"]
    except Exception:
        return None


def _video_verificar_2t(youtube_url, kickoff2, ventana=300):
    """Confirma con UN solo cuadro que el arranque del 2do tiempo calculado por
    hora real cae donde tiene que caer: mira el cartel en kickoff2+ventana y
    se fija que el reloj del partido vaya por ahi.

    Sirve de red contra el unico caso feo de esta via: que hayan PAUSADO la
    transmision en el entretiempo (ahi el video dura menos que el reloj real y
    el 2T queda corrido varios minutos, sin que ninguna otra cuenta lo note).
    Devuelve True tambien cuando el video no tiene cartel legible -- eso no
    prueba nada en contra, y el chequeo de duracion ya descarto lo grosero."""
    if not _video_configurar_tesseract():
        return True
    stream_url = _video_stream_url(youtube_url)
    if not stream_url:
        return True
    frame = _video_frame_en(stream_url, int(kickoff2 + ventana), imageio_ffmpeg.get_ffmpeg_exe())
    if not frame:
        return True
    try:
        veo = _video_leer_marcador(frame)   # cartel VEO: (periodo, reloj del tiempo)
    except Exception:
        veo = None
    if veo:
        return veo[0] == 2 and abs(veo[1] - ventana) <= 120
    reloj = _video_leer_reloj_lpf(frame)    # cartel LPF: reloj corrido, el 2T arranca en 45:00
    if reloj is not None:
        return abs(reloj - (2700 + ventana)) <= 120
    return True


def detectar_kickoffs_metadata(youtube_url, periodos, offset=0.0, meta=None):
    """kickoff1/kickoff2 a partir de la hora real de arranque del stream.
    None si el video no fue transmision en vivo, si YouTube no da esa hora, o
    si el video no cubre los dos tiempos completos (stream pausado, o
    arrancado despues del saque inicial), o si el cartel del partido desmiente
    el 2T calculado -- en todos esos casos sigue el OCR.
    'offset' es la correccion medida contra las fechas ya calibradas (ver
    _video_metadata_offset)."""
    p1, p2 = _video_periodos_1y2(periodos)
    if not p1:
        return None
    meta = meta or _video_metadata_yt(youtube_url)
    if not meta or meta.get("live_status") not in ("was_live", "is_live"):
        return None   # video subido como archivo: YouTube ya le borro la hora de grabacion
    rts, duracion = meta.get("release_timestamp"), meta.get("duration")
    if not rts or not duracion:
        return None
    ancla = rts + offset
    k1 = p1["start"] - ancla
    k2 = p2["start"] - ancla
    if not (0 <= k1 <= _VIDEO_PREVIA_MAX) or k2 <= k1:
        return None   # el stream arranco despues del saque inicial, o la hora no cierra
    if k2 + (p2["end"] - p2["start"]) > duracion + _VIDEO_TOLERANCIA_FIN:
        return None   # el video dura menos de lo que deberia -> lo pausaron o esta editado
    if not _video_verificar_2t(youtube_url, k2):
        return None   # el cartel dice otra cosa en el 2T -> transmision pausada, que lo resuelva el OCR
    return {"kickoff1": float(k1), "kickoff2": float(k2), "fuente": "metadata"}


def _video_metadata_offset(catapult_efforts, token, muestras=5):
    """Mide el desfasaje de la via de metadata contra las fechas que YA estan
    calibradas (por OCR o a mano): compara el kickoff1 guardado contra el que
    sale de la hora real del stream. Devuelve la correccion en segundos a
    aplicar en esta corrida. Asi la via nueva se auto-calibra sola contra lo
    ya verificado, sin ninguna constante para mantener a mano. 0 si no hay
    muestras suficientes, o si las muestras no se parecen entre si (ahi el
    dato no es confiable y es mejor no corregir nada)."""
    errores = []
    sondeos = 0   # cada sondeo es una consulta a YouTube: hay que acotarlos
    for cat, fechas in (catapult_efforts or {}).items():
        for fecha_key, dia in fechas.items():
            if len(errores) >= muestras or sondeos >= _VIDEO_SONDEOS_MAX:
                break
            p1, _ = _video_periodos_1y2((dia or {}).get("periodos"))
            if not p1:
                continue
            try:
                sync = _tigre_fb_get("gps/videoSync/%s/%s" % (cat, fecha_key), token())
                # Solo contra calibraciones hechas por OCR o a mano: medirse
                # contra una fecha que YA salio por esta misma via seria
                # confirmar la correccion con ella misma.
                if not sync or sync.get("kickoff1") is None or sync.get("fuente") == "metadata":
                    continue
                link = _tigre_fb_get("stats/links/%s/%s/par" % (cat, fecha_key.lstrip("F")), token())
            except Exception:
                continue
            if not link:
                continue
            meta = _video_metadata_yt(link)
            sondeos += 1
            if not meta or meta.get("live_status") not in ("was_live", "is_live") or not meta.get("release_timestamp"):
                continue
            errores.append((p1["start"] - meta["release_timestamp"]) - float(sync["kickoff1"]))
    if len(errores) < 3:
        return 0.0
    errores.sort()
    mediana = errores[len(errores) // 2]
    if errores[-1] - errores[0] > 30:
        print("[AVISO] Video: la hora real del stream no concuerda con las fechas ya "
              "calibradas (%s) -- se usa sin corregir y conviene revisarlo con "
              "scripts/medir_video_sync.py" % ", ".join("%.0f" % e for e in errores))
        return 0.0
    if abs(mediana) >= 2:
        print("[OK] Video: la hora real del stream se corrige en %+.1fs "
              "(medido contra %d fecha(s) ya calibradas)" % (mediana, len(errores)))
    return float(mediana)


# --- Arranque del 2do tiempo por el CORTE del entretiempo -------------------
# A TODOS los videos les recortan el entretiempo (medido el 2026-09-20: 0 de 17
# continuos), asi que en algun punto hay un corte seco entre el final del 1er
# tiempo y el arranque del 2do. Ese corte se puede encontrar SIN leer ningun
# cartel: la imagen cambia de golpe entre un cuadro y el siguiente. Es la via
# automatica que queda para los videos que el OCR no puede leer (los de
# visitante, filmados a mano y sin marcador en pantalla).
#
# El arranque del 1er tiempo no hace falta detectarlo: a estos videos tambien
# les recortan la previa y arrancan en el saque inicial (0-5s en las 17 fechas
# ya calibradas, mediana 3), y la app muestra 4s antes de cada esfuerzo, asi
# que un par de segundos de error no se notan.
_VIDEO_K1_TIPICO = 3.0         # de ultima; en la corrida se usa la mediana real
_VIDEO_HUECO_TIPICO = 2750.0   # idem (2699-2795 en las 17 fechas medidas)
_VIDEO_CORTE_MARGEN = 150      # cuanto se mira a cada lado del hueco tipico
_VIDEO_CORTE_UMBRAL = 0.12     # que tan distinto tiene que ser un cuadro del anterior
_VIDEO_CORTE_AJUSTE = 0.0      # correccion fija (el corte puede caer unos segundos antes del saque)
# Con que criterio elegir cuando en la ventana hay mas de un corte: "fuerte" =
# el cambio de imagen mas marcado, "cercano" = el que cae mas cerca de donde
# suele arrancar el 2T. Lo decide la medicion (medir_video_sync.py --cortes).
_VIDEO_CORTE_REGLA = "fuerte"


def _video_cortes_escena(stream_url, desde, hasta, ffmpeg_exe, umbral=_VIDEO_CORTE_UMBRAL):
    """Segundos del video (absolutos) donde la imagen cambia de golpe, dentro
    de la ventana pedida. Devuelve [(segundo, cuanto_cambio), ...] ordenado por
    segundo. Solo decodifica esa ventana, no el video entero."""
    desde = int(max(0, desde))
    dur = max(1, int(hasta) - desde)
    # OJO: el "-t" va ANTES del "-i" a proposito. Como option de salida no
    # corta nada aca (el filtro descarta todos los cuadros iguales, asi que al
    # final de la cadena no llega ninguno que pase del limite y ffmpeg sigue
    # leyendo el video entero); como option de entrada si limita lo que baja.
    cmd = [ffmpeg_exe, "-ss", str(desde), "-t", str(dur), "-i", stream_url,
           "-an", "-sn",
           "-vf", "select='gt(scene,%.3f)',metadata=print:file=-" % umbral,
           "-f", "null", "-"]
    try:
        proc = _video_subprocess.run(cmd, capture_output=True, timeout=300)
    except Exception:
        return []
    cortes, pendiente = [], None
    for linea in (proc.stdout or b"").decode("utf-8", "ignore").splitlines():
        m = re.search(r"pts_time:([0-9.]+)", linea)
        if m:
            pendiente = float(m.group(1))
            # ffmpeg a veces arranca el reloj de cero en el punto de corte y a
            # veces mantiene el del video entero; se distingue solo, porque la
            # ventana que miramos arranca muy lejos del segundo 0.
            if pendiente <= dur + 5:
                pendiente += desde
            continue
        m = re.search(r"scene_score=([0-9.]+)", linea)
        if m and pendiente is not None:
            cortes.append((pendiente, float(m.group(1))))
            pendiente = None
    return sorted(cortes)


def detectar_kickoffs_corte(youtube_url, k1=None, hueco=None, margen=_VIDEO_CORTE_MARGEN):
    """kickoff1/kickoff2 buscando el corte del entretiempo dentro de una
    ventana angosta alrededor del hueco tipico. None si ahi no hay ningun corte
    claro -- nunca inventa un valor."""
    if not VIDEO_SYNC_DISPONIBLE:
        return None
    k1 = _VIDEO_K1_TIPICO if k1 is None else float(k1)
    hueco = _VIDEO_HUECO_TIPICO if hueco is None else float(hueco)
    stream_url = _video_stream_url(youtube_url, _VIDEO_FORMATO_LIVIANO)
    if not stream_url:
        return None
    desde, hasta = k1 + hueco - margen, k1 + hueco + margen
    cortes = _video_cortes_escena(stream_url, desde, hasta, imageio_ffmpeg.get_ffmpeg_exe())
    if not cortes:
        return None
    if _VIDEO_CORTE_REGLA == "cercano":
        segundo = min(cortes, key=lambda c: abs(c[0] - (k1 + hueco)))[0]
    else:
        segundo = max(cortes, key=lambda c: c[1])[0]
    segundo += _VIDEO_CORTE_AJUSTE
    if not (desde <= segundo <= hasta):
        return None
    return {"kickoff1": round(k1, 1), "kickoff2": round(segundo, 1), "fuente": "corte"}


def detectar_kickoffs_auto(youtube_url, periodos=None, offset=0.0):
    """Prueba primero la hora real del stream (detectar_kickoffs_metadata, sin
    mirar el video) y, si el video no fue transmision en vivo, los carteles:
    VEO (1T/2T explicito) y si no LPF (reloj corrido). Clasifica antes con un
    par de frames para no barrer todo el video con el detector VEO cuando el
    cartel es LPF. None si no se pudo por ninguna via (tipico de los partidos
    de visitante filmados a mano) -> calibrar a mano."""
    if not VIDEO_SYNC_DISPONIBLE:
        return None
    if periodos and _video_vale_la_pena_metadata():
        por_metadata = detectar_kickoffs_metadata(youtube_url, periodos, offset)
        if por_metadata:
            return por_metadata
    if not _video_configurar_tesseract():
        return None
    ydl_opts = {"quiet": True, "no_warnings": True, "format": "136/135/134/160/243"}
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            stream_url = info["url"]
    except Exception:
        return None
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    es_veo = es_lpf = False
    for t in (180, 360, 600, 900, 1320):
        frame = _video_frame_en(stream_url, t, ffmpeg_exe)
        if not frame:
            continue
        try:
            if _video_leer_marcador(frame):
                es_veo = True
                break
        except Exception:
            pass
        if _video_leer_reloj_lpf(frame) is not None:
            es_lpf = True
            break
    if es_veo:
        return detectar_kickoffs_video(youtube_url)
    if es_lpf:
        return detectar_kickoffs_lpf(youtube_url)
    return None


# Firebase de Tigre (SOLO para leer el link del video cargado y guardar la
# calibracion, gps/videoSync) -- credenciales de administrador en
# variables de entorno (FIREBASE_EMAIL/FIREBASE_PASSWORD), mismo criterio
# que CATAPULT_USER/BL_USER: si no estan configuradas, esta parte se
# saltea sola. apiKey/databaseURL son los mismos que usa index.html (no
# son secretos, ya estan en el HTML publico). A diferencia de
# subir_a_firebase.py (que sube TODO lo de futdetail), esto SOLO lee
# stats/links/{cat}/{fecha}/par y escribe gps/videoSync/{cat}/{fecha} --
# nunca toca nada mas, y nunca pisa una calibracion que ya exista (ni
# manual ni de una corrida anterior de esto mismo). Ojo: "links" vive
# ANIDADO bajo "stats" (todo lo que guarda saveData() en index.html
# cuelga de ahi) -- "gps" en cambio es su propio nodo raiz aparte.
TIGRE_FB_API_KEY = "AIzaSyCw7zfTu06EfT9PNvwcUQq5yGZiy5AGDPE"
TIGRE_FB_DB_URL = "https://tigre-2026-default-rtdb.firebaseio.com"


def _tigre_fb_login(email, password):
    auth_url = ("https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
                f"?key={TIGRE_FB_API_KEY}")
    body = json.dumps({"email": email, "password": password, "returnSecureToken": True}).encode()
    req = urllib.request.Request(auth_url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))["idToken"]


def _tigre_fb_get(path, id_token):
    url = f"{TIGRE_FB_DB_URL}/{path}.json?auth={id_token}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _tigre_fb_put(path, valor, id_token):
    url = f"{TIGRE_FB_DB_URL}/{path}.json?auth={id_token}"
    req = urllib.request.Request(url, data=json.dumps(valor).encode(),
                                  headers={"Content-Type": "application/json"}, method="PUT")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.status


def _video_kickoffs_ok(r):
    """Sanity del resultado del detector antes de guardarlo: kickoff1 chico y
    separacion 1T-2T de un partido real (~45 min + entretiempo recortado en
    video). Descarta lecturas malas del 2T (un offset equivocado da un dk
    absurdo, ej. F25 -> 3/3749). Mismo criterio que la validacion del batch."""
    if not r:
        return False
    k1, k2 = r.get("kickoff1"), r.get("kickoff2")
    if k1 is None or k2 is None:
        return False
    dk = k2 - k1
    if r.get("fuente") == "metadata":
        # Aca el kickoff no sale de una lectura sino de dos relojes reales, y
        # el hueco entre tiempos lo da Catapult: solo se descarta lo imposible
        # (el limite fino de k1 ya lo puso detectar_kickoffs_metadata, que
        # ademas admite la previa del stream antes del saque inicial).
        return 0 <= k1 <= _VIDEO_PREVIA_MAX and 1200 <= dk <= 5400
    return 0 <= k1 <= 600 and 2100 <= dk <= 3600


def sincronizar_video_kickoffs(email, password, catapult_efforts):
    """Para cada fecha con esfuerzos de Catapult (catapult_efforts) que ya
    tenga un link de video cargado y todavia NO tenga calibracion
    (gps/videoSync), intenta detectarla sola con detectar_kickoffs_auto (hora
    real del stream si fue transmision en vivo, y si no cartel VEO o LPF). Si
    no se puede, no hace nada -- la fecha queda para calibrar a mano como
    hasta ahora, sin romper nada."""
    if not VIDEO_SYNC_DISPONIBLE:
        print("[AVISO] Sincronizacion de video: faltan paquetes de Python "
              "(yt-dlp/imageio-ffmpeg/pytesseract/Pillow) o Tesseract OCR -- se omite.")
        return

    # El idToken de Firebase vence a la hora; en una corrida larga (backfill de
    # muchas fechas) hay que renovarlo o los PUT empiezan a dar 401. Se
    # re-loguea cada 40 min y, ante un fallo de guardado, se fuerza un
    # re-login con un reintento.
    _tok = {"id": None, "ts": 0.0}
    def token(force=False):
        if force or not _tok["id"] or (time.time() - _tok["ts"]) > 2400:
            _tok["id"] = _tigre_fb_login(email, password)
            _tok["ts"] = time.time()
        return _tok["id"]
    try:
        token()
    except Exception as e:
        print(f"[ERROR] Sincronizacion de video: no se pudo loguear en Firebase: {e}", file=sys.stderr)
        return

    try:
        fallos = _tigre_fb_get("gps/videoSyncFallos", token()) or {}
    except Exception:
        fallos = {}

    # La correccion de la via de metadata se mide una sola vez por corrida, y
    # recien cuando aparece la primera fecha para calibrar (si no hay nada
    # pendiente no cuesta ni una llamada de mas).
    _off = {"v": None}
    def offset():
        if _off["v"] is None:
            _off["v"] = _video_metadata_offset(catapult_efforts, token)
        return _off["v"]
    MAX_INTENTOS = 3  # los de visitante sin cartel no van a leer nunca -> dejar de reintentarlos

    detectadas = 0
    for cat, fechas in catapult_efforts.items():
        for fecha_key in fechas:
            fecha_num = fecha_key.lstrip("F")
            try:
                if _tigre_fb_get(f"gps/videoSync/{cat}/{fecha_key}", token()):
                    continue
                link = _tigre_fb_get(f"stats/links/{cat}/{fecha_num}/par", token())
            except Exception:
                continue
            if not link:
                continue
            # Si ya se intento MAX_INTENTOS veces con ESTE mismo video sin
            # exito, no se vuelve a intentar (evita bajar cuadros al pedo en
            # cada corrida con los partidos de visitante sin cartel). Si el
            # link cambia (video nuevo), el contador se reinicia y se reintenta.
            # Un fallo viejo solo cuenta si se intento con las MISMAS vias que
            # hay hoy: al sumar una via nueva (ver _VIDEO_VIA_ACTUAL) las
            # fechas que nunca se pudieron leer se reintentan una vez mas.
            # PERO ese reintento solo vale la pena si la via nueva puede
            # aportar algo: si ya se vio que los videos de esta corrida no son
            # transmisiones en vivo, reintentar es repetir el mismo barrido de
            # OCR que ya fallo 3 veces (con estos videos, horas de PC al pedo).
            prev = (fallos.get(cat) or {}).get(fecha_key) or {}
            mismo_link = prev.get("link") == link
            mismo_intento = mismo_link and (prev.get("via") == _VIDEO_VIA_ACTUAL
                                            or not _video_vale_la_pena_metadata())
            if mismo_intento and prev.get("intentos", 0) >= MAX_INTENTOS:
                continue
            resultado = detectar_kickoffs_auto(link, (fechas.get(fecha_key) or {}).get("periodos"), offset())
            if not _video_kickoffs_ok(resultado):
                n = prev.get("intentos", 0) + 1 if mismo_link else 1
                try:
                    _tigre_fb_put(f"gps/videoSyncFallos/{cat}/{fecha_key}",
                                  {"intentos": n, "link": link, "via": _VIDEO_VIA_ACTUAL}, token())
                except Exception:
                    pass
                continue
            guardado = False
            for reintento in (False, True):
                try:
                    _tigre_fb_put(f"gps/videoSync/{cat}/{fecha_key}", resultado, token(force=reintento))
                    detectadas += 1
                    guardado = True
                    print(f"[OK] Video sincronizado solo ({resultado.get('fuente', 'cartel')}): "
                          f"{cat} {fecha_key} (kickoff1={resultado['kickoff1']:.0f}s, "
                          f"kickoff2={resultado['kickoff2']:.0f}s)")
                    break
                except Exception as e:
                    if not reintento:
                        continue
                    print(f"[ERROR] Sincronizacion de video {cat} {fecha_key}: no se pudo guardar: {e}", file=sys.stderr)
            if guardado and prev:  # se pudo al fin -> limpiar el registro de fallos
                try:
                    _tigre_fb_put(f"gps/videoSyncFallos/{cat}/{fecha_key}", None, token())
                except Exception:
                    pass
    if detectadas:
        print(f"[OK] Sincronizacion de video: {detectadas} fecha(s) calibradas solas")


def _statfutbol_formacion_tigre(catnum, id_partido, equipos, tid):
    """Formacion de Tigre (titulares/suplentes con numero) desde la sintesis
    de statfutbol de un partido. Devuelve (titulares, suplentes, rival) o
    (None, None, None) si no se pudo (sintesis sin publicar, no se ubico el
    lado de Tigre, formacion incompleta)."""
    url = f"{STATFUTBOL_BASE}sintesispartido{catnum}2026.php"
    try:
        html = fetch_post(url, {"idPartido": id_partido, "fixGL": "0", "fixGV": "0"})
    except Exception:
        return None, None, None
    idx = html.find('<th class="encabezado-equipo"')
    idx2 = html.find("</table>", idx)
    if idx < 0 or idx2 < 0:
        return None, None, None
    bloque = html[idx:idx2]
    nombres = re.findall(r'encabezado-equipo">.*?;(.+?)\s*\(\d+ gol(?:es)?\)\s*</th>', bloque)
    tds = re.findall(r'<td class="jugadores-equipo"[^>]*>(.*?)</td>', bloque, re.DOTALL)
    if len(nombres) != 2 or len(tds) != 2:
        return None, None, None
    lado = None
    for i, ne in enumerate(nombres):
        m = statfutbol_match_equipo(ne, equipos)
        if m and m[0] == tid:
            lado = i
    if lado is None:
        return None, None, None
    td = tds[lado]
    rival = nombres[1 - lado]
    # El header "SUPLENTE" separa los 11 titulares de los suplentes.
    mk = re.search(r"SUPLENTE", td)
    corte = mk.start() if mk else len(td)
    titulares, suplentes = [], []
    for mm in re.finditer(r'<span class="linea-jugador">(.*?)</span>', td, re.DOTALL):
        txt = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", mm.group(1))).strip()
        m2 = re.match(r"(\d+)\.\s*(.+)", txt)
        if not m2:
            continue
        num = int(m2.group(1))
        resto = m2.group(2)
        apellidos, nombres_j = resto.split(",", 1) if "," in resto else (resto, "")
        prim = nombres_j.split()[0] if nombres_j.split() else ""
        nombre = (prim.capitalize() + " " + " ".join(w.capitalize() for w in apellidos.split())).strip()
        (titulares if mm.start() < corte else suplentes).append({"num": num, "nombre": nombre, "warn": False})
    return titulares, suplentes, rival


def sincronizar_citaciones_provisionales(email, password):
    """Para cada fecha jugada de 4TA-9NA que TODAVIA no tenga citacion cargada
    (ni planilla oficial ni provisional), completa la formacion desde
    statfutbol marcada `provisional: true`. NUNCA pisa lo que ya haya cargado
    (prioridad: planilla oficial > provisional existente). Cuando se sube el
    PDF, parseCitacionPdf en la app pisa la provisional. Se saltea sola si
    faltan las credenciales (main solo la llama si estan)."""
    _tok = {"id": None, "ts": 0.0}
    def token(force=False):
        if force or not _tok["id"] or (time.time() - _tok["ts"]) > 2400:
            _tok["id"] = _tigre_fb_login(email, password)
            _tok["ts"] = time.time()
        return _tok["id"]
    try:
        md_all = _tigre_fb_get("stats/matchData", token()) or {}
    except Exception as e:
        print(f"[ERROR] Citaciones provisionales: no se pudo leer matchData: {e}", file=sys.stderr)
        return

    def ya_tiene(cat, fecha):
        arr = md_all.get(cat)
        if not arr:
            return False
        d = arr[fecha] if isinstance(arr, list) and fecha < len(arr) else (arr.get(str(fecha)) if isinstance(arr, dict) else None)
        return bool(d and d.get("titulares"))

    total = 0
    for cat, catnum in STATFUTBOL_CATNUM.items():
        try:
            fixture = fetch_statfutbol_fixture(catnum)
            equipos = fetch_statfutbol_equipos(catnum)
        except Exception:
            continue
        tid = next((eid for eid, en in equipos if "tigre" in en.lower()), None)
        if not tid:
            continue
        for row in fixture:
            if not row.get("jugado"):
                continue
            if not ("tigre" in row["local"].lower() or "tigre" in row["visita"].lower()):
                continue
            fecha = row["jornada"]
            if ya_tiene(cat, fecha):
                continue  # ya hay planilla (oficial o provisional) -> prioridad, no se toca
            titulares, suplentes, rival = _statfutbol_formacion_tigre(catnum, row["id_partido"], equipos, tid)
            if not titulares or len(titulares) < 7:
                continue  # sintesis sin publicar / incompleta -> se deja para la proxima corrida
            rival_disp = " ".join(w.capitalize() for w in (rival or "").split())
            entry = {"rival": rival_disp, "titulares": titulares, "suplentes": suplentes, "provisional": True}
            for reintento in (False, True):
                try:
                    _tigre_fb_put(f"stats/matchData/{cat}/{fecha}", entry, token(force=reintento))
                    total += 1
                    print(f"[OK] Citacion provisional: {cat} F{fecha} vs {rival_disp} ({len(titulares)}+{len(suplentes)})")
                    break
                except Exception as e:
                    if not reintento:
                        continue
                    print(f"[ERROR] Citacion provisional {cat} F{fecha}: no se pudo guardar: {e}", file=sys.stderr)
    if total:
        print(f"[OK] Citaciones provisionales: {total} fecha(s) completadas desde statfutbol")


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
        jugado = score not in ("", ".-.")
        # El score viene como "GF_LOCAL-GF_VISITA" (ej. "TIGRE 3-1 LANUS" =
        # 3 para Tigre) -- confirmado con datos reales 2026-09-01.
        gf_local = gf_visita = None
        if jugado:
            sm = re.match(r"(\d+)\s*-\s*(\d+)", score)
            if sm:
                gf_local, gf_visita = int(sm.group(1)), int(sm.group(2))
        out.append({
            "jornada": int(jm.group(1)), "local": local, "visita": visita,
            "jugado": jugado, "gf_local": gf_local, "gf_visita": gf_visita,
            "fecha_iso": fm.group(1), "id_partido": idm.group(1),
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
    def _int(c):
        try:
            return int(re.sub(r"[^0-9]", "", re.sub(r"<[^>]+>", "", c)) or 0)
        except Exception:
            return 0
    for fila in filas:
        nombre_m = re.search(r'jugador-pc">([^<]*)</span>', fila)
        celdas = re.findall(r"<td[^>]*>(.*?)</td>", fila, re.DOTALL)
        # celdas: [0]=nombre, [1]=PJ, [2]=MIN, [3]=GOL, [4]=AM, [5]=EXP, [6]=OUT, [7]=IN, [8]=boton
        if not nombre_m or len(celdas) < 6:
            continue
        try:
            gol = int(re.sub(r"<[^>]+>", "", celdas[3]).strip())
            am = int(re.sub(r"<[^>]+>", "", celdas[4]).strip())
            roja = int(re.sub(r"<[^>]+>", "", celdas[5]).strip())
        except (ValueError, IndexError):
            continue
        # PJ (celda 1) y minutos (celda 2): fuente publica de "partidos
        # jugados"/minutos para 7MA-9NA (sin COMET). Parseo tolerante -> 0.
        out.append({"nombre": nombre_m.group(1).strip(), "pj": _int(celdas[1]), "min": _int(celdas[2]),
                    "gol": gol, "am": am, "roja": roja})
    return out


def fetch_statfutbol_sintesis_tarjetas(sintesis_url, id_partido, team_id_objetivo, equipos):
    """Devuelve {nombre: {'amarilla': bool, 'roja': bool}} para los
    jugadores del equipo team_id_objetivo en ese partido puntual. Devuelve
    {} (sin marcar error) si la sintesis todavia no esta publicada del lado
    de statfutbol -- pasa seguido con el partido mas reciente, la tabla
    viene vacia (sin nombre de equipo ni jugadores), no es un cambio de
    formato.

    sintesis_url es la URL completa (antes era "catnum" y se armaba aca
    mismo "sintesispartido{catnum}2026.php" -- se movio a parametro para
    poder reusar esta misma funcion con las URLs irregulares de Reserva,
    que no siguen el patron de catnum de las juveniles)."""
    html = fetch_post(sintesis_url, {"idPartido": id_partido, "fixGL": "0", "fixGV": "0"})
    # ojo: "encabezado-equipo" tambien aparece en el <style> inline mas
    # arriba en la pagina -- hay que buscar el <th>, no el string suelto.
    idx = html.find('<th class="encabezado-equipo"')
    idx2 = html.find("</table>", idx)
    if idx < 0 or idx2 < 0:
        return {}
    bloque = html[idx:idx2]
    # "1 gol" (singular) vs "2 goles" (plural) -- statfutbol usa las dos. El
    # nombre del equipo puede traer su propio parentesis (ej. "GODOY CRUZ
    # A.T. (MENDOZA)"), asi que no se puede cortar en el primer "(" -- se
    # captura todo sin exigir nada mas que terminar justo antes de
    # "(N gol/es)</th>" (ese es siempre el ultimo parentesis de la celda).
    nombres_equipo = re.findall(r'encabezado-equipo">.*?;(.+?)\s*\(\d+ gol(?:es)?\)\s*</th>', bloque)
    tds = re.findall(r'<td class="jugadores-equipo"[^>]*>(.*?)</td>', bloque, re.DOTALL)
    if len(nombres_equipo) != 2 or len(tds) != 2:
        return {}
    lado = None
    for i, ne in enumerate(nombres_equipo):
        m = statfutbol_match_equipo(ne, equipos)
        if m and m[0] == team_id_objetivo:
            lado = i
    if lado is None:
        return {}
    spans = re.findall(r'<span class="linea-jugador">(.*?)</span>', tds[lado], re.DOTALL)
    eventos = {}
    for sp in spans:
        iconos = re.findall(r'<i class="([^"]+)"[^>]*?style="color:([^;"]+)', sp)
        amarilla = any("fa-square" in cls and color == "yellow" for cls, color in iconos)
        roja = any("fa-square" in cls and color == "red" for cls, color in iconos)
        if not (amarilla or roja):
            continue
        texto = re.sub(r"<form.*?</form>", "", sp, flags=re.DOTALL)
        texto = re.sub(r"<i.*?</i>|<i[^>]*/?>", "", texto, flags=re.DOTALL)
        nombre = re.sub(r"^\s*\d+\.\s*", "", texto).strip()
        if nombre:
            eventos[nombre] = {"amarilla": amarilla, "roja": roja}
    return eventos


def fetch_statfutbol_sintesis_completa(sintesis_url, id_partido, team_id_objetivo, equipos):
    """Igual que fetch_statfutbol_sintesis_tarjetas, pero ademas cuenta
    goles (no solo amarilla/roja) -- para completar partidos/matchData
    cuando no hay planilla de COMET cargada para esa fecha (Javi,
    2026-09-02: "prioridad comet, si no hay planilla, traer el dato de la
    pagina"). Devuelve {nombre: {"goles": n, "amarilla": bool, "roja":
    bool}}, solo con jugadores que tuvieron algun evento (se omiten los que
    no metieron gol ni vieron tarjeta, para no inflar el resultado).
    sintesis_url: ver comentario en fetch_statfutbol_sintesis_tarjetas."""
    html = fetch_post(sintesis_url, {"idPartido": id_partido, "fixGL": "0", "fixGV": "0"})
    idx = html.find('<th class="encabezado-equipo"')
    idx2 = html.find("</table>", idx)
    if idx < 0 or idx2 < 0:
        return {}
    bloque = html[idx:idx2]
    nombres_equipo = re.findall(r'encabezado-equipo">.*?;(.+?)\s*\(\d+ gol(?:es)?\)\s*</th>', bloque)
    tds = re.findall(r'<td class="jugadores-equipo"[^>]*>(.*?)</td>', bloque, re.DOTALL)
    if len(nombres_equipo) != 2 or len(tds) != 2:
        return {}
    lado = None
    for i, ne in enumerate(nombres_equipo):
        m = statfutbol_match_equipo(ne, equipos)
        if m and m[0] == team_id_objetivo:
            lado = i
    if lado is None:
        return {}
    spans = re.findall(r'<span class="linea-jugador">(.*?)</span>', tds[lado], re.DOTALL)
    eventos = {}
    for sp in spans:
        # El icono de gol (fa-futbol) NO trae style="color:..." (a
        # diferencia de las tarjetas) -- por eso se busca la clase sola,
        # aparte del regex de color que ya usaba fetch_statfutbol_sintesis_tarjetas.
        clases = re.findall(r'<i class="([^"]+)"', sp)
        goles = sum(1 for c in clases if "fa-futbol" in c)
        colores = re.findall(r'<i class="([^"]+)"[^>]*?style="color:([^;"]+)', sp)
        amarilla = any("fa-square" in cls and color == "yellow" for cls, color in colores)
        roja = any("fa-square" in cls and color == "red" for cls, color in colores)
        if not (goles or amarilla or roja):
            continue
        texto = re.sub(r"<form.*?</form>", "", sp, flags=re.DOTALL)
        texto = re.sub(r"<i.*?</i>|<i[^>]*/?>", "", texto, flags=re.DOTALL)
        nombre = re.sub(r"^\s*\d+\.\s*", "", texto).strip()
        if nombre:
            eventos[nombre] = {"goles": goles, "amarilla": amarilla, "roja": roja}
    return eventos


AMARILLAS_SUSPENSION = 5


def calcular_riesgo_suspension(sintesis_url, team_id, team_nombre, equipos, fixture):
    """Recorre TODOS los partidos jugados por team_id en la temporada, en
    orden cronologico, y arma el conteo VIGENTE de amarillas por jugador --
    no el acumulado bruto, sino el que queda despues de reiniciar en cero
    cada vez que el jugador llego a la 5ta amarilla acumulada o fue
    expulsado (roja directa o doble amarilla). Mismo criterio de "ciclo"
    que amarillasEnAlerta() en index.html para nuestros propios jugadores.

    A diferencia de antes, esto YA NO devuelve a los que estan "en riesgo"
    (4 amarillas, podrian llegar a la 5ta en cualquier partido) -- eso no
    servia como aviso util (Javi, 2026-09-01: "hoy me muestra varios con 4,
    eso no me sirve"). Ahora solo devuelve a los que llegaron JUSTO a la
    5ta amarilla en el ULTIMO partido jugado por el rival, O que fueron
    expulsados (roja directa o doble amarilla) en ese mismo ultimo partido
    -- los dos casos dejan al jugador afuera del partido que nos toca jugar
    (Javi, 2026-09-18: encontro que la expulsion sin llegar a la 5ta
    amarilla no se estaba avisando). Cada entrada trae "motivo" ('amarilla'
    o 'roja') para que la pantalla pueda mostrarlo distinto."""
    nombre_corto = team_nombre.split(" (")[0]
    partidos_equipo = [p for p in fixture if p["jugado"] and (
        p["local"] == nombre_corto or p["visita"] == nombre_corto
        or statfutbol_match_equipo(p["local"], equipos) == (team_id, team_nombre)
        or statfutbol_match_equipo(p["visita"], equipos) == (team_id, team_nombre)
    )]
    partidos_equipo.sort(key=lambda p: p["fecha_iso"])
    conteo = {}
    suspendidos_ultimo_partido = []
    for idx, p in enumerate(partidos_equipo):
        es_ultimo = idx == len(partidos_equipo) - 1
        try:
            eventos = fetch_statfutbol_sintesis_tarjetas(sintesis_url, p["id_partido"], team_id, equipos)
        except Exception:  # noqa -- un partido puntual con la pagina rota no debe tirar abajo toda la temporada
            eventos = {}
        for nombre, ev in eventos.items():
            if ev["amarilla"]:
                conteo[nombre] = conteo.get(nombre, 0) + 1
        agregados_este_partido = set()
        for nombre in list(conteo.keys()):
            llego_a_la_5ta = conteo[nombre] >= AMARILLAS_SUSPENSION
            expulsado = eventos.get(nombre, {}).get("roja", False)
            if llego_a_la_5ta or expulsado:
                conteo[nombre] = 0
                if es_ultimo:
                    if llego_a_la_5ta:
                        suspendidos_ultimo_partido.append({"nombre": nombre, "motivo": "amarilla", "amarillas": AMARILLAS_SUSPENSION})
                    else:
                        suspendidos_ultimo_partido.append({"nombre": nombre, "motivo": "roja"})
                    agregados_este_partido.add(nombre)
        if es_ultimo:
            # Expulsado sin amarillas acumuladas este ciclo (roja directa de
            # entrada, nunca paso por el loop de arriba porque nunca tuvo
            # una amarilla que lo metiera en `conteo`).
            for nombre, ev in eventos.items():
                if ev.get("roja") and nombre not in agregados_este_partido:
                    suspendidos_ultimo_partido.append({"nombre": nombre, "motivo": "roja"})
    return suspendidos_ultimo_partido


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

    riesgo = calcular_riesgo_suspension(f"{STATFUTBOL_BASE}sintesispartido{catnum}2026.php",
                                         team_id, team_nombre, equipos, fixture)

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


def fetch_statfutbol_reserva_fixture(fixture_path):
    """Fixture completo de un torneo de Reserva (Apertura o Clausura),
    zonas A y B juntas en la misma pagina (trae una columna de zona de mas
    respecto al fixture de las juveniles).

    OJO -- confirmado con datos reales, 2026-09-02: Apertura y Clausura
    vienen de plantillas HTML DISTINTAS del lado de statfutbol:
      - Apertura: nombre de equipo en <span class="pc">, resultado en UNA
        celda combinada "GL-GV", fecha ISO en una celda oculta (d-none)
        aparte de la fecha visible DD-MM.
      - Clausura: nombre de equipo pegado a un "&nbsp;" (sin span.pc), GL y
        GV en dos celdas separadas, fecha ISO directa (sin celda oculta).
      - Partido no jugado: en Apertura el resultado no matchea "N-N"; en
        Clausura las celdas de gol traen literalmente "." (confirmado).
    Se detecta el formato por fila (la de Apertura siempre trae
    class="pc") en vez de asumir uno solo, para no romper si el torneo que
    todavia no arranco/temrino usa el otro molde."""
    html = fetch(STATFUTBOL_BASE + fixture_path)
    filas = re.findall(r'<tr class="trConsult[^"]*">(.*?)</tr>', html, re.DOTALL)
    out = []
    for fila in filas:
        celdas = re.findall(r"<td[^>]*>(.*?)</td>", fila, re.DOTALL)

        def equipo_pc(c):
            m = re.search(r'class="pc">([^<]*)</span>', c)
            return m.group(1).strip() if m else None

        def equipo_nbsp(c):
            m = re.search(r"&nbsp;\s*([^<]+)", c)
            return re.sub(r"\s+", " ", m.group(1)).strip() if m else None

        try:
            if 'class="pc"' in fila:
                if len(celdas) < 10:
                    continue
                jm = re.match(r"\s*(\d+)", re.sub(r"<[^>]+>", "", celdas[1]))
                zona = re.sub(r"<[^>]+>", "", celdas[2]).strip()
                local, visita = equipo_pc(celdas[3]), equipo_pc(celdas[5])
                score = re.sub(r"<[^>]+>", "", celdas[4]).strip()
                fm = re.search(r"(\d{4}-\d{2}-\d{2})", celdas[7])
                idm = re.search(r'name="idPartido" value="(\d+)"', celdas[9])
                if not (jm and zona and local and visita and fm and idm):
                    continue
                sm = re.match(r"(\d+)\s*-\s*(\d+)", score)
                jugado = bool(sm)
                gf_local, gf_visita = (int(sm.group(1)), int(sm.group(2))) if sm else (None, None)
            else:
                if len(celdas) < 9:
                    continue
                jm = re.match(r"\s*(\d+)", re.sub(r"<[^>]+>", "", celdas[0]))
                zona = re.sub(r"<[^>]+>", "", celdas[1]).strip()
                local, visita = equipo_nbsp(celdas[2]), equipo_nbsp(celdas[4])
                gl_raw = re.sub(r"<[^>]+>", "", celdas[3]).strip()
                gv_raw = re.sub(r"<[^>]+>", "", celdas[5]).strip()
                fm = re.search(r"(\d{4}-\d{2}-\d{2})", celdas[6])
                idm = re.search(r'name="idPartido" value="(\d+)"', celdas[8])
                if not (jm and zona and local and visita and fm and idm):
                    continue
                jugado = gl_raw not in ("", ".") and gv_raw not in ("", ".")
                gf_local = int(gl_raw) if jugado else None
                gf_visita = int(gv_raw) if jugado else None
        except (ValueError, IndexError):
            continue

        out.append({
            "jornada": int(jm.group(1)), "zona": zona, "local": local, "visita": visita,
            "jugado": jugado, "gf_local": gf_local, "gf_visita": gf_visita,
            "fecha_iso": fm.group(1), "id_partido": idm.group(1),
        })
    return out


def fetch_statfutbol_reserva_equipos(planteles_base):
    """Lista (id, nombre) del selector 'Elija un equipo' de PLANTELES de
    Reserva -- mismo formato que fetch_statfutbol_equipos, URL literal."""
    html = fetch(f"{STATFUTBOL_BASE}{planteles_base}.php")
    opts = re.findall(r'<option value="(\d+)">\s*([^<]+?)\s*</option>', html)
    return [(v, n.strip()) for v, n in opts]


def fetch_statfutbol_reserva_plantel(planteles_base, team_id):
    """Plantel de Reserva de un equipo, acumulado de temporada por jugador
    -- mismo formato/columnas que fetch_statfutbol_plantel (confirmado con
    datos reales de Tigre, 2026-09-02), URL literal en vez de catnum."""
    html = fetch_post(f"{STATFUTBOL_BASE}{planteles_base}Resolucion.php", {"player": team_id})
    filas = re.findall(r'<tr class="trConsultParaJugadores">(.*?)</tr>', html, re.DOTALL)
    out = []
    for fila in filas:
        nombre_m = re.search(r'jugador-pc">([^<]*)</span>', fila)
        celdas = re.findall(r"<td[^>]*>(.*?)</td>", fila, re.DOTALL)
        if not nombre_m or len(celdas) < 6:
            continue
        try:
            gol = int(re.sub(r"<[^>]+>", "", celdas[3]).strip())
            am = int(re.sub(r"<[^>]+>", "", celdas[4]).strip())
            roja = int(re.sub(r"<[^>]+>", "", celdas[5]).strip())
        except (ValueError, IndexError):
            continue
        out.append({"nombre": nombre_m.group(1).strip(), "gol": gol, "am": am, "roja": roja})
    return out


def calcular_alerta_rival_reserva(torneo_cfg):
    """Igual que calcular_alerta_rival, pero para un torneo de Reserva --
    usa las URLs literales de RESERVA_TORNEOS en vez del catnum de las
    juveniles. torneo_cfg es un valor de RESERVA_TORNEOS (dict con
    fixture/planteles_base/sintesis)."""
    fixture = fetch_statfutbol_reserva_fixture(torneo_cfg["fixture"])
    proximo = next((p for p in fixture if not p["jugado"] and (p["local"] == "TIGRE" or p["visita"] == "TIGRE")), None)
    if not proximo:
        return None
    rival_nombre_fx = proximo["visita"] if proximo["local"] == "TIGRE" else proximo["local"]

    equipos = fetch_statfutbol_reserva_equipos(torneo_cfg["planteles_base"])
    match = statfutbol_match_equipo(rival_nombre_fx, equipos)
    if not match:
        raise ValueError(f"No pude identificar al equipo rival {rival_nombre_fx!r} en el listado de planteles de Reserva")
    team_id, team_nombre = match

    plantel = fetch_statfutbol_reserva_plantel(torneo_cfg["planteles_base"], team_id)
    if not plantel:
        raise ValueError(f"Plantel vacio para {team_nombre!r} (Reserva)")
    goleador = max(plantel, key=lambda j: j["gol"])

    riesgo = calcular_riesgo_suspension(STATFUTBOL_BASE + torneo_cfg["sintesis"], team_id, team_nombre, equipos, fixture)

    return {
        "fecha": proximo["jornada"],
        "rival": team_nombre,
        "goleador": {"nombre": goleador["nombre"], "goles": goleador["gol"]} if goleador["gol"] > 0 else None,
        "amarillas_riesgo": riesgo,
    }


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

    # Para el modo incremental de fetch_catapult_efforts: si ya existe un
    # data/tablas.json de una corrida anterior, se rescata su
    # catapult_efforts para no volver a pedir partidos ya procesados. Si
    # no existe el archivo (primera corrida) o esta corrupto, arranca
    # vacio sin romper nada -- es solo una optimizacion, no una fuente de
    # verdad.
    catapult_efforts_previos = {}
    try:
        with open(OUT_PATH, "r", encoding="utf-8") as f:
            catapult_efforts_previos = json.load(f).get("catapult_efforts") or {}
    except Exception:  # noqa
        pass
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

    # Goles/amarillas/rojas de TIGRE partido por partido, jugador por
    # jugador, segun la sintesis de cada partido en statfutbol -- respaldo
    # para completar partidos/matchData (stats/partidos/{cat}/{fecha}) en
    # las fechas donde todavia no se cargo la planilla de COMET (a pedido
    # de Javi, 2026-09-02: "prioridad comet, si no hay planilla, traer el
    # dato de la pagina"). No decide ACA si hace falta completar o no --
    # eso lo resuelve subir_a_firebase.py mirando si esa fecha ya tiene
    # datos en Firebase antes de escribir nada (nunca pisa una carga real).
    # Un pedido HTTP por partido jugado (~20 por categoria) -- mas lento que
    # el resto de statfutbol pero son datos que valen la pena.
    resultado["statfutbol_partidos"] = {}
    for cat, catnum in STATFUTBOL_CATNUM.items():
        try:
            equipos = fetch_statfutbol_equipos(catnum)
            match = statfutbol_match_equipo("TIGRE", equipos)
            if not match:
                raise ValueError("No se encontro a Tigre en el listado de planteles")
            team_id, _ = match
            fixture = fetch_statfutbol_fixture(catnum)
            por_fecha = {}
            for p in fixture:
                if not p["jugado"] or (p["local"] != "TIGRE" and p["visita"] != "TIGRE"):
                    continue
                eventos = fetch_statfutbol_sintesis_completa(f"{STATFUTBOL_BASE}sintesispartido{catnum}2026.php",
                                                               p["id_partido"], team_id, equipos)
                if eventos:
                    por_fecha[p["jornada"]] = eventos
            resultado["statfutbol_partidos"][cat] = por_fecha
            print(f"[OK] statfutbol partidos {cat}: {len(por_fecha)} fechas con datos")
        except Exception as e:  # noqa
            errores.append(f"statfutbol partidos {cat}: {e}")
            print(f"[ERROR] statfutbol partidos {cat}: {e}", file=sys.stderr)

    # Resultado de Tigre partido por partido segun statfutbol -- mismo uso
    # que rival_alertas (fetch_statfutbol_fixture ya lo trae con el gol de
    # cada lado, agregado 2026-09-01). Se guarda por jornada para que
    # Confiabilidad lo pueda mostrar como referencia externa (COMET > Liga
    # oficial > futdetail siguen siendo las fuentes que definen "la verdad";
    # esto es solo un cuarto punto de comparacion, no gana empates).
    resultado["statfutbol_resultados"] = {}
    for cat, catnum in STATFUTBOL_CATNUM.items():
        try:
            fixture = fetch_statfutbol_fixture(catnum)
            propios = {}
            for p in fixture:
                if not p["jugado"] or p["gf_local"] is None:
                    continue
                if p["local"] == "TIGRE":
                    propios[p["jornada"]] = {"gf": p["gf_local"], "gc": p["gf_visita"], "rival": p["visita"]}
                elif p["visita"] == "TIGRE":
                    propios[p["jornada"]] = {"gf": p["gf_visita"], "gc": p["gf_local"], "rival": p["local"]}
            resultado["statfutbol_resultados"][cat] = propios
            print(f"[OK] statfutbol resultados {cat}: {len(propios)} fechas")
        except Exception as e:  # noqa
            errores.append(f"statfutbol resultados {cat}: {e}")
            print(f"[ERROR] statfutbol resultados {cat}: {e}", file=sys.stderr)

    # Reserva (Apertura/Clausura): mismos 3 datos de arriba (resultados
    # propios, alerta de proximo rival, plantel propio) pero con las URLs
    # literales de RESERVA_TORNEOS -- a pedido de Javi, 2026-09-02 ("traer
    # todos los datos que se puedan automatizar" para Reserva). RESERVA_APE
    # se guarda como "RESERVA" (1er semestre de la app) y RESERVA_CLA como
    # "RESERVA_S2" (2do semestre), mismo criterio que reservaSemestre en
    # index.html.
    RESERVA_TORNEO_A_CAT = {"RESERVA_APE": "RESERVA", "RESERVA_CLA": "RESERVA_S2"}
    resultado["fixture_reserva"] = {}
    for torneo, cfg in RESERVA_TORNEOS.items():
        cat = RESERVA_TORNEO_A_CAT[torneo]
        try:
            fixture_r = fetch_statfutbol_reserva_fixture(cfg["fixture"])
            propios = {}
            for p in fixture_r:
                if not p["jugado"] or p["gf_local"] is None:
                    continue
                if p["local"] == "TIGRE":
                    propios[p["jornada"]] = {"gf": p["gf_local"], "gc": p["gf_visita"], "rival": p["visita"]}
                elif p["visita"] == "TIGRE":
                    propios[p["jornada"]] = {"gf": p["gf_visita"], "gc": p["gf_local"], "rival": p["local"]}
            resultado["statfutbol_resultados"][cat] = propios
            print(f"[OK] statfutbol resultados {cat}: {len(propios)} fechas")

            # Fixture completo (jugados y pendientes) de los partidos de
            # Tigre -- a diferencia de "propios" de arriba (solo resultados
            # ya jugados, usado como respaldo de RESULTADOS), esto alimenta
            # la seccion FIXTURE de la app (proxima fecha + calendario
            # completo), que necesita ver tambien los partidos que todavia
            # no se jugaron. Mismos datos ya traidos por fetch_statfutbol_
            # reserva_fixture, no hace falta pedirlos de nuevo.
            fixture_tigre = {}
            for p in fixture_r:
                if p["local"] == "TIGRE":
                    fixture_tigre[p["jornada"]] = {
                        "rival": p["visita"], "cond": "L", "fecha_iso": p["fecha_iso"], "jugado": p["jugado"],
                        "gf": p["gf_local"], "gc": p["gf_visita"],
                    }
                elif p["visita"] == "TIGRE":
                    fixture_tigre[p["jornada"]] = {
                        "rival": p["local"], "cond": "V", "fecha_iso": p["fecha_iso"], "jugado": p["jugado"],
                        "gf": p["gf_visita"], "gc": p["gf_local"],
                    }
            resultado["fixture_reserva"][cat] = fixture_tigre
            print(f"[OK] statfutbol fixture reserva {cat}: {len(fixture_tigre)} fechas")
        except Exception as e:  # noqa
            errores.append(f"statfutbol resultados {cat}: {e}")
            print(f"[ERROR] statfutbol resultados {cat}: {e}", file=sys.stderr)

        try:
            alerta = calcular_alerta_rival_reserva(cfg)
            if alerta:
                resultado["rival_alertas"][cat] = alerta
                print(f"[OK] statfutbol {cat}: rival {alerta['rival']}, "
                      f"{len(alerta['amarillas_riesgo'])} en riesgo de suspension")
            else:
                print(f"[OK] statfutbol {cat}: sin proximo partido pendiente")
        except Exception as e:  # noqa
            errores.append(f"statfutbol {cat}: {e}")
            print(f"[ERROR] statfutbol {cat}: {e}", file=sys.stderr)

        try:
            equipos_r = fetch_statfutbol_reserva_equipos(cfg["planteles_base"])
            match = statfutbol_match_equipo("TIGRE", equipos_r)
            if not match:
                raise ValueError("No se encontro a Tigre en el listado de planteles de Reserva")
            team_id_r, _ = match
            plantel_r = fetch_statfutbol_reserva_plantel(cfg["planteles_base"], team_id_r)
            resultado["statfutbol_jugadores"][cat] = plantel_r
            print(f"[OK] statfutbol jugadores {cat}: {len(plantel_r)} jugadores")
        except Exception as e:  # noqa
            errores.append(f"statfutbol jugadores {cat}: {e}")
            print(f"[ERROR] statfutbol jugadores {cat}: {e}", file=sys.stderr)

        # Goles de Tigre partido por partido (quien metio cada gol) -- para
        # completar GOLEADORES de RESERVA en las fechas donde la carga manual
        # no llega al resultado real (index.html, golesEfectivos). Mismo dato
        # que ya se trae para 4TA-9NA, aca con la sintesis de cada torneo.
        try:
            por_fecha = {}
            for p in fetch_statfutbol_reserva_fixture(cfg["fixture"]):
                if not p["jugado"] or "TIGRE" not in (p["local"], p["visita"]):
                    continue
                eventos = fetch_statfutbol_sintesis_completa(
                    STATFUTBOL_BASE + cfg["sintesis"], p["id_partido"], team_id_r, equipos_r)
                if eventos:
                    por_fecha[p["jornada"]] = eventos
            resultado["statfutbol_partidos"][cat] = por_fecha
            print(f"[OK] statfutbol partidos {cat}: {len(por_fecha)} fechas con datos")
        except Exception as e:  # noqa
            errores.append(f"statfutbol partidos {cat}: {e}")
            print(f"[ERROR] statfutbol partidos {cat}: {e}", file=sys.stderr)

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

    # Catapult OpenField directo -- modulo aparte de BL GPS Performance
    # (ver fetch_catapult_players), pensado para comparar los dos antes de
    # decidir con cual quedarse. Opcional: si no estan las credenciales
    # configuradas se saltea sin romper el resto.
    usuario_catapult = os.environ.get("CATAPULT_USER")
    password_catapult = os.environ.get("CATAPULT_PASS")
    if usuario_catapult and password_catapult:
        try:
            jugadores_catapult = fetch_catapult_players(
                usuario_catapult, password_catapult, plantel_por_cat=resultado.get("plantel_futdetail"))
            resultado["catapult_gps"] = {"players": jugadores_catapult}
            total_jug = sum(len(v) for v in jugadores_catapult.values())
            print(f"[OK] Catapult OpenField: {total_jug} jugadores en {len(jugadores_catapult)} categorias")
        except Exception as e:  # noqa
            errores.append(f"Catapult OpenField: {e}")
            print(f"[ERROR] Catapult OpenField: {e}", file=sys.stderr)

        # Esfuerzos individuales (sprints con hora real) + periodos, para
        # "clic en la metrica destacada -> ver el momento en video" (ver
        # fetch_catapult_efforts). Pipeline aparte de catapult_gps de
        # arriba, a proposito: no se toca lo que ya funciona en produccion.
        # Empezo siendo solo 4TA (piloto, Javi 2026-09-05); sumadas 5TA y
        # 6TA (Javi, 2026-09-18); extendido a 7MA/8VA/9NA (Javi, 2026-09-20)
        # -- todas las juveniles. Reserva queda afuera a pedido. Sumar mas es
        # agregar el nombre a esta lista; trae datos solo si el club uso los
        # chalecos GPS en esa categoria (si no, queda vacia, no rompe nada).
        CATAPULT_EFFORTS_CATS = ["4TA", "5TA", "6TA", "7MA", "8VA", "9NA"]
        try:
            efforts = fetch_catapult_efforts(
                usuario_catapult, password_catapult, CATAPULT_EFFORTS_CATS,
                existentes=catapult_efforts_previos)
            resultado["catapult_efforts"] = efforts
            total_fechas = sum(len(v) for v in efforts.values())
            print(f"[OK] Catapult efforts: {total_fechas} fecha(s) en {len(efforts)} categoria(s)")
        except Exception as e:  # noqa
            errores.append(f"Catapult efforts: {e}")
            print(f"[ERROR] Catapult efforts: {e}", file=sys.stderr)
            # Si esta corrida fallo, no se pierde lo que ya estaba
            # guardado de corridas anteriores.
            if catapult_efforts_previos:
                resultado["catapult_efforts"] = catapult_efforts_previos
    else:
        print("[AVISO] CATAPULT_USER/CATAPULT_PASS no configurados, se omite Catapult OpenField")

    # Sincronizacion automatica de video (arranque de cada tiempo) para
    # "Esfuerzos en video" -- ver detectar_kickoffs_video/
    # sincronizar_video_kickoffs mas arriba. Necesita catapult_efforts (ya
    # calculado arriba) y credenciales de Firebase con permiso de editor.
    # Opcional en los dos sentidos: si faltan las credenciales, o si falta
    # algun paquete de Python/Tesseract OCR en esta PC, se saltea sola sin
    # romper nada -- la calibracion sigue funcionando a mano como siempre.
    usuario_firebase = os.environ.get("FIREBASE_EMAIL")
    password_firebase = os.environ.get("FIREBASE_PASSWORD")
    if usuario_firebase and password_firebase:
        # Citaciones provisionales desde statfutbol para fechas jugadas sin
        # planilla oficial (no depende de Catapult).
        try:
            sincronizar_citaciones_provisionales(usuario_firebase, password_firebase)
        except Exception as e:  # noqa -- nunca debe tirar abajo el resto del scraper
            print(f"[ERROR] Citaciones provisionales: {e}", file=sys.stderr)
        # Sincronizacion de video (necesita los esfuerzos de Catapult).
        if resultado.get("catapult_efforts"):
            try:
                sincronizar_video_kickoffs(usuario_firebase, password_firebase, resultado["catapult_efforts"])
            except Exception as e:  # noqa -- nunca debe tirar abajo el resto del scraper
                print(f"[ERROR] Sincronizacion de video: {e}", file=sys.stderr)
    else:
        print("[AVISO] FIREBASE_EMAIL/FIREBASE_PASSWORD no configurados, se omite video y citaciones provisionales")

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
