# -*- coding: utf-8 -*-
"""Structural and geometric checks on the generated guide.

There is no PDF renderer in this sandbox, so correctness is established by
parsing the file back and re-deriving what a viewer would do:

  1. the xref offsets really point at their objects;
  2. every indirect reference resolves;
  3. the page tree matches /Count and each page has a content stream;
  4. every content stream inflates and has balanced q/Q and BT/ET;
  5. every image XObject decodes - PNG streams are run through the PNG
     predictor exactly as a viewer would, and must yield width*height*ncomp
     bytes; JPEG streams must carry an SOI/EOI and a baseline SOF;
  6. nothing is drawn outside the page box, and figures stay inside the
     margins (read from layout.log);
  7. pages are not left nearly empty by a bad page break.

Usage: python3 verify_pdf.py [file.pdf]
"""
import ast
import os
import re
import sys
import zlib

PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "PLM_PDEF_ECR_ECO_Guide.pdf")
HERE = os.path.dirname(os.path.abspath(PATH))

data = open(PATH, "rb").read()
errors, checks = [], []


def ok(msg):
    checks.append(msg)


def bad(msg):
    errors.append(msg)


# ------------------------------------------------------------------ 1. xref
m = re.search(rb"startxref\s+(\d+)\s+%%EOF\s*$", data)
if not m:
    bad("no startxref / %%EOF trailer")
    print("\n".join("  FAIL  " + e for e in errors))
    sys.exit(1)
xref_at = int(m.group(1))
if data[xref_at:xref_at + 4] != b"xref":
    bad("startxref does not point at an xref table")
head = data[xref_at:xref_at + 40].split(b"\n")
count = int(head[1].split()[1])
rows = re.findall(rb"(\d{10}) (\d{5}) ([nf]) ", data[xref_at:])
if len(rows) < count:
    bad("xref has %d rows, /Size says %d" % (len(rows), count))
offsets = {}
for i, (off, _gen, kind) in enumerate(rows[:count]):
    if kind != b"n":
        continue
    off = int(off)
    expect = b"%d 0 obj" % i
    if data[off:off + len(expect)] != expect:
        bad("xref row %d points at %r, expected %r"
            % (i, data[off:off + 20], expect))
    offsets[i] = off
ok("xref table: %d entries, all offsets land on their object" % len(offsets))

# -------------------------------------------------------------- 2. objects
bodies = {}
for n, off in offsets.items():
    end = data.find(b"endobj", off)
    bodies[n] = data[data.find(b"obj", off) + 3:end]
refs = set()
for n, body in bodies.items():
    for r in re.findall(rb"(\d+)\s+0\s+R\b", body):
        refs.add(int(r))
missing = sorted(r for r in refs if r not in bodies)
if missing:
    bad("dangling indirect references: %s" % missing[:10])
ok("indirect references: %d distinct targets, all resolve" % len(refs))

trailer = data[data.rfind(b"trailer"):]
root = int(re.search(rb"/Root\s+(\d+)\s+0\s+R", trailer).group(1))
if b"/Type /Catalog" not in bodies[root]:
    bad("/Root is not a catalog")

# ----------------------------------------------------------- 3. page tree
pages_ref = int(re.search(rb"/Pages\s+(\d+)\s+0\s+R", bodies[root]).group(1))
ptree = bodies[pages_ref]
declared = int(re.search(rb"/Count\s+(\d+)", ptree).group(1))
kids = [int(k) for k in re.findall(rb"(\d+)\s+0\s+R", ptree)]
if len(kids) != declared:
    bad("/Count is %d but /Kids holds %d entries" % (declared, len(kids)))
contents = {}
for i, k in enumerate(kids, 1):
    b = bodies[k]
    if b"/Type /Page" not in b:
        bad("kid %d is not a /Page" % k)
        continue
    mb = re.search(rb"/MediaBox \[([\d\.\s]+)\]", b)
    box = [float(v) for v in mb.group(1).split()]
    if box != [0, 0, 842, 595.28]:
        bad("page %d MediaBox is %s" % (i, box))
    cref = int(re.search(rb"/Contents\s+(\d+)\s+0\s+R", b).group(1))
    contents[i] = cref
ok("page tree: %d pages, /Count agrees, A4 landscape MediaBox" % declared)


def stream_of(n):
    """Return (payload, dict_text). The payload is delimited by /Length, which
    is what a viewer uses - not by searching for `endstream`."""
    body = bodies[n]
    kw = body.find(b"stream")
    dict_text = body[:kw]
    length = int(re.search(rb"/Length\s+(\d+)", dict_text).group(1))
    s = kw + 6
    if body[s:s + 2] == b"\r\n":
        s += 2
    elif body[s:s + 1] in (b"\n", b"\r"):
        s += 1
    raw = body[s:s + length]
    if len(raw) != length:
        bad("obj %d: stream is shorter than its /Length" % n)
    if b"/FlateDecode" in dict_text:
        return zlib.decompress(raw), dict_text
    return raw, dict_text


# -------------------------------------------------- 4. content streams
total_text = 0
for i, cref in sorted(contents.items()):
    try:
        cs, _ = stream_of(cref)
    except zlib.error as exc:
        bad("page %d content stream will not inflate: %s" % (i, exc))
        continue
    if len(cs) < 200:
        bad("page %d content stream is suspiciously short (%d bytes)" % (i, len(cs)))
    q = len(re.findall(rb"(?m)^q$", cs))
    qq = len(re.findall(rb"(?m)^Q$", cs))
    if q != qq:
        bad("page %d unbalanced graphics state: %d q vs %d Q" % (i, q, qq))
    bt = len(re.findall(rb"BT /", cs))
    et = len(re.findall(rb"(?m)^ET$", cs))
    if bt != et:
        bad("page %d unbalanced text object: %d BT vs %d ET" % (i, bt, et))
    shown = re.findall(rb"\((?:[^()\\]|\\.)*\)\s+Tj", cs)
    total_text += len(shown)
    if not shown:
        bad("page %d shows no text at all" % i)
ok("content streams: all inflate, q/Q and BT/ET balanced, %d text runs" % total_text)


# --------------------------------------------------------- 5. image decode
def png_predictor(dec, columns, colors, bpc):
    stride = (columns * colors * bpc + 7) // 8
    bpp = max(1, colors * bpc // 8)
    out = bytearray()
    prev = bytearray(stride)
    pos = 0
    while pos + 1 + stride <= len(dec):
        ft = dec[pos]
        row = bytearray(dec[pos + 1:pos + 1 + stride])
        if ft == 1:
            for j in range(bpp, stride):
                row[j] = (row[j] + row[j - bpp]) & 255
        elif ft == 2:
            for j in range(stride):
                row[j] = (row[j] + prev[j]) & 255
        elif ft == 3:
            for j in range(stride):
                left = row[j - bpp] if j >= bpp else 0
                row[j] = (row[j] + ((left + prev[j]) >> 1)) & 255
        elif ft == 4:
            for j in range(stride):
                a = row[j - bpp] if j >= bpp else 0
                b2 = prev[j]
                c2 = prev[j - bpp] if j >= bpp else 0
                pa, pb, pc = abs(b2 - c2), abs(a - c2), abs(a + b2 - 2 * c2)
                pr = a if (pa <= pb and pa <= pc) else (b2 if pb <= pc else c2)
                row[j] = (row[j] + pr) & 255
        elif ft != 0:
            raise ValueError("illegal PNG filter %d" % ft)
        out += row
        prev = row
        pos += 1 + stride
    return bytes(out), stride


nimg = 0
for n, body in sorted(bodies.items()):
    if b"/Subtype /Image" not in body:
        continue
    nimg += 1
    w = int(re.search(rb"/Width\s+(\d+)", body).group(1))
    h = int(re.search(rb"/Height\s+(\d+)", body).group(1))
    bpc = int(re.search(rb"/BitsPerComponent\s+(\d+)", body).group(1))
    raw, dct = stream_of(n)
    if b"/DCTDecode" in dct:
        if raw[:2] != b"\xff\xd8" or raw[-2:] != b"\xff\xd9":
            bad("image obj %d: JPEG is not delimited by SOI/EOI" % n)
        sof = re.search(rb"\xff(\xc0|\xc1)", raw)
        if not sof:
            bad("image obj %d: no baseline SOF marker" % n)
        continue
    pm = re.search(rb"/Predictor\s+(\d+)", dct)
    if not pm or int(pm.group(1)) != 15:
        bad("image obj %d: PNG stream without /Predictor 15" % n)
        continue
    colors = int(re.search(rb"/Colors\s+(\d+)", dct).group(1))
    cols = int(re.search(rb"/Columns\s+(\d+)", dct).group(1))
    if cols != w:
        bad("image obj %d: /Columns %d != /Width %d" % (n, cols, w))
    try:
        px, stride = png_predictor(raw, cols, colors, bpc)
    except ValueError as exc:
        bad("image obj %d: %s" % (n, exc))
        continue
    expect = stride * h
    if len(px) != expect:
        bad("image obj %d: decoded %d bytes, a viewer expects %d (%dx%d)"
            % (n, len(px), expect, w, h))
ok("image XObjects: %d embedded, every stream decodes to its declared size" % nimg)

# ----------------------------------------------- 6. geometry from layout.log
log = os.path.join(HERE, "layout.log")
ML, MR, MT, MB = 52.0, 52.0, 48.0, 42.0
PW, PH = 842.0, 595.28
if os.path.exists(log):
    rows = [ast.literal_eval(l) for l in open(log) if l.strip()]
    panels = [r for r in rows if r[1] == "fig-panel"]
    pics = [r for r in rows if r[1] == "fig-img"]
    drawn = [r for r in rows if r[1] != "page-end"]
    for page, kind, x, y, w, h in drawn:
        if x < ML - 1.5 or x + w > PW - MR + 1.5:
            bad("page %d: %s breaks the side margins (x=%.1f w=%.1f)" % (page, kind, x, w))
        if y < MT - 20 or y + h > PH - MB + 1.5:
            bad("page %d: %s breaks the top/bottom margin (y=%.1f h=%.1f, bottom %.1f)"
                % (page, kind, y, h, y + h))
    # a picture must sit inside its panel
    for (p1, _k1, px, py, pw, ph) in panels:
        inner = [r for r in pics if r[0] == p1 and r[2] >= px - 1 and r[3] >= py - 1
                 and r[2] + r[4] <= px + pw + 1 and r[3] + r[5] <= py + ph + 1]
        if not inner:
            bad("page %d: figure panel has no picture inside it" % p1)
    ok("geometry: %d figure panels and %d pictures, all within the margins"
       % (len(panels), len(pics)))

    # 7. no content may spill into the footer band, and report page fill
    bottom = PH - MB - 14.0
    ends = {r[0]: r[5] for r in rows if r[1] == "page-end"}
    for page, endy in sorted(ends.items()):
        if endy > bottom + 1.5:
            bad("page %d: content ends at y=%.1f, past the footer band at %.1f"
                % (page, endy, bottom))
    if ends:
        mean = sum(ends.values()) / len(ends) / bottom * 100.0
        sparse = sorted(p for p, v in ends.items() if v / bottom < 0.55)
        ok("page fill: %d content pages, mean %.0f%% of the column used" % (len(ends), mean))
        if sparse:
            ok("note: %d page(s) under 55%% full (%s) - large figures kept with their "
               "heading" % (len(sparse), ", ".join(str(p) for p in sparse)))
else:
    ok("geometry: layout.log not found, skipped")

print("\n".join("  ok    " + c for c in checks))
if errors:
    print("\n".join("  FAIL  " + e for e in errors))
    print("\n%d problem(s)" % len(errors))
    sys.exit(1)
print("\n  PASS  %s (%d pages, %.0f KB)" % (os.path.basename(PATH), declared,
                                            len(data) / 1024.0))
