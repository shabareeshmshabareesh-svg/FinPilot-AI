# =========================================================
# FINPILOT HOME ROUTE
# =========================================================

from datetime import date

from flask import Blueprint, render_template

from flask_login import current_user

from sqlalchemy import func

from models.database import db
from models.income import Income
from models.expense import Expense


# =========================================================
# BLUEPRINT
# =========================================================

home = Blueprint(
    "home",
    __name__
)


# =========================================================
# HOME
# =========================================================

@home.route("/")
def index():

    # =====================================================
    # DEFAULT VALUES
    # =====================================================

    monthly_income = 0.0
    monthly_spending = 0.0
    monthly_savings = 0.0
    savings_rate = 0.0

    # =====================================================
    # CURRENT MONTH
    # =====================================================

    today = date.today()

    month_start = today.replace(
        day=1
    )

    # =====================================================
    # ONLY LOAD PERSONAL DATA WHEN USER IS LOGGED IN
    # =====================================================

    if current_user.is_authenticated:

        # =================================================
        # MONTHLY INCOME
        # =================================================

        monthly_income = (
            db.session.query(
                func.coalesce(
                    func.sum(Income.amount),
                    0
                )
            )
            .filter(
                Income.user_id == current_user.id,
                Income.date >= month_start,
                Income.date <= today
            )
            .scalar()
            or 0
        )


        # =================================================
        # MONTHLY SPENDING
        # =================================================

        monthly_spending = (
            db.session.query(
                func.coalesce(
                    func.sum(Expense.amount),
                    0
                )
            )
            .filter(
                Expense.user_id == current_user.id,
                Expense.date >= month_start,
                Expense.date <= today
            )
            .scalar()
            or 0
        )


        # =================================================
        # CONVERT TO FLOAT
        # =================================================

        monthly_income = float(
            monthly_income
        )

        monthly_spending = float(
            monthly_spending
        )


        # =================================================
        # MONTHLY SAVINGS
        # =================================================

        monthly_savings = (
            monthly_income -
            monthly_spending
        )


        # =================================================
        # SAVINGS RATE
        # =================================================

        if monthly_income > 0:

            savings_rate = (
                monthly_savings /
                monthly_income
            ) * 100

        else:

            savings_rate = 0.0


        # =================================================
        # LIMIT NEGATIVE / INVALID VALUES
        # =================================================

        savings_rate = max(
            min(
                savings_rate,
                100
            ),
            -100
        )


    # =====================================================
    # RENDER HOME
    # =====================================================

    return render_template(

        "home.html",

        monthly_income=monthly_income,

        monthly_spending=monthly_spending,

        monthly_savings=monthly_savings,

        savings_rate=savings_rate

    )