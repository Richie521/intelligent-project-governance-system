# Topic Map

Use this file as a router. Do not read every linked document by default.

| Problem type | Primary context | Read only if needed | Writeback target |
| --- | --- | --- | --- |
| What this project is | `README.md` | `docs/10-decisions.md` | `README.md` |
| Governance language selection or mismatch | `AGENTS.md` | intake evidence and language-matched templates | `AGENTS.md`, intake report |
| File roles and authority | `docs/01-source-of-truth.md` | relevant source files | `docs/01-source-of-truth.md` |
| Local context rules | `AGENTS.md`, `docs/02-context-management.md` | `docs/10-decisions.md` | `AGENTS.md`, `docs/02-context-management.md` |
| Governance events and log routing | `docs/04-governance-log.md` | actual monthly, development, or domain log | actual log owner |
| Durable knowledge has no suitable destination | `docs/02-context-management.md`, `docs/01-source-of-truth.md` | relevant topic docs | existing owner, or a focused topic file plus this map |
| Durable decisions | `docs/10-decisions.md` | relevant topic docs | `docs/10-decisions.md` |
| Governance event logging or machine evidence | local logging policy or existing log owner | relevant run archive and decision/state owner | existing local log owner, or an approved focused governance log |
| Naming, copy, explanation, confirmed wording, or a material wording conflict in a project with user-approved unified wording | declared wording surface | relevant product or decision source | declared wording surface after user confirmation |
| Example-specific question | relevant example or topic doc | source files after scope declaration | relevant local doc |

If no row fits, first decide whether the result is durable and whether an existing file can own it. During authorized execution, create a focused topic file and update this map in the same turn only when its responsibility and path are clear and authority, privacy, and long-term governance structure do not change. Confirm high-impact changes first. During discussion-only work, report the proposed file as deferred. Do not create a long-term file for one-off content.
