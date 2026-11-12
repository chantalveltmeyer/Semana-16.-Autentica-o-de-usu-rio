import re
from functools import wraps
from sqlite3 import IntegrityError

from flask import (
    Blueprint, current_app, flash, redirect, render_template,
    request, session, url_for
)
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from werkzeug.security import check_password_hash, generate_password_hash

from .database import get_db
from .email_service import (
    send_confirmation_email,
    send_new_user_notification,
)

main = Blueprint("main", __name__)

def valid_email(value):
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value or ""))

def token_serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if "user_id" not in session:
            flash("Entre na sua conta para visualizar esta página.", "warning")
            return redirect(url_for("main.login"))
        return view(*args, **kwargs)
    return wrapped_view

@main.route("/")
def index():
    # Visitantes podem acessar a página inicial sem fazer login.
    if "user_id" not in session:
        return render_template(
            "index.html",
            users=None,
            logged_user=None
        )

    db = get_db()
    logged_user = db.execute(
        "SELECT id, name, username FROM users WHERE id = ?",
        (session["user_id"],)
    ).fetchone()

    if logged_user is None:
        session.clear()
        return redirect(url_for("main.index"))

    users = db.execute("""
        SELECT id, name, username, email, role, created_at, confirmed
        FROM users
        ORDER BY id DESC
    """).fetchall()

    return render_template(
        "index.html",
        users=users,
        logged_user=logged_user
    )

@main.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        db = get_db()
        user = db.execute(
            "SELECT id, username, password_hash, confirmed FROM users "
            "WHERE username = ? COLLATE NOCASE",
            (username,)
        ).fetchone()

        if user is None or not check_password_hash(user["password_hash"], password):
            flash("Usuário ou senha inválidos.", "error")
        else:
            session.clear()
            session["user_id"] = user["id"]
            if not user["confirmed"]:
                flash(
                    "Sua conta ainda não foi confirmada pelo e-mail. "
                    "A lista está disponível, conforme a atividade.",
                    "warning"
                )
            else:
                flash("Login realizado com sucesso.", "success")
            return redirect(url_for("main.index"))

    return render_template("login.html")

@main.route("/logout", methods=["POST"])
@login_required
def logout():
    session.clear()
    flash("Você saiu do sistema.", "success")
    return redirect(url_for("main.login"))

@main.route("/cadastro", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not all((name, username, email, password)):
            flash("Preencha todos os campos obrigatórios.", "error")
        elif not valid_email(email):
            flash("Informe um endereço de e-mail válido.", "error")
        elif len(password) < 8:
            flash("A senha deve ter pelo menos 8 caracteres.", "error")
        else:
            db = get_db()
            try:
                cursor = db.execute("""
                    INSERT INTO users
                    (name, username, email, password_hash, role, confirmed)
                    VALUES (?, ?, ?, ?, 'User', 0)
                """, (
                    name, username, email,
                    generate_password_hash(password)
                ))
                db.commit()

                user = {
                    "id": cursor.lastrowid,
                    "name": name,
                    "username": username,
                    "email": email,
                    "role": "User",
                }
                token = token_serializer().dumps(
                    user["id"],
                    salt="email-confirmation"
                )
                confirmation_sent = send_confirmation_email(user, token)
                send_new_user_notification(user)

                if confirmation_sent:
                    flash(
                        "Cadastro realizado. Enviamos um link de confirmação "
                        "para o e-mail informado.",
                        "success"
                    )
                else:
                    flash(
                        "Cadastro realizado, mas não foi possível enviar o "
                        "e-mail de confirmação. Verifique o Mailgun.",
                        "warning"
                    )
                return redirect(url_for("main.login"))

            except IntegrityError:
                db.rollback()
                flash("Este nome de usuário já está cadastrado.", "error")

    return render_template("register.html")

@main.route("/confirmar/<token>")
def confirm_email(token):
    try:
        user_id = token_serializer().loads(
            token,
            salt="email-confirmation",
            max_age=current_app.config["CONFIRMATION_TOKEN_MAX_AGE"]
        )
    except SignatureExpired:
        flash("O link de confirmação expirou. Solicite um novo cadastro.", "error")
        return redirect(url_for("main.login"))
    except BadSignature:
        flash("Link de confirmação inválido.", "error")
        return redirect(url_for("main.login"))

    db = get_db()
    cursor = db.execute(
        "UPDATE users SET confirmed = 1 WHERE id = ?",
        (user_id,)
    )
    db.commit()

    if cursor.rowcount:
        flash("Seu e-mail foi confirmado com sucesso. Você já pode entrar.", "success")
    else:
        flash("Usuário não encontrado.", "error")

    return redirect(url_for("main.login"))

@main.route("/editar/<int:user_id>", methods=["GET", "POST"])
@login_required
def edit_user(user_id):
    db = get_db()
    user = db.execute("""
        SELECT id, name, username, email, role
        FROM users WHERE id = ?
    """, (user_id,)).fetchone()

    if user is None:
        flash("Usuário não encontrado.", "error")
        return redirect(url_for("main.index"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not all((name, username, email)):
            flash("Preencha todos os campos obrigatórios.", "error")
        elif not valid_email(email):
            flash("Informe um endereço de e-mail válido.", "error")
        elif password and len(password) < 8:
            flash("A nova senha deve ter pelo menos 8 caracteres.", "error")
        else:
            try:
                if password:
                    db.execute("""
                        UPDATE users
                        SET name = ?, username = ?, email = ?, password_hash = ?
                        WHERE id = ?
                    """, (
                        name, username, email,
                        generate_password_hash(password), user_id
                    ))
                else:
                    db.execute("""
                        UPDATE users
                        SET name = ?, username = ?, email = ?
                        WHERE id = ?
                    """, (name, username, email, user_id))
                db.commit()
                flash("Usuário atualizado com sucesso.", "success")
                return redirect(url_for("main.index"))
            except IntegrityError:
                db.rollback()
                flash("Esse nome de usuário já pertence a outra conta.", "error")

            user = {
                "id": user_id, "name": name, "username": username,
                "email": email, "role": "User"
            }

    return render_template("edit.html", user=user)

@main.route("/excluir/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id):
    db = get_db()
    cursor = db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()

    if cursor.rowcount:
        flash("Usuário excluído.", "success")
    else:
        flash("Usuário não encontrado.", "error")
    return redirect(url_for("main.index"))
