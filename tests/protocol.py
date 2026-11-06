"""Actual CLI boundary, with explicit unsupported response for the empty baseline.

Once ANY production Python file exists, import/runtime/setup failures are never
caught or converted to UNSUPPORTED. The exact same harness is used on GREEN.
"""
import json
from pathlib import Path
import subprocess
import sys

repo = Path(__file__).resolve().parents[1]
request = json.load(sys.stdin)
if not list((repo / 'utlyze_memory').glob('*.py')):
    print(json.dumps({'ok': False, 'error': {'code': 'UNSUPPORTED', 'message': 'Empty greenfield baseline has no durable memory/context capability'}}))
else:
    args = dict(request['args'])
    db = args.pop('db_override', request['db'])
    launcher = "import importlib.util,runpy;from pathlib import Path;s=importlib.util.find_spec('utlyze_memory');assert s is not None and s.origin is not None and Path(s.origin).resolve().parent == Path('utlyze_memory').resolve(), 'Package must resolve to actual candidate';runpy.run_module('utlyze_memory',run_name='__main__')"
    p = subprocess.run([sys.executable, '-c', launcher, '--db', db, '--scope', request['scope'], '--product', request['product'], request['op']], input=json.dumps(args), capture_output=True, text=True, cwd=repo)
    # A present package must resolve to this actual candidate. Setup/import errors
    # yield a non-JSON failure and remain test errors, not baseline feature RED.
    if not p.stdout:
        sys.stderr.write(p.stderr)
        sys.exit(p.returncode or 1)
    value = json.loads(p.stdout)
    print(json.dumps(value))
