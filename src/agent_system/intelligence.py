import hashlib, json, re, sqlite3, subprocess, os, shutil
from pathlib import Path
from .core import timestamp
def init(db):
    db.executescript("""CREATE TABLE IF NOT EXISTS artifacts(id TEXT PRIMARY KEY, repo TEXT, kind TEXT NOT NULL, content TEXT NOT NULL, sources TEXT NOT NULL, fingerprint TEXT NOT NULL, confidence TEXT NOT NULL, created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS lessons(id INTEGER PRIMARY KEY AUTOINCREMENT, repo TEXT, problem TEXT NOT NULL, solution TEXT NOT NULL, evidence TEXT NOT NULL, created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS checks(id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT, repo TEXT, kind TEXT NOT NULL, status TEXT NOT NULL, evidence TEXT, created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS skill_evals(id INTEGER PRIMARY KEY AUTOINCREMENT, skill TEXT NOT NULL, task TEXT NOT NULL, outcome TEXT NOT NULL, notes TEXT, created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS worktrees(id INTEGER PRIMARY KEY AUTOINCREMENT, repo TEXT NOT NULL, branch TEXT NOT NULL, path TEXT NOT NULL, created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS benchmarks(id INTEGER PRIMARY KEY AUTOINCREMENT, task TEXT NOT NULL, provider TEXT NOT NULL, model TEXT, success INTEGER NOT NULL, seconds REAL NOT NULL, tokens INTEGER, human_interventions INTEGER, created_at TEXT NOT NULL);""")
    db.commit()
def sha(b):return hashlib.sha256(b).hexdigest()
def file_sources(db,repo,paths):
    out=[]
    for p in paths:
        row=db.execute('SELECT hash FROM files WHERE repo=? AND path=?',(repo,p)).fetchone()
        if not row: raise ValueError('Unknown indexed file: '+p)
        out.append({'repo':repo,'path':p,'sha256':row[0]})
    return out
def fingerprint(sources,policy='v1'):
    return sha(json.dumps({'sources':sources,'policy':policy},sort_keys=True).encode())
def save_artifact(db,identifier,repo,kind,content,paths,confidence='unverified'):
    sources=file_sources(db,repo,paths); fp=fingerprint(sources)
    with db: db.execute('INSERT OR REPLACE INTO artifacts VALUES(?,?,?,?,?,?,?,?)',(identifier,repo,kind,content,json.dumps(sources),fp,confidence,timestamp()))
    return {'id':identifier,'fingerprint':fp,'sources':sources}
def stale(db):
    result=[]
    for ident,repo,sources,fp in db.execute('SELECT id,repo,sources,fingerprint FROM artifacts'):
        parsed=json.loads(sources); current=[]
        for s in parsed:
            row=db.execute('SELECT hash FROM files WHERE repo=? AND path=?',(s['repo'],s['path'])).fetchone()
            current.append({'repo':s['repo'],'path':s['path'],'sha256':row[0] if row else None})
        if fingerprint(current)!=fp:result.append({'id':ident,'repo':repo,'reason':'source_changed_or_deleted'})
    return result
def search(db,query,limit=15):
    words=[w.lower() for w in re.findall(r'[\w-]{3,}',query)][:12]
    if not words:return []
    results=[]
    for repo,path,inventory in db.execute('SELECT repo,path,inventory FROM files'):
        for item in json.loads(inventory):
            blob=' '.join([repo,path,item.get('name',''),item.get('docstring') or '', ' '.join(item.get('calls',[]))]).lower()
            score=sum(blob.count(w) for w in words)
            if score:results.append({'repo':repo,'path':path,'symbol':item['name'],'line':item.get('line'),'score':score,'confidence':item.get('confidence','ast')})
    return sorted(results,key=lambda x:-x['score'])[:limit]
def impact(db,repo,path):
    target=db.execute('SELECT inventory FROM files WHERE repo=? AND path=?',(repo,path)).fetchone()
    if not target:raise ValueError('File not indexed: '+path)
    symbols={i['name'].split('.')[-1] for i in json.loads(target[0])}
    matches=[]
    for r,p,inv in db.execute('SELECT repo,path,inventory FROM files'):
        if r==repo and p==path:continue
        for item in json.loads(inv):
            overlap=sorted(symbols.intersection(item.get('calls',[])))
            if overlap:matches.append({'repo':r,'path':p,'symbol':item['name'],'line':item.get('line'),'calls':overlap,'certainty':'heuristic_name_match'})
    return {'target':{'repo':repo,'path':path},'possible_dependents':matches,'warning':'Name matching is not resolved call graph; imports/events/runtime may be missed.'}
def context(db,query,budget=3000):
    results=search(db,query,40); used=0; blocks=[]
    for hit in results:
        row=db.execute('SELECT path FROM repositories WHERE name=?',(hit['repo'],)).fetchone()
        if not row:continue
        file=Path(row[0])/hit['path']
        try: lines=file.read_text(encoding='utf-8').splitlines()
        except (UnicodeError,OSError):continue
        n=hit['line'] or 1; excerpt='\n'.join(f'{i+1}: {lines[i]}' for i in range(max(0,n-3),min(len(lines),n+15)))
        block=f"### {hit['repo']} / {hit['path']}:{n} {hit['symbol']}\n{excerpt}\n"
        estimated=max(1,len(block)//4)
        if used+estimated>budget:continue
        blocks.append(block);used+=estimated
    from .advanced import safe_context
    safe=safe_context('\n'.join(blocks))
    return {'query':query,'estimated_tokens':used,'budget':budget,'text':safe['text'],'redactions':safe['findings'],'blocked_sensitive_content':safe['blocked'],'note':'Token estimates approximate; verify original files. Redaction is best-effort, not a guarantee.'}
def quality(db,task,required=('unit','integration','regression')):
    rows=db.execute('SELECT kind,status,evidence FROM checks WHERE task=? ORDER BY id DESC',(task,)).fetchall(); latest={}
    for kind,status,evidence in rows:
        if kind not in latest:latest[kind]={'status':status,'evidence':evidence}
    missing=[k for k in required if latest.get(k,{}).get('status')!='pass']
    return {'task':task,'passed':not missing,'missing_or_failed':missing,'checks':latest}
def worktree(db,repo,branch,path):
    row=db.execute('SELECT path FROM repositories WHERE name=?',(repo,)).fetchone()
    if not row:raise ValueError('Unknown repo')
    root=Path(row[0]); target=Path(path).resolve()
    if target.exists():raise ValueError('Target exists')
    if not re.fullmatch(r'[a-zA-Z0-9._/-]+',branch) or '..' in branch:raise ValueError('Unsafe branch')
    proc=subprocess.run(['git','-C',str(root),'worktree','add','-b',branch,str(target)],capture_output=True,text=True,timeout=60)
    if proc.returncode:raise ValueError(proc.stderr.strip())
    with db:db.execute('INSERT INTO worktrees(repo,branch,path,created_at) VALUES(?,?,?,?)',(repo,branch,str(target),timestamp()))
    return {'repo':repo,'branch':branch,'path':str(target)}
