# manual-tests

Maintains `.agents/manual-tests.md`: the git-tracked list of behaviors a human must check, each with an ID and a risk level (low/medium/high). Can also walk a human tester through the list and record results.

- **Use when:** adding a manual test, retiring one that got automated, listing what to check before a release, starting a manual test session.
- **Operations:** add, retire, review, present to a tester (results go in each entry's "Last run" line).
- **Fed by:** [`plan-tests-for-change`](../plan-tests-for-change/README.md) (new entries) and [`review-tests`](../review-tests/README.md) (entries that can now be automated).
- **Feeds:** [`test-run-report`](../test-run-report/README.md) lists high-risk or never-run entries as "manual tests due".
- **Shared definitions:** risk levels in [`review-tests/references/test-strategy.md`](../review-tests/references/test-strategy.md).

Entry point: [`SKILL.md`](SKILL.md) · Up: [skills index](../README.md)
