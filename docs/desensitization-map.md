# Desensitization Map

This file defines how the private working version is transformed into the public GitHub version.

## Public Boundary

The public version must be portable. It should not reveal a maintainer's local machine, private projects, account setup, raw logs, or conversation history.

## Mapping Rules

| Private/internal material | Public replacement |
| --- | --- |
| Local absolute project paths | `<project-root>`, `<method-home>`, or a relative path |
| Real adopted-project names | Generic example names such as `demo-project` |
| Real sync registry entries | A sanitized example registry or no registry entry |
| Raw conversations and handoff prompts | Short reusable principles or templates |
| Runtime logs and machine archives | A policy that explains where such files belong locally |
| Private governance-event history | Public logging rules and an empty localized template |
| Credentials, account identifiers, tokens, cookies | Omit entirely |
| Private tool state or editor state | Omit entirely |
| One-off migration history | A generic migration method or a sanitized example |

## Content Allowed In Public

- Core method principles.
- Reusable adoption steps.
- Generic templates.
- Sanitized examples.
- Verification probes.
- Privacy and publication rules.
- Visual explanations.
- Event-triggered logging rules and empty localized templates.

## Content Kept Private

- Real local path registry.
- Internal sync status for private adopted projects.
- Raw project conversations.
- Private account or network details.
- Runtime state, logs, generated outputs, caches, and temporary plans.

## Review Rule

Before publishing, scan the exact public file set for local paths, private project names, personal email, account material, secrets, raw logs, and raw conversation text.
