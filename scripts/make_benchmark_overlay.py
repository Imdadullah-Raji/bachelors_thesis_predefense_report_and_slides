"""Report version of the flat-plate benchmark overlay.

Reuses the data loaders in figs/pitch_plot_digitized/overlay_summary.py (left
unchanged) and redraws at page width with no suptitle.
Run with:  conda run -n plot-digitizer python scripts/make_benchmark_overlay.py
Writes     figs/benchmark_overlay.{pdf,png}
"""
import sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "figs/pitch_plot_digitized"))
import overlay_summary as ov   # noqa: E402

plt.rcParams.update({"font.family": "serif", "font.serif": ["DejaVu Serif"], "mathtext.fontset": "cm",
                     "font.size": 8, "axes.titlesize": 8.5, "pdf.fonttype": 42, "axes.linewidth": 0.6})
fig = plt.figure(figsize=(6.5, 5.4), layout="constrained")
g = fig.add_gridspec(2, 2, height_ratios=(1, 1.05))
axes = {"a_lift_time": fig.add_subplot(g[0, 0]), "b_drag_time": fig.add_subplot(g[0, 1]),
        "c_lift_rescaled_time": fig.add_subplot(g[1, :])}
for k in ov.RATES:
    sim = ov.SUMMARY.loc[np.isclose(ov.SUMMARY.K, k)].iloc[0]
    mark = {"a_lift_time": (1 + sim.s_Cl / k, sim.Cl_max), "b_drag_time": (1 + sim.s_Cd / k, sim.Cd_max),
            "c_lift_rescaled_time": (sim.s_Cl, sim.Cl_max)}
    for p, ax in axes.items():
        c = ov.paper_curve(p, k)
        ax.plot(c.x, c.coefficient, color=ov.COLORS[k], lw=0.9, ls="-." if k == 1.0 else "-", zorder=2)
        ax.scatter(*mark[p], s=18, facecolor=ov.COLORS[k], edgecolor="black", linewidth=0.6, zorder=5)
titles = {"a_lift_time": "(a) Lift", "b_drag_time": "(b) Drag", "c_lift_rescaled_time": "(c) Lift on rescaled time"}
for p, ax in axes.items():
    ax.grid(color="0.9", lw=0.4); ax.set_axisbelow(True)
    ax.set_title(titles[p], loc="left")
    ax.set_ylabel(r"$C_D$" if p == "b_drag_time" else r"$C_L$")
    if p == "c_lift_rescaled_time":
        ax.set_xlim(-0.4, 0.4); ax.set_ylim(0, 20.5); ax.set_yticks(range(0, 17, 4)); ax.set_xlabel(r"$K(tU_\infty/c-1)$")
    else:
        ax.set_xlim(0, 5); ax.set_ylim(0, 8.1 if p == "b_drag_time" else 16.5); ax.set_xlabel(r"$tU_\infty/c$")
handles = [Line2D([], [], color="0.25", lw=1.1, label="Eldredge & Wang (2010)"),
           Line2D([], [], marker="o", color="none", markerfacecolor="0.6", markeredgecolor="black",
                  markersize=4.5, label="Present simulation, peak")]
handles += [Line2D([], [], color=ov.COLORS[k], lw=1.1, ls="-." if k == 1.0 else "-", label=f"$K={k:g}$") for k in ov.RATES]
axes["c_lift_rescaled_time"].legend(handles=handles, ncol=5, loc="upper left", fontsize=7, framealpha=0.95)
for ext, kw in (("pdf", {}), ("png", {"dpi": 400})):
    fig.savefig(ROOT / f"figs/benchmark_overlay.{ext}", **kw)
print("wrote figs/benchmark_overlay.pdf")
