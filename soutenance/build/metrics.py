# -*- coding: utf-8 -*-
"""Approximate Segoe UI text metrics, shared by the builder and the checker."""

PT_IN = 72.0
LINE_EM = 1.30  # single-line box height in em

_W = {}
for _chars, _val in [
    (" \u00a0", 0.26),
    (".,:;'`!|iljI\u2019", 0.30),
    ("ft()[]{}/\\-\u2013\u2014r", 0.36),
    ("abcdeghknopqsuvxyzcL1\u00e9\u00e8\u00ea\u00e0\u00e7\u00f9\u00fb\u00ee\u00ef\u00f4", 0.51),
    ("023456789", 0.56),
    ("ABCDEFGHJKNOPQRSTUVXYZ?&+=<>\u00c9\u00c0\u00c7\u2192\u2713\u2715\u00b7%", 0.62),
    ("mwMW\u0153", 0.80),
    ("@", 0.75),
]:
    for _c in _chars:
        _W[_c] = _val


def text_w(s, size_pt, bold=False):
    """Rendered width of a string, in inches."""
    em = sum(_W.get(c, 0.55) for c in s)
    return em * (size_pt / PT_IN) * (1.045 if bold else 1.0)


def wrap_info(text, size_pt, bold, avail_in):
    """(line count, width of the widest resulting line, widest single word).

    Honours hard newlines, so a manually broken heading is measured on its
    real line widths rather than assumed to fill the whole box.
    """
    total, widest_line, widest_word = 0, 0.0, 0.0
    for hard in str(text).split("\n"):
        words = hard.split(" ")
        if not words:
            total += 1
            continue
        line, n = "", 1
        for wd in words:
            widest_word = max(widest_word, text_w(wd, size_pt, bold))
            cand = wd if not line else line + " " + wd
            if text_w(cand, size_pt, bold) <= avail_in:
                line = cand
            else:
                widest_line = max(widest_line, text_w(line, size_pt, bold))
                n += 1
                line = wd
        widest_line = max(widest_line, text_w(line, size_pt, bold))
        total += n
    return total, min(widest_line, avail_in), widest_word


def wrap_lines(text, size_pt, bold, avail_in):
    """(line count after wrapping, width of widest unbreakable word)."""
    lines, _, word = wrap_info(text, size_pt, bold, avail_in)
    return lines, word


def line_h(size_pt, mult=1.0):
    """Height of one line, in inches."""
    return (size_pt / PT_IN) * LINE_EM * mult


def block_h(text, size_pt, avail_in, bold=False, mult=1.0):
    """Height needed to render `text` wrapped to `avail_in`, in inches."""
    lines, _ = wrap_lines(text, size_pt, bold, avail_in)
    return lines * line_h(size_pt, mult)
