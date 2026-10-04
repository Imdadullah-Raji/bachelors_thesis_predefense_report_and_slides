"""Generate ghostwritten/reader/*.tex from ghostwritten/author/*.tex.

Removes every \\gap{...} note, deletes "% BEGIN AUTHOR-ONLY ... % END AUTHOR-ONLY"
blocks, and uncomments "% BEGIN READER-ONLY ... % END READER-ONLY" blocks.
Re-run after editing the author copy; it overwrites the reader copy.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1] / "ghostwritten"
SRC, DST = ROOT / "author", ROOT / "reader"

def strip_gaps(s):
    out, i = [], 0
    while (j := s.find("\\gap{", i)) != -1:
        out.append(s[i:j]); k, depth = j + 5, 1
        while depth:
            depth += {"{": 1, "}": -1}.get(s[k], 0) if s[k - 1] != "\\" else 0
            k += 1
        if k < len(s) and s[k] == "\n":
            k += 1
        i = k
    out.append(s[i:])
    return "".join(out)

def blocks(s):
    s = re.sub(r"% BEGIN AUTHOR-ONLY\n.*?% END AUTHOR-ONLY\n?", "", s, flags=re.S)
    s = re.sub(r"% BEGIN READER-ONLY\n(.*?)% END READER-ONLY\n?",
               lambda m: re.sub(r"^% ?", "", m.group(1), flags=re.M), s, flags=re.S)
    return s

DST.mkdir(exist_ok=True)
for f in sorted(SRC.glob("*.tex")):
    t = strip_gaps(blocks(f.read_text()))
    assert "\\gap" not in t and "AUTHOR-ONLY" not in t, f
    (DST / f.name).write_text(t)
    print("wrote", DST / f.name)
