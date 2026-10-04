"""Closed polygon of the airfoil wall, recovered from the mesh: boundary edges
(used by exactly one cell) that lie within 0.1c of the section."""
import numpy as np
from collections import Counter, defaultdict

def outline(P, q):
    E = np.sort(np.stack([q, np.roll(q, -1, 1)], -1).reshape(-1, 2), 1)
    cnt = Counter(map(tuple, E))
    bnd = [e for e, n in cnt.items() if n == 1]
    near = [e for e in bnd if np.all(np.abs(P[list(e), 1]) < 0.2) and np.all(P[list(e), 0] > -0.2) and np.all(P[list(e), 0] < 1.2)]
    adj = defaultdict(list)
    for a, b in near: adj[a].append(b); adj[b].append(a)
    start = near[0][0]; path = [start]; prev = None; cur = start
    while True:
        nxt = [n for n in adj[cur] if n != prev][0]
        if nxt == start: break
        path.append(nxt); prev, cur = cur, nxt
    return P[path]
