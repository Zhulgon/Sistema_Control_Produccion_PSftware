# 1. Análisis y contexto del caso (MES)

## 1.1 Descripción general

El Sistema de Control de Producción (MES - Manufacturing Execution System) es un sistema que permite gestionar y supervisar la ejecución de la producción en planta.

En el caso asignado, el sistema contempla:

- Planificación y programación de producción  
- Control de calidad y trazabilidad  
- Integración con máquinas CNC y robots  
- Análisis de OEE (Overall Equipment Effectiveness)

## 1.2 Problemas de diseño identificados

En este tipo de sistema se presentan dos problemas principales:

### A) Necesidad de coordinación central

El sistema requiere un punto único que controle:

- Programación de producción
- Estado general del sistema
- Cálculo de métricas globales (OEE)

Si existieran múltiples controladores independientes podrían generarse inconsistencias en los datos y decisiones contradictorias.

### B) Creación flexible de máquinas

El sistema integra distintos tipos de máquinas (CNC, robots, etc.).  
Si cada tipo se crea mediante condicionales repetitivos, el sistema:

- Se acopla fuertemente a clases concretas
- Se vuelve difícil de extender
- Viola el principio Open/Closed

## 1.3 Objetivo de la aplicación de patrones

Aplicar patrones de diseño para:

- Garantizar una única instancia de control central (Singleton)
- Permitir la creación flexible y extensible de máquinas (Factory Method)

## 1.4 Alcance

La implementación es conceptual y busca evidenciar la estructura de los patrones mediante:

- Análisis formal
- Diagramas UML
- Código demostrativo en Python

No se desarrolla funcionalidad real del sistema.