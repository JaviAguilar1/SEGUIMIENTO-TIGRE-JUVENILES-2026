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
# Cruz: 57min/5425m/94.77mpm/241-173-45m/2 sprints/28.1kmh/13-17
# acc-dcc/0 rhie), asi que estan verificados, no adivinados.
CATAPULT_STATS_PARAMS = [
    "athlete_id", "athlete_name", "activity_id", "activity_name",
    "total_duration", "average_distance_session", "meterage_per_minute",
    "velocity_band6_total_distance", "velocity_band7_total_distance", "velocity_band8_total_distance",
    "gen2_velocity_band8_total_effort_count", "max_vel",
    "gen2_acceleration_band8_total_effort_count", "gen2_acceleration_band1_total_effort_count",
    "gen2_acceleration_band2_total_effort_count", "rhie_total_bouts",
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

        # Por cada actividad-partido, se busca a que fecha del fixture le
        # corresponde el dia real en que se jugo (no lo que diga el
        # nombre). Actividades de antes del arranque de temporada se
        # descartan derecho (quedaron de un año anterior); actividades
        # cuyo dia no coincide con NINGUNA fecha del fixture tambien se
        # descartan (amistosos, partidos internos, etc.).
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
                fila.get("gen2_acceleration_band2_total_effort_count"), fila.get("rhie_total_bouts"),
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
    5ta amarilla en el ULTIMO partido jugado por el rival -- esos si estan
    confirmados afuera del partido que nos toca jugar."""
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
        for nombre in list(conteo.keys()):
            llego_a_la_5ta = conteo[nombre] >= AMARILLAS_SUSPENSION
            expulsado = eventos.get(nombre, {}).get("roja", False)
            if llego_a_la_5ta or expulsado:
                conteo[nombre] = 0
                if es_ultimo and llego_a_la_5ta:
                    suspendidos_ultimo_partido.append({"nombre": nombre, "amarillas": AMARILLAS_SUSPENSION})
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
        if not nombre_m or len(celdas) < 5:
            continue
        try:
            gol = int(re.sub(r"<[^>]+>", "", celdas[3]).strip())
            am = int(re.sub(r"<[^>]+>", "", celdas[4]).strip())
        except (ValueError, IndexError):
            continue
        out.append({"nombre": nombre_m.group(1).strip(), "gol": gol, "am": am})
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
    else:
        print("[AVISO] CATAPULT_USER/CATAPULT_PASS no configurados, se omite Catapult OpenField")

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
