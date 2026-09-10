"""Pure-python layout preview rasterizer: renders the shape specs to a PNG
contact sheet so the composition can be inspected without PowerPoint.
Text is drawn as measured bars (real wrap widths), which is what matters for
catching overflow, collisions and rhythm problems."""
import struct, zlib
import pptxlib as L


class Canvas:
    def __init__(self, w, h, bg=(8, 20, 40)):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def blend(self, x, y, rgb, a):
        if 0 <= x < self.w and 0 <= y < self.h and a > 0:
            i = (y * self.w + x) * 3
            p = self.px
            if a >= 1.0:
                p[i], p[i + 1], p[i + 2] = rgb
            else:
                for k in range(3):
                    p[i + k] = int(p[i + k] + (rgb[k] - p[i + k]) * a)

    def rect(self, x, y, w, h, rgb, a=1.0, r=0):
        x0, y0, x1, y1 = int(x), int(y), int(x + w), int(y + h)
        for yy in range(max(0, y0), min(self.h, y1)):
            for xx in range(max(0, x0), min(self.w, x1)):
                if r:
                    dx = min(xx - x0, x1 - 1 - xx)
                    dy = min(yy - y0, y1 - 1 - yy)
                    if dx < r and dy < r and (r - dx) ** 2 + (r - dy) ** 2 > r * r:
                        continue
                self.blend(xx, yy, rgb, a)

    def frame(self, x, y, w, h, rgb, a=1.0, t=1, r=0):
        for i in range(int(max(1, t))):
            self.ring(x + i, y + i, w - 2 * i, h - 2 * i, rgb, a, r)

    def ring(self, x, y, w, h, rgb, a, r=0):
        x0, y0, x1, y1 = int(x), int(y), int(x + w), int(y + h)
        for xx in range(x0, x1):
            self.blend(xx, y0, rgb, a); self.blend(xx, y1 - 1, rgb, a)
        for yy in range(y0, y1):
            self.blend(x0, yy, rgb, a); self.blend(x1 - 1, yy, rgb, a)

    def ellipse(self, x, y, w, h, rgb, a=1.0, fill=True):
        cx, cy, rx, ry = x + w / 2.0, y + h / 2.0, w / 2.0, h / 2.0
        for yy in range(int(y), int(y + h) + 1):
            for xx in range(int(x), int(x + w) + 1):
                d = ((xx - cx) / max(rx, .5)) ** 2 + ((yy - cy) / max(ry, .5)) ** 2
                if fill and d <= 1.0:
                    self.blend(xx, yy, rgb, a)
                elif not fill and 0.8 <= d <= 1.05:
                    self.blend(xx, yy, rgb, a)

    def line(self, x0, y0, x1, y1, rgb, a=1.0, t=1):
        n = int(max(abs(x1 - x0), abs(y1 - y0), 1))
        for i in range(n + 1):
            x = x0 + (x1 - x0) * i / n
            y = y0 + (y1 - y0) * i / n
            for oy in range(-(t // 2), t // 2 + 1):
                for ox in range(-(t // 2), t // 2 + 1):
                    self.blend(int(x) + ox, int(y) + oy, rgb, a)

    def png(self, path):
        raw = bytearray()
        for y in range(self.h):
            raw.append(0)
            raw += self.px[y * self.w * 3:(y + 1) * self.w * 3]
        def chunk(tag, data):
            c = struct.pack('>I', len(data)) + tag + data
            return c + struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
        out = b'\x89PNG\r\n\x1a\n'
        out += chunk(b'IHDR', struct.pack('>IIBBBBB', self.w, self.h, 8, 2, 0, 0, 0))
        out += chunk(b'IDAT', zlib.compress(bytes(raw), 6))
        out += chunk(b'IEND', b'')
        open(path, 'wb').write(out)


def rgb(hexs):
    return (int(hexs[0:2], 16), int(hexs[2:4], 16), int(hexs[4:6], 16))


def draw_slide(c, shapes, ox, oy, sc):
    def X(v): return ox + v * sc
    for s in shapes:
        x, y, w, h = X(s['x']), oy + s['y'] * sc, s['w'] * sc, s['h'] * sc
        k = s['kind']
        f = s.get('fill')
        rr = s.get('r', 0) * sc
        if s.get('shadow'):
            c.rect(x + 2, y + 4, w, h, (0, 4, 12), .35, int(rr))
        if k == 'pic':
            c.rect(x, y, w, h, (205, 212, 222), 1.0, int(rr))
            c.line(x, y, x + w, y + h, (150, 160, 175), .8, 1)
            c.line(x, y + h, x + w, y, (150, 160, 175), .8, 1)
        elif f:
            if f[0] == 'solid':
                col, al = rgb(f[1]), f[2] / 100.0
            elif f[0] == 'radial':
                col, al = rgb(f[1]), f[2] / 220.0
            else:
                col, al = rgb(f[1]), (f[4] + f[5]) / 200.0
            if k == 'ellipse' or k == 'donut':
                c.ellipse(x, y, w, h, col, al)
            else:
                c.rect(x, y, w, h, col, al, int(rr))
        ln = s.get('line')
        if ln:
            col = rgb(ln[0]); t = max(1, int(ln[1] * sc)); al = (ln[2] if len(ln) > 2 else 100) / 100.
            if k == 'line':
                c.line(x, y, x + w, y + h, col, al, t)
            elif k == 'ellipse':
                c.ellipse(x, y, w, h, col, al, fill=False)
            else:
                c.frame(x, y, w, h, col, al, t, int(rr))
        if s.get('text'):
            li, tt, ri, bi = s.get('ins', (0, 0, 0, 0))
            lines, th = L.measure(s)
            anchor = s.get('anchor', 't')
            cy = oy + (s['y'] + tt) * sc
            if anchor == 'ctr':
                cy = oy + (s['y'] + (s['h'] - th) / 2.0) * sc
            elif anchor == 'b':
                cy = oy + (s['y'] + s['h'] - bi - th) * sc
            algn = (s['text'][0]['align'] if s.get('text') else 'l')
            for txt, lw, sz, lh in lines:
                bh = max(1.0, sz * 1.333 * 0.62 * sc)
                pad = (lh * sc - bh) / 2.0
                bx = X(s['x'] + li)
                if algn == 'ctr':
                    bx = X(s['x'] + li + (s['w'] - li - ri - lw / 1.0) / 2.0)
                elif algn == 'r':
                    bx = X(s['x'] + s['w'] - ri - lw)
                col = (222, 232, 245) if sz >= 15 else (168, 186, 210)
                c.rect(bx, cy + pad, max(1, lw * sc), bh, col, .80 if sz >= 15 else .62)
                cy += lh * sc


def contact_sheet(slides, path, cols=2, sc=0.5, gap=14):
    sw, sh = int(L.CW * sc), int(L.CH * sc)
    rows = (len(slides) + cols - 1) // cols
    W = cols * sw + (cols + 1) * gap
    H = rows * sh + (rows + 1) * gap
    c = Canvas(W, H, bg=(26, 28, 34))
    for i, shapes in enumerate(slides):
        r, q = divmod(i, cols)
        ox = gap + q * (sw + gap)
        oy = gap + r * (sh + gap)
        c.rect(ox, oy, sw, sh, (10, 22, 44))
        draw_slide(c, shapes, ox, oy, sc)
        c.frame(ox, oy, sw, sh, (90, 100, 120), .9, 1)
    c.png(path)


def single(slides, idx, path, sc=1.0):
    c = Canvas(int(L.CW * sc), int(L.CH * sc), bg=(10, 22, 44))
    draw_slide(c, slides[idx], 0, 0, sc)
    c.png(path)
