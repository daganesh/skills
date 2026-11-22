# Testing skills: shared concepts

Applies to: [plan-tests-for-change](../../plugins/test/skills/plan-tests-for-change/README.md), [review-tests](../../plugins/test/skills/review-tests/README.md), [manual-tests](../../plugins/test/skills/manual-tests/README.md), [test-run-report](../../plugins/test/skills/test-run-report/README.md), all in the `test` plugin, and the test section of [create-knowledge-base](../../plugins/develop/skills/create-knowledge-base/README.md).

## Shared vocabulary
Levels: unit, component, multi-component, e2e. Risk: low/medium/high. Rule: cheapest sufficient level. Defined in `references/test-strategy.md`.

## Files in a target repo (not here)
- `.agents/knowledge/testing.md`: commands, level locations, baseline. Template: [testing-knowledge-template](../../plugins/test/skills/review-tests/references/testing-knowledge-template.md).
- `.agents/manual-tests.md`: owned by `manual-tests`.
- Run reports: written by `test-run-report`.

## Duplication to know about
- `plan-tests-for-change/references/{test-strategy,playbooks}.md` and `review-tests/references/{test-strategy,playbooks}.md` are byte-identical copies. Edit both together (check with `diff`).
- `manual-tests` and `test-run-report` have no `references/`; their SKILL.md points at `../review-tests/references/test-strategy.md`. All four live in the `test` plugin, so the link works when the plugin is installed. It breaks if one skill is copied alone into `~/.claude/skills/`.
- `delivery-pipeline/SKILL.md` has its own short "Test levels" section; keep it consistent with `test-strategy.md`.
- `create-knowledge-base` is in the `develop` plugin. It names the test skills but reads none of their files; when they are missing it tells the user to install `test@daganesh-skills`.
