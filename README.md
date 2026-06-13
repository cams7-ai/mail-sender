# Mail Sender

API REST em Python 3.12 com FastAPI para envio de e-mails via SMTP.

## Requisitos

- Python 3.12 ou superior

## Instalar dependências

Antes de reinstalar o projeto no Windows, pare a API se ela estiver rodando por `gmail-reader` ou `python -m main`. O `pip` precisa substituir o executável `.venv\Scripts\gmail-reader.exe` durante a instalação.

```powershell
python -m pip install -e ".[dev]"
```

## Configuração

Configure os dados SMTP no arquivo `.env` ou por variáveis de ambiente. Não versione credenciais reais.

Para configurar envio pelo Gmail, veja [GMAIL_SETUP.md](GMAIL_SETUP.md).

Crie o `.env` a partir do exemplo:

```powershell
Copy-Item .env.example .env
```

Exemplo para Gmail:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD='senha de app do gmail'
SMTP_FROM=seu-email@gmail.com
SMTP_USE_TLS=true
```

Também é possível configurar pela sessão do PowerShell:

```powershell
$env:SMTP_HOST="smtp.gmail.com"
$env:SMTP_PORT="587"
$env:SMTP_USER="seu-email@gmail.com"
$env:SMTP_PASSWORD="senha de app do gmail"
$env:SMTP_FROM="seu-email@gmail.com"
$env:SMTP_USE_TLS="true"
```

## Executar a API

Com o projeto instalado em modo editável:

```powershell
python -m main
```

Também é possível iniciar pelo comando instalado:

```powershell
gmail-reader
```

A API ficará disponível em:

```text
http://127.0.0.1:8000
```

## Documentação da API

Com a API em execução, acesse:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

## Enviar e-mail

Com SMTP configurado no `.env`, execute:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/mail/send" `
  -ContentType "application/json" `
  -Body '{"to":"outro-email@gmail.com","subject":"Teste Gmail","body":"Mensagem enviada pelo mail-sender via API REST"}'
```

Resposta esperada:

```json
{
  "message": "E-mail enviado com sucesso."
}
```

## Erros da API

Todos os erros retornados pelos endpoints usam o schema `ErrorResponse`:

```json
{
  "error": {
    "code": "string",
    "message": "string"
  }
}
```

As mensagens de erro são retornadas em português do Brasil.

## Executar testes

```powershell
python -m pytest
```

Os testes executam com cobertura mínima de 100% e não enviam e-mails reais.

## Segurança

- Não coloque senhas diretamente no código.
- Prefira `.env` ou `SMTP_PASSWORD` para informar a senha.
- Para Gmail, use uma senha de app em vez da senha principal da conta.
- Não exponha `SMTP_PASSWORD` em logs, respostas HTTP ou mensagens de erro.
