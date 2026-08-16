"""
skill OVOS Tuning Fork
Copyright (C) 2026  Andreas Lorensen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

---

A reference-tone generator - "give me an A" plays a clean 440Hz sine
tone, "play 300 hertz" plays an arbitrary frequency. Fully offline,
fully deterministic: every tone is a generated sine wave (equal-
temperament, A4 = 440Hz standard concert pitch), nothing recorded,
nothing to source or license.

WHY NOT A START/STOP LOOP LIKE THE METRONOME OR RHYTHM BOX
--------------------------------------------------------------
Unlike ovos-skill-metronome and ovos-skill-rhythm-box, this skill does
NOT run a background thread with an explicit "stop" intent. There is
no reliable way to interrupt an already-playing sound via the standard
OVOSSkill API - play_audio() has no counterpart to
"mycroft.audio.speech.stop" (that only stops TTS speech, not sounds
played via play_sound/queue). Rather than build a "stop" intent that
can't actually stop anything, each tone is generated with a FIXED
duration (TONE_DURATION_SECONDS) and left to end on its own - the same
way striking a real tuning fork produces a tone that rings and then
naturally fades, not one you interrupt mid-ring.

WHY NO LISTEN-AND-IDENTIFY FEATURE
---------------------------------------
A natural-sounding extension would be "listen to what I'm playing and
tell me the pitch" - useful for an actual instrument tuner (guitar,
bass, ukulele: listen to a plucked string, say whether it's sharp or
flat). Deliberately NOT built here, for a real technical reason, not
just a scope preference: a standard OVOSSkill has no access to raw
microphone audio for analysis - the only "listening" primitive
available (get_response()) goes through the full STT pipeline and
returns TRANSCRIBED TEXT, not a waveform. Real pitch detection would
need a dedicated PHAL plugin or audio-transformer tapping the raw
audio stream, plus an actual pitch-detection algorithm (e.g. YIN or
autocorrelation) - a different technical domain (audio analysis)
from what this skill does (audio synthesis), and arguably a different
product entirely (an instrument tuner, not a reference-tone
generator). Left as a possible separate future skill, not a feature
of this one.

ONLY NAMED NOTES, ONLY OCTAVE 4 - NO OCTAVE SELECTION YET
---------------------------------------------------------------
"give me an A" always means A4 (440Hz, standard concert pitch) - there
is no "give me an A in octave 2" yet. This is a deliberate v0.0.x
scope limit, not an oversight: octave-in-speech parsing ("A two" vs
"A 2" vs a number word) adds real ambiguity that wasn't worth solving
before the basic note-name lookup was working. For a specific
frequency regardless of note name, use "play {N} hertz" instead.
"""

import json
import math
import struct
import tempfile
import wave
from pathlib import Path

from ovos_workshop.skills import OVOSSkill
from ovos_workshop.decorators import intent_handler
from ovos_number_parser import extract_number

A4_FREQUENCY = 440.0
A4_MIDI = 69
SAMPLE_RATE = 44100
TONE_DURATION_SECONDS = 4
FADE_IN_MS = 10
FADE_OUT_MS = 100

MIN_FREQUENCY = 20
MAX_FREQUENCY = 5000

CACHE_DIR = Path(tempfile.gettempdir()) / "ovos-skill-tuning-fork"

# semitone offset from A, WITHIN THE SAME (scientific-pitch-notation)
# octave number - i.e. C4 is 9 semitones BELOW A4, not "in octave 3"
NOTE_SEMITONES = {
    "c": -9, "c#": -8, "db": -8,
    "d": -7, "d#": -6, "eb": -6,
    "e": -5,
    "f": -4, "f#": -3, "gb": -3,
    "g": -2, "g#": -1, "ab": -1,
    "a": 0, "a#": 1, "bb": 1,
    "b": 2,
}


def note_to_frequency(note_name, octave=4):
    """Equal-temperament frequency for a named note in a given octave,
    A4 = 440Hz standard concert pitch. See NOTE_SEMITONES for the
    octave-numbering convention (increments at C, matching scientific
    pitch notation - so C4 is below A4, not the octave 'above' it)."""
    semitone = NOTE_SEMITONES[note_name.lower()]
    midi = A4_MIDI + semitone + (octave - 4) * 12
    return A4_FREQUENCY * (2 ** ((midi - A4_MIDI) / 12))


def _generate_tone_wav(path, freq, duration_s=TONE_DURATION_SECONDS,
                        sample_rate=SAMPLE_RATE):
    n = int(sample_rate * duration_s)
    fade_in_n = int(sample_rate * FADE_IN_MS / 1000)
    fade_out_n = int(sample_rate * FADE_OUT_MS / 1000)
    with wave.open(str(path), "w") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        frames = []
        for i in range(n):
            t = i / sample_rate
            amp = 0.6
            if i < fade_in_n:
                amp *= i / fade_in_n
            elif i > n - fade_out_n:
                amp *= (n - i) / fade_out_n
            sample = amp * math.sin(2 * math.pi * freq * t)
            frames.append(struct.pack("<h", int(sample * 32767)))
        f.writeframes(b"".join(frames))


def _tone_path_for_frequency(freq):
    """Generated tones are cached by frequency (rounded to 2 decimal
    places) under a temp dir, so repeat requests for the same note
    don't regenerate identical audio."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"tone_{freq:.2f}.wav"
    if not path.exists():
        _generate_tone_wav(path, freq)
    return str(path)


SKILL_ROOT = Path(__file__).resolve().parent
LOCALE_DIR = SKILL_ROOT / "locale"


def _load_note_aliases_from_disk():
    """locale/<lang>/note_aliases.json - {spoken form: canonical note
    key in NOTE_SEMITONES}. Same JSON-in-locale convention as
    ovos-skill-convert/ovos-skill-sound-like/ovos-skill-rhythm-box."""
    merged = {}
    if not LOCALE_DIR.is_dir():
        return merged
    for lang_dir in sorted(LOCALE_DIR.iterdir()):
        if not lang_dir.is_dir():
            continue
        alias_file = lang_dir / "note_aliases.json"
        if not alias_file.exists():
            continue
        with open(alias_file, encoding="utf-8") as f:
            aliases = json.load(f)
        lang = lang_dir.name.lower()
        merged[lang] = {k: v for k, v in aliases.items() if not k.startswith("_")}
    return merged


NOTE_ALIASES = _load_note_aliases_from_disk()


class TuningFork(OVOSSkill):

    def _note_aliases_for(self, lang):
        lang = lang.lower()
        return NOTE_ALIASES.get(lang) or NOTE_ALIASES.get("en-us", {})

    def _resolve_note(self, raw, lang):
        """Exact match only, no fuzzy matching - same reasoning as
        every other alias resolver in this project family: a wrong
        note is a much more noticeable wrong answer than a slightly
        mis-parsed number would be."""
        if not raw:
            return None
        return self._note_aliases_for(lang).get(raw.strip().lower())

    @intent_handler("give_note.intent")
    def handle_give_note(self, message):
        note_raw = (message.data.get("note") or "").strip()
        note_key = self._resolve_note(note_raw, self.lang)
        if note_key is None:
            self.speak_dialog("note_not_understood", {"note": note_raw})
            return
        freq = note_to_frequency(note_key)
        self.speak_dialog("playing_note", {"note": note_raw})
        self.play_audio(_tone_path_for_frequency(freq), instant=True)

    @intent_handler("play_frequency.intent")
    def handle_play_frequency(self, message):
        freq_raw = message.data.get("frequency")
        freq = extract_number(freq_raw, lang=self.lang) if freq_raw else None
        if freq is False or freq is None:
            self.speak_dialog("frequency_not_understood")
            return
        freq = float(freq)
        if not (MIN_FREQUENCY <= freq <= MAX_FREQUENCY):
            self.speak_dialog("frequency_out_of_range",
                               {"min": MIN_FREQUENCY, "max": MAX_FREQUENCY})
            return
        self.play_audio(_tone_path_for_frequency(freq), instant=True)
