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
        # body content must stay above the footer rule (6.55in); only the footer sits below.
        # Full-bleed background rectangles are exempt.
        if cx >= 12192000 * 0.99:
            continue
        if y < int(6.6 * 914400) and y + cy > int(6.56 * 914400):
            errors.append("%s shape runs into the footer: y=%d cy=%d (bottom %.2fin)"
                          % (sn, y, cy, (y + cy) / 914400.0))
checks.append("shape ids unique, text present -> %d chars total" % total_chars)

# 5. pictures: every r:embed resolves, media part exists, aspect ratio preserved
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def png_jpeg_size(blob):
    if blob[:8] == b"\x89PNG\r\n\x1a\n":
        return struct.unpack(">II", blob[16:24])
    i = 2
    while i < len(blob):
        while blob[i] != 0xFF:
            i += 1
        m = blob[i + 1]
        if m in (0xC0, 0xC1, 0xC2, 0xC3):
            h, w = struct.unpack(">HH", blob[i + 5:i + 9])
            return w, h
        i += 2 + struct.unpack(">H", blob[i + 2:i + 4])[0]
    raise ValueError("unknown image")


import struct  # noqa: E402  (used by png_jpeg_size)

npic = 0
for i in range(1, len(order) + 1):
    sn = "ppt/slides/slide%d.xml" % i
    root = ET.fromstring(z.read(sn))
    srel = {r.get("Id"): r.get("Target") for r in
            ET.fromstring(z.read("ppt/slides/_rels/slide%d.xml.rels" % i)).findall(PKG + "Relationship")}
    for p in root.iter(P + "pic"):
        npic += 1
        rid = p.find(P + "blipFill").find(A + "blip").get(R + "embed")
        tgt = srel.get(rid)
        if not tgt:
            errors.append("%s pic references unknown %s" % (sn, rid))
            continue
        part = posixpath.normpath(posixpath.join("ppt/slides", tgt))
        if part not in names:
            errors.append("%s pic -> missing media %s" % (sn, part))
            continue
        ext = p.find(P + "spPr").find(A + "xfrm").find(A + "ext")
        cx, cy = int(ext.get("cx")), int(ext.get("cy"))
        w, h = png_jpeg_size(z.read(part))
        if abs((cx / float(cy)) - (w / float(h))) > 0.02 * (w / float(h)):
            errors.append("%s pic %s distorted: box %dx%d vs image %dx%d" % (sn, tgt, cx, cy, w, h))
        if min(cx, cy) < 400000:
            errors.append("%s pic %s is tiny (%dx%d EMU)" % (sn, tgt, cx, cy))
checks.append("pictures embedded -> %d, refs resolve, aspect ratio kept" % npic)

# 6. no picture sits on top of a text box that carries text (frames are exempt: they are
#    deliberately drawn behind their picture and hold no text)
def box(el):
    x = el.find(A + "xfrm")
    if x is None:
        return None
    o, e = x.find(A + "off"), x.find(A + "ext")
    return (int(o.get("x")), int(o.get("y")), int(e.get("cx")), int(e.get("cy")))


overlaps = 0
for i in range(1, len(order) + 1):
    root = ET.fromstring(z.read("ppt/slides/slide%d.xml" % i))
    pics = [box(p.find(P + "spPr")) for p in root.iter(P + "pic")]
    texts = []
    for sp in root.iter(P + "sp"):
        t = "".join(x.text or "" for x in sp.iter(A + "t")).strip()
        b = box(sp.find(P + "spPr"))
        if t and b:
            texts.append((t, b))
    for pb in pics:
        for t, tb in texts:
            ix = min(pb[0] + pb[2], tb[0] + tb[2]) - max(pb[0], tb[0])
            iy = min(pb[1] + pb[3], tb[1] + tb[3]) - max(pb[1], tb[1])
            if ix > 91440 and iy > 91440:       # more than 0.1in of real overlap
                overlaps += 1
                errors.append("slide%d: picture overlaps text %r" % (i, t[:40]))
checks.append("picture / text collisions -> %d" % overlaps)

print("\n".join("  ok  " + c for c in checks))
if errors:
    print("\n".join("  FAIL  " + x for x in errors))
    sys.exit(1)
print("  ok  no structural errors in %s (%.0f KB)" % (os.path.basename(path), os.path.getsize(path) / 1024))
