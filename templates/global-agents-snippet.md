# Project Intelligent Governance Center Bridge

When a project declares that it uses the Project Intelligent Governance Center and runs a local Project Intelligent Governance System:

- Start from the project's local `AGENTS.md`.
- Follow its `zh-CN` or `en` authoritative governance-language declaration. If adoption finds no valid declaration, infer only when the user's primary language and existing governance entry agree, ask once on conflict, and persist the confirmed value locally. Do not switch it because one later turn uses another language, or batch-translate business files.
- If the task is unclear, read the project's `docs/00-topic-map.md`.
- Only after the user approves unified wording and the local entry declares it enabled with a wording surface, read that surface once after the local entry in a new conversation and once after context compression; within the same context refresh only after it changes or for naming work, and raise only material semantic differences.
- Use the smallest useful context for the task.
- Treat project-local source-of-truth files and current implementation as higher authority than old chat history, memory, reports, or handoff drafts.
- Let the user's latest instruction determine the current work. Historical plans and handoff notes are evidence only. Do not read or use discontinued planning files.
- Handle ordinary corrections in the current task. An already-defined governance transaction with explicit projections, target owners, and authorization is a lightweight runtime path: do not load `$project-governance`, memory, the topic map, or full verification docs; pre-read a target at most once when required, call `apply` once, and finish from its terminal receipt. Use `$project-governance` for structural governance. Public-release work stays outside this routing.
- Use central method docs only for governance, adoption, synchronization, verification, migration, handoff, self-improvement, or public release questions.
- Do not store project-specific business facts, private paths, credentials, logs, raw conversations, runtime state, or generated outputs in global instructions.
- Do not automatically edit all adopted projects when a central method changes. Local adoption requires project-specific analysis and user confirmation.
- Keep ordinary governance Markdown paragraphs and list continuations on one physical line; do not introduce fixed-column hard wraps inside unfinished sentences or semantic phrases. Preserve code, math, tables, quoted blocks, explicit hard breaks, and blank-line paragraph boundaries.
- Rules apply from global guidance to the project mechanism and then the current task. Full layered diagnosis is manually activated only by a dedicated user command such as `启动分层诊断`; ordinary corrections and governance discussion do not open the gate. After activation, diagnose in the opposite direction: current task first, project mechanism second, and global guidance, Skill, or tooling only when the defect may recur across unrelated projects. Repair the smallest durable surface; promote a local lesson centrally only when it is genuinely reusable.
