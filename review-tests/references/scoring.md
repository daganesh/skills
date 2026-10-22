# Scoring and prioritization

Keep it light: rank actions, do not grade every test against a rulebook.

## Finding types and the action each leads to

| Finding | Evidence to collect | Action |
|---|---|---|
| Redundant | Same behavior asserted by another test at equal or cheaper level; same files exercised with same outcome; near-identical titles or assertions | Delete (or Merge if one adds a unique assertion) |
| Wrong level (too high) | Behavior observable at a lower level but only tested at a higher one | Move down (add the lower test, delete the higher one) |
| Wrong level (mocks internals) | Test fakes a collaborator inside the product, so it neither isolates a unit nor checks wiring | Rewrite as component or multi-component |
| Missing | Behavior or code path with no test at any level, weighted by risk | Add (at the cheapest sufficient level) |
| Brittle | Asserts implementation details, sleeps or fixed waits, order dependence, flaky or slow | Rewrite |

Do not report style nitpicks. A finding must change cost, risk or trust.

## Priority

For each todo item:

- impact (1-5): cost saved (runtime, maintenance, noise) for Delete/Merge/Move down; risk removed for Add/Rewrite (likelihood x damage of the uncovered behavior).
- effort: S (under 1 hour), M (a few hours), L (a day or more).
- priority = impact / effort weight (S=1, M=2, L=4). Sort descending. Ties: prefer Delete and Move down (they shrink the suite).

Show the top 15 by default. Mention how many lower-priority findings were left out.

## Area ranking

Also rank areas (feature, page or service) from worst to best: sum of priorities of open items in that area. Show as a short table.
