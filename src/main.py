from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List
import os
import uuid
import re
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io
import httpx
from dotenv import load_dotenv
import pdfplumber

load_dotenv()

APP_PORT = int(os.getenv('APP_PORT', 8000))
UPLOAD_DIR = os.getenv('UPLOAD_DIR', './uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Anonimizacao de Processos", version="0.2.0")

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


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


def detect_entities_in_text(text: str) -> List[dict]:
    """Detecta entidades no texto e retorna lista com tipo e valor"""
    entities = []
    
    # CPF (formatted or digits)
    cpf_regex = re.compile(r"\b\d{3}\.\d{3}\.\d{3}-\d{2}\b|\b\d{11}\b")
    for m in cpf_regex.finditer(text):
        entities.append({"type": "CPF", "value": m.group(0), "start": m.start(), "end": m.end()})

    # CNPJ
    cnpj_regex = re.compile(r"\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b|\b\d{14}\b")
    for m in cnpj_regex.finditer(text):
        entities.append({"type": "CNPJ", "value": m.group(0), "start": m.start(), "end": m.end()})

    # Emails
    email_regex = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    for m in email_regex.finditer(text):
        entities.append({"type": "EMAIL", "value": m.group(0), "start": m.start(), "end": m.end()})

    # Phones (very permissive)
    phone_regex = re.compile(r"\b\+?\d[\d\s().-]{7,}\d\b")
    for m in phone_regex.finditer(text):
        entities.append({"type": "PHONE", "value": m.group(0), "start": m.start(), "end": m.end()})

    # Nomes: procura por padrões após títulos (Sr., Sra., Dr.) ou em contextos específicos
    # Padrão: (Sr\.|Sra\.|Dr\.) + Nome + (Sobrenome)+
    name_after_title = re.compile(
        r"(?:Sr\.|Sra\.|Dr\.)\s+([A-ZÁÉÍÓÚ][a-záéíóú]+(?:\s+[A-ZÁÉÍÓÚ][a-záéíóú]+){1,4})",
        re.IGNORECASE
    )
    for m in name_after_title.finditer(text):
        entities.append({"type": "NAME", "value": m.group(1), "start": m.start(1), "end": m.end(1)})

    # Padrão: NOME COMPLETO em maiúsculas seguido de "(" ou ", " ou "brasileiro"
    name_uppercase = re.compile(
        r"\b([A-ZÁÉÍÓÚ][A-ZÁÉÍÓÚ]+(?:\s+[A-ZÁÉÍÓÚ][A-ZÁÉÍÓÚ]+){1,4})\s*(?:\(|,\s+brasileiro|,\s+casado)",
        re.IGNORECASE
    )
    for m in name_uppercase.finditer(text):
        name_candidate = m.group(1)
        # Evitar detectar siglas ou nomes de órgãos
        if not all(c.isupper() or c.isspace() for c in name_candidate if c.isalpha()):
            # Se tem letras minúsculas, significa que pode ser nome próprio
            entities.append({"type": "NAME", "value": name_candidate, "start": m.start(1), "end": m.end(1)})
        elif len(name_candidate.split()) >= 2:
            # Se tem múltiplas palavras em maiúsculas (ex: "CARLOS ALBERTO SILVEIRA"), considere como nome
            entities.append({"type": "NAME", "value": name_candidate, "start": m.start(1), "end": m.end(1)})

    # Normalizar espaços e remover duplicatas mantendo primeira ocorrência
    seen = set()
    unique_entities = []
    for entity in entities:
        entity['value'] = re.sub(r'\s+', ' ', entity['value'].strip())
        key = (entity['type'], entity['value'].lower())
        if key not in seen:
            seen.add(key)
            unique_entities.append(entity)
    
    return unique_entities


def redact_pdf_with_overlays(pdf_bytes: bytes, redaction_boxes: List[dict]) -> bytes:
    """
    Cria um PDF com tarjas pretas sobrepondo as áreas a anonimizar
    Usa pdfplumber para localizar e PyPDF2 para desenhar redações
    """
    reader = PdfReader(io.BytesIO(pdf_bytes))
    writer = PdfWriter()
    
    # Agrupa redações por página
    redactions_by_page = {}
    for box in redaction_boxes:
        page_num = box['page']
        if page_num not in redactions_by_page:
            redactions_by_page[page_num] = []
        redactions_by_page[page_num].append(box)
    
    # Processar cada página
    for page_num, page in enumerate(reader.pages):
        if page_num in redactions_by_page:
            # Obter dimensões da página original
            page_height = float(page.mediabox.height)
            page_width = float(page.mediabox.width)
            
            # Criar overlay com tarjas pretas usando reportlab
            packet = io.BytesIO()
            overlay_canvas = canvas.Canvas(packet, pagesize=(page_width, page_height))
            
            # Desenhar retângulos pretos nas posições das redações
            overlay_canvas.setFillColor('black')
            overlay_canvas.setStrokeColor('black')
            
            for i, box in enumerate(redactions_by_page[page_num]):
                # Coordenadas do pdfplumber (origem no canto superior)
                x0 = box['x0']
                x1 = box['x1']
                top = box['top']
                bottom = box['bottom']
                
                # Converter para sistema PyPDF2 (origem no canto inferior)
                # No reportlab canvas, origem também é canto inferior
                rect_x0 = x0
                rect_y0 = page_height - bottom  # bottom > top, então isso fica mais baixo
                rect_x1 = x1
                rect_y1 = page_height - top     # top < bottom, então isso fica mais alto
                
                width = rect_x1 - rect_x0
                height = rect_y1 - rect_y0
                
                # DEBUG: Log das coordenadas
                print(f"[PAGE {page_num}, BOX {i}] Entity: {box.get('entity_value', 'N/A')}")
                print(f"  pdfplumber: x0={x0:.2f}, x1={x1:.2f}, top={top:.2f}, bottom={bottom:.2f}")
                print(f"  reportlab: x={rect_x0:.2f}, y={rect_y0:.2f}, w={width:.2f}, h={height:.2f}")
                
                # Desenhar retângulo sólido
                overlay_canvas.rect(
                    rect_x0, 
                    rect_y0, 
                    width,  # largura
                    height, # altura
                    fill=1, 
                    stroke=0
                )
            
            overlay_canvas.save()
            packet.seek(0)
            
            # Fazer merge do overlay com a página original
            try:
                overlay_pdf = PdfReader(packet)
                overlay_page = overlay_pdf.pages[0]
                page.merge_page(overlay_page)
            except Exception as e:
                print(f"Erro ao fazer merge da página {page_num}: {e}")
        
        writer.add_page(page)
    
    # Salvar PDF modificado
    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output.getvalue()


def find_entity_boxes_in_pdf(pdf_bytes: bytes, entities: List[dict]) -> List[dict]:
    """
    Localiza as entidades no PDF usando pdfplumber e retorna as coordenadas das redações
    """
    redaction_boxes = []
    found_pairs = set()  # Rastrear (page, x0, x1, top, bottom) para evitar duplicatas
    
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page_num, page in enumerate(pdf.pages):
                page_text = page.extract_text()
                if not page_text:
                    continue
                
                all_words = page.extract_words()
                if not all_words:
                    continue
                
                for entity in entities:
                    entity_value = re.sub(r'\s+', ' ', entity['value'].strip())
                    words_in_entity = entity_value.split()
                    if not words_in_entity:
                        continue
                    # Normalizar para comparação
                    entity_normalized = re.sub(r'[^\w\s]', '', entity_value).lower()
                    
                    # Verifica se a entidade está nesta página (com normalização)
                    page_text_normalized = re.sub(r'[^\w\s]', '', page_text).lower()
                    if entity_normalized not in page_text_normalized:
                        continue
                    
                    # Procura por múltiplas ocorrências
                    for start_idx, word in enumerate(all_words):
                        word_normalized = re.sub(r'[^\w\s]', '', word['text']).lower()
                        first_word_normalized = re.sub(r'[^\w\s]', '', words_in_entity[0]).lower()
                        
                        if word_normalized == first_word_normalized:
                            # Coleta todas as palavras que compõem a entidade
                            boxes = [word]
                            matched = True
                            
                            for j in range(1, len(words_in_entity)):
                                if start_idx + j < len(all_words):
                                    next_word = all_words[start_idx + j]
                                    next_word_normalized = re.sub(r'[^\w\s]', '', next_word['text']).lower()
                                    expected_word_normalized = re.sub(r'[^\w\s]', '', words_in_entity[j]).lower()
                                    
                                    if next_word_normalized == expected_word_normalized:
                                        boxes.append(next_word)
                                    else:
                                        matched = False
                                        break
                                else:
                                    matched = False
                                    break
                            
                            # Se encontrou todas as palavras
                            if matched and len(boxes) == len(words_in_entity):
                                # Calcula a caixa que engloba todas as palavras
                                x0 = min(b['x0'] for b in boxes)
                                x1 = max(b['x1'] for b in boxes)
                                top = min(b['top'] for b in boxes)
                                bottom = max(b['bottom'] for b in boxes)
                                
                                # Evitar duplicatas na mesma página
                                pair_key = (page_num, round(x0, 2), round(x1, 2), round(top, 2), round(bottom, 2))
                                if pair_key not in found_pairs:
                                    found_pairs.add(pair_key)
                                    redaction_boxes.append({
                                        'page': page_num,
                                        'x0': x0,
                                        'x1': x1,
                                        'top': top,
                                        'bottom': bottom,
                                        'entity_type': entity['type'],
                                        'entity_value': entity_value
                                    })
    except Exception as e:
        print(f"Erro ao processar PDF com pdfplumber: {e}")
        import traceback
        traceback.print_exc()
    
    return redaction_boxes


async def generate_summary(text: str) -> str:
    # Prefer DeepSeek if configured
    deepseek_key = os.getenv('DEEPSEEK_API_KEY')
    deepseek_base = os.getenv('DEEPSEEK_API_BASE')
    if deepseek_key and deepseek_base:
        try:
            payload = {"task": "summarize", "text": text}
            headers = {"Authorization": f"Bearer {deepseek_key}"}
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.post(f"{deepseek_base}/summaries", json=payload, headers=headers)
                if r.status_code == 200:
                    return r.json().get('summary', '')
        except Exception:
            pass

    # fallback naive summary: first 3 sentences
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return ' '.join(sentences[:3])


@app.post('/test-redaction-debug')
async def test_redaction_debug(file: UploadFile = File(...)):
    """Debug endpoint: mostra detalhes das tarjas com coordenadas"""
    content = await file.read()
    text = extract_text_from_pdf_bytes(content)
    entities = detect_entities_in_text(text)
    redaction_boxes = find_entity_boxes_in_pdf(content, entities)
    
    # Obter dimensões das páginas para debug
    with pdfplumber.open(io.BytesIO(content)) as pdf:
        pages_info = []
        for idx, page in enumerate(pdf.pages):
            pages_info.append({
                'page_num': idx,
                'width': page.width,
                'height': page.height
            })
    
    # Detalhes das redações
    redaction_details = []
    for box in redaction_boxes:
        redaction_details.append({
            'page': box['page'],
            'entity_value': box['entity_value'],
            'entity_type': box['entity_type'],
            'x0': round(box['x0'], 2),
            'x1': round(box['x1'], 2),
            'top': round(box['top'], 2),
            'bottom': round(box['bottom'], 2),
            'width': round(box['x1'] - box['x0'], 2),
            'height': round(box['bottom'] - box['top'], 2)
        })
    
    return JSONResponse({
        'pages_info': pages_info,
        'total_entities': len(entities),
        'redaction_count': len(redaction_boxes),
        'redactions': redaction_details
    })


@app.post('/test-entities')
async def test_entities(file: UploadFile = File(...)):
    """Endpoint para testes: retorna entidades detectadas e localizadas"""
    content = await file.read()
    text = extract_text_from_pdf_bytes(content)
    entities = detect_entities_in_text(text)
    
    # Localiza as caixas de redação no PDF
    redaction_boxes = find_entity_boxes_in_pdf(content, entities)
    
    # Organizar resultados
    redacted = [r['entity_value'] for r in redaction_boxes]
    not_redacted = [e['value'] for e in entities if e['value'] not in redacted]
    
    return JSONResponse({
        'total_entities': len(entities),
        'detected': [{"type": e['type'], "value": e['value']} for e in entities],
        'redacted_count': len(redaction_boxes),
        'redacted': redacted,
        'not_redacted': not_redacted,
        'redaction_details': redaction_boxes
    })


@app.post('/process-file')
async def process_file(file: UploadFile = File(...)):
    content = await file.read()
    text = extract_text_from_pdf_bytes(content)
    entities = detect_entities_in_text(text)
    
    # Localiza as caixas de redação no PDF
    redaction_boxes = find_entity_boxes_in_pdf(content, entities)
    
    # Cria PDF com redações
    anonymized_pdf = redact_pdf_with_overlays(content, redaction_boxes)
    
    # Salva o PDF anonimizado
    original_name = file.filename or 'document.pdf'
    original_stem = os.path.splitext(original_name)[0]
    anonymized_filename = f"{original_stem}_anon.pdf"
    anonymized_path = os.path.join(UPLOAD_DIR, anonymized_filename)
    
    with open(anonymized_path, 'wb') as f:
        f.write(anonymized_pdf)
    
    summary = await generate_summary(text)
    
    return JSONResponse({
        'summary': summary,
        'entities': [{"type": e['type'], "value": e['value']} for e in entities],
        'entities_total': len(entities),
        'redactions_applied': len(redaction_boxes),
        'anonymized_download': f"/download/{anonymized_filename}"
    })


@app.get('/download/{filename}')
def download_file(filename: str):
    path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(path):
        return FileResponse(path, media_type='application/pdf', filename=filename)
    return JSONResponse({'error': 'not found'}, status_code=404)

