# -*- coding: utf-8 -*-
"""Measures the spoken length of the speech: words, then duration per rate."""

import io
import re
import sys

PATH = sys.argv[1] if len(sys.argv) > 1 else "/projects/sandbox/DISCOURS_9MIN.md"
LIMIT = 9 * 60          # the hard ceiling asked for
PAUSES = 7              # the three held silences + the opening beat
SLIDES = 22
PER_SLIDE = 1.2         # click + breath between slides, in seconds

text = io.open(PATH, encoding="utf-8").read()


def spoken(seg):
    """Strip stage directions, headings and tables - keep only what is said."""
    out = []
    for ln in seg.split("\n"):
        s = ln.strip()
        if not s or s.startswith(("#", "|", "---", ">")):
            continue
        if s.startswith("**[") and s.endswith("]**"):
            continue
        s = re.sub(r"\*\*\[[^\]]*\]\*\*", "", s).replace("**", "").strip()
        if s:
            out.append(s)
    return " ".join(out)


def words(seg):
    return len(re.findall(r"[\w\u00c0-\u00ff'\u2019-]+", spoken(seg)))


body = text.split("## OUVERTURE")[1].split("## Repères de contrôle")[0]
total = words(body)
overhead = PAUSES + SLIDES * PER_SLIDE

print("Mots prononcés          : %d" % total)
print("Silences + transitions  : %d s" % overhead)
print("")
worst = 0
for rate, label in [(115, "très lent"), (120, "lent"), (130, "posé"),
                    (140, "posé/normal"), (150, "normal")]:
    sec = total / float(rate) * 60 + overhead
    worst = max(worst, sec if rate >= 120 else 0)
    print("  %3d mots/min (%-12s) -> %d min %02d s   %s"
          % (rate, label, sec // 60, sec % 60,
             "OK" if sec <= LIMIT else "!! DEPASSE 9 MIN"))

print("")
print("Découpage par section (à 130 mots/min) :")
marks = [("Ouverture", "## OUVERTURE"), ("Chapitre 01", "## CHAPITRE 01"),
         ("Chapitre 02", "## CHAPITRE 02"), ("Chapitre 03", "## CHAPITRE 03"),
         ("Chapitre 04", "## CHAPITRE 04"), ("Conclusion", "## CONCLUSION")]
cum = 0.0
for name, key in marks:
    seg = text.split(key)[1]
    for nxt in ["## CHAPITRE", "## CONCLUSION", "## Repères"]:
        if nxt in seg:
            seg = seg.split(nxt)[0]
    w = words(seg)
    sec = w / 130.0 * 60
    cum += sec
    print("  %-12s %4d mots   %d:%02d   cumul %d:%02d"
          % (name, w, sec // 60, sec % 60, cum // 60, cum % 60))

print("")
if worst <= LIMIT:
    print("OK — reste sous 9 min même à 120 mots/min (débit lent).")
    sys.exit(0)
print("!! trop long : retirer environ %d mots."
       % int((worst - LIMIT) / 60.0 * 120))
sys.exit(1)
