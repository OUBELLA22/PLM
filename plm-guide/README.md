# PLM Change Guide — PDEF / ECR / ECO

A field guide to creating a **PDEF**, an **ECR** and a **Product ECO** in PLM
(ENOVIA V6): the click paths, the attributes that are genuinely mandatory, the
order the system expects, and the tricks and blockers that decide whether a
promotion goes through.

Two editions, built from the same content module:

| Deliverable | Format | For |
|---|---|---|
| [`PLM_PDEF_ECR_ECO_Guide.docx`](PLM_PDEF_ECR_ECO_Guide.docx) | A4 portrait, white, greyscale only, 28 figures | **Editing.** Every highlight is a real Word shape you can move, resize, restyle or delete |
| [`PLM_PDEF_ECR_ECO_Guide.pdf`](PLM_PDEF_ECR_ECO_Guide.pdf) | A4 landscape, 59 pages, dark theme, 28 figures | Reading and presenting |

## The Word edition

White page, black text, grey rules — no colour theme. Built so that **everything
can be changed**:

- Each figure is a **group of Word shapes** over the unmodified screenshot: one
  rectangle per highlight, one numbered circle per marker. Click into the group
  and drag, resize, recolour or delete any of them; copy one to add another.
- Every shape is **named**, so `Home ▸ Find & Select ▸ Selection Pane` lists them
  as e.g. `Highlight 7.3 — Create Product ECO…` and `Marker 7.3`.
- Nothing is burnt into the image, so the screenshot underneath stays intact
  whatever you do to the annotations.
- Real **Heading 1/2/3 styles**, so the Navigation pane works and the table of
  contents field builds itself (`right-click ▸ Update Field`).
- Legends under each figure are plain numbered text, so they are editable too.
- Tables, lists and note boxes are native Word objects.

The front of the document repeats these instructions, so whoever opens it knows
how to adjust the annotations.

Only the screenshots carry colour, because they are the PLM interface as it
actually looks; the document design itself is verified greyscale.

## What is in it

| Chapter | Content |
|---|---|
| Start here | How to read the figures; what each highlight colour means |
| Orientation | The change chain: PDEF/PREA → ECR → ECO → RT → RAL → Released |
| 1 | Creating a PDEF (and a PREA): the cloning principle, which library, the identity card |
| 2 | Creating an ECR: entry point, the `Design` state gate, the ECO under the ECR |
| 3 | Creating a Product ECO: three use cases, the form, V/O/M impacts, batch creation, due dates |
| 4 | From created to released: documents first, promote/demote, RT then RAL, PREA specifics, prohibition |
| 5 | Typical cases and traps, including the `Promotion Failed` diversity-manager block |
| 6 | Tricks that save time, consolidated |
| 7 | Troubleshooting: symptom → fix |
| 8 | French-to-English UI decoder, acronyms, source references |

## How the screenshots are treated

The platform screenshots are **not modified**. Their original bytes are embedded
in the PDF untouched:

- PNG — the `IDAT` stream is copied verbatim into a `/FlateDecode` image with
  `/Predictor 15`, because a PNG IDAT already *is* a zlib stream of
  filter-prefixed scanlines.
- JPEG — the compressed data is copied verbatim into a `/DCTDecode` image.

Everything that makes a figure look enhanced — the HUD panel, corner brackets,
neon glow, highlight rings, numbered markers and legends — is **PDF vector art
drawn on top of** the picture. So the PLM interface is pixel-identical to the
source methodology; only the annotation layer is new. `verify_pdf.py` re-decodes
every embedded image to prove it.

Highlight boxes are authored in *screenshot pixel coordinates*, so they stay
aligned at whatever scale a figure is drawn.

## Files

| File | Role |
|---|---|
| `content_guide.py` | **Shared content**: chapters, tables, tips, and the figure/highlight coordinates |
| `guide.py` | PDF layout engine (paginating blocks) and its annotation layer |
| `pdfwriter.py` | Minimal PDF writer: pages, Helvetica metrics, images, alpha, gradients |
| `build_guide.py` | Builds the PDF (two passes, so footers can show `n / total`) |
| `docxwriter.py` | Minimal .docx writer; `figure_group` emits the editable shape groups |
| `build_docx.py` | Maps the shared content blocks to WordprocessingML |
| `verify_pdf.py` | Structure, geometry, image decode and page fill of the PDF |
| `verify_docx.py` | Package, relationships, shape bounds, schema order and greyscale of the .docx |
| `verify_marks.py` | Checks every highlight box sits inside its screenshot |
| `extract_pdf_text.py` | Pulls text and a per-page image inventory out of a source PDF |
| `img/`, `img_prea/` | The screenshots, exactly as extracted from the sources |

No third-party dependency: the whole toolchain is the Python standard library,
because this environment has no reportlab, python-docx, PIL, PyMuPDF, LibreOffice
or headless browser.

## Build

```bash
python3 build_guide.py && python3 verify_pdf.py && python3 verify_marks.py
python3 build_docx.py  && python3 verify_docx.py
```

Edit `content_guide.py` and both editions pick the change up.

## Sources

| Tag | Document | Reference |
|---|---|---|
| [A] | METHODOLOGY Creating a Product ECO (TRANSVERSAL, COMETH PLM) | 20061_17_01638 · v8.0 · 17/04/2024 |
| [B] | METHODOLOGY PDEF and PREA lifecycle management (EE specific) | 20061_15_01662 · v1.0 |
| [C] | PREA methodologies — Creation of a PDEF / Creation of a PREA in PLM | Word memo in this repo |

### Known scope limit

The three source documents specify the ECR only as *the object an ECO hangs
under* — its entry point in the `Actions ▸ Change` menu and the `Design` state it
must reach. They do **not** contain a field-by-field ECR creation form. Chapter 2
covers what the sources actually show and points to
`METHODOLOGY Add/Remove ECO under ECR` (20061_17_01982) for the rest. Nothing in
that chapter is invented.

## Confidentiality

The screenshots come from internal methodologies and still carry real product
references, project names and user IDs. Treat this document as internal.
