#!/usr/bin/env python3
"""
Turkish & Multilingual Audio/Video Cleaner CLI & API.
Detects and removes vocal fillers ("ııı", "eee", "şey", "yani", "ımm" etc.)
and awkward pauses with smooth cross-fades using local Faster-Whisper + FFmpeg.
"""

import os
import sys
import argparse
import json
import time
import logging
from typing import Dict, List, Optional, Any

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure tool directory is on sys.path
tool_dir = os.path.dirname(os.path.abspath(__file__))
if tool_dir not in sys.path:
    sys.path.insert(0, tool_dir)

from filler_detector import FillerDetector, DetectionPlan
from audio_cutter import AudioCutter

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] [CLEAN-AUDIO] %(message)s")
logger = logging.getLogger("clean_audio")


class AudioCleaningPipeline:
    """
    Unified end-to-end audio/video disfluency and pause remover.
    """

    def __init__(
        self,
        model_size: str = "base",
        include_conversational: bool = True,
        custom_fillers: Optional[List[str]] = None,
        max_pause_sec: float = 0.45,
        pause_retention_sec: float = 0.20,
        fade_duration_ms: float = 12.0
    ):
        self.detector = FillerDetector(
            model_size=model_size,
            include_conversational=include_conversational,
            custom_fillers=custom_fillers,
            max_pause_sec=max_pause_sec,
            pause_retention_sec=pause_retention_sec
        )
        self.cutter = AudioCutter(fade_duration_ms=fade_duration_ms)

    def process(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        language: str = "tr",
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Processes the input audio/video file and returns the cleaning results.
        """
        start_time = time.time()
        if not os.path.isfile(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Derive output path if not given
        if not output_path:
            base, ext = os.path.splitext(input_path)
            output_path = f"{base}_clean{ext}"

        logger.info(f"Starting audio cleaning on: {input_path}")

        # 1. Detect words and timestamps with Faster-Whisper
        words, total_duration = self.detector.transcribe_with_words(input_path, language=language)

        # 2. Plan cuts and keep intervals
        plan = self.detector.plan_cuts(words, total_duration)

        logger.info(
            f"Analysis complete: {plan.fillers_detected} fillers detected, "
            f"{plan.silences_trimmed} pauses trimmed. "
            f"Reduction: {plan.cut_duration:.2f}s (-{plan.reduction_percentage:.1f}%)"
        )

        if dry_run:
            logger.info("Dry-run mode active. No audio cutting performed.")
            return {
                "success": True,
                "dry_run": True,
                "input_file": input_path,
                "plan": plan.to_dict(),
                "duration_sec": round(time.time() - start_time, 2)
            }

        if not plan.cuts:
            logger.info("No fillers or pauses detected. Media is already clean!")
            return {
                "success": True,
                "cleaned": False,
                "input_file": input_path,
                "output_file": input_path,
                "message": "Media has no detected fillers or awkward pauses.",
                "plan": plan.to_dict(),
                "duration_sec": round(time.time() - start_time, 2)
            }

        # 3. Perform cutting with anti-click zero-crossing micro-fades
        keep_dicts = [{"start": k.start, "end": k.end} for k in plan.keep_segments]
        ok = self.cutter.cut_media(input_path, output_path, keep_dicts)

        elapsed = round(time.time() - start_time, 2)
        if ok:
            logger.info(f"🎉 Cleaning finished in {elapsed}s! Output saved to: {output_path}")
            return {
                "success": True,
                "cleaned": True,
                "input_file": input_path,
                "output_file": output_path,
                "plan": plan.to_dict(),
                "duration_sec": elapsed
            }
        else:
            logger.error("FFmpeg cutting failed.")
            return {
                "success": False,
                "cleaned": False,
                "error": "FFmpeg slice rendering failed.",
                "plan": plan.to_dict(),
                "duration_sec": elapsed
            }


def main():
    parser = argparse.ArgumentParser(description="Turkish & Multilingual Audio Filler Word and Pause Remover")
    parser.add_argument("input", help="Path to input audio or video file")
    parser.add_argument("-o", "--output", help="Path to output file (default: <input>_clean.<ext>)")
    parser.add_argument("--lang", default="tr", help="Language code (default: 'tr')")
    parser.add_argument("--mode", choices=["all", "sounds_only"], default="all",
                        help="Filler mode: 'all' (sounds + conversational words like şey/yani) or 'sounds_only' (ııı/eee only)")
    parser.add_argument("--max-pause", type=float, default=0.45, help="Maximum allowed silence pause in seconds (default: 0.45)")
    parser.add_argument("--crossfade-ms", type=float, default=12.0, help="Micro-fade duration in ms (default: 12.0)")
    parser.add_argument("--dry-run", action="store_true", help="Analyze and print plan without cutting media")
    parser.add_argument("--report", action="store_true", help="Print full JSON detection plan to stdout")

    args = parser.parse_args()

    include_conv = (args.mode == "all")
    pipeline = AudioCleaningPipeline(
        include_conversational=include_conv,
        max_pause_sec=args.max_pause,
        fade_duration_ms=args.crossfade_ms
    )

    res = pipeline.process(
        input_path=args.input,
        output_path=args.output,
        language=args.lang,
        dry_run=args.dry_run
    )

    if args.report:
        print(json.dumps(res, ensure_ascii=False, indent=2))
    else:
        print("\n" + "="*50)
        print("🎙️ AUDIO CLEANER İŞLEM ÖZETİ")
        print("="*50)
        print(f"Girdi: {res.get('input_file')}")
        if res.get('cleaned'):
            print(f"Çıktı: {res.get('output_file')}")
            plan = res.get('plan', {})
            print(f"Orijinal Süre: {plan.get('total_duration')}s")
            print(f"Temizlenmiş Süre: {plan.get('kept_duration')}s (-{plan.get('reduction_percentage')}%)")
            print(f"Temizlenen Asalak Sesler: {plan.get('fillers_detected')} adet")
            print(f"Budanan Sessizlikler: {plan.get('silences_trimmed')} adet")
            print(f"Toplam İşlem Süresi: {res.get('duration_sec')}s")
        elif res.get('dry_run'):
            plan = res.get('plan', {})
            print(f"Tespit Edilen Asalak Sesler: {plan.get('fillers_detected')} adet")
            print(f"Budanacak Süre: {plan.get('cut_duration')}s (-{plan.get('reduction_percentage')}%)")
        print("="*50)


if __name__ == "__main__":
    main()
