---
name: validate-unit
description: Run 11-point structural, link, code, and glossary validation on translated units.
---

# Validate Unit Skill

Run `book/tools/validate.py` with `python -X utf8`:
- Pilot validation: `python -X utf8 "e:\Microsoft Dynamics\book\tools\validate.py" --pilot`
- Single unit validation: `python -X utf8 "e:\Microsoft Dynamics\book\tools\validate.py" --unit <unit_id>`
- Volume validation: `python -X utf8 "e:\Microsoft Dynamics\book\tools\validate.py" --volume v2`

Fix every reported failure in `book/translated/<rel_path>.md` and re-run until `0 errors` are reported.
