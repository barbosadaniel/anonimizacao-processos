# Contrato 04 - Especificação de Funcionalidades

## 1. Upload e ingestão
- Aceitar arquivos .txt, .pdf e .docx.
- Validar tamanho máximo.
- Armazenar metadados básicos.

## 2. Extração de texto
- Converter o conteúdo para texto legível.
- Preservar estrutura básica.

## 3. Detecção de entidades sensíveis
- Nome de pessoa.
- CPF, CNPJ, endereço, telefone, e-mail.
- Datas, números de processo e referências judiciais.

## 4. Anonimização
- Substituir por tags como [NOME], [CPF], [ENDERECO].
- Garantir que a substituição seja consistente ao longo do documento.

## 5. Metadados
- Autor, data de upload, hash, idioma, tamanho, status de processamento.

## 6. Resumo do documento
- Resumo executivo em linguagem simples.
- Resumo técnico opcional.

## 7. Revisão humana
- Permitir aprovação/rejeição de entidades identificadas.
- Registrar alterações para auditoria.
