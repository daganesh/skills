# Test strategy: levels and the decision rule

Shared by both skills. If the repo's `.agents/knowledge/testing.md` defines its own levels, those win; this file is the default.

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

## Decision rule: cheapest sufficient level

For each behavior, pick the lowest level at which the risk it guards against is observable.

- Many input combinations of pure logic: unit.
- User-visible or API-visible outcome of one component: component.
- A use case that depends on the wiring between components (contracts, ordering, shared state): multi-component.
- A critical user journey, or wiring that cannot be observed below (deploy config, auth across services, real browser behavior): e2e. Keep this set small and named.

Redundancy test: if deleting a test leaves the same behavior covered at an equal or cheaper level, the test is redundant.
Level test: if a behavior is only asserted at a level above the one the rule gives, push it down.

## Budgets (defaults, override in testing.md)

- New tests per change: at most 4 unless the change is large; prefer extending an existing test.
- e2e: only critical journeys; adding one requires naming the journey.
