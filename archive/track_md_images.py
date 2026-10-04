#!/usr/bin/env python3
"""Keep images that markdown files display in git, so they render on GitHub.

Scans every .md file git tracks for image embeds and links to image files,
resolves each path relative to its .md file, and rewrites the managed block
at the end of .gitignore to un-ignore exactly those files. Broken paths are
reported, not fixed. Run after adding an image to a markdown file.
"""
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGE = re.compile(r'\.(png|jpe?g|gif|svg|webp)$', re.I)
REF = re.compile(r'!?\[[^\]]*\]\(([^)\s]+)\)|<img[^>]*\bsrc="([^"]+)"')
BEGIN = '# BEGIN markdown images (managed by archive/track_md_images.py)'
END = '# END markdown images'

mds = subprocess.run(['git', 'ls-files', '*.md'], cwd=ROOT, capture_output=True,
                     text=True, check=True).stdout.split()
keep, broken = set(), []
for md in mds:
    for m in REF.finditer((ROOT / md).read_text()):
        ref = m.group(1) or m.group(2)
        if '://' in ref or not IMAGE.search(ref):
            continue
        target = (ROOT / md).parent / ref
        if target.is_file():
            keep.add(target.resolve().relative_to(ROOT).as_posix())
        else:
            broken.append(f'{md}: {ref}')

gi = ROOT / '.gitignore'
text = gi.read_text()
if BEGIN in text:
    text = text[:text.index(BEGIN)].rstrip('\n') + '\n'
block = [BEGIN] + [f'!/{p}' for p in sorted(keep)] + [END]
gi.write_text(text + '\n' + '\n'.join(block) + '\n')

print(f'{len(keep)} markdown images tracked in git')
for b in broken:
    print('BROKEN', b)
