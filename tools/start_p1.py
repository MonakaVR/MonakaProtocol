"""One-time P1 evidence capture; no audit/source writes outside this development clone."""
import hashlib,json,pathlib,re,subprocess
R=pathlib.Path(__file__).resolve().parents[1]
W=R.parents[1]
P0=W/'hil/phase2cp0-protocol-audit-20261015'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report=(P0/'report.md').read_text(encoding='utf-8')
ids=['H-01','M-02','M-03','M-05']
findings={i:next(x for x in report.splitlines() if x.startswith('**'+i+' ')) for i in ids}
notes=R/'docs/p1';notes.mkdir(parents=True,exist_ok=True)
(notes/'p0-capabilities-findings.md').write_text('# Exact P0 findings for P1\n\nSource: '+str(P0/'report.md')+'\n\nSHA256: `'+sha(P0/'report.md')+'`\n\n'+ '\n\n'.join(findings.values())+'\n\nM-02: multi-channel representability is in scope; independent raw IMU streams/authenticity remain deferred. M-03: effective validity/diagnostic separation only. M-05: capability-related compatibility harness only; session/space/reconnect remain deferred. No severity is changed.\n',encoding='utf-8')
states=[]
for role,path in [('audit',W/'MonakaVRInputProtocol'),('audit',W/'MonakaBridgeInputProtocol'),('development',R),('development',R.parent/'MonakaBridgeInputProtocol')]:
 def git(*a):return subprocess.check_output(['git','--no-optional-locks','-C',str(path),*a]).decode().strip()
 states.append(dict(role=role,path=str(path),remote=git('remote','get-url','origin'),branch=git('branch','--show-current'),head=git('rev-parse','HEAD'),origin_dev=git('rev-parse','origin/dev'),status=git('status','--porcelain=v1'),git_common_dir=git('rev-parse','--path-format=absolute','--git-common-dir')))
(notes/'phase-start.json').write_text(json.dumps(dict(base_mvip='cad72656f6e90def6dc55ee4c20fe9a181d37baf',base_mbip='e334bfeceb7f922b3cacfc0d17eace82c0fabf33',frozen_reference='0b4a27c2e2de88705c92fb6dbf5a8d9ca752bf39',instruction_sha256=sha(pathlib.Path('C:/Users/nynyp/Downloads/Phase_2C-P1_Capabilities_Contract_Reconciliation.md')),p0_report_sha256=sha(P0/'report.md'),p0_targets_sha256=sha(P0/'frozen-targets.md'),states=states),indent=2),encoding='utf-8')
print('Captured exact findings and independent clone state')
