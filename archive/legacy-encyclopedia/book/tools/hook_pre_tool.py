import json
import sys
from pathlib import Path

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parents[2]
ORIG_DIR = (ROOT_DIR / "book" / "original").resolve()


def main():
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        print(json.dumps({"decision": "allow"}))
        return

    tool_input = payload.get("tool_input") or payload.get("toolInput") or {}
    target_str = (
        tool_input.get("Path")
        or tool_input.get("TargetFile")
        or tool_input.get("file_path")
        or tool_input.get("path")
        or ""
    )
    if target_str:
        try:
            target_path = Path(target_str).resolve()
            if ORIG_DIR in target_path.parents and target_path.exists():
                print(
                    json.dumps(
                        {
                            "decision": "block",
                            "reason": f"Immutable original file protection: {target_path} already exists in book/original/. Write translations to book/translated/ instead.",
                        }
                    )
                )
                return
        except Exception:
            pass

    print(json.dumps({"decision": "allow"}))


if __name__ == "__main__":
    main()
