#!/usr/bin/env python3
"""Focused boundary/regression proof on new private data, never stored recipes."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys
from unittest.mock import patch

REPO=Path(__file__).resolve().parents[1];sys.path.insert(0,str(REPO))
from utlyze_memory import Memory,MemoryError
from utlyze_memory import cases
from utlyze_memory.validation import canonical,digest,loads,read_regular,source_state

def evidence(ref,root):
    assert type(ref) is dict and set(ref)=={'reference','sha256'}
    path=Path(ref['reference']);assert path.is_absolute() and path.is_relative_to(root) and path!=root
    assert hashlib.sha256(read_regular(path)).hexdigest()==ref['sha256']

def check_record(path,root):
    record=loads(read_regular(path,2*1024*1024),2*1024*1024)
    count=0
    def walk(value):
        nonlocal count
        if type(value) is dict:
            if 'reference' in value:evidence(value,root);count+=1
            else:
                for child in value.values():walk(child)
        elif type(value) is list:
            for child in value:walk(child)
    walk(record)
    for bad in (None,{}, {'reference':'/outside','sha256':'a'*64}):
        try:evidence(bad,root)
        except (AssertionError,TypeError,KeyError,OSError,ValueError):pass
        else:raise AssertionError('Malformed/unauthorized evidence accepted')
    good=record['contract']['authority']
    try:evidence({**good,'sha256':'0'*64},root)
    except AssertionError:pass
    else:raise AssertionError('Altered evidence accepted')
    return count

def run(root,actual_cases=(),record=None,evidence_root=None):
    root=Path(root);assert root.is_absolute() and not root.exists();root.mkdir(parents=True,mode=0o700)
    source=root/'source.md';source.write_text('Reviewed synthetic contract and observation evidence.\n')
    ref={'path':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
    db=root/'memory.sqlite3';Memory.create(db);m=Memory(db);m.register('utlyze-eco','boundary',[str(root)],cases.DEFAULT_STORE,'utlyze-eco')
    passed=[]
    def rejects(call,code=None):
        try:call()
        except MemoryError as exc:
            if code:assert exc.code==code,(exc.code,code)
        else:raise AssertionError('Invalid boundary accepted')
    def fact(id,text='Synthetic objective',kind='objective',links=None,anchor=False):
        return {'kind':kind,'text':text,'key':id,'status':'proposed','sources':[ref],'links':links or [],'acceptance':[],'anchor':anchor}
    def add(id,data,kind='fact',revision=0):return m.append('utlyze-eco','boundary',kind,id,data,id+'-'+str(revision),revision)
    objective=add('objective',fact('objective',anchor=True))
    add('feature',fact('feature','Synthetic feature','feature',['objective']))
    task=fact('task','Synthetic task','task',['feature']);task.update(candidate='a'*64,acceptance=[{'id':'A1','description':'Exact dependency closure','checks':['closure'],'evidence':[ref]}])
    add('task',task)
    add('objective',fact('objective','Changed objective',anchor=True),revision=1)
    pack=m.context('utlyze-eco','boundary','',24000,[],task='task',task_revision=1)
    exact={(i['entity_id'],i['revision']) for i in pack['items']}
    assert {('objective',1),('objective',2),('feature',1),('task',1)}<=exact
    passed.append('transitive_exact_task_revision_closure')
    for index,kind in enumerate(('symlink','hardlink','directory','fifo','oversized','changed')):
        path=root/('unsafe-'+kind)
        if kind=='symlink':path.symlink_to(source)
        elif kind=='hardlink':os.link(source,path)
        elif kind=='directory':path.mkdir()
        elif kind=='fifo':os.mkfifo(path)
        elif kind=='oversized':path.write_bytes(b'x'*(8*1024*1024+1))
        else:path.write_text('Different bytes')
        bad=fact('bad'+str(index));bad['sources']=[{'path':str(path),'sha256':ref['sha256']}]
        rejects(lambda b=bad,i=index:add('bad'+str(i),b),'EVIDENCE')
        if kind=='hardlink':path.unlink()
    passed.append('unsafe_nonregular_oversized_changed_evidence')
    for raw in (b'{"x":1,"x":2}',b'{"x":NaN}',b'{"x":1e999}',b'x'*65537):rejects(lambda r=raw:loads(r),'VALIDATION')
    passed.append('strict_json_duplicate_nonfinite_oversize')
    for i in range(6):add('unicode'+str(i),fact('unicode'+str(i),'信頼できる文脈'*80,anchor=True))
    compact=m.context('utlyze-eco','boundary','',4096,[])
    assert len(canonical(compact).encode())<=4096 and compact['status']=='INCOMPLETE' and len(compact['fetch_ids'])==7
    passed.append('utf8_budget_and_complete_mandatory_manifest')
    rejects(lambda:cases.consult(cases.DEFAULT_STORE,'x'*65,'scope'), 'VALIDATION')
    passed.append('canonical_scope_limit')
    if actual_cases:
        shown=cases.consult(cases.DEFAULT_STORE,'utlyze-eco','deliberate-nonmatching-token',actual_cases)
        assert shown['status']=='OK' and set(actual_cases)<={c['digest'] for c in shown['cases']}
        (root/'actual-consultation.json').write_text(canonical(shown));(root/'actual-consultation.json').chmod(0o600)
        base_run=cases._run
        def failed_search(argv):
            if argv[2]=='search':return {'argv':argv,'exit_code':1,'stdout':'','stderr':'deliberate negative search fixture'}
            return base_run(argv)
        with patch.object(cases,'_run',failed_search):
            partial=cases.consult(cases.DEFAULT_STORE,'utlyze-eco','synthetic',actual_cases)
        assert partial['status']=='UNAVAILABLE' and set(actual_cases)<={c['digest'] for c in partial['cases']}
        def corrupt_show(argv):
            result=base_run(argv)
            if argv[2]=='show' and result['exit_code']==0:
                malformed=loads(result['stdout'],262144);malformed['record']['title']='Altered canonical bytes';result={**result,'stdout':canonical(malformed)}
            return result
        with patch.object(cases,'_run',corrupt_show):
            corrupt=cases.consult(cases.DEFAULT_STORE,'utlyze-eco','synthetic',actual_cases)
        assert corrupt['status']=='UNAVAILABLE' and not corrupt['cases']
        def missing_shape(argv):
            return {'argv':argv,'exit_code':0,'stdout':'{}\n','stderr':''}
        with patch.object(cases,'_run',missing_shape):
            malformed=cases.consult(cases.DEFAULT_STORE,'utlyze-eco','synthetic',actual_cases)
        assert malformed['status']=='UNAVAILABLE' and not malformed['cases']
        passed.append('canonical_full_show_proof_and_adversarial_outputs')
        case_digest=actual_cases[0]
        add('applies',{'digest':case_digest,'applicability':'APPLIES','regressions':['required_guard'],'sources':[ref]},'case_link')
        add('later-na',{'digest':case_digest,'applicability':'NOT_APPLICABLE','regressions':[],'sources':[ref]},'case_link')
        output=m.context('utlyze-eco','boundary','nothing-matches',64000,[])
        kept=next(c for c in output['cases'] if c['digest']==case_digest)
        assert kept['applicability']=='APPLIES' and 'required_guard' in kept['regressions']
        passed.append('ever_applicable_obligation_monotonicity')
    m.close()
    con=sqlite3.connect(db);con.execute('PRAGMA user_version=2');con.close()
    rejects(lambda:Memory(db),'STORE')
    passed.append('incompatible_schema_rejected_without_reset')
    pointers=check_record(Path(record),Path(evidence_root)) if record else None
    if record:passed.append('immutable_exact_record_evidence_and_negative_controls')
    return {'status':'PASS','checks':passed,'evidence_references':pointers,'private_fixture':str(root),'limits':'Local claims, hashes and fixtures do not authenticate human authority or establish measured improvement.'}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--workdir',required=True);p.add_argument('--actual-case',action='append',default=[]);p.add_argument('--record');p.add_argument('--evidence-root')
    a=p.parse_args();print(canonical(run(a.workdir,a.actual_case,a.record,a.evidence_root)),end='')
