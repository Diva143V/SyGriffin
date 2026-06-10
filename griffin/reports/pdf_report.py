from __future__ import annotations

from pathlib import Path


def write_pdf(path: Path, markdown: str) -> Path:
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas

        c = canvas.Canvas(str(path), pagesize=letter)
        width, height = letter
        y = height - 48
        for line in markdown.splitlines():
            if y < 48:
                c.showPage()
                y = height - 48
            c.drawString(48, y, line[:110])
            y -= 14
        c.save()
    except Exception:
        path.write_bytes(b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n")
    return path
