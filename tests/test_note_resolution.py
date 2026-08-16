"""Tests for note-name alias resolution, including the Danish H/B
swap - the single most important thing to get right in this skill,
same class of trap as the false-friend units in ovos-skill-convert."""
import pytest


def test_resolve_note_en_us_exact_match(skill):
    assert skill._resolve_note("a", "en-us") == "a"
    assert skill._resolve_note("f sharp", "en-us") == "f#"


def test_resolve_note_no_fuzzy_match(skill):
    """A near-miss note name should not silently resolve to a
    DIFFERENT note - same reasoning as every other alias resolver in
    this project family."""
    assert skill._resolve_note("ay", "en-us") is None
    assert skill._resolve_note("cee", "en-us") is None


def test_resolve_note_unknown_returns_none(skill):
    assert skill._resolve_note("purple", "en-us") is None


def test_danish_h_resolves_to_b_natural_not_bb(skill):
    """The critical Danish/German convention swap: 'H' in Danish means
    English 'B' (natural), NOT English 'H' (which doesn't exist) and
    NOT a Danish spelling of 'B-flat'."""
    assert skill._resolve_note("h", "da-dk") == "b"


def test_danish_b_resolves_to_b_flat_not_b_natural(skill):
    """The other half of the same swap: Danish 'B' means English
    'Bb' (flat), NOT English 'B' (natural) - getting this backwards
    would be a real wrong-note bug, not just a translation nicety."""
    assert skill._resolve_note("b", "da-dk") == "bb"


def test_danish_h_and_b_produce_different_frequencies():
    """End-to-end: the two Danish notes must produce genuinely
    different, correct frequencies - this is the test that would have
    caught the swap being backwards."""
    from tuningfork_skill import note_to_frequency
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location(
        "tuningfork_check", Path(__file__).resolve().parents[1] / "__init__.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)

    h_freq = m.note_to_frequency(m.NOTE_ALIASES["da-dk"]["h"])
    b_freq = m.note_to_frequency(m.NOTE_ALIASES["da-dk"]["b"])
    assert round(h_freq, 2) == 493.88  # B natural
    assert round(b_freq, 2) == 466.16  # B flat
    assert h_freq != b_freq
