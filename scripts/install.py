"""Install reviewed i2e-team bytes locally; retain a guarded rollback receipt.

Receipts and locks are private local consistency records, not signatures or
authorization. Operations never execute package or receipt contents. POSIX only.
"""
import argparse
from contextlib import contextmanager
import ctypes
import errno
import fcntl
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tempfile
import uuid


ROUTE_BLOCK = (
    b"<!-- i2e-team default route: begin -->\n"
    b"For an explicit `i2e-chat-astra-sol` or full-v3 request, use that installed "
    b"profile and its unchanged gates.\n"
    b"For default engineering work in I2E Mode, use "
    b"[$i2e-team](../i2e-team/SKILL.md) and its delivery workflow. "
    b"Preserve the requested read-only, scope, review and action boundaries.\n"
    b"<!-- i2e-team default route: end -->\n\n"
)
PHASES = {"PREPARED", "STAGED", "INSTALLING_PACKAGE", "PACKAGE_INSTALLED",
          "INSTALLING_ROUTER", "INSTALLED", "ROLLING_BACK_ROUTER",
          "ROLLING_BACK_PACKAGE", "ROLLED_BACK"}
RECEIPT_KEYS = {"version", "installation_id", "source_root", "skills_root",
                "state_root", "manifest", "router_before_sha256",
                "router_after_sha256", "router_mode", "binding_sha256", "phase",
                "objects", "directories", "operations"}


class InstallError(ValueError):
    """The requested operation cannot safely use the supplied local state."""


def _sha(data):
    return hashlib.sha256(data).hexdigest()


def _digest(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise InstallError("Expected a lowercase SHA-256 digest")
    return value


def _safe_path(value):
    path = Path(os.path.abspath(os.fspath(value)))
    # macOS system aliases are root-owned platform paths, not package links.
    system_aliases = {Path("/var"): "/private/var", Path("/tmp"): "/private/tmp"}
    for item in reversed((path, *path.parents)):
        if item.is_symlink():
            if (item in system_aliases
                    and (item.parent / os.readlink(item)).resolve() == Path(system_aliases[item])
                    and item.lstat().st_uid == 0):
                continue
            raise InstallError(f"Symlink refused: {item}")
    return path


def _disjoint(state, source, skills):
    for other in (source, skills):
        a, b = state.resolve(), other.resolve()
        if a == b or a in b.parents or b in a.parents:
            raise InstallError("Installation state must be outside source and skills roots")


def _manifest(value):
    if not isinstance(value, dict) or not value or "SKILL.md" not in value:
        raise InstallError("Manifest must be a nonempty file map containing SKILL.md")
    for name, digest in value.items():
        if (not isinstance(name, str) or not name or "\\" in name
                or PurePosixPath(name).is_absolute()
                or any(part in ("", ".", "..") for part in name.split("/"))):
            raise InstallError("Unsafe manifest path")
        _digest(digest)
    return dict(sorted(value.items()))


def _read_regular(path):
    path = _safe_path(path)
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        with os.fdopen(fd, "rb") as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise InstallError(f"Regular file required: {path}")
            return stream.read()
    except OSError as exc:
        raise InstallError(f"Cannot read regular file {path}: {exc}") from exc


def _tree(root, expected=None):
    root = _safe_path(root)
    if not root.is_dir():
        raise InstallError(f"Directory required: {root}")
    allowed_dirs = {"."}
    if expected is not None:
        for name in expected:
            allowed_dirs.update(str(p) for p in PurePosixPath(name).parents)
    result = {}
    for parent, dirs, names in os.walk(root, followlinks=False):
        for name in sorted(dirs + names):
            path = _safe_path(Path(parent) / name)
            mode = path.lstat().st_mode
            relative = path.relative_to(root).as_posix()
            if stat.S_ISDIR(mode):
                if expected is not None and relative not in allowed_dirs:
                    raise InstallError(f"Unexpected directory: {path}")
            elif stat.S_ISREG(mode):
                result[relative] = _sha(_read_regular(path))
            else:
                raise InstallError(f"Unsupported source entry: {path}")
    return dict(sorted(result.items()))


def source_manifest(source_root):
    """Return literal package-relative file hashes; follow no package symlinks."""
    return _manifest(_tree(_safe_path(source_root) / "skills" / "i2e-team"))


def _route(before):
    if b"i2e-team default route:" in before:
        raise InstallError("Router already contains an unowned i2e-team route")
    lines = before.splitlines(keepends=True)
    if not lines or lines[0].rstrip(b"\r\n") != b"---":
        raise InstallError("Router requires YAML frontmatter")
    for index, line in enumerate(lines[1:], 1):
        if line.rstrip(b"\r\n") == b"---":
            position = sum(map(len, lines[:index + 1]))
            if index + 1 < len(lines) and not lines[index + 1].strip():
                position += len(lines[index + 1])
            return before[:position] + ROUTE_BLOCK + before[position:]
    raise InstallError("Router frontmatter is not closed")


def _fsync_dir(path):
    fd = os.open(path, os.O_RDONLY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _exclusive_write(path, data, mode=0o600):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, mode)
    with os.fdopen(fd, "wb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    _fsync_dir(path.parent)


def _atomic_write(path, data, mode=0o600):
    _safe_path(path)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.i2e-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            os.fchmod(stream.fileno(), mode)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        _fsync_dir(path.parent)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def _write_receipt(path, data):
    _atomic_write(path, (json.dumps(data, sort_keys=True, indent=2) + "\n").encode())


def _phase(path, data, phase):
    data["phase"] = phase
    _write_receipt(path, data)


def _binding(data):
    fields = {k: v for k, v in data.items()
              if k not in ("phase", "binding_sha256", "objects", "operations")}
    return _sha(json.dumps(fields, sort_keys=True, separators=(",", ":")).encode())


@contextmanager
def _lock(state, create=False):
    state = _safe_path(state)
    if create:
        state.mkdir(parents=True, mode=0o700, exist_ok=True)
    if not state.is_dir():
        raise InstallError("Existing installation state directory required")
    mode = state.stat()
    if (not stat.S_ISDIR(mode.st_mode) or mode.st_uid != os.getuid()
            or stat.S_IMODE(mode.st_mode) != 0o700):
        raise InstallError("State root must be a private owned 0700 directory")
    lock = _safe_path(state / ".installer.lock")
    fd = os.open(lock, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
            raise InstallError("Unsafe installer lock")
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def _identity(path):
    path = _safe_path(path)
    try:
        info = path.lstat()
    except FileNotFoundError:
        return None
    return [info.st_dev, info.st_ino]


@contextmanager
def _parents(source, destination):
    """Pin both directories so the syscall uses names relative to actual objects."""
    source, destination = _safe_path(source), _safe_path(destination)
    descriptors = []
    try:
        for directory in (source.parent, destination.parent):
            fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            descriptors.append(fd)
            info = os.fstat(fd)
            if [info.st_dev, info.st_ino] != _identity(directory):
                raise InstallError("Directory changed while pinning mutation")
        if os.fstat(descriptors[0]).st_dev != os.fstat(descriptors[1]).st_dev:
            raise OSError(errno.EXDEV, "Recovery must be on the same filesystem")
        yield descriptors[0], source.name, descriptors[1], destination.name
    finally:
        for fd in descriptors:
            os.close(fd)


def _rename_noreplace(source, destination):
    """macOS renameatx_np with RENAME_EXCL; there is no replace fallback.

    Primary contract: apple-oss-distributions/xnu bsd/man/man2/rename.2.
    Flag values/signature also checked against the host SDK sys/stdio.h.
    """
    if sys.platform != "darwin":
        raise InstallError("Exclusive rename primitive is unsupported on this platform")
    try:
        rename = ctypes.CDLL(None, use_errno=True).renameatx_np
    except AttributeError as exc:
        raise InstallError("Exclusive rename primitive is unavailable") from exc
    rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int,
                       ctypes.c_char_p, ctypes.c_uint]
    rename.restype = ctypes.c_int
    with _parents(source, destination) as (sfd, name, dfd, new):
        if rename(sfd, os.fsencode(name), dfd, os.fsencode(new), 0x4 | 0x10):
            error = ctypes.get_errno()
            raise OSError(error, os.strerror(error), str(destination))


def _link_noreplace(source, destination):
    """Publish a retained file inode under an absent name, without replacement."""
    with _parents(source, destination) as (sfd, name, dfd, new):
        os.link(name, new, src_dir_fd=sfd, dst_dir_fd=dfd, follow_symlinks=False)


def _paths(data, receipt):
    skills, private = Path(data["skills_root"]), receipt.parent
    return skills / "i2e-mode" / "SKILL.md", skills / "i2e-team", private


def _check_directories(data):
    for directory, identity in data["directories"].items():
        if _identity(Path(directory)) != identity:
            raise InstallError(f"Pinned directory identity changed: {directory}")


def _sync_operation(operation):
    for directory in sorted({Path(operation["source"]).parent,
                             Path(operation["destination"]).parent}):
        _fsync_dir(directory)


def _operate(receipt, data, kind, source, destination, expected, link=False):
    _check_directories(data)
    operation = {"kind": kind, "source": str(source), "destination": str(destination),
                 "expected": expected, "actual": None, "link": link, "state": "INTENT"}
    data["operations"].append(operation)
    _write_receipt(receipt, data)
    try:
        (_link_noreplace if link else _rename_noreplace)(source, destination)
    except (OSError, InstallError):
        operation["state"] = "BLOCKED"
        _write_receipt(receipt, data)
        raise
    operation["actual"] = _identity(destination)
    _sync_operation(operation)
    operation["state"] = "DONE" if operation["actual"] == expected else "FOREIGN"
    _write_receipt(receipt, data)
    if operation["state"] != "DONE":
        raise InstallError("Captured a different object; retained for conflict recovery")
    _check_directories(data)
    return Path(destination)


def _reconcile(receipt, data):
    """Recover the after-syscall/before-receipt window using pinned object identity."""
    for operation in data["operations"]:
        if operation["state"] == "INTENT":
            actual = _identity(operation["destination"])
            if actual == operation["expected"]:
                _sync_operation(operation)
                operation["actual"], operation["state"] = actual, "DONE"
            elif actual is not None:
                operation["state"] = "BLOCKED"
    _write_receipt(receipt, data)


def _capture(receipt, data, role, live, expected):
    destination = receipt.parent / "captures" / f"{len(data['operations']):06d}-{role}"
    return _operate(receipt, data, "capture_" + role, live, destination, expected)


def _captures(data, role):
    return [Path(op["destination"]) for op in data["operations"]
            if op["kind"] == "capture_" + role and op["actual"] is not None
            and _identity(op["destination"]) == op["actual"]]


def _package_owned(path, data, private):
    return (_identity(path) == data["objects"]["package"]
            and _identity(path / "SKILL.md") == data["objects"]["package_skill"]
            and _identity(private / "anchors" / "package-skill") == data["objects"]["package_skill"])


def _find_package(data, receipt):
    _, target, private = _paths(data, receipt)
    candidates = [target, private / "package-stage", *_captures(data, "package")]
    return next((p for p in candidates if data["objects"]["package"] is not None
                 and _package_owned(p, data, private)), None)


def _result(status, receipt, data, reason=None):
    result = {"status": status, "receipt": str(receipt),
              "generation": data["installation_id"], "retained_paths": [str(receipt.parent)]}
    if reason:
        result["reason"] = reason
    return result


def _restore_pair(receipt, data):
    """Restore package before router on conflict; never consume a competing name."""
    router, target, _ = _paths(data, receipt)
    packages = _captures(data, "package")
    if packages:
        package = packages[-1]
        if _identity(target) is None:
            _operate(receipt, data, "restore_package", package, target, _identity(package))
        elif not _package_owned(target, data, receipt.parent):
            return
    elif _identity(target) is not None and not _package_owned(target, data, receipt.parent):
        return
    routers = _captures(data, "router")
    if routers and _identity(router) is None:
        captured = routers[-1]
        _operate(receipt, data, "restore_router", captured, router, _identity(captured))


def install(source_root, skills_root, state_root, expected_manifest,
            expected_router_sha256):
    """Install one generation, retaining all displaced objects outside discovery.

    Validation/conflicts raise InstallError with the recovery receipt path.
    Noncooperating writers can cause transient missing names; byte retention
    and explicit detected conflicts are guaranteed, not continuous availability.
    """
    source, skills, state = map(_safe_path, (source_root, skills_root, state_root))
    expected = _manifest(expected_manifest)
    _digest(expected_router_sha256)
    _disjoint(state, source, skills)
    if source_manifest(source) != expected:
        raise InstallError("Source differs from reviewed manifest")
    target = _safe_path(skills / "i2e-team")
    router = _safe_path(skills / "i2e-mode" / "SKILL.md")
    _read_regular(skills / "i2e-failure-cases" / "scripts" / "shared_cases.py")
    before = _read_regular(router)
    if _sha(before) != expected_router_sha256:
        raise InstallError("Router differs from expected destination bytes")
    after = _route(before)
    if target.exists():
        raise InstallError("Existing i2e-team destination is unowned")
    with _lock(state, create=True):
        if (state.stat().st_dev != skills.stat().st_dev
                or state.stat().st_dev != router.parent.stat().st_dev):
            raise InstallError("Private recovery must be on the same filesystem")
        if target.exists() or _read_regular(router) != before:
            raise InstallError("Destination changed before installation")
        private = state / str(uuid.uuid4())
        private.mkdir(mode=0o700)
        for name in ("anchors", "captures"):
            (private / name).mkdir(mode=0o700)
        _fsync_dir(state)
        _fsync_dir(private)
        receipt = private / "receipt.json"
        _exclusive_write(private / "router-before.bin", before)
        original_id = _identity(router)
        os.link(router, private / "anchors" / "router-before", follow_symlinks=False)
        _fsync_dir(private / "anchors")
        if _identity(private / "anchors" / "router-before") != original_id:
            raise InstallError(f"Router identity changed; retained={private}")
        data = {"version": 2, "installation_id": private.name,
                "source_root": str(source), "skills_root": str(skills),
                "state_root": str(state), "manifest": expected,
                "router_before_sha256": _sha(before), "router_after_sha256": _sha(after),
                "router_mode": stat.S_IMODE(router.stat().st_mode) & 0o777,
                "objects": {"package": None, "package_skill": None,
                            "router_before": original_id, "router_after": None},
                "directories": {str(path): _identity(path) for path in
                                (state, private, private / "anchors", private / "captures",
                                 skills, router.parent)}, "operations": []}
        data["binding_sha256"] = _binding(data)
        _phase(receipt, data, "PREPARED")
        try:
            stage = private / "package-stage"
            stage.mkdir(mode=0o700)
            _fsync_dir(private)
            package = source / "skills" / "i2e-team"
            for name, digest in expected.items():
                payload = _read_regular(package / name)
                if _sha(payload) != digest:
                    raise InstallError("Source changed while staging")
                destination = stage / name
                destination.parent.mkdir(parents=True, mode=0o755, exist_ok=True)
                _exclusive_write(destination, payload,
                                 stat.S_IMODE((package / name).stat().st_mode) & 0o777)
            if _tree(stage, expected) != expected or source_manifest(source) != expected:
                raise InstallError("Source changed while staging")
            _exclusive_write(private / "router-stage", after, data["router_mode"])
            os.link(stage / "SKILL.md", private / "anchors" / "package-skill", follow_symlinks=False)
            os.link(private / "router-stage", private / "anchors" / "router-after", follow_symlinks=False)
            for directory, _, _ in os.walk(stage, topdown=False):
                _fsync_dir(Path(directory))
            _fsync_dir(private / "anchors")
            data["objects"].update(package=_identity(stage), package_skill=_identity(stage / "SKILL.md"),
                                   router_after=_identity(private / "router-stage"))
            _phase(receipt, data, "STAGED")
            if target.exists() or _read_regular(router) != before or _identity(router) != original_id:
                raise InstallError("Destination changed while staging")
            _phase(receipt, data, "INSTALLING_PACKAGE")
            _operate(receipt, data, "install_package", stage, target, data["objects"]["package"])
            _phase(receipt, data, "PACKAGE_INSTALLED")
            _phase(receipt, data, "INSTALLING_ROUTER")
            captured = _capture(receipt, data, "router", router, original_id)
            if _read_regular(captured) != before or not _package_owned(target, data, private) or not _matches(target, expected):
                raise InstallError("Captured router/package changed before publication")
            _operate(receipt, data, "publish_router", private / "anchors" / "router-after", router,
                     data["objects"]["router_after"], link=True)
            if (_identity(router) != data["objects"]["router_after"] or _read_regular(router) != after
                    or _read_regular(captured) != before or not _package_owned(target, data, private)
                    or not _matches(target, expected)):
                raise InstallError("Observed conflict after publication")
            _phase(receipt, data, "INSTALLED")
            return {**_result("INSTALLED", receipt, data), "manifest": expected,
                    "router_sha256": _sha(after)}
        except (OSError, InstallError) as exc:
            try:
                _restore_pair(receipt, data)
            except (OSError, InstallError):
                pass  # Recovery paths and competing live objects are retained.
            raise InstallError(f"{exc}; receipt={receipt}; retained={private}") from exc


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InstallError("Duplicate JSON key")
        result[key] = value
    return result


def _json(data):
    try:
        return json.loads(data, object_pairs_hook=_unique_object,
                          parse_constant=lambda value: (_ for _ in ()).throw(
                              InstallError(f"Nonfinite JSON value: {value}")))
    except (ValueError, UnicodeError) as exc:
        raise InstallError(f"Invalid JSON: {exc}") from exc


def _receipt(path, state):
    path = _safe_path(path)
    data = _json(_read_regular(path))
    if not isinstance(data, dict) or set(data) != RECEIPT_KEYS:
        raise InstallError("Unsupported receipt fields")
    try:
        identity = str(uuid.UUID(data["installation_id"], version=4))
    except (ValueError, TypeError, AttributeError) as exc:
        raise InstallError("Invalid installation identity") from exc
    if (identity != data["installation_id"] or type(data["version"]) is not int or data["version"] != 2
            or not isinstance(data["phase"], str)
            or data["phase"] not in PHASES or data["state_root"] != str(state)
            or path != state / identity / "receipt.json"
            or data["binding_sha256"] != _binding(data)):
        raise InstallError("Receipt identity or binding mismatch")
    if (type(data["router_mode"]) is not int or not 0 <= data["router_mode"] <= 0o777):
        raise InstallError("Invalid router mode")
    for item in (path.parent, path, path.parent / "router-before.bin"):
        info = item.stat()
        wanted = 0o700 if item == path.parent else 0o600
        if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != wanted:
            raise InstallError("Receipt and backup must be private and locally owned")
    for key in ("router_before_sha256", "router_after_sha256", "binding_sha256"):
        _digest(data[key])
    data["manifest"] = _manifest(data["manifest"])
    source, skills = _safe_path(data["source_root"]), _safe_path(data["skills_root"])
    _disjoint(state, source, skills)
    before = _read_regular(path.parent / "router-before.bin")
    if _sha(before) != data["router_before_sha256"] or _sha(_route(before)) != data["router_after_sha256"]:
        raise InstallError("Router backup does not match receipt")
    objects = data["objects"]
    if (not isinstance(objects, dict) or set(objects) != {"package", "package_skill", "router_before", "router_after"}
            or not isinstance(data["directories"], dict) or not isinstance(data["operations"], list)):
        raise InstallError("Invalid object or operation records")
    def valid_identity(value):
        return (isinstance(value, list) and len(value) == 2
                and all(type(number) is int and number >= 0 for number in value))
    if any(value is not None and not valid_identity(value) for value in objects.values()):
        raise InstallError("Invalid filesystem identity")
    expected_dirs = {str(p) for p in (state, path.parent, path.parent / "anchors",
                                     path.parent / "captures", skills, skills / "i2e-mode")}
    if set(data["directories"]) != expected_dirs or any(not valid_identity(v) for v in data["directories"].values()):
        raise InstallError("Invalid pinned directory identities")
    _check_directories(data)
    for key, anchor in (("router_before", "router-before"), ("router_after", "router-after"),
                         ("package_skill", "package-skill")):
        if objects[key] is not None and _identity(path.parent / "anchors" / anchor) != objects[key]:
            raise InstallError("Missing or replaced persistent inode anchor")
    allowed_kinds = {"install_package", "capture_router", "capture_package", "publish_router",
                     "restore_original", "restore_router", "restore_package"}
    for operation in data["operations"]:
        if (not isinstance(operation, dict)
                or set(operation) != {"kind", "source", "destination", "expected", "actual", "link", "state"}
                or not isinstance(operation["kind"], str) or operation["kind"] not in allowed_kinds
                or not isinstance(operation["state"], str)
                or operation["state"] not in {"INTENT", "DONE", "FOREIGN", "BLOCKED"}
                or type(operation["link"]) is not bool or not valid_identity(operation["expected"])
                or (operation["actual"] is not None and not valid_identity(operation["actual"]))):
            raise InstallError("Malformed operation intent")
        for key in ("source", "destination"):
            value = operation[key]
            if not isinstance(value, str) or not Path(value).is_absolute():
                raise InstallError("Invalid operation path")
            candidate = _safe_path(value)
            if candidate not in (skills / "i2e-team", skills / "i2e-mode" / "SKILL.md"):
                if path.parent not in candidate.parents:
                    raise InstallError("Operation escapes installation recovery")
    return data, before, skills


def _matches(path, expected, partial=False):
    _safe_path(path)
    if not path.exists():
        return True
    actual = _tree(path, expected)
    return (all(expected.get(k) == v for k, v in actual.items())
            if partial else actual == expected)


def rollback(receipt, state_root):
    """Capture/verify the dependency pair, restore exclusively, retain every object.

    Original routes, retired packages and anchors are retained indefinitely.
    No automatic garbage collection or destructive recursive removal occurs.
    """
    state, receipt = _safe_path(state_root), _safe_path(receipt)
    with _lock(state):
        data, before, skills = _receipt(receipt, state)
        _reconcile(receipt, data)
        router, target, private = _paths(data, receipt)
        try:
            objects = data["objects"]
            router_id, target_id = _identity(router), _identity(target)
            original = router_id == objects["router_before"] and _read_regular(router) == before
            if data["phase"] == "ROLLED_BACK":
                return _result("ALREADY_ROLLED_BACK" if original and target_id is None else "CONFLICT",
                               receipt, data)
            conflict_package_restored = any(
                op["kind"] == "restore_package" and op["state"] == "DONE"
                and op["actual"] == objects["package"] for op in data["operations"])
            if (conflict_package_restored and router_id is None
                    and _package_owned(target, data, private)):
                # Conflict recovery deliberately preserves the edited package.
                # Resume its captured router before the normal byte-drift guard.
                _restore_pair(receipt, data)
                return _result("CONFLICT", receipt, data, "Resumed retained conflict-pair restoration")
            if target_id is not None and (not _package_owned(target, data, private)
                                          or not _matches(target, data["manifest"])):
                return _result("CONFLICT", receipt, data, "Live package is changed or belongs to another generation")
            if router_id is not None:
                expected_hash = (data["router_before_sha256"] if router_id == objects["router_before"]
                                 else data["router_after_sha256"] if router_id == objects["router_after"] else None)
                if expected_hash is None or _sha(_read_regular(router)) != expected_hash:
                    return _result("CONFLICT", receipt, data, "Live router changed or belongs to another generation")
            promoted = any(op["kind"] == "install_package" and op["state"] == "DONE"
                           for op in data["operations"])
            if not promoted and target_id is None and original:
                _phase(receipt, data, "ROLLED_BACK")
                return _result("ROLLED_BACK", receipt, data)
            # A completed restore may have been interrupted before its final receipt.
            restored = any(op["kind"] == "restore_original" and op["state"] == "DONE"
                           for op in data["operations"])
            if original and target_id is None and restored:
                _phase(receipt, data, "ROLLED_BACK")
                return _result("ROLLED_BACK", receipt, data)
            package = _find_package(data, receipt)
            if promoted and package is None:
                return _result("CONFLICT", receipt, data, "Owned package location is unavailable")
            _phase(receipt, data, "ROLLING_BACK_ROUTER")
            if router_id is not None:
                captured_router = _capture(receipt, data, "router", router, router_id)
            else:
                candidates = _captures(data, "router")
                captured_router = candidates[-1] if candidates else None
            _phase(receipt, data, "ROLLING_BACK_PACKAGE")
            if target_id is not None:
                package = _capture(receipt, data, "package", target, objects["package"])
            if captured_router is None or _identity(captured_router) not in (objects["router_before"], objects["router_after"]):
                raise InstallError("Captured router identity is unavailable")
            captured_hash = (data["router_before_sha256"] if _identity(captured_router) == objects["router_before"]
                             else data["router_after_sha256"])
            if (_sha(_read_regular(captured_router)) != captured_hash
                    or package is None or not _package_owned(package, data, private)
                    or not _matches(package, data["manifest"])
                    or _read_regular(private / "anchors" / "router-before") != before):
                raise InstallError("Captured router/package pair changed; retaining both")
            _operate(receipt, data, "restore_original", private / "anchors" / "router-before", router,
                     objects["router_before"], link=True)
            if _identity(router) != objects["router_before"] or _read_regular(router) != before or _identity(target) is not None:
                raise InstallError("Observed conflict after original route restoration")
            _phase(receipt, data, "ROLLED_BACK")
            return _result("ROLLED_BACK", receipt, data)
        except (InstallError, OSError) as exc:
            try:
                _restore_pair(receipt, data)
            except (InstallError, OSError):
                pass
            return _result("CONFLICT", receipt, data, str(exc))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    manifest = commands.add_parser("manifest", help="Hash the exact source package")
    manifest.add_argument("--source-root", required=True)
    activate = commands.add_parser("install", help="Install reviewed local bytes")
    for option in ("source-root", "skills-root", "state-root", "manifest", "expected-router-sha256"):
        activate.add_argument(f"--{option}", required=True)
    undo = commands.add_parser("rollback", help="Guarded recovery from any receipt phase")
    undo.add_argument("--receipt", required=True)
    undo.add_argument("--state-root", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "manifest":
            result = source_manifest(args.source_root)
        elif args.command == "install":
            result = install(args.source_root, args.skills_root, args.state_root,
                             _json(_read_regular(Path(args.manifest))), args.expected_router_sha256)
        else:
            result = rollback(args.receipt, args.state_root)
        print(json.dumps(result, sort_keys=True))
        return 2 if result.get("status") == "CONFLICT" else 0
    except (InstallError, OSError) as exc:
        print(json.dumps({"status": "REFUSED", "error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
