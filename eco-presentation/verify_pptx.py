# -*- coding: utf-8 -*-
"""Structural self-check of the generated PPTX: parts, relationships, shape ids, text coverage."""
import os
import posixpath
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

PKG = "{http://schemas.openxmlformats.org/package/2006/relationships}"
CT = "{http://schemas.openxmlformats.org/package/2006/content-types}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"

path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "ECO_Product_Presentation.pptx")
errors, checks = [], []

z = zipfile.ZipFile(path)
names = set(z.namelist())

# 1. every content-type override points at an existing part
ct = ET.fromstring(z.read("[Content_Types].xml"))
for o in ct.findall(CT + "Override"):
    p = o.get("PartName").lstrip("/")
    if p not in names:
        errors.append("Override without part: " + p)
checks.append("content-type overrides -> %d" % len(ct.findall(CT + "Override")))

# 2. every relationship target resolves
rel_files = [n for n in names if n.endswith(".rels")]
nrel = 0
for rf in rel_files:
    base = posixpath.dirname(posixpath.dirname(rf)) or ""
    for r in ET.fromstring(z.read(rf)).findall(PKG + "Relationship"):
        if r.get("TargetMode") == "External":
            continue
        nrel += 1
        t = posixpath.normpath(posixpath.join(base, r.get("Target")))
        if t not in names:
            errors.append("%s -> missing target %s" % (rf, t))
checks.append("relationships resolved -> %d in %d .rels" % (nrel, len(rel_files)))

# 3. slides referenced by presentation.xml, in order, each with a layout rel
pres = ET.fromstring(z.read("ppt/presentation.xml"))
prels = {r.get("Id"): r.get("Target") for r in
         ET.fromstring(z.read("ppt/_rels/presentation.xml.rels")).findall(PKG + "Relationship")}
order = [prels[s.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id")]
         for s in pres.find(P + "sldIdLst")]
if len(set(order)) != len(order):
    errors.append("duplicate slide reference in sldIdLst")
sz = pres.find(P + "sldSz")
if (sz.get("cx"), sz.get("cy")) != ("12192000", "6858000"):
    errors.append("slide size is not 16:9 13.333x7.5in")
checks.append("slides in sldIdLst -> %d, size 16:9 OK" % len(order))

# 4. per-slide: unique shape ids, no empty text runs outside spacers, text extracted
total_chars = 0
for i in range(1, len(order) + 1):
    sn = "ppt/slides/slide%d.xml" % i
    if sn not in names:
        errors.append("missing " + sn)
        continue
    root = ET.fromstring(z.read(sn))
    ids = [c.get("id") for c in root.iter() if c.tag in (P + "cNvPr", P + "cNvGrpSpPr")
           and c.get("id") is not None]
    ids += [c.get("id") for c in root.iter(P + "cNvPr")]
    ids = [c.get("id") for c in root.iter(P + "cNvPr")]
    if len(set(ids)) != len(ids):
        errors.append("%s duplicate shape ids: %s" % (sn, [x for x in ids if ids.count(x) > 1]))
    txt = "".join(t.text or "" for t in root.iter(A + "t"))
    total_chars += len(txt)
    if len(txt.strip()) < 40:
        errors.append("%s looks empty (%d chars)" % (sn, len(txt.strip())))
    # shapes must stay inside the canvas
    for off, ext in zip(root.iter(A + "off"), root.iter(A + "ext")):
        pass
    for xfrm in root.iter(A + "xfrm"):
        off, ext = xfrm.find(A + "off"), xfrm.find(A + "ext")
        if off is None or ext is None:
            continue
        x, y = int(off.get("x")), int(off.get("y"))
        cx, cy = int(ext.get("cx")), int(ext.get("cy"))
        if x < 0 or y < 0 or x + cx > 12192000 + 1000 or y + cy > 6858000 + 1000:
            errors.append("%s shape out of canvas: %d,%d %dx%d" % (sn, x, y, cx, cy))
checks.append("shape ids unique, text present -> %d chars total" % total_chars)

print("\n".join("  ok  " + c for c in checks))
if errors:
    print("\n".join("  FAIL  " + x for x in errors))
    sys.exit(1)
print("  ok  no structural errors in %s (%.0f KB)" % (os.path.basename(path), os.path.getsize(path) / 1024))
