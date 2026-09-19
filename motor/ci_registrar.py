#!/usr/bin/env python3
"""ci_registrar.py v1 (19/09/2026) - el puente entre el render y el libro de cuentas.

POR QUE EXISTE
--------------
`produce.py` deja un `resultado.json` con una linea por pieza y ahi termina su trabajo. Hasta el
19/09 ese archivo moria con el sandbox y lo que habia pasado quedaba solo en la memoria de la
sesion: si la sesion se caia, nadie sabia que pieza se habia alojado y cual no. Este script lee
ese resultado y lo anota en `estado/<fecha>.json`, que si sobrevive porque se commitea.

NO REIMPLEMENTA LOS PORTONES
----------------------------
Podria escribir el JSON del dia directamente. No lo hace: invoca `motor/cadena.py marcar` como
subproceso, para que las reglas vivan en UN solo lugar. Es la misma decision que llevo los
controles de `produce.py` y de `build_sv.py` a `control.py` el 15/09: una receta que se escribe
sus propias reglas nace con los controles apagados y no se entera. Si `cadena.py` rechaza un
paso, aqui se respeta el rechazo y la pieza se marca fallida con el motivo.

QUE ESPERA
----------
  cola/<fecha>.json   la tanda: {"piezas":[{"id","slot",...}]}
  resultado.json      lo que dejo produce.py en el directorio de trabajo
  --base-url          donde quedo alojado el mp4. El workflow sube cada pieza como asset de una
                      Release de GitHub y pasa aqui la base de descarga; la url de la pieza es
                      <base-url>/<id>.mp4. Antes la pieza traia una upload_url presignada de
                      Higgsfield, de ~2.400 caracteres, que la sesion que armaba la cola copiaba
                      A MANO: diez piezas eran 24.000 caracteres transcritos sin un solo error,
                      todos los dias. La url de la Release es corta, publica y no caduca.

QUE HACE, POR PIEZA
-------------------
  control.pasa true  ->  marcar renderizado  y luego  marcar alojado con la url de la Release
  cualquier otra cosa ->  fallar con el motivo exacto

Una pieza solo puede marcarse renderizada si su ranura ya esta en `guion`: la tarea de la manana
tiene que haber anotado tema, derecho y guion antes de que el render corra. Si no lo esta,
`cadena.py` rechaza el paso y aqui se informa con esas palabras, sin inventar el paso que falta.

Uso:  python3 motor/ci_registrar.py --cola cola/2026-09-19.json --resultado _salida/resultado.json
"""

import argparse
import json
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CADENA = os.path.join(RAIZ, "motor", "cadena.py")


def cadena(*args):
    """Llama a cadena.py. Devuelve (ok, salida)."""
    r = subprocess.run([sys.executable, CADENA] + list(args),
                       capture_output=True, text=True, cwd=RAIZ)
    return r.returncode == 0, (r.stdout + r.stderr).strip()


def motivo_de(res):
    """El motivo exacto por el que una pieza no quedo alojada, en las palabras del pipeline."""
    if res.get("error"):
        return "produce.py: %s" % res["error"][:300]
    c = res.get("control") or {}
    if c.get("pasa") is not True:
        return "control.py reprobo: %s" % ", ".join(c.get("falla") or ["sin detalle"])
    subida = str(res.get("subida", ""))
    if "200" not in subida:
        return "la subida no devolvio 200: %s" % subida[:200]
    return "motivo desconocido; resultado: %s" % json.dumps(res, ensure_ascii=False)[:300]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cola", required=True)
    ap.add_argument("--resultado", required=True)
    ap.add_argument("--fecha", help="AAAA-MM-DD; por defecto el del nombre de la cola")
    ap.add_argument("--base-url", help="base publica donde el workflow dejo los mp4")
    args = ap.parse_args()

    fecha = args.fecha or os.path.basename(args.cola).replace(".json", "")

    with open(args.cola, encoding="utf-8") as f:
        piezas = {str(p["id"]): p for p in json.load(f)["piezas"]}

    if not os.path.exists(args.resultado):
        print("NO HAY resultado.json en %s: produce.py no llego a escribir nada." % args.resultado)
        print("Las ranuras de la cola quedan como estaban; la proxima corrida las retoma.")
        return 1

    with open(args.resultado, encoding="utf-8") as f:
        resultados = json.load(f)

    alojadas, fallidas, rechazadas = 0, 0, 0
    for res in resultados:
        pid = str(res.get("id"))
        pieza = piezas.get(pid)
        if not pieza:
            print("  pieza %s no esta en la cola; se ignora." % pid)
            continue
        slot = str(pieza["slot"])
        c = res.get("control") or {}
        # La pieza esta alojada si paso la puerta Y hay donde apuntarla: la Release que subio el
        # workflow (--base-url) o, por la via vieja, un PUT a una upload_url que devolvio 200.
        paso = c.get("pasa") is True
        url = ("%s/%s.mp4" % (args.base_url.rstrip("/"), pid)) if args.base_url else pieza.get("url")
        subio = paso and (bool(args.base_url) or "200" in str(res.get("subida", "")))

        if not subio:
            motivo = motivo_de(res) if not paso else (
                "la pieza paso los controles pero no quedo alojada: ni Release ni upload_url")
            ok, salida = cadena("fallar", slot, "--fecha", fecha, "--motivo", motivo)
            print("  #%s FALLIDA: %s" % (slot, motivo))
            if not ok:
                print("     (cadena.py: %s)" % salida)
            fallidas += 1
            continue

        ok, salida = cadena("marcar", slot, "renderizado", "--fecha", fecha,
                            "--json", json.dumps({"control": c}, ensure_ascii=False))
        if not ok:
            # cadena.py rechazo el paso: casi siempre porque la ranura no llego a 'guion'.
            print("  #%s RECHAZADA por cadena.py: %s" % (slot, salida))
            cadena("fallar", slot, "--fecha", fecha,
                   "--motivo", "el render paso pero cadena.py rechazo el paso: %s" % salida[:200])
            rechazadas += 1
            continue

        campos = ["--campo", "url=%s" % url]
        if pieza.get("media_id"):
            campos += ["--campo", "media_id=%s" % pieza["media_id"]]
        ok, salida = cadena("marcar", slot, "alojado", "--fecha", fecha, *campos)
        if not ok:
            print("  #%s renderizada pero NO alojada: %s" % (slot, salida))
            rechazadas += 1
            continue
        print("  #%s alojada: %s" % (slot, url))
        alojadas += 1

    print("REGISTRO %s: %d alojadas, %d fallidas, %d rechazadas" %
          (fecha, alojadas, fallidas, rechazadas))
    subprocess.run([sys.executable, CADENA, "resumen", "--fecha", fecha], cwd=RAIZ)
    return 0 if alojadas else 1


if __name__ == "__main__":
    sys.exit(main())
