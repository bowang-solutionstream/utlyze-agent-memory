#!/usr/bin/env python3
"""Run an observable CLI round trip only in a new private demo directory."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

REPO=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(REPO))
from utlyze_memory.validation import canonical, digest, path_checked

def run(workdir, case_store=None, carry=()):
    root=path_checked(workdir)
    root.mkdir(parents=True,mode=0o700,exist_ok=False)
    source=root/'intent.md';source.write_text('Synthetic demo objective: trustworthy scoped bootstrap. This is proposed intent, not a product roadmap.\n')
    ref={'path':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
    db=root/'memory.sqlite3';steps=[]
    def cli(op,body):
        argv=[sys.executable,'-m','utlyze_memory','--db',str(db),'--scope','utlyze-eco','--product','memory-demo',op]
        p=subprocess.run(argv,input=canonical(body),capture_output=True,text=True,cwd=REPO,timeout=30)
        step={'argv':argv,'stdin':body,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr};steps.append(step)
        if p.returncode!=0:raise RuntimeError('Direct CLI failed: '+canonical(step))
        result=json.loads(p.stdout);assert result['ok'],result
        return result['result']
    def append(kind,id,data):return cli('append',{'kind':kind,'entity_id':id,'data':data,'event_id':id+'-intent','expected_revision':0})
    cli('init',{});cli('register',{'roots':[str(root)],'case_store':case_store,'case_scope':'utlyze-eco'})
    fact={'kind':'objective','text':'Trustworthy scoped bootstrap','key':'trust','status':'proposed','sources':[ref],'authority':None,'links':[],'acceptance':[],'anchor':True,'conflicts_with':[],'expires_at':None,'candidate':None}
    append('fact','trust',fact)
    pack=cli('context',{'query':'unrelated','max_chars':24000,'carry':list(carry)})
    assert any(i['entity_id']=='trust' for i in pack['items']),pack
    assert 'feature' in pack['unpopulated'] and not pack['product_truth_verified']
    exact=cli('get',{'kind':'fact','entity_id':'trust','revision':1});assert exact['data']['sources']==[ref]
    checkfile=root/'bootstrap-check.json';checkfile.write_text(canonical({'observed':'fresh-process context and exact source reference matched','result':'PASS','pack_sha256':digest(pack),'candidate':'d'*64}))
    checked={'path':str(checkfile),'sha256':hashlib.sha256(checkfile.read_bytes()).hexdigest()}
    task={**fact,'kind':'task','text':'Exercise local context round trip','key':'demo-task','anchor':False,'candidate':'d'*64,'links':['trust'],'acceptance':[{'id':'A1','description':'Fresh subprocess returns the scoped objective and source','checks':['bootstrap_check'],'evidence':[checked]}]}
    append('fact','demo-task',task)
    episode={'task':'demo-task','task_revision':1,'candidate':'d'*64,'attempt':1,'hypothesis':'Explicit source anchors should survive unrelated keyword search','observed_cause':'','outcome':'observed_success','checks':[{'id':'bootstrap_check','outcome':'PASS','evidence':checked}],'sources':[ref,checked],'case_digests':list(carry),'claim_level':'observation'}
    append('episode','demo-attempt',episode)
    retrieval=cli('context',{'query':'trustworthy','max_chars':24000,'carry':list(carry),'task':'demo-task','task_revision':1})
    retrieved=[i['kind']+'/'+i['entity_id']+'@'+str(i['revision']) for i in retrieval['items']]
    append('feedback','demo-feedback',{'pack_sha256':digest(retrieval),'query':'trustworthy','retrieved_ids':retrieved,'used_ids':['fact/trust@1'],'missed_known_ids':[],'rating':'useful','note':'The objective survived a fresh session; feature roadmap remains unknown','task':'demo-task','task_revision':1,'candidate':'d'*64,'actions':[{'description':'Verify bootstrap source link','checks':['bootstrap_check'],'evidence':[checked]}]})
    append('lesson','demo-lesson',{'text':'Keep source anchors independent of query ranking','episodes':['demo-attempt'],'proposed_change':'Consider this invariant in future retrieval reviews','sources':[checked]})
    if case_store:
        consultation=cli('consult',{'query':'deliberate-no-hit-token','carry':list(carry)})
        assert set(carry)<={c['digest'] for c in consultation['cases']},consultation
        assert consultation['status']=='OK',consultation
    cli('integrity',{})
    output=root/'direct-cli-steps.json';output.write_text(canonical(steps));output.chmod(0o600)
    return {'status':'PASS','db':str(db),'steps':len(steps),'raw_steps':str(output),'bootstrap_status':pack['status'],'product_truth_verified':False,'improvement_proven':False}

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--workdir',required=True);parser.add_argument('--case-store');parser.add_argument('--carry',action='append',default=[])
    args=parser.parse_args();print(canonical(run(args.workdir,args.case_store,args.carry)),end='')
