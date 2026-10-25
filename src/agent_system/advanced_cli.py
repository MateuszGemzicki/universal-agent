import argparse,json,os
from pathlib import Path
from . import advanced as A
from .cli import config
from .core import connect
ROOT=Path(__file__).resolve().parents[2]
def emit(x):print(json.dumps(x,indent=2,ensure_ascii=False))
def repo_root(name):
    db=connect(ROOT/'.agent-system/state.sqlite3')
    row=db.execute('SELECT path FROM repositories WHERE name=?',(name,)).fetchone()
    if not row:raise ValueError('Unknown registered repository; run sync first')
    return Path(row[0]).resolve()
def file_in_repo(repo,rel):
    root=repo_root(repo);p=(root/rel).resolve()
    if not p.is_relative_to(root):raise ValueError('Path outside repository')
    return p

def run(argv):
    p=argparse.ArgumentParser(prog='agent.py advanced');s=p.add_subparsers(dest='command',required=True)
    a=s.add_parser('parse');a.add_argument('repo');a.add_argument('file')
    a=s.add_parser('lsp');a.add_argument('repo');a.add_argument('file');a.add_argument('line',type=int);a.add_argument('column',type=int);a.add_argument('--operation',choices=['definition','references'],default='definition');a.add_argument('--server',required=True,help='Name from config lsp_servers; no arbitrary commands')
    a=s.add_parser('coverage');a.add_argument('coverage_json');a.add_argument('files',nargs='+')
    a=s.add_parser('contracts');a.add_argument('old_json');a.add_argument('new_json')
    a=s.add_parser('redact');a.add_argument('file');a.add_argument('--output',help='Output path for redacted text')
    a=s.add_parser('mutate');a.add_argument('repo');a.add_argument('file');a.add_argument('--confirm',action='store_true');a.add_argument('test_argv',nargs=argparse.REMAINDER)
    a=p.parse_args(argv)
    try:
        if a.command=='parse':emit(A.parse_symbols(file_in_repo(a.repo,a.file)))
        elif a.command=='lsp':
            servers=config().get('lsp_servers',{});argv=servers.get(a.server)
            if not isinstance(argv,list) or not argv:raise ValueError('LSP server not configured in config.yaml')
            emit(A.lsp_lookup(argv,repo_root(a.repo),file_in_repo(a.repo,a.file),a.line,a.column,a.operation))
        elif a.command=='coverage':emit(A.coverage_map(a.coverage_json,a.files))
        elif a.command=='contracts':emit(A.contract_diff(a.old_json,a.new_json))
        elif a.command=='redact':
            result=A.safe_context(Path(a.file).read_text(encoding='utf-8'))
            if a.output:
                Path(a.output).write_text(result['text'],encoding='utf-8');emit({'findings':result['findings'],'blocked':result['blocked'],'output':a.output})
            else:emit(result)
        elif a.command=='mutate':
            # REMAINDER swallows a --confirm placed after the file argument, so look for it here too
            confirm=a.confirm or '--confirm' in a.test_argv
            if not confirm:raise ValueError('Mutation runs tests; review test argv and add --confirm')
            cmd=[x for x in a.test_argv if x!='--confirm']
            cmd=cmd[1:] if cmd[:1]==['--'] else cmd
            emit(A.mutation_test(repo_root(a.repo),a.file,cmd))
    except (ValueError,OSError,RuntimeError,TimeoutError,SyntaxError) as e:p.error(str(e))
