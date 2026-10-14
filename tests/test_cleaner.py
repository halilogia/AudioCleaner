#!/usr/bin/env python3
"""
Unit tests for AudioCleaner.
"""

import os
import sys
import tempfile
import subprocess
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from filler_detector import FillerDetector, WordToken
from audio_cutter import AudioCutter


class TestAudioCleaner(unittest.TestCase):

    def setUp(self):
        self.detector = FillerDetector(include_conversational=True)
        self.cutter = AudioCutter(fade_duration_ms=12.0)

    def test_turkish_text_cleaning(self):
        raw = "Iıı, ŞEY, Yani... İŞTE!"
        cleaned = FillerDetector._clean_text(raw)
        self.assertEqual(cleaned, "ııı şey yani işte")

    def test_cut_planning_fillers_and_pauses(self):
        words = [
            WordToken("Merhaba", "merhaba", 0.0, 0.8, 0.99),
            WordToken("ııı", "ııı", 1.2, 1.8, 0.85, is_filler=True, filler_type="sound"),
            WordToken("arkadaşlar", "arkadaşlar", 3.0, 3.8, 0.98),  # pause before
            WordToken("şey", "şey", 4.0, 4.4, 0.90, is_filler=True, filler_type="conversational"),
            WordToken("hoşgeldiniz", "hoşgeldiniz", 4.6, 5.4, 0.99)
        ]
        plan = self.detector.plan_cuts(words, total_duration=6.5)
        self.assertEqual(plan.fillers_detected, 2)
        self.assertGreater(plan.cut_duration, 1.0)
        self.assertGreater(len(plan.keep_segments), 1)

    def test_audio_cutter_slicing(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            input_wav = os.path.join(tmpdir, "in.wav")
            out_wav = os.path.join(tmpdir, "out.wav")

            # Generate synthetic 4-second audio
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi", "-i", "sine=frequency=440:duration=4",
                "-c:a", "pcm_s16le", input_wav
            ], capture_output=True, check=True)

            keep = [{"start": 0.0, "end": 1.0}, {"start": 2.0, "end": 3.0}]
            ok = self.cutter.cut_media(input_wav, out_wav, keep, is_video=False)
            self.assertTrue(ok)
            self.assertTrue(os.path.exists(out_wav))


if __name__ == "__main__":
    unittest.main()
