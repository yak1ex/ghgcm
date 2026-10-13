from __future__ import annotations

import sys
import unittest

from github_credential_groups.wincred import enumerate_credentials


class PlatformGuardTests(unittest.TestCase):
    @unittest.skipIf(sys.platform == "win32", "non-Windows guard test")
    def test_rejects_non_windows_platform(self) -> None:
        with self.assertRaisesRegex(OSError, "only on Windows"):
            enumerate_credentials()


if __name__ == "__main__":
    unittest.main()

