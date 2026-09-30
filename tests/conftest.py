"""Shared pytest fixtures for the tuning-fork skill test suite."""
import importlib.util
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_INIT_PATH = Path(__file__).resolve().parents[1] / "__init__.py"
_spec = importlib.util.spec_from_file_location("tuningfork_skill", _INIT_PATH)
_module = importlib.util.module_from_spec(_spec)
sys.modules["tuningfork_skill"] = _module
_spec.loader.exec_module(_module)

TuningFork = _module.TuningFork


@pytest.fixture
def skill(monkeypatch):
    s = TuningFork.__new__(TuningFork)
    s.log = MagicMock()
    s.skill_id = "ovos-skill-tuning-fork.test"
    s.status = MagicMock()
    s._bus = MagicMock()
    monkeypatch.setattr(TuningFork, "lang", "en-us", raising=False)
    s.res_dir = str(Path(__file__).resolve().parents[1])
    s._lang_resources = {}
    s._voc_cache = {}
    s.skill_icon = ""
    return s
