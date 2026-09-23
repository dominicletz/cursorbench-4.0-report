#!/usr/bin/env python3
"""CursorBench 4.0 report — scales match official cursor.com/cursorbench chart."""

import base64
import json
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import numpy as np

OUT = Path(__file__).resolve().parent

# Official chart axis logic (from cursor.com/cursorbench JS):
# X cost: LINEAR 0 → max(2*ceil(maxCost/2), 2) → for Fable Max $17.28 → $18
# Y score: min = floor(min(20, minScore)/5)*5 ; max = floor(maxScore/5)*5 + 5
#          → for our scope (24.3..57.8) → 20..60, ticks every 5
X_MAX = 18
X_TICKS = [0, 3, 6, 9, 12, 15, 18]
Y_MIN, Y_MAX = 20, 60
Y_TICKS = list(range(Y_MIN, Y_MAX + 1, 5))

SERIES_COLORS = {
    "Opus 5.5": "#F59E0B",
    "Fable 5.1": "#FB923C",
    "Grok 4.7": "#3B82F6",
    "Muse Spark 1.3": "#A855F7",
    "GPT-6 Astra": "#22C55E",
    "GPT-6 Luna": "#22C55E",
}

EFFORT_ORDER = ["minimal", "low", "medium", "high", "xhigh", "extra high", "max"]

LABEL_MODELS = {
    "Opus 5.5 Max",
    "Opus 5.5 High",
    "Opus 5.5 Medium",
    "Opus 5.5 Low",
    "Fable 5.1 Max",
    "Fable 5.1 High",
    "Fable 5.1 Low",
    "Grok 4.7 Extra High",
    "Grok 4.7 Medium",
    "Grok 4.7 Low",
    "Muse Spark 1.3 Max",
    "Muse Spark 1.3 High",
    "Muse Spark 1.3 Minimal",
    "GPT-6 Astra Max",
    "GPT-6 Luna Max",
}

LABEL_OFFSETS = {
    "Opus 5.5 Max": (10, 8),
    "Opus 5.5 High": (-95, 10),
    "Opus 5.5 Medium": (-110, -14),
    "Opus 5.5 Low": (-90, -12),
    "Fable 5.1 Max": (10, -14),
    "Fable 5.1 High": (10, 8),
    "Fable 5.1 Low": (10, -12),
    "Grok 4.7 Extra High": (10, 10),
    "Grok 4.7 Medium": (10, -14),
    "Grok 4.7 Low": (10, 8),
    "Muse Spark 1.3 Max": (-130, 10),
    "Muse Spark 1.3 High": (-120, -12),
    "Muse Spark 1.3 Minimal": (10, -12),
    "GPT-6 Astra Max": (12, 14),
    "GPT-6 Luna Max": (10, -16),
}


def load_points():
    with open(OUT / "data.json") as f:
        return json.load(f)["points"]


def load_throughput():
    with open(OUT / "throughput.json") as f:
        return json.load(f)


def effort_key(m) -> int:
    name = m["model"] if isinstance(m, dict) else str(m)
    lower = name.lower()
    for i, key in enumerate(EFFORT_ORDER):
        if lower.endswith(" " + key) or lower.endswith("-" + key):
            return i
    return 50


def style_dark(ax, fig):
    fig.patch.set_facecolor("#0B1220")
    ax.set_facecolor("#111827")
    ax.tick_params(colors="#9CA3AF", labelsize=9)
    for spine in ax.spines.values():
        spine.set_color("#1F2A44")
    ax.xaxis.label.set_color("#E5E7EB")
    ax.yaxis.label.set_color("#E5E7EB")
    ax.title.set_color("#F9FAFB")
    ax.grid(True, which="major", color="#1F2937", linestyle="-", linewidth=0.7, alpha=0.85)


def make_scatter(models):
    fig, ax = plt.subplots(figsize=(12.5, 8.2), dpi=160)
    style_dark(ax, fig)

    # Connect effort tiers within each series (Low → … → Max by effort order)
    by_series = defaultdict(list)
    for m in models:
        if not m["estimated"]:
            by_series[m["series"]].append(m)
    for series, pts in by_series.items():
        pts = sorted(pts, key=effort_key)
        xs = [p["cost"] for p in pts]
        ys = [p["score"] for p in pts]
        ax.plot(
            xs, ys,
            color=SERIES_COLORS[series],
            linewidth=2.2,
            alpha=0.85,
            zorder=3,
            solid_capstyle="round",
        )

    for m in models:
        color = SERIES_COLORS[m["series"]]
        x, y = m["cost"], m["score"]
        if m["estimated"]:
            ax.scatter(
                [x], [y],
                s=180,
                facecolors="none",
                edgecolors=color,
                linewidths=2.4,
                linestyle="--",
                zorder=5,
                marker="o",
            )
            ax.scatter(
                [x], [y],
                s=48,
                facecolors=color,
                edgecolors="none",
                alpha=0.35,
                zorder=4,
            )
        else:
            ax.scatter(
                [x], [y],
                s=105,
                c=color,
                edgecolors="#0B1220",
                linewidths=0.8,
                zorder=4,
                alpha=0.95,
            )

    # Official scales: linear cost 0–18, score 20–60
    ax.set_xlim(0, X_MAX)
    ax.set_ylim(Y_MIN, Y_MAX)
    ax.set_xticks(X_TICKS)
    ax.set_xticklabels([f"${t}" if t else "$0" for t in X_TICKS])
    ax.set_yticks(Y_TICKS)
    ax.set_xlabel("Cost / task", fontsize=11, labelpad=10)
    ax.set_ylabel("Score", fontsize=11, labelpad=10)
    ax.set_title(
        "CursorBench 4.0 — Score vs Cost",
        fontsize=16,
        fontweight="bold",
        pad=18,
        color="#F9FAFB",
    )
    fig.text(
        0.5,
        0.955,
        "Scales match official cursor.com/cursorbench (linear cost $0–$18 · score 20–60%)  ·  Lines connect effort tiers",
        ha="center",
        va="top",
        fontsize=9,
        color="#9CA3AF",
        style="italic",
    )

    for m in models:
        if m["model"] not in LABEL_MODELS:
            continue
        dx, dy = LABEL_OFFSETS.get(m["model"], (8, 8))
        color = SERIES_COLORS[m["series"]]
        if m["estimated"]:
            ax.annotate(
                f"{m['model']}*  EST",
                xy=(m["cost"], m["score"]),
                xytext=(dx, dy),
                textcoords="offset points",
                fontsize=8.5,
                color=color,
                fontweight="bold",
                fontstyle="italic",
                arrowprops=dict(
                    arrowstyle="-",
                    color=color,
                    lw=0.9,
                    linestyle="dashed",
                    alpha=0.75,
                ),
                zorder=6,
            )
        else:
            ax.annotate(
                m["model"],
                xy=(m["cost"], m["score"]),
                xytext=(dx, dy),
                textcoords="offset points",
                fontsize=7.8,
                color="#D1D5DB",
                arrowprops=dict(arrowstyle="-", color="#4B5563", lw=0.55, alpha=0.55)
                if abs(dx) > 20 or abs(dy) > 10
                else None,
                zorder=6,
            )

    family_handles = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=c, markersize=9, label=s)
        for s, c in [
            ("Opus 5.5", SERIES_COLORS["Opus 5.5"]),
            ("Fable 5.1", SERIES_COLORS["Fable 5.1"]),
            ("Grok 4.7", SERIES_COLORS["Grok 4.7"]),
            ("Muse Spark 1.3", SERIES_COLORS["Muse Spark 1.3"]),
            ("GPT-6 est.", SERIES_COLORS["GPT-6 Astra"]),
        ]
    ]
    leg = ax.legend(
        handles=family_handles,
        loc="lower right",
        frameon=True,
        fontsize=8.5,
        title="Model family",
        title_fontsize=9,
    )
    leg.get_frame().set_facecolor("#1A2332")
    leg.get_frame().set_edgecolor("#374151")
    for t in leg.get_texts():
        t.set_color("#E5E7EB")
    leg.get_title().set_color("#F9FAFB")

    fig.text(
        0.02,
        0.012,
        "* Estimates from FrontierCode 1.1 + Terminal-Bench 4.0. Cursor has not run GPT-6. Axes match official CB linear cost / score domains.",
        fontsize=7.5,
        color="#6B7280",
        ha="left",
    )

    plt.tight_layout(rect=[0, 0.035, 1, 0.94])
    path = OUT / "cursorbench-4.0-score-vs-cost.png"
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


def make_bar(models):
    ranked = sorted(models, key=lambda m: m["score"], reverse=True)
    fig, ax = plt.subplots(figsize=(11.5, 10.2), dpi=160)
    style_dark(ax, fig)

    y_pos = np.arange(len(ranked))
    scores = [m["score"] for m in ranked]
    colors = [SERIES_COLORS[m["series"]] for m in ranked]
    bars = ax.barh(y_pos, scores, color=colors, edgecolor="#0B1220", height=0.72, alpha=0.92)

    for i, m in enumerate(ranked):
        if m["estimated"]:
            bars[i].set_hatch("///")
            bars[i].set_alpha(0.75)
            bars[i].set_linewidth(1.5)
            bars[i].set_edgecolor(SERIES_COLORS[m["series"]])
            bars[i].set_linestyle("--")

    labels = [
        f"{m['model']} (est.)" if m["estimated"] else m["model"]
        for m in ranked
    ]
    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, fontsize=8.8)
    ax.invert_yaxis()
    # Match official score domain end (60) for bar width too
    ax.set_xlim(0, Y_MAX)
    ax.set_xticks(Y_TICKS)
    ax.set_xlabel("Score (%)", fontsize=11, labelpad=8)
    ax.set_title(
        "CursorBench 4.0 — Top configs by score",
        fontsize=15,
        fontweight="bold",
        pad=14,
        color="#F9FAFB",
    )
    fig.text(
        0.5,
        0.965,
        "Hatched / “(est.)” rows = rough GPT-6 estimates · not official CursorBench results",
        ha="center",
        va="top",
        fontsize=9,
        color="#9CA3AF",
        style="italic",
    )

    for i, m in enumerate(ranked):
        suffix = " *" if m["estimated"] else ""
        ax.text(
            m["score"] + 0.5,
            i,
            f"{m['score']:.1f}%{suffix}",
            va="center",
            ha="left",
            fontsize=7.8,
            color="#86EFAC" if m["estimated"] else "#D1D5DB",
            fontweight="bold" if m["estimated"] else "normal",
            fontstyle="italic" if m["estimated"] else "normal",
        )

    family_handles = [
        mpatches.Patch(facecolor=c, edgecolor="#0B1220", label=s)
        for s, c in [
            ("Opus 5.5", SERIES_COLORS["Opus 5.5"]),
            ("Fable 5.1", SERIES_COLORS["Fable 5.1"]),
            ("Grok 4.7", SERIES_COLORS["Grok 4.7"]),
            ("Muse Spark 1.3", SERIES_COLORS["Muse Spark 1.3"]),
            ("GPT-6 est.", SERIES_COLORS["GPT-6 Astra"]),
        ]
    ]
    leg = ax.legend(
        handles=family_handles,
        loc="lower right",
        frameon=True,
        fontsize=8,
        title="Family",
        title_fontsize=9,
    )
    leg.get_frame().set_facecolor("#1A2332")
    leg.get_frame().set_edgecolor("#374151")
    for t in leg.get_texts():
        t.set_color("#E5E7EB")
    leg.get_title().set_color("#F9FAFB")

    fig.text(
        0.02,
        0.01,
        "* Cursor has not published GPT-6 CursorBench scores. Estimates from FC 1.1 + TB 4.0 relative positioning.",
        fontsize=7.5,
        color="#6B7280",
        ha="left",
    )

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    path = OUT / "cursorbench-4.0-top-bar.png"
    fig.savefig(path, dpi=200, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)
    return path


def make_html(models, scatter_path, bar_path, throughput):
    with open(scatter_path, "rb") as f:
        scatter_b64 = base64.b64encode(f.read()).decode("ascii")
    with open(bar_path, "rb") as f:
        bar_b64 = base64.b64encode(f.read()).decode("ascii")

    speed_rows = []
    for r in throughput["rows"]:
        val = "—" if r["tokens_per_sec"] is None else str(r["tokens_per_sec"])
        speed_rows.append(
            f'<tr><td>{r["family"]}</td><td>{val}</td><td class="muted">{r["note"]}</td></tr>'
        )

    table_rows = []
    for m in sorted(models, key=lambda x: -x["score"]):
        cls = ' class="est"' if m["estimated"] else ""
        name = m["model"] + (" *" if m["estimated"] else "")
        src = "Estimated" if m["estimated"] else "Official"
        table_rows.append(
            f'<tr{cls}><td>{name}</td><td>{m["score"]:.1f}%</td>'
            f'<td>${m["cost"]:.2f}</td><td>{m["series"]}</td><td>{src}</td></tr>'
        )

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>CursorBench 4.0 — Score vs Cost Report</title>
<style>
body{{margin:0;background:#0B1220;color:#E5E7EB;font-family:Inter,Segoe UI,system-ui,sans-serif;padding:32px;max-width:1100px}}
h1{{margin:0 0 8px;font-size:1.75rem}} h2{{margin:0 0 12px;font-size:1.15rem;color:#E5E7EB}}
.sub{{color:#9CA3AF;margin:0 0 20px}}
.note{{background:#14532D33;border:1px solid #22C55E66;border-radius:10px;padding:12px 16px;margin:0 0 24px}}
.swatches{{display:flex;flex-wrap:wrap;gap:12px;margin:0 0 24px;font-size:.85rem;color:#9CA3AF}}
.dot{{width:10px;height:10px;border-radius:50%;display:inline-block;margin-right:6px}}
.card{{background:#111827;border:1px solid #1F2A44;border-radius:14px;padding:16px;margin:0 0 24px}}
img{{width:100%;height:auto;border-radius:8px}}
table{{width:100%;border-collapse:collapse;font-size:.9rem}}
th,td{{padding:8px 10px;border-bottom:1px solid #1F2A44;text-align:left}}
th{{color:#9CA3AF;font-weight:600}}
tr.est td{{color:#86EFAC}}
td.muted{{color:#9CA3AF;font-size:.85rem}}
.speed td:nth-child(2){{font-variant-numeric:tabular-nums;font-weight:600}}
footer{{color:#6B7280;font-size:.8rem;margin-top:24px}}
</style></head><body>
<h1>CursorBench 4.0 — Score vs Cost</h1>
<p class="sub">September 2026 · Axes match official cursor.com/cursorbench (linear cost $0–$18 · score 20–60%) · Lines connect Low→…→Max · GPT-6 Astra &amp; Luna estimated</p>
<div class="note"><strong>Important:</strong> Cursor has <em>not</em> published GPT-6 CursorBench scores.
GPT-6 Astra Max (~54% / ~$8.50) and GPT-6 Luna Max (~31% / ~$0.22) are unofficial rough estimates from FrontierCode 1.1 and Terminal-Bench 4.0 relative positioning.</div>
<div class="swatches">
<span><span class="dot" style="background:#F59E0B"></span>Opus 5.5</span>
<span><span class="dot" style="background:#FB923C"></span>Fable 5.1</span>
<span><span class="dot" style="background:#3B82F6"></span>Grok 4.7</span>
<span><span class="dot" style="background:#A855F7"></span>Muse Spark 1.3</span>
<span><span class="dot" style="border:2px dashed #22C55E;background:transparent"></span>GPT-6 estimated</span>
</div>
<div class="card"><img alt="Score vs cost" src="data:image/png;base64,{scatter_b64}"/></div>
<div class="card">
  <h2>Average output speed by model family</h2>
  <table class="speed">
    <thead><tr><th>Model family</th><th>Avg tokens/s</th><th>Source</th></tr></thead>
    <tbody>{''.join(speed_rows)}</tbody>
  </table>
  <p class="sub" style="margin:12px 0 0">Figures are Artificial Analysis output speed (tokens/s after streaming starts), not CursorBench metrics.
  Opus 5.5 had no AA throughput yet as of late Sep 2026. *Luna max figure is third-party AA-derived; AA’s own Luna (max) provider page listed no speed.</p>
</div>
<div class="card"><img alt="Top bar" src="data:image/png;base64,{bar_b64}"/></div>
<div class="card"><table><thead><tr><th>Model</th><th>Score</th><th>Cost / task</th><th>Series</th><th>Source</th></tr></thead>
<tbody>
{''.join(table_rows)}
</tbody></table></div>
<footer>Official scores from cursor.com/cursorbench (CursorBench 4.0, Sep 2026). Chart axes matched to the official visual: linear cost $0–$18, score 20–60%. Estimated rows marked with *. Not affiliated with Cursor.</footer>
</body></html>
"""
    path = OUT / "index.html"
    path.write_text(html)
    return path


def main():
    models = load_points()
    throughput = load_throughput()
    scatter = make_scatter(models)
    bar = make_bar(models)
    html = make_html(models, scatter, bar, throughput)
    print("Created:")
    for p in (scatter, bar, html):
        print(p)


if __name__ == "__main__":
    main()
