import requests
from flask import current_app, url_for

def _mailgun_send(recipient, subject, body):
    cfg = current_app.config
    api_key = cfg.get("MAILGUN_API_KEY")
    domain = cfg.get("MAILGUN_DOMAIN")
    sender = cfg.get("MAIL_FROM")

    if not all((api_key, domain, sender)):
        current_app.logger.warning("Mailgun não está completamente configurado.")
        return False

    url = (
        f"{cfg.get('MAILGUN_API_BASE', 'https://api.mailgun.net').rstrip('/')}"
        f"/v3/{domain}/messages"
    )

    try:
        response = requests.post(
            url,
            auth=("api", api_key),
            data={
                "from": sender,
                "to": recipient,
                "subject": subject,
                "text": body,
            },
            timeout=20,
        )
        response.raise_for_status()
        return True
    except requests.RequestException as exc:
        detail = getattr(getattr(exc, "response", None), "text", str(exc))
        current_app.logger.exception("Falha no envio Mailgun: %s", detail)
        return False

def send_confirmation_email(user, token):
    confirmation_url = url_for(
        "main.confirm_email",
        token=token,
        _external=True
    )
    body = (
        f"Olá, {user['name']}!\n\n"
        "Seu cadastro foi realizado. Para confirmar seu endereço de e-mail, "
        "acesse o link abaixo:\n\n"
        f"{confirmation_url}\n\n"
        "Se você não realizou esse cadastro, ignore esta mensagem."
    )
    return _mailgun_send(
        user["email"],
        "Confirme seu cadastro no Flasky",
        body
    )

def send_new_user_notification(user):
    """Envia aviso administrativo, sem substituir o e-mail de confirmação."""
    cfg = current_app.config
    recipients = []
    for address in (cfg.get("ADMIN_EMAIL"), cfg.get("INSTITUTIONAL_EMAIL")):
        if address and address not in recipients:
            recipients.append(address)

    if not recipients:
        return False, "Nenhum destinatário administrativo foi configurado."

    body = (
        "Um novo usuário foi cadastrado na aplicação.\n\n"
        f"Prontuário: {cfg.get('PRONTUARIO')}\n"
        f"Nome do aluno: {cfg.get('STUDENT_NAME')}\n"
        f"Usuário cadastrado: {user['username']}\n"
        f"Nome: {user['name']}\n"
        f"E-mail informado: {user['email']}\n"
        f"Função: {user['role']}\n"
    )

    sent = _mailgun_send(
        recipients,
        "Novo usuário cadastrado",
        body
    )
    if sent:
        return True, "Notificação administrativa enviada."
    return False, "Não foi possível enviar a notificação administrativa."
