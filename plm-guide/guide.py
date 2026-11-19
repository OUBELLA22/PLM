# -*- coding: utf-8 -*-
"""Layout engine and the "futuristic" annotation layer for the PLM guide.

Design rule that drives this whole module: a platform screenshot is never
modified. The original PNG/JPEG bytes are embedded untouched (see pdfwriter.Image)
and everything that makes the figure look enhanced - glow frames, HUD brackets,
highlight rings, numbered markers, leader lines, labels - is drawn as PDF vector
art *on top of* the picture. So the PLM UI itself is pixel-identical to the
source guide; only the annotation layer is new.

Blocks measure themselves before they draw, which lets `Renderer.flow` paginate
without ever overflowing a page.
"""
from pdfwriter import Canvas, text_width


def hx(s):
    return tuple(int(s[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


T = {
    "bg": hx("0B1220"), "bg2": hx("081020"), "panel": hx("16233A"), "panel2": hx("0E1829"),
    "line": hx("25344F"), "line2": hx("1B2740"), "tx": hx("E2EAF6"), "mut": hx("93A8C6"),
    "dim": hx("65799A"), "acc": hx("4F8DFF"), "acc2": hx("22D3EE"), "ok": hx("34D399"),
    "warn": hx("FBBF24"), "dan": hx("F87171"), "white": (1.0, 1.0, 1.0), "cap": hx("8FA5C4"),
    "card": hx("18263E"), "head": hx("0D1829"),
}
TONE = {"acc": T["acc"], "acc2": T["acc2"], "ok": T["ok"], "warn": T["warn"],
        "dan": T["dan"], "": T["acc2"]}
TONE_BG = {"acc": hx("111E36"), "acc2": hx("0C2230"), "ok": hx("0F2418"),
           "warn": hx("241D0F"), "dan": hx("2A1418"), "": hx("111E36")}

# Inline run styles -> (font, colour key)
STYLE = {
    "": ("F1", "tx"), "b": ("F2", "white"), "i": ("F3", "mut"), "bi": ("F4", "white"),
    "m": ("F1", "mut"), "acc": ("F2", "acc2"), "ok": ("F2", "ok"),
    "warn": ("F2", "warn"), "dan": ("F2", "dan"), "ui": ("F2", "acc2"),
    "dim": ("F1", "dim"),
}

PAGE_W, PAGE_H = 842.0, 595.28
ML, MR, MT, MB = 52.0, 52.0, 48.0, 42.0
CW = PAGE_W - ML - MR               # 738 pt usable width
TEXT_W = 660.0                      # comfortable measure for prose


# --------------------------------------------------------------- rich text
def _runs(item):
    """Normalise a block's text into a list of (text, style) runs."""
    if isinstance(item, str):
        return [(item, "")]
    if isinstance(item, tuple):
        return [item]
    return list(item)


def wrap(runs, width, size):
    """Greedy word wrap across styled runs. Returns a list of lines of runs."""
    words = []                       # (text, style, width, is_space)
    for text, style in runs:
        font = STYLE.get(style, STYLE[""])[0]
        bold = font in ("F2", "F4")
        parts = text.split(" ")
        for i, p in enumerate(parts):
            if i:
                words.append((" ", style, text_width(" ", size, bold), True))
            if p:
                words.append((p, style, text_width(p, size, bold), False))
    lines, cur, cur_w = [], [], 0.0
    for text, style, w, is_space in words:
        if is_space and not cur:
            continue
        if cur_w + w > width and not is_space and cur:
            while cur and cur[-1][0] == " ":
                cur_w -= cur.pop()[2]
            lines.append(cur)
            cur, cur_w = [], 0.0
        cur.append((text, style, w))
        cur_w += w
    if cur:
        while cur and cur[-1][0] == " ":
            cur.pop()
        lines.append(cur)
    return lines or [[]]


# ------------------------------------------------------------------ renderer
class Renderer:
    """Paginating block renderer for a dark-themed A4-landscape guide."""

    def __init__(self, doc, meta):
        self.doc = doc
        self.meta = meta
        self.c = None
        self.y = 0.0
        self.page_no = 0
        self.total = None
        self.chapter = ""
        self.boxes = []              # layout log, used by verify_pdf.py

    # ---- page chrome -----------------------------------------------------
    def _log(self, kind, x, y, w, h):
        self.boxes.append((self.page_no, kind, round(x, 1), round(y, 1),
                           round(w, 1), round(h, 1)))

    def new_page(self, chapter=None, plain=False):
        if self.c is not None:
            self._log("page-end", ML, 0.0, CW, self.y)
            self._footer()
            self.doc.page(self.c)
        self.c = Canvas(self.doc)
        self.page_no += 1
        if chapter is not None:
            self.chapter = chapter
        c = self.c
        # background + a very faint technical grid (page furniture only,
        # never over a screenshot)
        c.fill_color(T["bg"])
        c.rect(0, 0, PAGE_W, PAGE_H)
        c.save()
        c.set_alpha(0.5)
        c.fill_gradient_rect(0, 0, PAGE_W, 230, hx("12203A"), T["bg"])
        c.restore()
        c.save()
        c.set_alpha(0.055)
        c.stroke_color(T["acc"])
        c.line_width(0.4)
        for gx in range(0, int(PAGE_W), 42):
            c.line(gx, 0, gx, PAGE_H)
        for gy in range(0, int(PAGE_H), 42):
            c.line(0, gy, PAGE_W, gy)
        c.restore()
        # left accent rail
        c.save()
        c.set_alpha(0.85)
        c.fill_gradient_rect(0, 0, 3.0, PAGE_H, T["acc"], T["acc2"])
        c.restore()
        self.y = MT
        if not plain:
            self._header()

    def _header(self):
        c = self.c
        c.text(ML, self.y, self.meta["short"].upper(), 6.8, "F2", T["dim"], char_space=1.6)
        if self.chapter:
            c.text(ML, self.y, self.chapter.upper(), 6.8, "F2", T["acc2"],
                   align="r", width=CW, char_space=1.6)
        self.y += 7.0
        c.save()
        c.set_alpha(0.5)
        c.stroke_color(T["line"])
        c.line_width(0.6)
        c.line(ML, self.y, ML + CW, self.y)
        c.restore()
        self.y += 20.0

    def _footer(self):
        c = self.c
        fy = PAGE_H - MB + 10
        c.save()
        c.set_alpha(0.45)
        c.stroke_color(T["line"])
        c.line_width(0.6)
        c.line(ML, fy - 10, ML + CW, fy - 10)
        c.restore()
        c.text(ML, fy, self.meta["footer"], 6.6, "F1", T["dim"])
        label = ("%d / %d" % (self.page_no, self.total)) if self.total else "%d" % self.page_no
        c.text(ML, fy, label, 7.2, "F2", T["mut"], align="r", width=CW)

    def finish(self):
        if self.c is not None:
            self._log("page-end", ML, 0.0, CW, self.y)
            self._footer()
            self.doc.page(self.c)
            self.c = None

    # ---- pagination ------------------------------------------------------
    @property
    def avail(self):
        return PAGE_H - MB - 14 - self.y

    def need(self, h):
        """Start a new page when `h` will not fit in the current column."""
        if h > self.avail:
            self.new_page()
            return True
        return False

    def flow(self, blocks):
        """Place blocks in order, keeping a heading on the same page as the
        block it introduces so no heading is orphaned at a page foot."""
        for i, b in enumerate(blocks):
            if b["kind"] in ("h2", "h3") and i + 1 < len(blocks):
                nxt = blocks[i + 1]
                if nxt["kind"] not in ("cover", "chapter"):
                    own = getattr(self, "b_" + b["kind"])(b, measure=True)
                    nh = getattr(self, "b_" + nxt["kind"])(nxt, measure=True)
                    if own + nh + nxt.get("gap", 0.0) > self.avail:
                        self.new_page()
            self.block(b)

    def block(self, b):
        kind = b["kind"]
        fn = getattr(self, "b_" + kind)
        if kind in ("cover", "chapter"):
            fn(b)
            return
        gap = b.get("gap", 0.0)
        self.y += gap
        h = fn(b, measure=True)
        keep = b.get("keep_with", 0)
        if self.need(h + keep):
            pass
        fn(b, measure=False)

    # ---- primitives ------------------------------------------------------
    def _draw_lines(self, x, y, lines, size, leading, indent=0.0):
        c = self.c
        for i, line in enumerate(lines):
            ly = y + leading * i + size * 0.78
            lx = x + (indent if i else 0.0)
            for text, style, w in line:
                font, ck = STYLE.get(style, STYLE[""])
                c.text(lx, ly, text, size, font, T[ck])
                lx += w
        return leading * len(lines)

    def _tag(self, x, y, text, tone="acc2", size=6.8):
        """Small uppercase pill used as a section eyebrow / figure label."""
        c = self.c
        tw = text_width(text.upper(), size, True) + 14
        h = size + 7
        c.save()
        c.set_alpha(0.16)
        c.fill_color(TONE[tone])
        c.rrect(x, y, tw, h, h / 2.0, "f")
        c.restore()
        c.save()
        c.set_alpha(0.55)
        c.stroke_color(TONE[tone])
        c.line_width(0.5)
        c.rrect(x, y, tw, h, h / 2.0, "S")
        c.restore()
        c.text(x, y + h * 0.5 + size * 0.36, text.upper(), size, "F2", TONE[tone],
               align="c", width=tw)
        return tw, h

    # ---- blocks ----------------------------------------------------------
    def b_cover(self, b):
        self.new_page(chapter="", plain=True)
        c = self.c
        c.fill_color(T["bg2"])
        c.rect(0, 0, PAGE_W, PAGE_H)
        c.save()
        c.set_alpha(0.75)
        c.fill_gradient_rect(0, 0, PAGE_W, PAGE_H, hx("16304F"), T["bg2"])
        c.restore()
        # HUD grid
        c.save()
        c.set_alpha(0.07)
        c.stroke_color(T["acc2"])
        c.line_width(0.5)
        for gx in range(0, int(PAGE_W), 30):
            c.line(gx, 0, gx, PAGE_H)
        for gy in range(0, int(PAGE_H), 30):
            c.line(0, gy, PAGE_W, gy)
        c.restore()
        # concentric arcs, bottom-right
        c.save()
        for i, r in enumerate((300, 240, 180, 120)):
            c.set_alpha(0.10 - i * 0.015)
            c.stroke_color(T["acc2"])
            c.line_width(1.2)
            c.circle(PAGE_W - 40, PAGE_H - 20, r, "S")
        c.restore()
        x = 70.0
        c.save()
        c.set_alpha(0.9)
        c.fill_gradient_rect(x, 150, 120, 4, T["acc"], T["acc2"], vertical=False, r=2)
        c.restore()
        c.text(x, 208, b["kicker"].upper(), 9.0, "F2", T["acc2"], char_space=3.4)
        c.text(x, 268, b["title"], 44, "F2", T["white"])
        c.text(x, 304, b["title2"], 44, "F2", T["acc2"])
        c.text(x, 342, b["subtitle"], 15.5, "F1", hx("BCD0EC"))
        lines = wrap(_runs(b["tagline"]), 560, 10.5)
        self._draw_lines(x, 364, lines, 10.5, 15.5)
        # spec strip
        sy = 452.0
        c.save()
        c.set_alpha(0.5)
        c.fill_color(T["panel"])
        c.rrect(x, sy, 640, 56, 8, "f")
        c.restore()
        c.save()
        c.set_alpha(0.5)
        c.stroke_color(T["line"])
        c.line_width(0.7)
        c.rrect(x, sy, 640, 56, 8, "S")
        c.restore()
        cols = b["specs"]
        colw = 640.0 / len(cols)
        for i, (k, v) in enumerate(cols):
            cx = x + i * colw + 16
            c.text(cx, sy + 21, k.upper(), 6.4, "F2", T["dim"], char_space=1.3)
            c.text(cx, sy + 40, v, 10.0, "F2", T["tx"])
            if i:
                c.save()
                c.set_alpha(0.5)
                c.stroke_color(T["line"])
                c.line_width(0.6)
                c.line(x + i * colw, sy + 12, x + i * colw, sy + 44)
                c.restore()
        c.text(x, 548, b["meta"], 7.4, "F1", T["dim"])

    def b_chapter(self, b):
        self.new_page(chapter=b["title"], plain=True)
        c = self.c
        c.save()
        c.set_alpha(0.6)
        c.fill_gradient_rect(0, 0, PAGE_W, PAGE_H, hx("13273F"), T["bg"])
        c.restore()
        c.save()
        c.set_alpha(0.07)
        c.stroke_color(T["acc"])
        c.line_width(0.5)
        for gx in range(0, int(PAGE_W), 36):
            c.line(gx, 0, gx, PAGE_H)
        for gy in range(0, int(PAGE_H), 36):
            c.line(0, gy, PAGE_W, gy)
        c.restore()
        c.save()
        c.set_alpha(0.85)
        c.fill_gradient_rect(0, 0, 3.0, PAGE_H, T["acc"], T["acc2"])
        c.restore()
        # oversized chapter numeral
        c.save()
        c.set_alpha(0.13)
        c.text(PAGE_W - 300, 430, b["num"], 260, "F2", T["acc"])
        c.restore()
        x = 70.0
        c.text(x, 196, b["eyebrow"].upper(), 8.4, "F2", T["acc2"], char_space=3.0)
        c.save()
        c.set_alpha(0.9)
        c.fill_gradient_rect(x, 212, 90, 3.5, T["acc"], T["acc2"], vertical=False, r=2)
        c.restore()
        c.text(x, 272, b["title"], 34, "F2", T["white"])
        lines = wrap(_runs(b["lead"]), 520, 11.5)
        self._draw_lines(x, 300, lines, 11.5, 17.5)
        y = 300 + 17.5 * len(lines) + 24
        for item in b.get("covers", []):
            c.save()
            c.set_alpha(0.9)
            c.fill_color(T["acc2"])
            c.circle(x + 3, y + 4.5, 2.2, "f")
            c.restore()
            c.text(x + 14, y + 8, item, 10.0, "F1", T["mut"])
            y += 17.0
        self._footer()
        self.doc.page(self.c)
        self.c = None
        self.new_page(chapter=b["title"])

    def b_h2(self, b, measure=False):
        size = 17.0
        lines = wrap(_runs(b["title"]), CW, size)
        h = 15.0 + size * 1.15 * len(lines) + 12.0
        if b.get("eyebrow"):
            h += 13.0
        if measure:
            return h
        c = self.c
        y = self.y
        if b.get("eyebrow"):
            c.text(ML, y + 7, b["eyebrow"].upper(), 6.8, "F2", T["acc2"], char_space=1.8)
            y += 13.0
        for i, line in enumerate(lines):
            lx = ML
            for text, style, w in line:
                font, ck = STYLE.get(style, STYLE[""])
                c.text(lx, y + size * 0.82 + i * size * 1.15, text, size, "F2", T["white"])
                lx += w
        y += size * 1.15 * len(lines) + 5.0
        c.save()
        c.set_alpha(0.95)
        c.fill_gradient_rect(ML, y, 54, 3.0, T["acc"], T["acc2"], vertical=False, r=1.5)
        c.restore()
        self.y += h
        return h

    def b_h3(self, b, measure=False):
        size = 11.5
        h = 12.0 + size * 1.2 + 4.0
        if measure:
            return h
        c = self.c
        y = self.y + 12.0
        c.save()
        c.set_alpha(0.9)
        c.fill_color(T["acc2"])
        c.rrect(ML, y + 1.5, 2.6, size * 0.95, 1.3, "f")
        c.restore()
        c.text(ML + 10, y + size * 0.85, b["title"], size, "F2", T["white"])
        self.y += h
        return h

    def b_para(self, b, measure=False):
        size = b.get("size", 9.8)
        width = b.get("width", TEXT_W)
        lead = size * 1.52
        lines = wrap(_runs(b["text"]), width, size)
        h = lead * len(lines) + 7.0
        if measure:
            return h
        self._draw_lines(ML, self.y, lines, size, lead)
        self.y += h
        return h

    def b_bullets(self, b, measure=False):
        size = b.get("size", 9.6)
        lead = size * 1.5
        cols = b.get("columns", 1)
        width = b.get("width", TEXT_W)
        gap = 26.0
        cw = (width - gap * (cols - 1)) / cols if cols > 1 else width
        ind = 15.0
        per = []
        for item in b["bullets"]:
            lines = wrap(_runs(item), cw - ind, size)
            per.append(lines)
        if cols == 1:
            h = sum(lead * len(l) + 6.0 for l in per) + 4.0
        else:
            half = (len(per) + 1) // 2
            h1 = sum(lead * len(l) + 6.0 for l in per[:half])
            h2 = sum(lead * len(l) + 6.0 for l in per[half:])
            h = max(h1, h2) + 4.0
        if measure:
            return h
        c = self.c
        half = (len(per) + 1) // 2
        groups = [per] if cols == 1 else [per[:half], per[half:]]
        for ci, group in enumerate(groups):
            x = ML + ci * (cw + gap)
            y = self.y + 2.0
            for lines in group:
                c.save()
                c.set_alpha(0.95)
                c.fill_gradient_rect(x, y + size * 0.34, 5.0, 5.0, T["acc"], T["acc2"],
                                     vertical=False, r=1.2)
                c.restore()
                self._draw_lines(x + ind, y, lines, size, lead)
                y += lead * len(lines) + 6.0
        self.y += h
        return h

    def b_steps(self, b, measure=False):
        size = b.get("size", 9.8)
        lead = size * 1.5
        width = b.get("width", TEXT_W)
        ind = 26.0
        per = [wrap(_runs(s), width - ind, size) for s in b["steps"]]
        h = sum(lead * len(l) + 9.0 for l in per) + 4.0
        if measure:
            return h
        c = self.c
        y = self.y + 2.0
        for i, lines in enumerate(per, 1):
            r = 7.6
            cx, cy = ML + r, y + size * 0.62
            c.save()
            c.set_alpha(0.22)
            c.fill_color(T["acc"])
            c.circle(cx, cy, r + 2.0, "f")
            c.restore()
            c.save()
            c.fill_gradient_rect(cx - r, cy - r, r * 2, r * 2, T["acc"], hx("2563EB"))
            c.restore()
            c.save()
            c.clip_rect(cx - r - 1, cy - r - 1, r * 2 + 2, r * 2 + 2)
            c.fill_color(T["acc"])
            c.circle(cx, cy, r, "f")
            c.restore()
            c.save()
            c.set_alpha(0.75)
            c.stroke_color(T["acc2"])
            c.line_width(0.8)
            c.circle(cx, cy, r, "S")
            c.restore()
            c.text(cx - r, cy + 3.0, "%d" % i, 8.2, "F2", T["white"], align="c", width=r * 2)
            self._draw_lines(ML + ind, y, lines, size, lead)
            y += lead * len(lines) + 9.0
        self.y += h
        return h

    def b_callout(self, b, measure=False):
        size = b.get("size", 9.4)
        tone = b.get("tone", "")
        pad = 12.0
        width = b.get("width", CW)
        label = b.get("label")
        inner = width - pad * 2 - 8
        lines = wrap(_runs(b["text"]), inner, size)
        lead = size * 1.48
        h = lead * len(lines) + pad * 2 + (12.0 if label else 0.0)
        if measure:
            return h + 8.0
        c = self.c
        y = self.y
        c.save()
        c.set_alpha(0.92)
        c.fill_color(TONE_BG[tone])
        c.rrect(ML, y, width, h, 7, "f")
        c.restore()
        c.save()
        c.set_alpha(0.45)
        c.stroke_color(TONE[tone])
        c.line_width(0.7)
        c.rrect(ML, y, width, h, 7, "S")
        c.restore()
        c.save()
        c.clip_rrect(ML, y, width, h, 7)
        c.fill_color(TONE[tone])
        c.rect(ML, y, 3.2, h)
        c.restore()
        ty = y + pad
        if label:
            c.text(ML + pad + 6, ty + size * 0.7, label.upper(), 6.8, "F2", TONE[tone],
                   char_space=1.6)
            ty += 12.0
        self._draw_lines(ML + pad + 6, ty, lines, size, lead)
        self.y += h + 8.0
        return h + 8.0

    def b_table(self, b, measure=False):
        size = b.get("size", 8.8)
        width = b.get("width", CW)
        colw = [width * f for f in b["colw"]]
        pad = 8.0
        lead = size * 1.42
        hh = 20.0
        def cell_runs(ci, cell):
            runs = _runs(cell)
            if ci == 0 and b.get("bold_first", True):
                runs = [(t, s or "b") for t, s in runs]
            return runs

        rows_h = []
        for row in b["rows"]:
            n = 1
            for i, cell in enumerate(row):
                n = max(n, len(wrap(cell_runs(i, cell), colw[i] - pad * 2, size)))
            rows_h.append(max(lead * n + 11.0, 23.0))
        h = hh + sum(rows_h) + 6.0
        if measure:
            return h
        c = self.c
        y = self.y
        # header
        c.save()
        c.set_alpha(0.95)
        c.fill_color(T["head"])
        c.rrect(ML, y, width, hh, 4, "f")
        c.restore()
        x = ML
        for i, head in enumerate(b["head"]):
            c.text(x + pad, y + 13.5, head.upper(), 6.9, "F2", T["acc2"], char_space=1.4)
            x += colw[i]
        c.save()
        c.set_alpha(0.6)
        c.stroke_color(T["acc2"])
        c.line_width(0.7)
        c.line(ML, y + hh, ML + width, y + hh)
        c.restore()
        y += hh
        for ri, row in enumerate(b["rows"]):
            rh = rows_h[ri]
            if ri % 2 == 0:
                c.save()
                c.set_alpha(0.5)
                c.fill_color(T["panel"])
                c.rect(ML, y, width, rh)
                c.restore()
            x = ML
            for ci, cell in enumerate(row):
                lines = wrap(cell_runs(ci, cell), colw[ci] - pad * 2, size)
                self._draw_lines(x + pad, y + 5.0, lines, size, lead)
                x += colw[ci]
            c.save()
            c.set_alpha(0.35)
            c.stroke_color(T["line"])
            c.line_width(0.5)
            c.line(ML, y + rh, ML + width, y + rh)
            c.restore()
            y += rh
        self.y += h
        return h

    def b_cards(self, b, measure=False):
        cards = b["cards"]
        n = len(cards)
        gap = 14.0
        width = b.get("width", CW)
        cwid = (width - gap * (n - 1)) / n
        pad = 12.0
        size = 8.8
        lead = size * 1.42
        heights = []
        for cd in cards:
            hh = pad + 11.0 + 6.0
            tl = wrap(_runs(cd["title"]), cwid - pad * 2, 11.5)
            hh += 11.5 * 1.2 * len(tl) + 7.0
            for ln in cd["lines"]:
                hh += lead * len(wrap(_runs(ln), cwid - pad * 2 - 10, size)) + 4.5
            heights.append(hh + pad)
        h = max(heights)
        if measure:
            return h + 6.0
        c = self.c
        for i, cd in enumerate(cards):
            x = ML + i * (cwid + gap)
            y = self.y
            tone = cd.get("tone", "acc")
            c.save()
            c.set_alpha(0.95)
            c.fill_color(T["card"])
            c.rrect(x, y, cwid, h, 7, "f")
            c.restore()
            c.save()
            c.set_alpha(0.55)
            c.stroke_color(T["line"])
            c.line_width(0.7)
            c.rrect(x, y, cwid, h, 7, "S")
            c.restore()
            c.save()
            c.clip_rrect(x, y, cwid, h, 7)
            c.fill_gradient_rect(x, y, cwid, 3.0, TONE[tone], T["acc"], vertical=False)
            c.restore()
            ty = y + pad + 2
            c.text(x + pad, ty + 7, cd["tag"].upper(), 6.8, "F2", TONE[tone], char_space=1.6)
            ty += 15.0
            tl = wrap(_runs(cd["title"]), cwid - pad * 2, 11.5)
            for j, line in enumerate(tl):
                lx = x + pad
                for text, style, w in line:
                    c.text(lx, ty + 11.5 * 0.82 + j * 11.5 * 1.2, text, 11.5, "F2", T["white"])
                    lx += w
            ty += 11.5 * 1.2 * len(tl) + 7.0
            for ln in cd["lines"]:
                lines = wrap(_runs(ln), cwid - pad * 2 - 10, size)
                c.save()
                c.set_alpha(0.9)
                c.fill_color(TONE[tone])
                c.circle(x + pad + 2.4, ty + size * 0.55, 1.9, "f")
                c.restore()
                self._draw_lines(x + pad + 10, ty, lines, size, lead)
                ty += lead * len(lines) + 4.5
        self.y += h + 6.0
        return h + 6.0

    def b_flow(self, b, measure=False):
        rows = b["rows"]
        h = 0.0
        for r in rows:
            h += 14.0 + 30.0 + 12.0
        if measure:
            return h
        c = self.c
        y = self.y
        for r in rows:
            c.text(ML, y + 7, r["label"].upper(), 6.8, "F2", T["mut"], char_space=1.6)
            y += 14.0
            chips = r["chips"]
            # measure chips, then lay them out with chevrons between
            sizes = [text_width(ch, 8.8, True) + 20 for ch in chips]
            arrow = 16.0
            total = sum(sizes) + arrow * (len(chips) - 1)
            scale = min(1.0, CW / total)
            x = ML
            for i, ch in enumerate(chips):
                cwid = sizes[i] * scale
                if i:
                    ax = x + (arrow * scale) * 0.5
                    c.save()
                    c.set_alpha(0.9)
                    c.stroke_color(T["acc2"])
                    c.line_width(1.3)
                    c.line_cap(1)
                    c.polyline([(ax - 2.5, y + 10), (ax + 2.5, y + 15), (ax - 2.5, y + 20)])
                    c.restore()
                    x += arrow * scale
                hot = r.get("style") == "accent"
                c.save()
                c.set_alpha(0.95)
                if hot:
                    c.fill_gradient_rect(x, y, cwid, 30, hx("1B3A6B"), hx("12293F"), r=15)
                else:
                    c.fill_color(T["card"])
                    c.rrect(x, y, cwid, 30, 15, "f")
                c.restore()
                c.save()
                c.set_alpha(0.6)
                c.stroke_color(hx("2F5F9E") if hot else T["line"])
                c.line_width(0.7)
                c.rrect(x, y, cwid, 30, 15, "S")
                c.restore()
                c.text(x, y + 19.5, ch, 8.8, "F2", T["white"] if hot else T["tx"],
                       align="c", width=cwid)
                x += cwid
            y += 30.0 + 12.0
        self.y += h
        return h

    def b_glossary(self, b, measure=False):
        pairs = b["pairs"]
        size = 8.8
        lead = size * 1.4
        gap = 30.0
        cols = 2
        cw = (CW - gap) / cols
        keyw = b.get("keyw", 112.0)
        half = (len(pairs) + 1) // 2
        groups = [pairs[:half], pairs[half:]]
        hs = []
        for g in groups:
            hh = 0.0
            for k, v in g:
                n = max(len(wrap(_runs(v), cw - keyw - 8, size)),
                        len(wrap(_runs(k), keyw - 6, size)))
                hh += lead * n + 7.0
            hs.append(hh)
        h = max(hs) + 4.0
        if measure:
            return h
        c = self.c
        for gi, g in enumerate(groups):
            x = ML + gi * (cw + gap)
            y = self.y + 2.0
            for k, v in g:
                kl = wrap(_runs([(k, "acc")]), keyw - 6, size)
                vl = wrap(_runs(v), cw - keyw - 8, size)
                self._draw_lines(x, y, kl, size, lead)
                self._draw_lines(x + keyw, y, vl, size, lead)
                n = max(len(kl), len(vl))
                y += lead * n + 7.0
                c.save()
                c.set_alpha(0.3)
                c.stroke_color(T["line"])
                c.line_width(0.5)
                c.line(x, y - 4.0, x + cw, y - 4.0)
                c.restore()
        self.y += h
        return h

    def b_divider(self, b, measure=False):
        h = b.get("h", 14.0)
        if measure:
            return h
        c = self.c
        c.save()
        c.set_alpha(0.4)
        c.stroke_color(T["line"])
        c.line_width(0.6)
        c.line(ML, self.y + h / 2, ML + CW, self.y + h / 2)
        c.restore()
        self.y += h
        return h

    def b_space(self, b, measure=False):
        h = b.get("h", 10.0)
        if not measure:
            self.y += h
        return h

    # ---- the annotated figure -------------------------------------------
    def _figure_geom(self, b):
        """Resolve a figure's geometry once, so measure and draw always agree.

        The panel is fitted to the height a fresh page can offer, and the image
        scale is derived from whatever space the legend and caption leave. That
        is what keeps a figure from running off the bottom of the page.
        """
        im = self.doc.image(b["image"], b["path"])
        width = b.get("width", CW)
        marks = b.get("marks", [])
        legend = [m for m in marks if m.get("note") or m.get("label")]
        legend_pos = b.get("legend", "right" if legend else "none")
        if not legend:
            legend_pos = "none"
        pad, cap_size = 13.0, 7.8
        label_h = 16.0 if b.get("label") else 0.0

        cap_lines = wrap(_runs(b["caption"]), width - pad * 2, cap_size) if b.get("caption") else []
        cap_h = cap_size * 1.4 * len(cap_lines) + 8.0 if cap_lines else 0.0

        # height a figure may occupy on a page that carries the running header
        budget = PAGE_H - MB - 14.0 - (MT + 27.0) - 10.0

        if legend_pos == "right":
            lw = b.get("legend_w", 212.0)
            img_area_w = width - pad * 2 - lw - 16.0
            cols, item_w = 1, lw
        elif legend_pos == "below":
            lw = width - pad * 2
            img_area_w = lw
            cols = b.get("legend_cols", min(len(legend), 3))
            item_w = (lw - 14.0 * (cols - 1)) / cols
        else:
            lw, img_area_w, cols, item_w = 0.0, width - pad * 2, 1, 0.0

        # Shrink the legend type a notch at a time until the whole figure fits.
        for lsize in (8.4, 7.8, 7.2, 6.8):
            lead = lsize * 1.42
            items = []
            for m in legend:
                ind = 19.0 if m.get("n") else 0.0
                ih = 12.0
                if m.get("label"):           # a long label may wrap too
                    ll = wrap(_runs([(m["label"], "b")]), item_w - ind - 4, lsize + 0.2)
                    ih += max(0.0, (len(ll) - 1) * (lsize + 0.2) * 1.3)
                if m.get("note"):
                    ih += lead * len(wrap(_runs(m["note"]), item_w - ind - 4, lsize)) + 6.0
                else:
                    ih += 4.0
                items.append(ih)
            if cols > 1:
                target = sum(items) / float(cols)
                chunks, cur, acc = [], [], 0.0
                for i, ih in enumerate(items):
                    cur.append(i)
                    acc += ih
                    if acc >= target and len(chunks) < cols - 1:
                        chunks.append(cur)
                        cur, acc = [], 0.0
                chunks.append(cur)
                leg_h = max(sum(items[i] for i in ch) for ch in chunks if ch)
            else:
                chunks = [list(range(len(items)))]
                leg_h = sum(items)

            fixed = pad * 2 + label_h + cap_h
            if legend_pos == "below":
                img_h_room = budget - fixed - leg_h - 10.0
            else:
                img_h_room = budget - fixed
            img_h_room = max(40.0, img_h_room)

            scap = b.get("scale_cap", 0.92 if im.w < 420 else 0.66)
            s = min(img_area_w / im.w, b.get("max_h", 300.0) / im.h,
                    img_h_room / im.h, scap)
            dw, dh = im.w * s, im.h * s
            body_h = dh + 10.0 + leg_h if legend_pos == "below" else max(dh, leg_h)
            panel_h = fixed + body_h
            if panel_h <= budget:
                break

        return {
            "im": im, "width": width, "marks": marks, "legend": legend,
            "legend_pos": legend_pos, "pad": pad, "cap_size": cap_size,
            "cap_lines": cap_lines, "cap_h": cap_h, "label_h": label_h,
            "lw": lw, "img_area_w": img_area_w, "cols": cols, "item_w": item_w,
            "lsize": lsize, "lead": lead, "items": items, "chunks": chunks,
            "leg_h": leg_h, "s": s, "dw": dw, "dh": dh, "body_h": body_h,
            "panel_h": panel_h,
        }

    def b_figure(self, b, measure=False):
        """A screenshot inside a HUD panel, with vector highlights on top.

        The picture bytes are embedded untouched; every ring, marker, label and
        leader line below is vector art drawn over it.
        """
        g = self._figure_geom(b)
        h = g["panel_h"] + 10.0
        if measure:
            return h

        name = b["image"]
        im, width, pad = g["im"], g["width"], g["pad"]
        marks, legend, legend_pos = g["marks"], g["legend"], g["legend_pos"]
        img_area_w, lw = g["img_area_w"], g["lw"]
        s, dw, dh = g["s"], g["dw"], g["dh"]
        leg_h, body_h, panel_h = g["leg_h"], g["body_h"], g["panel_h"]
        cap_lines, cap_h, cap_size = g["cap_lines"], g["cap_h"], g["cap_size"]
        label_h, lead = g["label_h"], g["lead"]

        c = self.c
        y = self.y
        px, py = ML, y

        # ---------- panel: gradient, border, outer glow, HUD brackets
        c.save()
        c.set_alpha(0.5)
        c.stroke_color(T["acc"])
        c.line_width(3.0)
        c.rrect(px - 1.2, py - 1.2, width + 2.4, panel_h + 2.4, 9, "S")
        c.restore()
        c.fill_gradient_rect(px, py, width, panel_h, T["panel"], T["panel2"], r=8)
        c.save()
        c.set_alpha(0.75)
        c.stroke_color(T["line"])
        c.line_width(0.8)
        c.rrect(px, py, width, panel_h, 8, "S")
        c.restore()
        self._brackets(px, py, width, panel_h, b.get("tone", "acc2"))

        ty = py + pad
        if b.get("label"):
            self._tag(px + pad, ty - 2, b["label"], b.get("tone", "acc2"))
            ty += label_h

        # ---------- the screenshot, on a white mat with a neon glow
        ix = px + pad + (img_area_w - dw) / 2.0
        iy = ty + (body_h - dh) / 2.0 if legend_pos != "below" else ty
        mat = 2.6
        for off, a in ((5.0, 0.10), (3.2, 0.18), (1.7, 0.34)):
            c.save()
            c.set_alpha(a)
            c.stroke_color(TONE[b.get("tone", "acc2")])
            c.line_width(1.6)
            c.rrect(ix - mat - off, iy - mat - off, dw + (mat + off) * 2,
                    dh + (mat + off) * 2, 5, "S")
            c.restore()
        c.fill_color(T["white"])
        c.rrect(ix - mat, iy - mat, dw + mat * 2, dh + mat * 2, 3, "f")
        c.image(name, ix, iy, dw, dh)
        self._log("fig-img", ix, iy, dw, dh)

        # ---------- highlights + markers, in screenshot pixel space
        def to_page(bx, by, bw, bh):
            return ix + bx * s, iy + by * s, bw * s, bh * s

        for m in marks:
            tone = m.get("tone", b.get("tone", "acc2"))
            col = TONE[tone]
            if m.get("box"):
                hx_, hy_, hw_, hh_ = to_page(*m["box"])
                hx_, hy_ = hx_ - 1.5, hy_ - 1.5
                hw_, hh_ = hw_ + 3.0, hh_ + 3.0
                if m.get("fill", True):
                    c.save()
                    c.set_alpha(0.14)
                    c.fill_color(col)
                    c.rrect(hx_, hy_, hw_, hh_, 3, "f")
                    c.restore()
                for off, a, lwd in ((2.6, 0.16, 2.2), (1.3, 0.30, 1.8)):
                    c.save()
                    c.set_alpha(a)
                    c.stroke_color(col)
                    c.line_width(lwd)
                    c.rrect(hx_ - off, hy_ - off, hw_ + off * 2, hh_ + off * 2, 3.5, "S")
                    c.restore()
                c.save()
                c.set_alpha(0.95)
                c.stroke_color(col)
                c.line_width(1.3)
                c.rrect(hx_, hy_, hw_, hh_, 3, "S")
                c.restore()
                anchor = self._marker_anchor(m.get("mpos", "tl"), hx_, hy_, hw_, hh_)
            elif m.get("at"):
                ax, ay = ix + m["at"][0] * s, iy + m["at"][1] * s
                anchor = (ax, ay)
            else:
                continue
            if m.get("n"):
                self._marker(anchor[0], anchor[1], str(m["n"]), tone)

        # ---------- legend, laid out in the columns the geometry pass chose
        if legend:
            lsize, item_w, chunks = g["lsize"], g["item_w"], g["chunks"]
            if legend_pos == "below":
                lx0, ly0 = px + pad, iy + dh + 12.0
            else:
                lx0 = px + pad + img_area_w + 16.0
                ly0 = ty + max(0.0, (body_h - leg_h) / 2.0)
            for ci, chunk in enumerate(chunks):
                lx = lx0 + ci * (item_w + 14.0)
                ly = ly0
                for idx in chunk:
                    m = legend[idx]
                    tone = m.get("tone", b.get("tone", "acc2"))
                    if m.get("n"):
                        self._marker(lx + 7.0, ly + 5.5, str(m["n"]), tone, r=6.6, fs=7.2)
                        tx, ind = lx + 19.0, 19.0
                    else:
                        tx, ind = lx, 0.0
                    if m.get("label"):
                        ll = wrap(_runs([(m["label"], "b")]), item_w - ind - 4, lsize + 0.2)
                        self._draw_lines(tx, ly - 1.0, ll, lsize + 0.2, (lsize + 0.2) * 1.3)
                        extra = max(0.0, (len(ll) - 1) * (lsize + 0.2) * 1.3)
                    else:
                        extra = 0.0
                    ly += 12.0 + extra
                    if m.get("note"):
                        nl = wrap(_runs(m["note"]), item_w - ind - 4, lsize)
                        self._draw_lines(tx, ly - 1.0, nl, lsize, lead)
                        ly += lead * len(nl) + 6.0
                    else:
                        ly += 4.0

        # ---------- caption
        if cap_lines:
            cy = py + panel_h - cap_h + 2.0
            c.save()
            c.set_alpha(0.35)
            c.stroke_color(T["line"])
            c.line_width(0.5)
            c.line(px + pad, cy - 3.0, px + width - pad, cy - 3.0)
            c.restore()
            self._draw_lines(px + pad, cy, cap_lines, cap_size, cap_size * 1.4)

        self._log("fig-panel", px, py, width, panel_h)
        self.y += h
        return h

    @staticmethod
    def _marker_anchor(mpos, x, y, w, h):
        return {
            "tl": (x, y), "tr": (x + w, y), "bl": (x, y + h), "br": (x + w, y + h),
            "l": (x, y + h / 2), "r": (x + w, y + h / 2),
            "t": (x + w / 2, y), "b": (x + w / 2, y + h),
        }.get(mpos, (x, y))

    def _marker(self, cx, cy, label, tone="acc2", r=7.8, fs=8.0):
        """A numbered disc: outer halo, solid core, neon ring, white numeral."""
        c = self.c
        col = TONE[tone]
        c.save()
        c.set_alpha(0.28)
        c.fill_color(col)
        c.circle(cx, cy, r + 2.6, "f")
        c.restore()
        c.fill_color(hx("0B1220"))
        c.circle(cx, cy, r, "f")
        c.save()
        c.set_alpha(0.9)
        c.fill_color(col)
        c.circle(cx, cy, r - 1.4, "f")
        c.restore()
        c.save()
        c.set_alpha(0.95)
        c.stroke_color(T["white"])
        c.line_width(0.7)
        c.circle(cx, cy, r, "S")
        c.restore()
        dark = tone in ("warn", "acc2", "ok")
        c.text(cx - r, cy + fs * 0.36, label, fs, "F2",
               hx("08121F") if dark else T["white"], align="c", width=r * 2)

    def _brackets(self, x, y, w, h, tone="acc2"):
        """HUD corner brackets around a panel."""
        c = self.c
        col = TONE[tone]
        L, inset = 16.0, 5.0
        c.save()
        c.set_alpha(0.8)
        c.stroke_color(col)
        c.line_width(1.5)
        c.line_cap(0)
        for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
            cx = x + inset if sx > 0 else x + w - inset
            cy = y + inset if sy > 0 else y + h - inset
            c.polyline([(cx + sx * L, cy), (cx, cy), (cx, cy + sy * L)])
        c.restore()
