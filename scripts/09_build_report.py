"""Stage 9: build the report (Word file from the course template, Markdown copy).

The Word file keeps the template's styles (title: Heading 1, sections:
Heading 3) and applies the course page rules: A4, 3 cm margins, 12 pt Times,
single line spacing. The same blocks are also written as a print-ready HTML
file with identical page rules, which ``scripts/10_export_pdf.sh`` prints to PDF.
"""
import _bootstrap  # noqa: F401
import json
import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

from batnet import config
from batnet.logutil import get_logger

sys.path.insert(0, str(config.ROOT / "report"))
import content  # noqa: E402

log = get_logger("09_report")
TEMPLATE = config.ROOT / "docs" / "reference" / "Network_Analysis_Project_Template.docx"
REPORT_DIR = config.ROOT / "report"
FONT = "Times New Roman"
WORD_LIMIT = 5000


def set_font(run, size: float, bold: bool = False, italic: bool = False) -> None:
    run.font.name = FONT
    run._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic


def para(doc, text: str, size: float = 12, style: str = "Normal", align=WD_ALIGN_PARAGRAPH.JUSTIFY,
         after: float = 6, italic: bool = False, lead_bold: bool = True):
    """Paragraph; a leading 'Label.' or 'Label (RQx).' phrase is set in bold."""
    p = doc.add_paragraph(style=style)
    p.alignment = align
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    m = re.match(r"^((?:Table|Figure) \d+\.|[A-Z][A-Za-z ,\-]{2,60}?(?: \(RQ[\d, RQ]+\))?\.) ", text) if lead_bold else None
    if m and (len(m.group(1).split()) <= 3 or "(RQ" in m.group(1)):
        set_font(p.add_run(m.group(1) + " "), size, bold=True, italic=italic)
        text = text[m.end():]
    set_font(p.add_run(text), size, italic=italic)
    return p


def borders(table) -> None:
    """Horizontal rules only: top, header bottom, table bottom."""
    tbl_pr = table._tbl.tblPr
    el = OxmlElement("w:tblBorders")
    for edge in ("top", "bottom", "insideH"):
        b = OxmlElement(f"w:{edge}")
        b.set(qn("w:val"), "single"); b.set(qn("w:sz"), "4" if edge != "insideH" else "2")
        b.set(qn("w:color"), "7F7F7F" if edge != "insideH" else "D9D9D9")
        el.append(b)
    tbl_pr.append(el)


def add_table(doc, caption: str, header: list[str], rows: list[list[str]]) -> None:
    para(doc, caption, size=10, align=WD_ALIGN_PARAGRAPH.LEFT, after=3)
    t = doc.add_table(rows=1 + len(rows), cols=len(header))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    borders(t)
    wide = max(len(str(x)) for r in rows for x in r[1:]) > 30
    size = 8 if wide else 9.5
    for i, row in enumerate([header] + rows):
        for j, text in enumerate(row):
            cell = t.cell(i, j)
            cp = cell.paragraphs[0]
            cp.paragraph_format.space_after = Pt(1)
            cp.paragraph_format.line_spacing = 1.0
            cp.alignment = WD_ALIGN_PARAGRAPH.LEFT if (j == 0 or wide) else WD_ALIGN_PARAGRAPH.RIGHT
            set_font(cp.add_run(str(text)), size, bold=(i == 0))
    if wide:
        for row in t.rows:
            row.cells[0].width = Cm(2.2)
            for cell in row.cells[1:]:
                cell.width = Cm(4.3)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)


def build_docx(blocks: list[tuple], meta: dict, out: Path) -> None:
    doc = Document(TEMPLATE)
    body = doc.element.body
    for el in list(body):
        if el.tag != qn("w:sectPr"):
            body.remove(el)
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
    sec.left_margin = sec.right_margin = sec.top_margin = sec.bottom_margin = Cm(3)
    normal = doc.styles["Normal"]
    normal.font.name, normal.font.size = FONT, Pt(12)
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)

    title = doc.add_paragraph(style="Heading 1")
    set_font(title.add_run(meta["title"]), 16, bold=True)
    for a in meta["authors"]:
        para(doc, a, after=0, align=WD_ALIGN_PARAGRAPH.LEFT, lead_bold=False)
    for kind, *rest in blocks:
        if kind == "h":
            hd = doc.add_paragraph(style="Heading 3")
            set_font(hd.add_run(rest[0]), 13, bold=True)
        elif kind == "p":
            para(doc, rest[0])
        elif kind == "ref":
            para(doc, rest[0], size=10, after=2, align=WD_ALIGN_PARAGRAPH.LEFT, lead_bold=False)
        elif kind == "table":
            add_table(doc, *rest)
        elif kind == "fig":
            fp = doc.add_paragraph()
            fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            fp.paragraph_format.space_after = Pt(2)
            fp.add_run().add_picture(str(rest[0]), width=Cm(15))
            para(doc, rest[1], size=10, after=8)
    doc.save(out)


def build_markdown(blocks: list[tuple], meta: dict, out: Path) -> str:
    lines = [f"# {meta['title']}", ""] + [f"{a}  " for a in meta["authors"]] + [""]
    for kind, *rest in blocks:
        if kind == "h":
            lines += [f"## {rest[0]}", ""]
        elif kind in ("p", "ref"):
            lines += [rest[0], ""]
        elif kind == "table":
            cap, header, rows = rest
            lines += [f"**{cap}**", "", "| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
            lines += ["| " + " | ".join(map(str, r)) + " |" for r in rows] + [""]
        elif kind == "fig":
            lines += [f"![{rest[1][:9]}](../{Path(rest[0]).relative_to(config.ROOT).as_posix()})", "", f"*{rest[1]}*", ""]
    text = "\n".join(lines)
    out.write_text(text, encoding="utf-8")
    return text


HTML_CSS = """
@page { size: A4; margin: 3cm; }
body { font-family: 'Times New Roman', Times, serif; font-size: 12pt; line-height: 1.0; margin: 0; color: #000; }
h1 { font-size: 16pt; margin: 0 0 8pt 0; }
h3 { font-size: 13pt; margin: 12pt 0 4pt 0; break-after: avoid; }
p { margin: 0 0 6pt 0; text-align: justify; }
p.author { margin: 0; text-align: left; }
p.caption { font-size: 10pt; text-align: left; margin: 6pt 0 3pt 0; break-after: avoid; }
p.figcap { font-size: 10pt; margin: 2pt 0 8pt 0; }
p.ref { font-size: 10pt; text-align: left; margin: 0 0 2pt 0; }
table { border-collapse: collapse; width: 100%; margin: 0 0 8pt 0; font-size: 9.5pt; break-inside: avoid;
        border-top: 1px solid #7f7f7f; border-bottom: 1px solid #7f7f7f; }
table.wide { font-size: 8pt; }
th, td { padding: 1.5pt 4pt; text-align: right; vertical-align: top; border-bottom: 0.5px solid #d9d9d9; }
th:first-child, td:first-child, table.wide th, table.wide td { text-align: left; }
th { border-bottom: 1px solid #7f7f7f; }
figure { margin: 6pt 0 0 0; break-inside: avoid; }
img { width: 100%; }
.pb { break-before: page; }
"""


def build_html(blocks: list[tuple], meta: dict, out: Path) -> None:
    """Print-ready HTML with the same page rules as the Word file."""
    from html import escape as e

    def lead(text: str) -> str:
        m = re.match(r"^((?:Table|Figure) \d+\.|[A-Z][A-Za-z ,\-]{2,60}?(?: \(RQ[\d, RQ]+\))?\.) ", text)
        if m and (len(m.group(1).split()) <= 3 or "(RQ" in m.group(1)):
            return f"<b>{e(m.group(1))}</b> {e(text[m.end():])}"
        return e(text)

    parts = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'><title>{e(meta['title'])}</title>"
             f"<style>{HTML_CSS}</style></head><body>", f"<h1>{e(meta['title'])}</h1>"]
    parts += [f"<p class='author'>{e(a)}</p>" for a in meta["authors"]]
    for kind, *rest in blocks:
        if kind == "h":
            parts.append(f"<h3>{e(rest[0])}</h3>")
        elif kind == "p":
            parts.append(f"<p>{lead(rest[0])}</p>")
        elif kind == "ref":
            parts.append(f"<p class='ref'>{e(rest[0])}</p>")
        elif kind == "table":
            cap, header, rows = rest
            wide = max(len(str(x)) for r in rows for x in r[1:]) > 30
            parts.append(f"<p class='caption'>{lead(cap)}</p><table class='{'wide' if wide else ''}'><tr>"
                         + "".join(f"<th>{e(h)}</th>" for h in header) + "</tr>"
                         + "".join("<tr>" + "".join(f"<td>{e(str(x))}</td>" for x in r) + "</tr>" for r in rows)
                         + "</table>")
        elif kind == "fig":
            parts.append(f"<figure><img src='{Path(rest[0]).resolve().as_uri()}'></figure>"
                         f"<p class='figcap'>{lead(rest[1])}</p>")
    parts.append("</body></html>")
    out.write_text("\n".join(parts), encoding="utf-8")


def word_count(blocks: list[tuple], meta: dict) -> int:
    """Words in title, authors, headings, paragraphs, captions, tables and references."""
    parts = [meta["title"]] + meta["authors"]
    for kind, *rest in blocks:
        if kind in ("h", "p", "ref"):
            parts.append(rest[0])
        elif kind == "table":
            parts += [rest[0]] + rest[1] + [str(x) for r in rest[2] for x in r]
        elif kind == "fig":
            parts.append(rest[1])
    return len(" ".join(parts).split())


def main() -> int:
    meta = json.loads((REPORT_DIR / "authors.json").read_text(encoding="utf-8"))
    blocks = content.build(content.Ctx())
    build_docx(blocks, meta, REPORT_DIR / "report.docx")
    build_markdown(blocks, meta, REPORT_DIR / "report.md")
    build_html(blocks, meta, REPORT_DIR / "report.html")
    n = word_count(blocks, meta)
    log.info("report written: %d words (limit %d) - %s", n, WORD_LIMIT, "OK" if n <= WORD_LIMIT else "TOO LONG")
    return 0 if n <= WORD_LIMIT else 1


if __name__ == "__main__":
    sys.exit(main())
