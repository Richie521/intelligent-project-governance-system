from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import statistics
import tempfile
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 1
DEFAULT_MANIFEST = Path(".codex/governance-runtime.json")
TRANSACTION_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,127}$")
EVENT_ID_RE = re.compile(r"^gov-[A-Za-z0-9][A-Za-z0-9._-]{2,127}$")
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")
VARIABLE_RE = re.compile(r"^[A-Za-z0-9._-]{1,128}$")
FORBIDDEN_REQUEST_KEYS = {
    "prompt",
    "raw_prompt",
    "transcript",
    "conversation",
    "hidden_reasoning",
    "chain_of_thought",
    "credential",
    "credentials",
    "secret",
    "secrets",
    "token",
    "tokens",
    "password",
    "api_key",
}


class GovernanceTransactionError(RuntimeError):
    def __init__(self, code: str, message: str, *, details: Any | None = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details


@dataclass
class RenderedFile:
    owner: str
    relative_path: str
    path: Path
    existed: bool
    before: bytes
    after: bytes

    @property
    def changed(self) -> bool:
        return self.before != self.after


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


def normalized_request(request: dict[str, Any]) -> dict[str, Any]:
    """Return the request representation used for idempotency binding.

    Optional list fields have one canonical representation so omission and an
    explicit empty list mean the same request.  All other fields, including
    unknown fields accepted by the schema, remain part of the digest.
    """
    normalized = dict(request)
    normalized.setdefault("evidence_refs", [])
    normalized.setdefault("contract_tags", [])
    return normalized


def request_sha256(request: dict[str, Any]) -> str:
    return sha256_bytes(canonical_json_bytes(normalized_request(request)))


def _json_load(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise GovernanceTransactionError("manifest_missing", f"Missing JSON file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise GovernanceTransactionError(
            "invalid_json", f"Invalid JSON in {path}: {exc.msg} at line {exc.lineno}"
        ) from exc
    if not isinstance(value, dict):
        raise GovernanceTransactionError("invalid_json", f"JSON root must be an object: {path}")
    return value


def _assert_no_forbidden_keys(value: Any, path: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).strip().lower()
            if normalized in FORBIDDEN_REQUEST_KEYS:
                raise GovernanceTransactionError(
                    "privacy_violation",
                    f"Transaction requests cannot contain the field {path}.{key}.",
                )
            _assert_no_forbidden_keys(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _assert_no_forbidden_keys(child, f"{path}[{index}]")


def _require_string(value: Any, field: str, *, nonempty: bool = True) -> str:
    if not isinstance(value, str) or (nonempty and not value):
        raise GovernanceTransactionError("invalid_schema", f"{field} must be a string.")
    return value


def _require_string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise GovernanceTransactionError("invalid_schema", f"{field} must be a string array.")
    return list(value)


def _resolve_inside(project_root: Path, relative: str) -> Path:
    raw = Path(relative)
    if raw.is_absolute():
        raise GovernanceTransactionError("path_escape", f"Absolute paths are not allowed: {relative}")
    root = project_root.resolve()
    candidate = (root / raw).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise GovernanceTransactionError("path_escape", f"Path escapes project root: {relative}") from exc
    return candidate


def _state_root(override: Path | None = None) -> Path:
    if override is not None:
        return override.resolve()
    configured = os.environ.get("GOVERNANCE_TRANSACTION_STATE_DIR")
    if configured:
        return Path(configured).resolve()
    if os.name == "nt":
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            return Path(local_app_data) / "OpenAI" / "Codex" / "governance-transactions"
    xdg_state = os.environ.get("XDG_STATE_HOME")
    if xdg_state:
        return Path(xdg_state) / "openai-codex" / "governance-transactions"
    return Path.home() / ".local" / "state" / "openai-codex" / "governance-transactions"


def project_state_dir(project_root: Path, override: Path | None = None) -> Path:
    normalized = str(project_root.resolve())
    if os.name == "nt":
        normalized = normalized.casefold()
    project_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:20]
    return _state_root(override) / project_hash


def load_manifest(project_root: Path, manifest_relative: Path = DEFAULT_MANIFEST) -> tuple[dict[str, Any], Path, str]:
    manifest_path = _resolve_inside(project_root, manifest_relative.as_posix())
    raw = manifest_path.read_bytes()
    try:
        manifest = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GovernanceTransactionError("invalid_manifest", f"Invalid manifest: {manifest_path}") from exc
    if not isinstance(manifest, dict):
        raise GovernanceTransactionError("invalid_manifest", "Manifest root must be an object.")
    validate_manifest_shape(manifest, project_root)
    return manifest, manifest_path, sha256_bytes(raw)


def validate_manifest_shape(manifest: dict[str, Any], project_root: Path) -> None:
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise GovernanceTransactionError(
            "unsupported_schema", f"Manifest schema_version must be {SCHEMA_VERSION}."
        )
    _require_string(manifest.get("project_id"), "manifest.project_id")
    if manifest.get("governance_language") not in {"zh-CN", "en"}:
        raise GovernanceTransactionError(
            "invalid_schema", "manifest.governance_language must be zh-CN or en."
        )
    if manifest.get("project_role") not in {"central", "adopted"}:
        raise GovernanceTransactionError(
            "invalid_schema", "manifest.project_role must be central or adopted."
        )

    sources = manifest.get("routing_sources")
    if not isinstance(sources, dict) or not sources:
        raise GovernanceTransactionError(
            "invalid_schema", "manifest.routing_sources must be a non-empty object."
        )
    for name, source in sources.items():
        if not isinstance(source, dict):
            raise GovernanceTransactionError(
                "invalid_schema", f"manifest.routing_sources.{name} must be an object."
            )
        relative = _require_string(source.get("path"), f"routing_sources.{name}.path")
        _resolve_inside(project_root, relative)
        digest = _require_string(source.get("sha256"), f"routing_sources.{name}.sha256")
        if not SHA256_RE.fullmatch(digest):
            raise GovernanceTransactionError(
                "invalid_schema", f"routing_sources.{name}.sha256 is not SHA-256."
            )
        if not isinstance(source.get("size"), int) or source["size"] < 0:
            raise GovernanceTransactionError(
                "invalid_schema", f"routing_sources.{name}.size must be a non-negative integer."
            )
        if not isinstance(source.get("mtime_ns"), int) or source["mtime_ns"] < 0:
            raise GovernanceTransactionError(
                "invalid_schema", f"routing_sources.{name}.mtime_ns must be a non-negative integer."
            )

    projections = manifest.get("projections")
    if not isinstance(projections, dict) or not projections:
        raise GovernanceTransactionError(
            "invalid_schema", "manifest.projections must be a non-empty object."
        )
    for name, projection in projections.items():
        if not isinstance(projection, dict):
            raise GovernanceTransactionError(
                "invalid_schema", f"manifest.projections.{name} must be an object."
            )
        has_path = isinstance(projection.get("path"), str)
        has_pattern = isinstance(projection.get("path_pattern"), str)
        if has_path == has_pattern:
            raise GovernanceTransactionError(
                "invalid_schema",
                f"Projection {name} must define exactly one of path or path_pattern.",
            )
        path_value = projection.get("path") if has_path else projection.get("path_pattern")
        if not isinstance(path_value, str) or not path_value:
            raise GovernanceTransactionError("invalid_schema", f"Projection {name} has no path.")
        if has_path:
            _resolve_inside(project_root, path_value)
        else:
            sample = re.sub(r"\{[A-Za-z_][A-Za-z0-9_]*\}", "sample", path_value)
            _resolve_inside(project_root, sample)
        operations = _require_string_list(projection.get("operations"), f"projections.{name}.operations")
        if not operations or not set(operations).issubset(
            {"replace_exact", "insert_after", "append_unique", "compare_exchange"}
        ):
            raise GovernanceTransactionError(
                "invalid_schema", f"Projection {name} has unsupported operations."
            )
        authorizations = _require_string_list(
            projection.get("allowed_authorizations"),
            f"projections.{name}.allowed_authorizations",
        )
        if not authorizations or not set(authorizations).issubset(
            {"automatic_low_risk", "explicit_current_task"}
        ):
            raise GovernanceTransactionError(
                "invalid_schema", f"Projection {name} has unsupported authorizations."
            )
        if not isinstance(projection.get("create_if_missing", False), bool):
            raise GovernanceTransactionError(
                "invalid_schema", f"Projection {name}.create_if_missing must be boolean."
            )
        preamble = projection.get("new_file_preamble", "")
        if not isinstance(preamble, str):
            raise GovernanceTransactionError(
                "invalid_schema", f"Projection {name}.new_file_preamble must be a string."
            )

    contracts = manifest.get("transaction_contracts", [])
    if not isinstance(contracts, list):
        raise GovernanceTransactionError(
            "invalid_schema", "manifest.transaction_contracts must be an array."
        )
    contract_names: set[str] = set()
    projection_names = set(projections)
    for index, contract in enumerate(contracts):
        field = f"manifest.transaction_contracts[{index}]"
        if not isinstance(contract, dict):
            raise GovernanceTransactionError("invalid_schema", f"{field} must be an object.")
        name = _require_string(contract.get("name"), f"{field}.name")
        if not VARIABLE_RE.fullmatch(name) or name in contract_names:
            raise GovernanceTransactionError(
                "invalid_schema", f"{field}.name must be unique and use safe characters."
            )
        contract_names.add(name)
        trigger_owners = _require_string_list(
            contract.get("trigger_owners", []), f"{field}.trigger_owners"
        )
        trigger_tags = _require_string_list(
            contract.get("trigger_tags", []), f"{field}.trigger_tags"
        )
        required_owners = _require_string_list(
            contract.get("required_owners"), f"{field}.required_owners"
        )
        if (not trigger_owners and not trigger_tags) or not required_owners:
            raise GovernanceTransactionError(
                "invalid_schema",
                f"{field} must declare trigger_owners or trigger_tags, and required_owners.",
            )
        if (
            len(set(trigger_owners)) != len(trigger_owners)
            or len(set(trigger_tags)) != len(trigger_tags)
            or len(set(required_owners)) != len(required_owners)
        ):
            raise GovernanceTransactionError(
                "invalid_schema", f"{field} trigger and owner lists must not contain duplicates."
            )
        if any(not VARIABLE_RE.fullmatch(tag) for tag in trigger_tags):
            raise GovernanceTransactionError(
                "invalid_schema", f"{field}.trigger_tags contains unsafe characters."
            )
        unknown = (set(trigger_owners) | set(required_owners)) - projection_names
        if unknown:
            raise GovernanceTransactionError(
                "invalid_schema",
                f"{field} refers to unknown projection owners: {sorted(unknown)}.",
            )


def validate_routing_sources(
    manifest: dict[str, Any], project_root: Path, *, full_hash: bool
) -> dict[str, Any]:
    checked: list[str] = []
    hashed: list[str] = []
    for name, source in manifest["routing_sources"].items():
        path = _resolve_inside(project_root, source["path"])
        try:
            stat = path.stat()
        except FileNotFoundError as exc:
            raise GovernanceTransactionError(
                "routing_source_missing", f"Routing source is missing: {source['path']}"
            ) from exc
        metadata_matches = stat.st_size == source["size"] and stat.st_mtime_ns == source["mtime_ns"]
        if full_hash or not metadata_matches:
            hashed.append(name)
            actual = sha256_file(path)
            if actual.lower() != source["sha256"].lower():
                raise GovernanceTransactionError(
                    "routing_source_drift",
                    f"Routing source changed: {source['path']}",
                    details={"source": name, "expected": source["sha256"], "actual": actual},
                )
        checked.append(name)
    return {"checked": checked, "hashed": hashed}


def _render_pattern(
    pattern: str, variables: dict[str, Any], field: str, *, allow_extra: bool = False
) -> str:
    if not isinstance(variables, dict):
        raise GovernanceTransactionError("invalid_schema", f"{field} must be an object.")
    rendered = pattern
    expected = set(re.findall(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", pattern))
    if (allow_extra and not expected.issubset(variables)) or (
        not allow_extra and set(variables) != expected
    ):
        raise GovernanceTransactionError(
            "invalid_schema", f"{field} keys must exactly match {sorted(expected)}."
        )
    for name, value in variables.items():
        if not isinstance(value, str) or not VARIABLE_RE.fullmatch(value):
            raise GovernanceTransactionError(
                "invalid_schema", f"{field}.{name} contains unsafe characters."
            )
        rendered = rendered.replace("{" + name + "}", value)
    return rendered


def _projection_target(
    project_root: Path,
    projection: dict[str, Any],
    operation: dict[str, Any],
) -> tuple[str, Path, str]:
    variables = operation.get("target_variables", {})
    if "path" in projection:
        if variables not in ({}, None):
            raise GovernanceTransactionError(
                "invalid_schema", "target_variables are only valid for path_pattern projections."
            )
        relative = projection["path"]
        preamble = projection.get("new_file_preamble", "")
    else:
        relative = _render_pattern(
            projection["path_pattern"], variables, "operation.target_variables"
        )
        preamble = _render_pattern(
            projection.get("new_file_preamble", ""),
            variables,
            "operation.target_variables",
            allow_extra=True,
        )
    return relative, _resolve_inside(project_root, relative), preamble


def validate_request_shape(request: dict[str, Any]) -> None:
    _assert_no_forbidden_keys(request)
    if request.get("schema_version") != SCHEMA_VERSION:
        raise GovernanceTransactionError(
            "unsupported_schema", f"Transaction schema_version must be {SCHEMA_VERSION}."
        )
    transaction_id = _require_string(request.get("transaction_id"), "transaction_id")
    if not TRANSACTION_ID_RE.fullmatch(transaction_id):
        raise GovernanceTransactionError("invalid_schema", "transaction_id has an invalid format.")
    digest = _require_string(request.get("manifest_sha256"), "manifest_sha256")
    if not SHA256_RE.fullmatch(digest):
        raise GovernanceTransactionError("invalid_schema", "manifest_sha256 is not SHA-256.")
    if request.get("authorization") not in {"automatic_low_risk", "explicit_current_task"}:
        raise GovernanceTransactionError(
            "invalid_schema", "authorization must be automatic_low_risk or explicit_current_task."
        )
    projections = request.get("projections")
    if not isinstance(projections, list):
        raise GovernanceTransactionError("invalid_schema", "projections must be an array.")
    evidence_refs = request.get("evidence_refs", [])
    _require_string_list(evidence_refs, "evidence_refs")
    if any(len(item) > 512 for item in evidence_refs):
        raise GovernanceTransactionError("invalid_schema", "evidence_refs entries are too long.")
    contract_tags = _require_string_list(request.get("contract_tags", []), "contract_tags")
    if len(set(contract_tags)) != len(contract_tags):
        raise GovernanceTransactionError("invalid_schema", "contract_tags must not contain duplicates.")
    if any(not VARIABLE_RE.fullmatch(tag) for tag in contract_tags):
        raise GovernanceTransactionError(
            "invalid_schema", "contract_tags entries must use safe characters."
        )


def _apply_operation(current: bytes, operation: dict[str, Any], *, encoding: str) -> bytes:
    try:
        text = current.decode(encoding)
    except UnicodeDecodeError as exc:
        raise GovernanceTransactionError(
            "unsupported_encoding", f"Projection target is not valid {encoding}."
        ) from exc
    kind = operation.get("operation")
    if kind == "replace_exact":
        old = _require_string(operation.get("old"), "operation.old")
        new = _require_string(operation.get("new"), "operation.new", nonempty=False)
        count = text.count(old)
        if count == 0 and new and text.count(new) == 1:
            return current
        if count != 1:
            raise GovernanceTransactionError(
                "exact_match_conflict", f"replace_exact expected one match, found {count}."
            )
        return text.replace(old, new, 1).encode(encoding)

    if kind == "insert_after":
        anchor = _require_string(operation.get("anchor"), "operation.anchor")
        content = _require_string(operation.get("content"), "operation.content")
        if text.count(content) == 1:
            return current
        count = text.count(anchor)
        if count != 1:
            raise GovernanceTransactionError(
                "exact_match_conflict", f"insert_after expected one anchor, found {count}."
            )
        return text.replace(anchor, anchor + content, 1).encode(encoding)

    if kind == "append_unique":
        event_id = _require_string(operation.get("event_id"), "operation.event_id")
        content = _require_string(operation.get("content"), "operation.content")
        if not EVENT_ID_RE.fullmatch(event_id):
            raise GovernanceTransactionError("invalid_schema", "event_id has an invalid format.")
        heading = f"## {event_id}"
        if not content.lstrip().startswith(heading):
            raise GovernanceTransactionError(
                "invalid_schema", "append_unique content must start with its event heading."
            )
        if re.search(rf"(?m)^##\s+{re.escape(event_id)}\s*$", text):
            if content.strip() in text:
                return current
            raise GovernanceTransactionError(
                "duplicate_event_conflict", f"Event ID already exists with different content: {event_id}"
            )
        separator = "" if not text else ("\n\n" if not text.endswith("\n\n") else "")
        return (text + separator + content.strip() + "\n").encode(encoding)

    if kind == "compare_exchange":
        expected = _require_string(operation.get("expected_sha256"), "operation.expected_sha256")
        content = _require_string(operation.get("content"), "operation.content", nonempty=False)
        if not SHA256_RE.fullmatch(expected):
            raise GovernanceTransactionError(
                "invalid_schema", "operation.expected_sha256 is not SHA-256."
            )
        target = content.encode(encoding)
        current_hash = sha256_bytes(current)
        if current_hash == sha256_bytes(target):
            return current
        if current_hash.lower() != expected.lower():
            raise GovernanceTransactionError(
                "source_conflict",
                "compare_exchange source hash does not match.",
                details={"expected": expected, "actual": current_hash},
            )
        return target

    raise GovernanceTransactionError("invalid_schema", f"Unsupported operation: {kind}")


def render_transaction(
    manifest: dict[str, Any], request: dict[str, Any], project_root: Path
) -> tuple[list[RenderedFile], int]:
    authorization = request["authorization"]
    grouped: dict[Path, RenderedFile] = {}
    read_paths: set[Path] = set()
    for index, operation in enumerate(request["projections"]):
        if not isinstance(operation, dict):
            raise GovernanceTransactionError(
                "invalid_schema", f"projections[{index}] must be an object."
            )
        owner = _require_string(operation.get("owner"), f"projections[{index}].owner")
        if owner not in manifest["projections"]:
            raise GovernanceTransactionError("unknown_owner", f"Unknown projection owner: {owner}")
        projection = manifest["projections"][owner]
        kind = _require_string(operation.get("operation"), f"projections[{index}].operation")
        if kind not in projection["operations"]:
            raise GovernanceTransactionError(
                "operation_not_allowed", f"Operation {kind} is not allowed for {owner}."
            )
        if authorization not in projection["allowed_authorizations"]:
            raise GovernanceTransactionError(
                "authorization_not_allowed",
                f"Authorization {authorization} is not allowed for {owner}.",
            )
        relative, path, preamble = _projection_target(project_root, projection, operation)
        if path not in grouped:
            existed = path.exists()
            if not existed and not projection.get("create_if_missing", False):
                raise GovernanceTransactionError(
                    "projection_missing", f"Projection target does not exist: {relative}"
                )
            before = path.read_bytes() if existed else preamble.encode("utf-8")
            if existed:
                read_paths.add(path)
            grouped[path] = RenderedFile(owner, relative, path, existed, before, before)
        rendered = grouped[path]
        try:
            rendered.after = _apply_operation(
                rendered.after, operation, encoding=projection.get("encoding", "utf-8")
            )
        except GovernanceTransactionError as exc:
            details = {
                "projection_index": index,
                "owner": owner,
                "operation": kind,
                "relative_path": relative,
            }
            if isinstance(exc.details, dict):
                details.update(exc.details)
            raise GovernanceTransactionError(exc.code, exc.message, details=details) from exc
    changed_owners = {item.owner for item in grouped.values() if item.changed}
    declared_owners = {item.owner for item in grouped.values()}
    request_tags = set(request.get("contract_tags", []))
    for contract in manifest.get("transaction_contracts", []):
        trigger_owners = set(contract.get("trigger_owners", []))
        trigger_tags = set(contract.get("trigger_tags", []))
        required_owners = set(contract["required_owners"])
        if changed_owners.intersection(trigger_owners) or request_tags.intersection(trigger_tags):
            missing = sorted(required_owners - declared_owners)
            if missing:
                raise GovernanceTransactionError(
                    "missing_required_owner",
                    f"Transaction contract {contract['name']} requires projection owners: "
                    f"{', '.join(missing)}.",
                    details={
                        "contract": contract["name"],
                        "changed_owners": sorted(changed_owners),
                        "declared_owners": sorted(declared_owners),
                        "contract_tags": sorted(request_tags),
                        "trigger_tags": sorted(trigger_tags),
                        "required_owners": sorted(required_owners),
                    },
                )
    return list(grouped.values()), len(read_paths)


class ProjectLock:
    def __init__(self, path: Path, transaction_id: str):
        self.path = path
        self.transaction_id = transaction_id
        self.acquired = False

    def __enter__(self) -> "ProjectLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(
            {"transaction_id": self.transaction_id, "pid": os.getpid(), "created_ns": time.time_ns()},
            separators=(",", ":"),
        ).encode("utf-8")
        with _active_lock_guard(self.path):
            try:
                descriptor = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            except FileExistsError as exc:
                raise GovernanceTransactionError(
                    "project_locked", "Another governance transaction is already active."
                ) from exc
            try:
                os.write(descriptor, payload)
                os.fsync(descriptor)
            finally:
                os.close(descriptor)
        self.acquired = True
        return self

    def __exit__(self, exc_type: Any, exc: Any, traceback: Any) -> None:
        if self.acquired:
            with _active_lock_guard(self.path):
                self.path.unlink(missing_ok=True)


@contextmanager
def _active_lock_guard(lock_path: Path) -> Iterable[None]:
    """Serialize active.lock creation and stale-lock removal across processes."""
    guard_path = lock_path.with_name(f"{lock_path.name}.guard")
    guard_path.parent.mkdir(parents=True, exist_ok=True)
    with guard_path.open("a+b", buffering=0) as guard:
        if os.name == "nt":
            import msvcrt

            guard.seek(0, os.SEEK_END)
            if guard.tell() == 0:
                guard.write(b"\0")
            guard.seek(0)
            msvcrt.locking(guard.fileno(), msvcrt.LK_LOCK, 1)
            try:
                yield
            finally:
                guard.seek(0)
                msvcrt.locking(guard.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl

            fcntl.flock(guard.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(guard.fileno(), fcntl.LOCK_UN)


def _pid_is_alive(pid: int) -> bool:
    if type(pid) is not int or pid <= 0 or pid > 0xFFFFFFFF:
        return True
    if os.name == "nt":
        # os.kill(pid, 0) is not a read-only liveness check on Windows: it can
        # deliver a signal to the target process. Query a process handle only.
        import ctypes
        from ctypes import wintypes

        try:
            kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
            kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
            kernel32.OpenProcess.restype = wintypes.HANDLE
            kernel32.GetExitCodeProcess.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
            kernel32.GetExitCodeProcess.restype = wintypes.BOOL
            kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
            kernel32.CloseHandle.restype = wintypes.BOOL
            handle = kernel32.OpenProcess(0x1000, False, pid)  # PROCESS_QUERY_LIMITED_INFORMATION
        except (AttributeError, OSError):
            return True
        if not handle:
            # ERROR_INVALID_PARAMETER denotes an invalid PID. Other failures
            # are ambiguous and therefore cannot prove a stale lock.
            return ctypes.get_last_error() != 87
        try:
            exit_code = wintypes.DWORD()
            if not kernel32.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
                return True
            return exit_code.value == 259  # STILL_ACTIVE
        finally:
            kernel32.CloseHandle(handle)
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        # An inaccessible process is treated as alive.  Recovery must not
        # delete a lock when ownership cannot be disproved.
        return True
    return True


def _prepare_recovery_lock(lock_path: Path) -> tuple[bool, dict[str, Any] | None]:
    """Remove only a provably stale lock, preserving live or ambiguous locks."""
    with _active_lock_guard(lock_path):
        if not lock_path.exists():
            return True, None
        try:
            raw = lock_path.read_bytes()
        except OSError as exc:
            return False, {"reason": "lock_unreadable", "error": str(exc)}
        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            return False, {"reason": "lock_invalid", "error": str(exc)}
        pid = payload.get("pid") if isinstance(payload, dict) else None
        if type(pid) is not int or not 0 < pid <= 0xFFFFFFFF:
            return False, {"reason": "lock_invalid", "error": "lock payload has no integer pid"}
        if _pid_is_alive(pid):
            return False, {
                "reason": "active_lock",
                "transaction_id": payload.get("transaction_id"),
                "pid": pid,
            }
        try:
            # Lock creators and stale-lock removers hold this same guard.
            if lock_path.read_bytes() != raw:
                return False, {"reason": "lock_changed", "error": "lock changed during inspection"}
            lock_path.unlink()
        except FileNotFoundError:
            pass
        except OSError as exc:
            return False, {"reason": "lock_remove_failed", "error": str(exc)}
        return True, None


def _write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _backup_files(files: Iterable[RenderedFile], backup_dir: Path) -> list[dict[str, Any]]:
    backup_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    for index, rendered in enumerate(files):
        backup_name = f"{index:04d}.bak"
        backup_path = backup_dir / backup_name
        if rendered.existed:
            backup_path.write_bytes(rendered.before)
        records.append(
            {
                "owner": rendered.owner,
                "relative_path": rendered.relative_path,
                "existed": rendered.existed,
                "backup": backup_name if rendered.existed else None,
                "before_sha256": sha256_bytes(rendered.before) if rendered.existed else None,
                "after_sha256": sha256_bytes(rendered.after),
            }
        )
    return records


def _replace_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
        temporary = Path(handle.name)
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def _current_sha256(path: Path) -> str | None:
    return sha256_file(path) if path.exists() else None


def _assert_current_sha256(path: Path, expected: str | None, relative_path: str) -> None:
    actual = _current_sha256(path)
    if actual != expected:
        raise GovernanceTransactionError(
            "source_conflict",
            f"Projection changed before commit: {relative_path}",
            details={
                "relative_path": relative_path,
                "expected": expected,
                "actual": actual,
                "write_state": "not_applied",
            },
        )


def _replace_bytes_checked(
    path: Path,
    data: bytes,
    *,
    expected_sha256: str | None,
    relative_path: str,
) -> None:
    _assert_current_sha256(path, expected_sha256, relative_path)
    if os.name != "nt":
        # The Windows candidate below preserves the atomically replaced version
        # when it detects a concurrent edit. Other platforms retain the prior
        # best-effort check and replace behavior and are not concurrency-verified.
        _replace_bytes(path, data)
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    replaced_version = path.with_name(
        f".{path.name}.governance-conflict-{uuid.uuid4().hex}.bak"
    )
    temporary.write_bytes(data)
    preserve_temporary = False
    try:
        if expected_sha256 is None:
            try:
                _move_file_windows(temporary, path)
            except OSError as exc:
                if path.exists():
                    raise GovernanceTransactionError(
                        "source_conflict",
                        f"Projection appeared during commit: {relative_path}",
                        details={
                            "relative_path": relative_path,
                            "actual": _current_sha256(path),
                            "conflict_path": str(path),
                            "winerror": getattr(exc, "winerror", None) or exc.errno,
                            "write_state": "not_applied",
                        },
                    ) from exc
                raise
            return

        try:
            _replace_file_windows(path, temporary, replaced_version)
        except OSError as exc:
            winerror = getattr(exc, "winerror", None) or exc.errno
            if winerror == 1177 or replaced_version.exists() or not path.exists():
                preserve_temporary = True
                raise GovernanceTransactionError(
                    "source_conflict",
                    f"Atomic replacement did not complete cleanly for {relative_path}; preserving filesystem recovery state.",
                    details={
                        "relative_path": relative_path,
                        "winerror": winerror,
                        "conflict_backup": str(replaced_version) if replaced_version.exists() else None,
                        "replacement_temp": str(temporary) if temporary.exists() else None,
                        "target_exists": path.exists(),
                        "write_state": "unknown",
                        "recovery_note": "Do not remove the conflict backup; ReplaceFileW may have moved the current target before returning an error.",
                    },
                ) from exc
            raise
        replaced_hash = _current_sha256(replaced_version)
        if replaced_hash != expected_sha256:
            raise GovernanceTransactionError(
                "source_conflict",
                f"Projection changed during commit: {relative_path}",
                details={
                    "relative_path": relative_path,
                    "expected": expected_sha256,
                    "actual": replaced_hash,
                    "conflict_backup": str(replaced_version),
                    "write_state": "applied_conflicting_snapshot",
                    "recovery_note": "The exact version atomically replaced at commit is preserved in conflict_backup. The transaction did not commit successfully.",
                },
            )
        replaced_version.unlink(missing_ok=True)
    finally:
        if not preserve_temporary:
            temporary.unlink(missing_ok=True)


def _windows_file_operation(name: str, *paths: Path) -> None:
    """Run one same-volume Win32 file move/replace operation."""
    import ctypes

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    operation = getattr(kernel32, name)
    if name == "ReplaceFileW":
        operation.argtypes = [
            ctypes.c_wchar_p,
            ctypes.c_wchar_p,
            ctypes.c_wchar_p,
            ctypes.c_uint32,
            ctypes.c_void_p,
            ctypes.c_void_p,
        ]
    else:
        operation.argtypes = [ctypes.c_wchar_p] * len(paths)
    operation.restype = ctypes.c_int
    arguments = [str(path) for path in paths]
    if name == "ReplaceFileW":
        arguments.extend([0, None, None])
    if not operation(*arguments):
        error = ctypes.get_last_error()
        raise OSError(error, f"{name} failed with Windows error {error}")


def _replace_file_windows(path: Path, replacement: Path, backup: Path) -> None:
    # ReplaceFileW atomically moves the prior destination to backup while
    # installing replacement. Hashing backup closes the final check/replace
    # gap without discarding the concurrently written version.
    _windows_file_operation("ReplaceFileW", path, replacement, backup)


def _move_file_windows(source: Path, destination: Path) -> None:
    # MoveFileW fails if another process creates destination after the initial
    # check, so a newly created projection is never silently replaced.
    _windows_file_operation("MoveFileW", source, destination)


def _rollback(project_root: Path, journal: dict[str, Any], journal_dir: Path) -> list[str]:
    failures: list[str] = []
    for record in reversed(journal["files"]):
        path = _resolve_inside(project_root, record["relative_path"])
        try:
            actual = _current_sha256(path)
            allowed = {record.get("before_sha256"), record.get("after_sha256")}
            if actual not in allowed:
                failures.append(
                    f"{record['relative_path']}: changed before rollback "
                    f"(expected one of {sorted(value for value in allowed if value)}, got {actual})"
                )
                continue
            if actual == record.get("before_sha256"):
                continue
            if record["existed"]:
                backup = journal_dir / "backups" / record["backup"]
                if not backup.exists():
                    raise FileNotFoundError(f"Missing backup {backup}")
                if actual is None:
                    raise GovernanceTransactionError(
                        "source_conflict",
                        f"Projection disappeared before rollback: {record['relative_path']}",
                        details={"rollback_conflict_path": str(path)},
                    )
                _replace_bytes_checked(
                    path,
                    backup.read_bytes(),
                    expected_sha256=actual,
                    relative_path=record["relative_path"],
                )
            else:
                if actual is not None:
                    tombstone = path.with_name(
                        f".{path.name}.governance-rollback-conflict-{uuid.uuid4().hex}.bak"
                    )
                    if os.name == "nt":
                        _move_file_windows(path, tombstone)
                    else:
                        path.rename(tombstone)
                    moved_hash = _current_sha256(tombstone)
                    if moved_hash != actual:
                        failures.append(
                            f"{record['relative_path']}: rollback content changed; recoverable copy={tombstone}"
                        )
                    else:
                        tombstone.unlink(missing_ok=True)
        except (OSError, GovernanceTransactionError) as exc:
            details = exc.details if isinstance(exc, GovernanceTransactionError) else None
            failures.append(f"{record['relative_path']}: rollback conflict/error={exc}; details={details}")
    return failures


def _minimal_file_result(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "owner": record["owner"],
        "before_sha256": record["before_sha256"],
        "after_sha256": record["after_sha256"],
    }


def apply_transaction(
    project_root: Path,
    request: dict[str, Any],
    *,
    manifest_relative: Path = DEFAULT_MANIFEST,
    state_root: Path | None = None,
) -> dict[str, Any]:
    started = time.perf_counter_ns()
    timings: dict[str, float] = {}
    validate_request_shape(request)
    normalized_request_sha256 = request_sha256(request)
    contract_tags = sorted(request.get("contract_tags", []))
    manifest_started = time.perf_counter_ns()
    manifest, _, manifest_hash = load_manifest(project_root, manifest_relative)
    if manifest_hash.lower() != request["manifest_sha256"].lower():
        raise GovernanceTransactionError(
            "manifest_conflict",
            "Transaction was prepared for a different governance runtime manifest.",
            details={"expected": request["manifest_sha256"], "actual": manifest_hash},
        )
    routing_result = validate_routing_sources(manifest, project_root, full_hash=False)
    timings["manifest"] = (time.perf_counter_ns() - manifest_started) / 1_000_000

    transaction_id = request["transaction_id"]
    state_dir = project_state_dir(project_root, state_root)
    transaction_dir = state_dir / "transactions" / transaction_id
    receipt_path = transaction_dir / "receipt.json"
    lock_started = time.perf_counter_ns()
    with ProjectLock(state_dir / "active.lock", transaction_id):
        timings["lock"] = (time.perf_counter_ns() - lock_started) / 1_000_000
        if receipt_path.exists():
            receipt = _json_load(receipt_path)
            stored_request_sha256 = receipt.get("request_sha256")
            if not isinstance(stored_request_sha256, str):
                raise GovernanceTransactionError(
                    "legacy_receipt_conflict",
                    "Existing transaction receipt has no request summary; refusing replay.",
                    details={"transaction_id": transaction_id},
                )
            if stored_request_sha256.lower() != normalized_request_sha256.lower():
                raise GovernanceTransactionError(
                    "transaction_id_conflict",
                    "Transaction ID is already bound to a different request.",
                    details={
                        "transaction_id": transaction_id,
                        "expected": stored_request_sha256,
                        "actual": normalized_request_sha256,
                    },
                )
            result = dict(receipt)
            result["idempotent_replay"] = True
            return result

        render_started = time.perf_counter_ns()
        rendered, read_count = render_transaction(manifest, request, project_root)
        changed = [item for item in rendered if item.changed]
        timings["render"] = (time.perf_counter_ns() - render_started) / 1_000_000
        if not changed:
            timings["total"] = (time.perf_counter_ns() - started) / 1_000_000
            return {
                "schema_version": SCHEMA_VERSION,
                "transaction_id": transaction_id,
                "contract_tags": contract_tags,
                "request_sha256": normalized_request_sha256,
                "status": "no_change",
                "terminal_projection": True,
                "changed_owners": [],
                "skipped_owners": sorted({item.owner for item in rendered}),
                "files_read": read_count,
                "files_written": 0,
                "routing_sources": routing_result,
                "timings_ms": timings,
                "hard_failures": [],
                "writeback": "Writeback: none",
            }

        transaction_dir.mkdir(parents=True, exist_ok=True)
        backup_started = time.perf_counter_ns()
        records = _backup_files(changed, transaction_dir / "backups")
        journal = {
            "schema_version": SCHEMA_VERSION,
            "project_hash": state_dir.name,
            "transaction_id": transaction_id,
            "contract_tags": contract_tags,
            "request_sha256": normalized_request_sha256,
            "status": "prepared",
            "manifest_sha256": manifest_hash,
            "created_ns": time.time_ns(),
            "files": records,
        }
        journal_path = transaction_dir / "journal.json"
        _write_json_atomic(journal_path, journal)
        timings["prepare"] = (time.perf_counter_ns() - backup_started) / 1_000_000

        commit_started = time.perf_counter_ns()
        fail_after = os.environ.get("GOVERNANCE_TRANSACTION_FAIL_AFTER")
        try:
            for index, rendered_file in enumerate(changed, start=1):
                record = records[index - 1]
                _replace_bytes_checked(
                    rendered_file.path,
                    rendered_file.after,
                    expected_sha256=record["before_sha256"],
                    relative_path=rendered_file.relative_path,
                )
                journal["status"] = "committing"
                journal["committed_count"] = index
                _write_json_atomic(journal_path, journal)
                if fail_after and index >= int(fail_after):
                    raise OSError("Injected transaction failure for testing.")
        except Exception as exc:
            preserved_conflict = (
                isinstance(exc, GovernanceTransactionError) and exc.code == "source_conflict"
            )
            conflict_write_state = (
                exc.details.get("write_state")
                if preserved_conflict and isinstance(exc.details, dict)
                else None
            )
            rollback_failures = (
                [] if preserved_conflict else _rollback(project_root, journal, transaction_dir)
            )
            known_committed_count = (
                index - 1
                + (1 if conflict_write_state == "applied_conflicting_snapshot" else 0)
                if preserved_conflict
                else (None if rollback_failures else 0)
            )
            status = (
                "conflict"
                if preserved_conflict
                else ("failed" if rollback_failures else "rolled_back")
            )
            journal["status"] = status
            journal["rollback_failures"] = rollback_failures
            journal["error"] = str(exc)
            if preserved_conflict:
                journal["conflict_details"] = exc.details
                journal["conflict_write_state"] = conflict_write_state or "unknown"
                if conflict_write_state == "applied_conflicting_snapshot":
                    journal["committed_count"] = index
            if rollback_failures:
                journal["rollback_conflicts"] = rollback_failures
            journal["known_committed_count"] = known_committed_count
            journal["partial_or_uncertain"] = preserved_conflict or bool(rollback_failures)
            _write_json_atomic(journal_path, journal)
            timings["commit"] = (time.perf_counter_ns() - commit_started) / 1_000_000
            timings["total"] = (time.perf_counter_ns() - started) / 1_000_000
            result = {
                "schema_version": SCHEMA_VERSION,
                "transaction_id": transaction_id,
                "contract_tags": contract_tags,
                "request_sha256": normalized_request_sha256,
                "status": status,
                "terminal_projection": False,
                "changed_owners": (
                    [item.owner for item in changed[:known_committed_count]]
                    if known_committed_count is not None
                    else None
                ),
                "skipped_owners": [],
                "files_read": read_count,
                "files_written": (
                    None
                    if known_committed_count is None
                    or (preserved_conflict and conflict_write_state in {None, "unknown"})
                    else known_committed_count
                ),
                "partial_or_uncertain": preserved_conflict or bool(rollback_failures),
                "known_committed_count": known_committed_count,
                "conflict_write_state": (
                    conflict_write_state or ("rollback_incomplete" if rollback_failures else None)
                ),
                "conflict": exc.details if preserved_conflict else None,
                "timings_ms": timings,
                "hard_failures": [str(exc), *rollback_failures],
                "writeback": "Writeback: deferred because governance transaction failed",
            }
            _write_json_atomic(receipt_path, result)
            return result
        timings["commit"] = (time.perf_counter_ns() - commit_started) / 1_000_000

        verify_started = time.perf_counter_ns()
        verification_failures: list[str] = []
        for rendered_file in changed:
            actual = sha256_file(rendered_file.path)
            expected = sha256_bytes(rendered_file.after)
            if actual != expected:
                verification_failures.append(
                    f"{rendered_file.relative_path}: expected {expected}, got {actual}"
                )
        if verification_failures:
            rollback_failures = _rollback(project_root, journal, transaction_dir)
            journal["status"] = "failed" if rollback_failures else "rolled_back"
            journal["verification_failures"] = verification_failures
            journal["rollback_failures"] = rollback_failures
            _write_json_atomic(journal_path, journal)
            raise GovernanceTransactionError(
                "verification_failed",
                "Post-write verification failed; transaction was rolled back.",
                details={
                    "verification_failures": verification_failures,
                    "rollback_failures": rollback_failures,
                },
            )
        timings["verify"] = (time.perf_counter_ns() - verify_started) / 1_000_000
        timings["total"] = (time.perf_counter_ns() - started) / 1_000_000

        journal["status"] = "completed"
        journal["completed_ns"] = time.time_ns()
        _write_json_atomic(journal_path, journal)
        result = {
            "schema_version": SCHEMA_VERSION,
            "transaction_id": transaction_id,
            "contract_tags": contract_tags,
            "request_sha256": normalized_request_sha256,
            "status": "applied",
            "terminal_projection": True,
            "changed_owners": [item.owner for item in changed],
            "skipped_owners": sorted({item.owner for item in rendered if not item.changed}),
            "files": [_minimal_file_result(record) for record in records],
            "files_read": read_count,
            "files_written": len(changed),
            "routing_sources": routing_result,
            "timings_ms": timings,
            "hard_failures": [],
            "writeback": "Writeback: updated " + ", ".join(item.owner for item in changed),
        }
        _write_json_atomic(receipt_path, result)
        _prune_receipts(state_dir, int(manifest.get("runtime", {}).get("receipt_limit", 200)))
        return result


def _prune_receipts(state_dir: Path, limit: int) -> None:
    if limit < 1:
        return
    completed: list[tuple[int, Path]] = []
    transactions = state_dir / "transactions"
    if not transactions.exists():
        return
    for transaction_dir in transactions.iterdir():
        journal_path = transaction_dir / "journal.json"
        receipt_path = transaction_dir / "receipt.json"
        if not journal_path.exists() or not receipt_path.exists():
            continue
        try:
            journal = _json_load(journal_path)
        except GovernanceTransactionError:
            continue
        if journal.get("status") == "completed":
            completed.append((int(journal.get("completed_ns", 0)), transaction_dir))
    for _, path in sorted(completed, reverse=True)[limit:]:
        shutil.rmtree(path, ignore_errors=True)


def recover_transactions(
    project_root: Path, *, state_root: Path | None = None
) -> dict[str, Any]:
    state_dir = project_state_dir(project_root, state_root)
    transactions = state_dir / "transactions"
    recovered: list[str] = []
    unresolved: list[dict[str, Any]] = []
    if not transactions.exists():
        return {"status": "no_change", "recovered": [], "unresolved": []}
    lock_path = state_dir / "active.lock"
    lock_ready, lock_issue = _prepare_recovery_lock(lock_path)
    if not lock_ready:
        return {
            "status": "conflict",
            "recovered": [],
            "unresolved": [{"reason": "recovery_lock", **(lock_issue or {})}],
        }
    try:
        with ProjectLock(lock_path, f"recovery-{os.getpid()}-{time.time_ns()}"):
            for transaction_dir in sorted(transactions.iterdir()):
                journal_path = transaction_dir / "journal.json"
                if not journal_path.exists():
                    continue
                journal = _json_load(journal_path)
                if journal.get("status") not in {"prepared", "committing"}:
                    continue
                safe = True
                conflicts: list[str] = []
                for record in journal.get("files", []):
                    path = _resolve_inside(project_root, record["relative_path"])
                    actual = _current_sha256(path)
                    allowed = {record.get("before_sha256"), record.get("after_sha256"), None}
                    if actual not in allowed:
                        safe = False
                        conflicts.append(record["relative_path"])
                if not safe:
                    unresolved.append(
                        {"transaction_id": journal.get("transaction_id"), "conflicts": conflicts}
                    )
                    continue
                failures = _rollback(project_root, journal, transaction_dir)
                if failures:
                    unresolved.append(
                        {"transaction_id": journal.get("transaction_id"), "rollback_failures": failures}
                    )
                    continue
                journal["status"] = "recovered"
                journal["recovered_ns"] = time.time_ns()
                _write_json_atomic(journal_path, journal)
                recovered.append(str(journal.get("transaction_id")))
    except GovernanceTransactionError as exc:
        if exc.code != "project_locked":
            raise
        return {
            "status": "conflict",
            "recovered": recovered,
            "unresolved": [{"reason": "recovery_lock", "error": exc.message}],
        }
    return {
        "status": "failed" if unresolved else ("applied" if recovered else "no_change"),
        "recovered": recovered,
        "unresolved": unresolved,
    }


def benchmark_receipts(
    project_root: Path, *, state_root: Path | None = None
) -> dict[str, Any]:
    state_dir = project_state_dir(project_root, state_root)
    receipts: list[dict[str, Any]] = []
    for receipt_path in (state_dir / "transactions").glob("*/receipt.json"):
        try:
            receipt = _json_load(receipt_path)
        except GovernanceTransactionError:
            continue
        if isinstance(receipt.get("timings_ms"), dict):
            receipts.append(receipt)
    stages = sorted(
        {stage for receipt in receipts for stage in receipt.get("timings_ms", {}).keys()}
    )
    metrics: dict[str, Any] = {}
    for stage in stages:
        values = [
            float(receipt["timings_ms"][stage])
            for receipt in receipts
            if stage in receipt.get("timings_ms", {})
        ]
        ordered = sorted(values)
        if not ordered:
            continue
        index = max(0, min(len(ordered) - 1, int((len(ordered) - 1) * 0.95 + 0.999999)))
        metrics[stage] = {
            "count": len(ordered),
            "median_ms": statistics.median(ordered),
            "p95_ms": ordered[index],
            "max_ms": max(ordered),
        }
    return {
        "status": "applied" if receipts else "no_change",
        "project_hash": state_dir.name,
        "receipt_count": len(receipts),
        "metrics": metrics,
    }


def manifest_report(
    project_root: Path, manifest_relative: Path = DEFAULT_MANIFEST, *, full_hash: bool = True
) -> dict[str, Any]:
    started = time.perf_counter_ns()
    manifest, manifest_path, manifest_hash = load_manifest(project_root, manifest_relative)
    routing = validate_routing_sources(manifest, project_root, full_hash=full_hash)
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "applied",
        "manifest_sha256": manifest_hash,
        "project_id": manifest["project_id"],
        "project_role": manifest["project_role"],
        "manifest": str(manifest_path.relative_to(project_root.resolve())).replace("\\", "/"),
        "routing_sources": routing,
        "projection_owners": sorted(manifest["projections"]),
        "transaction_contracts": [
            contract["name"] for contract in manifest.get("transaction_contracts", [])
        ],
        "elapsed_ms": (time.perf_counter_ns() - started) / 1_000_000,
    }


def exception_result(exc: GovernanceTransactionError) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "conflict"
        if exc.code
        in {
            "manifest_conflict",
            "routing_source_drift",
            "source_conflict",
            "exact_match_conflict",
            "duplicate_event_conflict",
            "project_locked",
            "transaction_id_conflict",
            "legacy_receipt_conflict",
        }
        else "failed",
        "error_code": exc.code,
        "message": exc.message,
        "details": exc.details,
        "terminal_projection": False,
        "hard_failures": [exc.message],
        "writeback": f"Writeback: deferred because {exc.code}",
    }
