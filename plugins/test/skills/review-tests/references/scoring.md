# Scoring and prioritization

Keep it light: rank actions, do not grade every test against a rulebook.

## Finding types and the action each leads to

| Finding | Evidence to collect | Action |
|---|---|---|
| Redundant | Same behavior asserted by another test at equal or cheaper level; same files exercised with same outcome; near-identical titles or assertions | Delete (or Merge if one adds a unique assertion) |
| Wrong level (too high) | Behavior observable at a lower level but only tested at a higher one | Move down (add the lower test, delete the higher one) |
| Wrong level (mocks internals) | Test fakes a collaborator inside the product, so it neither isolates a unit nor checks wiring | Rewrite as component or multi-component |
| Missing | Behavior or code path with no test at any level, weighted by risk | Add (at the cheapest sufficient level) |
| Brittle | Asserts implementation details, sleeps or fixed waits, order dependence, flaky or slow; or appears as flaky in the latest run report | Rewrite |
| Automatable manual | A manual entry whose behavior now has an automated test, or can be covered at a reasonable cost | Retire manual (after the test exists, via `manual-tests`) |
| Stale manual | A manual entry whose screen, endpoint or behavior has changed, or that has never been run while high risk | Review manual (via `manual-tests`) |

Do not report style nitpicks. A finding must change cost, risk or trust.

## Risk

Each behavior carries the risk level from `test-strategy.md`: low, medium or high. Use the highest level that applies. For Add, Rewrite and manual findings, risk is what the uncovered or unreliable behavior would cost users if it broke.

## Priority

For each todo item:

- impact (1-5):
  - For Delete, Merge, Move down: cost saved (runtime, maintenance, noise), 1 to 5.
  - For Add, Rewrite, Review manual: risk removed, from risk level: high = 5, medium = 3, low = 1. Add 1 (to a maximum of 5) when the behavior has already broken or is flaky in a run report.
  - For Retire manual: cost saved by no longer running it by hand, 1 to 3.
- effort: S (under 1 hour), M (a few hours), L (a day or more).
- priority = impact / effort weight (S=1, M=2, L=4). Sort descending. Ties: prefer Delete, Move down and Retire manual (they shrink the work), then higher risk.

Show the top 15 by default. Mention how many lower-priority findings were left out.

## Area ranking

Also rank areas (feature, page or service) from worst to best: sum of priorities of open items in that area. Show as a short table.
