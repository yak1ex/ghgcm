"""Classify GCM targets and group identical secrets without fingerprinting them."""

from __future__ import annotations

from collections import defaultdict
from urllib.parse import urlsplit

from .models import EntryStatus, InventoryEntry, InventoryReport, RawCredential, ReportGroup

LEGACY_PREFIX = "LegacyGeneric:target="
GCM_NAMESPACE = "git:"


def classify_credential(credential: RawCredential) -> InventoryEntry | None:
    """Return a GitHub inventory entry, or None for unrelated credentials."""

    target = credential.target_name
    normalized = target[len(LEGACY_PREFIX) :] if target.startswith(LEGACY_PREFIX) else target
    if not normalized.lower().startswith(GCM_NAMESPACE):
        return None

    service = normalized[len(GCM_NAMESPACE) :]
    try:
        parsed = urlsplit(service)
        host = parsed.hostname
        port = parsed.port
    except ValueError:
        return _unrecognized(target, "malformed GCM target")

    if host is None or host.lower() != "github.com":
        return None
    if credential.credential_type != 1:
        return _unrecognized(target, "credential is not a Generic credential")
    if parsed.scheme.lower() != "https":
        return _unrecognized(target, "GitHub target does not use HTTPS")
    if port not in (None, 443):
        return _unrecognized(target, "GitHub target uses an unexpected port")
    if not credential.secret:
        return _unrecognized(target, "credential secret is empty")
    if len(credential.secret) % 2:
        return _unrecognized(target, "credential blob is not valid UTF-16LE data")
    try:
        credential.secret.decode("utf-16-le")
    except UnicodeDecodeError:
        return _unrecognized(target, "credential blob is not valid UTF-16LE data")

    return InventoryEntry(target, EntryStatus.SUPPORTED, None, credential.secret)


def build_report(credentials: list[RawCredential]) -> InventoryReport:
    """Build a safe report using labels scoped to this invocation."""

    supported: list[InventoryEntry] = []
    unrecognized: list[InventoryEntry] = []
    for credential in credentials:
        entry = classify_credential(credential)
        if entry is None:
            continue
        if entry.status is EntryStatus.SUPPORTED:
            supported.append(entry)
        else:
            unrecognized.append(entry)

    by_secret: dict[bytes, list[str]] = defaultdict(list)
    for entry in supported:
        assert entry.secret is not None
        by_secret[entry.secret].append(entry.target_name)

    ordered = sorted(
        (tuple(sorted(targets, key=str.casefold)) for targets in by_secret.values()),
        key=lambda targets: tuple(value.casefold() for value in targets),
    )
    groups = tuple(
        ReportGroup(f"group-{index}", targets)
        for index, targets in enumerate(ordered, start=1)
    )
    return InventoryReport(groups, tuple(sorted(unrecognized, key=lambda item: item.target_name.casefold())))


def _unrecognized(target: str, reason: str) -> InventoryEntry:
    return InventoryEntry(target, EntryStatus.UNRECOGNIZED, reason, None)
