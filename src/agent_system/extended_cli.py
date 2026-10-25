import argparse,json,sqlite3
from pathlib import Path
from . import intelligence as I
from .core import connect,timestamp
ROOT=Path(__file__).resolve().parents[2]
def emit(x):print(json.dumps(x,indent=2,ensure_ascii=False))
def run(argv):
    p=argparse.ArgumentParser(prog='agent.py intelligence');s=p.add_subparsers(dest='cmd',required=True)
    q=s.add_parser('search');q.add_argument('query')
    c=s.add_parser('context');c.add_argument('query');c.add_argument('--budget',type=int,default=3000)
    im=s.add_parser('impact');im.add_argument('repo');im.add_argument('path')
    ar=s.add_parser('artifact');ar.add_argument('id');ar.add_argument('repo');ar.add_argument('kind');ar.add_argument('content_file');ar.add_argument('sources',nargs='+')
    s.add_parser('stale')
    l=s.add_parser('lesson');l.add_argument('repo');l.add_argument('problem');l.add_argument('solution');l.add_argument('evidence')
    s.add_parser('lessons')
    ck=s.add_parser('check');ck.add_argument('task');ck.add_argument('repo');ck.add_argument('kind');ck.add_argument('status',choices=['pass','fail','skip']);ck.add_argument('--evidence',default='')
    g=s.add_parser('gate');g.add_argument('task');g.add_argument('--required',default='unit,integration,regression')
    wt=s.add_parser('worktree');wt.add_argument('repo');wt.add_argument('branch');wt.add_argument('path');wt.add_argument('--confirm',action='store_true')
    se=s.add_parser('skill-eval');se.add_argument('skill');se.add_argument('task');se.add_argument('outcome',choices=['pass','fail']);se.add_argument('--notes',default='')
    be=s.add_parser('benchmark');be.add_argument('task');be.add_argument('provider');be.add_argument('success',type=int,choices=[0,1]);be.add_argument('seconds',type=float);be.add_argument('--tokens',type=int);be.add_argument('--model',default='');be.add_argument('--interventions',type=int,default=0)
    s.add_parser('benchmark-report')
    a=p.parse_args(argv);db=connect(ROOT/'.agent-system/state.sqlite3');I.init(db)
    if a.cmd=='search':emit(I.search(db,a.query))
    elif a.cmd=='context':emit(I.context(db,a.query,a.budget))
    elif a.cmd=='impact':emit(I.impact(db,a.repo,a.path))
    elif a.cmd=='artifact':emit(I.save_artifact(db,a.id,a.repo,a.kind,Path(a.content_file).read_text(encoding='utf-8'),a.sources))
    elif a.cmd=='stale':emit(I.stale(db))
    elif a.cmd=='lesson':
        with db:db.execute('INSERT INTO lessons(repo,problem,solution,evidence,created_at) VALUES(?,?,?,?,?)',(a.repo,a.problem,a.solution,a.evidence,timestamp()))
        emit({'saved':True})
    elif a.cmd=='lessons':emit([dict(zip(['id','repo','problem','solution','evidence'],r)) for r in db.execute('SELECT id,repo,problem,solution,evidence FROM lessons ORDER BY id DESC LIMIT 50')])
    elif a.cmd=='check':
        with db:db.execute('INSERT INTO checks(task,repo,kind,status,evidence,created_at) VALUES(?,?,?,?,?,?)',(a.task,a.repo,a.kind,a.status,a.evidence,timestamp()))
        emit(I.quality(db,a.task))
    elif a.cmd=='gate':
        result=I.quality(db,a.task,tuple(x for x in a.required.split(',') if x));emit(result)
        if not result['passed']:raise SystemExit(2)
    elif a.cmd=='worktree':
        if not a.confirm:raise SystemExit('Worktree changes git state. Re-run with --confirm after reviewing target and branch.')
        emit(I.worktree(db,a.repo,a.branch,a.path))
    elif a.cmd=='skill-eval':
        with db:db.execute('INSERT INTO skill_evals(skill,task,outcome,notes,created_at) VALUES(?,?,?,?,?)',(a.skill,a.task,a.outcome,a.notes,timestamp()))
        emit({'saved':True})
    elif a.cmd=='benchmark':
        with db:db.execute('INSERT INTO benchmarks(task,provider,model,success,seconds,tokens,human_interventions,created_at) VALUES(?,?,?,?,?,?,?,?)',(a.task,a.provider,a.model,a.success,a.seconds,a.tokens,a.interventions,timestamp()))
        emit({'saved':True})
    elif a.cmd=='benchmark-report':
        emit([dict(zip(['provider','runs','success_rate','avg_seconds','avg_tokens','avg_interventions'],r)) for r in db.execute('SELECT provider,COUNT(*),ROUND(AVG(success),3),ROUND(AVG(seconds),2),ROUND(AVG(tokens),1),ROUND(AVG(human_interventions),2) FROM benchmarks GROUP BY provider')])
