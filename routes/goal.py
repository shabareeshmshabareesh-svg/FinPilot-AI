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
from models.goal import Goal

from forms.goal_forms import GoalForm


goal = Blueprint(
    "goal",
    __name__,
    url_prefix="/goals"
)


# =========================================================
# CREATE GOAL
# =========================================================

@goal.route("/add", methods=["GET", "POST"])
@login_required
def add_goal():

    form = GoalForm()


    # =====================================================
    # SAVE GOAL
    # =====================================================

    if form.validate_on_submit():

        target_amount = form.target_amount.data

        saved_amount = form.saved_amount.data or 0


        # =============================================
        # PREVENT SAVED AMOUNT > TARGET
        # =============================================

        if saved_amount > target_amount:

            flash(
                "Saved amount cannot be greater than your target amount.",
                "danger"
            )

            return render_template(
                "goals/add.html",
                form=form
            )


        # =============================================
        # CREATE GOAL
        # =============================================

        new_goal = Goal(

            name=form.name.data,

            target_amount=target_amount,

            saved_amount=saved_amount,

            target_date=form.target_date.data,

            description=form.description.data,

            user_id=current_user.id

        )


        db.session.add(new_goal)

        db.session.commit()


        flash(
            "Your savings goal was created successfully! 🎯",
            "success"
        )


        return redirect(
            url_for("goal.goal_list")
        )


    # =====================================================
    # SHOW FORM
    # =====================================================

    return render_template(
        "goals/add.html",
        form=form
    )


# =========================================================
# VIEW ALL GOALS
# =========================================================

@goal.route("/")
@login_required
def goal_list():

    goals = Goal.query.filter_by(

        user_id=current_user.id

    ).order_by(

        Goal.created_at.desc()

    ).all()


    # =====================================================
    # CALCULATE PROGRESS
    # =====================================================

    goal_data = []


    for item in goals:

        if item.target_amount > 0:

            progress = (
                item.saved_amount /
                item.target_amount
            ) * 100

        else:

            progress = 0


        # Never exceed 100%

        progress = min(
            max(progress, 0),
            100
        )


        # =============================================
        # COMPLETION STATUS
        # =============================================

        completed = (
            item.saved_amount >=
            item.target_amount
        )


        goal_data.append({

            "goal": item,

            "progress": progress,

            "completed": completed

        })


    return render_template(
        "goals/list.html",
        goal_data=goal_data
    )


# =========================================================
# EDIT GOAL
# =========================================================

@goal.route(
    "/edit/<int:goal_id>",
    methods=["GET", "POST"]
)
@login_required
def edit_goal(goal_id):

    # =============================================
    # ONLY GET CURRENT USER'S GOAL
    # =============================================

    goal_item = Goal.query.filter_by(

        id=goal_id,

        user_id=current_user.id

    ).first_or_404()


    form = GoalForm()


    # =============================================
    # UPDATE GOAL
    # =============================================

    if form.validate_on_submit():

        target_amount = form.target_amount.data

        saved_amount = form.saved_amount.data or 0


        # =============================================
        # VALIDATE SAVED AMOUNT
        # =============================================

        if saved_amount > target_amount:

            flash(
                "Saved amount cannot be greater than your target amount.",
                "danger"
            )

            return render_template(
                "goals/edit.html",
                form=form,
                goal=goal_item
            )


        # =============================================
        # UPDATE VALUES
        # =============================================

        goal_item.name = form.name.data

        goal_item.target_amount = target_amount

        goal_item.saved_amount = saved_amount

        goal_item.target_date = form.target_date.data

        goal_item.description = form.description.data


        db.session.commit()


        flash(
            "Savings goal updated successfully! ✏️",
            "success"
        )


        return redirect(
            url_for("goal.goal_list")
        )


    # =============================================
    # LOAD EXISTING DATA
    # =============================================

    if not form.is_submitted():

        form.name.data = goal_item.name

        form.target_amount.data = (
            goal_item.target_amount
        )

        form.saved_amount.data = (
            goal_item.saved_amount
        )

        form.target_date.data = (
            goal_item.target_date
        )

        form.description.data = (
            goal_item.description
        )


    return render_template(
        "goals/edit.html",
        form=form,
        goal=goal_item
    )


# =========================================================
# DELETE GOAL
# =========================================================

@goal.route(
    "/delete/<int:goal_id>",
    methods=["POST"]
)
@login_required
def delete_goal(goal_id):

    # =============================================
    # ONLY DELETE CURRENT USER'S GOAL
    # =============================================

    goal_item = Goal.query.filter_by(

        id=goal_id,

        user_id=current_user.id

    ).first_or_404()


    db.session.delete(goal_item)

    db.session.commit()


    flash(
        "Savings goal deleted successfully. 🗑️",
        "success"
    )


    return redirect(
        url_for("goal.goal_list")
    )