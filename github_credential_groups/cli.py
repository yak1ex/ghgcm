"""Command-line interface for read-only credential inventory."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from .inventory import build_report
from .wincred import CredentialEnumerationError, enumerate_credentials


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="github-credential-groups")
    subparsers = parser.add_subparsers(dest="command", required=True)
    inventory = subparsers.add_parser("inventory", help="inventory GitHub credentials without modifying them")
    inventory.add_argument("--backend", choices=("wincredman",), default="wincredman")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command != "inventory":
        return 2

    try:
        report = build_report(enumerate_credentials())
    except (CredentialEnumerationError, OSError) as error:
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
