"""Transactional append-only memory. Scope is organization, not OS authorization."""
from contextlib import contextmanager
import json
import os
from pathlib import Path
import sqlite3

from . import cases
from .validation import (MemoryError, canonical, digest, fields, integer, label,
                         loads, now, path_checked, reference, references, require,
                         sequence, sha, source_state, text, timestamp,
                         verify_references)

APP_ID = 0x554D454D
VERSION = 1
KINDS = {'fact', 'episode', 'lesson', 'validation', 'feedback', 'case_link'}
SOURCE_ROOT = Path(__file__).resolve().parents[1]
SCHEMA = '''
CREATE TABLE scopes(scope TEXT PRIMARY KEY, config TEXT NOT NULL);
CREATE TABLE events(
 seq INTEGER PRIMARY KEY, scope TEXT NOT NULL REFERENCES scopes(scope),
 event_id TEXT NOT NULL, kind TEXT NOT NULL, entity_id TEXT NOT NULL,
 revision INTEGER NOT NULL, data TEXT NOT NULL, created_at TEXT NOT NULL,
 supersedes TEXT, linked_revisions TEXT NOT NULL, request_hash TEXT NOT NULL,
 digest TEXT NOT NULL, UNIQUE(scope,event_id), UNIQUE(scope,kind,entity_id,revision));
CREATE TRIGGER events_no_update BEFORE UPDATE ON events BEGIN SELECT RAISE(ABORT,'append-only events'); END;
CREATE TRIGGER events_no_delete BEFORE DELETE ON events BEGIN SELECT RAISE(ABORT,'append-only events'); END;
CREATE TRIGGER scopes_no_update BEFORE UPDATE ON scopes BEGIN SELECT RAISE(ABORT,'immutable scope configuration'); END;
CREATE TRIGGER scopes_no_delete BEFORE DELETE ON scopes BEGIN SELECT RAISE(ABORT,'immutable scope configuration'); END;
'''

def scope_key(project, product):
    return label(project) + '/' + label(product)

class Memory:
    """Use create once, register explicit roots per project/product, then append.

    _before_commit is a private deterministic fault-injection seam for local
    tests; it runs after the real transaction writes, before the actual commit.
    It is never selectable through the CLI or stored content.
    """
    def __init__(self, path):
        self.path = path_checked(path)
        require(self.path.is_file() and self.path.stat().st_nlink == 1 and self.path.stat().st_mode & 0o077 == 0, 'Private regular memory database required', 'STORE')
        self.connection = sqlite3.connect(self.path.as_uri() + '?mode=rw', uri=True, timeout=5, isolation_level=None)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute('PRAGMA foreign_keys=ON')
        require(self.connection.execute('PRAGMA application_id').fetchone()[0] == APP_ID and self.connection.execute('PRAGMA user_version').fetchone()[0] == VERSION, 'Foreign or unsupported memory schema; no reset performed', 'STORE')
        require({r[0] for r in self.connection.execute("SELECT name FROM sqlite_master WHERE type='table'")} >= {'scopes', 'events'}, 'Incomplete memory schema', 'STORE')
        self._before_commit = lambda: None

    @classmethod
    def create(cls, path):
        path = path_checked(path)
        require(not path.is_relative_to(SOURCE_ROOT) and not path.is_relative_to(Path.home()/'.codex-cli/skills') and not path.is_relative_to(Path(cases.DEFAULT_STORE)), 'Runtime database must remain outside source, skills and canonical failure store', 'STORE')
        require(not any(Path(str(path)+suffix).exists() for suffix in ('', '-wal', '-shm')), 'Database or journal path exists; initialization refuses overwrite', 'STORE')
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        path_checked(path.parent)
        require(path.parent.stat().st_mode & 0o077 == 0, 'Database parent must be a private directory (0700)', 'STORE')
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        os.close(fd)
        # A crash during first initialization leaves an explicit incomplete file;
        # it is never silently reset. Ordinary append recovery is transactional.
        con = sqlite3.connect(path, timeout=5)
        try:
            con.execute('PRAGMA journal_mode=WAL')
            con.execute('PRAGMA synchronous=FULL')
            con.executescript('BEGIN IMMEDIATE;\n' + SCHEMA + f'PRAGMA application_id={APP_ID}; PRAGMA user_version={VERSION}; COMMIT;')
        finally:
            con.close()
        return {'schema_version': VERSION}

    def close(self):
        self.connection.close()

    @contextmanager
    def transaction(self, write=False):
        self.connection.execute('BEGIN IMMEDIATE' if write else 'BEGIN')
        try:
            yield
            self.connection.execute('COMMIT')
        except BaseException:
            self.connection.execute('ROLLBACK')
            raise

    def register(self, project, product, roots, case_store=None, case_scope=None):
        key = scope_key(project, product)
        roots = sorted(set(str(path_checked(p)) for p in sequence(roots, 8, True)))
        require(all(Path(p).is_dir() and p != '/' for p in roots), 'Existing bounded local roots required', 'EVIDENCE')
        if case_store is not None:
            case_store = str(path_checked(case_store))
            require(Path(case_store).is_dir(), 'Canonical store directory missing', 'EVIDENCE')
        config = {'project': project, 'product': product, 'roots': roots, 'case_store': case_store, 'case_scope': label(case_scope or project)}
        with self.transaction(True):
            row = self.connection.execute('SELECT config FROM scopes WHERE scope=?', (key,)).fetchone()
            if row:
                require(loads(row['config']) == config, 'Scope already registered with different immutable configuration', 'CONFLICT')
            else:
                self.connection.execute('INSERT INTO scopes VALUES(?,?)', (key, canonical(config)))
        return config

    def config(self, project, product):
        key = scope_key(project, product)
        row = self.connection.execute('SELECT config FROM scopes WHERE scope=?', (key,)).fetchone()
        require(row is not None, 'Project/product not registered', 'NOT_FOUND')
        return loads(row['config'])

    def _decode(self, row):
        project, product = row['scope'].split('/')
        result = {'project': project, 'product': product, 'event_id': row['event_id'], 'kind': row['kind'], 'entity_id': row['entity_id'], 'revision': row['revision'], 'data': loads(row['data']), 'created_at': row['created_at'], 'supersedes': row['supersedes'], 'linked_revisions': loads(row['linked_revisions'])}
        require(digest(result) == row['digest'], 'Memory record integrity mismatch', 'STORE')
        result['digest'] = row['digest']
        return result

    def get(self, project, product, kind, entity_id, revision=None):
        key = scope_key(project, product)
        require(kind in KINDS, 'Unknown record kind')
        label(entity_id)
        query = 'SELECT * FROM events WHERE scope=? AND kind=? AND entity_id=?'
        args = [key, kind, entity_id]
        if revision is not None:
            integer(revision, 1)
            query += ' AND revision=?'
            args.append(revision)
        row = self.connection.execute(query + ' ORDER BY revision DESC LIMIT 1', args).fetchone()
        require(row is not None, 'Exact scoped record/revision not found', 'NOT_FOUND')
        return self._decode(row)

    def history(self, project, product, kind, entity_id, offset=0, limit=100):
        key = scope_key(project, product)
        require(kind in KINDS, 'Unknown record kind')
        label(entity_id);integer(offset);integer(limit, 1, 100)
        return [self._decode(r) for r in self.connection.execute('SELECT * FROM events WHERE scope=? AND kind=? AND entity_id=? ORDER BY revision LIMIT ? OFFSET ?', (key, kind, entity_id, limit, offset))]

    def latest(self, project, product):
        key = scope_key(project, product)
        rows = self.connection.execute('SELECT e.* FROM events e JOIN (SELECT kind,entity_id,MAX(revision) rev FROM events WHERE scope=? GROUP BY kind,entity_id) m ON e.kind=m.kind AND e.entity_id=m.entity_id AND e.revision=m.rev WHERE e.scope=? ORDER BY e.kind,e.entity_id', (key, key))
        result = [self._decode(r) for r in rows]
        require(len(result) <= 512, 'Scope entity limit exceeded', 'LIMIT')
        return result

    def all_case_links(self, project, product):
        return [self._decode(r) for r in self.connection.execute("SELECT * FROM events WHERE scope=? AND kind='case_link' ORDER BY seq", (scope_key(project, product),))]

    def _linked_get(self, project, product, kind, entity_id, revision=None):
        try:
            return self.get(project,product,kind,entity_id,revision)
        except MemoryError as exc:
            if exc.code=='NOT_FOUND':
                raise MemoryError('VALIDATION','Creation reference missing from the current project/product') from exc
            raise

    def _ref_list(self, refs, nonempty=True):
        for ref in sequence(refs, 16, nonempty):
            reference(ref)

    def _fact(self, project, product, entity_id, data, latest):
        for key, default in {'status':'proposed', 'authority':None, 'links':[], 'acceptance':[], 'anchor':False, 'conflicts_with':[], 'expires_at':None, 'candidate':None}.items():
            data.setdefault(key, default)
        fields(data, ('kind','text','key','status','sources','authority','links','acceptance','anchor','conflicts_with','expires_at','candidate'))
        require(data['kind'] in {'objective','feature','decision','constraint','task'}, 'Invalid knowledge subtype')
        text(data['text']);label(data['key']);self._ref_list(data['sources'])
        require(data['status'] in {'proposed','authoritative','withdrawn'}, 'Invalid recorded status')
        require(type(data['anchor']) is bool, 'Boolean anchor required')
        if data['authority'] is not None:
            reference(data['authority'])
        require(data['status'] != 'authoritative' or data['authority'] is not None, 'Recorded authority requires a source reference, still an attested claim')
        if data['expires_at'] is not None:
            timestamp(data['expires_at'])
        links = sequence(data['links'], 8)
        require(len(links) == len(set(label(i) for i in links)) and entity_id not in links, 'Invalid or duplicate fact links')
        linked = []
        for target in links:
            record = self._linked_get(project, product, 'fact', target)
            require(record['data']['status'] != 'withdrawn', 'Cannot link a withdrawn current fact')
            linked.append({'kind':'fact', 'entity_id':target, 'revision':record['revision']})
        acceptance = sequence(data['acceptance'], 16)
        seen = set()
        for item in acceptance:
            fields(item, ('id','description','checks','evidence'))
            label(item['id'].lower());text(item['description'])
            require(item['id'] not in seen, 'Duplicate acceptance identifier');seen.add(item['id'])
            for check in sequence(item['checks'], 16, True):label(check)
            self._ref_list(item['evidence'])
        if data['kind'] == 'task':
            require(links and acceptance, 'Task needs objective/feature links and acceptance/check mapping')
            sha(data['candidate'])
            require(any(self.get(project,product,'fact',t)['data']['kind'] in {'objective','feature'} for t in links), 'Task needs an objective or feature link')
        else:
            require(data['candidate'] is None, 'Candidate belongs to a task contract')
        previous = next((r for r in latest if r['kind']=='fact' and r['entity_id']==entity_id), None)
        if previous:
            require((previous['data']['kind'],previous['data']['key']) == (data['kind'],data['key']), 'Logical fact subtype/topic identity is immutable')
        competing = {r['entity_id'] for r in latest if r['kind']=='fact' and r['entity_id']!=entity_id and r['data']['kind']==data['kind'] and r['data']['key']==data['key'] and r['data']['status']!='withdrawn' and r['data']['text']!=data['text']}
        declared = set(label(i) for i in sequence(data['conflicts_with'], 16))
        require(declared == (competing if data['status']!='withdrawn' else set()), 'Competing topic value must explicitly declare all conflicting IDs', 'CONFLICT')
        if data['anchor'] and not (previous and previous['data']['anchor']):
            require(sum(r['kind']=='fact' and r['data']['anchor'] for r in latest)<16, 'At most sixteen designated anchors per project/product', 'LIMIT')
        return linked

    def _task_link(self, project, product, data):
        label(data['task']);integer(data['task_revision'],1);sha(data['candidate'])
        task = self._linked_get(project,product,'fact',data['task'],data['task_revision'])
        require(task['data']['kind']=='task' and task['data']['candidate']==data['candidate'], 'Task revision/candidate mismatch')
        return task

    def _validate(self, project, product, kind, entity_id, data, latest):
        linked = []
        if kind == 'fact':
            return self._fact(project,product,entity_id,data,latest)
        if kind == 'episode':
            fields(data, ('task','task_revision','candidate','attempt','hypothesis','observed_cause','outcome','checks','sources','case_digests','claim_level'))
            task=self._task_link(project,product,data)
            integer(data['attempt'],1,1000);text(data['hypothesis'],empty=True);text(data['observed_cause'],empty=True)
            require(data['outcome'] in {'observed_success','observed_failure','unknown'} and data['claim_level']=='observation', 'Outcome is an observation, never automatic verified product success')
            self._ref_list(data['sources'])
            checks=sequence(data['checks'],32,True)
            ids=[]
            for check in checks:
                fields(check,('id','outcome','evidence'));label(check['id']);reference(check['evidence']);ids.append(check['id'])
                require(check['outcome'] in {'PASS','FAIL','UNKNOWN'},'Invalid check observation')
            require(len(ids)==len(set(ids)),'Duplicate check identity')
            if data['outcome']=='observed_success':
                expected={c for a in task['data']['acceptance'] for c in a['checks']}
                require(all(c['outcome']=='PASS' for c in checks) and expected<=set(ids),'Observed success requires task checks with recorded passing evidence')
            for case in sequence(data['case_digests'],16):sha(case)
            linked=[{'kind':'fact','entity_id':data['task'],'revision':data['task_revision']}]
        elif kind=='lesson':
            data.setdefault('case_digests',[]);data.setdefault('limitations','Unvalidated, inert proposal');data.setdefault('intended_validation','Separate regression and disjoint held-out comparison plus independent review')
            fields(data,('text','episodes','proposed_change','sources','case_digests','limitations','intended_validation'))
            text(data['text']);text(data['proposed_change']);text(data['limitations']);text(data['intended_validation']);self._ref_list(data['sources'])
            for episode in sequence(data['episodes'],16,True):
                record=self._linked_get(project,product,'episode',label(episode))
                linked.append({'kind':'episode','entity_id':episode,'revision':record['revision']})
            for case in sequence(data['case_digests'],16):sha(case)
        elif kind=='validation':
            fields(data,('lesson','baseline_candidate','candidate','baseline_cases','heldout_cases','comparison','regressions','independent_review','baseline_failures','candidate_failures','decision'))
            record=self._linked_get(project,product,'lesson',label(data['lesson']))
            linked=[{'kind':'lesson','entity_id':data['lesson'],'revision':record['revision']}]
            sha(data['baseline_candidate']);sha(data['candidate'])
            require(data['candidate']!=data['baseline_candidate'],'Comparison must identify distinct frozen candidates')
            baseline=set(label(v) for v in sequence(data['baseline_cases'],32,True))
            heldout=set(label(v) for v in sequence(data['heldout_cases'],32,True))
            require(not baseline & heldout,'Training/baseline and held-out case IDs must be disjoint')
            for key in ('comparison','regressions','independent_review'):self._ref_list(data[key])
            integer(data['baseline_failures']);integer(data['candidate_failures'])
            require(data['candidate_failures']<=data['baseline_failures'] and data['decision']=='supported_proposal','Regressing comparison cannot support even an inert positive proposal')
        elif kind=='feedback':
            fields(data,('pack_sha256','query','retrieved_ids','used_ids','missed_known_ids','rating','note','task','task_revision','candidate','actions'))
            task=self._task_link(project,product,data)
            sha(data['pack_sha256']);text(data['query'],1000,True);text(data['note']);require(data['rating'] in {'useful','miss','irrelevant','harmful'},'Invalid feedback rating')
            retrieved=sequence(data['retrieved_ids'],64);used=sequence(data['used_ids'],64);missed=sequence(data['missed_known_ids'],64)
            require(set(used)<=set(retrieved),'Used IDs must belong to submitted retrieved IDs')
            for item in retrieved+used+missed:text(item,100)
            for item in retrieved:
                if item.startswith('case/'):
                    sha(item[5:])
                else:
                    try:
                        k,tail=item.split('/',1);ident,rev=tail.rsplit('@',1)
                        self.get(project,product,k,ident,int(rev))
                    except (ValueError,TypeError) as exc:
                        raise MemoryError('VALIDATION','Invalid scoped retrieved revision ID') from exc
            for action in sequence(data['actions'],16,True):
                fields(action,('description','checks','evidence'));text(action['description'])
                for check in sequence(action['checks'],16,True):label(check)
                self._ref_list(action['evidence'])
            linked=[{'kind':'fact','entity_id':data['task'],'revision':task['revision']}]
        elif kind=='case_link':
            fields(data,('digest','applicability','regressions','sources'));sha(data['digest']);self._ref_list(data['sources'])
            require(data['applicability'] in {'APPLIES','NOT_APPLICABLE'},'Invalid applicability')
            for check in sequence(data['regressions'],16):label(check)
            require(data['applicability']!='APPLIES' or data['regressions'],'Applicable case needs explicit regressions')
            known={r['data']['digest'] for r in self.all_case_links(project,product)}
            require(data['digest'] in known or len(known)<16,'At most sixteen exact case obligations per product', 'LIMIT')
        return linked

    def append(self, project, product, kind, entity_id, data, event_id, expected_revision):
        key=scope_key(project,product);require(kind in KINDS,'Unknown record kind');label(entity_id);label(event_id);integer(expected_revision)
        require(type(data) is dict and len(canonical(data).encode())<=16384,'Bounded record object required')
        data=json.loads(canonical(data))  # Isolate caller mutation; never persist raw source bytes.
        request_hash=digest({'kind':kind,'entity_id':entity_id,'data':data,'expected_revision':expected_revision})
        with self.transaction(True):
            config=self.config(project,product)
            replay=self.connection.execute('SELECT * FROM events WHERE scope=? AND event_id=?',(key,event_id)).fetchone()
            if replay:
                require(replay['request_hash']==request_hash,'Idempotency key reused with different intent','CONFLICT')
                return self._decode(replay)
            latest=self.latest(project,product)
            previous=next((r for r in latest if r['kind']==kind and r['entity_id']==entity_id),None)
            if kind!='fact' and previous:
                raise MemoryError('IMMUTABLE','Observation/proposal/case metadata is append-only; use a new ID')
            require((previous['revision'] if previous else 0)==expected_revision,'Expected revision conflict','CONFLICT')
            require(self.connection.execute('SELECT COUNT(*) FROM events WHERE scope=?',(key,)).fetchone()[0]<10000,'Scope event limit exceeded','LIMIT')
            linked=self._validate(project,product,kind,entity_id,data,latest)
            verify_references(data,config['roots'])
            require(previous or len(latest)<512,'Scope entity limit exceeded','LIMIT')
            record={'project':project,'product':product,'event_id':event_id,'kind':kind,'entity_id':entity_id,'revision':expected_revision+1,'data':data,'created_at':now(),'supersedes':previous['digest'] if previous else None,'linked_revisions':linked}
            record['digest']=digest(record)
            self.connection.execute('INSERT INTO events(scope,event_id,kind,entity_id,revision,data,created_at,supersedes,linked_revisions,request_hash,digest) VALUES(?,?,?,?,?,?,?,?,?,?,?)',(key,event_id,kind,entity_id,record['revision'],canonical(data),record['created_at'],record['supersedes'],canonical(linked),request_hash,record['digest']))
            self._before_commit()
        return record

    def context(self, project, product, query='', max_chars=12000, carry=(), task=None, task_revision=None):
        from .context import build
        with self.transaction():
            return build(self,project,product,query,max_chars,list(carry),task,task_revision)

    def consult(self, project, product, query='', carry=()):
        config=self.config(project,product)
        known={r['data']['digest'] for r in self.all_case_links(project,product)}|set(carry)
        sequence(list(known),16)
        require(config['case_store'] is not None,'No canonical case store configured','CASE_UNAVAILABLE')
        return cases.consult(config['case_store'],config['case_scope'],query,sorted(known))

    def integrity(self, project, product):
        self.config(project,product)
        require(self.connection.execute('PRAGMA integrity_check').fetchone()[0]=='ok','SQLite integrity check failed','STORE')
        rows=[self._decode(r) for r in self.connection.execute('SELECT * FROM events WHERE scope=? ORDER BY seq',(scope_key(project,product),))]
        return {'schema_version':VERSION,'verified_record_digests':len(rows),'source_truth_verified':False}
