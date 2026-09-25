# Layered Diagnosis

Use this reference only after a dedicated user command activates layered diagnosis. Mistakes, dissatisfaction, friction, conflicts, and possible writeback misses alone remain ordinary task handling and do not load this reference.

## Diagnosis Order

Rules apply top-down: global guidance, project mechanism, current task. Diagnosis runs bottom-up so the smallest responsibility is checked first:

1. User input and current task layer. Check whether missing information, changed goal, unclear authorization, or a misunderstanding of the current request fully explains the issue.

2. Project mechanism layer. Check local entry rules, topic routing, source boundaries, verification, decisions, writeback rules, local logs, and local domain documents.

3. General agent behavior layer. Use this only for failures likely to recur across unrelated projects, such as poor uncertainty handling, over-reading, under-verification, acting without authorization, or treating rules as background instead of workflow.

If multiple layers contributed, separate them. Do not hide all responsibility inside one convenient layer.

This order controls evidence gathering, not answer formatting. Select exactly one primary root cause and record the inspection stop. The current task must be examined; do not skip a lower layer or continue above the stop. Mark each layer as `primary`, `contributing`, `ruled_out`, or `not_examined`. A ruled-out layer records only why it was excluded, and a not-examined layer records only why the investigation stopped. Neither receives a repair recommendation. A contributing layer is valid only with an explicit causal connection to the primary root.

## Prevention Contract

A diagnosis must go beyond naming the responsible layer. Explain the causal failure mechanism and the conditions that would let the same class of failure recur. Then define all four parts of the smallest durable prevention plan:

- repair layer;
- durable change;
- recurrence barrier that breaks the failure chain;
- representative regression probe for the same class of risk.

Create one prevention plan whose repair layer is the primary root-cause layer. Evidence-backed contributing layers may constrain that plan, but they do not receive separate advice lists or expand the repair by default.

After the repair, run the regression probe and record its result, evidence, and recurrence-control conclusion. Do not close the diagnosis when only the current output is correct or when the prevention probe still fails.

## Manual Repeated-Correction Gate

Do not enter the full gate automatically. After the user sends a dedicated manual activation command, a repeated failure requires pausing domain writes before the next mutation. Reconstruct the correction and failure sequence, inspect the current task and project mechanism, continue to global agent, Skill, or tooling only when the defect may recur elsewhere, state the active-plan and writeback consequences, and make an explicit continue-or-stop decision.

Do not use this gate to build a persistent profile of user expression.

## Repair Target

Choose the smallest durable correction:

- current reply;
- current task plan;
- local project governance files;
- central method documents;
- adopted-project registry or sync status;
- global agent rules;
- Skill, plugin, MCP, hook, script, or app.

High-impact changes require user confirmation.
