from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Callable

from software_mes_persistence import SQLiteMESDatabase
from software_mes_queries import (
    build_audit_activity_query,
    QueryFilters,
    build_capacity_query,
    build_dispatch_query,
    build_execution_query,
    build_line_load_query,
    build_operator_productivity_query,
    build_planning_query,
    build_product_performance_query,
    build_shift_performance_query,
    build_traceability_query,
)


@dataclass
class StateTransitionRecord:
    order_id: str
    from_state: str
    to_state: str
    changed_at: str
    note: str
    changed_by: str


class OrderObserver(ABC):
    @abstractmethod
    def update(self, event: dict[str, Any]) -> None:
        pass


class OrderEventSubject:
    def __init__(self) -> None:
        self._observers: list[OrderObserver] = []

    def attach(self, observer: OrderObserver) -> None:
        self._observers.append(observer)

    def notify(self, event: dict[str, Any]) -> None:
        for observer in self._observers:
            observer.update(event)


class OrderState(ABC):
    name = "UNDEFINED"

    def plan(self, context: "OrderLifecycleContext", note: str, changed_by: str) -> None:
        raise ValueError(f"No es posible planificar desde el estado {self.name}.")

    def dispatch(self, context: "OrderLifecycleContext", note: str, changed_by: str) -> None:
        raise ValueError(f"No es posible despachar desde el estado {self.name}.")

    def start(self, context: "OrderLifecycleContext", note: str, changed_by: str) -> None:
        raise ValueError(f"No es posible iniciar desde el estado {self.name}.")

    def complete(self, context: "OrderLifecycleContext", note: str, changed_by: str) -> None:
        raise ValueError(f"No es posible completar desde el estado {self.name}.")


class CreatedState(OrderState):
    name = "CREATED"

    def plan(self, context: "OrderLifecycleContext", note: str, changed_by: str) -> None:
        context.transition_to(PlannedState(), note, changed_by)


class PlannedState(OrderState):
    name = "PLANNED"

    def dispatch(self, context: "OrderLifecycleContext", note: str, changed_by: str) -> None:
        context.transition_to(DispatchedState(), note, changed_by)


class DispatchedState(OrderState):
    name = "DISPATCHED"

    def start(self, context: "OrderLifecycleContext", note: str, changed_by: str) -> None:
        context.transition_to(RunningState(), note, changed_by)


class RunningState(OrderState):
    name = "RUNNING"

    def complete(self, context: "OrderLifecycleContext", note: str, changed_by: str) -> None:
        context.transition_to(CompletedState(), note, changed_by)


class CompletedState(OrderState):
    name = "COMPLETED"


class OrderLifecycleContext:
    def __init__(self, order_id: str, production_line: str) -> None:
        self.order_id = order_id
        self.production_line = production_line
        self._subject = OrderEventSubject()
        self._state: OrderState = CreatedState()
        self._history: list[StateTransitionRecord] = []

    @property
    def current_state(self) -> str:
        return self._state.name

    def attach(self, observer: OrderObserver) -> None:
        self._subject.attach(observer)

    def history(self) -> list[dict[str, Any]]:
        return [asdict(item) for item in self._history]

    def transition_to(self, next_state: OrderState, note: str, changed_by: str) -> None:
        transition = StateTransitionRecord(
            order_id=self.order_id,
            from_state=self._state.name,
            to_state=next_state.name,
            changed_at=datetime.now().isoformat(timespec="seconds"),
            note=note,
            changed_by=changed_by,
        )
        self._state = next_state
        self._history.append(transition)
        self._subject.notify({**asdict(transition), "production_line": self.production_line})

    def plan(self, note: str, changed_by: str) -> None:
        self._state.plan(self, note, changed_by)

    def dispatch(self, note: str, changed_by: str) -> None:
        self._state.dispatch(self, note, changed_by)

    def start(self, note: str, changed_by: str) -> None:
        self._state.start(self, note, changed_by)

    def complete(self, note: str, changed_by: str) -> None:
        self._state.complete(self, note, changed_by)


class AuditRepositoryObserver(OrderObserver):
    def __init__(self, database: SQLiteMESDatabase) -> None:
        self._database = database

    def update(self, event: dict[str, Any]) -> None:
        self._database.save_audit_event(
            {
                "event_type": "STATE_TRANSITION",
                "username": event["changed_by"],
                "order_id": event["order_id"],
                "production_line": event["production_line"],
                "description": (
                    f"{event['from_state']} -> {event['to_state']} | "
                    f"{event['note']}"
                ),
                "created_at": event["changed_at"],
            }
        )


class NotificationObserver(OrderObserver):
    def __init__(self) -> None:
        self._messages: list[str] = []

    def update(self, event: dict[str, Any]) -> None:
        self._messages.append(
            f"{event['order_id']}: {event['from_state']} -> {event['to_state']} "
            f"({event['production_line']})"
        )

    def messages(self) -> list[str]:
        return list(self._messages)


@dataclass
class ConsultationDefinition:
    identifier: str
    title: str
    objective: str
    business_question: str
    query: str
    params: tuple[Any, ...]
    patterns: list[str]
    rows: list[dict[str, Any]]


class ConsultationStrategy(ABC):
    identifier = "UNDEFINED"
    title = ""
    objective = ""
    business_question = ""
    patterns: list[str] = []

    @abstractmethod
    def build(
        self,
        database: SQLiteMESDatabase,
        filters: QueryFilters,
        plant_capacity_units: int,
    ) -> ConsultationDefinition:
        pass


class PlanningConsultationStrategy(ConsultationStrategy):
    identifier = "SQ1"
    title = "Demanda confirmada por orden y contexto"
    objective = "Visualizar la demanda operativa registrada por orden, linea, turno y producto para respaldar la planificacion comercial."
    business_question = "Que ordenes y productos concentraron la demanda confirmada en el periodo consultado?"
    patterns = ["Prototype", "Facade", "Singleton", "State", "Strategy"]

    def build(
        self,
        database: SQLiteMESDatabase,
        filters: QueryFilters,
        plant_capacity_units: int,
    ) -> ConsultationDefinition:
        query, params = build_planning_query(filters)
        return ConsultationDefinition(
            identifier=self.identifier,
            title=self.title,
            objective=self.objective,
            business_question=self.business_question,
            query=query,
            params=params,
            patterns=list(self.patterns),
            rows=database.fetchall(query, params),
        )


class DispatchConsultationStrategy(ConsultationStrategy):
    identifier = "SQ2"
    title = "Integracion operativa por protocolo"
    objective = "Evidenciar como las ordenes se despacharon y que protocolos industriales soporta el sistema en la operacion real."
    business_question = "Que lineas, maquinas y protocolos se utilizaron para integrar la ejecucion de las ordenes?"
    patterns = ["Abstract Factory", "Factory Method", "Bridge", "Observer", "Strategy"]

    def build(
        self,
        database: SQLiteMESDatabase,
        filters: QueryFilters,
        plant_capacity_units: int,
    ) -> ConsultationDefinition:
        query, params = build_dispatch_query(filters)
        return ConsultationDefinition(
            identifier=self.identifier,
            title=self.title,
            objective=self.objective,
            business_question=self.business_question,
            query=query,
            params=params,
            patterns=list(self.patterns),
            rows=database.fetchall(query, params),
        )


class CapacityConsultationStrategy(ConsultationStrategy):
    identifier = "SQ3"
    title = "Capacidad disponible vs carga comprometida"
    objective = "Comparar unidades comprometidas contra capacidad disponible para justificar decisiones de balanceo o expansion."
    business_question = "La demanda registrada presiona la capacidad disponible de la planta o de una linea especifica?"
    patterns = ["Composite", "Builder", "Singleton", "Strategy"]

    def build(
        self,
        database: SQLiteMESDatabase,
        filters: QueryFilters,
        plant_capacity_units: int,
    ) -> ConsultationDefinition:
        query, params = build_capacity_query(filters, plant_capacity_units)
        return ConsultationDefinition(
            identifier=self.identifier,
            title=self.title,
            objective=self.objective,
            business_question=self.business_question,
            query=query,
            params=params,
            patterns=list(self.patterns),
            rows=database.fetchall(query, params),
        )


class ExecutionConsultationStrategy(ConsultationStrategy):
    identifier = "SQ4"
    title = "Cumplimiento de produccion y OEE"
    objective = "Medir cumplimiento del plan, tiempos de parada y eficiencia real de la ejecucion."
    business_question = "Que tan bien se cumplio el plan de produccion y con que nivel de eficiencia opero cada orden?"
    patterns = ["Builder", "Decorator", "Proxy", "State", "Strategy"]

    def build(
        self,
        database: SQLiteMESDatabase,
        filters: QueryFilters,
        plant_capacity_units: int,
    ) -> ConsultationDefinition:
        query, params = build_execution_query(filters)
        return ConsultationDefinition(
            identifier=self.identifier,
            title=self.title,
            objective=self.objective,
            business_question=self.business_question,
            query=query,
            params=params,
            patterns=list(self.patterns),
            rows=database.fetchall(query, params),
        )


class TraceabilityConsultationStrategy(ConsultationStrategy):
    identifier = "SQ5"
    title = "Trazabilidad y evidencia de cumplimiento"
    objective = "Consolidar eventos, historial y auditoria para demostrar trazabilidad y cumplimiento operativo."
    business_question = "Que evidencia deja el sistema para rastrear una orden de punta a punta?"
    patterns = ["Flyweight", "Adapter", "Observer", "State", "Strategy"]

    def build(
        self,
        database: SQLiteMESDatabase,
        filters: QueryFilters,
        plant_capacity_units: int,
    ) -> ConsultationDefinition:
        query, params = build_traceability_query(filters)
        return ConsultationDefinition(
            identifier=self.identifier,
            title=self.title,
            objective=self.objective,
            business_question=self.business_question,
            query=query,
            params=params,
            patterns=list(self.patterns),
            rows=database.fetchall(query, params),
        )


class OperatorProductivityConsultationStrategy(ConsultationStrategy):
    identifier = "SQ6"
    title = "Consulta de productividad por operador"
    objective = "Comparar aporte operativo por operador segun ordenes cerradas, volumen producido y eficiencia."
    business_question = "Que operadores entregan mejor productividad y donde hay oportunidad de mejora?"
    patterns = ["Builder", "Decorator", "Observer", "Strategy"]

    def build(
        self,
        database: SQLiteMESDatabase,
        filters: QueryFilters,
        plant_capacity_units: int,
    ) -> ConsultationDefinition:
        query, params = build_operator_productivity_query(filters)
        return ConsultationDefinition(
            identifier=self.identifier,
            title=self.title,
            objective=self.objective,
            business_question=self.business_question,
            query=query,
            params=params,
            patterns=list(self.patterns),
            rows=database.fetchall(query, params),
        )


class LineLoadConsultationStrategy(ConsultationStrategy):
    identifier = "SQ7"
    title = "Carga y utilizacion por linea"
    objective = "Mostrar como se distribuye la demanda entre lineas para balancear carga y priorizar recursos."
    business_question = "Que lineas concentran mas trabajo y como se esta utilizando la capacidad instalada?"
    patterns = ["Composite", "Facade", "Strategy"]

    def build(
        self,
        database: SQLiteMESDatabase,
        filters: QueryFilters,
        plant_capacity_units: int,
    ) -> ConsultationDefinition:
        query, params = build_line_load_query(filters)
        return ConsultationDefinition(
            identifier=self.identifier,
            title=self.title,
            objective=self.objective,
            business_question=self.business_question,
            query=query,
            params=params,
            patterns=list(self.patterns),
            rows=database.fetchall(query, params),
        )


class AuditActivityConsultationStrategy(ConsultationStrategy):
    identifier = "SQ8"
    title = "Seguridad operativa y auditoria"
    objective = "Rastrear accesos y acciones relevantes para reforzar confianza, control y gobierno operativo."
    business_question = "Que usuarios, ordenes o lineas presentan actividad auditada relevante en el periodo?"
    patterns = ["Proxy", "Observer", "Command", "Strategy"]

    def build(
        self,
        database: SQLiteMESDatabase,
        filters: QueryFilters,
        plant_capacity_units: int,
    ) -> ConsultationDefinition:
        query, params = build_audit_activity_query(filters)
        return ConsultationDefinition(
            identifier=self.identifier,
            title=self.title,
            objective=self.objective,
            business_question=self.business_question,
            query=query,
            params=params,
            patterns=list(self.patterns),
            rows=database.fetchall(query, params),
        )


class ProductPerformanceConsultationStrategy(ConsultationStrategy):
    identifier = "SQ9"
    title = "Desempeno por producto"
    objective = "Comparar volumen, cumplimiento y eficiencia por producto para priorizar el portafolio operativo."
    business_question = "Que productos mueven mas volumen y cuales presentan peor eficiencia o mayor desviacion?"
    patterns = ["Builder", "Decorator", "Strategy"]

    def build(
        self,
        database: SQLiteMESDatabase,
        filters: QueryFilters,
        plant_capacity_units: int,
    ) -> ConsultationDefinition:
        query, params = build_product_performance_query(filters)
        return ConsultationDefinition(
            identifier=self.identifier,
            title=self.title,
            objective=self.objective,
            business_question=self.business_question,
            query=query,
            params=params,
            patterns=list(self.patterns),
            rows=database.fetchall(query, params),
        )


class ShiftPerformanceConsultationStrategy(ConsultationStrategy):
    identifier = "SQ10"
    title = "Comparativo de desempeno por turno"
    objective = "Comparar rendimiento entre turnos usando volumen producido, paradas y eficiencia promedio."
    business_question = "Que diferencias operativas hay entre DAY y NIGHT y donde conviene intervenir?"
    patterns = ["State", "Decorator", "Strategy"]

    def build(
        self,
        database: SQLiteMESDatabase,
        filters: QueryFilters,
        plant_capacity_units: int,
    ) -> ConsultationDefinition:
        query, params = build_shift_performance_query(filters)
        return ConsultationDefinition(
            identifier=self.identifier,
            title=self.title,
            objective=self.objective,
            business_question=self.business_question,
            query=query,
            params=params,
            patterns=list(self.patterns),
            rows=database.fetchall(query, params),
        )


class ConsultationStrategyCatalog:
    def __init__(self, strategies: list[ConsultationStrategy] | None = None) -> None:
        self._strategies = strategies or [
            PlanningConsultationStrategy(),
            DispatchConsultationStrategy(),
            CapacityConsultationStrategy(),
            ExecutionConsultationStrategy(),
            TraceabilityConsultationStrategy(),
            OperatorProductivityConsultationStrategy(),
            LineLoadConsultationStrategy(),
            AuditActivityConsultationStrategy(),
            ProductPerformanceConsultationStrategy(),
            ShiftPerformanceConsultationStrategy(),
        ]

    def build_all(
        self,
        database: SQLiteMESDatabase,
        filters: QueryFilters,
        plant_capacity_units: int,
    ) -> list[ConsultationDefinition]:
        return [
            strategy.build(database, filters, plant_capacity_units)
            for strategy in self._strategies
        ]


class MESCommand(ABC):
    name = "UNDEFINED"

    @abstractmethod
    def execute(self) -> Any:
        pass


class ExecuteOrderCommand(MESCommand):
    name = "EXECUTE_ORDER"

    def __init__(
        self,
        executor: Callable[[Any, Any], dict[str, Any]],
        user: Any,
        request: Any,
    ) -> None:
        self._executor = executor
        self._user = user
        self._request = request

    def execute(self) -> dict[str, Any]:
        return self._executor(self._user, self._request)


class GenerateConsultationsCommand(MESCommand):
    name = "GENERATE_CONSULTATIONS"

    def __init__(
        self,
        executor: Callable[[Any, Any], list[dict[str, Any]]],
        user: Any,
        filters: Any,
    ) -> None:
        self._executor = executor
        self._user = user
        self._filters = filters

    def execute(self) -> list[dict[str, Any]]:
        return self._executor(self._user, self._filters)


class MESCommandInvoker:
    def __init__(self) -> None:
        self._history: list[dict[str, Any]] = []

    def run(self, command: MESCommand) -> Any:
        started_at = datetime.now().isoformat(timespec="seconds")
        result = command.execute()
        self._history.append(
            {
                "command": command.name,
                "executed_at": started_at,
            }
        )
        return result

    def history(self) -> list[dict[str, Any]]:
        return list(self._history)

