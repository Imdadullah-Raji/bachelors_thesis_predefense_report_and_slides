# Archive: code vs. assets

This workspace is split in two:

| Kind | What | Where |
|------|------|-------|
| **Code** | `.md`, `.py`, `.sh`, `.tex`, `.bib`, `.yaml` (the instructions that produce everything else) | git → `github.com/Imdadullah-Raji/bachelors_thesis_predefense_report_and_slides` |
| **Assets** | everything else: videos, images, PDFs, `.pptx`, data (`.csv/.json/.npz`), reference papers, and all of `build/` and `writeup/build/` | rclone → `gdrive-altair:bsc_predefense_assets` |

The single source of truth is `.gitignore`: **an asset is any file git ignores**.
`archive/never_upload.txt` (grep -E patterns) lists the junk that goes nowhere (`__pycache__`, LibreOffice lock files).
Assets keep their relative paths on Drive, so they drop back into place on restore.

## Everyday use

```bash
archive/list_split.sh            # preview what goes where
git add -A && git commit -m ... && git push
archive/push_assets.sh           # upload new/changed assets (never deletes remote files)
archive/push_assets.sh --dry-run
```

## Restoring on a new machine

```bash
git clone git@github.com:Imdadullah-Raji/bachelors_thesis_predefense_report_and_slides.git predefense
cd predefense
archive/pull_assets.sh
./build.sh                       # needs pdflatex; figure scripts need environment.yaml
```

## Images shown in markdown

Images that a tracked `.md` file displays (`![](...)` or `<img src>`) are the one exception: they live in git, at full resolution, so they render on GitHub.
After adding an image to a markdown file, run:

```bash
archive/track_md_images.py       # rewrites the managed block at the end of .gitignore; reports broken paths
```

Image paths in markdown are relative to the `.md` file (e.g. `../figs/x.png` from `markdowns/`).

## Changing the split

To start tracking a new code type, add a `!*.ext` line to `.gitignore`.
Once a file type is un-ignored, `push_assets.sh` stops uploading it.
