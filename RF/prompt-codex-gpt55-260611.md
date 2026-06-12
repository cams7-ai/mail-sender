# Prompt para Codex GPT-5.5 - `mail-sender` API REST

Atualize o projeto `mail-sender` para uma API REST em Python 3.12 com FastAPI, seguindo Clean Architecture com separação clara entre API, aplicação, domínio e infraestrutura, mantendo envio de e-mail via SMTP e cobertura de 100% nos testes.

## Contexto atual

O projeto atualmente é uma aplicação Python 3.12 simples de envio de e-mails via SMTP por CLI.

Arquivos relevantes existentes:

```text
mail-sender/
+-- README.md
+-- GMAIL_SETUP.md
+-- .env
+-- .env.example
+-- .gitignore
+-- pyproject.toml
+-- src/
|   +-- main.py
+-- tests/
    +-- test_main.py
```

A implementação atual em `src/main.py` possui:

- `MailConfig` como dataclass de configuração SMTP.
- `ConfigError` para configuração inválida.
- `load_dotenv()` para carregar variáveis do arquivo `.env` sem sobrescrever variáveis já existentes no ambiente.
- `parse_bool()` para converter valores booleanos comuns.
- `build_parser()` e `main()` para CLI.
- `load_config()` lendo SMTP de CLI e ambiente.
- `build_message()` montando `EmailMessage`.
- `send_email()` usando `smtplib.SMTP`, `starttls()`, `login()` e `send_message()`.

Variáveis de ambiente usadas:

```text
SMTP_HOST
SMTP_PORT
SMTP_USER
SMTP_PASSWORD
SMTP_FROM
SMTP_USE_TLS
```

O `README.md` já documenta uso com Gmail e `.env`. O arquivo `GMAIL_SETUP.md` documenta como habilitar envio SMTP com Gmail usando verificação em duas etapas e senha de app.

## Objetivo

Transformar a aplicação numa API REST com FastAPI para envio de e-mails, preservando a funcionalidade SMTP atual e reorganizando o código em Clean Architecture.

A API deve expor um endpoint para envio de e-mail que aceite destinatário, assunto e corpo da mensagem em JSON. As configurações SMTP devem continuar vindo de `.env` ou variáveis de ambiente.

## Requisitos de arquitetura

Organize o código separando responsabilidades em camadas diretamente dentro de `src`.

Estrutura alvo:

```text
mail-sender/
+-- README.md
+-- GMAIL_SETUP.md
+-- .env.example
+-- .gitignore
+-- pyproject.toml
+-- src/
|   +-- __init__.py
|   +-- main.py
|   +-- api/
|   |   +-- __init__.py
|   |   +-- app.py
|   |   +-- routes.py
|   |   +-- schemas.py
|   +-- application/
|   |   +-- __init__.py
|   |   +-- use_cases.py
|   +-- domain/
|   |   +-- __init__.py
|   |   +-- entities.py
|   |   +-- exceptions.py
|   |   +-- ports.py
|   +-- infrastructure/
|       +-- __init__.py
|       +-- config.py
|       +-- dotenv.py
|       +-- smtp_email_sender.py
+-- tests/
    +-- test_*.py
```

Regras obrigatórias de estrutura:

- Mantenha o ponto de entrada da aplicação em `src/main.py`.
- `src/main.py` deve expor a aplicação FastAPI, por exemplo, com uma variável `app`.

Diretrizes:

- A camada `domain` não deve depender de FastAPI, Pydantic, `smtplib` ou detalhes de ambiente.
- A camada `application` deve conter o caso de uso de envio, dependendo apenas de entidades e portas do domínio.
- A camada `infrastructure` deve implementar leitura de configuração e envio SMTP real.
- A camada `api` deve conter FastAPI, schemas de request/response e rotas.
- O endpoint deve chamar o caso de uso, não chamar `smtplib` diretamente.
- Não duplique lógica SMTP entre API, aplicação e infraestrutura.

## Contrato REST

Implemente pelo menos:

```text
POST /api/v1/mail/send
```

Request JSON:

```json
{
  "to": "destino@example.com",
  "subject": "Teste",
  "body": "Mensagem enviada pelo mail-sender"
}
```

Response de sucesso:

```json
{
  "message": "E-mail enviado com sucesso."
}
```

Códigos HTTP esperados:

- `200 OK` ou `202 Accepted` para envio aceito/enviado com sucesso.
- `422 Unprocessable Entity` para payload inválido.
- `500 Internal Server Error` para falha SMTP inesperada.
- `503 Service Unavailable` para configuração SMTP ausente ou inválida, se a aplicação não conseguir enviar por falta de configuração.

Use validação Pydantic para:

- `to` como e-mail válido, se possível usando `EmailStr`.
- `subject` obrigatório e não vazio.
- `body` obrigatório e não vazio.

Se usar `EmailStr`, inclua a dependência necessária no `pyproject.toml`.

## Configuração

Preserve suporte a `.env`, mas mova a lógica para a infraestrutura.

Regras:

- Carregar `.env` automaticamente na inicialização da aplicação.
- Não sobrescrever variáveis de ambiente já existentes.
- Validar `SMTP_PORT` como inteiro entre 1 e 65535.
- Validar `SMTP_USE_TLS` aceitando valores comuns: `true`, `false`, `1`, `0`, `yes`, `no`, `on`, `off`.
- Não expor `SMTP_PASSWORD` em responses, ‘logs’ ou exceções de usuário.
- Manter `.env.example` atualizado.

## Envio SMTP

A implementação SMTP deve:

1. Montar mensagem com `From`, `To`, `Subject` e corpo.
2. Abrir conexão com `smtplib.SMTP(host, port)`.
3. Executar `starttls()` quando `use_tls` estiver habilitado.
4. Executar `login(user, password)` apenas quando usuário e senha forem informados.
5. Enviar com `send_message()`.
6. Encerrar a conexão via context ‘manager’.

## Dependências

Atualize `pyproject.toml` para incluir dependências de runtime e testes.

Sugestão:

```toml
[project]
name = "mail-sender"
version = "0.2.0"
description = "API REST para envio de e-mails via SMTP"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
]

[project.optional-dependencies]
dev = [
    "pytest>=8",
    "pytest-cov>=5",
    "httpx>=0.27",
]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
addopts = "--cov=src --cov-report=term-missing --cov-fail-under=100"
```

Se `EmailStr` for usado, inclua também:

```toml
"pydantic[email]>=2"
```

## Testes

Atualize ou recrie os testes para 100% de cobertura.

Os testes devem cobrir:

- Conversão de booleanos de configuração.
- Carregamento de `.env`.
- `.env` não sobrescreve variáveis existentes.
- Validação de configuração obrigatória.
- Validação de porta SMTP inválida e fora do intervalo.
- Entidade de e-mail ou objeto de comando de envio.
- Caso de uso de envio chamando a porta `EmailSender`.
- Implementação SMTP usando fake/mock de `smtplib.SMTP`, sem rede real.
- Uso de TLS quando habilitado.
- ‘Login’ apenas quando usuário e senha existirem.
- Endpoint `POST /api/v1/mail/send` com sucesso.
- Endpoint `POST /api/v1/mail/send` com payload inválido.
- Endpoint traduzindo erro de configuração para status HTTP apropriado.
- Endpoint traduzindo erro SMTP para status HTTP apropriado.
- Criação da aplicação FastAPI.

Regras dos testes:

- Não enviar e-mails reais.
- Não depender de rede.
- Não depender de credenciais reais.
- Usar `TestClient` ou `httpx` conforme a versão do FastAPI.
- Usar fakes/mocks para a porta de envio.
- Rodar com `python -m pytest`.
- A cobertura deve ser 100%.

## README e documentação

Atualize `README.md` para documentar:

- Descrição da API REST.
- Requisitos: Python 3.12.
- Instalação das dependências.
- Configuração com `.env`.
- Como rodar a API com Uvicorn.
- Exemplo de request com PowerShell usando `Invoke-RestMethod`.
- Como executar os testes com cobertura.
- Link para `GMAIL_SETUP.md`.
- Aviso para não versionar credenciais.

Exemplo de execução:

```powershell
python -m uvicorn main:app --app-dir src --reload
```

Exemplo de request:

```powershell
Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/mail/send" `
  -ContentType "application/json" `
  -Body '{"to":"janedoe@gmail.com","subject":"Teste Gmail","body":"Mensagem enviada pelo mail-sender via API REST"}'
```

Atualize `GMAIL_SETUP.md` somente se a mudança da CLI para API exigir ajuste no exemplo de envio.

## Compatibilidade com CLI

A API REST passa a ser a ‘interface’ principal da aplicação. A CLI atual pode ser removida.

Se manter a CLI, ela deve reutilizar as mesmas camadas de aplicação, domínio e infraestrutura usadas pela API, sem duplicar lógica de SMTP.

## Qualidade

- A codificação deve ser feita em inglês, mas todos os comentários, documentação e exemplos devem ser escritos em português do Brasil.
- Use nomes claros e módulos pequenos.
- Prefira injeção de dependências explícita.
- Evite estado global mutável, exceto configuração de composição da app.
- Não misture regras de negócio com FastAPI.
- Não misture SMTP com schemas HTTP.
- Mantenha mensagens de erro claras para o usuário.
- Não exponha senhas.
- Mantenha compatibilidade com Windows/PowerShell.
- Escreva os textos de documentação em português do Brasil.

## Critérios de aceite

A tarefa está concluída quando:

- A API FastAPI existe e expõe `POST /api/v1/mail/send`.
- O ponto de entrada está em `src/main.py`.
- O código está organizado em `src/api`, `src/application`, `src/domain` e `src/infrastructure`.
- A configuração SMTP continua funcionando por `.env` e variáveis de ambiente.
- O envio SMTP real está encapsulado na infraestrutura.
- Os testes não enviam e-mail real.
- `python -m pytest` passa.
- A cobertura é 100%.
- `README.md`, `.env.example` e, se necessário, `GMAIL_SETUP.md` estão atualizados em português do Brasil.
- A aplicação pode ser iniciada com Uvicorn e receber request JSON para envio.

## Perguntas pendentes, se precisar refinar antes de implementar

Caso algum ponto seja importante para o produto final, pergunte antes de implementar:

- A API deve retornar `200 OK` apenas após envio SMTP concluído ou `202 Accepted` ao aceitar a requisição?
- O corpo do e-mail deve aceitar HTML ou apenas texto puro?
- Deve haver suporte a anexos?
- Deve haver envio para múltiplos destinatários, CC ou BCC?
- Deve haver autenticação na API REST antes de permitir envio?
- A CLI atual deve ser preservada ou removida?
