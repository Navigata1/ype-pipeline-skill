"""The README's cached quick-analysis example must still verify under the current code.

A changed parser or policy can invalidate a published example while its stored
validation.json still says pass: runs/cached-smoke went stale this way when the
caption parser changed on 2026-10-14. This check re-runs publish.validate on the
linked run with every write stubbed, so the example's bytes never change. A
failure means: make a new run and repoint README and HANDOFF; never edit the old run.
"""
import re
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/ype-pipeline/scripts'))
import community
import core
import publish

README = ROOT / 'README.md'
LINK = re.compile(r'\[See the cached quick-analysis example\]\((runs/[^)\s]+)/report\.html\)')


def linked_example(readme_text):
    """The run folder that the README's cached-example link points at."""
    match = LINK.search(readme_text)
    if not match:
        raise AssertionError('README has no "See the cached quick-analysis example" link to runs/RUN/report.html')
    return (ROOT / match.group(1)).resolve()


def fingerprint(folder):
    """SHA-256 of every file under folder, keyed by relative path."""
    return {str(p.relative_to(folder)): core.sha(p) for p in sorted(folder.rglob('*')) if p.is_file()}


def read_only_validation(run_root):
    """publish.validate with every file write stubbed out."""
    def refuse(path, text):
        pass
    with patch.object(core, 'write_text', refuse), patch.object(publish, 'write_text', refuse), \
            patch.object(community, 'write_text', refuse):
        return publish.validate(run_root)


class LinkedCachedExample(unittest.TestCase):
    """README promises a passing cached example; hold its link to that promise."""

    def setUp(self):
        if not (ROOT / 'runs').is_dir():
            self.skipTest('no runs/ folder: this checks a workspace example, not a bare skill checkout')
        self.run_root = linked_example(README.read_text())

    def test_link_points_at_a_rendered_cached_quick_run(self):
        run = core.read(self.run_root / 'run.json')
        self.assertTrue((self.run_root / 'report.html').is_file(), 'the linked report.html is missing')
        self.assertEqual(run['mode'], 'quick')
        self.assertFalse(run.get('test_fixture'), 'a synthetic fixture cannot be the published example')
        origins = {v['id']: core.read(self.run_root / 'videos' / v['id'] / 'media.json')['origin'] for v in run['videos']}
        self.assertEqual(set(origins.values()), {'cached-reprocessing'}, origins)

    def test_linked_example_verifies_without_changing_a_byte(self):
        before = fingerprint(self.run_root)
        report = read_only_validation(self.run_root)
        self.assertEqual(fingerprint(self.run_root), before, 'validation changed the example run')
        problems = report['batch_errors'] + [f"{row['id']}: {error}" for row in report['per_video'] for error in row['errors']]
        self.assertTrue(report['integrity_pass'],
                        f'{self.run_root.name} no longer verifies under the current code: {problems}. '
                        'Make a new run and repoint README and HANDOFF; do not edit the old run.')


if __name__ == '__main__':
    unittest.main()
