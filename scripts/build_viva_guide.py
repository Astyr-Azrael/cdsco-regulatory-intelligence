from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "viva" / "CDSCO_Viva_Presentation_Guide.docx"

NAVY = "17324D"
RED = "8E1D2C"
GRAY = "F3F5F7"
LIGHT_BLUE = "EAF1F7"
BORDER = "D9D9D9"


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_border(cell, color=BORDER):
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    for edge in ("top", "left", "bottom", "right"):
        tag = "w:" + edge
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), "6")
        element.set(qn("w:color"), color)


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    header = OxmlElement("w:tblHeader")
    header.set(qn("w:val"), "true")
    tr_pr.append(header)


def font(run, size=10.5, bold=False, color="000000", italic=False):
    run.font.name = "Aptos"
    run._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
    run._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor.from_string(color)


def add_text(doc, text, style=None, size=10.5, bold=False, color="000000", italic=False, align=None, before=0, after=6):
    p = doc.add_paragraph(style=style)
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.12
    if align is not None:
        p.alignment = align
    r = p.add_run(text)
    font(r, size=size, bold=bold, color=color, italic=italic)
    return p


def add_bullets(doc, items, size=10.5):
    for item in items:
        p = doc.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.06
        r = p.add_run(item)
        font(r, size=size)


def add_table(doc, headers, rows, widths, small=False):
    table = doc.add_table(rows=1, cols=len(headers))
    table.autofit = False
    table.style = "Table Grid"
    set_repeat_table_header(table.rows[0])
    for i, header in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.width = Inches(widths[i])
        cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_shading(cell, NAVY)
        set_cell_border(cell)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(header)
        font(r, size=9.2 if small else 9.8, bold=True, color="FFFFFF")
    for row_index, row in enumerate(rows):
        cells = table.add_row().cells
        for i, value in enumerate(row):
            cell = cells[i]
            cell.width = Inches(widths[i])
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            if row_index % 2 == 1:
                set_cell_shading(cell, GRAY)
            set_cell_border(cell)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.0
            r = p.add_run(value)
            font(r, size=8.7 if small else 9.4, bold=(i == 0))
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


def heading(doc, text, level=1):
    p = doc.add_paragraph(style=f"Heading {level}")
    p.paragraph_format.space_before = Pt(11 if level == 1 else 7)
    p.paragraph_format.space_after = Pt(5)
    r = p.add_run(text)
    font(r, size=15 if level == 1 else 12, bold=True, color="000000")
    return p


def page_break(doc):
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def script_block(doc, label, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.2)
    p.paragraph_format.right_indent = Inches(0.2)
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(7)
    p.paragraph_format.line_spacing = 1.12
    r = p.add_run(label + " ")
    font(r, size=10.6, bold=True, color=RED)
    r = p.add_run(text)
    font(r, size=10.6)


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.68)
    section.bottom_margin = Inches(0.62)
    section.left_margin = Inches(0.74)
    section.right_margin = Inches(0.74)

    styles = doc.styles
    styles["Normal"].font.name = "Aptos"
    styles["Normal"]._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
    styles["Normal"]._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
    styles["Normal"].font.size = Pt(10.5)
    for name in ("Title", "Heading 1", "Heading 2"):
        styles[name].font.name = "Aptos"
        styles[name]._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
        styles[name]._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
        styles[name].font.color.rgb = RGBColor(0, 0, 0)

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = footer.add_run("CDSCO Regulatory Intelligence   |   Viva Presentation Guide")
    font(r, size=8.5, color="666666")

    title = doc.add_paragraph(style="Title")
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title.paragraph_format.space_after = Pt(8)
    r = title.add_run("CDSCO Viva Presentation Guide")
    font(r, size=24, bold=True, color="000000")
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    subtitle.paragraph_format.space_after = Pt(20)
    r = subtitle.add_run("Exact speaking notes, model selection answers, demo flow and viva questions")
    font(r, size=12, color="404040")

    add_text(doc, "How to use this guide", style="Heading 1", size=15, bold=True)
    add_text(doc, "Use the short script under each heading as your speaking language. Do not memorise every word. Learn the opening, the method-selection explanation, the live demo route and the limitation answers. Speak slowly, explain the evidence on screen, and avoid claiming more than the project demonstrates.", size=10.8)
    add_text(doc, "Core message", style="Heading 2", size=12, bold=True)
    add_text(doc, "We built a reproducible local data-engineering system that converts selected official CDSCO records into source-traceable regulatory rows and cautious entity histories. The project does not predict medicine safety or prove legal company identity.", size=10.8, bold=True, color=RED)
    add_text(doc, "Verified final facts", style="Heading 2", size=12, bold=True)
    add_table(doc, ["Item", "What to state"], [
        ["Indexed corpus", "599 regulatory source rows from eight preserved 2025 PDFs and one August 2026 public portal snapshot"],
        ["Evidence", "Nine preserved source documents or snapshots, with matching SHA-256 hashes"],
        ["Entity layer", "399 organization-name clusters and 505 product-wording clusters"],
        ["Review state", "17 primary source-text decisions: 11 accepted links and six rejections; 348 suggestions remain unreviewed"],
        ["Verification", "33 automated tests passed; one optional live test skipped; the frontend production build passed"],
    ], [1.45, 5.85])

    page_break(doc)
    heading(doc, "One Minute Opening Script")
    script_block(doc, "Say this:", "Good morning, ma'am. Our project is Entity Centric Drug Regulatory Intelligence from Fragmented CDSCO Alerts. CDSCO publishes regulatory information through PDFs and a separate public portal. A user can read one document, but it is difficult to follow the same drug, manufacturer wording or batch across different publications while retaining the official source. Our project collects a bounded set of real CDSCO records, reconstructs rows from their layouts, preserves the raw evidence, and shows source-traceable histories through a web application.")
    script_block(doc, "Then state the scope:", "The final local demo indexes 599 source rows. These include 379 rows reconstructed from eight official PDFs and 220 rows from one August 2026 public NSQ portal snapshot. This is an indexed corpus for a working academic demonstration, not a claim of complete CDSCO coverage.")
    script_block(doc, "Then state the boundary:", "We organise regulator-published information. We do not predict whether a medicine is safe, do not rank manufacturers by risk, and do not replace any regulatory decision.")

    heading(doc, "Why We Chose This Topic")
    script_block(doc, "Say this:", "We chose this topic because the underlying information is public and important, but difficult to use in its original document-centric form. The same organization or product may appear with spelling variants, abbreviations, changing addresses, different table layouts and different publication dates. A normal search page can retrieve a document, but it cannot reliably reconstruct entity histories with source evidence. This gave us a practical Data Engineering problem involving acquisition, PDF parsing, data quality, normalization, entity matching, database design and a user interface.")
    add_bullets(doc, [
        "It uses real public regulatory data, so provenance and responsible interpretation matter.",
        "It combines Data Engineering and Text Analytics rather than being only a frontend project.",
        "It has a clear demonstrable outcome: follow a source row into a searchable profile and official evidence.",
        "It has meaningful technical constraints: heterogeneous layouts, missing fields, naming variation and uncertain identity links.",
    ])
    script_block(doc, "If asked why not a simple website:", "The website is only the presentation layer. The main work is the pipeline behind it: preserving source documents, reconstructing rows from PDFs, retaining page and row evidence, applying normalization, generating matching candidates, recording review decisions and reproducing the same database state offline.")

    page_break(doc)
    heading(doc, "Problem Statement and Solution")
    add_table(doc, ["Problem in the source data", "What our implementation does"], [
        ["Records are spread across PDFs and a separate portal", "Uses a legacy PDF path and a validated portal snapshot path, then maps both into one record schema"],
        ["PDF tables use different layouts", "Uses category-specific parsers for Central NSQ, State NSQ, Spurious and Revised Alert records"],
        ["Names vary across sources", "Preserves raw text, creates normalized keys and produces cautious candidate matches"],
        ["One batch number can appear in different contexts", "Shows every product, organization and observed-site context instead of treating a batch string as globally unique"],
        ["Users need to verify a finding", "Displays source provenance, PDF page and row evidence, portal snapshot position and official links"],
    ], [2.55, 4.75])
    script_block(doc, "One sentence summary:", "The system turns selected fragmented official records into searchable, dated histories while preserving the evidence needed to inspect every displayed record.")

    heading(doc, "Architecture Explanation")
    script_block(doc, "Say this:", "The pipeline has seven layers. First, we acquire the official legacy index, PDFs and the public portal response. Second, we preserve the original files and calculate hashes. Third, we extract rows with layout-aware parsing. Fourth, we validate and store raw and parsed fields. Fifth, we normalize organization and product wording. Sixth, we create similarity proposals and apply only recorded evidence-backed review decisions. Finally, FastAPI and React expose search, histories, analytics and official source evidence.")
    add_text(doc, "Important wording", style="Heading 2", size=12, bold=True)
    add_bullets(doc, [
        "Say organization-name cluster, not legally verified company identity.",
        "Say product-wording cluster, not clinically interchangeable medicine.",
        "Say source row or regulatory record, not necessarily a unique real-world event.",
        "Say similarity score, not confidence probability.",
    ])

    page_break(doc)
    heading(doc, "Exact Live Demonstration Flow")
    add_text(doc, "Follow this route while presenting the running application. Keep the source evidence visible whenever you make a claim.", size=10.8)
    steps = [
        ("1. Overview", "Show the 599 source rows and nine official sources. State that the counts refer to the indexed corpus."),
        ("2. Legacy record", "Open an event from a PDF. Point out the raw wording, source page, row number, parse status and official PDF link."),
        ("3. Portal record", "Open a current portal record. Explain that it has reporting-month and snapshot-row provenance, because the portal response did not expose a stable official row identifier."),
        ("4. Martin and Brown", "Search Martin and Brown. Open the organization profile. Explain that it has 20 linked records across legacy PDFs and the portal. Show aliases, observed addresses and the source-review rationale."),
        ("5. Product profile", "Open a product profile. Explain that raw wording is retained and strengths/forms remain separate when the evidence differs."),
        ("6. TST2301", "Search TST2301. Show all five contexts. State that a batch string is not globally unique, so the application does not show a single invented batch identity."),
        ("7. Review queue", "Show unresolved suggestions. Explain that a high string score does not automatically create an entity link."),
        ("8. Analytics", "Show regulatory analytics separately from portal usage analytics. The latter is about our application, not CDSCO private website traffic."),
    ]
    add_table(doc, ["Step", "What to show and say"], steps, [1.3, 6.0])

    page_break(doc)
    heading(doc, "Model and Algorithm Selection")
    script_block(doc, "Direct answer:", "We did not select a trained neural model for the final pipeline. We selected a transparent, evidence-preserving engineering approach because the available labelled data was small, the documents had structured tables, and the project required explainable record links rather than only high similarity scores.")
    add_table(doc, ["Area", "What we evaluated or considered", "Final decision and reason"], [
        ["PDF extraction", "PyMuPDF plain text, PyMuPDF coordinates, pdfplumber words and pdfplumber tables", "Selected pdfplumber tables for row and cell reconstruction. Retained PyMuPDF coordinates as independent page evidence."],
        ["PDF OCR", "Considered only as a fallback", "Not used because all eight tested PDFs were machine-readable. No false claim is made about OCR quality on future scanned files."],
        ["Entity baseline", "Raw exact equality and normalized equality", "Retained normalized equality for deterministic clusters, but it misses spelling variants and omitted suffixes."],
        ["Entity proposals", "RapidFuzz character and token similarity", "Selected as an interpretable baseline. It produces candidates for review, not automatic legal identity decisions."],
        ["Embeddings", "SentenceTransformers and pgvector considered", "Not retained. We did not have a measured semantic benchmark proving a benefit, and semantic similarity alone can merge different formulations incorrectly."],
        ["Custom NER", "spaCy training considered", "Not trained. The tested source tables already expose target columns, while independent annotations are too limited for a validated learned NER model."],
        ["LLM extraction", "Considered as a flexible extraction approach", "Not used. Unverified generative output would make row-level provenance and reproducibility harder. It was not benchmarked in this project."],
        ["Graph database", "Neo4j considered", "Not selected. Explicit relational joins answer the required questions at this corpus size. Adding a graph database would not improve the validated core pipeline."],
    ], [1.2, 2.45, 3.65], small=True)

    page_break(doc)
    heading(doc, "How to Explain the Selected Algorithms")
    heading(doc, "Layout Aware PDF Extraction", level=2)
    script_block(doc, "Say this:", "Plain PDF text preserves words but often loses the visual column relationship. Our task needed rows and columns, so we benchmarked four extraction paths on the same eight PDFs. pdfplumber table extraction gave the most useful table geometry for the supported ruled layouts. PyMuPDF coordinate extraction was faster and remains useful as independent page evidence. Therefore we retained both rather than pretending one library solves every problem.")
    add_table(doc, ["Document category", "PyMuPDF text", "PyMuPDF coordinates", "pdfplumber tables", "Decision"], [
        ["Central NSQ", "148.8 ms", "30.7 ms", "1524.5 ms", "pdfplumber for rows; PyMuPDF coordinates for evidence"],
        ["State NSQ", "453.9 ms", "87.4 ms", "7280.1 ms", "pdfplumber for rows; PyMuPDF coordinates for evidence"],
        ["Spurious", "33.2 ms", "10.4 ms", "206.2 ms", "pdfplumber with continuation-row repair"],
        ["Revised Alert", "29.1 ms", "16.4 ms", "178.3 ms", "pdfplumber with revised parser route"],
    ], [1.25, 1.1, 1.35, 1.2, 2.4], small=True)
    add_text(doc, "State clearly: These are one-run local benchmark averages used for a relative comparison. They are not production throughput guarantees.", size=9.6, italic=True, color="444444")

    heading(doc, "RapidFuzz Candidate Matching", level=2)
    script_block(doc, "Say this:", "For entity matching, we first normalize harmless formatting variation, then block candidates using distinctive name tokens, prefixes and location terms. This avoids comparing every record with every other record. We calculate RapidFuzz ratio, weighted ratio, token sort ratio and token set ratio. Our aggregate score is 0.45 times weighted ratio plus 0.35 times token set ratio plus 0.20 times ratio. These are engineering weights, not calibrated probabilities.")
    script_block(doc, "Most important safeguard:", "A high RapidFuzz score creates a proposal. It does not automatically change an entity cluster. We require source evidence and an explicit recorded review decision before applying a fuzzy link to the deployed profiles.")
    add_bullets(doc, [
        "Manufacturer proposals use match and review thresholds of 96 and 86, plus address context.",
        "Product proposals use thresholds of 98 and 90, plus number, strength, dosage-form and pharmacopoeia compatibility checks.",
        "Conflicting strengths or forms block a product proposal even if generic words look similar.",
        "Blocks larger than 80 entries are skipped to avoid low-value comparisons from common terms.",
    ])

    page_break(doc)
    heading(doc, "Results You Can State")
    add_table(doc, ["Measurement", "Result", "How to explain it"], [
        ["Legacy extraction", "379 rows reproduced exactly", "Eight preserved PDFs produced 360 PARSED and 19 PARTIAL rows. Partial means useful content with a conservative normalization warning, often a date."],
        ["Unseen extraction subset", "11 of 11 rows reconstructed", "Manufacturer normalized accuracy was 81.8 percent. Other applicable fields reached 100 percent normalized match in this small primary-reviewed subset."],
        ["Manufacturer proposals", "Precision 1.000, recall 0.900, F1 0.947", "Twenty candidate-enriched binary pairs. This is proposal quality, not a population estimate."],
        ["Product proposals", "Precision 1.000, recall 0.500, F1 0.667", "Seventeen binary pairs. Strict formulation checks protect against false merges but reduce recall."],
        ["Applied entity reviews", "11 accepted and six rejected", "Every review stores hashes, raw source mentions, locations and rationale. They are primary source-text reviews, not independent human review."],
        ["History validation", "904 profiles ordered chronologically", "Histories sort by date, source, serial and record ID. Portal dates are month precision."],
    ], [1.6, 1.35, 4.6])
    script_block(doc, "Honest explanation of results:", "The results show that the selected method works on the bounded corpus and is inspectable. They do not prove archive-wide accuracy. The entity-pair sample is small and candidate-enriched, so we report its limitations instead of presenting it as a general national accuracy number.")

    heading(doc, "Why product recall is lower", level=2)
    script_block(doc, "Say this:", "We intentionally use strict product compatibility rules. A generic product name may look similar to a different strength or dosage form. In a regulatory setting, a false merge can create a misleading history. We therefore prefer leaving uncertain product variants unmerged for review. This lowers recall, especially in the held-out product proposal subset, but makes the displayed entity links more cautious.")

    page_break(doc)
    heading(doc, "Likely Viva Questions and Exact Answers")
    qa = [
        ("Why did you choose RapidFuzz?", "RapidFuzz gives transparent character and token similarity scores that suit spelling variations, missing corporate suffixes and word-order changes. We can display the raw mentions, the score and the review rationale. It is appropriate as a candidate generator, not as proof of identity."),
        ("Why did you not use an LLM?", "The task required reproducible row-level results and source provenance. We had structured PDF tables and limited independent labels. We did not benchmark an LLM against the selected method, so claiming it would be better would be unsupported. We chose a deterministic parser plus reviewable similarity pipeline for this bounded release."),
        ("Why did you not use BERT or SentenceTransformers?", "Embeddings can support semantic similarity, but semantic similarity does not prove that two formulations or organizations are identical. We did not have a measured benchmark showing a benefit for this corpus, so we did not add a model and vector infrastructure without evidence."),
        ("Why no custom spaCy NER model?", "The target fields are already represented as columns in the supported PDFs. Our main problem was reconstructing table rows, not detecting entity spans in free narrative text. The independent labelled set is too small to claim a reliable trained NER model."),
        ("Why use SQLite instead of PostgreSQL?", "SQLite makes the classroom demo self-contained and reproducible. The schema and migrations are compatible with PostgreSQL, but PostgreSQL and Docker execution are configured rather than tested. We state that distinction clearly."),
        ("Is this an AI project?", "It contains Text Analytics and record linkage, but the final pipeline is not a trained neural AI system. The main contribution is data engineering with interpretable matching. We use algorithms and evaluation rather than presenting a black-box model."),
        ("How do you prevent false entity links?", "We preserve raw text, use strength and form compatibility checks, distinguish equality from reviewed links, exclude placeholder manufacturers, keep high-score candidates unreviewed until evidence is recorded, and show all batch contexts."),
        ("How do you know the source is real?", "We preserve official source URLs and bytes, retain source metadata, page and row evidence where available, and calculate SHA-256 hashes. This proves consistency with the preserved source snapshot, not the truth of the regulator's underlying claim."),
        ("Why is a revised alert not linked to an original alert?", "We do not invent that relationship. The revised row is preserved and searchable, but an explicit original-to-revised relation needs verified supporting evidence and is future work."),
        ("What is the difference between a source row and an event?", "A source row is a publication record. A real-world event may appear in more than one snapshot or publication. We do not claim that every source row is a unique deduplicated real-world event."),
        ("What would you improve next?", "First, obtain independent human annotations and reviewer agreement. Then add broader months and layouts, evaluate on random and difficult negatives, review more fuzzy candidates, and validate PostgreSQL, Docker and HTTPS deployment."),
    ]
    for index, (q, a) in enumerate(qa):
        # Keep the final question and its answer together rather than leaving
        # a short orphaned answer at the top of the next printed page.
        if index == len(qa) - 1:
            page_break(doc)
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(4)
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run("Question: " + q)
        font(r, size=10.5, bold=True, color=NAVY)
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.17)
        p.paragraph_format.space_after = Pt(5)
        r = p.add_run("Answer: " + a)
        font(r, size=10.3)

    heading(doc, "What Not to Say")
    add_table(doc, ["Avoid saying", "Say this instead"], [
        ["We have complete CDSCO data", "We have a bounded indexed corpus of eight PDFs and one portal snapshot."],
        ["The score means 96 percent confidence", "The score is an interpretable string-similarity score and is not a calibrated probability."],
        ["These are verified companies or factories", "These are organization-name clusters with observed source addresses, not legal identity verification."],
        ["Every same batch number is the same batch", "Batch strings require product, organization and observed-site context. TST2301 has five contexts."],
        ["Our accuracy is 100 percent", "Some regression fixtures agree fully with the current parser, but the unseen 11-row manufacturer metric is 81.8 percent and needs independent review."],
        ["We tested BERT, LLMs or embeddings", "We considered those approaches but did not benchmark or retain them in the final pipeline."],
        ["The project tells whether a medicine is unsafe", "The project organizes official regulatory findings and does not provide medical advice or a new safety verdict."],
    ], [3.05, 4.5])

    heading(doc, "Closing Script")
    script_block(doc, "Say this:", "To conclude, our contribution is a working, evidence-preserving data pipeline for selected fragmented CDSCO records. We show how an official source row becomes a structured record, then a cautious entity history that a user can inspect back to the source. The project is complete as a bounded local academic demonstration. The next validation work is independent human review, broader coverage and deployment testing, not adding unmeasured models.")

    heading(doc, "Preparation Checklist", level=2)
    add_bullets(doc, [
        "Start the backend and frontend before the viva and open the Overview page.",
        "Keep the PPT, the final Word report and this guide available locally.",
        "Practise the one-minute opening, Martin and Brown example, TST2301 example and model-selection answer.",
        "When unsure, return to source evidence and state the limitation honestly.",
        "Do not call a similarity proposal a confirmed match unless the profile shows a recorded source review decision.",
    ])

    heading(doc, "Evidence Used in This Guide", level=2)
    add_text(doc, "Project evidence: final implementation report, extraction benchmark, row extraction evaluation, entity resolution methodology, entity resolution evaluation, final stabilization record and release verification file. Library capability references: RapidFuzz documentation, PyMuPDF documentation, pdfplumber documentation, SentenceTransformers documentation and spaCy training documentation. All project performance figures in this guide come from the preserved local project evidence.", size=9.2, color="444444")

    doc.core_properties.title = "CDSCO Viva Presentation Guide"
    doc.core_properties.subject = "Viva speaking notes and model selection guidance"
    doc.core_properties.author = "Group 01"
    doc.save(OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    build()
