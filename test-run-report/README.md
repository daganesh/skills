# test-run-report

Runs the repo's automated suites and commits a report per run: results per level, failures by risk, flaky tests, coverage, runtime, manual tests due, comparison with the previous run. A human reviews it. Can also compare any two runs.

- **Use when:** "run the tests and report", checking a branch before review/release, comparing runs.
- **Reads:** `.agents/knowledge/testing.md` for exact commands ([`create-knowledge-base`](../create-knowledge-base/README.md)); levels and risk from [`review-tests/references/test-strategy.md`](../review-tests/references/test-strategy.md).
- **Related:** lists due entries from [`manual-tests`](../manual-tests/README.md) without running them; its numbers feed [`review-tests`](../review-tests/README.md).

Entry point: [`SKILL.md`](SKILL.md) · Up: [skills index](../README.md)
