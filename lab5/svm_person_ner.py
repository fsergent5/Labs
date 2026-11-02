"""
Lab 5 (Extra Credit): Person-name extraction with a Support Vector Machine.

Trains a linear SVM token classifier on Conll_NER_corpus.txt (word<TAB>tag)
and uses it to find person names in the first 10,000 sentences of the
BNC Baby corpus.

Labels: the corpus tags are collapsed to three classes
    B-PER  (first word of a person name)       <- B-per
    I-PER  (word inside a person name)         <- I-per
    O      (everything else, incl. geo/org/...)

Usage:
    python svm_person_ner.py --conll Conll_NER_corpus.txt \
        --bnc /path/to/BNC_Baby/download/Texts --out person_names.txt
"""
import argparse
import os
import re
import time
from collections import Counter

from nltk.corpus.reader.bnc import BNCCorpusReader
from sklearn.feature_extraction import DictVectorizer
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC

# A candidate name must look like a name: capitalised words, optionally with
# initials ("J."), apostrophes or hyphens ("O'Neill", "Lloyd-George") and a
# few lowercase particles ("van", "de", "bin") between capitalised words.
NAME_RE = re.compile(
    r"^[A-Z][\w'.\-]*"
    r"(?:\s+(?:(?:van|von|de|da|del|der|du|bin|al|la|le)\s+)*[A-Z][\w'.\-]*)*$"
)
HAS_LETTER = re.compile(r"[A-Za-z]")


# --------------------------------------------------------------------------
# 1. Load the annotated corpus
# --------------------------------------------------------------------------
def load_conll(path):
    """Return a list of sentences; each sentence is a list of (word, tag)."""
    sentences, current = [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if not line.strip():
                if current:
                    sentences.append(current)
                    current = []
                continue
            if "\t" not in line:          # header / comment line
                continue
            word, tag = line.split("\t", 1)
            current.append((word, map_tag(tag.strip())))
    if current:
        sentences.append(current)
    return sentences


def map_tag(tag):
    if tag == "B-per":
        return "B-PER"
    if tag == "I-per":
        return "I-PER"
    return "O"


# --------------------------------------------------------------------------
# 2. Feature extraction (one feature dictionary per token)
# --------------------------------------------------------------------------
def shape(word):
    """Collapse a word into its orthographic shape, e.g. 'McCain' -> 'XxXx'."""
    s = re.sub("[A-Z]", "X", word)
    s = re.sub("[a-z]", "x", s)
    s = re.sub("[0-9]", "d", s)
    return re.sub(r"(.)\1+", r"\1", s)


def token_features(words, i):
    w = words[i]
    feats = {
        "bias": 1.0,
        "w.lower=" + w.lower(): 1.0,
        "w.shape=" + shape(w): 1.0,
        "w.suffix3=" + w[-3:].lower(): 1.0,
        "w.prefix3=" + w[:3].lower(): 1.0,
        "w.istitle": float(w.istitle()),
        "w.isupper": float(w.isupper()),
        "w.isdigit": float(w.isdigit()),
        "w.first_in_sentence": float(i == 0),
        "w.ends_with_period": float(w.endswith(".")),
    }
    for offset in (-2, -1, 1, 2):
        j = i + offset
        if 0 <= j < len(words):
            c = words[j]
            feats[f"{offset}:w.lower=" + c.lower()] = 1.0
            feats[f"{offset}:w.shape=" + shape(c)] = 1.0
            feats[f"{offset}:w.istitle"] = float(c.istitle())
        else:
            feats[f"{offset}:<pad>"] = 1.0
    return feats


def sentence_features(words):
    return [token_features(words, i) for i in range(len(words))]


# --------------------------------------------------------------------------
# 3. Decode B/I/O predictions into name strings
# --------------------------------------------------------------------------
def decode_names(words, tags):
    names, span = [], []
    for w, t in zip(words, tags):
        if t == "B-PER" or (t == "I-PER" and not span):
            if span:
                names.append(span)
            span = [w]
        elif t == "I-PER":
            span.append(w)
        else:
            if span:
                names.append(span)
            span = []
    if span:
        names.append(span)
    out = []
    for span in names:
        name = " ".join(span)
        if HAS_LETTER.search(name) and NAME_RE.match(name):
            out.append(name)
    return out


def as_int32(X):
    """LinearSVC (liblinear) requires 32-bit sparse indices."""
    X = X.tocsr()
    X.indices = X.indices.astype("int32")
    X.indptr = X.indptr.astype("int32")
    return X


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--conll", required=True)
    ap.add_argument("--bnc", required=True, help="BNC Baby 'Texts' directory")
    ap.add_argument("--out", default="person_names.txt")
    ap.add_argument("--n-sents", type=int, default=10000)
    ap.add_argument("--C", type=float, default=0.1)
    args = ap.parse_args()

    t0 = time.time()
    data = load_conll(args.conll)
    print(f"Loaded {len(data)} annotated sentences")

    # ---- evaluation on a 10% held-out split -----------------------------
    train, test = train_test_split(data, test_size=0.1, random_state=42)
    vec = DictVectorizer()
    X_tr = vec.fit_transform(f for s in train for f in sentence_features([w for w, _ in s]))
    y_tr = [t for s in train for _, t in s]
    X_te = vec.transform(f for s in test for f in sentence_features([w for w, _ in s]))
    y_te = [t for s in test for _, t in s]
    svm = LinearSVC(C=args.C, class_weight="balanced", max_iter=5000)
    svm.fit(as_int32(X_tr), y_tr)
    report = classification_report(y_te, svm.predict(as_int32(X_te)), digits=3)
    print("Held-out evaluation (token level):\n" + report)

    # ---- final model on all 47,959 sentences ---------------------------
    vec = DictVectorizer()
    X = vec.fit_transform(f for s in data for f in sentence_features([w for w, _ in s]))
    y = [t for s in data for _, t in s]
    svm = LinearSVC(C=args.C, class_weight="balanced", max_iter=5000)
    svm.fit(as_int32(X), y)
    print(f"Trained final SVM on {X.shape[0]} tokens x {X.shape[1]} features")

    # ---- apply to the first N sentences of BNC Baby --------------------
    # Newer NLTK versions only read corpora under NLTK_DATA roots.
    bnc_root = os.path.abspath(args.bnc)
    os.environ["NLTK_DATA"] = os.pathsep.join(
        p for p in (bnc_root, os.environ.get("NLTK_DATA", "")) if p)
    bnc = BNCCorpusReader(root=bnc_root, fileids=r"[a-z]{3,4}/\w*\.xml")
    sents = []
    for fid in bnc.fileids():
        for s in bnc.sents(fid):
            sents.append(s)
            if len(sents) >= args.n_sents:
                break
        if len(sents) >= args.n_sents:
            break
    print(f"Read {len(sents)} BNC Baby sentences")

    found = []  # (sentence_no, name)
    for k, words in enumerate(sents, start=1):
        if not words:
            continue
        tags = svm.predict(vec.transform(sentence_features(words)))
        for name in decode_names(words, tags):
            found.append((k, name))

    counts = Counter(n for _, n in found)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write("# Person names extracted by a linear SVM from the first "
                f"{len(sents)} sentences of BNC Baby\n")
        f.write(f"# Training data: Conll_NER_corpus.txt ({len(data)} sentences)\n")
        f.write(f"# Mentions found: {len(found)}; distinct names: {len(counts)}\n\n")
        f.write("## Held-out token-level evaluation (10% of training corpus)\n")
        f.write(report + "\n")
        f.write("## Distinct names (frequency, name)\n")
        for name, c in counts.most_common():
            f.write(f"{c}\t{name}\n")
        f.write("\n## Every mention (sentence number, name)\n")
        for k, name in found:
            f.write(f"{k}\t{name}\n")
    print(f"{len(found)} mentions, {len(counts)} distinct names -> {args.out}")
    print(f"Done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
