# -*- coding: utf-8 -*-
"""Check the annotation coordinates against the real screenshots.

Highlight boxes are authored in screenshot pixel space by reading the picture,
so the main risk is a typo that puts a ring partly outside the image or makes it
absurdly large. This asserts, for every mark:

  * the box lies inside the picture (a small overshoot is tolerated, since a
    highlight is allowed to hug an edge);
  * the box is big enough to be visible and small enough to be a highlight
    rather than a full-image wash;
  * marker numbers inside one figure are unique and start at 1;
  * every figure's image file exists and every legend entry has text.

Usage: python3 verify_marks.py
"""
import sys

from content_guide import build
from pdfwriter import Image

TOL = 6          # px a box may stick out past an edge
errors, notes = [], []
figs = [b for b in build() if b["kind"] == "figure"]

for f in figs:
    im = Image(f["image"], f["path"])
    marks = f.get("marks", [])
    boxed = [m for m in marks if m.get("box")]
    numbers = [m["n"] for m in marks if m.get("n")]

    if len(set(numbers)) != len(numbers):
        errors.append("%s: duplicate marker numbers %s" % (f["image"], numbers))
    if numbers and sorted(numbers) != list(range(1, len(numbers) + 1)):
        errors.append("%s: marker numbers are not 1..n (%s)" % (f["image"], sorted(numbers)))

    for m in marks:
        if not m.get("label") and not m.get("note") and not m.get("box"):
            errors.append("%s: a mark carries nothing at all" % f["image"])
        if m.get("note") and len(m["note"]) > 230:
            notes.append("%s: legend note is %d chars, may crowd the panel"
                         % (f["image"], len(m["note"])))

    for m in boxed:
        x, y, w, h = m["box"]
        label = m.get("label", "?")
        if w <= 0 or h <= 0:
            errors.append("%s / %s: non-positive box %s" % (f["image"], label, m["box"]))
            continue
        if x < -TOL or y < -TOL:
            errors.append("%s / %s: box starts outside the image at (%d,%d)"
                          % (f["image"], label, x, y))
        if x + w > im.w + TOL or y + h > im.h + TOL:
            errors.append("%s / %s: box %s runs past the %dx%d image (right %d, bottom %d)"
                          % (f["image"], label, m["box"], im.w, im.h, x + w, y + h))
        if w < 14 or h < 12:
            errors.append("%s / %s: box %dx%d is too small to read as a highlight"
                          % (f["image"], label, w, h))
        area = (w * h) / float(im.w * im.h)
        if area > 0.75 and m.get("fill", True):
            notes.append("%s / %s: highlight covers %.0f%% of the image; consider "
                         "fill=False" % (f["image"], label, area * 100))

print("checked %d figures, %d marks (%d with a highlight box)"
      % (len(figs), sum(len(f.get("marks", [])) for f in figs),
         sum(1 for f in figs for m in f.get("marks", []) if m.get("box"))))
for n in notes:
    print("  note  " + n)
if errors:
    for e in errors:
        print("  FAIL  " + e)
    print("\n%d problem(s)" % len(errors))
    sys.exit(1)
print("  PASS  every highlight sits inside its screenshot")
