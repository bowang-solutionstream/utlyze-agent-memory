"""Strict local boundaries. Hash identity is evidence, never source authority."""
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat

MAX_INPUT = 65536
MAX_EVIDENCE = 8 * 1024 * 1024
LABEL = re.compile(r'[a-z0-9][a-z0-9._-]{0,63}\Z')
SHA = re.compile(r'[0-9a-f]{64}\Z')
SECRET = re.compile(r'-----BEGIN .*PRIVATE KEY-----|\b(?:sk-[A-Za-z0-9_-]{16,}|AKIA[A-Z0-9]{16})\b|\b(?:password|api[_-]?key|access[_-]?token)\s*[:=]\s*\S+|\bBearer\s+\S+', re.I)

class MemoryError(ValueError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code

def require(ok, message, code='VALIDATION'):
    if not ok:
        raise MemoryError(code, message)

def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n'

def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()

def loads(raw, limit=MAX_INPUT):
    if isinstance(raw, str):
        raw = raw.encode()
    require(type(raw) is bytes and len(raw) <= limit, 'JSON input exceeds supported byte limit')
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'Duplicate JSON key')
            result[key] = value
        return result
    def finite(value):
        number=float(value)
        require(math.isfinite(number),'Nonfinite JSON number')
        return number
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_float=finite, parse_constant=lambda _: require(False, 'Nonfinite JSON number'))
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise MemoryError('VALIDATION', 'Invalid bounded UTF-8 JSON') from exc

def fields(value, required, optional=()):
    require(type(value) is dict and set(required) <= set(value) <= set(required) | set(optional), 'Missing or unsupported fields')
    return value

def label(value):
    require(type(value) is str and LABEL.fullmatch(value), 'Expected lowercase safe identifier, 1–64 characters')
    return value

def sha(value):
    require(type(value) is str and SHA.fullmatch(value), 'Expected lowercase SHA-256')
    return value

def text(value, limit=2000, empty=False):
    require(type(value) is str and (empty or bool(value.strip())) and len(value.encode()) <= limit and '\0' not in value, 'Expected bounded reviewed text')
    require(not SECRET.search(value), 'Secret-like input refused; provide a sanitized statement')
    return value

def sequence(value, limit=32, nonempty=False):
    require(type(value) is list and len(value) <= limit and (not nonempty or bool(value)), 'Expected bounded list')
    return value

def integer(value, minimum=0, maximum=10000):
    require(type(value) is int and minimum <= value <= maximum, 'Integer outside supported bounds')
    return value

def timestamp(value):
    require(type(value) is str and value.endswith('Z'), 'Expected UTC timestamp ending Z')
    try:
        result = datetime.fromisoformat(value[:-1] + '+00:00')
    except ValueError as exc:
        raise MemoryError('VALIDATION', 'Invalid UTC timestamp') from exc
    require(result.utcoffset().total_seconds() == 0, 'UTC required')
    return result

def now():
    return datetime.now(timezone.utc).isoformat(timespec='microseconds').replace('+00:00', 'Z')

def path_checked(value):
    require(type(value) in (str, Path) or isinstance(value, Path), 'Expected local path', 'EVIDENCE')
    path = Path(value)
    require(path.is_absolute() and '..' not in path.parts, 'Absolute literal path required', 'EVIDENCE')
    for part in (path, *path.parents):
        require(not part.is_symlink(), 'Symlink path refused', 'EVIDENCE')
    return path

def read_regular(value, limit=MAX_EVIDENCE):
    path = path_checked(value)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    with os.fdopen(fd, 'rb') as stream:
        before = os.fstat(stream.fileno())
        require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= limit, 'Nonregular, linked or oversized evidence refused', 'EVIDENCE')
        raw = stream.read(limit + 1)
        after = os.fstat(stream.fileno())
    require(len(raw) <= limit and (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), 'Evidence changed while reading', 'EVIDENCE')
    return raw

def reference(value):
    fields(value, ('path', 'sha256'))
    path_checked(value['path'])
    sha(value['sha256'])
    return value

def references(value):
    if type(value) is dict:
        if set(value) == {'path', 'sha256'}:
            yield value  # Stored refs were schema-checked on append; current filesystem state is assessed by source_state.
        else:
            for item in value.values():
                yield from references(item)
    elif type(value) is list:
        for item in value:
            yield from references(item)

def source_state(ref, roots):
    try:
        reference(ref)
        path = path_checked(ref['path'])
        require(any(path != Path(root) and path.is_relative_to(root) for root in roots), 'Evidence outside configured roots', 'EVIDENCE')
        actual = hashlib.sha256(read_regular(path)).hexdigest()
        state = 'CURRENT' if actual == ref['sha256'] else 'CHANGED'
    except FileNotFoundError:
        state = 'MISSING'
    except (MemoryError, OSError, ValueError):
        state = 'UNSAFE_OR_UNREADABLE'
    return {'path': ref['path'], 'state': state}

def verify_references(value, roots):
    for ref in references(value):
        require(source_state(ref, roots)['state'] == 'CURRENT', 'Evidence missing, changed, unsafe or outside configured roots', 'EVIDENCE')
