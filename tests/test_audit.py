from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from github_credential_groups.audit import ConfigurationError, audit_configuration, load_configuration
from github_credential_groups.cli import main
from github_credential_groups.models import RawCredential


def credential(repository: str, value: str, *, legacy: bool = False) -> RawCredential:
    prefix = "LegacyGeneric:target=" if legacy else ""
    return RawCredential(f"{prefix}git:https://github.com/{repository}", "synthetic", value.encode("utf-16-le"))


def configuration(text: str):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "groups.toml"
        path.write_text(text, encoding="utf-8")
        return load_configuration(path)


class AuditTests(unittest.TestCase):
    def test_reports_missing_members_and_split_secrets(self) -> None:
        config = configuration(
            '''version = 1
backend = "wincredman"
[[groups]]
name = "shared-sso"
repositories = ["org/a", "org/b", "org/missing"]
'''
        )
        findings = audit_configuration(
            config,
            [credential("org/a", "synthetic-a"), credential("ORG/B", "synthetic-b", legacy=True)],
        )

        self.assertEqual(["missing", "split"], [finding.kind for finding in findings])
        self.assertEqual(("org/missing",), findings[0].repositories)
        self.assertEqual(("org/a", "org/b"), findings[1].repositories)

    def test_consistent_group_has_no_findings(self) -> None:
        config = configuration(
            '''version = 1
backend = "wincredman"
[[groups]]
name = "shared"
repositories = ["org/a", "org/b"]
'''
        )
        findings = audit_configuration(
            config, [credential("org/a", "same"), credential("org/b", "same")]
        )
        self.assertEqual((), findings)

    def test_rejects_duplicate_repository_membership(self) -> None:
        with self.assertRaisesRegex(ConfigurationError, "assigned to both"):
            configuration(
                '''version = 1
backend = "wincredman"
[[groups]]
name = "one"
repositories = ["org/repo"]
[[groups]]
name = "two"
repositories = ["ORG/REPO"]
'''
            )

    def test_rejects_malformed_configuration(self) -> None:
        cases = (
            'version = 2\nbackend = "wincredman"\ngroups = []',
            'version = 1\nbackend = "dpapi"\ngroups = []',
            'version = 1\nbackend = "wincredman"\n[[groups]]\nname = "x"\nrepositories = ["not-a-repository"]',
        )
        for text in cases:
            with self.subTest(text=text), self.assertRaises(ConfigurationError):
                configuration(text)

    def test_cli_reports_drift_without_printing_secrets(self) -> None:
        text = '''version = 1
backend = "wincredman"
[[groups]]
name = "shared"
repositories = ["org/a", "org/b"]
'''
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "groups.toml"
            path.write_text(text, encoding="utf-8")
            output = io.StringIO()
            credentials = [credential("org/a", "SECRET-A"), credential("org/b", "SECRET-B")]
            with patch("github_credential_groups.cli.enumerate_credentials", return_value=credentials):
                with redirect_stdout(output):
                    exit_code = main(["audit", "--backend", "wincredman", "--config", str(path)])

        self.assertEqual(3, exit_code)
        self.assertIn("repositories use different credentials", output.getvalue())
        self.assertNotIn("SECRET-A", output.getvalue())
        self.assertNotIn("SECRET-B", output.getvalue())

    def test_cli_reports_configuration_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "groups.toml"
            path.write_text('version = 1\nbackend = "dpapi"\ngroups = []', encoding="utf-8")
            output = io.StringIO()
            with redirect_stderr(output):
                exit_code = main(["audit", "--backend", "wincredman", "--config", str(path)])

        self.assertEqual(1, exit_code)
        self.assertIn("backend must be 'wincredman'", output.getvalue())


if __name__ == "__main__":
    unittest.main()
