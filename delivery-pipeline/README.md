# delivery-pipeline

Implements a whole backlog (task table, milestone plan, issue list) with three background agents: **planner**, **implementer**, **reviewer**. One PR per task; the reviewer reviews, fixes and merges.

- **Use when:** there is a real list of tasks. Not for a single bug fix or one-off PR.
- **Contents of `SKILL.md`:** pre-launch checks, shared test-level and best-practice vocabulary, how to spot complex tasks, the orchestration loop, known pitfalls, the three agent prompt templates.
- **Upstream:** [`project-design`](../project-design/README.md) writes the task table this skill executes.
- **Related:** its test-level vocabulary matches [`review-tests/references/test-strategy.md`](../review-tests/references/test-strategy.md); per-task test decisions can use [`plan-tests-for-change`](../plan-tests-for-change/README.md).

Entry point: [`SKILL.md`](SKILL.md) · Up: [skills index](../README.md)
