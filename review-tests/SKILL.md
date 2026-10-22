---
name: review-tests
description: Review an existing test suite (backend and frontend) and turn the findings into a prioritized to-do list, grouped into proposed PR requests, then open GitHub issues for the ones the user approves. Use when asked to review tests, find redundant or missing tests, check test levels, or clean up a bloated suite.
---

# Review tests

Goal: a smaller, cheaper suite with the right tests at the right level. Output is a prioritized to-do list grouped into proposed PRs. Nothing is written to GitHub until the user approves.

Read first: `references/test-strategy.md` (levels, decision rule), `references/scoring.md` (findings, priority), `references/issue-template.md`.

## Steps

1. **Load knowledge.** Read `.agents/knowledge/testing.md` (and `testing-strategy.md` if present). If it is missing or thin, derive commands, level locations, fakes, placement and CI facts from the repo (package manifests, test configs, CI files), show the proposed content using `references/testing-knowledge-template.md`, and ask before writing it. Commit knowledge changes separately and locally.

2. **Inventory.** List every test (title, file, runner) for each package or layer. Classify each by level using the evidence rules in the strategy, not file names. Record runtime and per-file coverage if a report already exists or the test commands are cheap to run; otherwise say what was not measured. Write the inventory to `.agents/.cache/` (ensure it is git-ignored) and never commit it.

3. **Find signals** (see `references/scoring.md`): redundant, wrong level (too high or mocks internals), missing, brittle. Keep to findings that change cost, risk or trust; skip style nitpicks. Use evidence from code and tests, and from coverage or mutation data only when it already exists.

4. **Build the prioritized to-do list.** One item per action: id, action (Delete, Merge, Move down, Rewrite, Add), target tests or files, level, reason with evidence, impact, effort, priority. Show the top 15, say how many were left out, and add the area ranking (worst to best).

5. **Group into proposed PR requests.** Rules:
   - One PR request = one area and one kind of change (do not mix deletions with additions).
   - Small enough to review in one sitting (about 10 files or fewer).
   - Independent where possible; if not, state the order.
   - Each has: title, goal, items, expected effect (tests, runtime, coverage that must not drop), how to verify, risk.
   Present them in priority order.

6. **Approval gate.** Ask which PR requests to open as issues (multi-select; the user can also edit or drop items). Do nothing on GitHub before this answer.

7. **Open issues.** For each approved group, create one issue using `references/issue-template.md`, with items as a checklist. Use the git integration the repo already uses (GitHub MCP tools, else `gh`); if unsure, ask once. Before creating, search open issues for the same title or items and skip duplicates. Use only labels that already exist. Report the issue URLs.

8. **Update the baseline.** Update the short baseline block in `testing.md` (date, commit, counts per level, runtime, coverage) as a separate local commit. Ask before pushing.

## Rules

- Issues only: never push code, open PRs, delete tests or edit production code.
- Never commit the inventory. Save the to-do list as a file only if the user asks (`.agents/reports/test-review-YYYY-MM-DD.md`).
- State what could not be measured instead of guessing. Do not claim a test is redundant without naming the test or level that covers the same behavior.
- Prefer shrinking the suite: Delete and Move down rank above Add when priorities tie.
