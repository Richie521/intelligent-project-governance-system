#!/usr/bin/env python3
"""Reflow Markdown prose without touching structural blocks.

The governance documents use physical lines as a readable surface.  This
utility removes accidental hard wraps from ordinary paragraphs and list-item
continuations while preserving Markdown structures that may depend on exact
line boundaries: front matter, fenced code, display math, tables, headings,
block quotes, nested lists, and explicit hard-break markers.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence


FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
LIST_RE = re.compile(r"^(?P<indent>\s*)(?P<marker>(?:[-+*]|\d+[.)]))(?P<gap>\s+)(?P<body>.*)$")
HEADING_RE = re.compile(r"^\s{0,3}#{1,6}(?:\s|$)")
BLOCKQUOTE_RE = re.compile(r"^\s{0,3}>")
TABLE_RE = re.compile(r"^\s*\|")
HTML_RE = re.compile(r"^\s*</?[A-Za-z][^>]*>\s*$")
EXCLUDED_DIRS = {".git", "node_modules", "history", "历史", "backups", "备份"}


@dataclass(frozen=True)
class FileText:
    text: str
    newline: str
    had_final_newline: bool
    bom: bool


@dataclass(frozen=True)
class ReflowResult:
    text: str
    joins: int


def read_file(path: Path) -> FileText:
    raw = path.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    if bom:
        raw = raw[3:]
    text = raw.decode("utf-8")
    newline = "\r\n" if "\r\n" in text else "\r" if "\r" in text else "\n"
    return FileText(text, newline, text.endswith(("\n", "\r")), bom)


def render_file(file_text: FileText, lines: Sequence[str]) -> str:
    result = file_text.newline.join(lines)
    if file_text.had_final_newline:
        result += file_text.newline
    if file_text.bom:
        return "\ufeff" + result
    return result


def is_fence(line: str) -> bool:
    return bool(FENCE_RE.match(line))


def fence_token(line: str) -> str | None:
    match = FENCE_RE.match(line)
    return match.group(1)[0] if match else None


def is_math_delimiter(line: str) -> bool:
    stripped = line.strip()
    return (
        stripped.startswith((r"\[", r"\]", "$$"))
        or stripped.startswith(r"\begin{")
        or stripped.startswith(r"\end{")
    )


def is_structural(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if is_fence(line) or is_math_delimiter(line):
        return True
    if HEADING_RE.match(line) or BLOCKQUOTE_RE.match(line):
        return True
    if TABLE_RE.match(line) or HTML_RE.match(line) or stripped.startswith("<!--"):
        return True
    if LIST_RE.match(line):
        return True
    if stripped == "---":
        return True
    return False


def is_list_item(line: str) -> bool:
    return bool(LIST_RE.match(line))


def indentation(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def has_explicit_hard_break(line: str) -> bool:
    stripped = line.rstrip("\r\n")
    return stripped.endswith("\\") or stripped.endswith("  ")


def is_cjk(character: str) -> bool:
    return bool(character) and "\u3400" <= character <= "\u9fff"


def join_separator(left: str, right: str) -> str:
    if not left or not right:
        return ""
    left_char = left[-1]
    right_char = right[0]
    if is_cjk(left_char) and is_cjk(right_char):
        return ""
    if left_char in "([{\u3010\u300a\u201c\u2018\u3002\uff0c\uff01\uff1f\uff1b\uff1a\u3001" or right_char in ".,!?;:)]}\u3002\uff0c\uff01\uff1f\uff1b\uff1a\u3001\u300d\u300b\u201d\u2019":
        return ""
    return " "


def join_lines(left: str, right: str) -> str:
    left_clean = left.rstrip()
    right_clean = right.strip()
    return left_clean + join_separator(left_clean, right_clean) + right_clean


def reflow_text(text: str) -> ReflowResult:
    lines = text.splitlines()
    output: list[str] = []
    joins = 0
    in_front_matter = bool(lines and lines[0].strip() == "---")
    fence_char: str | None = None
    in_math = False
    in_html_comment = False
    index = 0

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if in_front_matter:
            output.append(line)
            if index > 0 and stripped == "---":
                in_front_matter = False
            index += 1
            continue

        if in_html_comment:
            output.append(line)
            if "-->" in line:
                in_html_comment = False
            index += 1
            continue

        if stripped.startswith("<!--"):
            output.append(line)
            if "-->" not in line:
                in_html_comment = True
            index += 1
            continue

        if fence_char is not None:
            output.append(line)
            if is_fence(line) and fence_token(line) == fence_char:
                fence_char = None
            index += 1
            continue

        if is_fence(line):
            output.append(line)
            fence_char = fence_token(line)
            index += 1
            continue

        if in_math:
            output.append(line)
            if stripped.startswith((r"\]", "$$")) or stripped.startswith(r"\end{"):
                in_math = False
            index += 1
            continue

        if is_math_delimiter(line):
            output.append(line)
            if stripped.startswith((r"\[", "$$")) or stripped.startswith(r"\begin{"):
                in_math = not (stripped.startswith(r"\]") or stripped.startswith(r"\end{"))
            index += 1
            continue

        if not stripped or (is_structural(line) and not is_list_item(line)):
            output.append(line)
            index += 1
            continue

        if has_explicit_hard_break(line):
            output.append(line)
            index += 1
            continue

        if is_list_item(line):
            merged = line.rstrip()
            next_index = index + 1
            while next_index < len(lines):
                continuation = lines[next_index]
                if not continuation.strip():
                    break
                if is_structural(continuation):
                    break
                if indentation(continuation) >= 4:
                    break
                if has_explicit_hard_break(merged) or has_explicit_hard_break(continuation):
                    break
                merged = join_lines(merged, continuation)
                joins += 1
                next_index += 1
            output.append(merged)
            index = next_index
            continue

        merged = line.strip()
        next_index = index + 1
        while next_index < len(lines):
            continuation = lines[next_index]
            if not continuation.strip():
                break
            if is_structural(continuation) or indentation(continuation) > 0:
                break
            if has_explicit_hard_break(merged) or has_explicit_hard_break(continuation):
                break
            merged = join_lines(merged, continuation)
            joins += 1
            next_index += 1
        output.append(merged)
        index = next_index

    return ReflowResult("\n".join(output), joins)


def transformed_file(path: Path) -> tuple[str, ReflowResult]:
    original = read_file(path)
    result = reflow_text(original.text)
    return render_file(original, result.text.splitlines()), result


def iter_markdown(paths: Iterable[Path]) -> Iterator[Path]:
    seen: set[Path] = set()
    for raw_path in paths:
        path = raw_path.resolve()
        if path.is_file() and path.suffix.lower() == ".md":
            if any(part in EXCLUDED_DIRS for part in path.parts):
                continue
            if path not in seen:
                seen.add(path)
                yield path
            continue
        if not path.is_dir():
            continue
        for child in path.rglob("*.md"):
            if any(part in EXCLUDED_DIRS for part in child.parts):
                continue
            if child not in seen:
                seen.add(child)
                yield child


def manifest_paths(path: Path) -> Iterator[Path]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        for row in csv.DictReader(handle):
            original = row.get("Original")
            if original:
                yield Path(original)


def project_root_paths(root: Path) -> Iterator[Path]:
    entry = root / "AGENTS.md"
    if entry.is_file():
        yield entry
    docs = root / "docs"
    if docs.is_dir():
        # Governance material may be routed through nested current-docs
        # directories (for example monthly logs or a focused topic area).
        # Keep historical and backup trees out of the default project probe;
        # they are evidence, not current authority.
        yield from docs.rglob("*.md")


def collect_paths(
    path_args: Sequence[str], manifest: str | None, project_roots: Sequence[str]
) -> list[Path]:
    paths: list[Path] = []
    if manifest:
        paths.extend(manifest_paths(Path(manifest)))
    paths.extend(Path(value) for value in path_args)
    for root in project_roots:
        paths.extend(project_root_paths(Path(root)))
    return list(iter_markdown(paths))


def run_check(paths: Sequence[Path]) -> int:
    failures = 0
    for path in paths:
        try:
            rendered, result = transformed_file(path)
            original = read_file(path)
        except (OSError, UnicodeError) as exc:
            print(f"ERROR {path}: {exc}", file=sys.stderr)
            failures += 1
            continue
        if result.joins:
            print(f"{path}: {result.joins} semantic line join(s) needed")
            failures += 1
        if rendered != render_file(original, original.text.splitlines()):
            failures += 0
    return 1 if failures else 0


def run_reflow(paths: Sequence[Path]) -> int:
    changed = 0
    joins = 0
    for path in paths:
        try:
            original = read_file(path)
            result = reflow_text(original.text)
            rendered = render_file(original, result.text.splitlines())
        except (OSError, UnicodeError) as exc:
            print(f"ERROR {path}: {exc}", file=sys.stderr)
            return 1
        if rendered != render_file(original, original.text.splitlines()):
            path.write_bytes(rendered.encode("utf-8"))
            changed += 1
            joins += result.joins
            print(f"UPDATED {path} ({result.joins} join(s))")
    print(f"UPDATED_FILES={changed} JOINS={joins}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name in ("check", "reflow"):
        sub = subparsers.add_parser(name)
        sub.add_argument("paths", nargs="*", help="Markdown files or directories")
        sub.add_argument("--manifest", help="CSV manifest with an Original column")
        sub.add_argument(
            "--project-root",
            action="append",
            default=[],
            help="Select AGENTS.md and current Markdown below docs/ (history and backup directories are excluded)",
        )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    paths = collect_paths(args.paths, args.manifest, args.project_root)
    if not paths:
        print("No Markdown files selected", file=sys.stderr)
        return 2
    return run_check(paths) if args.command == "check" else run_reflow(paths)


if __name__ == "__main__":
    raise SystemExit(main())
