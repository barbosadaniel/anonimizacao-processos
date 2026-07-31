# Contrato 01 - Especificação de Produto

## Objetivo
Desenvolver um produto para anonimização automática de textos de processos judiciais, com geração de metadados, entidades identificadas, resumo do documento e rastreabilidade.

## Requisitos funcionais
- Upload de documentos em texto ou PDF.
- Extração de texto.
- Identificação automática de entidades sensíveis.
- Substituição por placeholders seguros.
- Geração de metadados do documento.
- Geração de resumo executivo.
- Registro de histórico e auditoria.
- Interface para revisão humana.

## Requisitos não funcionais
- Segurança: criptografia em repouso e em trânsito.
- Conformidade: LGPD, GDPR e padrões internos.
- Escalabilidade: 10 usuários iniciais, expandível.
- Manutenibilidade: modularização por camadas.
- Usabilidade: fluxo simples e revisão intuitiva.

## Critérios de aceite
- O usuário consegue enviar um documento e obter uma versão anonimizada.
- O sistema gera metadados e resumo.
- O sistema aponta as entidades detectadas.
- O sistema registra um histórico auditável.
