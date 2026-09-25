from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
OPEN_STATUSES = {"pending", "repair_authorized"}
LEGACY_AUTOMATIC_CATEGORIES = {"activation_failure", "repeated_correction"}
DIAGNOSIS_LAYERS = ("current_task", "project_mechanism", "global_or_tooling")
LAYER_STATUSES = {"primary", "contributing", "ruled_out", "not_examined"}


class GuardStateError(RuntimeError):
    pass


@dataclass(frozen=True)
class PromptClassification:
    trigger: bool
    category: str = "none"
    reason: str = ""


@dataclass(frozen=True)
class ToolDecision:
    allowed: bool
    reason: str


def _now() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def classify_prompt(prompt: str) -> PromptClassification:
    """Open the gate only for a dedicated, user-issued manual command line."""
    command = re.compile(
        r"(?:请)?(?:现在|立即|先)?(?:人工)?"
        r"(?:启动|进入|执行|触发)(?:分层诊断|治理诊断|治理模式|治理门禁)"
        r"(?:[：:,，]\s*\S.*)?[。！？!?]?"
    )
    in_fence = False
    for raw_line in prompt.splitlines():
        line = raw_line.strip()
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and command.fullmatch(line):
            return PromptClassification(
                True,
                "governance_instruction",
                "The user issued a dedicated manual governance command.",
            )
    return PromptClassification(False)


class GateStore:
    def __init__(self, root: Path):
        self.root = Path(root)

    def path_for(self, session_id: str) -> Path:
        safe_name = _sha256(session_id)[:32]
        return self.root / f"{safe_name}.json"

    def load(self, session_id: str) -> dict[str, Any] | None:
        path = self.path_for(session_id)
        if not path.exists():
            return None
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise GuardStateError(f"Cannot read governance gate state: {exc}") from exc
        self._validate(state, session_id)
        return state

    def find_by_gate_id(self, gate_id: str) -> dict[str, Any]:
        matches: list[dict[str, Any]] = []
        if self.root.exists():
            for path in self.root.glob("*.json"):
                try:
                    state = json.loads(path.read_text(encoding="utf-8"))
                    self._validate(state, state.get("session_id", ""))
                except (OSError, json.JSONDecodeError, GuardStateError):
                    continue
                if state.get("gate_id") == gate_id:
                    matches.append(state)
        if len(matches) != 1:
            raise GuardStateError(
                f"Expected one governance gate for {gate_id}, found {len(matches)}."
            )
        return matches[0]

    def save(self, state: dict[str, Any]) -> None:
        self._validate(state, state.get("session_id", ""))
        self.root.mkdir(parents=True, exist_ok=True)
        target = self.path_for(state["session_id"])
        fd, temp_name = tempfile.mkstemp(
            prefix=target.stem + "-", suffix=".tmp", dir=self.root
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                json.dump(state, handle, ensure_ascii=False, indent=2, sort_keys=True)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temp_name, target)
        finally:
            if os.path.exists(temp_name):
                os.unlink(temp_name)

    @staticmethod
    def _validate(state: Any, session_id: str) -> None:
        if not isinstance(state, dict):
            raise GuardStateError("Governance gate state is not an object.")
        required = {
            "schema_version",
            "gate_id",
            "session_id",
            "status",
            "category",
            "prompt_sha256",
            "triggered_at",
            "updated_at",
        }
        missing = required.difference(state)
        if missing:
            raise GuardStateError(f"Governance gate state is missing: {sorted(missing)}")
        if state["schema_version"] != SCHEMA_VERSION:
            raise GuardStateError("Unsupported governance gate state version.")
        if not session_id or state["session_id"] != session_id:
            raise GuardStateError("Governance gate session mismatch.")
        if state["status"] not in {
            "pending",
            "repair_authorized",
            "completed",
            "blocked",
            "bypassed",
        }:
            raise GuardStateError("Unknown governance gate status.")
        if not re.fullmatch(r"[0-9a-f]{64}", state["prompt_sha256"]):
            raise GuardStateError("Invalid prompt hash in governance gate state.")


def default_state_dir() -> Path:
    override = os.environ.get("GOVERNANCE_GUARD_STATE_DIR")
    if override:
        return Path(override)
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "OpenAI" / "Codex" / "governance-activation-guard"
    return Path.home() / ".codex" / "governance-activation-guard"


def _new_state(event: dict[str, Any], classification: PromptClassification) -> dict[str, Any]:
    prompt = event.get("prompt", "")
    timestamp = _now()
    return {
        "schema_version": SCHEMA_VERSION,
        "gate_id": f"gov-{uuid.uuid4().hex[:12]}",
        "session_id": event["session_id"],
        "turn_id": event.get("turn_id"),
        "status": "pending",
        "category": classification.category,
        "prompt_sha256": _sha256(prompt),
        "triggered_at": timestamp,
        "updated_at": timestamp,
    }


def _context_for(state: dict[str, Any]) -> str:
    gate_id = state["gate_id"]
    if state["status"] == "blocked":
        return (
            f"[治理激活门禁 {gate_id}] 上次治理工作已以 blocked 结束，未完成修复验收。"
            "失败记录保留；不得称为完成或自动继续原修复。后续工作依据用户当前指令。"
        )
    if state["status"] == "pending":
        return (
            f"[治理激活门禁 {gate_id}] 用户已人工触发分层诊断，立即暂停业务写入。"
            "只读重建失败序列，按当前任务、项目机制、全局规则或 Skill/工具的顺序检查；"
            "在首个足以解释问题的层级停止，只选一个主要根因。非责任层只记录排除或停止理由，"
            "不得逐层给修复建议；只有证据证明共同作用时才标记贡献层。"
            "明确失败机制、复发条件、防复发方案、当前计划影响、写回候选、证据、修复范围和继续或停止决定。"
            "不得把机器回执写进用户正文。诊断完成后，调用安装目录中的 receipt_entry.py，"
            "使用 --kind diagnosis 和 --payload-base64 记录带外回执。回执必须包含 gate_id、"
            "failure_sequence、layer_responsibility（含 primary_layer、inspection_stop 以及"
            " current_task、project_mechanism、global_or_tooling 的 status 和 finding）、"
            "failure_mechanism、recurrence_condition、prevention_plan、"
            "plan_impact、writeback_candidates、decision、repair_scope 和 evidence。"
            "每层 status 只能是 primary、contributing、ruled_out 或 not_examined；恰好一个 primary。"
            "contributing 还必须说明 causal_connection。prevention_plan 必须包含 repair_layer、"
            "durable_change、recurrence_barrier 和 regression_probe，且 repair_layer 必须等于 primary_layer。"
            "门禁授权修复前不得执行写入。"
        )
    return (
        f"[治理激活门禁 {gate_id}] 分层诊断已通过，只能继续已限定的修复。"
        f"修复范围约定：{state.get('repair_scope', '以诊断回执为准')}。"
        "repair_scope 是智能体遵守并在验收时核对的范围约定，不是机器强制的文件或命令边界。"
        "结束前必须报告验证、"
        "防复发验证、硬失败、非阻断风险、写回和最终状态。不得把机器回执写进用户正文。"
        "验证完成后，调用安装目录中的 receipt_entry.py，使用 --kind completion 和 "
        "--payload-base64 记录带外回执。回执必须包含 gate_id、verification、"
        "prevention_verification、hard_failures、non_blocking_risks、writeback 和 status（completed 或 blocked）。"
        "prevention_verification 必须绑定诊断阶段返回的 prevention_plan_sha256，并包含 "
        "regression_probe、result、evidence 和 recurrence_control；completed 要求 result=passed 且 hard_failures 为空。"
    )


_WRITE_SHELL_PATTERNS = [
    r"\b(set|add|clear)-content\b",
    r"\bout-file\b",
    r"\b(new|remove|move|copy|rename)-item\b",
    r"\bapply_patch\b",
    r"\b(git\s+(add|commit|push|reset|checkout|clean|mv|rm))\b",
    r"\b(pip|python\s+-m\s+pip|npm|pnpm|yarn|winget|choco)\s+(install|uninstall|update|upgrade|add|remove)\b",
    r"\b(invoke-restmethod|curl)\b.*\b(post|put|patch|delete)\b",
    r"(^|[^>])>(?![>&])",
    r"\btee(-object)?\b",
    r"\bmkdir\b",
]

_READ_SHELL_COMMANDS = {
    "get-content",
    "get-childitem",
    "get-item",
    "get-location",
    "get-command",
    "get-filehash",
    "get-process",
    "get-ciminstance",
    "select-string",
    "test-path",
    "resolve-path",
    "where-object",
    "select-object",
    "format-table",
    "format-list",
    "sort-object",
    "measure-object",
    "rg",
    "git",
    "python",
    "python.exe",
    "py",
}


def _split_shell_segments(command: str) -> list[str] | None:
    segments: list[str] = []
    current: list[str] = []
    quote: str | None = None
    escaped = False
    index = 0
    while index < len(command):
        char = command[index]
        if escaped:
            current.append(char)
            escaped = False
            index += 1
            continue
        if char == "`" and quote != "'":
            current.append(char)
            escaped = True
            index += 1
            continue
        if quote:
            current.append(char)
            if char == quote:
                if quote == "'" and index + 1 < len(command) and command[index + 1] == "'":
                    current.append(command[index + 1])
                    index += 2
                    continue
                quote = None
            index += 1
            continue
        if char in {"'", '"'}:
            quote = char
            current.append(char)
            index += 1
            continue
        if char in {";", "|", "\n", "\r"}:
            segment = "".join(current).strip()
            if segment:
                segments.append(segment)
            current = []
            index += 1
            continue
        current.append(char)
        index += 1
    if quote or escaped:
        return None
    segment = "".join(current).strip()
    if segment:
        segments.append(segment)
    return segments


def _inspect_shell(command: str) -> ToolDecision:
    lowered = command.lower()
    for pattern in _WRITE_SHELL_PATTERNS:
        if re.search(pattern, lowered, flags=re.IGNORECASE | re.DOTALL):
            return ToolDecision(False, f"Shell command matches write pattern: {pattern}")
    if re.search(r"(^|[^\d])&(?![>])", command):
        return ToolDecision(False, "Dynamic or background shell invocation is not read-only auditable.")

    cleaned = re.sub(r"\$outputencoding\s*=.*?;", "", lowered, flags=re.DOTALL)
    segments = _split_shell_segments(cleaned)
    if segments is None:
        return ToolDecision(False, "Shell quoting is incomplete and cannot be audited.")
    if not segments:
        return ToolDecision(False, "Empty shell input is not auditable.")
    for segment in segments:
        if segment.startswith("$") and "=" in segment:
            continue
        token_match = re.match(r"(?:&\s*)?['\"]?([^\s'\"]+)", segment)
        if not token_match:
            return ToolDecision(False, "Shell segment cannot be classified as read-only.")
        token = Path(token_match.group(1)).name.lower()
        if token == "git":
            if not re.search(r"\bgit\s+(status|diff|show|log|rev-parse|ls-files)\b", segment):
                return ToolDecision(False, "Only read-only git subcommands are allowed while pending.")
            continue
        if token in {"python", "python.exe", "py"}:
            if re.fullmatch(
                r"""(?is).*?receipt_entry\.py['"]?\s+
                --kind\s+(?:diagnosis|completion)\s+
                --payload-base64\s+['"]?[A-Za-z0-9_=-]+['"]?\s*""",
                segment,
                flags=re.VERBOSE,
            ):
                continue
            if re.fullmatch(
                r"(?is).*?reasoning_effort_context\.py['\"]?\s+--probe\s*",
                segment,
            ):
                continue
            return ToolDecision(False, "Arbitrary interpreter execution is blocked while diagnosis is pending.")
        if token not in _READ_SHELL_COMMANDS:
            return ToolDecision(False, f"Shell command is not on the read-only allowlist: {token}")
    return ToolDecision(True, "Read-only shell command.")


def _read_only_tool_name(tool_name: str) -> bool:
    lowered = tool_name.lower()
    if lowered in {"view_image", "get_goal", "list_mcp_resources", "list_mcp_resource_templates", "read_mcp_resource"}:
        return True
    if lowered.startswith(("read_", "get_", "list_", "view_", "search_", "fetch_", "inspect_")):
        return True
    if lowered.startswith("mcp__"):
        final = lowered.rsplit("__", 1)[-1]
        return final.startswith(("read", "get", "list", "view", "search", "fetch", "inspect"))
    if lowered.startswith("codex_app__"):
        final = lowered.rsplit("__", 1)[-1]
        return final.startswith(("read", "get", "list", "view", "search", "fetch", "inspect", "load"))
    return False


def _retire_legacy_automatic_gate(state: dict[str, Any], store: GateStore) -> bool:
    if state["status"] != "pending" or state["category"] not in LEGACY_AUTOMATIC_CATEGORIES:
        return False
    state["status"] = "bypassed"
    state["updated_at"] = _now()
    state["migration_reason"] = "automatic_activation_disabled"
    store.save(state)
    return True


def _inspect_code_mode(source: str) -> ToolDecision:
    if re.search(r"\bstore\s*\(", source):
        return ToolDecision(False, "Code mode attempts to persist state.")
    if re.search(r"tools\s*\[", source):
        return ToolDecision(False, "Dynamic nested tool selection cannot be audited.")
    nested = re.findall(r"tools\.([A-Za-z0-9_]+)", source)
    if not nested:
        return ToolDecision(True, "Code mode contains no nested tool call.")
    for name in nested:
        lowered = name.lower()
        if lowered in {"apply_patch", "update_plan"}:
            return ToolDecision(False, f"Nested write-capable tool is blocked: {name}")
        if lowered in {"shell_command", "bash"}:
            for pattern in _WRITE_SHELL_PATTERNS:
                if re.search(pattern, source, flags=re.IGNORECASE | re.DOTALL):
                    return ToolDecision(False, f"Nested shell source matches write pattern: {pattern}")
            if re.search(r"\b(command|source)\s*:\s*[A-Za-z_$]", source):
                return ToolDecision(False, "Nested shell command is constructed dynamically.")
            continue
        if not _read_only_tool_name(name):
            return ToolDecision(False, f"Nested tool is not proven read-only: {name}")
    return ToolDecision(True, "All statically named nested tools are read-only.")


def inspect_tool_call(tool_name: str, tool_input: Any) -> ToolDecision:
    lowered = tool_name.lower()
    if lowered in {"apply_patch", "edit", "write", "update_plan"}:
        return ToolDecision(False, f"Write-capable tool is blocked: {tool_name}")
    if lowered in {"bash", "shell_command", "exec_command"}:
        if not isinstance(tool_input, dict):
            return ToolDecision(False, "Shell tool input is not an auditable object.")
        supplied = [tool_input[key] for key in ("cmd", "command") if key in tool_input]
        if not supplied or any(not isinstance(value, str) or not value.strip() for value in supplied):
            return ToolDecision(False, "Shell command is missing or invalid.")
        if len(supplied) > 1 and supplied[0] != supplied[1]:
            return ToolDecision(False, "Shell command fields disagree and cannot be audited.")
        return _inspect_shell(supplied[0])
    if lowered in {"functions.exec", "exec"}:
        if not isinstance(tool_input, dict):
            return ToolDecision(False, "Code-mode input is not an auditable object.")
        source = tool_input.get("source", tool_input.get("code", ""))
        return _inspect_code_mode(str(source))
    if _read_only_tool_name(tool_name):
        return ToolDecision(True, "Tool name is classified as read-only.")
    return ToolDecision(False, f"Unknown or write-capable tool is blocked: {tool_name}")


def _extract_receipt(message: str, marker: str) -> dict[str, Any] | None:
    pattern = rf"<!--\s*{re.escape(marker)}\s+(\{{.*?\}})\s*-->"
    match = re.search(pattern, message or "", flags=re.DOTALL)
    if not match:
        return None
    try:
        parsed = json.loads(match.group(1))
    except json.JSONDecodeError:
        return None
    return parsed if isinstance(parsed, dict) else None


def _nonempty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, list):
        return bool(value) and all(_nonempty(item) for item in value)
    if isinstance(value, dict):
        return bool(value) and all(_nonempty(item) for item in value.values())
    return value is not None


def _valid_layer_responsibility(layers: Any) -> bool:
    required = {"primary_layer", "inspection_stop", *DIAGNOSIS_LAYERS}
    if not isinstance(layers, dict) or set(layers) != required:
        return False

    primary_layer = layers["primary_layer"]
    inspection_stop = layers["inspection_stop"]
    if primary_layer not in DIAGNOSIS_LAYERS or inspection_stop not in DIAGNOSIS_LAYERS:
        return False

    statuses: dict[str, str] = {}
    for layer_name in DIAGNOSIS_LAYERS:
        layer = layers[layer_name]
        if not isinstance(layer, dict):
            return False
        status = layer.get("status")
        if status not in LAYER_STATUSES or not _nonempty(layer.get("finding")):
            return False
        expected_fields = {"status", "finding"}
        if status == "contributing":
            expected_fields.add("causal_connection")
            if not _nonempty(layer.get("causal_connection")):
                return False
        if set(layer) != expected_fields:
            return False
        statuses[layer_name] = status

    primary_layers = [name for name, status in statuses.items() if status == "primary"]
    if primary_layers != [primary_layer]:
        return False
    if statuses["current_task"] == "not_examined":
        return False

    stop_index = DIAGNOSIS_LAYERS.index(inspection_stop)
    examined = [name for name in DIAGNOSIS_LAYERS if statuses[name] != "not_examined"]
    if not examined or DIAGNOSIS_LAYERS.index(examined[-1]) != stop_index:
        return False
    for index, layer_name in enumerate(DIAGNOSIS_LAYERS):
        if index <= stop_index and statuses[layer_name] == "not_examined":
            return False
        if index > stop_index and statuses[layer_name] != "not_examined":
            return False

    primary_index = DIAGNOSIS_LAYERS.index(primary_layer)
    if primary_index < stop_index and not any(
        statuses[DIAGNOSIS_LAYERS[index]] == "contributing"
        for index in range(primary_index + 1, stop_index + 1)
    ):
        return False
    return True


def _valid_diagnosis(receipt: dict[str, Any] | None, gate_id: str) -> bool:
    if not receipt or receipt.get("gate_id") != gate_id:
        return False
    required = {
        "failure_sequence",
        "layer_responsibility",
        "failure_mechanism",
        "recurrence_condition",
        "prevention_plan",
        "plan_impact",
        "writeback_candidates",
        "decision",
        "repair_scope",
        "evidence",
    }
    if not required.issubset(receipt):
        return False
    nonempty_required = required.difference({"writeback_candidates"})
    if not all(_nonempty(receipt[key]) for key in nonempty_required):
        return False
    if not isinstance(receipt["writeback_candidates"], list):
        return False
    layers = receipt["layer_responsibility"]
    if not _valid_layer_responsibility(layers):
        return False
    prevention_plan = receipt["prevention_plan"]
    required_plan_fields = {
        "repair_layer",
        "durable_change",
        "recurrence_barrier",
        "regression_probe",
    }
    if not isinstance(prevention_plan, dict) or not required_plan_fields.issubset(
        prevention_plan
    ):
        return False
    if not all(_nonempty(prevention_plan[key]) for key in required_plan_fields):
        return False
    if prevention_plan["repair_layer"] != layers["primary_layer"]:
        return False
    return receipt["decision"] in {"continue", "stop"}


def _valid_completion(
    receipt: dict[str, Any] | None,
    gate_id: str,
    prevention_plan_sha256: str | None,
) -> bool:
    if not receipt or receipt.get("gate_id") != gate_id:
        return False
    required = {
        "verification",
        "prevention_verification",
        "hard_failures",
        "non_blocking_risks",
        "writeback",
        "status",
    }
    if not required.issubset(receipt):
        return False
    if not _nonempty(receipt["verification"]) or not _nonempty(receipt["writeback"]):
        return False
    prevention_verification = receipt["prevention_verification"]
    required_verification_fields = {
        "prevention_plan_sha256",
        "regression_probe",
        "result",
        "evidence",
        "recurrence_control",
    }
    if not isinstance(prevention_verification, dict) or not required_verification_fields.issubset(
        prevention_verification
    ):
        return False
    if not all(
        _nonempty(prevention_verification[key])
        for key in required_verification_fields
    ):
        return False
    if (
        not prevention_plan_sha256
        or prevention_verification["prevention_plan_sha256"]
        != prevention_plan_sha256
    ):
        return False
    if prevention_verification["result"] not in {"passed", "failed", "blocked"}:
        return False
    status = receipt["status"]
    if status not in {"completed", "blocked"}:
        return False
    if not isinstance(receipt["hard_failures"], list) or not isinstance(
        receipt["non_blocking_risks"], list
    ):
        return False
    return status != "completed" or (
        prevention_verification["result"] == "passed" and not receipt["hard_failures"]
    )


def record_receipt(
    kind: str, receipt: dict[str, Any], store: GateStore
) -> dict[str, str]:
    gate_id = str(receipt.get("gate_id") or "")
    state = store.find_by_gate_id(gate_id)
    if kind == "diagnosis":
        if state["status"] != "pending" or not _valid_diagnosis(receipt, gate_id):
            raise GuardStateError("Diagnosis receipt is invalid for the current gate state.")
        state["diagnosis_sha256"] = _sha256(
            json.dumps(receipt, ensure_ascii=False, sort_keys=True)
        )
        state["prevention_plan_sha256"] = _sha256(
            json.dumps(
                receipt["prevention_plan"], ensure_ascii=False, sort_keys=True
            )
        )
        state["updated_at"] = _now()
        if receipt["decision"] == "stop":
            state["status"] = "completed"
        else:
            state["status"] = "repair_authorized"
            state["repair_scope"] = receipt["repair_scope"]
        store.save(state)
        return {
            "gate_id": gate_id,
            "status": state["status"],
            "prevention_plan_sha256": state["prevention_plan_sha256"],
        }
    if kind == "completion":
        if state["status"] != "repair_authorized" or not _valid_completion(
            receipt, gate_id, state.get("prevention_plan_sha256")
        ):
            raise GuardStateError("Completion receipt is invalid for the current gate state.")
        state["status"] = receipt["status"]
        state["updated_at"] = _now()
        state["completion_sha256"] = _sha256(
            json.dumps(receipt, ensure_ascii=False, sort_keys=True)
        )
        store.save(state)
        return {"gate_id": gate_id, "status": state["status"]}
    raise GuardStateError(f"Unknown governance receipt kind: {kind}")


def _additional_context(event_name: str, context: str) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": context,
        }
    }


def handle_event(event: dict[str, Any], store: GateStore) -> dict[str, Any]:
    event_name = event.get("hook_event_name")
    session_id = event.get("session_id")
    if not isinstance(session_id, str) or not session_id:
        raise GuardStateError("Hook event has no valid session_id.")

    state = store.load(session_id)
    if state and _retire_legacy_automatic_gate(state, store):
        state = None
    if event_name == "UserPromptSubmit":
        prompt = str(event.get("prompt", ""))
        if state and state["status"] in OPEN_STATUSES:
            if "这一次旁路治理门禁" in prompt:
                state["status"] = "bypassed"
                state["updated_at"] = _now()
                state["bypass_prompt_sha256"] = _sha256(prompt)
                store.save(state)
                return _additional_context(
                    event_name,
                    f"用户已明确要求一次性旁路治理门禁 {state['gate_id']}。",
                )
            return _additional_context(event_name, _context_for(state))
        classification = classify_prompt(prompt)
        if not classification.trigger:
            return _additional_context(
                event_name,
                f"[治理激活门禁待命] mode=manual status=ready schema={SCHEMA_VERSION}。"
                "只有用户单独发出人工触发命令才会开启门禁；本标签不证明任何治理任务已经完成。",
            )
        state = _new_state(event, classification)
        store.save(state)
        return _additional_context(event_name, _context_for(state))

    if state and state["status"] == "blocked" and event_name in {"SessionStart", "PostCompact"}:
        return _additional_context(event_name, _context_for(state))

    if not state or state["status"] not in OPEN_STATUSES:
        return {}

    if event_name in {"SessionStart", "PostCompact"}:
        return _additional_context(event_name, _context_for(state))

    if event_name == "PreToolUse":
        if state["status"] == "repair_authorized":
            return {}
        decision = inspect_tool_call(str(event.get("tool_name", "")), event.get("tool_input"))
        if decision.allowed:
            return {}
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    f"治理门禁 {state['gate_id']} 尚未完成，当前调用未被证明是只读操作。"
                    "请先完成分层诊断，再执行写入。"
                ),
            }
        }

    if event_name == "Stop":
        if state["status"] == "pending":
            return {
                "decision": "block",
                "reason": (
                    f"治理门禁 {state['gate_id']} 尚未记录带外诊断回执。"
                    "请完成分层诊断后通过 receipt_entry.py 记录；"
                    "不要把机器 JSON 写进用户正文。"
                ),
            }

        return {
            "decision": "block",
            "reason": (
                f"治理门禁 {state['gate_id']} 尚未记录带外完成回执。"
                "请完成限定修复和验证后通过 receipt_entry.py 记录；"
                "不要把机器 JSON 写进用户正文。"
            ),
        }

    return {}
