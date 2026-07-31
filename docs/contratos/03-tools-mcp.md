# Contrato 03 - Contratos de Tools e MCP

## Tools
- text_extraction_tool
- entity_detection_tool
- anonymization_tool
- metadata_generation_tool
- summary_generation_tool
- audit_log_tool

## MCP
- O sistema deve expor um canal MCP para integração com agentes externos.
- O MCP deve aceitar eventos de upload, processamento e revisão.
- As respostas devem ser estruturadas com status, resultado e metadados.

## Interface esperada
{
  "document_id": "uuid",
  "status": "processed",
  "entities": [],
  "anonymized_text": "...",
  "metadata": {},
  "summary": "..."
}
