import argparse, hashlib, json, os, re, shutil, sqlite3, subprocess, sys
from pathlib import Path
from .core import connect, scan, timestamp
ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / '.agent-system' / 'state.sqlite3'
def emit(x): print(json.dumps(x, ensure_ascii=False, indent=2))
def config():
    raw=(ROOT/'config.yaml').read_text(encoding='utf-8')
    try: data=json.loads(raw)
    except json.JSONDecodeError as e: raise ValueError('config.yaml must use JSON-compatible YAML syntax: '+str(e))
    if data.get('schema_version')!=1 or not isinstance(data.get('repositories'),list): raise ValueError('Invalid config schema')
    names=set()
    for r in data['repositories']:
        if not re.fullmatch(r'[a-zA-Z0-9_-]+',r['name']): raise ValueError('Unsafe repository name')
        if r['name'] in names: raise ValueError('Duplicate repo name')
        names.add(r['name'])
    return data
def repo_path(db,name):
    row=db.execute('SELECT path FROM repositories WHERE name=?',(name,)).fetchone()
    if not row: raise ValueError('Unknown repository: '+name)
    return Path(row[0])
def setup(db):
    db.executescript("""
    CREATE TABLE IF NOT EXISTS approvals_v2(id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, path TEXT NOT NULL, sha256 TEXT NOT NULL, purpose TEXT NOT NULL, state TEXT NOT NULL DEFAULT 'pending', created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS prompt_versions(id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT NOT NULL, sha256 TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL);
    """)
    db.commit()
def sync(db):
    enabled=[]
    for r in config()['repositories']:
        if not r.get('enabled',False): continue
        p=Path(os.path.expandvars(os.path.expanduser(r['path']))).resolve()
        if not p.is_dir(): raise ValueError(f"Missing directory for {r['name']}: {p}")
        with db: db.execute('INSERT INTO repositories(name,path) VALUES(?,?) ON CONFLICT(name) DO UPDATE SET path=excluded.path,root_hash=CASE WHEN path<>excluded.path THEN NULL ELSE root_hash END',(r['name'],str(p)))
        enabled.append(r['name'])
    with db:
        for (name,) in db.execute('SELECT name FROM repositories').fetchall():
            if name not in enabled:
                db.execute('DELETE FROM files WHERE repo=?',(name,))
                db.execute('DELETE FROM repositories WHERE name=?',(name,))
    return enabled
def docgen(db):
    out=ROOT/'knowledge';out.mkdir(exist_ok=True)
    result=[]; nodes=[]; edges=[]
    for name,path,rh in db.execute('SELECT name,path,root_hash FROM repositories ORDER BY name'):
        entries=db.execute('SELECT path,hash,inventory FROM files WHERE repo=? ORDER BY path',(name,)).fetchall()
        lines=[f'# {name}', '',f'Source: `{path}`',f'Root SHA-256: `{rh}`','','> Automatically extracted inventory. Business meaning requires verification.','','## Functions']
        nodes.append({'id':name,'type':'repository','path':path})
        for file,h,inventory in entries:
            fid=f'{name}:{file}';nodes.append({'id':fid,'type':'file','hash':h});edges.append({'from':name,'to':fid,'type':'contains'})
            for item in json.loads(inventory):
                symbol=f'{fid}:{item["name"]}'
                nodes.append({'id':symbol,'type':'function','line':item.get('line'),'inputs':item.get('inputs',[]),'output':item.get('output_annotation')})
                edges.append({'from':fid,'to':symbol,'type':'defines'})
                lines.append(f'- `{file}:{item.get("line",0)}` **{item["name"]}**({", ".join(item.get("inputs",[]))}) → `{item.get("output_annotation") or "unknown"}`; calls: {", ".join(item.get("calls",[])) or "unknown"}')
        (out/f'{name}.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
        result.append({'repo':name,'files':len(entries),'functions':sum(len(json.loads(e[2])) for e in entries)})
    (out/'graph.json').write_text(json.dumps({'nodes':nodes,'edges':edges},ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'index.md').write_text('# Code intelligence\n\n'+'\n'.join(f'- [{x["repo"]}]({x["repo"]}.md): {x["files"]} files, {x["functions"]} extracted functions' for x in result)+'\n',encoding='utf-8')
    return result
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def script_path(path):
    p=(ROOT/path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
    if p.suffix.lower()!='.cmd' or not p.is_relative_to((ROOT/'scripts').resolve()) or not p.is_file(): raise ValueError('Script must be an existing .cmd inside scripts/')
    return p
def main():
    p=argparse.ArgumentParser(description='Codex multi-repository agent control')
    s=p.add_subparsers(dest='command',required=True)
    for name in ['doctor','sync','scan-all','status','docs','graph','requests','prompt-list']:s.add_parser(name)
    inv=s.add_parser('inventory');inv.add_argument('repo')
    task=s.add_parser('task');task.add_argument('goal')
    test=s.add_parser('test');test.add_argument('repo');test.add_argument('args',nargs=argparse.REMAINDER)
    prop=s.add_parser('propose-script');prop.add_argument('path');prop.add_argument('purpose')
    approve=s.add_parser('approve');approve.add_argument('id',type=int)
    run=s.add_parser('run-script');run.add_argument('id',type=int);run.add_argument('args',nargs=argparse.REMAINDER)
    browser=s.add_parser('browser');browser.add_argument('url',nargs='?',default='http://localhost:3000')
    ps=s.add_parser('prompt-set');ps.add_argument('role');ps.add_argument('file')
    args=p.parse_args();db=connect(DB);setup(db)
    try:
        if args.command=='doctor':
            cfg=config();emit({'python':sys.version.split()[0],'git':shutil.which('git'),'node':shutil.which('node'),'codex':shutil.which('codex'),'configured_repos':len(cfg['repositories']),'enabled_repos':sum(bool(r.get('enabled')) for r in cfg['repositories']),'db':str(DB)})
        elif args.command=='sync':emit({'registered':sync(db)})
        elif args.command=='scan-all':
            names=sync(db);emit([scan(db,n) for n in names])
        elif args.command=='status':
            emit([{'name':n,'path':path,'root_hash':rh,'file_count':db.execute('SELECT COUNT(*) FROM files WHERE repo=?',(n,)).fetchone()[0]} for n,path,rh in db.execute('SELECT name,path,root_hash FROM repositories')])
        elif args.command=='docs':emit(docgen(db))
        elif args.command=='graph':
            path=ROOT/'knowledge/graph.json'
            if not path.exists():docgen(db)
            emit({'path':str(path),'data':json.loads(path.read_text(encoding='utf-8'))})
        elif args.command=='inventory':
            emit({f:json.loads(inv) for f,inv in db.execute('SELECT path,inventory FROM files WHERE repo=?',(args.repo,)) if json.loads(inv)})
        elif args.command=='task':
            with db: cur=db.execute('INSERT INTO tasks(goal,created_at) VALUES(?,?)',(args.goal,timestamp()))
            tid=cur.lastrowid;path=ROOT/'tasks'/f'TASK-{tid}.md';path.parent.mkdir(exist_ok=True)
            path.write_text(f'# Task {tid}: {args.goal}\n\nStatus: planned\n\n## Requirements\n- TBD\n\n## Acceptance criteria\n- TBD\n\n## Affected repositories\n- TBD\n\n## TDD evidence\n- Red: pending\n- Green: pending\n- Regression: pending\n\n## Decisions and risks\n- TBD\n',encoding='utf-8');emit({'task_id':tid,'file':str(path)})
        elif args.command=='requests':emit([{'id':i,'kind':k,'path':path,'sha256':h,'purpose':purpose,'state':st} for i,k,path,h,purpose,st in db.execute('SELECT id,kind,path,sha256,purpose,state FROM approvals_v2 ORDER BY id DESC')])
        elif args.command=='propose-script':
            path=script_path(args.path);h=sha(path)
            with db:cur=db.execute('INSERT INTO approvals_v2(kind,path,sha256,purpose,created_at) VALUES(?,?,?,?,?)',('cmd',str(path),h,args.purpose,timestamp()))
            emit({'request_id':cur.lastrowid,'path':str(path),'sha256':h,'status':'pending','instruction':'Human reviews file and executes: python agent.py approve '+str(cur.lastrowid)})
        elif args.command=='approve':
            row=db.execute('SELECT path,sha256,state FROM approvals_v2 WHERE id=?',(args.id,)).fetchone()
            if not row:raise ValueError('Approval request not found')
            path=script_path(row[0]);
            if sha(path)!=row[1]:raise ValueError('Script changed: propose again')
            with db:db.execute("UPDATE approvals_v2 SET state='approved' WHERE id=?",(args.id,))
            emit({'approved':args.id,'sha256':row[1]})
        elif args.command=='run-script':
            if os.name!='nt':raise ValueError('CMD execution requires Windows')
            row=db.execute('SELECT path,sha256,state FROM approvals_v2 WHERE id=?',(args.id,)).fetchone()
            if not row or row[2]!='approved':raise ValueError('Exact script has not been approved')
            path=script_path(row[0]);
            if sha(path)!=row[1]:raise ValueError('Script changed after approval')
            argv=args.args[1:] if args.args[:1]==['--'] else args.args
            if any(re.search(r'[&|<>^%\r\n"]',a) for a in argv):raise ValueError('Unsafe CMD argument')
            proc=subprocess.run(['cmd.exe','/d','/s','/c',str(path),*argv],cwd=ROOT,timeout=300,check=False)
            raise SystemExit(proc.returncode)
        elif args.command=='test':
            root=repo_path(db,args.repo)
            argv=args.args[1:] if args.args[:1]==['--'] else args.args
            if not argv:raise ValueError('Supply a test command after --')
            print('WARNING: This executes code in a repository. Confirm human authorization before use.',flush=True)
            try:
                result=subprocess.run(argv,cwd=root,capture_output=True,text=True,timeout=config().get('settings',{}).get('max_test_seconds',300),shell=False)
                code=result.returncode;output=(result.stdout+'\n'+result.stderr)[-20000:]
            except subprocess.TimeoutExpired:code=124;output='Timed out'
            with db:db.execute('INSERT INTO test_runs(repo,command,exit_code,output,created_at) VALUES(?,?,?,?,?)',(args.repo,json.dumps(argv),code,output,timestamp()))
            print(output);raise SystemExit(code)
        elif args.command=='browser':
            if not re.fullmatch(r'https?://(?:localhost|127\.0\.0\.1)(?::\d+)?(?:/[^\s]*)?',args.url):raise ValueError('Browser only accepts localhost')
            if not shutil.which('node'):raise ValueError('Node missing')
            result=subprocess.run(['node',str(ROOT/'browser/smoke.cjs'),args.url],cwd=ROOT/'browser',check=False);raise SystemExit(result.returncode)
        elif args.command=='prompt-list':emit([{'role':r,'versions':n} for r,n in db.execute('SELECT role,COUNT(*) FROM prompt_versions GROUP BY role')])
        elif args.command=='prompt-set':
            if not re.fullmatch(r'[a-z0-9_-]+',args.role):raise ValueError('Invalid role')
            src=Path(args.file).resolve();content=src.read_text(encoding='utf-8');h=hashlib.sha256(content.encode()).hexdigest()
            with db:db.execute('INSERT INTO prompt_versions(role,sha256,content,created_at) VALUES(?,?,?,?)',(args.role,h,content,timestamp()))
            dest=ROOT/'prompts'/f'{args.role}.md';dest.write_text(content,encoding='utf-8');emit({'role':args.role,'sha256':h,'file':str(dest)})
    except (ValueError,OSError,sqlite3.Error) as exc:p.error(str(exc))
if __name__=='__main__':main()
