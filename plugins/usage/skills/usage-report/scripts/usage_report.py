#!/usr/bin/env python3
"""Estimate Claude Code API-equivalent spend and active time, per project, from local
~/.claude/projects/ session transcripts.

This is a token-cost ESTIMATE, not a billing record: if usage is covered by a Pro/Max
subscription rather than metered API billing, actual dollars charged will differ. For an
authoritative number, see claude.ai/settings/usage. It only sees transcripts on the machine
it runs on (each machine, and each cloud sandbox, keeps its own ~/.claude/projects/).

Usage:
    python3 usage_report.py                  # current calendar month (UTC), table output
    python3 usage_report.py --month 2026-09  # a specific month
    python3 usage_report.py --days 7         # last N days instead of a calendar month
    python3 usage_report.py --all-time       # no date filter
    python3 usage_report.py --json           # machine-readable output
    python3 usage_report.py --idle-minutes 30  # change the active-time gap threshold
"""
from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

PROJECTS_DIR = Path.home() / ".claude" / "projects"

# $ per million tokens: (input, output). Cache multipliers (universal, non-Fable): write
# 5m = 1.25x input, write 1h = 2x input, read = 0.1x input (cached: 2026-06-24 pricing).
PRICING: dict[str, tuple[float, float]] = {
    "claude-fable-5-1": (10.00, 50.00),
    "claude-mythos-5-1": (10.00, 50.00),
    "claude-fable-5": (10.00, 50.00),
    "claude-opus-5": (5.00, 25.00),
    "claude-opus-4-8": (5.00, 25.00),
    "claude-opus-4-7": (5.00, 25.00),
    "claude-opus-4-6": (5.00, 25.00),
    "claude-sonnet-5": (2.00, 10.00),
    # Seen in real transcripts under this exact string; not a separate line in the public
    # model table. Treated as Claude Sonnet 5 pricing (same tier; no other "sonnet-5*" id).
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-sonnet-4-6": (3.00, 15.00),
    "claude-sonnet-4-5": (3.00, 15.00),
    "claude-haiku-4-5": (1.00, 5.00),
}
CACHE_WRITE_5M_MULT = 1.25
CACHE_WRITE_1H_MULT = 2.0
CACHE_READ_MULT = 0.1
# Claude Fable 5.1 / Mythos 5.1 price cache reads at 0.025x instead of 0.1x.
CACHE_READ_MULT_OVERRIDE = {"claude-fable-5-1": 0.025, "claude-mythos-5-1": 0.025}

# Active-time ("hours") estimation: consecutive usage timestamps within this many minutes of
# each other count as one continuous active span; a larger gap (e.g. a session resumed days
# later, or an idle human) does not. This is the same heuristic style as "git-hours" tools.
DEFAULT_IDLE_MINUTES = 15.0
# Credit for an isolated event (no neighbor within the idle window) that isn't otherwise part
# of a span: a single API round-trip is rarely instant.
MIN_EVENT_SECONDS = 20.0


@dataclass
class ProjectTotals:
    token_fields: dict[str, dict[str, int]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(int))
    )  # model -> field -> count
    timestamps: list[datetime] = field(default_factory=list)


def decode_project_name(dirname: str) -> str:
    """~/.claude/projects encodes the launch cwd by replacing every "/" with "-", which is NOT
    losslessly reversible when a real path segment itself contains a "-" (e.g. "irri-vision",
    "light-eqms-backend" both collide with path-separator dashes). Resolve it properly: try
    every way of turning some subset of dashes back into slashes and keep the one that is an
    existing directory on this machine (preferring the most-split match). Falls back to the
    raw encoded name (leading dash stripped, dashes kept) if nothing resolves."""
    if not dirname.startswith("-"):
        return dirname
    parts = dirname[1:].split("-")
    if len(parts) > 20:  # pathological name; brute force would be too slow, skip it
        return "/" + "-".join(parts)
    best: list[str] | None = None
    for mask in range(1 << (len(parts) - 1)):
        segments = [parts[0]]
        for i in range(1, len(parts)):
            if mask & (1 << (i - 1)):
                segments.append(parts[i])
            else:
                segments[-1] += "-" + parts[i]
        candidate = "/" + "/".join(segments)
        if os.path.isdir(candidate) and (best is None or len(segments) > len(best)):
            best = segments
    return "/" + "/".join(best) if best is not None else "/" + "-".join(parts)


def repo_root(path: str) -> str:
    """Collapse a decoded cwd to a stable project label, so running Claude Code from a
    subdirectory doesn't fragment one project's numbers. Primary heuristic: walk up looking
    for a `.git` (dir or file, so worktrees count); that's portable across machines and
    layouts. Fallback for non-git scratch trees: collapse to /private/tmp/<name> so a live-test
    workspace's many subdirectories still group together."""
    p = Path(path)
    for candidate in [p, *p.parents]:
        if (candidate / ".git").exists():
            return str(candidate)
    parts = path.strip("/").split("/")
    if len(parts) >= 3 and parts[0] == "private" and parts[1] == "tmp":
        return "/" + "/".join(parts[:3])
    return path


def iter_usage_entries(month_start: datetime | None, until: datetime):
    """Yield (project_label, model, usage_dict, timestamp) for every assistant message with
    token usage under every project directory, across all jsonl files including nested
    subagent transcripts."""
    for project_dir in sorted(PROJECTS_DIR.iterdir()):
        if not project_dir.is_dir():
            continue
        label = repo_root(decode_project_name(project_dir.name))
        for jsonl_path in project_dir.rglob("*.jsonl"):
            try:
                with open(jsonl_path, encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            entry = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        message = entry.get("message")
                        if not isinstance(message, dict):
                            continue
                        usage = message.get("usage")
                        if not isinstance(usage, dict):
                            continue
                        ts_raw = entry.get("timestamp")
                        if not isinstance(ts_raw, str):
                            continue
                        try:
                            ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
                        except ValueError:
                            continue
                        if ts > until or (month_start is not None and ts < month_start):
                            continue
                        model = message.get("model", "unknown")
                        yield label, model, usage, ts
            except OSError:
                continue


def active_seconds(timestamps: list[datetime], idle_minutes: float) -> float:
    """Sum of gaps between consecutive sorted timestamps that are <= idle_minutes apart, plus
    a small fixed credit for any timestamp that has no such neighbor (an isolated event still
    took some real time). This collapses multi-day idle gaps (a long-paused or later-resumed
    session) to ~0 instead of counting the whole gap as "active", and naturally merges
    overlapping parallel subagent activity into one wall-clock timeline since it only looks at
    the gaps between events, not which thread produced them."""
    if not timestamps:
        return 0.0
    ts = sorted(timestamps)
    if len(ts) == 1:
        return MIN_EVENT_SECONDS
    threshold = timedelta(minutes=idle_minutes)
    total = 0.0
    for prev, curr in zip(ts, ts[1:]):
        gap = (curr - prev).total_seconds()
        if gap <= threshold.total_seconds():
            total += gap
        else:
            total += MIN_EVENT_SECONDS  # credit the event after the gap; prev already credited
    total += MIN_EVENT_SECONDS  # the very first event in the series
    return total


def price_for(model: str) -> tuple[float, float] | None:
    return PRICING.get(model)


def cost_for(fields: dict[str, int], model: str) -> float | None:
    prices = price_for(model)
    if prices is None:
        return None
    price_in, price_out = prices
    read_mult = CACHE_READ_MULT_OVERRIDE.get(model, CACHE_READ_MULT)
    return (
        fields.get("input_tokens", 0) * price_in
        + fields.get("cache_5m", 0) * price_in * CACHE_WRITE_5M_MULT
        + fields.get("cache_1h", 0) * price_in * CACHE_WRITE_1H_MULT
        + fields.get("cache_read_input_tokens", 0) * price_in * read_mult
        + fields.get("output_tokens", 0) * price_out
    ) / 1_000_000


def build_report(month_start: datetime | None, until: datetime, idle_minutes: float) -> dict:
    projects: dict[str, ProjectTotals] = defaultdict(ProjectTotals)
    unknown_models: set[str] = set()
    entries_in_window = 0

    for label, model, usage, ts in iter_usage_entries(month_start, until):
        entries_in_window += 1
        totals = projects[label]
        totals.timestamps.append(ts)
        bucket = totals.token_fields[model]
        bucket["input_tokens"] += usage.get("input_tokens", 0) or 0
        bucket["output_tokens"] += usage.get("output_tokens", 0) or 0
        bucket["cache_read_input_tokens"] += usage.get("cache_read_input_tokens", 0) or 0
        cache_creation = usage.get("cache_creation") or {}
        five_m = cache_creation.get("ephemeral_5m_input_tokens", 0) or 0
        one_h = cache_creation.get("ephemeral_1h_input_tokens", 0) or 0
        bucket["cache_5m"] += five_m
        bucket["cache_1h"] += one_h
        flat_creation = usage.get("cache_creation_input_tokens", 0) or 0
        if flat_creation and not (five_m or one_h):
            bucket["cache_5m"] += flat_creation  # assume default 5m TTL; no breakdown present

    rows = []
    total_cost = 0.0
    total_hours = 0.0
    project_hours: dict[str, float] = {}
    for label, totals in projects.items():
        project_hours[label] = active_seconds(totals.timestamps, idle_minutes) / 3600.0
        total_hours += project_hours[label]

    for label, totals in projects.items():
        project_cost = 0.0
        by_model = {}
        for model, fields in totals.token_fields.items():
            cost = cost_for(fields, model)
            if cost is None:
                unknown_models.add(model)
                continue
            by_model[model] = cost
            project_cost += cost
        total_cost += project_cost
        rows.append(
            {
                "project": label,
                "cost": project_cost,
                "by_model": by_model,
                "hours": project_hours[label],
            }
        )

    for row in rows:
        row["spend_ratio"] = row["cost"] / total_cost if total_cost else 0.0
        row["hours_ratio"] = row["hours"] / total_hours if total_hours else 0.0
        row["per_hour"] = row["cost"] / row["hours"] if row["hours"] else 0.0

    rows.sort(key=lambda r: -r["cost"])
    return {
        "window_start": month_start.isoformat() if month_start else None,
        "window_end": until.isoformat(),
        "idle_minutes": idle_minutes,
        "entries_in_window": entries_in_window,
        "unknown_models": sorted(unknown_models),
        "total_cost": total_cost,
        "total_hours": total_hours,
        "projects": rows,
    }


def print_table(report: dict) -> None:
    print(f"Window: {report['window_start'] or '(all time)'} .. {report['window_end']}")
    print(f"Usage entries in window: {report['entries_in_window']}")
    if report["unknown_models"]:
        print(f"WARNING: no pricing for models {report['unknown_models']} - excluded")
    print()
    print(f"TOTAL ESTIMATED SPEND: ${report['total_cost']:,.2f}")
    print(f"TOTAL ACTIVE HOURS:    {report['total_hours']:,.2f}")
    print()
    header = f"{'Project':<50} {'Cost':>10} {'Spend%':>8} {'Hours':>8} {'Hours%':>8} {'$/hr':>8}"
    print(header)
    print("-" * len(header))
    for row in report["projects"]:
        print(
            f"{row['project']:<50.50} {row['cost']:>10,.2f} {row['spend_ratio'] * 100:>7.1f}% "
            f"{row['hours']:>8.2f} {row['hours_ratio'] * 100:>7.1f}% {row['per_hour']:>8,.2f}"
        )
        for model, cost in sorted(row["by_model"].items(), key=lambda kv: -kv[1]):
            print(f"    {model:<46} {cost:>10,.2f}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--month", help="YYYY-MM (UTC calendar month); default: current month")
    group.add_argument("--days", type=float, help="Last N days instead of a calendar month")
    group.add_argument("--all-time", action="store_true", help="No date filter")
    parser.add_argument(
        "--idle-minutes",
        type=float,
        default=DEFAULT_IDLE_MINUTES,
        help=f"Active-time gap threshold in minutes (default {DEFAULT_IDLE_MINUTES})",
    )
    parser.add_argument("--json", action="store_true", help="Machine-readable output")
    args = parser.parse_args()

    now = datetime.now(timezone.utc)
    if args.all_time:
        month_start = None
    elif args.days is not None:
        month_start = now - timedelta(days=args.days)
    elif args.month:
        year, month = (int(x) for x in args.month.split("-"))
        month_start = datetime(year, month, 1, tzinfo=timezone.utc)
    else:
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    report = build_report(month_start, now, args.idle_minutes)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_table(report)


if __name__ == "__main__":
    main()
