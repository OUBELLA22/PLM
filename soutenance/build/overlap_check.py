# -*- coding: utf-8 -*-
"""
Geometric checks on the generated deck.

1. No two blocks of rendered text collide.
2. No text escapes the card / column / step box that visually contains it.
3. No two sibling cards overlap.

Text extent is estimated from Segoe UI metrics plus the paragraph alignment
and the shape anchor, so a right-aligned short string is not treated as if it
filled its whole box.
"""

import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from metrics import wrap_info, line_h  # noqa: E402

PATH = sys.argv[1] if len(sys.argv) > 1 else \
    "/projects/sandbox/KATATOOL_Soutenance_Youssef_OUBELLA.pptx"

EMU_IN = 914400
PT_IN = 72.0
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"

CONTAINERS = ("Carte", "Colonne", "Étape", "Hub", "Bloc", "Icône", "Puce",
              "Logo", "Photo", "Emplacement capture", "Pastille")

EPS = 0.030          # tolerance, inches
MIN_AREA = 0.0035    # ignore hairline intersections


def parse_shape(sp):
    xfrm = sp.find("./" + P + "spPr/" + A + "xfrm")
    if xfrm is None:
        return None
    off, ext = xfrm.find(A + "off"), xfrm.find(A + "ext")
    box = [int(off.get("x")) / EMU_IN, int(off.get("y")) / EMU_IN,
           int(ext.get("cx")) / EMU_IN, int(ext.get("cy")) / EMU_IN]
    name = sp.find("./" + P + "nvSpPr/" + P + "cNvPr").get("name")
    body = sp.find("./" + P + "txBody/" + A + "bodyPr")
    tx = sp.find("./" + P + "txBody")
    filled = sp.find("./" + P + "spPr/" + A + "solidFill") is not None or \
        sp.find("./" + P + "spPr/" + A + "gradFill") is not None

    def ins(attr):
        v = body.get(attr) if body is not None else None
        return (int(v) / EMU_IN) if v is not None else 0.0

    anchor = body.get("anchor", "t") if body is not None else "t"
    x, y, w, h = box
    avail_w = w - ins("lIns") - ins("rIns")

    widest, total_h, align = 0.0, 0.0, "l"
    for p in tx.findall(A + "p") if tx is not None else []:
        runs = p.findall(A + "r")
        if not runs:
            continue
        txt = "".join(r.find(A + "t").text or "" for r in runs)
        rPr = runs[0].find(A + "rPr")
        size = int(rPr.get("sz", "1400")) / 100.0
        bold = rPr.get("b") == "1"
        spc = float(rPr.get("spc", "0")) / 100.0
        extra = (spc / PT_IN) * max(0, len(txt) - 1)
        pPr = p.find(A + "pPr")
        mult, before, after = 1.0, 0.0, 0.0
        if pPr is not None:
            align = pPr.get("algn", align)
            ln = pPr.find(A + "lnSpc/" + A + "spcPct")
            if ln is not None:
                mult = int(ln.get("val")) / 100000.0
            b = pPr.find(A + "spcBef/" + A + "spcPts")
            if b is not None:
                before = int(b.get("val")) / 100.0 / PT_IN
            af = pPr.find(A + "spcAft/" + A + "spcPts")
            if af is not None:
                after = int(af.get("val")) / 100.0 / PT_IN
        lines, line_w, _ = wrap_info(txt, size, bold, max(0.05, avail_w - extra))
        widest = max(widest, min(avail_w, line_w + extra))
        total_h += before + lines * line_h(size, mult) + after

    ink = None
    if widest > 0 and total_h > 0:
        if align == "ctr":
            ix = x + (w - widest) / 2.0
        elif align == "r":
            ix = x + w - ins("rIns") - widest
        else:
            ix = x + ins("lIns")
        if anchor == "ctr":
            iy = y + (h - total_h) / 2.0
        elif anchor == "b":
            iy = y + h - ins("bIns") - total_h
        else:
            iy = y + ins("tIns")
        ink = (ix, iy, widest, total_h)

    return {"name": name, "box": box, "ink": ink, "filled": filled,
            "container": any(name.startswith(c) for c in CONTAINERS)}


def inter(a, b):
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ox = min(ax + aw, bx + bw) - max(ax, bx)
    oy = min(ay + ah, by + bh) - max(ay, by)
    if ox <= EPS or oy <= EPS:
        return 0.0
    return ox * oy


def contains(outer, innr):
    ox, oy, ow, oh = outer
    ix, iy, iw, ih = innr
    return (ix >= ox - EPS and iy >= oy - EPS
            and ix + iw <= ox + ow + EPS and iy + ih <= oy + oh + EPS)


z = zipfile.ZipFile(PATH)
slide_files = sorted((n for n in z.namelist()
                      if re.match(r"ppt/slides/slide\d+\.xml$", n)),
                     key=lambda n: int(re.search(r"(\d+)", n).group(1)))

problems = []
for n in slide_files:
    num = int(re.search(r"slide(\d+)", n).group(1))
    root = ET.fromstring(z.read(n))
    shapes = [s for s in (parse_shape(sp) for sp in root.iter(P + "sp")) if s]

    texts = [s for s in shapes if s["ink"] and not s["container"]]
    boxes = [s for s in shapes if s["container"] and s["filled"]
             and s["name"].startswith(("Carte", "Colonne", "Étape", "Hub"))]

    # 1. text vs text
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            a, b = texts[i], texts[j]
            if inter(a["ink"], b["ink"]) > MIN_AREA:
                problems.append(
                    "diapo %02d : texte/texte « %s » ∩ « %s »"
                    % (num, a["name"], b["name"]))

    # 2. text must stay inside the card it sits in
    for t in texts:
        tx, ty, tw, th = t["ink"]
        cx, cy = tx + tw / 2.0, ty + th / 2.0
        for c in boxes:
            bx, by, bw, bh = c["box"]
            if bx <= cx <= bx + bw and by <= cy <= by + bh:
                if not contains(c["box"], t["ink"]):
                    problems.append(
                        "diapo %02d : texte hors carte « %s » "
                        "(texte %.2f,%.2f %.2fx%.2f / carte %.2f,%.2f %.2fx%.2f)"
                        % (num, t["name"], tx, ty, tw, th, bx, by, bw, bh))
                break

    # 3. cards must not overlap each other
    for i in range(len(boxes)):
        for j in range(i + 1, len(boxes)):
            if inter(boxes[i]["box"], boxes[j]["box"]) > MIN_AREA:
                problems.append("diapo %02d : cartes superposées « %s » / « %s »"
                                % (num, boxes[i]["name"], boxes[j]["name"]))

print("Diapositives analysées : %d" % len(slide_files))
print("")
if not problems:
    print("OK — aucune collision, aucun texte hors cadre.")
else:
    print("PROBLÈMES GÉOMÉTRIQUES (%d)" % len(problems))
    for p in problems:
        print("  ! %s" % p)
    sys.exit(1)
