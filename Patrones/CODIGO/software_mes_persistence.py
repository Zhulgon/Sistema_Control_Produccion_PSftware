from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Iterable


class SQLiteMESDatabase:
    """Singleton por ruta para centralizar la conexion SQLite del proyecto."""

    _instances: dict[str, "SQLiteMESDatabase"] = {}

    def __new__(cls, db_path: str | Path) -> "SQLiteMESDatabase":
        resolved_path = str(Path(db_path).resolve())
        if resolved_path not in cls._instances:
            instance = super().__new__(cls)
            cls._instances[resolved_path] = instance
        return cls._instances[resolved_path]

    def __init__(self, db_path: str | Path) -> None:
        resolved_path = str(Path(db_path).resolve())
        if getattr(self, "_initialized", False) and self._db_path == resolved_path:
            return

        self._initialized = True
        self._db_path = resolved_path
        Path(self._db_path).parent.mkdir(parents=True, exist_ok=True)
        self._connection = sqlite3.connect(self._db_path, check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._create_schema()

    @property
    def db_path(self) -> str:
        return self._db_path

    def _create_schema(self) -> None:
        self._connection.executescript(
            """
            PRAGMA foreign_keys = ON;

            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_salt TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                allowed_lines TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                template_key TEXT NOT NULL,
                template_name TEXT NOT NULL,
                product_code TEXT NOT NULL,
                product_name TEXT NOT NULL,
                machine_type TEXT NOT NULL,
                production_line TEXT NOT NULL,
                line_mode TEXT NOT NULL,
                shift TEXT NOT NULL,
                protocol TEXT NOT NULL,
                planned_units INTEGER NOT NULL,
                produced_units INTEGER NOT NULL,
                downtime_minutes INTEGER NOT NULL,
                operator_id TEXT NOT NULL,
                operator_name TEXT NOT NULL,
                requested_by TEXT NOT NULL,
                state TEXT NOT NULL,
                quality_rule TEXT NOT NULL,
                created_at TEXT NOT NULL,
                shift_start_at TEXT,
                shift_end_at TEXT,
                dispatch_at TEXT,
                completed_at TEXT,
                FOREIGN KEY (requested_by) REFERENCES users(username)
            );

            CREATE TABLE IF NOT EXISTS order_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                from_state TEXT NOT NULL,
                to_state TEXT NOT NULL,
                changed_at TEXT NOT NULL,
                note TEXT NOT NULL,
                changed_by TEXT NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id)
            );

            CREATE TABLE IF NOT EXISTS telemetry_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                production_line TEXT NOT NULL,
                event_minute INTEGER NOT NULL,
                units INTEGER NOT NULL,
                machine_type TEXT NOT NULL,
                protocol TEXT NOT NULL,
                quality_rule TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id)
            );

            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                username TEXT NOT NULL,
                order_id TEXT,
                production_line TEXT,
                description TEXT NOT NULL,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS consultation_batches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_code TEXT NOT NULL UNIQUE,
                username TEXT NOT NULL,
                created_at TEXT NOT NULL,
                filters_json TEXT NOT NULL,
                total_queries INTEGER NOT NULL,
                total_rows INTEGER NOT NULL,
                FOREIGN KEY (username) REFERENCES users(username)
            );

            CREATE TABLE IF NOT EXISTS consultation_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                batch_code TEXT NOT NULL,
                consultation_identifier TEXT NOT NULL,
                title TEXT NOT NULL,
                suggested_query TEXT NOT NULL,
                query_params_json TEXT NOT NULL,
                filters_json TEXT NOT NULL,
                patterns_json TEXT NOT NULL,
                row_count INTEGER NOT NULL,
                sample_result_json TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (batch_code) REFERENCES consultation_batches(batch_code)
            );

            CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
            CREATE INDEX IF NOT EXISTS idx_orders_line ON orders(production_line);
            CREATE INDEX IF NOT EXISTS idx_orders_shift ON orders(shift);
            CREATE INDEX IF NOT EXISTS idx_orders_protocol ON orders(protocol);
            CREATE INDEX IF NOT EXISTS idx_orders_state ON orders(state);
            CREATE INDEX IF NOT EXISTS idx_history_order_id ON order_history(order_id);
            CREATE INDEX IF NOT EXISTS idx_telemetry_order_id ON telemetry_events(order_id);
            CREATE INDEX IF NOT EXISTS idx_audit_order_id ON audit_events(order_id);
            CREATE INDEX IF NOT EXISTS idx_consultation_batches_username ON consultation_batches(username);
            CREATE INDEX IF NOT EXISTS idx_consultation_batches_created_at ON consultation_batches(created_at);
            CREATE INDEX IF NOT EXISTS idx_consultation_results_batch_code ON consultation_results(batch_code);
            """
        )
        self._ensure_column("orders", "shift_start_at", "TEXT")
        self._ensure_column("orders", "shift_end_at", "TEXT")
        self._connection.commit()

    def _ensure_column(self, table_name: str, column_name: str, column_definition: str) -> None:
        cursor = self._connection.execute(f"PRAGMA table_info({table_name})")
        columns = {str(row[1]) for row in cursor.fetchall()}
        if column_name not in columns:
            self._connection.execute(
                f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
            )

    def execute(self, query: str, params: Any = ()) -> None:
        if isinstance(params, dict):
            self._connection.execute(query, params)
        else:
            self._connection.execute(query, tuple(params))
        self._connection.commit()

    def executemany(self, query: str, rows: Iterable[Iterable[Any]]) -> None:
        self._connection.executemany(query, list(rows))
        self._connection.commit()

    def fetchone(self, query: str, params: Any = ()) -> dict[str, Any] | None:
        if isinstance(params, dict):
            cursor = self._connection.execute(query, params)
        else:
            cursor = self._connection.execute(query, tuple(params))
        row = cursor.fetchone()
        return dict(row) if row else None

    def fetchall(self, query: str, params: Any = ()) -> list[dict[str, Any]]:
        if isinstance(params, dict):
            cursor = self._connection.execute(query, params)
        else:
            cursor = self._connection.execute(query, tuple(params))
        return [dict(row) for row in cursor.fetchall()]

    def upsert_user(
        self,
        username: str,
        password_salt: str,
        password_hash: str,
        role: str,
        allowed_lines: str,
        created_at: str,
        active: int = 1,
    ) -> None:
        self.execute(
            """
            INSERT INTO users (username, password_salt, password_hash, role, allowed_lines, active, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(username) DO UPDATE SET
                password_salt = excluded.password_salt,
                password_hash = excluded.password_hash,
                role = excluded.role,
                allowed_lines = excluded.allowed_lines,
                active = excluded.active
            """,
            (username, password_salt, password_hash, role, allowed_lines, active, created_at),
        )

    def get_user(self, username: str) -> dict[str, Any] | None:
        return self.fetchone("SELECT * FROM users WHERE username = ?", (username,))

    def save_order(self, payload: dict[str, Any]) -> None:
        self.execute(
            """
            INSERT INTO orders (
                order_id, template_key, template_name, product_code, product_name,
                machine_type, production_line, line_mode, shift, protocol,
                planned_units, produced_units, downtime_minutes, operator_id,
                operator_name, requested_by, state, quality_rule,
                created_at, shift_start_at, shift_end_at, dispatch_at, completed_at
            )
            VALUES (
                :order_id, :template_key, :template_name, :product_code, :product_name,
                :machine_type, :production_line, :line_mode, :shift, :protocol,
                :planned_units, :produced_units, :downtime_minutes, :operator_id,
                :operator_name, :requested_by, :state, :quality_rule,
                :created_at, :shift_start_at, :shift_end_at, :dispatch_at, :completed_at
            )
            ON CONFLICT(order_id) DO UPDATE SET
                template_key = excluded.template_key,
                template_name = excluded.template_name,
                product_code = excluded.product_code,
                product_name = excluded.product_name,
                machine_type = excluded.machine_type,
                production_line = excluded.production_line,
                line_mode = excluded.line_mode,
                shift = excluded.shift,
                protocol = excluded.protocol,
                planned_units = excluded.planned_units,
                produced_units = excluded.produced_units,
                downtime_minutes = excluded.downtime_minutes,
                operator_id = excluded.operator_id,
                operator_name = excluded.operator_name,
                requested_by = excluded.requested_by,
                state = excluded.state,
                quality_rule = excluded.quality_rule,
                created_at = excluded.created_at,
                shift_start_at = excluded.shift_start_at,
                shift_end_at = excluded.shift_end_at,
                dispatch_at = excluded.dispatch_at,
                completed_at = excluded.completed_at
            """,
            payload,
        )

    def save_order_history(self, rows: list[dict[str, Any]]) -> None:
        if not rows:
            return
        self.executemany(
            """
            INSERT INTO order_history (
                order_id, from_state, to_state, changed_at, note, changed_by
            )
            VALUES (:order_id, :from_state, :to_state, :changed_at, :note, :changed_by)
            """,
            rows,
        )

    def save_telemetry_events(self, rows: list[dict[str, Any]]) -> None:
        if not rows:
            return
        self.executemany(
            """
            INSERT INTO telemetry_events (
                order_id, production_line, event_minute, units, machine_type,
                protocol, quality_rule, created_at
            )
            VALUES (
                :order_id, :production_line, :event_minute, :units, :machine_type,
                :protocol, :quality_rule, :created_at
            )
            """,
            rows,
        )

    def save_audit_event(self, payload: dict[str, Any]) -> None:
        self.execute(
            """
            INSERT INTO audit_events (
                event_type, username, order_id, production_line, description, created_at
            )
            VALUES (
                :event_type, :username, :order_id, :production_line, :description, :created_at
            )
            """,
            payload,
        )

    def save_consultation_batch(self, payload: dict[str, Any]) -> None:
        self.execute(
            """
            INSERT INTO consultation_batches (
                batch_code, username, created_at, filters_json, total_queries, total_rows
            )
            VALUES (
                :batch_code, :username, :created_at, :filters_json, :total_queries, :total_rows
            )
            """,
            payload,
        )

    def save_consultation_results(self, rows: list[dict[str, Any]]) -> None:
        if not rows:
            return
        self.executemany(
            """
            INSERT INTO consultation_results (
                batch_code, consultation_identifier, title, suggested_query,
                query_params_json, filters_json, patterns_json, row_count,
                sample_result_json, created_at
            )
            VALUES (
                :batch_code, :consultation_identifier, :title, :suggested_query,
                :query_params_json, :filters_json, :patterns_json, :row_count,
                :sample_result_json, :created_at
            )
            """,
            rows,
        )
