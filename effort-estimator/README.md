# Effort estimator (calibrated on your own sessions)

Estimates **time per stage, cost, tokens and model** for a new design + implement task, from what your
past Claude Code sessions actually did.

```bash
python3 estimate.py --kind feature --size M
python3 estimate.py --kind feature --size L --design --model opus
python3 estimate.py --tasks "feature:L:design,bugfix:S,infra:M"     # sum a whole plan
python3 estimate.py --kind bugfix --size S --json                    # machine-readable
```

* `--kind`: `feature | bugfix | design | infra | wave_subtask`
* `--size`: `XS | S | M | L | XL` = P10 / P25 / P50 / P80 / P90 of your history for that kind
* `--design`: add a separate design/plan session on top of the implementation
* `--model`: `auto | sonnet | opus | haiku` (auto = heuristic below)

## How to pick the size
Use the nearest of: **XS** one-line / copy tweak, **S** single component or small bug, **M** typical
feature touching UI + API + tests, **L** multi-area feature or tricky bug with iteration, **XL** cross-cutting
or architectural change. When unsure, **budget with L (P80)** and expect M.

## Data
149 sessions (Jun 14 – Nov 2 2026), 143 usable, ≈ $2,276 total reconstructed spend.
Per session: cost, tokens by model (fresh input, cache read/write, output, thinking), per-turn durations, turn origin
(human vs PR/CI wake-up), parent/child orchestration. Raw extracts: `data/chunk_*.jsonl`. Rebuild the calibration with
`python3 -I analyze.py` (writes `calibration.json`).

Reconstruction notes: cost/tokens come from the cumulative counters in each session's last result (summing peaks across
resets); 41 sessions had older turns truncated during extraction, so **time** stats use only the 102 untruncated sessions,
while **cost/token** stats use all of them. Cost percentiles use sessions dominated by `claude-sonnet-5-5` (n=85); older
models (`sonnet-4-6`, `sonnet-5`) cost differently per minute and are excluded from the cost baseline.

## What the numbers say (Sonnet 5.5 baseline, agent working time + cost)
| kind | n | cost P50 / P80 | agent time P50 / P80 | your follow-up turns P50 |
|---|---|---|---|---|
| bugfix | 21 | $1.31 / $4.46 | 7 / 27 min | 3 |
| feature | 38 | $3.51 / $5.88 | 12 / 25 min | 3 |
| infra | 11 | $2.40 / $3.57 | 13 / 21 min | 4 |
| design | 15 | $5.01 / $38.69 | 8 / 11 min | 3 |
| all | 85 | $2.77 / $7.71 | 11 / 24 min | 3 |

Model cost per minute vs Sonnet 5.5: **Opus 5.5 ≈ 2.1×**, **Haiku 5.5 ≈ 0.36×** (Haiku n=4, Opus n=6: weak evidence).
Typical token mix is dominated by cache reads (~1M tokens per working minute); output ≈ 4k tokens/min, of which ~20% thinking.

## Stage model
Your sessions don't label design/code/test phases, so stages are **turn-based proxies**:
1. *Design* (optional): your separate design/plan sessions.
2. *Implement*: the first autonomous build turn (≈ 60% of feature time).
3. *Revise*: your follow-up turns (≈ 30%).
4. *PR/CI watch*: wake-ups for CI/review/merge (small, except orchestrated wave sub-tasks, where it dominates).

Stage cost is apportioned by stage time share.

## Accuracy: read this
Leave-one-out backtest on your own data:
* **Point estimate is weak** — median error ≈ 70% for cost and 60% for time. Cost is heavy-tailed and task *kind* alone explains little.
* **Ranges are calibrated** — the actual value was ≤ P80 in **79% (cost)** and **78% (time)** of cases.

So: plan with the **P80 column**, treat P50 as "if it goes smoothly", and expect a ~1-in-5 chance of exceeding P80.
The tail is real: a few multi-agent design/orchestration sessions cost $100–$300 each (e.g. "shared company state" $243,
"Add signer role…" $299, "Game customization layer" $183). If your task is multi-agent/orchestrated, don't trust these tiers: budget separately.

## Other caveats
* Time is **agent working time** (sum of turn durations); calendar time includes your review gaps and CI (wave sub-tasks sat ~5 days waiting).
* Model auto-pick is a heuristic from observed usage and cost ratios, **not** a quality comparison.
* Costs are as reported (list basis); a per-token price table could not be reliably fitted from this data, so the estimator uses measured
  cost-per-minute and token mix per dollar instead.
* To improve accuracy, add features that explain variance (files touched, test count, size labels at kickoff) and re-run `analyze.py`
  as new sessions accumulate.

---
Not a skill (no `SKILL.md`): a standalone script. Companion to [`usage-report`](../usage-report/README.md) (actual spend); use it to budget work before [`delivery-pipeline`](../delivery-pipeline/README.md) runs a [`project-design`](../project-design/README.md) plan. Up: [skills index](../README.md)
