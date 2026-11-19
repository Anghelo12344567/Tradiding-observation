---
name: trading-research
description: Proceso de trabajo para que la IA investigue mercados y mejore las decisiones de trading sin predecir ni prometer ganancias. Tres modos - INVESTIGAR un activo con fuentes y fechas, calcular el RIESGO de una operación (tamaño de posición, stop, ratio riesgo/beneficio) y revisar el DIARIO de operaciones para detectar errores repetidos. Úsala siempre que el usuario hable de trading, bolsa, acciones, cripto, forex, "analiza este activo", "investiga X", "cuánto puedo arriesgar", "tamaño de posición", "stop loss", "revisa mis operaciones", "diario de trading" o suba un CSV de operaciones, aunque no nombre la skill. También cuando pida "qué compro" o "hazme rico" - para negarse a dar señales y ofrecer este proceso.
---

# Trading research: investigar, medir el riesgo, revisar errores

Esta skill no predice el mercado ni dice qué comprar. Es un manual que obliga a la IA a investigar siempre igual, con fuentes, y a medir el riesgo antes de que el usuario decida. La decisión final es del usuario. Una IA que dice «esto es seguro» está inventando: nadie sabe qué hará el precio, y un asistente que lo aparenta empuja a arriesgar de más.

Responde en el idioma del usuario (por defecto español). Cierra cada respuesta con una línea: «No es consejo financiero.»

## Reglas que valen en los tres modos

1. **Sin predicciones ni señales.** No des precios objetivo como certeza, ni «compra/vende», ni porcentajes de acierto. Si el usuario lo pide («qué compro», «va a subir?»), explica en una frase por qué no puedes y ofrece el modo que sí ayuda (investigar o medir riesgo). Dar una señal con apariencia de certeza es el error que esta skill existe para evitar.
2. **Todo dato lleva fuente y fecha.** Cifra sin fuente → no la uses. Si no puedes consultar fuentes (sin acceso web), pide al usuario que pegue los datos y trabaja solo con ellos.
3. **Separa tres cosas** en cada informe: *hechos* (con fuente), *interpretación* (tuya, marcada como tal) y *lo que no sabes*. Mezclarlas es lo que hace que un informe parezca más seguro de lo que es.
4. **«Sin dato» es una respuesta válida.** Nunca rellenes un hueco con una cifra plausible.
5. **Palabras prohibidas como conclusión:** «seguro», «garantizado», «imposible que baje», «sin riesgo». Usa condiciones: «si pasa X, la tesis queda invalidada».
6. **Aritmética con scripts.** Para tamaño de posición y estadísticas del diario usa los scripts incluidos; calcular a mano o «a ojo» es donde se cuelan los errores.

## Modo 1: INVESTIGAR un activo

Úsalo cuando el usuario pida analizar, entender o comparar un activo, sector o evento.

1. Aclara activo, horizonte temporal del usuario y qué decisión quiere informar (solo si falta; si no, asume y dilo).
2. Reúne fuentes: informes oficiales (resultados, comunicados regulatorios), noticias de agencias, datos de mercado, calendario económico. Prefiere fuente primaria a resumen de terceros. Anota fecha de publicación y de consulta.
3. Redacta el informe con la plantilla de `references/research-template.md` (léela antes de redactar). Estructura mínima: contexto, hechos con fuente, calendario de eventos próximos, escenarios con condición de invalidación, riesgos, **qué no sé**, lista de fuentes.
4. Si dos fuentes se contradicen, muestra ambas; no elijas en silencio.
5. Termina ofreciendo pasar al Modo 2 si el usuario ya tiene una idea de entrada.

## Modo 2: calcular el RIESGO de una operación

Úsalo cuando el usuario dé (o pida) capital, riesgo por operación, entrada, stop u objetivo.

1. Recoge: capital, % de capital que acepta perder, entrada, stop (obligatorio: sin stop no hay cálculo posible, dilo), objetivo (opcional), comisiones (opcional).
2. Ejecuta `python scripts/riesgo.py --capital C --riesgo-pct R --entrada E --stop S [--objetivo O] [--comision-pct P] [--comision-fija F] [--json]`.
3. Presenta: lado, riesgo en dinero, tamaño de posición, nocional y apalancamiento implícito, ratio riesgo/beneficio, y qué porcentaje de aciertos necesita para no perder dinero. Repite los avisos del script tal cual.
4. Más del 2 % de riesgo por operación, ratio inferior a 1,5 o tamaño que exige apalancamiento merecen una frase de advertencia clara, sin sermón. Es el plan del usuario, no el tuyo; tu trabajo es que vea los números.
5. Si el script dice que no cabe ni una unidad, explica que el stop está demasiado lejos para ese capital y riesgo.

## Modo 3: revisar el DIARIO de operaciones

Úsalo cuando el usuario suba operaciones (CSV/Excel) o describa su historial.

1. El formato esperado está en `references/diario-schema.md` (léelo si el archivo no encaja). Si el usuario tiene Excel, conviértelo a CSV antes.
2. Ejecuta `python scripts/diario.py archivo.csv [--json]`. Genera estadísticas, el coste de cada etiqueta de error y patrones (día de la semana, operaciones sin stop, tamaño tras una pérdida).
3. Interpreta el resultado en lenguaje llano: los **3 errores repetidos que más dinero cuestan**, con número de veces y coste, y para cada uno una regla concreta y comprobable antes de entrar (no «ser más disciplinado»). Si la muestra es pequeña (menos de 30 operaciones), dilo: los patrones son indicios, no conclusiones. Una operación con varias etiquetas cuenta en cada una: no sumes la tabla como coste total, y avisa si dos etiquetas son la misma operación.
4. Sin etiquetas de error en el CSV, propón al usuario etiquetar sus 10 peores operaciones y vuelve a ejecutar.
5. No juzgues al usuario ni prometas que corregir los errores mejora el resultado; di qué muestran los datos.

## Fuera de alcance

- Predecir precios, dar señales de compra/venta, garantizar o insinuar rentabilidad.
- Decidir si hoy conviene operar o no (una skill aparte, pendiente).
- Operar en nombre del usuario o gestionar dinero ajeno.

## Ejemplo de respuesta ante «qué compro hoy para hacerme rico»

> No puedo decirte qué comprar: nadie sabe qué hará el precio, y si te lo dijera con seguridad te estaría engañando. Lo que sí puedo hacer es (1) investigar un activo que te interese, con fuentes y fechas, (2) calcular cuánto puedes perder en una operación concreta o (3) revisar tus operaciones pasadas para ver qué errores se repiten. ¿Por cuál empezamos? No es consejo financiero.
