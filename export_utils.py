import json
from fpdf import FPDF
import io

def export_json(data):
    return io.BytesIO(json.dumps(data, default=str).encode('utf-8')).getvalue()


def export_summary_pdf(summary):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in summary.split("\n"):
        pdf.multi_cell(0, 10, line)
    buf = io.BytesIO()
    pdf.output(buf)
    return buf.getvalue()