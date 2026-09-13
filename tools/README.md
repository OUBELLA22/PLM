# Deck generator

`1 PLM INTERFACE - Enhanced.pptx` is generated from code, so the design system
(colours, spacing, typography) can be changed in one place and re-applied to
every slide.

```bash
cd tools
python3 build_deck.py              # rebuilds ../1 PLM INTERFACE - Enhanced.pptx
python3 build_deck.py --preview    # also writes preview_all.png (layout check)
```

No third-party packages required (Python 3 standard library only).

| File | Role |
| --- | --- |
| `build_deck.py` | Slide content and layout — the deck itself |
| `pptxlib.py` | Minimal OOXML `.pptx` writer + text-metric validator |
| `preview.py` | Renders the same shape specs to PNG for layout checking |

Wording comes from `../1 PLM INTERFACE.pptx`; the screenshots and base theme
are read straight out of that file at build time, so the original stays the
single source of truth for content.

`build_deck.py` prints a layout warning for any text that overflows its box or
any shape that leaves the canvas — it should report `0 layout warning(s)`.
