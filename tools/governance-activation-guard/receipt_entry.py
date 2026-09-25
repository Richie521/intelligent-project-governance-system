from __future__ import annotations

import argparse
import base64
import json
import sys

from governance_guard import GateStore, default_state_dir, record_receipt


def _decode_payload(value: str) -> dict:
    padding = "=" * (-len(value) % 4)
    raw = base64.urlsafe_b64decode((value + padding).encode("ascii"))
    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("Receipt payload must be a JSON object.")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Record a governance receipt outside the user-visible reply."
    )
    parser.add_argument("--kind", choices=("diagnosis", "completion"), required=True)
    parser.add_argument("--payload-base64", required=True)
    args = parser.parse_args()
    try:
        receipt = _decode_payload(args.payload_base64)
        result = record_receipt(
            args.kind, receipt, GateStore(default_state_dir())
        )
        json.dump(result, sys.stdout, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0
    except Exception as exc:
        print(f"治理门禁带外回执失败：{exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
