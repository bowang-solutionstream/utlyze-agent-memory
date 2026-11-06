#!/usr/bin/env python3
"""Local launcher; runtime code stays in the reviewed source repository."""
import os
from pathlib import Path
import sys
repo=Path(os.environ.get('UTLYZE_MEMORY_REPO','/Users/studio6/Documents/DEV/UtlyzeEco/memory-system'))
if not (repo/'utlyze_memory/__main__.py').is_file():
    raise SystemExit('Reviewed memory source missing; set UTLYZE_MEMORY_REPO to its local repository')
sys.path.insert(0,str(repo))
from utlyze_memory.__main__ import main
raise SystemExit(main())
