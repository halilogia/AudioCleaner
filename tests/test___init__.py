#!/usr/bin/env python3
"""
Unit tests for AudioCleaner package exports in src/__init__.py.
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

import src


class TestPackageInit(unittest.TestCase):

    def test_version_defined(self):
        self.assertTrue(hasattr(src, "__version__"))
        self.assertEqual(src.__version__, "1.0.0")

    def test_all_exports_present(self):
        expected_exports = [
            "FillerDetector",
            "DetectionPlan",
            "WordToken",
            "AudioCut",
            "KeepSegment",
            "AudioCutter",
            "AudioCleaningPipeline"
        ]
        for exp in expected_exports:
            self.assertTrue(hasattr(src, exp), f"Missing export: {exp}")
            self.assertIn(exp, src.__all__)


if __name__ == "__main__":
    unittest.main()
