from datetime import date, timedelta

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify
)

from flask_login import (
    login_required,
    current_user
)

from models.expense import Expense
from models.income import Income
from models.goal import Goal
from models.chat import ChatMessage

from models.database import db

from utils.money_coach import money_coach_response


# =========================================================
# FINPILOT AI ANALYTICS
# =========================================================

analytics = Blueprint(
    "analytics",
    __name__,
    url_prefix="/analytics"
)


# =========================================================
# ANALYTICS HOME
# =========================================================

@analytics.route("/")
@login_required
def analytics_home():

    # =====================================================
    # CURRENT DATE
    # =====================================================

    today = date.today()

    month_start = today.replace(day=1)


    # =====================================================
    # CURRENT MONTH EXPENSES
    # =====================================================

    expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        Expense.date >= month_start,
        Expense.date <= today
    ).order_by(
        Expense.date.asc()
    ).all()


    # =====================================================
    # TOTAL MONTHLY SPENDING
    # =====================================================

    total_spending = sum(
        float(expense.amount or 0)
        for expense in expenses
    )


    # =====================================================
    # NUMBER OF EXPENSES
    # =====================================================

    expense_count = len(expenses)


    # =====================================================
    # AVERAGE EXPENSE
    # =====================================================

    if expense_count > 0:

        average_expense = (
            total_spending /
            expense_count
        )

    else:

        average_expense = 0


    # =====================================================
    # CATEGORY SPENDING
    # =====================================================

    category_totals = {}


    for expense in expenses:

        category = expense.category

        if category not in category_totals:

            category_totals[category] = 0

        category_totals[category] += float(
            expense.amount or 0
        )


    # =====================================================
    # SORT CATEGORIES
    # =====================================================

    category_totals = dict(
        sorted(
            category_totals.items(),
            key=lambda item: item[1],
            reverse=True
        )
    )


    # =====================================================
    # TOP SPENDING CATEGORY
    # =====================================================

    if category_totals:

        top_category = next(
            iter(category_totals)
        )

        top_category_amount = (
            category_totals[top_category]
        )

    else:

        top_category = "No data"

        top_category_amount = 0


    # =====================================================
    # CATEGORY PERCENTAGES
    # =====================================================

    category_percentages = {}


    if total_spending > 0:

        for category, amount in category_totals.items():

            category_percentages[category] = (
                amount /
                total_spending
            ) * 100


    # =====================================================
    # DAILY SPENDING
    # =====================================================

    daily_totals = {}


    current_day = month_start


    while current_day <= today:

        daily_totals[current_day] = 0

        current_day += timedelta(
            days=1
        )


    # Add expenses to their days

    for expense in expenses:

        if expense.date in daily_totals:

            daily_totals[expense.date] += float(
                expense.amount or 0
            )


    # =====================================================
    # CHART DATA
    # =====================================================

    daily_labels = []

    daily_values = []


    for expense_day, amount in daily_totals.items():

        daily_labels.append(
            expense_day.strftime("%d %b")
        )

        daily_values.append(
            round(amount, 2)
        )


    # =====================================================
    # HIGHEST SPENDING DAY
    # =====================================================

    if daily_totals:

        highest_spending_day = max(
            daily_totals,
            key=daily_totals.get
        )

        highest_spending_day_amount = (
            daily_totals[highest_spending_day]
        )

    else:

        highest_spending_day = None

        highest_spending_day_amount = 0


    # =====================================================
    # PREVIOUS MONTH
    # =====================================================

    if month_start.month == 1:

        previous_month_year = (
            month_start.year - 1
        )

        previous_month_month = 12

    else:

        previous_month_year = (
            month_start.year
        )

        previous_month_month = (
            month_start.month - 1
        )


    previous_month_start = date(
        previous_month_year,
        previous_month_month,
        1
    )


    previous_month_end = (
        month_start -
        timedelta(days=1)
    )


    # =====================================================
    # LAST MONTH EXPENSES
    # =====================================================

    previous_month_expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        Expense.date >= previous_month_start,
        Expense.date <= previous_month_end
    ).all()


    # =====================================================
    # LAST MONTH TOTAL
    # =====================================================

    previous_month_spending = sum(
        float(expense.amount or 0)
        for expense in previous_month_expenses
    )


    # =====================================================
    # MONTH COMPARISON
    # =====================================================

    spending_difference = (
        total_spending -
        previous_month_spending
    )


    if previous_month_spending > 0:

        spending_change_percent = (
            spending_difference /
            previous_month_spending
        ) * 100

    else:

        spending_change_percent = 0


    # =====================================================
    # MONTH COMPARISON LABEL
    # =====================================================

    if spending_difference > 0:

        spending_change_label = "higher"

    elif spending_difference < 0:

        spending_change_label = "lower"

    else:

        spending_change_label = "same"


    # =====================================================
    # USER MONTHLY BUDGET
    # =====================================================

    monthly_budget = float(
        current_user.monthly_budget or 0
    )


    # =====================================================
    # BUDGET REMAINING
    # =====================================================

    budget_remaining = (
        monthly_budget -
        total_spending
    )


    # =====================================================
    # BUDGET PERCENTAGE
    # =====================================================

    if monthly_budget > 0:

        budget_percent = (
            total_spending /
            monthly_budget
        ) * 100

    else:

        budget_percent = 0


    # Keep progress bar between 0 and 100

    budget_percent = min(
        max(budget_percent, 0),
        100
    )


    # =====================================================
    # BUDGET STATUS
    # =====================================================

    if monthly_budget <= 0:

        budget_status = "not_set"

    elif total_spending > monthly_budget:

        budget_status = "exceeded"

    elif budget_percent >= 80:

        budget_status = "warning"

    else:

        budget_status = "safe"


    # =====================================================
    # BUDGET DIFFERENCE
    # =====================================================

    if monthly_budget <= 0:

        budget_difference = 0

    elif total_spending > monthly_budget:

        budget_difference = (
            total_spending -
            monthly_budget
        )

    else:

        budget_difference = (
            monthly_budget -
            total_spending
        )


    # =====================================================
    # CURRENT MONTH INCOME
    # =====================================================

    incomes = Income.query.filter(
        Income.user_id == current_user.id,
        Income.date >= month_start,
        Income.date <= today
    ).all()


    monthly_income = sum(
        float(income.amount or 0)
        for income in incomes
    )


    # =====================================================
    # MONTHLY SAVINGS / SURPLUS
    # =====================================================

    monthly_savings = (
        monthly_income -
        total_spending
    )


    # =====================================================
    # SAVINGS RATE
    # =====================================================

    if monthly_income > 0:

        savings_rate = (
            monthly_savings /
            monthly_income
        ) * 100

    else:

        savings_rate = 0


    # =====================================================
    # REMAINING DAYS IN MONTH
    # =====================================================

    if monthly_budget > 0:

        remaining_days = (
            today.replace(
                day=28
            ) + timedelta(days=4)
        ).replace(
            day=1
        ) - today

        remaining_days = remaining_days.days

        remaining_days = max(
            remaining_days,
            1
        )


        # Safe daily spending

        safe_daily_spending = max(
            budget_remaining,
            0
        ) / remaining_days

    else:

        safe_daily_spending = 0


    # =====================================================
    # ACTIVE SAVINGS GOAL
    # =====================================================

    active_goal = Goal.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Goal.created_at.desc()
    ).first()


    # =====================================================
    # SMART FINPILOT COACH
    # =====================================================

    # We use the existing money_coach.py.
    # No new AI engine is created.

    if monthly_budget <= 0:

        coach_question = (
            "What is my budget status?"
        )

    elif total_spending > monthly_budget:

        coach_question = (
            "What is my budget status?"
        )

    elif monthly_savings > 0:

        coach_question = (
            "How much am I saving?"
        )

    else:

        coach_question = (
            "How much am I saving?"
        )


    try:

        smart_coach = money_coach_response(

            question=coach_question,

            monthly_income=monthly_income,

            monthly_spending=total_spending,

            monthly_budget=monthly_budget,

            monthly_savings=monthly_savings,

            safe_daily_spending=safe_daily_spending,

            goal=active_goal,

            category_totals=category_totals,

            category_percentages=category_percentages,

            top_category=top_category,

            top_category_amount=top_category_amount,

            chat_history=(
                list(
                    reversed(
                        ChatMessage.query.filter_by(
                            user_id=current_user.id
                        ).order_by(
                            ChatMessage.created_at.desc()
                        ).limit(20).all()
                    )
                )
            )

        )

    except Exception:

        # Analytics should still work even if
        # the AI/Gemini service has a problem.

        smart_coach = {

            "type": "info",

            "icon": "🧠",

            "title": "FinPilot Smart Coach",

            "message": (
                "Continue tracking your income "
                "and expenses to receive personalized "
                "financial guidance."
            )

        }


    # =====================================================
    # RENDER ANALYTICS
    # =====================================================

    return render_template(

        "analytics/analytics.html",


        # =================================================
        # BASIC ANALYTICS
        # =================================================

        total_spending=total_spending,

        expense_count=expense_count,

        average_expense=average_expense,


        # =================================================
        # INCOME
        # =================================================

        monthly_income=monthly_income,

        monthly_savings=monthly_savings,

        savings_rate=savings_rate,


        # =================================================
        # CATEGORY ANALYTICS
        # =================================================

        category_totals=category_totals,

        category_percentages=category_percentages,

        top_category=top_category,

        top_category_amount=top_category_amount,


        # =================================================
        # DAILY ANALYTICS
        # =================================================

        daily_labels=daily_labels,

        daily_values=daily_values,

        highest_spending_day=highest_spending_day,

        highest_spending_day_amount=(
            highest_spending_day_amount
        ),


        # =================================================
        # PREVIOUS MONTH
        # =================================================

        previous_month_spending=(
            previous_month_spending
        ),

        spending_difference=(
            spending_difference
        ),

        spending_change_percent=(
            spending_change_percent
        ),

        spending_change_label=(
            spending_change_label
        ),


        # =================================================
        # BUDGET ANALYTICS
        # =================================================

        monthly_budget=monthly_budget,

        budget_remaining=budget_remaining,

        budget_percent=budget_percent,

        budget_status=budget_status,

        budget_difference=budget_difference,

        safe_daily_spending=safe_daily_spending,


        # =================================================
        # AI COACH
        # =================================================

        smart_coach=smart_coach

    )


# =========================================================
# FINPILOT AI COACH - ASK QUESTION
# =========================================================

@analytics.route("/ask", methods=["POST"])
@login_required
def ask_coach():

    question = request.form.get(
        "question",
        ""
    ).strip()


    # =====================================================
    # EMPTY QUESTION
    # =====================================================

    if not question:

        return jsonify({
            "success": False,
            "message": "Please enter a question."
        }), 400


    # =====================================================
    # CURRENT DATE
    # =====================================================

    today = date.today()

    month_start = today.replace(day=1)


    # =====================================================
    # CURRENT MONTH EXPENSES
    # =====================================================

    expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        Expense.date >= month_start,
        Expense.date <= today
    ).all()


    monthly_spending = sum(
        float(expense.amount or 0)
        for expense in expenses
    )


    # =====================================================
    # CATEGORY SPENDING FOR AI
    # =====================================================

    category_totals = {}

    for expense in expenses:

        category = (
            expense.category
            or "Other"
        )

        category_totals[category] = (
            category_totals.get(category, 0)
            + float(expense.amount or 0)
        )


    # =====================================================
    # SORT CATEGORIES
    # =====================================================

    category_totals = dict(
        sorted(
            category_totals.items(),
            key=lambda item: item[1],
            reverse=True
        )
    )


    # =====================================================
    # TOP SPENDING CATEGORY
    # =====================================================

    if category_totals:

        top_category = next(
            iter(category_totals)
        )

        top_category_amount = (
            category_totals[top_category]
        )

    else:

        top_category = "No data"

        top_category_amount = 0


    # =====================================================
    # CATEGORY PERCENTAGES
    # =====================================================

    category_percentages = {}

    if monthly_spending > 0:

        for category, amount in category_totals.items():

            category_percentages[category] = (
                amount /
                monthly_spending
            ) * 100


    # =====================================================
    # CURRENT MONTH INCOME
    # =====================================================

    incomes = Income.query.filter(
        Income.user_id == current_user.id,
        Income.date >= month_start,
        Income.date <= today
    ).all()


    monthly_income = sum(
        float(income.amount or 0)
        for income in incomes
    )


    # =====================================================
    # MONTHLY BUDGET
    # =====================================================

    monthly_budget = float(
        current_user.monthly_budget or 0
    )


    # =====================================================
    # MONTHLY SAVINGS
    # =====================================================

    monthly_savings = (
        monthly_income -
        monthly_spending
    )


    # =====================================================
    # REMAINING DAYS IN MONTH
    # =====================================================

    next_month = (
        month_start.replace(day=28)
        + timedelta(days=4)
    ).replace(day=1)


    remaining_days = (
        next_month - today
    ).days


    remaining_days = max(
        remaining_days,
        1
    )


    # =====================================================
    # SAFE DAILY SPENDING
    # =====================================================

    if monthly_budget > 0:

        budget_remaining = (
            monthly_budget -
            monthly_spending
        )

        safe_daily_spending = max(
            budget_remaining,
            0
        ) / remaining_days

    else:

        safe_daily_spending = 0


    # =====================================================
    # ACTIVE SAVINGS GOAL
    # =====================================================

    active_goal = Goal.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Goal.created_at.desc()
    ).first()


    # =====================================================
    # GET PREVIOUS CHAT HISTORY
    # =====================================================

    previous_chat_history = (
        ChatMessage.query.filter_by(
            user_id=current_user.id
        ).order_by(
            ChatMessage.created_at.desc()
        ).limit(20).all()
    )

    previous_chat_history = list(
        reversed(
            previous_chat_history
        )
    )


    # =====================================================
    # ASK EXISTING MONEY COACH
    # =====================================================

    try:

        response = money_coach_response(

            question=question,

            monthly_income=monthly_income,

            monthly_spending=monthly_spending,

            monthly_budget=monthly_budget,

            monthly_savings=monthly_savings,

            safe_daily_spending=safe_daily_spending,

            goal=active_goal,

            category_totals=category_totals,

            category_percentages=category_percentages,

            top_category=top_category,

            top_category_amount=top_category_amount,

            chat_history=previous_chat_history

        )


    except Exception as error:

        print(
            "Money Coach Error:",
            error
        )

        return jsonify({
            "success": False,
            "message": (
                "FinPilot Smart Coach is "
                "temporarily unavailable. "
                "Please try again."
            )
        }), 500


    # =====================================================
    # GET AI RESPONSE TEXT
    # =====================================================

    if isinstance(
        response,
        dict
    ):

        ai_response_text = (
            response.get(
                "message",
                ""
            )
        )

    else:

        ai_response_text = str(
            response
        )


    # =====================================================
    # SAVE CHAT HISTORY
    # =====================================================

    chat_message = None


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


    # =====================================================
    # RETURN COACH RESPONSE
    # =====================================================

    return jsonify({

        "success": True,

        "type": (
            response.get(
                "type",
                "info"
            )
            if isinstance(response, dict)
            else "ai"
        ),

        "icon": (
            response.get(
                "icon",
                "🧠"
            )
            if isinstance(response, dict)
            else "🤖"
        ),

        "title": (
            response.get(
                "title",
                "FinPilot Smart Coach"
            )
            if isinstance(response, dict)
            else "FinPilot AI"
        ),

        "message": ai_response_text,

        "response": ai_response_text,

        "message_id": (
            chat_message.id
            if chat_message
            else None
        )

    })