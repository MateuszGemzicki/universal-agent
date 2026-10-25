import ast
import hashlib
import json
import re
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime, timezone

EXCLUDED = {'.git', '.venv', 'venv', '__pycache__', 'node_modules', 'dist', 'build', '.next', '.pytest_cache', '.agent-system', '.turbo', 'coverage', '.idea', '.vscode'}

def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def git_ignored(root: Path) -> set:
    """Paths ignored by .gitignore (dirs end with '/'); empty when root is not a git repo."""
    try:
        r = subprocess.run(['git', '-C', str(root), 'ls-files', '-o', '-i', '--exclude-standard', '--directory'], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return set()
    return set(r.stdout.splitlines()) if r.returncode == 0 else set()

def collect(root: Path):
    root = root.resolve()
    files = {}
    ignored = git_ignored(root)
    def walk(directory):
        children = []
        for item in sorted(directory.iterdir(), key=lambda x: x.name):
            if item.name in EXCLUDED or item.is_symlink():
                continue
            rel_path = item.relative_to(root).as_posix()
            if (rel_path + '/' if item.is_dir() else rel_path) in ignored:
                continue
            if item.is_dir():
                child_hash = walk(item)
                children.append(('d', item.name, child_hash))
            elif item.is_file():
                if item.name in {'.env', '.env.local', '.env.production', 'id_rsa', 'id_ed25519'} or item.suffix.lower() in {'.pem', '.key', '.p12', '.pfx'}: continue
                try:
                    if item.stat().st_size > 5*1024*1024: continue
                    content = item.read_bytes()
                except (OSError, PermissionError):
                    continue
                h = digest(content)
                rel = item.relative_to(root).as_posix()
                files[rel] = h
                children.append(('f', item.name, h))
        return digest(json.dumps(children, ensure_ascii=False, separators=(',', ':')).encode())
    return walk(root), files

def inventory_python(path: Path):
    try:
        tree = ast.parse(path.read_text(encoding='utf-8-sig'))
    except (SyntaxError, UnicodeError, OSError):
        return []
    results = []
    class Visitor(ast.NodeVisitor):
        def __init__(self):
            self.scope = []
        def visit_ClassDef(self, node):
            self.scope.append(node.name)
            self.generic_visit(node)
            self.scope.pop()
        def visit_FunctionDef(self, node):
            self.add(node)
        visit_AsyncFunctionDef = visit_FunctionDef
        def add(self, node):
            args = [a.arg for a in node.args.posonlyargs + node.args.args + node.args.kwonlyargs]
            if node.args.vararg: args.append('*' + node.args.vararg.arg)
            if node.args.kwarg: args.append('**' + node.args.kwarg.arg)
            calls = sorted({n.func.id if isinstance(n.func, ast.Name) else n.func.attr for n in ast.walk(node) if isinstance(n, ast.Call) and isinstance(n.func, (ast.Name, ast.Attribute))})
            try: returns = ast.unparse(node.returns) if node.returns else None
            except Exception: returns = None
            results.append({'name': '.'.join(self.scope + [node.name]), 'line': node.lineno, 'inputs': args, 'output_annotation': returns, 'calls': calls, 'docstring': ast.get_docstring(node), 'async': isinstance(node, ast.AsyncFunctionDef)})
            self.scope.append(node.name)
            self.generic_visit(node)
            self.scope.pop()
    Visitor().visit(tree)
    return results

def inventory_javascript(path: Path):
    # Heuristic index only: does not claim full JS/TS parsing or type resolution.
    try: source = path.read_text(encoding='utf-8-sig')
    except (OSError, UnicodeError): return []
    pattern = re.compile(r'\b(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*\(([^)]*)\)|\b(?:export\s+)?(?:const|let)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*(?::[^=]+)?=>')
    result=[]
    for m in pattern.finditer(source):
        name=m.group(1) or m.group(3)
        params=m.group(2) if m.group(1) else m.group(4)
        result.append({'name':name,'line':source.count('\n',0,m.start())+1,'inputs':[x.strip() for x in params.split(',') if x.strip()],'output_annotation':None,'calls':[],'docstring':None,'confidence':'heuristic'})
    return result

def connect(db_path: Path):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(db_path)
    db.execute('PRAGMA foreign_keys=ON')
    db.executescript('''
    CREATE TABLE IF NOT EXISTS repositories(name TEXT PRIMARY KEY, path TEXT NOT NULL, root_hash TEXT);
    CREATE TABLE IF NOT EXISTS files(repo TEXT NOT NULL, path TEXT NOT NULL, hash TEXT NOT NULL, inventory TEXT NOT NULL, PRIMARY KEY(repo,path), FOREIGN KEY(repo) REFERENCES repositories(name));
    CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY AUTOINCREMENT, goal TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'planned', created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS approvals(id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT NOT NULL, payload TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending', created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS scripts(id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT NOT NULL, sha256 TEXT NOT NULL, approval_id INTEGER NOT NULL, FOREIGN KEY(approval_id) REFERENCES approvals(id));
    CREATE TABLE IF NOT EXISTS test_runs(id INTEGER PRIMARY KEY AUTOINCREMENT, repo TEXT NOT NULL, command TEXT NOT NULL, exit_code INTEGER NOT NULL, output TEXT NOT NULL, created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS notes(id INTEGER PRIMARY KEY AUTOINCREMENT, repo TEXT, kind TEXT NOT NULL, content TEXT NOT NULL, source_hash TEXT, created_at TEXT NOT NULL);
    ''')
    db.commit()
    return db

def timestamp():
    return datetime.now(timezone.utc).isoformat()

def scan(db, repo):
    record = db.execute('SELECT path, root_hash FROM repositories WHERE name=?', (repo,)).fetchone()
    if not record: raise ValueError(f'Unknown repository: {repo}')
    root = Path(record[0])
    if not root.is_dir(): raise ValueError(f'Repository directory missing: {root}')
    new_root, current = collect(root)
    old = dict(db.execute('SELECT path, hash FROM files WHERE repo=?', (repo,)).fetchall())
    changed = sorted(p for p, h in current.items() if old.get(p) != h)
    deleted = sorted(set(old) - set(current))
    with db:
        for path in changed:
            inv = inventory_python(root / path) if path.endswith('.py') else inventory_javascript(root / path) if path.endswith(('.js','.jsx','.ts','.tsx','.mjs','.cjs')) else []
            db.execute('INSERT INTO files(repo,path,hash,inventory) VALUES(?,?,?,?) ON CONFLICT(repo,path) DO UPDATE SET hash=excluded.hash, inventory=excluded.inventory', (repo,path,current[path],json.dumps(inv)))
        for path in deleted:
            db.execute('DELETE FROM files WHERE repo=? AND path=?', (repo,path))
        db.execute('UPDATE repositories SET root_hash=? WHERE name=?', (new_root,repo))
    return {'repository':repo, 'root_hash':new_root, 'changed':changed, 'deleted':deleted, 'unchanged_count':len(current)-len(changed)}
