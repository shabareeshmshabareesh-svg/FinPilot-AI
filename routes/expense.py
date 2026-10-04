from datetime import date, timedelta

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request
)

from flask_login import login_required, current_user

from models.database import db
from models.expense import Expense

from forms.expense_forms import (
    ExpenseForm,
    EXPENSE_CATEGORIES,
    EXPENSE_PAYMENT_METHODS
)


expense = Blueprint(
    "expense",
    __name__,
    url_prefix="/expenses"
)


# =========================================================
# ADD EXPENSE
# =========================================================

@expense.route("/add", methods=["GET", "POST"])
@login_required
def add_expense():

    form = ExpenseForm()

    # Automatically use today's date
    if not form.date.data:
        form.date.data = date.today()

    # Save expense
    if form.validate_on_submit():

        new_expense = Expense(
            amount=form.amount.data,
            category=form.category.data,
            description=form.description.data,
            payment_method=form.payment_method.data,
            date=form.date.data,
            user_id=current_user.id
        )

        db.session.add(new_expense)
        db.session.commit()

        flash(
            f"₹{form.amount.data:.2f} expense added successfully! 💸",
            "success"
        )

        return redirect(
            url_for("expense.expense_list")
        )

    return render_template(
        "expenses/add.html",
        form=form
    )


# =========================================================
# VIEW + SEARCH + FILTER EXPENSES
# =========================================================

@expense.route("/")
@login_required
def expense_list():

    # Get filter values from URL
    search = request.args.get(
        "search",
        "",
        type=str
    ).strip()

    category = request.args.get(
        "category",
        "",
        type=str
    ).strip()

    payment_method = request.args.get(
        "payment_method",
        "",
        type=str
    ).strip()

    date_filter = request.args.get(
        "date_filter",
        "",
        type=str
    ).strip()


    # Start with current user's expenses only
    query = Expense.query.filter_by(
        user_id=current_user.id
    )


    # =====================================================
    # SEARCH
    # =====================================================

    if search:

        search_pattern = f"%{search}%"

        query = query.filter(
            db.or_(
                Expense.description.ilike(search_pattern),
                Expense.category.ilike(search_pattern)
            )
        )


    # =====================================================
    # CATEGORY FILTER
    # =====================================================

    if category:

        query = query.filter(
            Expense.category == category
        )


    # =====================================================
    # PAYMENT METHOD FILTER
    # =====================================================

    if payment_method:

        query = query.filter(
            Expense.payment_method == payment_method
        )


    # =====================================================
    # DATE FILTER
    # =====================================================

    today = date.today()


    if date_filter == "today":

        query = query.filter(
            Expense.date == today
        )


    elif date_filter == "week":

        week_start = today - timedelta(
            days=today.weekday()
        )

        query = query.filter(
            Expense.date >= week_start,
            Expense.date <= today
        )


    elif date_filter == "month":

        month_start = today.replace(
            day=1
        )

        next_month_start = (
            month_start + timedelta(days=32)
        ).replace(day=1)

        query = query.filter(
            Expense.date >= month_start,
            Expense.date < next_month_start
        )


    # =====================================================
    # GET FINAL RESULTS
    # =====================================================

    expenses = query.order_by(
        Expense.date.desc(),
        Expense.created_at.desc()
    ).all()


    # =====================================================
    # FILTER OPTIONS
    # =====================================================
    #
    # Read from the shared form definition so the
    # filter list can never drift away from the
    # categories that can actually be saved.

    categories = [
        value
        for value, _ in EXPENSE_CATEGORIES
    ]


    payment_methods = [
        value
        for value, _ in EXPENSE_PAYMENT_METHODS
    ]


    return render_template(
        "expenses/list.html",
        expenses=expenses,
        search=search,
        selected_category=category,
        selected_payment_method=payment_method,
        selected_date_filter=date_filter,
        categories=categories,
        payment_methods=payment_methods
    )


# =========================================================
# EDIT EXPENSE
# =========================================================

@expense.route(
    "/edit/<int:expense_id>",
    methods=["GET", "POST"]
)
@login_required
def edit_expense(expense_id):

    # Only find an expense belonging
    # to the current user.

    expense_item = Expense.query.filter_by(
        id=expense_id,
        user_id=current_user.id
    ).first_or_404()


    form = ExpenseForm()


    # Update expense
    if form.validate_on_submit():

        expense_item.amount = form.amount.data

        expense_item.category = form.category.data

        expense_item.description = form.description.data

        expense_item.payment_method = form.payment_method.data

        expense_item.date = form.date.data


        db.session.commit()


        flash(
            "Expense updated successfully! ✏️",
            "success"
        )


        return redirect(
            url_for("expense.expense_list")
        )


    # Fill existing values into form
    if not form.is_submitted():

        form.amount.data = expense_item.amount

        form.category.data = expense_item.category

        form.description.data = expense_item.description

        form.payment_method.data = expense_item.payment_method

        form.date.data = expense_item.date


    return render_template(
        "expenses/edit.html",
        form=form,
        expense=expense_item
    )


# =========================================================
# DELETE EXPENSE
# =========================================================

@expense.route(
    "/delete/<int:expense_id>",
    methods=["POST"]
)
@login_required
def delete_expense(expense_id):

    # Only find an expense belonging
    # to the current user.

    expense_item = Expense.query.filter_by(
        id=expense_id,
        user_id=current_user.id
    ).first_or_404()


    db.session.delete(
        expense_item
    )

    db.session.commit()


    flash(
        "Expense deleted successfully. 🗑️",
        "success"
    )


    return redirect(
        url_for("expense.expense_list")
    )