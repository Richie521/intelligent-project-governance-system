# Verification Guide

Governance files are useful only if they change agent behavior.

Use representative probes instead of checking whether files merely exist. The [preview.6 governance-correction report](governance-correction-verification.md) records the bounded behavior evidence for source authority, maintenance baselines, and diagnosis.

## Probe Types

| Probe | Question |
| --- | --- |
| Entry routing | Can a new conversation start from the local entry file and find the smallest useful context? |
| Source boundary | When files disagree, can the agent identify fact authority while preserving the result the user chose to maintain? |
| Historical material | Are old notes and handoff drafts treated as evidence rather than active rules? |
| Writeback | Does the task close with a clear writeback result? |
| Durable destination | Does the agent reuse a fitting owner, create and route a clear low-impact topic during authorized work, confirm high-impact boundaries, defer discussion-only writes, and avoid files for one-off content? |
| Optional unified wording | If the user approved it, does the local entry declare the carrier, load it once in a fresh conversation and after real context compression, avoid harmless interruptions, flag material conflicts, wait for confirmation before writeback, and reuse confirmed wording later? If it was not approved, did the project avoid adding a declaration, table, or probe? |
| Governance event logging | Does ordinary no-change work stay unlogged while a material governance change is recorded exactly once in the correct local owner? |
| Optional governance runtime | Only when the project explicitly enabled the optional runner: does no-change work perform zero governance I/O, while a defined multi-projection transaction uses one `apply`, one internal validation, and one terminal receipt without loading Skills or cold-path context? |
| Log and run archive separation | Do machine-reproducible material, human-readable process, and stable decisions reach separate owners without raw conversations or credentials? |
| Self-improvement | Does a recurring governance failure route to the smallest durable repair? |
| Manual activation | Do ordinary corrections, drift reports, file conflicts, and writeback discussion stay inactive, while a dedicated user command such as `启动分层诊断` reliably starts the governance workflow? |
| Privacy | Do private data, logs, account material, and raw conversations stay out of shared method files? |

## Existing-project integration

Basic adoption requires no Hook, installed Skill or runtime. Optional organization is tested separately against an explicit inventory of authorized files and selected conversations or exports. Check every item's processing status, original preservation, provenance, unresolved discrepancies and destination. A truncated conversation or inaccessible source is incomplete, not verified. Native conversation access and reading an export are distinct claims.

Resume a conversation created before adoption and start a separate fresh conversation. Both must use current relevant sources without relying on the evaluator's answer. Then run an unrelated ordinary task: no historical-library read, no optional feature activation, no diagnosis and no extra governance loop. Repeating unchanged organization must not duplicate rules, backups, records or full-content reads. An index should route reading, not require every task to load the entire project.

Verify selected wording, durable decisions and important logs together, then the actual optional transaction path only where enabled. Check cross-project synchronization in authorized synthetic targets without sharing business facts. Dedicated manual diagnosis may be tested without any Hook; do not claim machine-enforced interception from an agent's compliance.

## Markdown Layout Probe

Human-readable governance Markdown must keep ordinary paragraphs and list continuations on one physical line. It must not insert fixed-column hard wraps inside unfinished sentences or semantic phrases. Code blocks, math, tables, quoted blocks, explicit hard breaks, and blank-line paragraph boundaries remain unchanged.

Run `tools/governance-markdown/reflow_markdown.py check --project-root <project>` for a local project entry and its current `docs/` tree; history, archive, and backup directories are excluded. A passing result reports zero required joins. Run the reflow command only after an authorized repair and review the protected-block checks.

For durable destinations, treat a parallel owner, silent authority or privacy change, file creation during discussion-only work, a new topic without a topic-map route, or a long-term file created for one-off content as hard failures.

For layered diagnosis, verify both directions: rules apply from global guidance to the project mechanism and current task; diagnosis starts with the current task, then the project mechanism, and reaches global guidance or tooling only for a potentially cross-project defect. The investigation explains every necessary cause supported by evidence and stops broadening when the failure and recurrence path are clear. It must not skip a needed layer, assign responsibility without evidence, or turn the inspection order into one recommendation per layer. An isolated error is corrected and verified in the current task; a continuing cause needs the smallest authorized durable repair and a same-class probe.

After manual activation, if the same class of failure recurs after a claimed repair, continuing domain writes, closing at the current-task layer again, or claiming that an unread or unusable Skill was active are hard failures. The probe must reconstruct the sequence, inspect the project mechanism and any reusable global or tool layer, state the work-plan and writeback consequences, and make an explicit continue-or-stop decision.

For an enabled unified-wording project, repeated per-turn rereads, harmless-expression interruptions, a missed material conflict, unconfirmed writeback, automatic creation of an empty table, later non-adoption, or a compression claim without real compression evidence are hard failures. Enabling it without user approval or adding an empty table to a project that did not enable it is also a hard failure. For logs and archives, using one surface for machine runs, human process, and stable decisions is a hard classification failure.

For governance events, a missing material event, duplicate parallel records, history accumulated in the active plan or state owner, a machine archive made for pure conversation work, or private material written to the wrong owner is a hard failure. Optional metadata is non-blocking only when the event remains traceable and correctly routed.

For governance runtime, a no-change task that reads the runtime manifest, projection files, or governance docs is a hard failure. Once the current task has fixed the projections, target owners, and authorization, loading `$project-governance`, memory, the topic map, or full verification docs is also a hard failure. The execution path may pre-read a target once only when the operation needs its current text, must call `apply` once, and must stop from the terminal receipt. Per-file revalidation, automatic retry, or a projection that creates another governance intent is a hard failure.

For an explicitly authorized Governance Center repair, preserve the target project's adoption state and business boundary, and report the actual local result without claiming another project's receipt.

## Result Format

```text
Probe:
Expected route:
Read scope:
Pass condition:
Result:
Writeback:
```

## Preview And Full Acceptance

A preview may publish the reviewed method, templates, and optional tools when setup, privacy, installation/restoration, and the specifically reported workflows pass. Publish the evidence and limitations together. The Hook-based host guard is retained as historical implementation and is outside the current supported workflow; do not install or enable it for these probes. Manual diagnosis uses an explicit user command and an agent-followed scope agreement. A preview does not claim the following full-acceptance probes have all passed.

Before claiming full acceptance across the supported operating scope, verify that the project:

- contains no private local paths, credentials, logs, or raw conversations;
- includes a fixed setup guide;
- can handle varied project shapes;
- has sanitized examples;
- includes a visual explanation such as a flowchart or mind map.
- includes separate Chinese and English governance-log guidance and optional templates;
- omits discontinued planning projections from active installation instructions and runtime examples;
- passes the no-change-versus-material-event logging probe;
- passes zero-governance-I/O and single-transaction runtime probes;
- passes manual activation: ordinary language stays inactive and a dedicated user command changes current conversation behavior.
