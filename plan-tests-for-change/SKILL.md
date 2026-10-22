---
name: plan-tests-for-change
description: When a component, feature or code change is added, decide which tests should be added or extended, at which level (unit, component, multi-component, e2e) and in which file. Use before or after implementing a feature, or when asked what tests a change needs. Prefers extending existing tests over adding new ones.
---

# Plan tests for a change

Goal: the smallest set of tests that gives real confidence in the change, at the cheapest sufficient level, placed where the repo expects them.

Read first: `.agents/knowledge/testing.md` (commands, level locations, placement, canonical examples, budget) and `references/test-strategy.md` (levels, decision rule). If the knowledge file is missing, say so and derive what you need from the repo.

## Steps

1. **Scope the change.** Use the git diff against the base branch, a branch name, or the feature description the user gives. Ask only if none exists.

2. **List the behaviors.** Write each changed or new behavior as one line: "When X, then Y" in terms of user-visible or API-visible outcomes. Skip refactors with no behavior change, styling and framework boilerplate.

3. **Check existing coverage.** For each behavior, search for tests that already exercise it (by code paths touched, titles, assertions) and note their level and file. Use an existing coverage report if one exists; do not run the full suite unless needed.

4. **Decide per behavior** using the decision rule:
   - already covered adequately: no new test
   - covered but not this case: extend that test or add a case to it
   - not covered: new test at the cheapest sufficient level
   Say explicitly when a higher-level test is not needed because a lower one covers the risk.

5. **Place each new test.** Give the file path and name following the placement conventions in `testing.md`, and the canonical example to copy from. Mention needed helpers or factories that already exist.

6. **Apply the budget.** Default at most 4 new tests (or the repo's setting). If the plan exceeds it, rank by risk (likelihood x damage) and say which were dropped and why; ask only if dropping looks risky. A new e2e test needs a named critical journey.

7. **Present the plan** as a short table: behavior, decision (covered / extend / new), level, file, reason. Add one line on any risk left uncovered. Offer to write the tests; do not write them unless asked. The plan belongs in the PR description, not in a committed file.

## Rules

- Never propose a test only because a file changed. Every test must guard a named behavior.
- Prefer extending over adding; prefer lower levels over higher ones.
- Do not edit production code or existing tests in this skill.
