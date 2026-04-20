# Estructura de `src`

## Modulos reales del proyecto

Estos archivos contienen la implementacion real por patron:

- `singleton_m.py`
- `factory_m.py`
- `abstract_factory_m.py`
- `builder_m.py`
- `adapter_m.py`
- `prototype_m.py`
- `bridge_m.py`
- `decorator_m.py`
- `composite_m.py`
- `facade_m.py`

## Integracion funcional

- `mes_functional_app.py`: integra todos los patrones en el flujo real del MES.

## Entradas para ejecutar

- `mini_interfaz_mes.py`: interfaz visual.
- `run_practica_guiada.py`: recorrido explicativo por consola.
- `run_mes_functional_demo.py`: demo rapido.

## Tests

- Carpeta: `test/`
- Ejecutar todos:

```bash
cd src/test
python test_PARCIAL.py
```

## Nota

Los archivos con nombres largos legacy fueron retirados para evitar duplicidad y confusion.
