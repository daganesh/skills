# Testing skills: shared concepts

Applies to: [plan-tests-for-change](../../plan-tests-for-change/README.md), [review-tests](../../review-tests/README.md), [manual-tests](../../manual-tests/README.md), [test-run-report](../../test-run-report/README.md), and the test section of [create-knowledge-base](../../create-knowledge-base/README.md).

## Shared vocabulary
Levels: unit, component, multi-component, e2e. Risk: low/medium/high. Rule: cheapest sufficient level. Defined in `references/test-strategy.md`.

## Files in a target repo (not here)
- `.agents/knowledge/testing.md`: commands, level locations, baseline. Template: [testing-knowledge-template](../../review-tests/references/testing-knowledge-template.md).
- `.agents/manual-tests.md`: owned by `manual-tests`.
- Run reports: written by `test-run-report`.

## Duplication to know about
- `plan-tests-for-change/references/{test-strategy,playbooks}.md` and `review-tests/references/{test-strategy,playbooks}.md` are byte-identical copies. Edit both together (check with `diff`).
- `manual-tests` and `test-run-report` have no `references/`; their SKILL.md points at `../review-tests/references/test-strategy.md`. That link breaks if a skill is copied alone into `~/.claude/skills/`; install the testing skills together.
- `delivery-pipeline/SKILL.md` has its own short "Test levels" section; keep it consistent with `test-strategy.md`.
