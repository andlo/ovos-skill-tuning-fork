"""Tests for the intent handlers - tone generation is real (writes an
actual WAV file to the cache dir), play_audio() is mocked."""
from pathlib import Path
from unittest.mock import MagicMock

import pytest


def test_give_note_plays_generated_tone(skill):
    skill.play_audio = MagicMock()
    skill.speak_dialog = MagicMock()
    message = MagicMock()
    message.data = {"note": "a"}
    skill.handle_give_note(message)
    skill.speak_dialog.assert_called_once_with("playing_note", {"note": "a"})
    skill.play_audio.assert_called_once()
    played_path = skill.play_audio.call_args[0][0]
    assert Path(played_path).exists()
    assert "440.00" in played_path


def test_give_note_unknown_note(skill):
    skill.play_audio = MagicMock()
    skill.speak_dialog = MagicMock()
    message = MagicMock()
    message.data = {"note": "purple"}
    skill.handle_give_note(message)
    skill.speak_dialog.assert_called_once_with("note_not_understood", {"note": "purple"})
    skill.play_audio.assert_not_called()


def test_play_frequency_valid(skill):
    skill.play_audio = MagicMock()
    skill.speak_dialog = MagicMock()
    message = MagicMock()
    message.data = {"frequency": "300"}
    skill.handle_play_frequency(message)
    skill.play_audio.assert_called_once()
    played_path = skill.play_audio.call_args[0][0]
    assert "300.00" in played_path
    skill.speak_dialog.assert_not_called()  # no confirmation for raw frequency, just plays


def test_play_frequency_out_of_range(skill):
    skill.play_audio = MagicMock()
    skill.speak_dialog = MagicMock()
    message = MagicMock()
    message.data = {"frequency": "50000"}
    skill.handle_play_frequency(message)
    skill.play_audio.assert_not_called()
    skill.speak_dialog.assert_called_once_with(
        "frequency_out_of_range", {"min": 20, "max": 5000})


def test_play_frequency_unparseable(skill):
    skill.play_audio = MagicMock()
    skill.speak_dialog = MagicMock()
    message = MagicMock()
    message.data = {"frequency": "banana"}
    skill.handle_play_frequency(message)
    skill.play_audio.assert_not_called()
    skill.speak_dialog.assert_called_once_with("frequency_not_understood")


def test_repeat_request_reuses_cached_tone_file(skill):
    """Same frequency requested twice should reuse the same cached
    WAV file, not regenerate it - confirms the caching actually
    works, not just that it doesn't crash."""
    skill.play_audio = MagicMock()
    skill.speak_dialog = MagicMock()
    message = MagicMock()
    message.data = {"note": "c"}
    skill.handle_give_note(message)
    first_path = skill.play_audio.call_args[0][0]
    first_mtime = Path(first_path).stat().st_mtime

    skill.handle_give_note(message)
    second_path = skill.play_audio.call_args[0][0]
    second_mtime = Path(second_path).stat().st_mtime

    assert first_path == second_path
    assert first_mtime == second_mtime  # file wasn't rewritten
