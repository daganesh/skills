# project-design

Turns a PRD into a technical design, a numbered decision log and a task-table implementation plan. The value is the interview: it lists every open architecture decision and asks them one at a time with a recommended option.

- **Use when:** "design this project", "here is the PRD", "what stack should we use". Not for a small change in an already-designed codebase.
- **Steps:** intake → PRD review → decision list → ask → write design → write plan → self-review → hand-off.
- **References (read only what the step needs):** [`decision-catalog`](references/decision-catalog.md) (decisions by category), [`house-preferences`](references/house-preferences.md) (recommended defaults), [`project-profiles`](references/project-profiles.md) (per project type), [`output-templates`](references/output-templates.md) (doc skeletons).
- **Hands off to:** [`delivery-pipeline`](../delivery-pipeline/README.md) to execute the plan. Test levels in the plan match [`review-tests/references/test-strategy.md`](../review-tests/references/test-strategy.md).

Entry point: [`SKILL.md`](SKILL.md) · Up: [skills index](../README.md)
