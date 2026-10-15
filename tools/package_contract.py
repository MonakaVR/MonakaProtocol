"""Create an exact clean-source MVIP dependency kit for MBIP; build output only."""
import hashlib,json,pathlib,subprocess,zipfile
R=pathlib.Path(__file__).resolve().parents[1]
assert not subprocess.check_output(['git','status','--porcelain'],cwd=R).strip(),'Commit reviewed implementation before packaging'
sha=subprocess.check_output(['git','rev-parse','HEAD'],cwd=R).decode().strip()
test=json.loads((R/'build/test-results.json').read_text());assert test['status']=='PASS'
tracked=subprocess.check_output(['git','ls-files'],cwd=R).decode().splitlines()
names=[n for n in tracked if n.startswith(('cpp/','schema/','licenses/')) or n in ['docs/capabilities-contract.md','docs/C1.md','docs/C2.md','docs/C2.1.md','docs/C2.2.md','NOTICE']]
data={n:(R/n).read_bytes() for n in names}
for name in ['monaka-input-protocol.jar','gson-2.11.0.jar','kotlin-stdlib-2.3.10.jar']:
 path=R/('jvm/build/libs/' if name=='monaka-input-protocol.jar' else 'jvm/libs/')/name
 data['jvm/libs/'+name]=path.read_bytes()
manifest=dict(repository='MonakaVR/MonakaVRInputProtocol',source_commit=sha,source_tree_clean=True,contract='mvip-capabilities-p1',frozen_wire_commit='0b4a27c2e2de88705c92fb6dbf5a8d9ca752bf39',files_sha256={n:hashlib.sha256(b).hexdigest() for n,b in sorted(data.items())})
data['kit.lock.json']=(json.dumps(manifest,indent=2)+'\n').encode()
out=R/'build/distribution';out.mkdir(exist_ok=True)
archive=out/'mvip-capabilities-p1.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for name,content in sorted(data.items()):
  info=zipfile.ZipInfo(name,(2026,10,15,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;z.writestr(info,content)
pin=dict(repository=manifest['repository'],source_commit=sha,artifact=archive.name,sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),contract=manifest['contract'],files_sha256=manifest['files_sha256'])
(out/'handoff.json').write_text(json.dumps(pin,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:pin[k] for k in ['source_commit','artifact','sha256']}))
