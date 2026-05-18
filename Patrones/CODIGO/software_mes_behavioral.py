from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any

from software_mes_persistence import SQLiteMESDatabase


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

