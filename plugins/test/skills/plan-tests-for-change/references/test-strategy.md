# Test strategy: levels, risk, and the decision rule

Shared by the testing skills (`plan-tests-for-change`, `review-tests`, `manual-tests`, `test-run-report`). If the repo's `.agents/knowledge/testing.md` defines its own levels, those win; this file is the default.

## Core principle

Cover each behavior once, at the cheapest level that gives real confidence. More tests are not safer: every test costs runtime, maintenance and review attention, and redundant tests hide the ones that matter.

## Levels (classify by evidence, not by file name)

| Level | Scope | What is real | What is faked |
|---|---|---|---|
| unit | One function, class or module | Only that unit | Nothing needed; no rendering, network, DB, filesystem or process calls |
| component | One UI component/page or one backend service, with its real internals | The component and everything inside it | Its external boundaries: network (MSW, route interception), DB or queue (in-memory/stand-in), third parties |
| multi-component (use-case) | Several components or services collaborating on one use case | Internal wiring between them, often a real DB | Only systems outside the product (payment, email, third-party APIs) |
| e2e | The entire deployed system | Everything, via real browser or real HTTP | Nothing internal |

Classification signals, in order of trust:
1. What the test starts (a function call, a rendered component, several services, a deployed environment).
2. What it fakes (nothing, boundaries only, external systems only, nothing).
3. Its runner and location (a hint only; do not trust names).

Unit vs component: use unit only for logic with many input combinations (calculations, parsing, validation rules, state machines). Anything else is a component test. If a test mocks a collaborator that is part of the same product, it is neither: flag it as "mocks internals".

## Risk levels

Every behavior gets one risk level. Use the highest level that applies.

- **low**: minimal risk, minimal impact on users. UI copy and styling, help text, comments, demos, internal tooling.
- **medium**: noticeable risk, some impact on users. Specific implementations, business logic users can notice, behavior that changes what a user sees or gets without touching data or contracts.
- **high**: elevated risk, high potential impact on users. Anything that changes or depends on an API, schema or data format; alters user data, databases, payments or accounts; or makes any non-backward-compatible change.

When unsure between two levels, pick the higher one and say why. The risk level drives budget ranking, prioritization in `review-tests`, and (later) SDLC gates, so keep it consistent across skills.

## Decision rule: cheapest sufficient level

For each behavior, pick the lowest level at which the risk it guards against is observable.

- Many input combinations of pure logic: unit.
- User-visible or API-visible outcome of one component: component.
- A use case that depends on the wiring between components (contracts, ordering, shared state): multi-component.
- A critical user journey, or wiring that cannot be observed below (deploy config, auth across services, real browser behavior): e2e. Keep this set small and named.
- Cannot be observed automatically at a reasonable cost (visual judgement, real device behavior, look and feel): manual, recorded in `.agents/manual-tests.md` (see the `manual-tests` skill).

Redundancy test: if deleting a test leaves the same behavior covered at an equal or cheaper level, the test is redundant.
Level test: if a behavior is only asserted at a level above the one the rule gives, push it down.

## Designing the cases inside a test

Pick inputs with named techniques, and name the technique in the plan:

- Equivalence partitioning: one case per class of input that behaves the same.
- Boundary values: the values on and either side of each limit (e.g. 7, 8, 12, 13 characters for a 8-12 character rule).
- Decision tables: combinations of conditions that change the outcome.
- State transitions: valid and invalid moves between states.
- CRUD: create, read, update, delete for each entity touched.
- Error guessing: known failure patterns (empty, null, duplicate, timeout, concurrent edit).

## Domain playbooks

When a change touches one of these areas, check the playbook in `references/playbooks.md` for behaviors that are easy to miss: auth, payments, forms, CRUD, i18n/RTL, mobile.

## Regression rule for bug fixes

A bug fix is not covered until its regression test is shown to be meaningful:

1. Write the regression test at the cheapest level that reproduces the bug.
2. Run it against the code without the fix. It must fail.
3. Run it with the fix. It must pass.

A test that passes both ways does not guard the bug and must be redone. If the bug cannot be reproduced at any automated level, record a manual test instead and say so.

## Budgets (defaults, override in testing.md)

- New tests per change: at most 4 unless the change is large; prefer extending an existing test.
- e2e: only critical journeys; adding one requires naming the journey.
