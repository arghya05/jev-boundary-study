"""Build every results table (LaTeX) and figure (PDF) for the paper from item-level data.

Usage (on the pod): python -m jevstudy.paper_assets --root /workspace/jev --out /workspace/jev/research-paper
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from . import analysis, router, stats  # noqa: E402
from .canonical import LETTERS, Task, read_jsonl  # noqa: E402

SYS = ["jev9b-s1", "jev9b-s2", "jev9b-h", "astra-high", "fable-high"]
LABEL = {"jev9b-s1": "JEV-9B S1", "jev9b-s2": "JEV-9B S2", "jev9b-h": "JEV-H harness", "astra-high": "Astra (high)", "fable-high": "Fable (high)",
         "astra-max": "Astra (max)", "fable-max": "Fable (max)"}
COLORS = {"jev9b-s1": "#2a6f97", "jev9b-s2": "#61a5c2", "jev9b-h": "#2d6a4f", "astra-high": "#c1121f", "fable-high": "#e09f3e",
          "astra-max": "#780000", "fable-max": "#9c6644"}
PANELS = [("final", "folio", "FOLIO"), ("final", "anli", "ANLI r3"), ("controlled_final", "controlled", "Controlled"),
          ("final_gpt", "judgebench", "JudgeBench-gpt"), ("final_claude", "judgebench", "JudgeBench-claude"),
          ("final", "banking77", "Banking77-16"), ("judge_track", "rewardbench", "RewardBench"),
          ("judge_track", "halueval", "HaluEval-QA")]
PRIMARY = {"FOLIO", "ANLI r3", "Controlled"}
ALL_PANELS = ["folio_final", "anli_final", "controlled_final", "judgebench_final", "banking_final",
              "folio_final_rev", "controlled_final_rev", "controlled_deep", "proofwriter_bridge", "rewardbench", "halueval"]
HD_JEV = [0.977, 0.877, 0.848, 0.799, 0.719, 0.810]   # Hard-Decisions v0.1.0, official Jev, OWA, depths 0-5
HD_LUNA = [0.933, 0.778, 0.604, 0.617, 0.446, 0.460]  # GPT-6 Luna, reasoning effort none
HD_KEV9 = [0.893, 0.738, 0.584, 0.495, 0.386, 0.412]


def pct(x, d=1):
    return "--" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{100 * x:.{d}f}"


def money(x):
    if x is None or np.isnan(x):
        return "--"
    return f"{x:.3f}" if x < 1 else f"{x:.2f}"


def write(path: Path, s: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(s)


def load(root: Path):
    pdir = root / "data" / "panels"
    tf = [pdir / f"{n}.tasks.jsonl" for n in ALL_PANELS]
    gf = [pdir / f"{n}.gold.jsonl" for n in ALL_PANELS]
    rf = sorted((root / "results" / "raw").glob("*.jsonl"))
    df = analysis.load_frame(tf, gf, rf)
    lat = analysis.load_frame(tf, gf, rf, include_latency=True)
    lat = lat[lat["mode"] == "sync-latency"]
    tasks = {d["task_id"]: Task.from_json(d) for f in tf for d in read_jsonl(f)}
    return df, lat, tasks


def panel_df(df, split, fam):
    return df[(df.split == split) & (df.family == fam) & ((df.get("m_condition").isna()) | (df.get("m_condition") == "base"))]


# ------------------------------------------------------------------ table: main accuracy and cost
def gpu_hours(root: Path) -> dict:
    """System-2 pod-hours per panel from logged run windows (track B)."""
    ev = [json.loads(l) for l in open(root / "results" / "gpu_windows.jsonl")] if (root / "results" / "gpu_windows.jsonl").exists() else []
    out = defaultdict(float)
    starts = {}
    for e in ev:
        if e["track"] != "B":
            continue
        if e["event"] == "start":
            starts[e["panel"]] = e["t"]
        elif e["panel"] in starts:
            out[e["panel"]] += (e["t"] - starts.pop(e["panel"])) / 3600
    return dict(out)


def main_table(df, out: Path, ghours: dict):
    rows, recs = [], []
    panel_file = {"FOLIO": "folio_final", "ANLI r3": "anli_final", "Controlled": "controlled_final",
                  "JudgeBench-gpt": "judgebench_final", "JudgeBench-claude": "judgebench_final", "Banking77-16": "banking_final",
                  "RewardBench": "rewardbench", "HaluEval-QA": "halueval"}
    for split, fam, name in PANELS:
        sub = panel_df(df, split, fam)
        n_panel = sub.task_id.nunique()
        for s in SYS:
            g = sub[sub.system == s]
            if g.empty:
                continue
            k, n = int(g.correct.sum()), len(g)
            lo, hi = stats.wilson(k, n)
            if s == "jev9b-s2":
                # pod-hours over the panel's batched run window, spread evenly over the panel file's rows
                h = ghours.get(panel_file[name], np.nan)
                rows_in_file = len(df[(df.system == s) & (df.family == fam) & (df.split.str.startswith(split.split("_")[0]))]) \
                    if not name.startswith("JudgeBench") else len(df[(df.system == s) & (df.family == "judgebench")])
                usd1k = 1000 * h * 0.59 / max(1, rows_in_file) if h == h else np.nan
            else:
                usd1k = 1000 * g.cost_usd.mean()
            fails = int((g.status != "ok").sum())
            rec = {"panel": name, "system": s, "n": n, "acc": k / n, "lo": lo, "hi": hi, "fail": fails, "usd_per_1k": usd1k,
                   "out_tok": g.output_tokens.mean(), "in_tok": g.input_tokens.mean()}
            recs.append(rec)
            rows.append(f"{name if s == SYS[0] else ''} & {LABEL[s]} & {n} & {pct(k / n)} & [{pct(lo)}, {pct(hi)}] & {fails} & "
                        f"{money(usd1k)} & {g.output_tokens.mean():.0f} \\\\")
        rows.append("\\addlinespace")
    body = "\n".join(rows[:-1])
    write(out / "tables" / "main.tex", rf"""\begin{{table*}}[t]
\centering\small
\caption{{Accuracy and cost on every panel. Accuracy in \%, 95\% Wilson interval; failures are scored incorrect.
Cost: USD per 1{{,}}000 decisions at list price (frontiers: billed tokens; JEV-9B S1: sequential GPU seconds; S2: pod-hours over the panel's batched run).
Output tokens include reasoning. Controlled = 288 base items (48 seeds $\times$ 6 conditions).}}
\label{{tab:main}}
\begin{{tabular}}{{@{{}}llrrcrrr@{{}}}}
\toprule
Panel & System & $n$ & Acc. & 95\% CI & Fail & \$/1k & Out tok. \\
\midrule
{body}
\bottomrule
\end{{tabular}}
\end{{table*}}
""")
    return pd.DataFrame(recs)


# ------------------------------------------------------------------ table: paired comparisons
def paired_table(df, out: Path, main: pd.DataFrame):
    prim = [(s, f, n) for s, f, n in PANELS if n in ("FOLIO", "ANLI r3")]
    sec = [(s, f, n) for s, f, n in PANELS if n in ("JudgeBench-gpt", "JudgeBench-claude", "Banking77-16")]
    jt = [(s, f, n) for s, f, n in PANELS if n in ("RewardBench", "HaluEval-QA")]
    recs, rows = [], []
    for fam_list, label in ((prim, "Primary"), (sec, "Secondary"), (jt, "Judge track")):
        m = len(fam_list) * 2
        a = 0.05 / m
        for split, fam, name in fam_list:
            sub = panel_df(df, split, fam)
            j = sub[sub.system == "jev9b-s1"].set_index("task_id")
            for fr in ("astra-high", "fable-high"):
                f = sub[sub.system == fr].set_index("task_id")
                ids = sorted(set(j.index) & set(f.index))
                rr = [{"cluster": j.cluster[i], "x": int(j.correct[i]), "y": int(f.correct[i])} for i in ids]
                if not rr:
                    continue
                res = stats.paired_delta(rr, alpha=a)
                cj = main[(main.panel == name) & (main.system == "jev9b-s1")].usd_per_1k.iloc[0]
                cf = main[(main.panel == name) & (main.system == fr)].usd_per_1k.iloc[0]
                concl = stats.classify(res, jev_cheaper=cj < cf)
                recs.append({**res, "panel": name, "frontier": fr, "family_label": label, "conclusion": concl, "m": m})
                rows.append(f"{label if (name, fr) == (fam_list[0][2], 'astra-high') else ''} & {name} & {LABEL[fr]} & "
                            f"{res['clusters']} & {res['jev_only']}/{res['frontier_only']} & {pct(res['delta'])} & "
                            f"[{pct(res['lo'])}, {pct(res['hi'])}] & {concl} \\\\")
        rows.append("\\midrule")
    body = "\n".join(rows[:-1])
    write(out / "tables" / "paired.tex", rf"""\begin{{table*}}[t]
\centering\small
\caption{{Paired comparisons of JEV-9B System~1 with each frontier (judge track: preregistration A3, $\alpha=0.05/4$). $\Delta$ = JEV-9B minus frontier accuracy (points).
Intervals are Bonferroni-adjusted within family (primary: $\alpha=0.05/4$; secondary: $\alpha=0.05/6$); cluster bootstrap where clusters repeat, Newcombe paired score interval otherwise.
Discordant = items only JEV-9B / only the frontier got right. Conclusions follow the frozen rule with a 2-point margin.}}
\label{{tab:paired}}
\begin{{tabularx}}{{\linewidth}}{{@{{}}lllrrrcX@{{}}}}
\toprule
Family & Panel & Frontier & Clusters & Discordant & $\Delta$ & Adj.\ CI & Conclusion \\
\midrule
{body}
\bottomrule
\end{{tabularx}}
\end{{table*}}
""")
    return recs


# ------------------------------------------------------------------ controlled panel
def harness_table(df, out: Path, main: pd.DataFrame):
    """A4: JEV-H vs each frontier on every panel; Bonferroni over all panel x frontier pairs."""
    names = [p for p in PANELS if not panel_df(df, p[0], p[1])[lambda d: d.system == "jev9b-h"].empty]
    m = 2 * len(names)
    a = 0.05 / max(1, m)
    rows, recs = [], []
    for split, fam, name in names:
        sub = panel_df(df, split, fam)
        h = sub[sub.system == "jev9b-h"].set_index("task_id")
        s1 = sub[sub.system == "jev9b-s1"].set_index("task_id")
        hm = main[(main.panel == name) & (main.system == "jev9b-h")]
        for fr in ("astra-high", "fable-high"):
            f = sub[sub.system == fr].set_index("task_id")
            ids = sorted(set(h.index) & set(f.index))
            if not ids:
                continue
            res = stats.paired_delta([{"cluster": h.cluster[i], "x": int(h.correct[i]), "y": int(f.correct[i])} for i in ids], alpha=a)
            cf = main[(main.panel == name) & (main.system == fr)].usd_per_1k
            ch = hm.usd_per_1k
            cheaper = bool(len(ch) and len(cf) and ch.iloc[0] < cf.iloc[0])
            concl = stats.classify(res, jev_cheaper=cheaper)
            recs.append({**res, "panel": name, "frontier": fr, "conclusion": concl, "m": m,
                         "usd1k_h": float(ch.iloc[0]) if len(ch) else None, "usd1k_f": float(cf.iloc[0]) if len(cf) else None})
            rows.append(f"{name if fr == 'astra-high' else ''} & {LABEL[fr]} & {pct(res['acc_jev'])} & {pct(res['acc_frontier'])} & "
                        f"{pct(res['delta'])} & [{pct(res['lo'])}, {pct(res['hi'])}] & {concl} \\\\")
    write(out / "tables" / "harness.tex", r"""\begin{table*}[t]
\centering\small
\caption{JEV-H harness (A4: two option orders, threshold 0.90 fixed a priori, escalation to JEV-9B's own System~2) against each frontier. $\Delta$ = JEV-H minus frontier (points); intervals Bonferroni-adjusted over all """ + str(m) + r""" panel $\times$ frontier pairs.}
\label{tab:harness}
\begin{tabularx}{\linewidth}{@{}llrrrcX@{}}
\toprule
Panel & Frontier & JEV-H & Frontier & $\Delta$ & Adj.\ CI & Conclusion \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabularx}
\end{table*}
""")
    return recs


def harness_routes(root: Path) -> dict:
    p = root / "results" / "raw" / "harness_jevh.jsonl"
    if not p.exists():
        return {}
    out = defaultdict(lambda: defaultdict(int))
    for r in read_jsonl(p):
        fam = r["task_id"].split("-")[0]
        out[fam][r["raw"]["route"]] += 1
    return {k: dict(v) for k, v in out.items()}


def judge_track_tables(df, out: Path):
    rb = df[(df.split == "judge_track") & (df.family == "rewardbench")]
    rows, recs = [], []
    secs = ["Chat", "Chat Hard", "Safety", "Reasoning"]
    for s in SYS:
        g = rb[rb.system == s]
        if g.empty:
            continue
        vals = [g[g.m_section == sec].correct.mean() for sec in secs]
        recs.append({"system": s, **dict(zip(secs, vals)), "overall": g.correct.mean(), "section_mean": float(np.nanmean(vals))})
        rows.append(f"{LABEL[s]} & " + " & ".join(pct(v) for v in vals) + f" & {pct(np.nanmean(vals))} & {pct(g.correct.mean())} \\\\")
    hv = df[(df.split == "judge_track") & (df.family == "halueval")]
    lb = None
    if not hv.empty:
        one = hv[hv.system == hv.system.iloc[0]]
        lb = evaluate_auroc_len(one)
    write(out / "tables" / "judgetrack.tex", r"""\begin{table}[t]
\centering\small
\caption{RewardBench (2{,}985 filtered pairs) accuracy (\%) by official section; ``Score'' is the unweighted section mean, ``All'' the item mean. HaluEval-QA answer-length-only AUROC (trivial baseline): """ + (f"{lb:.3f}" if lb is not None else "--") + r""".}
\label{tab:judgetrack}
\begin{tabular}{@{}lrrrrrr@{}}
\toprule
System & Chat & Chat Hard & Safety & Reasoning & Score & All \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table}
""")
    return {"rewardbench": recs, "halueval_length_auroc": lb}


def evaluate_auroc_len(one):
    from .evaluate import auroc
    # shorter answers more likely right? use -length as the score for "right"
    return auroc((-one.m_answer_chars).tolist(), (one.gold_label == "right").astype(int).tolist())


def controlled_tables(df, out: Path):
    base = df[(df.split == "controlled_final") & (df.m_condition == "base")]
    cells = base.groupby(["system", "m_depth", "m_irrelevant"]).correct.agg(["mean", "count"]).reset_index()
    rows = []
    for s in SYS:
        c = cells[cells.system == s]
        vals = []
        for d in (1, 3, 5):
            for ctx in (0, 8):
                v = c[(c.m_depth == d) & (c.m_irrelevant == ctx)]["mean"]
                vals.append(pct(v.iloc[0], 0) if len(v) else "--")
        bylab = base[base.system == s].groupby("gold_label").correct.mean()
        rows.append(f"{LABEL[s]} & " + " & ".join(vals) + " & " + " & ".join(pct(bylab.get(l), 0) for l in ("True", "False", "Unknown")) + " \\\\")
    write(out / "tables" / "controlled_cells.tex", r"""\begin{table}[t]
\centering\small
\caption{Controlled panel accuracy (\%) by dependency depth $d$ and irrelevant facts $c$ (48 seeds per cell), and by gold label (96 items each). Chance is 33\%.}
\label{tab:cells}
\begin{tabular}{@{}lcccccc|ccc@{}}
\toprule
& \multicolumn{2}{c}{$d=1$} & \multicolumn{2}{c}{$d=3$} & \multicolumn{2}{c|}{$d=5$} & \multicolumn{3}{c}{Gold label} \\
System & $c{=}0$ & $c{=}8$ & $c{=}0$ & $c{=}8$ & $c{=}0$ & $c{=}8$ & True & False & Unk. \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table}
""")
    # H1 DIDs
    a = 0.05 / 6
    recs, rows = [], []

    def rows_for(xs, ys):
        x = base[base.system == xs].set_index("task_id")
        y = base[base.system == ys].set_index("task_id")
        ids = sorted(set(x.index) & set(y.index))
        return [{"cluster": x.cluster[i], "depth": x.m_depth[i], "irrelevant": x.m_irrelevant[i],
                 "x": int(x.correct[i]), "y": int(y.correct[i])} for i in ids]

    for ys, alpha, fam in (("astra-high", a, "H1"), ("fable-high", a, "H1"), ("jev9b-s2", 0.05, "H1c")):
        rr = rows_for("jev9b-s1", ys)
        if not rr:
            continue
        for name, f, hi_, lo_ in (("depth 5 vs 1", "depth", 5, 1), ("depth 3 vs 1", "depth", 3, 1), ("distractors 8 vs 0", "irrelevant", 8, 0)):
            if fam == "H1c" and f == "irrelevant":
                continue
            r = stats.interaction(rr, f, hi_, lo_, alpha=alpha)
            recs.append({**r, "contrast": name, "vs": ys, "family": fam, "alpha": alpha})
            sig = "\\checkmark" if (r["lo"] > 0 or r["hi"] < 0) else ""
            rows.append(f"{fam} & {LABEL[ys]} & {name} & {pct(r['jev_change'])} & {pct(r['frontier_change'])} & "
                        f"{pct(r['did'])} & [{pct(r['lo'])}, {pct(r['hi'])}] & {sig} \\\\")
    write(out / "tables" / "did.tex", r"""\begin{table}[t]
\centering\small
\caption{Depth and distractor interactions on the controlled panel (points). $\Delta_J$, $\Delta_F$: change in JEV-9B~S1 and comparator accuracy between levels; DID $=\Delta_J-\Delta_F$. H1: Bonferroni $\alpha=0.05/6$; H1c (same-weights System~2 comparator): $\alpha=0.05$. Cluster bootstrap over 48 seeds. \checkmark: interval excludes 0.}
\label{tab:did}
\begin{tabular}{@{}lllrrrcc@{}}
\toprule
Fam. & Comparator & Contrast & $\Delta_J$ & $\Delta_F$ & DID & Adj.\ CI & \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table}
""")
    # paired controls
    ref = df[(df.split == "controlled_final") & (df.m_condition == "base") & (df.m_depth == 3) & (df.m_irrelevant == 8)]
    ctl = df[(df.split == "controlled_final") & df.m_condition.isin(["decision_changing", "decision_preserving"])]
    crow, crec = [], []
    for s in SYS:
        r0 = ref[ref.system == s].set_index("cluster")
        ch = ctl[(ctl.system == s) & (ctl.m_condition == "decision_changing")].set_index("cluster")
        pr = ctl[(ctl.system == s) & (ctl.m_condition == "decision_preserving")].set_index("cluster")
        ks = sorted(set(r0.index) & set(ch.index) & set(pr.index))
        if not ks:
            continue
        both = np.mean([bool(ch.correct[k] and r0.correct[k]) for k in ks])
        follows = np.mean([ch.answer[k] != r0.answer[k] for k in ks])
        inv = np.mean([pr.answer[k] == r0.answer[k] for k in ks])
        pacc = np.mean([pr.correct[k] for k in ks])
        crec.append({"system": s, "base_acc": np.mean([r0.correct[k] for k in ks]), "change_acc": np.mean([ch.correct[k] for k in ks]),
                     "both_correct": both, "answer_changed": follows, "preserve_acc": pacc, "invariant": inv, "n": len(ks)})
        crow.append(f"{LABEL[s]} & {pct(np.mean([r0.correct[k] for k in ks]), 0)} & {pct(np.mean([ch.correct[k] for k in ks]), 0)} & "
                    f"{pct(follows, 0)} & {pct(both, 0)} & {pct(pacc, 0)} & {pct(inv, 0)} \\\\")
    write(out / "tables" / "controls.tex", r"""\begin{table}[t]
\centering\small
\caption{Paired controls at $d{=}3$, $c{=}8$ (48 seeds, \%). Changing: one verified edit flips the gold label. Preserving: renamed entities and reordered premises, same label. ``Changed'' = answer differs from the base answer; ``Both'' = correct on base and edited item; ``Invariant'' = same answer as base.}
\label{tab:controls}
\begin{tabular}{@{}lrrrrrr@{}}
\toprule
& Base & \multicolumn{3}{c}{Decision-changing} & \multicolumn{2}{c}{Decision-preserving} \\
System & acc. & acc. & changed & both & acc. & invariant \\
\midrule
""" + "\n".join(crow) + r"""
\bottomrule
\end{tabular}
\end{table}
""")
    return recs, crec, cells


def controlled_figure(df, out: Path):
    base = df[(df.split == "controlled_final") & (df.m_condition == "base")]
    deep = df[(df.split == "controlled_deep")]
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.4))
    for ax, data, depths, title in ((axes[0], base, (1, 3, 5), "Controlled panel (8 rules, 48 seeds)"),
                                    (axes[1], deep, (1, 5, 9), "Deep extension A1 (12 rules, 24 seeds)")):
        for s in SYS:
            g = data[data.system == s]
            if g.empty:
                continue
            ys, los, his = [], [], []
            for d in depths:
                h = g[g.m_depth == d]
                byc = defaultdict(list)
                for r in h.itertuples():
                    byc[r.cluster].append(r.correct)
                est, lo, hi = stats.cluster_bootstrap(byc, B=2000) if byc else (np.nan,) * 3
                ys.append(est), los.append(est - lo), his.append(hi - est)
            ax.errorbar(depths, ys, yerr=[los, his], marker="o", capsize=3, label=LABEL[s], color=COLORS[s])
        ax.axhline(1 / 3, ls=":", color="grey", lw=1)
        ax.set_xticks(depths)
        ax.set_xlabel("dependency depth")
        ax.set_ylim(0, 1.03)
        ax.set_title(title, fontsize=9)
    axes[0].set_ylabel("accuracy")
    axes[0].legend(fontsize=7, loc="lower left")
    fig.tight_layout()
    fig.savefig(out / "figures" / "depth.pdf")
    plt.close(fig)


# ------------------------------------------------------------------ robustness: option reversal + effort
def robustness_tables(df, out: Path):
    rows, recs = [], []
    for orig_split, rev_split, fam, name in (("final", "final_rev", "folio", "FOLIO"), ("controlled_final", "controlled_final_rev", "controlled", "Controlled base")):
        o = df[(df.split == orig_split) & (df.family == fam) & ((df.m_condition.isna()) | (df.m_condition == "base"))]
        r = df[(df.split == rev_split) & (df.family == fam)]
        for s in SYS:
            oo = o[o.system == s].set_index("task_id")
            rr = r[r.system == s].copy()
            if rr.empty:
                continue
            rr["orig"] = rr.task_id.str.replace("-rev$", "", regex=True)
            n_ch = 3

            def unrev(a):
                return None if not isinstance(a, str) else LETTERS[n_ch - 1 - LETTERS.index(a)]
            rr["mapped"] = rr.answer.map(unrev)
            m = rr[rr.orig.isin(oo.index)]
            flips = np.mean([row.mapped != oo.answer[row.orig] for row in m.itertuples()])
            acc_o, acc_r = oo.correct.mean(), m.correct.mean()
            recs.append({"panel": name, "system": s, "acc_orig": acc_o, "acc_rev": acc_r, "flip_rate": flips, "n": len(m)})
            rows.append(f"{name if s == SYS[0] else ''} & {LABEL[s]} & {len(m)} & {pct(acc_o)} & {pct(acc_r)} & {pct(flips)} \\\\")
        rows.append("\\addlinespace")
    write(out / "tables" / "reversal.tex", r"""\begin{table}[t]
\centering\small
\caption{Option-order reversal (all systems see the reversed list). Flip rate: share of items whose answer, mapped back to the original order, differs from the original answer (\%).}
\label{tab:reversal}
\begin{tabular}{@{}llrrrr@{}}
\toprule
Panel & System & $n$ & Acc.\ orig. & Acc.\ rev. & Flip rate \\
\midrule
""" + "\n".join(rows[:-1]) + r"""
\bottomrule
\end{tabular}
\end{table}
""")
    erows, erecs = [], []
    for split, fam, name in (("final", "folio", "FOLIO"), ("controlled_final", "controlled", "Controlled base")):
        sub = df[(df.split == split) & (df.family == fam) & ((df.m_condition.isna()) | (df.m_condition == "base"))]
        for hi_s, mx in (("astra-high", "astra-max"), ("fable-high", "fable-max")):
            h, m = sub[sub.system == hi_s], sub[sub.system == mx]
            if m.empty:
                continue
            ids = sorted(set(h.task_id) & set(m.task_id))
            h2, m2 = h.set_index("task_id").loc[ids], m.set_index("task_id").loc[ids]
            erecs.append({"panel": name, "model": hi_s, "acc_high": h2.correct.mean(), "acc_max": m2.correct.mean(),
                          "out_high": h2.output_tokens.mean(), "out_max": m2.output_tokens.mean(),
                          "usd1k_high": 1000 * h2.cost_usd.mean(), "usd1k_max": 1000 * m2.cost_usd.mean(), "n": len(ids)})
            erows.append(f"{name} & {LABEL[hi_s].split(' ')[0]} & {len(ids)} & {pct(h2.correct.mean())} & {pct(m2.correct.mean())} & "
                         f"{h2.output_tokens.mean():.0f} & {m2.output_tokens.mean():.0f} & {money(1000 * h2.cost_usd.mean())} & {money(1000 * m2.cost_usd.mean())} \\\\")
    write(out / "tables" / "effort.tex", r"""\begin{table}[t]
\centering\small
\caption{Reasoning-effort sensitivity: \texttt{high} (primary) vs.\ \texttt{max} on the same items.}
\label{tab:effort}
\begin{tabular}{@{}llrrrrrrr@{}}
\toprule
& & & \multicolumn{2}{c}{Accuracy (\%)} & \multicolumn{2}{c}{Out tokens} & \multicolumn{2}{c}{\$/1k} \\
Panel & Model & $n$ & high & max & high & max & high & max \\
\midrule
""" + "\n".join(erows) + r"""
\bottomrule
\end{tabular}
\end{table}
""")
    return recs, erecs


# ------------------------------------------------------------------ length strata
def length_table(df, out: Path):
    rows, recs = [], []
    j = df[df.system == "jev9b-s1"][["task_id", "input_tokens"]].rename(columns={"input_tokens": "jev_tokens"})
    d = df.merge(j, on="task_id", how="left")
    for split, fam, name in PANELS:
        sub = panel_df(d, split, fam)
        if sub.empty:
            continue
        for s in SYS:
            g = sub[sub.system == s]
            short, long = g[g.jev_tokens <= 1024], g[g.jev_tokens > 1024]
            recs.append({"panel": name, "system": s, "n_short": len(short), "acc_short": short.correct.mean() if len(short) else None,
                         "n_long": len(long), "acc_long": long.correct.mean() if len(long) else None})
        if (sub.jev_tokens > 1024).sum() == 0:
            continue
        ns = sub[sub.system == "jev9b-s1"]
        rows.append(f"{name} & {(ns.jev_tokens <= 1024).sum()} / {(ns.jev_tokens > 1024).sum()} & " + " & ".join(
            f"{pct(r['acc_short'])} / {pct(r['acc_long'])}" for r in recs if r["panel"] == name) + " \\\\")
    write(out / "tables" / "length.tex", r"""\begin{table}[t]
\centering\small
\caption{Accuracy (\%) on inputs of at most / more than 1{,}024 JEV-9B tokens, the length on which JEV-9B was trained. Only panels with long inputs are shown.}
\label{tab:length}
\begin{tabular}{@{}lccccc@{}}
\toprule
Panel & $n$ short/long & JEV-9B S1 & JEV-9B S2 & Astra & Fable \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table}
""")
    return recs


# ------------------------------------------------------------------ routing
def routing_tables(df, tasks, out: Path):
    splits = ["final", "final_gpt", "final_claude", "controlled_final", "judge_track"]
    sub = df[df.split.isin(splits) & ((df.m_condition.isna()) | (df.m_condition == "base"))]
    res = analysis.router_evaluation(sub, tasks, splits)
    pols = ["always_jev", "always_frontier", "length_only", "family_lookup", "confidence_gate", "feature_rule", "feature_rule+conf", "oracle"]
    names = {"always_jev": "Always JEV-9B", "always_frontier": "Always frontier", "length_only": "Length only",
             "family_lookup": "Family lookup", "confidence_gate": "JEV-9B confidence gate", "feature_rule": "Feature rule",
             "feature_rule+conf": "Feature rule + conf.", "oracle": "Oracle (unattainable)"}
    rows = []
    summary = []
    for fr in ("astra-high", "fable-high"):
        r = res.get(fr)
        if not r:
            continue
        folds = r["leave_one_family_out"]
        tpl = r["unseen_template_T2"]
        for p in pols:
            accs = [folds[f][p]["accuracy"] for f in folds]
            costs = [folds[f][p]["cost_usd"] for f in folds]
            shares = [folds[f][p]["share_jev"] for f in folds]
            base_accs = [folds[f]["always_frontier"]["accuracy"] for f in folds]
            base_cost = sum(folds[f]["always_frontier"]["cost_usd"] for f in folds)
            within = sum(a >= b - 0.02 for a, b in zip(accs, base_accs))
            summary.append({"frontier": fr, "policy": p, "lofo_mean_acc": float(np.mean(accs)), "lofo_cost": float(sum(costs)),
                            "cost_vs_frontier": float(sum(costs) / base_cost) if base_cost else None, "folds_within_2pt": within,
                            "n_folds": len(folds), "share_jev": float(np.mean(shares)),
                            "T2_acc": tpl[p]["accuracy"] if tpl else None, "T2_share_jev": tpl[p]["share_jev"] if tpl else None})
            rows.append(f"{LABEL[fr].split(' ')[0] if p == pols[0] else ''} & {names[p]} & {pct(np.mean(accs))} & "
                        f"{within}/{len(folds)} & {pct(np.mean(shares), 0)} & {(sum(costs) / base_cost if base_cost else 0):.2f} & "
                        f"{pct(tpl[p]['accuracy']) if tpl else '--'} & {pct(tpl[p]['share_jev'], 0) if tpl else '--'} \\\\")
        rows.append("\\midrule")
    write(out / "tables" / "routing.tex", r"""\begin{table*}[t]
\centering\small
\caption{Selection rules (H3). Leave-one-family-out over five families: mean held-out accuracy (\%), number of folds within 2 points of always-frontier, share of items sent to JEV-9B (\%), and total cost relative to always-frontier. Unseen template: rules fit on everything except controlled template T2, evaluated on T2 items.}
\label{tab:routing}
\begin{tabular}{@{}llrrrrrr@{}}
\toprule
& & \multicolumn{4}{c}{Leave one family out} & \multicolumn{2}{c}{Unseen template T2} \\
Frontier & Policy & Acc. & Within 2 pt & To JEV & Cost ratio & Acc. & To JEV \\
\midrule
""" + "\n".join(rows[:-1]) + r"""
\bottomrule
\end{tabular}
\end{table*}
""")
    # per-fold detail for the appendix
    det = []
    for fr in ("astra-high", "fable-high"):
        for fam, pol in (res.get(fr) or {}).get("leave_one_family_out", {}).items():
            for p, v in pol.items():
                det.append({"frontier": fr, "held_out": fam, "policy": p, **{k: v[k] for k in ("accuracy", "cost_usd", "share_jev")}})
    return summary, det, res


# ------------------------------------------------------------------ bridge
def bridge_table(df, out: Path):
    b = df[(df.split == "bridge") & (df.system == "jev9b-s1")]
    rows, recs = [], []
    accs = []
    for d in range(6):
        g = b[b.m_depth == d]
        k, n = int(g.correct.sum()), len(g)
        lo, hi = stats.wilson(k, n) if n else (np.nan, np.nan)
        accs.append(k / n if n else np.nan)
        recs.append({"depth": d, "n": n, "jev9b": k / n if n else None, "lo": lo, "hi": hi, "official_jev_hd": HD_JEV[d], "luna_off_hd": HD_LUNA[d]})
        rows.append(f"{d} & {n} & {pct(k / n if n else None)} & [{pct(lo)}, {pct(hi)}] & {pct(HD_JEV[d])} & {pct(HD_KEV9[d])} & {pct(HD_LUNA[d])} \\\\")
    byl = b.groupby("gold_label").correct.mean()
    write(out / "tables" / "bridge.tex", r"""\begin{table}[t]
\centering\small
\caption{ProofWriter bridge (A2, exploratory). JEV-9B~S1 accuracy (\%) on 900 open-world items (50 per depth $\times$ label) with Hard-Decisions' task wording, beside official Jev, Kev-9B and GPT-6 Luna (reasoning off) as published by Hard-Decisions on a different sample of the same strata. JEV-9B by label: """ +
          ", ".join(f"{l} {pct(byl.get(l))}" for l in ("true", "false", "unknown")) + r""".}
\label{tab:bridge}
\begin{tabular}{@{}rrrcrrr@{}}
\toprule
Depth & $n$ & JEV-9B S1 & 95\% CI & Official Jev & Kev-9B & Luna (off) \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table}
""")
    fig, ax = plt.subplots(figsize=(4.6, 3.2))
    ax.plot(range(6), accs, "o-", color=COLORS["jev9b-s1"], label="JEV-9B S1 (this study)")
    ax.plot(range(6), HD_JEV, "s--", color="#3a5a40", label="Official Jev (Hard-Decisions)")
    ax.plot(range(6), HD_KEV9, "^--", color="#999999", label="Kev-9B (Hard-Decisions)")
    ax.plot(range(6), HD_LUNA, "d--", color=COLORS["astra-high"], label="GPT-6 Luna, reasoning off (H-D)")
    ax.axhline(1 / 3, ls=":", color="grey", lw=1)
    ax.set_xlabel("ProofWriter proof depth")
    ax.set_ylabel("accuracy (open world)")
    ax.set_ylim(0, 1.02)
    ax.legend(fontsize=6.5, loc="lower left")
    fig.tight_layout()
    fig.savefig(out / "figures" / "bridge.pdf")
    plt.close(fig)
    return recs


# ------------------------------------------------------------------ operating points figure + latency
def operating_points(main: pd.DataFrame, out: Path):
    names = [p[2] for p in PANELS]
    fig, axes = plt.subplots(2, 3, figsize=(10, 5.6), sharey=False)
    for ax, name in zip(axes.flat, names):
        m = main[main.panel == name]
        for r in m.itertuples():
            ax.errorbar(max(r.usd_per_1k, 1e-3), r.acc, yerr=[[r.acc - r.lo], [r.hi - r.acc]], fmt="o", color=COLORS[r.system],
                        label=LABEL[r.system], capsize=2)
            if r.system in ("astra-high", "fable-high"):
                ax.scatter(max(r.usd_per_1k / 2, 1e-3), r.acc, marker="x", color=COLORS[r.system], s=18)
        ax.set_xscale("log")
        ax.set_title(name, fontsize=9)
        ax.set_xlabel("USD per 1,000 decisions (log)", fontsize=7)
        ax.tick_params(labelsize=7)
    axes[0, 0].set_ylabel("accuracy")
    axes[1, 0].set_ylabel("accuracy")
    h, l = axes[0, 0].get_legend_handles_labels()
    fig.legend(h, l, loc="lower center", ncol=4, fontsize=8)
    fig.tight_layout(rect=(0, 0.06, 1, 1))
    fig.savefig(out / "figures" / "operating_points.pdf")
    plt.close(fig)


def latency_table(lat: pd.DataFrame, out: Path):
    rows, recs = [], []
    for s in ("jev9b-s1", "astra-high", "fable-high"):
        g = lat[lat.system == s]
        if g.empty:
            continue
        q = g.latency_s.quantile([0.5, 0.9, 0.95]).values
        recs.append({"system": s, "n": len(g), "p50": q[0], "p90": q[1], "p95": q[2], "mean": g.latency_s.mean(),
                     "usd1k": 1000 * g.cost_usd.mean(), "acc": g.correct.mean()})
        rows.append(f"{LABEL[s]} & {len(g)} & {q[0]:.2f} & {q[1]:.2f} & {q[2]:.2f} & {money(1000 * g.cost_usd.mean())} & {pct(g.correct.mean())} \\\\")
    write(out / "tables" / "latency.tex", r"""\begin{table}[t]
\centering\small
\caption{Interactive latency on a sealed 100-item FOLIO subset: fresh synchronous calls, concurrency 1, non-streaming, interleaved provider order, from the same pod. Seconds from dispatch to complete response. JEV-9B runs on the pod's GPU without a network hop, so its latency is not like-for-like with remote APIs.}
\label{tab:latency}
\begin{tabular}{@{}lrrrrrr@{}}
\toprule
System & $n$ & p50 & p90 & p95 & \$/1k & Acc.\ (\%) \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table}
""")
    return recs


def confidence_figure(df, out: Path):
    j = df[(df.system == "jev9b-s1") & df.conf.notna() & ~df.split.isin(["bridge", "final_rev", "controlled_final_rev"])]
    fig, ax = plt.subplots(figsize=(4.4, 3.2))
    for fam, g in j.groupby("family"):
        bins = np.linspace(0.3, 1.0, 8)
        idx = np.digitize(g.conf, bins)
        xs, ys = [], []
        for b in range(1, len(bins) + 1):
            h = g[idx == b]
            if len(h) >= 15:
                xs.append(h.conf.mean())
                ys.append(h.correct.mean())
        ax.plot(xs, ys, "o-", label=fam, ms=3)
    ax.plot([0.3, 1], [0.3, 1], ":", color="grey")
    ax.set_xlabel("JEV-9B top probability")
    ax.set_ylabel("observed accuracy")
    ax.legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(out / "figures" / "calibration.pdf")
    plt.close(fig)


def routing_detail_table(det: list, out: Path):
    d = pd.DataFrame(det)
    if d.empty:
        write(out / "tables" / "routing_detail.tex", "")
        return
    pols = ["always_jev", "always_frontier", "confidence_gate", "feature_rule", "feature_rule+conf", "oracle"]
    rows = []
    for fr in ("astra-high", "fable-high"):
        for fam in sorted(d[d.frontier == fr].held_out.unique()):
            g = d[(d.frontier == fr) & (d.held_out == fam)].set_index("policy")
            rows.append(f"{LABEL[fr].split(' ')[0]} & {fam} & " + " & ".join(
                f"{pct(g.accuracy[p])}/{pct(g.share_jev[p], 0)}" if p in g.index else "--" for p in pols) + " \\\\")
    write(out / "tables" / "routing_detail.tex", r"""\begin{table*}[t]
\centering\small
\caption{Leave-one-family-out detail: held-out accuracy (\%) / share routed to JEV-9B (\%) per policy.}
\label{tab:routingdetail}
\begin{tabular}{@{}llcccccc@{}}
\toprule
Frontier & Held-out family & Always JEV & Always frontier & Conf.\ gate & Feature rule & Rule + conf. & Oracle \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table*}
""")


def cost_ledger_table(root: Path, df: pd.DataFrame, gh: dict, out: Path):
    api = df[df.system.isin(["astra-high", "fable-high", "astra-max", "fable-max"])]
    pan = {"final": "public", "final_gpt": "public", "final_claude": "public"}
    g = api.groupby(["system", "family"]).agg(n=("task_id", "size"), usd=("cost_usd", "sum"),
                                              in_tok=("input_tokens", "sum"), out_tok=("output_tokens", "sum")).reset_index()
    rows = [f"{LABEL[r.system]} & {r.family} & {r.n} & {r.in_tok / 1e6:.2f} & {r.out_tok / 1e6:.3f} & {r.usd:.2f} \\\\" for r in g.itertuples()]
    led = [json.loads(l) for l in open(root / "results" / "budget_ledger.jsonl")]
    tot = defaultdict(float)
    for e in led:
        if e["event"] == "settle":
            tot[e["system"].replace("-batch", "")] += e["cost_usd"]
    api_total = sum(v for k, v in tot.items() if k.startswith(("astra", "fable")))
    pod_h = sum(gh.values())
    sess = json.load(open(root / "results" / "pod_sessions.json")) if (root / "results" / "pod_sessions.json").exists() else {}
    write(out / "tables" / "cost_ledger.tex", r"""\begin{table}[t]
\centering\small
\caption{Study cost ledger. API rows: billed usage at list price on the final, ablation and exploratory panels (development calls appear only in the ledger total). Ledger total for all API calls including probes: \$""" + f"{api_total:.2f}" + r""". System~2 pod-hours over its run windows: """ + f"{pod_h:.1f}" + r""" h (\$""" + f"{pod_h * 0.59:.2f}" + r""" at \$0.59/h); the whole pod's rental is reported in the text.}
\label{tab:ledger}
\begin{tabular}{@{}llrrrr@{}}
\toprule
System & Family & Calls & In (M tok) & Out (M tok) & USD \\
\midrule
""" + "\n".join(rows) + r"""
\bottomrule
\end{tabular}
\end{table}
""")
    return {"api_total_ledger": api_total, "by_system": dict(tot), "s2_pod_hours": pod_h}


def cost_summary(root: Path, df: pd.DataFrame) -> dict:
    led = [json.loads(l) for l in open(root / "results" / "budget_ledger.jsonl")]
    by = defaultdict(float)
    for e in led:
        if e["event"] == "settle":
            by[e["system"]] += e["cost_usd"]
    api = {k: v for k, v in by.items() if k.startswith(("astra", "fable"))}
    return {"api_usd_by_system": api, "api_usd_total": sum(api.values())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="research-paper")
    a = ap.parse_args()
    root, out = Path(a.root), Path(a.out)
    (out / "figures").mkdir(parents=True, exist_ok=True)
    df, lat, tasks = load(root)
    df.to_csv(root / "results" / "final_item_level.csv", index=False)
    gh = gpu_hours(root)
    main_df = main_table(df, out, gh)
    paired = paired_table(df, out, main_df)
    did, ctrl, cells = controlled_tables(df, out)
    controlled_figure(df, out)
    rev, eff = robustness_tables(df, out)
    length = length_table(df, out)
    routing, routing_detail, _ = routing_tables(df, tasks, out)
    routing_detail_table(routing_detail, out)
    harness = harness_table(df, out, main_df)
    judge = judge_track_tables(df, out)
    ledger = cost_ledger_table(root, df, gh, out)
    bridge = bridge_table(df, out)
    operating_points(main_df, out)
    latency = latency_table(lat, out)
    confidence_figure(df, out)
    deep = df[df.split == "controlled_deep"].groupby(["system", "m_depth"]).correct.agg(["mean", "count"]).reset_index()
    summary = {"main": main_df.to_dict("records"), "paired": paired, "did": did, "controls": ctrl,
               "reversal": rev, "effort": eff, "length": length, "routing": routing, "routing_detail": routing_detail,
               "bridge": bridge, "latency": latency, "deep": deep.to_dict("records"), "gpu_hours": gh,
               "cost": cost_summary(root, df), "ledger": ledger, "harness": harness, "harness_routes": harness_routes(root),
               "judge_track": judge, "n_items": int(df.task_id.nunique()), "n_rows": int(len(df)),
               "status_counts": df.groupby(["system", "status"]).size().reset_index().to_dict("records")}
    analysis.write_json(summary, root / "results" / "final_summary.json")
    print(json.dumps({k: (v if k in ("paired",) else "...") for k, v in summary.items()}, indent=1, default=str)[:6000])


if __name__ == "__main__":
    main()
