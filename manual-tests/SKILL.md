---
name: manual-tests
description: Keep the repo's list of manual tests (.agents/manual-tests.md) current, and when asked, present it to a human tester so they can run the manual tests one by one and record the results. Use when adding a manual test, retiring one that was automated, listing what a human should check before a release, or starting a manual test session.
---

# Manual tests

Goal: a single, git-tracked list of the behaviors that a human must check, kept accurate, and runnable by a human tester on request. The list lives in the repo at `.agents/manual-tests.md` so it survives sessions and is reviewed in PRs like any other file.

Read first: `references/test-strategy.md` (risk levels, when a behavior is manual). Read the list itself before changing it.

## The list

Path: `.agents/manual-tests.md`. If it does not exist, create it from the template below, commit it locally as its own commit, and tell the user.

Each entry is a block with a stable ID that is never reused:

```markdown
## MT-001 [high] Checkout shows the correct total in Hebrew RTL
- Behavior: when a cart with discounts is viewed in Hebrew, the total and discount lines are right-aligned and the currency sign is placed as the locale requires.
- Why manual: visual layout and reading direction; no reliable automated check at a reasonable cost.
- Preconditions: a test account with two discount codes.
- Steps:
  1. Switch the language to Hebrew.
  2. Add items and apply both codes.
  3. Open the cart and the checkout summary.
- Expected: all amounts and labels align right; the total matches the sum of the lines; no text overlaps.
- Added: 2026-10-25, commit abc1234.
- Last run: never.
- Automated by: (none)
```

Rules for entries:
- Risk level is required (low, medium, high), defined in `references/test-strategy.md`.
- Steps are concrete actions a person can follow without reading the code. Eight steps at most; split longer flows into two entries.
- Each entry names one behavior. Never record a result inside the entry except in "Last run".

## Maintaining the list

Other skills call this one. Run the matching action:

- **Add**: when `plan-tests-for-change` or a regression check decides a behavior is not practically automatable. Give it the next free ID, its risk level and a short "why manual" reason. Do not add a manual test for something a cheaper automated test can cover.
- **Retire**: when a behavior gets an automated test (for example after `review-tests` adds one). Delete the entry and write the replacing test's name in the commit message, so the history shows the handoff. Never delete an entry just because it is inconvenient to run.
- **Stale check**: when the code a manual test covers has changed (its behavior, screen or endpoint), set its Status to `review` and say why. A human confirms or rewrites it.
- **Header**: keep "Last updated" at the top of the file current (date and commit).

Commit list changes as a separate local commit. Ask before pushing.

## Presenting the list to a tester

Only when the user asks (for example "run the manual tests", "what should a human check before release").

1. Show the active entries sorted by risk (high first), then by last run (oldest first). Show ID, title, risk and last result.
2. Ask which to run: all high-risk, a chosen set, or one entry.
3. For each chosen entry, show the preconditions and steps, then ask the tester for the result: pass, fail, or blocked, plus a short note and any evidence (screenshot path or description).
4. Record the result in the entry's "Last run" line: date, result, tester name if given, and the run ID if a test run report is in progress (see `test-run-report`). Write results only after the tester gives them.
5. For a fail, ask whether to open a bug report or add the case to the regression plan. Do not create issues without approval.
6. End with a summary: run, passed, failed, blocked, and which high-risk entries are still not run.

## Rules

- Never mark a manual test as passed on your own. Only the tester's answer is recorded.
- Never run steps that change real user data, send messages or spend money unless the tester confirms the environment is a test environment.
- Keep the list short enough to run. If a release needs more high-risk manual checks than a tester can do in one session, say so rather than dropping them.

## Template

```markdown
# Manual tests

Last updated: <date> / <commit>

<entries in the format above, sorted by ID>
```
