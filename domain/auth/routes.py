import random
import string
import subprocess
import sys
import os
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from domain.auth import auth_bp
from domain.db.models import db, User

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SEND_SCRIPT = os.path.join(BASE_DIR, "send_email.py")
SEND_RESET_SCRIPT = os.path.join(BASE_DIR, "send_reset_email.py")


def send_reset_password_email(to_email, new_password):
    try:
        result = subprocess.call([sys.executable, SEND_RESET_SCRIPT, to_email, new_password])
        return result == 0
    except Exception as e:
        print("Mail subprocess error: {}".format(e))
        return False


def generate_password(length=10):
    chars = string.ascii_letters + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def send_verification_email(to_email, code):
    try:
        result = subprocess.call([sys.executable, SEND_SCRIPT, to_email, code])
        return result == 0
    except Exception as e:
        print("Mail subprocess error: {}".format(e))
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
        code = "{:06d}".format(random.randint(0, 999999))
        user.verification_code = code
        db.session.commit()
        session["pending_user_id"] = user.id
        send_verification_email(user.email, code)
        flash("Please check your email for activation.", "info")
        return redirect(url_for("auth.verify"))

    login_user(user)
    return redirect(url_for("home"))


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        user = User.query.filter_by(email=email).first()

        if user and user.is_active:
            new_password = generate_password()
            user.set_password(new_password)
            db.session.commit()
            send_reset_password_email(email, new_password)

        # Always show the same message to avoid email enumeration
        flash("If that email is registered, a new password has been sent.", "info")
        return redirect(url_for("auth.forgot_password"))

    return render_template("auth/forgot_password.html")
