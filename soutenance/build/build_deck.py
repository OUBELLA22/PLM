# -*- coding: utf-8 -*-
"""Builds the KATATOOL validation deck (FR)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pptxlite import Presentation, para, run, gradient  # noqa: E402
from metrics import wrap_lines, line_h, block_h  # noqa: E402

FITS = []  # copy that had to be shrunk to fit - reviewed at the end of build

# ---------------------------------------------------------------- design ---

SW, SH = 13.333, 7.5
M = 0.85
CW = SW - 2 * M

BLUE = "5B9DF9"
CYAN = "22D3EE"
GREEN = "34D399"
ORANGE = "F59E0B"
PURPLE = "A78BFA"
PINK = "F472B6"
W = "FFFFFF"
MUTED = "9FB6CE"
DIM = "6E89A6"
FOOT = "50708E"
CARD = "0F2842"

ACCENTS = [BLUE, GREEN, ORANGE, PURPLE, CYAN, PINK]

BG = gradient([(0, "16406A"), (50, "0A2440"), (100, "040E18")], angle=315)

TITLE = "KATATOOL — Soutenance carte de passage"
AUTHOR = "Youssef OUBELLA"
COMPANY = "MG2 Engineering"

prs = Presentation(SW, SH)
_page = [0]


def slide(notes="", numbered=True):
    s = prs.add_slide(background=BG, notes=notes)
    # crisp diagonal: an rtTriangle turned 180° darkens the upper-right half
    s.shape(0, 0, SW, SH, geom="rtTriangle", rot=180, fill="02090F", alpha=30,
            name="Diagonale")
    _page[0] += 1
    if numbered:
        s.text(M, SH - 0.58, CW * 0.6, 0.3,
               [para("KATATOOL · %s" % COMPANY, size=9, color=FOOT, spc=0.8)])
        s.text(SW - M - 1.2, SH - 0.58, 1.2, 0.3,
               [para("%02d" % _page[0], size=9, color=FOOT, align="r")])
    return s


def header(s, eyebrow, title, color=BLUE, align="l", title_size=38):
    x = M if align == "l" else 0
    w = CW if align == "l" else SW
    s.text(x, 0.60, w, 0.30,
           [para(eyebrow, size=11.5, color=color, bold=True, caps=True,
                 spc=1.9, align=align)])
    s.text(x, 0.96, w, 1.05,
           [para(title, size=title_size, color=W, bold=True, align=align,
                 line=1.05)])


TITLE_LS = 1.12
BODY_LS = 1.26


def card(s, x, y, w, h, color, num=None, title=None, body=None,
         title_size=17, body_size=12.5, icon=None, pad=0.38, title_h=None):
    """One bordered card. `title_h` lets a whole row share a baseline so the
    body paragraphs line up across cards."""
    s.shape(x, y, w, h, geom="roundRect", radius=0.05, fill=CARD, alpha=50,
            line=color, line_alpha=55, line_w=1.25, name="Carte")
    px, pw = x + pad, w - 2 * pad
    ty = y + 0.36
    badge = num if num is not None else icon
    if badge is not None:
        s.shape(px, ty, 0.50, 0.50, geom="roundRect", radius=0.2,
                fill=color, alpha=15, line=color, line_alpha=75, line_w=1.1,
                paras=[para(badge, size=13.5 if len(str(badge)) > 2 else 15.5,
                            color=color, bold=True, align="c")],
                anchor="ctr", name="Puce")
        ty += 0.78
    if title:
        th = title_h if title_h is not None else \
            wrap_lines(title, title_size, True, pw)[0] * line_h(title_size, TITLE_LS)
        s.text(px, ty, pw, th + 0.03,
               [para(title, size=title_size, color=W, bold=True, line=TITLE_LS)])
        ty += th + 0.13
    if body:
        s.text(px, ty, pw, max(0.3, y + h - ty - 0.24),
               [para(body, size=body_size, color=MUTED, line=BODY_LS)])


def cards_row(s, items, y, h, gap=0.30, title_size=16, body_size=12.5,
              pad=0.38):
    """Draws a row of cards with a uniform title height and a single body
    font size chosen so that the longest text in the row still fits."""
    n = len(items)
    w = (CW - gap * (n - 1)) / n
    pw = w - 2 * pad

    titles = [it["title"] for it in items if it.get("title")]
    title_h = max(wrap_lines(t, title_size, True, pw)[0]
                  for t in titles) * line_h(title_size, TITLE_LS) if titles else 0.0

    ty = y + 0.36
    if any(it.get("num") or it.get("icon") for it in items):
        ty += 0.78
    if titles:
        ty += title_h + 0.13
    avail = y + h - ty - 0.24

    bodies = [it["body"] for it in items if it.get("body")]
    size = body_size
    if bodies:
        while size > 9.8 and max(block_h(b, size, pw, False, BODY_LS)
                                 for b in bodies) > avail:
            size -= 0.25
        worst = max(block_h(b, size, pw, False, BODY_LS) for b in bodies)
        if worst > avail:
            FITS.append(("DEBORDE", "d%02d" % _page[0], size, worst, avail))
        elif size < body_size - 0.9:
            FITS.append(("reduit", "d%02d" % _page[0], size, worst, avail))

    for i, it in enumerate(items):
        card(s, M + i * (w + gap), y, w, h,
             it.get("color", ACCENTS[i % len(ACCENTS)]),
             num=it.get("num"), icon=it.get("icon"), title=it.get("title"),
             body=it.get("body"), title_size=title_size, body_size=size,
             pad=pad, title_h=title_h)
    return w


def kpi(s, x, y, w, value, label, color):
    s.text(x, y, w, 1.05, [para(value, size=58, color=color, bold=True, align="c")])
    s.text(x, y + 1.10, w, 0.32,
           [para(label, size=10.5, color=DIM, bold=True, caps=True, spc=1.6,
                 align="c")])


def chips(s, labels, y, color=None, size=12, cy=0.46, gap=0.22):
    widths = [0.52 + 0.081 * len(t) for t in labels]
    total = sum(widths) + gap * (len(labels) - 1)
    x = (SW - total) / 2.0
    for i, t in enumerate(labels):
        c = color or ACCENTS[i % len(ACCENTS)]
        s.shape(x, y, widths[i], cy, geom="roundRect", radius=0.5,
                fill=c, alpha=12, line=c, line_alpha=60, line_w=1.1,
                paras=[para(t, size=size, color=c, bold=True, align="c")],
                anchor="ctr", name="Pastille")
        x += widths[i] + gap


def flow(s, steps, y, h=1.15, colors=None, box_size=15.5, sub_size=10.5):
    n = len(steps)
    arrow = 0.44
    w = (CW - arrow * (n - 1)) / n
    for i, st in enumerate(steps):
        x = M + i * (w + arrow)
        c = (colors or ACCENTS)[i % len(colors or ACCENTS)]
        ps = [para(st[0], size=box_size, color=c if st[1] else W, bold=True,
                   align="c", line=1.1)]
        if st[1]:
            ps.append(para(st[1], size=sub_size, color=MUTED, align="c", before=4))
        s.shape(x, y, w, h, geom="roundRect", radius=0.07, fill=CARD, alpha=48,
                line=c, line_alpha=55, line_w=1.25, paras=ps, anchor="ctr",
                pad=(0.12, 0.14, 0.12, 0.14), name="Étape")
        if i < n - 1:
            s.text(x + w, y, arrow, h,
                   [para("→", size=17, color=DIM, align="c")], anchor="ctr")


def divider(s, number, title, subtitle=None, color=BLUE):
    s.text(SW - 5.4, 0.15, 5.0, line_h(210), 
           [para(number, size=210, color=W, alpha=6, bold=True, align="r")])
    s.shape(M, 2.62, 0.9, 0.045, fill=color, name="Filet")
    s.text(M, 2.95, CW, 0.34,
           [para("CHAPITRE %s" % number, size=12, color=color, bold=True,
                 caps=True, spc=2.4)])
    th = block_h(title, 48, CW - 1.0, True, 1.06)
    s.text(M, 3.36, CW - 1.0, th + 0.04,
           [para(title, size=48, color=W, bold=True, line=1.06)])
    if subtitle:
        y = 3.36 + th + 0.34
        s.text(M, y, CW - 2.4, block_h(subtitle, 15.5, CW - 2.4, False, 1.35) + 0.04,
               [para(subtitle, size=15.5, color=MUTED, line=1.35)])


def shot(s, x, y, w, h, caption, hint):
    s.shape(x, y, w, h, geom="roundRect", radius=0.03, fill="0C2035", alpha=45,
            line="3D5F82", line_alpha=60, line_w=1.1, dash="dash",
            name="Emplacement capture")
    s.text(x + 0.28, y + 0.20, w - 0.56, 0.3,
           [para(caption, size=10.5, color=DIM, bold=True, caps=True, spc=1.4)])
    s.text(x, y + h / 2 - 0.30, w, 0.6,
           [para(hint, size=13, color="53748F", align="c", italic=True)],
           anchor="ctr")


def statement(s, eyebrow, lines, color=CYAN, size=44, sub=None):
    s.text(0, 2.05, SW, 0.34,
           [para(eyebrow, size=12, color=color, bold=True, caps=True, spc=2.4,
                 align="c")])
    s.text(1.1, 2.60, SW - 2.2, 2.2,
           [para(l, size=size, color=W, bold=True, align="c", line=1.14)
            for l in lines])
    if sub:
        s.text(1.6, 5.05, SW - 3.2, 0.8,
               [para(sub, size=16, color=MUTED, align="c", line=1.35)])


# ============================================================== 01. TITRE ===

s = slide(notes=(
    "ACCUEIL (30 s)\n"
    "Bonjour, je m'appelle Youssef OUBELLA, Chargé de Développement 2D dans "
    "l'équipe CD2D.\n"
    "Aujourd'hui je vous présente KATATOOL : un hub unique et hors ligne qui "
    "réunit nos outils, nos formations et les ressources de chaque équipe.\n"
    "Trois temps : d'abord qui je suis et mon parcours, ensuite le problème que "
    "j'ai observé sur le terrain, enfin la solution que j'ai construite.\n"
    "Posture : calme, regarder le jury, ne pas lire l'écran."
), numbered=False)
s.shape((SW - 1.45) / 2, 0.80, 1.45, 1.45, geom="roundRect", radius=0.16,
        fill="0F2540", alpha=45, line="2E5177", line_alpha=60, line_w=1.2,
        dash="dash",
        paras=[para("LOGO", size=10, color="547590", bold=True, align="c",
                    spc=1.5)], anchor="ctr", name="Logo")
s.text(0, 2.42, SW, 0.32,
       [para("Soutenance · Carte de passage", size=12.5, color=CYAN, bold=True,
             caps=True, spc=2.6, align="c")])
s.text(0, 2.76, SW, line_h(84) + 0.02,
       [para("KATATOOL", size=84, color=W, bold=True, align="c", spc=1.5)])
s.text(1.4, 4.34, SW - 2.8, 0.46,
       [para("Un point d'accès unique pour les outils, la formation et les "
             "ressources métier.", size=16.5, color=MUTED, align="c", line=1.35)])
chips(s, ["Application hors ligne", "Formation & quiz", "FR / EN"], 5.00)
s.shape((SW - 2.0) / 2, 5.78, 2.0, 0.028, fill=CYAN, alpha=45, name="Filet")
s.text(0, 5.98, SW, 0.34,
       [para("Youssef OUBELLA", size=16, color=W, bold=True, align="c")])
s.text(0, 6.32, SW, 0.30,
       [para("Chargé de Développement 2D · Équipe CD2D · %s" % COMPANY,
             size=12, color=DIM, align="c")])

# =========================================================== 02. SOMMAIRE ===

s = slide(notes=(
    "SOMMAIRE (20 s)\n"
    "Annoncer le plan en une phrase par chapitre, puis enchaîner.\n"
    "« Mon parcours, le problème, la solution, et ce qu'elle nous apporte. »"
))
header(s, "Sommaire", "Le déroulé de cette présentation")
cards_row(s, [
    {"num": "01", "title": "Présentation & parcours",
     "body": "Qui je suis, ma formation et mon parcours professionnel jusqu'à "
             "mon poste actuel.", "color": BLUE},
    {"num": "02", "title": "Contexte & problématique",
     "body": "Ce que j'ai observé sur le terrain : le savoir existe, mais il "
             "est difficile à trouver.", "color": ORANGE},
    {"num": "03", "title": "KATATOOL",
     "body": "La solution : un hub unique, hors ligne, bilingue, avec "
             "formations et espaces équipes.", "color": GREEN},
    {"num": "04", "title": "Bénéfices & perspectives",
     "body": "L'impact pour l'équipe, pour l'entreprise et les prochaines "
             "étapes.", "color": PURPLE},
], y=2.28, h=3.78, title_size=15.5, body_size=12.5)

# ======================================================== CHAPITRE 01 ======

s = slide(notes=(
    "TRANSITION (5 s)\n"
    "« Commençons par le parcours qui m'a mené jusqu'ici. »"
))
divider(s, "01", "Présentation &\nparcours professionnel",
        "Du génie électrique à la conception de faisceaux automobiles.", BLUE)

s = slide(notes=(
    "QUI SUIS-JE (1 min 15)\n"
    "Bonjour à toutes et à tous. Je m'appelle Youssef OUBELLA, Chargé de "
    "Développement 2D au sein de l'équipe CD2D.\n"
    "Mon parcours a commencé dans le domaine scientifique : Baccalauréat "
    "Sciences Mathématiques A en 2018, puis Baccalauréat Sciences et "
    "Technologies en 2021.\n"
    "Ensuite j'ai choisi le génie électrique : DUT à l'École Supérieure de "
    "Technologie de Guelmim, obtenu en 2023.\n"
    "J'ai continué en parallèle de mon travail : Licence en Ingénierie de la "
    "Production Industrielle et Gestion de Projet en 2025, puis le Master en "
    "Ingénierie et Management Industriel — celui que je viens valider "
    "aujourd'hui devant vous.\n"
    "CETTE DERNIÈRE PHRASE EST FORTE : elle relie votre parcours à ce moment "
    "précis. Marquez un temps après.\n"
    "Déroulez la colonne de droite de haut en bas, sans citer les noms de "
    "lycées."
))
header(s, "Présentation personnelle", "Qui suis-je ?")
s.shape(M, 2.28, 3.05, 4.42, geom="roundRect", radius=0.06, fill="0F2540",
        alpha=45, line="2E5177", line_alpha=55, line_w=1.2, dash="dash",
        paras=[para("PHOTO", size=10.5, color="547590", bold=True, align="c",
                    spc=1.6)], anchor="ctr", name="Photo")
CX = M + 3.05 + 0.55
CWR = SW - M - CX
s.text(CX, 2.32, CWR, 0.62,
       [para("Youssef OUBELLA", size=32, color=W, bold=True)])
s.text(CX, 2.96, CWR, 0.34,
       [para("Chargé de Développement 2D  ·  Équipe CD2D  ·  %s" % COMPANY,
             size=14, color=CYAN)])
s.text(CX, 3.44, CWR - 0.2, 0.78, [
    para("Passionné par l'électricité et par la conception de faisceaux, et "
         "formé en parallèle à l'ingénierie et au management industriel.",
         size=13.5, color=MUTED, line=1.42),
])
s.text(CX, 4.40, CWR, 0.30,
       [para("Parcours académique", size=10, color=DIM, bold=True, caps=True,
             spc=1.8)])
edu4 = [
    ("2018", "Baccalauréat Sciences Mathématiques A", None, BLUE),
    ("2021", "Baccalauréat Sciences et Technologies", None, CYAN),
    ("2023", "DUT Génie Électrique", None, GREEN),
    ("2025", "Licence Ingénierie de la Production Industrielle "
     "et Gestion de Projet", None, ORANGE),
    ("2026", "Master Ingénierie et Management Industriel",
     "en cours de validation", PURPLE),
]
ROW_Y, ROW_STEP = 4.80, 0.39
s.shape(CX + 0.86, ROW_Y + 0.14, 0.022, (len(edu4) - 1) * ROW_STEP,
        fill="2A4A6B", name="Axe")
for i, (yr, deg, tag, col) in enumerate(edu4):
    y = ROW_Y + i * ROW_STEP
    s.text(CX, y, 0.72, 0.34,
           [para(yr, size=12, color=col, bold=True, align="r")], anchor="ctr")
    s.shape(CX + 0.808, y + 0.105, 0.13, 0.13, geom="ellipse", fill=col,
            line="040E18", line_w=1.6, name="Point")
    runs = [run(deg, size=12, color=W, bold=True)]
    if tag:
        runs.append(run("   " + tag, size=10.5, color=col, italic=True))
    s.text(CX + 1.08, y, CWR - 1.08, 0.34, [para(runs=runs)], anchor="ctr")

s = slide(notes=(
    "DIPLÔMES — DIAPO DE RÉSERVE (masquée dans la version 9 minutes)\n"
    "À garder sous la main : si le jury demande un détail sur la formation, ou "
    "sur le master en cours, affichez-la pendant les questions.\n"
    "Les cinq diplômes sont déjà résumés sur la diapo 4 — ici s'ajoutent les "
    "établissements.\n"
    "À COMPLÉTER : les établissements de la Licence 2025 et du Master 2026."
))
header(s, "Diplômes & formations", "Cinq étapes, une même trajectoire")
edu = [
    ("2017 / 2018", "Baccalauréat Sciences Mathématiques A",
     "Lycée Ibn Soulaiman Roudani — Taroudant", BLUE, None),
    ("2020 / 2021", "Baccalauréat Sciences et Technologies",
     "Lycée Al Inbiaat — Agadir", CYAN, None),
    ("2021 / 2023", "DUT — Génie Électrique",
     "École Supérieure de Technologie de Guelmim — Université Ibn Zohr",
     GREEN, None),
    ("2025", "Licence — Ingénierie de la Production Industrielle "
     "et Gestion de Projet", "Établissement à compléter", ORANGE, None),
    ("2026", "Master — Ingénierie et Management Industriel",
     "Établissement à compléter", PURPLE, "En cours de validation"),
]
AX = M + 1.42
s.shape(AX, 2.52, 0.022, 3.55, fill="2A4A6B", name="Axe")
for i, (date, deg, school, col, tag) in enumerate(edu):
    y = 2.34 + i * 0.88
    s.text(M, y, 1.20, 0.60,
           [para(date, size=14, color=col, bold=True, align="r")], anchor="ctr")
    s.shape(AX - 0.075, y + 0.215, 0.17, 0.17, geom="ellipse", fill=col,
            line="040E18", line_w=2.0, name="Point")
    ps = [para(deg, size=15, color=W, bold=True, line=1.15),
          para(school, size=11.5, color=MUTED, before=3)]
    if tag:
        ps[0] = para(runs=[
            run(deg, size=15, color=W, bold=True),
            run("   " + tag, size=11, color=col, bold=True, italic=True),
        ])
    s.text(AX + 0.34, y, CW - (AX - M) - 0.34, 0.60, ps, anchor="ctr")

s = slide(notes=(
    "PARCOURS PROFESSIONNEL (1 min 15)\n"
    "Deux stages d'abord : l'ONEE, sur les équipements de protection des "
    "postes sources. Puis Marsa Maroc, sur la mise à niveau des installations "
    "électriques du port d'Agadir — câblage des armoires électriques et "
    "réalisation des schémas unifilaires sur AutoCAD.\n"
    "En novembre 2023, j'ai rejoint MG2 comme Concepteur Faisceaux 2D. Depuis "
    "septembre 2024, je suis Chargé de Développement 2D.\n"
    "Terminer sur le bandeau du bas : analyser, concevoir, valider et "
    "approuver les plans 2D avec Capital XC et PLM."
))
header(s, "Expériences professionnelles", "Mon parcours professionnel")
s.shape(M + 0.1, 3.30, CW - 0.2, 0.022, fill="2A4A6B", name="Axe")
xp = [
    ("Juil. 2022", "ONEE", "Stage — équipements de protection des postes "
     "sources.", CYAN),
    ("Avr. 2023", "Marsa Maroc", "Stage — installations électriques du port "
     "d'Agadir. Câblage d'armoires, schémas unifilaires AutoCAD.", GREEN),
    ("Nov. 2023", "Concepteur Faisceaux 2D", "Arrivée chez %s. Conception et "
     "validation des faisceaux 2D." % COMPANY, ORANGE),
    ("Sept. 2024", "Chargé de Développement 2D", "Poste actuel, au sein de "
     "l'équipe CD2D.", BLUE),
]
cwid = (CW - 0.75) / 4
for i, (date, role, desc, col) in enumerate(xp):
    x = M + i * (cwid + 0.25)
    s.text(x, 2.58, cwid, 0.34,
           [para(date, size=13.5, color=col, bold=True, align="c")])
    s.shape(x + cwid / 2 - 0.085, 3.22, 0.17, 0.17, geom="ellipse", fill=col,
            line="040E18", line_w=2.0, name="Point")
    s.shape(x, 3.70, cwid, 2.05, geom="roundRect", radius=0.06, fill=CARD,
            alpha=48, line=col, line_alpha=50, line_w=1.2, paras=[
                para(role, size=14, color=W, bold=True, align="c", line=1.2),
                para(desc, size=11, color=MUTED, align="c", line=1.32,
                     before=7),
            ], anchor="ctr", pad=(0.16, 0.20, 0.16, 0.20), name="Carte")
s.shape(M, 5.94, CW, 0.76, geom="roundRect", radius=0.09, fill=BLUE, alpha=10,
        line=BLUE, line_alpha=50, line_w=1.3, paras=[
            para("Aujourd'hui", size=9.5, color=DIM, bold=True, caps=True,
                 spc=1.8, align="c"),
            para("Analyser, concevoir, valider et approuver les plans 2D avec "
                 "Capital XC et PLM.", size=14.5, color=W, bold=True,
                 align="c", before=3),
        ], anchor="ctr", pad=(0.10, 0.30, 0.10, 0.30), name="Bandeau")

s = slide(notes=(
    "COMPÉTENCES — DIAPO DE RÉSERVE (masquée dans la version 9 minutes)\n"
    "À afficher pendant les questions si on vous interroge sur vos outils, ou "
    "sur votre capacité à avoir développé l'application vous-même.\n"
    "La troisième colonne est la réponse à « comment avez-vous fait cela "
    "tout seul ? »"
))
header(s, "Compétences", "Métier, technique et numérique")
comp = [
    ("Ingénierie & métier", BLUE,
     "Capital XC  ·  Capital Logic  ·  Modular XC\nPLM / ENOVIA V6  ·  "
     "Teamcenter\nCATIA V5 / V6  ·  Schéma unifilaire"),
    ("Technique & analyse", GREEN,
     "AutoCAD  ·  MATLAB\nLangage C  ·  Programmation\nAnalyse de circuits  ·  "
     "Systèmes énergétiques"),
    ("Création & développement", PURPLE,
     "Photoshop  ·  Illustrator\nPremiere Pro  ·  After Effects\nMotion "
     "graphic  ·  Design  ·  Modélisation 3D"),
]
cwid = (CW - 0.60) / 3
for i, (title, col, body) in enumerate(comp):
    x = M + i * (cwid + 0.30)
    s.shape(x, 2.35, cwid, 2.75, geom="roundRect", radius=0.05, fill=CARD,
            alpha=50, line=col, line_alpha=55, line_w=1.25, name="Carte")
    s.shape(x + 0.38, 2.35, 0.055, 2.75, fill=col, alpha=70, name="Liseré")
    s.text(x + 0.62, 2.72, cwid - 1.0, 0.4,
           [para(title, size=15.5, color=W, bold=True)])
    s.text(x + 0.62, 3.28, cwid - 1.0, 1.6,
           [para(l, size=12, color=MUTED, line=1.5)
            for l in body.split("\n")])
s.text(M, 5.42, CW, 0.3,
       [para("Langues de travail", size=10.5, color=DIM, bold=True, caps=True,
             spc=1.6, align="c")])
chips(s, ["Arabe — langue maternelle", "Français — courant",
          "Anglais — courant"], 5.78, size=11.5, cy=0.42)

s = slide(notes=(
    "MON ÉVOLUTION CHEZ MG2 (1 min 15) — DIAPO CHARNIÈRE\n"
    "Depuis mon arrivée chez MG2, j'ai toujours eu envie de faire quelque "
    "chose de nouveau et d'apporter une valeur supplémentaire à l'équipe. "
    "J'ai donc commencé à proposer des sujets d'innovation.\n"
    "J'ai aussi eu l'occasion d'accompagner des stagiaires et des nouveaux "
    "arrivants, et d'animer des formations pour l'équipe 2D, surtout sur "
    "Capital XC.\n"
    "Avec le temps, j'ai remarqué un besoin : un nouvel arrivant doit "
    "apprendre beaucoup de choses en peu de temps — les bases du métier, "
    "Capital XC, les méthodes de travail et l'environnement du projet.\n"
    "MARQUEZ UN TEMPS, puis : « C'est à partir de ce constat que j'ai pensé "
    "à KATATOOL. »\n"
    "C'est la diapositive qui relie votre parcours au projet. Ne la survolez "
    "pas : c'est elle qui rend la suite légitime."
))
header(s, "Mon évolution chez %s" % COMPANY, "Concevoir, puis transmettre",
       GREEN)
cards_row(s, [
    {"num": "01", "title": "Sujets d'innovation",
     "body": "Proposer et porter des sujets d'innovation pour l'équipe.",
     "color": BLUE},
    {"num": "02", "title": "Accompagnement",
     "body": "Encadrer des stagiaires et les nouveaux arrivants.",
     "color": GREEN},
    {"num": "03", "title": "Formations 2D",
     "body": "Animer les formations de l'équipe 2D, surtout sur Capital XC.",
     "color": PURPLE},
], y=2.28, h=2.62, title_size=16, body_size=12.5)
s.shape(M, 5.10, CW, 1.62, geom="roundRect", radius=0.06, fill=CYAN, alpha=8,
        line=CYAN, line_alpha=45, line_w=1.3, paras=[
            para("Le constat", size=10, color=CYAN, bold=True, caps=True,
                 spc=1.8, align="c"),
            para("Un nouvel arrivant doit apprendre beaucoup de choses en peu "
                 "de temps : les bases du métier, Capital XC, les méthodes de "
                 "travail et l'environnement du projet.", size=12.5,
                 color=MUTED, align="c", line=1.35, before=6),
            para("C'est de ce constat qu'est né KATATOOL.", size=15,
                 color=W, bold=True, align="c", before=8),
        ], anchor="ctr", pad=(0.16, 0.60, 0.16, 0.60), name="Bandeau")

# ======================================================== CHAPITRE 02 ======

s = slide(notes=(
    "TRANSITION (5 s)\n"
    "« Maintenant, le problème que j'ai observé — et que vous connaissez "
    "probablement tous. »"
))
divider(s, "02", "Contexte &\nproblématique",
        "Ce que j'ai constaté sur le terrain, année après année.", ORANGE)

s = slide(notes=(
    "LE CONSTAT (40 s) — SLIDE À FORT IMPACT\n"
    "Marquer une pause de 2 secondes après avoir affiché la phrase.\n"
    "« Quand je suis arrivé, j'ai fait les formations obligatoires. Et après ? "
    "Plus rien. »\n"
    "Le savoir de l'entreprise existe — il est simplement dispersé et "
    "difficile d'accès. Laisser le jury acquiescer."
))
statement(s, "Le constat", ["Le savoir existe.", "Il est introuvable."],
          color=ORANGE, size=52,
          sub="Les formations obligatoires sont faites. Et après ? "
              "Chacun cherche, seul.")

s = slide(notes=(
    "LE PARCOURS ACTUEL (1 min)\n"
    "Dérouler le chemin réel d'un collaborateur qui veut apprendre un outil : "
    "il fait sa formation obligatoire, puis il va sur SharePoint, il cherche "
    "des vidéos, il finit par demander à un collègue sur Teams… et il attend.\n"
    "Point clé à dire clairement : « Ce chemin, chaque personne le refait "
    "depuis le début, à chaque nouveau besoin. »"
))
header(s, "Le parcours actuel", "Comment on apprend aujourd'hui", ORANGE)
flow(s, [
    ("Formation\nobligatoire", "Faite une fois"),
    ("SharePoint", "Où chercher ?"),
    ("Chercher\nune vidéo", "Éparpillée"),
    ("Demander\nsur Teams", "Dépendance"),
    ("Attendre", "Temps perdu"),
], y=2.85, h=1.75, colors=[BLUE, "8CA3BA", ORANGE, ORANGE, PINK],
    box_size=15, sub_size=10.5)
s.text(M, 5.05, CW, 0.4,
       [para("Chaque nouveau besoin recommence de zéro.", size=17, color=W,
             bold=True, align="c")])
s.text(M, 5.52, CW, 0.4,
       [para("Aucune trace, aucune capitalisation, aucun parcours balisé.",
             size=13, color=MUTED, align="c")])

s = slide(notes=(
    "LES QUATRE IRRITANTS (1 min)\n"
    "Nommer les quatre problèmes, un par un, sans lire le texte des cartes.\n"
    "Si le jury doit retenir un seul chiffre : le temps d'un collaborateur "
    "passé à chercher au lieu de produire.\n"
    "Enchaîner directement sur la problématique."
))
header(s, "Les irritants", "Quatre problèmes, un seul point commun", ORANGE)
cards_row(s, [
    {"num": "01", "title": "Information dispersée",
     "body": "Les supports vivent sur SharePoint, dans des mails, sur des "
             "postes locaux. Rien n'est au même endroit.", "color": ORANGE},
    {"num": "02", "title": "Dépendance aux collègues",
     "body": "Apprendre suppose la disponibilité de quelqu'un d'autre. Le "
             "savoir circule à l'oral.", "color": PINK},
    {"num": "03", "title": "Temps perdu",
     "body": "Chercher, attendre, redemander. Du temps d'ingénieur qui ne va "
             "pas au projet.", "color": PURPLE},
    {"num": "04", "title": "Savoir non capitalisé",
     "body": "Ce qui est expliqué en réunion ou en visio disparaît. Le "
             "prochain arrivant repart de zéro.", "color": BLUE},
], y=2.28, h=3.78, title_size=15, body_size=12.5)

s = slide(notes=(
    "PROBLÉMATIQUE (40 s) — LE CŒUR DE LA PRÉSENTATION\n"
    "Lire la question lentement, une seule fois, puis se taire 2 secondes.\n"
    "C'est la phrase que le jury doit retenir. Ne rien ajouter après."
))
statement(s, "Problématique", [
    "Comment réunir en un seul point d'accès",
    "les outils, la formation et les ressources",
    "de chaque équipe — hors ligne, à tout moment ?",
], color=ORANGE, size=34)

s = slide(notes=(
    "OBJECTIFS (45 s)\n"
    "Quatre objectifs fixés avant d'écrire la première ligne de code.\n"
    "Insister sur « Digitaliser » : ce projet s'inscrit dans la démarche de "
    "digitalisation de l'entreprise. Ce n'est pas un projet isolé."
))
header(s, "Objectifs", "Ce que la solution devait faire")
cards_row(s, [
    {"num": "01", "title": "Centraliser",
     "body": "Un seul point d'entrée pour tous les outils et tous les supports "
             "de formation.", "color": BLUE},
    {"num": "02", "title": "Rendre autonome",
     "body": "Apprendre sans attendre personne, à son rythme, quand on en a "
             "besoin.", "color": GREEN},
    {"num": "03", "title": "Standardiser",
     "body": "Le même contenu, le même niveau de départ et la même évaluation "
             "pour tous.", "color": CYAN},
    {"num": "04", "title": "Digitaliser",
     "body": "Transformer un savoir oral et dispersé en un actif numérique "
             "durable.", "color": PURPLE},
], y=2.28, h=3.78, title_size=15.5, body_size=12.5)

# ======================================================== CHAPITRE 03 ======

s = slide(notes=(
    "TRANSITION (5 s)\n"
    "« Voilà ce que j'ai construit. »\n"
    "Changement de ton : on passe du problème à la démonstration. Plus "
    "d'énergie dans la voix."
))
divider(s, "03", "KATATOOL", "La réponse : un hub unique, hors ligne, "
        "bilingue — construit en interne.", GREEN)

s = slide(notes=(
    "TOUT AU MÊME ENDROIT (50 s)\n"
    "La promesse en une phrase : pas d'internet, pas d'installation "
    "compliquée. On ouvre, et on travaille.\n"
    "Donner les chiffres du périmètre actuel, puis préciser que le socle est "
    "extensible : ajouter un outil ou une équipe se fait sans refaire l'app."
))
header(s, "Ce que c'est", "Tout au même endroit", GREEN, align="c")
s.text(1.6, 2.02, SW - 3.2, 0.45,
       [para("Pas d'internet. Pas d'installation compliquée. "
             "On l'ouvre, et on travaille.", size=17, color=MUTED, align="c")])
kw = (CW - 0.9) / 4
for i, (v, l, c) in enumerate([
    ("5", "Applications", BLUE), ("3", "Sections PLM", ORANGE),
    ("4", "Quiz", GREEN), ("2", "Équipes", PURPLE),
]):
    kpi(s, M + i * (kw + 0.30), 3.10, kw, v, l, c)
s.shape((SW - 3.0) / 2, 5.00, 3.0, 0.025, fill=GREEN, alpha=40, name="Filet")
s.text(1.4, 5.30, SW - 2.8, 0.7,
       [para("Le périmètre actuel. Le socle est conçu pour accueillir de "
             "nouveaux outils et de nouvelles équipes sans être reconstruit.",
             size=13.5, color=DIM, align="c", line=1.4)])

s = slide(notes=(
    "ARCHITECTURE (50 s)\n"
    "Expliquer la logique : un tableau de bord unique, puis quatre portes "
    "d'entrée.\n"
    "Cette structure est volontairement plate : deux clics maximum pour "
    "atteindre n'importe quelle ressource."
))
header(s, "Structure", "Un tableau de bord, quatre portes", GREEN)
s.shape((SW - 3.6) / 2, 2.30, 3.6, 0.95, geom="roundRect", radius=0.09,
        fill=CARD, alpha=55, line=GREEN, line_alpha=70, line_w=1.5, paras=[
            para("Tableau de bord", size=19, color=W, bold=True, align="c"),
            para("Point d'entrée unique", size=11, color=MUTED, align="c",
                 before=3),
        ], anchor="ctr", name="Hub")
s.shape(SW / 2 - 0.011, 3.25, 0.022, 0.42, fill="35577A", name="Liaison")
bw = (CW - 0.90) / 4
s.shape(M + bw / 2, 3.67, CW - bw, 0.022, fill="35577A", name="Liaison")
for i, (t, b, c) in enumerate([
    ("Applications", "Les 5 outils du quotidien, avec leur documentation.", BLUE),
    ("Formations", "Parcours débutant puis avancé, construits sur nos "
     "supports réels.", GREEN),
    ("Quiz", "Évaluation à 70 %, qui déverrouille le niveau suivant.", ORANGE),
    ("Espaces équipes", "CD2D et CD3D : macros, outils et procédures propres "
     "à chaque équipe.", PURPLE),
]):
    x = M + i * (bw + 0.30)
    s.shape(x + bw / 2 - 0.011, 3.67, 0.022, 0.36, fill="35577A", name="Liaison")
    s.shape(x, 4.03, bw, 1.85, geom="roundRect", radius=0.06, fill=CARD,
            alpha=48, line=c, line_alpha=55, line_w=1.25, paras=[
                para(t, size=15.5, color=c, bold=True, align="c"),
                para(b, size=11.5, color=MUTED, align="c", line=1.32, before=7),
            ], anchor="ctr", pad=(0.16, 0.22, 0.16, 0.22), name="Carte")

s = slide(notes=(
    "LES OUTILS (45 s)\n"
    "Les cinq applications que nous utilisons réellement. Chacune a sa fiche "
    "et ses supports dans KATATOOL.\n"
    "Ne pas décrire chaque outil : le jury les connaît. Dire simplement "
    "« tout est là, au même endroit »."
))
header(s, "Applications", "Les outils que nous utilisons", GREEN, align="c")
apps = [
    ("Catia V6", "Conception 3D", "3D", BLUE),
    ("Teamcenter", "PLM", "TC", GREEN),
    ("Capital Logic", "Électrique", "CL", PINK),
    ("Modular XC", "Faisceaux", "XC", CYAN),
    ("PLM", "ENOVIA V6", "PLM", PURPLE),
]
aw = (CW - 4 * 0.30) / 5
for i, (name, sub, tag, col) in enumerate(apps):
    x = M + i * (aw + 0.30)
    s.shape(x, 2.55, aw, 2.85, geom="roundRect", radius=0.06, fill=CARD,
            alpha=48, line=col, line_alpha=55, line_w=1.25, name="Carte")
    s.shape(x + aw / 2 - 0.55, 2.95, 1.10, 1.10, geom="roundRect", radius=0.18,
            fill=col, alpha=16, line=col, line_alpha=70, line_w=1.3,
            paras=[para(tag, size=22, color=col, bold=True, align="c")],
            anchor="ctr", name="Icône")
    s.text(x + 0.15, 4.32, aw - 0.30, 0.38,
           [para(name, size=15, color=W, bold=True, align="c")])
    s.text(x + 0.15, 4.72, aw - 0.30, 0.32,
           [para(sub, size=11.5, color=MUTED, align="c")])
s.text(M, 5.68, CW, 0.4,
       [para("Une fiche par outil, avec ses supports et ses points de "
             "vigilance.", size=13, color=DIM, align="c")])

s = slide(notes=(
    "PARCOURS D'APPRENTISSAGE (1 min)\n"
    "C'est le mécanisme central de l'application : on ne saute pas d'étape.\n"
    "On suit le cours débutant, on passe le quiz — 15 questions, 70 % pour "
    "valider — et le niveau avancé se déverrouille.\n"
    "Intérêt pour l'entreprise : on sait que la personne qui accède au niveau "
    "avancé maîtrise réellement les fondamentaux."
))
header(s, "Capital Modular XC", "Un parcours d'apprentissage guidé", GREEN)
flow(s, [
    ("Débutant", "Les fondamentaux"),
    ("Quiz", "15 questions · 70 %"),
    ("Avancé", "Déverrouillé"),
], y=2.90, h=1.70, colors=[GREEN, BLUE, PURPLE], box_size=22, sub_size=13)
s.text(M, 5.10, CW, 0.42,
       [para("On valide le test, le cours avancé s'ouvre.", size=18, color=W,
             bold=True, align="c")])
s.text(M, 5.60, CW, 0.4,
       [para("Le niveau atteint est mesuré, pas déclaré.", size=13.5,
             color=MUTED, align="c")])

s = slide(notes=(
    "CONSTRUIT SUR LES SUPPORTS RÉELS (40 s)\n"
    "Point de crédibilité important : les contenus ne sont pas inventés. Ils "
    "sont construits à partir de nos supports internes et de vraies captures "
    "d'écran de nos outils.\n"
    "Le collaborateur reconnaît immédiatement l'écran qu'il a devant lui.\n"
    "→ REMPLACER LE CADRE PAR VOTRE CAPTURE (Capital XC — Copy Harness Design)."
))
header(s, "Formation débutant", "Construite sur nos supports réels", GREEN)
shot(s, 2.15, 2.30, SW - 4.30, 3.60, "Capital XC — composants & ruban",
     "Insérer ici votre capture d'écran")
s.text(M, 6.08, CW, 0.4,
       [para("Les écrans montrés sont ceux du poste de travail. "
             "Aucun décalage entre la formation et le terrain.",
             size=13, color=DIM, align="c")])

s = slide(notes=(
    "LES EXERCICES (45 s)\n"
    "Deux formats de question : le QCM, tiré directement du cours, et "
    "l'identification de composant sur un schéma — connecteur, épissure, "
    "clip, isolant.\n"
    "À la fin : score, correction et déverrouillage du niveau suivant."
))
header(s, "Exercices", "Apprendre, puis le prouver", GREEN)
cards_row(s, [
    {"num": "01", "title": "Questions à choix multiples",
     "body": "Les questions sont issues directement du contenu du cours. Aucun "
             "piège, uniquement ce qui sert au poste.", "color": BLUE},
    {"num": "02", "title": "Identifier le composant",
     "body": "Connecteur, épissure, clip, isolant — à reconnaître sur un "
             "schéma réel de faisceau.", "color": GREEN},
    {"num": "03", "title": "Déverrouiller la suite",
     "body": "70 % pour valider. Le score et la correction détaillée sont "
             "affichés à la fin du test.", "color": PURPLE},
], y=2.28, h=3.78, title_size=16, body_size=13)

s = slide(notes=(
    "PLM — TROIS SECTIONS (50 s)\n"
    "Le PLM est la partie la plus coûteuse à apprendre, et celle où les "
    "erreurs bloquent le plus. Elle est donc découpée en trois sections.\n"
    "Généralités, Product ECO, puis PDEF & PREA."
))
header(s, "PLM", "Trois sections", ORANGE)
cards_row(s, [
    {"num": "01", "title": "PLM en général",
     "body": "Accès, Security Context, visite guidée de l'interface. Les "
             "bases, une fois pour toutes.", "color": CYAN},
    {"num": "02", "title": "Product ECO",
     "body": "Le créer, le remplir, le libérer — et surtout ce qui vous bloque "
             "et pourquoi.", "color": ORANGE},
    {"num": "03", "title": "PDEF & PREA",
     "body": "Promouvoir, rétrograder, interdire, réviser. Les deux échelles "
             "de statuts.", "color": PURPLE},
], y=2.28, h=3.78, title_size=16, body_size=13)

s = slide(notes=(
    "PLM / ECO — ÉCRANS RÉELS (50 s)\n"
    "C'est la section la plus utile au quotidien : les trois façons de créer "
    "un ECO, la checklist complète des champs à remplir avant de libérer, et "
    "les corrections des blocages les plus fréquents.\n"
    "Exemple concret à citer : « Promotion Failed — vous devez renseigner un "
    "Diversity Manager. » Avant, on cherchait. Maintenant, c'est écrit.\n"
    "→ REMPLACER LE CADRE PAR VOTRE CAPTURE (écran ECO + message d'erreur)."
))
header(s, "PLM / ECO", "Écrans réels, blocages réels", ORANGE)
shot(s, M, 2.30, 7.15, 3.55, "ENOVIA — Product ECO",
     "Insérer ici votre capture d'écran")
rx = M + 7.15 + 0.50
rw = SW - M - rx
for i, (n, t) in enumerate([
    ("1", "Les 3 façons de créer un ECO"),
    ("2", "La checklist de tous les champs à remplir"),
    ("3", "Les corrections des blocages fréquents"),
]):
    y = 2.48 + i * 1.20
    s.shape(rx, y, 0.52, 0.52, geom="roundRect", radius=0.2, fill=ORANGE,
            alpha=15, line=ORANGE, line_alpha=75, line_w=1.1,
            paras=[para(n, size=15.5, color=ORANGE, bold=True, align="c")],
            anchor="ctr", name="Puce")
    s.text(rx + 0.72, y - 0.13, rw - 0.72, 0.78,
           [para(t, size=14.5, color=W, line=1.3)], anchor="ctr")
s.text(rx, 5.95, rw, 0.5,
       [para("« Promotion Failed » n'est plus une énigme.", size=12.5,
             color=DIM, italic=True, line=1.35)])

s = slide(notes=(
    "PDEF & PREA (45 s)\n"
    "Une règle simple, souvent mal comprise : les documents montent d'abord, "
    "le produit suit ensuite, une étape à la fois.\n"
    "Le statut Frozen ne concerne que le PREA — c'est l'erreur classique.\n"
    "Cette seule slide fait gagner du temps à tout le monde."
))
header(s, "PLM / PDEF & PREA", "Les deux échelles", PURPLE)
flow(s, [
    ("In Work", None), ("Frozen", "PREA uniquement"), ("Wait App.", None),
    ("Approved", None), ("Released", None),
], y=2.95, h=1.55, colors=["8CA3BA", PURPLE, BLUE, CYAN, GREEN],
    box_size=17, sub_size=11)
s.text(M, 5.05, CW, 0.42,
       [para("Les documents montent d'abord. Le produit suit, une étape à la "
             "fois.", size=17, color=W, bold=True, align="c")])
s.text(M, 5.55, CW, 0.4,
       [para("Le statut Frozen ne concerne que le PREA — l'erreur la plus "
             "fréquente.", size=13, color=MUTED, align="c")])

s = slide(notes=(
    "ESPACES ÉQUIPES (50 s)\n"
    "C'est la partie que je considère comme la plus différenciante.\n"
    "Chaque équipe a son espace : si vous êtes en CD2D, vous ouvrez CD2D et "
    "vous y trouvez ce que vous devez faire et ce que vous devez savoir. Vous "
    "ne traversez pas le contenu des autres.\n"
    "Le modèle est réplicable pour n'importe quelle autre équipe."
))
header(s, "Espaces équipes", "CD2D & CD3D", CYAN, align="c")
s.text(1.6, 2.02, SW - 3.2, 0.45,
       [para("Chaque équipe ouvre son espace et trouve exactement ce qui la "
             "concerne.", size=17, color=MUTED, align="c")])
tw = 4.55
for i, (name, sub, body, col) in enumerate([
    ("CD2D", "Équipe 2D · Macros",
     "Macros, boîte à outils DSI, procédures de validation 2D et supports "
     "propres à l'équipe.", CYAN),
    ("CD3D", "Équipe 3D",
     "Ressources, méthodes et supports de l'ingénierie 3D faisceaux.", PURPLE),
]):
    x = (SW - (2 * tw + 0.60)) / 2 + i * (tw + 0.60)
    s.shape(x, 2.75, tw, 2.90, geom="roundRect", radius=0.07, fill=CARD,
            alpha=50, line=col, line_alpha=60, line_w=1.4, name="Carte")
    s.text(x + 0.4, 3.10, tw - 0.8, 0.75,
           [para(name, size=38, color=col, bold=True, align="c")])
    s.text(x + 0.4, 3.92, tw - 0.8, 0.34,
           [para(sub, size=13, color=W, bold=True, align="c")])
    s.shape(x + tw / 2 - 0.65, 4.42, 1.30, 0.022, fill=col, alpha=45,
            name="Filet")
    s.text(x + 0.55, 4.65, tw - 1.10, 0.85,
           [para(body, size=12.5, color=MUTED, align="c", line=1.4)])
s.text(M, 5.95, CW, 0.4,
       [para("Le modèle est réplicable : ajouter une équipe ne demande pas de "
             "reconstruire l'application.", size=12.5, color=DIM, align="c")])

s = slide(notes=(
    "BOÎTE À OUTILS DSI (50 s)\n"
    "Un exemple concret de ce que contient l'espace CD2D : un outil Excel "
    "que j'ai développé pour lire un DSI, comparer deux DSI et déplier l'arbre "
    "de diversité avec les règles EXCLUDE / REQUIRE.\n"
    "Ce n'est pas de la documentation : c'est un outil de production, "
    "téléchargeable directement depuis l'application."
))
header(s, "CD2D / .DSI", "La boîte à outils DSI", CYAN)
cards_row(s, [
    {"num": "01", "title": "Lire un DSI",
     "body": "Recensement, éléments, tableaux de cavités, table PTA — mis en "
             "forme et lisibles immédiatement.", "color": GREEN},
    {"num": "02", "title": "Comparer deux DSI",
     "body": "Synthèse, différences et écarts mis en couleur. On voit ce qui a "
             "changé en un coup d'œil.", "color": ORANGE},
    {"num": "03", "title": "Arbre de diversité",
     "body": "Dépliage des combinaisons avec application des règles EXCLUDE / "
             "REQUIRE.", "color": PURPLE},
], y=2.28, h=2.98, title_size=16, body_size=12.5)
chips(s, ["Excel .xlsm", "Téléchargeable dans l'application",
          "Développé en interne"], 5.55, size=12)

s = slide(notes=(
    "CONÇU POUR FONCTIONNER (45 s)\n"
    "Trois choix techniques qui répondent aux contraintes de nos postes.\n"
    "Hors ligne : tout est mis en cache à la première ouverture — aucune "
    "dépendance réseau, aucun problème d'accès.\n"
    "Installable : sa propre fenêtre et son icône sur le bureau.\n"
    "Bilingue FR / EN : un clic, et le choix est mémorisé."
))
header(s, "Choix techniques", "Hors ligne. Installable. Bilingue.", BLUE)
cards_row(s, [
    {"num": "01", "title": "Aucun internet requis",
     "body": "Tout est mis en cache localement dès la première ouverture. "
             "Aucune dépendance au réseau ni aux droits d'accès.", "color": BLUE},
    {"num": "02", "title": "S'installe comme une application",
     "body": "Sa propre fenêtre et son icône sur le bureau. Rien à déployer, "
             "rien à maintenir côté serveur.", "color": GREEN},
    {"num": "03", "title": "Bascule FR / EN",
     "body": "Un clic en haut à droite. Le choix de langue est mémorisé d'une "
             "session à l'autre.", "color": PURPLE},
], y=2.28, h=3.78, title_size=16, body_size=13)

# ======================================================== CHAPITRE 04 ======

s = slide(notes=(
    "TRANSITION (5 s)\n"
    "« Reste la question qui compte : qu'est-ce que ça change ? »"
))
divider(s, "04", "Bénéfices &\nperspectives",
        "Ce que le projet change, et où il peut aller.", PURPLE)

s = slide(notes=(
    "AVANT / APRÈS (1 min) — SLIDE LA PLUS PERSUASIVE\n"
    "Prendre le temps sur cette slide. Lire la colonne de gauche, puis celle "
    "de droite, ligne par ligne.\n"
    "C'est ici que le jury mesure la valeur. Ne pas se précipiter."
))
header(s, "Impact", "Avant / Après", PURPLE, align="c")
colw = 5.55
gapc = 0.55
x0 = (SW - (2 * colw + gapc)) / 2
before_items = [
    "Chercher sur SharePoint, dans les mails, en local",
    "Attendre la disponibilité d'un collègue",
    "Un niveau de départ différent pour chacun",
    "Le savoir expliqué à l'oral, puis perdu",
]
after_items = [
    "Un point d'accès unique, deux clics maximum",
    "Apprendre seul, immédiatement, hors ligne",
    "Le même parcours et la même évaluation pour tous",
    "Un actif numérique qui reste dans l'entreprise",
]
for col, (title, items, mark, ccol) in enumerate([
    ("Avant", before_items, "✕", PINK),
    ("Avec KATATOOL", after_items, "✓", GREEN),
]):
    x = x0 + col * (colw + gapc)
    s.shape(x, 2.25, colw, 3.85, geom="roundRect", radius=0.05, fill=CARD,
            alpha=48, line=ccol, line_alpha=55, line_w=1.3, name="Colonne")
    s.text(x, 2.50, colw, 0.42,
           [para(title, size=19, color=ccol, bold=True, align="c")])
    s.shape(x + colw / 2 - 0.85, 3.08, 1.70, 0.022, fill=ccol, alpha=40,
            name="Filet")
    for i, it in enumerate(items):
        y = 3.35 + i * 0.66
        s.text(x + 0.42, y, 0.34, 0.42,
               [para(mark, size=14, color=ccol, bold=True)])
        s.text(x + 0.86, y, colw - 1.30, 0.60,
               [para(it, size=12.5, color=MUTED if col == 0 else W, line=1.3)])

s = slide(notes=(
    "BÉNÉFICES (1 min)\n"
    "Quatre bénéfices, du plus opérationnel au plus stratégique.\n"
    "Le quatrième est celui qui parle à la direction : KATATOOL est montrable "
    "à un client qui visite le site."
))
header(s, "Bénéfices", "Ce que le projet apporte", PURPLE)
cards_row(s, [
    {"num": "01", "title": "Intégration accélérée",
     "body": "Un nouvel arrivant devient opérationnel plus vite, sans "
             "mobiliser un collègue senior.", "color": BLUE},
    {"num": "02", "title": "Autonomie réelle",
     "body": "Chacun apprend quand il en a besoin, à son rythme, sans "
             "dépendre de la disponibilité d'autrui.", "color": GREEN},
    {"num": "03", "title": "Savoir capitalisé",
     "body": "Ce qui était transmis à l'oral devient un contenu durable, "
             "réutilisable et vérifiable.", "color": ORANGE},
    {"num": "04", "title": "Image et différenciation",
     "body": "Un outil interne démontrable, qui prouve notre maturité "
             "numérique face à un client.", "color": PURPLE},
], y=2.28, h=3.78, title_size=15, body_size=12.5)

s = slide(notes=(
    "VITRINE CLIENT (40 s)\n"
    "Argument à assumer clairement devant le jury : quand un client visite nos "
    "locaux, nous pouvons ouvrir KATATOOL et montrer un outil que nous avons "
    "conçu nous-mêmes, pour nos propres besoins.\n"
    "Ce n'est pas un slogan : c'est une preuve de maturité et de démarche "
    "d'amélioration continue.\n"
    "Rester factuel, ne pas survendre."
))
statement(s, "Argument client", [
    "Un outil que nous montrons,",
    "pas seulement un discours.",
], color=PURPLE, size=44,
    sub="KATATOOL est la preuve concrète de notre démarche de digitalisation "
        "et d'amélioration continue.")
chips(s, ["Développé en interne", "Sans coût de licence",
          "Démontrable en 2 minutes"], 6.05, size=12)

s = slide(notes=(
    "PERSPECTIVES (50 s)\n"
    "Montrer que le projet n'est pas terminé et qu'il a une trajectoire.\n"
    "Étendre le catalogue d'outils, ouvrir à d'autres équipes, suivre les "
    "compétences validées, ajouter de la vidéo courte.\n"
    "Formulation : « Voilà ce que je propose pour la suite » — pas « il "
    "faudrait »."
))
header(s, "Perspectives", "Les prochaines étapes", PURPLE)
flow(s, [
    ("Étendre\nle catalogue", "Nouveaux outils"),
    ("Ouvrir à\nd'autres équipes", "Modèle réplicable"),
    ("Suivi des\ncompétences", "Qui a validé quoi"),
    ("Contenus\nvidéo", "Formats courts"),
], y=2.85, h=1.85, colors=[BLUE, GREEN, ORANGE, PURPLE], box_size=15.5,
    sub_size=11)
s.text(M, 5.20, CW, 0.42,
       [para("Le socle est en place. Ce qui vient ensuite est de "
             "l'enrichissement, pas de la reconstruction.",
             size=15.5, color=W, bold=True, align="c")])
s.text(M, 5.72, CW, 0.4,
       [para("Je suis disponible pour former les équipes qui souhaitent "
             "l'utiliser.", size=13, color=MUTED, align="c")])

s = slide(notes=(
    "CONCLUSION (30 s)\n"
    "Une seule phrase, dite lentement, en regardant le jury.\n"
    "Puis se taire. Ne pas ajouter de commentaire — laisser la phrase agir."
))
statement(s, "Conclusion", [
    "D'une recherche de plusieurs jours",
    "à un point d'accès unique.",
], color=GREEN, size=44,
    sub="J'ai identifié le problème sur le terrain, et j'ai construit la "
        "réponse avec les moyens de l'entreprise.")

s = slide(notes=(
    "MERCI / QUESTIONS (le reste du temps)\n"
    "Remercier, puis ouvrir les questions.\n"
    "\n"
    "QUESTIONS PROBABLES — réponses préparées :\n"
    "· « Combien de temps pour le développer ? » → donner un chiffre honnête, "
    "et préciser : sur mon temps, sans impact sur les livrables projet.\n"
    "· « Qui met le contenu à jour ? » → proposer un référent par équipe ; je "
    "reste garant de la structure.\n"
    "· « Et la confidentialité des données ? » → 100 % local, aucune donnée ne "
    "sort du poste, aucun serveur externe.\n"
    "· « Pourquoi pas SharePoint ? » → SharePoint stocke ; KATATOOL guide, "
    "évalue et fonctionne hors ligne.\n"
    "· « Est-ce maintenable si vous partez ? » → structure simple et "
    "documentée, contenu séparé du code."), numbered=False)
s.shape((SW - 1.35) / 2, 1.30, 1.35, 1.35, geom="roundRect", radius=0.16,
        fill="0F2540", alpha=45, line="2E5177", line_alpha=60, line_w=1.2,
        dash="dash",
        paras=[para("LOGO", size=10, color="547590", bold=True, align="c",
                    spc=1.5)], anchor="ctr", name="Logo")
s.text(0, 2.95, SW, line_h(68) + 0.03,
       [para("Merci", size=68, color=W, bold=True, align="c")])
s.text(1.4, 4.28, SW - 2.8, 0.5,
       [para("On l'ouvre, on apprend, on se teste, on récupère ses outils.",
             size=17, color=MUTED, align="c")])
chips(s, ["Tableau de bord", "Formations", "Quiz", "Outils équipes"], 4.95)
s.text(0, 5.85, SW, 0.4,
       [para("Vos questions", size=17, color=CYAN, bold=True, align="c")])
s.text(0, 6.35, SW, 0.32,
       [para("Youssef OUBELLA · Chargé de Développement 2D · Équipe CD2D",
             size=11.5, color=DIM, align="c")])

# ---------------------------------------------------------------- output ---

out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "KATATOOL_Soutenance_Youssef_OUBELLA.pptx")
prs.save(out, title=TITLE, author=AUTHOR)
print("%d slides -> %s" % (len(prs.slides), out))
if FITS:
    print("\nTextes ajustes automatiquement :")
    for kind, label, size, need, avail in FITS:
        print("  %-8s %-42s %.1f pt (%.2f\" / %.2f\")"
              % (kind, str(label)[:42], size, need, avail))
