# Development

## Setup
```bash
git clone https://github.com/andlo/ovos-skill-tuning-fork.git
cd ovos-skill-tuning-fork
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
pip install -r requirements-test.txt
```

## Running tests
```bash
pytest tests/ -v
```
`tests/test_frequencies.py` is pure math (no mocking) - checks the
equal-temperament formula against known reference values (A4=440,
middle C≈261.63, etc). `tests/test_note_resolution.py` covers alias
resolution including the Danish H/B swap specifically -
`test_danish_h_and_b_produce_different_frequencies` is the test that
would catch that swap being backwards, not just present. `tests/test_intents.py`
covers the actual intent handlers, including that repeat requests for
the same note reuse the cached WAV file rather than regenerating it.

## Adding octave selection

Not implemented yet (see README). If picking this up:
1. `note_to_frequency()` already accepts an `octave` parameter -
   the gap is entirely on the speech-parsing side, not the math.
2. The hard part is exactly HOW someone would say an octave number in
   a voice command ("give me a C two" vs "give me a C in octave two")
   without colliding with digit-parsing edge cases `extract_number()`
   might mishandle for a bare trailing digit. Worth sketching a few
   candidate utterance patterns and checking them against
   `ovos-number-parser`'s actual behavior before committing to a
   grammar.

## Adding listen-and-identify pitch detection

Explicitly out of scope for this skill - see README's "Why no listen-
and-identify pitch feature" for the real technical reason (no raw
mic-audio access from a standard OVOSSkill). If this is ever built,
it's very likely a new, separate skill (an instrument tuner) rather
than a feature added here - would need at minimum:
- A PHAL plugin or audio-transformer with access to the raw
  microphone stream (not currently something this project has any
  existing pattern for - would be new territory).
- A real pitch-detection algorithm (YIN, autocorrelation, or similar).
- A genuinely different UX: sustained listening + directional
  feedback ("sharp"/"flat"), not a one-shot request/response.

## Versioning

`version.py` follows `VERSION_MAJOR.VERSION_MINOR.VERSION_BUILD[aVERSION_ALPHA]`.
Stays on **0.0.x** until the Danish sharp/flat spelling has been
reviewed by an actual Danish speaker/musician (see
`locale/da-dk/note_aliases.json`'s `_notes`) and octave selection (or
a deliberate decision not to add it) is settled.

## Releasing

Releases are tag-triggered (`v*`):
```bash
git add version.py
git commit -m "chore: bump version to 0.0.X"
git tag vX.Y.Z
git push && git push --tags
```
Triggers `.github/workflows/test.yml` then `.github/workflows/publish.yml`
(PyPI via trusted publishing - see `ovos-skill-convert`'s
DEVELOPMENT.md for the one-time PyPI setup needed before the first
tagged release).

## Style / conventions

- License: GPL-3.0-or-later (matches the other `andlo` skill repos).
- `locale/<lang-code>/` layout, `skill.json` inside each locale folder.
- Alias JSON in locale (`note_aliases.json`) - same JSON-in-locale
  convention as `ovos-skill-convert`, `ovos-skill-sound-like`, and
  `ovos-skill-rhythm-box`.
- Present design changes for review before implementing - especially
  anything touching the Danish note names, given the H/B trap already
  found once.
