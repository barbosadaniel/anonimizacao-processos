# Anonimização de Processos

Produto de anonimização de textos para processos judiciais, com foco em segurança, privacidade, rastreabilidade, conformidade e integração com modelos de linguagem.

## Objetivo
Este repositório entrega a base para um serviço de anonimização de documentos jurídicos, com:
- extração de texto de PDFs
- identificação de entidades sensíveis
- resumo do documento
- geração de PDF anonimizado
- arquitetura pronta para Docker + PostgreSQL + FastAPI

## Stack
- Backend: Python 3.11 + FastAPI
- Banco: PostgreSQL
- Orquestração: Docker Compose
- IA: suporte a DeepSeek, OpenAI, Anthropic e Ollama
- Documentação: contratos e arquitetura em português

## Estrutura
- `docs/contratos/`: contratos e especificações de produto
- `src/`: aplicação principal e interface web
- `tests/`: testes e cenários BDD
- `docker/`: configuração de containers

## Execução rápida

### Local
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn src.main:app --reload
```

### Docker
```bash
docker-compose -f docker/docker-compose.yml build --no-cache api
docker-compose -f docker/docker-compose.yml up -d
```

### Verificar
```bash
curl http://localhost:8000/health
```

## Publicar no GitHub

```bash
git init
git add .
git commit -m "Initial import"
git branch -M main
git remote add origin https://github.com/<seu-usuario>/<seu-repo>.git
git push -u origin main
```

## Observações
- O arquivo `.env` deve manter as credenciais de ambiente e chaves de API. 
- O fluxo principal já permite upload do PDF, resumo, exibição de entidades e download do PDF anonimizado. 
