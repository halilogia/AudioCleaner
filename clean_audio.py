#!/usr/bin/env python3
"""
AudioCleaner Main CLI Entry Point.
"""

import sys
import os

# Add src to path
src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from src.clean_audio import main

if __name__ == "__main__":
    main()
