# Prompt para Codex GPT-5.5 - mail-sender

Você deve criar uma aplicação Python 3.12 chamada `mail-sender` para enviar e-mails via SMTP, com estrutura moderna de projeto, configuração segura por variáveis de ambiente e testes automatizados.

## Contexto atual

Existe atualmente um arquivo `main.py` na raiz com conteúdo padrão gerado pelo PyCharm. Ele deve ser substituído pela implementação real, movendo a entrada da aplicação para `src/main.py` conforme a estrutura alvo.

## Estrutura alvo

Crie ou ajuste a estrutura para ficar assim:

```text
mail-sender/
+-- pyproject.toml
+-- README.md
+-- .gitignore
+-- src/
|   +-- main.py
+-- tests/
    +-- test_main.py
```

Se o arquivo `main.py` existir na raiz, remova-o apos migrar a implementacao para `src/main.py`, desde que isso nao apague alteracoes relevantes do usuario.

## Objetivo funcional

A aplicação deve enviar um e-mail usando SMTP.

Ela deve permitir configurar, no minimo:

- Servidor SMTP.
- Porta SMTP.
- Usuário SMTP.
- Senha SMTP.
- Remetente.
- Destinatário.
- Assunto.
- Corpo do e-mail.
- Uso de TLS/STARTTLS.

As configurações sensíveis não devem ficar hardcoded no código. Use variáveis de ambiente.

## Interface de uso

Implemente uma CLI simples em `src/main.py` usando apenas biblioteca padrão do Python, salvo se houver justificativa clara para dependência externa.

A CLI deve aceitar argumentos para os campos não sensíveis e ler credenciais/configurações padrão de variáveis de ambiente.

Variáveis de ambiente recomendadas:

```text
SMTP_HOST
SMTP_PORT
SMTP_USER
SMTP_PASSWORD
SMTP_FROM
SMTP_USE_TLS
```

Argumentos CLI recomendados:

```text
--to destinatario@example.com
--subject "Assunto do email"
--body "Conteudo do email"
--from remetente@example.com
--host smtp.example.com
--port 587
--user usuário
--password senha
--use-tls
--no-use-tls
```

Regras:

- Argumentos CLI devem ter precedência sobre variáveis de ambiente.
- Se um campo obrigatorio estiver ausente, a aplicação deve exibir erro claro e retornar codigo de saida diferente de zero.
- `SMTP_PORT` deve ser convertido para inteiro e validado.
- `SMTP_USE_TLS` deve aceitar valores comuns como `true`, `false`, `1`, `0`, `yes`, `no`.
- A senha deve poder vir de `SMTP_PASSWORD` ou de `--password`, mas não deve ser exibida em ‘logs’ ou mensagens de erro.

## Implementação esperada

Em `src/main.py`, organize o código em funções testáveis. Sugestão:

- `parse_bool(value: str | bool | None) -> bool`
- `build_parser() -> argparse.ArgumentParser`
- `load_config(args: argparse.Namespace) -> MailConfig`
- `build_message(config: MailConfig) -> email.message.EmailMessage`
- `send_email(config: MailConfig) -> None`
- `main(argv: list[str] | None = None) -> int`

Use `dataclasses.dataclass` para representar a configuração, por exemplo `MailConfig`.

Use bibliotecas padrão:

- `argparse`
- `dataclasses`
- `email.message.EmailMessage`
- `os`
- `smtplib`
- `ssl`, se necessário
- `sys`

Fluxo esperado de envio:

1. Montar `EmailMessage` com `From`, `To`, `Subject` e corpo.
2. Abrir conexao SMTP com host e porta configurados.
3. Aplicar `starttls()` quando TLS estiver habilitado.
4. Fazer ‘login’ quando usuario e senha forem informados.
5. Enviar a mensagem com `send_message()`.
6. Encerrar conexao corretamente usando context ‘manager’.

## Pyproject

Crie `pyproject.toml` com configuração minima para Python 3.12.

Inclua dependências de desenvolvimento para testes, preferencialmente `pytest`.

Exemplo de requisitos:

```toml
[project]
name = "mail-sender"
version = "0.1.0"
description = "Aplicação simples para envio de emails via SMTP"
requires-python = ">=3.12"

[project.optional-dependencies]
dev = ["pytest>=8"]
```

Se optar por uma ferramenta de ‘build’ especifica, mantenha simples e documente no README.

## Testes

Crie testes em `tests/test_main.py` cobrindo pelo menos:

- Conversão de booleanos por `parse_bool`.
- Carregamento de configuração combinando CLI e variáveis de ambiente.
- Validação de campos obrigatórios.
- Montagem correta da mensagem (`From`, `To`, `Subject`, corpo).
- Envio usando mock/fake de `smtplib.SMTP`, sem enviar e-mail real.
- Uso de `starttls()` quando TLS estiver habilitado.
- Login somente quando usuário e senha forem informados.

Os testes não devem depender de rede, SMTP real ou credenciais reais.

## README

Crie `README.md` com:

- Descrição curta do projeto.
- Requisitos: Python 3.12.
- Como instalar dependências de desenvolvimento.
- Como executar os testes.
- Como configurar variáveis de ambiente.
- Exemplo de execução da CLI.
- Aviso para não versionar credenciais.

## Qualidade e segurança

- Não enviar e-mails reais durante testes.
- Não registrar senha ou credenciais sensíveis.
- Mensagens de erro devem ser claras para o usuário final.
- Código deve ser simples, idiomático e fácil de testar.
- Evite dependências externas desnecessárias.
- Mantenha compatibilidade com Windows/PowerShell.

## Critérios de aceite

A tarefa esta concluída quando:

- `pyproject.toml` existe e declara Python 3.12.
- `src/main.py` implementa a CLI e o envio SMTP.
- `tests/test_main.py` cobre os comportamentos principais sem rede real.
- `README.md` documenta instalação, configuração e uso.
- `python -m pytest` passa.
- A aplicação pode ser executada por comando semelhante a:

```powershell
$env:SMTP_HOST="smtp.example.com"
$env:SMTP_PORT="587"
$env:SMTP_USER="usuario@example.com"
$env:SMTP_PASSWORD="senha-segura"
$env:SMTP_FROM="usuario@example.com"
$env:SMTP_USE_TLS="true"
python .\src\main.py --to destino@example.com --subject "Teste" --body "Email de teste"
```

## Perguntas pendentes, se precisar refinar antes de implementar

Caso algum ponto seja importante para o produto final, pergunte antes de implementar:

- O provedor SMTP alvo será Gmail, Outlook, servidor corporativo ou outro?
- O corpo do e-mail precisa aceitar HTML ou apenas texto puro?
- Deve haver suporte a anexos?
- Deve haver envio para múltiplos destinatários, CC ou BCC?
- A aplicação deve ser apenas CLI ou também expor funções reutilizáveis como biblioteca?
