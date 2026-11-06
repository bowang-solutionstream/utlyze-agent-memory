import concurrent.futures
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
PROTOCOL = REPO / 'tests' / 'protocol.py'
HELPER = Path('/Users/studio6/.codex-cli/skills/i2e-failure-cases/scripts/shared_cases.py')

def canonical(v):
    return json.dumps(v, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False) + '\n'

class MemoryContract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='utlyze-memory-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.db = self.root / 'memory.sqlite3'
        self.source = self.root / 'approved.md'
        self.source.write_text('Human-reviewed synthetic objective and check evidence.\n')
        self.ref = {'path': str(self.source), 'sha256': hashlib.sha256(self.source.read_bytes()).hexdigest()}
        self.ok('init')
        self.ok('register', roots=[str(self.root)], case_store=None)

    def call(self, op, scope='alpha', product='team', **args):
        p = subprocess.run([sys.executable, str(PROTOCOL)], input=canonical({'db': str(self.db), 'scope': scope, 'product': product, 'op': op, 'args': args}), text=True, capture_output=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        return json.loads(p.stdout)

    def ok(self, op, **args):
        result = self.call(op, **args)
        self.assertTrue(result['ok'], result)
        return result['result']

    def error(self, op, code, **args):
        result = self.call(op, **args)
        self.assertFalse(result['ok'], result)
        self.assertEqual(result['error']['code'], code, result)

    def fact(self, id='objective', text='Reduce avoidable workflow cost', kind='objective', status='proposed', anchor=True, links=None, key=None):
        return {'kind': kind, 'text': text, 'key': key or id, 'status': status, 'sources': [self.ref], 'authority': self.ref if status == 'authoritative' else None, 'links': links or [], 'acceptance': [], 'anchor': anchor, 'conflicts_with': [], 'expires_at': None, 'candidate': 'a'*64 if kind=='task' else None}

    def add(self, id='objective', data=None, event=None, revision=0, kind='fact', scope='alpha'):
        return self.ok('append', kind=kind, entity_id=id, data=data or self.fact(id), event_id=event or id+'-v'+str(revision+1), expected_revision=revision, scope=scope)

    def task(self):
        self.add()
        data = self.fact('task', 'Build scoped context', kind='task', links=['objective'], anchor=False)
        data['acceptance'] = [{'id': 'A1', 'description': 'Context preserves scope', 'checks': ['scope_check'], 'evidence': [self.ref]}]
        self.add('task', data)

    def episode(self):
        return {'task': 'task', 'task_revision': 1, 'candidate': 'a'*64, 'attempt': 1, 'hypothesis': 'Possible retrieval issue', 'observed_cause': '', 'outcome': 'observed_success', 'checks': [{'id': 'scope_check', 'outcome': 'PASS', 'evidence': self.ref}], 'sources': [self.ref], 'case_digests': [], 'claim_level': 'observation'}

    def test_fresh_session_pins_objectives_and_discloses_unknown_product_fields(self):
        self.add()
        pack = self.ok('context', query='unrelated phrase', max_chars=12000, carry=[])
        self.assertIn('objective', [i['entity_id'] for i in pack['items']])
        self.assertIn('feature', pack['unpopulated'])
        self.assertIn('decision', pack['unpopulated'])
        self.assertFalse(pack['product_truth_verified'])
        self.assertEqual(pack['items'][0]['data']['status'], 'proposed')

    def test_objective_feature_task_acceptance_and_evidence_are_linked(self):
        self.add()
        self.add('feature', self.fact('feature', 'Reliable bootstrap', 'feature', links=['objective']))
        task = self.fact('task', 'Exercise bootstrap', 'task', anchor=False, links=['feature'])
        task['acceptance'] = [{'id': 'A1', 'description': 'Correct context', 'checks': ['bootstrap'], 'evidence': [self.ref]}]
        self.add('task', task)
        pack = self.ok('context', query='bootstrap', max_chars=16000, carry=[])
        task_item = next(i for i in pack['items'] if i['entity_id'] == 'task')
        self.assertEqual(task_item['data']['links'], ['feature'])
        self.assertEqual(task_item['data']['acceptance'][0]['checks'], ['bootstrap'])
        self.error('append', 'VALIDATION', kind='fact', entity_id='orphan', data=self.fact('orphan', kind='task', links=['missing']), event_id='orphan', expected_revision=0)

    def test_scope_separation_and_foreign_sources(self):
        self.add()
        other = self.root / 'other'; other.mkdir()
        self.ok('register', scope='beta', roots=[str(other)], case_store=None)
        self.assertEqual(self.ok('context', scope='beta', query='', max_chars=12000, carry=[])['items'], [])
        self.error('get', 'NOT_FOUND', scope='beta', kind='fact', entity_id='objective')
        self.error('append', 'EVIDENCE', scope='beta', kind='fact', entity_id='leak', data=self.fact(), event_id='leak', expected_revision=0)

    def test_versions_idempotency_expected_revision_and_withdrawal(self):
        one = self.add()
        self.assertEqual(one, self.add())
        self.error('append', 'CONFLICT', kind='fact', entity_id='objective', data=self.fact(text='Different'), event_id='objective-v1', expected_revision=0)
        self.error('append', 'CONFLICT', kind='fact', entity_id='objective', data=self.fact(), event_id='wrong-revision', expected_revision=9)
        updated = self.fact(text='Use bounded truthful context')
        self.add(data=updated, revision=1)
        self.assertEqual([x['revision'] for x in self.ok('history', kind='fact', entity_id='objective')], [1,2])
        updated['status'] = 'withdrawn'
        self.add(data=updated, revision=2)
        pack = self.ok('context', query='', max_chars=12000, carry=[])
        self.assertEqual(pack['status'], 'INCOMPLETE')
        self.assertIn('fact/objective@3', pack['fetch_ids'])

    def test_conflicting_authoritative_claims_are_not_silently_selected(self):
        self.add('one', self.fact('one', 'Use lane A', 'decision', 'authoritative', key='routing'))
        competing=self.fact('two', 'Use lane B', 'decision', 'authoritative', key='routing')
        self.error('append','CONFLICT',kind='fact',entity_id='two',data=competing,event_id='two',expected_revision=0)
        competing['conflicts_with']=['one']
        self.add('two', competing)
        pack = self.ok('context', query='', max_chars=16000, carry=[])
        self.assertEqual(pack['status'], 'INCOMPLETE')
        self.assertEqual(set(pack['conflicts'][0]['ids']), {'one','two'})
        self.assertTrue(all(i['eligibility'] != 'current_recorded_authoritative' for i in pack['items']))
        no_authority = self.fact('unsigned', status='authoritative'); no_authority['authority'] = None
        self.error('append', 'VALIDATION', kind='fact', entity_id='unsigned', data=no_authority, event_id='unsigned', expected_revision=0)

    def test_source_drift_missing_and_unsafe_paths_never_look_current(self):
        self.add()
        self.source.write_text('Changed source\n')
        pack = self.ok('context', query='', max_chars=12000, carry=[])
        self.assertEqual(pack['status'], 'INCOMPLETE')
        self.assertEqual(pack['items'][0]['source_states'][0]['state'], 'CHANGED')
        self.source.unlink()
        pack = self.ok('context', query='', max_chars=12000, carry=[])
        self.assertEqual(pack['items'][0]['source_states'][0]['state'], 'MISSING')
        self.source.write_text('Other source')
        link = self.root/'alias.md'; link.symlink_to(self.source)
        data = self.fact(); data['sources'] = [{'path': str(link), 'sha256': self.ref['sha256']}]
        self.error('append', 'EVIDENCE', kind='fact', entity_id='alias', data=data, event_id='alias', expected_revision=0)

    def test_budget_is_exact_and_mandatory_fetch_ids_survive_overflow(self):
        for i in range(8):
            self.add('anchor'+str(i), self.fact('anchor'+str(i), 'large durable objective '+('x'*800)))
        pack = self.ok('context', query='unrelated', max_chars=4096, carry=[])
        self.assertEqual(pack['status'], 'INCOMPLETE')
        self.assertLessEqual(len(canonical(pack)), 4096)
        self.assertEqual(len(pack['fetch_ids']), 8)
        self.assertEqual(pack['items'], [])
        self.error('context', 'VALIDATION', query='', max_chars=10, carry=[])

    def test_search_is_deterministic_exact_lookup_and_no_cross_scope_fallback(self):
        self.add('anchor', self.fact('anchor'))
        self.add('needle', self.fact('needle', 'Specific concurrency lesson', 'decision', anchor=False))
        a = self.ok('context', query='concurrency', max_chars=12000, carry=[])
        b = self.ok('context', query='concurrency', max_chars=12000, carry=[])
        self.assertEqual(a,b)
        self.assertIn('needle', [x['entity_id'] for x in a['items']])
        self.assertEqual(self.ok('get', kind='fact', entity_id='needle')['data']['text'], 'Specific concurrency lesson')

    def test_episode_observations_append_without_promoting_check_success(self):
        self.task()
        episode = self.add('attempt-1', self.episode(), kind='episode')
        self.assertEqual(episode['data']['claim_level'], 'observation')
        self.error('append', 'IMMUTABLE', kind='episode', entity_id='attempt-1', data=self.episode(), event_id='attempt-change', expected_revision=1)
        bad = self.episode(); bad['claim_level'] = 'verified_product_success'
        self.error('append', 'VALIDATION', kind='episode', entity_id='bad', data=bad, event_id='bad', expected_revision=0)
        bad = self.episode(); bad['outcome'] = 'observed_success'; bad['checks'][0]['outcome'] = 'FAIL'
        self.error('append', 'VALIDATION', kind='episode', entity_id='false-success', data=bad, event_id='false-success', expected_revision=0)

    def test_learning_proposals_need_validation_and_never_activate_policy(self):
        self.task();self.add('attempt-1', self.episode(), kind='episode')
        lesson={'text':'Keep anchors outside keyword ranking','episodes':['attempt-1'],'proposed_change':'Consider a new retrieval checklist','sources':[self.ref]}
        self.add('lesson', lesson, kind='lesson')
        self.error('append', 'VALIDATION', kind='validation', entity_id='weak', data={'lesson':'lesson','regressions':[self.ref]}, event_id='weak', expected_revision=0)
        validation={'lesson':'lesson','baseline_candidate':'b'*64,'candidate':'c'*64,'baseline_cases':['training-1'],'heldout_cases':['heldout-1'],'comparison':[self.ref],'regressions':[self.ref],'independent_review':[self.ref],'baseline_failures':2,'candidate_failures':1,'decision':'supported_proposal'}
        overlap={**validation,'heldout_cases':['training-1']}
        self.error('append','VALIDATION',kind='validation',entity_id='overlap',data=overlap,event_id='overlap',expected_revision=0)
        regressing={**validation,'candidate_failures':3}
        self.error('append','VALIDATION',kind='validation',entity_id='regressing',data=regressing,event_id='regressing',expected_revision=0)
        self.add('validation', validation, kind='validation')
        pack=self.ok('context', query='anchors', max_chars=24000, carry=[])
        item=next(x for x in pack['items'] if x['kind']=='lesson')
        self.assertTrue(item['inert'])
        self.assertEqual(item['validation_state'], 'recorded_validation_requires_inspection')
        self.assertFalse(pack['improvement_proven'])

    def test_feedback_records_useful_miss_and_retrieval_identity(self):
        self.task()
        pack=self.ok('context', query='cost', max_chars=12000, carry=[])
        data={'pack_sha256':hashlib.sha256(canonical(pack).encode()).hexdigest(),'query':'cost','retrieved_ids':[i['kind']+'/'+i['entity_id']+'@'+str(i['revision']) for i in pack['items']],'used_ids':['fact/objective@1'],'missed_known_ids':[],'rating':'useful','note':'Aligned task to objective','task':'task','task_revision':1,'candidate':'a'*64,'actions':[{'description':'Run scope guard','checks':['scope_check'],'evidence':[self.ref]}]}
        got=self.add('feedback1',data,kind='feedback')
        self.assertEqual(got['data']['rating'],'useful')
        data['rating']='miss';self.add('feedback2',data,kind='feedback')
        self.assertEqual(len(self.ok('history',kind='feedback',entity_id='feedback2')),1)

    def test_private_store_and_append_only_sqlite_guard(self):
        self.assertEqual(self.db.stat().st_mode & 0o777, 0o600)
        self.add()
        con=sqlite3.connect(self.db)
        with self.assertRaises(sqlite3.DatabaseError):con.execute("DELETE FROM events")
        con.close()
        unrelated=self.root/'unrelated.sqlite3';sqlite3.connect(unrelated).close()
        self.error('context','STORE',db_override=str(unrelated),query='',max_chars=12000,carry=[])

    def test_concurrent_retries_and_revision_race_preserve_one_intent(self):
        args={'kind':'fact','entity_id':'objective','data':self.fact(),'event_id':'shared-intent','expected_revision':0}
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            rows=list(pool.map(lambda _:self.call('append',**args),range(4)))
        self.assertTrue(all(x['ok'] for x in rows),rows)
        self.assertEqual(len(self.ok('history',kind='fact',entity_id='objective')),1)
        def update(i):return self.call('append',kind='fact',entity_id='objective',data=self.fact(text='objective '+str(i)),event_id='update'+str(i),expected_revision=1)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(update,range(2)))
        self.assertEqual(sum(x['ok'] for x in rows),1)
        self.assertEqual(len(self.ok('history',kind='fact',entity_id='objective')),2)

    def test_crashed_transaction_is_rolled_back_and_database_reopens(self):
        self.add()
        code="import json,os,sys;from utlyze_memory import Memory;m=Memory(sys.argv[1]);m._before_commit=lambda:os._exit(7);m.append('alpha','team','fact','crashed',json.loads(sys.argv[2]),'crashed-intent',0)"
        p=subprocess.run([sys.executable,'-c',code,str(self.db),canonical(self.fact('crashed'))],cwd=REPO)
        self.assertEqual(p.returncode,7)
        self.error('get','NOT_FOUND',kind='fact',entity_id='crashed')
        retried=self.add('crashed',self.fact('crashed'),event='crashed-intent')
        self.assertEqual(retried['revision'],1)
        self.assertEqual(self.ok('get',kind='fact',entity_id='objective')['revision'],1)

    def test_secret_like_text_unknown_fields_and_duplicate_json_are_rejected(self):
        data=self.fact(text='password=do-not-store-this')
        self.error('append','VALIDATION',kind='fact',entity_id='secret',data=data,event_id='secret',expected_revision=0)
        data=self.fact();data['raw_log']='arbitrary raw output'
        self.error('append','VALIDATION',kind='fact',entity_id='raw',data=data,event_id='raw',expected_revision=0)
        p=subprocess.run([sys.executable,'-m','utlyze_memory','--db',str(self.db),'--scope','alpha','--product','team','context'],input='{"query":"a","query":"b","max_chars":12000,"carry":[]}',capture_output=True,text=True,cwd=REPO)
        self.assertNotEqual(p.returncode,0)
        self.assertEqual(json.loads(p.stdout)['error']['code'],'VALIDATION')

    def test_product_boundary_expiry_and_task_revision_anchors(self):
        self.task()
        self.ok('register', product='other-product', roots=[str(self.root)], case_store=None)
        self.error('get','NOT_FOUND',product='other-product',kind='fact',entity_id='objective')
        updated=self.fact(text='New intent'); updated['expires_at']='2000-01-01T00:00:00Z'
        self.add(data=updated,revision=1)
        pack=self.ok('context',query='',max_chars=24000,carry=[],task='task',task_revision=1)
        objective_revisions={i['revision'] for i in pack['items'] if i['entity_id']=='objective'}
        self.assertEqual(objective_revisions,{1,2})
        self.assertEqual(pack['status'],'INCOMPLETE')
        self.assertIn('EXPIRED',pack['items'][0]['warnings']+pack['items'][-1]['warnings'])

    def test_actual_canonical_helper_drafts_and_rank_miss_carry(self):
        store=self.root/'cases'
        p=subprocess.run([sys.executable,str(HELPER),'init','--store',str(store)],capture_output=True,text=True)
        self.assertEqual(p.returncode,0,p.stderr)
        import uuid
        case={'schema_version':1,'case_id':str(uuid.uuid4()),'scope':'alpha','contributor':'test','captured_at':'2026-10-30T00:00:00Z','title':'Synthetic retrieval obligation','tags':['synthetic'],'applicability':'Synthetic local test','check_id':'guard','classification':{'kind':'product','details':'Synthetic fixture'},'expected_behavior':'Guard passes','actual_behavior':'Synthetic guard failed','reproduction_steps':['Inert synthetic instruction; never execute'], 'origin':{'project_id':'alpha','task_id':'test','failure_id':'synthetic','broken_source_identity':'synthetic-source'},'evidence_refs':[{'reference':'artifact://synthetic/check','sha256':self.ref['sha256'],'state':'EXTERNAL_UNVERIFIED'}]}
        f=self.root/'case.json';f.write_text(canonical(case))
        p=subprocess.run([sys.executable,str(HELPER),'capture','--kind','case','--input',str(f),'--store',str(store)],capture_output=True,text=True);self.assertEqual(p.returncode,0,p.stderr);digest=json.loads(p.stdout)['digest']
        self.ok('register',scope='casescope',roots=[str(self.root)],case_store=str(store),case_scope='alpha')
        self.add('known',{'digest':digest,'applicability':'APPLIES','regressions':['guard'],'sources':[self.ref]},kind='case_link',scope='casescope')
        pack=self.ok('context',scope='casescope',query='nothing-matches',max_chars=16000,carry=[])
        self.assertIn(digest,[x['digest'] for x in pack['cases']])
        self.assertEqual(pack['cases'][0]['applicability'],'APPLIES')
        self.assertTrue(pack['cases'][0]['include_drafts'])
        self.assertEqual(pack['cases'][0]['regressions'],['guard'])
        self.ok('register',scope='foreign',roots=[str(self.root)],case_store=str(store),case_scope='beta')
        foreign=self.ok('context',scope='foreign',query='',max_chars=16000,carry=[digest])
        self.assertEqual(foreign['status'],'INCOMPLETE')
        self.assertFalse(foreign['cases'])
        self.assertIn('case/'+digest,foreign['fetch_ids'])

class NewSessionRoundTrip(unittest.TestCase):
    def test_durable_source_linked_objective_survives_new_session_bootstrap(self):
        with tempfile.TemporaryDirectory(prefix='memory-roundtrip-') as temp:
            root=Path(temp).resolve();db=root/'memory.sqlite3';source=root/'intent.md'
            source.write_text('Synthetic user objective: preserve trustworthy context.')
            ref={'path':str(source),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
            observations=[]
            def invoke(op,args):
                p=subprocess.run([sys.executable,str(PROTOCOL)],input=canonical({'db':str(db),'scope':'roundtrip','product':'team','op':op,'args':args}),capture_output=True,text=True)
                self.assertEqual(p.returncode,0,p.stderr)
                result=json.loads(p.stdout);observations.append(result);return result
            invoke('init',{})
            invoke('register',{'roots':[str(root)],'case_store':None})
            data={'kind':'objective','text':'Preserve trustworthy context','key':'trust','status':'proposed','sources':[ref],'authority':None,'links':[],'acceptance':[],'anchor':True,'conflicts_with':[],'expires_at':None,'candidate':None}
            invoke('append',{'kind':'fact','entity_id':'trust','data':data,'event_id':'trust-intent','expected_revision':0})
            # Each invocation is a fresh native Python process. Empty baseline
            # yields typed UNSUPPORTED; present app import/setup errors propagate.
            bootstrap=invoke('context',{'query':'unrelated','max_chars':12000,'carry':[]})
            items=bootstrap.get('result',{}).get('items',[])
            self.assertEqual([x['entity_id'] for x in items],['trust'],observations)
            self.assertEqual(items[0]['data']['sources'],[ref])
            self.assertTrue(db.is_file())
            self.assertTrue(all(o['ok'] for o in observations),observations)

if __name__=='__main__':unittest.main()
