import json

from fpdf import FPDF
from fpdf.enums import XPos, YPos


def export_json(data):
    return json.dumps(data, default=str, indent=2).encode("utf-8")


def _latin1_safe(text: str) -> str:
    """fpdf2's built-in fonts cover Latin-1 only.

    Transcripts routinely contain characters outside that range (smart quotes,
    accents, CJK), which would otherwise raise mid-render. Substituting keeps
    the export working; the alternative is bundling a Unicode TTF.
    """
    return text.encode("latin-1", errors="replace").decode("latin-1")


def export_summary_pdf(summary: str) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    for line in _latin1_safe(summary).split("\n"):
        # multi_cell needs non-empty content; render blank lines as spacing.
        # new_x/new_y are required: fpdf2 leaves the cursor at the cell's right
        # edge by default, so the next line would start with no width left.
        pdf.multi_cell(
            0, 10, line if line.strip() else " ",
            new_x=XPos.LMARGIN, new_y=YPos.NEXT,
        )
    return bytes(pdf.output())
