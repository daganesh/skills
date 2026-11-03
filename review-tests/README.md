# review-tests

Reviews an existing backend/frontend test suite and the manual list. Findings (redundant, wrong level, missing, brittle, automatable manual entries) become a prioritized to-do list grouped into proposed PRs; after approval, one GitHub issue per group. Issues only: it never pushes code.

- **Use when:** "review the tests", "find redundant or missing tests", suite is slow or bloated.
- **References:** [`test-strategy`](references/test-strategy.md) (levels, risk, decision rule), [`scoring`](references/scoring.md) (priority), [`issue-template`](references/issue-template.md), [`playbooks`](references/playbooks.md), [`testing-knowledge-template`](references/testing-knowledge-template.md) (shape of `.agents/knowledge/testing.md`).
- **Reads:** `.agents/knowledge/testing.md` ([`create-knowledge-base`](../create-knowledge-base/README.md)) and `.agents/manual-tests.md`.
- **Related:** [`plan-tests-for-change`](../plan-tests-for-change/README.md) (per-change planning), [`manual-tests`](../manual-tests/README.md) (retires entries it flags), [`test-run-report`](../test-run-report/README.md) (provides run data).

Entry point: [`SKILL.md`](SKILL.md) · Up: [skills index](../README.md)
