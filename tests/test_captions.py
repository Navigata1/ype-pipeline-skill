"""Source-fidelity regressions for temporal caption cleanup."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'skills/ype-pipeline/scripts'))
import core


class CaptionTimeFidelity(unittest.TestCase):
    def test_separated_identical_caption_is_preserved(self):
        raw = ('00:00.000 --> 00:02.000\nTest the result.\n\n'
               '10:00.000 --> 10:02.000\nTest the result.\n')
        self.assertEqual(core.captions(raw), [
            {'start': 0., 'end': 2., 'text': 'Test the result.'},
            {'start': 600., 'end': 602., 'text': 'Test the result.'},
        ])

    def test_touching_windows_are_not_rolling_overlap(self):
        raw = ('00:00.000 --> 00:01.000\nhello world\n\n'
               '00:01.000 --> 00:02.000\nhello world and more\n')
        self.assertEqual([cue['text'] for cue in core.captions(raw)],
                         ['hello world', 'hello world and more'])

    def test_separated_sentence_keeps_shared_leading_word(self):
        raw = ('00:00.000 --> 00:02.000\nWe need tests\n\n'
               '10:00.000 --> 10:02.000\ntests should cover failure\n')
        self.assertEqual(core.captions(raw)[1]['text'], 'tests should cover failure')

    def test_single_word_match_is_ambiguous_even_during_overlap(self):
        raw = ('00:00.000 --> 00:02.000\nWe need tests\n\n'
               '00:01.000 --> 00:03.000\ntests should cover failure\n')
        self.assertEqual(core.captions(raw)[1]['text'], 'tests should cover failure')

    def test_identical_text_with_different_overlapping_times_is_preserved(self):
        raw = ('00:00.000 --> 00:02.000\nTest the result.\n\n'
               '00:01.000 --> 00:03.000\nTest the result.\n')
        self.assertEqual(len(core.captions(raw)), 2)

    def test_identical_text_at_identical_times_is_deduplicated(self):
        raw = ('00:00.000 --> 00:02.000\nTest the result.\n\n'
               '00:00.000 --> 00:02.000\nTest the result.\n')
        self.assertEqual(core.captions(raw), [
            {'start': 0., 'end': 2., 'text': 'Test the result.'},
        ])

    def test_rolling_overlap_preserves_fresh_words_and_original_cue_times(self):
        raw = ('WEBVTT\n\n00:00.000 --> 00:02.000\nhello world\n\n'
               '00:01.000 --> 00:03.000\nhello world and more\n\n'
               '00:02.000 --> 00:04.000\nand more follows\n')
        self.assertEqual(core.captions(raw), [
            {'start': 0., 'end': 2., 'text': 'hello world'},
            {'start': 1., 'end': 3., 'text': 'and more'},
            {'start': 2., 'end': 4., 'text': 'follows'},
        ])

    def test_contained_or_reordered_windows_are_preserved(self):
        for timing in ['00:01.000 --> 00:02.000', '00:00.000 --> 00:05.000']:
            with self.subTest(timing=timing):
                raw = ('00:01.000 --> 00:04.000\nhello world\n\n'
                       + timing + '\nhello world and more\n')
                self.assertEqual(core.captions(raw)[1]['text'], 'hello world and more')

    def test_overlap_without_new_words_is_preserved(self):
        raw = ('00:00.000 --> 00:02.000\nWe need thorough tests\n\n'
               '00:01.000 --> 00:03.000\nthorough tests\n')
        self.assertEqual([cue['text'] for cue in core.captions(raw)],
                         ['We need thorough tests', 'thorough tests'])

    def test_cleanup_audit_records_policy_and_exact_removals(self):
        self.assertTrue(callable(getattr(core, 'captions_with_audit', None)))
        raw = ('00:00.000 --> 00:02.000\nhello world\n\n'
               '00:01.000 --> 00:03.000\nhello world and more\n\n'
               '00:01.000 --> 00:03.000\nhello world and more\n')
        result = core.captions_with_audit(raw)
        self.assertEqual(result['policy'], 'caption-time-v1')
        self.assertEqual(result['cues'], core.captions(raw))
        self.assertEqual(result['input_cue_count'], 3)
        self.assertEqual(result['output_cue_count'], 2)
        self.assertEqual([d['action'] for d in result['decisions']],
                         ['kept', 'trimmed_rolling_prefix', 'skipped_same_time_duplicate'])
        trimmed = result['decisions'][1]
        self.assertEqual(trimmed['input_cue_index'], 1)
        self.assertEqual(trimmed['output_cue_index'], 1)
        self.assertEqual(trimmed['original_text'], 'hello world and more')
        self.assertEqual(trimmed['removed_prefix'], 'hello world')
        self.assertEqual(trimmed['start'], 1.)
        self.assertEqual(trimmed['end'], 3.)
        self.assertIsNone(result['decisions'][2]['output_cue_index'])

    def test_identical_window_with_distinct_text_is_ambiguous(self):
        raw = ('00:00.000 --> 00:02.000\nhello world\n\n'
               '00:00.000 --> 00:02.000\nhello world and more\n')
        self.assertEqual([cue['text'] for cue in core.captions(raw)],
                         ['hello world', 'hello world and more'])


if __name__ == '__main__':
    unittest.main()
