# AGENTS.md

## Propósito
Este projeto define um produto de anonimização de textos em processos judiciais, com foco em segurança, rastreabilidade, conformidade e integração com LLMs.

## Regras de desenvolvimento
- Priorizar segurança e privacidade por padrão.
- Manter logs auditáveis sem expor dados pessoais.
- Todos os documentos devem passar por validação de anonimização antes de qualquer armazenamento ou envio externo.
- O sistema deve suportar múltiplas LLMs, com provider abstraction.
- O uso de Docker e PostgreSQL é obrigatório.
- O projeto deve ter documentação contratual em português.

## Stack sugerida
- Backend: Python 3.11+
- Banco: PostgreSQL
- Orquestração: Docker Compose
- Workflow: orchestrator próprio ou n8n/Temporal
- Graph: LangGraph
- Frontend: React/Next.js
- IA: DeepSeek como padrão, com possibilidade de trocar por OpenAI, Anthropic, Ollama, etc.

## Entregáveis mínimos
- Contratos de produto e arquitetura
- Especificação de funcionalidades
- Testes BDD
- Estratégia de segurança
- Estratégia de frontend/usabilidade/manutenibilidade
- Projeção de custos para 10 usuários
- Arquivo .env.example e .env
