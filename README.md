# mail-sender

Aplicação Python 3.12 simples para envio de e-mails via SMTP.

## Requisitos

- Python 3.12 ou superior

## Instalar dependências de desenvolvimento

```bash
python -m pip install -e ".[dev]"
```

## Executar testes

```bash
python -m pytest
```

## Configuração

Configure os dados SMTP no arquivo `.env` ou por variáveis de ambiente. Não versione credenciais reais.

Para configurar envio pelo Gmail, veja [GMAIL_SETUP.md](GMAIL_SETUP.md).

Crie o `.env` a partir do exemplo:

```bash
Copy-Item .env.example .env
```

Exemplo para Gmail:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD='senha de app gerada pelo google'
SMTP_FROM=seu-email@gmail.com
SMTP_USE_TLS=true
```

Também é possível configurar pela sessão do PowerShell:

```bash
$env:SMTP_HOST="smtp.gmail.com"
$env:SMTP_PORT="587"
$env:SMTP_USER="seu-email@gmail.com"
$env:SMTP_PASSWORD="senha de app gerada pelo google"
$env:SMTP_FROM="seu-email@gmail.com"
$env:SMTP_USE_TLS="true"
```

## Uso

Com SMTP configurado no `.env`:

```bash
python .\src\main.py --to outro-email@gmail.com --subject "Teste Gmail" --body "Email de teste enviado pelo mail-sender via Gmail"
```

Argumentos de CLI tem precedência sobre variáveis de ambiente e sobre o `.env`:

```bash
python .\src\main.py --host smtp.gmail.com --port 587 --from seu-email@gmail.com --user seu-email@gmail.com --password "senha de app gerada pelo google" --to outro-email@gmail.com --subject "Teste Gmail" --body "Email de teste enviado pelo mail-sender via Gmail" --use-tls
```

## Segurança

- Nao coloque senhas diretamente no código.
- Prefira `.env` ou `SMTP_PASSWORD` para informar a senha.
- Para Gmail, use uma senha de app em vez da senha principal da conta.
- Os testes usam objetos falsos e não enviam e-mails reais.
