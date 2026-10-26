"""
Basic tests for the rule-based checker.

Run with:
    pytest tests/
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from rule_based_checker import check_sentence  # noqa: E402


def test_detects_ser_for_temporary_state():
    issues = check_sentence("Yo soy cansado después de trabajar todo el día.")
    assert any(i.rule_name == "ser_for_temporary_state" for i in issues)


def test_detects_edad_sin_plural():
    issues = check_sentence("Ella tiene veinte año.")
    assert any(i.rule_name == "edad_sin_plural" for i in issues)


def test_no_false_positive_on_correct_sentence():
    issues = check_sentence("Yo estoy cansado después de trabajar todo el día.")
    assert not any(i.rule_name == "ser_for_temporary_state" for i in issues)


def test_detects_mucha_gente_agreement():
    issues = check_sentence("Hay muchas gente en la fiesta.")
    assert any(i.rule_name == "mucha_gente_agreement" for i in issues)
