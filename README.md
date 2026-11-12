# Flasky — aplicação modular com Mailgun

Aplicação Flask com cadastro, listagem, edição e exclusão de usuários, banco SQLite e notificação de novo cadastro via API Mailgun.

## Estrutura

- `flasky.py`: ponto de entrada.
- `config.py`: configurações por variáveis de ambiente.
- `app/__init__.py`: factory `create_app()`.
- `app/routes.py`: rotas e validações.
- `app/database.py`: SQLite.
- `app/email_service.py`: integração HTTP com Mailgun (`requests`), sem SDK Resend.
- `app/templates/` e `app/static/`: interface.

## Rodar localmente

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux: source .venv/bin/activate
pip install -r requirements.txt
python flasky.py
```

Abra `http://127.0.0.1:5000`.

## Configuração Mailgun

Configure no ambiente do servidor (não coloque segredos no GitHub):

- `MAILGUN_API_KEY`: chave privada da API Mailgun.
- `MAILGUN_DOMAIN`: domínio Mailgun usado para envio (incluindo sandbox, se aplicável).
- `MAIL_FROM`: remetente permitido nesse domínio, por exemplo `Sistema Aula <postmaster@DOMINIO>`.
- `MAILGUN_API_BASE`: `https://api.mailgun.net` (ou `https://api.eu.mailgun.net` se sua conta estiver na região EU).
- `ADMIN_EMAIL`: `flaskaulasweb@zohomail.com`.
- `INSTITUTIONAL_EMAIL`: e-mail institucional do aluno.
- `STUDENT_NAME`: nome do aluno.
- `PRONTUARIO`: prontuário.
- `SECRET_KEY`: chave aleatória forte.
- `DATABASE_PATH`: caminho absoluto gravável para o SQLite.

A notificação é enviada para o e-mail administrativo e o institucional. **O usuário recém-cadastrado não recebe e-mail**, conforme definido para esta atividade. O corpo inclui prontuário, nome do aluno e usuário cadastrado. Se Mailgun falhar, o cadastro permanece salvo e a página mostra um aviso; o detalhe técnico fica no log do servidor.

Para domínio Sandbox, adicione/autorize os destinatários no painel Mailgun. Erros HTTP 401/403 geralmente indicam chave, domínio, remetente ou destinatário não autorizado.

## Publicar no PythonAnywhere

1. Faça backup da pasta `mysite` e do banco SQLite atual.
2. Envie o conteúdo deste ZIP para `/home/SEU_USUARIO/mysite/` (substitua os arquivos antigos; não apague o banco se quiser preservar cadastros).
3. No console Bash:

```bash
cd /home/ChantalVeltmeyer/mysite
source /home/ChantalVeltmeyer/.venv/bin/activate
pip install -r requirements.txt
python -m py_compile flasky.py config.py app/*.py
```

4. Em **Web > Code > WSGI configuration file**, use:

```python
import sys
path = '/home/ChantalVeltmeyer/mysite'
if path not in sys.path:
    sys.path.insert(0, path)
from flasky import app as application
```

5. Em **Web > Environment variables**, configure as variáveis Mailgun acima. Use os valores reais que já funcionaram no teste HTTP 200/Queued; não publique a chave no GitHub.
6. Confirme que `DATABASE_PATH` aponta para um arquivo em `mysite/instance/` e que a pasta tem permissão de escrita.
7. Clique em **Reload**. Se houver erro, consulte o error log do PythonAnywhere.

## Observação importante de segurança

Esta é uma aplicação didática CRUD. O acesso à lista, edição e exclusão exige autenticação. Para uso em produção, revise também as permissões por perfil e implemente proteção CSRF.
