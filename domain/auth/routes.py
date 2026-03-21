import random
import smtplib
from email.mime.text import MIMEText
from flask import render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from domain.auth import auth_bp
from domain.db.models import db, User


def send_verification_email(to_email, code):
    smtp_host = current_app.config["MAIL_SERVER"]
    smtp_port = int(current_app.config["MAIL_PORT"])
    smtp_user = current_app.config["MAIL_USERNAME"]
    smtp_pass = current_app.config["MAIL_PASSWORD"]
    sender = current_app.config["MAIL_SENDER"]

    body = "Your verification code: {}\n\nEnter this code to activate your account.".format(code)
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = "Account Verification Code"
    msg["From"] = sender
    msg["To"] = to_email

    try:
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10) as server:
                server.login(smtp_user, smtp_pass)
                server.sendmail(sender, [to_email], msg.as_string())
        elif smtp_port == 25:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.sendmail(sender, [to_email], msg.as_string())
        else:
            with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.sendmail(sender, [to_email], msg.as_string())
        return True
    except Exception as e:
        print("Mail error: {}".format(e))
        return False


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm_password", "")

        if not username or not email or not password:
            flash("All fields are required.", "danger")
            return render_template("auth/register.html")

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return render_template("auth/register.html")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "danger")
            return render_template("auth/register.html")

        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "danger")
            return render_template("auth/register.html")

        if User.query.filter_by(username=username).first():
            flash("Username already taken.", "danger")
            return render_template("auth/register.html")

        code = "{:06d}".format(random.randint(0, 999999))
        user = User(username=username, email=email, verification_code=code)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        session["pending_user_id"] = user.id
        send_verification_email(email, code)
        flash("Please check your email for activation.", "info")
        return redirect(url_for("auth.verify"))

    return render_template("auth/register.html")


@auth_bp.route("/verify", methods=["GET", "POST"])
def verify():
    user_id = session.get("pending_user_id")
    if not user_id:
        return redirect(url_for("auth.register"))

    user = User.query.get(user_id)
    if not user:
        return redirect(url_for("auth.register"))

    if user.is_active:
        return redirect(url_for("home"))

    if request.method == "POST":
        code = request.form.get("code", "").strip()
        if code == user.verification_code:
            user.is_active = True
            user.verification_code = None
            db.session.commit()
            session.pop("pending_user_id", None)
            login_user(user)
            flash("Account activated! Welcome, {}.".format(user.username), "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid code. Please try again.", "danger")

    return render_template("auth/verify.html", email=user.email)


@auth_bp.route("/login", methods=["POST"])
def login():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        flash("Invalid email or password.", "danger")
        return redirect(url_for("home"))

    if not user.is_active:
        session["pending_user_id"] = user.id
        flash("Please verify your email first.", "warning")
        return redirect(url_for("auth.verify"))

    login_user(user)
    return redirect(url_for("home"))


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))
