from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import Any

from mes_functional_app import (
    OrderExecutionRequest,
    PatternImplementation,
    build_default_mes_project,
    pattern_implementation_map,
)
from patrones_funcionales.proxy_funcional import MESReportClient, MESReportProxy, UserSession
from software_mes_behavioral import (
    AuditRepositoryObserver,
    ConsultationStrategyCatalog,
    ExecuteOrderCommand,
    GenerateConsultationsCommand,
    MESCommandInvoker,
    NotificationObserver,
    OrderLifecycleContext,
)
from software_mes_persistence import SQLiteMESDatabase
from software_mes_queries import QueryFilters
from software_mes_security import AuthenticatedUser, AuthenticationService


def software_pattern_implementation_map() -> list[PatternImplementation]:
    base_patterns = pattern_implementation_map()
    behavioral_patterns = [
        PatternImplementation(
            pattern="State",
            objective="Controlar el ciclo de vida de la orden evitando condicionales fragiles.",
            module="src/software_mes_behavioral.py",
            key_classes="OrderLifecycleContext, CreatedState, PlannedState, DispatchedState, RunningState, CompletedState",
            usage_point="execute_order(): plan()/dispatch()/start()/complete()",
        ),
        PatternImplementation(
            pattern="Observer",
            objective="Notificar y auditar cambios de estado sin acoplar la logica central.",
            module="src/software_mes_behavioral.py",
            key_classes="OrderEventSubject, AuditRepositoryObserver, NotificationObserver",
            usage_point="execute_order(): attach()/notify() durante las transiciones",
        ),
        PatternImplementation(
            pattern="Strategy",
            objective="Construir consultas persistentes con variantes intercambiables por tipo analitico.",
            module="src/software_mes_behavioral.py",
            key_classes="ConsultationStrategy, PlanningConsultationStrategy, DispatchConsultationStrategy, CapacityConsultationStrategy, ExecutionConsultationStrategy, TraceabilityConsultationStrategy, OperatorProductivityConsultationStrategy, LineLoadConsultationStrategy, AuditActivityConsultationStrategy, StateSummaryConsultationStrategy, ShiftPerformanceConsultationStrategy",
            usage_point="generate_filtered_consultations(): strategy_catalog.build_all()",
        ),
        PatternImplementation(
            pattern="Command",
            objective="Encapsular operaciones principales del sistema para ejecutarlas de forma uniforme.",
            module="src/software_mes_behavioral.py",
            key_classes="MESCommandInvoker, ExecuteOrderCommand, GenerateConsultationsCommand",
            usage_point="execute_order()/generate_filtered_consultations(): command_invoker.run(command)",
        ),
    ]
    return base_patterns + behavioral_patterns


class ScalableMESProject:
    def __init__(self, db_path: str | Path | None = None) -> None:
        target_path = db_path or Path(__file__).with_name("mes_software.db")
        self._database = SQLiteMESDatabase(target_path)
        self._auth = AuthenticationService(self._database)
        self._project = build_default_mes_project()
        self._consultation_strategy_catalog = ConsultationStrategyCatalog()
        self._command_invoker = MESCommandInvoker()
        self._bootstrap_default_users()

    @property
    def db_path(self) -> str:
        return self._database.db_path

    def _bootstrap_default_users(self) -> None:
        defaults = [
            ("admin_mes", "AdminMES2026!", "admin", ("LINE-A", "LINE-B", "LINE-C")),
            ("supervisor_linea_a", "SupervisorA2026!", "supervisor", ("LINE-A",)),
            ("operador_linea_b", "OperadorB2026!", "operator", ("LINE-B",)),
        ]
        for username, password, role, lines in defaults:
            if not self._database.get_user(username):
                self._auth.register_user(username, password, role, lines)

    def register_user(
        self,
        username: str,
        password: str,
        role: str,
        allowed_lines: tuple[str, ...] | list[str],
    ) -> None:
        self._auth.register_user(username, password, role, allowed_lines)

    def demo_credentials(self) -> list[dict[str, str]]:
        return [
            {
                "username": "admin_mes",
                "password": "AdminMES2026!",
                "role": "admin",
                "lines": "LINE-A, LINE-B, LINE-C",
            },
            {
                "username": "supervisor_linea_a",
                "password": "SupervisorA2026!",
                "role": "supervisor",
                "lines": "LINE-A",
            },
            {
                "username": "operador_linea_b",
                "password": "OperadorB2026!",
                "role": "operator",
                "lines": "LINE-B",
            },
        ]

    def authenticate(self, username: str, password: str) -> AuthenticatedUser:
        user = self._auth.authenticate(username, password)
        self._database.save_audit_event(
            {
                "event_type": "LOGIN_OK",
                "username": user.username,
                "order_id": None,
                "production_line": None,
                "description": f"Inicio de sesion exitoso para rol={user.role}",
                "created_at": datetime.now().isoformat(timespec="seconds"),
            }
        )
        return user

    def list_templates(self) -> list[str]:
        return self._project.list_templates()

    def get_template_definition(self, key: str) -> dict[str, Any]:
        return self._project.get_template_definition(key)

    def register_template(
        self,
        template_key: str,
        template_name: str,
        machine_type: str,
        line: str,
        program: str,
        product_code: str,
        product_name: str,
        quality_checks: list[str],
        line_mode: str,
        parameters: dict[str, Any] | None = None,
    ) -> None:
        self._project.register_template(
            template_key=template_key,
            template_name=template_name,
            machine_type=machine_type,
            line=line,
            program=program,
            product_code=product_code,
            product_name=product_name,
            quality_checks=quality_checks,
            line_mode=line_mode,
            parameters=parameters,
        )

    def pattern_map(self) -> list[dict[str, Any]]:
        return [asdict(item) for item in software_pattern_implementation_map()]

    def _shift_window(self, planning_time: str, shift: str) -> tuple[str, str]:
        base_dt = datetime.fromisoformat(planning_time)
        shift_key = shift.strip().upper()
        if shift_key == "NIGHT":
            start_dt = base_dt.replace(hour=18, minute=0, second=0, microsecond=0)
            end_dt = (start_dt + timedelta(hours=12)) - timedelta(seconds=1)
        else:
            start_dt = base_dt.replace(hour=6, minute=0, second=0, microsecond=0)
            end_dt = (start_dt + timedelta(hours=12)) - timedelta(seconds=1)
        return (
            start_dt.isoformat(timespec="seconds"),
            end_dt.isoformat(timespec="seconds"),
        )

    def dashboard_snapshot(self, user: AuthenticatedUser) -> dict[str, Any]:
        order_where = []
        order_params: list[Any] = []
        if user.role != "admin":
            order_where.append("requested_by = ?")
            order_params.append(user.username)

        where_clause = f"WHERE {' AND '.join(order_where)}" if order_where else ""
        totals_row = self._database.fetchone(
            f"""
            SELECT
                COUNT(*) AS total_orders,
                COALESCE(SUM(planned_units), 0) AS planned_units_total,
                COALESCE(SUM(produced_units), 0) AS produced_units_total,
                COALESCE(SUM(downtime_minutes), 0) AS downtime_minutes_total,
                COUNT(DISTINCT production_line) AS active_lines
            FROM orders
            {where_clause}
            """,
            tuple(order_params),
        ) or {}

        recent_orders = self._database.fetchall(
            f"""
            SELECT
                order_id, product_code, production_line, shift, protocol,
                planned_units, produced_units, state, created_at, shift_start_at,
                shift_end_at, completed_at, requested_by
            FROM orders
            {where_clause}
            ORDER BY datetime(completed_at) DESC, datetime(created_at) DESC
            LIMIT 8
            """,
            tuple(order_params),
        )

        oee_row = self._database.fetchone(
            f"""
            SELECT ROUND(AVG((produced_units * 100.0) / NULLIF(planned_units, 0)), 2) AS average_oee
            FROM orders
            {where_clause}
            """,
            tuple(order_params),
        ) or {}

        audits = self._database.fetchall(
            f"""
            SELECT event_type, username, order_id, production_line, description, created_at
            FROM audit_events
            {"WHERE username = ?" if user.role != "admin" else ""}
            ORDER BY datetime(created_at) DESC
            LIMIT 6
            """,
            (user.username,) if user.role != "admin" else (),
        )

        consultation_batches = self._database.fetchall(
            f"""
            SELECT batch_code, username, created_at, total_queries, total_rows, filters_json
            FROM consultation_batches
            {"WHERE username = ?" if user.role != "admin" else ""}
            ORDER BY datetime(created_at) DESC
            LIMIT 6
            """,
            (user.username,) if user.role != "admin" else (),
        )
        consultation_totals = self._database.fetchone(
            f"""
            SELECT COUNT(*) AS total_consultation_batches, COALESCE(SUM(total_rows), 0) AS consultation_rows_total
            FROM consultation_batches
            {"WHERE username = ?" if user.role != "admin" else ""}
            """,
            (user.username,) if user.role != "admin" else (),
        ) or {}

        totals_row["average_oee"] = oee_row.get("average_oee") or 0.0
        totals_row["total_consultation_batches"] = consultation_totals.get("total_consultation_batches", 0)
        totals_row["consultation_rows_total"] = consultation_totals.get("consultation_rows_total", 0)
        totals_row["recent_orders"] = recent_orders
        totals_row["recent_audits"] = audits
        totals_row["recent_consultation_batches"] = consultation_batches
        return totals_row

    def _set_proxy_session(self, user: AuthenticatedUser) -> None:
        proxy = MESReportProxy(
            UserSession(
                username=user.username,
                role=user.role,
                allowed_lines=user.allowed_lines,
            )
        )
        self._project._report_proxy = proxy
        self._project._report_client = MESReportClient(proxy)

    def _persist_telemetry(
        self,
        order_id: str,
        production_line: str,
        machine_type: str,
        protocol: str,
        quality_rule: str,
        produced_units: int,
        total_events: int,
        base_time: str,
    ) -> None:
        if total_events <= 0:
            return
        base_dt = datetime.fromisoformat(base_time)
        rows = []
        units_per_event = max(1, produced_units // total_events)
        for minute in range(1, total_events + 1):
            rows.append(
                {
                    "order_id": order_id,
                    "production_line": production_line,
                    "event_minute": minute,
                    "units": min(produced_units, units_per_event * minute),
                    "machine_type": machine_type.upper(),
                    "protocol": protocol.lower(),
                    "quality_rule": quality_rule,
                    "created_at": (base_dt + timedelta(minutes=minute)).isoformat(timespec="seconds"),
                }
            )
        self._database.save_telemetry_events(rows)

    def _execute_order_workflow(self, user: AuthenticatedUser, request: OrderExecutionRequest) -> dict[str, Any]:
        if not user.can_manage_orders():
            raise PermissionError("El usuario autenticado no puede gestionar ordenes.")

        template = self._project.get_template_definition(request.template_key)
        production_line = str(template["line"]).upper()
        if not user.can_read_line(production_line):
            raise PermissionError("El usuario no tiene permisos sobre la linea seleccionada.")

        lifecycle = OrderLifecycleContext(request.order_id, production_line)
        notification_observer = NotificationObserver()
        lifecycle.attach(AuditRepositoryObserver(self._database))
        lifecycle.attach(notification_observer)

        lifecycle.plan("Orden registrada en la capa persistente.", user.username)
        lifecycle.dispatch("Orden autorizada para despacho tecnico.", user.username)
        lifecycle.start("Orden en ejecucion sobre la linea productiva.", user.username)

        self._set_proxy_session(user)
        result = self._project.execute_order(request)
        if result.get("status") != "OK":
            raise RuntimeError(result.get("message", "La orden no pudo ejecutarse correctamente."))

        lifecycle.complete("Orden cerrada y consolidada con persistencia.", user.username)

        final_report = result.get("final_report", {})
        quality_checks = template.get("quality_checks", [])
        quality_rule = quality_checks[0] if quality_checks else "standard"
        history = lifecycle.history()
        planning_time = next(item["changed_at"] for item in history if item["to_state"] == "PLANNED")
        dispatch_time = next(item["changed_at"] for item in history if item["to_state"] == "DISPATCHED")
        completed_time = next(item["changed_at"] for item in history if item["to_state"] == "COMPLETED")
        shift_start_at, shift_end_at = self._shift_window(planning_time, request.shift)

        self._database.save_order(
            {
                "order_id": request.order_id,
                "template_key": request.template_key,
                "template_name": str(template["template_name"]),
                "product_code": str(template["product_code"]),
                "product_name": str(template["product_name"]),
                "machine_type": str(template["machine_type"]).lower(),
                "production_line": production_line,
                "line_mode": str(template["line_mode"]).lower(),
                "shift": request.shift.upper(),
                "protocol": request.protocol.lower(),
                "planned_units": int(request.planned_units),
                "produced_units": int(final_report.get("units_produced", request.planned_units)),
                "downtime_minutes": int(final_report.get("downtime_minutes", 0)),
                "operator_id": request.operator_id,
                "operator_name": request.operator_name,
                "requested_by": user.username,
                "state": lifecycle.current_state,
                "quality_rule": str(quality_rule),
                "created_at": planning_time,
                "shift_start_at": shift_start_at,
                "shift_end_at": shift_end_at,
                "dispatch_at": dispatch_time,
                "completed_at": completed_time,
            }
        )
        self._database.save_order_history(history)

        telemetry_summary = result.get("telemetry_summary", {})
        self._persist_telemetry(
            order_id=request.order_id,
            production_line=production_line,
            machine_type=str(template["machine_type"]),
            protocol=request.protocol,
            quality_rule=str(quality_rule),
            produced_units=int(final_report.get("units_produced", request.planned_units)),
            total_events=int(telemetry_summary.get("total_events", 0)),
            base_time=planning_time,
        )

        for entry in result.get("proxy_audit_log", []):
            self._database.save_audit_event(
                {
                    "event_type": "PROXY_AUDIT",
                    "username": user.username,
                    "order_id": request.order_id,
                    "production_line": production_line,
                    "description": entry,
                    "created_at": completed_time,
                }
            )

        result["state_history"] = history
        result["observer_notifications"] = notification_observer.messages()
        result["persistence"] = {
            "db_path": self.db_path,
            "stored_order_id": request.order_id,
            "stored_state": lifecycle.current_state,
            "shift_start_at": shift_start_at,
            "shift_end_at": shift_end_at,
        }
        result["implementation_map"] = [asdict(item) for item in software_pattern_implementation_map()]
        return result

    def execute_order(self, user: AuthenticatedUser, request: OrderExecutionRequest) -> dict[str, Any]:
        command = ExecuteOrderCommand(self._execute_order_workflow, user, request)
        result = self._command_invoker.run(command)
        result["command_history"] = self._command_invoker.history()
        return result

    def _store_consultation_batch(
        self,
        user: AuthenticatedUser,
        filters: QueryFilters,
        consultations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        created_at = datetime.now().isoformat(timespec="seconds")
        batch_code = f"QRY-{datetime.now().strftime('%Y%m%d%H%M%S%f')}-{user.username.upper()}"
        total_rows = sum(int(item.get("row_count", 0)) for item in consultations)
        self._database.save_consultation_batch(
            {
                "batch_code": batch_code,
                "username": user.username,
                "created_at": created_at,
                "filters_json": json.dumps(asdict(filters), ensure_ascii=False),
                "total_queries": len(consultations),
                "total_rows": total_rows,
            }
        )
        rows = []
        for consultation in consultations:
            rows.append(
                {
                    "batch_code": batch_code,
                    "consultation_identifier": consultation["identifier"],
                    "title": consultation["title"],
                    "suggested_query": consultation["suggested_query"],
                    "query_params_json": json.dumps(consultation["query_params"], ensure_ascii=False),
                    "filters_json": json.dumps(consultation["filters"], ensure_ascii=False),
                    "patterns_json": json.dumps(consultation["patterns"], ensure_ascii=False),
                    "row_count": int(consultation["row_count"]),
                    "sample_result_json": json.dumps(consultation["sample_result"], ensure_ascii=False),
                    "created_at": created_at,
                }
            )
        self._database.save_consultation_results(rows)
        return {
            "batch_code": batch_code,
            "created_at": created_at,
            "total_queries": len(consultations),
            "total_rows": total_rows,
        }

    def _consultation_payload(
        self,
        identifier: str,
        title: str,
        objective: str,
        business_question: str,
        query: str,
        params: tuple[Any, ...],
        filters: QueryFilters,
        patterns: list[str],
        rows: list[dict[str, Any]],
    ) -> dict[str, Any]:
        pattern_details = {
            item.pattern: asdict(item)
            for item in software_pattern_implementation_map()
        }
        applied_filters = []
        for key, value in asdict(filters).items():
            if value not in (None, "", []):
                applied_filters.append(f"{key}={value}")

        return {
            "identifier": identifier,
            "title": title,
            "objective": objective,
            "business_question": business_question,
            "suggested_query": query.strip(),
            "query_params": list(params),
            "filters": applied_filters,
            "patterns": patterns,
            "pattern_details": [pattern_details[name] for name in patterns if name in pattern_details],
            "row_count": len(rows),
            "sample_result": rows[:3],
        }

    def _consultation_metadata_map(self) -> dict[str, dict[str, str]]:
        return {
            "SQ1": {
                "objective": "Visualizar la demanda operativa registrada por orden, linea, turno y producto para respaldar la planificacion comercial.",
                "business_question": "Que ordenes y productos concentraron la demanda confirmada en el periodo consultado?",
            },
            "SQ2": {
                "objective": "Evidenciar como las ordenes se despacharon y que protocolos industriales soporta el sistema en la operacion real.",
                "business_question": "Que lineas, maquinas y protocolos se utilizaron para integrar la ejecucion de las ordenes?",
            },
            "SQ3": {
                "objective": "Comparar unidades comprometidas contra capacidad disponible para justificar decisiones de balanceo o expansion.",
                "business_question": "La demanda registrada presiona la capacidad disponible de la planta o de una linea especifica?",
            },
            "SQ4": {
                "objective": "Medir cumplimiento del plan, tiempos de parada y eficiencia real de la ejecucion.",
                "business_question": "Que tan bien se cumplio el plan de produccion y con que nivel de eficiencia opero cada orden?",
            },
            "SQ5": {
                "objective": "Consolidar eventos, historial y auditoria para demostrar trazabilidad y cumplimiento operativo.",
                "business_question": "Que evidencia deja el sistema para rastrear una orden de punta a punta?",
            },
            "SQ6": {
                "objective": "Comparar aporte operativo por operador segun ordenes cerradas, volumen producido y eficiencia.",
                "business_question": "Que operadores entregan mejor productividad y donde hay oportunidad de mejora?",
            },
            "SQ7": {
                "objective": "Mostrar como se distribuye la demanda entre lineas para balancear carga y priorizar recursos.",
                "business_question": "Que lineas concentran mas trabajo y como se esta utilizando la capacidad instalada?",
            },
            "SQ8": {
                "objective": "Rastrear accesos y acciones relevantes para reforzar confianza, control y gobierno operativo.",
                "business_question": "Que usuarios, ordenes o lineas presentan actividad auditada relevante en el periodo?",
            },
            "SQ9": {
                "objective": "Comparar volumen, cumplimiento y eficiencia por producto para priorizar el portafolio operativo.",
                "business_question": "Que productos mueven mas volumen y cuales presentan peor eficiencia o mayor desviacion?",
            },
            "SQ10": {
                "objective": "Comparar rendimiento entre turnos usando volumen producido, paradas y eficiencia promedio.",
                "business_question": "Que diferencias operativas hay entre DAY y NIGHT y donde conviene intervenir?",
            },
        }

    def _generate_filtered_consultations_workflow(
        self,
        user: AuthenticatedUser,
        filters: QueryFilters | dict[str, Any],
    ) -> list[dict[str, Any]]:
        normalized_filters = filters if isinstance(filters, QueryFilters) else QueryFilters(**filters)
        if normalized_filters.production_line and not user.can_read_line(normalized_filters.production_line):
            raise PermissionError("El usuario no tiene acceso para consultar esa linea.")

        if not normalized_filters.requested_by and user.role != "admin":
            normalized_filters.requested_by = user.username

        definitions = self._consultation_strategy_catalog.build_all(
            self._database,
            normalized_filters,
            self._project._capacity_service.calculate_total_units(),
        )
        consultations = [
            self._consultation_payload(
                identifier=definition.identifier,
                title=definition.title,
                objective=definition.objective,
                business_question=definition.business_question,
                query=definition.query,
                params=definition.params,
                filters=normalized_filters,
                patterns=definition.patterns,
                rows=definition.rows,
            )
            for definition in definitions
        ]
        batch_info = self._store_consultation_batch(user, normalized_filters, consultations)
        for item in consultations:
            item["batch_code"] = batch_info["batch_code"]
            item["generated_at"] = batch_info["created_at"]
            item["generated_by_command"] = "GENERATE_CONSULTATIONS"
        return consultations

    def generate_filtered_consultations(
        self,
        user: AuthenticatedUser,
        filters: QueryFilters | dict[str, Any],
    ) -> list[dict[str, Any]]:
        command = GenerateConsultationsCommand(self._generate_filtered_consultations_workflow, user, filters)
        return self._command_invoker.run(command)

    def load_persisted_consultations(
        self,
        user: AuthenticatedUser,
        limit: int = 25,
    ) -> list[dict[str, Any]]:
        params: list[Any] = []
        where_clause = ""
        if user.role != "admin":
            where_clause = "WHERE cb.username = ?"
            params.append(user.username)

        rows = self._database.fetchall(
            f"""
            SELECT
                cr.consultation_identifier,
                cr.title,
                cr.suggested_query,
                cr.query_params_json,
                cr.filters_json,
                cr.patterns_json,
                cr.row_count,
                cr.sample_result_json,
                cr.created_at,
                cb.batch_code,
                cb.username,
                cb.filters_json AS batch_filters_json
            FROM consultation_results cr
            INNER JOIN consultation_batches cb ON cb.batch_code = cr.batch_code
            {where_clause}
            ORDER BY datetime(cr.created_at) DESC, cr.batch_code DESC, cr.consultation_identifier ASC
            LIMIT ?
            """,
            tuple(params + [limit]),
        )

        metadata_map = self._consultation_metadata_map()
        pattern_details = {
            item.pattern: asdict(item)
            for item in software_pattern_implementation_map()
        }
        consultations: list[dict[str, Any]] = []
        for row in rows:
            metadata = metadata_map.get(
                row["consultation_identifier"],
                {
                    "objective": "Consulta persistente recuperada desde la base de datos.",
                    "business_question": "¿Que informacion quedo almacenada en la ejecucion historica?",
                },
            )
            patterns = json.loads(row["patterns_json"])
            consultations.append(
                {
                    "identifier": row["consultation_identifier"],
                    "title": row["title"],
                    "objective": metadata["objective"],
                    "business_question": metadata["business_question"],
                    "suggested_query": row["suggested_query"],
                    "query_params": json.loads(row["query_params_json"]),
                    "filters": json.loads(row["filters_json"]),
                    "patterns": patterns,
                    "pattern_details": [pattern_details[name] for name in patterns if name in pattern_details],
                    "row_count": int(row["row_count"]),
                    "sample_result": json.loads(row["sample_result_json"]),
                    "batch_code": row["batch_code"],
                    "generated_at": row["created_at"],
                    "generated_by": row["username"],
                    "persisted_filters": json.loads(row["batch_filters_json"]),
                }
            )
        return consultations


def run_software_demo() -> dict[str, Any]:
    app = ScalableMESProject()
    user = app.authenticate("admin_mes", "AdminMES2026!")
    order_id = f"OP-SW-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    result = app.execute_order(
        user,
        OrderExecutionRequest(
            template_key="cnc_standard",
            order_id=order_id,
            planned_units=420,
            shift="DAY",
            protocol="opcua",
            operator_id="USR-SW-01",
            operator_name="Supervisor Software",
        ),
    )
    consultations = app.generate_filtered_consultations(
        user,
        QueryFilters(
            order_id=order_id,
            production_line="LINE-A",
            date_from=datetime.now().date().isoformat(),
            date_to=datetime.now().date().isoformat(),
            hour_from="00:00:00",
            hour_to="23:59:59",
        ),
    )
    return {
        "order_id": order_id,
        "status": result["status"],
        "db_path": app.db_path,
        "consultation_rows": {item["identifier"]: item["row_count"] for item in consultations},
    }


if __name__ == "__main__":
    print(run_software_demo())
