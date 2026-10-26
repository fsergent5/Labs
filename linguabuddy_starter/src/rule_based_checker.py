"""
rule_based_checker.py

A minimal, dependency-free rule-based baseline for detecting a handful of
common Spanish learner grammar errors. This is intentionally simple -- it's
meant as a quick, no-setup-required baseline to compare against the
LanguageTool baseline and the ML/LLM-based approach later in the project.

Each rule is a (name, regex pattern, message, fix_hint) tuple. The checker
scans a sentence and reports every rule that matches.

Run directly to check the sample sentences in data/sample_sentences.txt:
    python src/rule_based_checker.py
"""

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Issue:
    rule_name: str
    message: str
    fix_hint: str


# Each rule: (name, compiled regex, message, fix_hint)
# These target specific, well-known learner error patterns and are not
# meant to be a complete grammar checker.
RULES = [
    (
        "ser_for_temporary_state",
        re.compile(r"\b(soy|eres|es|somos|sois|son)\s+cansad[oa]s?\b", re.IGNORECASE),
        "Use of 'ser' with a temporary physical/emotional state.",
        "Use 'estar' instead (e.g., 'estoy cansado', not 'soy cansado').",
    ),
    (
        "ser_for_location",
        re.compile(r"\b(soy|eres|es|somos|sois|son)\s+en\s+la\b", re.IGNORECASE),
        "Use of 'ser' to express location.",
        "Use 'estar' for location (e.g., 'está en la cocina', not 'es en la cocina').",
    ),
    (
        "gender_agreement_grande_bonito",
        re.compile(r"\bgrande\s+y\s+bonito\b", re.IGNORECASE),
        "Possible gender agreement mismatch with a feminine noun earlier in the sentence.",
        "Check agreement: 'la casa ... bonita' (feminine), not 'bonito'.",
    ),
    (
        "plural_article_singular_noun",
        re.compile(r"\b(los|las)\s+(niño|niña|flore|hombre|mujere)\b", re.IGNORECASE),
        "Plural article with a noun that looks singular/misspelled plural.",
        "Match number: 'los niños', 'las flores', etc.",
    ),
    (
        "edad_sin_plural",
        re.compile(r"\b(veinte|treinta|cuarenta|cincuenta|\d{2,})\s+año\b(?!s)", re.IGNORECASE),
        "'año' should usually be plural after a number other than one.",
        "Use 'años' (e.g., 'tiene veinte años').",
    ),
    (
        "ser_plural_agreement",
        re.compile(r"\b(el|la)\s+\w+\s+son\b", re.IGNORECASE),
        "Singular subject (el/la + noun) used with plural verb 'son'.",
        "Match number: 'El problema es difícil', not 'El problema son difícil'.",
    ),
    (
        "desde_duration_missing_hace",
        re.compile(r"\bdesde\s+(dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez)\s+años?\b", re.IGNORECASE),
        "'desde' + a duration is a common learner slip; Spanish usually uses 'desde hace' for elapsed time.",
        "Use 'desde hace dos años' (not 'desde dos años') to express duration.",
    ),
    (
        "ningun_gender_mismatch",
        re.compile(r"\bningún\s+idea\b", re.IGNORECASE),
        "'ningún' (masculine) used with a feminine noun.",
        "Use 'ninguna idea' (feminine agreement).",
    ),
    (
        "mucha_gente_agreement",
        re.compile(r"\bmuchas\s+gente\b", re.IGNORECASE),
        "'gente' is singular and feminine; 'muchas' (plural) does not agree.",
        "Use 'mucha gente' (singular feminine agreement).",
    ),
    (
        "es_muy_bonitas_plural_subject",
        re.compile(r"\bes\s+muy\s+bonitas\b", re.IGNORECASE),
        "Singular verb 'es' used with what looks like a plural subject.",
        "Match number: 'son muy bonitas' if the subject is plural.",
    ),
]


def check_sentence(sentence: str) -> list[Issue]:
    """Return a list of Issue objects for every rule that matches the sentence."""
    issues = []
    for name, pattern, message, fix_hint in RULES:
        if pattern.search(sentence):
            issues.append(Issue(rule_name=name, message=message, fix_hint=fix_hint))
    return issues


def check_file(path: str) -> dict:
    """Check every line in a text file and return a dict of sentence -> issues."""
    results = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            sentence = line.strip()
            if not sentence:
                continue
            results[sentence] = check_sentence(sentence)
    return results


def main():
    data_path = Path(__file__).resolve().parent.parent / "data" / "sample_sentences.txt"
    results = check_file(str(data_path))

    total_sentences = len(results)
    flagged = sum(1 for issues in results.values() if issues)

    print(f"Checked {total_sentences} sentences, flagged {flagged} with at least one issue.\n")

    for sentence, issues in results.items():
        print(f"- {sentence}")
        if not issues:
            print("    (no issues detected by rule-based baseline)")
        for issue in issues:
            print(f"    [{issue.rule_name}] {issue.message}")
            print(f"      Fix: {issue.fix_hint}")
        print()


if __name__ == "__main__":
    main()
