# Release Verification

This is `v0.1.0-preview.1`, evaluated on 2026-09-25. It delivers the method, templates, Skill and optional Windows tools with bounded evidence. It is not a claim of complete cross-platform or long-term reliability. Machine-readable results: [release-validation.json](../evidence/release-validation.json).

## Reproduce The Program Checks

On Windows with Python 3.14 and PowerShell, from the repository root:

```powershell
python -m unittest discover -s tools/governance-transaction/tests -p 'test_release*.py' -v
python -m unittest discover -s tools/governance-activation-guard/tests -p 'test_release*.py' -v
```

The exact exported package passed 5 transaction and 6 guard tests, with zero failures and zero skips. These cover final replacement and rollback conflicts, preserved recovery content, uncertain write receipts, managed-file uninstall boundaries, requirements restoration, legacy backup limits, blocked-completion rejection and current shell argument compatibility. Temporary states are used; the lifecycle test does not activate a live host gate. The 1177 test injects an error after a real Windows replacement, rather than claiming every native error state was reproduced. Non-Windows skips are not passes.

Two controlled installation rounds updated the actual runtime after checks; eight installed runtime files matched the accepted candidate, and 27 Skill files were backed up and updated. The second round fixed a compatibility issue found by the source-review task. Old installation evidence was preserved. Read [installation and recovery](runtime-tools.md) before enabling optional tools.

## Controlled Real Work

Three fresh Codex CLI sessions completed actual release work: source review, a caretaker handoff using the accepted review, and a single installed-runner transaction updating release status and one unique governance event. The main evaluator checked artifacts, file differences and the real receipt. Requested and recorded model were Astra low; Codex 0.155.0-alpha.16.4, memories disabled, global and local instruction injection observed. The handoff and writeback intentionally depend on earlier accepted work; these are not independent repetitions of one benchmark. No additional model reruns or comparisons were performed.

| Task | Accepted result | Seconds | Tool calls | Input tokens | Cached input tokens | Output tokens |
| --- | --- | --- | --- | --- | --- | --- |
| source | pass | 203.77 | 7 | 352171 | 281216 | 3534 |
| handoff | pass | 214.95 | 6 | 269754 | 204672 | 3968 |
| writeback | pass | 80.54 | 4 | 109244 | 82944 | 840 |

Input totals are cumulative API-reported usage; cached input is part of input, not additional input. These values cover the three sessions, not implementation, subagents or this entire delivery. No cost advantage or quality non-inferiority versus an unguided agent is established. The writeback used one apply and produced two projections with one log event; its preliminary protocol discovery still required three commands. The result collector failed only while printing a Unicode summary after saving the valid result, and was corrected without redoing the write.

The source review found inconsistent optional-bridge wording, mixed preview/full-acceptance criteria, missing Python dependency documentation and an unhandled `cmd` field. Those findings were accepted and repaired. The handoff used the corrected candidate and retained the original findings as history. Final publication-only additions are this evidence summary, release links, byte-preserving Git attributes and an explicit discontinued warning on an unlinked historical rule reference; runtime code is unchanged from the accepted installation.

## Remaining Boundaries

The manual host guard remains optional and experimental: live activation, restart loading and compaction recovery have not been measured. Repair scope is a human/agent agreement, not a general command sandbox. Windows concurrency handling preserves an atomically displaced edit and reports a conflict; it does not promise zero temporary overwrite or multi-file snapshot isolation. A legacy installer cannot restore original configuration it never backed up. macOS/Linux runtime behavior, long-term use across unrelated projects, and comparative token/quality benefits remain unverified.

GitHub Actions runs the same release checks on Windows. Its actual run status is available in the repository Actions tab; configuration alone is not CI evidence. `release-manifest.json` identifies the exact published bytes. Git attributes preserve those bytes without line-ending normalization. Private source history, raw conversations, runtime backups and retired planning files are not distributed. Actual evaluation dates are retained; the current release is not presented as a July/August source snapshot.
