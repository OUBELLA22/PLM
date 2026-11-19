# -*- coding: utf-8 -*-
"""A small PDF writer built on the standard library only.

Why hand-rolled: this sandbox has no reportlab / PIL / PyMuPDF / headless browser,
so the guide is emitted as raw PDF syntax.

What it supports, which is all the guide needs:
  * A4 landscape pages with a shared resource dictionary.
  * Base-14 Helvetica (regular / bold / oblique) with real AFM widths, so text can
    be measured and wrapped. No font embedding, so the file stays small.
  * PNG and JPEG images passed through *without re-encoding*:
      - PNG  -> /FlateDecode with /Predictor 15 (a PNG IDAT already is a zlib
                stream of filter-prefixed scanlines, which is exactly what the
                PNG predictor expects).
      - JPEG -> /DCTDecode, the compressed bytes copied verbatim.
    Screenshots therefore keep their original pixels, bit for bit.
  * Vector drawing, constant alpha via /ExtGState, and axial gradients via
    shading patterns - enough to paint the "futuristic" overlays on top of the
    untouched screenshots.

Coordinates: every public method takes top-down page coordinates (y grows
downward, origin at the top-left corner) and converts to PDF's bottom-up space
internally.
"""
import struct
import zlib

# --------------------------------------------------------------------- metrics
# Helvetica and Helvetica-Bold advance widths (1/1000 em) for codes 32..126,
# straight from the Adobe AFM tables.
_ASCII_REG = [
    278, 278, 355, 556, 556, 889, 667, 191, 333, 333, 389, 584, 278, 333, 278, 278,
    556, 556, 556, 556, 556, 556, 556, 556, 556, 556, 278, 278, 584, 584, 584, 556,
    1015, 667, 667, 722, 722, 667, 611, 778, 722, 278, 500, 667, 556, 833, 722, 778,
    667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 278, 278, 278, 469, 556,
    333, 556, 556, 500, 556, 556, 278, 556, 556, 222, 222, 500, 222, 833, 556, 556,
    556, 556, 333, 500, 278, 556, 500, 722, 500, 500, 500, 334, 260, 334, 584,
]
_ASCII_BOLD = [
    278, 333, 474, 556, 556, 889, 722, 238, 333, 333, 389, 584, 278, 333, 278, 278,
    556, 556, 556, 556, 556, 556, 556, 556, 556, 556, 333, 333, 584, 584, 584, 611,
    975, 722, 722, 722, 722, 667, 611, 778, 722, 278, 556, 722, 611, 833, 722, 778,
    667, 778, 722, 667, 611, 722, 667, 944, 667, 667, 611, 333, 278, 333, 584, 556,
    333, 556, 611, 556, 611, 556, 333, 611, 611, 278, 278, 556, 278, 889, 611, 611,
    611, 611, 389, 556, 333, 611, 556, 778, 556, 556, 500, 389, 280, 389, 584,
]

# Accented / ligature codes in WinAnsi, resolved to the base letter they widen.
_ACCENT_BASE = {
    192: "A", 193: "A", 194: "A", 195: "A", 196: "A", 197: "A", 199: "C",
    200: "E", 201: "E", 202: "E", 203: "E", 208: "D", 209: "N",
    210: "O", 211: "O", 212: "O", 213: "O", 214: "O", 216: "O",
    217: "U", 218: "U", 219: "U", 220: "U", 221: "Y", 222: "P",
    224: "a", 225: "a", 226: "a", 227: "a", 228: "a", 229: "a", 231: "c",
    232: "e", 233: "e", 234: "e", 235: "e", 240: "o", 241: "n",
    242: "o", 243: "o", 244: "o", 245: "o", 246: "o", 248: "o",
    249: "u", 250: "u", 251: "u", 252: "u", 253: "y", 254: "p", 255: "y",
    138: "S", 140: "O", 142: "Z", 154: "s", 156: "o", 158: "z", 159: "Y", 131: "f",
}
# Punctuation, symbols and the dotted i-family, which do not follow a base letter.
_SPECIAL = {
    128: 556, 130: 222, 132: 333, 133: 1000, 134: 556, 135: 556, 136: 333,
    137: 1000, 139: 333, 145: 222, 146: 222, 147: 333, 148: 333, 149: 350,
    150: 556, 151: 1000, 152: 333, 153: 1000, 155: 333, 160: 278, 161: 333,
    162: 556, 163: 556, 164: 556, 165: 556, 166: 260, 167: 556, 168: 333,
    169: 737, 170: 370, 171: 556, 172: 584, 173: 333, 174: 737, 175: 333,
    176: 400, 177: 584, 178: 333, 179: 333, 180: 333, 181: 556, 182: 537,
    183: 278, 184: 333, 185: 333, 186: 365, 187: 556, 188: 834, 189: 834,
    190: 834, 191: 611, 198: 1000, 204: 278, 205: 278, 206: 278, 207: 278,
    215: 584, 223: 611, 230: 889, 236: 278, 237: 278, 238: 278, 239: 278,
    247: 584,
}


def _build(ascii_widths):
    w = {c: ascii_widths[c - 32] for c in range(32, 127)}
    for code, ch in _ACCENT_BASE.items():
        w[code] = ascii_widths[ord(ch) - 32]
    w.update(_SPECIAL)
    return w


W_REG = _build(_ASCII_REG)
W_BOLD = _build(_ASCII_BOLD)

# Unicode the sources use that WinAnsi cannot encode -> a safe stand-in.
# Arrows and ticks are never set as text; they are drawn as vector paths.
_FOLD = {
    "\u2192": "\u203a", "\u2190": "\u2039", "\u21d2": "\u203a", "\u2794": "\u203a",
    "\u2022": "\u2022", "\u25aa": "\u2022", "\u25b8": "\u203a", "\u25b6": "\u203a",
    "\u2713": "+", "\u2717": "x", "\u2714": "+", "\u00d7": "x",
    "\u2026": "\u2026", "\u2013": "\u2013", "\u2014": "\u2014",
    "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
    "\u00a0": " ", "\u2009": " ", "\u202f": " ", "\u200b": "",
    "\u2265": ">=", "\u2264": "<=", "\u2260": "!=", "\u00ab": "\u00ab", "\u00bb": "\u00bb",
}


def fold(s):
    """Replace characters WinAnsi cannot represent with close equivalents."""
    out = []
    for ch in s:
        if ch in _FOLD:
            out.append(_FOLD[ch])
            continue
        try:
            ch.encode("cp1252")
            out.append(ch)
        except UnicodeEncodeError:
            out.append("?")
    return "".join(out)


def text_width(s, size, bold=False):
    """Advance width of `s` at `size` points."""
    table = W_BOLD if bold else W_REG
    total = 0
    for ch in fold(s):
        total += table.get(ord(ch), 556)
    return total * size / 1000.0


def _pdf_string(s):
    """Escape a string into a PDF literal, encoded WinAnsi."""
    raw = fold(s).encode("cp1252", "replace")
    out = bytearray()
    for b in raw:
        if b in (0x28, 0x29, 0x5C):          # ( ) \
            out += b"\\" + bytes([b])
        elif b == 0x0D:
            out += b"\\r"
        elif b == 0x0A:
            out += b"\\n"
        elif b < 32 or b > 126:
            out += ("\\%03o" % b).encode()
        else:
            out.append(b)
    return b"(" + bytes(out) + b")"


def _num(v):
    """Compact fixed-point number for content streams."""
    if abs(v - round(v)) < 1e-6:
        return b"%d" % int(round(v))
    return ("%.3f" % v).rstrip("0").rstrip(".").encode()


# ------------------------------------------------------------------ image read
class Image:
    """An image prepared for embedding, with its pixel size and PDF stream parts."""

    def __init__(self, name, path):
        self.name = name
        self.path = path
        blob = open(path, "rb").read()
        if blob[:8] == b"\x89PNG\r\n\x1a\n":
            self._from_png(blob)
        elif blob[:2] == b"\xff\xd8":
            self._from_jpeg(blob)
        else:
            raise ValueError("unsupported image: %s" % path)

    # PNG: hand the IDAT bytes to PDF unchanged and let the PNG predictor undo
    # the row filters. No pixel ever passes through Python.
    def _from_png(self, blob):
        w, h, bpc, ctype, comp, filt, interlace = struct.unpack(">IIBBBBB", blob[16:29])
        if interlace:
            raise ValueError("interlaced PNG not supported: %s" % self.path)
        if comp or filt:
            raise ValueError("unexpected PNG compression/filter: %s" % self.path)
        idat, plte, trns = bytearray(), None, None
        i = 8
        while i < len(blob):
            ln = struct.unpack(">I", blob[i:i + 4])[0]
            tag = blob[i + 4:i + 8]
            payload = blob[i + 8:i + 8 + ln]
            if tag == b"IDAT":
                idat += payload
            elif tag == b"PLTE":
                plte = payload
            elif tag == b"tRNS":
                trns = payload
            elif tag == b"IEND":
                break
            i += 12 + ln
        if trns is not None:
            raise ValueError("PNG transparency not supported: %s" % self.path)
        ncomp = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ctype]
        if ctype in (4, 6):
            raise ValueError("PNG alpha channel not supported: %s" % self.path)
        if ctype == 3:
            if plte is None:
                raise ValueError("indexed PNG without PLTE: %s" % self.path)
            hi = len(plte) // 3 - 1
            cs = b"[/Indexed /DeviceRGB %d <%s>]" % (hi, plte.hex().encode())
        else:
            cs = b"/DeviceGray" if ctype == 0 else b"/DeviceRGB"
        self.w, self.h, self.bpc, self.cs = w, h, bpc, cs
        self.data = bytes(idat)
        self.extra = (b"/Filter /FlateDecode /DecodeParms "
                      b"<< /Predictor 15 /Colors %d /BitsPerComponent %d /Columns %d >>"
                      % (ncomp, bpc, w))

    # JPEG: copy the entropy-coded bytes straight into a /DCTDecode stream.
    def _from_jpeg(self, blob):
        i, w, h, ncomp, prog = 2, None, None, 3, False
        while i < len(blob) - 1:
            if blob[i] != 0xFF:
                i += 1
                continue
            marker = blob[i + 1]
            if marker in (0xD8, 0xD9, 0x01) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            seglen = struct.unpack(">H", blob[i + 2:i + 4])[0]
            if marker in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                          0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                h, w = struct.unpack(">HH", blob[i + 5:i + 9])
                ncomp = blob[i + 9]
                prog = marker in (0xC2, 0xC6, 0xCA, 0xCE)
                break
            i += 2 + seglen
        if w is None:
            raise ValueError("no JPEG SOF marker: %s" % self.path)
        if prog:
            raise ValueError("progressive JPEG not supported by /DCTDecode: %s" % self.path)
        self.w, self.h, self.bpc = w, h, 8
        self.cs = {1: b"/DeviceGray", 3: b"/DeviceRGB", 4: b"/DeviceCMYK"}[ncomp]
        self.data = blob
        self.extra = b"/Filter /DCTDecode"

    def obj(self):
        return (b"<< /Type /XObject /Subtype /Image /Width %d /Height %d "
                b"/ColorSpace %s /BitsPerComponent %d %s /Length %d >>"
                % (self.w, self.h, self.cs, self.bpc, self.extra, len(self.data)))


# -------------------------------------------------------------------- document
class PDFDoc:
    """Collects pages and shared resources, then serialises the file."""

    def __init__(self, width=842.0, height=595.28, title="", author="", subject=""):
        self.W, self.H = width, height
        self.title, self.author, self.subject = title, author, subject
        self.pages = []                  # list of content-stream bytes
        self.images = {}                 # name -> Image
        self._alphas = {}                # alpha -> gs name
        self._grads = {}                 # key -> pattern name
        self._gradobjs = []

    # ---- resources
    def image(self, name, path):
        if name not in self.images:
            self.images[name] = Image(name, path)
        return self.images[name]

    def alpha(self, a):
        """Register a constant-alpha graphics state and return its resource name."""
        a = max(0.0, min(1.0, round(a, 3)))
        if a not in self._alphas:
            self._alphas[a] = "GA%d" % (len(self._alphas) + 1)
        return self._alphas[a]

    def gradient(self, x0, y0, x1, y1, c0, c1):
        """Register an axial gradient pattern in *PDF* coordinates."""
        key = (round(x0, 2), round(y0, 2), round(x1, 2), round(y1, 2), c0, c1)
        if key not in self._grads:
            name = "GR%d" % (len(self._grads) + 1)
            self._grads[key] = name
            self._gradobjs.append((name, key))
        return self._grads[key]

    def page(self, canvas):
        self.pages.append(canvas.data())

    # ---- serialise
    def save(self, path):
        objs = [None]                    # 1-based object table

        def add(body):
            objs.append(body)
            return len(objs) - 1          # objs[0] is the free entry

        def add_stream(dict_prefix, data, compress=True):
            if compress and b"/Filter" not in dict_prefix:
                data = zlib.compress(data, 9)
                dict_prefix = dict_prefix + b" /Filter /FlateDecode"
            body = (b"<< " + dict_prefix + b" /Length %d >>\nstream\n" % len(data)
                    + data + b"\nendstream")
            return add(body)

        font_objs = {
            "F1": add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica "
                      b"/Encoding /WinAnsiEncoding >>"),
            "F2": add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold "
                      b"/Encoding /WinAnsiEncoding >>"),
            "F3": add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Oblique "
                      b"/Encoding /WinAnsiEncoding >>"),
            "F4": add(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-BoldOblique "
                      b"/Encoding /WinAnsiEncoding >>"),
        }
        img_objs = {}
        for name, im in self.images.items():
            dict_prefix = im.obj()[3:-3].strip()        # strip the << >> wrapper
            dict_prefix = dict_prefix.rsplit(b"/Length", 1)[0].strip()
            img_objs[name] = add_stream(dict_prefix, im.data, compress=False)

        gs_objs = {}
        for a, name in self._alphas.items():
            gs_objs[name] = add(b"<< /Type /ExtGState /ca %s /CA %s >>"
                                % (_num(a), _num(a)))

        pat_objs = {}
        for name, (x0, y0, x1, y1, c0, c1) in self._gradobjs:
            sh = add(b"<< /ShadingType 2 /ColorSpace /DeviceRGB "
                     b"/Coords [%s %s %s %s] /Extend [true true] "
                     b"/Function << /FunctionType 2 /Domain [0 1] /C0 [%s] /C1 [%s] /N 1 >> >>"
                     % (_num(x0), _num(y0), _num(x1), _num(y1),
                        b" ".join(_num(v) for v in c0),
                        b" ".join(_num(v) for v in c1)))
            pat_objs[name] = add(b"<< /Type /Pattern /PatternType 2 /Shading %d 0 R >>" % sh)

        res_parts = [b"/ProcSet [/PDF /Text /ImageB /ImageC]"]
        res_parts.append(b"/Font << " + b" ".join(
            b"/%s %d 0 R" % (k.encode(), v) for k, v in sorted(font_objs.items())) + b" >>")
        if img_objs:
            res_parts.append(b"/XObject << " + b" ".join(
                b"/%s %d 0 R" % (k.encode(), v) for k, v in sorted(img_objs.items())) + b" >>")
        if gs_objs:
            res_parts.append(b"/ExtGState << " + b" ".join(
                b"/%s %d 0 R" % (k.encode(), v) for k, v in sorted(gs_objs.items())) + b" >>")
        if pat_objs:
            res_parts.append(b"/Pattern << " + b" ".join(
                b"/%s %d 0 R" % (k.encode(), v) for k, v in sorted(pat_objs.items())) + b" >>")
        res = add(b"<< " + b" ".join(res_parts) + b" >>")

        # Each page costs two objects (content stream + page dict); the /Pages
        # node is added right after them, so its number can be predicted here
        # and used as /Parent while the pages are being created.
        pages_ref = len(objs) + len(self.pages) * 2
        page_refs = []
        for content in self.pages:
            cs = add_stream(b"", content)
            page_refs.append(add(b"<< /Type /Page /Parent %d 0 R /MediaBox [0 0 %s %s] "
                                 b"/Resources %d 0 R /Contents %d 0 R >>"
                                 % (pages_ref, _num(self.W), _num(self.H), res, cs)))
        pages_obj = add(b"<< /Type /Pages /Count %d /Kids [%s] >>"
                        % (len(page_refs), b" ".join(b"%d 0 R" % r for r in page_refs)))
        assert pages_obj == pages_ref, (pages_obj, pages_ref)
        catalog = add(b"<< /Type /Catalog /Pages %d 0 R /PageLayout /SinglePage >>" % pages_obj)
        info = add(b"<< /Title %s /Author %s /Subject %s /Creator (Kiro) /Producer (Kiro) >>"
                   % (_pdf_string(self.title), _pdf_string(self.author),
                      _pdf_string(self.subject)))

        out = bytearray(b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0] * (len(objs) + 1)
        for n in range(1, len(objs)):
            offsets[n] = len(out)
            out += b"%d 0 obj\n" % n + objs[n] + b"\nendobj\n"
        xref = len(out)
        out += b"xref\n0 %d\n" % len(objs)
        out += b"0000000000 65535 f \n"
        for n in range(1, len(objs)):
            out += b"%010d 00000 n \n" % offsets[n]
        out += (b"trailer\n<< /Size %d /Root %d 0 R /Info %d 0 R >>\nstartxref\n%d\n%%%%EOF\n"
                % (len(objs), catalog, info, xref))
        with open(path, "wb") as f:
            f.write(bytes(out))
        return len(out)


# ---------------------------------------------------------------------- canvas
class Canvas:
    """A page content stream. All y coordinates are top-down."""

    def __init__(self, doc):
        self.doc = doc
        self.ops = []
        self.H = doc.H
        self.W = doc.W

    def data(self):
        return b"\n".join(self.ops)

    def _y(self, y):
        return self.H - y

    def raw(self, op):
        self.ops.append(op if isinstance(op, bytes) else op.encode())

    # ---- state
    def save(self):
        self.raw(b"q")

    def restore(self):
        self.raw(b"Q")

    def set_alpha(self, a):
        self.raw(b"/%s gs" % self.doc.alpha(a).encode())

    def fill_color(self, rgb):
        self.raw(b"%s %s %s rg" % tuple(_num(c) for c in rgb))

    def stroke_color(self, rgb):
        self.raw(b"%s %s %s RG" % tuple(_num(c) for c in rgb))

    def line_width(self, w):
        self.raw(b"%s w" % _num(w))

    def dash(self, pattern=None, phase=0):
        if not pattern:
            self.raw(b"[] 0 d")
        else:
            self.raw(b"[%s] %s d" % (b" ".join(_num(p) for p in pattern), _num(phase)))

    def line_cap(self, style=0):
        self.raw(b"%d J" % style)

    # ---- paths
    def rect(self, x, y, w, h, op="f"):
        self.raw(b"%s %s %s %s re %s" % (_num(x), _num(self._y(y + h)),
                                         _num(w), _num(h), op.encode()))

    def rrect_path(self, x, y, w, h, r):
        """Append a rounded-rectangle subpath (no paint operator)."""
        r = max(0.0, min(r, w / 2.0, h / 2.0))
        k = r * 0.5523
        y0 = self._y(y + h)        # bottom in PDF space
        y1 = self._y(y)            # top in PDF space
        x0, x1 = x, x + w
        a = _num
        self.raw(b"%s %s m" % (a(x0 + r), a(y0)))
        self.raw(b"%s %s l" % (a(x1 - r), a(y0)))
        self.raw(b"%s %s %s %s %s %s c" % (a(x1 - r + k), a(y0), a(x1), a(y0 + r - k),
                                           a(x1), a(y0 + r)))
        self.raw(b"%s %s l" % (a(x1), a(y1 - r)))
        self.raw(b"%s %s %s %s %s %s c" % (a(x1), a(y1 - r + k), a(x1 - r + k), a(y1),
                                           a(x1 - r), a(y1)))
        self.raw(b"%s %s l" % (a(x0 + r), a(y1)))
        self.raw(b"%s %s %s %s %s %s c" % (a(x0 + r - k), a(y1), a(x0), a(y1 - r + k),
                                           a(x0), a(y1 - r)))
        self.raw(b"%s %s l" % (a(x0), a(y0 + r)))
        self.raw(b"%s %s %s %s %s %s c" % (a(x0), a(y0 + r - k), a(x0 + r - k), a(y0),
                                           a(x0 + r), a(y0)))
        self.raw(b"h")

    def rrect(self, x, y, w, h, r, op="f"):
        self.rrect_path(x, y, w, h, r)
        self.raw(op.encode())

    def circle_path(self, cx, cy, r):
        k = r * 0.5523
        y = self._y(cy)
        a = _num
        self.raw(b"%s %s m" % (a(cx - r), a(y)))
        self.raw(b"%s %s %s %s %s %s c" % (a(cx - r), a(y + k), a(cx - k), a(y + r), a(cx), a(y + r)))
        self.raw(b"%s %s %s %s %s %s c" % (a(cx + k), a(y + r), a(cx + r), a(y + k), a(cx + r), a(y)))
        self.raw(b"%s %s %s %s %s %s c" % (a(cx + r), a(y - k), a(cx + k), a(y - r), a(cx), a(y - r)))
        self.raw(b"%s %s %s %s %s %s c" % (a(cx - k), a(y - r), a(cx - r), a(y - k), a(cx - r), a(y)))
        self.raw(b"h")

    def circle(self, cx, cy, r, op="f"):
        self.circle_path(cx, cy, r)
        self.raw(op.encode())

    def line(self, x0, y0, x1, y1):
        self.raw(b"%s %s m %s %s l S" % (_num(x0), _num(self._y(y0)),
                                         _num(x1), _num(self._y(y1))))

    def polyline(self, pts, op="S"):
        for i, (px, py) in enumerate(pts):
            self.raw(b"%s %s %s" % (_num(px), _num(self._y(py)), b"m" if i == 0 else b"l"))
        self.raw(op.encode())

    def clip_rect(self, x, y, w, h):
        self.raw(b"%s %s %s %s re W n" % (_num(x), _num(self._y(y + h)), _num(w), _num(h)))

    def clip_rrect(self, x, y, w, h, r):
        self.rrect_path(x, y, w, h, r)
        self.raw(b"W n")

    # ---- gradients
    def fill_gradient_rect(self, x, y, w, h, c0, c1, vertical=True, r=0):
        """Fill a (optionally rounded) rect with an axial gradient."""
        if vertical:
            name = self.doc.gradient(x, self._y(y + h), x, self._y(y), c0, c1)
        else:
            name = self.doc.gradient(x, self._y(y), x + w, self._y(y), c0, c1)
        self.save()
        if r:
            self.clip_rrect(x, y, w, h, r)
        else:
            self.clip_rect(x, y, w, h)
        self.raw(b"/Pattern cs /%s scn" % name.encode())
        self.rect(x, y, w, h, "f")
        self.restore()

    # ---- text
    def text(self, x, y, s, size=10, font="F1", color=(1, 1, 1), align="l", width=None,
             char_space=0):
        """Draw one line. `y` is the text baseline. `align` needs `width` for c/r."""
        if not s:
            return 0.0
        bold = font in ("F2", "F4")
        tw = text_width(s, size, bold)
        if char_space:
            tw += char_space * max(0, len(fold(s)) - 1)
        if align == "c" and width is not None:
            x = x + (width - tw) / 2.0
        elif align == "r" and width is not None:
            x = x + width - tw
        self.fill_color(color)
        self.raw(b"BT /%s %s Tf" % (font.encode(), _num(size)))
        if char_space:
            self.raw(b"%s Tc" % _num(char_space))
        self.raw(b"1 0 0 1 %s %s Tm" % (_num(x), _num(self._y(y))))
        self.raw(_pdf_string(s) + b" Tj")
        if char_space:
            self.raw(b"0 Tc")
        self.raw(b"ET")
        return tw

    # ---- images
    def image(self, name, x, y, w, h):
        """Draw a registered image into the box (x, y, w, h), y top-down."""
        self.save()
        self.raw(b"%s 0 0 %s %s %s cm" % (_num(w), _num(h), _num(x), _num(self._y(y + h))))
        self.raw(b"/%s Do" % name.encode())
        self.restore()
