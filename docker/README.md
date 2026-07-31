# Docker Setup

Use este diretório para iniciar a aplicação e o banco PostgreSQL com Docker Compose.

## Como executar
1. Garanta que o Docker daemon esteja rodando.
2. Entre no diretório `docker`:
   ```powershell
   cd C:\Users\admin\anonimizacao-processos\docker
   ```
3. Execute:
   ```powershell
   docker compose up --build
   ```

## Variáveis de ambiente
O arquivo `.env` neste diretório define as credenciais do PostgreSQL usadas pelo `docker-compose.yml`.

## Observações
- Se usar WSL, garanta que o Docker Desktop esteja ativo.
- Se o daemon não estiver acessível, o comando falhará com `dial unix /var/run/docker.sock`.
