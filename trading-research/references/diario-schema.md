# Formato del diario de operaciones (CSV)

Una fila por operación cerrada. Cabecera en la primera línea. Separador coma o punto y coma. Decimales con punto o coma.

| Columna (alias aceptados) | Obligatoria | Ejemplo | Notas |
|---|---|---|---|
| fecha (date) | sí | 2025-03-14 o 14/03/2025 | fecha de cierre |
| activo (symbol, ticker) | sí | AAPL | |
| lado (side) | sí | largo / corto (long / short, buy / sell) | |
| entrada (entry) | sí | 50,00 | precio |
| salida (exit) | sí | 51,20 | precio |
| stop | recomendada | 48,50 | sin stop no se calcula R y la operación cuenta como «sin stop» |
| tamano (size, cantidad) | recomendada | 66 | unidades |
| resultado (pnl) | opcional | 79,2 | si falta se calcula con entrada/salida/tamaño |
| comision (fees) | opcional | 1,5 | suma al coste |
| errores (tags, etiquetas) | muy recomendada | sin-stop;fomo | etiquetas separadas por `;` o `,`, vacío si la operación siguió el plan |
| notas | opcional | | texto libre, no se analiza |

## Etiquetas de error habituales (sugeridas, no obligatorias)
`sin-stop`, `moví-stop`, `fomo`, `venganza`, `sobreoperar`, `tamaño-excesivo`, `salida-temprana`, `contra-plan`, `noticia-no-revisada`.

Usa siempre las mismas palabras: el script cuenta etiquetas idénticas.
