from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell.exe")


@unittest.skipUnless(os.name == "nt" and POWERSHELL, "Release installer acceptance targets Windows PowerShell")
class ReleaseTransactionUninstallTests(unittest.TestCase):
    def test_uninstall_removes_only_hash_matched_managed_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            install_dir = Path(temp) / "managed"
            install = subprocess.run(
                [
                    POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                    str(ROOT / "install.ps1"), "-InstallDir", str(install_dir),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, install.returncode, install.stderr)
            unmanaged = install_dir / "operator-notes.txt"
            unmanaged.write_text("keep this file\n", encoding="utf-8")
            uninstall = subprocess.run(
                [
                    POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                    str(ROOT / "uninstall.ps1"), "-InstallDir", str(install_dir),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(0, uninstall.returncode, uninstall.stderr)
            self.assertEqual("keep this file\n", unmanaged.read_text(encoding="utf-8"))
            self.assertTrue(install_dir.exists())

    def test_uninstall_preserves_modified_managed_file_and_other_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            install_dir = Path(temp) / "managed"
            subprocess.run(
                [
                    POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                    str(ROOT / "install.ps1"), "-InstallDir", str(install_dir),
                ],
                check=True,
                capture_output=True,
            )
            managed = install_dir / "run.ps1"
            managed.write_text("operator edit\n", encoding="utf-8")
            result = subprocess.run(
                [
                    "powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                    str(ROOT / "uninstall.ps1"), "-InstallDir", str(install_dir),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertEqual("operator edit\n", managed.read_text(encoding="utf-8"))
            self.assertTrue((install_dir / "installation.json").exists())


if __name__ == "__main__":
    unittest.main()
