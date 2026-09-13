# -*- coding: utf-8 -*-
"""
pptxlite - a tiny, dependency-free .pptx writer.

The sandbox has no PyPI access, so this module hand-builds the OOXML
(PresentationML + DrawingML) parts and zips them into a .pptx.

Only what this deck needs is implemented: gradient slide backgrounds,
rounded/plain/triangle shapes with solid fills + borders, rich text boxes
and per-slide speaker notes.
"""

import zipfile

EMU_PER_INCH = 914400

NS = (
    'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
)

XML_DECL = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'

ALIGN = {"l": "l", "c": "ctr", "r": "r", "j": "just"}


def emu(inches):
    return int(round(float(inches) * EMU_PER_INCH))


def esc(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# --------------------------------------------------------------------------
# text model
# --------------------------------------------------------------------------

def run(text, size=14, color="FFFFFF", bold=False, italic=False,
        font="Segoe UI", spc=None, caps=False, alpha=None):
    """A single stretch of formatted text inside a paragraph."""
    return {
        "text": text, "size": size, "color": color, "bold": bold,
        "italic": italic, "font": font, "spc": spc, "caps": caps,
        "alpha": alpha,
    }


def para(text=None, size=14, color="FFFFFF", bold=False, italic=False,
         font="Segoe UI", align="l", spc=None, caps=False, alpha=None,
         before=0, after=0, line=None, runs=None):
    """A paragraph. Either pass `text` (single run) or `runs` (list of run())."""
    if runs is None:
        runs = [] if text is None else [
            run(text, size, color, bold, italic, font, spc, caps, alpha)
        ]
    return {
        "runs": runs, "align": align, "before": before, "after": after,
        "line": line, "size": size, "color": color, "font": font,
    }


def _run_xml(r):
    attrs = ['lang="fr-FR"', 'sz="%d"' % int(r["size"] * 100), 'dirty="0"']
    if r["bold"]:
        attrs.append('b="1"')
    if r["italic"]:
        attrs.append('i="1"')
    if r["spc"] is not None:
        attrs.append('spc="%d"' % int(r["spc"] * 100))
    if r["caps"]:
        attrs.append('cap="all"')
    return (
        '<a:r><a:rPr %s>%s'
        '<a:latin typeface="%s"/><a:cs typeface="%s"/>'
        '</a:rPr><a:t>%s</a:t></a:r>'
    ) % (" ".join(attrs), solid(r["color"], r.get("alpha")),
         r["font"], r["font"], esc(r["text"]))


def _para_xml(p):
    bits = []
    if p["line"] is not None:
        bits.append('<a:lnSpc><a:spcPct val="%d"/></a:lnSpc>' % int(p["line"] * 100000))
    if p["before"]:
        bits.append('<a:spcBef><a:spcPts val="%d"/></a:spcBef>' % int(p["before"] * 100))
    if p["after"]:
        bits.append('<a:spcAft><a:spcPts val="%d"/></a:spcAft>' % int(p["after"] * 100))
    bits.append("<a:buNone/>")
    pPr = '<a:pPr marL="0" indent="0" algn="%s">%s</a:pPr>' % (
        ALIGN[p["align"]], "".join(bits)
    )
    body = "".join(_run_xml(r) for r in p["runs"])
    if not body:
        body = ('<a:endParaRPr lang="fr-FR" sz="%d"><a:latin typeface="%s"/>'
                "</a:endParaRPr>") % (int(p["size"] * 100), p["font"])
    return "<a:p>%s%s</a:p>" % (pPr, body)


# --------------------------------------------------------------------------
# fills
# --------------------------------------------------------------------------

def _srgb(color, alpha=None):
    inner = "" if alpha is None else '<a:alpha val="%d"/>' % int(alpha * 1000)
    return '<a:srgbClr val="%s">%s</a:srgbClr>' % (color, inner) if inner \
        else '<a:srgbClr val="%s"/>' % color


def solid(color, alpha=None):
    return "<a:solidFill>%s</a:solidFill>" % _srgb(color, alpha)


def gradient(stops, angle=315):
    """stops: list of (position 0..100, hex color[, alpha percent])."""
    gs = []
    for stop in stops:
        pos, color = stop[0], stop[1]
        alpha = stop[2] if len(stop) > 2 else None
        gs.append('<a:gs pos="%d">%s</a:gs>' % (int(pos * 1000), _srgb(color, alpha)))
    return (
        '<a:gradFill rotWithShape="1"><a:gsLst>%s</a:gsLst>'
        '<a:lin ang="%d" scaled="0"/></a:gradFill>'
    ) % ("".join(gs), int(angle % 360) * 60000)


# --------------------------------------------------------------------------
# slide
# --------------------------------------------------------------------------

class Slide(object):
    def __init__(self, background=None, notes=""):
        self.background = background
        self.notes = notes
        self._shapes = []
        self._next_id = 1

    def _id(self):
        self._next_id += 1
        return self._next_id

    # -- primitives --------------------------------------------------------

    def shape(self, x, y, w, h, geom="rect", radius=None, fill=None,
              alpha=None, gradient_fill=None, line=None, line_alpha=None,
              line_w=1.0, dash=None, rot=None, paras=None, anchor="t",
              pad=(0.0, 0.0, 0.0, 0.0), align=None, name=None):
        sid = self._id()
        xfrm_attrs = "" if rot is None else ' rot="%d"' % int(rot * 60000)
        xfrm = (
            '<a:xfrm%s><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
        ) % (xfrm_attrs, emu(x), emu(y), emu(w), emu(h))

        if radius is not None:
            geometry = (
                '<a:prstGeom prst="%s"><a:avLst>'
                '<a:gd name="adj" fmla="val %d"/></a:avLst></a:prstGeom>'
            ) % (geom, int(radius * 100000))
        else:
            geometry = '<a:prstGeom prst="%s"><a:avLst/></a:prstGeom>' % geom

        if gradient_fill is not None:
            fill_xml = gradient_fill
        elif fill is not None:
            fill_xml = solid(fill, alpha)
        else:
            fill_xml = "<a:noFill/>"

        if line is not None:
            dash_xml = '<a:prstDash val="%s"/>' % dash if dash else '<a:prstDash val="solid"/>'
            ln = '<a:ln w="%d" cap="flat" cmpd="sng" algn="ctr">%s%s</a:ln>' % (
                int(line_w * 12700), solid(line, line_alpha), dash_xml
            )
        else:
            ln = '<a:ln><a:noFill/></a:ln>'

        t, rgt, b, lft = pad if len(pad) == 4 else (0, 0, 0, 0)
        body_attrs = (
            'wrap="square" lIns="%d" tIns="%d" rIns="%d" bIns="%d" anchor="%s"'
        ) % (emu(lft), emu(t), emu(rgt), emu(b), anchor)

        if paras:
            if align:
                paras = [dict(p, align=align) for p in paras]
            txt = "".join(_para_xml(p) for p in paras)
        else:
            txt = "<a:p><a:pPr/><a:endParaRPr lang=\"fr-FR\"/></a:p>"

        self._shapes.append(
            '<p:sp><p:nvSpPr><p:cNvPr id="%d" name="%s"/><p:cNvSpPr/><p:nvPr/>'
            '</p:nvSpPr><p:spPr>%s%s%s%s</p:spPr>'
            '<p:txBody><a:bodyPr %s><a:noAutofit/></a:bodyPr><a:lstStyle/>%s'
            "</p:txBody></p:sp>"
            % (sid, esc(name or "Shape %d" % sid), xfrm, geometry, fill_xml, ln,
               body_attrs, txt)
        )

    def text(self, x, y, w, h, paras, anchor="t", align=None, name=None):
        self.shape(x, y, w, h, paras=paras, anchor=anchor, align=align,
                   name=name or "Text")

    # -- part serialisation ------------------------------------------------

    def xml(self):
        if self.background is not None:
            bg = "<p:bg><p:bgPr>%s<a:effectLst/></p:bgPr></p:bg>" % self.background
        else:
            bg = ""
        return (
            XML_DECL
            + '<p:sld %s><p:cSld>%s<p:spTree>'
              '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/>'
              "</p:nvGrpSpPr>"
              '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
              '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
              "%s</p:spTree></p:cSld>"
              "<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>"
            % (NS, bg, "".join(self._shapes))
        )

    def notes_xml(self):
        lines = self.notes.split("\n") if self.notes else [""]
        body = []
        for ln in lines:
            if ln.strip():
                body.append(
                    '<a:p><a:pPr/><a:r><a:rPr lang="fr-FR" dirty="0"/>'
                    "<a:t>%s</a:t></a:r></a:p>" % esc(ln)
                )
            else:
                body.append('<a:p><a:pPr/><a:endParaRPr lang="fr-FR"/></a:p>')
        return (
            XML_DECL
            + '<p:notes %s><p:cSld><p:spTree>'
              '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/>'
              "</p:nvGrpSpPr>"
              '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
              '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
              '<p:sp><p:nvSpPr><p:cNvPr id="2" name="Notes Placeholder 1"/>'
              '<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
              '<p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr>'
              '<p:spPr><a:xfrm><a:off x="685800" y="4343400"/>'
              '<a:ext cx="5486400" cy="4114800"/></a:xfrm></p:spPr>'
              "<p:txBody><a:bodyPr/><a:lstStyle/>%s</p:txBody></p:sp>"
              "</p:spTree></p:cSld>"
              "<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>"
            % (NS, "".join(body))
        )


# --------------------------------------------------------------------------
# presentation
# --------------------------------------------------------------------------

def _lvl_body(size, color):
    """The nine <a:lvlNpPr> children shared by every text-style container."""
    out = []
    for i in range(1, 10):
        name = "lvl%dpPr" % i
        out.append(
            '<a:%s marL="0" algn="l"><a:defRPr sz="%d">'
            '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>'
            '<a:latin typeface="Segoe UI"/></a:defRPr></a:%s>'
            % (name, size, color, name)
        )
    return "".join(out)


def _levels(tag, size, color):
    return "<p:%s>%s</p:%s>" % (tag, _lvl_body(size, color), tag)


THEME = XML_DECL + (
    '<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'name="KATATOOL"><a:themeElements>'
    '<a:clrScheme name="KATATOOL">'
    '<a:dk1><a:srgbClr val="0A1A2C"/></a:dk1>'
    '<a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>'
    '<a:dk2><a:srgbClr val="0E2440"/></a:dk2>'
    '<a:lt2><a:srgbClr val="E7EEF6"/></a:lt2>'
    '<a:accent1><a:srgbClr val="5B9DF9"/></a:accent1>'
    '<a:accent2><a:srgbClr val="22D3EE"/></a:accent2>'
    '<a:accent3><a:srgbClr val="34D399"/></a:accent3>'
    '<a:accent4><a:srgbClr val="F59E0B"/></a:accent4>'
    '<a:accent5><a:srgbClr val="A78BFA"/></a:accent5>'
    '<a:accent6><a:srgbClr val="F472B6"/></a:accent6>'
    '<a:hlink><a:srgbClr val="22D3EE"/></a:hlink>'
    '<a:folHlink><a:srgbClr val="A78BFA"/></a:folHlink>'
    "</a:clrScheme>"
    '<a:fontScheme name="Segoe UI">'
    '<a:majorFont><a:latin typeface="Segoe UI"/><a:ea typeface=""/>'
    '<a:cs typeface=""/></a:majorFont>'
    '<a:minorFont><a:latin typeface="Segoe UI"/><a:ea typeface=""/>'
    '<a:cs typeface=""/></a:minorFont>'
    "</a:fontScheme>"
    '<a:fmtScheme name="KATATOOL">'
    "<a:fillStyleLst>"
    + '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>' * 3
    + "</a:fillStyleLst><a:lnStyleLst>"
    + (
        '<a:ln w="9525" cap="flat" cmpd="sng" algn="ctr">'
        '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
        '<a:prstDash val="solid"/></a:ln>'
    ) * 3
    + "</a:lnStyleLst><a:effectStyleLst>"
    + "<a:effectStyle><a:effectLst/></a:effectStyle>" * 3
    + "</a:effectStyleLst><a:bgFillStyleLst>"
    + '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>' * 3
    + "</a:bgFillStyleLst></a:fmtScheme>"
    "</a:themeElements></a:theme>"
)

EMPTY_TREE = (
    '<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/>'
    "</p:nvGrpSpPr>"
    '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
    '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
    "</p:spTree>"
)

CLR_MAP = (
    '<p:clrMap bg1="dk1" tx1="lt1" bg2="dk2" tx2="lt2" accent1="accent1" '
    'accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" '
    'accent6="accent6" hlink="hlink" folHlink="folHlink"/>'
)

SLIDE_MASTER = XML_DECL + (
    '<p:sldMaster %s><p:cSld>'
    '<p:bg><p:bgPr><a:solidFill><a:srgbClr val="0A1A2C"/></a:solidFill>'
    "<a:effectLst/></p:bgPr></p:bg>%s</p:cSld>%s"
    '<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/>'
    "</p:sldLayoutIdLst><p:txStyles>%s%s%s</p:txStyles></p:sldMaster>"
) % (
    NS, EMPTY_TREE, CLR_MAP,
    _levels("titleStyle", 4000, "FFFFFF"),
    _levels("bodyStyle", 1400, "FFFFFF"),
    _levels("otherStyle", 1400, "FFFFFF"),
)

SLIDE_LAYOUT = XML_DECL + (
    '<p:sldLayout %s type="blank" preserve="1"><p:cSld name="Vide">%s</p:cSld>'
    "<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>"
) % (NS, EMPTY_TREE)

NOTES_MASTER = XML_DECL + (
    '<p:notesMaster %s><p:cSld>'
    '<p:bg><p:bgPr><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>'
    "<a:effectLst/></p:bgPr></p:bg>"
    '<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/>'
    "</p:nvGrpSpPr>"
    '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/>'
    '<a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'
    '<p:sp><p:nvSpPr><p:cNvPr id="2" name="Notes Placeholder 1"/>'
    '<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr>'
    '<p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr>'
    '<p:spPr><a:xfrm><a:off x="685800" y="4343400"/>'
    '<a:ext cx="5486400" cy="4114800"/></a:xfrm>'
    '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
    '<p:txBody><a:bodyPr vert="horz" wrap="square"/><a:lstStyle/>'
    '<a:p><a:pPr/><a:endParaRPr lang="fr-FR"/></a:p></p:txBody></p:sp>'
    "</p:spTree></p:cSld>%s<p:notesStyle>%s</p:notesStyle></p:notesMaster>"
) % (NS, CLR_MAP, _lvl_body(1200, "000000"))

PRES_PROPS = XML_DECL + '<p:presentationPr %s/>' % NS


class Presentation(object):
    def __init__(self, width=13.333, height=7.5):
        self.width = width
        self.height = height
        self.slides = []

    def add_slide(self, background=None, notes=""):
        s = Slide(background=background, notes=notes)
        self.slides.append(s)
        return s

    # ------------------------------------------------------------------

    def _content_types(self):
        ov = [
            '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>',
            '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>',
            '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>',
            '<Override PartName="/ppt/notesMasters/notesMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesMaster+xml"/>',
            '<Override PartName="/ppt/presProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"/>',
            '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>',
            '<Override PartName="/ppt/theme/theme2.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>',
            '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
            '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>',
        ]
        for i in range(1, len(self.slides) + 1):
            ov.append(
                '<Override PartName="/ppt/slides/slide%d.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>' % i
            )
            ov.append(
                '<Override PartName="/ppt/notesSlides/notesSlide%d.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"/>' % i
            )
        return (
            XML_DECL
            + '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Default Extension="png" ContentType="image/png"/>'
            '<Default Extension="jpeg" ContentType="image/jpeg"/>'
            '<Default Extension="jpg" ContentType="image/jpeg"/>'
            "%s</Types>" % "".join(ov)
        )

    def _root_rels(self):
        return XML_DECL + (
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
            '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>'
            "</Relationships>"
        )

    def _presentation(self):
        n = len(self.slides)
        ids = "".join(
            '<p:sldId id="%d" r:id="rId%d"/>' % (255 + i, i + 1)
            for i in range(1, n + 1)
        )
        return XML_DECL + (
            '<p:presentation %s saveSubsetFonts="1">'
            '<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/>'
            "</p:sldMasterIdLst>"
            '<p:notesMasterIdLst><p:notesMasterId r:id="rId%d"/></p:notesMasterIdLst>'
            "<p:sldIdLst>%s</p:sldIdLst>"
            '<p:sldSz cx="%d" cy="%d"/><p:notesSz cx="6858000" cy="9144000"/>'
            "</p:presentation>"
        ) % (NS, n + 2, ids, emu(self.width), emu(self.height))

    def _presentation_rels(self):
        n = len(self.slides)
        rels = [
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="slideMasters/slideMaster1.xml"/>'
        ]
        for i in range(1, n + 1):
            rels.append(
                '<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide%d.xml"/>'
                % (i + 1, i)
            )
        rels.append(
            '<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster" Target="notesMasters/notesMaster1.xml"/>'
            % (n + 2)
        )
        rels.append(
            '<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps" Target="presProps.xml"/>'
            % (n + 3)
        )
        rels.append(
            '<Relationship Id="rId%d" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="theme/theme1.xml"/>'
            % (n + 4)
        )
        return XML_DECL + (
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">%s</Relationships>'
            % "".join(rels)
        )

    def _core(self, title, author):
        return XML_DECL + (
            '<cp:coreProperties '
            'xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" '
            'xmlns:dcterms="http://purl.org/dc/terms/" '
            'xmlns:dcmitype="http://purl.org/dc/dcmitype/" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            # CT_CoreProperties is an xsd:sequence - keep this order.
            '<dcterms:created xsi:type="dcterms:W3CDTF">2026-01-01T00:00:00Z</dcterms:created>'
            "<dc:creator>%s</dc:creator>"
            "<cp:lastModifiedBy>%s</cp:lastModifiedBy>"
            '<dcterms:modified xsi:type="dcterms:W3CDTF">2026-01-01T00:00:00Z</dcterms:modified>'
            "<cp:revision>1</cp:revision>"
            "<dc:title>%s</dc:title></cp:coreProperties>"
        ) % (esc(author), esc(author), esc(title))

    def _app(self):
        # CT_Properties is an xsd:sequence: PresentationFormat, Paragraphs,
        # Slides, Notes, ... Application, AppVersion.
        return XML_DECL + (
            '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" '
            'xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">'
            "<PresentationFormat>Grand écran</PresentationFormat>"
            "<Paragraphs>0</Paragraphs><Slides>%d</Slides><Notes>%d</Notes>"
            "<Application>Microsoft Office PowerPoint</Application>"
            "<AppVersion>16.0000</AppVersion>"
            "</Properties>" % (len(self.slides), len(self.slides))
        )

    # ------------------------------------------------------------------

    def save(self, path, title="Présentation", author="Youssef OUBELLA"):
        z = zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED)

        def w(name, data):
            z.writestr(name, data.encode("utf-8"))

        w("[Content_Types].xml", self._content_types())
        w("_rels/.rels", self._root_rels())
        w("docProps/core.xml", self._core(title, author))
        w("docProps/app.xml", self._app())
        w("ppt/presentation.xml", self._presentation())
        w("ppt/_rels/presentation.xml.rels", self._presentation_rels())
        w("ppt/presProps.xml", PRES_PROPS)
        w("ppt/theme/theme1.xml", THEME)
        w("ppt/theme/theme2.xml", THEME)
        w("ppt/slideMasters/slideMaster1.xml", SLIDE_MASTER)
        w(
            "ppt/slideMasters/_rels/slideMaster1.xml.rels",
            XML_DECL
            + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
            '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>'
            "</Relationships>",
        )
        w("ppt/slideLayouts/slideLayout1.xml", SLIDE_LAYOUT)
        w(
            "ppt/slideLayouts/_rels/slideLayout1.xml.rels",
            XML_DECL
            + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>'
            "</Relationships>",
        )
        w("ppt/notesMasters/notesMaster1.xml", NOTES_MASTER)
        w(
            "ppt/notesMasters/_rels/notesMaster1.xml.rels",
            XML_DECL
            + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme2.xml"/>'
            "</Relationships>",
        )

        for i, s in enumerate(self.slides, start=1):
            w("ppt/slides/slide%d.xml" % i, s.xml())
            w(
                "ppt/slides/_rels/slide%d.xml.rels" % i,
                XML_DECL
                + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
                '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide" Target="../notesSlides/notesSlide%d.xml"/>'
                "</Relationships>" % i,
            )
            w("ppt/notesSlides/notesSlide%d.xml" % i, s.notes_xml())
            w(
                "ppt/notesSlides/_rels/notesSlide%d.xml.rels" % i,
                XML_DECL
                + '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesMaster" Target="../notesMasters/notesMaster1.xml"/>'
                '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="../slides/slide%d.xml"/>'
                "</Relationships>" % i,
            )

        z.close()
