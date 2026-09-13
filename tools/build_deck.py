#!/usr/bin/env python3
"""Builds the redesigned edition of "1 PLM INTERFACE.pptx".

All wording is derived from the source deck; layout, typography and visual
system are new. Assets (screenshots) are reused from the source package.
"""
import os, re, sys, zipfile
import pptxlib as L
from pptxlib import (shape, solid, grad, radial, run, para, text, MONO)
import preview

HERE = os.path.dirname(os.path.abspath(__file__))
# Screenshots and the base theme are reused from the original deck.
SRC = os.path.join(HERE, '..', '1 PLM INTERFACE.pptx')
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    HERE, '..', '1 PLM INTERFACE - Enhanced.pptx')

# ----------------------------------------------------------------- palette --
BG_A, BG_B = '05101F', '133258'
INK, SOFT, MUTED, DIM = 'FFFFFF', 'CBDAEC', '95AAC6', '61789A'
OR, OR2 = 'FF8A3D', 'FFC489'
CY, GR, VI, RED = '3ED0EE', '4ADE9B', 'A78BFA', 'FF7070'
M, RIGHT, CW = 72, 1208, 1136          # left margin, right edge, content width
NSL = 13


# ------------------------------------------------------------------ pieces --
def backdrop(accent=OR):
    return [
        shape('rect', 0, 0, 1280, 720, fill=grad(BG_A, BG_B, 125), name='bg'),
        shape('ellipse', 690, -230, 900, 900, fill=radial(accent, 17), name='glowA', bleed=1),
        shape('ellipse', -260, 300, 760, 760, fill=radial(CY, 11), name='glowB', bleed=1),
        shape('rect', 0, 0, 1280, 3, fill=grad(accent, CY, 0, 70, 40), name='topbar'),
    ]


def card(x, y, w, h, alpha=6, r=14, line=('FFFFFF', 1, 15), shadow=(24, 8, 26),
         fill=None, name='card', glow=None):
    return shape('round', x, y, w, h, fill=fill or solid('FFFFFF', alpha),
                 line=line, r=r, shadow=shadow, name=name, glow=glow)


def badge(x, y, d, label, c, sz=15, filled=True, dark='061423'):
    return [
        shape('ellipse', x, y, d, d,
              fill=solid(c, 100) if filled else solid(c, 16),
              line=None if filled else (c, 1.4, 65),
              glow=(c, 9, 28) if filled else None, name='badge'),
        text(x, y, d, d, para(run(label, sz=sz, b=True,
                                  c=dark if filled else c), align='ctr'),
             anchor='ctr', name='badgetxt'),
    ]


def sq_badge(x, y, d, label, c, sz=15, r=12):
    return [
        shape('round', x, y, d, d, fill=solid(c, 15), line=(c, 1.4, 60), r=r,
              name='sqbadge'),
        text(x, y, d, d, para(run(label, sz=sz, b=True, c=c), align='ctr'),
             anchor='ctr', name='sqbadgetxt'),
    ]


def header(eyebrow, title, sub=None, accent=OR, tw=1010, tsz=32):
    s = [text(M, 46, 760, 18, para(run(eyebrow, sz=10.5, b=True, c=accent,
                                       spc=2.4, caps=True)), name='eyebrow'),
         text(M, 68, tw, 54, para(run(title, sz=tsz, b=True, c=INK, spc=-0.4)),
              name='title'),
         shape('round', M, 126, 54, 4, fill=grad(accent, OR2, 0), r=2,
               name='rule')]
    if sub:
        s.append(text(M, 144, 880, 24, para(run(sub, sz=13.5, c=MUTED)),
                      name='sub'))
    return s


def chrome(n, label='Log in to PLM'):
    return [
        shape('rect', M, 674, CW, 1, fill=solid('FFFFFF', 9), name='hairline'),
        text(M, 684, 620, 16, para(run('PLM  ·  ENOVIA V6  ·  %s' % label,
                                       sz=9.5, c=DIM, spc=0.8)), name='foot'),
        text(RIGHT - 160, 684, 160, 16,
             para(run('%02d / %d' % (n, NSL), sz=9.5, b=True, c=DIM, spc=1.2),
                  align='r'), name='pagenum'),
    ]


def strip_note(y, txt, h=64, accent=OR, sz=13):
    return [card(M, y, CW, h, alpha=5, r=12),
            shape('round', M, y + 16, 3, h - 32, fill=solid(accent, 80), r=1,
                  name='accentbar'),
            text(M + 26, y, CW - 52, h, para(run(txt, sz=sz, c=SOFT)),
                 anchor='ctr', name='stripnote')]


def label_row(x, y, w, items, c=SOFT, sz=12, step=30, dot=GR):
    out = []
    for i, it in enumerate(items):
        yy = y + i * step
        out.append(shape('ellipse', x, yy + step / 2 - 4, 7, 7,
                         fill=solid(dot, 85), name='dot'))
        out.append(text(x + 18, yy, w - 18, step,
                        para(run(it, sz=sz, c=c)), anchor='ctr', name='item'))
    return out


# ------------------------------------------------------------------ slides --
S = []

# 01 ---------------------------------------------------------------- title --
s = backdrop()
s += [
    shape('ellipse', 852, 54, 470, 470, fill=None, line=('FFFFFF', 1, 8),
          name='ring1', bleed=1),
    shape('ellipse', 936, 138, 302, 302, fill=None, line=(OR, 1, 12),
          name='ring2'),
    text(880, 250, 340, 340, para(run('01', sz=190, b=True, c='FFFFFF', a=7),
                                  align='ctr'), anchor='ctr', name='ghostnum'),
    card(72, 102, 124, 124, r=22, fill=solid('FFFFFF', 96), line=('FFFFFF', 1, 40),
         shadow=(30, 10, 45), name='logocard'),
    shape('pic', 84, 122, 100, 84, img='image5.png', crop=(1.6, 2.5, 70.6, 66.5),
          name='PLM logo'),
    text(216, 116, 620, 20, para(run('Stellantis  ·  PLM onboarding  ·  Module 01',
                                     sz=11.5, b=True, c=CY, spc=2.4, caps=True)),
         name='eyebrow'),
    text(216, 146, 620, 20, para(run('ENOVIA V6R2013x   ·   PLM platform V3.1.11',
                                     sz=11, c=DIM, spc=0.8)), name='meta'),
    text(72, 240, 900, 122, para([run('Log in to ', sz=72, b=True, c=INK, spc=-1.4),
                                  run('PLM', sz=72, b=True, c=OR, spc=-1.4)]),
         name='hero'),
    shape('round', 72, 374, 104, 6, fill=grad(OR, OR2, 0), r=3, name='rule'),
    text(72, 400, 600, 112, para(run('Everything you need for your first '
         'connection: access rights, Security Context, and a guided tour of the '
         'ENOVIA interface.', sz=16.5, c=SOFT), line=130), name='sub'),
    text(RIGHT - 320, 648, 320, 18, para(run('13 slides  ·  about 10 minutes',
         sz=10, c=DIM, spc=0.6), align='r'), name='dur'),
    text(72, 648, 760, 18, para(run('Redesigned edition  ·  content sourced from '
         '"1 PLM INTERFACE.pptx"', sz=10, c=DIM, spc=0.6)), name='src'),
]
for x, w, lab, c in ((72, 204, '1 · Security Context', OR),
                     (292, 234, '2 · Two ways to connect', CY),
                     (542, 186, '3 · Interface tour', GR)):
    s += [shape('pill', x, 532, w, 44, fill=solid('FFFFFF', 6),
                line=('FFFFFF', 1, 16), r=22, name='pill'),
          shape('ellipse', x + 18, 550, 8, 8, fill=solid(c), name='pilldot'),
          text(x + 34, 532, w - 46, 44, para(run(lab, sz=12, b=True, c=SOFT)),
               anchor='ctr', name='pilltxt')]
S.append(s)

# 02 --------------------------------------------------------------- agenda --
s = backdrop(CY) + header('Agenda', 'What this module covers',
                          'Four steps, from access rights to your first click.',
                          accent=CY) + chrome(2)
AG = [(OR, '01', 'Before you log in',
       'PLM access and a Security Context. Both are requested in PLMPassport.',
       'Prerequisites'),
      (CY, '02', 'The Security Context',
       'Role + Organization + Project — the key that grants your creation rights.',
       'Core concept'),
      (GR, '03', 'Two ways to connect',
       'The PLM icon in the CFAO palette, or the direct intranet address.',
       'Access'),
      (VI, '04', 'Reading the interface',
       'Toolbar zones A, B and C — plus the one habit to unlearn.',
       'Navigation')]
for i, (c, num, ttl, body, tag) in enumerate(AG):
    x = M + i * 286
    s += [card(x, 196, 266, 372, alpha=6),
          shape('round', x + 26, 224, 34, 4, fill=solid(c), r=2, name='tab'),
          text(x + 26, 240, 214, 66, para(run(num, sz=40, b=True, c=c, a=90)),
               name='num'),
          text(x + 26, 316, 214, 80, para(run(ttl, sz=19.5, b=True, c=INK),
                                          line=115), name='cardttl'),
          text(x + 26, 404, 214, 130, para(run(body, sz=12.5, c=MUTED), line=140),
               name='cardbody'),
          text(x + 26, 540, 214, 18, para(run(tag, sz=9.5, b=True, c=c, spc=1.6,
                                              caps=True)), name='cardtag')]
s.append(text(M, 600, CW, 20, para(run('Each step builds on the previous one.',
                                       sz=11, c=DIM), align='ctr'), name='hint'))
S.append(s)

# 03 -------------------------------------------------------- prerequisites --
s = backdrop() + header('Step 01 · Before you start',
                        'Two things must be true before your first login',
                        'Without both, PLM opens — but you cannot create anything.',
                        tw=1100, tsz=28) + chrome(3)
s += [card(M, 196, 560, 166)] + badge(100, 224, 52, '1', OR, sz=19) + [
    text(172, 220, 420, 34, para(run('PLM access', sz=20, b=True, c=INK)),
         name='c1t'),
    text(172, 258, 420, 88, para(run('Your account must be granted access to the '
         'PLM platform. Access requests are raised in PLMPassport.', sz=12.5,
         c=MUTED), line=140), name='c1b'),
    card(M, 382, 560, 186)] + badge(100, 410, 52, '2', CY, sz=19) + [
    text(172, 406, 420, 34, para(run('Security Context', sz=20, b=True, c=INK)),
         name='c2t'),
    text(172, 444, 420, 112, para(run('A Security Context grants you creation '
         'rights in PLM, based on your role and the project you are working on.',
         sz=12.5, c=MUTED), line=140), name='c2b'),
    text(664, 196, 544, 20, para(run('The chain', sz=10.5, b=True, c=DIM, spc=2.2,
                                     caps=True)), name='chainlab'),
    shape('rect', 700, 244, 2, 214, fill=solid('FFFFFF', 13), name='spine'),
]
for i, (ttl, sub, c) in enumerate((
        ('Access granted', 'Your PLM account is active.', CY),
        ('Context assigned', 'Role · Organization · Project.', OR),
        ('You can create', 'Prototypes, documents, changes.', GR))):
    y = 230 + i * 100
    s += [shape('ellipse', 692, y + 6, 18, 18, fill=solid(c),
                glow=(c, 8, 30), name='node'),
          text(736, y, 460, 28, para(run(ttl, sz=16, b=True, c=INK)), name='nt'),
          text(736, y + 28, 460, 26, para(run(sub, sz=11.5, c=MUTED)), name='ns')]
s += strip_note(504, 'Missing one of them? Raise the request in PLMPassport '
                     'before your first login.', h=64, accent=CY)
s[-3]['x'], s[-3]['w'] = 664, 544
s[-2]['x'] = 664 + 16
s[-1]['x'], s[-1]['w'] = 664 + 26, 544 - 52
S.append(s)

# 04 -------------------------------------------------------- what it is -----
s = backdrop(CY) + header('Step 02 · Core concept',
                          'A Security Context = Role + Organization + Project',
                          'It tells PLM what you may create, and on which project.',
                          accent=CY, tw=1100, tsz=28) + chrome(4)
PIL = [(OR, 'R', 'Role', [run('PiloteProjet', sz=24, b=True, c=INK)],
        'Defines what you may do. Creating the expected prototypes requires the '
        'PiloteProjet role.'),
       (CY, 'O', 'Organization', [run('PSA', sz=24, b=True, c=INK)],
        'The organization you act for. For these prototypes, the organization '
        'is PSA.'),
       (GR, 'P', 'Project', [run('e.g. ', sz=14, c=DIM),
                             run('R832E', sz=24, b=True, c=INK)],
        'The project you are required to work on — one context covers one '
        'project.')]
for i, (c, letter, lab, val, body) in enumerate(PIL):
    x = M + i * 388
    s += [card(x, 196, 360, 300)] + badge(x + 28, 224, 56, letter, c, sz=20) + [
        text(x + 28, 300, 300, 20, para(run(lab, sz=10.5, b=True, c=c, spc=2.2,
                                            caps=True)), name='plab'),
        text(x + 28, 322, 304, 44, para(val), name='pval'),
        text(x + 28, 376, 304, 100, para(run(body, sz=12.5, c=MUTED), line=140),
             name='pbody')]
s += [card(M, 528, CW, 60, alpha=5, r=12),
      text(M, 528, CW, 60, para([
          run('Required for prototype creation:      ', sz=13, c=MUTED),
          run('PSA_PiloteProjet', sz=15, b=True, c=OR, font=MONO),
          run('  .  ', sz=15, b=True, c=DIM, font=MONO),
          run('PSA', sz=15, b=True, c=CY, font=MONO),
          run('  .  ', sz=15, b=True, c=DIM, font=MONO),
          run('your project', sz=15, b=True, c=GR, font=MONO)], align='ctr'),
           anchor='ctr', name='formula')]
S.append(s)

# 05 -------------------------------------------------------------- anatomy --
s = backdrop() + header('Step 02 · How to read it',
                        'Anatomy of a context string',
                        'Every Security Context is written as three parts, '
                        'separated by dots.') + chrome(5)
s.append(card(160, 208, 960, 200, alpha=4, r=18))
SEG = [(245, 420, 'PSA_PiloteProjet', OR, 'Role', 'what you may do'),
       (695, 130, 'PSA', CY, 'Organization', 'who you act for'),
       (855, 180, 'R832E', GR, 'Project', 'where you work')]
for i, (x, w, txt, c, lab, sub) in enumerate(SEG):
    cx = x + w / 2.0
    s += [shape('round', x, 240, w, 76, fill=solid(c, 12), line=(c, 1.4, 55),
                r=12, name='seg'),
          text(x, 240, w, 76, para(run(txt, sz=26, b=True, c=c, font=MONO),
                                   align='ctr'), anchor='ctr', name='segtxt'),
          shape('line', cx, 322, 0, 18, line=(c, 1, 45), name='tick'),
          text(cx - 80, 346, 160, 20, para(run(lab, sz=10.5, b=True, c=c, spc=2,
                                               caps=True), align='ctr'),
               name='seglab'),
          text(cx - 100, 370, 200, 20, para(run(sub, sz=11.5, c=MUTED),
                                            align='ctr'), name='segsub')]
    if i < 2:
        s.append(text(x + w, 240, 30, 76, para(run('.', sz=26, b=True, c=DIM,
                                                   font=MONO), align='ctr'),
                      anchor='ctr', name='dot'))
s += [text(160, 438, 340, 18, para(run('As displayed in PLM', sz=10, b=True,
                                       c=DIM, spc=2, caps=True)), name='exlab'),
      card(160, 464, 340, 56, r=10, fill=solid('FFFFFF', 96),
           line=('FFFFFF', 1, 30)),
      shape('pic', 178, 478, 300, 32, img='image2.png', name='context string'),
      card(540, 438, 580, 112),
      text(566, 458, 530, 28, para(run('One context at a time', sz=15, b=True,
                                       c=INK)), name='nt'),
      text(566, 490, 530, 60, para(run('You can only use one Security Context '
           'per project. If you change project, you change Security Context.',
           sz=12, c=MUTED), line=140), name='nb'),
      text(160, 556, 960, 20, para(run('The project code is the part that changes '
           'when you switch project: R832E, EMP2, P41E, B78 …', sz=11, c=DIM),
           align='ctr'), name='tip')]
S.append(s)

# 06 ---------------------------------------------------------------- rules --
s = backdrop() + header('Step 02 · Rules', 'Three rules to remember',
                        'Short list. No exceptions.') + chrome(6)
RU = [(OR, '01', 'One context per project', 'You can only use one Security '
       'Context per project. If you change project, you change Security Context.'),
      (CY, '02', 'Contractors', 'If you are a contractor, the request is made by '
       'your STELLANTIS client — not by you.'),
      (GR, '03', 'One door for requests', 'All PLM access requests go through '
       'PLMPassport — for yourself or for a colleague.')]
for i, (c, num, ttl, body) in enumerate(RU):
    x = M + i * 388
    s += [card(x, 196, 360, 320)] + sq_badge(x + 28, 224, 44, num, c, sz=16) + [
        text(x + 28, 288, 304, 84, para(run(ttl, sz=21, b=True, c=INK), line=115),
             name='rt'),
        text(x + 28, 384, 304, 112, para(run(body, sz=12.5, c=MUTED), line=140),
             name='rb')]
s += [card(354, 220, 48, 48, r=12, fill=solid('FFFFFF', 96),
           line=('FFFFFF', 1, 30), shadow=(18, 6, 35)),
      shape('pic', 359, 226, 38, 36, img='image7.png', name='warning')]
s += strip_note(548, 'Rule of thumb — your Security Context always matches the '
                     'project you are working on right now.', h=64, accent=OR)
S.append(s)

# 07 ---------------------------------------------------------- plmpassport --
PP = 'https://plmpassport.inetpsa.com/index.php/home'
s = backdrop() + header('Step 02 · Request access',
                        'Request your access in PLMPassport',
                        'One portal for every PLM access request.') + chrome(7)
s.append(shape('rect', 101, 234, 2, 220, fill=solid('FFFFFF', 12), name='spine'))
for i, (c, ttl, body) in enumerate((
        (OR, 'Open PLMPassport', 'plmpassport.inetpsa.com — the entry point for '
         'PLM rights.'),
        (CY, 'Raise the request', 'For yourself, or on behalf of a colleague who '
         'needs access.'),
        (GR, 'Receive your context', 'Role · Organization · Project, ready to use '
         'at your next login.'))):
    y = 206 + i * 120
    s += sq_badge(88, y, 28, str(i + 1), c, sz=12, r=8) + [
        text(140, y - 4, 420, 30, para(run(ttl, sz=17, b=True, c=INK)), name='st'),
        text(140, y + 28, 420, 60, para(run(body, sz=12.5, c=MUTED), line=140),
             name='sb')]
s += [card(664, 196, 544, 240, fill=grad(OR, 'C24E10', 125, 18, 9),
           line=(OR, 1.5, 45), glow=(OR, 16, 22), r=16),
      text(700, 230, 470, 20, para(run('Request portal', sz=10.5, b=True, c=OR2,
                                       spc=2.2, caps=True)), name='cl'),
      text(700, 258, 470, 42, para(run('plmpassport.inetpsa.com', sz=22, b=True,
                                       c=INK, link=PP)), name='url'),
      text(700, 306, 470, 22, para(run('/index.php/home', sz=12, c=SOFT,
                                       font=MONO)), name='path'),
      shape('rect', 700, 344, 470, 1, fill=solid('FFFFFF', 20), name='div'),
      text(700, 360, 470, 26, para(run('PLM access requests must be made in '
                                       'PLMPassport.', sz=13, b=True, c=GR)),
           name='green'),
      text(700, 392, 470, 24, para(run('Click the address to open the portal.',
                                       sz=11.5, c=SOFT)), name='cta'),
      card(664, 456, 544, 112),
      text(696, 478, 480, 18, para(run('Contractors', sz=10.5, b=True, c=CY,
                                       spc=2.2, caps=True)), name='colab'),
      text(696, 502, 480, 60, para(run('Your STELLANTIS client is the one who '
           'makes the request on your behalf.', sz=13, c=SOFT), line=140),
           name='cobody')]
S.append(s)

# 08 --------------------------------------------------------- two ways in ---
URL = 'http://plm.inetpsa.com/enovia/common/emxNavigator.jsp'
s = backdrop(GR) + header('Step 03 · Connect', 'Two ways in',
                          'Both routes open the same PLM platform.',
                          accent=GR) + chrome(8)
s += [card(M, 196, 552, 400),
      text(100, 220, 300, 20, para(run('Route A', sz=10.5, b=True, c=OR, spc=2.2,
                                       caps=True)), name='ra'),
      text(100, 244, 500, 34, para(run('From the CFAO palette', sz=21, b=True,
                                       c=INK)), name='rat'),
      text(100, 284, 500, 52, para(run('On psa.com, open the CFAO palette and '
           'click the PLM Platform icon.', sz=12.5, c=MUTED), line=125),
           name='rab'),
      shape('pic', 140, 340, 416, 236, img='image4.png', r=8,
            line=('FFFFFF', 1, 28), shadow=(24, 8, 40), name='CFAO palette'),
      card(656, 196, 552, 400),
      text(684, 220, 300, 20, para(run('Route B', sz=10.5, b=True, c=CY, spc=2.2,
                                       caps=True)), name='rb'),
      text(684, 244, 500, 34, para(run('Direct intranet address', sz=21, b=True,
                                       c=INK)), name='rbt'),
      text(684, 284, 500, 46, para(run('Paste the address into your browser on '
           'the Stellantis intranet.', sz=12.5, c=MUTED), line=125), name='rbb'),
      card(684, 340, 496, 132, r=12, fill=solid('020B18', 55),
           line=('FFFFFF', 1, 18), shadow=None)]
for i, c in enumerate((RED, 'FFC94D', GR)):
    s.append(shape('ellipse', 704 + i * 16, 360, 10, 10, fill=solid(c, 80),
                   name='wdot'))
s += [shape('round', 704, 384, 456, 40, fill=solid('FFFFFF', 6),
            line=('FFFFFF', 1, 13), r=10, name='urlbar'),
      text(718, 384, 430, 40, para(run(URL, sz=11, c=CY, font=MONO, link=URL)),
           anchor='ctr', name='url'),
      text(704, 434, 456, 22, para(run('Click to open  ·  intranet only', sz=10.5,
                                       c=DIM)), name='ucap'),
      text(684, 500, 496, 24, para(run('Same platform, same login, same context.',
                                       sz=11.5, c=SOFT)), name='b1'),
      text(684, 528, 496, 24, para(run('Bookmark the address for daily use.',
                                       sz=11.5, c=SOFT)), name='b2')]
S.append(s)

# 09 ------------------------------------------------------- pick a context --
s = backdrop(GR) + header('Step 03 · First screen',
                          'Pick your Security Context at launch',
                          'PLM opens on the splash screen and asks which context '
                          'to use.', accent=GR) + chrome(9)
s += [card(68, 192, 548, 412, alpha=9, r=12),
      shape('pic', 72, 196, 540, 404, img='image5.png', r=8,
            line=('FFFFFF', 1, 26), shadow=(26, 8, 40), name='context list'),
      text(72, 610, 540, 20, para(run('The context list at launch — select one, '
                                      'then confirm.', sz=10.5, c=DIM)),
           name='cap')]
PICK = [(OR, 'Every context you own is listed',
         'The list shows all Security Contexts assigned to you.'),
        (CY, 'Select the one for your project',
         'Match the last part of the string to the project you are working on.'),
        (GR, 'Confirm with Terminé',
         'The button closes the selection and opens the PLM home page.')]
for i, (c, ttl, body) in enumerate(PICK):
    y = 196 + i * 132
    s += [card(656, y, 552, 116)] + sq_badge(684, y + 24, 40, str(i + 1), c,
                                             sz=15) + [
        text(744, y + 20, 440, 28, para(run(ttl, sz=16, b=True, c=INK)),
             name='pt'),
        text(744, y + 50, 440, 54, para(run(body, sz=12, c=MUTED), line=135),
             name='pb')]
S.append(s)

# 10 ------------------------------------------------------------ home page --
s = backdrop(VI) + header('Step 04 · Interface', 'The home page at a glance',
                          'After login you land on the PLM home page. Everything '
                          'starts from the toolbar.', accent=VI) + chrome(10)
s += [card(68, 192, 712, 449, alpha=9, r=12),
      shape('pic', 72, 196, 704, 441, img='image6.png', r=6,
            line=('FFFFFF', 1, 22), shadow=(26, 8, 40), name='PLM home page'),
      shape('round', 541, 199, 156, 30, fill=solid('0A1E38', 92),
            line=('FFFFFF', 1, 22), r=6, name='anon'),
      text(541, 199, 156, 30, para(run('your name · your role', sz=8.5, c=SOFT),
                                   align='ctr'), anchor='ctr', name='anontxt'),
      text(72, 646, 704, 18, para(run('PLM home page after login — the toolbar '
                                      'runs across the top.', sz=10, c=DIM)),
           name='cap')]
ZONES = [(OR, 'A', 72, 219, 275, 'Actions & navigation',
          'My Enovia, Actions, Tools, PLM Indicators Portal, Previous / Next page.'),
         (CY, 'B', 363, 164, 511, 'Search tools',
          'The quick search field and the search icons beside it.'),
         (GR, 'C', 700, 76, 748, 'Session icons',
          'Return to the home page, platform information, and Exit PLM.')]
for i, (c, letter, zx, zw, bx, ttl, body) in enumerate(ZONES):
    y = 200 + i * 148
    s += [shape('round', zx, 196, zw, 41, fill=None, line=(c, 2, 90), r=6,
                name='zone')] + badge(bx, 231, 26, letter, c, sz=12) + [
        card(812, y, 396, 132)] + badge(836, y + 24, 36, letter, c, sz=15) + [
        text(884, y + 22, 300, 28, para(run(ttl, sz=15.5, b=True, c=INK)),
             name='lt'),
        text(884, y + 54, 300, 66, para(run(body, sz=11.5, c=MUTED), line=135),
             name='lb')]
S.append(s)

# 11 -------------------------------------------------------- zone by zone ---
s = backdrop(VI) + header('Step 04 · Toolbar', 'Zone by zone',
                          'The toolbar never changes — learn it once.',
                          accent=VI) + chrome(11)
ZB = [(OR, 'A', 'Actions & navigation',
       ['My Enovia', 'Actions', 'Tools', 'PLM Indicators Portal',
        'Previous / Next page'],
       'The two round arrows are the application\u2019s own back and forward.'),
      (CY, 'B', 'Search tools', ['Quick search field', 'Search icons'],
       'Type here to find objects without leaving the page.'),
      (GR, 'C', 'Session icons',
       ['Return to the home page', 'Platform information', 'Exit PLM'],
       'Use Exit PLM to close your session properly.')]
for i, (c, letter, ttl, items, note) in enumerate(ZB):
    x = M + i * 388
    s += [card(x, 196, 360, 296)] + badge(x + 28, 222, 40, letter, c, sz=17) + [
        text(x + 80, 224, 250, 22, para(run('Zone ' + letter, sz=11, b=True, c=c,
                                            spc=2.2, caps=True)), name='zl'),
        text(x + 80, 246, 250, 22, para(run(ttl, sz=12.5, c=MUTED)), name='zt'),
    ] + label_row(x + 28, 288, 304, items, dot=c) + [
        text(x + 28, 436, 304, 50, para(run(note, sz=11.5, c=DIM), line=135),
             name='zn')]
s += [card(68, 526, 1144, 74, alpha=8, r=10),
      shape('pic', 72, 530, 1136, 66, img='image6.png', crop=(0, 0, 0, 90.7),
            name='toolbar', r=4, line=('FFFFFF', 1, 18)),
      shape('round', 829, 534, 251, 50, fill=solid('0A1E38', 94),
            line=('FFFFFF', 1, 18), r=8, name='anon'),
      text(829, 534, 251, 50, para(run('your name  ·  your role', sz=10, b=True,
                                       c=SOFT, spc=1), align='ctr'), anchor='ctr',
           name='anontxt')]
for c, letter, zx, zw in ((OR, 'A', 72, 353), (CY, 'B', 541, 265),
                          (GR, 'C', 1085, 123)):
    s += [shape('round', zx, 530, zw, 66, fill=None, line=(c, 2, 85), r=8,
                name='zoneline')] + badge(zx - 6, 516, 24, letter, c, sz=11)
s.append(text(M, 606, CW, 20, para(run('The toolbar, full width — zones A, B and C.',
                                       sz=10.5, c=DIM), align='ctr'), name='cap'))
S.append(s)

# 12 ----------------------------------------------------------- golden rule -
s = backdrop() + header('Step 04 · Golden rule',
                        'Never use the browser\u2019s back / forward buttons',
                        'PLM has its own navigation — use it.',
                        tw=1100, tsz=28) + chrome(12)
s += [card(M, 196, 552, 340, fill=solid(RED, 7), line=(RED, 1.2, 34)),
      shape('pill', 100, 224, 96, 30, fill=solid(RED, 18), line=(RED, 1.2, 55),
            r=15, name='chip'),
      text(100, 224, 96, 30, para(run('Don\u2019t', sz=11, b=True, c=RED, spc=1.4,
                                      caps=True), align='ctr'), anchor='ctr',
           name='chiptxt'),
      card(100, 272, 64, 64, r=14, fill=solid('FFFFFF', 96),
           line=('FFFFFF', 1, 30), shadow=(16, 5, 32)),
      shape('pic', 108, 281, 48, 45, img='image7.png', name='warning'),
      text(184, 274, 410, 34, para(run('Browser back / forward', sz=19, b=True,
                                       c=INK)), name='dt'),
      text(184, 314, 410, 60, para(run('These buttons belong to the browser, not '
                                       'to PLM.', sz=12.5, c=MUTED), line=140),
           name='db'),
      card(100, 396, 496, 116, r=12, fill=solid('FFFFFF', 94),
           line=('FFFFFF', 1, 26)),
      shape('pic', 148, 408, 400, 91, img='image8.png', name='browser buttons'),
      shape('line', 180, 416, 340, 78, line=(RED, 4, 80), name='x1'),
      shape('line', 180, 416, 340, 78, line=(RED, 4, 80), flipV=True, name='x2'),
      card(656, 196, 552, 340, fill=solid(GR, 7), line=(GR, 1.2, 32)),
      shape('pill', 684, 224, 72, 30, fill=solid(GR, 18), line=(GR, 1.2, 55),
            r=15, name='chip'),
      text(684, 224, 72, 30, para(run('Do', sz=11, b=True, c=GR, spc=1.4,
                                      caps=True), align='ctr'), anchor='ctr',
           name='chiptxt'),
      text(684, 274, 500, 34, para(run('PLM Previous / Next page', sz=19, b=True,
                                       c=INK)), name='gt'),
      text(684, 314, 500, 60, para(run('The two round arrows in the toolbar move '
           'you through PLM the way the application expects.', sz=12.5, c=MUTED),
           line=140), name='gb'),
      card(684, 390, 496, 122, r=12, fill=solid('0A2038', 70),
           line=('FFFFFF', 1, 16)),
      shape('pic', 862, 396, 145, 110, img='image6.png',
            crop=(23.9, 0.9, 69.7, 91.3), name='PLM arrows')]
s += strip_note(562, 'If you get lost, the home icon in zone C brings you back to '
                     'the PLM home page.', h=66, accent=GR)
S.append(s)

# 13 ---------------------------------------------------------------- recap --
s = backdrop(GR) + header('Recap', 'Your first-login checklist',
                          'Five things, in order.', accent=GR) + chrome(13)
CK = [('PLM access requested and granted in PLMPassport', 'Step 01', OR),
      ('Security Context assigned: PiloteProjet · PSA · your project', 'Step 02', CY),
      ('PLM launched from the CFAO palette or the intranet address', 'Step 03', GR),
      ('Correct context selected at launch, then confirmed', 'Step 03', GR),
      ('Navigating with the PLM toolbar — never the browser buttons', 'Step 04', VI)]
for i, (txt, tag, c) in enumerate(CK):
    y = 196 + i * 72
    s += [card(M, y, CW, 64, alpha=5, r=12)] + sq_badge(100, y + 18, 28,
                                                        str(i + 1), c, sz=12,
                                                        r=8) + [
        text(148, y, 860, 64, para(run(txt, sz=14.5, c=SOFT)), anchor='ctr',
             name='ck'),
        text(1020, y, 162, 64, para(run(tag, sz=10.5, b=True, c=c, spc=1.4,
                                        caps=True), align='r'), anchor='ctr',
             name='cktag')]
s += [card(M, 570, CW, 66, fill=grad(GR, '0E7A55', 125, 12, 6),
           line=(GR, 1.2, 34), r=12),
      text(M, 570, CW, 66, para([
          run('Next in this series:   ', sz=13, c=SOFT),
          run('Creating a Product ECO', sz=13.5, b=True, c=INK),
          run('   ·   ', sz=13, c=DIM),
          run('PDEF / PREA lifecycle management', sz=13.5, b=True, c=INK)],
          align='ctr'), anchor='ctr', name='next')]
S.append(s)


# ------------------------------------------------------------------- build --
def main():
    with zipfile.ZipFile(SRC) as z:
        images = {n.rsplit('/', 1)[1]: z.read(n) for n in z.namelist()
                  if n.startswith('ppt/media/')}
        theme = z.read('ppt/theme/theme1.xml').decode('utf8')
    theme = (theme.replace('<a:srgbClr val="4472C4"/>', '<a:srgbClr val="%s"/>' % OR)
                  .replace('<a:srgbClr val="ED7D31"/>', '<a:srgbClr val="%s"/>' % CY)
                  .replace('<a:srgbClr val="A5A5A5"/>', '<a:srgbClr val="%s"/>' % GR)
                  .replace('<a:srgbClr val="FFC000"/>', '<a:srgbClr val="%s"/>' % VI)
                  .replace('<a:srgbClr val="44546A"/>', '<a:srgbClr val="%s"/>' % BG_B)
                  .replace('<a:srgbClr val="E7E6E6"/>', '<a:srgbClr val="E9F0F8"/>')
                  .replace('<a:srgbClr val="0563C1"/>', '<a:srgbClr val="%s"/>' % CY)
                  .replace('"Calibri Light"', '"Segoe UI"')
                  .replace('"Calibri"', '"Segoe UI"')
                  .replace('name="Office Theme"', 'name="PLM Onboarding"'))

    problems = L.validate(S)
    print('slides: %d   shapes: %d' % (len(S), sum(len(x) for x in S)))
    for p in problems:
        print('  ! ' + p)
    print('  %d layout warning(s)' % len(problems))

    used = L.write_pptx(S, images, theme, OUT,
                        'Log in to PLM — Access, Security Context & Interface',
                        'PLM onboarding')
    print('wrote %s (%.0f KB) images=%s'
          % (OUT, os.path.getsize(OUT) / 1024.0, used))
    if '--preview' in sys.argv:
        preview.contact_sheet(S, os.path.join(HERE, 'preview_all.png'),
                              cols=2, sc=0.5)
        print('preview -> preview_all.png')


if __name__ == '__main__':
    main()
