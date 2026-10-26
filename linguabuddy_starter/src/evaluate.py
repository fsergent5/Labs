"""
evaluate.py

A simplified evaluator for comparing a grammar-correction system's output
against gold-standard corrections. This is NOT a replacement for a proper
GEC scorer -- for the final project, look into ERRANT
(https://github.com/chrisjbryant/errant), which is the standard tool for
scoring grammatical error correction with Precision/Recall/F0.5 at the
edit level. This script gives a quick, dependency-free sanity check in
the meantime by comparing whole corrected sentences.

Usage:
    python src/evaluate.py
"""

from pathlib import Path


def load_lines(path: str) -> list[str]:
    with open(path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def exact_match_accuracy(system_outputs: list[str], gold_outputs: list[str]) -> float:
    """Fraction of sentences where the system's output exactly matches gold."""
    assert len(system_outputs) == len(gold_outputs), "Mismatched number of lines"
    correct = sum(1 for sys, gold in zip(system_outputs, gold_outputs) if sys.strip() == gold.strip())
    return correct / len(gold_outputs)


def main():
    base = Path(__file__).resolve().parent.parent / "data"
    originals = load_lines(str(base / "sample_sentences.txt"))
    gold = load_lines(str(base / "gold_corrections.txt"))

    # Placeholder: here the "system output" is just the uncorrected original,
    # i.e., a system that does nothing. Replace `system_outputs` with the
    # actual output of your rule-based / LanguageTool / ML / LLM system
    # once you have it producing corrected sentences.
    system_outputs = originals  # <-- replace with your system's corrected sentences

    accuracy = exact_match_accuracy(system_outputs, gold)
    print(f"Exact-match accuracy (system vs. gold): {accuracy:.2%}")
    print("\nNote: this is a placeholder baseline (no correction applied).")
    print("Swap `system_outputs` for your actual system's corrected sentences,")
    print("and consider using ERRANT for proper edit-level Precision/Recall/F0.5.")


if __name__ == "__main__":
    main()
