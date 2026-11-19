# -*- coding: utf-8 -*-
"""Build the PLM PDEF / ECR / ECO guide as a PDF.

Rendered twice: the first pass only counts pages so the footers can show
"n / total", the second pass is the one written to disk.

    python3 build_guide.py [output.pdf]
"""
import os
import sys

from content_guide import META, build
from guide import Renderer
from pdfwriter import PDFDoc

HERE = os.path.dirname(os.path.abspath(__file__))


def render(total=None):
    doc = PDFDoc(title=META["title"], author=META["author"], subject=META["subject"])
    r = Renderer(doc, META)
    r.total = total
    blocks = build()
    # the cover block opens the first page itself
    r.flow(blocks)
    r.finish()
    return doc, r


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        HERE, "PLM_PDEF_ECR_ECO_Guide.pdf")
    _, r1 = render()                       # pass 1: how many pages?
    doc, r2 = render(total=r1.page_no)
    if r2.page_no != r1.page_no:
        # pagination must be stable, otherwise the footers would lie
        raise SystemExit("unstable pagination: %d then %d" % (r1.page_no, r2.page_no))
    size = doc.save(out)
    figures = sum(1 for b in r2.boxes if b[1] == "fig-panel")
    print("PDF   : %s" % out)
    print("pages : %d" % r2.page_no)
    print("figures: %d annotated screenshots" % figures)
    print("images: %d embedded (originals, re-encoded: none)" % len(doc.images))
    print("size  : %.0f KB" % (size / 1024.0))
    with open(os.path.join(HERE, "layout.log"), "w") as f:
        for b in r2.boxes:
            f.write("%s\n" % (b,))
    return 0


if __name__ == "__main__":
    sys.exit(main())
