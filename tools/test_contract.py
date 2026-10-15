"""Executable native/JVM golden, malformed, semantic and legacy compatibility tests."""
import argparse,concurrent.futures,hashlib,json,os,pathlib,subprocess
R=pathlib.Path(__file__).resolve().parents[1]
JAVA=pathlib.Path(os.environ.get('JAVA_HOME','C:/Program Files/Microsoft/jdk-17.0.20.101-hotspot'))/'bin/java.exe'
def commands(kind):
 cp=os.pathsep.join(str(p) for p in [R/'jvm/build/classes/kotlin/test',R/'jvm/build/libs/monaka-input-protocol.jar',R/'jvm/libs/gson-2.11.0.jar',R/'jvm/libs/kotlin-stdlib-2.3.10.jar'])
 return [[str(R/'build/native/Release'/('mvip_codec_runner.exe' if kind=='codec' else 'mvip_capabilities_runner.exe'))],[str(JAVA),'-Dfile.encoding=UTF-8','-cp',cp,'dev.monaka.protocol.v2.Runner' if kind=='codec' else 'dev.monaka.input.CapabilityRunner']]
def run(cmd,*args):return subprocess.check_output(cmd+list(map(str,args)),encoding='utf-8',timeout=30).strip()
def main():
 scratch=R/'build/contract-tests';scratch.mkdir(parents=True,exist_ok=True)
 golden=json.loads((R/'tests/frozen-canonical.sha256.json').read_text())
 jobs=[]
 for family in ['v2','v2.1','v2.2']:
  for row in json.loads((R/'fixtures'/family/'index.json').read_text()):jobs.append((family,row))
 def check(pair):
  family,row=pair;path=R/'fixtures'/family/row['file'];outs=[];cross=0
  for i,cmd in enumerate(commands('codec')):
   out=run(cmd,path)
   if row['error']:assert out=='ERROR:'+row['error'],(family,row['file'],out)
   else:
    assert not out.startswith('ERROR:'),(family,row['file'],out)
    assert hashlib.sha256(out.encode()).hexdigest()==golden['hashes'][family+'/'+row['file']][str(i)],('frozen canonical bytes',family,row['file'],i)
    dest=scratch/(family.replace('.','_')+'-'+row['file'].replace('/','_')+'-'+str(i)+'.json');dest.write_text(out,encoding='utf-8')
    assert json.loads(run(commands('codec')[1-i],dest))==json.loads(out),('cross language',path)
    cross+=1
   outs.append(out)
  if not row['error']:assert json.loads(outs[0])==json.loads(outs[1]),path
  return cross
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:cross=sum(pool.map(check,jobs))
 semantic=0
 for row in json.loads((R/'fixtures/p1/index.json').read_text()):
  for cmd in commands('semantic'):
   out=run(cmd,R/'fixtures/p1'/row['file'])
   if row['error']:assert out=='ERROR:'+row['error'],(row['file'],out)
   else:
    actual=json.loads(out)
    for token in ['position','orientation','linear_velocity','angular_velocity','linear_acceleration','battery_fraction','charging']:
     assert actual['channels'][token]['state']==row['states'].get(token,'UNSUPPORTED'),(row['file'],token,actual['channels'][token])
     assert actual['channels'][token]['valid']==(row['states'].get(token)=='VALID')
    # Projection must not rewrite version, identity, validity, time, space or wire ordering.
    codec=run(commands('codec')[0],R/'fixtures/p1'/row['file'])
    assert actual['wire']==json.loads(codec),(row['file'],cmd[-1],actual['wire'],json.loads(codec))
   semantic+=1
 for cmd in commands('semantic'):assert run(cmd,'--self-test').startswith('PASS')
 assert run(commands('codec')[0],'--self-test').startswith('PASS')
 assert run(commands('codec')[1],R/'fixtures/v2/observation.json','--self-test').startswith('PASS')
 summary=dict(status='PASS',frozen_fixtures=len(jobs),codec_probes=len(jobs)*2,cross_language_directions=cross,semantic_probes=semantic,api_self_tests=4,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip())
 (R/'build/test-results.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary))
if __name__=='__main__':main()
