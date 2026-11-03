# usage-report

Estimates Claude Code spend (API-equivalent, not a bill) and active hours per project from local `~/.claude/projects/*.jsonl` transcripts.

- **Use when:** "what's my usage this month", "spend per project", "hours per project".
- **Run:** `python3 scripts/usage_report.py [--month YYYY-MM | --days N | --all-time | --json | --idle-minutes N]` ([script](scripts/usage_report.py)).
- **Related:** [`effort-estimator`](../effort-estimator/README.md) uses the same transcripts to forecast cost/time for a new task. Official billing: claude.ai/settings/usage.

Entry point: [`SKILL.md`](SKILL.md) · Up: [skills index](../README.md)
