from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / 'docs' / 'viva' / 'CDSCO_Workflow_Demonstration_Script.docx'
NAVY = '18334D'
RED = 'A52835'
PALE = 'F1F4F6'

def shade(cell, color):
    pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd'); shd.set(qn('w:fill'), color); pr.append(shd)

def set_font(run, size=10.5, bold=False, color='20262C', italic=False):
    run.font.name = 'Aptos'; run.font.size = Pt(size); run.bold = bold; run.italic = italic
    run.font.color.rgb = RGBColor.from_string(color)

def para(doc, text='', bold_lead=None, style=None):
    p = doc.add_paragraph(style=style)
    if bold_lead and text.startswith(bold_lead):
        set_font(p.add_run(bold_lead), bold=True, color=RED)
        set_font(p.add_run(text[len(bold_lead):]))
    else:
        set_font(p.add_run(text))
    p.paragraph_format.space_after = Pt(6)
    return p

def heading(doc, text, level=1):
    p = doc.add_paragraph(style=f'Heading {level}')
    r = p.add_run(text); set_font(r, 16 if level == 1 else 12.5, True, NAVY)
    p.paragraph_format.space_before = Pt(12); p.paragraph_format.space_after = Pt(5)
    return p

def say(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(.22); p.paragraph_format.right_indent = Inches(.12)
    p.paragraph_format.space_before = Pt(3); p.paragraph_format.space_after = Pt(9)
    set_font(p.add_run('SAY  '), 9, True, RED)
    set_font(p.add_run('“' + text + '”'), 10.5)

def do(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(.22); p.paragraph_format.space_after = Pt(4)
    set_font(p.add_run('DO  '), 9, True, NAVY); set_font(p.add_run(text), 10)

def table(doc, headers, rows):
    t = doc.add_table(rows=1, cols=len(headers)); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    t.style = 'Table Grid'
    for i, h in enumerate(headers):
        c=t.rows[0].cells[i]; c.text=h; shade(c,NAVY)
        for r in c.paragraphs[0].runs: set_font(r,9.5,True,'FFFFFF')
    for row in rows:
        cells=t.add_row().cells
        for i, value in enumerate(row):
            cells[i].text=value; cells[i].vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if len(t.rows)%2==0: shade(cells[i],PALE)
            for p in cells[i].paragraphs:
                p.paragraph_format.space_after=Pt(2)
                for r in p.runs: set_font(r,9.4)
    return t

def main():
    doc=Document(); sec=doc.sections[0]
    sec.top_margin=Inches(.68); sec.bottom_margin=Inches(.68); sec.left_margin=Inches(.78); sec.right_margin=Inches(.78)
    normal=doc.styles['Normal']; normal.font.name='Aptos'; normal.font.size=Pt(10.5)
    title=doc.styles['Title']; title.font.name='Aptos Display'; title.font.size=Pt(25); title.font.bold=True; title.font.color.rgb=RGBColor(0,0,0)
    p=doc.add_paragraph(style='Title'); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run('CDSCO Workflow Demonstration Script')
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; set_font(p.add_run('A click-by-click presentation script with words to say'),12,False,NAVY)
    heading(doc,'How to use this script')
    para(doc,'Keep this document beside you while presenting. Follow the numbered steps in order. The DO line tells you where to click; the SAY block is the exact wording to speak. Read the short transition only after the page is visible. If something takes time to load, use the waiting line in the recovery section rather than filling the silence or guessing.')
    para(doc,'The demo is designed for about 7 to 9 minutes. It shows the path from the indexed corpus to an official source, then demonstrates why entity histories and review are useful. Counts describe the saved project corpus and may change if the local database has been refreshed.')
    heading(doc,'Before the presentation')
    table(doc,['Check','What to do'],[
        ['Start the application','Start the backend and frontend using the project README instructions. Open the local site and wait for Overview to finish loading.'],
        ['Keep pages ready','Have the presentation deck and this script available. Do not pre-open a page that you cannot explain.'],
        ['Know the demo searches','Use “Martin and Brown” for the organization profile and “TST2301” for the batch-context example.'],
        ['Check the network','The application is a local demo. Internet access may be needed only when opening an official source link.'],
        ['If a count differs','Use the count currently displayed and call it the indexed corpus. Do not claim complete CDSCO coverage.']])
    heading(doc,'Opening and purpose')
    do(doc,'Start on the Overview page. Point to the title, corpus coverage and latest-record area. Do not click Search in the sidebar; it has been removed as a duplicate entry.')
    say(doc,'Good morning, ma’am. I will demonstrate our CDSCO Regulatory Intelligence project. It organizes selected regulatory records from official CDSCO sources into searchable records and entity histories, while keeping the source evidence visible so that a user can check where each item came from.')
    say(doc,'The challenge is that relevant information is published across different PDFs and a public portal. A person can open each publication separately, but following the same product or manufacturer across different names, layouts and dates is difficult. Our workflow collects a bounded set of source records, reconstructs their fields, and links the displayed information back to its source.')
    say(doc,'This is an academic demonstration over an indexed corpus. It does not represent complete CDSCO coverage, make a new safety judgment, or provide medical advice.')
    heading(doc,'Step 1  Overview')
    do(doc,'Show the corpus summary and the latest regulatory records. Point to the source or coverage figures that are currently visible.')
    say(doc,'This is the overview. The figures summarize the records and sources currently indexed in this local project. Each row represents information captured from a source publication. The overview helps a user see what is available, but the record detail and source link are where the evidence should be checked.')
    say(doc,'The purpose is traceability: a user can move from a summary to a particular record and then to the official publication that supports it.')
    heading(doc,'Step 2  Open a regulatory record')
    do(doc,'Click one visible record in the latest-records table. Choose a legacy PDF record if available. Point out finding, product, batch, manufacturer, parse status and provenance fields.')
    say(doc,'I am opening one regulatory record. The page shows the extracted fields alongside the source information. The displayed finding is the wording captured from the regulator’s publication; the application is organizing that information, not independently testing the medicine or issuing a regulatory conclusion.')
    say(doc,'For this record, the provenance panel identifies the source document and the page and row evidence where available. The official source link lets the user check the original publication. If a field is missing or uncertain in the source, we preserve that limitation instead of filling it with an assumption.')
    do(doc,'If a PDF page and row are shown, point to them. If this is a portal record, point to its reporting month and snapshot-row reference instead.')
    say(doc,'The legacy PDF records retain page and row evidence. The portal snapshot uses its available publication context and snapshot-row position. This distinction matters because the portal did not provide a stable official row identifier in the captured response.')
    heading(doc,'Step 3  Show the official source')
    do(doc,'Point to the official PDF or source link. Open it only if the connection is available and doing so will not interrupt the demo. Otherwise leave the link visible.')
    say(doc,'This is the source-provenance step. The record is not presented as unsupported text: it is connected to the preserved source and the location from which the row was reconstructed. A hash helps verify that the preserved file has not changed since it was collected; it does not prove the truth of the regulator’s underlying statement.')
    heading(doc,'Step 4  Search for an organization')
    do(doc,'Use Entity Search in the sidebar. Enter “Martin and Brown” and open the matching organization profile. If no exact result appears, use the profile listed in the demo data or return to Overview and use its record link.')
    say(doc,'Now I will move from a source row to an organization profile. Entity Search helps find a grouped profile and its linked records. This is different from opening one record: the profile brings together source mentions that have been connected through the project’s documented review process.')
    say(doc,'Here we can inspect the organization name, observed aliases, addresses and linked records. The aliases and addresses are evidence about how names appear in the indexed sources. This profile is an organization-name cluster; it is not legal verification that every mention belongs to one registered company or one factory.')
    do(doc,'Point out the linked records and any alias or review rationale visible on the profile. Avoid describing an unreviewed candidate as a confirmed link.')
    say(doc,'The linked history lets us follow how this organization name appears across the selected publications. Where a link is uncertain, the system keeps it in the review workflow instead of silently treating a similarity score as proof.')
    heading(doc,'Step 5  Show the entity review queue')
    do(doc,'Navigate back to the sidebar and open the entity review queue. Show a proposed pair and its evidence or status, but do not accept or reject anything during the presentation.')
    say(doc,'This is the entity review queue. The system generates candidate matches when source names look similar. A reviewer examines the raw names and available context, then records whether the proposed connection should be accepted or rejected. Until a decision is recorded, a suggestion remains unreviewed and does not become a confirmed profile link.')
    say(doc,'The review is about identity links between source mentions. It does not change the regulatory finding in the source record. Keeping this step explicit helps reduce incorrect merges, which could otherwise create a misleading history.')
    heading(doc,'Step 6  Show a product profile')
    do(doc,'Return to Entity Search, search for a product name already shown in the project, and open the corresponding product profile. Point out its linked records and preserved source wording.')
    say(doc,'This is a product profile. Similar product wording can be grouped to make related records easier to find, while the original wording remains available for inspection. Strength, dosage form and other meaningful details matter, so similar names are not automatically treated as clinically interchangeable products.')
    heading(doc,'Step 7  Demonstrate batch context')
    do(doc,'Search for batch “TST2301” and open the batch view or result showing its contexts. Point out the separate product, organization or source contexts.')
    say(doc,'This example shows why a batch number alone is not enough to establish identity. The same batch string can appear in multiple product or manufacturer contexts. The application shows those contexts so users can compare the source evidence instead of assuming that every matching string refers to one globally unique batch.')
    heading(doc,'Step 8  Show regulatory history')
    do(doc,'Open Timeline from the sidebar. Point to chronological ordering and the source references attached to entries.')
    say(doc,'The timeline presents indexed records in date order so a user can follow the published history. The timeline is built from the available source dates and publication context. A source row is a publication record; it is not necessarily a unique real-world event after deduplication.')
    heading(doc,'Step 9  Show analytics')
    do(doc,'Open Analytics. Point to the event or record distribution and any chart. Mention that counts come from the indexed corpus.')
    say(doc,'The analytics page summarizes the records that this project has indexed, such as their distribution by category or time. These charts describe this corpus. They do not measure private CDSCO website traffic, national medicine quality, or the risk of a particular manufacturer.')
    heading(doc,'Step 10  Close on Sources')
    do(doc,'Open Sources and point to the listed source documents, snapshot information and available hashes or retrieval details.')
    say(doc,'The Sources page provides the source inventory behind the records. The project preserves source metadata and file hashes so that the collected material and extraction history can be inspected. This closes the workflow from an indexed summary back to its supporting source.')
    heading(doc,'Closing statement')
    say(doc,'To conclude, our demonstration has followed the workflow from the indexed corpus to a regulatory record, its official source, an organization and product history, a batch context, and the review and analytics pages. The main contribution is a traceable data workflow for selected fragmented CDSCO records. Its scope is bounded, and the next step for stronger entity evaluation is broader independent review of the proposed links. Thank you, ma’am. I am ready for your questions.')
    heading(doc,'If something does not work during the demo')
    table(doc,['Situation','Say this, then do this'],[
        ['A page is loading','“This page is retrieving the indexed project data. I will give it a moment to load.” Wait briefly. If it remains blank, return to Overview and continue to the next prepared page.'],
        ['A search returns no result','“This query did not return a match in the current indexed corpus.” Clear the query and use the demonstrated Martin and Brown or TST2301 example.'],
        ['The official website is unavailable','“The external official site is not responding at the moment. The application still shows the preserved source reference and provenance for this record.” Continue without repeatedly refreshing.'],
        ['A displayed count differs','“This number reflects the current local indexed corpus.” Read the screen’s current value and continue.'],
        ['You lose your place','Return to Overview, then resume at the next numbered step. The workflow order is Overview, record, source, organization, review, product, batch, timeline, analytics, sources.'],
        ['You are unsure of a technical answer','“I want to answer that accurately. The evidence visible in this record is [name the source evidence]. I can distinguish that from the parts that remain future validation.” Do not guess.']])
    doc.add_page_break()
    heading(doc,'Presentation guardrails')
    table(doc,['Do not say','Say this instead'],[
        ['We have all CDSCO data','We have a bounded indexed corpus of selected PDFs and a public portal snapshot.'],
        ['The system proves these are the same company','The profile groups source mentions using documented review evidence; it is not legal identity verification.'],
        ['The similarity score is a confidence percentage','It is a string-similarity score used to propose candidates, not a calibrated probability.'],
        ['The project decides whether a medicine is unsafe','The project organizes regulator-published findings and preserves their sources.'],
        ['Every repeated batch number is the same batch','The application shows batch strings with their source, product and organization contexts.'],
        ['The source hash proves the alert is true','The hash helps verify the integrity of the preserved file; the official source supports the published statement.']])
    heading(doc,'One-line workflow to remember')
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    set_font(p.add_run('Overview  →  Record  →  Official source  →  Organization  →  Review  →  Product  →  Batch  →  Timeline  →  Analytics  →  Sources'),11,True,NAVY)
    footer=sec.footer.paragraphs[0]; footer.alignment=WD_ALIGN_PARAGRAPH.CENTER
    set_font(footer.add_run('CDSCO Regulatory Intelligence  |  Demonstration Script'),8.5,False,'66727D')
    OUT.parent.mkdir(parents=True,exist_ok=True); doc.save(OUT); print(OUT)

if __name__ == '__main__': main()
