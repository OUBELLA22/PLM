# -*- coding: utf-8 -*-
"""A small .docx writer built on the standard library only.

Written by hand because this environment has no python-docx. It emits the parts
of WordprocessingML the guide needs, and nothing else.

The point of interest is `figure_group`. Each annotated screenshot becomes a
DrawingML **group shape** (`wpg:wgp`) holding:

    * the picture, embedded as the original file bytes;
    * one `wps:wsp` rectangle per highlight;
    * one `wps:wsp` ellipse per numbered marker, with its number as shape text.

That is byte-for-byte the structure Word itself produces when you insert a
picture, draw rectangles over it and press Group. So in Word every highlight is
a normal shape: click it, drag it, resize it, recolour it, delete it, or find it
by name in the Selection Pane. Nothing is burnt into the image.

All geometry inside a group uses the group's child coordinate space, which is
set 1:1 with its extent, so a highlight authored in screenshot pixels maps to
EMU with a single scale factor.
"""
import struct
import zipfile
from xml.sax.saxutils import escape, quoteattr

EMU_IN = 914400          # EMU per inch
TWIP_IN = 1440           # twips per inch
EMU_TWIP = EMU_IN // TWIP_IN

NS = (
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
    'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" '
    'xmlns:wpg="http://schemas.microsoft.com/office/word/2010/wordprocessingGroup" '
    'xmlns:wps="http://schemas.microsoft.com/office/word/2010/wordprocessingShape" '
    'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
    'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" '
    'xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" '
    'mc:Ignorable="w14 wp14"'
)
# NB: wpg / wps are deliberately absent from mc:Ignorable - Word must process
# them, not skip them.

GROUP_URI = "http://schemas.microsoft.com/office/word/2010/wordprocessingGroup"


def esc(s):
    return escape(s if isinstance(s, str) else str(s))


def _img_size(path):
    """(width, height) in pixels for a PNG or baseline JPEG."""
    blob = open(path, "rb").read()
    if blob[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", blob[16:24])
        return w, h
    if blob[:2] == b"\xff\xd8":
        i = 2
        while i < len(blob) - 1:
            if blob[i] != 0xFF:
                i += 1
                continue
            marker = blob[i + 1]
            if marker in (0xD8, 0xD9, 0x01) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            seglen = struct.unpack(">H", blob[i + 2:i + 4])[0]
            if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
                h, w = struct.unpack(">HH", blob[i + 5:i + 9])
                return w, h
            i += 2 + seglen
    raise ValueError("cannot read image size: %s" % path)


# --------------------------------------------------------------------- runs
def run(text, bold=False, italic=False, size=None, font=None, caps=False,
        spacing=None, color=None, underline=False):
    """One text run. `size` is in points."""
    pr = []
    if font:
        pr.append('<w:rFonts w:ascii=%s w:hAnsi=%s w:cs=%s/>'
                  % (quoteattr(font), quoteattr(font), quoteattr(font)))
    if bold:
        pr.append("<w:b/>")
    if italic:
        pr.append("<w:i/>")
    if caps:
        pr.append("<w:caps/>")
    # CT_RPr is a sequence: rFonts, b, i, caps, color, spacing, sz, szCs, u.
    if color:
        pr.append('<w:color w:val="%s"/>' % color)
    if spacing is not None:
        pr.append('<w:spacing w:val="%d"/>' % spacing)
    if size is not None:
        half = int(round(size * 2))
        pr.append('<w:sz w:val="%d"/><w:szCs w:val="%d"/>' % (half, half))
    if underline:
        pr.append('<w:u w:val="single"/>')
    prx = "<w:rPr>%s</w:rPr>" % "".join(pr) if pr else ""
    return '<w:r>%s<w:t xml:space="preserve">%s</w:t></w:r>' % (prx, esc(text))


def tab():
    return "<w:r><w:tab/></w:r>"


def br():
    return "<w:r><w:br/></w:r>"


def para(runs_xml="", style=None, align=None, before=None, after=None,
         left=None, hanging=None, line=None, keep_next=False, page_break=False,
         border_bottom=False, shade=None, outline=None, tabs=None,
         contextual=False):
    pr = []
    if style:
        pr.append('<w:pStyle w:val="%s"/>' % style)
    if keep_next:
        pr.append("<w:keepNext/><w:keepLines/>")
    if page_break:
        pr.append("<w:pageBreakBefore/>")
    # CT_PPr is a sequence: ... pageBreakBefore, numPr, pBdr, shd, tabs,
    # spacing, ind, contextualSpacing, jc, outlineLvl ...
    if border_bottom:
        pr.append('<w:pBdr><w:bottom w:val="single" w:sz="6" w:space="2" '
                  'w:color="BFBFBF"/></w:pBdr>')
    if shade:
        pr.append('<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % shade)
    if tabs:
        stops = "".join('<w:tab w:val="left" w:pos="%d"/>' % t for t in tabs)
        pr.append("<w:tabs>%s</w:tabs>" % stops)
    sp = []
    if before is not None:
        sp.append('w:before="%d"' % before)
    if after is not None:
        sp.append('w:after="%d"' % after)
    if line is not None:
        sp.append('w:line="%d" w:lineRule="auto"' % line)
    if sp:
        pr.append("<w:spacing %s/>" % " ".join(sp))
    if left is not None or hanging is not None:
        bits = []
        if left is not None:
            bits.append('w:left="%d"' % left)
        if hanging is not None:
            bits.append('w:hanging="%d"' % hanging)
        pr.append("<w:ind %s/>" % " ".join(bits))
    if contextual:
        pr.append("<w:contextualSpacing/>")
    if align:
        pr.append('<w:jc w:val="%s"/>' % align)
    if outline is not None:
        pr.append('<w:outlineLvl w:val="%d"/>' % outline)
    prx = "<w:pPr>%s</w:pPr>" % "".join(pr) if pr else ""
    return "<w:p>%s%s</w:p>" % (prx, runs_xml)


def list_para(runs_xml, num_id, level=0, style="ListParagraph", after=60):
    pr = ('<w:pPr><w:pStyle w:val="%s"/><w:numPr><w:ilvl w:val="%d"/>'
          '<w:numId w:val="%d"/></w:numPr><w:spacing w:after="%d"/>'
          "<w:contextualSpacing/></w:pPr>" % (style, level, num_id, after))
    return "<w:p>%s%s</w:p>" % (pr, runs_xml)


# -------------------------------------------------------------------- tables
def table(rows, widths, header=True, header_shade="D9D9D9",
          stripe="F2F2F2", borders=True, font_size=9.5, pad=70):
    """rows: list of list of cell XML (already paragraphs). widths in twips."""
    total = sum(widths)
    if borders:
        edge = ('<w:tblBorders>'
                '<w:top w:val="single" w:sz="6" w:space="0" w:color="808080"/>'
                '<w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
                '<w:bottom w:val="single" w:sz="6" w:space="0" w:color="808080"/>'
                '<w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
                '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="BFBFBF"/>'
                '<w:insideV w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
                "</w:tblBorders>")
    else:
        edge = ('<w:tblBorders>'
                '<w:top w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
                '<w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
                '<w:bottom w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
                '<w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
                '<w:insideH w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
                '<w:insideV w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
                "</w:tblBorders>")
    out = ['<w:tbl><w:tblPr><w:tblStyle w:val="GuideTable"/>'
           '<w:tblW w:w="%d" w:type="dxa"/>%s'
           '<w:tblCellMar>'
           '<w:top w:w="%d" w:type="dxa"/><w:left w:w="%d" w:type="dxa"/>'
           '<w:bottom w:w="%d" w:type="dxa"/><w:right w:w="%d" w:type="dxa"/>'
           "</w:tblCellMar></w:tblPr>" % (total, edge, pad, pad + 20, pad, pad + 20)]
    out.append("<w:tblGrid>%s</w:tblGrid>"
               % "".join('<w:gridCol w:w="%d"/>' % w for w in widths))
    for ri, row in enumerate(rows):
        is_head = header and ri == 0
        # CT_TrPr sequence puts cantSplit before tblHeader
        trpr = ["<w:trPr><w:cantSplit/>"]
        if is_head:
            trpr.append("<w:tblHeader/>")
        trpr.append("</w:trPr>")
        out.append("<w:tr>%s" % "".join(trpr))
        for ci, cell in enumerate(row):
            shade = header_shade if is_head else (
                stripe if (stripe and ri % 2 == 0) else None)
            shd = ('<w:shd w:val="clear" w:color="auto" w:fill="%s"/>' % shade) if shade else ""
            out.append('<w:tc><w:tcPr><w:tcW w:w="%d" w:type="dxa"/>%s'
                       '<w:vAlign w:val="top"/></w:tcPr>%s</w:tc>'
                       % (widths[ci], shd, cell))
        out.append("</w:tr>")
    out.append("</w:tbl>")
    return "".join(out)


# ------------------------------------------------------------------ document
class Docx:
    def __init__(self, title="", subject="", author="", creator="Kiro"):
        self.title, self.subject, self.author, self.creator = (
            title, subject, author, creator)
        self.body = []
        self._images = {}        # path -> (rid, name, w, h)
        self._rid = 20           # 1..9 reserved for the fixed parts
        self._oid = 100          # DrawingML object ids
        self._fig = 0

    # ---- ids and relationships
    def oid(self):
        self._oid += 1
        return self._oid

    def add(self, xml):
        self.body.append(xml)

    def image(self, path):
        """Register an image; returns (rid, width_px, height_px)."""
        if path not in self._images:
            self._rid += 1
            w, h = _img_size(path)
            ext = "png" if path.lower().endswith(".png") else "jpeg"
            name = "image%d.%s" % (len(self._images) + 1, ext)
            self._images[path] = ("rId%d" % self._rid, name, w, h)
        rid, _name, w, h = self._images[path]
        return rid, w, h

    # ---- the annotated figure -----------------------------------------
    def figure_group(self, path, width_emu, marks=(), name=None,
                     pic_outline="808080", marker_d=None, line_w=19050):
        """A picture plus movable annotation shapes, as one Word group.

        `marks` entries use screenshot pixel coordinates:
            {"box": (x, y, w, h), "n": 1, "mpos": "tl", "ink": "dark"|"light",
             "label": "..."}
        """
        rid, pw, ph = self.image(path)
        scale = float(width_emu) / pw          # EMU per screenshot pixel
        gw = int(round(width_emu))
        gh = int(round(ph * scale))
        self._fig += 1
        fig_no = self._fig
        d = marker_d or int(0.21 * EMU_IN)

        def px(v):
            return int(round(v * scale))

        shapes = []
        # the screenshot itself, original bytes, drawn at the group's full size
        shapes.append(
            '<pic:pic><pic:nvPicPr>'
            '<pic:cNvPr id="%d" name="Screenshot %d" descr=%s/>'
            '<pic:cNvPicPr><a:picLocks noChangeAspect="1"/></pic:cNvPicPr>'
            "</pic:nvPicPr>"
            '<pic:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch>'
            "</pic:blipFill>"
            '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>%s</pic:spPr></pic:pic>'
            % (self.oid(), fig_no,
               quoteattr(name or ("Figure %d" % fig_no)), rid, gw, gh,
               ('<a:ln w="9525"><a:solidFill><a:srgbClr val="%s"/></a:solidFill></a:ln>'
                % pic_outline) if pic_outline else "<a:ln><a:noFill/></a:ln>"))

        # highlight rectangles
        for m in marks:
            if not m.get("box"):
                continue
            bx, by, bw, bh = m["box"]
            ink = "FFFFFF" if m.get("ink") == "light" else "000000"
            label = m.get("label") or "Highlight"
            shapes.append(
                '<wps:wsp><wps:cNvPr id="%d" name=%s descr=%s/><wps:cNvSpPr/>'
                '<wps:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
                '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:noFill/>'
                '<a:ln w="%d" cap="flat"><a:solidFill><a:srgbClr val="%s"/></a:solidFill>'
                "</a:ln></wps:spPr>"
                '<wps:bodyPr rot="0" wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" '
                'anchor="ctr" anchorCtr="0"><a:noAutofit/></wps:bodyPr></wps:wsp>'
                % (self.oid(),
                   quoteattr("Highlight %s%s - %s"
                             % (fig_no, (".%s" % m["n"]) if m.get("n") else "", label)),
                   quoteattr(label), px(bx), px(by), px(bw), px(bh), line_w, ink))

        # numbered markers
        for m in marks:
            if not m.get("n"):
                continue
            if m.get("box"):
                bx, by, bw, bh = m["box"]
                ax, ay = {
                    "tl": (bx, by), "tr": (bx + bw, by), "bl": (bx, by + bh),
                    "br": (bx + bw, by + bh), "l": (bx, by + bh / 2.0),
                    "r": (bx + bw, by + bh / 2.0), "t": (bx + bw / 2.0, by),
                    "b": (bx + bw / 2.0, by + bh),
                }.get(m.get("mpos", "tl"), (bx, by))
            elif m.get("at"):
                ax, ay = m["at"]
            else:
                continue
            cx, cy = px(ax) - d // 2, px(ay) - d // 2
            cx = max(0, min(cx, gw - d))
            cy = max(0, min(cy, gh - d))
            dark = m.get("ink") != "light"
            fill = "000000" if dark else "FFFFFF"
            txt = "FFFFFF" if dark else "000000"
            shapes.append(
                '<wps:wsp><wps:cNvPr id="%d" name=%s/><wps:cNvSpPr/>'
                '<wps:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
                '<a:prstGeom prst="ellipse"><a:avLst/></a:prstGeom>'
                '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>'
                '<a:ln w="12700"><a:solidFill><a:srgbClr val="%s"/></a:solidFill></a:ln>'
                "</wps:spPr>"
                "<wps:txbx><w:txbxContent>%s</w:txbxContent></wps:txbx>"
                '<wps:bodyPr rot="0" wrap="square" lIns="0" tIns="0" rIns="0" bIns="0" '
                'anchor="ctr" anchorCtr="0"><a:noAutofit/></wps:bodyPr></wps:wsp>'
                % (self.oid(), quoteattr("Marker %s.%s" % (fig_no, m["n"])),
                   cx, cy, d, d, fill, txt,
                   para(run(str(m["n"]), bold=True, size=8, font="Calibri", color=txt),
                        align="center", before=0, after=0, line=240)))

        fig_name = name or ("Figure %d" % fig_no)
        descr = "Annotated screenshot; highlights are editable shapes"

        group_drawing = (
            "<w:drawing>"
            '<wp:inline distT="0" distB="0" distL="0" distR="0">'
            '<wp:extent cx="%d" cy="%d"/>'
            '<wp:effectExtent l="0" t="0" r="0" b="0"/>'
            '<wp:docPr id="%d" name=%s descr=%s/>'
            "<wp:cNvGraphicFramePr/>"
            "<a:graphic>"
            '<a:graphicData uri="%s">'
            "<wpg:wgp><wpg:cNvGrpSpPr/>"
            '<wpg:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/>'
            '<a:chOff x="0" y="0"/><a:chExt cx="%d" cy="%d"/></a:xfrm></wpg:grpSpPr>'
            "%s"
            "</wpg:wgp></a:graphicData></a:graphic></wp:inline></w:drawing>"
            % (gw, gh, self.oid(), quoteattr(fig_name), quoteattr(descr),
               GROUP_URI, gw, gh, gw, gh, "".join(shapes)))

        # Word writes shape groups inside mc:AlternateContent. The fallback is a
        # plain picture, so a reader that does not understand wpg still shows the
        # screenshot instead of failing.
        fallback_drawing = (
            "<w:drawing>"
            '<wp:inline distT="0" distB="0" distL="0" distR="0">'
            '<wp:extent cx="%d" cy="%d"/>'
            '<wp:effectExtent l="0" t="0" r="0" b="0"/>'
            '<wp:docPr id="%d" name=%s descr=%s/>'
            '<wp:cNvGraphicFramePr><a:graphicFrameLocks noChangeAspect="1"/>'
            "</wp:cNvGraphicFramePr>"
            "<a:graphic>"
            '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            "<pic:pic><pic:nvPicPr>"
            '<pic:cNvPr id="%d" name="Screenshot %d"/>'
            '<pic:cNvPicPr><a:picLocks noChangeAspect="1"/></pic:cNvPicPr>'
            "</pic:nvPicPr>"
            '<pic:blipFill><a:blip r:embed="%s"/><a:stretch><a:fillRect/></a:stretch>'
            "</pic:blipFill>"
            '<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
            '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
            "</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing>"
            % (gw, gh, self.oid(), quoteattr(fig_name + " (picture only)"),
               quoteattr(descr), self.oid(), fig_no, rid, gw, gh))

        return ('<w:r><mc:AlternateContent>'
                '<mc:Choice Requires="wpg">%s</mc:Choice>'
                "<mc:Fallback>%s</mc:Fallback>"
                "</mc:AlternateContent></w:r>" % (group_drawing, fallback_drawing)), gh

    # ---- package -------------------------------------------------------
    def save(self, path, page=("A4", "portrait"), margins_cm=2.2,
             footer_text=""):
        if page[1] == "landscape":
            pw, phh = 16838, 11906
        else:
            pw, phh = 11906, 16838
        mar = int(round(margins_cm / 2.54 * TWIP_IN))
        sect = ('<w:sectPr><w:footerReference w:type="default" r:id="rId9"/>'
                '<w:pgSz w:w="%d" w:h="%d"%s/>'
                '<w:pgMar w:top="%d" w:right="%d" w:bottom="%d" w:left="%d" '
                'w:header="567" w:footer="567" w:gutter="0"/>'
                '<w:cols w:space="708"/><w:docGrid w:linePitch="360"/></w:sectPr>'
                % (pw, phh, ' w:orient="landscape"' if page[1] == "landscape" else "",
                   mar, mar, mar, mar))

        document = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                    "<w:document %s><w:body>%s%s</w:body></w:document>"
                    % (NS, "".join(self.body), sect))

        parts = {}
        parts["word/document.xml"] = document
        parts["word/styles.xml"] = _styles()
        parts["word/numbering.xml"] = _numbering()
        parts["word/settings.xml"] = _settings()
        parts["word/footer1.xml"] = _footer(footer_text)

        rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
                '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/numbering" Target="numbering.xml"/>'
                '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>'
                '<Relationship Id="rId9" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>']
        media = {}
        for src, (rid, name, _w, _h) in self._images.items():
            rels.append('<Relationship Id="%s" Type="http://schemas.openxmlformats.org/'
                        'officeDocument/2006/relationships/image" Target="media/%s"/>'
                        % (rid, name))
            media["word/media/" + name] = open(src, "rb").read()
        rels.append("</Relationships>")
        parts["word/_rels/document.xml.rels"] = "".join(rels)

        parts["_rels/.rels"] = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
            '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
            "</Relationships>")

        parts["docProps/core.xml"] = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            "<dc:title>%s</dc:title><dc:subject>%s</dc:subject><dc:creator>%s</dc:creator>"
            "<cp:lastModifiedBy>%s</cp:lastModifiedBy>"
            "</cp:coreProperties>"
            % (esc(self.title), esc(self.subject), esc(self.author), esc(self.creator)))
        parts["docProps/app.xml"] = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
            'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
            "<Application>Kiro</Application></Properties>")

        ct = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
              '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
              '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
              '<Default Extension="xml" ContentType="application/xml"/>'
              '<Default Extension="png" ContentType="image/png"/>'
              '<Default Extension="jpeg" ContentType="image/jpeg"/>'
              '<Default Extension="jpg" ContentType="image/jpeg"/>'
              '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
              '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
              '<Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/>'
              '<Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>'
              '<Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>'
              '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
              '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>'
              "</Types>"]
        parts["[Content_Types].xml"] = "".join(ct)

        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", parts.pop("[Content_Types].xml"))
            for k in sorted(parts):
                z.writestr(k, parts[k])
            for k in sorted(media):
                z.writestr(k, media[k])
        import os
        return os.path.getsize(path)


# ------------------------------------------------------------ fixed parts
def _styles():
    def style(sid, name, based=None, nextd=None, ppr="", rpr="", quick=True,
              kind="paragraph"):
        return ('<w:style w:type="%s" w:styleId="%s"%s>'
                "<w:name w:val=%s/>%s%s%s%s</w:style>"
                % (kind, sid, ' w:default="1"' if sid == "Normal" else "",
                   quoteattr(name),
                   ('<w:basedOn w:val="%s"/>' % based) if based else "",
                   ('<w:next w:val="%s"/>' % nextd) if nextd else "",
                   ("<w:pPr>%s</w:pPr>" % ppr) if ppr else "",
                   ("<w:rPr>%s</w:rPr>" % rpr) if rpr else ""))

    body_font = ('<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri" '
                 'w:eastAsia="Calibri"/>')
    out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
           "<w:styles %s>" % NS,
           "<w:docDefaults><w:rPrDefault><w:rPr>%s"
           '<w:color w:val="000000"/><w:sz w:val="21"/><w:szCs w:val="21"/>'
           '<w:lang w:val="en-GB"/></w:rPr></w:rPrDefault>'
           '<w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="276" '
           'w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>' % body_font]
    out.append(style("Normal", "Normal"))
    # No pageBreakBefore here: the chapter eyebrow paragraph carries the break,
    # so the Heading 1 text itself is what lands in the table of contents.
    out.append(style("Heading1", "heading 1", "Normal", "Normal",
                     ppr='<w:keepNext/><w:spacing w:before="0" '
                         'w:after="240"/><w:outlineLvl w:val="0"/>',
                     rpr='<w:b/><w:sz w:val="40"/><w:szCs w:val="40"/>'))
    out.append(style("Heading2", "heading 2", "Normal", "Normal",
                     ppr='<w:keepNext/><w:keepLines/>'
                         '<w:pBdr><w:bottom w:val="single" w:sz="6" '
                         'w:space="4" w:color="808080"/></w:pBdr>'
                         '<w:spacing w:before="320" w:after="120"/>'
                         '<w:outlineLvl w:val="1"/>',
                     rpr='<w:b/><w:sz w:val="26"/><w:szCs w:val="26"/>'))
    out.append(style("Heading3", "heading 3", "Normal", "Normal",
                     ppr='<w:keepNext/><w:keepLines/><w:spacing w:before="240" '
                         'w:after="80"/><w:outlineLvl w:val="2"/>',
                     rpr='<w:b/><w:sz w:val="22"/><w:szCs w:val="22"/>'))
    out.append(style("Title", "Title", "Normal", "Normal",
                     ppr='<w:spacing w:before="0" w:after="120"/>',
                     rpr='<w:b/><w:sz w:val="64"/><w:szCs w:val="64"/>'))
    out.append(style("Subtitle", "Subtitle", "Normal", "Normal",
                     ppr='<w:spacing w:after="240"/>',
                     rpr='<w:sz w:val="30"/><w:szCs w:val="30"/>'))
    out.append(style("Eyebrow", "Eyebrow", "Normal", "Normal",
                     ppr='<w:keepNext/><w:spacing w:before="200" w:after="0"/>',
                     rpr='<w:b/><w:caps/><w:spacing w:val="40"/><w:sz w:val="16"/>'
                         '<w:szCs w:val="16"/>'))
    out.append(style("Caption", "caption", "Normal", "Normal",
                     ppr='<w:spacing w:before="40" w:after="200"/>'
                         '<w:jc w:val="center"/>',
                     rpr='<w:i/><w:sz w:val="17"/><w:szCs w:val="17"/>'))
    out.append(style("LegendItem", "Legend Item", "Normal", "Normal",
                     ppr='<w:tabs><w:tab w:val="left" w:pos="340"/></w:tabs>'
                         '<w:spacing w:before="0" w:after="40"/>'
                         '<w:ind w:left="340" w:hanging="340"/>',
                     rpr='<w:sz w:val="18"/><w:szCs w:val="18"/>'))
    out.append(style("NoteText", "Note Text", "Normal", "Normal",
                     ppr='<w:spacing w:before="0" w:after="0"/>',
                     rpr='<w:sz w:val="19"/><w:szCs w:val="19"/>'))
    out.append(style("ListParagraph", "List Paragraph", "Normal", "Normal",
                     ppr='<w:ind w:left="360"/><w:contextualSpacing/>'))
    out.append(style("TOCHeading", "TOC Heading", "Heading1", "Normal",
                     ppr='<w:spacing w:before="0" '
                         'w:after="200"/><w:outlineLvl w:val="9"/>',
                     rpr='<w:b/><w:sz w:val="32"/><w:szCs w:val="32"/>'))
    for lvl in (1, 2, 3):
        out.append(style("TOC%d" % lvl, "toc %d" % lvl, "Normal", "Normal",
                         ppr='<w:tabs><w:tab w:val="right" w:leader="dot" '
                             'w:pos="9400"/></w:tabs>'
                             '<w:spacing w:after="60"/><w:ind w:left="%d"/>'
                             % ((lvl - 1) * 220),
                         rpr='<w:sz w:val="20"/><w:szCs w:val="20"/>'))
    out.append('<w:style w:type="table" w:styleId="GuideTable">'
               '<w:name w:val="Guide Table"/>'
               '<w:tblPr><w:tblCellMar><w:top w:w="70" w:type="dxa"/>'
               '<w:left w:w="90" w:type="dxa"/><w:bottom w:w="70" w:type="dxa"/>'
               '<w:right w:w="90" w:type="dxa"/></w:tblCellMar></w:tblPr>'
               "</w:style>")
    out.append('<w:style w:type="character" w:styleId="Hyperlink">'
               '<w:name w:val="Hyperlink"/><w:rPr><w:u w:val="single"/></w:rPr>'
               "</w:style>")
    out.append("</w:styles>")
    return "".join(out)


def _numbering():
    def abstract(aid, fmt, text, font=None, indent=360):
        lvls = []
        for lvl in range(3):
            left = indent + lvl * 320
            f = ('<w:rPr><w:rFonts w:ascii="%s" w:hAnsi="%s" w:hint="default"/></w:rPr>'
                 % (font, font)) if font else ""
            lvls.append('<w:lvl w:ilvl="%d"><w:start w:val="1"/>'
                        '<w:numFmt w:val="%s"/><w:lvlText w:val="%s"/>'
                        '<w:lvlJc w:val="left"/><w:pPr><w:ind w:left="%d" '
                        'w:hanging="%d"/></w:pPr>%s</w:lvl>'
                        % (lvl, fmt, text.replace("%1", "%%%d" % (lvl + 1)),
                           left, 300, f))
        return ('<w:abstractNum w:abstractNumId="%d">'
                '<w:multiLevelType w:val="hybridMultilevel"/>'
                "%s</w:abstractNum>" % (aid, "".join(lvls)))

    out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n',
           "<w:numbering %s>" % NS]
    out.append(abstract(1, "bullet", "\u2022", font="Symbol"))
    out.append(abstract(2, "decimal", "%1."))
    out.append('<w:num w:numId="1"><w:abstractNumId w:val="1"/></w:num>')
    out.append('<w:num w:numId="2"><w:abstractNumId w:val="2"/></w:num>')
    out.append("</w:numbering>")
    return "".join(out)


def _settings():
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            "<w:settings %s>"
            '<w:zoom w:percent="100"/>'
            "<w:defaultTabStop w:val=\"720\"/>"
            "<w:characterSpacingControl w:val=\"doNotCompress\"/>"
            "<w:updateFields w:val=\"true\"/>"
            '<w:compat><w:compatSetting w:name="compatibilityMode" '
            'w:uri="http://schemas.microsoft.com/office/word" w:val="15"/></w:compat>'
            "</w:settings>" % NS)


def _footer(text):
    runs = (run(text, size=8) if text else "")
    runs += tab() + tab()
    runs += run("Page ", size=8)
    runs += ('<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
             '<w:r><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
             '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
             '<w:r><w:rPr><w:sz w:val="16"/></w:rPr><w:t>1</w:t></w:r>'
             '<w:r><w:fldChar w:fldCharType="end"/></w:r>')
    runs += run(" of ", size=8)
    runs += ('<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
             '<w:r><w:instrText xml:space="preserve"> NUMPAGES </w:instrText></w:r>'
             '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
             '<w:r><w:rPr><w:sz w:val="16"/></w:rPr><w:t>1</w:t></w:r>'
             '<w:r><w:fldChar w:fldCharType="end"/></w:r>')
    body = para(runs, border_bottom=False, before=0, after=0,
                tabs=[4700, 9400])
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            "<w:ftr %s>%s</w:ftr>" % (NS, body))


def toc_field(placeholder="Right-click here and choose Update Field to build the "
                          "table of contents."):
    return ('<w:p><w:pPr><w:tabs><w:tab w:val="right" w:leader="dot" w:pos="9400"/>'
            "</w:tabs></w:pPr>"
            '<w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r>'
            '<w:r><w:instrText xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText></w:r>'
            '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
            "%s"
            '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>'
            % run(placeholder, italic=True, size=9))
