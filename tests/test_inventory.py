from __future__ import annotations

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from github_credential_groups.cli import main
from github_credential_groups.inventory import build_report, classify_credential
from github_credential_groups.models import EntryStatus, RawCredential
from github_credential_groups.wincred import CredentialEnumerationError


def secret(value: str) -> bytes:
    return value.encode("utf-16-le")


class InventoryTests(unittest.TestCase):
    def test_groups_identical_secrets_without_fingerprints(self) -> None:
        credentials = [
            RawCredential("git:https://github.com/acme/one", "alice", secret("synthetic-a")),
            RawCredential("LegacyGeneric:target=git:https://github.com/acme/two", "alice", secret("synthetic-a")),
            RawCredential("git:https://github.com/acme/three", "alice", secret("synthetic-b")),
            RawCredential("git:https://example.com/acme/one", "alice", secret("synthetic-a")),
        ]

        report = build_report(credentials)

        self.assertEqual([2, 1], [len(group.target_names) for group in report.groups])
        self.assertEqual(["group-1", "group-2"], [group.identifier for group in report.groups])

    def test_recognizes_host_level_and_user_specific_targets(self) -> None:
        for target in (
            "git:https://github.com",
            "git:https://alice@github.com/owner/repo",
            "LegacyGeneric:target=git:https://github.com/owner/repo",
        ):
            with self.subTest(target=target):
                entry = classify_credential(RawCredential(target, "alice", secret("synthetic")))
                self.assertIsNotNone(entry)
                self.assertEqual(EntryStatus.SUPPORTED, entry.status)

    def test_marks_malformed_github_entries_unrecognized(self) -> None:
        cases = [
            RawCredential("git:http://github.com/acme/repo", "alice", secret("synthetic")),
            RawCredential("git:https://github.com/acme/repo", "alice", b"odd"),
            RawCredential("git:https://github.com/acme/repo", "alice", b"\x00\xd8"),
            RawCredential("git:https://github.com/acme/repo", "alice", b""),
            RawCredential("git:https://github.com:444/acme/repo", "alice", secret("synthetic")),
        ]

        report = build_report(cases)

        self.assertEqual(0, len(report.groups))
        self.assertEqual(5, len(report.unrecognized))

    def test_cli_never_prints_secret(self) -> None:
        synthetic_token = "github_pat_SYNTHETIC_DO_NOT_USE"
        credential = RawCredential("git:https://github.com/acme/repo", "alice", secret(synthetic_token))
        output = io.StringIO()

        with patch("github_credential_groups.cli.enumerate_credentials", return_value=[credential]):
            with redirect_stdout(output):
                exit_code = main(["inventory"])

        self.assertEqual(0, exit_code)
        self.assertNotIn(synthetic_token, output.getvalue())
        self.assertIn("group-1", output.getvalue())

    def test_empty_inventory_is_successful(self) -> None:
        output = io.StringIO()
        with patch("github_credential_groups.cli.enumerate_credentials", return_value=[]):
            with redirect_stdout(output):
                exit_code = main(["inventory"])

        self.assertEqual(0, exit_code)
        self.assertIn("Supported GitHub credentials: 0", output.getvalue())

    def test_cli_reports_windows_api_failure_without_secret_data(self) -> None:
        output = io.StringIO()
        with patch(
            "github_credential_groups.cli.enumerate_credentials",
            side_effect=CredentialEnumerationError(5),
        ):
            with redirect_stderr(output):
                exit_code = main(["inventory"])

        self.assertEqual(1, exit_code)
        self.assertEqual("error: Windows credential enumeration failed (error 5)\n", output.getvalue())


if __name__ == "__main__":
    unittest.main()
