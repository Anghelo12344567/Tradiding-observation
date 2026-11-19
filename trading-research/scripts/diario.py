#!/usr/bin/env python3
"""Analiza un diario de operaciones (CSV) y saca estadísticas, coste de cada error y patrones.

Uso: python diario.py operaciones.csv [--json]
Formato: ver references/diario-schema.md. Solo librería estándar.
"""
import argparse, csv, json, sys, statistics
from collections import defaultdict
from datetime import datetime

ALIAS = {"fecha": ["fecha", "date"], "activo": ["activo", "symbol", "ticker"], "lado": ["lado", "side"],
         "entrada": ["entrada", "entry"], "salida": ["salida", "exit"], "stop": ["stop"],
         "tamano": ["tamano", "tamaño", "size", "cantidad"], "resultado": ["resultado", "pnl"],
         "comision": ["comision", "comisión", "fees"], "errores": ["errores", "tags", "etiquetas"]}
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

def num(x):
    if x is None: return None
    x = str(x).strip().replace("€", "").replace("$", "").replace(" ", "")
    if x == "": return None
    if "," in x and "." in x: x = x.replace(".", "").replace(",", ".")
    else: x = x.replace(",", ".")
    try: return float(x)
    except ValueError: return None

def fecha(x):
    for f in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try: return datetime.strptime(str(x).strip(), f)
        except ValueError: pass
    return None

def leer(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        muestra = f.read(2048); f.seek(0)
        delim = ";" if muestra.count(";") > muestra.count(",") else ","
        rd = csv.DictReader(f, delimiter=delim)
        cab = {(h or "").strip().lower(): h for h in (rd.fieldnames or [])}
        col = {k: next((cab[a] for a in v if a in cab), None) for k, v in ALIAS.items()}
        faltan = [k for k in ("fecha", "activo", "lado", "entrada", "salida") if not col[k]]
        if faltan: raise SystemExit(f"Error: faltan columnas obligatorias: {', '.join(faltan)}. Revisa references/diario-schema.md")
        ops = []
        for i, row in enumerate(rd, start=2):
            g = lambda k: row.get(col[k]) if col[k] else None
            e, s, st, t = num(g("entrada")), num(g("salida")), num(g("stop")), num(g("tamano"))
            lado = str(g("lado") or "").strip().lower()
            d = 1 if lado in ("largo", "long", "buy", "compra") else -1 if lado in ("corto", "short", "sell", "venta") else 0
            if e is None or s is None or d == 0:
                print(f"Aviso: fila {i} ignorada (entrada, salida o lado no válidos)", file=sys.stderr); continue
            com = num(g("comision")) or 0.0
            pnl = num(g("resultado"))
            if pnl is None: pnl = d * (s - e) * (t if t else 1.0) - com
            r = None
            if st is not None and st != e:
                riesgo_unit = abs(e - st)
                r = (d * (s - e)) / riesgo_unit if not num(g("resultado")) or not t else pnl / (riesgo_unit * t)
            tags = [x.strip().lower() for x in str(g("errores") or "").replace(",", ";").split(";") if x.strip()]
            ops.append(dict(fila=i, fecha=fecha(g("fecha")), activo=g("activo"), lado=lado, pnl=pnl, r=r, stop=st, tamano=t, tags=tags))
    return ops

def resumen(ops):
    n = len(ops); gan = [o for o in ops if o["pnl"] > 0]; per = [o for o in ops if o["pnl"] <= 0]
    tot = sum(o["pnl"] for o in ops); sg = sum(o["pnl"] for o in gan); sp = -sum(o["pnl"] for o in per)
    rs = [o["r"] for o in ops if o["r"] is not None]
    racha = mx = 0
    for o in ops:
        racha = racha + 1 if o["pnl"] <= 0 else 0; mx = max(mx, racha)
    acum = pico = dd = 0.0
    for o in ops:
        acum += o["pnl"]; pico = max(pico, acum); dd = max(dd, pico - acum)
    return dict(operaciones=n, ganadoras=len(gan), aciertos_pct=round(len(gan) / n * 100, 1) if n else 0,
                resultado_total=round(tot, 2), factor_beneficio=round(sg / sp, 2) if sp else None,
                ganancia_media=round(sg / len(gan), 2) if gan else 0, perdida_media=round(-sp / len(per), 2) if per else 0,
                expectativa_r=round(statistics.mean(rs), 3) if rs else None, operaciones_con_r=len(rs),
                racha_perdedora_max=mx, caida_max=round(dd, 2), sin_stop=sum(1 for o in ops if o["stop"] is None))

def por_etiqueta(ops):
    g = defaultdict(list)
    for o in ops:
        for t in o["tags"]: g[t].append(o)
    out = []
    for t, l in g.items():
        out.append(dict(etiqueta=t, veces=len(l), resultado_total=round(sum(o["pnl"] for o in l), 2),
                        perdida_total=round(sum(o["pnl"] for o in l if o["pnl"] < 0), 2),
                        aciertos_pct=round(sum(1 for o in l if o["pnl"] > 0) / len(l) * 100, 1)))
    return sorted(out, key=lambda x: x["perdida_total"])

def por_dia(ops):
    g = defaultdict(list)
    for o in ops:
        if o["fecha"]: g[o["fecha"].weekday()].append(o["pnl"])
    return [dict(dia=DIAS[d], veces=len(v), resultado_total=round(sum(v), 2)) for d, v in sorted(g.items())]

def tras_perdida(ops):
    a, b = [], []
    for prev, cur in zip(ops, ops[1:]):
        if cur["tamano"]: (a if prev["pnl"] < 0 else b).append(cur["tamano"])
    if len(a) >= 3 and len(b) >= 3:
        return dict(tamano_medio_tras_perdida=round(statistics.mean(a), 2), tamano_medio_resto=round(statistics.mean(b), 2))
    return None

def informe(path):
    ops = leer(path)
    if not ops: raise SystemExit("Error: no hay operaciones válidas.")
    ops.sort(key=lambda o: (o["fecha"] or datetime.min, o["fila"]))
    return dict(resumen=resumen(ops), errores=por_etiqueta(ops), por_dia=por_dia(ops), tras_perdida=tras_perdida(ops))

def md(r):
    s = r["resumen"]; L = ["# Revisión del diario", "", "## Resumen",
        f"- Operaciones: {s['operaciones']} · aciertos {s['aciertos_pct']} % · resultado total {s['resultado_total']}",
        f"- Ganancia media {s['ganancia_media']} · pérdida media {s['perdida_media']} · factor de beneficio {s['factor_beneficio']}",
        f"- Expectativa en R: {s['expectativa_r']} (sobre {s['operaciones_con_r']} operaciones con stop)",
        f"- Racha perdedora máxima: {s['racha_perdedora_max']} · caída máxima: {s['caida_max']}",
        f"- Operaciones sin stop: {s['sin_stop']}"]
    if s["operaciones"] < 30: L.append(f"- OJO: solo {s['operaciones']} operaciones; los patrones son indicios, no conclusiones.")
    L += ["", "## Errores repetidos (de más a menos coste)"]
    if r["errores"]:
        L += ["| Etiqueta | Veces | Pérdida acumulada | Resultado total | Aciertos |", "|---|---|---|---|---|"]
        L += [f"| {e['etiqueta']} | {e['veces']} | {e['perdida_total']} | {e['resultado_total']} | {e['aciertos_pct']} % |" for e in r["errores"]]
        L.append("Nota: una operación con varias etiquetas cuenta en cada una; no sumes esta tabla para obtener el coste total.")
    else: L.append("No hay etiquetas de error en el CSV. Etiqueta las peores operaciones y vuelve a ejecutar.")
    L += ["", "## Por día de la semana", "| Día | Operaciones | Resultado |", "|---|---|---|"]
    L += [f"| {d['dia']} | {d['veces']} | {d['resultado_total']} |" for d in r["por_dia"]]
    if r["tras_perdida"]: L += ["", "## Tamaño tras una pérdida", f"- Tras pérdida: {r['tras_perdida']['tamano_medio_tras_perdida']} · resto: {r['tras_perdida']['tamano_medio_resto']}"]
    return "\n".join(L)

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("csv"); ap.add_argument("--json", action="store_true"); a = ap.parse_args()
    r = informe(a.csv)
    print(json.dumps(r, ensure_ascii=False, indent=2) if a.json else md(r))
