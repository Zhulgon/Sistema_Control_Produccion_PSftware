# Patrones_Software

Repositorio de la asignatura Patrones de Software (Ing. de Sistemas).

## Descripcion breve

Caso academico: Sistema de Control de Produccion (MES), evolucionado hacia una base de software con persistencia, usuarios, seguridad minima y consultas filtradas.

## Integrantes

- Juan Sebastian Rubiano Romero
- Angie Lucero Vargas Amado

## Punto de entrada principal

La interfaz principal del proyecto es la nueva aplicacion:

- `main.py`

Tambien puede ejecutarse directamente desde:

- `Patrones/CODIGO/UI_MES_Software_Pro.py`

## Ejecucion

Desde la raiz del repositorio:

```powershell
python main.py
```

## Credenciales demo

- `admin_mes` / `AdminMES2026!`
- `supervisor_linea_a` / `SupervisorA2026!`
- `operador_linea_b` / `OperadorB2026!`

## Componentes principales

- `Patrones/CODIGO/UI_MES_Software_Pro.py`: interfaz profesional principal.
- `Patrones/CODIGO/software_mes_service.py`: capa de aplicacion conectada a la UI.
- `Patrones/CODIGO/software_mes_persistence.py`: persistencia SQLite.
- `Patrones/CODIGO/software_mes_security.py`: autenticacion y control minimo de acceso.
- `Patrones/CODIGO/software_mes_behavioral.py`: patrones `State` y `Observer`.
- `Patrones/CODIGO/software_mes_queries.py`: consultas filtradas por fecha, hora y contexto operativo.

## Alcance del proyecto

Para una descripcion clara del alcance y fuera de alcance:

- `Patrones/docs/00-alcance-proyecto.md`

## Nota

La interfaz `Patrones/CODIGO/UI_MES_Proyecto.py` se conserva como referencia de la fase funcional anterior, pero la interfaz recomendada para demostracion y sustentacion es la nueva `UI_MES_Software_Pro.py`.
