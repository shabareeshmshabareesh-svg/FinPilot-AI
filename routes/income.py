from datetime import date

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from models.database import db
from models.income import Income

from forms.income_forms import IncomeForm


income = Blueprint(
    "income",
    __name__,
    url_prefix="/income"
)


# =========================================================
# ADD INCOME
# =========================================================

@income.route(
    "/add",
    methods=["GET", "POST"]
)
@login_required
def add_income():

    form = IncomeForm()


    # =====================================================
    # DEFAULT DATE
    # =====================================================

    if not form.date.data:
        form.date.data = date.today()


    # =====================================================
    # SAVE INCOME
    # =====================================================

    if form.validate_on_submit():

        new_income = Income(

            amount=form.amount.data,

            source=form.source.data,

            description=form.description.data,

            date=form.date.data,

            user_id=current_user.id

        )


        db.session.add(new_income)

        db.session.commit()


        flash(
            f"₹{form.amount.data:.2f} income added successfully! 💰",
            "success"
        )


        return redirect(
            url_for("income.income_list")
        )


    return render_template(
        "income/add.html",
        form=form
    )


# =========================================================
# VIEW INCOME HISTORY
# =========================================================

@income.route("/")
@login_required
def income_list():

    incomes = Income.query.filter_by(

        user_id=current_user.id

    ).order_by(

        Income.date.desc(),

        Income.created_at.desc()

    ).all()


    return render_template(
        "income/list.html",
        incomes=incomes
    )


# =========================================================
# EDIT INCOME
# =========================================================

@income.route(
    "/edit/<int:income_id>",
    methods=["GET", "POST"]
)
@login_required
def edit_income(income_id):

    # =====================================================
    # GET ONLY CURRENT USER'S INCOME
    # =====================================================

    income_item = Income.query.filter_by(

        id=income_id,

        user_id=current_user.id

    ).first_or_404()


    # =====================================================
    # CREATE FORM
    # =====================================================

    form = IncomeForm()


    # =====================================================
    # UPDATE INCOME
    # =====================================================

    if form.validate_on_submit():

        income_item.amount = form.amount.data

        income_item.source = form.source.data

        income_item.description = form.description.data

        income_item.date = form.date.data


        db.session.commit()


        flash(
            "Income updated successfully! ✏️",
            "success"
        )


        return redirect(
            url_for("income.income_list")
        )


    # =====================================================
    # LOAD EXISTING DATA
    # =====================================================

    if not form.is_submitted():

        form.amount.data = income_item.amount

        form.source.data = income_item.source

        form.description.data = (
            income_item.description
        )

        form.date.data = income_item.date


    return render_template(
        "income/edit.html",
        form=form,
        income=income_item
    )


# =========================================================
# DELETE INCOME
# =========================================================

@income.route(
    "/delete/<int:income_id>",
    methods=["POST"]
)
@login_required
def delete_income(income_id):

    # =====================================================
    # ONLY DELETE CURRENT USER'S INCOME
    # =====================================================

    income_item = Income.query.filter_by(

        id=income_id,

        user_id=current_user.id

    ).first_or_404()


    # =====================================================
    # DELETE
    # =====================================================

    db.session.delete(income_item)

    db.session.commit()


    flash(
        "Income deleted successfully. 🗑️",
        "success"
    )


    return redirect(
        url_for("income.income_list")
    )