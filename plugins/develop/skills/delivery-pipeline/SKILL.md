---
name: delivery-pipeline
description: "Use when the user wants to implement a whole task list / design doc / milestone plan using a multi-agent pipeline — e.g. \"implement the task breakdown\", \"work through the milestones\", \"spin up a designer, test builder, implementer and reviewer\", \"build this out with parallel agents\", \"run the delivery process\". Orchestrates four types of background agents (designer, test-builder, implementer, reviewer): the designer writes a detailed design + test plan, the test-builder (TDD) and implementer then work in parallel from that design, and an autonomous reviewer verifies tests pass and the code meets the standards before merging one PR per task — modeled on mico's documented Delivery Process (docs/mico-implementation-design.md). Not for a single isolated bug fix or a one-off PR — use this only when there's a real backlog of tasks to work through."
---

# Delivery pipeline: designer + test-builder + implementer + reviewer

Runs a repo's task backlog (a design doc's task table, a milestone plan, a GitHub issue list —
whatever the repo uses) to completion using four types of independent background agents instead
of one session doing everything serially. This is the coordinator's playbook — **you** (the
invoking session) stay in the loop the whole time: launching agents, relaying messages between
them, resuming them when they stop, and reporting status to the user. You never do the design,
test, implementation or review work yourself once this is running; that's what the subagents are for.

## The four agent types

| Agent | Input | Output | Touches |
|---|---|---|---|
| **Designer** | the task + requirements + real code | a detailed design **and** test plan (a design file per task) | nothing (read-only) |
| **Test-builder** | the design + test plan (never the implementation) | all the tests, with expected outcomes, written TDD-style | test files only, on `<branch>-tests` |
| **Implementer** | the design (never the tests' internals beyond the plan) | the production code | non-test files only, on `<branch>-impl` |
| **Reviewer** | the requirements, the design, the tests, both branches | verified, fixed and merged PR — or a blocking report | the PR branch (fixes), `main` (merge) |

**There can be multiple instances of each type** (e.g. two implementers on independent tasks, a
second reviewer when PRs pile up). The rule that keeps this safe: *one instance per role per
task* — never two test-builders, two implementers or two reviewers on the same task/PR.

**Test-builder and implementer run in parallel** off the same design. They share no code and
don't wait for each other; they only *meet at the reviewer*, who combines their two branches,
runs the tests against the implementation, and decides — by root cause — whether the
implementation or the tests need fixing.

```
            ┌─► test-builder ─► <branch>-tests ─┐
designer ───┤                                    ├─► reviewer ─► PR ─► merge
 (design +  └─► implementer  ─► <branch>-impl  ─┘     (combine, run tests, check
  test plan)                                           standards, fix by root cause)
```

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
   granularity, the open-task cap per implementer/test-builder (default 3), how many instances of
   each agent type to run, and that it will merge PRs autonomously once CI
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

Every phase below (designing, test building, implementing, reviewing) refers to these by name. Not every task
needs every level — the point is to *decide* which apply, not skip silently:

| Level | Tests | Typical scope |
|---|---|---|
| **Unit** | a single function/class in isolation; collaborators faked/mocked | almost every task with any logic in it |
| **Component / integration** | a module or service boundary, with cheap real collaborators where practical (e.g. an in-memory fake store instead of a real DB) — still fast, still offline | a task that introduces or changes a module boundary, a port/ABC implementation, a service class |
| **Smoke** | does the entrypoint even come up and respond at all (a CLI command runs with `--help`/a trivial invocation, a server boots and answers one request) | any new CLI command, API route, worker entrypoint, or script |
| **System** | cross-module behavior exercised through the real application wiring, still inside the test process/sandbox (no real browser, no real network) | a task whose correctness depends on several modules working together, not just one in isolation |
| **E2E** | the full external-facing flow through the real interface — real browser automation, a real CLI subprocess invocation, a request against a real (test) server | a task that changes or adds a user-facing flow (UI, CLI command a user types, a public API) |

## Coding best-practices checklist (shared vocabulary)

The designer designs to it, the implementer self-checks against it before handing off, and the
reviewer checks it independently (fresh eyes, don't just trust the implementer's self-check)
before merging.
Adapt to the repo's own documented standards where it has them (a style guide, a review-gate
checklist, a linter config with opinions baked in) rather than overriding them with this generic
list — this is the default when the repo doesn't already say.

- **Interface-oriented encapsulation.** Code depends on the abstraction (the port/ABC/interface)
  a module exposes, not its concrete internals; callers don't reach around a boundary to touch
  what it hides. Layer boundaries this repo defines (e.g. a "don't import the data layer directly
  from the UI layer" rule) are respected, not routed around for convenience.
- **API quality.** Public signatures, names, types and error contracts are minimal, consistent,
  hard to misuse, and match the design; nothing is exposed that callers don't need.
- **Code reuse — no duplication.** The same logic isn't copy-pasted into two places; shared
  behavior is factored into one function/module both call. A near-duplicate found during review
  is a finding, not a style nitpick — duplicated logic drifts.
- **No magic numbers or magic strings.** Thresholds, limits, status strings, config keys, retry
  counts, timeouts — anything that isn't self-evidently `0`, `1`, or `-1` — are named constants
  (or config), not inline literals repeated across the diff.
- **Simplicity.** No speculative generality (a plugin system/abstraction layer for a single
  concrete use case), no premature optimization, no unused flexibility "for later." The simplest
  design that satisfies the actual acceptance criteria wins; three similar lines beat a premature
  abstraction.
- **Generalization (in balance with simplicity).** No hard-coded special cases, environment
  assumptions or values that belong in parameters/config; behavior that is naturally a family
  (several similar cases) is expressed once, generally — but only to the extent the real
  requirements need it, never for imagined future ones.
- **Testability.** Dependencies are injected or sit behind an interface so behavior can be tested
  in isolation; no hidden globals, clocks, randomness or I/O baked into logic; outcomes are
  observable through the public API, so tests never need to reach into internals.
- **Readability.** Clear naming that says what something is, not how it's computed internally;
  functions sized so a reader can hold one in their head; comments only where the *why* is
  non-obvious (a workaround, an invariant, a subtle constraint) — not restating what the code
  already says.
- **Security.** Untrusted input validated at the boundary it enters, not assumed clean downstream;
  no injection vectors (SQL built from string concatenation instead of parameters, shell commands
  built from unescaped input, path traversal from an unvalidated file path); secrets/credentials
  never logged, committed, or echoed in error messages; an API endpoint or CLI command enforces
  whatever authn/authz/scoping the task's security model requires — not left open because the
  happy-path test didn't need it.
- **Error handling at boundaries.** Expected failures (bad input, a network call that can fail, a
  missing file) are handled explicitly and reported usefully; they aren't silently swallowed
  (`except: pass`), and an error isn't caught so broadly that a real bug gets misreported as the
  expected failure case.
- **Consistency.** Matches this repo's existing conventions (naming, file layout, error-handling
  style, test style) rather than introducing a new pattern for the same problem the codebase
  already solves one way.

## Scaling the designer's effort

Every task gets a design + test plan, because the test-builder and implementer can only work in
parallel from a shared contract. The *depth* scales: a small task gets a short design (signatures,
file paths, named test cases); a **complex** task gets the full treatment. Treat a task as
complex when it's one or more of:
- a port/ABC definition other tasks will implement against (gets the contract wrong once, and
  everything downstream inherits the mistake)
- a task with many direct dependents in the task graph (a fan-in or fan-out point)
- explicitly flagged as complex/risky in the task source (a "spike", "flagged risk", etc.)
- touches concurrency, transactions, or a security/permission boundary
- large enough that one PR is unrealistic (note where to split it into sub-PRs)

For complex tasks consider a stronger model for the designer and have it also note where to
split into sub-PRs (each sub-PR carrying its own tests). Independent tasks can be designed by
several designer instances at once.

## Orchestration loop

1. **Design.** Launch **designer** instance(s) for the tasks that are unblocked (all of them, depth
   scaled per above). A designer is read-only and returns one design + test plan per task — save
   each to a shared scratch file (your session's scratchpad directory) all other agents can read;
   don't rely on passing it through chat. A task's design file is the contract the next two
   agents build against.
2. **Build in parallel.** As soon as a task's design file exists, launch a **test-builder** and an
   **implementer** for it *at the same time* (`Agent` tool, `subagent_type: "fork"`,
   `isolation: "worktree"` for each — never let them work in your own checkout). They work on
   separate branches (`<branch>-tests`, `<branch>-impl`) and **never read each other's work in
   progress**: the test-builder derives tests from the design/requirements, not from the code, and
   the implementer builds to the design, not to the tests. That independence is the point — it is
   what makes a passing run meaningful. Designers keep working on later tasks meanwhile.
3. **Review where they meet.** When *both* branches for a task are pushed, launch (or notify) a
   **reviewer** for it. The reviewer combines the two branches into the task's PR branch, runs the
   tests, checks the standards, fixes by root cause (see its template), and merges.
4. **Relay between agents as they stop.** Each agent is a single long *turn*, not a daemon — it
   stops when it hits its cap, finishes its pass with nothing left, or dies to a rate limit or an
   expired login. A task-notification fires each time. On each notification:
   - If the agent stopped *normally*: tell the agents downstream what changed (design files ready →
     start test-builder + implementer; both branches ready → start reviewer; PR merged → unblock
     dependents) and resume whichever one is now unblocked.
   - If a **reviewer reports a root cause that belongs upstream** (a design flaw or ambiguity, a
     test the implementer legitimately can't satisfy, an implementation gap too big to fix in
     review), route it: back to the designer (design/test-plan fix → test-builder and implementer
     re-sync to the revised design), to the test-builder, or to the implementer — then re-run
     review. Keep a short per-task log of these loops; if a task bounces more than twice, stop
     and ask the user.
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
5. **Never let two instances of the same role touch the same task/PR.** If you relaunch a reviewer
   while a PR is mid-review by another instance, tell the new one explicitly which PR(s) are
   off-limits. If you discover this already happened (two reviewers both touched one PR), get the
   in-progress one to hand off its findings to the one actually owning the PR rather than apply
   fixes itself. Different instances on *different* tasks is the intended way to scale.
6. **Re-sync with `main` at natural checkpoints**: before an agent starts a new task (fetch +
   merge/rebase), and again immediately before the reviewer merges (someone else may have landed
   a dependency, or just unrelated work, in between). A task whose dependency isn't merged yet
   can be designed early but its test-builder/implementer start only once the dependency is on
   `main` (or its design is the only thing they depend on, e.g. a port/ABC signature).
7. **Stop condition:** no PRs open, the task source has nothing left unmerged, and a couple of
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


- **Tests written from the code are vacuous tests.** The whole reason the test-builder never sees
  the implementation (and vice versa) is that a test shaped by the code it checks proves nothing.
  If either agent peeks, the independence — and the value of the review meeting — is gone.
- **A failing test is a question, not a verdict.** At review, "tests fail" does not automatically
  mean "fix the code" or "fix the test". The reviewer decides by root cause against the
  *requirements*, and must never weaken, skip or delete a test just to get green.

---

## Agent prompt templates

Fill in the bracketed placeholders from the repo's actual docs/conventions before launching. Keep
the structural instructions (caps, no-stacking, worktree isolation, role separation, attribution)
as-is — they're load-bearing, not cosmetic.

### 1. Designer (detailed design + test plan)

```
subagent_type: "Plan" (or "fork" if you want it to inherit this conversation's context)
isolation: not needed (read-only)
model: consider "opus" for genuinely hard design tasks

Prompt:
You are a DESIGNER in a pipeline for the repo at <repo path>. A TEST-BUILDER agent and an
IMPLEMENTER agent will work IN PARALLEL from your output, without seeing each other's work: the
test-builder writes every test from your test plan, the implementer writes the code from your
design. A REVIEWER later combines the two. Your document is therefore the only contract between
them — it must be precise enough that tests written from it and code written from it agree. You
are read-only — you cannot edit files; return each design as text.

Read <task-source-doc(s)>, <architecture-decisions-doc>, <PRD/requirements-doc>, and
<knowledge-base / README> plus the existing code under <source dirs> (state which tasks are
already merged, so the design matches real interfaces and conventions, not guessed ones).

Design these tasks: <list of task IDs/names>. Depth: <short for simple tasks / full for complex
ones, per the skill's complexity criteria>. Flag any dependency on unmerged work.

For each task produce ONE document with two parts.

PART A — DETAILED DESIGN (what the implementer builds):
- Requirements restated as numbered acceptance criteria (R1, R2, …), each traceable to the source.
- Files/modules to create or change (real paths, matching the repo's layering/module conventions)
  and, per module, the exact public API: names, signatures, types, return values, raised/returned
  errors, and the behavior of each. Fix the interface precisely — the test-builder will import
  these exact names.
- Data model/schema/migration details if relevant; sub-step ordering; named constants/config
  rather than magic values; the seams for testability (what is injected/behind an interface).
- Design to the shared coding best-practices checklist (encapsulation, no duplication, simplicity,
  API quality, testability, generalization, no magic values, security at boundaries).
- Risks and open questions, each with a stated default decision (don't leave anything open).
- How to split into smaller PRs if too large; each sub-PR carries its own tests.

PART B — TEST PLAN (what the test-builder builds), derived from the criteria, not from the code:
- Test cases, one line each ("test_X: given Y, when Z, expect <exact outcome>"), each mapped to
  the requirement(s) it proves (R#). Every acceptance criterion, edge case and failure mode must
  map to at least one named case, with concrete expected values/errors.
- Which test levels apply (unit / component / smoke / system / e2e — see the shared taxonomy) and
  why the others don't; don't default to unit-only out of habit.
- Test file paths, fixtures, fakes and test data to add or extend, matching the repo's test
  layout; the exact commands that run them.
- Which tests can only pass once the implementation exists (they're expected to fail/not import
  until then) — that's normal, say so.

Be concrete and grounded in the actual code, not generic.
```

### 2. Test-builder (TDD)

```
subagent_type: "fork"
isolation: "worktree"   # never let it work in your own checkout

Prompt:
You are a TEST-BUILDER in a pipeline (a DESIGNER wrote the design + test plan; an IMPLEMENTER is
writing the production code AT THE SAME TIME on another branch; a REVIEWER later combines your
work with theirs). Do not write or edit production code, and do NOT look at the implementer's
branch/worktree or any production code written for this task — your tests must come from the
requirements, not from the code, or they prove nothing. Do not review or merge PRs.

For your assigned task(s) <task IDs>:
1. `git fetch origin`; branch from origin/main as <branch naming convention>-tests. Read the
   design file at <path> (Part B is your spec; Part A gives the exact public API you import),
   the requirements it cites, and the repo's test conventions.
2. Write ALL the tests in the test plan — every named case, at every test level the plan lists
   (unit, component/integration, smoke, system, e2e), including failure and edge cases — with
   explicit expected outcomes (exact values, errors, state changes) taken from the requirements,
   not computed by reusing the logic under test. Add the fixtures/fakes/test data the plan names.
   Match the repo's test style, location and naming.
3. TDD discipline: the tests are the executable specification. They should fail now only because
   the implementation doesn't exist yet (import error/missing behavior) — never because of a bug
   in the test. Where you can, make them runnable against a trivial stub of the Part A API
   (kept in your test directory or an unmerged scratch copy, not committed to production paths)
   to prove each test can both fail and pass for the right reason.
4. Re-read your own tests with fresh eyes: does each assert something meaningful tied to a
   requirement (not `assert True`, not a mock configured to return the expected value, not
   silently skipped/xfailed)? Would it fail if the behavior were wrong? If the design is
   ambiguous or contradicts the requirements, do NOT guess silently — record the question in your
   hand-off (the reviewer routes it to the designer).
5. Commit only test files (<commit message convention>), push `git push -u origin HEAD`. Do not
   open the PR; the reviewer combines branches. Hand off in your final report (under 200 words):
   branch name, the test→requirement map (R# → test names), the exact command to run them, which
   tests need the implementation to exist, and any design ambiguities you hit. Use the attribution
   lines from your system reminders for commits.

Constraints: max <N, default 3> tasks of yours unreviewed at once — if you hit that, stop and
report. Never force-push main, never skip hooks.
```

### 3. Implementer

```
subagent_type: "fork"
isolation: "worktree"   # never let it work in your own checkout

Prompt:
You are an IMPLEMENTER in a pipeline (a DESIGNER wrote the design; a TEST-BUILDER is writing the
tests AT THE SAME TIME on another branch; a REVIEWER later combines your work with theirs and
runs the tests). Write production code only: do NOT write, edit or read the test-builder's
tests, branch or worktree — build to the design and requirements so your code is verified by
independent tests, not shaped around them. Do not review or merge PRs.

Loop over tasks from <task-source-doc>: read it, <architecture/requirements docs>, and
<knowledge-base/README> for conventions, build/lint/typecheck commands, and layering rules.

1. `git fetch origin`; take an assigned task (or the lowest-numbered/highest-priority one that has
   a design file, is not yet on origin/main, is not already covered by an open PR/branch — check
   `gh pr list --state all` and branch names — and whose dependencies are all merged into
   origin/main).
2. Branch from origin/main as <branch naming convention>-impl. Follow the design file at <path>
   (Part A) exactly for module layout and public API — the tests import those exact names. Flag
   any deviation, and the reason, in your hand-off; if the design is ambiguous or wrong, pick the
   most reasonable reading, state it in the hand-off, and don't silently diverge.
3. Implement every requirement R# in the design — everything asked, and nothing materially beyond
   it (an unplanned refactor or unrelated file makes review harder; leave it for its own task).
   Run the repo's build/lint/typecheck/layer-check commands (<list — find the exact commands in
   the CI workflow file or repo docs>) and make them green. You may write throwaway scratch
   checks of your own to exercise the code, but don't commit tests — the test-builder owns those.
4. Self-check the diff against the shared coding best-practices checklist (encapsulation, no
   duplicated logic, no magic numbers/strings, simplicity, API quality, testability,
   generalization, readability, security at any boundary the task touches, explicit error
   handling, consistency with existing conventions).
5. Commit only non-test files (<commit message convention>), push `git push -u origin HEAD`. Do
   not open the PR; the reviewer combines branches. Hand off in your final report (under 200
   words): branch name, requirement→code map (R# → files/functions), deviations from the design
   and why, ambiguities hit, and anything already done on origin/main.
6. Immediately move to the next task; do NOT wait for the reviewer.

Constraints: max <N, default 3> tasks of yours unreviewed at once — if you hit that, stop and
report. Never stack a branch on another of your own unmerged branches once more than one is
open (pick a different task instead). Never merge PRs, never force-push main, never skip hooks.
If the task you're about to build is already done on origin/main (other automation, or work you
can't see from here), say so and stop rather than pushing a redundant/conflicting version. Use
the attribution lines from your system reminders for commits.
```

### 4. Reviewer (autonomous)

```
subagent_type: "fork"
isolation: "worktree"

Prompt:
You are a REVIEWER in a pipeline. For each task, a TEST-BUILDER pushed `<branch>-tests` (all the
tests, written from the design) and an IMPLEMENTER pushed `<branch>-impl` (the production code,
built from the design), independently of each other. You are where they meet. You work
autonomously: you have the requirements (<requirements/PRD/architecture docs>, the task-source
entry, and the design + test plan at <path>) and the tests; decide and act without asking, except
where a step below says to stop and report. Do not implement new tasks.

Within a single ongoing turn, loop: find tasks whose two branches are both pushed and that have no
PR yet (or open PRs awaiting review), oldest first, and handle each (steps below). If none, wait
with a short **foreground** sleep (not `run_in_background`) and check again — keep looping across
many iterations in this one turn. Stop and report only after a generous number of empty passes
(e.g. 15-20 minutes of real elapsed time with nothing new) or a real stopping condition (task
source fully merged). Only one reviewer instance per task/PR — skip any PR assigned elsewhere
(<list off-limits PRs>).

For each task:
1. **Combine.** Branch from the latest origin/main as <branch naming convention>; merge
   `<branch>-tests` and `<branch>-impl` into it (they touch disjoint files; resolve any conflict
   or overlap on its merits) and open the PR (title <PR title convention>, summary + requirement →
   code → test map from the two hand-offs). Re-sync with origin/main if it moved.
2. **Run everything.** Run the full local checks CI runs (<list: lint, typecheck, tests,
   layer-check, build, …>) and the task's tests at every level in the test plan. **Verify the
   tests actually passed** — read the output, don't assume; also check CI is green: <name any
   known-flaky/non-blocking check for this repo, e.g. "review-gate is known-flaky here (reason X)
   — its failure alone does not block merging; anything else red does.">
3. **If anything fails, find the ROOT CAUSE against the requirements** — the requirements and design
   are the source of truth, not the tests and not the code:
   - **Implementation bug / gap** (code contradicts a requirement or the design) → fix the
     implementation (new commit; leave the test as is).
   - **Test bug** (the test contradicts the requirements or design, has a wrong expected value,
     is flaky, tests an internal rather than the API, or fails for a reason unrelated to the
     behavior) → fix the test, and state in the commit message which requirement shows the
     expectation was wrong.
   - **Design/requirement ambiguity or flaw** (both sides are defensible readings, or the design
     is wrong) → do not pick a side to get green; leave a PR comment, do NOT merge, and report it
     so the coordinator can send it back to the designer.
   Never weaken, loosen, skip, xfail or delete a test just to make it pass, and never special-
   case the code to the test. Re-run after each fix; repeat until green or blocked.
4. **Verify every requirement is implemented — exhaustively.** Walk the full requirement list (R#
   in the design, plus the task source/PRD entry) item by item and confirm each is really in the
   diff, not just plausible-sounding. A silently missing, partial or stubbed requirement is a
   blocking finding — fix it, or report it if too big for review.
5. **Verify the tests are real and complete.** Read the test files directly:
   - every named case in the test plan, and every requirement, has a real test (no TODOs, no
     deferrals), at every applicable level (a new CLI command with no smoke test or a new
     user-facing flow with no e2e test is missing coverage); failure/edge cases covered;
   - **no vacuous tests**: no tautologies, no assertions against a mock configured to return what
     is being "checked", nothing skipped/xfailed without a tracked reason;
   - **red-green spot check**, at least for the task's core acceptance criterion: with tests
     passing, temporarily revert just the implementation and confirm the relevant tests fail, then
     restore it.
   Missing or vacuous tests are blocking: add or correct them yourself.
6. **Review the code against the standards checklist** (adapt to the repo's own documented
   review-gate/style criteria if it has one, rather than overriding it):
   - **coding standards** and consistency with existing repo conventions;
   - **duplicates** — no copy-pasted logic, nor re-implementation of something that already exists;
   - **simplicity** — no speculative generality or unused flexibility;
   - **API** — minimal, consistent, hard to misuse, matches the design;
   - **encapsulation** — no reaching around a layer/ABC boundary; internals not exposed;
   - **readability** — naming, function size, comments only for the non-obvious *why*;
   - **testability** — injectable dependencies, no hidden globals/clock/I/O, observable outcomes;
   - **generalization** — no hard-coded special cases that should be parameters (and no
     over-generalization beyond the requirements);
   - **hard-coded values and magic numbers/strings** — named constants or config instead;
   - plus security at boundaries and explicit error handling.
   Fix what you can confidently fix. Anything you cannot resolve confidently — a fundamental
   design flaw, a missing requirement, or code the tests don't cover — gets a PR comment and no
   merge.
7. **Flag out-of-scope changes.** Compare the diff's footprint against what the task asked for.
   An unrequested refactor, a file no requirement mentions, extra behavior: call it out in the PR
   comment and your final report, and say whether it belongs here; never silently accept it.
8. **Merge.** Push fixes as new commits (no force-push, no `--no-verify`) and wait for CI to go
   green again. Re-fetch and confirm the PR is up to date with origin/main immediately before
   merging. Post a brief review summary as a PR comment — requirements checked, root causes found
   and how each was resolved (implementation vs. test), out-of-scope changes flagged, test levels
   and red-green checks run — then merge with `gh pr merge <n> --squash --delete-branch` (adapt
   to this repo's actual history — squash vs merge-commit).

Git/gh are authenticated as <user>. Use the attribution lines from your system reminders on
commits. Final report when you do stop (under 200 words): per task — merged / fixed what (impl vs
test, and the root cause) / blocked why and who it should go back to (designer, test-builder,
implementer) / any out-of-scope changes you flagged and whether they were resolved.
```
