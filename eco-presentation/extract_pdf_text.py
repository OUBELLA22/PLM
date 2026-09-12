# -*- coding: utf-8 -*-
"""Extract text (and the image inventory) from a PDF, standard library only.

Walks the page tree, resolves each page's fonts and their ToUnicode CMaps, then
replays the text-showing operators of the page content stream. Prints one section
per page, followed by the image XObjects that page references - which is what lets
screenshots be matched to the paragraph they illustrate.

Usage: python3 extract_pdf_text.py <file.pdf> [--images-only]
"""
import re
import sys
import zlib

PDF = sys.argv[1] if len(sys.argv) > 1 else ""
data = open(PDF, "rb").read()
offsets = {int(m.group(1)): m.end() for m in re.finditer(rb"(\d+)\s+(\d+)\s+obj\b", data)}


def raw_obj(n):
    if n not in offsets:
        return b"", None
    start = offsets[n]
    end = data.find(b"endobj", start)
    seg = data[start:end]
    i = seg.find(b"<<")
    if i < 0:
        return seg, None
    depth, j = 0, i
    while j < len(seg):
        if seg[j:j + 2] == b"<<":
            depth += 1
            j += 2
        elif seg[j:j + 2] == b">>":
            depth -= 1
            j += 2
            if depth == 0:
                break
        else:
            j += 1
    head = seg[i:j]
    s = seg.find(b"stream", j)
    if s == -1 or s - j > 40:
        return head, None
    s += 6
    if seg[s:s + 2] == b"\r\n":
        s += 2
    elif seg[s:s + 1] in (b"\n", b"\r"):
        s += 1
    e = seg.find(b"endstream", s)
    return head, seg[s:e]


def inflate(blob):
    if blob is None:
        return None
    try:
        return zlib.decompress(blob)
    except zlib.error:
        try:
            return zlib.decompressobj().decompress(blob)
        except zlib.error:
            return None


def refs(head, key):
    m = re.search(key + rb"\s*\[([^\]]*)\]", head)
    if m:
        return [int(x) for x in re.findall(rb"(\d+)\s+\d+\s+R", m.group(1))]
    m = re.search(key + rb"\s+(\d+)\s+\d+\s+R", head)
    return [int(m.group(1))] if m else []


def parse_cmap(txt):
    cmap = {}
    for blk in re.findall(rb"beginbfchar(.*?)endbfchar", txt, re.S):
        for src, dst in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", blk):
            cmap[int(src, 16)] = "".join(chr(int(dst[i:i + 4], 16)) for i in range(0, len(dst), 4)
                                         if len(dst[i:i + 4]) == 4)
    for blk in re.findall(rb"beginbfrange(.*?)endbfrange", txt, re.S):
        for lo, hi, dst in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", blk):
            a, b, d = int(lo, 16), int(hi, 16), int(dst, 16)
            for k in range(a, min(b, a + 4096) + 1):
                cmap[k] = chr(d + k - a)
    return cmap


_cm_cache = {}


def font_cmap(fobj):
    if fobj in _cm_cache:
        return _cm_cache[fobj]
    head, _ = raw_obj(fobj)
    cm, wide = {}, b"Identity-H" in head or b"/Type0" in head
    for tu in refs(head, rb"/ToUnicode"):
        _, st = raw_obj(tu)
        txt = inflate(st) or st or b""
        cm.update(parse_cmap(txt))
    if not cm:                                   # composite font: follow the descendant
        for d in refs(head, rb"/DescendantFonts"):
            dh, _ = raw_obj(d)
            for tu in refs(dh, rb"/ToUnicode"):
                _, st = raw_obj(tu)
                cm.update(parse_cmap(inflate(st) or st or b""))
    _cm_cache[fobj] = (cm, wide)
    return _cm_cache[fobj]


def unescape(s):
    out, i = bytearray(), 0
    octal = [bytes([d]) for d in b"01234567"]
    while i < len(s):
        c = s[i:i + 1]
        if c == b"\\":
            nxt = s[i + 1:i + 2]
            simple = {b"n": 10, b"r": 13, b"t": 9, b"b": 8, b"f": 12, b"(": 40, b")": 41, b"\\": 92}
            if nxt in simple:
                out.append(simple[nxt])
                i += 2
            elif nxt in octal:
                k = 0
                while k < 3 and s[i + 1 + k:i + 2 + k] in octal:
                    k += 1
                out.append(int(s[i + 1:i + 1 + k], 8) & 255)
                i += 1 + k
            elif nxt:
                out += nxt
                i += 2
            else:
                i += 1
        else:
            out += c
            i += 1
    return bytes(out)


def decode(raw, font):
    cm, wide = font if font else ({}, False)
    if wide or (cm and max(cm) > 255 and len(raw) % 2 == 0):
        codes = [raw[i] * 256 + raw[i + 1] for i in range(0, len(raw) - 1, 2)]
        if cm and sum(1 for c in codes if c in cm) >= len(codes) * 0.5:
            return "".join(cm.get(c, "") for c in codes)
    if cm and sum(1 for c in raw if c in cm) >= max(1, len(raw)) * 0.5:
        return "".join(cm.get(c, "") for c in raw)
    return raw.decode("cp1252", "replace")


TOKEN = re.compile(rb"/(\w+)\s+[-\d.]+\s+Tf|\((?:[^()\\]|\\.)*\)|<[0-9A-Fa-f\s]+>|TJ|Tj|'|\"|Td|TD|T\*|Tm|ET")


def page_text(content, fonts):
    out, cur, line = [], None, []
    for m in TOKEN.finditer(content):
        t = m.group(0)
        if t.endswith(b"Tf"):
            cur = fonts.get(m.group(1).decode())
        elif t.startswith(b"("):
            line.append(decode(unescape(t[1:-1]), cur))
        elif t.startswith(b"<"):
            h = re.sub(rb"\s", b"", t[1:-1])
            if len(h) % 2:
                h += b"0"
            line.append(decode(bytes.fromhex(h.decode()), cur))
        elif t in (b"Td", b"TD", b"T*", b"Tm", b"ET"):
            if line:
                out.append("".join(line).strip())
                line = []
    if line:
        out.append("".join(line).strip())
    return [x for x in out if x]


# ---------------------------------------------------------------- page tree, in order
root_pages = [n for n in offsets if b"/Type /Pages" in raw_obj(n)[0]]
order = []
if root_pages:
    order = refs(raw_obj(root_pages[0])[0], rb"/Kids")
pages = [n for n in order if b"/Type /Page" in raw_obj(n)[0]]
if not pages:
    pages = sorted(n for n in offsets if b"/Type /Page" in raw_obj(n)[0]
                   and b"/Type /Pages" not in raw_obj(n)[0])

images_only = "--images-only" in sys.argv
out = []
for pno, pn in enumerate(pages, 1):
    head, _ = raw_obj(pn)
    fonts, imgs = {}, []
    for rn in refs(head, rb"/Resources"):
        rh, _ = raw_obj(rn)
    else:
        rh = head if b"/Resources <<" in head else (raw_obj(refs(head, rb"/Resources")[0])[0]
                                                    if refs(head, rb"/Resources") else b"")
    for m in re.finditer(rb"/Font\s*<<(.*?)>>", rh, re.S):
        for name, fo in re.findall(rb"/(\w+)\s+(\d+)\s+\d+\s+R", m.group(1)):
            fonts[name.decode()] = font_cmap(int(fo))
    for m in re.finditer(rb"/XObject\s*<<(.*?)>>", rh, re.S):
        for name, xo in re.findall(rb"/(\w+)\s+(\d+)\s+\d+\s+R", m.group(1)):
            xh, _ = raw_obj(int(xo))
            if b"/Image" in xh:
                w = re.search(rb"/Width\s+(\d+)", xh)
                h = re.search(rb"/Height\s+(\d+)", xh)
                imgs.append("obj%s(%sx%s)" % (xo.decode(),
                                              w.group(1).decode() if w else "?",
                                              h.group(1).decode() if h else "?"))
    txt = []
    if not images_only:
        for cn in refs(head, rb"/Contents"):
            _, st = raw_obj(cn)
            dec = inflate(st) or st or b""
            txt += page_text(dec, fonts)
    out.append("\n===== PAGE %d (obj %d) =====" % (pno, pn))
    if imgs:
        out.append("[images: %s]" % ", ".join(imgs))
    out += txt

sys.stdout.write("\n".join(out) + "\n")
sys.stderr.write("[%d pages]\n" % len(pages))
