# Skill map

| Skill | Group | One line |
|---|---|---|
| [project-design](../../plugins/develop/skills/project-design/README.md) | build | PRD → design, decision log, task plan |
| [delivery-pipeline](../../plugins/develop/skills/delivery-pipeline/README.md) | build | designer / test-builder / implementer / reviewer agents work a task backlog |
| [create-feedback-form](../../plugins/develop/skills/create-feedback-form/README.md) | build | in-app feedback form recipe |
| [create-knowledge-base](../../plugins/develop/skills/create-knowledge-base/README.md) | repo setup | `.agents/` knowledge base for a repo |
| [plan-tests-for-change](../../plugins/test/skills/plan-tests-for-change/README.md) | testing | which tests a change needs |
| [review-tests](../../plugins/test/skills/review-tests/README.md) | testing | audit a suite, open issues |
| [manual-tests](../../plugins/test/skills/manual-tests/README.md) | testing | keep and run the manual test list |
| [test-run-report](../../plugins/test/skills/test-run-report/README.md) | testing | run suites, commit a report |
| [usage-report](../../plugins/usage/skills/usage-report/README.md) | cost | spend and hours per project |
| [effort-estimator](../../effort-estimator/README.md) | cost | forecast cost/time (script, not a skill) |

## Typical chains
- New project: `project-design` → `delivery-pipeline` (per task: `plan-tests-for-change`).
- Onboard a repo: `create-knowledge-base` → creates `testing.md` that the testing skills read.
- Test lifecycle: `plan-tests-for-change` (new manual entries) → `manual-tests` ← `review-tests` (retire automated ones); `test-run-report` records runs and lists manual tests due.
- Budget: `effort-estimator` before, `usage-report` after.
