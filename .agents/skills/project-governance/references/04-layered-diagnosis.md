# Layered Diagnosis

Use this reference only after a dedicated user command activates layered diagnosis. Mistakes, dissatisfaction, friction, conflicts, and possible writeback misses alone remain ordinary task handling and do not load this reference.

## Diagnosis Order

Rules apply top-down: global guidance, project mechanism, current task. Diagnosis runs bottom-up so the smallest responsibility is checked first:

1. User input and current task layer. Check whether missing information, changed goal, unclear authorization, or a misunderstanding explains this instance, and whether a continuing mechanism could reproduce it.

2. Project mechanism layer. Check local entry rules, topic routing, source boundaries, verification, decisions, writeback rules, local logs, and local domain documents.

3. General agent behavior layer. Use this only when the defect may recur across unrelated projects and local evidence does not determine the repair, such as a shared skill route or common verification failure.

If multiple causes are necessary to explain recurrence, state their causal relationship. An execution error can coexist with an outdated project entry or a build path that restores bad output.

This order controls evidence gathering, not answer formatting. Stop broadening the investigation once the evidence explains the failure and identifies the recurrence mechanism. Do not force one cause, fill out every layer's status, infer responsibility for unexamined layers, or generate a recommendation for each layer. Tell the user the concrete failure, necessary continuing causes, and exact correction in connected prose.

## Prevention Contract

A diagnosis must go beyond naming the responsible layer. Explain the causal failure mechanism and whether the same class of failure could recur. For a continuing cause, define the smallest durable prevention plan:

- repair layer;
- durable change;
- recurrence barrier that breaks the failure chain;
- representative regression probe for the same class of risk.

Choose the repair surface by what interrupts the recurrence chain, even if this instance failed at another layer. One repair may need coordinated changes to an existing project entry and a build path when both sustain the same failure. An isolated error with no continuing cause can stop after current-task correction and verification; do not invent a persistent rule.

After a durable repair, run the regression probe under representative conditions and record its result, evidence, and limits. For a changed project entry or routing rule, verify adoption in a fresh conversation; for a changed script, run the affected operation and inspect its output. Do not claim durable prevention when only the current output is correct or when the prevention probe fails.

## Manual Repeated-Correction Gate

Do not enter full diagnosis automatically. After the user sends a dedicated manual activation command, a repeated failure requires pausing domain writes before the next mutation. Reconstruct the correction and failure sequence, inspect the current task and project mechanism, continue to global agent, Skill, or tooling only when the defect may recur elsewhere and local evidence is insufficient, state necessary writeback consequences, and make an explicit continue-or-stop decision.

Do not use this gate to build a persistent profile of user expression.

## Repair Target

Choose the smallest durable correction:

- current reply;
- current task plan;
- local project governance files;
- central method documents;
- adopted-project registry or sync status;
- global agent rules;
- Skill, plugin, MCP, script, or app.

For high-impact changes, explain the cause, proposed change, expected effect, and risk before seeking authorization. Existing authorization for that change remains valid; do not ask again.
