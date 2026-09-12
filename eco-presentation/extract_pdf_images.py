# -*- coding: utf-8 -*-
"""Extract image XObjects from a PDF with the standard library only.

Handles the two filters produced by Word -> PDF exports: DCTDecode (JPEG, written
as-is) and FlateDecode (raw samples, re-wrapped into a PNG). Indexed, DeviceRGB,
DeviceGray and CalRGB colour spaces are supported.
"""
import os
import re
import struct
import sys
import zlib

PDF = sys.argv[1] if len(sys.argv) > 1 else "/projects/sandbox/PLM/2 METHODOLOGY_Creating_a_Product_ECO.pdf"
OUTDIR = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "img", "raw")

data = open(PDF, "rb").read()
os.makedirs(OUTDIR, exist_ok=True)

OBJ = re.compile(rb"(\d+)\s+(\d+)\s+obj\b")
objects = {}
for m in OBJ.finditer(data):
    objects[int(m.group(1))] = m.end()


def dict_of(start):
    """Return (dict_text, stream_start) for the object body at `start`."""
    i = data.find(b"<<", start)
    if i < 0:
        return None, None
    depth, j = 0, i
    while j < len(data):
        if data[j:j + 2] == b"<<":
            depth += 1
            j += 2
        elif data[j:j + 2] == b">>":
            depth -= 1
            j += 2
            if depth == 0:
                break
        else:
            j += 1
    head = data[i:j]
    s = data.find(b"stream", j)
    if s != -1 and s - j < 40:
        s += 6
        if data[s:s + 2] == b"\r\n":
            s += 2
        elif data[s:s + 1] in (b"\n", b"\r"):
            s += 1
    else:
        s = None
    return head, s


def num(head, key, default=None):
    m = re.search(key.encode() + rb"\s+(\d+)", head)
    return int(m.group(1)) if m else default


def resolve(head, key):
    """Value of `key`, following one level of indirection."""
    m = re.search(key.encode() + rb"\s+(\d+)\s+\d+\s+R", head)
    if m:
        n = int(m.group(1))
        if n in objects:
            h2, s2 = dict_of(objects[n])
            if s2:  # stream object (e.g. an Indexed palette)
                end = data.find(b"endstream", s2)
                return h2, data[s2:end]
            # plain object: grab the token/array after "obj"
            start = objects[n]
            seg = data[start:start + 400]
            return seg, None
        return None, None
    m = re.search(key.encode() + rb"\s*(\[[^\]]*\]|/[A-Za-z0-9]+)", head)
    return (m.group(1) if m else None), None


def png(path, w, h, ncomp, raw, bpc=8, palette=None):
    if palette is not None:
        ctype = 3
    else:
        ctype = {1: 0, 3: 2, 4: 6}.get(ncomp)
        if ctype is None:
            return False
    stride = (w * ncomp * bpc + 7) // 8
    if len(raw) < stride * h:
        return False
    scan = bytearray()
    for y in range(h):
        scan.append(0)
        scan += raw[y * stride:(y + 1) * stride]

    def chunk(tag, payload):
        return (struct.pack(">I", len(payload)) + tag + payload
                + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF))

    out = [b"\x89PNG\r\n\x1a\n",
           chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, bpc, ctype, 0, 0, 0))]
    if palette is not None:
        out.append(chunk(b"PLTE", palette[:768]))
    out.append(chunk(b"IDAT", zlib.compress(bytes(scan), 9)))
    out.append(chunk(b"IEND", b""))
    open(path, "wb").write(b"".join(out))
    return True


found, skipped = [], []
for objnum in sorted(objects):
    head, sstart = dict_of(objects[objnum])
    if not head or sstart is None or b"/Image" not in head:
        continue
    if b"/Subtype" not in head or b"/Image" not in re.search(rb"/Subtype\s*/(\w+)", head).group(0):
        continue
    w, h = num(head, "/Width"), num(head, "/Height")
    if not w or not h or w * h < 6000:          # drop logos / decorative slivers
        skipped.append((objnum, w, h, "small"))
        continue
    end = data.find(b"endstream", sstart)
    raw = data[sstart:end]
    filt = re.findall(rb"/(DCTDecode|FlateDecode|JPXDecode|CCITTFaxDecode|LZWDecode|RunLengthDecode)", head)
    filt = [f.decode() for f in filt]
    bpc = num(head, "/BitsPerComponent", 8)

    if "DCTDecode" in filt:
        p = os.path.join(OUTDIR, "obj%04d_%dx%d.jpg" % (objnum, w, h))
        open(p, "wb").write(raw.rstrip(b"\r\n"))
        found.append((objnum, w, h, "jpg", os.path.getsize(p)))
        continue

    if filt == ["FlateDecode"]:
        try:
            dec = zlib.decompress(raw)
        except zlib.error:
            try:
                dec = zlib.decompressobj().decompress(raw)
            except zlib.error:
                skipped.append((objnum, w, h, "inflate failed"))
                continue
        cs, pal = resolve(head, "/ColorSpace")
        cs = cs or b""
        if b"/Indexed" in cs or b"/I " in cs:
            ncomp, palette = 1, (pal or b"")
            if not palette:
                m = re.search(rb"<([0-9A-Fa-f\s]+)>", cs)
                if m:
                    palette = bytes.fromhex(re.sub(rb"\s", b"", m.group(1)).decode())
            if not palette:
                skipped.append((objnum, w, h, "indexed w/o palette"))
                continue
        elif b"DeviceGray" in cs or b"CalGray" in cs:
            ncomp, palette = 1, None
        elif b"DeviceCMYK" in cs:
            skipped.append((objnum, w, h, "cmyk"))
            continue
        else:
            ncomp, palette = 3, None
        # predictor?
        pred = num(head, "/Predictor", 1)
        if pred and pred >= 10:
            stride = (w * ncomp * bpc + 7) // 8
            out, prev = bytearray(), bytearray(stride)
            pos = 0
            bpp = max(1, ncomp * bpc // 8)
            while pos + 1 + stride <= len(dec):
                ft = dec[pos]
                row = bytearray(dec[pos + 1:pos + 1 + stride])
                if ft == 1:
                    for i in range(bpp, stride):
                        row[i] = (row[i] + row[i - bpp]) & 255
                elif ft == 2:
                    for i in range(stride):
                        row[i] = (row[i] + prev[i]) & 255
                elif ft == 3:
                    for i in range(stride):
                        left = row[i - bpp] if i >= bpp else 0
                        row[i] = (row[i] + ((left + prev[i]) >> 1)) & 255
                elif ft == 4:
                    for i in range(stride):
                        a = row[i - bpp] if i >= bpp else 0
                        b = prev[i]
                        c = prev[i - bpp] if i >= bpp else 0
                        pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                        pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                        row[i] = (row[i] + pr) & 255
                out += row
                prev = row
                pos += 1 + stride
            dec = bytes(out)
        p = os.path.join(OUTDIR, "obj%04d_%dx%d.png" % (objnum, w, h))
        if png(p, w, h, ncomp, dec, bpc, palette):
            found.append((objnum, w, h, "png", os.path.getsize(p)))
        else:
            skipped.append((objnum, w, h, "png write failed (bpc=%s comp=%s len=%d)" % (bpc, ncomp, len(dec))))
        continue

    skipped.append((objnum, w, h, "filter " + ",".join(filt or ["none"])))

print("extracted %d images -> %s" % (len(found), OUTDIR))
for f in found:
    print("   obj%-6d %5dx%-5d %-4s %6.1f KB" % (f[0], f[1], f[2], f[3], f[4] / 1024))
if skipped:
    print("skipped %d:" % len(skipped))
    for s in skipped:
        print("   obj%-6d %sx%s  %s" % (s[0], s[1], s[2], s[3]))
