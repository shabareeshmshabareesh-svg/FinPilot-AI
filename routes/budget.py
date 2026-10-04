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

from forms.budget_forms import BudgetForm


budget = Blueprint(
    "budget",
    __name__,
    url_prefix="/budget"
)


@budget.route("/", methods=["GET", "POST"])
@login_required
def set_budget():

    form = BudgetForm()


    # =========================
    # SHOW EXISTING BUDGET
    # =========================

    if request.method == "GET":

        form.monthly_budget.data = (
            current_user.monthly_budget or 0
        )


    # =========================
    # SAVE NEW BUDGET
    # =========================

    if form.validate_on_submit():

        current_user.monthly_budget = (
            form.monthly_budget.data
        )

        db.session.commit()


        flash(
            "Your monthly budget has been updated successfully! 🎯",
            "success"
        )


        return redirect(
            url_for("dashboard.dashboard_home")
        )


    # =========================
    # SHOW PAGE
    # =========================

    return render_template(
        "budget/budget.html",
        form=form
    )