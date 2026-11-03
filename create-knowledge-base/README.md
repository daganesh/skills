# create-knowledge-base

Sets up or refreshes a `.agents/` knowledge base in a repo, so agents read a short index and topic/component files instead of the whole source.

- **Use when:** onboarding a repo to agent workflows, or verifying/refreshing an existing `.agents/`.
- **Output:** `.agents/README.md`, `knowledge/` (topics + foundational components), `skills/` (bug-fix, new-feature, write-test), root pointer files (`CLAUDE.md`, `AGENTS.md`, …).
- **Modes:** create (full run) or update (verify and patch, never blind regenerate).
- **Test skills hook:** the generated `testing.md` and workflows point to [`plan-tests-for-change`](../plan-tests-for-change/README.md) and [`review-tests`](../review-tests/README.md); the user can opt out. Its `testing.md` template is [`review-tests/references/testing-knowledge-template.md`](../review-tests/references/testing-knowledge-template.md).
- **Consumed by:** [`plan-tests-for-change`](../plan-tests-for-change/README.md), [`review-tests`](../review-tests/README.md), [`test-run-report`](../test-run-report/README.md) all read `.agents/knowledge/testing.md`; [`manual-tests`](../manual-tests/README.md) owns `.agents/manual-tests.md`.

Entry point: [`SKILL.md`](SKILL.md) · Up: [skills index](../README.md)
