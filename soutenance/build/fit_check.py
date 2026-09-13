# -*- coding: utf-8 -*-
"""
Estimates whether every text block fits inside its shape.

Wraps each paragraph using approximate Segoe UI advance widths and compares
the resulting height (and longest unbreakable word) against the shape box.
Conservative on purpose: it should over-report rather than miss an overflow.
"""

import re
import sys
import zipfile
import xml.etree.ElementTree as ET

PATH = sys.argv[1] if len(sys.argv) > 1 else \
    "/projects/sandbox/KATATOOL_Soutenance_Youssef_OUBELLA.pptx"

EMU_IN = 914400
PT_IN = 72.0
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"

# approximate advance widths in em for Segoe UI
_W = {}
for chars, val in [
    (" \u00a0", 0.26),
    (".,:;'`!|iljI\u2019", 0.30),
    ("ft()[]{}/\\-\u2013\u2014r", 0.36),
    ("abcdeghknopqsuvxyzcL1\u00e9\u00e8\u00ea\u00e0\u00e7\u00f9\u00fb\u00ee\u00ef\u00f4", 0.51),
    ("023456789", 0.56),
    ("ABCDEFGHJKNOPQRSTUVXYZ?&+=<>\u00c9\u00c0\u00c7\u2192\u2713\u2715\u00b7%", 0.62),
    ("mwMW\u0153", 0.80),
    ("@", 0.75),
]:
    for c in chars:
        _W[c] = val

LINE_EM = 1.30  # Segoe UI single-line box height, in em


def text_w(s, size_pt, bold):
    em = sum(_W.get(c, 0.55) for c in s)
    return em * (size_pt / PT_IN) * (1.045 if bold else 1.0)


def wrap_lines(text, size_pt, bold, avail_in):
    """Number of lines after wrapping, plus the widest unbreakable word."""
    total, widest = 0, 0.0
    for hard in text.split("\n"):
        words = hard.split(" ")
        if not words:
            total += 1
            continue
        line, n = "", 1
        for wd in words:
            widest = max(widest, text_w(wd, size_pt, bold))
            cand = wd if not line else line + " " + wd
            if text_w(cand, size_pt, bold) <= avail_in:
                line = cand
            else:
                n += 1
                line = wd
        total += n
    return total, widest


z = zipfile.ZipFile(PATH)
slides = sorted((n for n in z.namelist()
                 if re.match(r"ppt/slides/slide\d+\.xml$", n)),
                key=lambda n: int(re.search(r"(\d+)", n).group(1)))

issues = []
checked = 0

for n in slides:
    num = int(re.search(r"slide(\d+)", n).group(1))
    root = ET.fromstring(z.read(n))
    for sp in root.iter(P + "sp"):
        xfrm = sp.find("./" + P + "spPr/" + A + "xfrm")
        if xfrm is None:
            continue
        ext = xfrm.find(A + "ext")
        bw = int(ext.get("cx")) / EMU_IN
        bh = int(ext.get("cy")) / EMU_IN
        name = sp.find("./" + P + "nvSpPr/" + P + "cNvPr").get("name")
        body = sp.find("./" + P + "txBody/" + A + "bodyPr")
        tx = sp.find("./" + P + "txBody")
        if body is None or tx is None:
            continue

        def ins(attr):
            v = body.get(attr)
            return (int(v) / EMU_IN) if v is not None else 0.0

        avail_w = bw - ins("lIns") - ins("rIns")
        avail_h = bh - ins("tIns") - ins("bIns")

        used_h, widest, has_text = 0.0, 0.0, False
        for p in tx.findall(A + "p"):
            runs = p.findall(A + "r")
            if not runs:
                continue
            has_text = True
            txt = "".join(r.find(A + "t").text or "" for r in runs)
            rPr = runs[0].find(A + "rPr")
            size = int(rPr.get("sz", "1400")) / 100.0
            bold = rPr.get("b") == "1"
            spc = float(rPr.get("spc", "0")) / 100.0
            extra = (spc / PT_IN) * max(0, len(txt) - 1)

            pPr = p.find(A + "pPr")
            mult, before, after = 1.0, 0.0, 0.0
            if pPr is not None:
                ln = pPr.find(A + "lnSpc/" + A + "spcPct")
                if ln is not None:
                    mult = int(ln.get("val")) / 100000.0
                b = pPr.find(A + "spcBef/" + A + "spcPts")
                if b is not None:
                    before = int(b.get("val")) / 100.0 / PT_IN
                af = pPr.find(A + "spcAft/" + A + "spcPts")
                if af is not None:
                    after = int(af.get("val")) / 100.0 / PT_IN

            lines, word_w = wrap_lines(txt, size, bold,
                                       max(0.05, avail_w - extra))
            widest = max(widest, word_w)
            used_h += before + lines * (size / PT_IN) * LINE_EM * mult + after

        if not has_text:
            continue
        checked += 1
        if used_h > avail_h + 0.015:
            issues.append((num, name, "hauteur", used_h, avail_h))
        if widest > avail_w + 0.01:
            issues.append((num, name, "largeur (mot)", widest, avail_w))

print("Blocs de texte contrôlés : %d" % checked)
print("")
if not issues:
    print("OK — tous les textes tiennent dans leur cadre (estimation).")
else:
    print("DÉPASSEMENTS POSSIBLES (%d)" % len(issues))
    for num, name, kind, used, avail in issues:
        print("  diapo %02d | %-22s | %-14s %.2f\" > %.2f\" (marge %+.2f\")"
              % (num, name[:22], kind, used, avail, avail - used))
    sys.exit(1)
