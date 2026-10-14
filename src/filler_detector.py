#!/usr/bin/env python3
"""
Turkish & Multilingual Audio Filler Word & Silence Detector.
Uses Faster-Whisper with word-level timestamps to detect disfluencies
("ııı", "eee", "şey", "yani", "ımm", "hmm" etc.) and awkward dead air pauses.
"""

import os
import sys
import re
import string
import logging
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field, asdict

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] [%(levelname)s] [FILLER-DETECT] %(message)s")
logger = logging.getLogger("filler_detector")

# Core Turkish & English filler sound sets
DEFAULT_FILLER_SOUNDS: Set[str] = {
    # Turkish phonetic fillers
    "ııı", "ıı", "ı", "ııh", "ıh", "eee", "ee", "e", "eh", "ımm", "imm",
    "hmm", "hım", "aam", "ööh", "öhm", "öff",
    # English phonetic fillers
    "um", "uh", "er", "ah", "erm", "mm", "hmm"
}

DEFAULT_CONVERSATIONAL_FILLERS: Set[str] = {
    # Turkish conversational crutch words (often spoken redundantly)
    "şey", "yani", "falan", "filan", "hani", "işte",
    # English conversational fillers
    "like", "basically", "literally"
}


@dataclass
class WordToken:
    word: str
    clean_word: str
    start: float
    end: float
    probability: float
    is_filler: bool = False
    filler_type: Optional[str] = None


@dataclass
class AudioCut:
    start: float
    end: float
    duration: float
    reason: str
    text: Optional[str] = None


@dataclass
class KeepSegment:
    start: float
    end: float
    duration: float


@dataclass
class DetectionPlan:
    total_duration: float
    kept_duration: float
    cut_duration: float
    reduction_percentage: float
    words_total: int
    fillers_detected: int
    silences_trimmed: int
    cuts: List[AudioCut] = field(default_factory=list)
    keep_segments: List[KeepSegment] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_duration": round(self.total_duration, 3),
            "kept_duration": round(self.kept_duration, 3),
            "cut_duration": round(self.cut_duration, 3),
            "reduction_percentage": round(self.reduction_percentage, 2),
            "words_total": self.words_total,
            "fillers_detected": self.fillers_detected,
            "silences_trimmed": self.silences_trimmed,
            "cuts": [asdict(c) for c in self.cuts],
            "keep_segments": [asdict(k) for k in self.keep_segments]
        }


class FillerDetector:
    """
    Detects vocal fillers and dead air in audio files.
    """

    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
        include_conversational: bool = True,
        custom_fillers: Optional[List[str]] = None,
        max_pause_sec: float = 0.5,
        pause_retention_sec: float = 0.2,
        min_cut_duration: float = 0.08
    ):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.max_pause_sec = max_pause_sec
        self.pause_retention_sec = pause_retention_sec
        self.min_cut_duration = min_cut_duration
        self._model = None

        # Build active filler word set
        self.active_fillers = set(DEFAULT_FILLER_SOUNDS)
        if include_conversational:
            self.active_fillers.update(DEFAULT_CONVERSATIONAL_FILLERS)
        if custom_fillers:
            for cf in custom_fillers:
                self.active_fillers.add(self._clean_text(cf))

    def _get_model(self):
        if self._model is None:
            from faster_whisper import WhisperModel
            logger.info(f"Loading Faster-Whisper '{self.model_size}' ({self.compute_type} on {self.device})...")
            self._model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
        return self._model

    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Turkish-aware lowercase and punctuation stripping.
        """
        # Turkish uppercase I -> ı and İ -> i
        cleaned = text.replace("I", "ı").replace("İ", "i").lower()
        cleaned = re.sub(r'[^\w\s]', '', cleaned).strip()
        return cleaned

    def transcribe_with_words(self, audio_path: str, language: str = "tr") -> Tuple[List[WordToken], float]:
        """
        Transcribes audio and extracts word-level timestamps.
        """
        model = self._get_model()
        logger.info(f"Analyzing audio: {audio_path} (language: {language})...")

        segments, info = model.transcribe(
            audio_path,
            language=language,
            word_timestamps=True,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=250)
        )

        all_words: List[WordToken] = []
        for segment in segments:
            if not segment.words:
                continue
            for w in segment.words:
                cleaned = self._clean_text(w.word)
                if not cleaned:
                    continue

                is_filler = cleaned in self.active_fillers
                filler_type = "sound" if cleaned in DEFAULT_FILLER_SOUNDS else ("conversational" if is_filler else None)

                all_words.append(WordToken(
                    word=w.word,
                    clean_word=cleaned,
                    start=round(w.start, 3),
                    end=round(w.end, 3),
                    probability=round(w.probability, 3),
                    is_filler=is_filler,
                    filler_type=filler_type
                ))

        total_duration = round(info.duration, 3)
        return all_words, total_duration

    def plan_cuts(self, words: List[WordToken], total_duration: float) -> DetectionPlan:
        """
        Generates cut intervals for filler words and excessive pauses,
        and derives the kept audio intervals.
        """
        raw_cuts: List[AudioCut] = []
        fillers_count = 0
        silence_count = 0

        # 1. Identify filler word cuts
        for i, token in enumerate(words):
            if token.is_filler:
                fillers_count += 1
                raw_cuts.append(AudioCut(
                    start=token.start,
                    end=token.end,
                    duration=round(token.end - token.start, 3),
                    reason=f"filler ({token.clean_word})",
                    text=token.word
                ))

        # 2. Identify excessive pauses between kept words
        # Filter kept words (non-fillers)
        kept_words = [w for w in words if not w.is_filler]

        if kept_words:
            # Check leading silence before first word
            if kept_words[0].start > self.max_pause_sec:
                cut_end = kept_words[0].start - self.pause_retention_sec
                if cut_end > 0.05:
                    raw_cuts.append(AudioCut(
                        start=0.0,
                        end=round(cut_end, 3),
                        duration=round(cut_end, 3),
                        reason="leading silence"
                    ))
                    silence_count += 1

            # Check pauses between consecutive words
            for i in range(len(kept_words) - 1):
                curr_end = kept_words[i].end
                next_start = kept_words[i + 1].start
                gap = next_start - curr_end

                if gap > self.max_pause_sec:
                    # Keep pause_retention_sec in the middle for natural breath
                    cut_start = curr_end + (self.pause_retention_sec / 2)
                    cut_end = next_start - (self.pause_retention_sec / 2)
                    cut_dur = cut_end - cut_start

                    if cut_dur >= self.min_cut_duration:
                        raw_cuts.append(AudioCut(
                            start=round(cut_start, 3),
                            end=round(cut_end, 3),
                            duration=round(cut_dur, 3),
                            reason="awkward pause"
                        ))
                        silence_count += 1

            # Check trailing silence after last word
            last_end = kept_words[-1].end
            if (total_duration - last_end) > self.max_pause_sec:
                cut_start = last_end + self.pause_retention_sec
                if cut_start < total_duration:
                    raw_cuts.append(AudioCut(
                        start=round(cut_start, 3),
                        end=round(total_duration, 3),
                        duration=round(total_duration - cut_start, 3),
                        reason="trailing silence"
                    ))
                    silence_count += 1

        # 3. Sort and merge overlapping or adjacent cuts
        raw_cuts.sort(key=lambda c: c.start)
        merged_cuts: List[AudioCut] = []
        for c in raw_cuts:
            if not merged_cuts:
                merged_cuts.append(c)
                continue
            last = merged_cuts[-1]
            if c.start <= last.end + 0.05:  # within 50ms, merge
                merged_end = max(last.end, c.end)
                merged_cuts[-1] = AudioCut(
                    start=last.start,
                    end=round(merged_end, 3),
                    duration=round(merged_end - last.start, 3),
                    reason=f"{last.reason} + {c.reason}",
                    text=(f"{last.text or ''} {c.text or ''}").strip() or None
                )
            else:
                merged_cuts.append(c)

        # 4. Invert cuts to compute kept segments
        kept_segments: List[KeepSegment] = []
        curr_pos = 0.0

        for cut in merged_cuts:
            if cut.start > curr_pos + self.min_cut_duration:
                kept_segments.append(KeepSegment(
                    start=round(curr_pos, 3),
                    end=round(cut.start, 3),
                    duration=round(cut.start - curr_pos, 3)
                ))
            curr_pos = max(curr_pos, cut.end)

        if curr_pos < total_duration - self.min_cut_duration:
            kept_segments.append(KeepSegment(
                start=round(curr_pos, 3),
                end=round(total_duration, 3),
                duration=round(total_duration - curr_pos, 3)
            ))

        total_cut_duration = sum(c.duration for c in merged_cuts)
        total_kept_duration = sum(k.duration for k in kept_segments)
        reduction_pct = (total_cut_duration / total_duration * 100.0) if total_duration > 0 else 0.0

        return DetectionPlan(
            total_duration=total_duration,
            kept_duration=total_kept_duration,
            cut_duration=total_cut_duration,
            reduction_percentage=reduction_pct,
            words_total=len(words),
            fillers_detected=fillers_count,
            silences_trimmed=silence_count,
            cuts=merged_cuts,
            keep_segments=kept_segments
        )


if __name__ == "__main__":
    print("=== Testing Filler Detector Core Logic ===")
    detector = FillerDetector()

    # Synthetic mock tokens to verify cut and keep logic without requiring audio run
    mock_tokens = [
        WordToken("Merhaba", "merhaba", 0.5, 1.0, 0.95),
        WordToken("arkadaşlar", "arkadaşlar", 1.1, 1.7, 0.95),
        WordToken("ııı", "ııı", 2.0, 2.7, 0.88, is_filler=True, filler_type="sound"),
        WordToken("bugün", "bugün", 4.0, 4.4, 0.96),  # 1.3s pause before 'bugün'
        WordToken("sizlerle", "sizlerle", 4.5, 5.0, 0.98),
        WordToken("şey", "şey", 5.2, 5.6, 0.91, is_filler=True, filler_type="conversational"),
        WordToken("Godot", "godot", 5.7, 6.2, 0.95),
        WordToken("öğreneceğiz.", "öğreneceğiz", 6.3, 7.0, 0.95),
    ]

    plan = detector.plan_cuts(mock_tokens, total_duration=8.5)
    print(f"Total Duration: {plan.total_duration}s")
    print(f"Kept Duration: {plan.kept_duration}s (Cut: {plan.cut_duration}s, -{plan.reduction_percentage:.1f}%)")
    print(f"Fillers Detected: {plan.fillers_detected}, Silences Trimmed: {plan.silences_trimmed}")
    print("\nCuts to make:")
    for c in plan.cuts:
        print(f"  - [{c.start:.2f}s -> {c.end:.2f}s] ({c.duration:.2f}s) Reason: {c.reason}")
    print("\nSegments to keep:")
    for k in plan.keep_segments:
        print(f"  - [{k.start:.2f}s -> {k.end:.2f}s] ({k.duration:.2f}s)")

    assert plan.fillers_detected >= 2, "Failed to identify synthetic fillers"
    print("\n✅ Filler Detector test passed successfully!")
