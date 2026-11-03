# Skill map

| Skill | Group | One line |
|---|---|---|
| [project-design](../../project-design/README.md) | build | PRD → design, decision log, task plan |
| [delivery-pipeline](../../delivery-pipeline/README.md) | build | planner/implementer/reviewer agents work a task backlog |
| [create-feedback-form](../../create-feedback-form/README.md) | build | in-app feedback form recipe |
| [create-knowledge-base](../../create-knowledge-base/README.md) | repo setup | `.agents/` knowledge base for a repo |
| [plan-tests-for-change](../../plan-tests-for-change/README.md) | testing | which tests a change needs |
| [review-tests](../../review-tests/README.md) | testing | audit a suite, open issues |
| [manual-tests](../../manual-tests/README.md) | testing | keep and run the manual test list |
| [test-run-report](../../test-run-report/README.md) | testing | run suites, commit a report |
| [usage-report](../../usage-report/README.md) | cost | spend and hours per project |
| [effort-estimator](../../effort-estimator/README.md) | cost | forecast cost/time (script, not a skill) |

## Typical chains
- New project: `project-design` → `delivery-pipeline` (per task: `plan-tests-for-change`).
- Onboard a repo: `create-knowledge-base` → creates `testing.md` that the testing skills read.
- Test lifecycle: `plan-tests-for-change` (new manual entries) → `manual-tests` ← `review-tests` (retire automated ones); `test-run-report` records runs and lists manual tests due.
- Budget: `effort-estimator` before, `usage-report` after.
