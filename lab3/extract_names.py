"""
Lab 3 - Person Name Extraction

Heuristically extracts person names from the first 10,000 sentences of the
BNC baby corpus (sents_BNCbaby.txt). Each line of the dataset has the
format:

    SentenceNumber<TAB>EnglishSentence

where the sentence has already been word-tokenized (punctuation may appear
as separate tokens).

Heuristics used (this is intentionally simple/regex-based - false
positives such as "Pembridge Investments" and false negatives are
expected and not corrected for, per the assignment):

  1. Title + name: a title (Mr, Mrs, Ms, Miss, Dr, Sir, Lord, Lady, Prof)
     followed by 1-3 capitalized words is treated as a person name, e.g.
     "Mr Franklin" -> "Franklin".
  2. Capitalized runs: two or more consecutive Title-Case words (e.g.
     "Roland Franklin") or ALL-CAPS words (e.g. "FRANK KANE", common in
     newspaper bylines) are treated as a person name.

Matches that are wholly contained in a longer match from the same
sentence (e.g. "Franklin" inside "Mr Franklin") are dropped to reduce
redundant output.
"""

import re
import sys

NUM_SENTENCES = 10000
INPUT_FILE = 'sents_BNCbaby.txt'
OUTPUT_FILE = 'person_names_output.txt'

TITLES = r'(?:Mr|Mrs|Ms|Miss|Dr|Sir|Lord|Lady|Prof)'

TITLE_NAME_RE = re.compile(
    rf"\b{TITLES}\.?\s+((?:[A-Z][a-zA-Z'-]*\s+){{0,2}}[A-Z][a-zA-Z'-]*)"
)
TITLECASE_RUN_RE = re.compile(r"\b(?:[A-Z][a-z]+\s+){1,}[A-Z][a-z]+\b")
ALLCAPS_RUN_RE = re.compile(r"\b(?:[A-Z]{2,}\s+){1,}[A-Z]{2,}\b")


def extract_names(sentence):
    """Return the deduplicated list of candidate person names in a sentence."""
    candidates = (
        TITLE_NAME_RE.findall(sentence)
        + TITLECASE_RUN_RE.findall(sentence)
        + ALLCAPS_RUN_RE.findall(sentence)
    )

    # Drop names that are wholly contained in a longer candidate name
    # (e.g. "Franklin" when "Mr Franklin" was also matched).
    names = []
    for name in sorted(set(candidates), key=len, reverse=True):
        if not any(name != kept and name in kept for kept in names):
            names.append(name)
    return names


def main():
    input_path = sys.argv[1] if len(sys.argv) > 1 else INPUT_FILE

    with open(input_path, encoding='utf-8') as f, \
         open(OUTPUT_FILE, 'w', encoding='utf-8') as out:
        for i, line in enumerate(f):
            if i >= NUM_SENTENCES:
                break
            line = line.rstrip('\n')
            if not line:
                continue
            sent_num, _, sentence = line.partition('\t')
            for name in extract_names(sentence):
                out.write(f"{sent_num}\t{name}\n")

    print(f"Done. Extracted names for the first {NUM_SENTENCES} sentences "
          f"written to {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
