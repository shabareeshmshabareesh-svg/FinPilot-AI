from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash
)

from werkzeug.security import generate_password_hash, check_password_hash

from flask_login import login_user, logout_user, login_required

from forms.auth_forms import (
    RegisterForm,
    LoginForm
)

from models.database import db
from models.user import User


auth = Blueprint("auth", __name__)


# ==========================
# REGISTER
# ==========================

@auth.route("/register", methods=["GET", "POST"])
def register():

    form = RegisterForm()

    if form.validate_on_submit():

        # ---------------------------------
        # EXISTING EMAIL
        # ---------------------------------
        # Neutral response. Never reveal
        # whether an account exists.

        existing_user = User.query.filter_by(
            email=form.email.data
        ).first()

        if existing_user:

            flash(
                "If an account already exists for this email, "
                "please log in instead.",
                "info"
            )

            return redirect(url_for("auth.login"))

        # ---------------------------------
        # NEW ACCOUNT
        # ---------------------------------

        hashed_password = generate_password_hash(
            form.password.data
        )

        new_user = User(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        flash(
            "Your account has been created. Please log in.",
            "success"
        )

        return redirect(url_for("auth.login"))

    return render_template(
        "auth/register.html",
        form=form
    )


# ==========================
# LOGIN
# ==========================

@auth.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(
            email=form.email.data
        ).first()

        if user and check_password_hash(
            user.password,
            form.password.data
        ):

            login_user(user)

            flash(
                f"Welcome back, {user.username}!",
                "success"
            )

            return redirect(
              url_for("dashboard.dashboard_home")
            )

        flash(
            "Invalid email or password.",
            "danger"
        )

    return render_template(
        "auth/login.html",
        form=form
    )


# ==========================
# LOGOUT
# ==========================

@auth.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "You have been logged out.",
        "info"
    )

    return redirect(
        url_for("home.index")
    )