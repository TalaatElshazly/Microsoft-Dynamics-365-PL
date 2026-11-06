# Microsoft Power Platform & Dynamics 365 Developer Arabic Book (`AB-400` / `PL-400`)

This workspace (`e:\Microsoft Dynamics`) contains the automated pipeline and multi-volume Arabic technical reference book for **Microsoft Power Platform & Dynamics 365 Developer (Course AB-400T00 / Exam AB-400)**, tailored for an experienced `.NET / C#` engineer.

## 1. Environment & Tooling Invariants
- **Python 3.12 Standard Library Only**: Do not import third-party packages (`yaml`, `bs4`, `markdown`, `requests`, `httpx`, `pygments` are NOT installed).
- **UTF-8 Execution**: Always run scripts using `python -X utf8 book/tools/<script>.py`.
- **JSON-Compatible YAML Configs**: `book/config/sources.yaml` and `book/config/glossary.yaml` are valid JSON (which is valid YAML 1.2) so Python's built-in `json` module parses them without `PyYAML`.
- **PDF Engine**: Headless Microsoft Edge (`C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`) converts compiled HTML volumes into print-ready A4 PDFs.

## 2. Non-Negotiable Translation Rules
1. **Zero Summarization / Zero Omission**: Translate every paragraph, list item, table cell, callout, and exercise step completely and faithfully into clear, professional Arabic. Never summarize or skip content.
2. **Keep Technical Terms in English**: Keep all terms in `book/config/glossary.yaml` (`strict_terms` and architectural uses of `contextual_platform_terms`), SDK classes, methods, CLI commands, OData operators (`$select`, `$filter`, `$expand`, `$top`, `$batch`, `$metadata`), and exact UI labels in English.
3. **Code Blocks 100% Byte-Identical**: Every fenced code block (` ```csharp `, ` ```javascript `, ` ```typescript `, ` ```json `, ` ```powershell `, ` ```xml `, ` ```sql `, ` ```http `, ` ```bash `, etc.) must remain 100% identical to `book/original/`.
4. **Hyperlinks & Local Images Preserved**: Keep every `[text](url)` hyperlink target identical and keep every `![alt](../../../../assets/...)` image path identical (translating the descriptive `alt` text into Arabic).
5. **Quizzes (`Check your knowledge`)**: Keep the normalized `   - [ ] <Option>` structure and append the delimited `<!-- study-aid-answer-key-start -->...<!-- study-aid-answer-key-end -->` block at the bottom of every quiz unit with the correct answers and technical explanations derived from the module.
6. **GitHub Labs (`v2/s12-labs/`)**: After translating all steps of a hands-on lab (`01`..`09`), append a **Code Walkthrough Appendix (`## ملحق شرح الكود المرجعي للمعمل`)** explaining the official reference implementation in `book/labs-code/Build/LabReference/Lab0X/` inside `<!-- study-aid-answer-key-start -->...<!-- study-aid-answer-key-end -->` delimiters so structural comparisons against the original lab remain 100% aligned.

## 3. CLI Runbook
- **Initialize Manifest & Crawl Pilot**:
  `python -X utf8 "e:\Microsoft Dynamics\book\tools\crawl.py" --init-manifest --pilot`
- **Crawl a Volume or All**:
  `python -X utf8 "e:\Microsoft Dynamics\book\tools\crawl.py" --volume v2`
- **Validate Pilot / Unit / Volume**:
  `python -X utf8 "e:\Microsoft Dynamics\book\tools\validate.py" --pilot`
  `python -X utf8 "e:\Microsoft Dynamics\book\tools\validate.py" --unit <unit_id>`
  `python -X utf8 "e:\Microsoft Dynamics\book\tools\validate.py" --volume v2`
- **Build HTML & PDF (Pilot / Volume / All)**:
  `python -X utf8 "e:\Microsoft Dynamics\book\tools\build.py" --pilot`
  `python -X utf8 "e:\Microsoft Dynamics\book\tools\build.py" --volume v2`
  `python -X utf8 "e:\Microsoft Dynamics\book\tools\build.py" --all`
