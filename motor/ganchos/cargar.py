#!/usr/bin/env python3
"""cargar.py (19/09/2026) - carga ganchos nuevos en motor/ganchos/cola.json.

POR QUE EXISTE
--------------
El 17/09 se implemento el CONTROL 0 de produce.py: una pieza de lamina cuyo gancho no
este en `motor/ganchos/cola.json` no se produce. El diagnostico de esa noche fue que la
regla vivia en prosa dentro de un archivo de memoria y ninguna pieza de codigo podia
leerla. Pero la CARGA siguio siendo manual: la noche del 17/09 se escribieron 15 ganchos
nuevos en memoria y la del 18/09 otros 15, y ninguno de los 30 llego al JSON. Dos noches
seguidas el banco crecio donde el motor no mira, y el CONTROL 0 los habria rechazado uno
por uno. Este script cierra ese hueco: el banco se carga con codigo, no a mano.

DEDUPE POR PREFIJO, no por texto exacto: el CONTROL 0 de produce.py acepta una pieza si
el gancho coincide con una entrada o si comparten los primeros 40 caracteres plegados.
Dos entradas con el mismo prefijo de 40 son indistinguibles para el control y rompen el
seguimiento de "usado", asi que aqui se rechazan con su motivo. Medido el 19/09:
"Renunciaste presionado y te dijeron que era lo mejor" choca con 14-09 en los 40 exactos.

USO
---
  python3 cargar.py cola.json nuevos.txt --lote 19 > cola.nueva.json
Formato de nuevos.txt: una linea por gancho, "materia|texto". Lineas vacias y las que
empiezan con # se ignoran. Los ids salen del lote: 19-01, 19-02, ...
Tambien, y se pueden combinar en la misma llamada:
  python3 cargar.py cola.json --usar 15-14=2026-09-19 --retirar 14-06="ventana vencida"
El informe (agregados, rechazados con motivo, total y libres) sale por stderr; el JSON
nuevo sale por stdout, asi que nunca se sobrescribe el banco a medias.

Los ganchos se escriben SIN tildes ni n-tilde, como el resto del banco: el CONTROL 0
compara plegado, y el guion de la pieza si lleva las tildes (regla dura 2, control 6).
"""
import json, sys, unicodedata


def fold(s):
    s = "".join(c for c in unicodedata.normalize("NFD", s.lower())
                if unicodedata.category(c) != "Mn")
    return " ".join(s.split())


def pref(s, n=40):
    return fold(s)[:n]


def cargar(banco, nuevos, lote):
    """Agrega los que no choquen. Devuelve (agregados, rechazados=[(texto, motivo)])."""
    vistos = {pref(e["texto"]): e["id"] for e in banco["cola"]}
    ag, rech, n = [], [], 0
    for materia, texto in nuevos:
        p = pref(texto)
        if p in vistos:
            rech.append((texto, "mismo prefijo de 40 que %s" % vistos[p]))
            continue
        n += 1
        e = {"id": "%s-%02d" % (lote, n), "materia": materia, "ventana": None,
             "usado": None, "texto": texto}
        vistos[p] = e["id"]
        ag.append(e)
        banco["cola"].append(e)
    return ag, rech


def usar(banco, id_, fecha, pieza=None):
    for e in banco["cola"]:
        if e["id"] == id_:
            e["usado"] = fecha
            if pieza:
                e["pieza"] = pieza
            return True
    return False


def retirar(banco, id_, motivo, hoy):
    banco.setdefault("retirados", {}).setdefault("ids", []).append(
        {"id": id_, "motivo": motivo, "fecha": hoy})
    antes = len(banco["cola"])
    banco["cola"] = [e for e in banco["cola"] if e["id"] != id_]
    return len(banco["cola"]) < antes


def main(argv):
    if len(argv) < 2:
        sys.exit(__doc__)
    banco = json.load(open(argv[1], encoding="utf-8"))
    hoy = __import__("datetime").date.today().isoformat()
    lote, nuevos, msg, i = None, [], [], 2
    while i < len(argv):
        a = argv[i]
        if a == "--lote":
            lote = argv[i + 1]; i += 2
        elif a == "--usar":
            k, v = argv[i + 1].split("=", 1)
            msg.append(("usar", k, usar(banco, k, v))); i += 2
        elif a == "--retirar":
            k, v = argv[i + 1].split("=", 1)
            msg.append(("retirar", k, retirar(banco, k, v, hoy))); i += 2
        else:
            for ln in open(a, encoding="utf-8"):
                ln = ln.strip()
                if not ln or ln.startswith("#"):
                    continue
                m, t = ln.split("|", 1)
                nuevos.append((m.strip(), t.strip()))
            i += 1
    if nuevos:
        if not lote:
            sys.exit("falta --lote")
        ag, rech = cargar(banco, nuevos, lote)
        msg.append(("agregados", len(ag), [e["id"] for e in ag]))
        msg.append(("rechazados", len(rech), rech))
    banco["actualizado"] = hoy
    libres = len([e for e in banco["cola"] if not e["usado"]])
    msg.append(("total", len(banco["cola"]), "libres %d" % libres))
    for m in msg:
        print(*m, file=sys.stderr)
    json.dump(banco, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(sys.argv)
