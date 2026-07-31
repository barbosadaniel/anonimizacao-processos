from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import os
import uuid
import re
from pypdf import PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io
import httpx
from dotenv import load_dotenv

load_dotenv()

APP_PORT = int(os.getenv('APP_PORT', 8000))
UPLOAD_DIR = os.getenv('UPLOAD_DIR', './uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Anonimizacao de Processos", version="0.2.0")

app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")


@app.get("/", response_class=HTMLResponse)
def index():
    html_path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
    with open(html_path, 'r', encoding='utf-8') as f:
        return HTMLResponse(f.read())


@app.get("/health")
def health():
    return {"status": "ok"}


def extract_text_from_pdf_bytes(data: bytes) -> str:
    reader = PdfReader(io.BytesIO(data))
    texts = []
    for page in reader.pages:
        try:
            texts.append(page.extract_text() or "")
        except Exception:
            texts.append("")
    return "\n\n".join(texts)


def anonymize_text(text: str):
    entities = []
    # CPF (formatted or digits)
    cpf_regex = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b|\b\d{11}\b")
    for m in cpf_regex.finditer(text):
        entities.append({"type": "CPF", "value": m.group(0), "start": m.start(), "end": m.end()})
    text = cpf_regex.sub('[CPF]', text)

    # CNPJ
    cnpj_regex = re.compile(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b|\b\d{14}\b")
    for m in cnpj_regex.finditer(text):
        entities.append({"type": "CNPJ", "value": m.group(0), "start": m.start(), "end": m.end()})
    text = cnpj_regex.sub('[CNPJ]', text)

    # Emails
    email_regex = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    for m in email_regex.finditer(text):
        entities.append({"type": "EMAIL", "value": m.group(0), "start": m.start(), "end": m.end()})
    text = email_regex.sub('[EMAIL]', text)

    # Phones (very permissive)
    phone_regex = re.compile(r"\b\+?\d[\d\s().-]{7,}\d\b")
    for m in phone_regex.finditer(text):
        entities.append({"type": "PHONE", "value": m.group(0), "start": m.start(), "end": m.end()})
    text = phone_regex.sub('[PHONE]', text)

    # Simple names heuristic: sequences of capitalized words (may produce false positives)
    name_regex = re.compile(r"\b([A-ZÁÉÍÓÚ][a-záéíóú]+(?:\s+[A-ZÁÉÍÓÚ][a-záéíóú]+)+)\b")
    for m in name_regex.finditer(text):
        entities.append({"type": "NAME", "value": m.group(0), "start": m.start(), "end": m.end()})
    text = name_regex.sub('[NAME]', text)

    return text, entities


def generate_summary(text: str) -> str:
    # Prefer DeepSeek if configured
    deepseek_key = os.getenv('DEEPSEEK_API_KEY')
    deepseek_base = os.getenv('DEEPSEEK_API_BASE')
    if deepseek_key and deepseek_base:
        try:
            payload = {"task": "summarize", "text": text}
            headers = {"Authorization": f"Bearer {deepseek_key}"}
            with httpx.Client(timeout=30) as client:
                r = client.post(f"{deepseek_base}/summaries", json=payload, headers=headers)
                if r.status_code == 200:
                    return r.json().get('summary', '')
        except Exception:
            pass

    # fallback naive summary: first 3 sentences
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return ' '.join(sentences[:3])


def create_pdf_from_text(text: str, out_path: str):
    # simple PDF writer with reportlab
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=A4)
    width, height = A4
    margin = 50
    y = height - margin
    line_height = 12
    for paragraph in text.split('\n'):
        words = paragraph.split(' ')
        line = ''
        for w in words:
            test_line = (line + ' ' + w).strip()
            if c.stringWidth(test_line, 'Helvetica', 10) < (width - 2 * margin):
                line = test_line
            else:
                c.setFont('Helvetica', 10)
                c.drawString(margin, y, line)
                y -= line_height
                line = w
                if y < margin:
                    c.showPage()
                    y = height - margin
        if line:
            c.setFont('Helvetica', 10)
            c.drawString(margin, y, line)
            y -= line_height
        y -= line_height  # paragraph gap
        if y < margin:
            c.showPage()
            y = height - margin
    c.save()
    packet.seek(0)
    with open(out_path, 'wb') as f:
        f.write(packet.read())


@app.post('/process-file')
async def process_file(file: UploadFile = File(...)):
    content = await file.read()
    text = extract_text_from_pdf_bytes(content)
    anonymized_text, entities = anonymize_text(text)
    summary = generate_summary(text)

    original_name = file.filename or 'document.pdf'
    original_stem = os.path.splitext(original_name)[0]
    anonymized_filename = f"{original_stem}_anon.pdf"
    anonymized_path = os.path.join(UPLOAD_DIR, anonymized_filename)

    create_pdf_from_text(anonymized_text, anonymized_path)
    return JSONResponse({
        'summary': summary,
        'entities': entities,
        'anonymized_download': f"/download/{anonymized_filename}"
    })


@app.get('/download/{filename}')
def download_file(filename: str):
    path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(path):
        return FileResponse(path, media_type='application/pdf', filename=filename)
    return JSONResponse({'error': 'not found'}, status_code=404)

