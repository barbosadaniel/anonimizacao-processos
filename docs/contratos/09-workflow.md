# Contrato 09 - Workflow e LangGraph

## Objetivo
Definir o fluxo operacional do produto, desde o upload do documento até a geração do resultado anonimizado.

## Nós do workflow
1. ingest_document
2. extract_text
3. detect_entities
4. review_entities
5. anonymize_text
6. generate_metadata
7. generate_summary
8. persist_result

## Regras de execução
- O fluxo deve ser síncrono para documentos pequenos e assíncrono para lotes maiores.
- Cada etapa deve registrar um evento de auditoria.
- O fluxo deve suportar fallback para outro provider de LLM.

## Integração com LangGraph
- Cada nó do workflow deve ter uma função bem definida.
- O estado do fluxo deve conter: documento, texto extraído, entidades, texto anonimizado, metadados, resumo e status.
