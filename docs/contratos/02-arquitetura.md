# Contrato 02 - Arquitetura e Stack

## Arquitetura proposta
- Frontend: React/Next.js
- Backend: Python FastAPI
- Orquestração de fluxo: LangGraph
- Banco: PostgreSQL
- Containerização: Docker Compose
- Armazenamento: filesystem local para uploads, com possibilidade de S3

## Fluxo principal
1. Upload do documento.
2. Extração de texto.
3. Classificação de entidades sensíveis.
4. Anonimização com substituição segura.
5. Geração de metadados, entidades e resumo.
6. Armazenamento no banco e disponibilização para revisão.

## Integração de LLMs
- DeepSeek como provider padrão.
- Provider abstraction para trocar por OpenAI, Anthropic, Ollama.
- Estratégia de fallback e retry.
