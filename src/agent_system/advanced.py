"""Optional code intelligence, security and verification utilities. No network calls."""
import ast, json, re, hashlib, subprocess, tempfile, shutil, os, time, threading, queue
from pathlib import Path

EXTENSIONS={'.py':'python','.js':'javascript','.jsx':'javascript','.ts':'typescript','.tsx':'tsx','.go':'go','.rs':'rust','.java':'java','.c':'c','.cpp':'cpp','.cs':'c_sharp'}

def parse_symbols(path):
    """Tree-sitter when installed; Python AST fallback. Never claim regex is AST."""
    p=Path(path); lang=EXTENSIONS.get(p.suffix.lower())
    if not lang:return {'language':None,'engine':'unsupported','symbols':[]}
    src=p.read_bytes()
    try:
        from tree_sitter_language_pack import get_parser
        parser=get_parser(lang);tree=parser.parse(src)
        types={'function_definition','function_declaration','method_definition','method_declaration','class_definition','class_declaration','function_item','impl_item','function_expression','arrow_function','method_definition','function_definition_item'}
        symbols=[]
        def walk(node):
            if node.type in types:
                name=node.child_by_field_name('name')
                if name is None:
                    for c in node.children:
                        if c.type in ('identifier','type_identifier','property_identifier'):
                            name=c;break
                symbols.append({'name':src[name.start_byte:name.end_byte].decode('utf-8','replace') if name else '<anonymous>','kind':node.type,'line':node.start_point.row+1,'end_line':node.end_point.row+1})
            for c in node.children:walk(c)
        walk(tree.root_node)
        return {'language':lang,'engine':'tree-sitter','has_syntax_errors':tree.root_node.has_error,'symbols':symbols}
    except ImportError:
        if lang=='python':
            tree=ast.parse(src.decode('utf-8-sig'))
            return {'language':lang,'engine':'python-ast','symbols':[{'name':n.name,'kind':type(n).__name__,'line':n.lineno,'end_line':n.end_lineno} for n in ast.walk(tree) if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef))]}
        return {'language':lang,'engine':'unavailable','symbols':[],'install':'pip install tree-sitter-language-pack'}

SECRET_PATTERNS={
 'private_key':r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----',
 'aws_access_key':r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
 'github_token':r'\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b',
 'github_fine_grained':r'\bgithub_pat_[A-Za-z0-9_]{20,}\b',
 'slack_token':r'\bxox[baprs]-[A-Za-z0-9-]{10,}\b',
 'generic_credential':r'(?i)\b(?:password|secret|api[_-]?key|access[_-]?token)\b\s*[:=]\s*[\'\"]?([A-Za-z0-9_+/.=-]{12,})',
 'email_pii':r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
}
def redact(text,include_pii=True):
    counts={};out=text
    for name,pattern in SECRET_PATTERNS.items():
        if not include_pii and name=='email_pii':continue
        compiled=re.compile(pattern)
        out,n=compiled.subn(f'[REDACTED:{name}]',out)
        if n:counts[name]=n
    return {'text':out,'findings':counts,'blocked':any(k!='email_pii' for k in counts)}

def safe_context(text,include_pii=True):
    result=redact(text,include_pii)
    if result['blocked']:result['warning']='Credentials detected; do not send raw source to an external model.'
    return result

def coverage_map(path,changed_files):
    """Reads coverage.py JSON or Istanbul JSON. Returns uncovered changed lines."""
    data=json.loads(Path(path).read_text(encoding='utf-8-sig'));out=[]
    for name in changed_files:
        normalized=name.replace('\\','/')
        match=next(((p,v) for p,v in data.get('files',{}).items() if p.replace('\\','/').endswith(normalized)),None)
        if match:
            p,v=match
            if 'executed_lines' in v:
                out.append({'file':name,'matched':p,'covered_lines':len(v.get('executed_lines',[])),'missing_lines':v.get('missing_lines',[]),'format':'coverage.py'})
            elif 's' in v:
                out.append({'file':name,'matched':p,'covered_statements':sum(int(x)>0 for x in v['s'].values()),'uncovered_statements':[k for k,x in v['s'].items() if int(x)==0],'format':'istanbul'})
        else:out.append({'file':name,'matched':None,'warning':'No coverage mapping; run broader tests'})
    return out

def contract_diff(old,new):
    """Conservative OpenAPI 3 comparison: removals and newly required parameters."""
    a=json.loads(Path(old).read_text(encoding='utf-8-sig'));b=json.loads(Path(new).read_text(encoding='utf-8-sig'))
    if not str(a.get('openapi','')).startswith('3.') or not str(b.get('openapi','')).startswith('3.'):
        raise ValueError('Only JSON OpenAPI 3.x supported')
    issues=[]
    for path,methods in a.get('paths',{}).items():
        if path not in b.get('paths',{}):issues.append({'kind':'removed_path','path':path});continue
        for method,operation in methods.items():
            if method not in ('get','post','put','patch','delete','head','options','trace'):continue
            newer=b['paths'][path].get(method)
            if not newer:issues.append({'kind':'removed_operation','path':path,'method':method});continue
            prev={(p.get('in'),p.get('name')):p for p in operation.get('parameters',[]) if '$ref' not in p}
            now={(p.get('in'),p.get('name')):p for p in newer.get('parameters',[]) if '$ref' not in p}
            for key,p in prev.items():
                if key not in now:issues.append({'kind':'removed_parameter','path':path,'method':method,'parameter':key})
                elif not p.get('required') and now[key].get('required'):issues.append({'kind':'parameter_now_required','path':path,'method':method,'parameter':key})
            for key,p in now.items():
                if key not in prev and p.get('required'):issues.append({'kind':'new_required_parameter','path':path,'method':method,'parameter':key})
            for status in operation.get('responses',{}):
                if status not in newer.get('responses',{}):issues.append({'kind':'removed_response','path':path,'method':method,'status':status})
    return {'breaking_candidates':issues,'compatible_by_checked_rules':not issues,'limitations':'Does not resolve $ref or compare schemas; manual review required.'}

class LSPClient:
    """Minimal stdio JSON-RPC client; runs only an explicitly configured executable."""
    def __init__(self,argv,root,timeout=12):
        if not argv or not isinstance(argv,list):raise ValueError('LSP argv must be an explicit list')
        # Windows npm shims (.cmd/.ps1) are only found via PATHEXT, which Popen does not apply
        argv=[shutil.which(argv[0]) or argv[0],*argv[1:]]
        self.proc=subprocess.Popen(argv,cwd=root,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)
        self.q=queue.Queue();self.seq=0;self.timeout=timeout
        threading.Thread(target=self._reader,daemon=True).start()
    def _reader(self):
        stream=self.proc.stdout
        try:
            while True:
                headers={}
                while True:
                    line=stream.readline()
                    if not line:return
                    if line in (b'\r\n',b'\n'):break
                    k,_,v=line.decode('ascii','replace').partition(':');headers[k.lower().strip()]=v.strip()
                length=int(headers['content-length'])
                self.q.put(json.loads(stream.read(length)))
        except (OSError,ValueError,KeyError):return
    def send(self,obj):
        payload=json.dumps(obj).encode();self.proc.stdin.write(f'Content-Length: {len(payload)}\r\n\r\n'.encode()+payload);self.proc.stdin.flush()
    def request(self,method,params):
        self.seq+=1;idx=self.seq;self.send({'jsonrpc':'2.0','id':idx,'method':method,'params':params})
        deadline=time.monotonic()+self.timeout
        while time.monotonic()<deadline:
            try:msg=self.q.get(timeout=max(.01,deadline-time.monotonic()))
            except queue.Empty:break
            if msg.get('id')==idx:
                if 'error' in msg:raise RuntimeError(str(msg['error']))
                return msg.get('result')
        raise TimeoutError('LSP request timed out: '+method)
    def close(self):
        try:self.request('shutdown',None);self.send({'jsonrpc':'2.0','method':'exit','params':{}})
        except Exception:pass
        finally:
            if self.proc.poll() is None:self.proc.terminate()
            try:self.proc.wait(timeout=2)
            except subprocess.TimeoutExpired:self.proc.kill()

def lsp_lookup(argv,root,path,line,column,operation='definition'):
    root=Path(root).resolve();file=Path(path).resolve()
    if not file.is_relative_to(root):raise ValueError('File must be within repo')
    from urllib.parse import quote
    uri=file.as_uri();client=LSPClient(argv,str(root))
    try:
        client.request('initialize',{'processId':os.getpid(),'rootUri':root.as_uri(),'capabilities':{},'workspaceFolders':[{'uri':root.as_uri(),'name':root.name}]})
        client.send({'jsonrpc':'2.0','method':'initialized','params':{}})
        client.send({'jsonrpc':'2.0','method':'textDocument/didOpen','params':{'textDocument':{'uri':uri,'languageId':EXTENSIONS.get(file.suffix,'.txt'),'version':1,'text':file.read_text(encoding='utf-8')}}})
        return client.request('textDocument/'+operation,{'textDocument':{'uri':uri},'position':{'line':line-1,'character':column-1},'context':{'includeDeclaration':True}} if operation=='references' else {'textDocument':{'uri':uri},'position':{'line':line-1,'character':column-1}})
    finally:client.close()

class Mutation(ast.NodeTransformer):
    def __init__(self):self.done=False
    def visit_Constant(self,node):
        if not self.done and isinstance(node.value,bool):
            self.done=True;return ast.copy_location(ast.Constant(not node.value),node)
        return self.generic_visit(node)
    def visit_Compare(self,node):
        self.generic_visit(node)
        if not self.done and node.ops and isinstance(node.ops[0],ast.Lt):
            node.ops[0]=ast.GtE();self.done=True
        return node

def mutation_test(repo,source,test_command,timeout=60):
    """Copies repo into temp dir, mutates one Python expression and runs tests there."""
    root=Path(repo).resolve();src=(root/source).resolve()
    if not src.is_relative_to(root) or src.suffix!='.py' or not src.is_file():raise ValueError('Only Python source within repository')
    if not isinstance(test_command,list) or not test_command:raise ValueError('Explicit test argv required')
    with tempfile.TemporaryDirectory(prefix='agent-mutant-') as temp:
        dest=Path(temp)/'repo'
        shutil.copytree(root,dest,ignore=shutil.ignore_patterns('.git','.venv','venv','node_modules','.agent-system','__pycache__','.env*','*.key','*.pem'),symlinks=False)
        target=dest/src.relative_to(root)
        tree=ast.parse(target.read_text(encoding='utf-8'));mut=Mutation();tree=mut.visit(tree)
        if not mut.done:return {'status':'no_supported_mutation'}
        target.write_text(ast.unparse(ast.fix_missing_locations(tree)),encoding='utf-8')
        try:
            result=subprocess.run(test_command,cwd=dest,capture_output=True,text=True,timeout=timeout,shell=False,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
            return {'status':'killed' if result.returncode else 'survived','exit_code':result.returncode,'output':redact((result.stdout+'\n'+result.stderr)[-2000:])['text'],'note':'Single deterministic mutant; isolated temporary copy; not full mutation coverage.'}
        except subprocess.TimeoutExpired:return {'status':'timeout','note':'Mutation result inconclusive'}
