"""Data models for credential inventory."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EntryStatus(str, Enum):
    SUPPORTED = "supported"
    UNRECOGNIZED = "unrecognized"


@dataclass(frozen=True)
class RawCredential:
    """A credential copied from the Windows API for in-process inspection."""

    target_name: str
    username: str | None
    secret: bytes
    credential_type: int = 1


@dataclass(frozen=True)
class InventoryEntry:
    target_name: str
    status: EntryStatus
    reason: str | None
    secret: bytes | None


@dataclass(frozen=True)
class ReportGroup:
    identifier: str
    target_names: tuple[str, ...]


@dataclass(frozen=True)
class InventoryReport:
    groups: tuple[ReportGroup, ...]
    unrecognized: tuple[InventoryEntry, ...]
