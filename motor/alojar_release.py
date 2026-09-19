#!/usr/bin/env python3
"""alojar_release.py v1 (19/09/2026) - subir los mp4 del dia a una Release, con su tipo de verdad.

POR QUE EXISTE
--------------
El 19/09 el dia quedo 0/10 hasta las 10:20 UTC. La cadena no estaba rota: estaba rota UNA linea.
`gh release upload` sube el archivo sin decir que es, y GitHub lo guarda como
`application/octet-stream`. Ese tipo viaja despues dentro de la url firmada de descarga
(`rsct=application%2Foctet-stream`), asi que cualquiera que baje la pieza recibe "un monton de
bytes", no un video. Higgsfield lo rechaza con todas sus letras:

    media_import_url -> "Unsupported content-type: application/octet-stream"

Y ahi empieza el dano de verdad. Sin `media_import_url`, la tarea que publica tiene que caer a la
via larga: `media_upload`, copiar A MANO una url firmada de 1.808 caracteres, hacerle un PUT,
`media_confirm`. Esa via funciona -asi se publico la ranura 1 de hoy- pero es lenta y la tarea se
alarga; las tareas largas de esta cuenta arrancan y nunca cierran (T2 disparo a las 10:08 y seguia
PENDING sin `finished_at` cuando hubo que publicar a mano). O sea: un tipo MIME equivocado en la
subida terminaba dejando el dia en cero. Exactamente el fallo que toda esta maquinaria vino a
arreglar.

LA REGLA QUE APLICA
-------------------
"Un control que se apaga por omision no es un control" (control.py v3, 15/09). El 18/09 las fuentes
se bajaron con `curl -sL`, el servidor devolvio un 403 de 378 bytes, el paso quedo VERDE y los
videos salieron sin tipografia. Aqui no: despues de subir, este script VUELVE A LEER el tipo que
GitHub guardo y, si no es `video/mp4`, termina con error. Un `200` de la API no es prueba de nada.

MODOS
-----
  subir    <mp4...>   sube cada archivo a la Release del dia con Content-Type: video/mp4
  retipar             repara una Release ya existente: baja los assets mal tipados y los vuelve a
                      subir bien. Sirve para las piezas que ya quedaron alojadas como octet-stream
                      antes de este arreglo, sin tener que renderizarlas de nuevo.
  verificar           solo mira: lista los assets y su tipo. Sale 1 si alguno esta mal.

El token sale de GH_TOKEN (el del propio workflow). No se guarda ni se imprime nunca.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.github.com"
UPLOADS = "https://uploads.github.com"
TIPO = "video/mp4"


def token():
    t = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not t:
        print("FALTA GH_TOKEN: sin token no se puede tocar la Release.", file=sys.stderr)
        sys.exit(2)
    return t


def pedir(url, metodo="GET", cuerpo=None, tipo="application/json", crudo=False, auth=True):
    req = urllib.request.Request(url, data=cuerpo, method=metodo)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if auth:
        req.add_header("Authorization", "Bearer %s" % token())
    if cuerpo is not None:
        req.add_header("Content-Type", tipo)
    with urllib.request.urlopen(req, timeout=300) as r:
        datos = r.read()
    if crudo:
        return datos
    return json.loads(datos) if datos else {}


def release(repo, tag, crear=True):
    """Devuelve la Release del tag; la crea si no existe."""
    try:
        return pedir("%s/repos/%s/releases/tags/%s" % (API, repo, tag))
    except urllib.error.HTTPError as e:
        if e.code != 404 or not crear:
            raise
    cuerpo = json.dumps({
        "tag_name": tag,
        "name": "Piezas %s" % tag.replace("piezas-", ""),
        "body": "mp4 del dia, subidos por render-diario. Se regeneran: no son un respaldo.",
    }).encode()
    return pedir("%s/repos/%s/releases" % (API, repo), "POST", cuerpo)


def borrar_asset(repo, asset_id):
    try:
        pedir("%s/repos/%s/releases/assets/%s" % (API, repo, asset_id), "DELETE")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            raise


def subir(repo, rel, nombre, datos):
    """Sube un asset DICIENDO que es un video. Reemplaza el que hubiera con ese nombre."""
    for a in rel.get("assets", []):
        if a["name"] == nombre:
            borrar_asset(repo, a["id"])
    url = "%s/repos/%s/releases/%s/assets?name=%s" % (UPLOADS, repo, rel["id"], nombre)
    return pedir(url, "POST", datos, tipo=TIPO)


def assets(repo, tag):
    return release(repo, tag, crear=False).get("assets", [])


def cmd_subir(a):
    rel = release(a.repo, a.tag)
    malos = 0
    for ruta in a.archivos:
        nombre = os.path.basename(ruta)
        with open(ruta, "rb") as f:
            datos = f.read()
        if not datos:
            print("::error::%s esta vacio: no se sube." % nombre)
            malos += 1
            continue
        r = subir(a.repo, rel, nombre, datos)
        print("  %s subido (%d bytes) como %s" % (nombre, len(datos), r.get("content_type")))
        rel = release(a.repo, a.tag, crear=False)   # refrescar para el proximo reemplazo
    return cmd_verificar(a) or (1 if malos else 0)


def cmd_retipar(a):
    """Repara assets ya subidos con el tipo equivocado, sin volver a renderizar."""
    rel = release(a.repo, a.tag, crear=False)
    arreglados = 0
    for asset in list(rel.get("assets", [])):
        if not asset["name"].endswith(".mp4") or asset["content_type"] == TIPO:
            continue
        print("  %s esta como %s; se rescata y se vuelve a subir." %
              (asset["name"], asset["content_type"]))
        # El repositorio es publico: la url de descarga no necesita token, y asi la firma de
        # Azure no se pelea con una cabecera Authorization reenviada.
        datos = pedir(asset["browser_download_url"], crudo=True, auth=False)
        if len(datos) != asset["size"]:
            print("::error::%s se bajo incompleto (%d de %d bytes): no se toca." %
                  (asset["name"], len(datos), asset["size"]))
            continue
        rel = release(a.repo, a.tag, crear=False)
        r = subir(a.repo, rel, asset["name"], datos)
        print("     ahora es %s" % r.get("content_type"))
        arreglados += 1
    print("RETIPADOS %d assets en %s" % (arreglados, a.tag))
    return cmd_verificar(a)


def cmd_verificar(a):
    """El porton: si GitHub no guardo video/mp4, esto NO pasa en silencio."""
    mal = [x for x in assets(a.repo, a.tag)
           if x["name"].endswith(".mp4") and x["content_type"] != TIPO]
    todos = [x for x in assets(a.repo, a.tag) if x["name"].endswith(".mp4")]
    for x in mal:
        print("::error::%s quedo como '%s' y no como %s: media_import_url lo va a rechazar."
              % (x["name"], x["content_type"], TIPO))
    print("VERIFICACION %s: %d mp4, %d con el tipo equivocado" % (a.tag, len(todos), len(mal)))
    return 1 if mal else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("modo", choices=["subir", "retipar", "verificar"])
    ap.add_argument("archivos", nargs="*")
    ap.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"), required=False)
    ap.add_argument("--tag", required=True)
    a = ap.parse_args()
    if not a.repo:
        print("FALTA --repo (o GITHUB_REPOSITORY).", file=sys.stderr)
        return 2
    return {"subir": cmd_subir, "retipar": cmd_retipar, "verificar": cmd_verificar}[a.modo](a)


if __name__ == "__main__":
    sys.exit(main())
