#!/usr/bin/env python3
"""
Unit tests for clean_audio CLI and pipeline runner.
"""

import unittest
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import clean_audio
from src.clean_audio import AudioCleaningPipeline


class TestCleanAudioCLI(unittest.TestCase):

    def test_pipeline_initialization(self):
        pipeline = AudioCleaningPipeline(
            include_conversational=True,
            max_pause_sec=0.40,
            fade_duration_ms=15.0
        )
        self.assertIsNotNone(pipeline.detector)
        self.assertIsNotNone(pipeline.cutter)
        self.assertEqual(pipeline.detector.max_pause_sec, 0.40)
        self.assertEqual(pipeline.cutter.fade_duration_sec, 0.015)

    def test_clean_audio_module_has_main(self):
        self.assertTrue(hasattr(clean_audio, "main"))
        self.assertTrue(callable(clean_audio.main))


if __name__ == "__main__":
    unittest.main()
