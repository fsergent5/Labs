#!/usr/bin/env python3
"""Lab 4 helper - flatten the BNC Baby XML texts into one sentence per line.

Usage: python3 bnc_to_sentences.py <BNCBaby_dir> [out.txt]
Walks the aca, dem, fic and news folders in order (files sorted by name),
joins the <w>/<c> tokens of every <s> element and writes
bnc_baby_sentences.txt.
"""
import os, sys
import xml.etree.ElementTree as ET

ROOT = sys.argv[1]
OUT  = sys.argv[2] if len(sys.argv) > 2 else "bnc_baby_sentences.txt"

count = 0
with open(OUT, "w", encoding="utf-8") as out:
    for genre in sorted(os.listdir(ROOT)):
        gdir = os.path.join(ROOT, genre)
        if not os.path.isdir(gdir):
            continue
        for fn in sorted(os.listdir(gdir)):
            if not fn.endswith(".xml"):
                continue
            for _, el in ET.iterparse(os.path.join(gdir, fn)):
                if el.tag == "s":
                    text = "".join(t.text or "" for t in el.iter() if t.tag in ("w", "c"))
                    text = " ".join(text.split())
                    if text:
                        out.write(text + "\n"); count += 1
                    el.clear()
print(f"Wrote {count} sentences -> {OUT}")
