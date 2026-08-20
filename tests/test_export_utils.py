import json

from export_utils import export_json, export_summary_pdf


def test_export_json_round_trips():
    payload = {"summary": "hello", "object_frames": 3}
    assert json.loads(export_json(payload).decode()) == payload


def test_export_json_survives_unserializable_values():
    class Odd:
        pass

    # default=str keeps the export from failing on stray objects.
    assert b"Odd" in export_json({"x": Odd()})


def test_pdf_export_produces_a_pdf():
    out = export_summary_pdf("A short summary.\n\nSecond paragraph.")
    assert out[:4] == b"%PDF"
    assert len(out) > 500


def test_pdf_export_handles_non_latin1_text():
    """Regression: smart quotes and CJK used to raise mid-render."""
    out = export_summary_pdf("He said “hello” — 你好")
    assert out[:4] == b"%PDF"
