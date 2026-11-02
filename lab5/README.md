# Lab 5 — SVM person-name extraction (follow-up of Lab 3)

| File | What it is |
|---|---|
| `report/Lab5_SVM_Person_Name_Extraction_Report.docx` (+ `.pdf`) | APA 7 report (6 pages): procedure, flowcharts, pseudocode, references |
| `svm_person_ner.py` | Extra credit: trains a linear SVM on `Conll_NER_corpus.txt` and tags person names in the first 10,000 BNC Baby sentences |
| `person_names.txt` | Program output: held-out scores, distinct names with counts, every mention with its sentence number |
| `report/make_flowcharts.py`, `report/build_report.js`, `report/results.json` | Scripts that regenerate the figures and the .docx |

## Running

```bash
pip install scikit-learn nltk
python svm_person_ner.py --conll Conll_NER_corpus.txt \
    --bnc /path/to/BNC_Baby/download/Texts --out person_names.txt
```

The BNC Baby files (OTA resource 2553) are not included because of their licence.
New NLTK versions refuse corpus files that other users can write to; run
`chmod -R go-w /path/to/BNC_Baby` if you see that error. The run takes about 3 minutes.
