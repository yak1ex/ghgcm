"""Load intended credential groups and audit them against an inventory."""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote, urlsplit

from .inventory import LEGACY_PREFIX, GCM_NAMESPACE, classify_credential
from .models import EntryStatus, RawCredential


class ConfigurationError(ValueError):
    """Raised when an audit configuration is malformed or ambiguous."""


@dataclass(frozen=True)
class IntendedGroup:
    name: str
    repositories: tuple[str, ...]


@dataclass(frozen=True)
class AuditConfiguration:
    backend: str
    groups: tuple[IntendedGroup, ...]


@dataclass(frozen=True)
class AuditFinding:
    group_name: str
    kind: str
    repositories: tuple[str, ...]


def load_configuration(path: Path) -> AuditConfiguration:
    try:
        with path.open("rb") as stream:
            document = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ConfigurationError(f"cannot read configuration: {error}") from error

    unknown_document_fields = set(document) - {"version", "backend", "groups"}
    if unknown_document_fields:
        raise ConfigurationError(
            f"configuration has unknown fields: {', '.join(sorted(unknown_document_fields))}"
        )
    if document.get("version") != 1:
        raise ConfigurationError("version must be 1")
    if document.get("backend") != "wincredman":
        raise ConfigurationError("backend must be 'wincredman'")
    raw_groups = document.get("groups")
    if not isinstance(raw_groups, list) or not raw_groups:
        raise ConfigurationError("groups must be a non-empty array of tables")

    groups: list[IntendedGroup] = []
    names: set[str] = set()
    assigned: dict[str, str] = {}
    for index, raw_group in enumerate(raw_groups, start=1):
        if not isinstance(raw_group, dict):
            raise ConfigurationError(f"groups[{index}] must be a table")
        unknown = set(raw_group) - {"name", "repositories"}
        if unknown:
            raise ConfigurationError(f"groups[{index}] has unknown fields: {', '.join(sorted(unknown))}")
        name = raw_group.get("name")
        repositories = raw_group.get("repositories")
        if not isinstance(name, str) or not name.strip():
            raise ConfigurationError(f"groups[{index}].name must be a non-empty string")
        if name.casefold() in names:
            raise ConfigurationError(f"duplicate group name: {name}")
        names.add(name.casefold())
        if not isinstance(repositories, list) or not repositories:
            raise ConfigurationError(f"group '{name}' must have at least one repository")

        normalized: list[str] = []
        for repository in repositories:
            identity = normalize_repository(repository)
            key = identity.casefold()
            if key in assigned:
                raise ConfigurationError(
                    f"repository '{identity}' is assigned to both '{assigned[key]}' and '{name}'"
                )
            assigned[key] = name
            normalized.append(identity)
        groups.append(IntendedGroup(name, tuple(normalized)))
    return AuditConfiguration("wincredman", tuple(groups))


def normalize_repository(value: object) -> str:
    if not isinstance(value, str) or value.count("/") != 1:
        raise ConfigurationError("repositories must use the form 'owner/repository'")
    owner, repository = value.split("/")
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", owner):
        raise ConfigurationError(f"invalid GitHub owner in repository identity: {value}")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", repository) or repository in {".", ".."}:
        raise ConfigurationError(f"invalid GitHub repository name: {value}")
    return value


def repository_identity(credential: RawCredential) -> str | None:
    entry = classify_credential(credential)
    if entry is None or entry.status is not EntryStatus.SUPPORTED:
        return None
    target = credential.target_name
    normalized = target[len(LEGACY_PREFIX) :] if target.startswith(LEGACY_PREFIX) else target
    parsed = urlsplit(normalized[len(GCM_NAMESPACE) :])
    segments = [unquote(segment) for segment in parsed.path.split("/") if segment]
    if len(segments) != 2 or any(segment in {".", ".."} for segment in segments):
        return None
    return f"{segments[0]}/{segments[1]}"


def audit_configuration(
    configuration: AuditConfiguration, credentials: list[RawCredential]
) -> tuple[AuditFinding, ...]:
    observed: dict[str, list[RawCredential]] = {}
    for credential in credentials:
        identity = repository_identity(credential)
        if identity is not None:
            observed.setdefault(identity.casefold(), []).append(credential)

    findings: list[AuditFinding] = []
    for group in configuration.groups:
        missing: list[str] = []
        secrets: dict[bytes, list[str]] = {}
        for repository in group.repositories:
            matches = observed.get(repository.casefold(), [])
            if not matches:
                missing.append(repository)
                continue
            for match in matches:
                secrets.setdefault(match.secret, []).append(repository)
        if missing:
            findings.append(AuditFinding(group.name, "missing", tuple(missing)))
        if len(secrets) > 1:
            split = tuple(sorted({item for values in secrets.values() for item in values}, key=str.casefold))
            findings.append(AuditFinding(group.name, "split", split))
    return tuple(findings)
