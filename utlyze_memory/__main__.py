"""Bounded JSON CLI. No stored command execution, providers or background jobs."""
import argparse
import json
from pathlib import Path
import sqlite3
import sys
from . import Memory
from .validation import MemoryError, MAX_INPUT, canonical, fields, loads, read_regular, require

DEFAULT_DB = str(Path.home()/'.local/share/utlyze-memory/memory.sqlite3')

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',default=DEFAULT_DB)
    parser.add_argument('--scope',required=True,help='Explicit project ID')
    parser.add_argument('--product',required=True,help='Explicit product ID within the project')
    parser.add_argument('--input',help='Sanitized JSON file; otherwise bounded stdin')
    parser.add_argument('command',choices=['init','register','append','get','history','context','search','consult','integrity'])
    args=parser.parse_args(argv)
    memory=None
    try:
        raw=read_regular(args.input,MAX_INPUT) if args.input else sys.stdin.buffer.read(MAX_INPUT+1)
        data=loads(raw or b'{}')
        require(type(data) is dict,'JSON input must be an object')
        if args.command=='init':
            fields(data,())
            result=Memory.create(args.db)
        else:
            memory=Memory(args.db)
            prefix=(args.scope,args.product)
            if args.command=='register':
                fields(data,('roots',),('case_store','case_scope'))
                result=memory.register(*prefix,**data)
            elif args.command=='append':
                fields(data,('kind','entity_id','data','event_id','expected_revision'))
                result=memory.append(*prefix,**data)
            elif args.command=='get':
                fields(data,('kind','entity_id'),('revision',))
                result=memory.get(*prefix,**data)
            elif args.command=='history':
                fields(data,('kind','entity_id'),('offset','limit'))
                result=memory.history(*prefix,**data)
            elif args.command in ('context','search'):
                fields(data,(),('query','max_chars','carry','task','task_revision'))
                result=memory.context(*prefix,**data)
            elif args.command=='consult':
                fields(data,(),('query','carry'))
                result=memory.consult(*prefix,**data)
            else:
                fields(data,())
                result=memory.integrity(*prefix)
        print(canonical({'ok':True,'result':result}),end='')
        return 0
    except MemoryError as exc:
        print(canonical({'ok':False,'error':{'code':exc.code,'message':str(exc)}}),end='')
        return 2
    except sqlite3.Error as exc:
        code='BUSY' if 'locked' in str(exc).lower() else 'STORE'
        print(canonical({'ok':False,'error':{'code':code,'message':'Memory transaction unavailable; no reset performed'}}),end='')
        return 2
    except (ValueError,TypeError,KeyError,RecursionError) as exc:
        print(canonical({'ok':False,'error':{'code':'VALIDATION','message':'Invalid bounded input or unsupported value'}}),end='')
        return 2
    except OSError as exc:
        print(canonical({'ok':False,'error':{'code':'STORE','message':'Local file unavailable; no reset performed'}}),end='')
        return 2
    finally:
        if memory is not None:memory.close()

if __name__=='__main__':
    sys.exit(main())
