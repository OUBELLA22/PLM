# -*- coding: utf-8 -*-
"""Pixel size of PNG/JPEG files, standard library only."""
import os
import struct

HERE = os.path.dirname(os.path.abspath(__file__))
IMGDIR = os.path.join(HERE, "img")


def set_dir(rel):
    """Point the loader at a deck's own picture folder."""
    global IMGDIR
    IMGDIR = rel if os.path.isabs(rel) else os.path.join(HERE, rel)


def path(name):
    return os.path.join(IMGDIR, name)


def size(name):
    p = path(name)
    with open(p, "rb") as f:
        head = f.read(32)
        if head[:8] == b"\x89PNG\r\n\x1a\n":
            w, h = struct.unpack(">II", head[16:24])
            return w, h
        if head[:2] == b"\xff\xd8":
            f.seek(2)
            while True:
                b = f.read(1)
                while b and b != b"\xff":
                    b = f.read(1)
                marker = f.read(1)
                while marker == b"\xff":
                    marker = f.read(1)
                if not marker:
                    break
                if marker[0] in (0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
                                 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF):
                    f.read(3)
                    h, w = struct.unpack(">HH", f.read(4))
                    return w, h
                ln = struct.unpack(">H", f.read(2))[0]
                f.seek(ln - 2, 1)
    raise ValueError("unsupported image: " + p)


def fit(name, x, y, cx, cy):
    """Largest centred rectangle inside the box that keeps the aspect ratio (EMU in, EMU out)."""
    w, h = size(name)
    scale = min(cx / float(w), cy / float(h))
    nw, nh = int(w * scale), int(h * scale)
    return x + (cx - nw) // 2, y + (cy - nh) // 2, nw, nh
