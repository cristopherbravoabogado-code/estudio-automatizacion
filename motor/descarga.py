#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""descarga.py - bajar un PDF grande desde donde SI se llega, y comprobar que llego entero.

POR QUE EXISTE (medido el 20/09/2026 desde el contenedor de Claude)

    archive.org:443        CONNECT -> 403   "policy denial or upstream failure"
    www.holybooks.com:443  CONNECT -> 403
    upload.wikimedia.org   CONNECT -> 403
    raw.githubusercontent.com -> 301        (o sea: lo unico que se alcanza es GitHub)

Ninguno de los espejos del Codice Rohonc es alcanzable desde el contenedor: el proxy de
egress rechaza el TUNEL, antes de que exista una peticion HTTP, asi que no hay cabecera,
reintento ni user-agent que sirva. Es el mismo muro que docs/RED-Y-BLOQUEOS.md ya anotaba
para archive.org. No se rodea -esta prohibido rodearlo-: se cambia de entorno. El runner de
Actions tiene internet sin proxy y el Mac tambien.

Por eso este archivo no depende de nada fuera de la biblioteca estandar: tiene que correr
igual en un runner recien creado, en el Mac y en el sandbox, sin pip.

LO QUE DE VERDAD APORTA ES COMPROBAR. `curl -sL url -o f` ante un 403 escribe la PAGINA DE
ERROR dentro del archivo y sale con codigo 0. Ya mordio una vez en este repo: las tres .ttf
de google/fonts que bajaron 378 bytes de HTML y dejaron el paso en verde con fuentes falsas
(.github/workflows/render-diario.yml). Un PDF que en realidad es un HTML de error tampoco
avisa: se nota cuando alguien lo abre, dias despues. Aca todo lo que baja se mide antes de
darlo por bueno -cabecera %PDF-, cola %%EOF, tamano minimo- y se imprime su sha256.

    python3 motor/descarga.py rohonc --destino _salida
    python3 motor/descarga.py --url https://ejemplo/x.pdf --destino _salida/x.pdf
"""

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

# Archive.org responde 403 a un urllib pelado; con un UA de navegador responde normal.
CABECERAS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) estudio-automatizacion/descarga.py"}

# Un espejo es {"archive": "<item>"} o {"url": "<url directa>"}.
# El orden importa: el primero que pase las comprobaciones gana y no se baja el resto.
CATALOGO = {
    "rohonc": {
        "titulo": "Codice Rohonc (Rohonci Kodex, K 114) - 448 paginas, escritura sin descifrar",
        "archivo": "codice-rohonc.pdf",
        # El facsimil completo ronda los 10 MB. Por debajo de 2 MB es una portada suelta o
        # una pagina de error con suerte: no es el codice.
        "minimo": 2_000_000,
        "espejos": [
            {"archive": "RohonciCodexK114cs"},  # escaneo sin marca de agua
            {"archive": "TheRohoncCodex"},      # copia hecha desde el microfilm
            {"url": "https://www.holybooks.com/wp-content/uploads/Rohonc-Codex.pdf"},
        ],
        "origen": "Biblioteca de la Academia Hungara de Ciencias (MTA), K 114. "
                  "Manuscrito del s. XVI-XVII; dominio publico por antiguedad.",
    },
}


def _leer(url, timeout=120):
    pedido = urllib.request.Request(url, headers=CABECERAS)
    return urllib.request.urlopen(pedido, timeout=timeout)


def pdf_de_archive(item):
    """Devuelve la url del PDF de un item de archive.org.

    Se pregunta por la API de metadatos en vez de adivinar el nombre del archivo. La
    convencion <item>/<item>.pdf NO se cumple: el PDF derivado se llama como el original que
    subio quien lo subio, y adivinarlo da un 404 que -otra vez- se guardaria como si fuera
    el PDF. Entre varios PDF gana el mas pesado, que es el facsimil y no el indice.
    """
    with _leer("https://archive.org/metadata/%s" % item, timeout=60) as r:
        meta = json.load(r)
    pdfs = [f for f in meta.get("files", []) if f.get("name", "").lower().endswith(".pdf")]
    if not pdfs:
        raise LookupError("el item %s no tiene ningun PDF en sus archivos" % item)
    pdfs.sort(key=lambda f: int(f.get("size") or 0), reverse=True)
    nombre = pdfs[0]["name"]
    return "https://archive.org/download/%s/%s" % (item, urllib.parse.quote(nombre))


def comprobar(ruta, minimo):
    """Mide el archivo bajado. Devuelve (sirve, motivo)."""
    if not os.path.exists(ruta):
        return False, "no existe"
    tam = os.path.getsize(ruta)
    if tam < minimo:
        return False, "pesa %d bytes, menos del minimo de %d" % (tam, minimo)
    with open(ruta, "rb") as f:
        cabeza = f.read(5)
        f.seek(max(0, tam - 2048))
        cola = f.read()
    if cabeza != b"%PDF-":
        # El caso tipico: una pagina de error HTML guardada con nombre de PDF.
        return False, "no empieza con %%PDF- sino con %r" % cabeza
    if b"%%EOF" not in cola:
        # Una descarga cortada a la mitad pesa lo suficiente y empieza bien igual.
        return False, "no termina en %%EOF: la descarga quedo cortada"
    return True, "%d bytes" % tam


def paginas(ruta):
    """Cuenta /Type /Page a ojo. Informativo: no decide nada, solo da una cifra que mirar."""
    try:
        with open(ruta, "rb") as f:
            crudo = f.read()
    except OSError:
        return 0
    return len(re.findall(rb"/Type\s*/Page[^s]", crudo))


def sha256(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for trozo in iter(lambda: f.read(1024 * 1024), b""):
            h.update(trozo)
    return h.hexdigest()


def bajar(espejo, destino, minimo):
    """Baja un espejo a destino. Devuelve la url usada, o levanta la ultima excepcion."""
    url = pdf_de_archive(espejo["archive"]) if "archive" in espejo else espejo["url"]
    print("  bajando %s" % url)
    parcial = destino + ".parcial"
    with _leer(url) as r, open(parcial, "wb") as f:
        while True:
            trozo = r.read(1024 * 256)
            if not trozo:
                break
            f.write(trozo)
    sirve, motivo = comprobar(parcial, minimo)
    if not sirve:
        os.replace(parcial, destino + ".rechazado")
        raise ValueError("lo que bajo no es el PDF: %s (queda en %s.rechazado)" % (motivo, destino))
    os.replace(parcial, destino)
    return url


def main():
    p = argparse.ArgumentParser(description="Baja un PDF y comprueba que sea un PDF entero.")
    p.add_argument("documento", nargs="?", help="nombre del catalogo: %s" % ", ".join(CATALOGO))
    p.add_argument("--url", help="url directa, en vez de un documento del catalogo")
    p.add_argument("--destino", default="_salida",
                   help="carpeta o ruta de archivo donde dejarlo (por defecto _salida)")
    p.add_argument("--minimo", type=int, default=100_000,
                   help="bytes minimos para dar por buena una descarga con --url")
    a = p.parse_args()

    if a.url:
        ficha = {"titulo": a.url, "archivo": os.path.basename(urllib.parse.urlparse(a.url).path)
                                             or "descarga.pdf",
                 "minimo": a.minimo, "espejos": [{"url": a.url}], "origen": ""}
    elif a.documento in CATALOGO:
        ficha = CATALOGO[a.documento]
    else:
        p.error("falta un documento del catalogo (%s) o --url" % ", ".join(CATALOGO))

    destino = a.destino
    if os.path.isdir(destino) or not destino.lower().endswith(".pdf"):
        os.makedirs(destino, exist_ok=True)
        destino = os.path.join(destino, ficha["archivo"])
    else:
        os.makedirs(os.path.dirname(os.path.abspath(destino)), exist_ok=True)

    print(ficha["titulo"])
    if ficha["origen"]:
        print(ficha["origen"])

    fallas = []
    for espejo in ficha["espejos"]:
        nombre = espejo.get("archive") or espejo["url"]
        try:
            url = bajar(espejo, destino, ficha["minimo"])
        except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError,
                LookupError, json.JSONDecodeError) as e:
            print("  NO: %s -> %s" % (nombre, e))
            fallas.append("%s: %s" % (nombre, e))
            continue
        print("\nOK  %s" % destino)
        print("    origen   %s" % url)
        print("    tamano   %d bytes" % os.path.getsize(destino))
        print("    paginas  ~%d (conteo a ojo sobre /Type /Page)" % paginas(destino))
        print("    sha256   %s" % sha256(destino))
        return 0

    print("\nNingun espejo sirvio. Si todos dicen 403 o 'CONNECT tunnel failed', el entorno "
          "es el problema y no los espejos: ver docs/RED-Y-BLOQUEOS.md y correr esto en un "
          "runner de Actions o en el Mac.", file=sys.stderr)
    for f in fallas:
        print("  - %s" % f, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
