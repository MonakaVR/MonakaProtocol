"""Selective, byte-preserving import from the P0 frozen Git commit (no merge)."""
import hashlib,json,pathlib,subprocess
R=pathlib.Path(__file__).resolve().parents[1]
REF='0b4a27c2e2de88705c92fb6dbf5a8d9ca752bf39'
files=subprocess.check_output(['git','-C',str(R),'ls-tree','-r','--name-only',REF]).decode().splitlines()
prefixes=('cpp/include/monaka/protocol/v2/','cpp/src/v2/','jvm/src/main/kotlin/dev/monaka/protocol/v2/','schema/v2/','fixtures/v2/','fixtures/v2.1/','fixtures/v2.2/')
exact={'cpp/third_party/nlohmann/json.hpp','cpp/tests/runner_v2.cpp','jvm/src/test/kotlin/dev/monaka/protocol/v2/Runner.kt','jvm/libs/gson-2.11.0.jar','jvm/libs/kotlin-stdlib-2.3.10.jar','docs/C1.md','docs/C2.md','docs/C2.1.md','docs/C2.2.md','LICENSE','NOTICE'}
selected=[p for p in files if p.startswith(prefixes) or p in exact or p.startswith('licenses/')]
hashes={}
for path in selected:
 data=subprocess.check_output(['git','-C',str(R),'show',REF+':'+path])
 out=R/path;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(data)
 hashes[path]=hashlib.sha256(data).hexdigest()
(R/'dependencies').mkdir(exist_ok=True)
(R/'dependencies/frozen-wire22.lock.json').write_text(json.dumps(dict(repository='MonakaVR/MonakaVRInputProtocol',ref='feature/common-world-publisher-identity-wire-v2.2',source_commit=REF,scope='selected v2 codecs/models/schema/specs/fixtures/dependencies only; no branch merge, v1 implementation, runtime, packaging or historical handoffs',files_sha256=hashes),indent=2),encoding='utf-8')
print('Imported',len(selected),'individually pinned files')
