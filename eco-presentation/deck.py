# -*- coding: utf-8 -*-
"""Deck selector: `python3 render_html.py [content_module]` (default: content).

Exposes META / SLIDES of the chosen module and resolves its output path, so the same
renderers serve several decks. META may carry "outfile" and "imgdir".
"""
import importlib
import os
import sys

import imgutil

HERE = os.path.dirname(os.path.abspath(__file__))
_name = "content"
for a in sys.argv[1:]:
    if not a.startswith("-"):
        _name = os.path.basename(a).replace(".py", "")
        break

_mod = importlib.import_module(_name)
META, SLIDES = _mod.META, _mod.SLIDES
imgutil.set_dir(META.get("imgdir", "img"))


def outfile(ext):
    return os.path.join(HERE, "%s.%s" % (META.get("outfile", "ECO_Product_Presentation"), ext))
