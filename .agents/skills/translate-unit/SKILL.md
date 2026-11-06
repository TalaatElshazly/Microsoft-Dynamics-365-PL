---
name: translate-unit
description: Translate an English unit from book/original to book/translated without summarizing.
---

# Translate Unit Skill

1. Read `book/original/<rel_path>.md` and `book/config/glossary.yaml`.
2. Translate every heading, paragraph, list item, callout, and table cell into clear Arabic in `book/translated/<rel_path>.md` with zero summarization.
3. Keep all fenced code blocks 100% byte-identical, preserve all URLs and image paths, and keep all `strict_terms` in English.
4. For quizzes (`Check your knowledge`) or labs (`01`..`09`), append the delimited `<!-- study-aid-answer-key-start -->...<!-- study-aid-answer-key-end -->` section at the end, then run `validate.py --unit <unit_id>`.
