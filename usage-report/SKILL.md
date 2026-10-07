---
name: usage-report
description: "Use when the user asks about their Claude Code spend, cost, usage, token usage, or how much time they've spent per project/repo this month (or in some other period) — e.g. \"what's my usage this month\", \"how much have I spent on X\", \"spend per project\", \"hours per project\". Estimates API-equivalent cost and active working hours per project/repo by parsing local ~/.claude/projects/ session transcripts. Not for official billing figures — point those requests at claude.ai/settings/usage instead and offer this skill as a supplementary local breakdown."
---

# Claude Code usage report

Estimates Claude Code spend and active time **per project**, from this machine's (or this
session's) own `~/.claude/projects/*.jsonl` transcripts. It is a **token-cost estimate**, not
an authoritative bill — see Caveats below.

## Running it

The script lives at `scripts/usage_report.py`, relative to this file. When this skill is
invoked, the harness reports this directory's actual path (e.g. a "Base directory for this
skill: ..." line, or an install under `~/.claude/skills/usage-report/`); run the script from
there with `Bash`:

```bash
python3 <skill_dir>/scripts/usage_report.py              # current month, table
python3 <skill_dir>/scripts/usage_report.py --month 2026-09
python3 <skill_dir>/scripts/usage_report.py --days 7
python3 <skill_dir>/scripts/usage_report.py --all-time
python3 <skill_dir>/scripts/usage_report.py --json       # for further processing
python3 <skill_dir>/scripts/usage_report.py --idle-minutes 30
```

No arguments needed for "this month" — that's the default. Read the output and present it to
the user (a markdown table or short prose summary both work well; don't just paste the raw
table unless they ask for raw output).

## What it reports

Per project (a project = a `.git` root found by walking up from the launch directory, or
`/private/tmp/<name>` for non-git scratch trees, so a monorepo subdirectory session doesn't
fragment that project's numbers):

- **Cost** — estimated spend at first-party metered API rates (sums `input_tokens`,
  `output_tokens`, and cache write/read tokens from every assistant message's `usage` block,
  including nested subagent transcripts, priced per the table embedded in the script).
- **Spend %** — that project's share of total estimated spend in the window.
- **Hours** — estimated *active* time: consecutive usage timestamps within `--idle-minutes`
  (default 15) of each other count as continuous activity; bigger gaps (an idle human, or a
  session resumed days later) don't inflate the number. This is computed from the merged,
  sorted timeline of *all* usage events in the project (main thread + subagents together), so
  parallel background agents don't double-count wall-clock time.
- **Hours %** — that project's share of total active hours in the window.
- **$/hr** — cost ÷ hours, derived from the two above.

## Caveats to pass along when reporting results

- **Estimate, not a bill.** If the user's Claude Code usage is covered by a Pro/Max
  subscription rather than pay-as-you-go API billing, their actual charge is the subscription
  price, not this number. For the authoritative figure, point them to
  `claude.ai/settings/usage`.
- **Local-machine/session scope only.** It only sees `~/.claude/projects/` on wherever it
  runs. Run in a cloud session, it reports that cloud session's own transcripts, not the
  user's other machines. If the user wants a combined view across machines/sessions, this
  script would need to run in each and the results added up manually (it has no mechanism to
  do that itself).
- **"Hours" is a heuristic**, same style as git-hours-type tools — reasonable for relative
  comparison between projects, not a precise time-tracking record.
- A model string seen in real transcripts, `claude-sonnet-5-5`, isn't a separate public model —
  the script prices it as Claude Sonnet 5 (same tier). Any other truly unrecognized model name
  is excluded from cost totals and surfaced as a warning rather than guessed at.

## Updating prices

Pricing lives in the `PRICING` dict near the top of `scripts/usage_report.py`. If current
prices are needed and might have changed, check the `claude-api` skill's cached model/pricing
table (or ask the user) before editing — don't guess new numbers.
