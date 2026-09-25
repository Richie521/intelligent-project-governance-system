from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from governance_transaction import (
    DEFAULT_MANIFEST,
    GovernanceTransactionError,
    apply_transaction,
    benchmark_receipts,
    exception_result,
    manifest_report,
    recover_transactions,
)


if hasattr(sys.stdin, "reconfigure"):
    sys.stdin.reconfigure(encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deterministic governance transaction runner")
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--state-root", type=Path)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate-manifest")
    validate.add_argument("--metadata-only", action="store_true")
    subparsers.add_parser("apply").add_argument("--request-stdin", action="store_true", required=True)
    subparsers.add_parser("recover")
    subparsers.add_parser("benchmark")
    return parser


def main() -> int:
    args = _parser().parse_args()
    project_root = args.project_root.resolve()
    try:
        if args.command == "validate-manifest":
            result = manifest_report(
                project_root, args.manifest, full_hash=not args.metadata_only
            )
        elif args.command == "apply":
            try:
                request = json.load(sys.stdin)
            except json.JSONDecodeError as exc:
                raise GovernanceTransactionError(
                    "invalid_json", f"Invalid request JSON: {exc.msg} at line {exc.lineno}"
                ) from exc
            if not isinstance(request, dict):
                raise GovernanceTransactionError("invalid_json", "Request root must be an object.")
            result = apply_transaction(
                project_root,
                request,
                manifest_relative=args.manifest,
                state_root=args.state_root,
            )
        elif args.command == "recover":
            result = recover_transactions(project_root, state_root=args.state_root)
        else:
            result = benchmark_receipts(project_root, state_root=args.state_root)
    except GovernanceTransactionError as exc:
        result = exception_result(exc)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("status") in {"applied", "no_change"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
