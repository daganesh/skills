---
name: plan-tests-for-change
description: When a component, feature or code change is added, decide which tests should be added or extended, at which level (unit, component, multi-component, e2e), in which file, and which behaviors need a manual test instead. Use before or after implementing a feature, for a bug fix that needs a regression test, or when asked what tests a change needs. Prefers extending existing tests over adding new ones.
---

# Plan tests for a change

Goal: the smallest set of tests that gives real confidence in the change, at the cheapest sufficient level, placed where the repo expects them, with the rest recorded as manual tests.

Read first: `.agents/knowledge/testing.md` (commands, level locations, placement, canonical examples, budget), `references/test-strategy.md` (levels, risk levels, decision rule, regression rule) and `references/playbooks.md` (easy-to-miss behaviors by domain). If the knowledge file is missing, say so and derive what you need from the repo.

## Steps

1. **Scope the change.** Use the git diff against the base branch, a branch name, or the feature description the user gives. Ask only if none exists. If the change fixes a bug, get the bug's reproduction steps too.

2. **List the behaviors.** Write each changed or new behavior as one line: "When X, then Y" in terms of user-visible or API-visible outcomes. Skip refactors with no behavior change, styling and framework boilerplate. For each behavior, give a risk level (low, medium, high) using the definitions in `test-strategy.md`. Check the relevant playbooks in `references/playbooks.md` for behaviors the diff may affect but does not obviously show.

3. **Check existing coverage.** For each behavior, search for tests that already exercise it (by code paths touched, titles, assertions) and note their level and file. Use an existing coverage report if one exists; do not run the full suite unless needed.

4. **Decide per behavior** using the decision rule:
   - already covered adequately: no new test
   - covered but not this case: extend that test or add a case to it
   - not covered and automatable: new test at the cheapest sufficient level
   - not covered and not practically automatable: manual test (add it to `.agents/manual-tests.md` via the `manual-tests` skill)
   Say explicitly when a higher-level test is not needed because a lower one covers the risk.

5. **Design the cases.** For each new or extended test, name the technique that picks its inputs (equivalence partitioning, boundary values, decision table, state transition, CRUD, error guessing) and list the concrete values, e.g. "boundary values: 7, 8, 12, 13 characters."

6. **Place each new test.** Give the file path and name following the placement conventions in `testing.md`, and the canonical example to copy from. Mention needed helpers or factories that already exist.

7. **Regression tests for bug fixes.** Apply the regression rule from `test-strategy.md`: the test must fail without the fix and pass with it. State how you verified this (for example, run it against the parent commit's production code). A bug fix without this check is not covered.

8. **Apply the budget.** Default at most 4 new tests (or the repo's setting). If the plan exceeds it, rank by risk level first (high before medium before low), then by likelihood, and say which were dropped and why. Dropped high-risk behaviors must be called out explicitly and may need a manual test instead. A new e2e test needs a named critical journey.

9. **Present the plan** as a short table: behavior, risk, decision (covered / extend / new / manual), technique, level or manual entry, file, reason. Add one line on any risk left uncovered. Offer to write the tests and manual entries; do not write them unless asked. The plan belongs in the PR description, not in a committed file.

## Rules

- Never propose a test only because a file changed. Every test must guard a named behavior.
- Prefer extending over adding; prefer lower levels over higher ones.
- Every high-risk behavior ends up as a test, a manual test, or an explicit stated gap.
- Do not edit production code or existing tests in this skill.
