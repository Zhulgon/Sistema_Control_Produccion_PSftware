"""
Proxy - Control de acceso a reportes MES

Proposito:
- Controlar el acceso a reportes sensibles de produccion.
- Cargar el servicio real solo cuando se necesita.
- Agregar cache y auditoria sin modificar el servicio real.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


class MESReportService(ABC):

    @abstractmethod
    def generate_oee_report(
        self,
        order_id: str,
        production_line: str,
        planned_units: int,
        produced_units: int,
        downtime_minutes: int,
    ) -> dict[str, Any]:
        pass


@dataclass(frozen=True)
class UserSession:
    username: str
    role: str
    allowed_lines: tuple[str, ...]

    def can_read_line(self, production_line: str) -> bool:
        return self.role == "admin" or production_line in self.allowed_lines

    def can_generate_reports(self) -> bool:
        return self.role in {"admin", "supervisor"}


class RealMESReportService(MESReportService):

    def __init__(self) -> None:
        self.load_message = "RealMESReportService cargado para analisis OEE."

    def generate_oee_report(
        self,
        order_id: str,
        production_line: str,
        planned_units: int,
        produced_units: int,
        downtime_minutes: int,
    ) -> dict[str, Any]:
        oee = 0.0 if planned_units <= 0 else round((produced_units / planned_units) * 100, 2)
        return {
            "order_id": order_id,
            "production_line": production_line,
            "planned_units": planned_units,
            "produced_units": produced_units,
            "downtime_minutes": downtime_minutes,
            "oee": oee,
            "status": "OK" if oee >= 85 else "REVIEW",
            "source": "real_service",
        }


class MESReportProxy(MESReportService):

    def __init__(self, session: UserSession) -> None:
        self._session = session
        self._real_service: RealMESReportService | None = None
        self._cache: dict[tuple[str, str, int, int, int], dict[str, Any]] = {}
        self._audit_log: list[str] = []

    def service_loaded(self) -> bool:
        return self._real_service is not None

    def get_audit_log(self) -> list[str]:
        return list(self._audit_log)

    def _get_real_service(self) -> RealMESReportService:
        if self._real_service is None:
            self._real_service = RealMESReportService()
            self._audit_log.append(self._real_service.load_message)
        return self._real_service

    def _authorize(self, production_line: str) -> None:
        if not self._session.can_generate_reports():
            self._audit_log.append(f"DENIED role={self._session.role} line={production_line}")
            raise PermissionError("El usuario no tiene permiso para generar reportes MES.")

        if not self._session.can_read_line(production_line):
            self._audit_log.append(f"DENIED user={self._session.username} line={production_line}")
            raise PermissionError("El usuario no tiene acceso a la linea solicitada.")

    def generate_oee_report(
        self,
        order_id: str,
        production_line: str,
        planned_units: int,
        produced_units: int,
        downtime_minutes: int,
    ) -> dict[str, Any]:
        self._authorize(production_line)
        cache_key = (order_id, production_line, planned_units, produced_units, downtime_minutes)

        if cache_key in self._cache:
            self._audit_log.append(f"CACHE_HIT order={order_id} line={production_line}")
            cached_report = dict(self._cache[cache_key])
            cached_report["source"] = "proxy_cache"
            return cached_report

        self._audit_log.append(f"AUTHORIZED user={self._session.username} order={order_id}")
        report = self._get_real_service().generate_oee_report(
            order_id,
            production_line,
            planned_units,
            produced_units,
            downtime_minutes,
        )
        self._cache[cache_key] = dict(report)
        return report


class MESReportClient:

    def __init__(self, report_service: MESReportService) -> None:
        self._report_service = report_service

    def request_shift_oee(
        self,
        order_id: str,
        production_line: str,
        planned_units: int,
        produced_units: int,
        downtime_minutes: int,
    ) -> dict[str, Any]:
        return self._report_service.generate_oee_report(
            order_id,
            production_line,
            planned_units,
            produced_units,
            downtime_minutes,
        )


def run_demo() -> dict:
    proxy = MESReportProxy(UserSession("supervisor_linea_a", "supervisor", ("LINE-A",)))
    client = MESReportClient(proxy)
    first = client.request_shift_oee("OP-2026-FUNC-PRX", "LINE-A", 600, 570, 3)
    second = client.request_shift_oee("OP-2026-FUNC-PRX", "LINE-A", 600, 570, 3)
    return {"first_report": first, "second_report": second, "audit_log": proxy.get_audit_log()}


if __name__ == "__main__":
    print(run_demo())
