"""
Flyweight - Perfiles compartidos de telemetria MES

Proposito:
- Evitar duplicar datos repetidos en cientos de eventos de produccion.
- Separar estado intrinseco compartido y estado extrinseco contextual.
- Centralizar la reutilizacion de perfiles de maquina desde una fabrica.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


class MachineProfileFlyweight(ABC):

    @abstractmethod
    def render_event(
        self,
        event_id: str,
        order_id: str,
        production_line: str,
        minute: int,
        units: int,
    ) -> str:
        pass


@dataclass(frozen=True)
class SharedMachineProfile(MachineProfileFlyweight):
    machine_type: str
    protocol: str
    quality_rule: str
    nominal_rate: int

    def render_event(
        self,
        event_id: str,
        order_id: str,
        production_line: str,
        minute: int,
        units: int,
    ) -> str:
        return (
            f"{event_id} | order={order_id} | line={production_line} | minute={minute} | "
            f"units={units} | profile={self.machine_type}/{self.protocol} | "
            f"quality={self.quality_rule} | nominal_rate={self.nominal_rate}"
        )


class MachineProfileFactory:

    def __init__(self) -> None:
        self._pool: dict[tuple[str, str, str, int], SharedMachineProfile] = {}

    def get_profile(
        self,
        machine_type: str,
        protocol: str,
        quality_rule: str,
        nominal_rate: int,
    ) -> SharedMachineProfile:
        key = (machine_type, protocol, quality_rule, nominal_rate)
        if key not in self._pool:
            self._pool[key] = SharedMachineProfile(
                machine_type=machine_type,
                protocol=protocol,
                quality_rule=quality_rule,
                nominal_rate=nominal_rate,
            )
        return self._pool[key]

    def pool_size(self) -> int:
        return len(self._pool)

    def pool_keys(self) -> list[str]:
        return ["/".join(map(str, key)) for key in self._pool]


@dataclass
class ProductionTelemetryEvent:
    profile: MachineProfileFlyweight
    event_id: str
    order_id: str
    production_line: str
    minute: int
    units: int

    def summary(self) -> str:
        return self.profile.render_event(
            self.event_id,
            self.order_id,
            self.production_line,
            self.minute,
            self.units,
        )


class MESTelemetryBoard:

    def __init__(self, factory: MachineProfileFactory) -> None:
        self._factory = factory
        self._events: list[ProductionTelemetryEvent] = []

    def capture_event(
        self,
        event_id: str,
        order_id: str,
        production_line: str,
        minute: int,
        units: int,
        machine_type: str,
        protocol: str,
        quality_rule: str,
        nominal_rate: int,
    ) -> ProductionTelemetryEvent:
        profile = self._factory.get_profile(machine_type, protocol, quality_rule, nominal_rate)
        event = ProductionTelemetryEvent(
            profile=profile,
            event_id=event_id,
            order_id=order_id,
            production_line=production_line,
            minute=minute,
            units=units,
        )
        self._events.append(event)
        return event

    def total_events(self) -> int:
        return len(self._events)

    def shared_profiles(self) -> int:
        return self._factory.pool_size()

    def estimated_objects_saved(self) -> int:
        return max(0, self.total_events() - self.shared_profiles())

    def export_sample(self, limit: int = 5) -> list[str]:
        return [event.summary() for event in self._events[:limit]]


def run_demo() -> dict:
    factory = MachineProfileFactory()
    board = MESTelemetryBoard(factory)
    for minute in range(1, 6):
        board.capture_event(
            event_id=f"EVT-FLY-{minute}",
            order_id="OP-2026-FUNC-FLY",
            production_line="LINE-A",
            minute=minute,
            units=minute * 100,
            machine_type="CNC",
            protocol="OPCUA",
            quality_rule="DIMENSION_CHECK",
            nominal_rate=60,
        )
    return {
        "total_events": board.total_events(),
        "shared_profiles": board.shared_profiles(),
        "estimated_objects_saved": board.estimated_objects_saved(),
        "sample": board.export_sample(3),
    }


if __name__ == "__main__":
    print(run_demo())
