"""
Prueba conceptual del patron Proxy para el caso MES.

Ejecucion:
python test_proxy.py
"""

from pathlib import Path
import sys

PATTERN_DIR = Path(__file__).resolve().parents[1] / "patrones"
if str(PATTERN_DIR) not in sys.path:
    sys.path.insert(0, str(PATTERN_DIR))

from proxy_m import MESReportClient, MESReportProxy, UserSession


def run_proxy_test():
    session = UserSession(
        username="supervisor_linea_a",
        role="supervisor",
        allowed_lines=("LINE-A",),
    )
    proxy = MESReportProxy(session)
    client = MESReportClient(proxy)

    assert proxy.service_loaded() is False

    report = client.request_shift_oee("OP-2026-1201", "LINE-A", 500, 470, 12)
    cached_report = client.request_shift_oee("OP-2026-1201", "LINE-A", 500, 470, 12)

    assert proxy.service_loaded() is True
    assert report["oee"] == 94.0
    assert report["source"] == "real_service"
    assert cached_report["source"] == "proxy_cache"
    assert any("AUTHORIZED" in entry for entry in proxy.get_audit_log())
    assert any("CACHE_HIT" in entry for entry in proxy.get_audit_log())

    print("Proxy test conceptual: OK")
    print(report)
    print(cached_report)
    print(proxy.get_audit_log())


if __name__ == "__main__":
    run_proxy_test()
