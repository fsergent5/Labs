"""Draws the two Lab 5 flowcharts as compact monospaced text.

Shapes (one line each):  ( Start )  terminal     / ... /  input/output
                         [ ... ]    process      < ... >  decision
A decision's side branch leaves on the right and loops back up to the
step it points to.  Writes flowchart1.txt and flowchart2.txt.
"""
import os

W = 38          # width of every shape
MID = W // 2    # column of the vertical arrows
RAIL = W + 6    # column of the loop-back line


def shape(kind, text):
    if kind == "term":
        s = "( " + text + " )"
        return s.center(W)
    inner = text.center(W - 4)
    left, right = {"data": ("/ ", " /"), "dec": ("< ", " >"), "proc": ("[ ", " ]")}[kind]
    return left + inner + right


def draw(steps):
    """steps: (kind, text) or ("dec", text, target_index, side_label, down_label)."""
    rows, at = [], []
    for i, st in enumerate(steps):
        at.append(len(rows))
        rows.append(list(shape(st[0], st[1]).ljust(RAIL + 1)))
        if i < len(steps) - 1:
            down = st[4] if st[0] == "dec" else ""
            rows.append(list((" " * MID + "v" + (" " + down if down else "")).ljust(RAIL + 1)))

    for i, st in enumerate(steps):
        if st[0] != "dec":
            continue
        top, bot, label = at[st[2]], at[i], st[3]
        # arrow back into the target step
        for c in range(W, RAIL):
            rows[top][c] = "-"
        rows[top][W] = "<"
        rows[top][RAIL] = "+"
        for r in range(top + 1, bot):
            if rows[r][RAIL] == " ":
                rows[r][RAIL] = "|"
        # branch leaving the decision
        branch = ("-" + label + "-" * RAIL)[: RAIL - W]
        for k, ch in enumerate(branch):
            rows[bot][W + k] = ch
        rows[bot][RAIL] = "+" if rows[bot][RAIL] == " " else "+"
    return ["".join(r).rstrip() for r in rows]


F1 = [
    ("term", "Start"),
    ("data", "Read Conll_NER_corpus.txt"),
    ("proc", "Split into 47,959 sentences"),
    ("proc", "Map tags to B-PER, I-PER, O"),
    ("proc", "Build features for every token"),
    ("proc", "Vectorize features into X, y"),
    ("proc", "Train LinearSVC on 90%"),
    ("proc", "Score precision/recall on 10%"),
    ("dec", "Scores acceptable?", 4, "No", "Yes"),
    ("proc", "Retrain LinearSVC on all data"),
    ("data", "Trained SVM + vectorizer"),
    ("term", "End"),
]
F2 = [
    ("term", "Start"),
    ("data", "Trained SVM + vectorizer"),
    ("data", "Read BNC Baby XML files"),
    ("proc", "Keep first 10,000 sentences"),
    ("proc", "Take next sentence; build features"),
    ("proc", "SVM tags tokens B-PER/I-PER/O"),
    ("proc", "Join B-PER + I-PER tokens = span"),
    ("dec", "Span matches name regex?", 4, "No", "Yes"),
    ("proc", "Record (sentence no., name)"),
    ("dec", "More sentences left?", 4, "Yes", "No"),
    ("data", "Write person_names.txt"),
    ("term", "End"),
]

if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    for name, steps in (("flowchart1.txt", F1), ("flowchart2.txt", F2)):
        text = "\n".join(draw(steps)) + "\n"
        with open(os.path.join(here, name), "w", encoding="utf-8") as f:
            f.write(text)
        print(text)
