# Fase funcional del proyecto MES

## 1. Contexto

Este documento extiende el trabajo conceptual del archivo `PARCIAL_PATRONES_Documento_General.docx`.
La fase previa demostro patrones de forma aislada. La fase actual integra esos patrones en un
flujo funcional de orden de produccion.

## 2. Alcance inicial vs alcance funcional

### 2.1 Alcance inicial (fase conceptual)

- UML por patron.
- Codigo demostrativo por modulo.
- Pruebas unitarias conceptuales.
- Sin orquestacion completa de orden end-to-end.

### 2.2 Alcance funcional actual

- Flujo integrado para ejecutar una orden completa:
  - inicio de orden
  - despacho a linea
  - sincronizacion legacy
  - cierre y reporte final
- Trazabilidad de patrones aplicados en cada ejecucion.
- Prueba funcional integrada (`test_mes_functional.py`).
- Demo ejecutable (`run_mes_functional_demo.py`).

## 3. Arquitectura funcional implementada

Archivo principal: `src/mes_functional_app.py`

Entradas:
- `template_key`
- `order_id`
- `planned_units`
- `shift`
- `protocol`

Salidas:
- Estado de ejecucion
- Resultado de despacho
- Confirmacion de integracion legacy
- Reporte final enriquecido
- Resumen global del controlador MES

## 4. Patrones implementados en el flujo real

1. Singleton: `MESController` centraliza estado y metricas globales.
2. Factory Method: crea maquinas concretas (`CNCFactory`, `RobotFactory`).
3. Abstract Factory: crea familias compatibles por tipo de linea.
4. Builder: construye `ProductionReport` paso a paso.
5. Adapter: traduce formato moderno al gateway legacy.
6. Prototype: clona plantillas de orden desde un registro.
7. Bridge: separa tipo de orden y protocolo de comunicacion.
8. Decorator: agrega calidad, trazabilidad y OEE al reporte final.
9. Composite: calcula capacidad total de planta por arbol jerarquico.
10. Facade: simplifica el arranque de orden para el cliente.

## 5. Evidencia de funcionamiento

Ejecucion de pruebas:

```bash
cd Patrones/src
python test_PARCIAL.py
```

Ejecucion del demo:

```bash
cd Patrones/src
python run_mes_functional_demo.py
```

## 6. UML funcional

- `docs/diagrams/functional-overview.puml`
- `docs/diagrams/functional-order-sequence.puml`

## 7. Resultado

El proyecto conserva la logica academica original y escala a una implementacion funcional
coherente, verificable y ejecutable de punta a punta.
