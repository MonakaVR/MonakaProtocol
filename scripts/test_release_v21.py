"""Minor-aware profile isolation and fail-closed receipt regressions, also under -O."""
import json
import unittest
import release_v2
from release_v21 import gate

class MinorReleaseTests(unittest.TestCase):
    def test_profile_isolation(self):
        self.assertEqual(release_v2.WIRE,{'major':2,'minor':0})
        self.assertEqual(gate.WIRE,{'major':2,'minor':1})
        self.assertEqual(release_v2.CONTRACT,'docs/C2.md')
        self.assertEqual(gate.CONTRACT,'docs/C2.1.md')

    def test_v20_cannot_validate_v21(self):
        raw=json.dumps({'wire_version':{'major':2,'minor':1}}).encode()
        with self.assertRaisesRegex(RuntimeError,'Not current wire'):
            release_v2.check_kit_bytes(b'',raw)

    def test_v21_cannot_validate_v20(self):
        raw=json.dumps({'wire_version':{'major':2,'minor':0}}).encode()
        with self.assertRaisesRegex(RuntimeError,'Not current wire'):
            gate.check_kit_bytes(b'',raw)

    def test_policy_required_commands(self):
        policy=json.loads((gate.ROOT/'scripts/release_v21.json').read_text())
        self.assertEqual(policy['required_steps'],[s['name'] for s in policy['commands']])
        self.assertIn('schema-codec-v21',policy['required_steps'])
        self.assertIn('old-decoder-build',policy['required_steps'])
        for s in policy['commands']:
            if s['name'] in ['package-kit-v21','isolated-consumer-v21']:
                self.assertEqual(s['command'][-2:],['--wire-minor','1'])

if __name__=='__main__': unittest.main()
