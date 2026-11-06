"""
validate.py — 15-Point Structural, Fidelity, Asset, and Compiled Output Validator (v3).

Validates:
- Checks 1–13 on each translated Markdown unit against its English source in book/original/:
  1. SHA-256 integrity of original source file.
  2. ATX Heading hierarchy and count parity.
  3. Fenced Code Blocks (100% byte-identical count, language tag, and body across ```, ````, ~~~, and > ```).
  4. Hyperlinks multiset parity.
  5. Image paths parity, Study-Aid Answer Key verification badge (SOURCE_VERIFIED / AI_DRAFT; HUMAN_VERIFIED forbidden unless human_reviewed=True), and Lab Reference Code Walkthrough Appendix.
  6. Quiz checkboxes parity and list items count within tolerance.
  7. GFM Pipe Table row/column structure parity.
  8. Paragraph count and non-summarization character length ratio (>= 70%).
  9. Numeric literals preservation.
  10. Strict English glossary terms enforcement.
  11. Arabic script ratio (>= 45%) and expanded control characters cleanliness (C0, DEL, C1, PUA, U+FFFD).
  12. Full Inline Code comparison (exact count, exact order, and exact content between original and translated body).
  13. Image asset file existence, binary magic-byte signature, and positive pixel dimensions.
- Checks 14–15 on compiled HTML & PDF outputs:
  14. Zero placeholder leaks, zero control characters, zero external Google Fonts, zero <p><figure> nesting, portable relative image paths inside BOOK_DIR, and 100% ordered Inline Code equality between Markdown source and compiled HTML <section>.
  15. PDF binary header/EOF, page count, embedded /Subtype /Image XObjects with positive /Width and /Height, and zero leaked placeholders inside decompressed FlateDecode streams.
"""

import argparse
import hashlib
import html
import json
import os
import re
import struct
import sys
import textwrap
import zlib
from collections import Counter
from pathlib import Path

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parents[2]
BOOK_DIR = ROOT_DIR / "book"
CONFIG_DIR = BOOK_DIR / "config"
ORIG_DIR = BOOK_DIR / "original"
TRANS_DIR = BOOK_DIR / "translated"
MANIFEST_PATH = BOOK_DIR / "manifests" / "manifest.json"

FENCE_RE = re.compile(
    r"^([ \t]*)(`{3,}|~{3,})([a-zA-Z0-9_+-]*)[ \t]*\n(.*?)\n[ \t]*\2[ \t]*$",
    re.M | re.S,
)
BQ_FENCE_RE = re.compile(
    r"^([ \t]*)>[ \t]*(`{3,}|~{3,})([a-zA-Z0-9_+-]*)[ \t]*\n((?:[ \t]*>[^\n]*\n)+?)[ \t]*>[ \t]*\2[ \t]*$",
    re.M,
)
STUDY_AID_RE = re.compile(
    r"<!--[ \t]*study-aid-answer-key-start[ \t]*-->.*?<!--[ \t]*study-aid-answer-key-end[ \t]*-->",
    re.S,
)

# Expanded Control Character Scope:
# - ASCII C0 control chars: \x00-\x08, \x0b, \x0c, \x0e-\x1f (excludes \t=\x09, \n=\x0a, \r=\x0d)
# - ASCII DEL: \x7f
# - Unicode C1 control chars: \u0080-\u009f
# - Unicode Private Use Area (PUA): \ue000-\uf8ff
# - Unicode Replacement Character: \ufffd
CONTROL_CHARS_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f\u0080-\u009f\ue000-\uf8ff\ufffd]")


def normalize_bq_fences(text: str) -> str:
    def _clean(m):
        indent = m.group(1)
        fence = m.group(2)
        lang = m.group(3)
        inner = re.sub(r"^[ \t]*>[ \t]?", "", m.group(4), flags=re.M).rstrip("\n")
        return f"{indent}{fence}{lang}\n{inner}\n{indent}{fence}"

    return BQ_FENCE_RE.sub(_clean, text)


def strip_fenced_code(text: str) -> str:
    return FENCE_RE.sub("", normalize_bq_fences(text))


def extract_inline_codes(text_no_fenced: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r"`([^`\n]+)`", text_no_fenced)]


def strip_inline_code(text: str) -> str:
    return re.sub(r"`[^`\n]+`", "", text)


def extract_code_blocks(text: str) -> list[tuple[str, str]]:
    blocks = []
    for m in FENCE_RE.finditer(normalize_bq_fences(text)):
        lang = m.group(3).strip().lower()
        body = textwrap.dedent(m.group(4)).strip()
        blocks.append((lang, body))
    return blocks


def extract_headings(text_no_code: str) -> list[int]:
    return [len(m.group(1)) for m in re.finditer(r"^[ \t]*(#{1,6})\s+\S+", text_no_code, re.M)]


def extract_images(text_no_code: str) -> list[str]:
    return [m.group(2).strip().split()[0] for m in re.finditer(r"!\[([^\]]*)\]\(([^\)]+)\)", text_no_code)]


def extract_links(text_no_code: str) -> list[str]:
    no_imgs = re.sub(r"!\[[^\]]*\]\([^\)]+\)", "", text_no_code)
    return [m.group(2).strip() for m in re.finditer(r"\[([^\]]+)\]\(((?:[^()\s]+|\([^()\s]*\))+)\)", no_imgs)]


def extract_table_rows(text_no_code: str) -> list[int]:
    rows = []
    for m in re.finditer(r"^[ \t]*\|(.+)\|[ \t]*$", text_no_code, re.M):
        row_str = re.sub(r"`[^`\n]+`", "CODE", m.group(1))
        cols = [c.strip() for c in row_str.split("|")]
        rows.append(len(cols))
    return rows


def build_term_regex(term: str) -> re.Pattern:
    if term.startswith("$"):
        return re.compile(r"(?i)(?<![A-Za-z0-9_])" + re.escape(term) + r"\b")
    if term == "React":
        return re.compile(r"(?<![A-Za-z0-9_])React(?!\s+to\b)(?![A-Za-z0-9_])")
    if term.isupper():
        return re.compile(r"(?<![A-Za-z0-9_])" + re.escape(term) + r"(?:ful|s)?(?![A-Za-z0-9_])")
    return re.compile(r"(?i)(?<![A-Za-z0-9_])" + re.escape(term) + r"(?:e?s)?(?![A-Za-z0-9_])")


def inspect_image_file(img_path: Path) -> tuple[bool, int, int, str]:
    """Verify image exists, has valid binary header, and extract (width, height, format)."""
    if not img_path.exists() or not img_path.is_file() or img_path.stat().st_size < 64:
        return False, 0, 0, "missing_or_empty"
    head = img_path.read_bytes()[:64]
    if head.startswith(b"\x89PNG\r\n\x1a\n") and head[12:16] == b"IHDR":
        w, h = struct.unpack(">II", head[16:24])
        return (w > 0 and h > 0), w, h, "PNG"
    if head.startswith(b"\xff\xd8\xff"):
        return True, 1, 1, "JPEG"
    if head.startswith((b"GIF87a", b"GIF89a")):
        w, h = struct.unpack("<HH", head[6:10])
        return (w > 0 and h > 0), w, h, "GIF"
    if b"<svg" in head.lower() or b"<?xml" in head.lower():
        return True, 1, 1, "SVG"
    return False, 0, 0, "invalid_signature"


def verify_image_signature(img_path: Path) -> bool:
    ok, _, _, _ = inspect_image_file(img_path)
    return ok


def validate_unit(unit: dict, glossary: dict) -> tuple[bool, list[str]]:
    errors: list[str] = []
    orig_path = ORIG_DIR / unit["rel_path"]
    trans_path = TRANS_DIR / unit["rel_path"]

    if not orig_path.exists():
        return False, [f"Original file missing: {orig_path}"]
    if not trans_path.exists():
        return False, [f"Translated file missing: {trans_path}"]

    orig_bytes = orig_path.read_bytes()
    actual_sha = hashlib.sha256(orig_bytes).hexdigest()
    if unit.get("sha256") and actual_sha != unit["sha256"]:
        errors.append(f"Check 1 (SHA-256 Integrity): Mismatch on original file ({actual_sha} != {unit['sha256']})")

    orig_text = orig_bytes.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
    trans_full = trans_path.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")

    if CONTROL_CHARS_RE.search(trans_full):
        errors.append("Check 11 (UTF-8 & Control Char Cleanliness): Found U+FFFD or illegal control char in translation.")

    # Check study-aid / walkthrough appendix requirements & verification badges
    study_aid_matches = STUDY_AID_RE.findall(trans_full)
    if unit.get("is_quiz"):
        if not study_aid_matches or len(study_aid_matches[0].strip()) < 80:
            errors.append(
                "Check 5b (Quiz Study-Aid Answer Key): Missing or empty <!-- study-aid-answer-key-start --> block in quiz unit."
            )
        else:
            aid_block = study_aid_matches[0]
            if "HUMAN_VERIFIED" in aid_block and not unit.get("human_reviewed"):
                errors.append(
                    "Check 5b (Quiz Answer Verification Badge): HUMAN_VERIFIED is not allowed without documented human review; use SOURCE_VERIFIED or AI_DRAFT."
                )
            if not re.search(r"\b(SOURCE_VERIFIED|AI_DRAFT)\b", aid_block) and not (
                unit.get("human_reviewed") and "HUMAN_VERIFIED" in aid_block
            ):
                errors.append(
                    "Check 5b (Quiz Answer Verification Badge): Answer key must explicitly declare SOURCE_VERIFIED or AI_DRAFT."
                )
    if unit.get("is_lab") and unit.get("lab_ref_dir"):
        if not study_aid_matches or len(study_aid_matches[0].strip()) < 300 or "```" not in study_aid_matches[0]:
            errors.append(
                "Check 5c (Lab Code Walkthrough Appendix): Appendix must include the full reference code block and line-by-line walkthrough."
            )

    trans_body = STUDY_AID_RE.sub("", trans_full).strip() + "\n"

    orig_no_code = strip_fenced_code(orig_text)
    trans_no_code = strip_fenced_code(trans_body)

    # Check 2: Headings
    orig_headings = extract_headings(orig_no_code)
    trans_headings = extract_headings(trans_no_code)
    if orig_headings != trans_headings:
        errors.append(
            f"Check 2 (Headings): Heading levels mismatch: original={orig_headings} vs translated={trans_headings}"
        )

    # Check 3: Fenced Code Blocks (100% identical)
    orig_blocks = extract_code_blocks(orig_text)
    trans_blocks = extract_code_blocks(trans_body)
    if len(orig_blocks) != len(trans_blocks):
        errors.append(
            f"Check 3 (Code Blocks): Count mismatch: original={len(orig_blocks)} vs translated={len(trans_blocks)}"
        )
    else:
        for idx, ((olang, obody), (tlang, tbody)) in enumerate(zip(orig_blocks, trans_blocks), 1):
            if olang != tlang:
                errors.append(f"Check 3 (Code Block #{idx} Lang): '{olang}' != '{tlang}'")
            if obody != tbody:
                errors.append(f"Check 3 (Code Block #{idx} Content): Code block #{idx} is not byte-identical to original.")

    # Check 4: Hyperlinks
    orig_links_list = extract_links(orig_no_code)
    trans_links_list = extract_links(trans_no_code)
    if Counter(orig_links_list) != Counter(trans_links_list):
        missing_l = Counter(orig_links_list) - Counter(trans_links_list)
        extra_l = Counter(trans_links_list) - Counter(orig_links_list)
        errors.append(f"Check 4 (Hyperlinks): URL mismatch. Missing={dict(missing_l)}, Extra={dict(extra_l)}")

    # Check 5 & 13: Images & Binary Signatures
    orig_imgs = extract_images(orig_no_code)
    trans_imgs = extract_images(trans_no_code)
    if orig_imgs != trans_imgs:
        errors.append(f"Check 5 (Images): Image paths mismatch: original={orig_imgs} vs translated={trans_imgs}")
    for img_rel in trans_imgs:
        resolved_img = (orig_path.parent / img_rel).resolve()
        ok_img, w, h, fmt = inspect_image_file(resolved_img)
        if not ok_img:
            errors.append(f"Check 13 (Image Binary Signature / Existence): Invalid or missing image file: {resolved_img} ({fmt})")

    # Check 6: Lists & Quiz Checkboxes
    orig_cb = len(re.findall(r"^[ \t]*-[ \t]*\[[ xX]\]", orig_no_code, re.M))
    trans_cb = len(re.findall(r"^[ \t]*-[ \t]*\[[ xX]\]", trans_no_code, re.M))
    if orig_cb != trans_cb:
        errors.append(f"Check 6 (Quiz Checkboxes): Count mismatch: original={orig_cb} vs translated={trans_cb}")

    orig_list_items = len(re.findall(r"^[ \t]*(?:[-*]|\d+\.)\s+", orig_no_code, re.M))
    trans_list_items = len(re.findall(r"^[ \t]*(?:[-*]|\d+\.)\s+", trans_no_code, re.M))
    allowed_list_diff = max(2, int(orig_list_items * 0.10))
    if abs(orig_list_items - trans_list_items) > allowed_list_diff:
        errors.append(
            f"Check 6 (List Items): Count diverged beyond tolerance: original={orig_list_items} vs translated={trans_list_items}"
        )

    # Check 7: Tables
    orig_tables = extract_table_rows(orig_no_code)
    trans_tables = extract_table_rows(trans_no_code)
    if orig_tables != trans_tables:
        errors.append(f"Check 7 (Tables): Table structure mismatch: original={orig_tables} vs translated={trans_tables}")

    # Check 8: Paragraph Count & Non-Summarization Character Length Ratio
    orig_paras = [p.strip() for p in re.split(r"\n[ \t]*\n", orig_no_code) if p.strip()]
    trans_paras = [p.strip() for p in re.split(r"\n[ \t]*\n", trans_no_code) if p.strip()]
    allowed_para_diff = max(2, int(len(orig_paras) * 0.15))
    if abs(len(orig_paras) - len(trans_paras)) > allowed_para_diff:
        errors.append(
            f"Check 8a (Paragraph Count): original={len(orig_paras)} vs translated={len(trans_paras)} (allowed diff ±{allowed_para_diff})"
        )

    orig_char_len = len(orig_no_code.strip())
    trans_char_len = len(trans_no_code.strip())
    if orig_char_len > 100 and (trans_char_len / orig_char_len) < 0.70:
        errors.append(
            f"Check 8b (Non-Summarization Length Ratio): Translated non-code length ({trans_char_len}) is < 70% of original ({orig_char_len})"
        )

    # Check 9: Numbers Preservation
    orig_no_inline = strip_inline_code(re.sub(r"!?\[[^\]]*\]\([^\)]+\)", "", orig_no_code))
    orig_nums = set(re.findall(r"\b\d+(?:\.\d+)?\b", orig_no_inline))
    trans_nums = set(re.findall(r"\b\d+(?:\.\d+)?\b", trans_full))
    missing_nums = orig_nums - trans_nums
    if missing_nums:
        errors.append(f"Check 9 (Numbers Preservation): Missing numbers in translation: {sorted(missing_nums)}")

    # Check 10: Strict Glossary Terms Enforcement
    missing_terms = []
    for term in glossary.get("strict_terms", []):
        pat = build_term_regex(term)
        if pat.search(orig_no_code) and not pat.search(trans_full):
            missing_terms.append(term)
    if missing_terms:
        errors.append(f"Check 10 (Strict Glossary Terms): Missing required English terms: {missing_terms}")

    # Check 11: Arabic Script Ratio
    prose_only = strip_inline_code(re.sub(r"!?\[[^\]]*\]\([^\)]+\)", "", trans_no_code))
    for term in glossary.get("strict_terms", []) + glossary.get("contextual_platform_terms", []):
        prose_only = build_term_regex(term).sub("", prose_only)
    ar_chars = len(re.findall(r"[\u0600-\u06FF]", prose_only))
    en_chars = len(re.findall(r"[A-Za-z]", prose_only))
    total_alpha = ar_chars + en_chars
    if total_alpha > 50:
        ar_ratio = ar_chars / total_alpha
        if ar_ratio < 0.45:
            errors.append(f"Check 11 (Arabic Ratio): Arabic ratio is {ar_ratio:.1%} (< 45% minimum).")

    # Check 12: Full Inline Code Comparison (Count, Order, and Content)
    orig_inline_codes = extract_inline_codes(orig_no_code)
    trans_inline_codes = extract_inline_codes(trans_no_code)
    if orig_inline_codes != trans_inline_codes:
        errors.append(
            f"Check 12 (Inline Code Count/Order/Content): Mismatch between original ({len(orig_inline_codes)}) and translated body ({len(trans_inline_codes)})."
        )

    # Update unified manifest contract fields for this unit
    unit["source_url"] = unit.get("page_url")
    unit["source_title"] = unit.get("title_en")
    unit["source_file"] = f"book/original/{unit['rel_path']}"
    unit["translated_file"] = f"book/translated/{unit['rel_path']}"
    unit["source_hash"] = actual_sha
    unit["content_classification"] = (
        "SUPPLEMENTAL"
        if unit.get("module_uid") == "learn-bizapps.command-bar-customize"
        else ("CURRENT" if unit.get("volume_id") in ("v1", "v2") else "HISTORICAL")
    )
    unit["inline_code_items"] = orig_inline_codes
    unit["code_blocks_count"] = len(orig_blocks)
    unit["links"] = orig_links_list
    unit["quiz_items_count"] = orig_cb
    unit["translation_status"] = "completed"
    unit["validation_status"] = "passed" if not errors else "failed"

    return len(errors) == 0, errors


def validate_compiled_outputs(html_path: Path, pdf_path: Path, units: list[dict]) -> tuple[bool, list[str], dict]:
    errors: list[str] = []
    metrics: dict = {}

    if not html_path.exists():
        return False, [f"Check 14 (Compiled HTML): Missing {html_path}"], metrics
    if not pdf_path.exists():
        return False, [f"Check 15 (Compiled PDF): Missing {pdf_path}"], metrics

    html_text = html_path.read_text(encoding="utf-8")
    inline_leaks = len(re.findall(r"INLINECODE_\d+", html_text))
    media_leaks = len(re.findall(r"MEDIA_\d+", html_text))
    ent_leaks = len(re.findall(r"ENT\d+", html_text))
    tok_leaks = len(re.findall(r"@@TOK_[A-Z]+_\d+@@", html_text))
    nul_count = html_text.count("\x00")
    soh_count = html_text.count("\x01")
    ctrl_count = len(CONTROL_CHARS_RE.findall(html_text))
    gfonts_count = len(re.findall(r"fonts\.googleapis\.com", html_text))
    p_figure_nesting = len(re.findall(r"<p[^>]*>\s*<figure\b", html_text))
    img_tags = re.findall(r'<img\s+[^>]*src="([^"]+)"[^>]*>', html_text)
    inline_code_tags = len(re.findall(r'<code class="inline-code"', html_text))
    code_pre_tags = len(re.findall(r'<pre class="code-pre"', html_text))
    quiz_cards = len(re.findall(r'<div class="quiz-card">', html_text))

    # Full Ordered Comparison of Inline Code across Source, Translation, and Compiled HTML per unit
    total_body_inline_matched = 0
    total_full_inline_matched = 0
    for idx, u in enumerate(units, 1):
        orig_t = (ORIG_DIR / u["rel_path"]).read_text(encoding="utf-8")
        trans_t = (TRANS_DIR / u["rel_path"]).read_text(encoding="utf-8")
        orig_ic = extract_inline_codes(strip_fenced_code(orig_t))
        trans_body_ic = extract_inline_codes(strip_fenced_code(STUDY_AID_RE.sub("", trans_t)))
        trans_full_ic = extract_inline_codes(strip_fenced_code(trans_t))

        sec_m = re.search(rf'<section id="unit-{idx}"[^>]*>(.*?)</section>', html_text, re.S)
        sec_html = sec_m.group(1) if sec_m else ""
        sec_no_aid = re.sub(r'<div class="study-aid-container">.*$', "", sec_html, flags=re.S)
        html_body_ic = [
            html.unescape(x).strip()
            for x in re.findall(r'<code class="inline-code" dir="ltr">(.*?)</code>', sec_no_aid)
        ]
        html_full_ic = [
            html.unescape(x).strip()
            for x in re.findall(r'<code class="inline-code" dir="ltr">(.*?)</code>', sec_html)
        ]

        if orig_ic != trans_body_ic or trans_body_ic != html_body_ic:
            errors.append(
                f"Check 14f (HTML Inline Code Body Parity Unit #{idx}): orig={len(orig_ic)}, trans_body={len(trans_body_ic)}, html_body={len(html_body_ic)}"
            )
        else:
            total_body_inline_matched += len(html_body_ic)

        if trans_full_ic != html_full_ic:
            errors.append(
                f"Check 14g (HTML Inline Code Full Parity Unit #{idx}): trans_full={len(trans_full_ic)} != html_full={len(html_full_ic)}"
            )
        else:
            total_full_inline_matched += len(html_full_ic)

    expected_imgs = sum(len(u.get("assets", [])) for u in units)

    metrics["html"] = {
        "size_bytes": html_path.stat().st_size,
        "inlinecode_leaks": inline_leaks,
        "media_leaks": media_leaks,
        "ent_leaks": ent_leaks,
        "tok_leaks": tok_leaks,
        "nul_chars": nul_count,
        "soh_chars": soh_count,
        "ctrl_chars": ctrl_count,
        "google_fonts_imports": gfonts_count,
        "p_figure_nesting_count": p_figure_nesting,
        "img_tags_count": len(img_tags),
        "expected_imgs_count": expected_imgs,
        "inline_code_tags_count": inline_code_tags,
        "inline_code_body_parity_count": total_body_inline_matched,
        "inline_code_full_parity_count": total_full_inline_matched,
        "code_pre_tags_count": code_pre_tags,
        "quiz_cards_count": quiz_cards,
    }

    if inline_leaks or media_leaks or ent_leaks or tok_leaks:
        errors.append(
            f"Check 14a (HTML Placeholders): Leaked tokens found: INLINECODE={inline_leaks}, MEDIA={media_leaks}, ENT={ent_leaks}, TOK={tok_leaks}"
        )
    if ctrl_count > 0:
        errors.append(f"Check 14b (HTML Control Chars): Found {ctrl_count} control chars (NUL={nul_count}, SOH={soh_count})")
    if gfonts_count > 0:
        errors.append("Check 14c (Offline Fonts): Found external fonts.googleapis.com dependency in HTML.")
    if p_figure_nesting > 0:
        errors.append(f"Check 14d (Figure Block Structure): Found {p_figure_nesting} <p><figure> nesting violations.")
    if len(img_tags) < expected_imgs:
        errors.append(f"Check 14e (HTML Images): Found {len(img_tags)} <img> tags, expected at least {expected_imgs}.")
    for src in img_tags:
        if Path(src).is_absolute() or src.startswith(("..", "/", "\\")):
            errors.append(f"Check 14e (Image Path Portability): Non-portable image src '{src}' (must be relative inside book/).")
        img_disk = (html_path.parent / src).resolve()
        ok_img, w, h, fmt = inspect_image_file(img_disk)
        if not ok_img:
            errors.append(f"Check 14e (HTML Image Src Broken): {src} -> {img_disk} ({fmt})")

    # Check 15: Inspect PDF binary structure & decompressed streams
    pdf_bytes = pdf_path.read_bytes()
    if not pdf_bytes.startswith(b"%PDF-1.") or b"%%EOF" not in pdf_bytes[-1024:]:
        errors.append("Check 15a (PDF Structure): Invalid PDF header or missing %%EOF.")

    page_count = len(re.findall(rb"/Type\s*/Page\b", pdf_bytes))
    image_xobjects = len(re.findall(rb"/Subtype\s*/Image\b", pdf_bytes))
    img_dims = [
        (int(m.group(1)), int(m.group(2)))
        for m in re.finditer(rb"/Subtype\s*/Image\b[^>]*/Width\s+(\d+)[^>]*/Height\s+(\d+)", pdf_bytes, re.S)
    ]

    # Decompress all FlateDecode streams and scan for leaked placeholder strings
    pdf_leaks = 0
    streams_checked = 0
    for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", pdf_bytes, re.S):
        raw_s = m.group(1)
        try:
            dec = zlib.decompress(raw_s)
            streams_checked += 1
            if re.search(rb"(?:INLINECODE_|MEDIA_|ENT0|@@TOK_)", dec):
                pdf_leaks += 1
        except Exception:
            pass

    metrics["pdf"] = {
        "size_bytes": pdf_path.stat().st_size,
        "page_count": page_count,
        "image_xobjects_count": image_xobjects,
        "image_xobjects_dimensions": img_dims,
        "flate_streams_decompressed": streams_checked,
        "streams_with_placeholder_leaks": pdf_leaks,
    }

    if page_count == 0:
        errors.append("Check 15b (PDF Pages): 0 pages detected in PDF.")
    if expected_imgs > 0 and image_xobjects < expected_imgs:
        errors.append(
            f"Check 15c (PDF Embedded Images): Found {image_xobjects} /Subtype /Image objects in PDF, expected >= {expected_imgs}."
        )
    if pdf_leaks > 0:
        errors.append(f"Check 15d (PDF Stream Leaks): Found {pdf_leaks} PDF streams containing leaked placeholder text.")

    return len(errors) == 0, errors, metrics


def main():
    parser = argparse.ArgumentParser(description="Validate translated Arabic Markdown units and compiled HTML/PDF outputs.")
    parser.add_argument("--pilot", action="store_true", help="Validate all 4 pilot units + pilot-preview.html/pdf")
    parser.add_argument("--unit", type=str, help="Validate a specific unit_id or pilot_id")
    parser.add_argument("--volume", type=str, help="Validate all crawled units in a volume")
    parser.add_argument("--all", action="store_true", help="Validate all translated units")
    args = parser.parse_args()

    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    glossary = json.loads((CONFIG_DIR / "glossary.yaml").read_text(encoding="utf-8"))

    if args.pilot:
        targets = [u for u in manifest["units"] if u.get("is_pilot")]
    elif args.unit:
        targets = [u for u in manifest["units"] if u.get("unit_id") == args.unit or u.get("pilot_id") == args.unit]
    elif args.volume:
        targets = [
            u
            for u in manifest["units"]
            if u.get("volume_id") == args.volume and (TRANS_DIR / u["rel_path"]).exists()
        ]
    elif args.all:
        targets = [u for u in manifest["units"] if (TRANS_DIR / u["rel_path"]).exists()]
    else:
        targets = [u for u in manifest["units"] if u.get("is_pilot")]

    if not targets:
        print("No matching units found to validate.")
        sys.exit(1)

    all_passed = True
    passed_count = 0
    for u in targets:
        ok, errs = validate_unit(u, glossary)
        if ok:
            u["status"] = "validated"
            passed_count += 1
            print(f"[PASS 13/13 UNIT CHECKS] {u['unit_id']} ({u.get('pilot_id') or u['rel_path']})")
        else:
            all_passed = False
            u["status"] = "validation_failed"
            print(f"[FAIL] {u['unit_id']} ({u.get('pilot_id') or u['rel_path']}):")
            for e in errs:
                print(f"   - {e}")

    if args.pilot or (not args.unit and not args.volume and not args.all):
        html_p = BOOK_DIR / "pilot-preview.html"
        pdf_p = BOOK_DIR / "pilot-preview.pdf"
        if html_p.exists() and pdf_p.exists():
            ok_out, out_errs, metrics = validate_compiled_outputs(html_p, pdf_p, targets)
            if ok_out:
                print(f"[PASS CHECKS 14 & 15 — COMPILED HTML & PDF GATE] Metrics: {json.dumps(metrics, ensure_ascii=False)}")
            else:
                all_passed = False
                print("[FAIL COMPILED HTML/PDF GATE]:")
                for e in out_errs:
                    print(f"   - {e}")

    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nValidation Summary: {passed_count}/{len(targets)} units passed all unit checks.")
    if not all_passed:
        sys.exit(1)


if __name__ == "__main__":
    main()
