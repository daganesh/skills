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

For each plan give: goal and exact acceptance criteria; files/modules to create or change (real
paths, matching this repo's layering/module conventions); key class/function signatures; data
model/schema/migration details if relevant; ordering of sub-steps; edge cases and failure modes;
test plan (what must have failing-case coverage, not just happy-path); risks, open questions, and
the reasonable default decision for each (state it, don't leave it open); and how to split into
smaller PRs if the task is too large for one. Be concrete and grounded in the actual code, not
generic. Return everything as one document with a section per task.
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
   planner covered, follow its plan file at <path> and flag any deviation in the PR description.
   For a task without a plan, make the reasonable call yourself and note it in the PR description.
3. Implement with tests (match existing test style/coverage expectations), run the exact local
   checks CI runs (<list: lint, typecheck, tests, layer-check, build, …> — find exact commands in
   the CI workflow file or repo docs) and make them green.
4. Commit (<this repo's commit message convention>), push with `git push -u origin HEAD`, open a
   PR titled <this repo's PR title convention> with a summary and test plan. Use the attribution
   lines from your system reminders for commits/PR bodies.
5. Immediately move to the next task; do NOT wait for the reviewer.

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
   criteria if it has one; otherwise default to>: requirements coverage, test coverage (every new
   function/branch/public method has a corresponding test, including failing-case tests, not just
   happy path), no duplicate logic, no magic numbers/hardcoded strings (named constants), correct
   API shape for whatever interface/contract the task implements.
2. Check out the PR branch in your own worktree and run the full local checks (same list as the
   implementer's step 3).
3. Check CI: all required jobs must be green. <name any known-flaky/non-blocking check for this
   repo, e.g. "review-gate is known-flaky here (reason X) — its failure alone does not block
   merging; anything else red does.">
4. Fix problems yourself: commit fixes to the PR branch and push (new commits, no force-push, no
   `--no-verify`), then wait for CI to go green again. If the PR conflicts with main, merge
   origin/main into the branch and resolve. If a problem is a fundamental design flaw you cannot
   resolve confidently, leave a PR comment and do NOT merge — report it instead.
5. Re-fetch and confirm the PR is still up to date with origin/main immediately before merging
   (someone may have landed something in between). Post a brief review summary as a PR comment,
   then merge with `gh pr merge <n> --squash --delete-branch` (adapt the merge style to this
   repo's actual history — squash vs merge-commit).

Git/gh are authenticated as <user>. Use the attribution lines from your system reminders on
commits. Final report when you do stop (under 200 words): per PR — merged / fixed what / blocked
why.
```
