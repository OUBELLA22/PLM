# PLM methodology presentations

Two decks generated from the methodology documents in this repository, plus the (dependency-free)
toolchain that builds them.

| Deck | Source document | Slides | Files |
|---|---|---|---|
| **Product ECO** | `2 METHODOLOGY_Creating_a_Product_ECO.pdf` (Ref. 20061_17_01638 v8.0) | 21, 11 screenshots | `ECO_Product_Presentation.pptx` / `.html`, `preview/`, `img/`, `content.py` |
| **PDEF & PREA lifecycle (EE)** | `4 METHODOLOGY_PDEF_PREA_lifecycle_management_EE_specific.pdf` (Ref. 20061_15_01662 v1.0) | 22, 13 screenshots | `PDEF_PREA_Lifecycle_Presentation.pptx` / `.html`, `preview_pdef/`, `img_pdef/`, `content_pdef.py` |

Each deck ships in three forms: an editable 16:9 **PowerPoint**, a self-contained **HTML** deck
(pictures inlined, `←` `→` to navigate, `Ctrl/Cmd+P` → Save as PDF), and **PNG previews** of every
slide for reading straight on GitHub.

## Rebuild

```bash
python3 render_html.py            && python3 render_pptx.py            && python3 verify_pptx.py ECO_Product_Presentation.pptx
python3 render_html.py content_pdef && python3 render_pptx.py content_pdef && python3 verify_pptx.py PDEF_PREA_Lifecycle_Presentation.pptx
```

## Toolchain

| File | Role |
|---|---|
| `content.py`, `content_pdef.py` | All slide text and picture assignments — the only files to edit for wording |
| `deck.py` | Picks the content module given on the command line; resolves output name and image folder |
| `render_html.py` | HTML deck: container-query layout, pictures as data URIs |
| `render_pptx.py` | PowerPoint: OOXML written directly (no python-pptx), pictures embedded as media parts |
| `verify_pptx.py` | Structural check: parts, relationships, shape ids, picture refs, aspect ratios, footer overrun, picture/text collisions |
| `extract_pdf_images.py` | Pulls image XObjects out of a PDF (FlateDecode → PNG, DCTDecode → JPEG) |
| `extract_pdf_text.py` | Extracts page text via ToUnicode CMaps, and lists the images each page uses |
| `pngtool.py` | Crops 8-bit RGB PNGs (used to split the tall ECO creation form) |
| `imgutil.py` | Picture size / aspect-fit helper |

Slide kinds available to a content module: `title`, `bullets` (1 or 2 columns), `steps`, `flow`,
`cards`, `table`, `glossary`, `shot` (one picture + notes), `shots` (two pictures side by side),
`close`. Any text slide can carry `"image"` for a side panel, or `"image_pos": "below"`.

> The screenshots come from internal methodology documents and show internal names, IDs and project
> references. Check that before sharing the decks outside the perimeter they were written for.
