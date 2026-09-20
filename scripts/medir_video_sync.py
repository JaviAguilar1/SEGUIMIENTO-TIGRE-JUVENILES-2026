# -*- coding: utf-8 -*-
"""Mide que tan bien funciona la sincronizacion de video por HORA REAL DEL
STREAM, comparandola contra las fechas que ya estan calibradas (por OCR o a
mano) -- NO escribe nada, ni en Firebase ni en el repo: solo mira e informa.

Para que sirve
--------------
La app salta al segundo exacto de un esfuerzo con la calibracion que hay en
Firebase (gps/videoSync = en que segundo del video arranca cada tiempo). Esa
calibracion se puede deducir sin mirar el video cuando el partido fue una
transmision EN VIVO: YouTube guarda a que hora real arranco el stream y
Catapult da a que hora real arranco cada tiempo, asi que

    kickoff = hora_del_saque_inicial - hora_del_segundo_0_del_video

Este script contesta tres preguntas antes de confiar en esa cuenta:
  1) De todas tus fechas, cuantas son transmision en vivo (se calibran solas
     por esta via) y cuantas son archivos subidos despues (quedan para el
     cartel/OCR o para cargar a mano).
  2) Cuanto se equivoca la cuenta contra lo ya calibrado: si el error es de
     0-3 segundos, la via nueva es mas confiable que el OCR; si el error es
     siempre el mismo numero, se corrige solo con ese numero; si da
     cualquier cosa, conviene dejar el OCR al mando.
  3) Que fechas tienen el video cortado o pausado (el 2T no cierra).

Como correrlo (en la PC del club, desde la carpeta del repo):

    python scripts\\medir_video_sync.py

(si FIREBASE_EMAIL/FIREBASE_PASSWORD no estan en el entorno, las pide por
teclado; son las mismas que ya usa el scraper)

Opcionales: un numero limita cuantas fechas mira (ej. "10"; si no, son ~2
segundos por fecha), y "--rapido" saltea YouTube por completo y solo informa
cuantas fechas estan calibradas y cuantas faltan (tarda segundos).

Modo "--cortes": prueba la OTRA via automatica, la del corte del entretiempo
------------------------------------------------------------------------
A todos los videos les recortan el entretiempo, asi que el arranque del 2do
tiempo deberia poder encontrarse solo: es el corte seco que queda entre los dos
tiempos, y para verlo no hace falta leer ningun cartel. Este modo corre ese
detector contra las fechas que YA estan calibradas a mano (o sea, con la
respuesta correcta al lado) y muestra cuanto se equivoca en cada una. Si da
bien, se engancha al scraper y las fechas que faltan se calibran solas.

    python scripts\\medir_video_sync.py --cortes

Tarda entre 20 y 40 segundos por fecha (baja y mira ~5 minutos de video en la
calidad mas baja). Un numero lo limita: "--cortes 5".

Modo "--pendientes": que haria con las fechas que TODAVIA no estan calibradas
---------------------------------------------------------------------------
Corre el mismo detector del corte sobre las fechas que faltan y muestra que
guardaria en cada una -- SIN escribir nada. Sirve para saber de antemano
cuantas se van a resolver solas y cuantas van a quedar a mano, en vez de
enterarse despues de que el scraper ya escribio.

    python scripts\\medir_video_sync.py --pendientes

Mismo tiempo por fecha que --cortes, y tambien se puede limitar con un numero.
"""
import getpass
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scrape_tablas as st  # noqa: E402

RUTA_TABLAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "tablas.json")


def _mediana(xs):
    xs = sorted(xs)
    return xs[len(xs) // 2] if xs else None


def medir_cortes(token, limite=0):
    """Corre el detector del corte del entretiempo contra las fechas que ya
    estan calibradas y compara con la respuesta correcta. No escribe nada."""
    if not st.VIDEO_SYNC_DISPONIBLE:
        print("[ERROR] Faltan yt-dlp / imageio-ffmpeg (pip install yt-dlp imageio-ffmpeg).")
        return 1
    try:
        sync = st._tigre_fb_get("gps/videoSync", token) or {}
    except Exception as e:
        print("[ERROR] No se pudo leer gps/videoSync: %s" % e)
        return 1

    listas = []
    for cat in sorted(sync):
        for fecha_key in sorted(sync[cat] or {}, key=lambda f: int(f.lstrip("F"))):
            v = (sync[cat] or {}).get(fecha_key) or {}
            k1, k2 = v.get("kickoff1"), v.get("kickoff2")
            if k1 is None or k2 is None:
                continue
            listas.append((cat, fecha_key, float(k1), float(k2)))
    if not listas:
        print("[ERROR] Todavia no hay ninguna fecha calibrada contra la cual comparar.")
        return 1

    # La ventana donde se busca el corte sale de lo ya calibrado, igual que lo
    # haria el scraper: mediana del arranque del 1T y mediana del hueco.
    k1_tip = _mediana([k1 for _, _, k1, _ in listas])
    hueco_tip = _mediana([k2 - k1 for _, _, k1, k2 in listas])
    margen = st._VIDEO_CORTE_MARGEN
    centro = k1_tip + hueco_tip
    print("Fechas calibradas para comparar: %d" % len(listas))
    print("Ventana donde se busca el corte: %.0fs a %.0fs del video "
          "(1T tipico %.1fs + hueco tipico %.0fs, +-%ds)"
          % (centro - margen, centro + margen, k1_tip, hueco_tip, margen))
    print("Umbral de cambio de imagen: %.2f\n" % st._VIDEO_CORTE_UMBRAL)
    print("%-5s %-5s %9s %9s %8s %9s %6s  %s" %
          ("CAT", "FECHA", "2T REAL", "CORTE", "DIF", "CERCANO", "CAND", "LOS 3 CORTES MAS FUERTES"))
    print("-" * 110)

    ffmpeg_exe = st.imageio_ffmpeg.get_ffmpeg_exe()
    difs_fuerte, difs_cercano, sin_corte, sin_link = [], [], [], 0
    for i, (cat, fecha_key, k1, k2) in enumerate(listas):
        if limite and i >= limite:
            break
        try:
            link = st._tigre_fb_get("stats/links/%s/%s/par" % (cat, fecha_key.lstrip("F")), token)
        except Exception:
            link = None
        if not link:
            sin_link += 1
            continue
        stream_url = st._video_stream_url(link, st._VIDEO_FORMATO_LIVIANO)
        if not stream_url:
            print("%-5s %-5s %9.1f %9s %8s %9s %6s  (no se pudo abrir el video)"
                  % (cat, fecha_key, k2, "-", "-", "-", "-"))
            continue
        cortes = st._video_cortes_escena(stream_url, centro - margen, centro + margen, ffmpeg_exe)
        if not cortes:
            sin_corte.append("%s %s" % (cat, fecha_key))
            print("%-5s %-5s %9.1f %9s %8s %9s %6d  (ningun corte en la ventana)"
                  % (cat, fecha_key, k2, "-", "-", "-", 0))
            continue
        fuerte = max(cortes, key=lambda c: c[1])[0]
        cercano = min(cortes, key=lambda c: abs(c[0] - centro))[0]
        difs_fuerte.append(fuerte - k2)
        difs_cercano.append(cercano - k2)
        top = sorted(cortes, key=lambda c: -c[1])[:3]
        print("%-5s %-5s %9.1f %9.1f %8.1f %9.1f %6d  %s"
              % (cat, fecha_key, k2, fuerte, fuerte - k2, cercano - k2, len(cortes),
                 "  ".join("%.0fs(%.2f)" % (s, sc) for s, sc in top)))

    print("-" * 110)
    if sin_link:
        print("Fechas calibradas sin link de video: %d" % sin_link)
    if sin_corte:
        print("Sin ningun corte en la ventana (%d): %s" % (len(sin_corte), ", ".join(sin_corte)))
    if not difs_fuerte:
        print("\n=> No se pudo medir ninguna fecha.")
        return 1

    # Cual de las dos reglas conviene para elegir entre varios cortes: quedarse
    # con el mas marcado, o con el mas cercano a donde suele arrancar el 2T.
    # Se juzga cada una DESPUES de sacarle el desfasaje fijo (la mediana): lo
    # que importa no es que el corte caiga exacto, sino que caiga siempre a la
    # misma distancia, porque eso se corrige con una constante.
    resumen = {}
    for clave, nombre, difs in (("fuerte", 'el corte mas marcado ("fuerte")', difs_fuerte),
                                ("cercano", 'el corte mas cercano al hueco tipico ("cercano")', difs_cercano)):
        mediana = _mediana(difs)
        ajustadas = [d - mediana for d in difs]
        resumen[clave] = {"clave": clave, "nombre": nombre, "mediana": mediana,
                          "dentro": sum(1 for d in ajustadas if abs(d) <= 3),
                          "peor": max(abs(d) for d in ajustadas), "n": len(difs)}
        r = resumen[clave]
        print("\nEligiendo %s:" % nombre)
        print("  Cae siempre %+.1fs respecto del arranque real del 2T" % mediana)
        print("  Corrigiendo esos %+.1fs, acierta dentro de +-3s en %d de %d "
              "(la peor se va %.1fs)" % (-mediana, r["dentro"], r["n"], r["peor"]))

    # A igualdad de aciertos gana la que ya cae mas cerca sin corregir nada:
    # una regla que necesita mover 45s "siempre igual" es mas sospechosa (esta
    # agarrando otro corte) que una que cae encima.
    mejor = max(resumen.values(),
                key=lambda r: (r["dentro"], -r["peor"], -abs(r["mediana"])))
    print("")
    if mejor["dentro"] == mejor["n"]:
        if abs(mejor["mediana"]) <= 2:
            print("=> SIRVE tal cual, eligiendo %s." % mejor["nombre"])
        else:
            print("=> SIRVE eligiendo %s y corrigiendo %+.1fs fijo "
                  "(_VIDEO_CORTE_AJUSTE)." % (mejor["nombre"], -mejor["mediana"]))
    elif mejor["dentro"] >= mejor["n"] - 1:
        print("=> Casi: falla %d de %d eligiendo %s. Mirar esa(s) fecha(s) en la "
              "columna de cortes antes de largarlo."
              % (mejor["n"] - mejor["dentro"], mejor["n"], mejor["nombre"]))
    else:
        print("=> NO sirve asi: el corte cae en cualquier lado (lo mejor es %s, y "
              "acierta %d de %d). Mirar la columna de los cortes mas fuertes para "
              "entender que esta agarrando."
              % (mejor["nombre"], mejor["dentro"], mejor["n"]))
    return 0


def medir_pendientes(token, efforts, limite=0):
    """Corre la via del corte sobre las fechas que faltan calibrar y muestra
    que guardaria en cada una. No escribe nada."""
    if not st.VIDEO_SYNC_DISPONIBLE:
        print("[ERROR] Faltan yt-dlp / imageio-ffmpeg (pip install yt-dlp imageio-ffmpeg).")
        return 1
    try:
        sync = st._tigre_fb_get("gps/videoSync", token) or {}
    except Exception as e:
        print("[ERROR] No se pudo leer gps/videoSync: %s" % e)
        return 1
    tipicos = st._video_tipicos(token)

    pendientes = []
    for cat in sorted(efforts):
        for fecha_key in sorted(efforts[cat] or {}, key=lambda f: int(f.lstrip("F"))):
            if ((sync.get(cat) or {}).get(fecha_key) or {}).get("kickoff1") is not None:
                continue
            p1, _ = st._video_periodos_1y2((efforts[cat][fecha_key] or {}).get("periodos"))
            if not p1:
                continue
            pendientes.append((cat, fecha_key))
    if not pendientes:
        print("No queda ninguna fecha sin calibrar.")
        return 0

    print("Fechas sin calibrar: %d (esto tarda entre 20 y 40 segundos cada una)\n"
          % len(pendientes))
    print("%-5s %-5s %8s %10s %8s %5s  %s" %
          ("CAT", "FECHA", "1T", "2T", "HUECO", "CAND", "QUE HARIA"))
    print("-" * 100)

    calibraria, a_mano, sin_link = 0, 0, 0
    for i, (cat, fecha_key) in enumerate(pendientes):
        if limite and i >= limite:
            break
        try:
            link = st._tigre_fb_get("stats/links/%s/%s/par" % (cat, fecha_key.lstrip("F")), token)
        except Exception:
            link = None
        if not link:
            sin_link += 1
            continue
        k1_tip, hueco_tip = tipicos(cat)
        r, motivo, cortes = st._detectar_corte(link, k1_tip, hueco_tip)
        if r:
            calibraria += 1
            print("%-5s %-5s %8.1f %10.1f %8.0f %5d  CALIBRARIA SOLA" %
                  (cat, fecha_key, r["kickoff1"], r["kickoff2"],
                   r["kickoff2"] - r["kickoff1"], len(cortes)))
        else:
            a_mano += 1
            print("%-5s %-5s %8s %10s %8s %5d  queda a mano (%s)" %
                  (cat, fecha_key, "-", "-", "-", len(cortes), motivo))

    print("-" * 100)
    print("\nSe calibrarian solas: %d" % calibraria)
    print("Quedan para el boton de dos clics: %d" % a_mano)
    if sin_link:
        print("Sin link de video cargado: %d" % sin_link)
    if calibraria:
        print("\n=> Al mergear a main, esa(s) %d fecha(s) se resuelven solas en la "
              "proxima corrida de la PC." % calibraria)
    else:
        print("\n=> Esta via no resuelve ninguna de las que faltan: esos videos "
              "estan editados de otra forma.")
    return 0


def main():
    args = sys.argv[1:]
    rapido = "--rapido" in args           # solo cobertura, sin consultar YouTube
    cortes = "--cortes" in args           # probar el detector del corte del entretiempo
    cortes = cortes or "--pendientes" in args   # idem, sobre las fechas que faltan
    limite = next((int(a) for a in args if a.isdigit()), 0)

    if not st.VIDEO_SYNC_DISPONIBLE and not (rapido or cortes):
        print("[ERROR] Falta yt-dlp (pip install yt-dlp) -- sin eso no se puede leer la "
              "hora de arranque de los videos.")
        return 1

    # Las credenciales salen de las mismas variables de entorno que usa el
    # scraper; si no estan puestas (correr el script suelto, a mano), las pide
    # por teclado en vez de fallar -- no se guardan en ningun lado.
    email = os.environ.get("FIREBASE_EMAIL")
    password = os.environ.get("FIREBASE_PASSWORD")
    if not (email and password):
        print("No estan FIREBASE_EMAIL / FIREBASE_PASSWORD en el entorno, asi que van a mano")
        print("(es el mismo usuario de Firebase que usa el scraper; no se guarda nada).")
        try:
            email = email or input("Email de Firebase: ").strip()
            password = password or getpass.getpass("Contrasena: ")
        except (EOFError, KeyboardInterrupt):
            print("\n[ERROR] Sin credenciales no se puede leer la calibracion que ya tenes.")
            return 1
    if not (email and password):
        print("[ERROR] Faltan las credenciales de Firebase.")
        return 1

    try:
        with open(RUTA_TABLAS, encoding="utf-8") as f:
            efforts = json.load(f).get("catapult_efforts") or {}
    except Exception as e:
        print("[ERROR] No se pudo leer data/tablas.json: %s" % e)
        return 1
    if not efforts:
        print("[ERROR] data/tablas.json no tiene catapult_efforts todavia.")
        return 1

    try:
        token = st._tigre_fb_login(email, password)
    except Exception as e:
        print("[ERROR] No se pudo entrar a Firebase: %s" % e)
        return 1

    if "--cortes" in args:
        return medir_cortes(token, limite)
    if "--pendientes" in args:
        return medir_pendientes(token, efforts, limite)

    if rapido:
        print("%-5s %-5s %10s %10s %12s %12s %9s  %s" %
              ("CAT", "FECHA", "1T", "2T", "HUECO VID", "HUECO CATA", "DIF", "OBS"))
    else:
        print("%-5s %-5s %-10s %10s %10s %8s  %s" %
              ("CAT", "FECHA", "VIDEO", "GUARDADO", "MEDIDO", "DIF", "OBS"))
    print("-" * 86)

    # Registro del detector automatico: cuantas veces intento cada fecha sin
    # poder leerla. Es lo que dice si a las que faltan las puede resolver el
    # OCR o si ya se rindio con ellas (3 intentos con el mismo link).
    try:
        fallos = st._tigre_fb_get("gps/videoSyncFallos", token) or {}
    except Exception:
        fallos = {}
    rendidas = []

    errores, en_vivo, subidos, sin_link, cortados, mirados = [], 0, 0, 0, 0, 0
    calibradas, sin_calibrar = 0, []
    huecos, k1s = [], []      # para el chequeo de video continuo vs recortado
    for cat in sorted(efforts):
        for fecha_key in sorted(efforts[cat], key=lambda f: int(f.lstrip("F"))):
            if limite and mirados >= limite:
                break
            dia = efforts[cat][fecha_key] or {}
            p1, p2 = st._video_periodos_1y2(dia.get("periodos"))
            if not p1:
                continue
            try:
                link = st._tigre_fb_get("stats/links/%s/%s/par" % (cat, fecha_key.lstrip("F")), token)
            except Exception:
                link = None
            if not link:
                sin_link += 1
                continue
            mirados += 1
            try:
                sync = st._tigre_fb_get("gps/videoSync/%s/%s" % (cat, fecha_key), token)
            except Exception:
                sync = None
            guardado = (sync or {}).get("kickoff1")
            if guardado is None:
                sin_calibrar.append("%s %s" % (cat, fecha_key))
                intentos = ((fallos.get(cat) or {}).get(fecha_key) or {}).get("intentos", 0)
                if intentos >= 3:
                    rendidas.append("%s %s" % (cat, fecha_key))
            else:
                calibradas += 1
            gtxt = "-" if guardado is None else "%.1f" % float(guardado)
            if rapido:
                # Con las fechas ya calibradas se contesta la pregunta clave:
                # el hueco entre el arranque del 1T y el del 2T DENTRO DEL
                # VIDEO, comparado con el hueco real que da Catapult. Si
                # coinciden, el video es continuo y el 2T se puede calcular
                # solo; si el del video es mas chico, al video le recortaron
                # el entretiempo y ese calculo pondria el 2T corrido.
                k2 = (sync or {}).get("kickoff2")
                if guardado is None or k2 is None:
                    print("%-5s %-5s %10s %10s %12s %12s %9s  %s" %
                          (cat, fecha_key, gtxt, "-", "-", "-", "-",
                           "SIN CALIBRAR" if guardado is None else "sin 2T guardado"))
                    continue
                hueco_video = float(k2) - float(guardado)
                hueco_real = p2["start"] - p1["start"]
                dif = hueco_video - hueco_real
                huecos.append(dif)
                k1s.append(float(guardado))
                print("%-5s %-5s %10.1f %10.1f %12.0f %12.0f %+9.0f  %s" %
                      (cat, fecha_key, float(guardado), float(k2), hueco_video, hueco_real, dif,
                       "continuo" if abs(dif) <= 30 else "ENTRETIEMPO RECORTADO"))
                continue
            meta = st._video_metadata_yt(link)
            if not meta:
                print("%-5s %-5s %-10s %10s %10s %8s  %s" %
                      (cat, fecha_key, "?", gtxt, "-", "-", "no se pudo leer el video"))
                continue
            es_vivo = meta.get("live_status") in ("was_live", "is_live") and meta.get("release_timestamp")
            if not es_vivo:
                subidos += 1
                print("%-5s %-5s %-10s %10s %10s %8s  %s" %
                      (cat, fecha_key, meta.get("live_status") or "?", gtxt, "-", "-",
                       "archivo subido: sin hora de grabacion"))
                continue
            en_vivo += 1
            k1 = p1["start"] - meta["release_timestamp"]
            k2 = p2["start"] - meta["release_timestamp"]
            obs = []
            duracion = meta.get("duration") or 0
            if k1 < 0:
                obs.append("el stream arranco DESPUES del saque inicial")
            if duracion and k2 + (p2["end"] - p2["start"]) > duracion + st._VIDEO_TOLERANCIA_FIN:
                cortados += 1
                obs.append("el video no cubre el 2T (pausado/cortado)")
            if guardado is None:
                obs.append("sin calibrar todavia (esta es la que ganariamos)")
                print("%-5s %-5s %-10s %10s %10.1f %8s  %s" %
                      (cat, fecha_key, "en vivo", "-", k1, "-", "; ".join(obs)))
                continue
            dif = k1 - float(guardado)
            errores.append(dif)
            print("%-5s %-5s %-10s %10.1f %10.1f %+8.1f  %s" %
                  (cat, fecha_key, "en vivo", float(guardado), k1, dif, "; ".join(obs)))

    print("-" * 78)
    print("Calibradas hoy: %d de %d   |   faltan calibrar: %d" %
          (calibradas, mirados, len(sin_calibrar)))
    if sin_calibrar:
        print("Sin calibrar: %s" % ", ".join(sin_calibrar))
    if sin_calibrar:
        nunca = len(sin_calibrar) - len(rendidas)
        print("De esas, el detector automatico ya se rindio con %d (3 intentos sin poder "
              "leer el cartel) y todavia no llego a %d." % (len(rendidas), nunca))
        if rendidas and len(rendidas) == len(sin_calibrar):
            print("=> El OCR no puede con ninguna de las que faltan: son todas a mano "
                  "(o haria falta leer el cartel con vision de Claude).")
    if rapido:
        if k1s:
            k1s.sort()
            print("Arranque del 1T en el video: entre %.0fs y %.0fs (mediana %.0fs)" %
                  (k1s[0], k1s[-1], k1s[len(k1s) // 2]))
        if huecos:
            continuos = sum(1 for d in huecos if abs(d) <= 30)
            huecos.sort()
            print("Hueco entre tiempos: coincide con Catapult en %d de %d fechas "
                  "(diferencia entre %+.0fs y %+.0fs)" %
                  (continuos, len(huecos), huecos[0], huecos[-1]))
            if continuos == len(huecos):
                print("=> Los videos son continuos: el 2T se puede calcular solo a partir del 1T.")
            elif continuos == 0:
                print("=> A los videos les recortan el entretiempo: el 2T NO se puede calcular "
                      "a partir del 1T, hay que marcarlo a mano.")
            else:
                print("=> Mezcla: algunos videos son continuos y a otros les recortan el "
                      "entretiempo. El 2T calculado solo sirve como sugerencia a confirmar.")
        return 0
    print("Videos mirados: %d   |   en vivo: %d   |   subidos como archivo: %d   |   "
          "sin link: %d" % (mirados, en_vivo, subidos, sin_link))
    if cortados:
        print("Videos pausados o cortados (el 2T no cierra): %d" % cortados)
    if not errores:
        print("No hubo ninguna fecha que este calibrada Y sea transmision en vivo, "
              "asi que todavia no se puede medir el error.")
        return 0

    errores.sort()
    mediana = errores[len(errores) // 2]
    print("Comparacion contra %d fecha(s) ya calibradas: "
          "min %+.1fs / mediana %+.1fs / max %+.1fs" % (len(errores), errores[0], mediana, errores[-1]))
    disperso = errores[-1] - errores[0]
    # Ojo: mirar solo la dispersion no alcanza -- un desfasaje PAREJO de varios
    # segundos tiene dispersion 0 y aun asi hay que corregirlo.
    if disperso <= 3 and abs(mediana) <= 3:
        print("=> La hora real del stream coincide con lo ya calibrado. La via automatica "
              "es confiable (y mas precisa que el OCR).")
    elif disperso <= 10:
        print("=> Hay un desfasaje parejo de ~%+.1fs. El scraper ya lo corrige solo "
              "(se mide en cada corrida contra las fechas ya calibradas)." % mediana)
    else:
        print("=> Los errores no se parecen entre si (%.0fs de diferencia entre el mejor y "
              "el peor): revisar esas fechas a ojo antes de confiar en esta via." % disperso)
    return 0


if __name__ == "__main__":
    sys.exit(main())
