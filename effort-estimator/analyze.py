#!/usr/bin/env python3 -I
"""Normalise extracted session records and build calibration.json for estimate.py."""
import glob, json, os, re, statistics as st, sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))  # run: python3 -I analyze.py  (reads data/chunk_*.jsonl)
F = ["inputTokens", "outputTokens", "cacheCreationInputTokens", "cacheReadInputTokens", "thinkingTokens", "costUSD"]
CUM_KEYS = ["cum_turn", "cum_at_turn", "mu", "event_usage"]   # per-turn *cumulative* snapshots (varies by chunk)

def ts(s): return datetime.fromisoformat(s.replace("Z", "+00:00"))

def pct(xs, p):
    xs = sorted(xs)
    if not xs: return None
    k = (len(xs) - 1) * p; f = int(k); c = min(f + 1, len(xs) - 1)
    return xs[f] + (xs[c] - xs[f]) * (k - f)

def zero(): return {k: 0.0 for k in F}
def add(a, b):
    for k in F: a[k] += (b.get(k) or 0)
def cost_of(u): return sum((v.get("costUSD") or 0) for v in u.values())

def classify(rec):
    t = rec["title"].lower(); tags = " ".join(rec.get("tags") or []).lower()
    if "mico-task" in tags or re.match(r"^m\d+\.\d+:", t): return "wave_subtask"
    if re.search(r"\bdesign\b|plan\b|architecture|requirements|analysis|test plan|options|strategy|protocol", t): return "design"
    if re.search(r"bug|issue #|\bfix|error|shaky|missing|broken|flashing|stuck|failure|limits|issues", t): return "bugfix"
    if re.search(r"setup|install|deploy|integration|connector|auth|actions|vercel|skill|knowledge", t): return "infra"
    return "feature"

def totals(rec):
    """Reconstruct whole-session per-model usage.
    Cumulative snapshots reset on /clear or resume -> sum the peak of each monotone segment.
    Delta turns are summed. Final `cum` is a floor when older turns were truncated."""
    seg_peak, seg_cost, deltas = {}, -1.0, {}
    total = {}
    def flush():
        for m, v in seg_peak.items(): add(total.setdefault(m, zero()), v)
        seg_peak.clear()
    for t in rec.get("turns", []):
        snap = next((t[k] for k in CUM_KEYS if t.get(k)), None)
        if snap is None and t.get("usage_is_cum") : snap = t["usage"]
        if snap is None and rec.get("note", "").startswith("modelUsage per result") and t.get("usage"):
            snap = t["usage"]
        if snap and "model" in snap:
            real = next((m for m in (rec.get("cum") or {}) if m != "model"), "claude-sonnet-5-5")
            snap = {real: snap["model"]}
        if snap:
            c = cost_of(snap)
            if c + 1e-9 < seg_cost: flush()
            seg_peak.clear(); seg_peak.update({m: dict(v) for m, v in snap.items()}); seg_cost = c
        elif t.get("usage"):
            for m, v in t["usage"].items(): add(deltas.setdefault(m, zero()), v)
    flush()
    for m, v in deltas.items(): add(total.setdefault(m, zero()), v)
    # floor with final cum (complete for the last process even if turns truncated)
    cum = rec.get("cum") or {}
    if cost_of(cum) > cost_of(total):
        total = {m: {k: (v.get(k) or 0) for k in F} for m, v in cum.items()}
    return total

TRUNC = re.compile(r"PARTIAL|truncat|oldest|older (events|results|turns)|hit the|12.page|cap\b", re.I)

def row(rec):
    mt = totals(rec); cost = cost_of(mt)
    turns = rec.get("turns", [])
    wall = (ts(rec["updated_at"]) - ts(rec["created_at"])).total_seconds()
    ori = lambda t: (t.get("origin") or "human")
    hum = [t for t in turns if ori(t) not in ("task-notification",) and (t.get("dur_ms") or 0) > 0]
    ntf = [t for t in turns if ori(t) == "task-notification"]
    seg, prev = 0.0, 0.0
    for t in turns:
        a = t.get("api_ms") or 0
        if a < prev: seg += prev
        prev = a
    api_total = (seg + prev) / 1000
    active = max(sum((t.get("dur_ms") or 0) for t in turns) / 1000, api_total)
    def tcost(t):
        if t.get("usage") and not any(t.get(k) for k in CUM_KEYS): return cost_of(t["usage"])
        return None
    # per-stage proxies from per-turn deltas where available
    hc = [tcost(t) for t in hum]; nc = [tcost(t) for t in ntf]
    agent_s = sum((t.get("dur_ms") or 0) for t in turns) / 1000
    r = dict(agent_s=agent_s, api_s=api_total, id=rec["id"], title=rec["title"], kind=classify(rec), origin=rec.get("origin"),
             orchestrated=bool(rec.get("parent_session_id")), truncated=bool(TRUNC.search(rec.get("note", ""))),
             created=rec["created_at"], n_turns=len(turns), n_human=len(hum), n_notif=len(ntf),
             tool_turns=sum(t.get("tool_turns") or 0 for t in turns),
             cost=cost, active_s=active, wall_s=wall, models=mt,
             main_model=max(mt, key=lambda m: mt[m]["costUSD"]) if mt else None,
             in_fresh=sum(v["inputTokens"] for v in mt.values()), out=sum(v["outputTokens"] for v in mt.values()),
             cache_write=sum(v["cacheCreationInputTokens"] for v in mt.values()),
             cache_read=sum(v["cacheReadInputTokens"] for v in mt.values()),
             think=sum(v["thinkingTokens"] for v in mt.values()),
             first_s=(hum[0]["dur_ms"] / 1000) if hum else 0,
             first_cost=(hc[0] if hc and hc[0] is not None else None),
             human_s=sum(t["dur_ms"] for t in hum) / 1000, notif_s=sum(t.get("dur_ms") or 0 for t in ntf) / 1000)
    return r

def load():
    out = []
    for f in sorted(glob.glob(os.path.join(HERE, "data", "chunk_*.jsonl"))):
        for l in open(f):
            if l.strip():
                try: out.append(json.loads(l))
                except Exception: pass
    return out

def summ(xs):
    xs = [x for x in xs if x is not None]
    return dict(n=len(xs), p10=pct(xs, .1), p25=pct(xs, .25), p50=pct(xs, .5), p80=pct(xs, .8), p90=pct(xs, .9), mean=(st.mean(xs) if xs else None)) if xs else dict(n=0)

def main():
    recs = load(); rows = [row(r) for r in recs]
    usable = [r for r in rows if r["cost"] > 0 and r["active_s"] > 0]
    complete = usable          # cost & api-time come from cumulative counters, robust to truncation
    print(f"records={len(recs)} cost>0&time>0={len(usable)} complete(not truncated)={len(complete)}", file=sys.stderr)
    cal = {"n_records": len(recs), "n_usable": len(usable), "n_complete": len(complete), "by_kind": {}, "by_model": {}}
    for kind in sorted({r["kind"] for r in usable}) + ["ALL"]:
        sub = [r for r in complete if kind == "ALL" or r["kind"] == kind]
        if len(sub) < 2: sub = [r for r in usable if kind == "ALL" or r["kind"] == kind]
        d = {k: summ([r[k] for r in sub]) for k in ["cost", "active_s", "wall_s", "n_turns", "n_human", "n_notif", "tool_turns", "out", "think", "in_fresh", "cache_write", "cache_read", "first_s", "first_cost", "human_s", "notif_s"]}
        agg = {}
        for r in sub:
            for m, v in r["models"].items(): agg[m] = agg.get(m, 0) + v["costUSD"]
        tot = sum(agg.values()) or 1
        d["model_cost_share"] = {m: round(c / tot, 3) for m, c in agg.items()}
        med = lambda f: st.median([f(r) for r in sub if r["cost"] > 0] or [0])
        d["ratios"] = dict(out_per_usd=med(lambda r: r["out"] / r["cost"]), cache_read_per_usd=med(lambda r: r["cache_read"] / r["cost"]),
                           cache_write_per_usd=med(lambda r: r["cache_write"] / r["cost"]), fresh_in_per_usd=med(lambda r: r["in_fresh"] / r["cost"]),
                           think_share=st.median([r["think"] / r["out"] for r in sub if r["out"]] or [0]),
                           usd_per_active_min=med(lambda r: r["cost"] / (r["active_s"] / 60)),
                           wall_to_active=med(lambda r: r["wall_s"] / r["active_s"]))
        d["n_sessions"] = len(sub)
        tsub = [r for r in sub if not r["truncated"] and r["agent_s"] > 0]
        d["agent_s"] = summ([r["agent_s"] for r in tsub])          # time you actually wait (sum of turn durations)
        d["api_to_agent"] = st.median([r["api_s"] / r["agent_s"] for r in tsub]) if tsub else None
        d["elapsed_s"] = summ([r["wall_s"] for r in tsub])          # created->last update (includes waiting on you/CI)
        cal["by_kind"][kind] = d
    mm = {}
    for r in usable:
        for m, v in r["models"].items():
            d = mm.setdefault(m, dict(sessions=0, **{k: 0.0 for k in F}))
            d["sessions"] += 1; add(d, v)
    # ---- per-model rates (sessions whose dominant model is m) ----
    rates = {}
    for m in mm:
        sub = [r for r in usable if r["main_model"] == m and r["active_s"] >= 60]
        if len(sub) < 3: continue
        mn = lambda f: st.median([f(r) / (r["active_s"] / 60) for r in sub])
        rates[m] = dict(n=len(sub), usd_per_min=mn(lambda r: r["cost"]), out_per_min=mn(lambda r: r["out"]),
                        think_per_min=mn(lambda r: r["think"]), fresh_per_min=mn(lambda r: r["in_fresh"]),
                        cache_write_per_min=mn(lambda r: r["cache_write"]), cache_read_per_min=mn(lambda r: r["cache_read"]),
                        usd_p80_per_min=pct([r["cost"] / (r["active_s"] / 60) for r in sub], .8))
    cal["model_rates"] = rates
    # cost percentiles restricted to the current baseline model (older models priced/behaved differently)
    cal["cost_current"] = {}
    for kind in sorted({r["kind"] for r in usable}) + ["ALL"]:
        sub = [r for r in usable if r["main_model"] == "claude-sonnet-5-5" and (kind == "ALL" or r["kind"] == kind)]
        if len(sub) >= 8:
            cal["cost_current"][kind] = dict(cost=summ([r["cost"] for r in sub]), n=len(sub),
                out=summ([r["out"] for r in sub]), cache_read=summ([r["cache_read"] for r in sub]),
                cache_write=summ([r["cache_write"] for r in sub]), fresh=summ([r["in_fresh"] for r in sub]),
                think=summ([r["think"] for r in sub]))
    # ---- stage split among untruncated sessions with a human first turn ----
    ok = [r for r in usable if not r["truncated"] and r["first_s"] > 0 and r["human_s"] > 0]
    def share(f): return st.median([f(r) for r in ok]) if ok else None
    cal["stage_split"] = {"n": len(ok), "by_kind": {}}
    for kind in sorted({r["kind"] for r in ok}) + ["ALL"]:
        sub = [r for r in ok if kind == "ALL" or r["kind"] == kind]
        if len(sub) < 3: continue
        tot = lambda r: max(r["human_s"] + r["notif_s"], 1)
        cal["stage_split"]["by_kind"][kind] = dict(
            n=len(sub),
            first_turn_time_share=st.median([r["first_s"] / tot(r) for r in sub]),
            revision_time_share=st.median([(r["human_s"] - r["first_s"]) / tot(r) for r in sub]),
            pr_ci_watch_time_share=st.median([r["notif_s"] / tot(r) for r in sub]),
            human_turns_p50=st.median([r["n_human"] for r in sub]), human_turns_p80=pct([r["n_human"] for r in sub], .8),
            notif_turns_p50=st.median([r["n_notif"] for r in sub]),
            first_turn_min_p50=st.median([r["first_s"] / 60 for r in sub]), first_turn_min_p80=pct([r["first_s"] / 60 for r in sub], .8),
            revision_turn_min_p50=st.median([(r["human_s"] - r["first_s"]) / 60 for r in sub]),
            notif_min_p50=st.median([r["notif_s"] / 60 for r in sub]))
    cal["by_model"] = mm
    json.dump({"calibration": cal, "rows": rows}, open(os.path.join(HERE, "calibration.json"), "w"), indent=1)
    print("TOTAL spend reconstructed: $%.2f over %d sessions" % (sum(r["cost"] for r in rows), len(rows)), file=sys.stderr)
    for k, d in cal["by_kind"].items():
        print(f"{k:13s} n={d['n_sessions']:3d} cost p50={d['cost']['p50']:.2f} p80={d['cost']['p80']:.2f} | active_min p50={d['active_s']['p50']/60:.1f} p80={d['active_s']['p80']/60:.1f} | wall_h p50={d['wall_s']['p50']/3600:.1f} | human_turns p50={d['n_human']['p50']}")
    print(json.dumps({m: dict(sessions=v['sessions'], cost=round(v['costUSD'], 2)) for m, v in mm.items()}))

if __name__ == "__main__":
    main()
