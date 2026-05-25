from __future__ import annotations

from datetime import datetime
from pathlib import Path

from mes_functional_app import OrderExecutionRequest
from software_mes_queries import QueryFilters
from software_mes_service import ScalableMESProject


def main() -> None:
    db_path = Path(__file__).with_name("test_mes_software.db")
    if db_path.exists():
        db_path.unlink()

    app = ScalableMESProject(db_path=db_path)
    admin = app.authenticate("admin_mes", "AdminMES2026!")
    order_id = f"OP-TEST-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    result = app.execute_order(
        admin,
        OrderExecutionRequest(
            template_key="robot_packaging",
            order_id=order_id,
            planned_units=180,
            shift="NIGHT",
            protocol="modbus",
            operator_id="USR-QA-01",
            operator_name="Operador QA",
        ),
    )
    assert result["status"] == "OK"
    assert result["persistence"]["stored_state"] == "COMPLETED"
    assert len(result["state_history"]) == 4
    assert result["persistence"]["shift_start_at"]
    assert result["persistence"]["shift_end_at"]
    assert any(item["command"] == "EXECUTE_ORDER" for item in result["command_history"])

    filters = QueryFilters(
        order_id=order_id,
        production_line="LINE-B",
        date_from=datetime.now().date().isoformat(),
        date_to=datetime.now().date().isoformat(),
        hour_from="00:00:00",
        hour_to="23:59:59",
        limit=10,
    )
    consultations = app.generate_filtered_consultations(admin, filters)
    assert len(consultations) == 5
    assert consultations[0]["row_count"] >= 1
    assert consultations[3]["row_count"] >= 1
    assert consultations[4]["row_count"] >= 1
    assert all(item.get("batch_code") for item in consultations)
    assert all(item.get("generated_at") for item in consultations)
    assert all("Strategy" in item.get("patterns", []) for item in consultations)

    snapshot = app.dashboard_snapshot(admin)
    assert snapshot["total_orders"] >= 1
    assert snapshot["total_consultation_batches"] >= 1
    assert snapshot["recent_consultation_batches"]

    persisted = app.load_persisted_consultations(admin, limit=10)
    assert len(persisted) == 5
    assert {item["identifier"] for item in persisted} == {"SQ1", "SQ2", "SQ3", "SQ4", "SQ5"}
    assert all(item.get("batch_code") for item in persisted)

    pattern_names = {item["pattern"] for item in app.pattern_map()}
    assert {"Observer", "Strategy", "Command", "State"}.issubset(pattern_names)

    supervisor = app.authenticate("supervisor_linea_a", "SupervisorA2026!")
    try:
        app.generate_filtered_consultations(supervisor, QueryFilters(production_line="LINE-B"))
    except PermissionError:
        pass
    else:
        raise AssertionError("La consulta sobre una linea no autorizada debio fallar.")

    print("Prueba de escalamiento MES completada correctamente.")


if __name__ == "__main__":
    main()
