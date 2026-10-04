"""Render the production M2 mesh (NACA0012, Re=500) for the pre-defense report.

Usage:  /home/raji/miniconda3/envs/research/bin/python render_mesh.py
Writes  ../figs/mesh_<view>.{pdf,png}   (PDF = vector, PNG = 600 dpi)

Reads the gmsh .msh directly; the z=0 face of each hex is the 2D cell.
Blocks (upper / lower / wake) are the three gmsh volume entities.
"""
import numpy as np, gmsh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
from pathlib import Path

MSH = "/home/raji/Research/Thesis/static_airfoil/meshes/M2_ns160_nr180_b025.msh"
OUT = Path(__file__).resolve().parent.parent / "figs"
plt.rcParams.update({"font.family": "serif", "font.size": 9, "mathtext.fontset": "cm"})

def load():
    gmsh.initialize(); gmsh.option.setNumber("General.Terminal", 0); gmsh.open(MSH)
    tags, xyz, _ = gmsh.model.mesh.getNodes(); xyz = xyz.reshape(-1, 3)
    idx = {t: i for i, t in enumerate(tags)}
    quads, block = [], []
    for b, (_, ent) in enumerate(gmsh.model.getEntities(3)):
        _, _, en = gmsh.model.mesh.getElements(3, ent)
        h = np.array([idx[t] for t in en[0]]).reshape(-1, 8)[:, :4]
        quads.append(h); block += [b] * len(h)
    gmsh.finalize()
    q = np.vstack(quads); P = xyz[:, :2]
    assert np.allclose(xyz[q, 2], 0) and len(q) == 63360
    return P, q, np.array(block)

P, q, block = load()
E = np.sort(np.stack([q, np.roll(q, -1, 1)], -1).reshape(-1, 2), 1)
E = np.unique(E, axis=0)
segs = P[E]
from airfoil_outline import outline  # noqa: E402  (closed polygon of the wall)
wall = outline(P, q)

BLOCK_FILL = ["#dfe8f3", "#f3e6d8", "#e2efdf"]    # pale, prints fine in greyscale

def view(name, xlim, ylim, lw, fill=True, size=(6.5, 6.5), ticks=True, note=None):
    fig, ax = plt.subplots(figsize=size)
    C = P[q].mean(1)
    pad = 0.05 * (xlim[1] - xlim[0])
    m = (C[:, 0] > xlim[0] - pad) & (C[:, 0] < xlim[1] + pad) & (C[:, 1] > ylim[0] - pad) & (C[:, 1] < ylim[1] + pad)
    if fill:
        ax.add_collection(PolyCollection(P[q[m]], facecolors=[BLOCK_FILL[b] for b in block[m]],
                                         edgecolors="none", zorder=0, rasterized=False))
    mid = segs.mean(1)
    me = (mid[:, 0] > xlim[0] - pad) & (mid[:, 0] < xlim[1] + pad) & (mid[:, 1] > ylim[0] - pad) & (mid[:, 1] < ylim[1] + pad)
    ax.add_collection(LineCollection(segs[me], colors="#1a1a1a", linewidths=lw, zorder=1))
    ax.fill(wall[:, 0], wall[:, 1], color="#555555", zorder=2, lw=0)
    ax.set_xlim(xlim); ax.set_ylim(ylim); ax.set_aspect("equal")
    ax.set_xlabel(r"$x/c$"); ax.set_ylabel(r"$y/c$")
    if not ticks: ax.set_xticks([]); ax.set_yticks([])
    if note: ax.text(0.02, 0.98, note, transform=ax.transAxes, va="top", ha="left", fontsize=8,
                     bbox=dict(fc="white", ec="0.6", lw=0.5, pad=2))
    fig.tight_layout()
    for ext, kw in [("pdf", {}), ("png", {"dpi": 600})]:
        fig.savefig(OUT / f"mesh_{name}.{ext}", bbox_inches="tight", **kw)
    plt.close(fig); print("wrote", name, me.sum(), "edges")

view("overview", (-31, 31), (-31, 31), 0.08, note="O-grid, $R = 30c$, 63 360 cells")
view("near", (-0.6, 1.9), (-1.0, 1.0), 0.15, size=(6.5, 5.3))
view("le", (-0.03, 0.09), (-0.05, 0.05), 0.25, size=(6.5, 5.5))
view("te", (0.955, 1.035), (-0.03, 0.03), 0.25, size=(6.5, 5.0))
view("te_base", (0.990, 1.010), (-0.0075, 0.0075), 0.3, size=(6.5, 5.0))

# --- boundary-layer close-up at mid-chord with the Blasius delta_99 reference --
RE = 500
def bl_view(x0=0.35, x1=0.65, ytop=0.26):
    fig, ax = plt.subplots(figsize=(6.5, 5.9))
    mid = segs.mean(1)
    me = (mid[:, 0] > x0 - 0.02) & (mid[:, 0] < x1 + 0.02) & (mid[:, 1] > -0.01) & (mid[:, 1] < ytop + 0.02)
    ax.add_collection(LineCollection(segs[me], colors="#1a1a1a", linewidths=0.3, zorder=1))
    ax.fill(wall[:, 0], wall[:, 1], color="#555555", zorder=2, lw=0)
    up = wall[wall[:, 1] > 0]; up = up[np.argsort(up[:, 0])]
    xs = np.linspace(x0, x1, 200); ys = np.interp(xs, up[:, 0], up[:, 1])
    d99 = 5.0 * xs / np.sqrt(RE * xs)
    ax.plot(xs, ys + d99, color="#c0392b", lw=1.4, zorder=3,
            label=r"Blasius $\delta_{99}(x)=5x/\sqrt{Re_x}$")
    ax.set_xlim(x0, x1); ax.set_ylim(0.03, ytop); ax.set_aspect("equal")
    ax.set_xlabel(r"$x/c$"); ax.set_ylabel(r"$y/c$")
    ax.legend(loc="upper left", fontsize=8, framealpha=0.95)
    ax.text(0.98, 0.97, "36 cells inside $\\delta_{99}$ at $x/c=0.5$\nfirst cell $2.24\\times10^{-3}c$, growth 1.035",
            transform=ax.transAxes, ha="right", va="top", fontsize=8,
            bbox=dict(fc="white", ec="0.6", lw=0.5, pad=2), zorder=4)
    fig.tight_layout()
    for ext, kw in [("pdf", {}), ("png", {"dpi": 600})]:
        fig.savefig(OUT / f"mesh_bl.{ext}", bbox_inches="tight", **kw)
    plt.close(fig); print("wrote bl")
bl_view()
