# -*- coding: utf-8 -*-
"""
Single source of truth for the ECO deck.
Content and screenshots are derived from: PLM METHODOLOGY - CREATING A PRODUCT ECO
Ref. 20061_17_01638, v8.0, update 17/04/2024 (Stellantis / COMETH PLM, TRANSVERSAL).
Screenshots were extracted from the source PDF by extract_pdf_images.py.
Renderers: render_html.py (HTML deck) and render_pptx.py (PowerPoint).
"""

META = {
    "title": "Product ECO",
    "subtitle": "Engineering Change Order in PLM \u2014 what everyone must know",
    "source": "PLM Methodology \u00b7 Ref. 20061_17_01638 \u00b7 v8.0 \u00b7 17/04/2024",
    "footer": "Product ECO \u2014 PLM Methodology (Ref. 20061_17_01638 v8.0)",
}

# kinds: title | bullets | flow | cards | steps | table | glossary | shot | shots | close
# any text slide may carry "image": {"file":..., "caption":...} rendered as a right-hand panel
SLIDES = [
    {
        "kind": "title",
        "title": "Product ECO",
        "subtitle": "Engineering Change Order in PLM",
        "tagline": "How to create it, what to fill, and what blocks you.",
        "meta": "Source: METHODOLOGY Creating a Product ECO \u00b7 Ref. 20061_17_01638 \u00b7 v8.0 \u00b7 17/04/2024",
    },
    {
        "kind": "bullets",
        "kicker": "The basics",
        "title": "What an ECO is",
        "bullets": [
            [("ECO = Engineering Change Order", True),
             (" \u2014 the PLM object that officialises a product change.", False)],
            [("Equivalent of the FM", True), (" (change sheet) in SAP / 3DCom.", False)],
            [("It carries the change, not the geometry:", True),
             (" approvals (RT / RAL), homologation, impacts, dates, notifications.", False)],
            [("Type used here: ", False), ("ECO Type = Product", True),
             (" (there are also Component ECOs).", False)],
            [("No released product without an ECO", True),
             (" \u2014 it is the gate to officialisation.", False)],
        ],
        "note": "One sentence to remember: the ECO is the passport of a change.",
    },
    {
        "kind": "flow",
        "kicker": "Positioning",
        "title": "Where the ECO sits",
        "rows": [
            {
                "label": "Chain",
                "chips": ["ECR (Design)", "ECO", "PDEF / PREA / DOC", "OA / LA", "Release"],
                "style": "accent",
            },
        ],
        "image": {"file": "09-lifecycle.png",
                  "caption": "ECO lifecycle \u2014 Categories \u203a Lifecycle: Create \u203a Define Components \u203a "
                             "Wait App. \u203a Reviewed \u203a Released \u203a Implemented (Cancelled stays reachable)"},
        "image_pos": "below",
    },
    {
        "kind": "bullets",
        "kicker": "Before you click",
        "title": "Prerequisites",
        "bullets": [
            [("Role: ", False), ("PSA_Pilote_Projet or PSA_Concepteur", True)],
            [("Diversity and applicability contexts are defined", True)],
            [("Expected Product (PA) created with diversity applicability", True)],
            [("Reviewer and approval lists created and defined", True),
             (" \u2014 RT and RAL templates must already exist.", False)],
            [("The PDEF, PREA or DOC concerned exists", True)],
            [("ECR in ", False), ("Design", True), (" for a revision \u2014 or OA/LA in ", False),
             ("Create", True), (" for a first release / reuse.", False)],
        ],
        "note": "Missing one of these is the #1 reason a creation or a promotion fails.",
    },
    {
        "kind": "cards",
        "kicker": "3 ways in",
        "title": "The three use cases",
        "cards": [
            {
                "tag": "UC 1",
                "title": "From the home page",
                "lines": ["Actions \u203a Create Product ECO",
                          "Fill attributes \u203a Finish",
                          "Then link it to a product, an LA or an ECR",
                          "Best for: batch creation"],
            },
            {
                "tag": "UC 2",
                "title": "From the product",
                "lines": ["Open the PDEF / PREA / DOC identity card",
                          "Categories \u203a Linked ECO and ECR",
                          "ECOs sub-tab \u203a Create Product ECO",
                          "Best for: creates AND links in one shot"],
            },
            {
                "tag": "UC 3",
                "title": "From the ECR",
                "lines": ["ECR must be in state Design",
                          "Categories \u203a ECOs & ECs",
                          "Structure View \u203a Actions \u203a Create Product ECO",
                          "Best for: change driven by an ECR"],
            },
        ],
    },
    {
        "kind": "shot",
        "kicker": "Method 1 \u00b7 step 1",
        "title": "Actions \u203a Create Product ECO",
        "image": "01-actions-menu.png",
        "notes": [
            [("Home page \u203a ", False), ("Actions", True), (" toolbar icon.", False)],
            [("Column ", False), ("Change", True), (" \u203a ", False), ("Create Product ECO\u2026", True)],
            [("Do not confuse it with ", False), ("Create Component ECO", True),
             (" just below, nor with ", False), ("Create ECR", True), (".", False)],
            [("From here the ECO is born unlinked \u2014 you must attach it afterwards.", False)],
        ],
    },
    {
        "kind": "shots",
        "kicker": "Method 1 \u00b7 step 2",
        "title": "The creation form",
        "images": [
            {"file": "03a-form-top.png",
             "label": "Basic attributes",
             "caption": "Type, Description, Maturity, Homologation Flow & User, Engineering approval (RT), "
                        "Release approval (RAL)."},
            {"file": "03b-form-bottom.png",
             "label": "Identification & impacts",
             "caption": "Responsible Design Engineer, Number of ECO to create, Cader, DUD, "
                        "Notification's context, V/O/M Impacts, Manufacturing Site."},
        ],
        "callout": {
            "tone": "warn",
            "text": "Red italic = required to confirm the creation. Black fields can wait \u2014 but only while the ECO "
                    "is in Create or Define Components maturity.",
        },
    },
    {
        "kind": "shot",
        "kicker": "Method 1 \u00b7 shortcut",
        "title": "Create several ECOs in one go",
        "image": "02-batch-grid.png",
        "notes": [
            [("Set ", False), ("Number of ECO to create", True), (" before validating.", False)],
            [("PLM opens a mass-update grid: same attributes, N ECO numbers.", False)],
            [("Use ", False), ("Mass Update", True), (" to change a column on every line, then ", False),
             ("Save", True), (".", False)],
            [("Ideal when one change hits several parts of the same perimeter.", False)],
        ],
    },
    {
        "kind": "table",
        "kicker": "The checklist",
        "title": "Attributes required to release",
        "head": ["Field", "Rule"],
        "rows": [
            ["Description", "Follow the Electricity/Electronics or Mechanical Engineering filling guides."],
            ["Due Date", "PROTO or SERIE."],
            ["Homologation Flow", "YES if the ECO has a PRODUCTION (SERIE) flow. Check with the Homologation Manager first."],
            ["Homologation User", "Mandatory when Homologation Flow = YES. Pick the ID from the Homologation User List."],
            ["Responsible Design Engineer", "Name of the component manager. Required for release."],
            ["RT Approvers", "Workflow template of the technical review (RT)."],
            ["RAL Approvers", "Workflow template of the deliverable approval review (RAL)."],
            ["CADER / DUD", "Select the CADER if one exists for the release, otherwise leave blank. DUD = milestone."],
            ["Notification's context", "Alerts the notification technician. Mandatory for a partner / JV project."],
        ],
    },
    {
        "kind": "steps",
        "kicker": "Impacts",
        "title": "V / O / M impacts & manufacturing site",
        "steps": [
            [("Check the ", False), ("Project Space", True), (" attribute.", False)],
            [("Search the project name.", False)],
            [("Select the result whose type is ", False), ("Project Space", True), (", then ", False),
             ("Submit", True), (".", False)],
            [("Choose one or more ", False), ("manufacturing sites", True),
             (" \u2014 they fill the Manufacturing Site field automatically.", False)],
        ],
        "image": {"file": "04-vom-warning.png", "caption": "The warning from the methodology"},
        "callout": {
            "tone": "warn",
            "text": "\u201cNo active manufacturing site in this project space\u201d \u203a the project space is not set up. "
                    "Contact the Project Owner (RPP / RPCR); you cannot fix it from the ECO.",
        },
    },
    {
        "kind": "shot",
        "kicker": "Impacts",
        "title": "Pick the project space, not the product line",
        "image": "05-project-space-search.png",
        "notes": [
            [("Refine on ", False), ("Types \u203a Project Management \u203a Project Space", True), (".", False)],
            [("Check the line whose ", False), ("Type", True), (" column reads ", False),
             ("Project Space", True), (", then Submit.", False)],
            [("Never select a ", False), ("Product Line (PL-000000)", True), (" \u2014 impacts would be wrong.", False)],
        ],
    },
    {
        "kind": "shots",
        "kicker": "Methods 2 & 3",
        "title": "Create the ECO from the object itself",
        "images": [
            {"file": "06-linked-eco-ecr.png",
             "label": "UC 2 \u00b7 from the product",
             "caption": "PDEF identity card \u203a Categories \u203a Linked ECO and ECR \u203a tab ECOs \u203a "
                        "Create Product ECO \u2014 creates and links in one action."},
            {"file": "07-ecr-structure-view.png",
             "label": "UC 3 \u00b7 from the ECR",
             "caption": "ECR (state Design) \u203a Categories \u203a ECOs & ECs \u203a Structure View \u203a "
                        "Actions \u203a Create Product ECO\u2026"},
        ],
    },
    {
        "kind": "table",
        "kicker": "Linking",
        "title": "Attach an existing ECO",
        "head": ["Target", "Reference document"],
        "rows": [
            ["PDEF / PREA or DOC", "MEMENTO Linking a Product to an ECO \u2014 20061_17_01640"],
            ["OA / LA (expected deliverable)", "METHODOLOGY Linking an ECO to an Expected Object \u2014 20061_16_01347"],
            ["ECR", "METHODOLOGY Add/Remove ECO under ECR \u2014 20061_17_01982"],
        ],
        "callout": {
            "tone": "ok",
            "text": "Shortcut: creating the ECO from the product identity card (UC 2) does the create + link in a single action.",
        },
    },
    {
        "kind": "shot",
        "kicker": "Management",
        "title": "Put a due date on the approvals",
        "image": "08-approvals-due-date.png",
        "notes": [
            [("Identity card or ", False), ("Categories \u203a Lifecycle", True), (" \u203a tab ", False),
             ("Approvals", True), (" \u203a ", False), ("Edit", True), (".", False)],
            [("Column = ", False), ("Due Date", True), (", Value = ", False), ("dd/MM/yy", True),
             (", pick the day in the calendar.", False)],
            [("Tick the RT / RAL lines \u203a ", False), ("Apply to Selected", True),
             (" (or Apply to all) \u203a ", False), ("Done", True), (".", False)],
            [("Result: every RT and RAL task carries a visible deadline.", False)],
        ],
    },
    {
        "kind": "bullets",
        "kicker": "Colours",
        "title": "Neutral PDEF & Diversity Manager",
        "bullets": [
            [("Defining colours requires a ", False), ("\u201cNeutral\u201d PDEF", True), (".", False)],
            [("The Diversity Manager must be informed \u203a put his ID on the ECO:", False)],
            [("ECO identity card \u203a Actions \u203a Edit Details \u203a field ", False),
             ("Diversity Manager", True), (" \u203a search the ID \u203a submit.", False)],
            [("Forget it and the promotion fails \u2014 see the next slide.", False)],
        ],
        "callout": {
            "tone": "danger",
            "text": "No Diversity Manager ID = blocked system. Fill it at creation, not when the workflow stops.",
        },
    },
    {
        "kind": "cards",
        "kicker": "Typical case",
        "title": "PDEF under a PA with coloured products",
        "cards": [
            {
                "tag": "Evolution 1",
                "title": "Revise the PDEF",
                "lines": ["PSA reference unchanged", "No RCD alert needed", "Simplest path"],
                "tone": "ok",
            },
            {
                "tag": "Evolution 2",
                "title": "Non-interchangeable revision",
                "lines": ["PSA reference changes", "Alert the RCD", "Diversity Manager ID required on the ECO"],
                "tone": "warn",
            },
            {
                "tag": "Evolution 3",
                "title": "Replace the PDEF",
                "lines": ["PSA reference changes", "Alert the RCD", "Diversity Manager ID required on the ECO"],
                "tone": "warn",
            },
        ],
        "footnote": "For Evolutions 2 and 3 the Diversity Manager receives the alert e-mail only if his ID is on the ECO \u2014 "
                    "otherwise the system blocks.",
    },
    {
        "kind": "shot",
        "kicker": "The blocker",
        "title": "Promotion failed: Neutral products connected",
        "image": "10-neutral-blocked.png",
        "notes": [
            [("A coloured product (COL-\u2026) sits next to the PDEF under the PA.", False)],
            [("The ECO shows ", False), ("Diversity Manager: Unassigned", True), (".", False)],
            [("Promotion is refused: ", False),
             ("\u201cThere are Neutral products connected to the ECO, you must enter a Diversity Manager ID\u201d", True),
             (".", False)],
            [("Fix: Actions \u203a Edit Details \u203a set the Diversity Manager, then promote again.", False)],
        ],
    },
    {
        "kind": "bullets",
        "kicker": "Tips",
        "title": "What experienced users do",
        "columns": 2,
        "bullets": [
            [("Create from the product", True), (" (UC 2) to avoid an orphan ECO.", False)],
            [("Batch-create", True), (" when several parts share one change.", False)],
            [("Call the Homologation Manager first", True),
             (" \u2014 some breakdowns are exempt from RHN flows; the approver holds the list.", False)],
            [("Fill Notification's context", True), (" on any JV / partner ECO, or the folder is never diffused.", False)],
            [("Set the Diversity Manager", True), (" as soon as colours are involved.", False)],
            [("Fill every black field early", True), (" \u2014 the window closes after Define Components.", False)],
            [("Put due dates on RT and RAL", True), (" \u2014 no date, no follow-up.", False)],
            [("Check the ECR is in Design", True), (" before hunting for the Create Product ECO action.", False)],
        ],
    },
    {
        "kind": "table",
        "kicker": "Troubleshooting",
        "title": "Blockers and their fix",
        "head": ["Symptom", "Fix"],
        "rows": [
            ["Cannot create the ECO", "A red field is empty, or the role is wrong (PSA_Pilote_Projet / PSA_Concepteur)."],
            ["Create Product ECO not available on the ECR", "The ECR is not in state Design."],
            ["Cannot edit an attribute anymore", "The ECO left Create / Define Components maturity."],
            ["No active manufacturing site in this project space", "Project space not configured \u2014 contact the Project Owner (RPP / RPCR)."],
            ["Promotion failed: Neutral products connected", "Add the Diversity Manager ID (Actions \u203a Edit Details)."],
            ["Release refused", "Missing Responsible Design Engineer, Homologation User, RT or RAL approvers."],
        ],
    },
    {
        "kind": "glossary",
        "kicker": "Vocabulary",
        "title": "Decoder",
        "pairs": [
            ["ECO", "Engineering Change Order \u2014 officialises a change"],
            ["ECR", "Engineering Change Request \u2014 upstream demand"],
            ["PDEF", "Defined Product"],
            ["PREA", "Realized Product"],
            ["PA", "Expected Product (structure)"],
            ["OA / LA", "Expected object / expected deliverable"],
            ["DOC", "Document object"],
            ["RT", "Technical review workflow"],
            ["RAL", "Deliverable approval review workflow"],
            ["V / O / M", "Impacts declared via the project space"],
            ["CADER", "Vehicle or Component code"],
            ["DUD", "Milestone (e.g. 1st pre-series vehicle)"],
            ["RCD", "Diversity/configuration referent to alert"],
            ["RPP / RPCR", "Project owner roles"],
            ["FM", "Change sheet in SAP / 3DCom (ECO equivalent)"],
            ["Neutral", "Colour-less PDEF required to define colours"],
        ],
    },
    {
        "kind": "close",
        "title": "Remember 5 things",
        "points": [
            "The ECO is the gate: no ECO, no released product.",
            "Prerequisites first \u2014 role, ECR in Design, RT/RAL templates.",
            "Red fields to create, black fields before Define Components ends.",
            "V/O/M = Project Space, never the Product Line.",
            "Colours involved \u203a Diversity Manager ID, or the system blocks.",
        ],
        "meta": "Full procedure and screenshots: METHODOLOGY Creating a Product ECO \u2014 Ref. 20061_17_01638 v8.0 (17/04/2024). "
                "Related: 20061_17_01640, 20061_16_01347, 20061_17_01982.",
    },
]
