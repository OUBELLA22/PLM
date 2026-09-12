# Product ECO — presentation

21 slides built from *METHODOLOGY Creating a Product ECO* (Ref. 20061_17_01638, v8.0, 17/04/2024),
including 11 screenshots extracted from the source PDF.

| File | Use |
|---|---|
| `ECO_Product_Presentation.pptx` | Editable PowerPoint, 16:9, pictures embedded |
| `ECO_Product_Presentation.html` | Self-contained deck (images inlined): `←` `→` to navigate, `Ctrl/Cmd+P` → Save as PDF |
| `preview/slide-01..21.png` | Static preview of every slide |
| `img/` | Curated screenshots used by the deck |
| `content.py` | All slide text and picture assignments — edit here, then rebuild |
| `render_html.py` / `render_pptx.py` | Renderers, no dependencies |
| `verify_pptx.py` | Checks the generated `.pptx`: parts, relationships, shape ids, picture refs, aspect ratios, collisions |
| `extract_pdf_images.py` | Pulls image XObjects out of a PDF (stdlib only) |
| `pngtool.py` | Crops 8-bit RGB PNGs (used to split the tall creation form in two) |

Rebuild:

```bash
python3 render_html.py && python3 render_pptx.py && python3 verify_pptx.py
```

Deck flow: what an ECO is → where it sits (lifecycle) → prerequisites → 3 ways to create →
Actions menu → creation form → batch creation → attribute checklist → V/O/M & manufacturing site →
project-space search → create from product / from ECR → linking → due dates → Neutral & colours →
3 evolutions → the promotion blocker → tips → blockers & fixes → glossary → 5 takeaways.

> The screenshots come from the internal methodology document and show internal names, IDs and
> project references. Check that before sharing the deck outside the perimeter it was written for.
