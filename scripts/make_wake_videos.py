"""Wake animations for the literature-review slide (Kurtulus modes 2 and 3).

Raw OpenFOAM snapshots from the Re = 500 stationary cases, in the report's
vorticity style (pod_figures.panel: BRIGHT colour map, +-4.57 limit, isolines,
negative dashed), rotated so the freestream is horizontal.  One MP4 + poster
PNG per case:

    conda run -n flowkit python scripts/make_wake_videos.py
    conda run -n flowkit python scripts/make_wake_videos.py --preview

Writes figs/wake_video/<case>.{mp4,png}.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from fluidfoam import readmesh, readvector

POD = Path("/home/raji/ddse/pod_recon")
sys.path.insert(0, str(POD))
from flowkit.dataprocessing import _rotate, _rotate_vector        # noqa: E402
from pod_superposition import airfoil_contour, masked_triangulation, curl, continuous_vorticity  # noqa: E402
from pod_figures import panel                                     # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT.parents[1] / "static_airfoil"
OUT = ROOT / "figs" / "wake_video"
XLIM, YLIM = (-0.8, 9.0), (-2.2, 1.6)
CROP = (-1.2, 9.4, -2.6, 2.0)


def times(case):
    t = [d for d in os.listdir(case) if d[0].isdigit() and (case / d / "U").exists()]
    return sorted(t, key=float)


def render(case, aoa, frames, fps, limit, preview):
    x, y, _ = readmesh(str(case), verbose=False)
    xr, yr = _rotate(x, y, aoa, (0, 0), True)
    keep = (xr >= CROP[0]) & (xr <= CROP[1]) & (yr >= CROP[2]) & (yr <= CROP[3])
    contour = airfoil_contour(str(case), {"frame_origin": [0, 0], "frame_angle": aoa})
    triang = masked_triangulation(xr[keep], yr[keep], contour)
    names = times(case)[-frames:]

    plt.rcParams.update({"font.family": "STIXGeneral", "mathtext.fontset": "stix"})
    w = 12.0
    h = w * (YLIM[1] - YLIM[0]) / (XLIM[1] - XLIM[0])
    fig = plt.figure(figsize=(w, h), dpi=160, facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])

    def draw(name):
        ax.clear()
        U = readvector(str(case), name, "U", verbose=False)
        u, v = _rotate_vector(U[0], U[1], aoa, True)
        omega = continuous_vorticity(triang, curl(triang, np.column_stack([u[keep], v[keep]])))
        panel(ax, triang, contour, omega, limit, 36, 8)
        ax.set(xlim=XLIM, ylim=YLIM, aspect="equal", xticks=[], yticks=[])
        for s in ax.spines.values():
            s.set_color("#3a4350")
            s.set_linewidth(1.2)

    OUT.mkdir(parents=True, exist_ok=True)
    stem = OUT / case.name
    draw(names[0])
    fig.savefig(f"{stem}.png", dpi=160, facecolor="white")
    if preview:
        plt.close(fig)
        return
    fig.canvas.draw()
    W, H = fig.canvas.get_width_height()
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
                           "-s", f"{W}x{H}", "-r", str(fps), "-i", "pipe:0",
                           "-vf", "pad=ceil(iw/2)*2:ceil(ih/2)*2", "-c:v", "libx264",
                           "-crf", "20", "-preset", "slow", "-pix_fmt", "yuv420p",
                           "-movflags", "+faststart", f"{stem}.mp4"], stdin=subprocess.PIPE)
    for k, name in enumerate(names):
        draw(name)
        fig.canvas.draw()
        ff.stdin.write(fig.canvas.buffer_rgba())
        if k % 32 == 0:
            print(f"{case.name}: frame {k}/{len(names)} (t = {name})", flush=True)
    ff.stdin.close()
    if ff.wait():
        raise SystemExit("ffmpeg failed")
    plt.close(fig)
    print(f"{stem}.mp4  t = {names[0]} .. {names[-1]}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cases", nargs="+", default=["re500_aoa14:14", "re500_aoa26:26"])
    p.add_argument("--frames", type=int, default=192, help="snapshots (32 per shedding period)")
    p.add_argument("--fps", type=int, default=16)
    p.add_argument("--limit", type=float, default=4.57, help="report's shared colour limit")
    p.add_argument("--preview", action="store_true")
    a = p.parse_args()
    for spec in a.cases:
        name, aoa = spec.split(":")
        render(CASES / name, float(aoa), a.frames, a.fps, a.limit, a.preview)


if __name__ == "__main__":
    main()
