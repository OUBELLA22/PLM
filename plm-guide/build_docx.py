# -*- coding: utf-8 -*-
"""Build the Word edition of the PLM PDEF / ECR / ECO guide.

Same content as the PDF (`content_guide.py` is shared), rendered for Word:

  * white page, no colour theme - black text, grey rules, grey table shading;
  * A4 portrait with real Word heading styles, so the Navigation pane and the
    table of contents work;
  * every figure is a **group of editable shapes** over an unmodified
    screenshot, so each highlight and each numbered marker can be dragged,
    resized, restyled or deleted in Word.

    python3 build_docx.py [output.docx]
"""
import os
import sys

import docxwriter as D
from content_guide import META, build
from docxwriter import Docx, list_para, para, run, table, tab, toc_field

HERE = os.path.dirname(os.path.abspath(__file__))

# A4 portrait, 2.2 cm margins
MARGIN_CM = 2.2
CONTENT_TWIP = 11906 - 2 * int(round(MARGIN_CM / 2.54 * D.TWIP_IN))
CONTENT_EMU = CONTENT_TWIP * D.EMU_TWIP

BULLET, NUMBER = 1, 2

# Run styles from content_guide -> Word formatting. The colourful ones all
# collapse to bold, because the document is black and white by request.
BOLD = {"b", "bi", "acc", "ok", "warn", "dan", "ui"}
ITALIC = {"i", "bi"}

# Highlights that sit on a dark part of a screenshot need white ink instead of
# black, keyed by (image, label).
LIGHT_INK = {("01-actions-menu.png", "Actions toolbar")}


def runs_of(item):
    """content_guide rich text -> Word runs."""
    if isinstance(item, str):
        segs = [(item, "")]
    elif isinstance(item, tuple):
        segs = [item]
    else:
        segs = list(item)
    out = []
    for text, style in segs:
        out.append(run(text, bold=style in BOLD, italic=style in ITALIC))
    return "".join(out)


def plain(item):
    if isinstance(item, str):
        return item
    if isinstance(item, tuple):
        return item[0]
    return "".join(t for t, _s in item)


def cell(item, bold=False, size=9.5, align=None, after=0):
    if bold:
        body = run(plain(item), bold=True, size=size)
    else:
        body = "".join(
            run(t, bold=(s in BOLD) or bold, italic=s in ITALIC, size=size)
            for t, s in ([(item, "")] if isinstance(item, str)
                         else [item] if isinstance(item, tuple) else item))
    return para(body, before=0, after=after, align=align, line=252)


def note_box(text, label=None):
    """A shaded single-cell table: the professional 'note' block."""
    inner = ""
    if label:
        inner += para(run(label.upper(), bold=True, size=8, spacing=30),
                      before=0, after=40)
    inner += para(runs_of(text), before=0, after=0, line=252)
    return table([[inner]], [CONTENT_TWIP], header=False, stripe=None,
                 borders=True, pad=110)


def ink_for(image, mark):
    if (image, mark.get("label")) in LIGHT_INK:
        return "light"
    return "dark"


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        HERE, "PLM_PDEF_ECR_ECO_Guide.docx")
    doc = Docx(title=META["title"], subject=META["subject"], author=META["author"])
    blocks = build()
    figures = 0

    for b in blocks:
        k = b["kind"]

        # ------------------------------------------------ title page + TOC
        if k == "cover":
            doc.add(para(run(b["kicker"].upper(), bold=True, size=9, spacing=60),
                         before=1200, after=200))
            doc.add(para(run("%s %s" % (b["title"], b["title2"]), bold=True, size=32),
                         before=0, after=120))
            doc.add(para(run(b["subtitle"], size=15), before=0, after=200))
            doc.add(para(runs_of(b["tagline"]), before=0, after=360))
            rows = [[cell(k2, bold=True, size=9), cell(v, size=9)]
                    for k2, v in b["specs"]]
            doc.add(table(rows, [int(CONTENT_TWIP * 0.26), int(CONTENT_TWIP * 0.74)],
                          header=False, stripe=None, borders=True))
            doc.add(para(run(b["meta"], italic=True, size=8.5),
                         before=320, after=0))
            # how to edit the annotations - the point of the Word edition
            doc.add(para(run("Working with the annotations", bold=True, size=12),
                         before=400, after=100, page_break=True))
            doc.add(para(
                run("Every screenshot in this document is the original, unmodified "
                    "picture from the source methodology. The rectangles and numbered "
                    "circles drawn on top are ordinary Word shapes, grouped with the "
                    "picture. Nothing is burnt into the image, so you can change any "
                    "annotation:", size=10.5), after=160))
            for step in [
                "Click a figure once to select the group, then click a rectangle or a "
                "circle inside it to select that shape on its own.",
                "Drag it to move it, or use its handles to resize it. Arrow keys nudge "
                "it a pixel at a time.",
                "Change its look with Shape Format \u25b8 Shape Outline (weight, dash, "
                "colour) or Shape Fill.",
                "Delete a shape you do not need, or copy and paste one to add another "
                "highlight.",
                "To find a specific shape, open Home \u25b8 Find & Select \u25b8 Selection "
                "Pane. Every shape is named, for example \u201cHighlight 7.3 \u2014 Create "
                "Product ECO\u2026\u201d or \u201cMarker 7.3\u201d.",
                "Right-click the group and choose Group \u25b8 Ungroup if you would rather "
                "work with the picture and the shapes separately.",
            ]:
                doc.add(list_para(run(step, size=10), NUMBER))
            doc.add(note_box(
                [("The numbers in the circles match the numbered list printed under "
                  "each figure.", "b"),
                 (" If you move or renumber a marker, update the list below the figure "
                  "to match \u2014 it is plain text, so you can edit it directly.", "")],
                label="Keep them in step"))
            doc.add(para(run("Contents", bold=True, size=20), page_break=True,
                         before=0, after=200))
            doc.add(toc_field())
            continue

        # --------------------------------------------------------- chapter
        if k == "chapter":
            # the eyebrow carries the page break so the Heading 1 run below is
            # what the table of contents picks up
            doc.add(para(run("CHAPTER %s" % b["num"], bold=True, size=9, spacing=50),
                         before=0, after=60, page_break=True, keep_next=True))
            doc.add(para(run(b["title"], bold=True, size=20),
                         style="Heading1", outline=0, before=0, after=160))
            doc.add(para(runs_of(b["lead"]), after=160))
            for item in b.get("covers", []):
                doc.add(list_para(run(item, size=10), BULLET))
            continue

        if k == "h2":
            if b.get("eyebrow"):
                doc.add(para(run(b["eyebrow"].upper(), bold=True, size=8, spacing=40),
                             style="Eyebrow"))
            doc.add(para(run(plain(b["title"]), bold=True, size=13),
                         style="Heading2", outline=1))
            continue

        if k == "h3":
            doc.add(para(run(plain(b["title"]), bold=True, size=11),
                         style="Heading3", outline=2))
            continue

        if k == "para":
            doc.add(para(runs_of(b["text"]), after=140))
            continue

        if k == "bullets":
            for item in b["bullets"]:
                doc.add(list_para(runs_of(item), BULLET))
            doc.add(para("", before=0, after=60))
            continue

        if k == "steps":
            for item in b["steps"]:
                doc.add(list_para(runs_of(item), NUMBER))
            doc.add(para("", before=0, after=60))
            continue

        if k == "callout":
            doc.add(note_box(b["text"], b.get("label")))
            doc.add(para("", before=0, after=80))
            continue

        if k == "table":
            colw = [int(CONTENT_TWIP * f) for f in b["colw"]]
            colw[-1] = CONTENT_TWIP - sum(colw[:-1])
            rows = [[cell(h, bold=True, size=9) for h in b["head"]]]
            for r in b["rows"]:
                rows.append([cell(c, bold=(i == 0), size=9)
                             for i, c in enumerate(r)])
            doc.add(table(rows, colw))
            doc.add(para("", before=0, after=100))
            continue

        if k == "cards":
            colw = [int(CONTENT_TWIP * 0.30),
                    CONTENT_TWIP - int(CONTENT_TWIP * 0.30)]
            rows = [[cell("Option", bold=True, size=9),
                     cell("What it involves", bold=True, size=9)]]
            for cd in b["cards"]:
                left = para(run(cd["tag"].upper(), bold=True, size=8, spacing=30),
                            before=0, after=30)
                left += para(run(cd["title"], bold=True, size=10.5),
                             before=0, after=0, line=252)
                right = "".join(
                    para(run("\u2022  ", size=9) + run(ln, size=9),
                         before=0, after=30, left=160, hanging=160, line=252)
                    for ln in cd["lines"])
                rows.append([left, right])
            doc.add(table(rows, colw))
            doc.add(para("", before=0, after=100))
            continue

        if k == "flow":
            for r in b["rows"]:
                doc.add(para(run(r["label"].upper(), bold=True, size=8, spacing=40),
                             before=120, after=40))
                body = ""
                for i, chip in enumerate(r["chips"]):
                    if i:
                        body += run("   \u25b8   ", size=10)
                    body += run(chip, bold=True, size=10.5)
                doc.add(para(body, after=140))
            continue

        if k == "glossary":
            colw = [int(CONTENT_TWIP * 0.34),
                    CONTENT_TWIP - int(CONTENT_TWIP * 0.34)]
            rows = [[cell("Label on screen", bold=True, size=9),
                     cell("Meaning", bold=True, size=9)]]
            for a, c in b["pairs"]:
                rows.append([cell(a, bold=True, size=9), cell(c, size=9)])
            doc.add(table(rows, colw))
            doc.add(para("", before=0, after=100))
            continue

        if k in ("space", "divider"):
            doc.add(para("", before=0, after=60))
            continue

        # ---------------------------------------------------------- figure
        if k == "figure":
            figures += 1
            marks = list(b.get("marks", []))
            for m in marks:
                m = dict(m)
            marks = [dict(m, ink=ink_for(b["image"], m)) for m in marks]
            # wide screenshots take the full measure; narrow ones are capped so
            # they are not blown up past a readable resolution
            _rid, pw, _ph = doc.image(b["path"])
            target = min(CONTENT_EMU, int(pw / 130.0 * D.EMU_IN))
            xml, _gh = doc.figure_group(
                b["path"], target, marks,
                name="Figure %d \u2014 %s" % (figures, plain(b.get("label", b["image"]))))
            doc.add(para(xml, align="center", before=160, after=60,
                         keep_next=True))
            cap = "Figure %d. %s" % (figures, plain(b.get("caption", "")))
            doc.add(para(run(cap, italic=True, size=8.5), style="Caption",
                         keep_next=bool(marks)))
            for m in marks:
                if not (m.get("label") or m.get("note")):
                    continue
                body = ""
                if m.get("n"):
                    body += run(str(m["n"]), bold=True, size=9) + tab()
                if m.get("label"):
                    body += run(plain(m["label"]), bold=True, size=9)
                if m.get("label") and m.get("note"):
                    body += run("  \u2014  ", size=9)
                if m.get("note"):
                    body += run(plain(m["note"]), size=9)
                doc.add(para(body, style="LegendItem"))
            doc.add(para("", before=0, after=100))
            continue

        raise SystemExit("unhandled block kind: %s" % k)

    size = doc.save(out, page=("A4", "portrait"), margins_cm=MARGIN_CM,
                    footer_text=META["title"] + " \u2014 PDEF / ECR / ECO")
    print("DOCX   : %s" % out)
    print("figures: %d, each an editable shape group" % figures)
    print("images : %d embedded (originals, unmodified)" % len(doc._images))
    print("size   : %.0f KB" % (size / 1024.0))
    return 0


if __name__ == "__main__":
    sys.exit(main())
