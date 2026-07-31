import io
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from fastapi.testclient import TestClient

from src.main import app, UPLOAD_DIR

client = TestClient(app)


def _make_pdf_bytes(content: str = 'CPF 123.456.789-00') -> bytes:
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont('Helvetica', 12)
    c.drawString(50, 780, content)
    c.save()
    buffer.seek(0)
    return buffer.getvalue()


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_process_file_uses_original_name_plus_anon():
    pdf_bytes = _make_pdf_bytes('CPF 123.456.789-00')
    response = client.post(
        '/process-file',
        files={'file': ('sample.pdf', pdf_bytes, 'application/pdf')}
    )

    assert response.status_code == 200
    data = response.json()
    assert data['anonymized_download'].endswith('/download/sample_anon.pdf')

    saved_path = Path(UPLOAD_DIR) / 'sample_anon.pdf'
    assert saved_path.exists()

