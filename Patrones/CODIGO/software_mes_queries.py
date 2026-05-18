from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class QueryFilters:
    order_id: str | None = None
    product_code: str | None = None
    production_line: str | None = None
    shift: str | None = None
    protocol: str | None = None
    operator_id: str | None = None
    state: str | None = None
    requested_by: str | None = None
    date_from: str | None = None
    date_to: str | None = None
    hour_from: str | None = None
    hour_to: str | None = None
    limit: int = 25


class SQLQueryBuilder:
    def __init__(self, base_query: str) -> None:
        self._base_query = base_query
        self._conditions: list[str] = []
        self._params: list[Any] = []
        self._group_clause = ""
        self._order_clause = ""
        self._limit_clause = ""

    def where(self, condition: str, value: Any | None = None) -> "SQLQueryBuilder":
        self._conditions.append(condition)
        if value is not None:
            self._params.append(value)
        return self

    def date_range(self, column: str, start: str | None, end: str | None) -> "SQLQueryBuilder":
        if start:
            self.where(f"date({column}) >= date(?)", start)
        if end:
            self.where(f"date({column}) <= date(?)", end)
        return self

    def hour_range(self, column: str, start: str | None, end: str | None) -> "SQLQueryBuilder":
        if start:
            self.where(f"time({column}) >= time(?)", start)
        if end:
            self.where(f"time({column}) <= time(?)", end)
        return self

    def order_by(self, clause: str) -> "SQLQueryBuilder":
        self._order_clause = clause
        return self

    def group_by(self, clause: str) -> "SQLQueryBuilder":
        self._group_clause = clause
        return self

    def limit(self, value: int) -> "SQLQueryBuilder":
        if value > 0:
            self._limit_clause = " LIMIT ?"
            self._params.append(value)
        return self

    def build(self) -> tuple[str, tuple[Any, ...]]:
        query = self._base_query
        if self._conditions:
            query = f"{query} WHERE {' AND '.join(self._conditions)}"
        if self._group_clause:
            query = f"{query} GROUP BY {self._group_clause}"
        if self._order_clause:
            query = f"{query} ORDER BY {self._order_clause}"
        if self._limit_clause:
            query = f"{query}{self._limit_clause}"
        return query, tuple(self._params)


def _apply_order_filters(
    builder: SQLQueryBuilder,
    filters: QueryFilters,
    timestamp_column: str = "created_at",
) -> SQLQueryBuilder:
    if filters.order_id:
        builder.where("order_id = ?", filters.order_id)
    if filters.product_code:
        builder.where("product_code = ?", filters.product_code)
    if filters.production_line:
        builder.where("production_line = ?", filters.production_line.upper())
    if filters.shift:
        builder.where("shift = ?", filters.shift.upper())
    if filters.protocol:
        builder.where("protocol = ?", filters.protocol.lower())
    if filters.operator_id:
        builder.where("operator_id = ?", filters.operator_id)
    if filters.state:
        builder.where("state = ?", filters.state.upper())
    if filters.requested_by:
        builder.where("requested_by = ?", filters.requested_by.lower())
    builder.date_range(timestamp_column, filters.date_from, filters.date_to)
    builder.hour_range(timestamp_column, filters.hour_from, filters.hour_to)
    builder.limit(filters.limit)
    return builder


def build_planning_query(filters: QueryFilters) -> tuple[str, tuple[Any, ...]]:
    builder = SQLQueryBuilder(
        """
        SELECT order_id, template_key, production_line, shift, planned_units,
               product_code, product_name, created_at
        FROM orders
        """
    )
    _apply_order_filters(builder, filters, "created_at")
    builder.order_by("created_at DESC")
    return builder.build()


def build_dispatch_query(filters: QueryFilters) -> tuple[str, tuple[Any, ...]]:
    builder = SQLQueryBuilder(
        """
        SELECT order_id, production_line, machine_type, line_mode, protocol,
               operator_id, operator_name, dispatch_at
        FROM orders
        """
    )
    builder.where("dispatch_at IS NOT NULL")
    _apply_order_filters(builder, filters, "dispatch_at")
    builder.order_by("dispatch_at DESC")
    return builder.build()


def build_capacity_query(filters: QueryFilters, plant_capacity_units: int) -> tuple[str, tuple[Any, ...]]:
    builder = SQLQueryBuilder(
        f"""
        SELECT order_id, production_line, planned_units,
               {plant_capacity_units} AS plant_capacity_units,
               ({plant_capacity_units} - planned_units) AS remaining_capacity,
               created_at
        FROM orders
        """
    )
    _apply_order_filters(builder, filters, "created_at")
    builder.order_by("created_at DESC")
    return builder.build()


def build_execution_query(filters: QueryFilters) -> tuple[str, tuple[Any, ...]]:
    builder = SQLQueryBuilder(
        """
        SELECT order_id, shift, planned_units, produced_units, downtime_minutes,
               ROUND((produced_units * 100.0) / NULLIF(planned_units, 0), 2) AS oee,
               state, completed_at
        FROM orders
        """
    )
    builder.where("completed_at IS NOT NULL")
    _apply_order_filters(builder, filters, "completed_at")
    builder.order_by("completed_at DESC")
    return builder.build()


def build_traceability_query(filters: QueryFilters) -> tuple[str, tuple[Any, ...]]:
    builder = SQLQueryBuilder(
        """
        SELECT
            o.order_id,
            o.production_line,
            o.product_code,
            o.quality_rule,
            COUNT(DISTINCT t.id) AS telemetry_events,
            COUNT(DISTINCT h.id) AS state_changes,
            COUNT(DISTINCT a.id) AS audit_events,
            MAX(a.created_at) AS last_audit_at
        FROM orders o
        LEFT JOIN telemetry_events t ON o.order_id = t.order_id
        LEFT JOIN order_history h ON o.order_id = h.order_id
        LEFT JOIN audit_events a ON o.order_id = a.order_id
        """
    )
    if filters.order_id:
        builder.where("o.order_id = ?", filters.order_id)
    if filters.product_code:
        builder.where("o.product_code = ?", filters.product_code)
    if filters.production_line:
        builder.where("o.production_line = ?", filters.production_line.upper())
    if filters.shift:
        builder.where("o.shift = ?", filters.shift.upper())
    if filters.protocol:
        builder.where("o.protocol = ?", filters.protocol.lower())
    if filters.operator_id:
        builder.where("o.operator_id = ?", filters.operator_id)
    if filters.state:
        builder.where("o.state = ?", filters.state.upper())
    if filters.requested_by:
        builder.where("o.requested_by = ?", filters.requested_by.lower())
    builder.date_range("o.created_at", filters.date_from, filters.date_to)
    builder.hour_range("o.created_at", filters.hour_from, filters.hour_to)
    builder.group_by("o.order_id, o.production_line, o.product_code, o.quality_rule")
    builder.order_by("MAX(o.created_at) DESC")
    builder.limit(filters.limit)
    return builder.build()
