// Builds Lab5_SVM_Person_Name_Extraction_Report.docx (APA 7 student paper).
// Run: node build_report.js   (from this folder)
const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Header, AlignmentType, PageNumber,
  ImageRun, Table, TableRow, TableCell, WidthType, BorderStyle, PageBreak,
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
  spacing: DOUBLE, children: [new TextRun({ text, bold: true })] });
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

function figureCell(path, w, h, width) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA }, borders: noBorders,
    children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [
      new ImageRun({ type: "png", data: fs.readFileSync(path), transformation: { width: w, height: h } }),
    ] })],
  });
}
function captionCell(label, title, width) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA }, borders: noBorders,
    children: [
      new Paragraph({ spacing: SINGLE, children: [new TextRun({ text: label, bold: true, size: 22 })] }),
      new Paragraph({ spacing: { ...SINGLE, after: 120 }, children: [new TextRun({ text: title, italics: true, size: 22 })] }),
    ],
  });
}
// image sizes in px (docx-js uses 96 dpi); keep aspect ratio of the PNGs
const { imageSize } = (() => {
  function imageSize(path) {
    const b = fs.readFileSync(path);
    return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
  }
  return { imageSize };
})();
function scaled(path, targetW) {
  const s = imageSize(path);
  return [targetW, Math.round(targetW * s.h / s.w)];
}

const f1 = "fig1_training.png", f2 = "fig2_extraction.png";
const [w1, hh1] = scaled(f1, 290), [w2, hh2] = scaled(f2, 290);
const COL = 4680;
const figures = new Table({
  width: { size: COL * 2, type: WidthType.DXA }, columnWidths: [COL, COL], borders: noBorders,
  rows: [
    new TableRow({ children: [
      captionCell("Figure 1", "Training the SVM Person-Name Tagger on the CoNLL Corpus", COL),
      captionCell("Figure 2", "Extracting Person Names From the First 10,000 BNC Baby Sentences", COL),
    ] }),
    new TableRow({ children: [figureCell(f1, w1, hh1, COL), figureCell(f2, w2, hh2, COL)] }),
  ],
});

// --- content --------------------------------------------------------------
const titlePage = [
  blank(), blank(), blank(),
  centered("Person-Name Extraction With Support Vector Machines:", true),
  centered("Applying the CoNLL NER Corpus to the BNC Baby Corpus", true),
  blank(),
  centered("[Student Name]"),
  centered("[Department], [University]"),
  centered("[Course Number]: [Course Name]"),
  centered("[Instructor Name]"),
  centered("[Due Date]"),
  new Paragraph({ children: [new PageBreak()] }),
];

const text = [
  h1("Person-Name Extraction With Support Vector Machines"),
  body("Named entity recognition (NER) is the task of finding spans of text that name real-world things and labeling each span with a type such as person, location, or organization (Nadeau & Sekine, 2007). This report describes how a support vector machine (SVM) trained on *Conll_NER_corpus.txt* can identify person names in the first 10,000 sentences of the BNC Baby corpus, and reports results from a working implementation."),

  h2("Named Entities and the Training Data"),
  body(`*Conll_NER_corpus.txt* is derived from the Annotated Corpus for Named Entity Recognition on Kaggle (Walia, n.d.) and follows the CoNLL column format (Tjong Kim Sang & De Meulder, 2003): one token per line, a tab, and the token's tag, with a blank line between sentences. The file holds 47,959 human-tagged sentences and ${R.train_tokens} tokens. Tags use the BIO scheme (Ramshaw & Marcus, 1995): *B-* marks the first word of an entity, *I-* marks a word inside it, and *O* marks a word outside any entity. Person names are tagged *B-per* (${R.b_per} tokens) and *I-per* (${R.i_per} tokens); in this corpus a title such as *President* or *Mr.* is part of the name, so "President Mahmoud Ahmadinejad" is tagged B-per I-per I-per. All other tags (geo, org, gpe, tim, art, eve, nat) are mapped to O, leaving three classes: B-PER, I-PER, and O.`),

  h2("Why an SVM"),
  body("An SVM finds the hyperplane that separates two classes with the largest margin (Cortes & Vapnik, 1995). Linear SVMs handle the very large, sparse feature vectors produced by text well and were a strong NER baseline before neural models (Isozaki & Kazawa, 2002). With three tags, one binary SVM is trained per tag (one-versus-rest) and each token receives the tag with the highest score. The implementation uses the LIBLINEAR solver (Fan et al., 2008) through scikit-learn's *LinearSVC* (Pedregosa et al., 2011), and NLTK's *BNCCorpusReader* to read the BNC XML files (Bird et al., 2009)."),

  h2("Procedure"),
  body("The procedure has two phases, shown in Figures 1 and 2. In training (Figure 1), every token becomes a feature dictionary describing the word itself (lowercased form, first and last three letters, capitalization, all-caps, digits, a trailing period as in *Mr.*), its shape (e.g., *McCain* becomes *XxXx*), and the same information for the two words on each side, since context such as *said* or a preceding title signals a name. A vectorizer builds a sparse matrix, 10% of sentences are held out to measure precision and recall, and the final model is retrained on all sentences with balanced class weights, because O covers about 97% of tokens."),
  body("In extraction (Figure 2), the first 10,000 sentences (*<s>* units) of BNC Baby are read in file order, given the same features, and tagged; each B-PER and its following I-PER tokens form a candidate name. A regular expression keeps only spans that look like names (capitalized words, initials, hyphens, apostrophes, and inner particles such as *van* or *de*). Names are written with their sentence numbers, followed by a frequency list."),
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
  h2("Results"),
  body(`On the 10% held-out split, token-level scores for B-PER were precision ${R.bp_p}, recall ${R.bp_r}, and *F*1 ${R.bp_f}; for I-PER they were ${R.ip_p}, ${R.ip_r}, and ${R.ip_f}. Applied to the first ${R.n_sents} BNC Baby sentences (${R.n_files} academic texts), the program extracted ${R.mentions} person-name mentions covering ${R.distinct} distinct names. The most frequent were ${R.top}. As the lab allows, these errors were not corrected.`),
];

const refs = [
  new Paragraph({ spacing: DOUBLE, alignment: AlignmentType.CENTER, pageBreakBefore: true,
    children: [new TextRun({ text: "References", bold: true })] }),
  ref("Bird, S., Klein, E., & Loper, E. (2009). *Natural language processing with Python.* O'Reilly Media."),
  ref("BNC Consortium. (2005). *The BNC Baby* (2nd ed.) [Data set]. Oxford Text Archive. http://hdl.handle.net/20.500.12024/2553"),
  ref("Cortes, C., & Vapnik, V. (1995). Support-vector networks. *Machine Learning, 20*(3), 273–297. https://doi.org/10.1007/BF00994018"),
  ref("Fan, R.-E., Chang, K.-W., Hsieh, C.-J., Wang, X.-R., & Lin, C.-J. (2008). LIBLINEAR: A library for large linear classification. *Journal of Machine Learning Research, 9*, 1871–1874."),
  ref("Isozaki, H., & Kazawa, H. (2002). Efficient support vector classifiers for named entity recognition. In *Proceedings of the 19th International Conference on Computational Linguistics* (pp. 390–396). Association for Computational Linguistics. https://doi.org/10.3115/1072228.1072282"),
  ref("Nadeau, D., & Sekine, S. (2007). A survey of named entity recognition and classification. *Lingvisticae Investigationes, 30*(1), 3–26. https://doi.org/10.1075/li.30.1.03nad"),
  ref("Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, É. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research, 12*, 2825–2830."),
  ref("Ramshaw, L. A., & Marcus, M. P. (1995). Text chunking using transformation-based learning. In *Proceedings of the Third Workshop on Very Large Corpora* (pp. 82–94). Association for Computational Linguistics."),
  ref("Tjong Kim Sang, E. F., & De Meulder, F. (2003). Introduction to the CoNLL-2003 shared task: Language-independent named entity recognition. In *Proceedings of the Seventh Conference on Natural Language Learning at HLT-NAACL 2003* (pp. 142–147). Association for Computational Linguistics."),
  ref("Walia, A. (n.d.). *Annotated corpus for named entity recognition* [Data set]. Kaggle. Retrieved November 1, 2026, from https://www.kaggle.com/abhinavwalia95/entity-annotated-corpus"),
];

const doc = new Document({
  creator: "[Student Name]",
  title: "Person-Name Extraction With Support Vector Machines",
  styles: { default: { document: { run: { font: FONT, size: 24 } } } },
  sections: [{
    properties: { page: {
      size: { width: 12240, height: 15840 },
      margin: { top: 1440, bottom: 1440, left: 1440, right: 1440, header: 720 },
    } },
    headers: { default: new Header({ children: [new Paragraph({
      alignment: AlignmentType.RIGHT, children: [new TextRun({ children: [PageNumber.CURRENT] })] })] }) },
    children: [...titlePage, ...text, ...pseudocode, ...results, ...refs],
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("Lab5_SVM_Person_Name_Extraction_Report.docx", buf);
  console.log("written");
});
