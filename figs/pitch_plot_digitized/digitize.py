"""Extract the eight coloured traces in each panel of pitch_plot_tobedigitized.png.

Run with: conda run -n plot-digitizer python digitize.py
Coordinates below are pixel positions of the labelled plot-axis intersections.
"""

from __future__ import annotations

import csv
from pathlib import Path

import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent / "pitch_plot_tobedigitized.png"
RGB = np.asarray(Image.open(SOURCE).convert("RGB"))

# x(pixel at axis minimum), x(pixel at axis maximum), x-min, x-max,
# y(pixel at zero), y(pixel at top tick), y-max
PANELS = {
    "a_lift_time": (102.5, 568.5, 0.0, 5.0, 425.1, 98.4, 16.0),
    "b_drag_time": (606.4, 1072.4, 0.0, 5.0, 466.2, 93.2, 8.0),
    "c_lift_rescaled_time": (354.3, 816.3, -0.4, 0.4, 880.7, 516.1, 16.0),
}

# Reference colours measured from the un-antialiased centres of the curves.
COLORS = {
    0.1: (57, 83, 164),
    0.2: (9, 129, 64),
    0.3: (237, 32, 36),
    0.4: (26, 188, 189),
    0.5: (165, 62, 151),
    0.6: (190, 191, 50),
    0.8: (99, 100, 102),
    1.0: (57, 83, 164),  # dash-dot; separated spatially from solid K=0.1
}

# Last visible x coordinates; the figure does not show every curve to x-max.
ENDS = {
    "a_lift_time": {0.1: 562, 0.2: 379, 0.3: 317, 0.4: 275, 0.5: 258, 0.6: 267, 0.8: 257, 1.0: 239},
    "b_drag_time": {0.1: 1072, 0.2: 886, 0.3: 826, 0.4: 794, 0.5: 776, 0.6: 764, 0.8: 750, 1.0: 741},
    "c_lift_rescaled_time": {rate: 816 for rate in COLORS},
}


def pixel_mask(color: tuple[int, int, int], panel: str) -> np.ndarray:
    p = PANELS[panel]
    xmin, xmax = int(np.ceil(p[0])), int(np.floor(p[1]))
    ymin, ymax = int(np.ceil(p[5])), int(np.floor(p[4]))
    crop = RGB[ymin : ymax + 1, xmin : xmax + 1].astype(np.int32)
    distance = np.sqrt(np.sum((crop - np.array(color, dtype=np.int32)) ** 2, axis=2))
    mask = np.zeros(RGB.shape[:2], dtype=bool)
    mask[ymin : ymax + 1, xmin : xmax + 1] = distance < 32
    return mask


def columns(mask: np.ndarray, xmin: int, xmax: int) -> tuple[np.ndarray, np.ndarray]:
    xs, ys = [], []
    for x in range(xmin, xmax + 1):
        hits = np.flatnonzero(mask[:, x])
        if len(hits):
            xs.append(x)
            ys.append(float(np.median(hits)))
    return np.array(xs), np.array(ys)


def trace_masks(panel: str) -> dict[float, np.ndarray]:
    masks = {rate: pixel_mask(color, panel) for rate, color in COLORS.items()}
    blue = masks[0.1]
    green = masks[0.2]
    grey = masks[0.8]
    xmin, xmax = int(np.ceil(PANELS[panel][0])), int(np.floor(PANELS[panel][1]))
    green_x, green_y = columns(green, xmin, xmax)
    grey_x, grey_y = columns(grey, xmin, xmax)
    solid = np.zeros_like(blue)
    dashed = np.zeros_like(blue)
    for x in range(xmin, xmax + 1):
        hits = np.flatnonzero(blue[:, x])
        if not len(hits):
            continue
        if len(green_x) and green_x[0] <= x <= green_x[-1]:
            boundary = np.interp(x, green_x, green_y)
            dashed[hits[hits < boundary - 3.0], x] = True
            solid[hits[hits > boundary + 3.0], x] = True
        elif grey_x[0] <= x < green_x[0]:
            boundary = np.interp(x, grey_x, grey_y)
            dashed[hits[hits < boundary - 3.0], x] = True
        elif panel == "c_lift_rescaled_time" and x > green_x[-1]:
            boundary = np.interp(x, [green_x[-1], 811], [green_y[-1], 840.0])
            dashed[hits[hits < boundary - 2.0], x] = True
            solid[hits[hits > boundary + 2.0], x] = True
        elif x > green_x[-1]:
            solid[hits, x] = True
    masks[0.1], masks[1.0] = solid, dashed
    return masks


def convert(panel: str, px: np.ndarray, py: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    x0, x1, u0, u1, y0, y1, v1 = PANELS[panel]
    return u0 + (px - x0) * (u1 - u0) / (x1 - x0), (y0 - py) * v1 / (y0 - y1)


def main() -> None:
    rows = []
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), layout="constrained")
    axes = axes.flat
    for panel_index, panel in enumerate(PANELS):
        p = PANELS[panel]
        xmin, xmax = int(np.ceil(p[0])), int(np.floor(p[1]))
        masks = trace_masks(panel)
        ax = axes[panel_index]
        for rate, color in COLORS.items():
            end = ENDS[panel][rate]
            obs_x, obs_y = columns(masks[rate], xmin, min(xmax, end))
            if panel == "b_drag_time":
                keep = obs_x > 696
                obs_x, obs_y = obs_x[keep], obs_y[keep]
            if len(obs_x) < 5:
                raise RuntimeError(f"Too few pixels for {panel}, K={rate}")
            # The rightmost masks sometimes contain no curve pixels. Do not
            # extend the last observed value as a spurious horizontal tail.
            actual_end = 811 if panel == "c_lift_rescaled_time" else int(obs_x[-1])
            grid_x = np.arange(xmin, actual_end + 1)
            grid_y = np.interp(grid_x, obs_x, obs_y)
            observed = np.isin(grid_x, obs_x)
            if panel != "b_drag_time":
                grid_y[grid_x < obs_x[0]] = p[4]
            else:
                # Early drag is shared by the eight nearly coincident traces.
                # Use the visible grey reference there, then join each colour.
                common_x, common_y = columns(pixel_mask(COLORS[0.8], panel), xmin, 696)
                early = grid_x <= 696
                grid_y[early] = np.interp(grid_x[early], common_x, common_y)
            if panel == "c_lift_rescaled_time":
                # The coloured traces merge at the shared visible endpoint.
                # Their last separate pixels are joined to that point.
                join = grid_x > obs_x[-1]
                grid_y[join] = np.interp(grid_x[join], [obs_x[-1], 811], [obs_y[-1], 840.0])
            # Short-window median rejects isolated antialiasing fragments.
            grid_y = cv2.medianBlur(grid_y.astype(np.float32).reshape(1, -1), 5).ravel()
            plot_x, plot_y = convert(panel, grid_x, grid_y)
            plot_y = np.clip(plot_y, 0, p[6])
            style = "-." if rate == 1.0 else "-"
            ax.plot(plot_x, plot_y, linestyle=style, color=np.array(color) / 255, lw=1.2, label=f"K={rate:g}")
            for px, x, y, seen in zip(grid_x, plot_x, plot_y, observed):
                status = "observed" if seen else "interpolated"
                if panel == "c_lift_rescaled_time" and px > obs_x[-1]:
                    status = "shared_endpoint"
                elif panel == "b_drag_time" and px <= 696:
                    status = "common_baseline"
                elif px < obs_x[0]:
                    status = "common_baseline"
                rows.append((panel, f"{rate:g}", f"{x:.6f}", f"{y:.6f}", status))
            print(f"{panel:22s} K={rate:g}: {len(obs_x):3d} observed columns, {len(grid_x):3d} total, visible x={obs_x[0]}..{obs_x[-1]}")
        ax.set_xlim(p[2], p[3])
        ax.set_ylim(0, p[6])
        ax.set_xlabel("tU/c" if panel != "c_lift_rescaled_time" else "K(tU/c − 1)")
        ax.set_ylabel("C_L" if panel != "b_drag_time" else "C_D")
        ax.set_title(panel.replace("_", " "))
        ax.grid(alpha=0.2)
    axes[3].axis("off")
    axes[3].legend(*axes[0].get_legend_handles_labels(), loc="center", ncol=2, frameon=False)
    fig.savefig(HERE / "redrawn.png", dpi=180)
    plt.close(fig)
    with (HERE / "curves.csv").open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["panel", "K", "x", "coefficient", "source"])
        writer.writerows(rows)


if __name__ == "__main__":
    main()
