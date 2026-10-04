"""Overlay peak results from nabla's plate_summary.csv on digitized Fig. 3.

Run with: conda run -n plot-digitizer python overlay_summary.py
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd


HERE = Path(__file__).resolve().parent
CURVES = pd.read_csv(HERE / "curves.csv")
VECTOR = np.load(HERE / "eldredge_fig3_vector.npz")
SUMMARY = pd.read_csv(HERE / "plate_summary_nabla.csv")
RATES = (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0)
COLORS = {
    0.1: "#3953a4",
    0.2: "#098140",
    0.3: "#ed2024",
    0.4: "#1abdbd",
    0.5: "#a53e97",
    0.6: "#bebf32",
    0.8: "#636466",
    1.0: "#3953a4",
}


def paper_curve(panel: str, rate: float, source: str = "vector") -> pd.DataFrame:
    if source == "raster":
        return CURVES[(CURVES.panel == panel) & np.isclose(CURVES.K, rate)].sort_values("x")
    prefix = {
        "a_lift_time": "a_CL_t",
        "b_drag_time": "b_CD_t",
        "c_lift_rescaled_time": "c_CL_s",
    }[panel]
    return pd.DataFrame(VECTOR[f"{prefix}_K{rate:g}"], columns=["x", "coefficient"]).sort_values("x")


def paper_peak(panel: str, rate: float) -> tuple[float, float]:
    curve = paper_curve(panel, rate)
    row = curve.loc[curve.coefficient.idxmax()]
    return float(row.x), float(row.coefficient)


def comparison() -> pd.DataFrame:
    if set(np.round(SUMMARY.K, 6)) != set(RATES):
        raise ValueError("Summary K values do not match the eight figure curves")
    rows = []
    for rate in RATES:
        sim = SUMMARY.loc[np.isclose(SUMMARY.K, rate)].iloc[0]
        lift_t, lift_peak = paper_peak("a_lift_time", rate)
        lift_s = rate * (lift_t - 1.0)
        drag_t, drag_peak = paper_peak("b_drag_time", rate)
        drag_s = rate * (drag_t - 1.0)
        rows.append(
            {
                "K": rate,
                "Cl_peak_sim": sim.Cl_max,
                "Cl_peak_digitized": lift_peak,
                "Cl_peak_delta_pct": 100 * (sim.Cl_max / lift_peak - 1),
                "s_Cl_peak_sim": sim.s_Cl,
                "s_Cl_peak_digitized": lift_s,
                "s_Cl_peak_delta": sim.s_Cl - lift_s,
                "Cd_peak_sim": sim.Cd_max,
                "Cd_peak_digitized": drag_peak,
                "Cd_peak_delta_pct": 100 * (sim.Cd_max / drag_peak - 1),
                "s_Cd_peak_sim": sim.s_Cd,
                "s_Cd_peak_digitized": drag_s,
                "s_Cd_peak_delta": sim.s_Cd - drag_s,
            }
        )
    return pd.DataFrame(rows)


def plot_overlay(source: str, basename: str) -> None:
    fig = plt.figure(figsize=(12.2, 9.2), layout="constrained")
    grid = fig.add_gridspec(2, 2, height_ratios=(1, 1.05))
    axes = {
        "a_lift_time": fig.add_subplot(grid[0, 0]),
        "b_drag_time": fig.add_subplot(grid[0, 1]),
        "c_lift_rescaled_time": fig.add_subplot(grid[1, :]),
    }
    for rate in RATES:
        sim = SUMMARY.loc[np.isclose(SUMMARY.K, rate)].iloc[0]
        lift_t = 1.0 + sim.s_Cl / rate
        drag_t = 1.0 + sim.s_Cd / rate
        markers = {
            "a_lift_time": (lift_t, sim.Cl_max),
            "b_drag_time": (drag_t, sim.Cd_max),
            "c_lift_rescaled_time": (sim.s_Cl, sim.Cl_max),
        }
        for panel, ax in axes.items():
            paper = paper_curve(panel, rate, source=source)
            ax.plot(
                paper.x,
                paper.coefficient,
                color=COLORS[rate],
                lw=1.35,
                linestyle="-." if rate == 1.0 else "-",
                label=f"K={rate:g}",
                zorder=2,
            )
            mx, my = markers[panel]
            ax.scatter(
                mx,
                my,
                s=45,
                facecolor=COLORS[rate],
                edgecolor="black",
                linewidth=0.85,
                zorder=5,
            )
    for panel, ax in axes.items():
        ax.grid(color="0.88", lw=0.5)
        ax.set_axisbelow(True)
        ax.set_title(
            {
                "a_lift_time": "(a) Lift versus time",
                "b_drag_time": "(b) Drag versus time",
                "c_lift_rescaled_time": "(c) Lift versus rescaled time",
            }[panel]
        )
        ax.set_ylabel(r"$C_D$" if panel == "b_drag_time" else r"$C_L$")
        if panel == "c_lift_rescaled_time":
            ax.set_xlim(-0.4, 0.4)
            ax.set_ylim(0, 16.5)
            ax.set_xlabel(r"$K(tU/c - 1)$")
        else:
            ax.set_xlim(0, 5)
            ax.set_ylim(0, 8.1 if panel == "b_drag_time" else 16.5)
            ax.set_xlabel(r"$tU/c$")
    source_handles = [
        Line2D([], [], color="0.25", lw=1.5, label="Digitized paper curve"),
        Line2D([], [], marker="o", color="none", markerfacecolor="0.6", markeredgecolor="black", markersize=6, label="Simulation peak"),
    ]
    rate_handles = [
        Line2D([], [], color=COLORS[k], lw=1.6, linestyle="-." if k == 1.0 else "-", label=f"K={k:g}")
        for k in RATES
    ]
    axes["c_lift_rescaled_time"].legend(
        handles=source_handles + rate_handles,
        ncol=5,
        loc="upper left",
        fontsize=8,
        frameon=True,
        facecolor="white",
        framealpha=0.9,
    )
    fig.suptitle(
        "Flat-plate pitch-up: simulation peaks over "
        + ("vector-extracted" if source == "vector" else "raster-digitized")
        + " paper curves",
        fontsize=14,
    )
    fig.savefig(HERE / f"{basename}.png", dpi=220)
    if source == "vector":
        fig.savefig(HERE / f"{basename}.pdf")
    plt.close(fig)


def main() -> None:
    result = comparison()
    result.to_csv(HERE / "peak_comparison.csv", index=False, float_format="%.5f")
    plot_overlay("vector", "summary_overlay")
    plot_overlay("raster", "summary_overlay_raster")
    print(result[["K", "Cl_peak_delta_pct", "Cd_peak_delta_pct", "s_Cl_peak_delta", "s_Cd_peak_delta"]].round(3).to_string(index=False))


if __name__ == "__main__":
    main()
