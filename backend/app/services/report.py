"""
PDF style report generation.

Built with ReportLab's platypus flowables rather than an HTML-to-PDF
converter: no headless browser, no system libraries, and the whole thing
fits in a container layer small enough for a free container host.
"""
import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ACCENT = colors.HexColor("#d81b60")
INK = colors.HexColor("#1a0d14")
MUTED = colors.HexColor("#6b7280")
RULE = colors.HexColor("#e5e7eb")

CATEGORY_LABELS = {
    "necklines": "Necklines",
    "silhouettes": "Silhouettes & Fits",
    "colors": "Colour Palette",
    "patterns": "Patterns",
    "accessories": "Accessories",
    "hairstyles": "Hairstyles",
}


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "title", parent=base["Title"], fontSize=26, leading=30,
            textColor=INK, spaceAfter=2,
        ),
        "subtitle": ParagraphStyle(
            "subtitle", parent=base["Normal"], fontSize=10, leading=14,
            textColor=MUTED, alignment=TA_CENTER, spaceAfter=18,
        ),
        "section": ParagraphStyle(
            "section", parent=base["Heading2"], fontSize=14, leading=18,
            textColor=ACCENT, spaceBefore=16, spaceAfter=8,
        ),
        "rec": ParagraphStyle(
            "rec", parent=base["Normal"], fontSize=11, leading=14,
            textColor=INK, spaceAfter=2,
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"], fontSize=9.5, leading=13,
            textColor=MUTED, spaceAfter=4,
        ),
        "reason": ParagraphStyle(
            "reason", parent=base["Normal"], fontSize=8.5, leading=11,
            textColor=ACCENT, spaceAfter=10,
        ),
        "footer": ParagraphStyle(
            "footer", parent=base["Normal"], fontSize=8, leading=11,
            textColor=MUTED, alignment=TA_CENTER,
        ),
    }


def _attribute_table(analysis, style) -> Table | None:
    """The detected attributes, one row each. None if nothing was detected."""
    rows = []

    if analysis.face_shape:
        rows.append([
            "Face shape",
            analysis.face_shape.replace("_", " ").title(),
            _percent(analysis.face_confidence),
        ])

    if analysis.skin_depth:
        tone = f"{analysis.skin_depth.title()}, {(analysis.skin_undertone or '').title()} undertone"
        if analysis.skin_hex_color:
            tone += f"  ({analysis.skin_hex_color})"
        rows.append(["Skin tone", tone, _percent(analysis.skin_confidence)])

    if analysis.body_shape:
        rows.append([
            "Body shape",
            analysis.body_shape.replace("_", " ").title(),
            _percent(analysis.body_confidence),
        ])

    if not rows:
        return None

    table = Table(
        [["Attribute", "Result", "Confidence"]] + rows,
        colWidths=[38 * mm, 90 * mm, 32 * mm],
        hAlign="LEFT",
    )
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("TEXTCOLOR", (0, 1), (-1, -1), INK),
        ("ALIGN", (2, 0), (2, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, RULE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#faf9ff")]),
    ]))
    return table


def _percent(value) -> str:
    return f"{round(value * 100)}%" if value is not None else "—"


def _palette_strip(palette: list[dict]) -> Table | None:
    """
    A colour palette as swatches rather than adjectives.

    "Jewel tones" is not something you can hold up against a shirt in a shop,
    which is what this report is for. Each swatch carries its hex code so the
    page survives being printed in greyscale.
    """
    swatches = [s for s in (palette or []) if s.get("hex")][:8]
    if not swatches:
        return None

    width = 20 * mm
    table = Table(
        [[""] * len(swatches), [s.get("hex", "") for s in swatches]],
        colWidths=[width] * len(swatches),
        rowHeights=[13 * mm, 5 * mm],
        hAlign="LEFT",
    )

    style = [
        ("FONTSIZE", (0, 1), (-1, 1), 6),
        ("TEXTCOLOR", (0, 1), (-1, 1), MUTED),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 1), (-1, 1), "TOP"),
        ("TOPPADDING", (0, 1), (-1, 1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]
    for i, swatch in enumerate(swatches):
        style.append(("BACKGROUND", (i, 0), (i, 0), colors.HexColor(swatch["hex"])))
        style.append(("BOX", (i, 0), (i, 0), 0.4, RULE))

    table.setStyle(TableStyle(style))
    return table


def _escape(text) -> str:
    """Recommendation text is editorial copy, but it lands in RML markup."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_style_report(analysis) -> bytes:
    """
    Render an analysis as a PDF.

    The photo is deliberately not included — the report is meant to be
    forwarded, printed, and taken shopping.
    """
    style = _styles()
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        title="StyleSense AI — Style Report",
        author="StyleSense AI",
        subject="Personal style analysis",
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=16 * mm,
    )

    story = [
        Paragraph("Your Style Report", style["title"]),
        Paragraph(
            f"StyleSense AI &nbsp;·&nbsp; "
            f"{analysis.created_at.strftime('%d %B %Y')}",
            style["subtitle"],
        ),
        HRFlowable(width="100%", thickness=0.6, color=RULE, spaceAfter=14),
    ]

    table = _attribute_table(analysis, style)
    if table:
        story.append(Paragraph("Detected attributes", style["section"]))
        story.append(table)

    grouped = {}
    for rec in analysis.recommendations or []:
        grouped.setdefault(rec.get("category", "other"), []).append(rec)

    if grouped:
        story.append(Spacer(1, 10))
        story.append(Paragraph("Recommendations", style["section"]))

        for category, recs in grouped.items():
            block = [
                Paragraph(
                    CATEGORY_LABELS.get(category, category.title()),
                    style["section"],
                )
            ]
            for rec in recs:
                block.append(
                    Paragraph(f"<b>{_escape(rec.get('recommendation', ''))}</b>", style["rec"])
                )
                if rec.get("explanation"):
                    block.append(Paragraph(_escape(rec["explanation"]), style["body"]))
                strip = _palette_strip(rec.get("palette"))
                if strip:
                    block.append(strip)
                    block.append(Spacer(1, 4))
                reasons = rec.get("match_reasons") or []
                if reasons:
                    block.append(
                        Paragraph(
                            " &nbsp;·&nbsp; ".join(_escape(r) for r in reasons[:3]),
                            style["reason"],
                        )
                    )
            # Keep a category's heading with at least its first item.
            story.append(KeepTogether(block[:3]))
            story.extend(block[3:])
    else:
        story.append(Paragraph("No recommendations were generated.", style["body"]))

    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.6, color=RULE, spaceAfter=8))
    story.append(
        Paragraph(
            "Generated by StyleSense AI. These suggestions are guidance, not rules — "
            "wear what you like.",
            style["footer"],
        )
    )

    doc.build(story)
    return buffer.getvalue()


def report_filename(analysis) -> str:
    stamp = analysis.created_at.strftime("%Y-%m-%d")
    return f"stylesense-report-{stamp}.pdf"
