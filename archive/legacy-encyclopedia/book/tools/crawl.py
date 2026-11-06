import argparse
import hashlib
import io
import json
import os
import re
import stat
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

BOOK_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BOOK_DIR.parents[1]
CONFIG_DIR = BOOK_DIR / "config"
ORIG_DIR = BOOK_DIR / "original"
TRANS_DIR = BOOK_DIR / "translated"
ASSETS_DIR = BOOK_DIR / "assets"
LABS_CODE_DIR = BOOK_DIR / "labs-code"
MANIFEST_PATH = BOOK_DIR / "manifests" / "manifest.json"

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def fetch_bytes(url: str, timeout: int = 25, retries: int = 4) -> bytes:
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except Exception as exc:
            if attempt == retries - 1:
                raise RuntimeError(f"Failed to fetch {url} after {retries} attempts: {exc}") from exc
            time.sleep(1.5 * (attempt + 1))
    return b""


def fetch_text(url: str, timeout: int = 25, retries: int = 4) -> str:
    return fetch_bytes(url, timeout=timeout, retries=retries).decode("utf-8", errors="replace")


def slugify(text: str, max_len: int = 48) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", text.lower()).strip("-")
    return s[:max_len].strip("-") or "unit"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_readonly_utf8(path: Path, content: str) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
    normalized = content.replace("\r\n", "\n").replace("\r", "\n")
    raw_bytes = normalized.encode("utf-8")
    path.write_bytes(raw_bytes)
    os.chmod(path, stat.S_IREAD)
    return sha256_bytes(raw_bytes)


def split_code_blocks(md_text: str):
    """Split markdown into alternating [non_code, code_block, non_code, ...] segments."""
    pattern = re.compile(r"(^[ \t]*```[^\n]*\n.*?\n[ \t]*```[ \t]*$)", re.M | re.S)
    return pattern.split(md_text)


def normalize_markdown_and_assets(
    raw_text: str,
    unit_entry: dict,
    orig_file_path: Path,
    asset_folder: Path,
    github_media_map: dict | None = None,
) -> tuple[str, bool, list[str]]:
    text = raw_text.replace("\r\n", "\n").replace("\r", "\n")
    is_quiz = bool(unit_entry.get("is_quiz", False))

    # 1. Inspect and strip YAML frontmatter (\A---\n.*?\n---\n)
    fm_match = re.match(r"\A---\n(.*?)\n---\n[ \t\n]*", text, flags=re.S)
    if fm_match:
        fm_body = fm_match.group(1)
        if "unit_completion_type: quiz" in fm_body or "module_assessment: true" in fm_body:
            is_quiz = True
        text = text[fm_match.end() :]

    # 2. Strip MS Learn UI chrome right after # H1 ("Completed", "Completed 100 XP", "- 3 minutes")
    text = re.sub(
        r"(^#\s+[^\n]+\n+)[ \t]*(?:Completed(?:\s+\d+\s*XP)?[ \t]*\n+)?[ \t]*(?:-\s*\d+\s*minutes?[ \t]*\n+)?[ \t]*",
        r"\1\n",
        text,
        count=1,
        flags=re.I | re.M,
    )

    # 3. Ensure # H1 exists at the top
    if not re.search(r"^\s*#\s+", text, flags=re.M):
        title = unit_entry.get("title_en", "Unit")
        text = f"# {title}\n\n" + text

    # 4. Normalize Knowledge Check / Quiz units
    if is_quiz or re.search(r"^##\s+Check your knowledge\b", text, flags=re.I | re.M):
        is_quiz = True
        parts = re.split(r"(^##\s+Check your knowledge[ \t]*\n+)", text, maxsplit=1, flags=re.I | re.M)
        if len(parts) == 3:
            before, header, quiz_body = parts
            # Join standalone question numbers "1.\nQuestion text" -> "1. Question text"
            quiz_body = re.sub(r"^(\d+)\.[ \t]*\n+([^\n]+)", r"\1. \2", quiz_body, flags=re.M)
            lines = quiz_body.split("\n")
            out_lines = []
            in_q = False
            for line in lines:
                s = line.strip()
                if not s:
                    out_lines.append("")
                    continue
                if re.match(r"^\d+\.\s+\S+", s):
                    in_q = True
                    out_lines.append(s)
                elif s.startswith("#"):
                    in_q = False
                    out_lines.append(s)
                elif in_q and not s.startswith(("- ", "* ")):
                    out_lines.append(f"   - [ ] {s}")
                else:
                    out_lines.append(line)
            text = before + header + "\n".join(out_lines)

    # 5. Process non-code segments for lightbox unwrapping, image downloading, and relative URL resolution
    segments = split_code_blocks(text)
    downloaded_assets = []
    module_base_url = unit_entry.get("module_base_url", "")
    unit_page_url = unit_entry.get("page_url", "")

    for i in range(0, len(segments), 2):
        seg = segments[i]

        # 5a. Convert DocFX :::image::: if any exist
        def replace_docfx_img(m):
            block = m.group(0)
            src_m = re.search(r'source="([^"]+)"', block)
            alt_m = re.search(r'alt-text="([^"]*)"', block)
            if src_m:
                return f"![{alt_m.group(1) if alt_m else 'Diagram'}]({src_m.group(1)})"
            return block

        seg = re.sub(r":::image\b.*?:::", replace_docfx_img, seg, flags=re.I | re.S)

        # 5b. Unwrap nested lightbox image links [![alt](img)](img#lightbox) -> ![alt](img)
        seg = re.sub(
            r"\[!\[([^\]]*)\]\(([^\)]+)\)\]\(([^\)]*)\)",
            lambda m: f"![{m.group(1)}]({m.group(2)})"
            if ("#lightbox" in m.group(3) or m.group(2).split("?")[0] == m.group(3).split("#")[0].split("?")[0])
            else m.group(0),
            seg,
        )

        # 5c. Download images and rewrite src to exact relative path to book/assets/...
        def process_image(m):
            alt_text = m.group(1)
            raw_target = m.group(2).strip()
            # Strip optional title attribute: url "title"
            url_part = re.split(r'\s+["\']', raw_target, maxsplit=1)[0].strip()
            clean_name = Path(urllib.parse.unquote(url_part.split("?")[0].split("#")[0])).name
            if not clean_name:
                return m.group(0)

            asset_folder.mkdir(parents=True, exist_ok=True)
            local_img_path = asset_folder / clean_name

            if not local_img_path.exists():
                if github_media_map is not None and clean_name in github_media_map:
                    local_img_path.write_bytes(github_media_map[clean_name])
                else:
                    if url_part.startswith(("http://", "https://")):
                        img_url = url_part
                    elif module_base_url:
                        img_url = urllib.parse.urljoin(module_base_url, url_part)
                    else:
                        img_url = urllib.parse.urljoin(unit_page_url, url_part)
                    try:
                        img_bytes = fetch_bytes(img_url)
                        local_img_path.write_bytes(img_bytes)
                    except Exception as exc:
                        print(f"  [WARN] Could not download image {img_url}: {exc}")
                        return m.group(0)

            rel_asset = os.path.relpath(local_img_path, orig_file_path.parent).replace("\\", "/")
            downloaded_assets.append(str(local_img_path.relative_to(BOOK_DIR)).replace("\\", "/"))
            return f"![{alt_text}]({rel_asset})"

        seg = re.sub(r"!\[([^\]]*)\]\(([^\)]+)\)", process_image, seg)

        # 5d. Resolve relative hyperlinks [text](href) (not preceded by !)
        def process_link(m):
            prefix = m.group(1)
            link_text = m.group(2)
            href = m.group(3).strip()
            if href.startswith(("http://", "https://", "mailto:", "#")) or href.startswith("../"):
                if href.startswith("../") and unit_page_url and "learn.microsoft.com" in unit_page_url:
                    resolved = urllib.parse.urljoin(unit_page_url, href)
                    return f"{prefix}[{link_text}]({resolved})"
                return m.group(0)
            if href.startswith("/"):
                return f"{prefix}[{link_text}](https://learn.microsoft.com{href})"
            if unit_page_url and "learn.microsoft.com" in unit_page_url:
                resolved = urllib.parse.urljoin(unit_page_url, href)
                return f"{prefix}[{link_text}]({resolved})"
            return m.group(0)

        seg = re.sub(r"(^|[^!])\[([^\]]+)\]\(([^\)]+)\)", process_link, seg)
        segments[i] = seg

    final_md = "".join(segments).strip() + "\n"
    return final_md, is_quiz, downloaded_assets


def init_manifest() -> dict:
    print("=== Initializing Full Book Manifest (Catalog + 57 Module Hierarchies + GitHub Labs) ===")
    sources_cfg = json.loads((CONFIG_DIR / "sources.yaml").read_text(encoding="utf-8"))
    cat_raw = fetch_text("https://learn.microsoft.com/api/catalog/?type=learningPaths,modules&locale=en-us", timeout=35)
    catalog = json.loads(cat_raw)

    lp_by_url = {lp["url"].split("?")[0].rstrip("/").lower(): lp for lp in catalog.get("learningPaths", [])}
    mod_by_uid = {m["uid"]: m for m in catalog.get("modules", [])}

    # Collect all unique module UIDs needed across all volumes
    needed_mod_uids = set()
    for vol in sources_cfg["volumes"]:
        for src in vol["sources"]:
            if src["type"] == "learning_path":
                u_norm = src["url"].split("?")[0].rstrip("/").lower()
                lp = lp_by_url.get(u_norm)
                if not lp:
                    raise RuntimeError(f"Learning path not found in catalog: {src['url']}")
                for muid in lp.get("modules", []):
                    needed_mod_uids.add(muid)
                for extra_m in src.get("extra_modules", []):
                    needed_mod_uids.add(extra_m)

    print(f"Fetching hierarchies for {len(needed_mod_uids)} unique modules...")
    hierarchies = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {
            ex.submit(
                fetch_text, f"https://learn.microsoft.com/api/hierarchy/modules/{muid}?locale=en-us", 25
            ): muid
            for muid in needed_mod_uids
        }
        for f in as_completed(futs):
            muid = futs[f]
            hierarchies[muid] = json.loads(f.result())

    # Pre- register modules promoted to Volume 2 (like learn-bizapps.command-bar-customize)
    # so Volume 3 marks them as deduplicated if they appear again in Volume 3.
    seen_modules: dict[str, dict] = {}
    manifest_units: list[dict] = []
    manifest_modules: list[dict] = []

    pilot_selectors = sources_cfg.get("pilot_unit_selectors", [])

    # Also download and extract GitHub Labs ZIP once during init_manifest
    github_zip_url = "https://codeload.github.com/MicrosoftLearning/AB-400-microsoft-power-platform-developer/zip/refs/heads/main"
    print("Fetching & extracting official GitHub Labs repository ZIP...")
    zip_bytes = fetch_bytes(github_zip_url, timeout=45)
    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    lab_md_entries = []
    github_media_files = {}

    for zname in sorted(zf.namelist()):
        if zname.endswith("/"):
            continue
        rel_in_repo = "/".join(zname.split("/")[1:])
        if not rel_in_repo:
            continue
        if rel_in_repo.startswith(("Allfiles/", "Build/")):
            dest = LABS_CODE_DIR / rel_in_repo
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(zf.read(zname))
        elif rel_in_repo.startswith("Instructions/Labs/Media/"):
            fname = Path(rel_in_repo).name
            data = zf.read(zname)
            github_media_files[fname] = data
            dest_media = ASSETS_DIR / "v2" / "s12-labs" / fname
            dest_media.parent.mkdir(parents=True, exist_ok=True)
            dest_media.write_bytes(data)
        elif rel_in_repo.startswith("Instructions/Labs/") and rel_in_repo.endswith(".md"):
            lab_md_entries.append((Path(rel_in_repo).name, zf.read(zname).decode("utf-8", errors="replace")))
        elif rel_in_repo.lower() == "readme.md":
            lab_md_entries.insert(0, ("00-readme.md", zf.read(zname).decode("utf-8", errors="replace")))

    for vol in sources_cfg["volumes"]:
        vol_id = vol["id"]
        for src in vol["sources"]:
            src_id = src["id"]
            stype = src["type"]

            if stype == "single_page":
                unit_id = f"{vol_id}-{src_id}-m01-u01"
                rel_path = f"{vol_id}/{src_id}/m01/01-study-guide.md"
                manifest_modules.append(
                    {
                        "module_id": f"{vol_id}-{src_id}-m01",
                        "uid": "exam.ab-400.study-guide",
                        "volume_id": vol_id,
                        "source_id": src_id,
                        "title_en": src["title_en"],
                        "title_ar": src["title_ar"],
                        "is_duplicate": False,
                    }
                )
                manifest_units.append(
                    {
                        "unit_id": unit_id,
                        "uid": "exam.ab-400.study-guide.unit",
                        "volume_id": vol_id,
                        "source_id": src_id,
                        "module_id": f"{vol_id}-{src_id}-m01",
                        "module_uid": "exam.ab-400.study-guide",
                        "unit_index": 1,
                        "title_en": src["title_en"],
                        "page_url": src["url"],
                        "fetch_url": f"{src['url']}?accept=text/markdown",
                        "module_base_url": src["url"].rstrip("/") + "/",
                        "rel_path": rel_path,
                        "asset_folder": f"{vol_id}/{src_id}-m01",
                        "is_quiz": False,
                        "is_pilot": False,
                        "pilot_id": None,
                        "status": "pending",
                        "sha256": None,
                    }
                )

            elif stype == "learning_path":
                u_norm = src["url"].split("?")[0].rstrip("/").lower()
                lp = lp_by_url[u_norm]
                mod_uids = list(lp.get("modules", [])) + list(src.get("extra_modules", []))
                for m_idx, muid in enumerate(mod_uids, 1):
                    mod_code = f"m{m_idx:02d}"
                    mod_full_id = f"{vol_id}-{src_id}-{mod_code}"
                    m_meta = mod_by_uid.get(muid, {})
                    m_title = m_meta.get("title") or hierarchies.get(muid, {}).get("title") or muid
                    m_url = m_meta.get("url", "").split("?")[0].rstrip("/") + "/"

                    if muid in seen_modules:
                        first_ref = seen_modules[muid]
                        manifest_modules.append(
                            {
                                "module_id": mod_full_id,
                                "uid": muid,
                                "volume_id": vol_id,
                                "source_id": src_id,
                                "title_en": m_title,
                                "is_duplicate": True,
                                "duplicate_of": first_ref["module_id"],
                                "duplicate_of_title": first_ref["title_en"],
                            }
                        )
                        continue

                    seen_modules[muid] = {"module_id": mod_full_id, "title_en": m_title, "volume_id": vol_id}
                    manifest_modules.append(
                        {
                            "module_id": mod_full_id,
                            "uid": muid,
                            "volume_id": vol_id,
                            "source_id": src_id,
                            "title_en": m_title,
                            "is_duplicate": False,
                        }
                    )

                    h_units = hierarchies.get(muid, {}).get("units", [])
                    for u_idx, u_obj in enumerate(h_units, 1):
                        u_url = u_obj.get("url", "")
                        page_url = f"https://learn.microsoft.com{u_url}" if u_url.startswith("/") else u_url
                        u_slug = u_url.rstrip("/").split("/")[-1] if u_url else slugify(u_obj.get("title", "unit"))
                        # strip leading number if already present in slug
                        u_slug_clean = re.sub(r"^\d+-", "", u_slug)
                        rel_path = f"{vol_id}/{src_id}/{mod_code}/{u_idx:02d}-{u_slug_clean}.md"
                        unit_id = f"{mod_full_id}-u{u_idx:02d}"

                        # Check if this unit matches a pilot selector
                        pilot_id = None
                        for ps in pilot_selectors:
                            if ps.get("module_uid") == muid and ps.get("unit_index") == u_idx:
                                pilot_id = ps["pilot_id"]
                                break

                        is_quiz_guess = "knowledge-check" in u_slug or "assessment" in u_obj.get("title", "").lower()
                        manifest_units.append(
                            {
                                "unit_id": unit_id,
                                "uid": u_obj.get("uid", unit_id),
                                "volume_id": vol_id,
                                "source_id": src_id,
                                "module_id": mod_full_id,
                                "module_uid": muid,
                                "unit_index": u_idx,
                                "title_en": u_obj.get("title", f"Unit {u_idx}"),
                                "page_url": page_url,
                                "fetch_url": f"{page_url}?accept=text/markdown",
                                "module_base_url": m_url,
                                "rel_path": rel_path,
                                "asset_folder": f"{vol_id}/{src_id}-{mod_code}",
                                "is_quiz": is_quiz_guess,
                                "is_pilot": pilot_id is not None,
                                "pilot_id": pilot_id,
                                "status": "pending",
                                "sha256": None,
                            }
                        )

            elif stype == "github_labs":
                mod_full_id = f"{vol_id}-{src_id}-labs"
                manifest_modules.append(
                    {
                        "module_id": mod_full_id,
                        "uid": "github.ab-400.labs",
                        "volume_id": vol_id,
                        "source_id": src_id,
                        "title_en": src["title_en"],
                        "title_ar": src["title_ar"],
                        "is_duplicate": False,
                    }
                )
                for l_idx, (lab_fname, lab_raw_md) in enumerate(lab_md_entries, 1):
                    unit_id = f"{mod_full_id}-u{l_idx:02d}"
                    rel_path = f"{vol_id}/{src_id}-labs/{lab_fname}"
                    pilot_id = None
                    lab_ref_dir = None
                    for ps in pilot_selectors:
                        if ps.get("lab_file") == lab_fname:
                            pilot_id = ps["pilot_id"]
                            lab_ref_dir = ps.get("lab_ref_dir")
                            break
                    if not lab_ref_dir:
                        m_num = re.match(r"^0([1-9])-", lab_fname)
                        if m_num:
                            lab_ref_dir = f"Build/LabReference/Lab0{m_num.group(1)}"

                    # Extract title from YAML frontmatter or H1
                    title_m = re.search(r"title:\s*['\"]([^'\"]+)['\"]", lab_raw_md) or re.search(
                        r"^#\s+(.+)$", lab_raw_md, flags=re.M
                    )
                    lab_title = title_m.group(1).strip() if title_m else lab_fname

                    # Save normalized lab markdown immediately since we already have the ZIP in memory!
                    orig_file_path = ORIG_DIR / rel_path
                    asset_folder = ASSETS_DIR / vol_id / f"{src_id}-labs"
                    norm_md, _, dl_assets = normalize_markdown_and_assets(
                        lab_raw_md,
                        {
                            "title_en": lab_title,
                            "is_quiz": False,
                            "module_base_url": "",
                            "page_url": "https://github.com/MicrosoftLearning/AB-400-microsoft-power-platform-developer/blob/main/Instructions/Labs/"
                            + lab_fname,
                        },
                        orig_file_path,
                        asset_folder,
                        github_media_map=github_media_files,
                    )
                    file_hash = write_readonly_utf8(orig_file_path, norm_md)

                    manifest_units.append(
                        {
                            "unit_id": unit_id,
                            "uid": f"github.ab-400.labs.{lab_fname}",
                            "volume_id": vol_id,
                            "source_id": src_id,
                            "module_id": mod_full_id,
                            "module_uid": "github.ab-400.labs",
                            "unit_index": l_idx,
                            "title_en": lab_title,
                            "page_url": "https://github.com/MicrosoftLearning/AB-400-microsoft-power-platform-developer/blob/main/Instructions/Labs/"
                            + lab_fname,
                            "fetch_url": "github_zip",
                            "module_base_url": "",
                            "rel_path": rel_path,
                            "asset_folder": f"{vol_id}/{src_id}-labs",
                            "lab_ref_dir": lab_ref_dir,
                            "is_quiz": False,
                            "is_lab": True,
                            "is_pilot": pilot_id is not None,
                            "pilot_id": pilot_id,
                            "status": "crawled",
                            "sha256": file_hash,
                            "assets": dl_assets,
                        }
                    )

    manifest_data = {
        "phase": "pilot",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "stats": {
            "total_modules": len(manifest_modules),
            "unique_modules": sum(1 for m in manifest_modules if not m.get("is_duplicate")),
            "duplicate_modules": sum(1 for m in manifest_modules if m.get("is_duplicate")),
            "total_units": len(manifest_units),
            "pilot_units": sum(1 for u in manifest_units if u.get("is_pilot")),
        },
        "modules": manifest_modules,
        "units": manifest_units,
    }
    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(json.dumps(manifest_data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Manifest initialized at {MANIFEST_PATH}: {manifest_data['stats']}")
    return manifest_data


def crawl_selected_units(manifest: dict, filter_fn) -> None:
    targets = [u for u in manifest["units"] if filter_fn(u) and u.get("fetch_url") != "github_zip"]
    print(f"Crawling {len(targets)} Microsoft Learn units...")

    def process_one(unit: dict):
        raw_md = fetch_text(unit["fetch_url"], timeout=25)
        orig_path = ORIG_DIR / unit["rel_path"]
        asset_folder = ASSETS_DIR / unit["asset_folder"]
        norm_md, is_quiz, dl_assets = normalize_markdown_and_assets(raw_md, unit, orig_path, asset_folder)
        fhash = write_readonly_utf8(orig_path, norm_md)
        unit["is_quiz"] = is_quiz
        unit["sha256"] = fhash
        unit["assets"] = dl_assets
        if unit.get("status") == "pending":
            unit["status"] = "crawled"
        return unit["unit_id"], len(norm_md), len(dl_assets)

    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = {ex.submit(process_one, u): u for u in targets}
        for f in as_completed(futs):
            u = futs[f]
            uid, char_len, asset_cnt = f.result()
            print(f"  [OK] {uid} ({u['rel_path']}): {char_len} chars, {asset_cnt} assets")

    MANIFEST_PATH.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Crawl Microsoft Learn & GitHub Labs sources.")
    parser.add_argument("--init-manifest", action="store_true", help="Initialize book/manifests/manifest.json")
    parser.add_argument("--pilot", action="store_true", help="Crawl the 4 pilot units")
    parser.add_argument("--volume", type=str, help="Crawl a specific volume (v1, v2, v3)")
    parser.add_argument("--unit", type=str, help="Crawl a specific unit_id or pilot_id")
    parser.add_argument("--all", action="store_true", help="Crawl all units across all volumes")
    args = parser.parse_args()

    if args.init_manifest or not MANIFEST_PATH.exists():
        manifest = init_manifest()
    else:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    if args.pilot:
        crawl_selected_units(manifest, lambda u: u.get("is_pilot") is True)
    if args.volume:
        crawl_selected_units(manifest, lambda u: u.get("volume_id") == args.volume)
    if args.unit:
        crawl_selected_units(manifest, lambda u: u.get("unit_id") == args.unit or u.get("pilot_id") == args.unit)
    if args.all:
        crawl_selected_units(manifest, lambda u: True)


if __name__ == "__main__":
    main()
