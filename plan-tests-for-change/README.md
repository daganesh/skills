# plan-tests-for-change

For a new or changed component/feature/bug fix: decides which tests to add or extend, at which level (unit, component, multi-component, e2e), in which file, and which behaviors go to the manual list. Prefers extending existing tests.

- **Use when:** before or after implementing a change, or "what tests does this need?".
- **Rules it enforces:** risk level per case, a named design technique, and bug-fix regression tests that fail without the fix and pass with it.
- **Reads:** `.agents/knowledge/testing.md` (created by [`create-knowledge-base`](../create-knowledge-base/README.md)), [`references/test-strategy.md`](references/test-strategy.md), [`references/playbooks.md`](references/playbooks.md).
- **Hands off to:** [`manual-tests`](../manual-tests/README.md) for non-automatable behaviors.
- **Sibling:** [`review-tests`](../review-tests/README.md) does the same thinking for an existing suite. Its `references/` are copies of these files (see [shared testing concepts](../.agents/knowledge/testing-skills.md)).

Entry point: [`SKILL.md`](SKILL.md) · Up: [skills index](../README.md)
