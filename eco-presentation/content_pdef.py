# -*- coding: utf-8 -*-
"""
PDEF & PREA lifecycle deck.
Content and screenshots derived from: METHODOLOGY PDEF and PREA lifecycle management
(EE specific) - Ref. 20061_15_01662, v1.0, ELECTRICAL SPEC, updated 08/07/2026.
Screenshots extracted from the source PDF by extract_pdf_images.py.
Build: python3 render_html.py content_pdef && python3 render_pptx.py content_pdef
"""

META = {
    "title": "PDEF & PREA lifecycle",
    "subtitle": "Promote, demote, prohibit, revise \u2014 EE specific",
    "source": "PLM Methodology \u00b7 Ref. 20061_15_01662 \u00b7 v1.0",
    "footer": "PDEF & PREA lifecycle management (EE) \u2014 Ref. 20061_15_01662 v1.0",
    "outfile": "PDEF_PREA_Lifecycle_Presentation",
    "imgdir": "img_pdef",
}

SLIDES = [
    {
        "kind": "title",
        "title": "PDEF & PREA lifecycle",
        "subtitle": "Promote, demote, prohibit, revise \u2014 EE specific",
        "tagline": "How a defined product and a realized product climb to Released, and what stops them.",
        "meta": "Source: METHODOLOGY PDEF and PREA lifecycle management (EE specific) \u00b7 "
                "Ref. 20061_15_01662 \u00b7 v1.0 \u00b7 ELECTRICAL SPEC",
    },
    {
        "kind": "bullets",
        "kicker": "Scope",
        "title": "What this covers",
        "bullets": [
            [("Guide for EE professionals and designers", True),
             (" on the lifecycle of PDEF and PREA.", False)],
            [("Valid for the four general classes: ", False), ("HW, SW, CAL, DOTE", True), (".", False)],
            [("Tool: ", False), ("ENOVIA V6 (PLM)", True), (", role ", False),
             ("PSA_Concepteur.Elec.XXX", True), (".", False)],
            [("The PDEF / PREA must already exist in the database", True),
             (" \u2014 this is not a creation guide.", False)],
            [("Everything above ", False), ("Approved", True),
             (" is driven by the ECO, not by the product itself.", False)],
        ],
        "note": "The source document is bilingual FR/EN and the screens are the French UI \u2014 "
                "slide 20 maps the labels.",
    },
    {
        "kind": "flow",
        "kicker": "The two ladders",
        "title": "States you must know",
        "rows": [
            {"label": "PDEF \u00b7 defined product",
             "chips": ["In Work", "Wait App.", "Approved", "Released"], "style": "accent"},
            {"label": "PREA \u00b7 realized product",
             "chips": ["In Work", "Frozen", "Wait App.", "Approved", "Released"], "style": "muted"},
        ],
        "footnote": "Only the PREA has a Frozen step, and only the PREA can be cancelled & revised. "
                    "Both can end up Prohibited. The ECO runs its own ladder: "
                    "Create \u203a Define Components \u203a Wait App. \u203a Review \u203a Released \u203a Implemented.",
    },
    {
        "kind": "table",
        "kicker": "The golden rule",
        "title": "Documents move first",
        "head": ["To reach this state", "the specification documents must already be"],
        "rows": [
            ["PDEF \u2192 Wait App.", "Wait App."],
            ["PDEF \u2192 Approved", "Approved"],
            ["PDEF \u2192 Released (via the ECO)", "Released / Published"],
            ["PREA \u2192 Frozen", "Frozen"],
            ["PREA \u2192 Wait App.", "Wait App."],
            ["PREA \u2192 Approved", "Approved"],
            ["PREA \u2192 Released (via the ECO)", "Published"],
        ],
        "callout": {
            "tone": "ok",
            "text": "Where to check: Categories \u203a Specification Documents. In the State column, "
                    "the green arrow promotes each document one step.",
        },
    },
    {
        "kind": "steps",
        "kicker": "Mechanics",
        "title": "Two ways to move one step",
        "steps": [
            [("Green arrow", True), (" next to the state on the identity card \u2014 fastest.", False)],
            [("Or ", False), ("Categories \u203a Lifecycle", True), (" \u203a ", False), ("Promote", True),
             (" in the lifecycle window.", False)],
            [("Going back down is the same gesture: ", False), ("red arrow", True), (" or ", False),
             ("Demote", True), (".", False)],
            [("Each click moves exactly one state \u2014 there is no jump to Released.", False)],
        ],
        "image": {"file": "02-pdef-wait-app.jpg",
                  "caption": "PDEF promoted to Attente Approbation (Wait App.)"},
    },
    {
        "kind": "shot",
        "kicker": "Before Wait App.",
        "title": "Two things must be on the PDEF",
        "image": "01-pdef-in-work.jpg",
        "notes": [
            [("An ", False), ("ECO", True), (" must be linked (top right of the card). "
                                            "If not, create one \u2014 see the ECO methodology.", False)],
            [("A ", False), ("PSA Reference", True),
             (" must be assigned. If not, run the PSA Reference methodology.", False)],
            [("Here the product is still ", False), ("En Cours (In Work)", True),
             (" and the PSA Reference cell is empty.", False)],
            [("Check the specification documents too \u2014 they gate the promotion.", False)],
        ],
    },
    {
        "kind": "shot",
        "kicker": "Result",
        "title": "Wait App. locks the content",
        "image": "03-pdef-demoted.jpg",
        "notes": [
            [("Once in ", False), ("Wait App.", True), (", no modification is possible.", False)],
            [("To edit again: ", False), ("Demote", True), (" back to ", False), ("In Work", True),
             (" (red arrow or Categories \u203a Lifecycle \u203a Demote).", False)],
            [("Demotion does not touch the specification documents", True),
             (" \u2014 they stay where they are.", False)],
            [("Same logic one floor up: Approved \u2192 Wait App. to reopen, or make a revision.", False)],
        ],
    },
    {
        "kind": "steps",
        "kicker": "Release",
        "title": "The ECO releases the product",
        "steps": [
            [("Open the PDEF (or PREA) in ", False), ("Approved", True),
             (" and click the ", False), ("ECO link", True), (" on the card.", False)],
            [("On the ECO: ", False), ("Actions \u203a Edit Details", True), (".", False)],
            [("Check the three attributes that drive the workflow:", False)],
            [("RT approvers", True), (" (technical review), ", False), ("RAL approvers", True),
             (" (deliverable approval), ", False), ("Responsible Design Engineer", True), (".", False)],
            [("Use the ", False), ("\u201c\u2026\u201d", True), (" buttons to change a value, then ", False),
             ("Done", True), (".", False)],
        ],
    },
    {
        "kind": "shot",
        "kicker": "Release",
        "title": "The three attributes to check",
        "image": "04-eco-edit-details.jpg",
        "notes": [
            [("Valideurs de la RT", True), (" \u2014 workflow template of the technical review.", False)],
            [("Valideurs de la RAL", True), (" \u2014 workflow template of the deliverable approval.", False)],
            [("Ing\u00e9nieur concepteur responsable", True),
             (" \u2014 the designer answering for the change.", False)],
            [("Red italic fields are required", True),
             (" (R\u00e8gle de gestion, Description, Flux Homologation).", False)],
            [("\u201c\u2026\u201d opens the picker, ", False), ("Effacer", True),
             (" clears a value, ", False), ("Termin\u00e9", True), (" saves.", False)],
        ],
    },
    {
        "kind": "steps",
        "kicker": "Release",
        "title": "Climbing the ECO",
        "steps": [
            [("Promote to ", False), ("Define Components", True),
             (" \u2014 possible once project and business agree on the deliverable target dates. "
              "The designer becomes the ECO owner.", False)],
            [("Promote again to ", False), ("Wait App.", True), (": the business signals the work is finished.", False)],
            [("Allowed only if everything attached to the ECO is ready: ", False),
             ("PDEF Approved and its DOC Approved", True), (" (for a PREA: PREA Approved, DOC Validated).", False)],
            [("Check it in ", False), ("Categories \u203a Affected Items", True),
             (" and promote what is late.", False)],
        ],
        "image": {"file": "05-eco-lifecycle.jpg",
                  "caption": "The ECO ladder: Cr\u00e9er \u203a D\u00e9finir composants \u203a Attente appro. \u203a "
                             "Revue \u203a Valid\u00e9 \u203a Impl\u00e9ment\u00e9"},
        "callout": {
            "tone": "warn",
            "text": "The ECO cannot be promoted while one attached document or product is still one floor below. "
                    "That is the most common blocker at release time.",
        },
    },
    {
        "kind": "shots",
        "kicker": "Approvals",
        "title": "RT then RAL: the two routes",
        "images": [
            {"file": "06-eco-approvals.jpg",
             "label": "Lifecycle \u203a Approvals",
             "caption": "Tick the state line (A), then Approve/Reject (B). The assignee appears in "
                        "T\u00e2ches/Signatures; a task notification lands in his mailbox."},
            {"file": "07-approve-popup.jpg",
             "label": "The pop-up",
             "caption": "Add a comment, select Approuver (Approve), then Termin\u00e9 (Done). "
                        "The route is launched."},
        ],
    },
    {
        "kind": "bullets",
        "kicker": "Approvals",
        "title": "Who does what, in order",
        "bullets": [
            [("RT approver", True), (" validates the route that takes the ECO to ", False),
             ("Wait App.", True), (" \u2014 the ECO then moves to ", False), ("Review", True), (".", False)],
            [("RAL approver", True), (" validates the route that takes the ECO to ", False),
             ("Released", True), (".", False)],
            [("Each one works from ", False), ("Categories \u203a Lifecycle \u203a Approvals", True),
             (" on the ECO, never from the product.", False)],
            [("A route waiting for a signature is marked by an icon on the ECO.", False)],
            [("When the RAL route is approved, the ECO is ", False), ("Released", True),
             (" \u2014 and so is everything it carries.", False)],
        ],
    },
    {
        "kind": "shot",
        "kicker": "Done",
        "title": "Check the result on Affected Items",
        "image": "08-affected-items.jpg",
        "notes": [
            [("On the released ECO: ", False), ("Categories \u203a Affected Items", True), (".", False)],
            [("The PDEF is ", False), ("Valid\u00e9 / Released", True),
             (" and the specification document is ", False), ("Publi\u00e9 / Published", True), (".", False)],
            [("The previous revision flips to ", False), ("Obsolete", True),
             (" \u2014 visible under the state.", False)],
            [("If a line is not at the expected state, the release is not finished.", False)],
        ],
    },
    {
        "kind": "bullets",
        "kicker": "PREA specifics",
        "title": "What changes for a realized product",
        "bullets": [
            [("Extra first step: ", False), ("Frozen", True),
             (" \u2014 reachable only when the documents are Frozen.", False)],
            [("After Frozen, no modification: content changes need a ", False), ("revision", True), (".", False)],
            [("A PREA in ", False), ("Wait App.", True), (" or ", False), ("Approved", True),
             (" cannot be revised \u2014 demote it back to Frozen first.", False)],
            [("For Released, the attached documents must be ", False), ("Published", True), (".", False)],
            [("Only the PREA offers ", False), ("Cancel and revise", True), (" (next slide).", False)],
        ],
    },
    {
        "kind": "steps",
        "kicker": "PREA \u00b7 repair",
        "title": "Cancel and revise a faulty PREA",
        "steps": [
            [("Use it to retire a faulty PSA Reference and get a new one.", False)],
            [("Conditions: the PREA is ", False), ("Frozen", True), (" and it is the ", False),
             ("last revision on the line", True), (".", False)],
            [("On the PREA: ", False), ("Actions \u203a Cancel and revise", True), (".", False)],
            [("The faulty PREA becomes ", False), ("Cancelled", True),
             ("; a new revision is created in ", False), ("In Work", True), (".", False)],
            [("Then link the new revision to an ECO and launch the ", False),
             ("creation of its PSA Reference", True),
             (". The PDEF\u2013PREA link is carried over (Categories \u203a Referenced By).", False)],
        ],
        "callout": {
            "tone": "danger",
            "text": "This action is irreversible. Check the revision and the state before you click.",
        },
    },
    {
        "kind": "shots",
        "kicker": "PREA \u00b7 repair",
        "title": "Before and after",
        "images": [
            {"file": "12-prea-frozen.jpg",
             "label": "Before \u00b7 Fig\u00e9 (Frozen)",
             "caption": "The faulty PREA, still Frozen, with its PSA Reference and its ECO pour "
                        "Officialisation."},
            {"file": "13-prea-cancelled.jpg",
             "label": "After \u00b7 Annul\u00e9 (Cancelled)",
             "caption": "The PREA is Cancelled and R\u00e9vision la plus haute points to the new "
                        "revision, which starts In Work."},
        ],
    },
    {
        "kind": "steps",
        "kicker": "Prohibition \u00b7 1/2",
        "title": "Prepare the ECO that forbids",
        "steps": [
            [("Open the PDEF or PREA in ", False), ("Released / Validated", True), (".", False)],
            [("Categories \u203a Referenced By", True),
             (" to see which PA (for a PDEF) or which PDEF (for a PREA) the prohibition will hit.", False)],
            [("Create an ECO", True), (" for the prohibition and link it to the product.", False)],
            [("Actions \u203a Edit Details: fill the ", False), ("RAL approvers", True), (" and the ", False),
             ("Responsible Design Engineer", True), (".", False)],
        ],
        "image": {"file": "09-referenced-by.jpg",
                  "caption": "Categories \u203a R\u00e9f\u00e9renc\u00e9 par (Referenced By)"},
        "callout": {
            "tone": "ok",
            "text": "The RT approver is not required for a prohibition \u2014 only the RAL route runs.",
        },
    },
    {
        "kind": "shots",
        "kicker": "Prohibition \u00b7 2/2",
        "title": "Declare the intent, then release it",
        "images": [
            {"file": "10-for-prohibition.jpg",
             "label": "Affected Items \u203a Edit All",
             "caption": "Modification demand\u00e9e (Requested Change) = Pour interdiction "
                        "(For Prohibition), then Save."},
            {"file": "11-vom-project-search.jpg",
             "label": "V/O/M Impacts \u203a Add Existing",
             "caption": "Search the project and Submit \u2014 the project is then linked to the ECO."},
        ],
        "callout": {
            "tone": "warn",
            "text": "Then Lifecycle \u203a Promote up to Review, the RAL approver validates, the ECO turns Released "
                    "and Affected Items shows the product as Prohibited.",
        },
    },
    {
        "kind": "bullets",
        "kicker": "Tips",
        "title": "What saves time",
        "columns": 2,
        "bullets": [
            [("Promote the documents first", True), (", then the product \u2014 never the other way round.", False)],
            [("Check ECO + PSA Reference", True), (" before touching the state of a PDEF.", False)],
            [("Fill RT / RAL / RDE early", True), (" on the ECO; an empty route blocks the release.", False)],
            [("Use Affected Items", True), (" as your checklist before promoting an ECO.", False)],
            [("Demote instead of forcing", True), (" \u2014 demotion is free and leaves documents untouched.", False)],
            [("Revise a PREA only from Frozen", True), (" \u2014 Wait App. and Approved refuse it.", False)],
            [("Referenced By", True), (" tells you who suffers from a prohibition, before you launch it.", False)],
            [("Cancel and revise is final", True), (" \u2014 note the new revision number immediately.", False)],
        ],
    },
    {
        "kind": "table",
        "kicker": "Troubleshooting",
        "title": "Blockers and their fix",
        "head": ["Symptom", "Fix"],
        "rows": [
            ["The green arrow does nothing on the PDEF", "A specification document is one state below. Promote it first."],
            ["Cannot promote the ECO to Wait App.", "An attached product or DOC is not Approved yet \u2014 check Affected Items."],
            ["Cannot modify the product anymore", "It left In Work. Demote it, or create a revision."],
            ["Cannot revise the PREA", "It is in Wait App. or Approved \u2014 demote back to Frozen."],
            ["Cancel and revise is greyed out", "The PREA is not Frozen, or it is not the last revision on the line."],
            ["Nobody signs the route", "RT / RAL approvers or the Responsible Design Engineer are missing on the ECO."],
        ],
    },
    {
        "kind": "glossary",
        "kicker": "French UI",
        "title": "Label decoder",
        "pairs": [
            ["En cours", "In Work"],
            ["Fig\u00e9", "Frozen"],
            ["Attente approbation", "Wait App."],
            ["Approuv\u00e9", "Approved"],
            ["Valid\u00e9", "Released / Validated"],
            ["Publi\u00e9", "Published (documents)"],
            ["Annul\u00e9", "Cancelled"],
            ["Promouvoir / R\u00e9trograder", "Promote / Demote"],
            ["Cycle de vie", "Lifecycle"],
            ["\u00c9l\u00e9ments concern\u00e9s", "Affected Items"],
            ["R\u00e9f\u00e9renc\u00e9 par", "Referenced By"],
            ["Documents de sp\u00e9cifications", "Specification Documents"],
            ["Modification demand\u00e9e", "Requested Change"],
            ["Pour interdiction", "For Prohibition"],
            ["Valideurs de la RT / RAL", "RT / RAL approvers"],
            ["Ing\u00e9nieur concepteur responsable", "Responsible Design Engineer"],
            ["\u00c9dition des d\u00e9tails", "Edit Details"],
            ["Termin\u00e9 / Approuver", "Done / Approve"],
        ],
    },
    {
        "kind": "close",
        "title": "Remember 5 things",
        "points": [
            "Documents climb first \u2014 the product follows one state at a time.",
            "No PDEF promotion without an ECO and a PSA Reference.",
            "Above Approved, it is the ECO (RT then RAL) that releases everything.",
            "Affected Items is the truth: check it before and after.",
            "PREA only: Frozen to revise, and Cancel and revise is irreversible.",
        ],
        "meta": "Full procedure and screenshots: METHODOLOGY PDEF and PREA lifecycle management (EE specific) \u2014 "
                "Ref. 20061_15_01662 v1.0. Related: ENOVIA Glossary 20061_13_01595, "
                "PDEF/PREA management HW 20061_14_01621, SW/CAL 20061_15_01666, DOTE 20061_14_01619.",
    },
]
