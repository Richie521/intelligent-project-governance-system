from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import governance_transaction as transaction  # noqa: E402


@unittest.skipUnless(os.name == "nt", "Release concurrency acceptance targets Windows ReplaceFileW")
class ReleaseConcurrentCommitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "project"
        self.state = Path(self.temp.name) / "state"
        (self.root / ".codex").mkdir(parents=True)
        (self.root / "docs").mkdir()
        (self.root / "AGENTS.md").write_text("# Test entry\n", encoding="utf-8")
        self.target = self.root / "docs" / "10-status.md"
        self.target.write_text("state: old\n", encoding="utf-8")
        self.second = self.root / "docs" / "11-note.md"
        self.second.write_text("note: old\n", encoding="utf-8")
        source = self.root / "AGENTS.md"
        stat = source.stat()
        manifest = {
            "schema_version": 1,
            "project_id": "release-concurrency-test",
            "governance_language": "en",
            "project_role": "adopted",
            "routing_sources": {
                "entry": {
                    "path": "AGENTS.md",
                    "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                    "size": stat.st_size,
                    "mtime_ns": stat.st_mtime_ns,
                }
            },
            "projections": {
                "status": {
                    "path": "docs/10-status.md",
                    "operations": ["replace_exact"],
                    "allowed_authorizations": ["explicit_current_task"],
                    "create_if_missing": False,
                    "encoding": "utf-8",
                },
                "note": {
                    "path": "docs/11-note.md",
                    "operations": ["replace_exact"],
                    "allowed_authorizations": ["explicit_current_task"],
                    "create_if_missing": False,
                    "encoding": "utf-8",
                },
            },
            "transaction_contracts": [],
        }
        manifest_path = self.root / ".codex" / "governance-runtime.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        self.manifest_hash = hashlib.sha256(manifest_path.read_bytes()).hexdigest()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def request(self) -> dict[str, object]:
        return {
            "schema_version": 1,
            "transaction_id": "tx-release-final-window",
            "manifest_sha256": self.manifest_hash,
            "authorization": "explicit_current_task",
            "projections": [
                {
                    "owner": "status",
                    "operation": "replace_exact",
                    "old": "state: old",
                    "new": "state: proposed",
                }
            ],
            "evidence_refs": [],
        }

    def test_edit_in_final_replace_window_is_conflict_with_recoverable_copy(self) -> None:
        real_replace = transaction._replace_file_windows

        def inject_external_edit(path: Path, replacement: Path, backup: Path) -> None:
            path.write_text("state: external\n", encoding="utf-8")
            real_replace(path, replacement, backup)

        with mock.patch(
            "governance_transaction._replace_file_windows", side_effect=inject_external_edit
        ):
            result = transaction.apply_transaction(
                self.root, self.request(), state_root=self.state
            )

        self.assertEqual("conflict", result["status"])
        self.assertFalse(result["terminal_projection"])
        self.assertNotEqual("Writeback: updated status", result["writeback"])
        self.assertTrue(result["partial_or_uncertain"])
        self.assertEqual(1, result["known_committed_count"])
        self.assertEqual(1, result["files_written"])
        preserved = Path(result["conflict"]["conflict_backup"])
        self.assertEqual("state: external\n", preserved.read_text(encoding="utf-8"))
        self.assertEqual("state: proposed\n", self.target.read_text(encoding="utf-8"))

    def test_replacefile_1177_keeps_filesystem_recovery_state(self) -> None:
        real_replace = transaction._replace_file_windows

        def inject_1177(path: Path, replacement: Path, backup: Path) -> None:
            path.write_text("state: external\n", encoding="utf-8")
            real_replace(path, replacement, backup)
            raise OSError(1177, "injected ReplaceFileW error")

        with mock.patch(
            "governance_transaction._replace_file_windows", side_effect=inject_1177
        ):
            result = transaction.apply_transaction(
                self.root, self.request(), state_root=self.state
            )

        self.assertEqual("conflict", result["status"])
        conflict = result["conflict"]
        self.assertEqual(1177, conflict["winerror"])
        self.assertEqual("unknown", result["conflict_write_state"])
        self.assertIsNone(result["files_written"])
        self.assertTrue(result["partial_or_uncertain"])
        preserved = Path(conflict["conflict_backup"])
        self.assertEqual("state: external\n", preserved.read_text(encoding="utf-8"))
        self.assertTrue(self.target.exists())

    def test_rollback_window_edit_is_preserved_and_not_reported_as_rolled_back(self) -> None:
        real_replace = transaction._replace_file_windows
        calls = 0

        def inject_during_rollback(path: Path, replacement: Path, backup: Path) -> None:
            nonlocal calls
            calls += 1
            if calls == 2:
                path.write_text("state: external during rollback\n", encoding="utf-8")
            real_replace(path, replacement, backup)

        request = self.request()
        request["transaction_id"] = "tx-release-rollback-window"
        request["projections"] = [
            request["projections"][0],
            {
                "owner": "note",
                "operation": "replace_exact",
                "old": "note: old",
                "new": "note: proposed",
            },
        ]
        with mock.patch.dict(os.environ, {"GOVERNANCE_TRANSACTION_FAIL_AFTER": "1"}):
            with mock.patch(
                "governance_transaction._replace_file_windows", side_effect=inject_during_rollback
            ):
                result = transaction.apply_transaction(
                    self.root, request, state_root=self.state
                )

        self.assertEqual("failed", result["status"])
        self.assertFalse(result["terminal_projection"])
        self.assertTrue(result["hard_failures"])
        self.assertTrue(result["partial_or_uncertain"])
        self.assertIsNone(result["files_written"])
        self.assertIsNone(result["known_committed_count"])
        self.assertIsNone(result["changed_owners"])
        recoverable = list(self.target.parent.glob(".10-status.md.governance-conflict-*.bak"))
        self.assertEqual(1, len(recoverable), result)
        self.assertEqual(
            "state: external during rollback\n",
            recoverable[0].read_text(encoding="utf-8"),
        )
        self.assertEqual("note: old\n", self.second.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
