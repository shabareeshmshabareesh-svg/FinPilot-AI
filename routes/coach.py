from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify
)

from flask_login import (
    login_required,
    current_user
)

from datetime import date, datetime, timedelta

from models.expense import Expense
from models.income import Income
from models.goal import Goal
from models.chat import ChatMessage

from models.database import db

from utils.money_coach import (
    money_coach_response
)


# =========================================
# COACH BLUEPRINT
# =========================================

coach = Blueprint(
    "coach",
    __name__,
    url_prefix="/coach"
)


# =========================================
# MONEY COACH
# =========================================

@coach.route(
    "/",
    methods=["GET", "POST"]
)
@login_required
def money_coach():

    # =====================================
    # TODAY
    # =====================================

    today = date.today()

    month_start = today.replace(
        day=1
    )


    # =====================================
    # NEXT MONTH START
    # =====================================
    #
    # "This month" covers the whole calendar
    # month on every page, exactly like the
    # dashboard, so all totals agree.

    next_month_start = (

        month_start +
        timedelta(days=32)

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
    # CATEGORY TOTALS
    # =====================================
    #
    # The Money Coach needs these to answer
    # "where am I spending the most" on this
    # page as well, not only on Analytics.

    category_totals = {}


    for expense in expenses:

        category = (

            expense.category
            or
            "Others"

        )


        category_totals[category] = (

            category_totals.get(
                category,
                0
            )

            +

            float(expense.amount or 0)

        )


    # =====================================
    # CATEGORY PERCENTAGES
    # =====================================

    category_percentages = {}


    if monthly_spending > 0:

        category_percentages = {

            category: (
                amount / monthly_spending
            ) * 100

            for category, amount
            in category_totals.items()

            if amount > 0

        }


    # =====================================
    # MONTHLY BUDGET
    # =====================================

    monthly_budget = (

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
    # NEXT MONTH
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


    # =====================================
    # DAYS REMAINING
    # =====================================

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

    remaining_budget = max(

        monthly_budget -
        monthly_spending,

        0

    )


    # =====================================
    # SAFE DAILY SPENDING
    # =====================================

    safe_daily_spending = (

        remaining_budget /
        days_remaining

    )


    # =====================================
    # CURRENT SAVINGS GOAL
    # =====================================

    current_goal = Goal.query.filter_by(

        user_id=current_user.id

    ).order_by(

        Goal.created_at.desc()

    ).first()


    # =====================================
    # QUESTION
    # =====================================

    question = ""

    coach_response = None


    # =====================================
    # CURRENT CHAT MESSAGE
    # =====================================
    #
    # These values are used by coach.html
    # for the newly generated AI response.
    #
    # =====================================

    chat_message = None


    # =====================================
    # GET PREVIOUS CHAT HISTORY
    # =====================================

    previous_chat_history = (

        ChatMessage.query.filter_by(

            user_id=current_user.id

        ).order_by(

            ChatMessage.created_at.desc()

        ).limit(20).all()

    )


    # =====================================
    # REVERSE HISTORY
    # =====================================

    previous_chat_history = list(

        reversed(
            previous_chat_history
        )

    )


    # =====================================
    # HANDLE POST
    # =====================================

    if request.method == "POST":

        question = request.form.get(

            "question",

            ""

        ).strip()


        # =================================
        # EMPTY QUESTION
        # =================================

        if not question:

            if request.headers.get(
                "X-Requested-With"
            ) == "XMLHttpRequest":

                return jsonify({

                    "success": False,

                    "error":
                        "Please enter a question."

                }), 400


            flash(
                "Please enter a question.",
                "warning"
            )

            return redirect(

                url_for(
                    "coach.money_coach"
                )

            )


        # =================================
        # ASK FINPILOT AI
        # =================================

        try:

            coach_response = (
                money_coach_response(

                    question=question,

                    monthly_income=
                        monthly_income,

                    monthly_spending=
                        monthly_spending,

                    monthly_budget=
                        monthly_budget,

                    monthly_savings=
                        monthly_savings,

                    safe_daily_spending=
                        safe_daily_spending,

                    goal=
                        current_goal,

                    category_totals=
                        category_totals,

                    category_percentages=
                        category_percentages,

                    chat_history=
                        previous_chat_history

                )
            )


        except Exception as error:

            print(
                "Money Coach Error:",
                error
            )


            if request.headers.get(
                "X-Requested-With"
            ) == "XMLHttpRequest":

                return jsonify({

                    "success": False,

                    "error":
                        "FinPilot AI could not process your question right now."

                }), 500


            flash(
                "FinPilot AI could not process your question right now.",
                "danger"
            )

            return redirect(

                url_for(
                    "coach.money_coach"
                )

            )


        # =================================
        # GET AI RESPONSE TEXT
        # =================================

        if isinstance(
            coach_response,
            dict
        ):

            ai_response_text = (

                coach_response.get(

                    "message",

                    ""

                )

            )

        else:

            ai_response_text = str(

                coach_response

            )


        # =================================
        # SAVE CHAT MESSAGE
        # =================================

        if ai_response_text:

            chat_message = ChatMessage(

                user_id=current_user.id,

                question=question,

                response=ai_response_text

            )


            db.session.add(
                chat_message
            )


            db.session.commit()


        # =================================
        # AJAX RESPONSE
        # =================================

        if request.headers.get(
            "X-Requested-With"
        ) == "XMLHttpRequest":

            return jsonify({

                "success": True,

                "response":
                    ai_response_text,

                "message_id": (

                    chat_message.id

                    if chat_message

                    else None

                ),

                "feedback": (

                    chat_message.feedback

                    if chat_message

                    else None

                )

            })


    # =====================================
    # GET UPDATED CHAT HISTORY
    # =====================================

    chat_history = (

        ChatMessage.query.filter_by(

            user_id=current_user.id

        ).order_by(

            ChatMessage.created_at.desc()

        ).limit(20).all()

    )


    # =====================================
    # REVERSE FOR DISPLAY
    # =====================================

    chat_history = list(

        reversed(
            chat_history
        )

    )


    # =====================================
    # CURRENT RESPONSE MESSAGE DATA
    # =====================================
    #
    # This is the important Step 33C fix.
    #
    # coach.html can now attach:
    #
    # data-message-id
    # data-feedback
    #
    # to the newly generated response.
    #
    # =====================================

    coach_message_id = (

        chat_message.id

        if chat_message

        else None

    )


    coach_message_feedback = (

        chat_message.feedback

        if chat_message

        else ""

    )


    # =====================================
    # RENDER PAGE
    # =====================================

    return render_template(

        "coach/coach.html",

        # ---------------------------------
        # QUESTION
        # ---------------------------------

        question=question,

        coach_response=coach_response,


        # ---------------------------------
        # CURRENT AI MESSAGE
        # ---------------------------------

        coach_message_id=
            coach_message_id,

        coach_message_feedback=
            coach_message_feedback,


        # ---------------------------------
        # FINANCIAL INFORMATION
        # ---------------------------------

        monthly_income=
            monthly_income,

        monthly_spending=
            monthly_spending,

        monthly_budget=
            monthly_budget,

        monthly_savings=
            monthly_savings,

        safe_daily_spending=
            safe_daily_spending,


        # ---------------------------------
        # GOAL
        # ---------------------------------

        current_goal=
            current_goal,


        # ---------------------------------
        # CHAT HISTORY
        # ---------------------------------

        chat_history=
            chat_history

    )


# =========================================
# CLEAR CHAT HISTORY
# =========================================

@coach.route(
    "/clear",
    methods=["POST"]
)
@login_required
def clear_chat_history():

    # =====================================
    # DELETE CURRENT USER'S CHATS
    # =====================================

    ChatMessage.query.filter_by(

        user_id=current_user.id

    ).delete(

        synchronize_session=False

    )


    # =====================================
    # SAVE DATABASE CHANGES
    # =====================================

    db.session.commit()


    # =====================================
    # SUCCESS MESSAGE
    # =====================================

    flash(

        "Your Money Coach chat history "
        "has been cleared.",

        "success"

    )


    # =====================================
    # RETURN TO COACH
    # =====================================

    return redirect(

        url_for(
            "coach.money_coach"
        )

    )


# =========================================
# CHAT MESSAGE FEEDBACK
# =========================================
#
# Saves:
#
# helpful
# not_helpful
#
# Endpoint:
#
# POST /coach/feedback
#
# =========================================

@coach.route(
    "/feedback",
    methods=["POST"]
)
@login_required
def chat_message_feedback():

    # =====================================
    # GET MESSAGE ID
    # =====================================

    message_id = request.form.get(
        "message_id"
    )


    # =====================================
    # GET FEEDBACK
    # =====================================

    feedback = request.form.get(
        "feedback"
    )


    # =====================================
    # VALIDATE MESSAGE ID
    # =====================================

    if not message_id:

        return jsonify({

            "success": False,

            "error":
                "Message ID is required."

        }), 400


    try:

        message_id = int(
            message_id
        )

    except (
        ValueError,
        TypeError
    ):

        return jsonify({

            "success": False,

            "error":
                "Invalid message ID."

        }), 400


    # =====================================
    # VALIDATE FEEDBACK
    # =====================================

    allowed_feedback = {

        "helpful",

        "not_helpful"

    }


    if feedback not in allowed_feedback:

        return jsonify({

            "success": False,

            "error":
                "Invalid feedback."

        }), 400


    # =====================================
    # FIND CHAT MESSAGE
    # =====================================
    #
    # IMPORTANT:
    #
    # Only allow the current user
    # to modify their own message.
    #
    # =====================================

    chat_message = ChatMessage.query.filter_by(

        id=message_id,

        user_id=current_user.id

    ).first()


    # =====================================
    # MESSAGE NOT FOUND
    # =====================================

    if not chat_message:

        return jsonify({

            "success": False,

            "error":
                "Chat message not found."

        }), 404


    # =====================================
    # SAVE FEEDBACK
    # =====================================

    chat_message.feedback = feedback


    # =====================================
    # SAVE FEEDBACK TIME
    # =====================================

    chat_message.feedback_at = datetime.utcnow()


    # =====================================
    # COMMIT
    # =====================================

    db.session.commit()


    # =====================================
    # SUCCESS
    # =====================================

    return jsonify({

        "success": True,

        "message_id":
            chat_message.id,

        "feedback":
            chat_message.feedback

    })