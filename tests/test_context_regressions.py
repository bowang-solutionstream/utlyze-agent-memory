"""Regression outcomes found by independent current decision review."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import uuid

from utlyze_memory import Memory
from utlyze_memory.validation import canonical

HELPER='/Users/studio6/.codex-cli/skills/i2e-failure-cases/scripts/shared_cases.py'

class RetrievalRegressions(unittest.TestCase):
    def test_overflow_fetches_recover_local_applicability_and_regression_duties(self):
        with tempfile.TemporaryDirectory(prefix='memory-overflow-') as temp:
            root=Path(temp).resolve()
            refs=[]
            for i in range(16):
                source=root/('source-'+str(i)+'.md');source.write_text('Synthetic reviewed source '+str(i))
                refs.append({'path':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()})
            store=root/'canonical-cases'
            def helper(*args):
                p=subprocess.run([sys.executable,HELPER,*args],capture_output=True,text=True)
                self.assertEqual(p.returncode,0,p.stderr)
                return json.loads(p.stdout)
            helper('init','--store',str(store))
            case={'schema_version':1,'case_id':str(uuid.uuid4()),'scope':'regression-project','contributor':'synthetic-test','captured_at':'2026-10-30T00:00:00Z','title':'Synthetic delimiter guard','tags':['synthetic'],'applicability':'Synthetic disposable fixture','check_id':'synthetic_guard','classification':{'kind':'product','details':'Synthetic regression fixture'},'expected_behavior':'Preserve the local obligation','actual_behavior':'Synthetic miss','reproduction_steps':['Inert synthetic data'],'origin':{'project_id':'regression-project','task_id':'test','failure_id':'synthetic','broken_source_identity':'synthetic-only'},'evidence_refs':[{'reference':'artifact://synthetic/source','sha256':refs[0]['sha256'],'state':'EXTERNAL_UNVERIFIED'}]}
            case_file=root/'case-input.json';case_file.write_text(canonical(case))
            case_digest=helper('capture','--kind','case','--input',str(case_file),'--store',str(store))['digest']
            Memory.create(root/'memory.sqlite3');memory=Memory(root/'memory.sqlite3')
            try:
                memory.register('regression-project','overflow',[str(root)],str(store),'regression-project')
                for i in range(16):
                    memory.append('regression-project','overflow','fact','anchor'+str(i),{'kind':'objective','text':'Reviewed objective '+('x'*1850),'key':'anchor'+str(i),'sources':refs,'anchor':True},'anchor-'+str(i),0)
                regression='unique-local-regression'
                memory.append('regression-project','overflow','case_link','local-assessment',{'digest':case_digest,'applicability':'APPLIES','regressions':[regression],'sources':[refs[0]]},'local-intent',0)
                pack=memory.context('regression-project','overflow','unmatched-delimiter-token',64000,[])
                recovered=[pack]
                for fetch in pack['fetch_ids']:
                    if fetch.startswith('case/'):
                        result=memory.consult('regression-project','overflow','unmatched-delimiter-token',[fetch[5:]])
                    else:
                        kind,tail=fetch.split('/',1);entity_id,revision=tail.rsplit('@',1)
                        result=memory.get('regression-project','overflow',kind,entity_id,int(revision))
                    recovered.append(result)
                available=canonical(recovered)
                self.assertEqual(pack['status'],'INCOMPLETE')
                self.assertIn('MANDATORY_CONTEXT_EXCEEDS_BUDGET',pack['reasons'])
                self.assertIn(regression,available,'Following every listed fetch must recover the local regression duty')
                self.assertIn('APPLIES',available)
            finally:memory.close()

    def test_exact_task_history_never_revives_withdrawn_authority(self):
        with tempfile.TemporaryDirectory(prefix='memory-lifecycle-') as temp:
            root=Path(temp).resolve();source=root/'source.md';source.write_text('Synthetic reviewed source')
            ref={'path':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
            Memory.create(root/'memory.sqlite3');memory=Memory(root/'memory.sqlite3')
            try:
                memory.register('regression-project','lifecycle',[str(root)])
                def fact(kind,text,status='proposed',links=None):
                    return {'kind':kind,'text':text,'key':kind,'status':status,'sources':[ref],'authority':ref if status=='authoritative' else None,'anchor':False,'links':links or [],'acceptance':[]}
                memory.append('regression-project','lifecycle','fact','objective',fact('objective','Old objective','authoritative'),'objective1',0)
                task=fact('task','Task frozen to old objective',links=['objective'])
                task.update(candidate='a'*64,acceptance=[{'id':'A1','description':'Synthetic scope','checks':['guard'],'evidence':[ref]}])
                memory.append('regression-project','lifecycle','fact','task',task,'task1',0)
                memory.append('regression-project','lifecycle','fact','objective',fact('objective','Withdrawn objective','withdrawn'),'objective2',1)
                pack=memory.context('regression-project','lifecycle','',12000,[],task='task',task_revision=1)
                historical=next(item for item in pack['items'] if item['entity_id']=='objective' and item['revision']==1)
                self.assertEqual(pack['status'],'INCOMPLETE')
                self.assertNotEqual(historical['eligibility'],'current_recorded_authoritative')
                self.assertEqual(historical['lifecycle'],'historical')
                self.assertEqual(historical['current_revision'],2)
                self.assertTrue(any(i['entity_id']=='objective' and i['revision']==2 and i['data']['status']=='withdrawn' for i in pack['items']))
            finally:memory.close()

if __name__=='__main__':unittest.main()
