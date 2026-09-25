from __future__ import annotations

import json
import sys

from governance_guard import GateStore, default_state_dir, handle_event


if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def main() -> int:
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict):
            raise ValueError("Hook input must be a JSON object.")
        output = handle_event(event, GateStore(default_state_dir()))
        if output:
            json.dump(output, sys.stdout, ensure_ascii=False)
            sys.stdout.write("\n")
        return 0
    except Exception as exc:
        print(f"治理激活门禁异常，已按失败关闭处理：{exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
