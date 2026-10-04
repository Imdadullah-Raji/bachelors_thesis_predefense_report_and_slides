"""POD superposition video for the objective slide, in the report's figure style.

Same colour map (BRIGHT), linear colour limit and isoline rule as the report's
vorticity figure (pod_figures.py / pod_regimes.py), on a white canvas with no
title text, so it sits inside a slide.  The reconstruction on the left equals
the mean plus the mode contributions on the right; each coefficient trace has a
moving marker.

    conda run -n flowkit python scripts/make_pod_video.py            # full video
    conda run -n flowkit python scripts/make_pod_video.py --preview  # poster only

Writes figs/pod_video/pod_superposition.{mp4,png}.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np
from matplotlib.patches import Polygon

POD = Path("/home/raji/ddse/pod_recon")
sys.path.insert(0, str(POD))
from flowkit.pod import PODResult                                     # noqa: E402
from pod_superposition import (airfoil_contour, masked_triangulation, curl,  # noqa: E402
                               continuous_vorticity, fit_periodic_coefficients,
                               harmonic_basis)
from pod_figures import BRIGHT                                        # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "figs" / "pod_video"
INK = "#17212b"


def grid_fields(triang, fields, xlim, ylim, nx):
    ny = round(nx * (ylim[1] - ylim[0]) / (xlim[1] - xlim[0]))
    gx = np.linspace(*xlim, nx)
    gy = np.linspace(*ylim, ny)
    xx, yy = np.meshgrid(gx, gy)
    # Interpolation is linear, so gridded modes still superpose exactly.
    out = [mtri.LinearTriInterpolator(triang, continuous_vorticity(triang, f))(xx, yy) for f in fields]
    return gx, gy, np.ma.stack(out)


def draw(ax, gx, gy, field, contour, limit, n_fill=36, n_line=8):
    """Report rule: filled levels over +-limit, 4 isolines per sign (negative dashed)."""
    for c in ax.collections[:]:
        c.remove()
    ax.contourf(gx, gy, field, levels=np.linspace(-limit, limit, n_fill), cmap=BRIGHT, extend="both")
    frac = np.linspace(1.0, 0.0, n_line // 2 + 1)[:-1]
    ax.contour(gx, gy, field, levels=np.sort(np.concatenate([-frac, frac])) * limit,
               colors="#0d0d0d", linewidths=.5, alpha=.6)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, default=POD / "data/pod_re500_aoa28_20.nc")
    p.add_argument("--modes", type=int, default=4)
    p.add_argument("--cycles", type=int, default=2)
    p.add_argument("--seconds-per-cycle", type=float, default=10)
    p.add_argument("--fps", type=int, default=30)
    p.add_argument("--limit", type=float, default=4.57, help="report's shared colour limit")
    p.add_argument("--preview", action="store_true")
    a = p.parse_args()

    ds = PODResult.load(str(a.input))
    n = a.modes
    contour = airfoil_contour(ds.meta["source_case"], ds.meta)
    triang = masked_triangulation(ds.x, ds.y, contour)
    mean = curl(triang, np.column_stack([ds.mean_u, ds.mean_v]))
    modes = [curl(triang, m) for m in ds.modes[:n]]
    period, weights, err = fit_periodic_coefficients(ds.times, ds.coefficients[:, :n])
    frames = round(a.cycles * a.seconds_per_cycle * a.fps)
    t0 = ds.times[0]
    times = t0 + np.arange(frames) * a.cycles * period / frames      # endpoint excluded: loops cleanly
    coef = harmonic_basis(times, period, t0) @ weights
    curve_t = np.linspace(t0, t0 + a.cycles * period, 1200)
    curve = harmonic_basis(curve_t, period, t0) @ weights
    cum = ds.cumulative_energy() if callable(ds.cumulative_energy) else ds.cumulative_energy
    energy = float(np.asarray(cum)[n - 1])
    print(f"period {period:.4f}, fit rms {np.round(err, 4)}, frames {frames}, energy {energy:.4f}")

    xlim, ylim = (-1.0, 8.8), (-2.15, 1.0)
    gx, gy, big = grid_fields(triang, [mean, *modes], xlim, ylim, 900)
    sx, sy, small = grid_fields(triang, [mean, *modes], xlim, ylim, 450)
    wake = gx > 1.2
    for i in range(n):
        amp = np.nanpercentile(np.abs(coef[:, i:i+1, None] * small[1+i][None, :, sx > 1.2].filled(np.nan)), 99)
        print(f"mode {i+1}: wake p99 |a w| = {amp:.2f}")

    plt.rcParams.update({"font.family": "STIXGeneral", "mathtext.fontset": "stix",
                         "text.color": INK, "axes.edgecolor": "#3a4350",
                         "xtick.color": INK, "ytick.color": INK})
    W, H = 16, 9
    fig = plt.figure(figsize=(W, H), dpi=120, facecolor="white")

    def axes_in(x, y, w):                       # inches -> figure fraction, field aspect kept
        h = w * (ylim[1] - ylim[0]) / (xlim[1] - xlim[0])
        return fig.add_axes([x / W, y / H, w / W, h / H]), h

    def dress(ax, title, size):
        ax.add_patch(Polygon(contour, closed=True, facecolor="#d9d9d9", edgecolor="#101010",
                             linewidth=.8, zorder=6))
        ax.set(xlim=xlim, ylim=ylim, aspect="equal", xticks=[], yticks=[])
        ax.set_title(title, fontsize=size, pad=8)

    # left: reconstruction
    rec_ax, rh = axes_in(0.25, 3.3, 7.6)
    dress(rec_ax, rf"Reconstruction, {n} modes", 30)
    fig.text(8.25 / W, (3.3 + rh / 2) / H, "=", fontsize=48, ha="center", va="center")

    # right: mean on top, 2 x 2 modes, each with its coefficient trace
    colw, x0, x1 = 2.95, 8.75, 12.05
    mean_ax, mh = axes_in((x0 + x1 + colw) / 2 - colw, 7.45, colw)
    dress(mean_ax, r"Mean $\overline{\omega}$", 24)
    draw(mean_ax, sx, sy, small[0], contour, a.limit)
    mode_axes, dots, cursors = [], [], []
    rows_y = [4.35, 1.05]
    for i in range(n):
        x = x0 if i % 2 == 0 else x1
        y = rows_y[i // 2]
        ax, h = axes_in(x, y + 1.2, colw)
        dress(ax, rf"$a_{i+1}(t)\,\omega_{i+1}$", 24)
        mode_axes.append(ax)
        tr = fig.add_axes([x / W, (y + .05) / H, colw / W, .85 / H])
        tr.plot(np.linspace(0, a.cycles, len(curve)), curve[:, i], color=INK, lw=1.6)
        tr.axhline(0, color="#8a93a0", lw=.8)
        bound = 1.2 * np.abs(curve[:, i]).max()
        tr.set(xlim=(0, a.cycles), ylim=(-bound, bound), yticks=[])
        tr.set_xticks(range(a.cycles + 1))
        tr.tick_params(labelsize=18, length=3)
        tr.spines[["top", "right", "left"]].set_visible(False)
        cursors.append(tr.axvline(0, color=INK, lw=1, alpha=.6))
        dots.append(tr.plot(0, coef[0, i], "o", color="#cc1405", ms=8, zorder=5)[0])
        if i % 2 == 1:
            fig.text((x1 - .2) / W, (y + 1.2 + h / 2) / H, "+", fontsize=34, ha="center", va="center")
    fig.text((x0 + colw / 2) / W, 7.25 / H, "+", fontsize=34, ha="center", va="center")
    fig.text((x1 - .2) / W, 0.35 / H, r"$t\,/\,T$", fontsize=22, ha="center", va="center")
    fig.text(4.05 / W, 2.45 / H, rf"$\omega(x,y,t)\approx\overline{{\omega}}(x,y)+\sum_{{i=1}}^{{{n}}}a_i(t)\,\omega_i(x,y)$",
             fontsize=30, ha="center", va="center")
    fig.text(4.05 / W, 1.5 / H, rf"$Re=500$, $\alpha=28^\circ$: {n} modes hold {100 * energy:.0f}% of the fluctuation energy",
             fontsize=22, ha="center", va="center")

    cax = fig.add_axes([15.02 / W, 3.3 / H, .16 / W, 4.2 / H])
    sm = plt.cm.ScalarMappable(cmap=BRIGHT, norm=plt.Normalize(-a.limit, a.limit))
    bar = fig.colorbar(sm, cax=cax, extend="both")
    bar.set_ticks([-a.limit, 0, a.limit])
    bar.ax.set_yticklabels([f"$-{a.limit:g}$", "$0$", f"${a.limit:g}$"], fontsize=17)
    bar.ax.set_title(r"$\omega_z$", fontsize=24, pad=12)

    def update(k):
        c = coef[k]
        draw(rec_ax, gx, gy, big[0] + np.einsum("i,ijk->jk", c, big[1:]), contour, a.limit)
        for i in range(n):
            draw(mode_axes[i], sx, sy, c[i] * small[1 + i], contour, a.limit)
            s = k / frames * a.cycles
            dots[i].set_data([s], [c[i]])
            cursors[i].set_xdata([s, s])

    OUT.mkdir(parents=True, exist_ok=True)
    update(0)
    fig.savefig(OUT / "pod_superposition.png", dpi=120, facecolor="white")
    if a.preview:
        return
    w, h = fig.canvas.get_width_height()
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
                           "-s", f"{w}x{h}", "-r", str(a.fps), "-i", "pipe:0", "-c:v", "libx264",
                           "-crf", "20", "-preset", "slow", "-pix_fmt", "yuv420p",
                           "-movflags", "+faststart", str(OUT / "pod_superposition.mp4")],
                          stdin=subprocess.PIPE)
    for k in range(frames):
        update(k)
        fig.canvas.draw()
        ff.stdin.write(fig.canvas.buffer_rgba())
        if k % 60 == 0:
            print(f"frame {k}/{frames}", flush=True)
    ff.stdin.close()
    if ff.wait():
        raise SystemExit("ffmpeg failed")
    print(OUT / "pod_superposition.mp4")


if __name__ == "__main__":
    main()
