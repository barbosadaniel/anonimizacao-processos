# Contrato 05 - Testes com BDD

## Cenário 1: upload e anonimização básica
Dado um documento com nome e CPF
Quando o usuário envia o arquivo
Então o sistema deve retornar uma versão anonimizada e os metadados correspondentes.

## Cenário 2: resumo gerado
Dado um documento com conteúdo de múltiplos parágrafos
Quando o processamento terminar
Então o sistema deve gerar um resumo executivo.

## Cenário 3: revisão humana
Dado uma entidade identificada incorretamente
Quando o usuário corrigir a marcação
Então o sistema deve registrar a alteração na auditoria.

## Cenário 4: troca de provider
Dado um provider configurado
Quando o provider for trocado para outro modelo
Então o fluxo deve continuar sem alteração do contrato externo.
