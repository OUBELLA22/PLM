"""Minimal, dependency-free OOXML .pptx writer + layout preview rasterizer.

Design coordinates are in pixels on a 1280x720 canvas (16:9), converted to EMU.
"""
import os, re, shutil, zipfile, zlib, struct, math

PX = 9525                      # EMU per px (96 dpi)
CW, CH = 1280, 720             # design canvas
SLD_CX, SLD_CY = CW * PX, CH * PX

A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
NS = (' xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
      ' xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"'
      ' xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"')
FONT = 'Segoe UI'
MONO = 'Consolas'


def esc(s):
    return (s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
             .replace('"', '&quot;'))


# --------------------------------------------------------------------------- #
# shape spec helpers
# --------------------------------------------------------------------------- #
def shape(kind='rect', x=0, y=0, w=100, h=100, **kw):
    s = dict(kind=kind, x=x, y=y, w=w, h=h)
    s.update(kw)
    return s


def solid(c, a=100):
    return ('solid', c, a)


def grad(c1, c2, ang=90, a1=100, a2=100):
    return ('grad', c1, c2, ang, a1, a2)


def radial(c, a_center=20, a_edge=0):
    return ('radial', c, a_center, a_edge)


def run(t, sz=14, b=False, c='FFFFFF', a=100, font=None, spc=0, i=False,
        link=None, caps=False, u=False):
    return dict(t=t, sz=sz, b=b, c=c, a=a, font=font or FONT, spc=spc, i=i,
                link=link, caps=caps, u=u)


def para(runs, align='l', line=100, before=0, after=0, bullet=None, marL=0,
         indent=0):
    if isinstance(runs, dict):
        runs = [runs]
    return dict(runs=runs, align=align, line=line, before=before, after=after,
                bullet=bullet, marL=marL, indent=indent)


def text(x, y, w, h, paras, anchor='t', ins=(0, 0, 0, 0), wrap=True, name='txt',
         rot=0):
    if isinstance(paras, dict):
        paras = [paras]
    return shape('rect', x, y, w, h, text=paras, anchor=anchor, ins=ins,
                 fill=None, line=None, wrap=wrap, name=name, rot=rot)


# --------------------------------------------------------------------------- #
# XML fragments
# --------------------------------------------------------------------------- #
def _clr(c, a=100):
    inner = '' if a >= 100 else '<a:alpha val="%d"/>' % int(a * 1000)
    return '<a:srgbClr val="%s">%s</a:srgbClr>' % (c, inner) if inner else \
           '<a:srgbClr val="%s"/>' % c


def _fill(f):
    if f is None:
        return '<a:noFill/>'
    if f[0] == 'solid':
        return '<a:solidFill>%s</a:solidFill>' % _clr(f[1], f[2])
    if f[0] == 'grad':
        _, c1, c2, ang, a1, a2 = f
        return ('<a:gradFill flip="none" rotWithShape="1"><a:gsLst>'
                '<a:gs pos="0">%s</a:gs><a:gs pos="100000">%s</a:gs>'
                '</a:gsLst><a:lin ang="%d" scaled="0"/></a:gradFill>'
                % (_clr(c1, a1), _clr(c2, a2), int(ang * 60000) % 21600000))
    if f[0] == 'radial':
        _, c, ac, ae = f
        return ('<a:gradFill flip="none" rotWithShape="1"><a:gsLst>'
                '<a:gs pos="0">%s</a:gs><a:gs pos="100000">%s</a:gs></a:gsLst>'
                '<a:path path="circle"><a:fillToRect l="50000" t="50000" '
                'r="50000" b="50000"/></a:path></a:gradFill>'
                % (_clr(c, ac), _clr(c, ae)))
    raise ValueError(f)


def _ln(s):
    ln = s.get('line')
    if ln is None:
        return '' if s['kind'] == 'line' else '<a:ln><a:noFill/></a:ln>'
    c, wpx, a = (list(ln) + [100])[:3]
    extra = ''
    if s.get('dash'):
        extra += '<a:prstDash val="%s"/>' % s['dash']
    extra += '<a:round/>'
    if s.get('arrow'):
        extra += '<a:tailEnd type="triangle" w="med" len="med"/>'
    return ('<a:ln w="%d" cap="rnd"><a:solidFill>%s</a:solidFill>%s</a:ln>'
            % (int(wpx * 12700), _clr(c, a), extra))


def _effects(s):
    out = ''
    sh = s.get('shadow')
    if sh:
        blur, dist, alpha = sh if isinstance(sh, (tuple, list)) else (28, 10, 40)
        out += ('<a:outerShdw blurRad="%d" dist="%d" dir="5400000" '
                'rotWithShape="0">%s</a:outerShdw>'
                % (blur * PX, dist * PX, _clr('000814', alpha)))
    if s.get('glow'):
        c, radpx, alpha = s['glow']
        out += '<a:glow rad="%d">%s</a:glow>' % (radpx * PX, _clr(c, alpha))
    return '<a:effectLst>%s</a:effectLst>' % out if out else ''


def _geom(s):
    k = s['kind']
    prst = {'rect': 'rect', 'round': 'roundRect', 'ellipse': 'ellipse',
            'line': 'line', 'tri': 'triangle', 'chevron': 'homePlate',
            'pill': 'roundRect', 'donut': 'donut', 'plus': 'mathPlus',
            'arc': 'blockArc', 'trapezoid': 'trapezoid'}[k]
    av = ''
    if k in ('round', 'pill'):
        r = s.get('r', 10)
        m = max(1.0, min(s['w'], s['h']))
        adj = min(50000, int(100000.0 * r / m))
        av = '<a:gd name="adj" fmla="val %d"/>' % adj
    elif k == 'donut':
        av = '<a:gd name="adj" fmla="val %d"/>' % int(s.get('thick', 12000))
    return '<a:prstGeom prst="%s"><a:avLst>%s</a:avLst></a:prstGeom>' % (prst, av)


def _txbody(s, relmap):
    paras = s.get('text')
    if not paras:
        return ('<p:txBody><a:bodyPr wrap="square" lIns="0" tIns="0" rIns="0" '
                'bIns="0"/><a:lstStyle/><a:p><a:endParaRPr lang="en-US"/></a:p>'
                '</p:txBody>')
    l, t, rr, b = s.get('ins', (0, 0, 0, 0))
    bp = ('<a:bodyPr wrap="%s" lIns="%d" tIns="%d" rIns="%d" bIns="%d" '
          'rtlCol="0" anchor="%s"><a:noAutofit/></a:bodyPr>'
          % ('square' if s.get('wrap', True) else 'none',
             l * PX, t * PX, rr * PX, b * PX, s.get('anchor', 't')))
    out = []
    for p in paras:
        pr = ['<a:pPr algn="%s"' % p['align']]
        if p.get('marL'):
            pr.append(' marL="%d"' % (p['marL'] * PX))
        if p.get('indent'):
            pr.append(' indent="%d"' % (p['indent'] * PX))
        pr.append('>')
        if p.get('line', 100) != 100:
            pr.append('<a:lnSpc><a:spcPct val="%d"/></a:lnSpc>' % (p['line'] * 1000))
        if p.get('before'):
            pr.append('<a:spcBef><a:spcPts val="%d"/></a:spcBef>' % (p['before'] * 100))
        if p.get('after'):
            pr.append('<a:spcAft><a:spcPts val="%d"/></a:spcAft>' % (p['after'] * 100))
        if p.get('bullet'):
            ch, col = p['bullet']
            pr.append('<a:buClr>%s</a:buClr><a:buFont typeface="Arial" '
                      'panose="020B0604020202020204" pitchFamily="34" charset="0"/>'
                      '<a:buChar char="%s"/>' % (_clr(col), esc(ch)))
        else:
            pr.append('<a:buNone/>')
        pr.append('</a:pPr>')
        rs = []
        for r in p['runs']:
            rpr = ['<a:rPr lang="en-US" sz="%d"' % int(r['sz'] * 100)]
            if r['b']:
                rpr.append(' b="1"')
            if r['i']:
                rpr.append(' i="1"')
            if r['u']:
                rpr.append(' u="sng"')
            if r['spc']:
                rpr.append(' spc="%d"' % int(r['spc'] * 100))
            if r['caps']:
                rpr.append(' cap="all"')
            rpr.append(' dirty="0">')
            rpr.append('<a:solidFill>%s</a:solidFill>' % _clr(r['c'], r['a']))
            rpr.append('<a:latin typeface="%s"/><a:cs typeface="%s"/>'
                       % (r['font'], r['font']))
            if r['link']:
                rpr.append('<a:hlinkClick xmlns:r="http://schemas.openxmlformats.org'
                           '/officeDocument/2006/relationships" r:id="%s"/>'
                           % relmap['link:' + r['link']])
            rpr.append('</a:rPr>')
            rs.append('<a:r>%s<a:t>%s</a:t></a:r>' % (''.join(rpr), esc(r['t'])))
        if not rs:
            rs.append('<a:endParaRPr lang="en-US"/>')
        out.append('<a:p>%s%s</a:p>' % (''.join(pr), ''.join(rs)))
    return '<p:txBody>%s<a:lstStyle/>%s</p:txBody>' % (bp, ''.join(out))


def _xfrm(s):
    at = ''
    if s.get('rot'):
        at += ' rot="%d"' % (int(s['rot'] * 60000) % 21600000)
    if s.get('flipH'):
        at += ' flipH="1"'
    if s.get('flipV'):
        at += ' flipV="1"'
    return ('<a:xfrm%s><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
            % (at, round(s['x'] * PX), round(s['y'] * PX),
               round(s['w'] * PX), round(max(0, s['h']) * PX)))


def _shape_xml(s, sid, relmap):
    if s['kind'] == 'pic':
        src = ''
        if s.get('crop'):
            l, t, r, b = s['crop']
            src = ('<a:srcRect l="%d" t="%d" r="%d" b="%d"/>'
                   % (l * 1000, t * 1000, r * 1000, b * 1000))
        return ('<p:pic><p:nvPicPr><p:cNvPr id="%d" name="%s"/><p:cNvPicPr>'
                '<a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/>'
                '</p:nvPicPr><p:blipFill><a:blip r:embed="%s"/>%s<a:stretch>'
                '<a:fillRect/></a:stretch></p:blipFill><p:spPr>%s%s%s%s'
                '</p:spPr></p:pic>'
                % (sid, s.get('name', 'Picture %d' % sid),
                   relmap['img:' + s['img']], src, _xfrm(s),
                   _geom(dict(s, kind='round' if s.get('r') else 'rect')),
                   _ln(s), _effects(s)))
    return ('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="%s"/><p:cNvSpPr%s/>'
            '<p:nvPr/></p:nvSpPr><p:spPr>%s%s%s%s%s</p:spPr>%s</p:sp>'
            % (sid, s.get('name', 'Shape %d' % sid),
               ' txBox="1"' if s['kind'] == 'rect' and s.get('fill') is None
               and s.get('text') else '',
               _xfrm(s), _geom(s), _fill(s.get('fill')), _ln(s), _effects(s),
               _txbody(s, relmap)))


# --------------------------------------------------------------------------- #
# package writer
# --------------------------------------------------------------------------- #
CT = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Default Extension="png" ContentType="image/png"/>
<Default Extension="jpeg" ContentType="image/jpeg"/>
<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
{slides}
<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
<Override PartName="/ppt/presProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"/>
<Override PartName="/ppt/viewProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"/>
<Override PartName="/ppt/tableStyles.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>'''

ROOT_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''

MASTER = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster{ns}><p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="081428"/></a:solidFill><a:effectLst/></p:bgPr></p:bg><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/><p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle><a:lvl1pPr algn="l"><a:defRPr sz="3200" b="1"><a:solidFill><a:schemeClr val="lt1"/></a:solidFill><a:latin typeface="+mj-lt"/></a:defRPr></a:lvl1pPr></p:titleStyle><p:bodyStyle><a:lvl1pPr algn="l"><a:defRPr sz="1600"><a:solidFill><a:schemeClr val="lt1"/></a:solidFill><a:latin typeface="+mn-lt"/></a:defRPr></a:lvl1pPr></p:bodyStyle><p:otherStyle><a:lvl1pPr algn="l"><a:defRPr sz="1400"><a:solidFill><a:schemeClr val="lt1"/></a:solidFill><a:latin typeface="+mn-lt"/></a:defRPr></a:lvl1pPr></p:otherStyle></p:txStyles></p:sldMaster>'''

MASTER_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme" Target="../theme/theme1.xml"/>
</Relationships>'''

LAYOUT = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout{ns} type="blank" preserve="1"><p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'''

LAYOUT_RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster" Target="../slideMasters/slideMaster1.xml"/>
</Relationships>'''


def write_pptx(slides, images, theme_src, out_path, title, author):
    """slides: list of (list_of_shapes). images: {name: bytes}."""
    parts = {}
    parts['[Content_Types].xml'] = CT.format(slides='\n'.join(
        '<Override PartName="/ppt/slides/slide%d.xml" ContentType="application/'
        'vnd.openxmlformats-officedocument.presentationml.slide+xml"/>' % (i + 1)
        for i in range(len(slides))))
    parts['_rels/.rels'] = ROOT_RELS
    parts['ppt/slideMasters/slideMaster1.xml'] = MASTER.format(ns=NS)
    parts['ppt/slideMasters/_rels/slideMaster1.xml.rels'] = MASTER_RELS
    parts['ppt/slideLayouts/slideLayout1.xml'] = LAYOUT.format(ns=NS)
    parts['ppt/slideLayouts/_rels/slideLayout1.xml.rels'] = LAYOUT_RELS
    parts['ppt/theme/theme1.xml'] = theme_src
    parts['ppt/presProps.xml'] = ('<?xml version="1.0" encoding="UTF-8" '
                                  'standalone="yes"?>\n<p:presentationPr%s/>' % NS)
    parts['ppt/viewProps.xml'] = ('<?xml version="1.0" encoding="UTF-8" '
                                  'standalone="yes"?>\n<p:viewPr%s/>' % NS)
    parts['ppt/tableStyles.xml'] = ('<?xml version="1.0" encoding="UTF-8" '
        'standalone="yes"?>\n<a:tblStyleLst xmlns:a="%s" '
        'def="{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}"/>' % A)
    parts['docProps/core.xml'] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/'
        '2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/"'
        ' xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org'
        '/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
        '<dc:title>%s</dc:title><dc:creator>%s</dc:creator>'
        '<cp:lastModifiedBy>%s</cp:lastModifiedBy>'
        '<dcterms:created xsi:type="dcterms:W3CDTF">2026-09-10T00:00:00Z</dcterms:created>'
        '<dcterms:modified xsi:type="dcterms:W3CDTF">2026-09-10T00:00:00Z</dcterms:modified>'
        '</cp:coreProperties>' % (esc(title), esc(author), esc(author)))
    parts['docProps/app.xml'] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/'
        'extended-properties" xmlns:vt="http://schemas.openxmlformats.org/'
        'officeDocument/2006/docPropsVTypes"><Application>Microsoft Office '
        'PowerPoint</Application><Slides>%d</Slides><Company></Company>'
        '</Properties>' % len(slides))

    used_images = set()
    for i, shapes in enumerate(slides):
        n = i + 1
        rels, relmap, rid = [], {}, 1
        rels.append('<Relationship Id="rId1" Type="http://schemas.openxmlformats'
                    '.org/officeDocument/2006/relationships/slideLayout" '
                    'Target="../slideLayouts/slideLayout1.xml"/>')
        keys = []
        for s in shapes:
            if s['kind'] == 'pic':
                keys.append('img:' + s['img'])
            for p in s.get('text') or []:
                for r in p['runs']:
                    if r['link']:
                        keys.append('link:' + r['link'])
        for k in keys:
            if k in relmap:
                continue
            rid += 1
            relmap[k] = 'rId%d' % rid
            if k.startswith('img:'):
                used_images.add(k[4:])
                rels.append('<Relationship Id="rId%d" Type="http://schemas.'
                            'openxmlformats.org/officeDocument/2006/relationships'
                            '/image" Target="../media/%s"/>' % (rid, k[4:]))
            else:
                rels.append('<Relationship Id="rId%d" Type="http://schemas.'
                            'openxmlformats.org/officeDocument/2006/relationships'
                            '/hyperlink" Target="%s" TargetMode="External"/>'
                            % (rid, esc(k[5:])))
        body = ''.join(_shape_xml(s, j + 2, relmap) for j, s in enumerate(shapes))
        parts['ppt/slides/slide%d.xml' % n] = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<p:sld%s><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/>'
            '<p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm>'
            '<a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/>'
            '<a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>%s</p:spTree></p:cSld>'
            '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>'
            '<p:transition spd="med"><p:fade/></p:transition></p:sld>' % (NS, body))
        parts['ppt/slides/_rels/slide%d.xml.rels' % n] = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/'
            'relationships">%s</Relationships>' % ''.join(rels))

    prels = ['<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/'
             'officeDocument/2006/relationships/slideMaster" '
             'Target="slideMasters/slideMaster1.xml"/>']
    sldids = []
    for i in range(len(slides)):
        rid = i + 2
        prels.append('<Relationship Id="rId%d" Type="http://schemas.openxmlformats'
                     '.org/officeDocument/2006/relationships/slide" '
                     'Target="slides/slide%d.xml"/>' % (rid, i + 1))
        sldids.append('<p:sldId id="%d" r:id="rId%d"/>' % (256 + i, rid))
    base = len(slides) + 2
    for j, (nm, tgt) in enumerate([('presProps', 'presProps.xml'),
                                   ('viewProps', 'viewProps.xml'),
                                   ('theme', 'theme/theme1.xml'),
                                   ('tableStyles', 'tableStyles.xml')]):
        prels.append('<Relationship Id="rId%d" Type="http://schemas.openxmlformats'
                     '.org/officeDocument/2006/relationships/%s" Target="%s"/>'
                     % (base + j, nm, tgt))
    parts['ppt/_rels/presentation.xml.rels'] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/'
        'relationships">%s</Relationships>' % ''.join(prels))
    parts['ppt/presentation.xml'] = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<p:presentation%s saveSubsetFonts="1"><p:sldMasterIdLst>'
        '<p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>'
        '<p:sldIdLst>%s</p:sldIdLst><p:sldSz cx="%d" cy="%d"/>'
        '<p:notesSz cx="6858000" cy="9144000"/></p:presentation>'
        % (NS, ''.join(sldids), SLD_CX, SLD_CY))

    with zipfile.ZipFile(out_path, 'w', zipfile.ZIP_DEFLATED) as z:
        for name in ['[Content_Types].xml', '_rels/.rels']:
            z.writestr(name, parts.pop(name))
        for name, data in sorted(parts.items()):
            z.writestr(name, data)
        for name in sorted(used_images):
            z.writestr('ppt/media/' + name, images[name])
    return sorted(used_images)


# --------------------------------------------------------------------------- #
# text metrics (approximate Segoe UI) + validation
# --------------------------------------------------------------------------- #
_NARROW = "ijltfrI'!|.,;:()[]{}/\\ "
_WIDE = "MWmw@"


def char_w(ch, sz, bold):
    if ch == ' ':
        f = 0.26
    elif ch in _NARROW:
        f = 0.32
    elif ch in _WIDE:
        f = 0.86
    elif ch.isdigit():
        f = 0.56
    elif ch.isupper():
        f = 0.66
    else:
        f = 0.53
    return f * sz * (1.045 if bold else 1.0) * 1.333   # pt -> px


def line_width(runs):
    return sum(sum(char_w(c, r['sz'], r['b']) for c in r['t']) +
               len(r['t']) * r['spc'] * 1.333 for r in runs)


def wrap_para(p, width):
    """Return list of rendered lines [(text, width, size)] for a paragraph."""
    words, cur = [], []
    for r in p['runs']:
        for tok in re.split(r'(\s+)', r['t']):
            if tok:
                words.append((tok, r))
    lines, cur, curw = [], [], 0.0
    for tok, r in words:
        w = sum(char_w(c, r['sz'], r['b']) for c in tok) + len(tok) * r['spc'] * 1.333
        if cur and curw + w > width and tok.strip():
            lines.append((''.join(t for t, _ in cur).strip(), curw,
                          max(rr['sz'] for _, rr in cur)))
            cur, curw = [(tok, r)], w
        else:
            cur.append((tok, r))
            curw += w
    if cur:
        lines.append((''.join(t for t, _ in cur).strip(), curw,
                      max(rr['sz'] for _, rr in cur)))
    if not lines:
        lines = [('', 0, max((r['sz'] for r in p['runs']), default=12))]
    return lines


def measure(s):
    """Estimated (lines, total_height_px) for a shape's text."""
    l, t, r, b = s.get('ins', (0, 0, 0, 0))
    width = max(10, s['w'] - l - r)
    total, all_lines = 0.0, []
    for p in s.get('text') or []:
        lines = wrap_para(p, width) if s.get('wrap', True) else [
            (''.join(x['t'] for x in p['runs']), line_width(p['runs']),
             max(x['sz'] for x in p['runs']))]
        total += p.get('before', 0) * 1.333 + p.get('after', 0) * 1.333
        for txt, w, sz in lines:
            lh = sz * 1.333 * (p.get('line', 100) / 100.0) * 1.2
            total += lh
            all_lines.append((txt, w, sz, lh))
    return all_lines, total


def validate(slides):
    problems = []
    for i, shapes in enumerate(slides):
        for s in shapes:
            tag = 'S%02d %s' % (i + 1, s.get('name', s['kind']))
            if s.get('bleed'):
                pass
            elif s['x'] < 0 or s['y'] < 0 or s['x'] + s['w'] > CW + 0.6 or \
               s['y'] + s['h'] > CH + 0.6:
                problems.append('%s: outside canvas (%.0f,%.0f %.0fx%.0f)'
                                % (tag, s['x'], s['y'], s['w'], s['h']))
            if s.get('text'):
                lines, h = measure(s)
                l, t, r, b = s.get('ins', (0, 0, 0, 0))
                avail_w = s['w'] - l - r
                if h > s['h'] - t - b + 1.5:
                    problems.append('%s: text %.0fpx > box %.0fpx | %r'
                                    % (tag, h, s['h'] - t - b,
                                       ' / '.join(x[0] for x in lines)[:70]))
                for txt, w, sz, lh in lines:
                    if not s.get('wrap', True) and w > avail_w + 2:
                        problems.append('%s: nowrap line %.0f>%.0f %r'
                                        % (tag, w, avail_w, txt[:50]))
    return problems
