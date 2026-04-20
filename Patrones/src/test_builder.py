"""
Prueba conceptual del patrón Builder para el caso MES.

Ejecución:
python test_builder.py
"""

from _bootstrap import ensure_src_path

ensure_src_path()

from builder_m import ReportDirector, StandardProductionReportBuilder


def run_builder_demo():
    builder = StandardProductionReportBuilder()
    director = ReportDirector(builder)

    standard_report = director.build_standard_shift_report(
        order_id="OP-2026-0313",
        production_line="LINE-A",
        shift="NIGHT",
        units_planned=1200,
        units_produced=1180,
        downtime_minutes=25,
        notes="Turno estable con ajuste menor en alimentacion.",
    )

    incident_report = director.build_report_with_alerts(
        order_id="OP-2026-0314",
        production_line="LINE-B",
        shift="DAY",
        units_planned=900,
        units_produced=840,
        downtime_minutes=50,
        notes="Se aplico inspeccion extra al lote final.",
        alerts=[
            "Defecto superficial detectado en lote B-17.",
            "Reproceso parcial por desviacion dimensional.",
        ],
    )

    assert standard_report.order_id == "OP-2026-0313"
    assert standard_report.quality_alerts == []
    assert incident_report.order_id == "OP-2026-0314"
    assert len(incident_report.quality_alerts) == 2

    print("Builder test conceptual: OK")
    print(standard_report)
    print(incident_report)


if __name__ == "__main__":
    run_builder_demo()
