---
name: delivery-pipeline
description: "Use when the user wants to implement a whole task list / design doc / milestone plan using a multi-agent pipeline — e.g. \"implement the task breakdown\", \"work through the milestones\", \"spin up a planner, implementer and reviewer\", \"build this out with parallel agents\", \"run the delivery process\". Orchestrates three background agents (planner, implementer, reviewer) that plan complex tasks, open one PR per task, and independently review/fix/merge — modeled on mico's documented Delivery Process (docs/mico-implementation-design.md). Not for a single isolated bug fix or a one-off PR — use this only when there's a real backlog of tasks to work through."
---

# Delivery pipeline: planner + implementer + reviewer

Runs a repo's task backlog (a design doc's task table, a milestone plan, a GitHub issue list —
whatever the repo uses) to completion using three independent background agents instead of one
session doing everything serially. This is the coordinator's playbook — **you** (the invoking
session) stay in the loop the whole time: launching agents, relaying messages between them,
resuming them when they stop, and reporting status to the user. You never do the implementation
or review work yourself once this is running; that's what the subagents are for.

This mirrors the process this skill was extracted from: `docs/mico-implementation-design.md`'s
"Delivery Process: Commits, PRs, and the CI Gate" section, generalized beyond that one repo.

## Before launching anything

1. **Find the task source.** A task-breakdown table (ID, scope, dependencies) in a design doc
   is ideal — if the repo has one (grep for "task breakdown", "milestone", a table of IDs like
   `M1.1`/`T-042`/issue numbers), use it as-is: don't invent your own task list on top of it.
   If there's no such doc, ask the user what the task source is (a GitHub issue list filtered by
   label, a TODO file, a plain list they paste) before launching agents — the pipeline cannot run
   without a backlog to pull from.
2. **Check for existing automation.** grep recent PR/commit history and any CI workflow files for
   a bot or label-triggered automation already implementing this same backlog (mico had a
   `claude-implement` GitHub Action doing exactly that in parallel with this pipeline — see the
   note on "Check before you build" below). If one exists, tell the user and ask whether they
   still want a second, independent pipeline running, since the two can race or duplicate work.
3. **Confirm with the user**, briefly, before launching: what the task source is, the one-PR-per-task
   granularity, the PR cap per agent (default 3), and that it will merge PRs autonomously once CI
   is green (a real, hard-to-reverse action across potentially many PRs — get an explicit go-ahead
   for autonomous merging, not just autonomous implementing).
4. **Make sure `git`/`gh` are authenticated** and `git config http.version HTTP/1.1` plus a
   reasonable `http.postBuffer` are set if pushes have been flaky — a known failure mode is an
   HTTP/2 push truncation that looks like an auth error but isn't.
5. **Inventory the repo's actual test setup** before writing any agent prompt: which test levels
   below it already has real tooling for (unit framework, component/integration harness, a smoke
   check, a system/CLI-driven suite, an e2e framework like Playwright/Cypress), where each kind of
   test file lives, the exact commands CI runs for each, and the repo's own coverage/quality bar if
   it documents one (mico's review-gate checklist is one example — use the repo's own if it has
   one, don't substitute a generic bar for a documented one). This inventory is what you'll fill
   into every `<...>` placeholder about tests in the templates below — don't leave them generic
   when the repo already answers them.

## Test levels (shared vocabulary)

Every phase below (planning, implementing, reviewing) refers to these by name. Not every task
needs every level — the point is to *decide* which apply, not skip silently:

| Level | Tests | Typical scope |
|---|---|---|
| **Unit** | a single function/class in isolation; collaborators faked/mocked | almost every task with any logic in it |
| **Component / integration** | a module or service boundary, with cheap real collaborators where practical (e.g. an in-memory fake store instead of a real DB) — still fast, still offline | a task that introduces or changes a module boundary, a port/ABC implementation, a service class |
| **Smoke** | does the entrypoint even come up and respond at all (a CLI command runs with `--help`/a trivial invocation, a server boots and answers one request) | any new CLI command, API route, worker entrypoint, or script |
| **System** | cross-module behavior exercised through the real application wiring, still inside the test process/sandbox (no real browser, no real network) | a task whose correctness depends on several modules working together, not just one in isolation |
| **E2E** | the full external-facing flow through the real interface — real browser automation, a real CLI subprocess invocation, a request against a real (test) server | a task that changes or adds a user-facing flow (UI, CLI command a user types, a public API) |

## Identifying complex tasks (for the planner)

Not every task needs a plan. Send a task to the planner first when it's one or more of:
- a port/ABC definition other tasks will implement against (gets the contract wrong once, and
  everything downstream inherits the mistake)
- a task with many direct dependents in the task graph (a fan-in or fan-out point)
- explicitly flagged as complex/risky in the task source (a "spike", "flagged risk", etc.)
- touches concurrency, transactions, or a security/permission boundary
- large enough that one PR is unrealistic (note where to split it into sub-PRs)

Everything else, the implementer can scope and build on its own judgment.

## Orchestration loop

1. Launch the **planner** (see template below) for the complex tasks identified above. It is
   read-only and returns a written plan — save its output to a shared scratch file (your
   session's scratchpad directory) both agents below can read; don't rely on passing it through
   chat.
2. Launch the **implementer** and **reviewer** as background agents (`Agent` tool,
   `subagent_type: "fork"`, `isolation: "worktree"` for both — never let them work in your own
   checkout). Point the implementer at the plan file once it exists; it can start on
   non-complex tasks before the planner finishes.
3. **Relay between them as they stop.** Each agent is a single long *turn*, not a daemon — it
   stops when it hits its PR cap, finishes a review pass with nothing left, dies to a rate limit
   or an expired login, or finishes a planning pass. A task-notification fires each time. On each
   notification:
   - If the agent stopped *normally* (cap reached, nothing left to review): tell the other agent
     what changed (PRs opened / merged) and resume whichever one is now unblocked.
   - If the agent **died** (rate limit, login expiry, out-of-memory, etc.) and can still be
     resumed (`SendMessage` to its name/id succeeds): resume it with a note about what happened and
     to check its own worktree state before continuing.
   - If the agent died and **cannot** be resumed (`SendMessage` reports no reachable agent — this
     happens often; a dead subagent's worktree frequently survives even though the agent process
     doesn't): inspect its leftover worktree (`git status`/`git diff` in
     `<repo>/.claude/worktrees/agent-<id>/`) for salvageable uncommitted work, then launch a
     **fresh** replacement agent of the same role, instructing it to look at that worktree first
     and decide whether to finish that work or discard it — don't silently lose or silently
     resubmit unreviewed work.
4. **Never let two instances of the same role touch the same PR.** If you relaunch a reviewer
   while a PR is mid-review by another instance, tell the new one explicitly which PR(s) are
   off-limits. If you discover this already happened (two reviewers both touched one PR), get the
   in-progress one to hand off its findings to the one actually owning the PR rather than apply
   fixes itself.
5. **Re-sync with `main` at natural checkpoints**: before an agent starts a new task (fetch +
   merge/rebase), and again immediately before it merges a PR (someone else may have landed a
   dependency, or just unrelated work, in between).
6. **Stop condition:** no PRs open, the task source has nothing left unmerged, and a couple of
   idle polling passes from the reviewer confirm it. State this to the user plainly rather than
   continuing to relaunch agents with nothing to do.

## Known pitfalls (from running this for real)

- **Check before you build.** On a long-running pipeline, re-verify against `origin/main` before
  resuming after any gap — other automation (a separate bot, another session, a teammate) may
  have already finished some or all of the remaining backlog. An implementer that discovers its
  in-progress work duplicates something already merged should refuse to push it and say so,
  not force it in.
- **A reviewer must not poll via a detached background shell.** An agent that starts a
  `run_in_background` sleep-loop and then ends its own turn is reported "completed" immediately —
  it never actually watches anything. Polling must happen as repeated *foreground* waits inside
  one continuous agent turn.
- **Rate limits and login expiry kill the whole agent process**, not just the in-flight tool
  call — sometimes resumable, sometimes not (see step 3 above). Don't assume either outcome;
  check.
- **Stash safety:** a dead agent's worktree is shared stash-stack state with everything else on
  the machine — never run a bare `git stash`/`git stash pop` to inspect or recover one; use
  `git status`/`git diff`/a tagged `git stash push -u -m "<tag>"` if you must set something aside.
- **CI flakiness isn't the same as a red build.** A repo may have one known-flaky required check
  (mico's `review-gate` had a structured-output bug and was explicitly made non-blocking) — know
  which checks on this repo are like that *before* telling the reviewer what "green" means, don't
  guess.
- **Green CI with vacuous tests is not "done."** A passing test suite only means something if the
  tests themselves would fail on a real regression — tests written after the fact to match
  whatever the code already does, or asserting against a mock of the exact thing under test, pass
  trivially and prove nothing. This is why the reviewer template includes an explicit
  vacuous-test check and a red-green spot check, not just "make sure tests exist."

---

## Agent prompt templates

Fill in the bracketed placeholders from the repo's actual docs/conventions before launching. Keep
the structural instructions (caps, no-stacking, worktree isolation, attribution) as-is — they're
load-bearing, not cosmetic.

### 1. Planner

```
subagent_type: "Plan" (or "fork" if you want it to inherit this conversation's context)
isolation: not needed (read-only)
model: consider "opus" for genuinely hard design tasks

Prompt:
You are the PLANNER in a pipeline for the repo at <repo path>. An implementer agent builds one
task per PR; you produce implementation plans for the complex tasks in advance so it can build
faster and more consistently. You are read-only — you cannot edit files; return each plan as text.

Read <task-source-doc(s)>, <architecture-decisions-doc>, <PRD/requirements-doc>, and
<knowledge-base / README> plus the existing code under <source dirs> (state which tasks are
already merged, so plans match real interfaces and conventions, not guessed ones).

Produce plans for these tasks, in dependency order: <list of task IDs/names judged complex>.
Also flag any other task you judge complex enough to need a plan, with a one-line reason.

For each plan, work TDD-style: express the goal and acceptance criteria **as tests first** —
name the actual test cases (one line each: "test_X rejects Y when Z") that would prove the task
done, derived directly from the acceptance criteria, before sketching the implementation that
would satisfy them. Then give: files/modules to create or change (real paths, matching this
repo's layering/module conventions); key class/function signatures; data model/schema/migration
details if relevant; ordering of sub-steps; edge cases and failure modes (each must map to a named
test case from your list, not just be mentioned in prose); which test levels apply from the
shared taxonomy above and why the others don't (most tasks need unit + component; add smoke for a
new entrypoint, system for cross-module behavior, e2e for a user-facing flow — don't default to
unit-only out of habit); the actual test file paths/fixtures to add or extend, matching this
repo's test layout; risks, open questions, and the reasonable default decision for each (state it,
don't leave it open); and how to split into smaller PRs if the task is too large for one — a
sub-PR boundary must still carry its own tests, not defer them to a later sub-PR. Be concrete and
grounded in the actual code, not generic. Return everything as one document with a section per
task.
```

### 2. Implementer

```
subagent_type: "fork"
isolation: "worktree"   # never let it work in your own checkout

Prompt:
You are the IMPLEMENTER in a two-agent pipeline (a separate REVIEWER agent reviews and merges
PRs independently; do not review or merge PRs yourself).

Loop over tasks from <task-source-doc>: read it, <architecture/requirements docs>, and
<knowledge-base/README> for conventions, test/lint/build commands, and layering rules.

1. `git fetch origin`; pick the lowest-numbered/highest-priority task not yet on origin/main and
   not already covered by an open PR (check `gh pr list --state all` and branch names), whose
   dependencies are all merged into origin/main. If a task's only unmet dependency is an open,
   unmerged PR, either pick a different task or stack on that branch (prefer picking a different
   task, to avoid the stacking hazard below).
2. Branch from origin/main as <branch naming convention, e.g. feat/<id>-<slug>>. For a task the
   planner covered, follow its plan file at <path> — including its named test cases and which test
   levels apply — and flag any deviation in the PR description. For a task without a plan, work out
   the same thing yourself before writing implementation code: name the test cases the acceptance
   criteria imply, and which of unit/component/smoke/system/e2e (see the shared taxonomy) apply to
   this task; note the reasoning in the PR description.
3. Work test-first where practical: write a test (or its skeleton/assertions) for a unit of
   behavior before or alongside the code that satisfies it, not after the fact as a rubber stamp
   on code you already believe works. Implement every test level you identified in step 2 — not
   just unit tests by default:
   - **Unit**: every new function/class with real logic.
   - **Component/integration**: every new module boundary or port/ABC implementation, against a
     fake/in-memory collaborator if a real one is slow or external.
   - **Smoke**: a new CLI command, API route, or entrypoint — at minimum, prove it starts and
     responds without crashing.
   - **System**: cross-module behavior the task introduces or changes, exercised through the
     real wiring (not a single class in isolation).
   - **E2E**: a user-facing flow the task adds or changes, through the real interface.
   Cover the failure/edge cases named in the plan (or that you identified yourself), not just the
   happy path — an untested failure path is exactly where a silent regression hides. Match this
   repo's existing test style/location/naming conventions; run the exact local checks CI runs
   (<list: lint, typecheck, tests, layer-check, build, …> — find exact commands in the CI workflow
   file or repo docs) and make them green.
4. Before committing, re-read your own tests with fresh eyes: does each one actually assert
   something meaningful tied to the real behavior (not `assert True`, not asserting on a mock you
   configured to return the expected value, not silently skipped/xfailed)? Would it fail if the
   implementation were wrong? If you're not sure, temporarily break the implementation and confirm
   the test catches it, then restore the fix — cheap insurance, especially for the test(s) covering
   the task's core acceptance criterion.
5. Commit (<this repo's commit message convention>), push with `git push -u origin HEAD`, open a
   PR titled <this repo's PR title convention> with a summary and a test plan that lists what you
   tested at which level and why (not just "added tests"). Use the attribution lines from your
   system reminders for commits/PR bodies.
6. Immediately move to the next task; do NOT wait for the reviewer.

Constraints: max <N, default 3> of your PRs open-and-unmerged at once — if you hit that, stop and
report. Never stack a new PR on another of your own unmerged branches once more than one is open
(GitHub auto-closes a stacked PR when its base branch's PR merges first, silently discarding it —
pick a different task instead, or explicitly re-open and retarget if it happens). Never merge
PRs, never force-push main, never skip hooks. If you discover the task you're about to build is
already done on origin/main (by other automation, or work you can't see from here), say so and
stop rather than pushing a redundant/conflicting version. Final report (under 200 words): PRs
opened (numbers, tasks), anything blocked, ambiguous, or already-done-elsewhere.
```

### 3. Reviewer

```
subagent_type: "fork"
isolation: "worktree"

Prompt:
You are the REVIEWER in a two-agent pipeline (a separate IMPLEMENTER agent writes tasks and opens
PRs; you review independently — do not implement new tasks yourself).

Within a single ongoing turn, loop: check `gh pr list --state open`. If PRs exist, review/fix/merge
them (steps below, oldest first). If none exist, wait with a short **foreground** sleep (not
`run_in_background`) and check again — keep looping across many iterations in this one turn
rather than ending early. Stop and report only after a generous number of empty passes (e.g.
15-20 minutes of real elapsed time with nothing new) or a real stopping condition (task source
fully merged).

For each PR:
1. Review with fresh eyes against <task-source-doc>'s entry for that task, <architecture/
   requirements docs>, repo conventions, and a plan file at <path> if that task was planned.
   Check: correctness, spec conformance, layer/module boundaries, security (secrets never
   logged/committed, injection-safe handling of untrusted input), no scope creep, and — the
   review-gate checklist this repo documents — <adapt from the repo's own CI/review-gate
   criteria if it has one; otherwise default to>: requirements coverage, no duplicate logic, no
   magic numbers/hardcoded strings (named constants), correct API shape for whatever
   interface/contract the task implements.
2. **Verify the tests are actually implemented, not just claimed.** The PR description saying
   "added tests" is not evidence — read the diff's test files directly:
   - Every acceptance criterion / named test case from the plan (or the task's stated
     requirements, if unplanned) has a real, corresponding test — not a TODO, not deferred to a
     later PR, not silently dropped.
   - Every test level identified as applicable (unit/component/smoke/system/e2e — see the shared
     taxonomy) is actually present, not just unit tests when the task clearly also needed a smoke
     or e2e test (a new CLI command with no smoke test, or a new user-facing flow with no e2e
     test, is a missing-coverage finding, not a nice-to-have).
   - Failure/edge cases are covered, not just the happy path.
   - **No vacuous tests**: nothing that asserts a tautology, asserts against a mock configured to
     return exactly what's being "checked", or is skipped/xfailed without a tracked reason. A test
     that would pass even if the implementation were deleted is worse than no test — it's false
     confidence.
   - **Spot-check that tests are real, not just present**, especially for the task's core
     acceptance criterion: run the test suite once as-is (should pass), then temporarily revert
     just the implementation change (keep the tests) and re-run — the relevant test(s) should now
     fail. Restore the implementation afterward. This "red-green" check is cheap and catches tests
     that were written to match the code rather than to verify the requirement; you don't need to
     do it for every single test in a large PR, but do it for whatever test covers the task's
     central claim.
   If coverage is missing or a test is vacuous, that's a blocking finding — fix it yourself (add or
   correct the test) the same as any other bug, don't wave it through because CI is green.
3. Check out the PR branch in your own worktree and run the full local checks (same list as the
   implementer's step 3).
4. Check CI: all required jobs must be green. <name any known-flaky/non-blocking check for this
   repo, e.g. "review-gate is known-flaky here (reason X) — its failure alone does not block
   merging; anything else red does.">
5. Fix problems yourself: commit fixes to the PR branch and push (new commits, no force-push, no
   `--no-verify`), then wait for CI to go green again. If the PR conflicts with main, merge
   origin/main into the branch and resolve. If a problem is a fundamental design flaw you cannot
   resolve confidently, leave a PR comment and do NOT merge — report it instead.
6. Re-fetch and confirm the PR is still up to date with origin/main immediately before merging
   (someone may have landed something in between). Post a brief review summary as a PR comment —
   including which test levels you verified and any red-green spot checks you ran — then merge
   with `gh pr merge <n> --squash --delete-branch` (adapt the merge style to this repo's actual
   history — squash vs merge-commit).

Git/gh are authenticated as <user>. Use the attribution lines from your system reminders on
commits. Final report when you do stop (under 200 words): per PR — merged / fixed what / blocked
why.
```
