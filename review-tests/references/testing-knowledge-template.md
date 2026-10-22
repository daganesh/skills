# Template: `.agents/knowledge/testing.md`

Fill with real values found in the repo. No placeholders left behind. Keep to about 60 lines; if it grows, move strategy details to `testing-strategy.md` in the same folder.

```markdown
# Testing

## Commands
- All tests: `<exact command>`
- One file: `<exact command>`
- One test by title: `<exact command>`
- With coverage: `<exact command>` (report at `<path>`)
(one block per package or layer, e.g. backend, frontend)

## Levels in this repo
| Level | Where / naming | Framework | Faked at this level |
|---|---|---|---|
| unit | `<glob>` | `<name>` | none |
| component | `<glob>` | `<name>` | `<boundaries>` |
| multi-component | `<glob>` | `<name>` | `<externals only>` |
| e2e | `<glob>` | `<name>` | none |

## Placement
- New test of level X goes in `<path pattern>`, named `<pattern>`.
- Helpers and factories live in `<path>`.
- Canonical examples: unit `<path>`, component `<path>`, multi-component `<path>`, e2e `<path>`.

## Policy
- Cheapest sufficient level (see `test-strategy.md` in the review-tests skill). Default budget: at most 4 new tests per change.
- e2e only for named critical journeys: `<list>`.

## CI and cost
- Stages: `<which levels run where>`; total runtime budget `<time>`.
- Known slow or flaky areas: `<list or none>`.
- Required setup: `<services, env vars>`.

## Baseline (updated by the review-tests skill)
- Date / commit: `<date>` / `<sha>`
- Tests per level: unit `<n>`, component `<n>`, multi-component `<n>`, e2e `<n>`
- Total runtime: `<time>`; coverage: `<percent>`
```
