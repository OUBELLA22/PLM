# -*- coding: utf-8 -*-
"""Render the ECO deck to a PowerPoint file, writing OOXML directly (no external deps)."""
import os
import zipfile
from xml.sax.saxutils import escape

import imgutil
from deck import META, SLIDES, outfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = outfile("pptx")

EMU = 914400
W, H = 12192000, 6858000          # 13.333 x 7.5 in (16:9)
L = int(0.85 * EMU)
CW = W - 2 * L
KICK_Y = int(0.52 * EMU)
TITLE_Y = int(0.82 * EMU)
RULE_Y = int(1.72 * EMU)
BODY_Y = int(2.02 * EMU)
FOOT_Y = int(6.82 * EMU)
FOOT_LINE = int(6.72 * EMU)
BODY_BOT = int(6.45 * EMU)

BG = "0B1220"
CARD = "16233A"
LINE = "25344F"
TX = "E2EAF6"
WHITE = "FFFFFF"
MUT = "93A8C6"
ACC = "4F8DFF"
ACC2 = "22D3EE"
OK = "34D399"
WARN = "FBBF24"
DAN = "F87171"
FONT = "Segoe UI"

NS = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"')


def e(t):
    return escape(t)


def runs(segs, sz, color=TX, bold=False, font=FONT):
    """segs: str or list of (text, bold)."""
    if isinstance(segs, str):
        segs = [(segs, bold)]
    out = []
    for t, b in segs:
        out.append(
            '<a:r><a:rPr lang="en-US" sz="%d"%s dirty="0"><a:solidFill><a:srgbClr val="%s"/></a:solidFill>'
            '<a:latin typeface="%s"/><a:cs typeface="%s"/></a:rPr><a:t>%s</a:t></a:r>'
            % (sz, ' b="1"' if (b or bold) else "", color, font, font, e(t)))
    return "".join(out)


def para(segs, sz=1500, color=TX, bold=False, bullet=None, before=0, after=0,
         marL=0, indent=0, line=100000, algn="l", buclr=ACC):
    p = ['<a:p><a:pPr marL="%d" indent="%d" algn="%s">' % (marL, indent, algn)]
    p.append('<a:lnSpc><a:spcPct val="%d"/></a:lnSpc>' % line)
    if before:
        p.append('<a:spcBef><a:spcPts val="%d"/></a:spcBef>' % before)
    if after:
        p.append('<a:spcAft><a:spcPts val="%d"/></a:spcAft>' % after)
    if bullet == "char":
        p.append('<a:buClr><a:srgbClr val="%s"/></a:buClr><a:buSzPct val="80000"/>'
                 '<a:buFont typeface="Arial"/><a:buChar char="\u25aa"/>' % buclr)
    elif bullet == "num":
        p.append('<a:buClr><a:srgbClr val="%s"/></a:buClr><a:buFont typeface="%s"/>'
                 '<a:buAutoNum type="arabicPeriod"/>' % (buclr, FONT))
    elif bullet == "dot":
        p.append('<a:buClr><a:srgbClr val="%s"/></a:buClr><a:buSzPct val="70000"/>'
                 '<a:buFont typeface="Arial"/><a:buChar char="\u2022"/>' % buclr)
    else:
        p.append("<a:buNone/>")
    p.append("</a:pPr>")
    p.append(runs(segs, sz, color, bold))
    p.append("</a:p>")
    return "".join(p)


def txbox(sid, x, y, cx, cy, paras, anchor="t", ins=0):
    return (
        '<p:sp><p:nvSpPr><p:cNvPr id="%d" name="t%d"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>'
        '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/></p:spPr>'
        '<p:txBody><a:bodyPr wrap="square" lIns="%d" tIns="0" rIns="%d" bIns="0" anchor="%s">'
        '<a:normAutofit/></a:bodyPr><a:lstStyle/>%s</p:txBody></p:sp>'
        % (sid, sid, x, y, cx, cy, ins, ins, anchor, paras))


def shape(sid, x, y, cx, cy, fill, geom="rect", paras="", anchor="ctr", lnclr=None, ins=91440, adj=None):
    av = '<a:avLst>%s</a:avLst>' % (adj or "")
    ln = ('<a:ln w="12700"><a:solidFill><a:srgbClr val="%s"/></a:solidFill></a:ln>' % lnclr) if lnclr else '<a:ln><a:noFill/></a:ln>'
    body = ('<p:txBody><a:bodyPr wrap="square" lIns="%d" tIns="45720" rIns="%d" bIns="45720" anchor="%s">'
            '<a:normAutofit/></a:bodyPr><a:lstStyle/>%s</p:txBody>' % (ins, ins, anchor, paras or para("", 1000)))
    return (
        '<p:sp><p:nvSpPr><p:cNvPr id="%d" name="s%d"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
        '<a:prstGeom prst="%s">%s</a:prstGeom><a:solidFill><a:srgbClr val="%s"/></a:solidFill>%s</p:spPr>%s</p:sp>'
        % (sid, sid, x, y, cx, cy, geom, av, fill, ln, body))


def table(sid, x, y, cx, head, rows, fsz=1150, colw=(0.32, 0.68)):
    grid = "".join('<a:gridCol w="%d"/>' % int(cx * f) for f in colw)
    xml = ['<p:graphicFrame><p:nvGraphicFramePr><p:cNvPr id="%d" name="tbl%d"/>'
           '<p:cNvGraphicFramePr><a:graphicFrameLocks noGrp="1"/></p:cNvGraphicFramePr><p:nvPr/>'
           '</p:nvGraphicFramePr><p:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></p:xfrm>'
           '<a:graphic><a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/table">'
           '<a:tbl><a:tblPr/><a:tblGrid>%s</a:tblGrid>' % (sid, sid, x, y, cx, int(0.4 * EMU), grid)]

    def cell(segs, sz, color, bold, fill, pad_top=45720):
        # NB: CT_TableCellProperties requires line children BEFORE the fill.
        return ('<a:tc><a:txBody><a:bodyPr lIns="109728" rIns="109728" tIns="%d" bIns="%d" anchor="t"/>'
                '<a:lstStyle/>%s</a:txBody><a:tcPr marL="0">'
                '<a:lnB w="12700" cap="flat"><a:solidFill><a:srgbClr val="%s"/></a:solidFill></a:lnB>'
                '<a:solidFill><a:srgbClr val="%s"/></a:solidFill></a:tcPr></a:tc>'
                % (pad_top, pad_top, para(segs, sz, color, bold, line=95000), LINE, fill))

    xml.append('<a:tr h="%d">' % int(0.34 * EMU))
    for hcell in head:
        xml.append(cell(hcell.upper(), int(fsz * 0.85), ACC2, True, BG))
    xml.append("</a:tr>")
    for i, r in enumerate(rows):
        fill = CARD if i % 2 == 0 else "101B2D"
        xml.append('<a:tr h="%d">' % int(0.33 * EMU))
        xml.append(cell(r[0], fsz, WHITE, True, fill))
        xml.append(cell(r[1], fsz, TX, False, fill))
        xml.append("</a:tr>")
    xml.append("</a:tbl></a:graphicData></a:graphic></p:graphicFrame>")
    return "".join(xml)


def pic(sid, rid, x, y, cx, cy):
    return ('<p:pic><p:nvPicPr><p:cNvPr id="%d" name="p%d"/>'
            '<p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
            '<p:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
            '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>'
            % (sid, sid, rid, x, y, cx, cy))


TONE = {"warn": WARN, "danger": DAN, "ok": OK, "": ACC}


def callout_shapes(sid, y, text, tone):
    clr = TONE.get(tone, ACC)
    bg = {"warn": "241D0F", "danger": "2A1418", "ok": "0F2418"}.get(tone, "132039")
    h = int(0.78 * EMU)
    out = shape(sid, L, y, CW, h, bg, lnclr=LINE, anchor="ctr",
                paras=para(text, 1250, TX, line=95000), ins=228600)
    out += shape(sid + 1, L, y, int(0.06 * EMU), h, clr)
    return out


def slide_xml(s, idx, total):
    sh = []
    sid = [10]
    imgs = []               # image files used by this slide, in relationship order

    def nid():
        sid[0] += 1
        return sid[0]

    def add_img(file, x, y, cx, cy, caption=None, label=None, cap_sz=900):
        """Place a picture inside the box, on a white frame, with optional label / caption."""
        cap_h = int(0.5 * EMU) if caption else 0
        lab_h = int(0.3 * EMU) if label else 0
        fx, fy, fw, fh = imgutil.fit(file, x, y + lab_h, cx, cy - cap_h - lab_h)
        pad = int(0.05 * EMU)
        imgs.append(file)
        rid = "rId%d" % (len(imgs) + 1)
        sh.append(shape(nid(), fx - pad, fy - pad, fw + 2 * pad, fh + 2 * pad, "FFFFFF", lnclr="2B3D5C"))
        sh.append(pic(nid(), rid, fx, fy, fw, fh))
        if label:
            sh.append(txbox(nid(), x, fy - pad - int(0.3 * EMU), cx, int(0.26 * EMU),
                            para(label.upper(), 1000, ACC2, True, algn="ctr")))
        if caption:
            cy_cap = min(fy + fh + pad + int(0.1 * EMU), y + cy - cap_h)   # never leave the box
            sh.append(txbox(nid(), x, cy_cap, cx, cap_h,
                            para(caption, cap_sz, "8FA5C4", algn="ctr", line=95000)))

    if s["kind"] == "title":
        sh.append(shape(nid(), 0, 0, W, H, "0A1424"))
        sh.append(shape(nid(), L, int(1.55 * EMU), int(1.45 * EMU), int(0.11 * EMU), ACC))
        sh.append(txbox(nid(), L, int(1.95 * EMU), CW, int(1.5 * EMU),
                        para(s["title"], 6600, WHITE, True, line=95000)))
        sh.append(txbox(nid(), L, int(3.35 * EMU), CW, int(0.7 * EMU),
                        para(s["subtitle"], 2600, "BCD0EC", True)))
        sh.append(txbox(nid(), L, int(4.15 * EMU), int(CW * 0.72), int(0.7 * EMU),
                        para(s["tagline"], 1700, MUT)))
        sh.append(txbox(nid(), L, int(5.9 * EMU), CW, int(0.5 * EMU),
                        para(s["meta"], 1050, "6F87A8")))
        return wrap_slide("".join(sh)), imgs

    if s["kind"] == "close":
        sh.append(txbox(nid(), L, KICK_Y, CW, int(0.35 * EMU),
                        para("WRAP-UP", 1150, ACC2, True)))
        sh.append(txbox(nid(), L, TITLE_Y, CW, int(0.9 * EMU),
                        para(s["title"], 3200, WHITE, True, line=95000)))
        sh.append(shape(nid(), L, RULE_Y, int(0.8 * EMU), int(0.08 * EMU), ACC))
        ps = "".join(para([("%02d   " % (j + 1), True), (p, False)], 1800, TX,
                          before=700, marL=0, line=100000)
                     for j, p in enumerate(s["points"]))
        sh.append(txbox(nid(), L, BODY_Y + int(0.15 * EMU), CW, int(3.5 * EMU), ps))
        sh.append(txbox(nid(), L, int(5.95 * EMU), CW, int(0.6 * EMU), para(s["meta"], 1000, "6F87A8", line=95000)))
        sh.append(shape(nid(), L, FOOT_LINE, CW, 9525, LINE))
        sh.append(txbox(nid(), L, FOOT_Y, CW, int(0.3 * EMU), para(META["footer"], 950, "65799A")))
        sh.append(txbox(nid(), L, FOOT_Y, CW, int(0.3 * EMU), para("%d / %d" % (idx, total), 950, "65799A", algn="r")))
        return wrap_slide("".join(sh)), imgs

    # standard slide chrome
    if s.get("kicker"):
        sh.append(txbox(nid(), L, KICK_Y, CW, int(0.35 * EMU), para(s["kicker"].upper(), 1150, ACC2, True)))
    sh.append(txbox(nid(), L, TITLE_Y, CW, int(0.9 * EMU), para(s["title"], 3200, WHITE, True, line=95000)))
    sh.append(shape(nid(), L, RULE_Y, int(0.8 * EMU), int(0.08 * EMU), ACC))

    tail = s.get("callout") or ({"tone": "", "text": s["note"]} if s.get("note") else None) \
        or ({"tone": "", "text": s["footnote"]} if s.get("footnote") else None)
    body_bot = BODY_BOT - (int(1.0 * EMU) if tail else 0)
    body_h = body_bot - BODY_Y
    k = s["kind"]

    panel = s.get("image") if isinstance(s.get("image"), dict) else None
    side = panel and s.get("image_pos") != "below"
    text_w = int(CW * 0.62) if side else CW

    if k == "bullets":
        bl = s["bullets"]
        if s.get("columns") == 2:
            half = (len(bl) + 1) // 2
            gap = int(0.4 * EMU)
            cwid = (text_w - gap) // 2
            for c, chunk in enumerate((bl[:half], bl[half:])):
                ps = "".join(para(b, 1250, TX, bullet="char", before=500,
                                  marL=int(0.28 * EMU), indent=int(-0.28 * EMU), line=100000) for b in chunk)
                sh.append(txbox(nid(), L + c * (cwid + gap), BODY_Y, cwid, body_h, ps))
        else:
            sz = 1600 if len(bl) <= 5 else 1450
            ps = "".join(para(b, sz, TX, bullet="char", before=800,
                              marL=int(0.32 * EMU), indent=int(-0.32 * EMU), line=100000) for b in bl)
            sh.append(txbox(nid(), L, BODY_Y, text_w, body_h, ps))

    elif k == "steps":
        ps = "".join(para(st, 1550, TX, bullet="num", before=900,
                          marL=int(0.4 * EMU), indent=int(-0.4 * EMU), line=100000) for st in s["steps"])
        sh.append(txbox(nid(), L, BODY_Y + int(0.1 * EMU), text_w, body_h, ps))

    elif k == "shot":
        gap = int(0.35 * EMU)
        iw = int(CW * 0.64)
        add_img(s["image"], L, BODY_Y, iw, body_h)
        ps = "".join(para(x, 1300, TX, bullet="char", before=700,
                          marL=int(0.28 * EMU), indent=int(-0.28 * EMU), line=100000) for x in s["notes"])
        sh.append(txbox(nid(), L + iw + gap, BODY_Y, CW - iw - gap, body_h, ps, anchor="ctr"))

    elif k == "shots":
        gap = int(0.45 * EMU)
        cwid = (CW - gap) // 2
        for i, im in enumerate(s["images"]):
            add_img(im["file"], L + i * (cwid + gap), BODY_Y, cwid, body_h,
                    caption=im.get("caption"), label=im.get("label"), cap_sz=850)

    elif k == "flow":
        y = BODY_Y - int(0.12 * EMU)
        for r in s["rows"]:
            sh.append(txbox(nid(), L, y, CW, int(0.3 * EMU), para(r["label"].upper(), 1050, MUT, True)))
            y += int(0.42 * EMU)
            x = L
            chip_h = int(0.52 * EMU)
            for j, c in enumerate(r["chips"]):
                if j:
                    sh.append(txbox(nid(), x, y + int(0.08 * EMU), int(0.24 * EMU), chip_h,
                                    para("\u203a", 1600, ACC2, True, algn="ctr")))
                    x += int(0.24 * EMU)
                cwid = int(0.34 * EMU) + int(0.098 * EMU * len(c))
                fill = "1B3A6B" if r["style"] == "accent" else CARD
                sh.append(shape(nid(), x, y, cwid, chip_h, fill, geom="roundRect", lnclr=LINE,
                                paras=para(c, 1200, WHITE if r["style"] == "accent" else TX, True, algn="ctr"),
                                adj='<a:gd name="adj" fmla="val 40000"/>'))
                x += cwid
            y += int(1.0 * EMU)
        if panel and not side:
            add_img(panel["file"], L, y, CW, body_bot - y,
                    caption=panel.get("caption"), cap_sz=900)

    elif k == "cards":
        gap = int(0.3 * EMU)
        n = len(s["cards"])
        cwid = (CW - gap * (n - 1)) // n
        ch = min(body_h, int(3.15 * EMU))
        for i, c in enumerate(s["cards"]):
            x = L + i * (cwid + gap)
            sh.append(shape(nid(), x, BODY_Y, cwid, ch, CARD, lnclr=LINE, anchor="t"))
            sh.append(shape(nid(), x, BODY_Y, cwid, int(0.07 * EMU), TONE.get(c.get("tone", ""), ACC)))
            inner = para(c["tag"].upper(), 1050, ACC2, True)
            inner += para(c["title"], 1700, WHITE, True, before=300, line=95000)
            for ln in c["lines"]:
                inner += para(ln, 1200, "CDDBEE", bullet="dot", before=450,
                              marL=int(0.24 * EMU), indent=int(-0.24 * EMU), line=95000)
            sh.append(txbox(nid(), x + int(0.22 * EMU), BODY_Y + int(0.3 * EMU),
                            cwid - int(0.44 * EMU), ch - int(0.45 * EMU), inner))

    elif k == "table":
        fsz = 1150 if len(s["rows"]) > 5 else 1350
        sh.append(table(nid(), L, BODY_Y, CW, s["head"], s["rows"], fsz))

    elif k == "glossary":
        pairs = s["pairs"]
        half = (len(pairs) + 1) // 2
        gap = int(0.5 * EMU)
        cwid = (CW - gap) // 2
        for c, chunk in enumerate((pairs[:half], pairs[half:])):
            ps = "".join(para([(a, True), ("   " + b, False)], 1200, "CDDBEE", before=520, line=95000)
                         for a, b in chunk)
            sh.append(txbox(nid(), L + c * (cwid + gap), BODY_Y, cwid, body_h, ps))

    if side:
        px = L + text_w + int(0.35 * EMU)
        add_img(panel["file"], px, BODY_Y, CW - text_w - int(0.35 * EMU), body_h,
                caption=panel.get("caption"), cap_sz=850)

    if tail:
        sh.append(callout_shapes(nid() and sid[0], body_bot + int(0.2 * EMU), tail["text"], tail["tone"]))
        sid[0] += 1

    sh.append(shape(nid(), L, FOOT_LINE, CW, 9525, LINE))
    sh.append(txbox(nid(), L, FOOT_Y, CW, int(0.3 * EMU), para(META["footer"], 950, "65799A")))
    sh.append(txbox(nid(), L, FOOT_Y, CW, int(0.3 * EMU), para("%d / %d" % (idx, total), 950, "65799A", algn="r")))
    return wrap_slide("".join(sh)), imgs


def wrap_slide(shapes):
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<p:sld %s><p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="%s"/></a:solidFill>'
            '<a:effectLst/></p:bgPr></p:bg><p:spTree>'
            '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
            '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
            '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>%s'
            '</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'
            % (NS, BG, shapes))


# ---------------------------------------------------------------- package parts
def theme_xml():
    def fill_style():
        return ('<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
                '<a:gradFill rotWithShape="1"><a:gsLst>'
                '<a:gs pos="0"><a:schemeClr val="phClr"><a:tint val="60000"/></a:schemeClr></a:gs>'
                '<a:gs pos="100000"><a:schemeClr val="phClr"><a:shade val="80000"/></a:schemeClr></a:gs>'
                '</a:gsLst><a:lin ang="5400000" scaled="0"/></a:gradFill>'
                '<a:solidFill><a:schemeClr val="phClr"><a:shade val="90000"/></a:schemeClr></a:solidFill>')

    ln = ('<a:ln w="%d" cap="flat" cmpd="sng" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
          '<a:prstDash val="solid"/></a:ln>')
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="ECO">'
            '<a:themeElements><a:clrScheme name="ECO">'
            '<a:dk1><a:srgbClr val="0B1220"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>'
            '<a:dk2><a:srgbClr val="16233A"/></a:dk2><a:lt2><a:srgbClr val="E2EAF6"/></a:lt2>'
            '<a:accent1><a:srgbClr val="4F8DFF"/></a:accent1><a:accent2><a:srgbClr val="22D3EE"/></a:accent2>'
            '<a:accent3><a:srgbClr val="34D399"/></a:accent3><a:accent4><a:srgbClr val="FBBF24"/></a:accent4>'
            '<a:accent5><a:srgbClr val="F87171"/></a:accent5><a:accent6><a:srgbClr val="93A8C6"/></a:accent6>'
            '<a:hlink><a:srgbClr val="22D3EE"/></a:hlink><a:folHlink><a:srgbClr val="93A8C6"/></a:folHlink>'
            '</a:clrScheme><a:fontScheme name="ECO">'
            '<a:majorFont><a:latin typeface="Segoe UI"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont>'
            '<a:minorFont><a:latin typeface="Segoe UI"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont>'
            '</a:fontScheme><a:fmtScheme name="ECO">'
            '<a:fillStyleLst>%s</a:fillStyleLst>'
            '<a:lnStyleLst>%s%s%s</a:lnStyleLst>'
            '<a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle>'
            '<a:effectStyle><a:effectLst/></a:effectStyle>'
            '<a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>'
            '<a:bgFillStyleLst>%s</a:bgFillStyleLst>'
            '</a:fmtScheme></a:themeElements><a:objectDefaults/><a:extraClrSchemeLst/></a:theme>'
            % (fill_style(), ln % 6350, ln % 12700, ln % 19050, fill_style()))


def build():
    n = len(SLIDES)
    parts = {}

    ct = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
          '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="xml" ContentType="application/xml"/>'
          '<Default Extension="png" ContentType="image/png"/>'
          '<Default Extension="jpg" ContentType="image/jpeg"/>'
          '<Default Extension="jpeg" ContentType="image/jpeg"/>'
          '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>'
          '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>'
          '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>'
          '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
          '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
          '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>']
    for i in range(1, n + 1):
        ct.append('<Override PartName="/ppt/slides/slide%d.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>' % i)
    ct.append("</Types>")
    parts["[Content_Types].xml"] = "".join(ct)

    parts["_rels/.rels"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
        '</Relationships>')

    parts["docProps/core.xml"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
        'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        '<dc:title>%s \u2014 %s</dc:title><dc:subject>%s</dc:subject>'
        '<dcterms:created xsi:type="dcterms:W3CDTF">2026-09-12T00:00:00Z</dcterms:created>'
        '</cp:coreProperties>' % (e(META["title"]), e(META["subtitle"]), e(META["source"])))

    parts["docProps/app.xml"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
        'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
        '<Slides>%d</Slides><Application>Kiro</Application></Properties>' % n)

    prs_rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>']
    sld_ids = []
    for i in range(1, n + 1):
        rid = "rId%d" % (i + 1)
        prs_rels.append('<Relationship Id="%s" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide%d.xml"/>' % (rid, i))
        sld_ids.append('<p:sldId id="%d" r:id="%s"/>' % (255 + i, rid))
    prs_rels.append('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>' % (n + 2))
    prs_rels.append("</Relationships>")
    parts["ppt/_rels/presentation.xml.rels"] = "".join(prs_rels)

    parts["ppt/presentation.xml"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<p:presentation %s saveSubsetFonts="1">'
        '<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>'
        '<p:sldIdLst>%s</p:sldIdLst>'
        '<p:sldSz cx="%d" cy="%d"/><p:notesSz cx="%d" cy="%d"/>'
        '</p:presentation>' % (NS, "".join(sld_ids), W, H, H, W))

    parts["ppt/theme/theme1.xml"] = theme_xml()

    empty_tree = ('<p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="%s"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>'
                  '<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
                  '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
                  '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>' % BG)

    parts["ppt/slideMasters/slideMaster1.xml"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<p:sldMaster %s>%s'
        '<p:clrMap bg1="dk1" tx1="lt1" bg2="dk2" tx2="lt2" accent1="accent1" accent2="accent2" '
        'accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>'
        '<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>'
        '</p:sldMaster>' % (NS, empty_tree))
    parts["ppt/slideMasters/_rels/slideMaster1.xml.rels"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>'
        '</Relationships>')

    parts["ppt/slideLayouts/slideLayout1.xml"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<p:sldLayout %s type="blank" preserve="1">%s'
        '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>' % (NS, empty_tree))
    parts["ppt/slideLayouts/_rels/slideLayout1.xml.rels"] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>'
        '</Relationships>')

    media = {}
    for i, s in enumerate(SLIDES, 1):
        xml, imgs = slide_xml(s, i, n)
        parts["ppt/slides/slide%d.xml" % i] = xml
        rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>']
        for j, f in enumerate(imgs, 2):
            media[f] = open(imgutil.path(f), "rb").read()
            rels.append('<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="../media/%s"/>' % (j, f))
        rels.append("</Relationships>")
        parts["ppt/slides/_rels/slide%d.xml.rels" % i] = "".join(rels)
    for f, blob in media.items():
        parts["ppt/media/" + f] = blob

    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", parts.pop("[Content_Types].xml"))
        for k in sorted(parts):
            z.writestr(k, parts[k])
    return OUT, n


if __name__ == "__main__":
    p, n = build()
    print("PPTX deck: %s (%d slides, %d KB)" % (p, n, os.path.getsize(p) // 1024))
