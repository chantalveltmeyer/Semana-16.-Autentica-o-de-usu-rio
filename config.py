import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "troque-por-uma-chave-forte")
    DATABASE = os.getenv(
        "DATABASE_PATH",
        str(BASE_DIR / "instance" / "usuarios.sqlite")
    )

    MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY", os.getenv("API_KEY", ""))
    MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN", "")
    MAILGUN_API_BASE = os.getenv("MAILGUN_API_BASE", "https://api.mailgun.net")
    MAIL_FROM = os.getenv("MAIL_FROM", os.getenv("API_FROM", ""))

    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "flaskaulasweb@zohomail.com")
    INSTITUTIONAL_EMAIL = os.getenv(
        "INSTITUTIONAL_EMAIL",
        "chantal.veltmeyer@aluno.ifsp.edu.br"
    )
    STUDENT_NAME = os.getenv(
        "STUDENT_NAME",
        "Chantal Nicole Veltmeyer Souza"
    )
    PRONTUARIO = os.getenv(
        "PRONTUARIO",
        os.getenv("STUDENT_RECORD", "PT3039471")
    )

    CONFIRMATION_TOKEN_MAX_AGE = 60 * 60 * 24
