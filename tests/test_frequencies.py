"""Tests for the equal-temperament frequency calculation - no mocking
needed, this is pure math."""
import pytest


def test_a4_is_exactly_440():
    from tuningfork_skill import note_to_frequency
    assert note_to_frequency("a") == 440.0


def test_middle_c_is_correct():
    from tuningfork_skill import note_to_frequency
    assert round(note_to_frequency("c"), 2) == 261.63


def test_b_natural_is_correct():
    from tuningfork_skill import note_to_frequency
    assert round(note_to_frequency("b"), 2) == 493.88


def test_octave_up_doubles_frequency():
    from tuningfork_skill import note_to_frequency
    a4 = note_to_frequency("a", octave=4)
    a5 = note_to_frequency("a", octave=5)
    assert round(a5 / a4, 4) == 2.0


def test_sharp_and_flat_enharmonic_equivalents_match():
    from tuningfork_skill import note_to_frequency
    assert round(note_to_frequency("c#"), 4) == round(note_to_frequency("db"), 4)
    assert round(note_to_frequency("a#"), 4) == round(note_to_frequency("bb"), 4)
