#!/usr/bin/env python3
"""Tamaño de posición y riesgo de una operación a partir del plan del usuario (aritmética, no consejo).

Uso:
  python riesgo.py --capital 10000 --riesgo-pct 1 --entrada 50 --stop 48.5 [--objetivo 55]
                   [--comision-pct 0.1] [--comision-fija 1] [--lote 1] [--json]
"""
import argparse, json, math, sys

def calcular(capital, riesgo_pct, entrada, stop, objetivo=None, comision_pct=0.0, comision_fija=0.0, lote=1.0):
    if capital <= 0: raise ValueError("El capital debe ser mayor que 0.")
    if not 0 < riesgo_pct <= 100: raise ValueError("El riesgo por operación debe estar entre 0 y 100 %.")
    if entrada <= 0 or stop <= 0: raise ValueError("Entrada y stop deben ser mayores que 0.")
    if entrada == stop: raise ValueError("Entrada y stop no pueden ser iguales: sin distancia al stop no hay riesgo medible.")
    if lote <= 0: raise ValueError("El lote mínimo debe ser mayor que 0.")
    lado = "largo" if stop < entrada else "corto"
    dist = abs(entrada - stop)
    riesgo_obj = capital * riesgo_pct / 100.0
    com_unit = (entrada + stop) * comision_pct / 100.0          # comisión proporcional, entrada + salida en el stop
    presupuesto = riesgo_obj - comision_fija
    avisos = []
    if presupuesto <= 0:
        raise ValueError("La comisión fija se come todo el riesgo permitido: sube el riesgo o baja la comisión.")
    unidades = math.floor((presupuesto / (dist + com_unit)) / lote) * lote
    if unidades < lote:
        unidades = 0
        avisos.append("No cabe ni una unidad con ese capital, riesgo y distancia al stop: el stop está demasiado lejos para este plan.")
    riesgo_real = unidades * (dist + com_unit) + (comision_fija if unidades else 0.0)
    nocional = unidades * entrada
    apal = nocional / capital
    res = dict(lado=lado, capital=capital, riesgo_pct=riesgo_pct, riesgo_objetivo=round(riesgo_obj, 2),
               distancia_stop=round(dist, 6), distancia_stop_pct=round(dist / entrada * 100, 3),
               unidades=unidades, riesgo_real=round(riesgo_real, 2), riesgo_real_pct=round(riesgo_real / capital * 100, 3),
               nocional=round(nocional, 2), apalancamiento_implicito=round(apal, 3))
    if objetivo is not None:
        if (lado == "largo" and objetivo <= entrada) or (lado == "corto" and objetivo >= entrada):
            raise ValueError(f"El objetivo no tiene sentido para una operación en {lado}.")
        rr = abs(objetivo - entrada) / dist
        res.update(objetivo=objetivo, ratio_riesgo_beneficio=round(rr, 2),
                   beneficio_en_objetivo=round(unidades * abs(objetivo - entrada) - com_unit * unidades - (comision_fija if unidades else 0.0), 2),
                   acierto_minimo_para_no_perder_pct=round(100.0 / (1.0 + rr), 1))
        if rr < 1.5: avisos.append(f"Ratio riesgo/beneficio {rr:.2f}: por debajo de 1,5 necesitas acertar muy a menudo.")
    if riesgo_pct > 2: avisos.append(f"Arriesgas el {riesgo_pct:g} % por operación: más del 2 % hace que una racha de pérdidas pese mucho.")
    if apal > 1: avisos.append(f"El tamaño exige apalancamiento (nocional = {apal:.2f}x el capital): una caída contra ti pesa más que el riesgo calculado si el stop no se ejecuta al precio exacto (huecos, comisiones).")
    avisos.append("El stop debe colocarse de verdad en el mercado; calcular el tamaño sin ponerlo no limita nada.")
    res["avisos"] = avisos
    return res

def texto(r):
    l = [f"Operación en {r['lado']}",
         f"Riesgo permitido: {r['riesgo_objetivo']:.2f} ({r['riesgo_pct']:g} % de {r['capital']:g})",
         f"Distancia al stop: {r['distancia_stop']:g} ({r['distancia_stop_pct']:g} % del precio de entrada)",
         f"Tamaño de posición: {r['unidades']:g} unidades",
         f"Riesgo real con ese tamaño: {r['riesgo_real']:.2f} ({r['riesgo_real_pct']:g} % del capital)",
         f"Valor de la posición: {r['nocional']:.2f} · apalancamiento implícito {r['apalancamiento_implicito']:g}x"]
    if 'objetivo' in r:
        l += [f"Objetivo {r['objetivo']:g}: ratio riesgo/beneficio {r['ratio_riesgo_beneficio']:g}, beneficio si se alcanza {r['beneficio_en_objetivo']:.2f}",
              f"Porcentaje de aciertos mínimo para no perder dinero con ese ratio: {r['acierto_minimo_para_no_perder_pct']:g} %"]
    l += ["Avisos:"] + [f"- {a}" for a in r['avisos']]
    return "\n".join(l)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--capital", type=float, required=True)
    ap.add_argument("--riesgo-pct", type=float, required=True)
    ap.add_argument("--entrada", type=float, required=True)
    ap.add_argument("--stop", type=float, required=True)
    ap.add_argument("--objetivo", type=float)
    ap.add_argument("--comision-pct", type=float, default=0.0, help="comisión proporcional por operación, en %")
    ap.add_argument("--comision-fija", type=float, default=0.0, help="comisión fija ida y vuelta")
    ap.add_argument("--lote", type=float, default=1.0, help="tamaño mínimo de contrato/lote (1 = unidades enteras)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        r = calcular(a.capital, a.riesgo_pct, a.entrada, a.stop, a.objetivo, a.comision_pct, a.comision_fija, a.lote)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr); sys.exit(2)
    print(json.dumps(r, ensure_ascii=False, indent=2) if a.json else texto(r))

if __name__ == "__main__":
    main()
