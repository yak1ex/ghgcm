"""Command-line interface for read-only credential inventory."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .audit import ConfigurationError, audit_configuration, load_configuration
from .inventory import build_report
from .wincred import CredentialEnumerationError, enumerate_credentials


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="github-credential-groups")
    subparsers = parser.add_subparsers(dest="command", required=True)
    inventory = subparsers.add_parser("inventory", help="inventory GitHub credentials without modifying them")
    inventory.add_argument("--backend", choices=("wincredman",), default="wincredman")
    audit = subparsers.add_parser("audit", help="compare GitHub credentials with intended groups")
    audit.add_argument("--backend", choices=("wincredman",), required=True)
    audit.add_argument("--config", type=Path, required=True)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "audit":
            configuration = load_configuration(args.config)
            if configuration.backend != args.backend:
                raise ConfigurationError("configuration backend does not match --backend")
            findings = audit_configuration(configuration, enumerate_credentials())
            if not findings:
                print(f"Audit passed: {len(configuration.groups)} configured groups are consistent")
                return 0
            print(f"Audit found {len(findings)} finding(s)")
            for finding in findings:
                if finding.kind == "missing":
                    print(f"\n{finding.group_name}: missing configured repositories")
                else:
                    print(f"\n{finding.group_name}: repositories use different credentials")
                for repository in finding.repositories:
                    print(f"  - {repository}")
            return 3
        report = build_report(enumerate_credentials())
    except (ConfigurationError, CredentialEnumerationError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    entry_count = sum(len(group.target_names) for group in report.groups)
    print(f"Supported GitHub credentials: {entry_count}")
    print(f"Credential groups: {len(report.groups)}")
    for group in report.groups:
        qualifier = "duplicate" if len(group.target_names) > 1 else "unique"
        print(f"\n{group.identifier} ({qualifier}, {len(group.target_names)} entries)")
        for target in group.target_names:
            print(f"  - {target}")

    print(f"\nUnrecognized GitHub entries: {len(report.unrecognized)}")
    for entry in report.unrecognized:
        print(f"  - {entry.target_name}: {entry.reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
