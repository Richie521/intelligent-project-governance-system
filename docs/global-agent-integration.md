# Global Agent Integration

The Project Intelligent Governance Center works best when it has two layers:

- a lightweight global bridge in the user's global agent instructions;
- project-local governance files inside each adopted project.

The global bridge should not contain the full method. Its job is to tell the agent how to recognize projects that use this system and how to route work into the local project files.

## Why This Layer Matters

Without a global bridge, a new agent session may not know that project-local governance files should be read first. It may rely on chat history, broad file search, or stale memory before checking the project's actual entry rules.

With a global bridge, the agent can start from the right local authority while keeping global instructions small and reusable.

## What Belongs In Global Instructions

Global instructions should define only stable cross-project behavior:

- when a project declares adoption of this system, read the project's local entry file first;
- use the project's topic map only when the task is unclear or routing is needed;
- treat central method docs as guidance for governance, adoption, synchronization, verification, and self-improvement;
- keep project-specific business facts, private paths, logs, raw conversations, and runtime state out of global instructions;
- do not automatically apply a central pattern to every project;
- let rules apply from global guidance to the project mechanism and current task, but diagnose failures from the current task through the project mechanism to global guidance or tooling;
- let the user's latest instruction determine current work; historical plans are evidence only, and discontinued planning files are not read or used;
- use `$project-governance` for structural governance; ordinary corrections and governance discussion do not activate manual layered diagnosis, which requires a dedicated user command;
- only when the user approved unified wording and the local entry declares it enabled with a wording surface, read that surface once after the local entry in a new conversation and once after context compression; refresh only after it changes or for naming work, and raise only material semantic differences.

## What Belongs In Project Files

Project files should hold local reality:

- what the project is for;
- which files are authoritative;
- which files are generated, runtime state, reports, caches, historical notes, or private material;
- local topic routes;
- durable decisions;
- the local unified-wording declaration and its carrier, when one exists;
- project-specific writeback rules;
- local verification probes.

## Setup

Install the structural-governance Skill, `.agents/skills/project-governance/`, into `$HOME/.agents/skills/`. Then copy `templates/global-agents-snippet.md` into the user's global agent instructions and adapt the project templates inside each project that should use the system.

Keep the global bridge short. If a rule depends on one project's domain, runtime, data, users, logs, or private workflow, it belongs in that project instead of the global file.
