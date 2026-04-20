# Proyecto MES - Patrones de Software

## Estado del proyecto

Este repositorio tiene dos fases:

- Fase conceptual: analisis y demos por patron.
- Fase funcional: flujo MES end-to-end implementado y verificable.

## Alcance funcional real (fase actual)

Se implementa de forma ejecutable:
- Inicio de orden de produccion.
- Despacho de orden por protocolo (OPCUA/Modbus).
- Integracion con gateway legacy.
- Cierre de orden con reporte final enriquecido.
- Consolidacion de metricas globales y capacidad de planta.

No se implementa:
- Integracion fisica con maquinaria real.
- Base de datos o interfaz web productiva.

## Donde ver cada patron en codigo

Ver el mapa claro en:
- `docs/14-mapa-implementacion-patrones.md`

Integracion principal:
- `src/mes_functional_app.py`

## Ejecucion recomendada (practica guiada)

Desde `Patrones/src`:

```bash
python run_practica_guiada.py
```

## Mini interfaz visual (desktop)

Desde `Patrones/src`:

```bash
python mini_interfaz_mes.py
```

Guia:
- `docs/15-mini-interfaz.md`

## Ejecucion de pruebas

Desde `Patrones/src`:

```bash
python test_PARCIAL.py
```

Incluye pruebas conceptuales por patron y prueba funcional integrada (`test_mes_functional.py`).

## UML funcional

- `docs/diagrams/functional-overview.puml`
- `docs/diagrams/functional-order-sequence.puml`

## Contexto academico

Trabajo realizado para la asignatura Patrones de Software (UTS).
