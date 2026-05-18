from __future__ import annotations

import hashlib
import hmac
import os
from dataclasses import dataclass
from datetime import datetime

from software_mes_persistence import SQLiteMESDatabase


def _normalize_allowed_lines(allowed_lines: tuple[str, ...] | list[str]) -> tuple[str, ...]:
    normalized = []
    for item in allowed_lines:
        clean_item = item.strip().upper()
        if clean_item:
            normalized.append(clean_item)
    return tuple(normalized)


def hash_password(password: str, salt: bytes | None = None) -> tuple[str, str]:
    if len(password) < 8:
        raise ValueError("La contrasena debe tener al menos 8 caracteres.")
    salt_bytes = salt or os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_bytes, 120_000)
    return salt_bytes.hex(), digest.hex()


def verify_password(password: str, password_salt: str, password_hash: str) -> bool:
    computed_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(password_salt),
        120_000,
    ).hex()
    return hmac.compare_digest(computed_hash, password_hash)


@dataclass(frozen=True)
class AuthenticatedUser:
    username: str
    role: str
    allowed_lines: tuple[str, ...]

    def can_read_line(self, production_line: str) -> bool:
        line = production_line.strip().upper()
        return self.role == "admin" or line in self.allowed_lines

    def can_generate_reports(self) -> bool:
        return self.role in {"admin", "supervisor"}

    def can_manage_orders(self) -> bool:
        return self.role in {"admin", "supervisor", "operator"}


class AuthenticationService:
    def __init__(self, database: SQLiteMESDatabase) -> None:
        self._database = database

    def register_user(
        self,
        username: str,
        password: str,
        role: str,
        allowed_lines: tuple[str, ...] | list[str],
    ) -> None:
        clean_username = username.strip().lower()
        clean_role = role.strip().lower()
        if not clean_username:
            raise ValueError("El username es obligatorio.")
        if clean_role not in {"admin", "supervisor", "operator"}:
            raise ValueError("El rol debe ser admin, supervisor u operator.")

        normalized_lines = _normalize_allowed_lines(allowed_lines)
        if clean_role != "admin" and not normalized_lines:
            raise ValueError("Los usuarios no administradores deben tener lineas autorizadas.")

        salt_hex, hash_hex = hash_password(password)
        self._database.upsert_user(
            username=clean_username,
            password_salt=salt_hex,
            password_hash=hash_hex,
            role=clean_role,
            allowed_lines=",".join(normalized_lines),
            created_at=datetime.now().isoformat(timespec="seconds"),
        )

    def authenticate(self, username: str, password: str) -> AuthenticatedUser:
        clean_username = username.strip().lower()
        user_row = self._database.get_user(clean_username)
        if not user_row or not int(user_row.get("active", 0)):
            raise PermissionError("El usuario no existe o esta inactivo.")

        if not verify_password(password, str(user_row["password_salt"]), str(user_row["password_hash"])):
            raise PermissionError("Credenciales invalidas.")

        allowed_lines = tuple(
            item.strip().upper()
            for item in str(user_row.get("allowed_lines", "")).split(",")
            if item.strip()
        )
        return AuthenticatedUser(
            username=clean_username,
            role=str(user_row["role"]).lower(),
            allowed_lines=allowed_lines,
        )

