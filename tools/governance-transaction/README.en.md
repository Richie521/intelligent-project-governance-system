# Governance Transaction Runner

[中文](README.md)

This runner combines material governance changes into one recoverable transaction. It only writes owners registered in the target project's `.codex/governance-runtime.json`; it does not handle ordinary business files or declare a disabled task projection. The target project's current manifest defines the owners and paths.

The method and manual diagnosis do not require a Hook. A dedicated user command starts the documented agent process; this is an agent-followed agreement, not a machine-enforced boundary.

## Common Commands

```powershell
# Set CODEX_PYTHON only when Python 3 is not available as python on PATH.
$env:CODEX_PYTHON = '<absolute path to python.exe>'
.\tools\governance-transaction\run.ps1 --project-root . validate-manifest
Get-Content -Raw .\request.json | .\tools\governance-transaction\run.ps1 --project-root . apply --request-stdin
.\tools\governance-transaction\run.ps1 --project-root . recover
.\tools\governance-transaction\run.ps1 --project-root . benchmark
```

Do not set `CODEX_PYTHON` when `python` is already on `PATH`. Do not invoke the runner when there is no governance change.

## Request Interface

Use `apply --request-stdin` only for an authorized, persistent change. It accepts one UTF-8 JSON object. Do not include raw conversation text, credentials, or hidden reasoning. Read only the current manifest and source text needed to prepare the change.

| Field | Meaning |
| --- | --- |
| `schema_version` | Fixed at `1`. |
| `transaction_id` | Stable ID for one logical transaction: 3–128 ASCII letters, digits, dots, underscores, or hyphens; starts with a letter or digit. The same ID binds to the same request. |
| `manifest_sha256` | SHA-256 of the current `.codex/governance-runtime.json` raw bytes, not a re-serialized JSON value. |
| `authorization` | `explicit_current_task` or `automatic_low_risk`, subject to the current authorization and each owner's allowed values. |
| `projections` | Array of operations. Each item contains a manifest-registered `owner` and an allowed `operation`. The manifest determines paths; a request cannot choose arbitrary paths. |
| `evidence_refs` | Optional short source references; do not include private source text. |
| `contract_tags` | Optional contract tags. Cross-project repair uses the agreed `central_repair_sync` tag. |

The manifest can use `transaction_contracts` to bind required projections. A contract can be activated by an actual change to its triggering owner or by a request's `contract_tags`. If an activated request omits a required owner, the runner rejects the whole transaction before writing. Declare an idempotent projection when a required owner must remain bound but needs no content change. The receipt retains safety tags showing that the contract was applied.

Each operation also requires these fields and applies the stated conflict rule:

| Operation | Required fields and behavior |
| --- | --- |
| `replace_exact` | `old`, `new`. The old text must be unique. If it is absent and the new text is already unique, the result is unchanged; otherwise report a conflict. |
| `insert_after` | `anchor`, `content`. The anchor must be unique. If the content is already present uniquely, do not insert it again. |
| `append_unique` | `event_id`, `content`. The ID starts with `gov-` and is followed by 3–128 allowed characters. Content starts with a standalone `## <event_id>` line. The same ID and body are not appended twice; the same ID with a different body is a conflict. |
| `compare_exchange` | `expected_sha256`, `content`. Compare the target's current raw-byte hash. A mismatch is a conflict unless the content is already at the requested target state. |

An owner with `path_pattern` also requires a `target_variables` object whose keys match the pattern placeholders. For example, `docs/governance-log/{period}.md` uses `{"period":"2026-09"}`; choose the period from the actual event rather than copying the example.

Put all projections needed for one change in a single request and call `apply` once. The successful receipt's `status`, `terminal_projection`, `changed_owners`, `files_written`, and `writeback` are the unified result. Do not recheck each file or create another log transaction afterward. Do not call the runner just to get a receipt when there is no change.

## Recovery And Concurrency

Keep the actual failure receipt, journal, and recovery paths. `recover` handles only a genuinely unfinished transaction; it does not decide how to resolve an external edit conflict. If recovery is unsafe, report the conflict. Do not overwrite later edits or automatically replay the request. If using `--state-root`, use the same authorized directory for `apply`, `recover`, and `benchmark`. The default state directory is separate from source files; do not copy machine receipts into human-readable logs.

On Windows, per-file replacement and rollback use `ReplaceFileW` and verify the displaced version. A conflict can be detected after a target path briefly contains candidate content, and multi-file readers do not receive an atomic snapshot. Receipts may report partial writes or an unknown write count. If `ReplaceFileW` returns error 1177, the target, backup, and temporary file may be in an intermediate state: preserve the paths named in the receipt, reconcile them manually, and do not treat the error as no change. Non-Windows concurrent writes and recovery are unverified.
