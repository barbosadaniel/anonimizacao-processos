# Contrato 06 - Segurança

## Requisitos de segurança
- Criptografia TLS para todas as comunicações.
- Criptografia em repouso para dados sensíveis.
- Controle de acesso por função.
- Auditoria completa de ações.
- Redução de risco com anonimização antes de qualquer envio a LLM externa.

## Política de dados
- Nenhum dado pessoal deve ser enviado a provedores externos sem pré-processamento.
- O armazenamento de textos brutos deve ser opcional e controlado.
- Logs devem ser sanitizados.

## Recomendações
- Uso de secrets via .env ou secret manager.
- Rotação de chaves.
- Backup e recuperação.
