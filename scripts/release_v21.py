"""Explicit wire 2.1 release profile; default release_v2 remains strict 2.0."""
import json
import importlib.util
from pathlib import Path

# Load an isolated gate module: importing this profile never changes release_v2.
spec=importlib.util.spec_from_file_location('monaka_release_v21_gate',Path(__file__).with_name('release_v2.py'))
gate=importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

gate.WIRE={'major':2,'minor':1}
gate.CONTRACT='docs/C2.1.md'
gate.KIT_PROFILE='v2.1'
gate.RELEASE_PROFILE='release-v21'

if __name__=='__main__':
    gate.run(json.loads((gate.ROOT/'scripts/release_v21.json').read_bytes()))
