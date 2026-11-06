"""Read-only adapter to the installed canonical store; never executes case data."""
import hashlib
from pathlib import Path
import re
import subprocess
import sys
from .validation import canonical, digest, fields, label, loads, path_checked, require, sequence, sha, text, MemoryError

HELPER = Path('/Users/studio6/.codex-cli/skills/i2e-failure-cases/scripts/shared_cases.py')
DEFAULT_STORE = '/Users/studio6/.local/share/i2e-chat-astra-sol/failure-cases'

def _run(argv):
    p = subprocess.run(argv, capture_output=True, timeout=15)
    require(len(p.stdout) <= 262144 and len(p.stderr) <= 65536, 'Canonical helper output limit', 'LIMIT')
    return {'argv': argv, 'exit_code': p.returncode, 'stdout': p.stdout.decode('utf-8'), 'stderr': p.stderr.decode('utf-8')}

def consult(store, scope, query, carried=(), limit=5):
    label(scope)
    text(query, 1000, empty=True)
    require(type(limit) is int and 1 <= limit <= 5, 'Canonical search limit must be 1–5')
    carried = sorted(set(sha(d) for d in sequence(list(carried), 16)))
    path_checked(store)
    # The canonical helper rejects empty/punctuation-only queries. Disclose the
    # stable keyword used while still showing every exact carried obligation.
    actual_query = query if re.search(r'\w', query, re.UNICODE) else 'memory'
    executions, errors, returned, records = [], [], [], []
    base = [sys.executable, str(HELPER)]
    try:
        execution = _run(base + ['search', '--store', str(store), '--scope', scope, '--query', actual_query, '--include-drafts', '--limit', str(limit)])
        executions.append(execution)
        require(execution['exit_code'] == 0, 'Canonical search unavailable', 'CASE_UNAVAILABLE')
        result = loads(execution['stdout'], 262144)
        require(type(result) is dict and result.get('scope') == scope and result.get('include_drafts') is True, 'Malformed scoped search response', 'CASE_UNAVAILABLE')
        for item in sequence(result.get('results'), 5):
            require(type(item) is dict and item.get('scope') == scope, 'Foreign scope search result', 'CASE_UNAVAILABLE')
            returned.append(sha(item.get('digest')))
        require(len(returned) == len(set(returned)), 'Duplicate canonical search digest', 'CASE_UNAVAILABLE')
    except (MemoryError, OSError, ValueError, subprocess.TimeoutExpired, UnicodeError) as exc:
        errors.append('SEARCH_UNAVAILABLE: ' + type(exc).__name__)
    for case_digest in sorted(set(returned) | set(carried)):
        try:
            execution = _run(base + ['show', '--store', str(store), '--digest', case_digest, '--include-drafts'])
            executions.append(execution)
            require(execution['exit_code'] == 0, 'Canonical show unavailable', 'CASE_UNAVAILABLE')
            shown = loads(execution['stdout'], 262144)
            require(type(shown) is dict and shown.get('digest') == case_digest and shown.get('kind') == 'case', 'Malformed canonical show', 'CASE_UNAVAILABLE')
            record = shown.get('record')
            require(type(record) is dict and record.get('scope') == scope and digest(record) == case_digest, 'Case scope or canonical digest mismatch', 'CASE_UNAVAILABLE')
            require(record.get('schema_version') == 1 and type(record.get('case_id')) is str and type(record.get('title')) is str and type(record.get('check_id')) is str, 'Malformed canonical record', 'CASE_UNAVAILABLE')
            require(type(shown.get('review')) is dict and type(shown['review'].get('state')) is str and type(shown.get('freshness')) is str, 'Malformed canonical wrapper metadata', 'CASE_UNAVAILABLE')
            records.append({'digest': case_digest, 'record': record, 'freshness': shown.get('freshness'), 'review_state': shown.get('review', {}).get('state'), 'include_drafts': True, 'show_sha256': hashlib.sha256(execution['stdout'].encode()).hexdigest()})
        except (MemoryError, OSError, ValueError, subprocess.TimeoutExpired, UnicodeError) as exc:
            errors.append('SHOW_UNAVAILABLE:' + case_digest + ':' + type(exc).__name__)
    return {'status': 'OK' if not errors else 'UNAVAILABLE', 'scope': scope, 'query': query, 'actual_query': actual_query, 'include_drafts': True, 'returned': returned, 'carried': carried, 'cases': records, 'errors': errors, 'executions': executions, 'executions_sha256': digest(executions)}
