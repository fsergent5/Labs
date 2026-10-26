# LinguaBuddy

An LLM-based chatbot for practicing Spanish, with text-based grammatical
error detection and correction (GEC).

This is an early, work-in-progress scaffold: a minimal rule-based baseline
checker you can run right now with no setup, plus a LanguageTool-based
baseline to run once you have internet/Java available locally. The
ML/LLM-based correction model and the conversational chatbot layer are
planned next.

## Repository structure

```
linguabuddy/
├── data/
│   ├── sample_sentences.txt      # Spanish learner sentences with intentional errors
│   └── gold_corrections.txt      # Hand-corrected versions of the above, for evaluation
├── src/
│   ├── rule_based_checker.py     # Dependency-free regex baseline (works offline)
│   ├── languagetool_checker.py   # LanguageTool-based baseline (needs internet/Java)
│   └── evaluate.py               # Simple exact-match evaluator (placeholder for ERRANT)
├── tests/
│   └── test_rule_based_checker.py
├── requirements.txt
└── README.md
```

## Quick start

```bash
# No setup needed - runs immediately
python src/rule_based_checker.py

# Run the test suite
pip install -r requirements.txt
pytest tests/

# LanguageTool baseline (needs internet + Java; downloads ~200MB on first run)
python src/languagetool_checker.py

# Evaluation (currently a placeholder comparing uncorrected text to gold)
python src/evaluate.py
```

## Status

- [x] Repo scaffolded with sample data and a working rule-based baseline
- [ ] LanguageTool baseline results recorded on the full dataset
- [ ] Fine-tuned / prompted ML or LLM correction model
- [ ] Conversational chatbot layer
- [ ] Web demo (Flask/Streamlit)
- [ ] Final evaluation (Precision/Recall/F0.5 via ERRANT)

## Datasets planned for training/testing

- [COWS-L2H](https://github.com/ucdaviscl/cowsl2h) — Corpus Of Written Spanish, L2 and Heritage speakers
- Spanish subset of the Lang-8 Learner Corpus
- CEDEL2 — Corpus Escrito del Español L2

## License

TBD.
