"""Imported files are immutable; modifications require an explicit provenance update."""
import hashlib,json,pathlib
R=pathlib.Path(__file__).resolve().parents[1]
lock=json.loads((R/'dependencies/frozen-wire22.lock.json').read_text())
for name,digest in lock['files_sha256'].items():
 assert hashlib.sha256((R/name).read_bytes()).hexdigest()==digest,'Frozen import changed: '+name
print('PASS',len(lock['files_sha256']),'frozen 2.2 source/fixture/dependency hashes')
