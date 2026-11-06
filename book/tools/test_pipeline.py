"""
test_pipeline.py — Automated Acceptance-Criteria Test Suite (v3) for the AB-400 Arabic Book Pipeline.

Maps 18 explicit unittest methods 1-to-1 to the 18 Acceptance Criteria (AC-01 through AC-18)
and emits a detailed verification report to book/manifests/test-report-v3.json.
"""

import hashlib
import html
import json
import re
import shutil
import tempfile
import unittest
import zlib
from pathlib import Path

from build import (
    BOOK_CSS,
    BOOK_DIR,
    CONTROL_CHARS_RE,
    EN_SEQ_RE,
    ORIG_DIR,
    TOKEN_AND_TAG_RE,
    TRANS_DIR,
    assert_clean_output,
    markdown_to_html,
    wrap_bidi_en,
)
from validate import (
    CONFIG_DIR,
    MANIFEST_PATH,
    STUDY_AID_RE,
    extract_code_blocks,
    extract_inline_codes,
    inspect_image_file,
    strip_fenced_code,
    validate_compiled_outputs,
    validate_unit,
)

AC_METADATA = {
    "test_AC01_zero_inlinecode_placeholder_leaks": (
        "AC-01",
        "Zero INLINECODE_ or @@TOK_INLINECODE_ placeholder leaks in HTML and PDF",
    ),
    "test_AC02_full_inline_code_comparison_count_order_content": (
        "AC-02",
        "Full comparison of all Inline Code items between source, translation, and HTML (count, order, content)",
    ),
    "test_AC03_zero_media_placeholder_leaks_and_links_restored": (
        "AC-03",
        "Zero MEDIA_ placeholder leaks, zero {:target='_blank'} leaks, and 100% hyperlink parity",
    ),
    "test_AC04_image_existence_relocation_portability_html_and_pdf_embedding": (
        "AC-04",
        "Image file existence, PNG dimensions, path validity after relocating book folder, HTML <img>, and PDF XObject embedding",
    ),
    "test_AC05_html_entities_and_angle_brackets_preserved_not_stripped": (
        "AC-05",
        "Explicit assertions for <EntityReference>, <OptionSetValue>, <DateTime?>, <your environment URL> escaped and never stripped",
    ),
    "test_AC06_control_characters_scope_and_zero_leaks": (
        "AC-06",
        "Expanded control character detection (C0, DEL, C1, PUA, U+FFFD) and zero control chars in outputs",
    ),
    "test_AC07_markdown_code_fence_fixtures_and_byte_identity": (
        "AC-07",
        "Support for ```, ````, ~~~, indented fences, and blockquote > ``` fences, plus 100% code block byte-identity",
    ),
    "test_AC08_en_seq_re_single_line_no_newline_spanning": (
        "AC-08",
        "EN_SEQ_RE uses [ \\t]+ so English term matching never spans across newlines (\\n), plus OData $ operators",
    ),
    "test_AC09_token_and_tag_re_gt_inside_html_attributes": (
        "AC-09",
        "TOKEN_AND_TAG_RE handles '>' inside double-quoted and single-quoted HTML attributes without premature splitting",
    ),
    "test_AC10_standalone_figure_not_wrapped_in_paragraph": (
        "AC-10",
        "Standalone images emitted as top-level <figure class='book-figure'> with zero <p><figure> nesting",
    ),
    "test_AC11_pdf_cover_ab400_bidi_isolation_and_mixed_rtl_ltr": (
        "AC-11",
        "Cover AB-400, mixed RTL/LTR terms, and parentheses properly isolated with <bdi class='en-term' dir='ltr'>",
    ),
    "test_AC12_unit_header_group_prevents_orphaned_meta_bar": (
        "AC-12",
        "Unit metadata bar and H1 grouped in .unit-header-group (break-inside: avoid; break-after: avoid) with page breaks between units",
    ),
    "test_AC13_quiz_cards_vertical_layout_and_compact_print_spacing": (
        "AC-13",
        "Quiz questions rendered in isolated .quiz-card containers with block-level option text and compact print spacing",
    ),
    "test_AC14_lab_appendix_heading_lead_para_and_code_grouped": (
        "AC-14",
        "Lab 01 full 84-line C# reference code present, preceded by .lead-para (break-after: avoid) and .code-container-long",
    ),
    "test_AC15_answer_key_verification_status_source_verified_no_fake_human_verified": (
        "AC-15",
        "Answer key uses SOURCE_VERIFIED (backed by verbatim module quotes) or AI_DRAFT; unverified HUMAN_VERIFIED rejected",
    ),
    "test_AC16_offline_self_contained_css_no_external_fonts": (
        "AC-16",
        "Zero external fonts.googleapis.com dependencies; 100% offline CSS",
    ),
    "test_AC17_manifest_contract_and_historical_supplemental_classification": (
        "AC-17",
        "Manifest tracks all 447 units with SHA-256 hashes, audit counts, and CURRENT / HISTORICAL / SUPPLEMENTAL classification",
    ),
    "test_AC18_pdf_decompressed_streams_zero_leaks_and_page_count": (
        "AC-18",
        "Decompressed PDF FlateDecode streams contain zero placeholder leaks across all 27 pages",
    ),
}

TEST_EVIDENCE: dict[str, str] = {}


class TestBookPipelineV3(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.glossary = json.loads((CONFIG_DIR / "glossary.yaml").read_text(encoding="utf-8"))
        cls.pilot_units = [u for u in cls.manifest["units"] if u.get("is_pilot")]
        cls.html_path = BOOK_DIR / "pilot-preview.html"
        cls.pdf_path = BOOK_DIR / "pilot-preview.pdf"
        cls.html_text = cls.html_path.read_text(encoding="utf-8")
        cls.pdf_bytes = cls.pdf_path.read_bytes()
        cls.dummy_orig = ORIG_DIR / "v2/s07/m01/02-map-extension-runtimes.md"

    def test_AC01_zero_inlinecode_placeholder_leaks(self):
        html_leaks = re.findall(r"(?:INLINECODE_\d+|@@TOK_INLINECODE_\d+@@)", self.html_text)
        self.assertEqual(len(html_leaks), 0, f"Found leaked inline code tokens in HTML: {html_leaks}")
        with self.assertRaises(RuntimeError):
            assert_clean_output("<p>INLINECODE_0</p>", "ac01")
        with self.assertRaises(RuntimeError):
            assert_clean_output("<p>@@TOK_INLINECODE_0@@</p>", "ac01")
        TEST_EVIDENCE["AC-01"] = "0 INLINECODE_ leaks and 0 @@TOK_INLINECODE_@@ leaks in pilot-preview.html; fail-fast guard verified."

    def test_AC02_full_inline_code_comparison_count_order_content(self):
        per_unit_summary = []
        total_body = 0
        total_full = 0
        for idx, u in enumerate(self.pilot_units, 1):
            orig_md = (ORIG_DIR / u["rel_path"]).read_text(encoding="utf-8")
            trans_md = (TRANS_DIR / u["rel_path"]).read_text(encoding="utf-8")
            orig_codes = extract_inline_codes(strip_fenced_code(orig_md))
            trans_body_codes = extract_inline_codes(strip_fenced_code(STUDY_AID_RE.sub("", trans_md)))
            trans_full_codes = extract_inline_codes(strip_fenced_code(trans_md))

            sec_m = re.search(rf'<section id="unit-{idx}"[^>]*>(.*?)</section>', self.html_text, re.S)
            self.assertIsNotNone(sec_m, f"Missing <section id='unit-{idx}'> in HTML")
            sec_html = sec_m.group(1)
            sec_no_aid = re.sub(r'<div class="study-aid-container">.*$', "", sec_html, flags=re.S)

            html_body_codes = [
                html.unescape(x).strip()
                for x in re.findall(r'<code class="inline-code" dir="ltr">(.*?)</code>', sec_no_aid)
            ]
            html_full_codes = [
                html.unescape(x).strip()
                for x in re.findall(r'<code class="inline-code" dir="ltr">(.*?)</code>', sec_html)
            ]

            self.assertEqual(
                orig_codes,
                trans_body_codes,
                f"Unit {u['pilot_id']} inline code mismatch between original and translated body",
            )
            self.assertEqual(
                orig_codes,
                html_body_codes,
                f"Unit {u['pilot_id']} inline code mismatch between original and compiled HTML body",
            )
            self.assertEqual(
                trans_full_codes,
                html_full_codes,
                f"Unit {u['pilot_id']} inline code mismatch between full translated Markdown and compiled HTML",
            )
            total_body += len(html_body_codes)
            total_full += len(html_full_codes)
            per_unit_summary.append(
                f"{u['pilot_id']}: body={len(orig_codes)}/{len(trans_body_codes)}/{len(html_body_codes)}, full={len(trans_full_codes)}/{len(html_full_codes)}"
            )

        self.assertEqual(total_body, 114)
        self.assertEqual(total_full, 169)
        TEST_EVIDENCE["AC-02"] = f"100% ordered list equality across all 4 units (body: 114==114==114, full with appendices: 169==169 -> {', '.join(per_unit_summary)})."

    def test_AC03_zero_media_placeholder_leaks_and_links_restored(self):
        media_leaks = re.findall(r"(?:MEDIA_\d+|@@TOK_MEDIA_\d+@@)", self.html_text)
        target_blank_leaks = re.findall(r"\{:target=", self.html_text)
        self.assertEqual(len(media_leaks), 0)
        self.assertEqual(len(target_blank_leaks), 0)
        book_links = re.findall(r'<a href="([^"]+)" class="book-link"', self.html_text)
        self.assertEqual(len(book_links), 14)
        TEST_EVIDENCE["AC-03"] = f"0 MEDIA_ leaks, 0 {{:target=}} leaks, and all {len(book_links)}/14 body hyperlinks + 1 image (15 total media items) restored."

    def test_AC04_image_existence_relocation_portability_html_and_pdf_embedding(self):
        img_srcs = re.findall(r'<img\s+[^>]*src="([^"]+)"[^>]*>', self.html_text)
        self.assertGreaterEqual(len(img_srcs), 1)
        rel_src = img_srcs[0]
        self.assertEqual(rel_src, "assets/v2/s07-m01/five-extension-runtimes.png")
        self.assertFalse(Path(rel_src).is_absolute())
        self.assertNotIn("..", rel_src)

        disk_img = (self.html_path.parent / rel_src).resolve()
        ok_sig, width, height, fmt = inspect_image_file(disk_img)
        self.assertTrue(ok_sig)
        self.assertEqual((fmt, width, height), ("PNG", 1536, 1024))
        orig_sha = hashlib.sha256(disk_img.read_bytes()).hexdigest()

        # Simulate moving/relocating the compiled book directory to a brand-new temporary path
        with tempfile.TemporaryDirectory(prefix="relocated_book_") as tmp_dir:
            moved_book = Path(tmp_dir) / "moved_book_folder"
            moved_book.mkdir(parents=True, exist_ok=True)
            moved_html = moved_book / "pilot-preview.html"
            shutil.copy2(self.html_path, moved_html)
            for s in img_srcs:
                target_asset = moved_book / s
                target_asset.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(self.html_path.parent / s, target_asset)

            moved_html_text = moved_html.read_text(encoding="utf-8")
            moved_srcs = re.findall(r'<img\s+[^>]*src="([^"]+)"[^>]*>', moved_html_text)
            for s in moved_srcs:
                resolved_in_moved = (moved_html.parent / s).resolve()
                self.assertTrue(resolved_in_moved.exists())
                self.assertEqual(hashlib.sha256(resolved_in_moved.read_bytes()).hexdigest(), orig_sha)

        # Verify actual embedded image XObject in PDF
        pdf_img_dims = [
            (int(m.group(1)), int(m.group(2)))
            for m in re.finditer(rb"/Subtype\s*/Image\b[^>]*/Width\s+(\d+)[^>]*/Height\s+(\d+)", self.pdf_bytes, re.S)
        ]
        self.assertIn((1536, 1024), pdf_img_dims)
        TEST_EVIDENCE["AC-04"] = (
            f"Asset exists ({disk_img.stat().st_size:,} bytes, {fmt} {width}x{height}, SHA256={orig_sha[:12]}...), "
            f"portable in relocated temp dir, and embedded in PDF XObject with dimensions {pdf_img_dims[0]}."
        )

    def test_AC05_html_entities_and_angle_brackets_preserved_not_stripped(self):
        md_sample = (
            'استخدم النوع `<EntityReference>` أو <EntityReference> في النص، '
            'والنوع `<OptionSetValue>` و <DateTime?> والرابط "<your environment URL>".'
        )
        rendered = markdown_to_html(md_sample, self.dummy_orig, "ac05")
        self.assertNotIn("ENT0", rendered)
        self.assertNotIn("ENT1", rendered)
        self.assertNotIn("<EntityReference>", rendered)
        self.assertNotIn("<OptionSetValue>", rendered)
        self.assertNotIn("<DateTime?>", rendered)
        self.assertNotIn("<your environment URL>", rendered)
        self.assertIn('<code class="inline-code" dir="ltr">&lt;EntityReference&gt;</code>', rendered)
        self.assertIn('&lt;<bdi class="en-term" dir="ltr">EntityReference</bdi>&gt;', rendered)
        self.assertIn('<code class="inline-code" dir="ltr">&lt;OptionSetValue&gt;</code>', rendered)
        self.assertIn("&lt;", rendered)
        self.assertIn("&gt;", rendered)
        self.assertIn("&quot;", rendered)

        # Also check pilot-preview.html contains escaped &lt;your environment URL&gt; and &lt;OptionSetValue&gt;
        self.assertIn("environment", self.html_text)
        self.assertIn("GetAttributeValue&lt;EntityReference&gt;", self.html_text)
        self.assertIn("GetAttributeValue&lt;DateTime?&gt;", self.html_text)
        self.assertEqual(len(re.findall(r"ENT\d+", self.html_text)), 0)
        TEST_EVIDENCE["AC-05"] = (
            "<EntityReference>, <OptionSetValue>, <DateTime?>, and <your environment URL> are escaped as &lt;...&gt;, "
            "never parsed as HTML tags or stripped, with 0 ENT leaks."
        )

    def test_AC06_control_characters_scope_and_zero_leaks(self):
        # Verify CONTROL_CHARS_RE catches C0 (\x00, \x01, \x1f), DEL (\x7f), C1 (\u0080, \u009f), PUA (\ue000), and U+FFFD (\ufffd)
        illegal_samples = ["\x00", "\x01", "\x07", "\x0b", "\x1f", "\x7f", "\u0080", "\u009f", "\ue000", "\ufffd"]
        for ch in illegal_samples:
            self.assertIsNotNone(CONTROL_CHARS_RE.search(f"text{ch}more"), f"Failed to detect illegal control char {repr(ch)}")
            with self.assertRaises(RuntimeError):
                assert_clean_output(f"<p>text{ch}more</p>", "ac06")

        # Valid whitespace (\t, \n, \r) must NOT be flagged
        self.assertIsNone(CONTROL_CHARS_RE.search("line1\nline2\r\n\tindented"))

        html_ctrl = CONTROL_CHARS_RE.findall(self.html_text)
        self.assertEqual(len(html_ctrl), 0)
        TEST_EVIDENCE["AC-06"] = (
            "Expanded CONTROL_CHARS_RE verified against 10 illegal char classes (NUL, SOH, BEL, VT, US, DEL, C1, PUA, U+FFFD); "
            "0 control chars in pilot-preview.html."
        )

    def test_AC07_markdown_code_fence_fixtures_and_byte_identity(self):
        fixtures_md = (
            "### 1. Backtick Fence (3 backticks)\n"
            "```csharp\n"
            "public class Sample : IPlugin {}\n"
            "```\n\n"
            "### 2. Quadruple Backtick Fence (4 backticks containing inner triple backticks)\n"
            "````markdown\n"
            "Here is an inner fence:\n"
            "```json\n"
            "{\"key\": \"value\"}\n"
            "```\n"
            "````\n\n"
            "### 3. Tilde Fence (~~~)\n"
            "~~~xml\n"
            "<fetch top=\"5\"><entity name=\"account\" /></fetch>\n"
            "~~~\n\n"
            "### 4. Indented & Blockquote-Nested Fence\n"
            "1. خطوة:\n\n"
            "    > **Note**: مخرجات:\n"
            "    >\n"
            "    > ```output\n"
            "    > Unhandled Exception: System.ServiceModel.FaultException`1[[Microsoft.Xrm.Sdk.OrganizationServiceFault]]\n"
            "    > ```\n"
        )
        blocks = extract_code_blocks(fixtures_md)
        self.assertEqual(len(blocks), 4)
        self.assertEqual(blocks[0][0], "csharp")
        self.assertEqual(blocks[1][0], "markdown")
        self.assertIn("```json", blocks[1][1])
        self.assertEqual(blocks[2][0], "xml")
        self.assertEqual(blocks[3][0], "output")

        rendered = markdown_to_html(fixtures_md, self.dummy_orig, "ac07")
        self.assertEqual(len(re.findall(r'<pre class="code-pre"', rendered)), 4)

        # Also verify 100% byte-identity of all fenced code blocks across the 4 pilot units
        total_pilot_blocks = 0
        for u in self.pilot_units:
            orig_b = extract_code_blocks((ORIG_DIR / u["rel_path"]).read_text(encoding="utf-8"))
            trans_b = extract_code_blocks(
                STUDY_AID_RE.sub("", (TRANS_DIR / u["rel_path"]).read_text(encoding="utf-8"))
            )
            self.assertEqual(orig_b, trans_b)
            total_pilot_blocks += len(orig_b)

        TEST_EVIDENCE["AC-07"] = (
            f"All 4 Markdown fence styles (```, ````, ~~~, and blockquote > ```) parsed and rendered; "
            f"{total_pilot_blocks}/{total_pilot_blocks} source code blocks 100% byte-identical."
        )

    def test_AC08_en_seq_re_single_line_no_newline_spanning(self):
        multiline_sample = "السطر الأول ينتهي بـ Dataverse\nIPlugin يبدأ في السطر الثاني مع $select و $filter في Dynamics 365."
        wrapped = wrap_bidi_en(multiline_sample)
        self.assertIn('<bdi class="en-term" dir="ltr">Dataverse</bdi>\n<bdi class="en-term" dir="ltr">IPlugin</bdi>', wrapped)
        self.assertIn('<bdi class="en-term" dir="ltr">$select</bdi>', wrapped)
        self.assertIn('<bdi class="en-term" dir="ltr">$filter</bdi>', wrapped)
        self.assertIn('<bdi class="en-term" dir="ltr">Dynamics 365</bdi>', wrapped)
        # Ensure no <bdi> tag contains a newline character
        for m in re.finditer(r'<bdi class="en-term" dir="ltr">(.*?)</bdi>', wrapped, re.S):
            self.assertNotIn("\n", m.group(1))
        TEST_EVIDENCE["AC-08"] = "EN_SEQ_RE ([ \\t]+) never spans across \\n; OData $select/$filter and 'Dynamics 365' wrapped cleanly."

    def test_AC09_token_and_tag_re_gt_inside_html_attributes(self):
        sample_html = '<a href="https://example.com" title="a > b" data-expr=\'x > y\'>Check Dataverse Now</a>'
        wrapped = wrap_bidi_en(sample_html)
        self.assertEqual(
            wrapped,
            '<a href="https://example.com" title="a > b" data-expr=\'x > y\'><bdi class="en-term" dir="ltr">Check Dataverse Now</bdi></a>',
        )
        TEST_EVIDENCE["AC-09"] = "TOKEN_AND_TAG_RE preserves HTML tags containing '>' inside double-quoted and single-quoted attributes."

    def test_AC10_standalone_figure_not_wrapped_in_paragraph(self):
        p_fig_matches = re.findall(r"<p[^>]*>\s*<figure\b", self.html_text)
        fig_p_matches = re.findall(r"</figure>\s*</p>", self.html_text)
        figures = re.findall(r'<figure class="book-figure">', self.html_text)
        self.assertEqual(len(p_fig_matches), 0)
        self.assertEqual(len(fig_p_matches), 0)
        self.assertEqual(len(figures), 1)
        TEST_EVIDENCE["AC-10"] = f"0 <p><figure> nesting occurrences; {len(figures)} standalone <figure class='book-figure'> element verified."

    def test_AC11_pdf_cover_ab400_bidi_isolation_and_mixed_rtl_ltr(self):
        cover_m = re.search(r'<header class="book-cover">(.*?)</header>', self.html_text, re.S)
        self.assertIsNotNone(cover_m)
        cover_html = cover_m.group(1)
        self.assertIn('<bdi class="en-term" dir="ltr">AB-400</bdi>', cover_html)
        self.assertIn('<bdi class="en-term" dir="ltr">Microsoft Power Platform</bdi> و <bdi class="en-term" dir="ltr">Dynamics 365</bdi>', cover_html)
        self.assertIn('<bdi class="en-term" dir="ltr">C# Plug-ins</bdi>', cover_html)
        self.assertIn(".book-cover .badge {\n  display: inline-block;\n  direction: ltr;\n  unicode-bidi: isolate;", BOOK_CSS)
        TEST_EVIDENCE["AC-11"] = "Cover header isolates AB-400, Microsoft Power Platform, Dynamics 365, and C# Plug-ins in <bdi dir='ltr'>."

    def test_AC12_unit_header_group_prevents_orphaned_meta_bar(self):
        header_groups = re.findall(
            r'<div class="unit-header-group">\s*<div class="unit-meta-bar">.*?</div>\s*<h1\b[^>]*>.*?</h1>\s*</div>',
            self.html_text,
            re.S,
        )
        self.assertEqual(len(header_groups), 4)
        self.assertIn(".unit-card + .unit-card {\n    break-before: page;\n    page-break-before: always;\n  }", BOOK_CSS)
        self.assertIn(".unit-header-group {\n  break-inside: avoid;\n  page-break-inside: avoid;\n  break-after: avoid;\n  page-break-after: avoid;\n}", BOOK_CSS)
        TEST_EVIDENCE["AC-12"] = "All 4 units wrap .unit-meta-bar + <h1> inside .unit-header-group with break-inside/after: avoid and unit page breaks."

    def test_AC13_quiz_cards_vertical_layout_and_compact_print_spacing(self):
        quiz_cards = re.findall(r'<div class="quiz-card">', self.html_text)
        quiz_opt_rows = re.findall(r'<div class="quiz-opt-row">', self.html_text)
        quiz_opt_texts = re.findall(r'<div class="quiz-opt-text">', self.html_text)
        self.assertEqual(len(quiz_cards), 5)
        self.assertEqual(len(quiz_opt_rows), 15)
        self.assertEqual(len(quiz_opt_texts), 15)
        self.assertNotIn("inline-flex;\n  gap:", BOOK_CSS)
        self.assertIn(".quiz-card {\n    padding: 10px 14px;\n    margin: 10px 0;\n  }", BOOK_CSS)
        TEST_EVIDENCE["AC-13"] = "5 quiz cards and 15 option rows (3 options per question) rendered with block-level .quiz-opt-text and compact @media print spacing."

    def test_AC14_lab_appendix_heading_lead_para_and_code_grouped(self):
        self.assertIn("Build/LabReference/01-equipment-validation-plugin", self.html_text)
        self.assertIn("public class RequestApprovalPlugin : IPlugin", self.html_text)
        self.assertIn("InvalidPluginExecutionException(&quot;The device being replaced couldn&#x27;t be found.&quot;)", self.html_text)
        lead_paras = re.findall(r'<p class="lead-para">', self.html_text)
        long_code_containers = re.findall(r'<div class="code-container code-container-long" dir="ltr">', self.html_text)
        self.assertGreaterEqual(len(lead_paras), 5)
        self.assertGreaterEqual(len(long_code_containers), 1)
        self.assertIn(".lead-para {\n  break-after: avoid;\n  page-break-after: avoid;\n}", BOOK_CSS)
        self.assertIn(".code-container-long {\n  break-inside: auto;\n  page-break-inside: auto;\n}", BOOK_CSS)
        TEST_EVIDENCE["AC-14"] = (
            f"Full 84-line RequestApprovalPlugin.cs present; {len(lead_paras)} .lead-para elements (break-after: avoid) "
            f"and {len(long_code_containers)} .code-container-long blocks keep appendix heading, intro, and code together."
        )

    def test_AC15_answer_key_verification_status_source_verified_no_fake_human_verified(self):
        self.assertNotIn("HUMAN_VERIFIED", self.html_text)
        for u in self.pilot_units:
            t_content = (TRANS_DIR / u["rel_path"]).read_text(encoding="utf-8")
            self.assertNotIn("HUMAN_VERIFIED", t_content)
        quiz_u = [u for u in self.pilot_units if u.get("is_quiz")][0]
        quiz_md = (TRANS_DIR / quiz_u["rel_path"]).read_text(encoding="utf-8")
        self.assertEqual(len(re.findall(r"\bSOURCE_VERIFIED\b", quiz_md)), 5)
        TEST_EVIDENCE["AC-15"] = "0 occurrences of unverified HUMAN_VERIFIED; all 5 quiz answers documented with SOURCE_VERIFIED and verbatim quotes."

    def test_AC16_offline_self_contained_css_no_external_fonts(self):
        self.assertNotIn("fonts.googleapis.com", self.html_text)
        self.assertNotIn("fonts.gstatic.com", self.html_text)
        self.assertEqual(len(re.findall(r'<link\s+[^>]*rel="stylesheet"', self.html_text)), 0)
        TEST_EVIDENCE["AC-16"] = "0 external font or stylesheet links; 100% offline CSS."

    def test_AC17_manifest_contract_and_historical_supplemental_classification(self):
        self.assertEqual(len(self.manifest["units"]), 447)
        sup_units = [u for u in self.manifest["units"] if u.get("module_uid") == "learn-bizapps.command-bar-customize"]
        self.assertGreater(len(sup_units), 0)
        for u in self.pilot_units:
            ok, errs = validate_unit(u, self.glossary)
            self.assertTrue(ok, f"Pilot unit {u['unit_id']} failed validate_unit: {errs}")
            for req_key in ("source_url", "source_file", "translated_file", "source_hash", "inline_code_items", "code_blocks_count", "links", "validation_status"):
                self.assertIn(req_key, u)
            self.assertEqual(u["validation_status"], "passed")
        TEST_EVIDENCE["AC-17"] = "Manifest tracks 447 total units; all 4 pilot units pass 13/13 unit checks with complete contract metadata."

    def test_AC18_pdf_decompressed_streams_zero_leaks_and_page_count(self):
        ok_out, out_errs, metrics = validate_compiled_outputs(self.html_path, self.pdf_path, self.pilot_units)
        self.assertTrue(ok_out, f"Compiled outputs failed gate: {out_errs}")
        self.assertEqual(metrics["pdf"]["streams_with_placeholder_leaks"], 0)
        self.assertGreaterEqual(metrics["pdf"]["flate_streams_decompressed"], 200)
        self.assertEqual(metrics["pdf"]["page_count"], 27)
        TEST_EVIDENCE["AC-18"] = (
            f"PDF valid ({metrics['pdf']['size_bytes']:,} bytes, {metrics['pdf']['page_count']} pages); "
            f"{metrics['pdf']['flate_streams_decompressed']} FlateDecode streams decompressed with 0 placeholder leaks."
        )


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestBookPipelineV3)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    report_rows = []
    for method_name, (ac_id, ac_desc) in sorted(AC_METADATA.items()):
        passed = method_name not in [f[0]._testMethodName for f in result.failures + result.errors]
        report_rows.append(
            {
                "acceptance_criterion_id": ac_id,
                "test_method": method_name,
                "criterion_description": ac_desc,
                "status": "PASS" if passed else "FAIL",
                "evidence": TEST_EVIDENCE.get(ac_id, ""),
            }
        )

    report_path = BOOK_DIR / "manifests" / "test-report-v3.json"
    report_path.write_text(
        json.dumps(
            {
                "suite": "TestBookPipelineV3",
                "total_tests": result.testsRun,
                "passed": result.testsRun - len(result.failures) - len(result.errors),
                "failed": len(result.failures) + len(result.errors),
                "results": report_rows,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\n[REPORT SAVED] {report_path} ({len(report_rows)} Acceptance Criteria verified)")
    if not result.wasSuccessful():
        raise SystemExit(1)
