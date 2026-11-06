---
name: crawl-sources
description: Crawl and normalize Microsoft Learn units and GitHub labs into book/original.
---

# Crawl Sources Skill

Use `book/tools/crawl.py` with `python -X utf8`:
1. Initialize manifest and crawl pilot units:
   `python -X utf8 "e:\Microsoft Dynamics\book\tools\crawl.py" --init-manifest --pilot`
2. Crawl a specific volume (`v1`, `v2`, `v3`) or `--all`:
   `python -X utf8 "e:\Microsoft Dynamics\book\tools\crawl.py" --volume v2`
3. Never edit files inside `book/original/` manually; they are locked read-only and verified via `SHA-256`.
