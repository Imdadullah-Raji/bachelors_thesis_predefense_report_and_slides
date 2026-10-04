"""Two-panel mesh figure for the LaTeX report.
(a) full O-grid domain; (b) near field with LE and TE insets.

Usage:  /home/raji/miniconda3/envs/research/bin/python make_mesh_figure.py
Writes  ../figs/mesh_figure.{pdf,png}   sized for a full-width figure* (7.0 in)
"""
import numpy as np, gmsh, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection, PolyCollection
from mpl_toolkits.axes_grid1.inset_locator import mark_inset
from pathlib import Path
from airfoil_outline import outline

MSH = "/home/raji/Research/Thesis/static_airfoil/meshes/M2_ns160_nr180_b025.msh"
OUT = Path(__file__).resolve().parent.parent / "figs"
plt.rcParams.update({"font.family": "serif", "font.serif": ["DejaVu Serif"],
                     "mathtext.fontset": "cm", "font.size": 8, "pdf.fonttype": 42,
                     "axes.linewidth": 0.6, "xtick.major.width": 0.5, "ytick.major.width": 0.5,
                     "xtick.major.size": 2.5, "ytick.major.size": 2.5})
BLOCK_FILL = ["#dfe8f3", "#f3e6d8", "#e2efdf"]   # upper / lower / wake

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
    q = np.vstack(quads); assert np.allclose(xyz[q, 2], 0) and len(q) == 63360
    return xyz[:, :2], q, np.array(block)

P, q, block = load()
E = np.unique(np.sort(np.stack([q, np.roll(q, -1, 1)], -1).reshape(-1, 2), 1), axis=0)
segs, segmid = P[E], P[E].mean(1)
cent = P[q].mean(1)
wall = outline(P, q)

def draw(ax, xlim, ylim, lw, ticks=True):
    pad = 0.1 * (xlim[1] - xlim[0])
    inb = lambda c: (c[:, 0] > xlim[0] - pad) & (c[:, 0] < xlim[1] + pad) & \
                    (c[:, 1] > ylim[0] - pad) & (c[:, 1] < ylim[1] + pad)
    m = inb(cent)
    ax.add_collection(PolyCollection(P[q[m]], facecolors=[BLOCK_FILL[b] for b in block[m]],
                                     edgecolors="none", zorder=0))
    ax.add_collection(LineCollection(segs[inb(segmid)], colors="#1a1a1a", linewidths=lw, zorder=1))
    ax.fill(wall[:, 0], wall[:, 1], color="#555555", lw=0, zorder=2)
    ax.set_xlim(xlim); ax.set_ylim(ylim); ax.set_aspect("equal")
    if not ticks:
        ax.set_xticks([]); ax.set_yticks([])

# explicit layout in inches: both panels share height H; (b) keeps its data aspect
W, L, GAP, R, B, T = 7.0, 0.42, 0.52, 0.06, 0.40, 0.22
AR_B = (1.55 + 0.45) / (0.62 * 2)                  # width/height of panel (b)
H = (W - L - GAP - R) / (1 + AR_B)
FH = B + H + T
fig = plt.figure(figsize=(W, FH))
axa = fig.add_axes([L / W, B / FH, H / W, H / FH])
axb = fig.add_axes([(L + H + GAP) / W, B / FH, AR_B * H / W, H / FH])

# (a) full domain
draw(axa, (-31, 31), (-31, 31), 0.06)
axa.set_xticks([-30, -15, 0, 15, 30]); axa.set_yticks([-30, -15, 0, 15, 30])
axa.set_xlabel(r"$x/c$"); axa.set_ylabel(r"$y/c$", labelpad=1)
axa.set_title("(a)", loc="left", fontsize=9, pad=3)

# (b) near field + insets
draw(axb, (-0.45, 1.55), (-0.62, 0.62), 0.12)
axb.set_xlabel(r"$x/c$"); axb.set_ylabel(r"$y/c$", labelpad=1)
axb.set_title("(b)", loc="left", fontsize=9, pad=3)

def inset(bounds, xlim, ylim, lw, loc1, loc2, label):
    ax = axb.inset_axes(bounds)
    draw(ax, xlim, ylim, lw, ticks=False)
    for s in ax.spines.values(): s.set_linewidth(0.8); s.set_edgecolor("#b03a2e")
    ax.text(0.04, 0.93, label, transform=ax.transAxes, va="top", fontsize=7,
            bbox=dict(fc="white", ec="none", pad=1.0, alpha=0.9), zorder=5)
    mark_inset(axb, ax, loc1=loc1, loc2=loc2, fc="none", ec="#b03a2e", lw=0.6, zorder=6)
    return ax

# LE inset top-left, TE inset bottom-right
inset([0.015, 0.575, 0.40, 0.41], (-0.02, 0.06), (-0.041, 0.041), 0.25, 3, 4, "LE")
inset([0.585, 0.015, 0.40, 0.41], (0.984, 1.016), (-0.0164, 0.0164), 0.25, 1, 2, "TE")

for ext, kw in [("pdf", {}), ("png", {"dpi": 600})]:
    fig.savefig(OUT / f"mesh_figure.{ext}", **kw)
print("wrote", OUT / "mesh_figure.pdf")
