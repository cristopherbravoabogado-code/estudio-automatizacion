#!/usr/bin/env python3
"""RADAR GLOBAL — qué está en tendencia HOY en el mundo, normalizado a una sola tabla.

Uso:  python3 radar.py [salida.json] [--video]

Fuentes gratis, sin clave y verificadas el 05/09/2026 desde el sandbox:
  1. Google Trends RSS  https://trends.google.com/trending/rss?geo=XX   (tema + volumen + noticia)
  2. Google News RSS    https://news.google.com/rss?hl=..&gl=..&ceid=.. (titulares del día)
  3. Wikipedia          wikimedia.org/api/rest_v1/metrics/pageviews/top (qué leyó el mundo ayer)
  4. trends24           https://trends24.in/<pais>/                     (tendencias de X)
NO sirven (probado): Reddit (bloquea la IP del datacenter), TikTok Creative Center (pide firma),
YouTube /feed/trending (YouTube lo retiró). Los sonidos de TikTok salen del conector Higgsfield.

Cada tema recibe un PUNTAJE DE ÁNGULO JURÍDICO con un diccionario por materia y un peso por país
(Chile vale 3x: es el mercado). Los que puntúan pasan a la capa de video (--video): yt-dlp busca
en YouTube Shorts el viral real de ese tema y devuelve vistas y duración, para copiar la
ESTRUCTURA (nunca el contenido). Corre en 3 s sin --video y en ~2 min con --video.
"""
import sys, json, re, subprocess, urllib.request, urllib.parse, datetime, xml.etree.ElementTree as ET

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36"}
PAISES = [("CL", "chile", "es-419", "CL:es-419"), ("MX", "mexico", "es-419", "MX:es-419"),
          ("ES", "spain", "es", "ES:es"), ("AR", "argentina", "es-419", "AR:es-419"),
          ("US", "united-states", "en-US", "US:en")]

MATERIAS = {
 "laboral": "despido despiden finiquito sueldo salario trabajo empleo jefe empleador licencia vacaciones contrato renuncia acoso sindicato huelga indemnizacion cotizaciones afp reajuste jornada",
 "familia": "pension alimentos hijo hija divorcio custodia cuidado personal visitas violencia intrafamiliar matrimonio separacion tuicion",
 "penal": "detenido detencion carabineros fiscalia policia robo portonazo carcel delito denuncia estafa droga homicidio condena imputado formalizacion juicio prision",
 "civil": "arriendo arrendador deuda contrato garantia vecino propiedad herencia testamento cobranza desalojo posesion efectiva",
 "consumidor": "sernac garantia compra retracto aerolinea vuelo banco tarjeta retail reembolso servicio cliente estafa online suscripcion",
 "transito": "accidente choque licencia conducir multa alcotest alcoholemia seguro soap parte transito",
 "salud": "isapre fonasa licencia medica compin ges auge cotizacion salud",
}
CONFLICTO = "ley leyes corte tribunal demanda denuncia fallo sentencia reforma juicio condena multa indemnizacion derecho derechos abogado fiscal decreto norma proyecto"
PESO_PAIS = {"CL": 3.0, "chile": 3.0, "es": 1.5, "MX": 1.2, "AR": 1.2, "ES": 1.2, "US": 1.0}

def fetch(url, timeout=20):
    try:
        return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout).read().decode("utf8", "ignore")
    except Exception as e:
        return ""

def norm(s):
    s = s.lower()
    for a, b in zip("áéíóúñü", "aeioun u"): s = s.replace(a, b)
    return s

def score_legal(texto, pais="CL"):
    """Cuánto se puede aterrizar el tema a un ángulo jurídico. Pesa el país: Chile es el mercado."""
    t = " " + norm(texto) + " "
    hits, total = {}, 0
    for mat, words in MATERIAS.items():
        n = sum(1 for w in words.split() if " " + w in t)
        if n: hits[mat] = n; total += n
    total += 0.5 * sum(1 for w in CONFLICTO.split() if " " + w in t)
    mat = max(hits, key=hits.get) if hits else ("general" if total else None)
    return round(total * PESO_PAIS.get(pais, 1.0), 1), mat

def gtrends(geo):
    xml = fetch(f"https://trends.google.com/trending/rss?geo={geo}")
    out = []
    if not xml.startswith("<?xml"): return out
    try: root = ET.fromstring(xml)
    except Exception: return out
    ns = {"ht": "https://trends.google.com/trending/rss"}
    for it in root.iter("item"):
        t = (it.findtext("title") or "").strip()
        traf = (it.findtext("ht:approx_traffic", namespaces=ns) or "").strip()
        news = [n.text.strip() for n in it.iterfind("ht:news_item/ht:news_item_title", ns) if n.text][:2]
        if t: out.append({"fuente": "google_trends", "pais": geo, "tema": t, "volumen": traf, "contexto": news})
    return out

def gnews(geo, hl, ceid):
    xml = fetch(f"https://news.google.com/rss?hl={hl}&gl={geo}&ceid={ceid}")
    out = []
    try: root = ET.fromstring(xml)
    except Exception: return out
    for it in list(root.iter("item"))[:15]:
        t = (it.findtext("title") or "").strip()
        if t: out.append({"fuente": "google_news", "pais": geo, "tema": t, "volumen": "", "contexto": []})
    return out

def wiki(lang="es"):
    d = datetime.date.today() - datetime.timedelta(days=1)
    j = fetch(f"https://wikimedia.org/api/rest_v1/metrics/pageviews/top/{lang}.wikipedia/all-access/{d:%Y/%m/%d}")
    out = []
    try: arts = json.loads(j)["items"][0]["articles"]
    except Exception: return out
    for a in arts[:25]:
        t = a["article"].replace("_", " ")
        if ":" in t or t in ("Portada", "Main Page"): continue
        out.append({"fuente": "wikipedia", "pais": lang, "tema": t, "volumen": f"{a['views']} vistas", "contexto": []})
    return out

def x_trends(pais):
    h = fetch(f"https://trends24.in/{pais}/")
    ts = re.findall(r'trend-name[^>]*>\s*<a[^>]*>([^<]{2,40})', h)[:15]
    return [{"fuente": "x_twitter", "pais": pais, "tema": t.strip(), "volumen": "", "contexto": []} for t in ts]

def videos_del_tema(tema, materia, n=8):
    """El viral REAL que ya funcionó con ese tema: YouTube Shorts ordenado por vistas.
    Dos pasadas: primero acotado a Chile y <=120 s; si no hay nada, abierto y <=180 s."""
    for q, maxdur in ((f"{tema} {materia or ''} chile".strip(), 120), (f"{tema} {materia or ''}".strip(), 180)):
        cmd = ['yt-dlp', '--flat-playlist', '--no-warnings', '--print',
               '%(id)s|%(view_count)s|%(duration)s|%(channel)s|%(title).60s', f'ytsearch{n}:{q} shorts']
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=70).stdout.strip().splitlines()
        except Exception:
            r = []
        out = []
        for l in r:
            p = l.split("|")
            if len(p) < 5: continue
            try: v = int(p[1]); dur = float(p[2] or 0)
            except Exception: continue
            if dur and dur <= maxdur:
                out.append({"url": f"https://youtube.com/watch?v={p[0]}", "vistas": v, "dur_s": int(dur), "canal": p[3], "titulo": p[4], "busqueda": q})
        if out: return sorted(out, key=lambda x: -x["vistas"])[:3]
    return []

def main():
    salida = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else f"radar-{datetime.date.today()}.json"
    con_video = "--video" in sys.argv
    crudo = []
    for geo, slug, hl, ceid in PAISES:
        crudo += gtrends(geo)
        crudo += gnews(geo, geo, ceid)
        crudo += x_trends(slug)
    crudo += wiki("es") + wiki("en")
    vistos, temas = set(), []
    for t in crudo:
        k = norm(t["tema"])[:40]
        if k in vistos: continue
        vistos.add(k)
        sc, mat = score_legal(t["tema"] + " " + " ".join(t.get("contexto", [])), t["pais"])
        t["score_legal"], t["materia"] = sc, mat
        temas.append(t)
    legales = sorted([t for t in temas if t["score_legal"] > 0], key=lambda x: -x["score_legal"])
    if con_video:
        for t in legales[:4]:
            t["videos"] = videos_del_tema(t["tema"], t["materia"])
    res = {"fecha": str(datetime.datetime.now().astimezone()), "total_temas": len(temas),
           "por_fuente": {f: sum(1 for t in temas if t["fuente"] == f) for f in {x["fuente"] for x in temas}},
           "con_angulo_legal": legales[:20], "todos": temas}
    json.dump(res, open(salida, "w"), ensure_ascii=False, indent=1)
    print(f"RADAR_OK temas={len(temas)} legales={len(legales)} fuentes={res['por_fuente']} -> {salida}")
    for t in legales[:8]:
        v = t.get("videos") or []
        print(f"  [{t['score_legal']}] {t['materia']:11s} {t['pais']:3s} {t['fuente'][:13]:13s} {t['tema'][:60]}" + (f"  | video top: {v[0]['vistas']} vistas {v[0]['dur_s']}s" if v else ""))
if __name__ == "__main__":
    main()
