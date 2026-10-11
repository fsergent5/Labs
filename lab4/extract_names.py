#!/usr/bin/env python3
"""Lab 4 - heuristic person-name extractor (Naive Bayes over simple features).

Usage: python3 extract_names.py <bnc_sentences.txt> [surnames.txt] [given_names.txt]
Reads the first 10,000 lines (sentences) of the corpus and writes
extracted_names.txt (one 'sentence_no<TAB>name' per line).
"""
import re, sys, math

CORPUS = sys.argv[1] if len(sys.argv) > 1 else "bnc_baby_sentences.txt"
SUR    = sys.argv[2] if len(sys.argv) > 2 else "surnames.txt"
GIV    = sys.argv[3] if len(sys.argv) > 3 else "given_names.txt"
N_SENT = 10000

# ---- name lists (case-insensitive) ----
surnames = set()
with open(SUR, encoding="utf-8", errors="ignore") as f:
    for line in f:
        w = line.strip().lower()
        if w.isalpha():            # skips the census header lines
            surnames.add(w)
given = set()
with open(GIV, encoding="utf-8", errors="ignore") as f:
    for line in f:
        w = line.strip().lower()
        if w.isalpha():
            given.add(w)

# Common English words that also occur in the name lists (will, may, the, ...)
COMMON = set("""the a an and or but if then so of in on at to for from by with without about as
is are was were be been being am do does did have has had will would shall should may might can could must
i you he she it we they me him her us them my your his its our their this that these those there here
who whom whose which what when where why how not no yes all any some each every both few more most other
such only own same than too very just also now once again still even ever never always often well
mr mrs ms miss dr sir lady lord mister madam monday tuesday wednesday thursday friday saturday sunday
january february march april june july august september october november december
english british london england britain european europe american america french german
north south east west new old good great little big long high first last next""".split())
TITLES = {"mr","mrs","ms","miss","dr","sir","lady","lord","mister","madam","prof","professor","rev","captain","colonel","mrs.","mr.","dr.","ms."}
DAYS_MONTHS = {"monday","tuesday","wednesday","thursday","friday","saturday","sunday","january","february",
               "march","april","june","july","august","september","october","november","december"}

# ---- Naive Bayes: P(feature | Name) and P(feature | NotName), hand-set heuristics ----
PRIOR_NAME = 0.05
LIK = {  # feature: (P(f|Name), P(f|Not))
    "in_given":      (0.80, 0.03),
    "in_surname":    (0.85, 0.10),
    "in_neither":    (0.05, 0.85),   # complements: fires when in neither list
    "common_word":   (0.10, 0.60),
    "title_before":  (0.30, 0.01),
    "cap_neighbor":  (0.55, 0.08),   # adjacent capitalised token (Firstname Surname)
    "sent_initial":  (0.15, 0.30),   # capitalised anyway -> less evidence
    "mid_sentence":  (0.85, 0.35),   # capitalised mid-sentence -> evidence
}

def posterior(feats):
    lp_n, lp_o = math.log(PRIOR_NAME), math.log(1 - PRIOR_NAME)
    for f in feats:
        pn, po = LIK[f]
        lp_n += math.log(pn); lp_o += math.log(po)
    m = max(lp_n, lp_o)
    a, b = math.exp(lp_n - m), math.exp(lp_o - m)
    return a / (a + b)

TOKEN = re.compile(r"[A-Za-z][A-Za-z'\-\.]*|[^\sA-Za-z]")
def tokenize(s):
    return [t.rstrip(".") if t.rstrip(".") and t.lower() not in TITLES else t for t in TOKEN.findall(s)]

def is_cap(t):
    return len(t) > 1 and t[0].isupper() and not t.isupper() or (len(t) > 1 and t.isupper() and False)

def score_tokens(toks):
    scores = []
    for i, t in enumerate(toks):
        if not (t[:1].isalpha() and t[0].isupper() and len(t) > 1 and not t.isupper()):
            scores.append(0.0); continue
        base = re.sub(r"[^a-z]", "", t.lower().replace("'s", ""))
        if base in COMMON or base in DAYS_MONTHS:   # hard stoplist: function words, days, months, places
            scores.append(0.0); continue
        feats = []
        g, s = base in given, base in surnames
        if g: feats.append("in_given")
        if s: feats.append("in_surname")
        if not (g or s): feats.append("in_neither")
        if base in COMMON or base in DAYS_MONTHS: feats.append("common_word")
        prev = toks[i-1].lower() if i else ""
        nxt  = toks[i+1] if i + 1 < len(toks) else ""
        pv   = toks[i-1] if i else ""
        if prev in TITLES: feats.append("title_before")
        if (nxt[:1].isupper() and len(nxt) > 1) or (pv[:1].isupper() and len(pv) > 1 and i > 0):
            feats.append("cap_neighbor")
        feats.append("sent_initial" if i == 0 else "mid_sentence")
        scores.append(posterior(feats))
    return scores

THRESH = 0.5
def extract(sentence):
    toks = tokenize(sentence)
    sc = score_tokens(toks)
    names, i = [], 0
    while i < len(toks):
        if sc[i] >= THRESH:
            j = i
            while j + 1 < len(toks) and sc[j + 1] >= THRESH:
                j += 1
            # attach a preceding title (e.g. "Mr Smith")
            start = i - 1 if i and toks[i-1].lower() in TITLES else i
            names.append(" ".join(toks[start:j+1]))
            i = j + 1
        else:
            i += 1
    return names

if __name__ == "__main__":
    out, count = [], 0
    with open(CORPUS, encoding="utf-8", errors="ignore") as f:
        for n, line in enumerate(f, 1):
            if n > N_SENT: break
            for nm in extract(line.strip()):
                out.append(f"{n}\t{nm}"); count += 1
    with open("extracted_names.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print(f"Processed {min(n, N_SENT)} sentences, extracted {count} names -> extracted_names.txt")
