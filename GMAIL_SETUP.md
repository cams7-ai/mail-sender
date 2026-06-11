# Habilitar envio de e-mail pelo Gmail

Este guia mostra como configurar uma conta Gmail para envio de e-mails via SMTP usando esta aplicação.

## 1. Ativar a verificação em duas etapas

1. Acesse a sua Conta Google:

   https://myaccount.google.com/security

2. Entre com a conta que será usada para envio. Exemplo:

   `seu-email@gmail.com`

3. Na seção **Como você faz login no Google**, selecione **Verificação em duas etapas**.
4. Siga as instruções do Google até concluir a ativação.

## 2. Criar uma senha de app

1. Acesse:

   https://myaccount.google.com/apppasswords

2. Confirme o login, se solicitado.
3. Crie uma senha de app para uso com e-mail/SMTP.
4. Copie a senha gerada pelo Google.

Use essa senha de app no projeto. Não use a senha principal da conta Gmail.

## 3. Configurar o arquivo `.env`

Atualize o arquivo `.env` com os dados da conta Gmail:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD='senha de app gerada pelo google'
SMTP_FROM=seu-email@gmail.com
SMTP_USE_TLS=true
```

O valor de `SMTP_FROM` deve ser o mesmo e-mail autenticado em `SMTP_USER`, a menos que outro endereco esteja configurado no Gmail como remetente autorizado.

## 4. Enviar um e-mail de teste

Execute:

```bash
python .\src\main.py --to outro-email@gmail.com --subject "Teste Gmail" --body "Mensagem enviada pelo mail-sender via Gmail"
```

Se estiver usando o ambiente virtual do projeto:

```bash
.\.venv\Scripts\python.exe .\src\main.py --to outro-email@gmail.com --subject "Teste Gmail" --body "Mensagem enviada pelo mail-sender via Gmail"
```

## Erro comum: Username and Password not accepted

Se aparecer um erro parecido com:

```text
535 5.7.8 Username and Password not accepted
```

Verifique:

- `SMTP_PASSWORD` deve ser uma senha de app do Google, não a senha normal da conta.
- A verificação em duas etapas precisa estar ativa.
- `SMTP_USER` deve ser a conta Gmail usada para gerar a senha de app.
- `SMTP_FROM` deve ser o mesmo e-mail de `SMTP_USER` ou um alias autorizado no Gmail.
