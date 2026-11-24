# -*- coding: utf-8 -*-
"""Content of the PDEF / ECR / ECO creation guide.

Every statement below is taken from one of the three source documents that ship
with this repository, and every screenshot is the untouched picture extracted
from them:

  [A] METHODOLOGY Creating a Product ECO
      Ref. 20061_17_01638, v8.0, 17/04/2024, TRANSVERSAL (COMETH PLM).
  [B] METHODOLOGY PDEF and PREA lifecycle management (EE specific)
      Ref. 20061_15_01662, v1.0, ELECTRICAL SPEC.
  [C] PREA methodologies - Creation of a PDEF / Creation of a PREA in PLM
      (Word memo, with its own embedded screenshots).

`marks` coordinates are pixel rectangles (x, y, w, h) measured on the original
screenshot, so the annotation layer stays aligned whatever scale the figure is
drawn at.
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))

META = {
    "title": "PLM Change Guide",
    "short": "PLM \u00b7 PDEF \u00b7 ECR \u00b7 ECO",
    "footer": "PLM Change Guide \u2014 PDEF / ECR / ECO creation \u00b7 sources 20061_17_01638 v8.0, "
              "20061_15_01662 v1.0",
    "author": "COMETH PLM methodologies (compiled)",
    "subject": "Creating a PDEF, an ECR and a Product ECO in PLM (ENOVIA): steps, "
               "required attributes, tricks and blockers",
}


def img(name):
    """Resolve a screenshot to its folder."""
    for sub in ("img", "img_prea"):
        p = os.path.join(HERE, sub, name)
        if os.path.exists(p):
            return p
    raise IOError("missing screenshot: %s" % name)


def fig(image, **kw):
    b = {"kind": "figure", "image": image, "path": img(image)}
    b.update(kw)
    return b


# ===========================================================================
def build():
    B = []
    add = B.append

    # ----------------------------------------------------------------- cover
    add({
        "kind": "cover",
        "kicker": "Stellantis \u00b7 COMETH PLM \u00b7 ENOVIA V6",
        "title": "Creating a PDEF,",
        "title2": "an ECR and an ECO",
        "subtitle": "The three objects that make a product change official",
        "tagline": [("A field guide: the exact click path, the attributes that are really "
                     "mandatory, the order the system expects \u2014 and the ", ""),
                    ("tricks and blockers", "b"),
                    (" that decide whether your promotion goes through or fails.", "")],
        "specs": [("Scope", "PDEF \u00b7 ECR \u00b7 ECO"),
                  ("Tool", "ENOVIA V6 (PLM)"),
                  ("Roles", "Pilote Projet / Concepteur"),
                  ("Screens", "Annotated, unmodified")],
        "meta": "Compiled from METHODOLOGY Creating a Product ECO (20061_17_01638 v8.0, 17/04/2024) \u00b7 "
                "METHODOLOGY PDEF and PREA lifecycle management EE (20061_15_01662 v1.0) \u00b7 "
                "PREA methodologies: Creation of a PDEF / PREA in PLM.",
    })

    # ------------------------------------------------------- how to read it
    add({"kind": "h2", "eyebrow": "Start here", "title": "How to read this guide"})
    add({"kind": "para", "text": [
        ("Every screenshot in this document is the ", ""),
        ("original picture from the official methodology, unmodified", "b"),
        (". The PLM interface you see is exactly the interface in the source guide \u2014 no "
         "button, label or value has been altered. What has been added is an ", ""),
        ("annotation layer", "acc"),
        (": rings around the control you need, numbered markers, and a short note for each "
         "one. The colour of a ring tells you what kind of thing it is.", "")]})
    add({"kind": "space", "h": 4})
    add({"kind": "cards", "cards": [
        {"tag": "Cyan", "title": "Where to click", "tone": "acc2",
         "lines": ["The control, tab or menu entry that moves you forward.",
                   "Follow the numbers in order."]},
        {"tag": "Blue", "title": "Context", "tone": "acc",
         "lines": ["The field or column that explains the screen.",
                   "Useful to understand, not a click."]},
        {"tag": "Amber", "title": "Mandatory / careful", "tone": "warn",
         "lines": ["Required to create or to release.",
                   "Or an action that is easy to get wrong."]},
        {"tag": "Red", "title": "Blocker", "tone": "dan",
         "lines": ["The thing that makes a promotion fail.",
                   "Fix it before you try again."]},
    ]})
    add({"kind": "space", "h": 8})
    add({"kind": "callout", "tone": "ok", "label": "Reading order",
         "text": [("Chapters 1 to 3 are the three creations, in the order the process "
                   "needs them. Chapter 4 is what happens after creation \u2014 how the ECO "
                   "actually releases the product. Chapters 5 to 8 are the special cases, "
                   "the consolidated tricks, the troubleshooting table and a ", ""),
                  ("French-to-English label decoder", "b"),
                  (", because several PLM screens in the sources are the French UI.", "")]})

    # ---------------------------------------------------------- the chain
    add({"kind": "h2", "eyebrow": "Orientation", "title": "The change chain"})
    add({"kind": "para", "text": [
        ("Nothing becomes official on its own. A product is ", ""),
        ("defined", "b"), (" (PDEF) or ", ""), ("realized", "b"),
        (" (PREA), a change is ", ""), ("requested", "b"), (" (ECR), and the change is ", ""),
        ("ordered and approved", "b"),
        (" (ECO). The ECO is the gate: it is the object that carries approvals, "
         "homologation and impacts, and it is what finally turns a product into "
         "Released.", "")]})
    add({"kind": "flow", "rows": [
        {"label": "The objects, in order", "style": "accent",
         "chips": ["PDEF / PREA", "ECR (Design)", "ECO", "RT review", "RAL review",
                   "Released"]},
    ]})
    add({"kind": "space", "h": 2})
    add({"kind": "table", "colw": (0.14, 0.30, 0.56), "head": ["Object", "What it is", "Who creates it, and when"], "rows": [
        ["PDEF", "Defined Product \u2014 the engineering definition of a part.",
         "Cloned from a generic in a library by the designer, before any change is "
         "requested. Source [C]."],
        ["PREA", "Realized Product \u2014 the manufactured answer to a PDEF.",
         "Cloned from a generic PREA, same principle as the PDEF. Only the PREA has a "
         "Frozen state and a Cancel-and-revise action. Source [C] and [B]."],
        ["ECR", "Engineering Change Request \u2014 the demand for a change.",
         "Created from Actions \u203a Change \u203a Create ECR. It must reach the state "
         "Design before an ECO can be created under it. Source [A]."],
        ["ECO", "Engineering Change Order \u2014 the official change itself; the "
                "equivalent of the FM (change sheet) in SAP / 3DCom.",
         "Created in one of three ways (chapter 3), then promoted through RT and RAL "
         "reviews until Released. Source [A]."],
    ]})
    add({"kind": "callout", "tone": "warn", "label": "The one rule to remember",
         "text": [("No released product without an ECO.", "b"),
                  (" Every other rule in this guide exists to get the ECO through its "
                   "two approval routes.", "")]})

    # =====================================================================
    # CHAPTER 1 - PDEF
    # =====================================================================
    add({
        "kind": "chapter", "num": "1", "eyebrow": "Chapter 1",
        "title": "Creating a PDEF (and a PREA)",
        "lead": [("A defined product is never built from a blank form. You ", ""),
                 ("clone a generic", "b"),
                 (" from the right library, then fill its identity card. Which library "
                  "depends on the product nature \u2014 and cloning the wrong thing is "
                  "explicitly prohibited.", "")],
        "covers": ["The cloning principle and the library to start from",
                   "Which attributes are mandatory, and which one you cannot undo",
                   "The identity card, screen by screen",
                   "Electrical / electronic specifics and mass creation",
                   "Tricks and traps"],
    })

    add({"kind": "h2", "eyebrow": "Principle", "title": "You clone, you do not create from scratch"})
    add({"kind": "steps", "steps": [
        [("Find the ", ""), ("generic product", "b"),
         (" that matches your ", ""), ("Product Nature", "ui"),
         (" in the right library (table below).", "")],
        [("Clone it ", ""), ("via the Graphical Browser", "b"),
         (", using the generic product as the source.", "")],
        [("Fill the identity card", "b"),
         (" \u2014 the mandatory attributes are the ones shown in red italics.", "")],
        [("Take the ", ""), ("PSA Reference", "ui"),
         (" afterwards, with the PSA Reference methodology. It is empty at creation "
          "time and it is required later to promote the product.", "")],
        [("Attach an ", ""), ("ECO", "ui"),
         (" to the product. Without it the product cannot leave In Work. See chapter 3.", "")],
    ]})
    add({"kind": "callout", "tone": "dan", "label": "Prohibited",
         "text": [("Cloning a non-generic PREA is prohibited.", "b"),
                  (" Always start from the generic published in the library for your "
                   "product nature. Source [C].", "")]})

    add({"kind": "h2", "eyebrow": "Where to start", "title": "Which library holds your generic"})
    add({"kind": "table", "colw": (0.44, 0.33, 0.23), "head": ["Product nature", "Library holding the generic", "Note"], "rows": [
        ["Mecanique", "DECOUPAGE PSA (PSA Classification Library)",
         "Clone the generic PREA."],
        ["Calibration, Data Library, Dote, Logiciel masque, Mecanique Electronique "
         "Electrique, Soft, Vehicle Application",
         "CATALOGUE INGENIERIE", "Clone the generic PREA."],
        ["Products held in LIBRARY REPETITIVE (POFI and NON POFI)",
         "No generic",
         "The PDEF is created without a generic."],
        ["Connectors and peri-connectors",
         "LIBRARY REPETITIVE NON POFI",
         "PDEF creation is handled by the NON POFI Manager, not by you."],
        ["Electrical harness (PREA)",
         "Created automatically",
         "Mass-created with the PTA Auto tool (mass creation of NP / PA / PDEF)."],
    ]})
    add({"kind": "callout", "tone": "acc2", "label": "Shortcut worth knowing",
         "text": [("If your perimeter is electrical harness or connectors, stop before you "
                   "clone anything.", "b"),
                  (" Those PDEFs and PREAs are produced by a manager or by PTA Auto. "
                   "Creating them by hand duplicates references. Source [C].", "")]})

    add({"kind": "h2", "eyebrow": "Identity card \u00b7 1 of 3",
         "title": "Basic attributes"})
    add({"kind": "figure", "image": "prea-basic-attributes.png", "path": img("prea-basic-attributes.png"),
         "tone": "acc2", "label": "Basic attributes", "max_h": 300, "legend": "right",
         "legend_w": 224,
         "caption": "Identity card of a PREA \u2014 Basic Attributes block. Mandatory "
                    "attributes are the ones in red italics. Source [C].",
         "marks": [
             {"n": 1, "box": (2, 138, 328, 42), "tone": "warn", "mpos": "tl",
              "label": "Owner",
              "note": "Who owns the product. You can take the ownership over."},
             {"n": 2, "box": (330, 420, 502, 42), "tone": "dan", "mpos": "tl",
              "label": "Design Context",
              "note": "Drives the prefix of the PSA reference. See the warning below \u2014 "
                      "this is the one you cannot undo."},
             {"n": 3, "box": (2, 540, 328, 40), "tone": "warn", "mpos": "tl",
              "label": "Traceability",
              "note": "Three levels of quality control: RNF reinforced, STD standard, "
                      "UNT unitary."},
             {"n": 4, "box": (330, 618, 184, 48), "tone": "acc", "mpos": "tl",
              "label": "Stellantis System Creator",
              "note": "Mandatory. Identifies the creating system."},
         ]})
    add({"kind": "callout", "tone": "dan", "label": "The expensive mistake",
         "text": [("To change the Design Context, the ", ""), ("PSA Reference must be empty", "b"),
                  (". If a PSA reference has already been taken \u2014 even with the PDEF still "
                   "In Work \u2014 you have to ", ""),
                  ("recreate the PDEF from scratch", "b"),
                  (". Decide the design context before you request the reference. Source [C].", "")]})

    add({"kind": "h2", "eyebrow": "Identity card \u00b7 2 of 3",
         "title": "Identification and the link to the ECO"})
    add({"kind": "figure", "image": "prea-identification.png", "path": img("prea-identification.png"),
         "tone": "acc", "label": "Identification", "max_h": 250, "legend": "right",
         "legend_w": 224,
         "caption": "The same identity card, identification block: PSA Reference, the ECO "
                    "that will release the product, and Product Type. Source [C].",
         "marks": [
             {"n": 1, "box": (160, 0, 158, 18), "tone": "warn", "mpos": "tr",
              "label": "Red italics = required",
              "note": "The legend the PLM forms use everywhere, including the ECO form "
                      "in chapter 3."},
             {"n": 2, "box": (0, 22, 328, 40), "tone": "acc2", "mpos": "tl",
              "label": "PSA Reference",
              "note": "Empty at creation. Obtained afterwards through the PSA Reference "
                      "methodology, and required to promote."},
             {"n": 3, "box": (330, 24, 318, 40), "tone": "ok", "mpos": "tl",
              "label": "ECO for Release",
              "note": "The ECO that will officialise this product. Attach it before you "
                      "try to promote anything."},
             {"n": 4, "box": (0, 236, 328, 44), "tone": "warn", "mpos": "tl",
              "label": "Product Type",
              "note": "Mandatory. Paired with Product Nature, it decides which library "
                      "and which flow apply."},
         ]})

    add({"kind": "h2", "eyebrow": "Identity card \u00b7 3 of 3",
         "title": "Physical and supplier attributes"})
    add({"kind": "bullets", "columns": 2, "bullets": [
        [("Realized Mass", "ui"), (" \u2014 the weight given by the supplier.", "")],
        [("Gross weight", "ui"), (" \u2014 the mass of the part including its packaging.", "")],
        [("Welding reference point", "ui"),
         (" \u2014 YES means the part will be welded with welding points.", "")],
        [("Weighted Mass PSA", "ui"),
         (" \u2014 YES means the displayed mass is a real mass weighed in the plant; "
          "enter it with the Weighted Mass declaration command.", "")],
        [("COFOR attributes", "ui"),
         (" \u2014 Intellectual Property, Contracting and Manufacturer COFOR.", "")],
        [("COFOR is not optional in practice:", "warn"),
         (" these attributes are mandatory to manage an APQP grid in PLM.", "")],
    ]})
    add({"kind": "figure", "image": "prea-supplier-code.png", "path": img("prea-supplier-code.png"),
         "tone": "acc2", "label": "Supplier code", "max_h": 190, "legend": "right",
         "legend_w": 230,
         "caption": "Supplier Code block of the identity card. Source [C].",
         "marks": [
             {"n": 1, "box": (0, 54, 940, 102), "tone": "acc2", "mpos": "tl",
              "label": "COFOR Intellectual Property",
              "note": "Who owns the design. Each COFOR field has a matching Name field "
                      "filled automatically from the picker."},
             {"n": 2, "box": (0, 294, 940, 90), "tone": "warn", "mpos": "tl",
              "label": "Manufacturer COFOR",
              "note": "Required, with the other COFOR fields, before an APQP grid can be "
                      "managed on this product."},
         ]})

    add({"kind": "h2", "eyebrow": "Tricks", "title": "What saves you a re-creation"})
    add({"kind": "bullets", "columns": 2, "bullets": [
        [("Fix the Design Context first.", "b"),
         (" It drives the PSA reference prefix and freezes as soon as a reference "
          "is taken.", "")],
        [("Check who owns the creation.", "b"),
         (" Connectors, peri-connectors and harnesses are created by a manager or by "
          "PTA Auto \u2014 not by you.", "")],
        [("Never clone a non-generic.", "b"),
         (" Start from the library generic for your product nature.", "")],
        [("Fill the COFOR block early.", "b"),
         (" Missing COFOR blocks the APQP grid later, when it is urgent.", "")],
        [("Take ownership if you need to edit.", "b"),
         (" The Owner attribute can be taken over.", "")],
        [("Plan the ECO at the same time.", "b"),
         (" The product cannot leave In Work without one, so create it while you are "
          "still in context.", "")],
    ]})

    # =====================================================================
    # CHAPTER 2 - ECR
    # =====================================================================
    add({
        "kind": "chapter", "num": "2", "eyebrow": "Chapter 2",
        "title": "Creating an ECR",
        "lead": [("The ECR is the ", ""), ("request", "b"),
                 (" for a change. It is created from the same Actions menu as the ECO, "
                  "and it has one hard requirement: it must reach the state ", ""),
                 ("Design", "ui"),
                 (" before an ECO can live under it.", "")],
        "covers": ["Where the ECR entry point is, and its two variants",
                   "The Design-state gate",
                   "Creating the ECO under the ECR",
                   "What the provided methodologies do and do not specify"],
    })

    add({"kind": "h2", "eyebrow": "What it is for", "title": "The ECR in one screen"})
    add({"kind": "para", "text": [
        ("An ECR \u2014 Engineering Change Request \u2014 groups the ECOs that answer one "
         "request. Use case no. 3 of the ECO methodology starts from it: ", ""),
        ("\u201cThe user has just created an ECR, then he associates it to a Product ECO "
         "using the function Create a Product ECO in the category ECOs & ECs of the "
         "ECR\u201d", "i"),
        (". The prerequisite list of the same document is blunt about the state: ", ""),
        ("ECR in Design", "ui"),
        (" in case of a revision, or an OA / LA in Create for a first release or a "
         "reuse. Source [A].", "")]})
    add({"kind": "figure", "image": "01-actions-menu.png", "path": img("01-actions-menu.png"),
         "tone": "warn", "label": "Actions \u203a Change", "max_h": 286, "legend": "right",
         "legend_w": 226,
         "caption": "PLM home page \u203a Actions. The Change column carries every change "
                    "object: the ECR entries and, lower down, the ECO entries. Source [A].",
         "marks": [
             {"n": 1, "box": (44, 8, 40, 34), "tone": "acc2", "mpos": "bl",
              "label": "Actions toolbar",
              "note": "Top-left of the home page. It opens this full-width menu."},
             {"n": 2, "box": (528, 214, 132, 22), "tone": "acc", "mpos": "tl",
              "label": "Change column",
              "note": "Both the ECR and the ECO are created from this single column."},
             {"n": 3, "box": (546, 236, 142, 22), "tone": "warn", "mpos": "tr",
              "label": "Create ECR\u2026",
              "note": "The ECR entry point."},
             {"n": 4, "box": (546, 258, 172, 46), "tone": "acc2", "mpos": "br",
              "label": "Template and copy",
              "note": "Create ECR Template\u2026 defines a reusable shape; Create ECR "
                      "from\u2026 starts from an existing ECR."},
         ]})
    add({"kind": "callout", "tone": "acc2", "label": "Trick",
         "text": [("If your project repeats the same kind of request, use ", ""),
                  ("Create ECR from\u2026", "ui"),
                  (" or a template instead of the blank form. The classification and "
                   "context come along, which is where most of the typing is.", "")]})

    add({"kind": "h2", "eyebrow": "The gate", "title": "An ECR in Design, then the ECO under it"})
    add({"kind": "figure", "image": "07-ecr-structure-view.png",
         "path": img("07-ecr-structure-view.png"),
         "tone": "ok", "label": "ECR \u203a ECOs & ECs \u203a Structure View",
         "max_h": 252, "legend": "right", "legend_w": 226,
         "caption": "The ECR identity card, Structure View. Categories \u203a ECOs & ECs, "
                    "then Actions \u203a Create Product ECO\u2026 Source [A], use case no. 3.",
         "marks": [
             {"n": 1, "box": (200, 16, 112, 42), "tone": "acc", "mpos": "bl",
              "label": "The ECR",
              "note": "Its number, title and project context."},
             {"n": 2, "box": (718, 14, 92, 24), "tone": "warn", "mpos": "tr",
              "label": "State : Design",
              "note": "The gate. Outside Design, the Create Product ECO action will not "
                      "give you a usable ECO."},
             {"n": 3, "box": (82, 90, 58, 22), "tone": "acc2", "mpos": "tl",
              "label": "Actions",
              "note": "Reachable once you are inside Categories \u203a ECOs & ECs, in the "
                      "Structure View."},
             {"n": 4, "box": (100, 160, 156, 22), "tone": "ok", "mpos": "br",
              "label": "Create Product ECO\u2026",
              "note": "Creates the ECO already attached to this ECR. Then fill it exactly "
                      "as in chapter 3."},
         ]})
    add({"kind": "table", "colw": (0.34, 0.66), "head": ["To do this on an ECR", "Use"], "rows": [
        ["Create a new ECO under the ECR",
         "The ECR identity card \u203a Categories \u203a ECOs & ECs \u203a Structure View \u203a "
         "Actions \u203a Create Product ECO\u2026 (shown above)."],
        ["Attach an ECO that already exists",
         "METHODOLOGY Add/Remove ECO under ECR \u2014 Ref. 20061_17_01982."],
        ["Attach the ECO to a product instead",
         "MEMENTO Linking a Product to an ECO \u2014 Ref. 20061_17_01640."],
        ["Attach the ECO to an expected deliverable",
         "METHODOLOGY Linking an ECO to an Expected Object \u2014 Ref. 20061_16_01347."],
    ]})
    add({"kind": "callout", "tone": "warn", "label": "Scope of this chapter",
         "text": [("The documents provided with this guide specify the ECR as the object "
                   "an ECO hangs under \u2014 its entry point in the Actions menu, and the "
                   "Design state it must be in. They do ", ""),
                  ("not", "b"),
                  (" contain the field-by-field ECR creation form. For that, use ", ""),
                  ("METHODOLOGY Add/Remove ECO under ECR (20061_17_01982)", "ui"),
                  (" and the ECR filling guides of your perimeter. Everything shown in "
                   "this chapter comes from screens that are in the source set.", "")]})

    # =====================================================================
    # CHAPTER 3 - ECO
    # =====================================================================
    add({
        "kind": "chapter", "num": "3", "eyebrow": "Chapter 3",
        "title": "Creating a Product ECO",
        "lead": [("The ECO is the passport of a change. There are ", ""),
                 ("three ways in", "b"),
                 (", one form to fill, a short list of attributes that genuinely block "
                  "you, and one field \u2014 V/O/M Impacts \u2014 that trips up almost "
                  "everyone the first time.", "")],
        "covers": ["Prerequisites that must already be true",
                   "The three use cases, and which one to pick",
                   "The creation form: red now, black later",
                   "V/O/M impacts via the Project Space",
                   "Creating several ECOs in one go",
                   "Due dates on the approval routes"],
    })

    add({"kind": "h2", "eyebrow": "Before you click", "title": "Prerequisites"})
    add({"kind": "bullets", "bullets": [
        [("Log-on role ", ""), ("PSA_Pilote_Projet", "ui"), (" or ", ""),
         ("PSA_Concepteur", "ui"), (".", "")],
        [("The ", ""), ("diversity and applicability contexts", "b"), (" are defined.", "")],
        [("The ", ""), ("Expected Product (PA)", "b"),
         (" is created, with diversity applicability.", "")],
        [("The ", ""), ("reviewer and approval lists", "b"),
         (" are created and defined \u2014 the RT and RAL workflow templates must already "
          "exist, because you will have to name them on the form.", "")],
        [("The relevant ", ""), ("PDEF, PREA or DOC", "b"), (" is created.", "")],
        [("An ", ""), ("ECR in Design", "ui"), (" for a revision, or an ", ""),
         ("OA / LA in Create", "ui"),
         (" for a first release or a reuse.", "")],
    ]})
    add({"kind": "callout", "tone": "warn",
         "text": [("Missing one of these is the most common reason a creation or a "
                   "promotion fails.", "b"),
                  (" Check the list before you open the form, not after. Source [A].", "")]})

    add({"kind": "h2", "eyebrow": "Three ways in", "title": "Pick the right use case"})
    add({"kind": "cards", "cards": [
        {"tag": "Use case 1", "title": "From the home page", "tone": "acc",
         "lines": ["Actions \u203a Create Product ECO.",
                   "Fill the attributes, then Finish.",
                   "The ECO is born unlinked \u2014 attach it afterwards.",
                   "Best for: creating several ECOs at once."]},
        {"tag": "Use case 2", "title": "From the product", "tone": "ok",
         "lines": ["Open the PDEF / PREA / DOC identity card.",
                   "Categories \u203a Linked ECO and ECR.",
                   "ECOs sub-tab \u203a Create Product ECO.",
                   "Best for: creates and links in one action."]},
        {"tag": "Use case 3", "title": "From the ECR", "tone": "acc2",
         "lines": ["The ECR must be in state Design.",
                   "Categories \u203a ECOs & ECs.",
                   "Structure View \u203a Actions \u203a Create Product ECO\u2026",
                   "Best for: a change driven by an ECR."]},
    ]})

    add({"kind": "h2", "eyebrow": "Method 1 \u00b7 step 1",
         "title": "Actions \u203a Create Product ECO"})
    add({"kind": "figure", "image": "01-actions-menu.png", "path": img("01-actions-menu.png"),
         "tone": "ok", "label": "Method 1 \u00b7 entry point", "max_h": 286,
         "legend": "right", "legend_w": 226,
         "caption": "The same Actions menu as in chapter 2, read for the ECO. Note how "
                    "close the wrong entry sits. Source [A].",
         "marks": [
             {"n": 1, "box": (44, 8, 40, 34), "tone": "acc2", "mpos": "bl",
              "label": "Actions toolbar",
              "note": "Home page, top-left."},
             {"n": 2, "box": (528, 214, 132, 22), "tone": "acc", "mpos": "tl",
              "label": "Change column",
              "note": "Scroll down this column past the ECR entries."},
             {"n": 3, "box": (536, 366, 212, 26), "tone": "ok", "mpos": "tr",
              "label": "Create Product ECO\u2026",
              "note": "Selected here. This is the one you want."},
             {"n": 4, "box": (546, 392, 166, 22), "tone": "dan", "mpos": "br",
              "label": "Not Create Component ECO",
              "note": "Sits immediately below and makes a different object. The most "
                      "frequent mis-click on this screen."},
         ]})

    add({"kind": "h2", "eyebrow": "Method 1 \u00b7 step 2",
         "title": "The form, top half: what blocks the creation"})
    add({"kind": "figure", "image": "03a-form-top.png", "path": img("03a-form-top.png"),
         "tone": "warn", "label": "Creation form \u00b7 basic attributes", "max_h": 268,
         "legend": "right", "legend_w": 250,
         "caption": "Window for filling the ECO attributes, upper part. Source [A].",
         "marks": [
             {"n": 1, "box": (218, 0, 202, 17), "tone": "warn", "mpos": "tr",
              "label": "Red italics = required",
              "note": "Only the red fields are needed to confirm the creation. Black "
                      "fields can be filled later \u2014 but only while the ECO is still in "
                      "Create or Define Components maturity."},
             {"n": 2, "box": (0, 112, 594, 74), "tone": "acc2", "mpos": "tl",
              "label": "Description",
              "note": "Follow the Electricity/Electronics or the Mechanical Engineering "
                      "filling guide. Required to release."},
             {"n": 3, "box": (0, 186, 330, 60), "tone": "acc", "mpos": "tl",
              "label": "Maturity and Homologation Flow",
              "note": "Homologation Flow = YES when the ECO has a PRODUCTION (SERIE) "
                      "flow. Ask the Homologation Manager first: some breakdowns are "
                      "exempt from RHN flows."},
             {"n": 4, "box": (0, 278, 330, 66), "tone": "ok", "mpos": "bl",
              "label": "Engineering approval, Homologation User",
              "note": "Engineering approval carries the RT workflow template. The "
                      "Homologation User ID is mandatory as soon as the flow is YES, and "
                      "comes from the Homologation User List link."},
         ]})

    add({"kind": "h2", "eyebrow": "Method 1 \u00b7 step 3",
         "title": "The form, bottom half: identification and impacts"})
    add({"kind": "figure", "image": "03b-form-bottom.png", "path": img("03b-form-bottom.png"),
         "tone": "acc", "label": "Creation form \u00b7 identification", "max_h": 252,
         "legend": "right", "legend_w": 250,
         "caption": "Same window, lower part. This is where the batch trick and the "
                    "V/O/M field live. Source [A].",
         "marks": [
             {"n": 1, "box": (0, 28, 330, 32), "tone": "acc", "mpos": "tl",
              "label": "Release approval (RAL)",
              "note": "The workflow template of the deliverable approval review."},
             {"n": 2, "box": (0, 88, 330, 36), "tone": "acc2", "mpos": "tl",
              "label": "Responsible Design Engineer",
              "note": "The component manager. Reads Unassigned until you set it \u2014 and "
                      "it is required for release."},
             {"n": 3, "box": (0, 126, 330, 38), "tone": "ok", "mpos": "bl",
              "label": "Number of ECO to create",
              "note": "Leave it at 1, or raise it and PLM opens a mass-update grid. See "
                      "two pages on."},
             {"n": 4, "box": (0, 291, 330, 60), "tone": "warn", "mpos": "bl",
              "label": "V/O/M Impacts, Manufacturing Site",
              "note": "Never typed by hand. Both come from the Project Space, as the next "
                      "section shows."},
         ]})

    add({"kind": "h2", "eyebrow": "The checklist",
         "title": "Attributes you must fill to release"})
    add({"kind": "table", "colw": (0.26, 0.74), "size": 8.6,
         "head": ["Field", "Rule"], "rows": [
             ["Description", "Follow the Electricity/Electronics or Mechanical Engineering "
                             "filling guide."],
             ["Due Date", "PROTO or SERIE."],
             ["Homologation Flow", "YES if the ECO has a PRODUCTION (SERIE) flow. Contact "
                                   "the Homologation Manager beforehand: some PSA "
                                   "breakdowns are exempt from RHN flows and the approver "
                                   "holds the list."],
             ["Homologation User", "Mandatory when Homologation Flow = YES. Take the ID "
                                   "from the Homologation User List link."],
             ["Responsible Design Engineer", "Name of the component manager. Required for "
                                             "release."],
             ["RT Approvers", "Workflow template of the technical review (RT)."],
             ["RAL Approvers", "Workflow template of the deliverable approval review (RAL)."],
             ["CADER", "Select the CADER (vehicle or component code) if one exists for the "
                       "current release; otherwise leave it blank."],
             ["DUD", "The milestone."],
             ["Notification's context", "Alerts the notification technician so the folder "
                                        "reaches the right partners. Imperative for a "
                                        "partner project or a JV."],
         ]})

    add({"kind": "h2", "eyebrow": "V / O / M impacts",
         "title": "Four clicks, and the one column to check"})
    add({"kind": "steps", "steps": [
        [("Check the ", ""), ("Project Space", "ui"), (" attribute.", "")],
        [("Search the name of the project you want.", "")],
        [("Select the result whose ", ""), ("Type", "ui"), (" is ", ""),
         ("Project Space", "ui"), (".", "")],
        [("Submit", "b"),
         (". Then choose one or more manufacturing sites \u2014 they fill the ", ""),
         ("Manufacturing Site", "ui"), (" field automatically.", "")],
    ]})
    add({"kind": "figure", "image": "05-project-space-search.png",
         "path": img("05-project-space-search.png"),
         "tone": "acc2", "label": "V/O/M \u203a search the project space",
         "max_h": 300, "legend": "below",
         "caption": "The search refinement dialog. The numbers are the four steps of the "
                    "methodology, in place on the screen. Source [A].",
         "marks": [
             {"n": 1, "box": (44, 196, 216, 28), "tone": "acc2", "mpos": "tl",
              "label": "Types \u203a Project Management \u203a Project Space",
              "note": "Refine on the Project Space type first."},
             {"n": 2, "box": (0, 48, 278, 28), "tone": "acc", "mpos": "tl",
              "label": "Search the project name",
              "note": "Here, MB6."},
             {"n": 3, "box": (452, 334, 1048, 44), "tone": "ok", "mpos": "tl",
              "label": "Select the result",
              "note": "One radio button, one project."},
             {"n": 4, "box": (1428, 860, 82, 26), "tone": "acc2", "mpos": "tl",
              "label": "Submit",
              "note": "Attaches the project space to the ECO."},
             {"n": 5, "box": (828, 66, 60, 26), "tone": "warn", "mpos": "tr",
              "label": "The Type column",
              "note": "Verify it reads Project Space. Never select a Product Line "
                      "(PL-000000) \u2014 the impacts would be wrong."},
         ]})
    add({"kind": "figure", "image": "04-vom-warning.png", "path": img("04-vom-warning.png"),
         "tone": "dan", "label": "If you see this", "max_h": 128, "legend": "right",
         "legend_w": 400,
         "caption": "The warning reproduced from the methodology. Source [A].",
         "marks": [
             {"box": (0, 0, 376, 138), "tone": "dan", "fill": False,
              "label": "\u201cNo active manufacturing site in this project space\u201d",
              "note": "The project space is not set up. You cannot fix this from the ECO: "
                      "contact the Project Owner (RPP or RPCR) so the manufacturing sites "
                      "are filled in on the project space."},
         ]})
    add({"kind": "callout", "tone": "acc2", "label": "Good to know",
         "text": [("When a single manufacturing site is associated with a V/O/M impact, "
                   "PLM fills it in for you.", "b"),
                  (" With several, you pick. The field stays editable afterwards. "
                   "Source [A].", "")]})

    add({"kind": "h2", "eyebrow": "Method 1 \u00b7 shortcut",
         "title": "Create several ECOs in one go"})
    add({"kind": "para", "text": [
        ("Set ", ""), ("Number of ECO to create", "ui"),
        (" to N before validating and PLM does not open N forms \u2014 it opens one grid "
         "with N ECO numbers already allocated, sharing the attributes you just typed. "
         "This is the single biggest time-saver on the form.", "")]})
    add({"kind": "figure", "image": "02-batch-grid.png", "path": img("02-batch-grid.png"),
         "tone": "ok", "label": "Mass update grid", "max_h": 250, "legend": "below",
         "caption": "Example from the methodology: three ECOs created in one go. "
                    "Source [A].",
         "marks": [
             {"n": 1, "box": (14, 96, 276, 28), "tone": "acc2", "mpos": "tl",
              "label": "Mass Update",
              "note": "Pick a column here to write one value into every row at once."},
             {"n": 2, "box": (6, 174, 222, 94), "tone": "ok", "mpos": "bl",
              "label": "One row per ECO",
              "note": "ECO-0031157 to 0031159: three numbers already allocated."},
             {"n": 3, "box": (326, 131, 304, 48), "tone": "warn", "mpos": "tl",
              "label": "The red columns are still the required ones",
              "note": "Description, Maturity and Homologation Flow gate the creation here "
                      "exactly as they do on the single form."},
             {"n": 4, "box": (1248, 96, 60, 28), "tone": "dan", "mpos": "tl",
              "label": "Save",
              "note": "Nothing exists until the grid is saved."},
         ]})

    add({"kind": "h2", "eyebrow": "Method 2",
         "title": "Create and link in a single action"})
    add({"kind": "figure", "image": "06-linked-eco-ecr.png",
         "path": img("06-linked-eco-ecr.png"),
         "tone": "ok", "label": "Product \u203a Linked ECO and ECR", "max_h": 200,
         "legend": "right", "legend_w": 250,
         "caption": "The identity card of a Defined Product, Linked ECO and ECR view. "
                    "The red boxes are in the original methodology screenshot. Source [A].",
         "marks": [
             {"n": 1, "box": (4, 68, 86, 24), "tone": "acc2", "mpos": "bl",
              "label": "Categories",
              "note": "From the PDEF, PREA or DOC identity card."},
             {"n": 2, "box": (54, 97, 54, 25), "tone": "acc", "mpos": "tr",
              "label": "ECOs sub-tab",
              "note": "The view opens on ECRs \u2014 switch to ECOs."},
             {"n": 3, "box": (150, 120, 150, 28), "tone": "ok", "mpos": "br",
              "label": "Create Product ECO",
              "note": "Creates the ECO and attaches it to this product at the same time. "
                      "That is the whole advantage of method 2."},
             {"n": 4, "box": (582, 6, 100, 24), "tone": "warn", "mpos": "tr",
              "label": "State : In Work",
              "note": "The product is still editable here \u2014 the normal moment to give "
                      "it its ECO."},
         ]})
    add({"kind": "callout", "tone": "ok", "label": "Which method to use",
         "text": [("Use method 2 whenever you already have the product open.", "b"),
                  (" Method 1 creates the ECO unlinked and you then have to attach it "
                   "with a separate memento, which is extra work and the step people "
                   "forget.", "")]})

    add({"kind": "h2", "eyebrow": "Management",
         "title": "Put a due date on the approval routes"})
    add({"kind": "para", "text": [
        ("From the ECO identity card, or via ", ""), ("Categories \u203a Lifecycle", "ui"),
        (", open the ", ""), ("Approvals", "ui"), (" tab and click ", ""), ("Edit", "ui"),
        (". You can then date the RT and RAL tasks, which is what makes the ECO "
         "followable by the project. Source [A].", "")]})
    add({"kind": "figure", "image": "08-approvals-due-date.png",
         "path": img("08-approvals-due-date.png"),
         "tone": "acc", "label": "Lifecycle \u203a Approvals \u203a Edit", "max_h": 290,
         "legend": "below",
         "caption": "The Approvals tab in edit mode. Source [A].",
         "marks": [
             {"n": 1, "box": (2, 34, 152, 30), "tone": "acc2", "mpos": "tl",
              "label": "Column = Due Date",
              "note": "Choose the column you are about to write."},
             {"n": 2, "box": (150, 34, 232, 30), "tone": "acc", "mpos": "tl",
              "label": "Value = dd/MM/yy",
              "note": "Type it, or use the calendar icon."},
             {"n": 3, "box": (20, 150, 524, 68), "tone": "ok", "mpos": "bl",
              "label": "Tick the state lines",
              "note": "Select the RT rows (Wait App.) or the RAL rows (Reviewed) you want "
                      "to date."},
             {"n": 4, "box": (378, 34, 182, 30), "tone": "warn", "mpos": "tr",
              "label": "Apply to Selected",
              "note": "Prefer it to Apply to all, which overwrites every line including "
                      "the ones you did not mean to touch."},
             {"n": 5, "box": (1156, 542, 120, 28), "tone": "acc2", "mpos": "tl",
              "label": "Done",
              "note": "Confirms the due dates on the workflow tasks."},
         ]})

    add({"kind": "h2", "eyebrow": "The ladder", "title": "Where the ECO goes next"})
    add({"kind": "figure", "image": "09-lifecycle.png", "path": img("09-lifecycle.png"),
         "tone": "acc2", "label": "ECO \u203a Categories \u203a Lifecycle", "max_h": 282,
         "legend": "below",
         "caption": "The ECO lifecycle, with the Approvals tab underneath. Source [A].",
         "marks": [
             {"n": 1, "box": (154, 268, 106, 42), "tone": "ok", "mpos": "tl",
              "label": "Create",
              "note": "Where a new ECO starts."},
             {"n": 2, "box": (302, 268, 110, 42), "tone": "acc", "mpos": "tl",
              "label": "Define Components",
              "note": "Last state where the black attributes can still be completed."},
             {"n": 3, "box": (452, 268, 106, 42), "tone": "acc2", "mpos": "tl",
              "label": "Wait App. \u2192 Reviewed",
              "note": "The RT route runs here."},
             {"n": 4, "box": (752, 268, 106, 42), "tone": "warn", "mpos": "tr",
              "label": "Released",
              "note": "The RAL route gets you here. Everything the ECO carries becomes "
                      "official."},
             {"n": 5, "box": (1052, 268, 106, 42), "tone": "dan", "mpos": "tr",
              "label": "Cancelled",
              "note": "Reachable from several states."},
             {"n": 6, "box": (78, 168, 148, 26), "tone": "acc", "mpos": "bl",
              "label": "Promote / Demote",
              "note": "One click moves exactly one state. There is no jump straight to "
                      "Released."},
         ]})

    # =====================================================================
    # CHAPTER 4 - release
    # =====================================================================
    add({
        "kind": "chapter", "num": "4", "eyebrow": "Chapter 4",
        "title": "From created to released",
        "lead": [("Creating the objects is the easy half. Getting them to ", ""),
                 ("Released", "ui"),
                 (" means climbing two ladders in the right order: the documents first, "
                  "then the product, and above Approved it is the ECO that does the "
                  "work.", "")],
        "covers": ["The golden rule: documents move first",
                   "The two checks before a PDEF can be promoted",
                   "Promote, demote, and why demoting is cheap",
                   "RT then RAL \u2014 who signs what",
                   "PREA specifics: Frozen, and Cancel and revise"],
    })

    add({"kind": "h2", "eyebrow": "The golden rule", "title": "Documents move first"})
    add({"kind": "table", "colw": (0.42, 0.58),
         "head": ["To reach this state", "the specification documents must already be"],
         "rows": [
             ["PDEF \u2192 Wait App.", "Wait App."],
             ["PDEF \u2192 Approved", "Approved"],
             ["PDEF \u2192 Released (through the ECO)", "Released / Published"],
             ["PREA \u2192 Frozen", "Frozen"],
             ["PREA \u2192 Wait App.", "Wait App."],
             ["PREA \u2192 Approved", "Approved"],
             ["PREA \u2192 Released (through the ECO)", "Published"],
         ]})
    add({"kind": "callout", "tone": "ok", "label": "Where to check",
         "text": [("From the PDEF identity card: ", ""),
                  ("Categories \u203a Specification Documents", "ui"),
                  (". In the ", ""), ("State", "ui"),
                  (" column, the green arrow promotes a document one step \u2014 click it "
                   "once for Frozen, again for Wait App. Source [B].", "")]})

    add({"kind": "h2", "eyebrow": "Two checks",
         "title": "No ECO and no PSA Reference means no promotion"})
    add({"kind": "figure", "image": "01-pdef-in-work.jpg", "path": img("01-pdef-in-work.jpg"),
         "tone": "warn", "label": "PDEF \u00b7 \u00c9tat : En Cours (In Work)", "max_h": 282,
         "legend": "right", "legend_w": 246,
         "caption": "A PDEF still In Work. The source methodology labels these two checks "
                    "(A) and (B). The UI here is French \u2014 see the decoder in chapter 8. "
                    "Source [B].",
         "marks": [
             {"n": 1, "box": (548, 0, 134, 24), "tone": "acc2", "mpos": "bl",
              "label": "\u00c9tat : En Cours",
              "note": "In Work \u2014 the only state where the content can still be "
                      "modified."},
             {"n": 2, "box": (392, 96, 292, 30), "tone": "ok", "mpos": "tl",
              "label": "(A) an ECO is attached",
              "note": "Here ECO-0000771. If this is empty, create one with method 2 "
                      "before going further."},
             {"n": 3, "box": (424, 178, 312, 28), "tone": "dan", "mpos": "br",
              "label": "(B) R\u00e9f\u00e9rence PSA \u2014 empty",
              "note": "This PDEF cannot be promoted until a PSA Reference is assigned, "
                      "via the PSA Reference methodology."},
             {"n": 4, "box": (0, 242, 232, 28), "tone": "warn", "mpos": "bl",
              "label": "Documents de sp\u00e9cifications",
              "note": "They have to reach Wait App. before the PDEF can. Open them from "
                      "Cat\u00e9gories."},
         ]})

    add({"kind": "h2", "eyebrow": "Mechanics", "title": "Two ways to move one step"})
    add({"kind": "steps", "steps": [
        [("The ", ""), ("green arrow", "ok"),
         (" next to the state on the identity card \u2014 the fastest way.", "")],
        [("Or ", ""), ("Categories \u203a Lifecycle", "ui"), (" and ", ""), ("Promote", "ui"),
         (" in the lifecycle window.", "")],
        [("Going back down is the same gesture: ", ""), ("red arrow", "dan"), (" or ", ""),
         ("Demote", "ui"), (".", "")],
        [("Each click moves exactly one state.", "b"),
         (" Demoting a product does not touch its specification documents \u2014 they stay "
          "where they are.", "")],
    ]})
    add({"kind": "figure", "image": "02-pdef-wait-app.jpg",
         "path": img("02-pdef-wait-app.jpg"),
         "tone": "ok", "label": "After the promotion", "max_h": 268,
         "legend": "right", "legend_w": 250,
         "caption": "The same PDEF, now in Attente Approbation (Wait App.). Compare it "
                    "with the previous figure. Source [B].",
         "marks": [
             {"n": 1, "box": (324, 0, 212, 26), "tone": "ok", "mpos": "bl",
              "label": "\u00c9tat : Attente Approbation",
              "note": "Wait App. From here the content is locked \u2014 no modification is "
                      "possible."},
             {"n": 2, "box": (294, 206, 238, 30), "tone": "acc2", "mpos": "bl",
              "label": "R\u00e9f\u00e9rence PSA is filled now",
              "note": "9809679280 00. This is check (B) satisfied, and it is what let the "
                      "promotion through."},
             {"n": 3, "box": (456, 90, 124, 26), "tone": "acc", "mpos": "tr",
              "label": "The ECO is still attached",
              "note": "ECO-0000771 \u2014 the ECO that will later carry this product all the "
                      "way to Released."},
         ]})
    add({"kind": "figure", "image": "03-pdef-demoted.jpg",
         "path": img("03-pdef-demoted.jpg"),
         "tone": "acc2", "label": "After a demotion", "max_h": 262,
         "legend": "right", "legend_w": 250,
         "caption": "Demoted back to En Cours (In Work) with the red arrow, so the card "
                    "can be edited again. Source [B].",
         "marks": [
             {"n": 1, "box": (578, 0, 114, 26), "tone": "acc2", "mpos": "bl",
              "label": "\u00c9tat : En Cours",
              "note": "Back to In Work. Use the red arrow next to the state, or "
                      "Cat\u00e9gories \u203a Cycle de vie \u203a R\u00e9trograder."},
             {"n": 2, "box": (0, 334, 242, 32), "tone": "ok", "mpos": "bl",
              "label": "Documents de sp\u00e9cifications",
              "note": "They keep the state they had reached. Demoting the product does "
                      "not demote its documents, which is why demoting is cheap."},
         ]})
    add({"kind": "callout", "tone": "acc2", "label": "Trick",
         "text": [("Demote instead of forcing.", "b"),
                  (" Once a PDEF is in Wait App. it cannot be modified; dropping it back "
                   "to In Work costs one click and loses nothing. People create "
                   "unnecessary revisions because they do not realise this.", "")]})

    add({"kind": "h2", "eyebrow": "Release",
         "title": "The ECO carries the product over the line"})
    add({"kind": "steps", "steps": [
        [("Open the PDEF or PREA in ", ""), ("Approved", "ui"),
         (" and click the ", ""), ("ECO link", "ui"), (" on the card.", "")],
        [("On the ECO: ", ""), ("Actions \u203a Edit Details", "ui"), (".", "")],
        [("Check the three attributes that drive the workflow: ", ""),
         ("RT approvers", "b"), (", ", ""), ("RAL approvers", "b"), (" and the ", ""),
         ("Responsible Design Engineer", "b"), (".", "")],
        [("Promote the ECO to ", ""), ("Define Components", "ui"),
         (", then to ", ""), ("Wait App.", "ui"),
         (" once everything attached to it is ready.", "")],
        [("Check what is attached in ", ""), ("Categories \u203a Affected Items", "ui"),
         (" and promote whatever is late.", "")],
    ]})
    add({"kind": "figure", "image": "04-eco-edit-details.jpg",
         "path": img("04-eco-edit-details.jpg"),
         "tone": "acc", "label": "ECO \u203a Actions \u203a \u00c9dition des d\u00e9tails",
         "max_h": 272, "legend": "right", "legend_w": 266,
         "caption": "Edit Details on the ECO, French UI. The same attributes as the "
                    "creation form in chapter 3. Source [B].",
         "marks": [
             {"label": "Valideurs de la RT",
              "note": "RT approvers \u2014 workflow template of the technical review."},
             {"label": "Valideurs de la RAL",
              "note": "RAL approvers \u2014 workflow template of the deliverable approval "
                      "review."},
             {"label": "Ing\u00e9nieur concepteur responsable",
              "note": "Responsible Design Engineer \u2014 the designer answering for the "
                      "change."},
             {"label": "\u201c\u2026\u201d / Effacer / Termin\u00e9",
              "note": "Opens the picker, clears a value, saves. Red italic fields are the "
                      "required ones, exactly as on the creation form."},
         ]})
    add({"kind": "figure", "image": "05-eco-lifecycle.jpg", "path": img("05-eco-lifecycle.jpg"),
         "tone": "acc2", "label": "The ECO ladder, French UI", "max_h": 180,
         "legend": "below", "legend_cols": 2,
         "caption": "Cr\u00e9er \u203a D\u00e9finir composants \u203a Attente Appro. \u203a Revu \u203a "
                    "Valid\u00e9 \u203a Impl\u00e9ment\u00e9, with Annul\u00e9 reachable from several "
                    "states. Source [B].",
         "marks": [
             {"n": 1, "box": (74, 62, 94, 32), "tone": "acc", "mpos": "tl",
              "label": "Promouvoir / R\u00e9trograder",
              "note": "Promote and Demote. One click moves exactly one state."},
             {"n": 2, "box": (234, 162, 110, 48), "tone": "ok", "mpos": "tl",
              "label": "D\u00e9finir composants",
              "note": "Define Components, the current state here. Your last chance to "
                      "complete the black attributes."},
             {"n": 3, "box": (389, 162, 106, 48), "tone": "acc2", "mpos": "tr",
              "label": "Attente Appro. \u2192 Revu",
              "note": "Wait App. then Reviewed. The RT route runs between these two."},
             {"n": 4, "box": (689, 162, 106, 48), "tone": "warn", "mpos": "tr",
              "label": "Valid\u00e9",
              "note": "Released, reached by the RAL route. Everything the ECO carries "
                      "becomes official."},
         ]})
    add({"kind": "callout", "tone": "warn", "label": "The most common release blocker",
         "text": [("The ECO cannot be promoted while one attached document or product is "
                   "still one floor below.", "b"),
                  (" For a PDEF the rule is: PDEF Approved and its DOC Approved. For a "
                   "PREA: PREA Approved, DOC Validated. Source [B].", "")]})

    add({"kind": "h2", "eyebrow": "Approvals", "title": "RT first, then RAL"})
    add({"kind": "bullets", "bullets": [
        [("The ", ""), ("RT approver", "b"),
         (" validates the route that takes the ECO to Wait App.; the ECO then moves to ", ""),
         ("Reviewed", "ui"), (".", "")],
        [("The ", ""), ("RAL approver", "b"),
         (" validates the route that takes the ECO to ", ""), ("Released", "ui"), (".", "")],
        [("Both work from ", ""), ("Categories \u203a Lifecycle \u203a Approvals", "ui"),
         (" on the ECO \u2014 never from the product.", "")],
        [("Tick the state line, then Approve or Reject.", "b"),
         (" The assignee appears under T\u00e2ches / Signatures and gets a task "
          "notification in his mailbox.", "")],
        [("When the RAL route is approved the ECO is Released", "b"),
         (" \u2014 and so is everything it carries.", "")],
    ]})
    add({"kind": "figure", "image": "06-eco-approvals.jpg", "path": img("06-eco-approvals.jpg"),
         "tone": "acc2", "label": "Lifecycle \u203a Approvals", "max_h": 262,
         "legend": "right", "legend_w": 250,
         "caption": "The approval tab on the ECO, French UI. Source [B].",
         "marks": [
             {"label": "Tick the state line",
              "note": "Select the row for the state whose route you are signing."},
             {"label": "Approve / Reject",
              "note": "Then confirm in the pop-up shown below."},
             {"label": "T\u00e2ches / Signatures",
              "note": "Where the assignee of each route appears."},
         ]})
    add({"kind": "figure", "image": "07-approve-popup.jpg", "path": img("07-approve-popup.jpg"),
         "tone": "ok", "label": "The confirmation pop-up", "max_h": 230,
         "legend": "right", "legend_w": 300,
         "caption": "Add a comment, choose Approuver, then Termin\u00e9. Source [B].",
         "marks": [
             {"label": "Approuver = Approve",
              "note": "Select it, add a comment if useful, then Termin\u00e9 (Done). The "
                      "route is launched and the ECO moves one state."},
         ]})
    add({"kind": "figure", "image": "08-affected-items.jpg", "path": img("08-affected-items.jpg"),
         "tone": "ok", "label": "Categories \u203a Affected Items", "max_h": 240,
         "legend": "right", "legend_w": 266,
         "caption": "After release, Affected Items is the proof. Source [B].",
         "marks": [
             {"label": "Use it as your checklist",
              "note": "Before promoting: everything listed must be at the expected state. "
                      "After releasing: the PDEF reads Valid\u00e9 / Released and the "
                      "specification document Publi\u00e9 / Published."},
             {"label": "The previous revision flips to Obsolete",
              "note": "Visible under the state. If a line is not where you expect, the "
                      "release is not finished."},
         ]})

    add({"kind": "h2", "eyebrow": "PREA specifics",
         "title": "Frozen, and the only repair action"})
    add({"kind": "bullets", "bullets": [
        [("The PREA has an extra first step: ", ""), ("Frozen", "ui"),
         (" \u2014 reachable only once the documents are Frozen.", "")],
        [("After Frozen there is no modification:", "b"),
         (" a content change needs a revision.", "")],
        [("A PREA in Wait App. or Approved cannot be revised", "b"),
         (" \u2014 demote it back to Frozen first.", "")],
        [("Only the PREA offers ", ""), ("Cancel and revise", "ui"),
         (", to retire a faulty PSA Reference and get a new one.", "")],
        [("Conditions: the PREA is Frozen and it is the last revision on the line.", "b"),
         (" Then Actions \u203a Cancel and revise.", "")],
    ]})
    add({"kind": "callout", "tone": "dan", "label": "Irreversible",
         "text": [("Cancel and revise cannot be undone.", "b"),
                  (" The faulty PREA becomes Cancelled and a new revision is created In "
                   "Work. Check the revision and the state before you click, and note the "
                   "new revision number immediately. Source [B].", "")]})
    add({"kind": "figure", "image": "12-prea-frozen.jpg", "path": img("12-prea-frozen.jpg"),
         "tone": "warn", "label": "Before \u00b7 Fig\u00e9 (Frozen)", "max_h": 236,
         "legend": "right", "legend_w": 270,
         "caption": "The faulty PREA, still Frozen, with its PSA Reference and its ECO "
                    "pour Officialisation. Source [B].",
         "marks": [
             {"label": "Both conditions visible on the card",
              "note": "State Fig\u00e9, and R\u00e9vision la plus haute confirming this is the "
                      "last revision on the line."},
         ]})
    add({"kind": "figure", "image": "13-prea-cancelled.jpg", "path": img("13-prea-cancelled.jpg"),
         "tone": "dan", "label": "After \u00b7 Annul\u00e9 (Cancelled)", "max_h": 236,
         "legend": "right", "legend_w": 270,
         "caption": "The PREA is Cancelled and the highest revision now points to the new "
                    "one, which starts In Work. Source [B].",
         "marks": [
             {"label": "What you must do next",
              "note": "Link the new revision to an ECO and launch the creation of its PSA "
                      "Reference. The PDEF-PREA link is carried over \u2014 check it in "
                      "Categories \u203a Referenced By."},
         ]})

    add({"kind": "h2", "eyebrow": "Prohibition", "title": "Taking a product out of service"})
    add({"kind": "steps", "steps": [
        [("Open the PDEF or PREA in ", ""), ("Released / Validated", "ui"), (".", "")],
        [("Categories \u203a Referenced By", "ui"),
         (" to see which PA (for a PDEF) or which PDEF (for a PREA) the prohibition "
          "will hit.", "")],
        [("Create an ECO for the prohibition", "b"), (" and link it to the product.", "")],
        [("Actions \u203a Edit Details", "ui"), (": fill the ", ""), ("RAL approvers", "b"),
         (" and the ", ""), ("Responsible Design Engineer", "b"),
         (". The RT approver is not required for a prohibition \u2014 only the RAL route "
          "runs.", "")],
        [("Affected Items \u203a Edit All", "ui"), (": set ", ""),
         ("Requested Change = For Prohibition", "ui"), (", then Save.", "")],
        [("Promote up to Reviewed, let the RAL approver sign, and the ECO turns "
          "Released \u2014 Affected Items then shows the product as Prohibited.", "")],
    ]})
    add({"kind": "figure", "image": "09-referenced-by.jpg", "path": img("09-referenced-by.jpg"),
         "tone": "acc", "label": "Categories \u203a R\u00e9f\u00e9renc\u00e9 par", "max_h": 212,
         "legend": "right", "legend_w": 320,
         "caption": "Referenced By tells you who depends on the product. Source [B].",
         "marks": [
             {"label": "Check this before you prohibit anything",
              "note": "It lists what will be affected. Prohibiting a product that is "
                      "still referenced is how you break someone else's structure."},
         ]})
    add({"kind": "figure", "image": "10-for-prohibition.jpg", "path": img("10-for-prohibition.jpg"),
         "tone": "warn", "label": "Affected Items \u203a Edit All", "max_h": 230,
         "legend": "right", "legend_w": 290,
         "caption": "Modification demand\u00e9e (Requested Change) set to Pour interdiction "
                    "(For Prohibition). Source [B].",
         "marks": [
             {"label": "The declaration of intent",
              "note": "Until this column says For Prohibition, the ECO will release the "
                      "product normally instead of forbidding it."},
         ]})
    add({"kind": "figure", "image": "11-vom-project-search.jpg",
         "path": img("11-vom-project-search.jpg"),
         "tone": "acc2", "label": "V/O/M Impacts \u203a the same search, in French",
         "max_h": 282, "legend": "below", "legend_cols": 2,
         "caption": "The prohibition ECO also needs its V/O/M impacts. This is the French "
                    "twin of the search screen in chapter 3 \u2014 and it shows the trap "
                    "side by side. Source [B].",
         "marks": [
             {"n": 1, "box": (2, 72, 278, 30), "tone": "acc", "mpos": "tl",
              "label": "Recherche",
              "note": "Wildcards work: R82* here."},
             {"n": 2, "box": (38, 194, 202, 28), "tone": "acc2", "mpos": "tl",
              "label": "Espace de projet",
              "note": "Project Space, nested under Gestion de projet (Project "
                      "Management). Refine on it first."},
             {"n": 3, "box": (362, 180, 642, 38), "tone": "ok", "mpos": "bl",
              "label": "R82E \u2014 Espace de projet",
              "note": "The right line: its Type column reads Espace de projet."},
             {"n": 4, "box": (362, 148, 642, 32), "tone": "dan", "mpos": "tl",
              "label": "PL-0000004 \u2014 Ligne de produits",
              "note": "A Product Line sitting in the same result list. Pick this one and "
                      "the V/O/M impacts are wrong. This is exactly the mistake the "
                      "methodology warns about."},
             {"n": 5, "box": (924, 522, 84, 30), "tone": "acc2", "mpos": "tl",
              "label": "Soumettre",
              "note": "Submit."},
         ]})

    # =====================================================================
    # CHAPTER 5 - typical cases
    # =====================================================================
    add({
        "kind": "chapter", "num": "5", "eyebrow": "Chapter 5",
        "title": "Typical cases and traps",
        "lead": [("Three situations from the methodology's own \u201ctypical cases\u201d "
                  "chapter. The last one is the classic ", ""),
                 ("Promotion Failed", "dan"),
                 (" that stops a release dead, and it has a one-field fix.", "")],
        "covers": ["ECO dates for project management",
                   "The ECO used to create a Neutral PDEF",
                   "Revising or reusing a PDEF under a PA with coloured products"],
    })

    add({"kind": "h2", "eyebrow": "Case 1", "title": "A Neutral PDEF needs a diversity manager"})
    add({"kind": "para", "text": [
        ("When colours have to be defined, a ", ""), ("\u201cNeutral\u201d PDEF", "b"),
        (" is created. For the diversity manager to be told about that creation, ", ""),
        ("his ID must be entered on the ECO", "b"),
        (" that will be used. Go to the ECO identity card, ", ""),
        ("Actions \u203a Edit details", "ui"),
        (", and use the search engine to find and submit the ID of the diversity "
         "manager. Source [A].", "")]})
    add({"kind": "h2", "eyebrow": "Case 2",
         "title": "A PDEF under a PA that contains coloured products"})
    add({"kind": "table", "colw": (0.30, 0.42, 0.28),
         "head": ["Evolution", "What happens to the PSA reference", "Alert the RCD?"],
         "rows": [
             ["1 \u2014 You revise the PDEF", "The PSA reference does not change.",
              [("No", "ok")]],
             ["2 \u2014 You create a non-interchangeable revision",
              "The PSA reference changes.", [("Yes", "warn")]],
             ["3 \u2014 You replace the PDEF by another one",
              "The PSA reference changes.", [("Yes", "warn")]],
         ]})
    add({"kind": "callout", "tone": "dan", "label": "Cases 2 and 3",
         "text": [("Verify that the ECO carries a diversity manager ID.", "b"),
                  (" He then receives an alert email. If the field is empty, ", ""),
                  ("the system blocks", "dan"), (". Source [A].", "")]})
    add({"kind": "figure", "image": "10-neutral-blocked.png",
         "path": img("10-neutral-blocked.png"),
         "tone": "dan", "label": "Promotion Failed", "max_h": 296, "legend": "below",
         "caption": "The failure, its cause and its context in one screen, as reproduced "
                    "in the methodology. Source [A].",
         "marks": [
             {"n": 1, "box": (4, 186, 220, 72), "tone": "warn", "mpos": "tl",
              "label": "A coloured product under the PA",
              "note": "The COL-\u2026 line means colours are involved, so this ECO needs a "
                      "diversity manager."},
             {"n": 2, "box": (256, 442, 260, 42), "tone": "dan", "mpos": "bl",
              "label": "Diversity Manager: Unassigned",
              "note": "The actual cause. Fix it from Actions \u203a Edit Details on the ECO."},
             {"n": 3, "box": (698, 294, 418, 134), "tone": "dan", "mpos": "tr",
              "label": "The error message",
              "note": "\u201cPromotion Failed: There are Neutral products connected to the "
                      "ECO, you must enter a Diversity Manager ID.\u201d"},
         ]})

    # =====================================================================
    # CHAPTER 6 - tips
    # =====================================================================
    add({
        "kind": "chapter", "num": "6", "eyebrow": "Chapter 6",
        "title": "Tricks that save time",
        "lead": [("Everything on this page is a consequence of a rule stated earlier. "
                  "Collected here because this is the page worth printing.", "")],
        "covers": ["Before you create", "While you fill the form", "When you promote"],
    })
    add({"kind": "h3", "title": "Before you create"})
    add({"kind": "bullets", "columns": 2, "bullets": [
        [("Settle the Design Context first.", "b"),
         (" It freezes the moment a PSA reference is taken, and changing it then means "
          "recreating the PDEF.", "")],
        [("Check who owns the creation.", "b"),
         (" Connectors, peri-connectors and harnesses come from a manager or PTA Auto.", "")],
        [("Make sure the RT and RAL templates exist.", "b"),
         (" You have to name them on the ECO form, so a missing template stops you "
          "mid-form.", "")],
        [("Have the ECR in Design.", "b"),
         (" Use case 3 simply does not work otherwise.", "")],
    ]})
    add({"kind": "h3", "title": "While you fill the form"})
    add({"kind": "bullets", "columns": 2, "bullets": [
        [("Red now, black later \u2014 but not much later.", "b"),
         (" Black attributes can only be completed while the ECO is in Create or Define "
          "Components.", "")],
        [("Use Number of ECO to create.", "b"),
         (" One form, N ECOs, then Mass Update on a column. The biggest single "
          "time-saver.", "")],
        [("Create from the product (method 2).", "b"),
         (" It links in the same action and removes the step everyone forgets.", "")],
        [("V/O/M means Project Space.", "b"),
         (" Verify the Type column reads Project Space, never a Product Line "
          "(PL-000000).", "")],
        [("Fill Notification's context for partner and JV projects.", "b"),
         (" It is imperative there, and nobody chases you for it until it is late.", "")],
        [("Do not confuse Create Product ECO with Create Component ECO.", "b"),
         (" They sit one line apart in the menu.", "")],
    ]})
    add({"kind": "h3", "title": "When you promote"})
    add({"kind": "bullets", "columns": 2, "bullets": [
        [("Promote the documents first, then the product.", "b"),
         (" Never the other way round.", "")],
        [("Check ECO and PSA Reference", "b"),
         (" before touching the state of a PDEF \u2014 checks (A) and (B).", "")],
        [("Use Affected Items as the checklist", "b"),
         (" before promoting the ECO, and as the proof afterwards.", "")],
        [("Demote instead of forcing.", "b"),
         (" It is free and it leaves the documents untouched.", "")],
        [("Date the approval routes with Apply to Selected.", "b"),
         (" Apply to all overwrites lines you did not mean to touch.", "")],
        [("Colours involved? Set the Diversity Manager ID", "b"),
         (" on the ECO, or the promotion fails.", "")],
    ]})

    # =====================================================================
    # CHAPTER 7 - troubleshooting
    # =====================================================================
    add({
        "kind": "chapter", "num": "7", "eyebrow": "Chapter 7",
        "title": "When it does not work",
        "lead": [("Symptom on the left, the thing to actually fix on the right.", "")],
        "covers": ["Creation problems", "Promotion and release problems"],
    })
    add({"kind": "table", "colw": (0.40, 0.60), "size": 8.8,
         "head": ["Symptom", "Fix"], "rows": [
             ["\u201cNo active manufacturing site in this project space\u201d",
              "The project space is not set up. Contact the Project Owner (RPP or RPCR). "
              "You cannot fix it from the ECO."],
             ["\u201cPromotion Failed: There are Neutral products connected to the ECO\u2026\u201d",
              "The ECO has no Diversity Manager ID. Set it from Actions \u203a Edit Details "
              "on the ECO."],
             ["The green arrow does nothing on the PDEF",
              "A specification document is one state below. Promote it first, from "
              "Categories \u203a Specification Documents."],
             ["The PDEF refuses to leave In Work",
              "One of the two checks is missing: no ECO attached (A), or no PSA Reference "
              "(B)."],
             ["Cannot promote the ECO to Wait App.",
              "An attached product or DOC is not Approved yet. Check Categories \u203a "
              "Affected Items and promote what is late."],
             ["Cannot modify the product any more",
              "It has left In Work. Demote it one step, or create a revision."],
             ["Cannot revise the PREA",
              "It is in Wait App. or Approved. Demote it back to Frozen first."],
             ["Cancel and revise is greyed out",
              "The PREA is not Frozen, or it is not the last revision on the line."],
             ["Nobody signs the route",
              "RT / RAL approvers or the Responsible Design Engineer are missing on the "
              "ECO."],
             ["The design context is wrong and will not change",
              "A PSA reference has been taken. The PDEF has to be recreated."],
             ["The APQP grid cannot be managed",
              "The COFOR attributes are incomplete on the product identity card."],
         ]})

    # =====================================================================
    # CHAPTER 8 - decoder
    # =====================================================================
    add({
        "kind": "chapter", "num": "8", "eyebrow": "Chapter 8",
        "title": "Label decoder and sources",
        "lead": [("Several PLM screens in the source documents are the French interface. "
                  "This is the mapping, followed by the exact references of everything "
                  "used to build this guide.", "")],
        "covers": ["French to English UI labels", "Acronyms", "Source documents"],
    })
    add({"kind": "h2", "eyebrow": "French UI", "title": "What the screens say"})
    add({"kind": "glossary", "keyw": 126, "pairs": [
        ["En cours", "In Work"],
        ["Fig\u00e9", "Frozen"],
        ["Attente approbation", "Wait App."],
        ["Approuv\u00e9", "Approved"],
        ["Valid\u00e9", "Released / Validated"],
        ["Publi\u00e9", "Published (documents)"],
        ["Annul\u00e9", "Cancelled"],
        ["\u00c9tat", "State"],
        ["Promouvoir / R\u00e9trograder", "Promote / Demote"],
        ["Cycle de vie", "Lifecycle"],
        ["Cat\u00e9gories", "Categories"],
        ["\u00c9l\u00e9ments concern\u00e9s", "Affected Items"],
        ["R\u00e9f\u00e9renc\u00e9 par", "Referenced By"],
        ["Documents de sp\u00e9cifications", "Specification Documents"],
        ["Modification demand\u00e9e", "Requested Change"],
        ["Pour interdiction", "For Prohibition"],
        ["Valideurs de la RT / RAL", "RT / RAL approvers"],
        ["Ing\u00e9nieur concepteur responsable", "Responsible Design Engineer"],
        ["\u00c9dition des d\u00e9tails", "Edit Details"],
        ["Termin\u00e9 / Approuver", "Done / Approve"],
        ["Produit de D\u00e9finition", "Defined Product (PDEF)"],
        ["Produit R\u00e9alis\u00e9", "Realized Product (PREA)"],
        ["R\u00e9f\u00e9rence PSA", "PSA Reference"],
        ["R\u00e9vision la plus haute", "Highest revision"],
        ["Livrables attendus", "Expected deliverables"],
        ["T\u00e2ches / Signatures", "Tasks / Signatures"],
    ]})
    add({"kind": "h2", "eyebrow": "Acronyms", "title": "The short forms"})
    add({"kind": "glossary", "keyw": 74, "pairs": [
        ["PDEF", "Produit de D\u00e9finition \u2014 Defined Product"],
        ["PREA", "Produit R\u00e9alis\u00e9 \u2014 Realized Product"],
        ["ECR", "Engineering Change Request"],
        ["ECO", "Engineering Change Order (the FM / change sheet of SAP and 3DCom)"],
        ["RT", "Revue Technique \u2014 technical review"],
        ["RAL", "Revue d'Approbation des Livrables \u2014 deliverable approval review"],
        ["PA", "Produit Attendu \u2014 Expected Product"],
        ["OA / LA", "Objet attendu / Livrable attendu \u2014 expected object / deliverable"],
        ["DOC", "Specification document attached to a product"],
        ["V/O/M", "Vehicle / Organ / Module impacts, taken from the Project Space"],
        ["CADER", "Vehicle or component code for the current release"],
        ["DUD", "The milestone carried by the ECO"],
        ["COFOR", "Supplier code (intellectual property, contracting, manufacturer)"],
        ["RCD", "Contacted when a PSA reference changes under a PA with colours"],
        ["RPP / RPCR", "Project Owner, who sets up manufacturing sites on a project space"],
        ["PTA Auto", "Tool that mass-creates NP / PA / PDEF for electrical harnesses"],
        ["POFI / NON POFI", "Repetitive-library perimeters; NON POFI has its own manager"],
        ["APQP", "Advanced Product Quality Planning grid, driven by the COFOR attributes"],
    ]})

    add({"kind": "h2", "eyebrow": "Provenance", "title": "Source documents"})
    add({"kind": "table", "colw": (0.08, 0.52, 0.40),
         "head": ["Tag", "Document", "Reference"], "rows": [
             ["[A]", "METHODOLOGY Creating a Product ECO (TRANSVERSAL, COMETH PLM)",
              "Ref. 20061_17_01638 \u00b7 v8.0 \u00b7 updated 17/04/2024"],
             ["[B]", "METHODOLOGY PDEF and PREA lifecycle management (EE specific)",
              "Ref. 20061_15_01662 \u00b7 v1.0 \u00b7 ELECTRICAL SPEC"],
             ["[C]", "PREA methodologies \u2014 Creation of a PDEF / Creation of a PREA in PLM",
              "Word memo supplied with this package"],
         ]})
    add({"kind": "h3", "title": "Referenced but not included in this package"})
    add({"kind": "bullets", "columns": 2, "size": 8.8, "bullets": [
        [("MEMENTO Linking a Product to an ECO", "b"), (" \u2014 20061_17_01640", "")],
        [("METHODOLOGY Linking an ECO to an Expected Object", "b"),
         (" \u2014 20061_16_01347", "")],
        [("METHODOLOGY Add/Remove ECO under ECR", "b"), (" \u2014 20061_17_01982", "")],
        [("METHODOLOGIE R\u00e9f\u00e9rence PSA", "b"), (" \u2014 20061_14_02084", "")],
        [("Cr\u00e9ation ECO", "b"), (" \u2014 20061_14_01974", "")],
        [("ENOVIA Glossary", "b"), (" \u2014 20061_13_01595", "")],
        [("PDEF/PREA management", "b"),
         (" \u2014 HW 20061_14_01621, SW/CAL 20061_15_01666, DOTE 20061_14_01619", "")],
        [("UCG", "b"), (" \u2014 1534 creating an ECO, 1538 completing its attributes, "
                        "1535 promoting to Define Components", "")],
    ]})
    add({"kind": "callout", "tone": "warn", "label": "Confidentiality",
         "text": [("The screenshots reproduced here come from internal methodologies and "
                   "still carry real product references, project names and user IDs.", "b"),
                  (" Treat this document as internal.", "")]})

    return B
