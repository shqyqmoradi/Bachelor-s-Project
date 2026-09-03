from __future__ import annotations

import argparse
import re
from html import escape
from pathlib import Path

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    Image,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "report" / "final_report_fa.md"
DEFAULT_OUTPUT = ROOT / "report" / "final-project-report-fa.pdf"

NAVY = colors.HexColor("#0C3D57")
TEAL = colors.HexColor("#008A9A")
BLUE = colors.HexColor("#185A96")
TEXT = colors.HexColor("#1C2D3F")
MUTED = colors.HexColor("#5C7283")
LIGHT = colors.HexColor("#EFF5F8")
GREEN_BG = colors.HexColor("#EEF8F2")
GREEN_BORDER = colors.HexColor("#5C9E78")


def find_font(bold: bool = False) -> str:
    regular = (
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
    )
    bold_candidates = (
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansArabic-Bold.ttf",
    )
    for candidate in bold_candidates if bold else regular:
        if Path(candidate).exists():
            return candidate
    raise FileNotFoundError("No Persian-capable TrueType font was found")


pdfmetrics.registerFont(TTFont("ReportFont", find_font()))
pdfmetrics.registerFont(TTFont("ReportFont-Bold", find_font(bold=True)))


def rtl(value: str) -> str:
    return get_display(arabic_reshaper.reshape(value))


def paragraph(value: str, style: ParagraphStyle) -> Paragraph:
    cleaned = value.replace("`", "")
    return Paragraph(rtl(escape(cleaned)), style)


base_styles = getSampleStyleSheet()
BODY = ParagraphStyle(
    "body",
    parent=base_styles["Normal"],
    fontName="ReportFont",
    fontSize=10.2,
    leading=18,
    textColor=TEXT,
    alignment=TA_RIGHT,
    spaceAfter=5,
)
BULLET = ParagraphStyle("bullet", parent=BODY, leftIndent=15, firstLineIndent=-10, spaceAfter=2)
H1 = ParagraphStyle(
    "h1",
    parent=BODY,
    fontName="ReportFont-Bold",
    fontSize=18,
    leading=24,
    textColor=NAVY,
    alignment=TA_RIGHT,
    spaceBefore=7,
    spaceAfter=9,
)
H2 = ParagraphStyle(
    "h2",
    parent=BODY,
    fontName="ReportFont-Bold",
    fontSize=14,
    leading=20,
    textColor=TEAL,
    alignment=TA_RIGHT,
    spaceBefore=8,
    spaceAfter=5,
)
H3 = ParagraphStyle(
    "h3",
    parent=BODY,
    fontName="ReportFont-Bold",
    fontSize=12,
    leading=18,
    textColor=BLUE,
    alignment=TA_RIGHT,
    spaceBefore=5,
    spaceAfter=3,
)
CODE = ParagraphStyle(
    "code",
    parent=BODY,
    fontName="Courier",
    fontSize=8.4,
    leading=12,
    alignment=TA_LEFT,
    leftIndent=10,
    rightIndent=10,
    backColor=colors.HexColor("#F2F5F7"),
    borderColor=colors.HexColor("#CAD6DE"),
    borderWidth=0.5,
    borderPadding=6,
    spaceBefore=4,
    spaceAfter=7,
)
TABLE_CELL = ParagraphStyle("table-cell", parent=BODY, fontSize=8.4, leading=12, spaceAfter=0)
TABLE_HEADER = ParagraphStyle(
    "table-header",
    parent=TABLE_CELL,
    fontName="ReportFont-Bold",
    textColor=colors.white,
)
COVER_TITLE = ParagraphStyle(
    "cover-title",
    parent=BODY,
    fontName="ReportFont-Bold",
    fontSize=27,
    leading=36,
    textColor=NAVY,
    alignment=TA_CENTER,
    spaceAfter=20,
)
COVER_SUBTITLE = ParagraphStyle(
    "cover-subtitle",
    parent=BODY,
    fontSize=14,
    leading=24,
    textColor=TEAL,
    alignment=TA_CENTER,
    spaceAfter=28,
)
COVER_META = ParagraphStyle(
    "cover-meta",
    parent=BODY,
    fontSize=10.5,
    leading=19,
    textColor=colors.white,
    alignment=TA_CENTER,
)
CALLOUT = ParagraphStyle(
    "callout",
    parent=BODY,
    textColor=colors.HexColor("#265C44"),
    alignment=TA_RIGHT,
    fontSize=10.3,
    leading=18,
)
CAPTION = ParagraphStyle(
    "caption",
    parent=BODY,
    fontSize=8.7,
    leading=13,
    textColor=MUTED,
    alignment=TA_CENTER,
    spaceBefore=3,
    spaceAfter=8,
)


def footer(canvas: Canvas, document) -> None:
    canvas.saveState()
    width, _ = A4
    canvas.setStrokeColor(colors.HexColor("#C8D7DF"))
    canvas.setLineWidth(0.5)
    canvas.line(22 * mm, 15 * mm, width - 22 * mm, 15 * mm)
    canvas.setFont("ReportFont", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(22 * mm, 10.8 * mm, str(document.page))
    canvas.drawRightString(
        width - 22 * mm,
        10.8 * mm,
        rtl("گزارش مقایسه پایگاه‌های داده فروشگاه آنلاین"),
    )
    canvas.restoreState()


def parse_table(lines: list[str], start: int) -> tuple[list[list[str]], int]:
    rows = []
    index = start
    while index < len(lines) and lines[index].strip().startswith("|"):
        cells = [cell.strip() for cell in lines[index].strip().strip("|").split("|")]
        if not all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells):
            rows.append(cells)
        index += 1
    return rows, index


def report_table(rows: list[list[str]]) -> Table:
    column_count = max(len(row) for row in rows)
    normalized = [row + [""] * (column_count - len(row)) for row in rows]
    rendered = []
    for row_index, row in enumerate(normalized):
        style = TABLE_HEADER if row_index == 0 else TABLE_CELL
        rendered.append([paragraph(cell, style) for cell in row])

    total_width = 523
    if column_count == 2:
        widths = [total_width * 0.56, total_width * 0.44]
    elif column_count == 3:
        widths = [total_width * 0.36, total_width * 0.32, total_width * 0.32]
    elif column_count == 4:
        widths = [total_width * 0.27, total_width * 0.25, total_width * 0.24, total_width * 0.24]
    else:
        widths = [total_width / column_count] * column_count

    table = Table(rendered, colWidths=widths, repeatRows=1, hAlign="RIGHT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#B7C8D2")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return table


def chart(path: Path, caption: str) -> list:
    image = Image(str(path))
    max_width, max_height = 510, 235
    scale = min(max_width / image.imageWidth, max_height / image.imageHeight)
    image.drawWidth = image.imageWidth * scale
    image.drawHeight = image.imageHeight * scale
    image.hAlign = "CENTER"
    return [Spacer(1, 4), image, paragraph(caption, CAPTION)]


def cover() -> list:
    metadata = Table(
        [
            [paragraph("سناریو: فروشگاه آنلاین یکسان", COVER_META)],
            [paragraph("Benchmark واقعی با ۱۰۰٬۰۰۰ سفارش", COVER_META)],
            [paragraph("۱۶ عملیات، ۱۰ تکرار و دو فاز Index", COVER_META)],
        ],
        colWidths=[523],
        rowHeights=[13 * mm, 13 * mm, 13 * mm],
        hAlign="CENTER",
    )
    metadata.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), NAVY),
                ("BOX", (0, 0), (-1, -1), 1.1, TEAL),
                ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#4B7890")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    return [
        Spacer(1, 48 * mm),
        paragraph("گزارش نهایی پروژه", COVER_TITLE),
        paragraph("تحلیل و مقایسه SQL Server، PostgreSQL و MongoDB", COVER_SUBTITLE),
        Spacer(1, 10 * mm),
        metadata,
        Spacer(1, 35 * mm),
        HRFlowable(width="70%", thickness=1, color=TEAL, hAlign="CENTER"),
        PageBreak(),
    ]


def build_story(markdown: str) -> list:
    lines = markdown.splitlines()
    story = cover()
    index = 0
    in_code = False
    code_lines: list[str] = []

    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith("```"):
            if in_code:
                value = escape("\n".join(code_lines)).replace("\n", "<br/>")
                story.append(Paragraph(value, CODE))
                code_lines = []
            in_code = not in_code
            index += 1
            continue
        if in_code:
            code_lines.append(lines[index])
            index += 1
            continue
        if not stripped:
            story.append(Spacer(1, 2))
            index += 1
            continue

        heading = re.match(r"^(#{1,3})\s+(.*)$", stripped)
        if heading:
            level = len(heading.group(1))
            story.append(paragraph(heading.group(2), {1: H1, 2: H2, 3: H3}[level]))
            index += 1
            continue

        image_match = re.fullmatch(r"!\[([^]]*)\]\(([^)]+)\)", stripped)
        if image_match:
            image_path = (SOURCE.parent / image_match.group(2)).resolve()
            story.extend(chart(image_path, image_match.group(1)))
            index += 1
            continue

        if stripped.startswith("|"):
            rows, index = parse_table(lines, index)
            story.extend([Spacer(1, 3), report_table(rows), Spacer(1, 7)])
            continue

        if stripped.startswith("- "):
            story.append(paragraph("• " + stripped[2:], BULLET))
            index += 1
            continue

        if stripped.startswith("> "):
            callout = Table([[paragraph(stripped[2:], CALLOUT)]], colWidths=[523], hAlign="RIGHT")
            callout.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), GREEN_BG),
                        ("BOX", (0, 0), (-1, -1), 0.8, GREEN_BORDER),
                        ("LEFTPADDING", (0, 0), (-1, -1), 10),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )
            story.extend([callout, Spacer(1, 5)])
            index += 1
            continue

        clean = re.sub(r"\[([^]]+)\]\(([^)]+)\)", r"\1", stripped).replace("**", "")
        story.append(paragraph(clean, BODY))
        index += 1

    return story


class ReportDocument(BaseDocTemplate):
    def __init__(self, filename: str, **kwargs) -> None:
        super().__init__(filename, **kwargs)
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
            id="normal",
        )
        self.addPageTemplates([PageTemplate(id="all", frames=[frame], onPage=footer)])


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the final Persian project report PDF.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    document = ReportDocument(
        str(args.output),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=17 * mm,
        bottomMargin=21 * mm,
        title="گزارش نهایی پروژه",
        author="",
    )
    document.build(build_story(SOURCE.read_text(encoding="utf-8")))
    print(args.output)


if __name__ == "__main__":
    main()
