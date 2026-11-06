---
name: build-book
description: Compile validated Arabic Markdown units into offline RTL HTML and PDF volumes.
---

# Build Book Skill

Run `book/tools/build.py` with `python -X utf8`:
- Build Pilot HTML & PDF (`book/pilot-preview.html` and `book/pilot-preview.pdf`):
  `python -X utf8 "e:\Microsoft Dynamics\book\tools\build.py" --pilot`
- Build a Volume (`v1`, `v2`, `v3`) or `--all`:
  `python -X utf8 "e:\Microsoft Dynamics\book\tools\build.py" --volume v2`
  `python -X utf8 "e:\Microsoft Dynamics\book\tools\build.py" --all`
