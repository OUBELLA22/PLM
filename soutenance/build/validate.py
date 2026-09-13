# -*- coding: utf-8 -*-
"""Structural checks on the generated .pptx (no external deps)."""

import re
import sys
import zipfile
import posixpath
import xml.etree.ElementTree as ET

PATH = sys.argv[1] if len(sys.argv) > 1 else \
    "/projects/sandbox/KATATOOL_Soutenance_Youssef_OUBELLA.pptx"

EMU_IN = 914400
SLIDE_W, SLIDE_H = 13.333, 7.5
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
P = "{http://schemas.openxmlformats.org/presentationml/2006/main}"

errors, warnings = [], []
z = zipfile.ZipFile(PATH)
names = set(z.namelist())

# 1. every part must be well-formed XML -------------------------------------
trees = {}
for n in sorted(names):
    if not n.endswith((".xml", ".rels")):
        continue
    try:
        trees[n] = ET.fromstring(z.read(n))
    except ET.ParseError as e:
        errors.append("XML mal formé dans %s : %s" % (n, e))

# 2. content-type overrides must point at real parts ------------------------
ct = trees.get("[Content_Types].xml")
declared = set()
for ov in ct.iter("{http://schemas.openxmlformats.org/package/2006/content-types}Override"):
    part = ov.get("PartName").lstrip("/")
    declared.add(part)
    if part not in names:
        errors.append("Content_Types déclare %s qui n'existe pas" % part)
for n in names:
    if n.endswith(".xml") and n not in declared and not n.startswith("_rels"):
        warnings.append("Part sans Override : %s" % n)

# 3. every relationship target must resolve --------------------------------
R = "{http://schemas.openxmlformats.org/package/2006/relationships}Relationship"
rel_map = {}
for n, t in trees.items():
    if not n.endswith(".rels"):
        continue
    base = posixpath.dirname(posixpath.dirname(n))  # strip _rels/
    ids = set()
    for rel in t.iter(R):
        rid, target = rel.get("Id"), rel.get("Target")
        if rid in ids:
            errors.append("Id de relation dupliqué %s dans %s" % (rid, n))
        ids.add(rid)
        if rel.get("TargetMode") == "External":
            continue
        resolved = posixpath.normpath(posixpath.join(base, target)).lstrip("/")
        if resolved not in names:
            errors.append("%s : cible introuvable %s -> %s" % (n, rid, resolved))
    rel_map[n] = ids

# 4. r:id references inside parts must exist in the matching .rels ----------
RID = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
for n, t in trees.items():
    if n.endswith(".rels") or not n.endswith(".xml"):
        continue
    rels_name = posixpath.join(posixpath.dirname(n), "_rels",
                               posixpath.basename(n) + ".rels")
    used = {el.get(RID) for el in t.iter() if el.get(RID)}
    if not used:
        continue
    have = rel_map.get(rels_name, set())
    for rid in used:
        if rid not in have:
            errors.append("%s référence %s absent de %s" % (n, rid, rels_name))

# 5. slide count consistency ------------------------------------------------
pres = trees["ppt/presentation.xml"]
sld_ids = list(pres.iter(P + "sldId"))
slide_files = sorted(n for n in names
                     if re.match(r"ppt/slides/slide\d+\.xml$", n))
if len(sld_ids) != len(slide_files):
    errors.append("presentation.xml liste %d diapos, %d fichiers présents"
                  % (len(sld_ids), len(slide_files)))
seen = set()
for e in sld_ids:
    v = e.get("id")
    if v in seen:
        errors.append("sldId dupliqué : %s" % v)
    seen.add(v)
    if not (256 <= int(v) <= 2147483647):
        errors.append("sldId hors plage : %s" % v)

# 6. geometry sanity: nothing outside the canvas ---------------------------
shape_total = 0
for n in slide_files:
    t = trees[n]
    for sp in t.iter(P + "sp"):
        xfrm = sp.find("./" + P + "spPr/" + A + "xfrm")
        if xfrm is None:
            continue
        shape_total += 1
        off, ext = xfrm.find(A + "off"), xfrm.find(A + "ext")
        x = int(off.get("x")) / EMU_IN
        y = int(off.get("y")) / EMU_IN
        w = int(ext.get("cx")) / EMU_IN
        h = int(ext.get("cy")) / EMU_IN
        if w <= 0 or h <= 0:
            errors.append("%s : forme de taille nulle/négative" % n)
        name = sp.find("./" + P + "nvSpPr/" + P + "cNvPr").get("name")
        if x < -0.02 or y < -0.02 or x + w > SLIDE_W + 0.02 \
                or y + h > SLIDE_H + 0.02:
            warnings.append("%s : « %s » dépasse le cadre "
                            "(x=%.2f y=%.2f w=%.2f h=%.2f)"
                            % (n.split("/")[-1], name, x, y, w, h))

# 7. every slide must carry notes with real text ---------------------------
for n in sorted(x for x in names
                if re.match(r"ppt/notesSlides/notesSlide\d+\.xml$", x)):
    txt = "".join(e.text or "" for e in trees[n].iter(A + "t")).strip()
    if len(txt) < 20:
        warnings.append("%s : notes vides ou trop courtes" % n)

# 8. duplicate shape ids within one slide ---------------------------------
for n in slide_files:
    ids = [sp.find("./" + P + "nvSpPr/" + P + "cNvPr").get("id")
           for sp in trees[n].iter(P + "sp")]
    if len(ids) != len(set(ids)):
        errors.append("%s : identifiants de forme dupliqués" % n)

print("Fichier      : %s" % PATH)
print("Parts        : %d" % len(names))
print("Diapositives : %d" % len(slide_files))
print("Formes       : %d" % shape_total)
print("")
if warnings:
    print("AVERTISSEMENTS (%d)" % len(warnings))
    for x in warnings:
        print("  ~ %s" % x)
    print("")
if errors:
    print("ERREURS (%d)" % len(errors))
    for x in errors:
        print("  x %s" % x)
    sys.exit(1)
print("OK — aucune erreur structurelle.")
