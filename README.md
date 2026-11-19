# Tradiding-observation: skill `trading-research`

Skill para Claude que enseña a la IA a investigar mercados con un proceso fijo. No predice precios, no da señales y no promete ganancias: es un manual para investigar siempre igual y medir el riesgo antes de decidir.

## Qué hace (3 modos)

| Modo | Qué hace |
|---|---|
| **Investigar** | Informe de un activo con hechos, fuente y fecha, calendario de eventos, escenarios con su condición de invalidación y una sección «Qué no sé». |
| **Riesgo** | Tamaño de posición, riesgo en dinero, ratio riesgo/beneficio y acierto mínimo para no perder, con `scripts/riesgo.py`. |
| **Diario** | Revisa un CSV de operaciones, saca el coste de cada error repetido y propone reglas comprobables, con `scripts/diario.py`. |

## Instalación

- **Claude Code:** copia la carpeta `trading-research/` en `~/.claude/skills/`.
- **Claude (app web o escritorio):** importa el archivo `trading-research.skill` como skill.

## Uso de los scripts (Python 3, sin dependencias)

```bash
python3 trading-research/scripts/riesgo.py --capital 10000 --riesgo-pct 1 --entrada 50 --stop 48.5 --objetivo 55
python3 trading-research/scripts/diario.py trading-research/evals/diario-errores-repetidos/files/diario.csv
```

## Contenido

- `trading-research/SKILL.md`: instrucciones de la skill.
- `trading-research/references/`: plantilla de informe y formato del diario.
- `trading-research/scripts/`: calculadora de riesgo y analizador del diario.
- `trading-research/evals/`: 4 casos de prueba. El diario de ejemplo es **sintético**.
- `trading-research.skill`: paquete instalable.

## Aviso

No es consejo financiero. Operar con dinero real conlleva riesgo de pérdida.
