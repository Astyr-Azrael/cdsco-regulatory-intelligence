"""Create the academic Word report from the repository final written report."""
from __future__ import annotations
import re
from pathlib import Path
from docx import Document
from docx.shared import Inches,Pt,RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT,WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"docs/project-report/final-report.md"
OUTPUT=ROOT/"docs/project-report/CDSCO_Implementation_and_Method_Selection_Report.docx"

def text(s):
    return s.replace("**","").replace(chr(96),"").strip()

def table(doc,lines):
    data=[[text(c) for c in line.strip().strip("|").split("|")] for line in lines]
    data=[r for r in data if not all(re.fullmatch(r"[-: ]+",c or "-") for c in r)]
    columns=len(data[0])
    t=doc.add_table(rows=0,cols=columns)
    t.alignment=WD_TABLE_ALIGNMENT.CENTER
    t.autofit=False
    total=6.95
    widths=([4.6,2.35] if columns==2 else [1.4,2.55,3.0] if columns==3 else [3.45]+[(total-3.45)/(columns-1)]*(columns-1))
    if columns==5: widths=[2.35,1.15,1.15,1.15,1.15]
    if columns==3 and data[0][0]=="Method": widths=[2.05,2.15,2.75]
    for col,w in zip(t.columns,widths): col.width=Inches(w)
    for index,row in enumerate(data):
        cells=t.add_row().cells
        for j,value in enumerate(row):
            cell=cells[j];cell.width=Inches(widths[j])
            cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
            tcpr=cell._tc.get_or_add_tcPr()
            shading=OxmlElement("w:shd");shading.set(qn("w:fill"),"23384D" if index==0 else ("F2F5F7" if index%2==0 else "FFFFFF"));tcpr.append(shading)
            margin=OxmlElement("w:tcMar")
            for side in ("top","left","bottom","right"):
                el=OxmlElement("w:"+side);el.set(qn("w:w"),"95");el.set(qn("w:type"),"dxa");margin.append(el)
            tcpr.append(margin)
            p=cell.paragraphs[0];p.paragraph_format.space_after=Pt(0);p.paragraph_format.line_spacing=1.05
            p.alignment=WD_ALIGN_PARAGRAPH.LEFT if j==0 or columns==3 else WD_ALIGN_PARAGRAPH.CENTER
            run=p.add_run(value);run.font.size=Pt(10.5 if columns<5 else 10)
            run.bold=index==0;run.font.color.rgb=RGBColor.from_string("FFFFFF" if index==0 else "000000")
        trpr=t.rows[-1]._tr.get_or_add_trPr()
        trpr.append(OxmlElement("w:cantSplit"))
        if index==0: trpr.append(OxmlElement("w:tblHeader"))
    borders=OxmlElement("w:tblBorders")
    for name in ("top","left","bottom","right","insideH","insideV"):
        b=OxmlElement("w:"+name);b.set(qn("w:val"),"single");b.set(qn("w:sz"),"5");b.set(qn("w:color"),"D9D9D9");borders.append(b)
    t._tbl.tblPr.append(borders)
    after=doc.add_paragraph();after.paragraph_format.space_after=Pt(2);after.paragraph_format.space_before=Pt(0);after.paragraph_format.line_spacing=Pt(3)

def main():
    doc=Document()
    section=doc.sections[0]
    section.page_width=Inches(8.5);section.page_height=Inches(11)
    section.top_margin=section.bottom_margin=Inches(.7)
    section.left_margin=section.right_margin=Inches(.775)
    for name in ("Normal","Title","Subtitle","Heading 1","Heading 2","Heading 3"):
        style=doc.styles[name];style.font.name="Calibri";style.font.color.rgb=RGBColor(0,0,0)
        style.paragraph_format.widow_control=True
    normal=doc.styles["Normal"];normal.font.size=Pt(11)
    normal.paragraph_format.line_spacing=1.1
    normal.paragraph_format.space_after=Pt(7)
    doc.styles["Title"].font.size=Pt(26);doc.styles["Title"].paragraph_format.space_after=Pt(14)
    doc.styles["Heading 1"].font.size=Pt(18);doc.styles["Heading 1"].paragraph_format.space_after=Pt(10)
    doc.styles["Heading 2"].font.size=Pt(12.5);doc.styles["Heading 2"].paragraph_format.space_before=Pt(8)
    doc.styles["Heading 2"].paragraph_format.space_after=Pt(5)
    footer=section.footer.paragraphs[0];footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
    run=footer.add_run("CDSCO Regulatory Intelligence   |   ");run.font.size=Pt(8)
    field=OxmlElement("w:fldSimple");field.set(qn("w:instr"),"PAGE");footer._p.append(field)
    doc.core_properties.title="CDSCO Regulatory Intelligence Implementation and Method Selection"
    doc.core_properties.subject="Achievements architecture methods evaluation and demonstration"
    doc.core_properties.author="CDSCO Regulatory Intelligence Project"
    lines=SOURCE.read_text(encoding="utf-8").splitlines()
    first=True;i=0
    while i<len(lines):
        line=lines[i].strip()
        if line=="<!-- page -->": doc.add_page_break()
        elif line.startswith("|"):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith("|"):
                rows.append(lines[i]);i+=1
            table(doc,rows);continue
        elif line.startswith("# "):
            doc.add_paragraph(text(line[2:]),style="Title" if first else "Heading 1");first=False
        elif line.startswith("## "): doc.add_paragraph(text(line[3:]),style="Heading 2")
        elif re.match(r"^\d+\.\s",line):
            p=doc.add_paragraph(text(line),style="Normal");p.paragraph_format.left_indent=Inches(.15)
        elif line:
            p=doc.add_paragraph(text(line))
            if line.startswith("http") or line.startswith("["): p.paragraph_format.space_after=Pt(5)
        i+=1
    # Word's default template can carry a blue Title paragraph border.
    for root in (doc.styles.element,doc.element):
        for border in list(root.iter(qn("w:pBdr"))):
            border.getparent().remove(border)
    doc.save(OUTPUT)
    print(OUTPUT)

if __name__=="__main__":main()
