# <img src='icon.png' card_color='#40DB7A' width='50' height='50' style='vertical-align:bottom'/> Tuning Fork

A reference-tone generator for OVOS - "give me an A" plays a clean
440Hz sine tone, "play 300 hertz" plays an arbitrary frequency. Fully
offline, fully deterministic: every tone is generated (equal-
temperament, A4 = 440Hz standard concert pitch), nothing recorded,
nothing to source or license.

[![Tests](https://github.com/andlo/ovos-skill-tuning-fork/actions/workflows/test.yml/badge.svg)](https://github.com/andlo/ovos-skill-tuning-fork/actions/workflows/test.yml)
[![PyPI version](https://img.shields.io/pypi/v/ovos-skill-tuning-fork.svg)](https://pypi.org/project/ovos-skill-tuning-fork/)

> **Early 0.0.x release.** Named notes always play octave 4 - no
> octave selection yet. See "Not yet implemented" below.

## Usage
```
"give me an A"
"play a C sharp"
"play 300 hertz"
"giv mig et A"          (Danish)
"spil et H"             (Danish - see "The Danish H/B swap" below)
```

Each tone rings for 4 seconds (short fade-in/out to avoid clicks) and
stops on its own - see "Why no stop intent" below.

## The Danish H/B swap - a real trap, not a translation nicety

Danish (like German) uses a different note-naming convention than
English for one specific note:

| Danish | English | Frequency (octave 4) |
|---|---|---|
| **H** | B (natural) | 493.88 Hz |
| **B** | B♭ (flat) | 466.16 Hz |

Saying "H" in Danish means the natural B - **not** a flat, and
**not** "the letter after G" the way English speakers might assume.
Saying "B" in Danish means B-flat. This is the actual Danish/German
musical convention, the same shape of false-friend trap as the unit-
conversion ones in `ovos-skill-convert` (Danish "ton" vs the English
"ton", etc) - getting it backwards would produce a confidently wrong
note, not just an awkward translation. See
`tests/test_note_resolution.py` for the regression tests that would
catch this being backwards.

The exact spelling of sharp/flat suffixes (ciss vs cis, ess vs es) is
lower-confidence - see `locale/da-dk/note_aliases.json`'s `_notes` key
for what's hedged and why.

## Why no "stop" intent

Unlike [ovos-skill-metronome](https://github.com/andlo/ovos-skill-metronome)
and [ovos-skill-rhythm-box](https://github.com/andlo/ovos-skill-rhythm-box),
there's no background thread or stop intent here. `play_audio()` has
no reliable "stop this sound" counterpart in the standard OVOSSkill
API (only `mycroft.audio.speech.stop`, which stops TTS speech, not
sounds). Rather than build a stop intent that can't actually stop
anything, each tone just has a fixed, short duration and ends on its
own - the same way a real tuning fork rings out rather than being
interrupted.

## Why no "listen and identify the pitch" feature

A natural-feeling extension: strike an instrument, have the skill
listen and say whether it's sharp or flat. Deliberately not built -
not a scope preference, a real technical blocker: a standard
OVOSSkill has no access to raw microphone audio for analysis. The
only "listening" primitive (`get_response()`) goes through the full
STT pipeline and returns *transcribed text*, not a waveform. Real
pitch detection would need a dedicated PHAL plugin or audio-
transformer tapping the raw audio stream, plus an actual pitch-
detection algorithm - a different technical domain (audio analysis)
from this skill (audio synthesis), and arguably a different product
(an instrument tuner) from this one (a reference-tone generator).
Left as a possible future skill, not a feature of this one.

## Not yet implemented

- **Octave selection.** "give me an A" is always A4 (440Hz). Octave-
  in-speech parsing ("A two" vs "A 2") adds real ambiguity that
  wasn't worth solving before the basic note lookup worked - use
  "play {N} hertz" for a specific frequency in the meantime.
- **Listen-and-identify pitch** - see above, likely a separate future
  skill rather than an extension of this one.

## Install
```bash
pip install ovos-skill-tuning-fork
```

## Development

See [DEVELOPMENT.md](DEVELOPMENT.md).

## Category
**Utility**

## Tags
#music #tuning #reference-tone #instrument
