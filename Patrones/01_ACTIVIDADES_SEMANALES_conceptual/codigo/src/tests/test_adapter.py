"""
Prueba conceptual del patron Adapter para el caso MES.

Ejecucion:
python test_adapter.py
"""

from pathlib import Path
import sys

PATTERN_DIR = Path(__file__).resolve().parents[1] / "patrones"
if str(PATTERN_DIR) not in sys.path:
    sys.path.insert(0, str(PATTERN_DIR))

from adapter_m import LegacyMachineAdapter, LegacyMachineGateway, MESProductionClient


def run_adapter_test():
    legacy_gateway = LegacyMachineGateway()
    adapter = LegacyMachineAdapter(legacy_gateway)
    client = MESProductionClient(adapter)

    result = client.close_partial_report(
        order_id="OP-2026-0701",
        production_line="line-a",
        units=320,
    )

    assert "LEGACY_OK" in result
    assert "order_ref=OP20260701" in result
    assert "line=LINE_A" in result
    assert "qty=320" in result

    print("Adapter test conceptual: OK")
    print(result)


if __name__ == "__main__":
    run_adapter_test()
