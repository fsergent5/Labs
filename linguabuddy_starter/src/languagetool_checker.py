"""
languagetool_checker.py

Spanish grammar checking using LanguageTool, used as the project's main
baseline (the "no-ML" reference point described in the initial plan).

Requires:
    pip install language-tool-python
    Java installed locally (LanguageTool runs a local server backed by Java)

NOTE: On first run, language_tool_python downloads the LanguageTool engine
(~200MB) from languagetool.org, so this needs an internet connection and
will not work in network-restricted sandboxes. Run this on your own machine.

Usage:
    python src/languagetool_checker.py
"""

from pathlib import Path

try:
    import language_tool_python
except ImportError as e:
    raise SystemExit(
        "language_tool_python is not installed. Run:\n"
        "    pip install language-tool-python\n"
        "and make sure Java is installed on your machine."
    ) from e


def check_sentence(tool, sentence: str):
    """Return LanguageTool's matches (detected issues) for one sentence."""
    return tool.check(sentence)


def main():
    data_path = Path(__file__).resolve().parent.parent / "data" / "sample_sentences.txt"

    print("Starting LanguageTool (Spanish)... this may take a moment on first run.")
    tool = language_tool_python.LanguageTool("es")

    with open(data_path, encoding="utf-8") as f:
        sentences = [line.strip() for line in f if line.strip()]

    total_issues = 0
    for sentence in sentences:
        matches = check_sentence(tool, sentence)
        print(f"\n- {sentence}")
        if not matches:
            print("    (no issues detected by LanguageTool)")
        for match in matches:
            total_issues += 1
            suggestion = match.replacements[0] if match.replacements else "(no suggestion)"
            print(f"    [{match.ruleId}] {match.message}")
            print(f"      Suggested fix: {suggestion}")

    print(f"\nTotal issues found across {len(sentences)} sentences: {total_issues}")
    tool.close()


if __name__ == "__main__":
    main()
