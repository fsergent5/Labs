// Builds Lab5_SVM_Person_Name_Extraction_Report.docx (MLA 9 format).
// Run: node build_report.js   (from this folder)
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Header, AlignmentType, PageNumber,
  Table, TableRow, TableCell, WidthType, BorderStyle, PageBreak,
  LineRuleType,
} = require("docx");

const R = JSON.parse(fs.readFileSync("results.json", "utf8"));

const FONT = "Times New Roman";
const DOUBLE = { line: 480, lineRule: LineRuleType.AUTO, before: 0, after: 0 };
const SINGLE = { line: 240, lineRule: LineRuleType.AUTO, before: 0, after: 0 };

// --- helpers --------------------------------------------------------------
// Inline markup: *italic*  (used for titles of works, statistics, terms)
function runs(text, opts = {}) {
  return text.split(/(\*[^*]+\*)/).filter(Boolean).map((t) =>
    t.startsWith("*") && t.endsWith("*")
      ? new TextRun({ text: t.slice(1, -1), italics: true, ...opts })
      : new TextRun({ text: t, ...opts }));
}
const body = (text) => new Paragraph({
  spacing: DOUBLE, indent: { firstLine: 720 }, children: runs(text) });
const h1 = (text) => new Paragraph({
  spacing: DOUBLE, alignment: AlignmentType.CENTER,
  children: [new TextRun({ text, bold: true })] });
const h2 = (text) => new Paragraph({
  spacing: DOUBLE, keepNext: true, keepLines: true, children: [new TextRun({ text, bold: true })] });
const centered = (text, bold = false) => new Paragraph({
  spacing: DOUBLE, alignment: AlignmentType.CENTER,
  children: [new TextRun({ text, bold })] });
const blank = () => new Paragraph({ spacing: DOUBLE, children: [] });
const ref = (text) => new Paragraph({
  spacing: DOUBLE, indent: { left: 720, hanging: 720 }, children: runs(text) });

// Pseudocode: single-spaced monospace block (APA allows code to be single-spaced)
function code(lines) {
  return lines.map((l, i) => new Paragraph({
    spacing: { ...SINGLE, after: i === lines.length - 1 ? 240 : 0 },
    indent: { left: 360 },
    children: [new TextRun({ text: l.replace(/ /g, " "), font: "Courier New", size: 18 })],
  }));
}

const NB = { style: BorderStyle.NONE, size: 0, color: "FFFFFF" };
const noBorders = { top: NB, bottom: NB, left: NB, right: NB, insideHorizontal: NB, insideVertical: NB };

// Flowcharts drawn as monospaced text (see make_text_flowcharts.py)
function flowCell(file, width) {
  const lines = fs.readFileSync(file, "utf8").replace(/\n$/, "").split("\n");
  return new TableCell({
    width: { size: width, type: WidthType.DXA }, borders: noBorders,
    children: lines.map((l) => new Paragraph({ spacing: SINGLE, children: [
      new TextRun({ text: l.replace(/ /g, "\u00a0") || "\u00a0", font: "Courier New", size: 16 })] })),
  });
}
function captionCell(text, width) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA }, borders: noBorders,
    children: [new Paragraph({ spacing: { ...SINGLE, before: 120 }, children: [new TextRun({ text, size: 22 })] })],
  });
}

const COL = 4680;
const figures = new Table({
  width: { size: COL * 2, type: WidthType.DXA }, columnWidths: [COL, COL], borders: noBorders,
  rows: [
    new TableRow({ children: [flowCell("flowchart1.txt", COL), flowCell("flowchart2.txt", COL)] }),
    new TableRow({ children: [
      captionCell("Flowchart 1. Training the SVM person-name tagger on the CoNLL corpus.", COL),
      captionCell("Flowchart 2. Extracting person names from the first 10,000 BNC Baby sentences.", COL),
    ] }),
  ],
});
// --- content --------------------------------------------------------------
// MLA first-page heading (flush left, double spaced) instead of a title page
const left = (text) => new Paragraph({ spacing: DOUBLE, children: [new TextRun(text)] });
const titlePage = [
  left("Faith James"),
  left("Dr. Huang"),
  left("COSC 645"),
  left("2 November 2026"),
  centered("Person-Name Extraction with Support Vector Machines: Applying the CoNLL NER Corpus to the BNC Baby Corpus"),
];

const text = [
  body("Named entity recognition (NER) is the task of finding spans of text that name real-world things and labeling each span with a type such as person, location, or organization (Nadeau and Sekine). This report describes how a support vector machine (SVM) trained on *Conll_NER_corpus.txt* can identify person names in the first 10,000 sentences of the BNC Baby corpus, and reports results from a working implementation."),

  h2("Named Entities and the Training Data"),
  body(`*Conll_NER_corpus.txt* is derived from the Annotated Corpus for Named Entity Recognition on Kaggle (Walia) and follows the CoNLL column format (Tjong Kim Sang and De Meulder): one token per line, a tab, and the token's tag, with a blank line between sentences. The file holds 47,959 human-tagged sentences and ${R.train_tokens} tokens. Tags use the BIO scheme (Ramshaw and Marcus): *B-* marks the first word of an entity, *I-* marks a word inside it, and *O* marks a word outside any entity. Person names are tagged *B-per* (${R.b_per} tokens) and *I-per* (${R.i_per} tokens); in this corpus a title such as *President* or *Mr.* is part of the name, so “President Mahmoud Ahmadinejad” is tagged B-per I-per I-per. All other tags (geo, org, gpe, tim, art, eve, nat) are mapped to O, leaving three classes: B-PER, I-PER, and O.`),

  h2("Why an SVM"),
  body("An SVM finds the hyperplane that separates two classes with the largest margin (Cortes and Vapnik). Linear SVMs handle the very large, sparse feature vectors produced by text well and were a strong NER baseline before neural models (Isozaki and Kazawa). With three tags, one binary SVM is trained per tag (one-versus-rest) and each token receives the tag with the highest score. The implementation uses the LIBLINEAR solver (Fan et al.) through scikit-learn's *LinearSVC* (Pedregosa et al.), and NLTK's *BNCCorpusReader* to read the BNC XML files (Bird et al.)."),

  h2("Procedure"),
  body("The procedure has two phases, shown in Flowcharts 1 and 2. In training (Flowchart 1), every token becomes a feature dictionary describing the word itself (lowercased form, first and last three letters, capitalization, all-caps, digits, a trailing period as in *Mr.*), its shape (for example, *McCain* becomes *XxXx*), and the same information for the two words on each side, since context such as *said* or a preceding title signals a name. A vectorizer builds a sparse matrix, 10% of sentences are held out to measure precision and recall, and the final model is retrained on all sentences with balanced class weights, because O covers about 97% of tokens."),
  body("In extraction (Flowchart 2), the first 10,000 sentences (*<s>* units) of BNC Baby are read in file order, given the same features, and tagged; each B-PER and its following I-PER tokens form a candidate name. A regular expression keeps only spans that look like names (capitalized words, initials, hyphens, apostrophes, and inner particles such as *van* or *de*). Names are written with their sentence numbers, followed by a frequency list."),
];

const pseudocode = [
  h2("Pseudocode"),
  ...code([
    "PROCEDURE TrainPersonTagger(conllFile)",
    "    sentences ← ReadSentences(conllFile)          // split at blank lines",
    "    FOR each (word, tag) in sentences:",
    "        tag ← 'B-PER' if tag = 'B-per', 'I-PER' if tag = 'I-per', else 'O'",
    "    X, y ← [], []",
    "    FOR each sentence s, FOR i ← 0 TO |s|-1:",
    "        X.append(Features(s, i));  y.append(tag of s[i])",
    "    vectorizer ← DictVectorizer().fit(X)",
    "    (Xtr, ytr), (Xte, yte) ← Split(X, y, 90% / 10%)",
    "    svm ← LinearSVC(C = 0.1, class_weight = balanced).fit(Xtr, ytr)",
    "    Report precision, recall, F1 of svm on (Xte, yte)",
    "    RETURN LinearSVC(...).fit(X, y), vectorizer  // retrain on all data",
    "",
    "FUNCTION Features(s, i)",
    "    f ← {lower(s[i]), shape(s[i]), prefix3, suffix3, isTitle, isUpper,",
    "         isDigit, endsWithPeriod, isFirstWord}",
    "    FOR k IN {-2, -1, +1, +2}:",
    "        f ← f ∪ {lower(s[i+k]), shape(s[i+k]), isTitle(s[i+k])} or <pad>",
    "    RETURN f",
    "",
    "PROCEDURE ExtractPersons(svm, vectorizer, bncDir, N = 10000)",
    "    sents ← first N sentences of BNCCorpusReader(bncDir).sents()",
    "    results ← []",
    "    FOR k, s IN enumerate(sents):",
    "        tags ← svm.predict(vectorizer.transform(Features(s, i) for each i))",
    "        FOR span IN JoinSpans(s, tags):     // B-PER followed by I-PER*",
    "            IF Matches(NAME_REGEX, span): results.append((k, span))",
    "    Write results and name frequencies to person_names.txt",
  ]),
];

const results = [
  figures,
  new Paragraph({ spacing: { ...SINGLE, after: 120 }, children: [] }),
  h2("Results"),
  body(`On the 10% held-out split, token-level scores for B-PER were precision ${R.bp_p}, recall ${R.bp_r}, and *F*1 ${R.bp_f}; for I-PER they were ${R.ip_p}, ${R.ip_r}, and ${R.ip_f}. Applied to the first ${R.n_sents} BNC Baby sentences (${R.n_files} academic texts), the program extracted ${R.mentions} person-name mentions covering ${R.distinct} distinct names. The most frequent were ${R.top}. As the lab allows, these errors were not corrected.`),
];

const refs = [
  new Paragraph({ spacing: DOUBLE, alignment: AlignmentType.CENTER, pageBreakBefore: true,
    children: [new TextRun("Works Cited")] }),
  ref("Bird, Steven, et al. *Natural Language Processing with Python.* O'Reilly Media, 2009."),
  ref("BNC Consortium. *The BNC Baby.* 2nd ed., Oxford Text Archive, 2005, hdl.handle.net/20.500.12024/2553."),
  ref("Cortes, Corinna, and Vladimir Vapnik. \u201cSupport-Vector Networks.\u201d *Machine Learning*, vol. 20, no. 3, 1995, pp. 273\u201397, https://doi.org/10.1007/BF00994018."),
  ref("Fan, Rong-En, et al. \u201cLIBLINEAR: A Library for Large Linear Classification.\u201d *Journal of Machine Learning Research*, vol. 9, 2008, pp. 1871\u201374."),
  ref("Isozaki, Hideki, and Hideto Kazawa. \u201cEfficient Support Vector Classifiers for Named Entity Recognition.\u201d *Proceedings of the 19th International Conference on Computational Linguistics*, Association for Computational Linguistics, 2002, pp. 390\u201396, https://doi.org/10.3115/1072228.1072282."),
  ref("Nadeau, David, and Satoshi Sekine. \u201cA Survey of Named Entity Recognition and Classification.\u201d *Lingvisticae Investigationes*, vol. 30, no. 1, 2007, pp. 3\u201326, https://doi.org/10.1075/li.30.1.03nad."),
  ref("Pedregosa, Fabian, et al. \u201cScikit-learn: Machine Learning in Python.\u201d *Journal of Machine Learning Research*, vol. 12, 2011, pp. 2825\u201330."),
  ref("Ramshaw, Lance A., and Mitchell P. Marcus. \u201cText Chunking Using Transformation-Based Learning.\u201d *Proceedings of the Third Workshop on Very Large Corpora*, Association for Computational Linguistics, 1995, pp. 82\u201394."),
  ref("Tjong Kim Sang, Erik F., and Fien De Meulder. \u201cIntroduction to the CoNLL-2003 Shared Task: Language-Independent Named Entity Recognition.\u201d *Proceedings of the Seventh Conference on Natural Language Learning at HLT-NAACL 2003*, Association for Computational Linguistics, 2003, pp. 142\u201347."),
  ref("Walia, Abhinav. \u201cAnnotated Corpus for Named Entity Recognition.\u201d *Kaggle*, www.kaggle.com/abhinavwalia95/entity-annotated-corpus. Accessed 1 Nov. 2026."),
];

const doc = new Document({
  creator: "Faith James",
  title: "Person-Name Extraction with Support Vector Machines",
  styles: { default: { document: { run: { font: FONT, size: 24 } } } },
  sections: [{
    properties: { page: {
      size: { width: 12240, height: 15840 },
      margin: { top: 1440, bottom: 1440, left: 1440, right: 1440, header: 720 },
    } },
    headers: { default: new Header({ children: [new Paragraph({
      alignment: AlignmentType.RIGHT, children: [new TextRun({ children: ["James ", PageNumber.CURRENT] })] })] }) },
    children: [...titlePage, ...text, ...pseudocode, ...results, ...refs],
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("Lab5_SVM_Person_Name_Extraction_Report.docx", buf);
  console.log("written");
});
