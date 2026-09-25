# Publication Checklist

Use this before creating or updating a public GitHub repository.

## Scope

- [ ] Public project root is separate from the private working root.
- [ ] Git repository is initialized only in the public project root.
- [ ] Repository visibility is confirmed before publishing.
- [ ] License is selected and added.
- [ ] Global agent bridge is documented and does not contain private local rules.

## Privacy

- [ ] No local absolute paths.
- [ ] No private project names.
- [ ] No personal email addresses.
- [ ] No credentials, tokens, cookies, or account identifiers.
- [ ] No raw logs, caches, machine archives, or runtime state.
- [ ] No raw conversations or internal handoff prompts.

## Usability

- [ ] English README explains the user problem and value.
- [ ] Chinese README exists.
- [ ] Quickstart is fixed and easy to follow.
- [ ] Quickstart includes the global agent bridge step.
- [ ] Skill prototype location and boundaries are documented.
- [ ] Global Skill installation uses the current `$HOME/.agents/skills` path.
- [ ] Discontinued planning templates and projections are absent from the active installation path; any retained historical depiction is labeled as inactive.
- [ ] Event-triggered logging guidance and separate Chinese and English optional templates are documented.
- [ ] Templates are usable without private context.
- [ ] Examples are sanitized.
- [ ] Flowchart or mind map explains the method.

## Verification

- [ ] Entry routing probe passes.
- [ ] Source boundary probe passes.
- [ ] Historical material probe passes.
- [ ] Privacy probe passes.
- [ ] Writeback probe passes.
- [ ] Governance Markdown checker reports zero required joins for public templates and Skill sources.
- [ ] Ordinary corrections and governance discussion leave manual layered diagnosis inactive; the dedicated user command activates it.
- [ ] No-change work stays unlogged and a material governance change is recorded exactly once in the correct local owner.
- [ ] Host activation evidence is reported separately from isolated lifecycle tests. Only a dedicated user command activates layered diagnosis; ordinary missed requirements, execution drift, file conflicts, or possible writeback do not activate it. If host activation has not been measured, the optional guard remains experimental.
