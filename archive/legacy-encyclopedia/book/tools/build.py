"""
build.py — Offline RTL/LTR HTML & Headless Edge PDF Compiler for the AB-400 Arabic Reference Book.

Supported Markdown Dialect (Deterministic State-Machine Parser):
1. Fenced Code Blocks:
   - Backtick fences (3 or more: ``` or ````) and tilde fences (3 or more: ~~~).
   - Top-level, list-indented (    ```), and blockquote-nested (    > ```).
   - Preserves exact inner code indentation (via textwrap.dedent) and escapes HTML entities.
2. Inline Code Spans:
   - Single-backtick spans (`code`) protected via TokenRegistry before any table, link, or Bidi processing.
3. Headings:
   - ATX headings (# H1 through ###### H6) with deterministic anchor IDs.
4. Images & Hyperlinks:
   - Standalone block images ![alt](src) emitted directly as top-level <figure class="book-figure"> (never inside <p>).
   - Inline links [label](url) supporting balanced parentheses inside URLs.
   - Relative asset paths resolved against the source unit directory and verified on disk before build.
5. Tables:
   - GFM pipe tables (| col1 | col2 |) with header separator rows (| :--- | :---: |).
   - Inline code extracted prior to pipe splitting so pipes inside `a | b` never break cells.
6. Blockquotes & Alerts:
   - Standard blockquotes (> text) and GitHub Alerts (> [!NOTE], [!TIP], [!IMPORTANT], [!WARNING], [!CAUTION]).
7. Lists & Structured Quizzes:
   - Ordered lists (1. item) with explicit <ol start="N"> support and unordered lists (- item, * item).
   - Dedicated Knowledge Check parser rendering each question and its options inside an isolated <div class="quiz-card">.
8. Study-Aid & Code Walkthrough Containers:
   - Delimited <!-- study-aid-answer-key-start -->...<!-- study-aid-answer-key-end --> sections.
"""

import argparse
import html
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BOOK_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BOOK_DIR.parents[1]
CONFIG_DIR = BOOK_DIR / "config"
ORIG_DIR = BOOK_DIR / "original"
TRANS_DIR = BOOK_DIR / "translated"
MANIFEST_PATH = BOOK_DIR / "manifests" / "manifest.json"

EDGE_PATHS = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
]

ALERT_LABELS = {
    "NOTE": ("ملاحظة", "alert-note"),
    "TIP": ("نصيحة تقنية", "alert-tip"),
    "IMPORTANT": ("هام جداً", "alert-important"),
    "WARNING": ("تحذير", "alert-warning"),
    "CAUTION": ("تنبيه حرج", "alert-caution"),
}

ARABIC_OPTION_LETTERS = ["أ", "ب", "ج", "د", "هـ", "و"]

# Matches HTML tags (including quoted attributes that may contain '>'), @@TOK_...@@ placeholders, and HTML entities
TOKEN_AND_TAG_RE = re.compile(r"(<(?:[^\"'>]|\"[^\"]*\"|'[^']*')+>|@@TOK_[A-Z]+_\d+@@|&[a-zA-Z0-9#]+;)")

# Matches single-line English/OData technical sequences (uses [ \t]+ instead of \s+ so it NEVER crosses newlines,
# and includes trailing version/model numbers like "Dynamics 365", ".NET 4.8", "OAuth 2.0", "Lab 01")
EN_SEQ_RE = re.compile(
    r"(?<![A-Za-z0-9_@])(\$[A-Za-z][A-Za-z0-9_]*|[A-Za-z][A-Za-z0-9_+#./:-]*(?:[ \t]+(?:[A-Za-z][A-Za-z0-9_+#./:-]*|\d+(?:\.\d+)*))*)(?![A-Za-z0-9_@])"
)

# Comprehensive control character check:
# - ASCII C0 control chars \x00-\x08, \x0b, \x0c, \x0e-\x1f (excluding \t, \n, \r)
# - ASCII DEL \x7f
# - Unicode C1 control chars \u0080-\u009f
# - Unicode Private Use Area \ue000-\uf8ff and Replacement Char \ufffd
CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\u0080-\u009f\ue000-\uf8ff\ufffd]")

FENCE_BLOCK_RE = re.compile(
    r"^([ \t]*)(`{3,}|~{3,})([a-zA-Z0-9_+-]*)[ \t]*\n(.*?)\n[ \t]*\2[ \t]*$",
    re.M | re.S,
)
BQ_FENCE_BLOCK_RE = re.compile(
    r"^([ \t]*)>[ \t]*(`{3,}|~{3,})([a-zA-Z0-9_+-]*)[ \t]*\n((?:[ \t]*>[^\n]*\n)+?)[ \t]*>[ \t]*\2[ \t]*$",
    re.M,
)
LINK_RE = re.compile(r"\[([^\]]+)\]\(((?:[^()\s]+|\([^()\s]*\))+)\)")
IMG_RE = re.compile(r"!\[([^\]]*)\]\(((?:[^()\s]+|\([^()\s]*\))+)\)")


def wrap_bidi_en(escaped_html_text: str) -> str:
    """Wrap English/OData technical sequences in <bdi class='en-term' dir='ltr'> outside HTML tags, entities, and @@TOK_...@@ placeholders."""
    parts = TOKEN_AND_TAG_RE.split(escaped_html_text)
    for i in range(0, len(parts), 2):
        if parts[i]:
            parts[i] = EN_SEQ_RE.sub(r'<bdi class="en-term" dir="ltr">\1</bdi>', parts[i])
    return "".join(parts)


def assert_clean_output(html_str: str, context_label: str) -> None:
    leaked_toks = re.findall(r"(?:@@TOK_[A-Z]+_\d+@@|INLINECODE_\d+|MEDIA_\d+|CODEBLOCK_\d+|ENT\d+)", html_str)
    if leaked_toks:
        raise RuntimeError(f"[{context_label}] Unrestored placeholder tokens detected: {leaked_toks[:10]}")
    ctrl_matches = CONTROL_CHARS_RE.findall(html_str)
    if ctrl_matches:
        raise RuntimeError(
            f"[{context_label}] Illegal control characters detected (count={len(ctrl_matches)}, sample={repr(ctrl_matches[:5])})"
        )


def markdown_to_html(md_text: str, unit_orig_path: Path, unit_id_prefix: str = "u") -> str:
    text = md_text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\{:target=[\"']_blank[\"']\}", "", text)

    def _clean_bq_fence(m):
        indent = m.group(1)
        fence = m.group(2)
        lang = m.group(3)
        inner = re.sub(r"^[ \t]*>[ \t]?", "", m.group(4), flags=re.M).rstrip("\n")
        return f"{indent}{fence}{lang}\n{inner}\n{indent}{fence}"

    text = BQ_FENCE_BLOCK_RE.sub(_clean_bq_fence, text)

    text = re.sub(r"<!--[ \t]*study-aid-answer-key-start[ \t]*-->", "\n:::STUDY_AID_START:::\n", text)
    text = re.sub(r"<!--[ \t]*study-aid-answer-key-end[ \t]*-->", "\n:::STUDY_AID_END:::\n", text)

    code_blocks: list[str] = []

    def replace_fenced_code(m):
        indent = m.group(1)
        lang = m.group(3).strip() or "text"
        code_raw = textwrap.dedent(m.group(4)).strip("\n")
        line_cnt = len(code_raw.splitlines())
        escaped_code = html.escape(code_raw)
        idx = len(code_blocks)
        lang_badge = html.escape(lang.upper())
        long_cls = " code-container-long" if line_cnt > 25 else ""
        block_html = (
            f'<div class="code-container{long_cls}" dir="ltr">'
            f'<div class="code-header"><span class="code-lang">{lang_badge}</span></div>'
            f'<pre class="code-pre" dir="ltr"><code class="language-{html.escape(lang.lower())}">{escaped_code}</code></pre>'
            f"</div>"
        )
        code_blocks.append(block_html)
        return f"{indent}@@TOK_CODEBLOCK_{idx}@@"

    text = FENCE_BLOCK_RE.sub(replace_fenced_code, text)

    inline_codes: list[str] = []
    inline_raw_texts: list[str] = []

    def replace_inline_code(m):
        idx = len(inline_codes)
        raw_c = m.group(1)
        inline_raw_texts.append(raw_c)
        escaped = html.escape(raw_c)
        inline_codes.append(f'<code class="inline-code" dir="ltr">{escaped}</code>')
        return f"@@TOK_INLINECODE_{idx}@@"

    text = re.sub(r"`([^`\n]+)`", replace_inline_code, text)

    def restore_inline_plain(s_in: str) -> str:
        return re.sub(r"@@TOK_INLINECODE_(\d+)@@", lambda m: inline_raw_texts[int(m.group(1))], s_in)

    def build_figure_html(alt_raw: str, src_raw: str) -> str:
        clean_src = restore_inline_plain(src_raw.strip().split()[0])
        resolved_path = (unit_orig_path.parent / clean_src).resolve()
        if not resolved_path.exists():
            raise FileNotFoundError(f"Missing required image asset on disk: {resolved_path} (from {clean_src})")
        rebased_src = os.path.relpath(resolved_path, BOOK_DIR).replace("\\", "/")
        alt_plain = restore_inline_plain(alt_raw.strip())
        alt_caption = wrap_bidi_en(html.escape(alt_raw.strip()))
        for idx, ic in enumerate(inline_codes):
            alt_caption = alt_caption.replace(f"@@TOK_INLINECODE_{idx}@@", ic)
        src_esc = html.escape(rebased_src)
        return (
            f'<figure class="book-figure">'
            f'<a href="{src_esc}" target="_blank"><img src="{src_esc}" alt="{html.escape(alt_plain)}" /></a>'
            f'{f"<figcaption>{alt_caption}</figcaption>" if alt_raw.strip() else ""}'
            f"</figure>"
        )

    def format_inline(line_str: str) -> str:
        media_tokens: list[str] = []

        def sub_img(m):
            fig_html = build_figure_html(m.group(1), m.group(2))
            idx = len(media_tokens)
            media_tokens.append(fig_html)
            return f"@@TOK_MEDIA_{idx}@@"

        s = IMG_RE.sub(sub_img, line_str)

        def sub_link(m):
            lbl_raw = m.group(1).strip()
            href_raw = restore_inline_plain(m.group(2).strip())
            lbl_esc = html.escape(lbl_raw)
            lbl_esc = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", lbl_esc)
            lbl_esc = wrap_bidi_en(lbl_esc)
            href_esc = html.escape(href_raw)
            a_html = f'<a href="{href_esc}" class="book-link" target="_blank" rel="noopener">{lbl_esc}</a>'
            idx = len(media_tokens)
            media_tokens.append(a_html)
            return f"@@TOK_MEDIA_{idx}@@"

        s = LINK_RE.sub(sub_link, s)
        s = html.escape(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        s = re.sub(r"(?<!\*)\*([^\*\n]+)\*(?!\*)", r"<em>\1</em>", s)
        s = wrap_bidi_en(s)

        for idx, tok in enumerate(media_tokens):
            s = s.replace(f"@@TOK_MEDIA_{idx}@@", tok)
        for idx, ic in enumerate(inline_codes):
            s = s.replace(f"@@TOK_INLINECODE_{idx}@@", ic)
        return s

    lines = text.split("\n")
    out: list[str] = []
    i = 0
    n = len(lines)
    in_ol = False
    in_ul = False
    in_quiz_section = False

    def close_lists():
        nonlocal in_ol, in_ul
        if in_ul:
            out.append("</ul>")
            in_ul = False
        if in_ol:
            out.append("</ol>")
            in_ol = False

    while i < n:
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            j = i + 1
            while j < n and not lines[j].strip():
                j += 1
            if j < n:
                nxt = lines[j]
                nxt_s = nxt.strip()
                is_list_item = bool(re.match(r"^(\d+\.|[-*])\s+", nxt_s))
                is_indented = nxt.startswith(("   ", "\t"))
                if (in_ol or in_ul) and (is_list_item or is_indented):
                    i += 1
                    continue
            close_lists()
            i += 1
            continue

        if stripped == ":::STUDY_AID_START:::":
            close_lists()
            in_quiz_section = False
            out.append('<div class="study-aid-container">')
            i += 1
            continue

        if stripped == ":::STUDY_AID_END:::":
            close_lists()
            out.append("</div>")
            i += 1
            continue

        m_cb = re.match(r"^([ \t]*)@@TOK_CODEBLOCK_(\d+)@@$", line)
        if m_cb:
            if not m_cb.group(1) and (in_ol or in_ul):
                close_lists()
            out.append(f"@@TOK_CODEBLOCK_{m_cb.group(2)}@@")
            i += 1
            continue

        m_standalone_img = re.match(r"^([ \t]*)!\[([^\]]*)\]\(((?:[^()\s]+|\([^()\s]*\))+)\)[ \t]*$", line)
        if m_standalone_img:
            if not m_standalone_img.group(1) and (in_ol or in_ul):
                close_lists()
            out.append(build_figure_html(m_standalone_img.group(2), m_standalone_img.group(3)))
            i += 1
            continue

        if re.match(r"^[-*_]{3,}$", stripped):
            close_lists()
            out.append("<hr />")
            i += 1
            continue

        m_h = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if m_h:
            close_lists()
            level = len(m_h.group(1))
            raw_h_title = m_h.group(2).strip()
            if level == 2 and ("Check your knowledge" in raw_h_title or "اختبر معلوماتك" in raw_h_title):
                in_quiz_section = True
            elif level <= 2:
                in_quiz_section = False
            h_content = format_inline(raw_h_title)
            h_id = f"{unit_id_prefix}-h-{i}"
            out.append(f'<h{level} id="{h_id}" class="book-h{level}">{h_content}</h{level}>')
            i += 1
            continue

        m_quiz_q = re.match(r"^[ \t]*(\d+)\.\s+(.+)$", line) if in_quiz_section else None
        if m_quiz_q:
            close_lists()
            q_num = m_quiz_q.group(1)
            q_stem = m_quiz_q.group(2).strip()
            i += 1
            q_options: list[str] = []
            while i < n:
                cur_s = lines[i].strip()
                if not cur_s:
                    i += 1
                    continue
                m_opt = re.match(r"^[-*]\s*\[\s*[xX ]?\s*\]\s+(.+)$", cur_s)
                if m_opt:
                    q_options.append(m_opt.group(1).strip())
                    i += 1
                    continue
                if re.match(r"^\d+\.\s+", cur_s) or cur_s.startswith(("#", ":::STUDY_AID")):
                    break
                break

            opt_rows_html = []
            for opt_idx, opt_str in enumerate(q_options):
                letter = ARABIC_OPTION_LETTERS[opt_idx] if opt_idx < len(ARABIC_OPTION_LETTERS) else str(opt_idx + 1)
                opt_rows_html.append(
                    f'<div class="quiz-opt-row">'
                    f'<span class="quiz-opt-letter">{letter}</span>'
                    f'<div class="quiz-opt-text">{format_inline(opt_str)}</div>'
                    f"</div>"
                )
            out.append(
                f'<div class="quiz-card">'
                f'<div class="quiz-q-header">'
                f'<span class="quiz-q-badge">السؤال {q_num}</span>'
                f'<div class="quiz-q-stem">{format_inline(q_stem)}</div>'
                f"</div>"
                f'<div class="quiz-options">{"".join(opt_rows_html)}</div>'
                f"</div>"
            )
            continue

        if stripped.startswith("|") and stripped.endswith("|"):
            close_lists()
            tbl_lines = []
            while i < n and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                tbl_lines.append(lines[i].strip())
                i += 1
            if tbl_lines:
                out.append('<div class="table-wrapper"><table class="book-table">')
                header_cells = [c.strip() for c in tbl_lines[0].strip("|").split("|")]
                out.append("<thead><tr>")
                for hc in header_cells:
                    out.append(f"<th>{format_inline(hc)}</th>")
                out.append("</tr></thead><tbody>")
                start_row = 2 if (len(tbl_lines) > 1 and re.match(r"^[\s|:-]+$", tbl_lines[1])) else 1
                for r_line in tbl_lines[start_row:]:
                    r_cells = [c.strip() for c in r_line.strip("|").split("|")]
                    out.append("<tr>")
                    for rc in r_cells:
                        out.append(f"<td>{format_inline(rc)}</td>")
                    out.append("</tr>")
                out.append("</tbody></table></div>")
            continue

        if stripped.startswith(">"):
            if not line.startswith(("   ", "\t")):
                close_lists()
            bq_lines = []
            while i < n and lines[i].strip().startswith(">"):
                bq_lines.append(re.sub(r"^[ \t]*>[ \t]?", "", lines[i]))
                i += 1
            first_bq = bq_lines[0].strip() if bq_lines else ""
            m_alert = re.match(r"^\[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION)\]", first_bq, re.I)
            if m_alert:
                atype = m_alert.group(1).upper()
                label_ar, css_cls = ALERT_LABELS.get(atype, ("ملاحظة", "alert-note"))
                body_lines = bq_lines[1:]
                body_html = "<br />".join(format_inline(bl) for bl in body_lines if bl.strip())
                out.append(
                    f'<div class="callout {css_cls}">'
                    f'<div class="callout-title">{label_ar} ({atype})</div>'
                    f'<div class="callout-body">{body_html}</div>'
                    f"</div>"
                )
            else:
                body_html = "<br />".join(format_inline(bl) for bl in bq_lines if bl.strip())
                out.append(f'<blockquote class="book-quote">{body_html}</blockquote>')
            continue

        m_ol = re.match(r"^[ \t]*(\d+)\.\s+(.+)$", line)
        if m_ol:
            if in_ul:
                out.append("</ul>")
                in_ul = False
            num_val = int(m_ol.group(1))
            if not in_ol:
                start_attr = f' start="{num_val}"' if num_val > 1 else ""
                out.append(f"<ol{start_attr}>")
                in_ol = True
            out.append(f"<li>{format_inline(m_ol.group(2).strip())}</li>")
            i += 1
            continue

        m_ul = re.match(r"^[ \t]*[-*]\s+(.+)$", line)
        if m_ul:
            if in_ol:
                out.append("</ol>")
                in_ol = False
            if not in_ul:
                out.append("<ul>")
                in_ul = True
            item_raw = re.sub(r"^\[\s*[xX ]?\s*\]\s+", "", m_ul.group(1).strip())
            out.append(f"<li>{format_inline(item_raw)}</li>")
            i += 1
            continue

        if not line.startswith(("   ", "\t")):
            close_lists()
        para_lines = [stripped]
        i += 1
        while i < n:
            nxt_l = lines[i]
            nxt_s = nxt_l.strip()
            if (
                not nxt_s
                or nxt_s.startswith(("#", "|", ">", ":::"))
                or re.match(r"^[ \t]*(?:\d+\.|[-*])\s+", nxt_l)
                or re.match(r"^[ \t]*@@TOK_CODEBLOCK_\d+@@$", nxt_l)
                or re.match(r"^[ \t]*!\[([^\]]*)\]\(((?:[^()\s]+|\([^()\s]*\))+)\)[ \t]*$", nxt_l)
                or re.match(r"^[-*_]{3,}$", nxt_s)
            ):
                break
            para_lines.append(nxt_s)
            i += 1

        k = i
        while k < n and not lines[k].strip():
            k += 1
        is_lead = False
        if k < n:
            next_non_empty = lines[k].strip()
            if re.match(r"^@@TOK_CODEBLOCK_\d+@@$", next_non_empty) or next_non_empty.startswith("|"):
                is_lead = True
        p_cls = ' class="lead-para"' if is_lead else ""
        out.append(f"<p{p_cls}>{format_inline(' '.join(para_lines))}</p>")

    close_lists()
    final_html = "\n".join(out)

    for idx, block_html in enumerate(code_blocks):
        final_html = final_html.replace(f"@@TOK_CODEBLOCK_{idx}@@", block_html)
    for idx, ic_html in enumerate(inline_codes):
        final_html = final_html.replace(f"@@TOK_INLINECODE_{idx}@@", ic_html)

    assert_clean_output(final_html, f"Unit {unit_id_prefix} ({unit_orig_path.name})")
    return final_html

BOOK_CSS = """
:root {
  --bg-page: #f8fafc;
  --bg-card: #ffffff;
  --text-main: #0f172a;
  --text-muted: #475569;
  --primary: #0f6cbd;
  --primary-dark: #0c4a6e;
  --border-color: #cbd5e1;
  --code-bg: #0f172a;
  --code-text: #f8fafc;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  padding: 0;
  direction: rtl;
  text-align: right;
  font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
  font-size: 16px;
  line-height: 1.8;
  color: var(--text-main);
  background: var(--bg-page);
}

.layout-shell {
  display: flex;
  min-height: 100vh;
}

.sidebar-toc {
  width: 300px;
  background: #0f172a;
  color: #f1f5f9;
  padding: 24px 18px;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  flex-shrink: 0;
  border-left: 1px solid #1e293b;
}

.sidebar-toc h2 {
  font-size: 1.05rem;
  color: #38bdf8;
  margin-top: 0;
  padding-bottom: 12px;
  border-bottom: 1px solid #334155;
}

.toc-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.toc-list li {
  margin-bottom: 8px;
}

.toc-list a {
  color: #cbd5e1;
  text-decoration: none;
  font-size: 0.92rem;
  display: block;
  padding: 6px 10px;
  border-radius: 6px;
}

.toc-list a:hover {
  background: #1e293b;
  color: #ffffff;
}

.main-content {
  flex: 1;
  max-width: 980px;
  margin: 0 auto;
  padding: 32px 40px;
}

.book-cover {
  background: linear-gradient(135deg, #0c4a6e 0%, #0f172a 100%);
  color: #ffffff;
  padding: 36px 36px;
  border-radius: 14px;
  margin-bottom: 32px;
}

.book-cover .badge {
  display: inline-block;
  direction: ltr;
  unicode-bidi: isolate;
  background: rgba(56, 189, 248, 0.2);
  color: #7dd3fc;
  border: 1px solid rgba(56, 189, 248, 0.4);
  padding: 4px 14px;
  border-radius: 999px;
  font-size: 0.85rem;
  margin-bottom: 12px;
}

.book-cover h1 {
  margin: 0 0 10px 0;
  font-size: 1.85rem;
  line-height: 1.45;
}

.book-cover h1 .en-term {
  color: #7dd3fc;
}

.book-cover p {
  margin: 0;
  color: #cbd5e1;
  font-size: 1rem;
}

.book-cover p .en-term {
  color: #e0f2fe;
}

.unit-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 30px 34px;
  margin-bottom: 30px;
}

.unit-header-group {
  break-inside: avoid;
  page-break-inside: avoid;
  break-after: avoid;
  page-break-after: avoid;
}

.unit-meta-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  background: #f1f5f9;
  padding: 8px 14px;
  border-radius: 8px;
  margin-bottom: 16px;
  font-size: 0.85rem;
  color: var(--text-muted);
  break-after: avoid;
  page-break-after: avoid;
}

.unit-meta-bar a {
  color: var(--primary);
  text-decoration: none;
  font-weight: 600;
}

.book-h1 {
  font-size: 1.65rem;
  color: #0f172a;
  border-bottom: 3px solid var(--primary);
  padding-bottom: 10px;
  margin-top: 0;
  break-after: avoid;
  page-break-after: avoid;
}

.book-h2 {
  font-size: 1.32rem;
  color: #0c4a6e;
  margin-top: 26px;
  padding-right: 12px;
  border-right: 4px solid var(--primary);
  break-after: avoid;
  page-break-after: avoid;
}

.book-h3 {
  font-size: 1.14rem;
  color: #1e293b;
  margin-top: 20px;
  break-after: avoid;
  page-break-after: avoid;
}

.lead-para {
  break-after: avoid;
  page-break-after: avoid;
}

.en-term {
  direction: ltr;
  unicode-bidi: isolate;
  font-family: 'Segoe UI', Tahoma, sans-serif;
  font-weight: 600;
  color: #0369a1;
  padding: 0 2px;
}

.inline-code {
  direction: ltr;
  unicode-bidi: isolate;
  font-family: 'Cascadia Code', Consolas, 'Courier New', monospace;
  font-size: 0.88em;
  background: #f1f5f9;
  color: #be123c;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid #cbd5e1;
}

.code-container {
  direction: ltr;
  text-align: left;
  margin: 18px 0;
  border-radius: 8px;
  overflow: hidden;
  background: var(--code-bg);
  border: 1px solid #1e293b;
  break-inside: avoid;
  page-break-inside: avoid;
}

.code-container-long {
  break-inside: auto;
  page-break-inside: auto;
}

.code-header {
  background: #1e293b;
  padding: 5px 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  break-after: avoid;
  page-break-after: avoid;
}

.code-lang {
  color: #38bdf8;
  font-family: 'Cascadia Code', Consolas, monospace;
  font-size: 0.76rem;
  font-weight: 600;
}

.code-pre {
  margin: 0;
  padding: 14px 16px;
  overflow-x: auto;
  font-family: 'Cascadia Code', Consolas, 'Courier New', monospace;
  font-size: 0.86rem;
  line-height: 1.55;
  color: var(--code-text);
  white-space: pre-wrap;
  word-break: break-word;
}

.table-wrapper {
  overflow-x: auto;
  margin: 18px 0;
}

.book-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.93rem;
}

.book-table thead {
  display: table-header-group;
}

.book-table tr {
  break-inside: avoid;
  page-break-inside: avoid;
}

.book-table th, .book-table td {
  border: 1px solid #cbd5e1;
  padding: 10px 12px;
  text-align: right;
  vertical-align: top;
}

.book-table th {
  background: #f1f5f9;
  color: #0f172a;
  font-weight: 700;
}

.book-table tr:nth-child(even) td {
  background: #f8fafc;
}

.callout {
  border-radius: 8px;
  padding: 14px 18px;
  margin: 16px 0;
  border-right: 5px solid #0284c7;
  background: #f0f9ff;
  break-inside: avoid;
  page-break-inside: avoid;
}

.callout-title {
  font-weight: 700;
  margin-bottom: 6px;
  color: #0369a1;
}

.alert-tip { border-right-color: #16a34a; background: #f0fdf4; }
.alert-tip .callout-title { color: #15803d; }
.alert-important { border-right-color: #7c3aed; background: #f5f3ff; }
.alert-important .callout-title { color: #6d28d9; }
.alert-warning { border-right-color: #d97706; background: #fffbeb; }
.alert-warning .callout-title { color: #b45309; }
.alert-caution { border-right-color: #dc2626; background: #fef2f2; }
.alert-caution .callout-title { color: #b91c1c; }

.quiz-card {
  border: 1px solid #cbd5e1;
  border-radius: 10px;
  background: #f8fafc;
  padding: 14px 18px;
  margin: 14px 0;
  break-inside: avoid;
  page-break-inside: avoid;
}

.quiz-q-header {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e2e8f0;
}

.quiz-q-badge {
  background: var(--primary);
  color: #ffffff;
  font-weight: 700;
  font-size: 0.82rem;
  padding: 3px 10px;
  border-radius: 6px;
  white-space: nowrap;
  flex-shrink: 0;
}

.quiz-q-stem {
  display: block;
  flex: 1;
  font-weight: 600;
  color: #0f172a;
  direction: rtl;
  text-align: right;
}

.quiz-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quiz-opt-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: #ffffff;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  padding: 8px 12px;
}

.quiz-opt-letter {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: #e0f2fe;
  color: #0369a1;
  font-weight: 700;
  font-size: 0.88rem;
  flex-shrink: 0;
}

.quiz-opt-text {
  display: block;
  flex: 1;
  direction: rtl;
  text-align: right;
  line-height: 1.6;
}

.study-aid-container {
  margin-top: 22px;
  padding: 18px 22px;
  border-radius: 10px;
  background: #f8fafc;
  border: 2px solid #0284c7;
}

.book-figure {
  margin: 20px auto;
  text-align: center;
  background: #f8fafc;
  padding: 14px;
  border-radius: 10px;
  border: 1px solid #cbd5e1;
  break-inside: avoid;
  page-break-inside: avoid;
}

.book-figure img {
  max-width: 100%;
  height: auto;
  border-radius: 6px;
}

.book-figure figcaption {
  margin-top: 8px;
  font-size: 0.88rem;
  color: var(--text-muted);
}

@media (max-width: 900px) {
  .layout-shell {
    flex-direction: column;
  }
  .sidebar-toc {
    width: 100%;
    height: auto;
    position: relative;
  }
  .main-content {
    padding: 20px 16px;
  }
}

@media print {
  @page {
    size: A4;
    margin: 12mm 12mm;
  }
  body {
    background: #ffffff;
    font-size: 10.5pt;
    line-height: 1.58;
  }
  .sidebar-toc {
    display: none !important;
  }
  .main-content {
    max-width: 100%;
    padding: 0;
  }
  .book-cover {
    margin-bottom: 18px;
    padding: 22px 26px;
  }
  .unit-card {
    box-shadow: none;
    border: 1px solid #cbd5e1;
    page-break-inside: auto;
    margin-bottom: 16px;
    padding: 16px 20px;
  }
  .unit-card + .unit-card {
    break-before: page;
    page-break-before: always;
  }
  .unit-header-group, .unit-meta-bar, .lead-para, h1, h2, h3, h4, .book-h1, .book-h2, .book-h3 {
    break-after: avoid;
    page-break-after: avoid;
  }
  .unit-header-group, .callout, .book-figure, .quiz-card {
    break-inside: avoid;
    page-break-inside: avoid;
  }
  .code-container {
    break-inside: avoid;
    page-break-inside: avoid;
  }
  .code-container-long {
    break-inside: auto;
    page-break-inside: auto;
  }
  .quiz-card {
    padding: 10px 14px;
    margin: 10px 0;
  }
  .quiz-q-header {
    margin-bottom: 8px;
    padding-bottom: 6px;
  }
  .quiz-options {
    gap: 6px;
  }
  .quiz-opt-row {
    padding: 6px 10px;
  }
}
"""


def render_pdf_with_edge(html_path: Path, pdf_path: Path) -> bool:
    edge_bin = None
    for candidate in EDGE_PATHS:
        if Path(candidate).exists():
            edge_bin = candidate
            break
    if not edge_bin:
        print("[WARN] Microsoft Edge / Chrome executable not found for PDF rendering.")
        return False

    if pdf_path.exists():
        pdf_path.unlink()

    file_uri = html_path.resolve().as_uri()
    with tempfile.TemporaryDirectory(prefix="edge_pdf_") as tmp_profile:
        cmd = [
            edge_bin,
            "--headless",
            "--disable-gpu",
            f"--user-data-dir={tmp_profile}",
            "--no-pdf-header-footer",
            "--virtual-time-budget=5000",
            f"--print-to-pdf={pdf_path.resolve()}",
            file_uri,
        ]
        subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=90)

    return pdf_path.exists() and pdf_path.stat().st_size > 1000


def compile_units_to_html_and_pdf(
    units: list[dict],
    title_ar: str,
    subtitle_ar: str,
    badge_text: str,
    out_html_path: Path,
    out_pdf_path: Path,
) -> None:
    toc_items = []
    unit_sections = []

    for idx, u in enumerate(units, 1):
        trans_path = TRANS_DIR / u["rel_path"]
        orig_path = ORIG_DIR / u["rel_path"]
        if not trans_path.exists():
            continue
        md_content = trans_path.read_text(encoding="utf-8")
        m_h1 = re.search(r"^\s*#\s+(.+)$", md_content, re.M)
        h1_title = m_h1.group(1).strip() if m_h1 else u["title_en"]
        h1_title_plain = re.sub(r"`([^`]+)`", r"\1", h1_title)
        anchor = f"unit-{idx}"
        toc_items.append(
            f'<li><a href="#{anchor}">{idx}. {wrap_bidi_en(html.escape(h1_title_plain))}</a></li>'
        )
        body_html = markdown_to_html(md_content, orig_path, unit_id_prefix=f"u{idx}")
        meta_bar = (
            f'<div class="unit-meta-bar">'
            f'<span><strong>الوحدة:</strong> <bdi class="en-term" dir="ltr">{html.escape(u["unit_id"])}</bdi> — <bdi class="en-term" dir="ltr">{html.escape(u["title_en"])}</bdi></span>'
            f'<a href="{html.escape(u["page_url"])}" target="_blank" rel="noopener">المصدر الرسمي على <bdi class="en-term" dir="ltr">Microsoft Learn / GitHub</bdi> ↗</a>'
            f"</div>"
        )
        body_grouped = re.sub(
            r"^(\s*<h1\b[^>]*>.*?</h1>)",
            lambda m: f'<div class="unit-header-group">\n{meta_bar}\n{m.group(1)}\n</div>',
            body_html,
            count=1,
            flags=re.S,
        )
        if '<div class="unit-header-group">' not in body_grouped:
            body_grouped = f'<div class="unit-header-group">\n{meta_bar}\n</div>\n{body_html}'

        unit_sections.append(
            f'<section id="{anchor}" class="unit-card">\n{body_grouped}\n</section>'
        )

    full_html = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{html.escape(title_ar)}</title>
  <style>{BOOK_CSS}</style>
</head>
<body>
  <div class="layout-shell">
    <aside class="sidebar-toc">
      <h2>فهرس المحتويات ({len(unit_sections)} وحدات)</h2>
      <ul class="toc-list">
        {"".join(toc_items)}
      </ul>
    </aside>
    <main class="main-content">
      <header class="book-cover">
        <div class="badge">{html.escape(badge_text)}</div>
        <h1>{wrap_bidi_en(html.escape(title_ar))}</h1>
        <p>{wrap_bidi_en(html.escape(subtitle_ar))}</p>
      </header>
      {"".join(unit_sections)}
    </main>
  </div>
</body>
</html>
"""
    assert_clean_output(full_html, f"Full HTML ({out_html_path.name})")
    out_html_path.write_text(full_html, encoding="utf-8")
    print(f"[OK] Generated HTML: {out_html_path} ({out_html_path.stat().st_size:,} bytes)")
    if render_pdf_with_edge(out_html_path, out_pdf_path):
        print(f"[OK] Generated PDF : {out_pdf_path} ({out_pdf_path.stat().st_size:,} bytes)")
    else:
        raise RuntimeError(f"[FAIL] Could not generate PDF: {out_pdf_path}")


def main():
    parser = argparse.ArgumentParser(description="Compile validated Arabic Markdown units into HTML & PDF.")
    parser.add_argument("--pilot", action="store_true", help="Build pilot-preview.html and pilot-preview.pdf")
    parser.add_argument("--volume", type=str, help="Build a specific volume (v1, v2, v3)")
    parser.add_argument("--all", action="store_true", help="Build all volumes")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    sources_cfg = json.loads((CONFIG_DIR / "sources.yaml").read_text(encoding="utf-8"))

    if args.pilot or (not args.volume and not args.all):
        pilot_units = [u for u in manifest["units"] if u.get("is_pilot")]
        compile_units_to_html_and_pdf(
            pilot_units,
            title_ar="الإصدار التجريبي (Pilot Preview) — موسوعة مطوّر Microsoft Power Platform و Dynamics 365 لشهادة AB-400",
            subtitle_ar="عينة معمارية وتطبيقية شاملة (4 وحدات: معمارية المنصة + كود C# Plug-ins + اختبار تقييمي + معمل تطبيقي كامل مع الكود المرجعي الكامل وشرحه)",
            badge_text="Exam AB-400 / Course AB-400T00 — Pilot Build v3",
            out_html_path=BOOK_DIR / "pilot-preview.html",
            out_pdf_path=BOOK_DIR / "pilot-preview.pdf",
        )

    if args.volume or args.all:
        for vol in sources_cfg["volumes"]:
            vid = vol["id"]
            if args.volume and args.volume != vid:
                continue
            v_num = vol["number"]
            v_units = [
                u
                for u in manifest["units"]
                if u.get("volume_id") == vid and (TRANS_DIR / u["rel_path"]).exists()
            ]
            if not v_units:
                print(f"[SKIP] No translated units found yet for {vid}.")
                continue
            compile_units_to_html_and_pdf(
                v_units,
                title_ar=vol["title_ar"],
                subtitle_ar=sources_cfg["book_subtitle_ar"],
                badge_text=vol["title_en"],
                out_html_path=BOOK_DIR / f"volume-{v_num}.html",
                out_pdf_path=BOOK_DIR / f"volume-{v_num}.pdf",
            )


if __name__ == "__main__":
    main()
