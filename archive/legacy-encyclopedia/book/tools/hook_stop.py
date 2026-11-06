import json
import sys
from pathlib import Path

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parents[2]
BOOK_DIR = ROOT_DIR / "book"
MANIFEST_PATH = BOOK_DIR / "manifests" / "manifest.json"


def main():
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        print(json.dumps({"decision": "allow"}))
        return

    # Never block user cancellations or error terminations
    term_reason = payload.get("terminationReason", "NO_TOOL_CALL")
    if term_reason != "NO_TOOL_CALL":
        print(json.dumps({"decision": "allow"}))
        return

    if not MANIFEST_PATH.exists():
        print(json.dumps({"decision": "allow"}))
        return

    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        phase = manifest.get("phase", "pilot")
        if phase == "pilot":
            pilot_units = [u for u in manifest.get("units", []) if u.get("is_pilot")]
            not_validated = [u["unit_id"] for u in pilot_units if u.get("status") != "validated"]
            html_ok = (BOOK_DIR / "pilot-preview.html").exists()
            pdf_ok = (BOOK_DIR / "pilot-preview.pdf").exists()
            if not_validated or not html_ok or not pdf_ok:
                print(
                    json.dumps(
                        {
                            "decision": "block",
                            "reason": f"Pilot phase incomplete: unvalidated pilot units={not_validated}, pilot-preview.html={html_ok}, pilot-preview.pdf={pdf_ok}. Finish Pilot validation and build before stopping.",
                        }
                    )
                )
                return
    except Exception:
        pass

    print(json.dumps({"decision": "allow"}))


if __name__ == "__main__":
    main()
