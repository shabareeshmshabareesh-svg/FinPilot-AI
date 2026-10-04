import logging

from datetime import date, timedelta

from flask import (
    Flask,
    render_template
)
from flask_login import current_user

from flask_wtf.csrf import (
    CSRFError,
    CSRFProtect
)

from config import Config

from models.database import db
from models.user import User
from models.expense import Expense
from models.income import Income

from routes.home import home
from routes.auth import auth
from routes.dashboard import dashboard
from routes.expense import expense
from routes.budget import budget
from routes.analytics import analytics
from routes.income import income
from routes.goal import goal
from routes.coach import coach

from utils.login_manager import login_manager

from utils.financial_alerts import (
    generate_financial_alerts
)


# =========================================
# CREATE APPLICATION
# =========================================

app = Flask(__name__)

app.config.from_object(Config)


# =========================================
# LOGGING
# =========================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


# =========================================
# CSRF PROTECTION
# =========================================
#
# Every POST request must carry a valid
# CSRF token. This covers the plain HTML
# delete forms and the AJAX endpoints.

csrf = CSRFProtect()

csrf.init_app(app)


# =========================================
# DATABASE
# =========================================

db.init_app(app)


# =========================================
# LOGIN MANAGER
# =========================================

login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):

    return db.session.get(
        User,
        int(user_id)
    )


# =========================================
# REGISTER BLUEPRINTS
# =========================================

app.register_blueprint(home)

app.register_blueprint(auth)

app.register_blueprint(dashboard)

app.register_blueprint(expense)

app.register_blueprint(budget)

app.register_blueprint(analytics)

app.register_blueprint(income)

app.register_blueprint(goal)

app.register_blueprint(coach)


# =========================================
# GLOBAL FINANCIAL ALERTS
# =========================================

def _build_financial_alerts():
    """
    Build the alert list used by the navbar and
    the dashboard.

    Callers get the result through the
    inject_financial_alerts context processor,
    which makes sure a failure here can never
    break page rendering.
    """

    # -------------------------------------
    # Guest user
    # -------------------------------------

    if not current_user.is_authenticated:

        return {
            "financial_alerts": []
        }


    today = date.today()


    # =====================================
    # MONTH START
    # =====================================

    month_start = today.replace(
        day=1
    )


    # =====================================
    # NEXT MONTH START
    # =====================================
    #
    # "This month" covers the whole calendar
    # month so every page reports the same
    # totals as the dashboard.

    next_month_start = (
        month_start + timedelta(days=32)
    ).replace(day=1)


    # =====================================
    # MONTH EXPENSES
    # =====================================

    expenses = Expense.query.filter(

        Expense.user_id ==
        current_user.id,

        Expense.date >=
        month_start,

        Expense.date <
        next_month_start

    ).all()


    monthly_spending = sum(

        expense.amount

        for expense in expenses

    )


    # =====================================
    # MONTH INCOME
    # =====================================

    incomes = Income.query.filter(

        Income.user_id ==
        current_user.id,

        Income.date >=
        month_start,

        Income.date <
        next_month_start

    ).all()


    monthly_income = sum(

        income.amount

        for income in incomes

    )


    # =====================================
    # MONTHLY BUDGET
    # =====================================

    monthly_allowance = (

        current_user.monthly_budget or 0

    )


    # =====================================
    # MONTHLY SAVINGS
    # =====================================

    monthly_savings = (

        monthly_income -
        monthly_spending

    )


    # =====================================
    # DAYS REMAINING
    # =====================================

    if today.month == 12:

        next_month = date(

            today.year + 1,

            1,

            1

        )

    else:

        next_month = date(

            today.year,

            today.month + 1,

            1

        )


    days_remaining = max(

        (
            next_month -
            today
        ).days,

        1

    )


    # =====================================
    # REMAINING BUDGET
    # =====================================

    remaining = max(

        monthly_allowance -
        monthly_spending,

        0

    )


    # =====================================
    # SAFE DAILY SPENDING
    # =====================================

    if remaining > 0:

        safe_daily_spending = (

            remaining /
            days_remaining

        )

    else:

        safe_daily_spending = 0


    # =====================================
    # CATEGORY TOTALS
    # =====================================

    category_totals = {}


    for expense_item in expenses:

        category = expense_item.category


        if category not in category_totals:

            category_totals[category] = 0


        category_totals[category] += (
            expense_item.amount
        )


    # =====================================
    # GENERATE ALERTS
    # =====================================

    financial_alerts = (
        generate_financial_alerts(

            monthly_income=
                monthly_income,

            monthly_spending=
                monthly_spending,

            monthly_allowance=
                monthly_allowance,

            monthly_savings=
                monthly_savings,

            safe_daily_spending=
                safe_daily_spending,

            category_totals=
                category_totals

        )
    )


    return {

        "financial_alerts":
            financial_alerts

    }


# =========================================
# GLOBAL FINANCIAL ALERTS
# =========================================
#
# Wrapped so an unexpected query failure
# degrades to "no alerts" instead of breaking
# every page in the application.

@app.context_processor
def inject_financial_alerts():

    try:

        return _build_financial_alerts()

    except Exception as error:

        app.logger.warning(
            "Financial alerts unavailable: %s",
            error
        )

        return {
            "financial_alerts": []
        }


# =========================================
# ERROR HANDLERS
# =========================================

@app.errorhandler(404)
def handle_not_found(error):

    return render_template(
        "errors/error.html",
        code=404,
        title="Page not found",
        message=(
            "That page does not exist. "
            "Use the navigation above to get back "
            "to your dashboard."
        )
    ), 404


@app.errorhandler(500)
def handle_server_error(error):

    app.logger.error(
        "Internal server error: %s",
        error
    )

    try:

        db.session.rollback()

    except Exception:

        pass

    return render_template(
        "errors/error.html",
        code=500,
        title="Something went wrong",
        message=(
            "FinPilot hit an unexpected problem. "
            "Please go back and try again."
        )
    ), 500


@app.errorhandler(CSRFError)
def handle_csrf_error(error):

    app.logger.warning(
        "CSRF validation failed: %s",
        error.description
    )

    return render_template(
        "errors/error.html",
        code=400,
        title="Your session expired",
        message=(
            "For your security this form was rejected. "
            "Please reload the page and try again."
        )
    ), 400


# =========================================
# CREATE DATABASE TABLES
# =========================================

with app.app_context():

    db.create_all()


# =========================================
# RUN APPLICATION
# =========================================

if __name__ == "__main__":

    app.run(
        debug=False
    )