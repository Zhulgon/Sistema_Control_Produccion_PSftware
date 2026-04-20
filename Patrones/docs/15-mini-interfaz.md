# Mini interfaz visual MES

## Archivo

- `src/mini_interfaz_mes.py`

## Como ejecutarla

```bash
cd Patrones/src
python mini_interfaz_mes.py
```

## Que permite hacer

1. Ingresar datos de orden:
- template (`cnc_standard` o `robot_packaging`)
- `order_id`
- `planned_units`
- `shift`
- `protocol`

2. Ejecutar el flujo funcional del MES.
3. Ver resultados en pestañas:
- `Resumen`
- `Bitacora de patrones`
- `Reporte final`
- `Mapa patron-codigo`

## Botones utiles

- `Ejemplo CNC`
- `Ejemplo Robot`
- `Reiniciar contexto`
- `Ejecutar orden`

## Relacion con el backend

La interfaz llama directamente a:
- `build_default_mes_project()`
- `execute_order(OrderExecutionRequest(...))`

del archivo `src/mes_functional_app.py`.
