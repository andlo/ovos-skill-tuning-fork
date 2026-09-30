"""OCP: "play a C sharp" / "play 300 hertz" is taken by the OCP pipeline
before padatious, so the skill answers OCP's search (#3)."""
import pytest
from ovos_utils.ocp import MediaType, PlaybackType

import tuningfork_skill as tf


@pytest.fixture(autouse=True)
def _no_entity_autoregister(monkeypatch, tmp_path):
    monkeypatch.setattr(tf.TuningFork, "_auto_register_entity_files",
                        lambda *a, **k: None, raising=False)
    monkeypatch.setattr(tf, "CACHE_DIR", tmp_path)


@pytest.mark.parametrize("phrase,freq", [
    ("a c sharp", 277.18),
    ("a concert a", 440.0),
    ("an e", 329.63),
    ("300 hertz", 300.0),
    ("a 440 hertz tone", 440.0),
])
def test_search_answers_notes_and_frequencies(skill, phrase, freq):
    [r] = skill.search_tone(phrase, MediaType.MUSIC)
    assert r.uri.startswith("file://") and r.uri.endswith(f"tone_{freq:.2f}.wav")
    assert r.match_confidence == 100 and r.playback == PlaybackType.AUDIO
    assert r.media_type == MediaType.MUSIC


@pytest.mark.parametrize("phrase", [
    "a day in the life",
    "c sharp by some band",
    "9000 hertz",          # out of range
    "radio 100 hertz fm",
    "",
])
def test_search_ignores_other_phrases(skill, phrase):
    assert skill.search_tone(phrase, MediaType.MUSIC) == []


def test_search_danish(skill, monkeypatch):
    monkeypatch.setattr(tf.TuningFork, "lang", "da-dk", raising=False)
    [r] = skill.search_tone("et cis", MediaType.AUDIO)
    assert r.uri.endswith("tone_277.18.wav")
