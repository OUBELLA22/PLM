# -*- coding: utf-8 -*-
"""Validate the generated .docx.

Word reports "unreadable content" and silently drops parts rather than telling
you what is wrong, so the package is checked here instead:

  1. the zip holds every part its [Content_Types].xml declares, and vice versa;
  2. every part is well-formed XML;
  3. every relationship target exists, and every r:embed in the document
     resolves to an image part;
  4. DrawingML object ids are unique (Word mangles duplicates);
  5. every figure is a wpg group that contains exactly one picture and its
     annotation shapes, with a child coordinate space declared;
  6. every annotation shape sits inside its group's bounds;
  7. the document is greyscale only - every colour is checked for R=G=B,
     which is the "white background, no colours" requirement;
  8. embedded images are byte-identical to the source screenshots;
  9. property elements appear in the order the schema requires.

Usage: python3 verify_docx.py [file.docx]
"""
import os
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "PLM_PDEF_ECR_ECO_Guide.docx")
HERE = os.path.dirname(os.path.abspath(PATH))

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
WP = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}"
PIC = "{http://schemas.openxmlformats.org/drawingml/2006/picture}"
WPG = "{http://schemas.microsoft.com/office/word/2010/wordprocessingGroup}"
WPS = "{http://schemas.microsoft.com/office/word/2010/wordprocessingShape}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
CT = "{http://schemas.openxmlformats.org/package/2006/content-types}"
PKG = "{http://schemas.openxmlformats.org/package/2006/relationships}"

errors, checks, notes = [], [], []
z = zipfile.ZipFile(PATH)
names = set(z.namelist())

# ------------------------------------------------------------ 1. content types
ct = ET.fromstring(z.read("[Content_Types].xml"))
defaults = {d.get("Extension").lower(): d.get("ContentType")
            for d in ct.findall(CT + "Default")}
overrides = {o.get("PartName").lstrip("/"): o.get("ContentType")
             for o in ct.findall(CT + "Override")}
for part in overrides:
    if part not in names:
        errors.append("declared but missing from the zip: %s" % part)
for n in names:
    if n == "[Content_Types].xml" or n.endswith("/"):
        continue
    ext = n.rsplit(".", 1)[-1].lower()
    if n not in overrides and ext not in defaults:
        errors.append("part has no content type: %s" % n)
checks.append("content types: %d overrides, %d defaults, all parts covered"
              % (len(overrides), len(defaults)))

# ------------------------------------------------------------- 2. well-formed
trees = {}
for n in sorted(names):
    if not (n.endswith(".xml") or n.endswith(".rels")):
        continue
    try:
        trees[n] = ET.fromstring(z.read(n))
    except ET.ParseError as exc:
        errors.append("%s is not well-formed XML: %s" % (n, exc))
checks.append("xml: %d parts parse" % len(trees))

for required in ("word/document.xml", "word/styles.xml", "word/numbering.xml",
                 "word/settings.xml", "word/_rels/document.xml.rels",
                 "_rels/.rels", "docProps/core.xml"):
    if required not in names:
        errors.append("missing required part: %s" % required)

# ---------------------------------------------------------- 3. relationships
rels = {}
for n, tree in trees.items():
    if not n.endswith(".rels"):
        continue
    base = os.path.dirname(os.path.dirname(n)) if "/_rels/" in n else ""
    for rel in tree.findall(PKG + "Relationship"):
        if rel.get("TargetMode") == "External":
            continue
        tgt = os.path.normpath(os.path.join(base, rel.get("Target"))).replace("\\", "/")
        if tgt not in names:
            errors.append("%s -> missing target %s" % (n, tgt))
        if n == "word/_rels/document.xml.rels":
            rels[rel.get("Id")] = tgt
checks.append("relationships: %d resolve, %d from document.xml" % (
    sum(len(t.findall(PKG + "Relationship")) for nn, t in trees.items()
        if nn.endswith(".rels")), len(rels)))

doc = trees["word/document.xml"]
embeds = [b.get(R + "embed") for b in doc.iter(A + "blip")]
for rid in embeds:
    if rid not in rels:
        errors.append("r:embed %s has no relationship" % rid)
    elif not rels[rid].startswith("word/media/"):
        errors.append("r:embed %s does not point at media (%s)" % (rid, rels[rid]))
checks.append("pictures: %d r:embed references, all resolve to media parts" % len(embeds))

footer_refs = [f.get(R + "id") for f in doc.iter(W + "footerReference")]
for rid in footer_refs:
    if rid not in rels:
        errors.append("footerReference %s has no relationship" % rid)

# ------------------------------------------------------------- 4. object ids
ids = []
for tag in (WP + "docPr", PIC + "cNvPr", WPS + "cNvPr"):
    ids += [e.get("id") for e in doc.iter(tag) if e.get("id")]
dupes = {i for i in ids if ids.count(i) > 1}
if dupes:
    errors.append("duplicate DrawingML object ids: %s" % sorted(dupes)[:10])
checks.append("drawing object ids: %d, all unique" % len(ids))

# ------------------------------------------------- 5/6. groups and their shapes
groups = list(doc.iter(WPG + "wgp"))
total_rect = total_oval = 0
for gi, g in enumerate(groups, 1):
    pics = g.findall(PIC + "pic")
    if len(pics) != 1:
        errors.append("group %d holds %d pictures, expected 1" % (gi, len(pics)))
    grp = g.find(WPG + "grpSpPr")
    xfrm = grp.find(A + "xfrm") if grp is not None else None
    if xfrm is None:
        errors.append("group %d has no grpSpPr/xfrm" % gi)
        continue
    ext = xfrm.find(A + "ext")
    chext = xfrm.find(A + "chExt")
    choff = xfrm.find(A + "chOff")
    if ext is None or chext is None or choff is None:
        errors.append("group %d is missing ext / chExt / chOff" % gi)
        continue
    gw, gh = int(ext.get("cx")), int(ext.get("cy"))
    if (int(chext.get("cx")), int(chext.get("cy"))) != (gw, gh):
        errors.append("group %d chExt does not match ext, shapes would be scaled" % gi)
    for wsp in g.findall(WPS + "wsp"):
        # schema order inside wsp: cNvPr, cNvSpPr, spPr, [txbx], bodyPr
        kids = [k.tag.split("}")[-1] for k in list(wsp)]
        expected = ["cNvPr", "cNvSpPr", "spPr"]
        if kids[:3] != expected or kids[-1] != "bodyPr":
            errors.append("group %d shape has children in the wrong order: %s"
                          % (gi, kids))
        sp = wsp.find(WPS + "spPr")
        geom = sp.find(A + "prstGeom")
        kind = geom.get("prst") if geom is not None else "?"
        if kind == "rect":
            total_rect += 1
        elif kind == "ellipse":
            total_oval += 1
        sx = sp.find(A + "xfrm")
        off, sext = sx.find(A + "off"), sx.find(A + "ext")
        x, y = int(off.get("x")), int(off.get("y"))
        cx, cy = int(sext.get("cx")), int(sext.get("cy"))
        if x < 0 or y < 0 or x + cx > gw + 1000 or y + cy > gh + 1000:
            errors.append("group %d: shape %dx%d at (%d,%d) escapes the %dx%d group"
                          % (gi, cx, cy, x, y, gw, gh))
        name = wsp.find(WPS + "cNvPr").get("name") or ""
        if not name:
            notes.append("group %d: a shape has no name, harder to find in the "
                         "Selection Pane" % gi)
checks.append("figures: %d groups, %d highlight rectangles, %d numbered markers, "
              "all inside their group" % (len(groups), total_rect, total_oval))

# ------------------------------------------------------------- 7. greyscale
raw_doc = z.read("word/document.xml").decode("utf8")
raw_sty = z.read("word/styles.xml").decode("utf8")
bad_colors = set()
for blob in (raw_doc, raw_sty):
    for val in re.findall(r'(?:srgbClr val|w:color w:val|w:fill)="([0-9A-Fa-f]{6})"', blob):
        r_, g_, b_ = val[0:2].lower(), val[2:4].lower(), val[4:6].lower()
        if not (r_ == g_ == b_):
            bad_colors.add(val.upper())
if bad_colors:
    errors.append("non-greyscale colours in the document: %s" % sorted(bad_colors))
checks.append("palette: greyscale only (every colour has R=G=B)")

if 'w:fill="FFFFFF"' in raw_doc or "background" in raw_doc.lower():
    notes.append("an explicit white fill is present, which is harmless")

# -------------------------------------------------- 8. images byte-identical
import hashlib

src_hash = {}
for sub in ("img", "img_prea"):
    d = os.path.join(HERE, sub)
    if not os.path.isdir(d):
        continue
    for fn in os.listdir(d):
        p = os.path.join(d, fn)
        src_hash[hashlib.sha256(open(p, "rb").read()).hexdigest()] = fn
matched = 0
for n in sorted(names):
    if not n.startswith("word/media/"):
        continue
    h = hashlib.sha256(z.read(n)).hexdigest()
    if h in src_hash:
        matched += 1
    else:
        errors.append("%s does not match any source screenshot (re-encoded?)" % n)
checks.append("media: %d images, all byte-identical to the source screenshots" % matched)

# ------------------------------------------------------- 9. property ordering
RPR = ["rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps", "strike", "color",
       "spacing", "w", "kern", "position", "sz", "szCs", "highlight", "u"]
PPR = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "numPr", "pBdr",
       "shd", "tabs", "spacing", "ind", "contextualSpacing", "jc", "outlineLvl"]


def check_order(tree, tag, order, what):
    pos = {n: i for i, n in enumerate(order)}
    bad = 0
    for el in tree.iter(tag):
        seq = [k.tag.split("}")[-1] for k in list(el)]
        idx = [pos[s] for s in seq if s in pos]
        if idx != sorted(idx):
            bad += 1
            if bad == 1:
                errors.append("%s children out of schema order in %s: %s"
                              % (tag.split('}')[-1], what, seq))
    return bad


bad = 0
for part in ("word/document.xml", "word/styles.xml", "word/footer1.xml"):
    if part in trees:
        bad += check_order(trees[part], W + "rPr", RPR, part)
        bad += check_order(trees[part], W + "pPr", PPR, part)
if not bad:
    checks.append("schema order: w:rPr and w:pPr children in sequence everywhere")

# ------------------------------------------------------------------- report
paras = len(list(doc.iter(W + "p")))
tables = len(list(doc.iter(W + "tbl")))
headings = len([p for p in doc.iter(W + "p")
                if p.find(W + "pPr/" + W + "pStyle") is not None
                and (p.find(W + "pPr/" + W + "pStyle").get(W + "val") or "")
                .startswith("Heading")])
has_toc = " TOC " in raw_doc
checks.append("document: %d paragraphs, %d tables, %d headings, TOC field %s"
              % (paras, tables, headings, "present" if has_toc else "MISSING"))
if not has_toc:
    errors.append("no TOC field found")

print("\n".join("  ok    " + c for c in checks))
for n in notes:
    print("  note  " + n)
if errors:
    print("\n".join("  FAIL  " + e for e in errors))
    print("\n%d problem(s)" % len(errors))
    sys.exit(1)
print("\n  PASS  %s (%.0f KB)" % (os.path.basename(PATH), os.path.getsize(PATH) / 1024.0))
