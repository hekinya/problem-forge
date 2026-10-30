import json
import hashlib
from pathlib import Path
import shutil
import uuid
import unittest

from tools.export_xcpc import make_contest


class XcpcExportTests(unittest.TestCase):
    def setUp(self):
        scratch = Path(__file__).resolve().parents[1] / '.tmp'
        self.root = scratch / uuid.uuid4().hex
        self.root.mkdir(parents=True)
        def cleanup():
            assert self.root.resolve().parent == scratch.resolve()
            shutil.rmtree(self.root)
        self.addCleanup(cleanup)
        samples = self.root / 'data/samples'
        samples.mkdir(parents=True)
        (samples / '01.in').write_text('1\n', encoding='utf-8')
        (samples / '01.out').write_text('2\n', encoding='utf-8')
        (self.root / 'problem.json').write_text(json.dumps({
            'title': 'Example', 'time_limit_ms': 2500, 'memory_limit_mb': 128,
        }), encoding='utf-8')
        self.source = self.root / 'statement.md'
        self.text = '''---
title: Example
---
Compute $a+1$.
# Input {#input}
An integer $a$.
# Output {#output}
The result.
::: {.samples}
``` {.input}
1
```
``` {.output}
2
```
:::
# Explanation {#explanation}
One plus one is two.
'''
        self.source.write_text(self.text, encoding='utf-8')

    def test_actual_limits_and_samples_are_preserved(self):
        p = make_contest([self.root], 'Contest')['problems'][0]
        self.assertEqual(p['problem']['samples'], [{'input': '1', 'output': '2'}])
        self.assertEqual(p['problem']['limits'][2]['value'], '2.5 s')
        self.assertEqual(p['problem']['limits'][3]['value'], '128 MB')
        self.assertIn('$a+1$', p['statement']['description'])

    def test_stale_markdown_sample_is_rejected(self):
        (self.root / 'data/samples/01.out').write_text('3\n')
        with self.assertRaisesRegex(ValueError, 'samples differ'):
            make_contest([self.root], 'Contest')

    def test_tutorial_is_excluded(self):
        self.source.write_text(self.text + '\n# Tutorial {#tutorial}\nSECRET\n', encoding='utf-8')
        self.assertNotIn('SECRET', json.dumps(make_contest([self.root], 'Contest')))

    def test_unknown_section_is_not_silently_lost(self):
        self.source.write_text(self.text + '\n# Scoring {#scoring}\nPartial credit.\n', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'Unsupported section'):
            make_contest([self.root], 'Contest')


class DependencyArchiveTests(unittest.TestCase):
    def test_bundled_packages_match_manifest(self):
        vendor = Path(__file__).resolve().parents[1] / 'vendor/xcpc-statement-generator'
        manifest = json.loads((vendor / 'dependencies.json').read_text(encoding='utf-8'))
        for package in manifest['packages']:
            with self.subTest(package=package['name']):
                payload = (vendor / package['file']).read_bytes()
                self.assertEqual(hashlib.sha256(payload).hexdigest(), package['sha256'])
