# Contrato 10 - Modelos de Dados

## Documento
- id: uuid
- filename: string
- content_type: string
- created_at: datetime
- status: enum
- language: string
- hash: string

## EntidadeSensivel
- id: uuid
- document_id: uuid
- type: string
- value: string
- start: int
- end: int
- confidence: float
- approved: bool

## ResultadoAnonimizado
- id: uuid
- document_id: uuid
- anonymized_text: text
- summary: text
- metadata_json: json
- provider: string
- created_at: datetime

## Auditoria
- id: uuid
- document_id: uuid
- action: string
- actor: string
- created_at: datetime
- details: json
