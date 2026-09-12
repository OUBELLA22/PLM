# -*- coding: utf-8 -*-
"""Minimal PNG read/crop/write for 8-bit RGB images (standard library only)."""
import struct
import sys
import zlib


def _chunks(data):
    i = 8
    while i < len(data):
        ln = struct.unpack(">I", data[i:i + 4])[0]
        tag = data[i + 4:i + 8]
        yield tag, data[i + 8:i + 8 + ln]
        i += 12 + ln


def read_rgb(path):
    data = open(path, "rb").read()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not a PNG: " + path)
    idat, w, h = b"", 0, 0
    for tag, payload in _chunks(data):
        if tag == b"IHDR":
            w, h, bpc, ct = struct.unpack(">IIBB", payload[:10])
            if (bpc, ct) != (8, 2):
                raise ValueError("only 8-bit RGB supported (got bpc=%d ct=%d)" % (bpc, ct))
        elif tag == b"IDAT":
            idat += payload
    raw = zlib.decompress(idat)
    stride = w * 3
    rows, prev, pos = [], bytearray(stride), 0
    for _ in range(h):
        ft = raw[pos]
        row = bytearray(raw[pos + 1:pos + 1 + stride])
        if ft == 1:
            for i in range(3, stride):
                row[i] = (row[i] + row[i - 3]) & 255
        elif ft == 2:
            for i in range(stride):
                row[i] = (row[i] + prev[i]) & 255
        elif ft == 3:
            for i in range(stride):
                left = row[i - 3] if i >= 3 else 0
                row[i] = (row[i] + ((left + prev[i]) >> 1)) & 255
        elif ft == 4:
            for i in range(stride):
                a = row[i - 3] if i >= 3 else 0
                b = prev[i]
                c = prev[i - 3] if i >= 3 else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                row[i] = (row[i] + pr) & 255
        rows.append(row)
        prev = row
        pos += 1 + stride
    return w, h, rows


def write_rgb(path, w, h, rows):
    scan = bytearray()
    for r in rows:
        scan.append(0)
        scan += r

    def chunk(tag, payload):
        return (struct.pack(">I", len(payload)) + tag + payload
                + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF))

    out = [b"\x89PNG\r\n\x1a\n",
           chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)),
           chunk(b"IDAT", zlib.compress(bytes(scan), 9)),
           chunk(b"IEND", b"")]
    open(path, "wb").write(b"".join(out))


def crop(src, dst, x, y, cw, ch):
    w, h, rows = read_rgb(src)
    x, y = max(0, x), max(0, y)
    cw, ch = min(cw, w - x), min(ch, h - y)
    out = [rows[y + j][x * 3:(x + cw) * 3] for j in range(ch)]
    write_rgb(dst, cw, ch, out)
    return cw, ch


if __name__ == "__main__":
    # crop src dst x y w h
    a = sys.argv[1:]
    print(crop(a[0], a[1], *map(int, a[2:6])))
