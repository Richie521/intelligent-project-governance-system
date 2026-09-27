# Earlier interactive adoption verification

This is the preserved preview.2 test record. Its unverified-platform statements describe that earlier batch; see the [current acceptance record](integration-verification.md) for subsequent native Windows, desktop and English evidence.

The interactive installer is a self-contained prompt, not a mandatory global Skill or Hook. It asks for missing target paths and meaningful preferences, preserves existing local rules, and reports file adoption separately from actual use in a fresh session. Start with [English](../INSTALL.md) or [Chinese](../INSTALL.zh-CN.md).

## Evidence and result

On 2026-09-26, six fresh-context retest turns used Codex CLI 0.157.1, gpt-6-astra with low reasoning, isolated user homes, and no injected governance Skill, Hook, plugin, or memory. Only the question-and-answer pair shared a conversation. Prompts came from one frozen archive; user answers supplied paths and preferences, not expected operations. Credentials were used only for authentication and removed after testing.

| Case | Observed result |
| --- | --- |
| Missing target, then user answer (2 turns) | Recognized the package directory, asked once, then installed one 1720-byte entry in the selected empty folder without repeated confirmation |
| Existing override and optional wording | Selected the effective override; preserved original bytes, UTF-8 BOM, CRLF, fallback entry and business sentinel; verified the exact backup |
| Repeated adoption | No file/hash changes, new backup or log; read effective entry content once and reused the inspection |
| Multiple targets with real write restriction | Installed one 1627-byte entry in the writable target; preserved the restricted target and reported it incomplete, without escalation |
| Ordinary task in a fresh session | Actual local instructions were present in session context; produced the exact requested file with one tool call and no governance loop |

The earlier batch had 12 turns and was not accepted for release: two CLI setup attempts failed, cross-OS inspection blocked an interactive install, a mixed-target sandbox mount failed, and redundant reads remained. Those results were retained. Native metadata checks and a known default instruction limit were introduced first; the final prompt then combined initial entry inspection and removed repeated reads on the no-write path. The mixed-target fixture was moved outside the sandbox's special temporary-directory mount and tested with a non-model command in the same sandbox before retrying. Actual write denial was observed, not simulated by a text instruction.

The earlier unchanged external-link boundary probe preserved the link and outside target, and two local-work probes demonstrated bounded use. The retest changed inspection reuse, not those authority or privacy boundaries. These are finite examples; they do not establish universal or long-term reliability.

## Cost and limitations

The six retest turns totaled 615.27 seconds, 365595 input tokens (310784 cached) and 7379 output tokens. Reasoning tokens, where reported, are an output breakdown rather than additional output. WSL DNS and transport retries contributed to elapsed time. All six stayed within the 240-second per-turn limit, and the reserve round was unused. No retest performed a web search. Full per-turn measurements and the retained first-batch totals are in [the evidence summary](../evidence/onboarding-validation.json).

Observed redundant reads were removed in the repeated-adoption example. We do not infer a token-saving percentage, equivalent quality against an unguided control, or production performance from different task runs. The installation prompt itself is larger than a minimal entry; entry sizes are not token measurements.

This onboarding acceptance covers WSL with Windows-mounted target folders. Native Windows and macOS onboarding, all reparse-point variants, English-language behavioral acceptance, arbitrary permission environments and long-term operation remain unverified. English and Chinese prompt contracts were statically reviewed for parity. Earlier native Windows runtime checks concern separate optional tools, not proof of this installation path. Basic adoption neither installs nor requires those tools or Hooks.

Private paths, credentials, raw conversations, experiment helpers and the current work specification are excluded from the release. The summary includes only environment versions, task labels, aggregate outcomes and usage. Existing project-specific rules still govern each folder; safe refusal is a valid outcome for a blocked target.
