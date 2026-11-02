import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon

L, R = 0.8, 8.6   # box left/right
C = (L+R)/2
def draw(steps, path):
    n = len(steps)
    fig, ax = plt.subplots(figsize=(5.2, 0.62*n + 0.3))
    ax.set_xlim(0, 10.5); ax.set_ylim(0, n); ax.axis("off")
    ys = [n - i - 0.5 for i in range(n)]
    for i, step in enumerate(steps):
        kind, text = step[0], step[1]
        y = ys[i]
        if kind == "term":
            p = FancyBboxPatch((L+1.5, y-0.28), R-L-3, 0.56, boxstyle="round,pad=0,rounding_size=0.28", fc="#e6e6e6", ec="black", lw=1)
        elif kind == "data":
            p = Polygon([(L+0.3, y-0.3), (R+0.3, y-0.3), (R-0.3, y+0.3), (L-0.3, y+0.3)], closed=True, fc="white", ec="black", lw=1)
        elif kind == "dec":
            p = Polygon([(C, y+0.4), (R, y), (C, y-0.4), (L, y)], closed=True, fc="white", ec="black", lw=1)
        else:
            p = FancyBboxPatch((L, y-0.3), R-L, 0.6, boxstyle="square,pad=0", fc="white", ec="black", lw=1)
        ax.add_patch(p)
        ax.text(C, y, text, ha="center", va="center", fontsize=6.8, family="serif")
        if i < n-1:
            top = y-0.4 if kind == "dec" else y-0.3
            ax.annotate("", xy=(C, ys[i+1]+(0.4 if steps[i+1][0]=="dec" else 0.3)), xytext=(C, top),
                        arrowprops=dict(arrowstyle="-|>", lw=0.9, color="black"))
            if kind == "dec":
                ax.text(C+0.15, y-0.52, step[4] if len(step)>4 else "Yes", fontsize=6.5, family="serif", va="center")
        if kind == "dec":
            tgt, label = step[2], step[3]
            ty = ys[tgt]
            ax.plot([R, 10.3], [y, y], color="black", lw=0.9)
            ax.plot([10.3, 10.3], [y, ty], color="black", lw=0.9)
            ax.annotate("", xy=(R + (0.0 if steps[tgt][0]=="proc" else 0.3), ty), xytext=(10.3, ty),
                        arrowprops=dict(arrowstyle="-|>", lw=0.9, color="black"))
            ax.text(R+0.1, y+0.06, label, fontsize=6.0, family="serif", va="bottom", ha="left", bbox=dict(fc="white", ec="none", pad=0.5))
    fig.savefig(path, dpi=220, bbox_inches="tight")

draw([
 ("term", "Start"),
 ("data", "Read Conll_NER_corpus.txt (word TAB tag)"),
 ("proc", "Split into 47,959 sentences at blank lines"),
 ("proc", "Map tags: B-per → B-PER, I-per → I-PER, all others → O"),
 ("proc", "Build features per token (word, shape, affixes,\ncapitalisation, words at positions ±1 and ±2)"),
 ("proc", "DictVectorizer → sparse feature matrix X; labels y"),
 ("proc", "Hold out 10% of sentences; train LinearSVC on 90%"),
 ("dec",  "Held-out precision\nand recall acceptable?", 4, "No: revise\nfeatures"),
 ("proc", "Retrain LinearSVC on all 47,959 sentences"),
 ("data", "Trained SVM model + fitted vectorizer"),
 ("term", "End"),
], "/home/user/Labs/lab5/report/fig1_training.png")

draw([
 ("term", "Start"),
 ("data", "Trained SVM model + fitted vectorizer"),
 ("data", "Read BNC Baby XML with NLTK BNCCorpusReader"),
 ("proc", "Keep the first 10,000 sentences (<s> units)"),
 ("proc", "Take next sentence; build the same token features"),
 ("proc", "SVM predicts B-PER / I-PER / O for every token"),
 ("proc", "Join each B-PER with the I-PER tokens after it"),
 ("dec",  "Span matches the\nname regex?", 4, "No: discard"),
 ("proc", "Record (sentence number, name); update counts"),
 ("dec",  "More sentences\nleft?", 4, "Yes: loop", "No"),
 ("data", "Write person_names.txt"),
 ("term", "End"),
], "/home/user/Labs/lab5/report/fig2_extraction.png")
