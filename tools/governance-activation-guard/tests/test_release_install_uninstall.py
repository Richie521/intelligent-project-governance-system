from __future__ import annotations

import os
import json
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import governance_guard  # noqa: E402
from governance_guard import inspect_tool_call  # noqa: E402
POWERSHELL = shutil.which("pwsh") or shutil.which("powershell.exe")


@unittest.skipUnless(os.name == "nt" and POWERSHELL, "Release installer acceptance targets Windows PowerShell")
class ReleaseGuardInstallTests(unittest.TestCase):
    def invoke(self, script: str, install_dir: Path, requirements: Path, *, install: bool) -> subprocess.CompletedProcess[str]:
        args = [
            POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
            str(ROOT / script), "-InstallDir", str(install_dir),
            "-RequirementsPath", str(requirements),
        ]
        if install:
            args.extend(["-PythonPath", sys.executable])
        return subprocess.run(args, text=True, capture_output=True, check=False)

    def test_exec_command_cmd_field_is_audited_and_invalid_input_fails_closed(self) -> None:
        write = inspect_tool_call("exec_command", {"cmd": "Set-Content result.txt changed"})
        self.assertFalse(write.allowed)

        readonly = inspect_tool_call("exec_command", {"cmd": "Get-Content README.md"})
        self.assertTrue(readonly.allowed, readonly.reason)

        legacy = inspect_tool_call("exec_command", {"command": "Get-Content README.md"})
        self.assertTrue(legacy.allowed, legacy.reason)

        missing = inspect_tool_call("exec_command", {"workdir": "C:/project"})
        self.assertFalse(missing.allowed)
        invalid = inspect_tool_call("exec_command", {"cmd": None})
        self.assertFalse(invalid.allowed)

        wrapper = (ROOT / "run-hook.ps1").read_text(encoding="utf-8")
        self.assertNotIn("F:\\python\\python.exe", wrapper.lower())
        self.assertIn("Get-Command python", wrapper)

    def test_install_preserves_unrelated_toml_and_uninstall_restores_exact_bytes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            install_dir = base / "managed"
            requirements = base / "requirements.toml"
            original = b"[unrelated]\nvalue = 'keep me'\n"
            requirements.write_bytes(original)
            installed = self.invoke("install.ps1", install_dir, requirements, install=True)
            self.assertEqual(0, installed.returncode, installed.stderr)
            installed_text = requirements.read_text(encoding="utf-8-sig")
            self.assertIn("[unrelated]", installed_text)
            parsed = tomllib.loads(installed_text)
            self.assertEqual("keep me", parsed["unrelated"]["value"])
            self.assertIn("PreToolUse", parsed["hooks"])
            record = json.loads((install_dir / "install-record.json").read_text(encoding="utf-8"))
            self.assertTrue(Path(record["backup_path"]).is_file())

            uninstalled = self.invoke("uninstall.ps1", install_dir, requirements, install=False)
            self.assertEqual(0, uninstalled.returncode, uninstalled.stderr)
            self.assertEqual(original, requirements.read_bytes())
            self.assertFalse(install_dir.exists())

    def test_duplicate_root_tables_fail_closed_without_changing_requirements(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            install_dir = base / "managed"
            requirements = base / "requirements.toml"
            original = b"[hooks]\nexisting = true\n"
            requirements.write_bytes(original)
            result = self.invoke("install.ps1", install_dir, requirements, install=True)
            self.assertNotEqual(0, result.returncode)
            self.assertEqual(original, requirements.read_bytes())

    def test_uninstall_refuses_modified_requirements_and_keeps_recovery_backup(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            install_dir = base / "managed"
            requirements = base / "requirements.toml"
            original = b"[unrelated]\nvalue = 1\n"
            requirements.write_bytes(original)
            installed = self.invoke("install.ps1", install_dir, requirements, install=True)
            self.assertEqual(0, installed.returncode, installed.stderr)
            record = json.loads((install_dir / "install-record.json").read_text(encoding="utf-8"))
            backup = Path(record["backup_path"])
            requirements.write_text(requirements.read_text(encoding="utf-8") + "# operator edit\n", encoding="utf-8")
            current = requirements.read_bytes()

            result = self.invoke("uninstall.ps1", install_dir, requirements, install=False)
            self.assertNotEqual(0, result.returncode)
            self.assertEqual(current, requirements.read_bytes())
            self.assertTrue(backup.exists())
            self.assertTrue((install_dir / "install-record.json").exists())

    def test_legacy_install_without_backup_migrates_only_observed_unmanaged_remainder(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            install_dir = base / "managed"
            requirements = base / "requirements.toml"
            first = self.invoke("install.ps1", install_dir, requirements, install=True)
            self.assertEqual(0, first.returncode, first.stderr)
            record_path = install_dir / "install-record.json"
            record = json.loads(record_path.read_text(encoding="utf-8"))
            record["backup_path"] = None
            record["requirements_backup_sha256"] = None
            record.pop("requirements_recovery", None)
            record_path.write_text(json.dumps(record), encoding="utf-8")

            upgraded = self.invoke("install.ps1", install_dir, requirements, install=True)
            self.assertEqual(0, upgraded.returncode, upgraded.stderr)
            migrated = json.loads(record_path.read_text(encoding="utf-8"))
            self.assertEqual("legacy_unmanaged_remainder_only", migrated["requirements_recovery"])
            remainder_backup = Path(migrated["backup_path"])
            self.assertTrue(remainder_backup.exists())
            self.assertEqual(b"", remainder_backup.read_bytes())

    def test_blocked_probe_cannot_be_recorded_as_completed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            store = governance_guard.GateStore(Path(temp))
            event = {
                "session_id": "release-lifecycle-session",
                "hook_event_name": "UserPromptSubmit",
                "cwd": str(Path(temp)),
                "prompt": "启动分层诊断",
            }
            governance_guard.handle_event(event, store)
            state = store.load(event["session_id"])
            state["status"] = "repair_authorized"
            state["prevention_plan_sha256"] = "a" * 64
            state["repair_scope"] = "isolated lifecycle probe"
            store.save(state)
            receipt = {
                "gate_id": state["gate_id"],
                "verification": ["isolated probe"],
                "prevention_verification": {
                    "prevention_plan_sha256": state["prevention_plan_sha256"],
                    "regression_probe": "probe was blocked",
                    "result": "blocked",
                    "evidence": ["temporary state only"],
                    "recurrence_control": "gate remains open",
                },
                "hard_failures": [],
                "non_blocking_risks": [],
                "writeback": "none",
                "status": "completed",
            }
            with self.assertRaises(governance_guard.GuardStateError):
                governance_guard.record_receipt("completion", receipt, store)
            self.assertEqual("repair_authorized", store.load(event["session_id"])["status"])

            receipt["status"] = "blocked"
            receipt["hard_failures"] = ["probe did not pass"]
            result = governance_guard.record_receipt("completion", receipt, store)
            self.assertEqual("blocked", result["status"])
            self.assertEqual("blocked", store.load(event["session_id"])["status"])


if __name__ == "__main__":
    unittest.main()
