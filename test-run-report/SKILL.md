---
name: test-run-report
description: Run the repo's automated test suites, write a report for the run (results per level, failures with their risk, coverage, runtime, manual tests due) and compare it with an earlier run so a human tester can review it. Use when asked to run the tests and report, to check a branch before review or release, or to compare two test runs.
---

# Test run report

Goal: every test run leaves a report in git that a human can review, and that can be compared with earlier runs. The skill runs and records; the human decides whether the run is acceptable.

Read first: `.agents/knowledge/testing.md` (exact commands per package and level, coverage command and report path, baseline), `references/test-strategy.md` (levels and risk levels). If `testing.md` is missing, derive the commands from the repo and ask before running anything long.

## Run

1. Record the context: branch, commit, date, machine (OS and runtime versions), and who asked.
2. Run each level's command from `testing.md`, in the order it lists. Use the repo's own commands; do not invent new ones. Capture the full output to `.agents/.cache/runs/<date>-<shortsha>/` (git-ignored) and keep the pass/fail counts, failing test names and runtime from it.
3. Run coverage only if the repo has a coverage command. If not, say coverage was not measured.
4. If a test fails, rerun that test once. Report both results. A test that fails once and passes on rerun is marked **flaky** and listed separately; it is never silently counted as passed.

## Report

Write two files to `.agents/reports/runs/`:

- `<date>-<shortsha>.md`: the human report, described below.
- `<date>-<shortsha>.json`: the same numbers in machine form, for comparison.

Both are committed (locally, as their own commit). Ask before pushing.

The markdown report, in this order:

```markdown
# Test run <date> / <shortsha>

Branch: <name> · Commit: <sha> · Machine: <os, runtime versions> · Requested by: <who>

## Summary
| Level | Passed | Failed | Flaky | Skipped | Total | Runtime |
|---|---|---|---|---|---|---|
| unit | | | | | | |
| component | | | | | | |
| multi-component | | | | | | |
| e2e | | | | | | |

Coverage: <percent per package, or "not measured">.

## Failures
For each failing test: name, file, level, the behavior it guards and that behavior's risk level. Order by risk (high first).

## Flaky
Tests that failed then passed on rerun: name, file, both results.

## Not run or not measured
Any level, package or metric that could not run and why.

## Manual tests due
Active entries in `.agents/manual-tests.md` that are high risk, or whose status is `review`, or that have never been run. Do not run them here; list them for the `manual-tests` skill.

## Compared with previous run
Previous run: <date / sha> (or "none, first run").
- New failures: <list>
- Fixed since last run: <list>
- Tests added / removed: <counts and names>
- Runtime change per level: <numbers>
- Coverage change: <numbers or "not measured">

## Review
- Reviewer: (blank until a human fills it in)
- Decision: (accepted / needs attention / rejected) (blank)
- Notes: (blank)
```

Leave the Review section blank. Only the human reviewer fills it in. The skill never sets the decision.

## Compare two runs

When asked to compare two runs (by date, sha or file name), read both JSON files and produce the same "Compared with previous run" block, with the first run as the baseline. Present the result in chat as a short table, and write it into the newer run's markdown file only if the user asks.

## Rules

- Never edit tests, production code or the manual list in this skill. Report only.
- Never claim a level passed if its command did not run. Say what was not run.
- Keep the report factual: numbers, names, files, commands. No judgement about quality beyond the recorded failures and flakiness.
- The JSON must include the same counts as the markdown summary. If they disagree, stop and fix the report before committing.
- Update the baseline block in `testing.md` only if the user asks for a baseline update.
