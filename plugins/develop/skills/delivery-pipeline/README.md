# delivery-pipeline

Implements a whole backlog (task table, milestone plan, issue list) with four types of background agents: **designer** (detailed design + test plan), **test-builder** (TDD: writes all tests from the design), **implementer** (writes the code from the design) and **reviewer** (autonomous: verifies tests pass and standards are met, fixes by root cause, merges). Test-builder and implementer run in parallel and only meet at the review. One PR per task; each type can have multiple instances.

- **Use when:** there is a real list of tasks. Not for a single bug fix or one-off PR.
- **Contents of `SKILL.md`:** pre-launch checks, shared test-level and best-practice vocabulary, how to spot complex tasks, the orchestration loop, known pitfalls, the four agent prompt templates.
- **Upstream:** [`project-design`](../project-design/README.md) writes the task table this skill executes.
- **Related:** its test-level vocabulary matches [`review-tests/references/test-strategy.md`](../../../test/skills/review-tests/references/test-strategy.md); per-task test decisions can use [`plan-tests-for-change`](../../../test/skills/plan-tests-for-change/README.md).

Entry point: [`SKILL.md`](SKILL.md) · Up: [skills index](../../../../README.md)
