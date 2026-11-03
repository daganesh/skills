#!/usr/bin/env python3
"""Effort estimator calibrated on your past Claude Code sessions.

Examples
  python3 estimate.py --kind feature --size M
  python3 estimate.py --kind feature --size L --design --model opus
  python3 estimate.py --kind bugfix --size S --json
  python3 estimate.py --tasks "feature:L:design,bugfix:S,infra:M"    # a whole plan, summed

kind : feature | bugfix | design | infra | wave_subtask      (wave_subtask = small spec'd unit from an orchestrator)
size : XS | S | M | L | XL   -> P10 | P25 | P50 | P80 | P90 of your own history for that kind
model: auto | sonnet | opus | haiku    (scales cost by the observed cost-per-minute ratio vs sonnet-5-5)

Numbers are percentiles of what your sessions actually did, not guarantees. Budget with the
'P80' column; use 'P50' for the expected value.
"""
import argparse, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CAL = json.load(open(os.path.join(HERE, "calibration.json")))["calibration"]
SIZE_Q = {"XS": "p10", "S": "p25", "M": "p50", "L": "p80", "XL": "p90"}
MODEL_ALIAS = {"sonnet": "claude-sonnet-5-5", "opus": "claude-opus-5-5", "haiku": "claude-haiku-5-5"}
BASE = "claude-sonnet-5-5"

def fmt_min(m):
    return f"{m:.0f} min" if m < 90 else f"{m/60:.1f} h"

def fmt_tok(n):
    return f"{n/1e6:.1f}M" if n >= 1e6 else f"{n/1e3:.0f}k"

def pick_model(kind, size):
    """Heuristic from observed usage + cost ratios (NOT a quality benchmark)."""
    if kind == "design" and size in ("L", "XL"):
        return "opus", "large design/architecture work: where your history spent on Opus; ~2x cost/min of Sonnet"
    if size in ("XS", "S") and kind in ("bugfix", "infra"):
        return "haiku", "tiny, well-scoped fix: Haiku is ~0.35x cost/min (weak evidence, few sessions)"
    return "sonnet", "default workhorse for feature/bugfix/infra in your history (most sessions, best-covered data)"

def model_mult(model_id):
    r = CAL["model_rates"]
    if model_id not in r or BASE not in r:
        return 1.0, "no data"
    return r[model_id]["usd_per_min"] / r[BASE]["usd_per_min"], f"n={r[model_id]['n']} sessions"

def estimate(kind, size, model="auto", design=False):
    q = SIZE_Q[size]
    byk = CAL["by_kind"].get(kind)
    if not byk:
        raise SystemExit(f"unknown kind {kind}; choose from {list(CAL['by_kind'])}")
    cur = CAL["cost_current"].get(kind) or CAL["cost_current"]["ALL"]
    why = ""
    if model == "auto":
        model, why = pick_model(kind, size)
    model_id = MODEL_ALIAS.get(model, model)
    mult, mult_note = model_mult(model_id)

    def tier(d, key):  # robust percentile lookup with fallback to p50
        return d[key].get(q) if d[key].get(q) is not None else d[key]["p50"]

    cost_base = tier(cur, "cost")
    cost_p50_base = cur["cost"]["p50"]; cost_p80_base = cur["cost"]["p80"]
    agent_min = tier(byk, "agent_s") / 60
    elapsed_h = tier(byk, "elapsed_s") / 3600

    # token mix per dollar, from sessions on the current model; scaled to the estimate
    scale = lambda key: (tier(cur, key) / max(cur["cost"][q], 1e-9)) * cost_base * mult
    tokens = dict(output=scale("out"), thinking_incl_in_output=scale("think"), fresh_input=scale("fresh"),
                  cache_write=scale("cache_write"), cache_read=scale("cache_read"))

    # stage split (turn-time shares) -> apportion time & cost
    ss = CAL["stage_split"]["by_kind"].get(kind) or CAL["stage_split"]["by_kind"]["ALL"]
    shares = {"Implement: first autonomous build turn": ss["first_turn_time_share"],
              "Revise: your follow-up turns": ss["revision_time_share"],
              "PR/CI watch & merge wake-ups": ss["pr_ci_watch_time_share"]}
    tot = sum(shares.values()) or 1
    stages = []
    for name, sh in shares.items():
        f = sh / tot
        stages.append(dict(stage=name, share=f, agent_min=agent_min * f, cost_usd=cost_base * mult * f))
    if design:
        dz = CAL["by_kind"]["design"]; dc = CAL["cost_current"]["design"]
        d_q = q
        stages.insert(0, dict(stage="Design: plan / doc session (separate session)", share=None,
                              agent_min=(dz["agent_s"].get(d_q) or dz["agent_s"]["p50"]) / 60,
                              cost_usd=(dc["cost"].get(d_q) or dc["cost"]["p50"]) * mult))
    total_cost = sum(s["cost_usd"] for s in stages)
    total_min = sum(s["agent_min"] for s in stages)
    return dict(kind=kind, size=size, percentile=q.upper(), model=model_id, model_why=why,
                model_cost_multiplier=round(mult, 2), model_multiplier_basis=mult_note,
                agent_minutes=total_min, elapsed_hours_calendar=elapsed_h + (stages[0]["agent_min"] / 60 if design else 0),
                cost_usd=dict(selected=total_cost, p50=cost_p50_base * mult, p80=cost_p80_base * mult),
                tokens=tokens, stages=stages, n_cost=cur.get("n"), n_time=byk["agent_s"]["n"],
                human_turns_p50=ss["human_turns_p50"], human_turns_p80=ss["human_turns_p80"])

def show(e):
    print(f"\n=== {e['kind']} / size {e['size']} ({e['percentile']} of your history) ===")
    print(f"Model       : {e['model']}  (x{e['model_cost_multiplier']} cost vs {BASE}; {e['model_multiplier_basis']})")
    if e["model_why"]: print(f"  why       : {e['model_why']}")
    print(f"Agent time  : {fmt_min(e['agent_minutes'])} of working time (+ your review gaps)  | calendar elapsed to merge ~ {e['elapsed_hours_calendar']:.1f} h typical")
    print(f"Cost        : ${e['cost_usd']['selected']:.2f}   (kind P50 ${e['cost_usd']['p50']:.2f} / P80 ${e['cost_usd']['p80']:.2f} for this model)")
    t = e["tokens"]
    print(f"Tokens      : output {fmt_tok(t['output'])} (thinking {fmt_tok(t['thinking_incl_in_output'])}), "
          f"cache-read {fmt_tok(t['cache_read'])}, cache-write {fmt_tok(t['cache_write'])}, fresh input {fmt_tok(t['fresh_input'])}")
    print(f"Your turns  : ~{e['human_turns_p50']:.0f} follow-up turns typical, {e['human_turns_p80']:.0f} at P80")
    print("Stages:")
    for s in e["stages"]:
        print(f"  - {s['stage']:<46} {fmt_min(s['agent_min']):>8}   ${s['cost_usd']:.2f}")
    print(f"  (basis: {e['n_cost']} cost sessions, {e['n_time']} timed sessions)")

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kind", default="feature"); ap.add_argument("--size", default="M", choices=list(SIZE_Q))
    ap.add_argument("--model", default="auto"); ap.add_argument("--design", action="store_true")
    ap.add_argument("--tasks", help="comma list kind:size[:design], summed")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    items = []
    if a.tasks:
        for part in a.tasks.split(","):
            f = part.split(":"); items.append(estimate(f[0], f[1].upper(), a.model, "design" in f[2:]))
    else:
        items.append(estimate(a.kind, a.size.upper(), a.model, a.design))
    if a.json:
        print(json.dumps(items if len(items) > 1 else items[0], indent=2)); return
    for e in items: show(e)
    if len(items) > 1:
        print(f"\nPLAN TOTAL: {fmt_min(sum(e['agent_minutes'] for e in items))} agent time, "
              f"${sum(e['cost_usd']['selected'] for e in items):.2f}, "
              f"{fmt_tok(sum(e['tokens']['output'] for e in items))} output tokens")

if __name__ == "__main__":
    main()
