from datetime import date
import hashlib
import json
import threading
import time

from flask import (
    Blueprint,
    render_template,
    jsonify,
    request
)

from flask_login import (
    login_required,
    current_user
)

from models.expense import Expense
from models.income import Income
from models.goal import Goal

from utils.financial_insights import (
    generate_financial_insights
)

from utils.financial_alerts import (
    generate_financial_alerts
)

from utils.ai_insights import (
    generate_ai_financial_insight
)

from utils.ai_command_center import (
    build_ai_command_center
)


# =========================================================
# BLUEPRINT
# =========================================================

dashboard = Blueprint(
    "dashboard",
    __name__,
    url_prefix="/dashboard"
)


# =========================================================
# STEP 23F - AI INSIGHT CACHE
# =========================================================

_AI_INSIGHT_CACHE = {}

_AI_INSIGHT_LOCK = threading.Lock()

_AI_CACHE_MAX_AGE = 60 * 60 * 24


def _get_cached_ai_insight(user_id, signature):
    """Return a valid cached insight or None."""

    cache_key = (
        user_id,
        signature
    )

    with _AI_INSIGHT_LOCK:

        cached = _AI_INSIGHT_CACHE.get(
            cache_key
        )

        if not cached:
            return None

        if (
            time.time() -
            cached["created_at"]
        ) > _AI_CACHE_MAX_AGE:

            _AI_INSIGHT_CACHE.pop(
                cache_key,
                None
            )

            return None

        return cached["insight"]


def _store_ai_insight(
    user_id,
    signature,
    insight
):
    """Store the latest Gemini insight."""

    cache_key = (
        user_id,
        signature
    )

    with _AI_INSIGHT_LOCK:

        _AI_INSIGHT_CACHE[cache_key] = {

            "insight": insight,

            "created_at": time.time()

        }

        # Keep development cache small
        user_keys = [

            key

            for key in _AI_INSIGHT_CACHE

            if key[0] == user_id

        ]

        if len(user_keys) > 5:

            oldest_key = min(

                user_keys,

                key=lambda key:
                    _AI_INSIGHT_CACHE[key][
                        "created_at"
                    ]

            )

            _AI_INSIGHT_CACHE.pop(
                oldest_key,
                None
            )


def _generate_or_get_ai_insight(
    monthly_income,
    monthly_spending,
    monthly_allowance,
    monthly_savings,
    savings_rate,
    safe_daily_spending,
    category_totals,
    goal,
    signature,
    force=False
):
    """Use cache when possible; call Gemini only when necessary."""

    if not force:

        cached = _get_cached_ai_insight(

            current_user.id,

            signature

        )

        if cached:

            return cached, True


    insight = generate_ai_financial_insight(

        monthly_income=monthly_income,

        monthly_spending=monthly_spending,

        monthly_allowance=monthly_allowance,

        monthly_savings=monthly_savings,

        savings_rate=savings_rate,

        safe_daily_spending=safe_daily_spending,

        category_totals=category_totals,

        goal=goal

    )


    _store_ai_insight(

        current_user.id,

        signature,

        insight

    )


    return insight, False


# =========================================================
# FINANCIAL DATA SIGNATURE
# =========================================================

def _get_financial_state_signature():

    today = date.today()


    # -----------------------------------------------------
    # CURRENT MONTH EXPENSES
    # -----------------------------------------------------

    expenses = Expense.query.filter_by(

        user_id=current_user.id

    ).all()


    current_month_expenses = [

        expense

        for expense in expenses

        if (
            expense.date.year == today.year
            and
            expense.date.month == today.month
        )

    ]


    monthly_spending = sum(

        float(expense.amount or 0)

        for expense in current_month_expenses

    )


    category_totals = {}


    for expense in current_month_expenses:

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

            float(
                expense.amount or 0
            )

        )


    # -----------------------------------------------------
    # CURRENT MONTH INCOME
    # -----------------------------------------------------

    incomes = Income.query.filter_by(

        user_id=current_user.id

    ).all()


    current_month_incomes = [

        income

        for income in incomes

        if (
            income.date.year == today.year
            and
            income.date.month == today.month
        )

    ]


    monthly_income = sum(

        float(income.amount or 0)

        for income in current_month_incomes

    )


    # -----------------------------------------------------
    # BUDGET
    # -----------------------------------------------------

    monthly_allowance = float(

        current_user.monthly_budget or 0

    )


    # -----------------------------------------------------
    # CURRENT GOAL
    # -----------------------------------------------------

    current_goal = Goal.query.filter_by(

        user_id=current_user.id

    ).order_by(

        Goal.created_at.desc()

    ).first()


    if current_goal:

        goal_state = {

            "id": current_goal.id,

            "name": current_goal.name,

            "target": float(
                current_goal.target_amount or 0
            ),

            "saved": float(
                current_goal.saved_amount or 0
            )

        }

    else:

        goal_state = None


    # -----------------------------------------------------
    # BUILD STATE
    # -----------------------------------------------------

    state = {

        "date":
            today.isoformat(),

        "monthly_income":
            round(
                monthly_income,
                2
            ),

        "monthly_spending":
            round(
                monthly_spending,
                2
            ),

        "monthly_allowance":
            round(
                monthly_allowance,
                2
            ),

        "category_totals": {

            key: round(
                value,
                2
            )

            for key, value

            in sorted(
                category_totals.items()
            )

        },

        "goal":
            goal_state

    }


    state_json = json.dumps(

        state,

        sort_keys=True,

        separators=(
            ",",
            ":"
        )

    )


    signature = hashlib.sha256(

        state_json.encode(
            "utf-8"
        )

    ).hexdigest()


    return signature, state


# =========================================================
# STEP 40 - FINANCIAL HEALTH SCORE
# =========================================================

def _calculate_expense_prediction(
    monthly_spending,
    today
):
    """
    Forecast current-month spending from the user's
    average daily spending so far.

    Returns a dashboard-friendly dictionary.
    """

    monthly_spending = float(
        monthly_spending or 0
    )

    # Number of days in the current month
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

    days_in_month = (
        next_month - date(
            today.year,
            today.month,
            1
        )
    ).days

    days_elapsed = max(
        today.day,
        1
    )

    average_daily_spending = (
        monthly_spending /
        days_elapsed
    )

    projected_monthly_spending = (
        average_daily_spending *
        days_in_month
    )

    return {
        "average_daily_spending":
            round(
                average_daily_spending,
                2
            ),

        "projected_monthly_spending":
            round(
                projected_monthly_spending,
                2
            ),

        "days_elapsed":
            days_elapsed,

        "days_in_month":
            days_in_month
    }


def _calculate_financial_health_score(
    monthly_income,
    monthly_spending,
    monthly_allowance,
    monthly_savings,
    savings_rate,
    goal_progress
):
    """
    Calculate the FinPilot Financial Health Score.

    Components:

    Budget Control   = 30%
    Savings Health   = 30%
    Spending Control = 25%
    Goal Progress    = 15%

    Final score = 0 to 100.
    """

    # -----------------------------------------------------
    # 1. BUDGET CONTROL
    # -----------------------------------------------------

    if monthly_allowance > 0:

        budget_usage = (

            monthly_spending /
            monthly_allowance

        ) * 100


        if budget_usage <= 50:

            budget_score = 100

        elif budget_usage <= 75:

            budget_score = 90 - (
                (budget_usage - 50) * 0.8
            )

        elif budget_usage <= 90:

            budget_score = 70 - (
                (budget_usage - 75) * 1.2
            )

        elif budget_usage <= 100:

            budget_score = 52 - (
                (budget_usage - 90) * 2.0
            )

        else:

            budget_score = max(

                0,

                32 - (
                    budget_usage - 100
                ) * 1.5

            )

    else:

        # No budget set.
        # Give partial score rather than
        # pretending the user has good budget control.

        budget_score = 45


    budget_score = min(
        max(
            budget_score,
            0
        ),
        100
    )


    # -----------------------------------------------------
    # 2. SAVINGS HEALTH
    # -----------------------------------------------------

    if monthly_income <= 0:

        savings_score = 0

    elif monthly_savings <= 0:

        savings_score = 0

    else:

        # 20%+ savings rate = excellent
        savings_score = min(

            (
                savings_rate /
                20
            ) * 100,

            100

        )


    savings_score = min(
        max(
            savings_score,
            0
        ),
        100
    )


    # -----------------------------------------------------
    # 3. SPENDING CONTROL
    # -----------------------------------------------------

    if monthly_income <= 0:

        spending_score = 50

    else:

        spending_ratio = (

            monthly_spending /
            monthly_income

        ) * 100


        if spending_ratio <= 50:

            spending_score = 100

        elif spending_ratio <= 70:

            spending_score = 90 - (
                (spending_ratio - 50) * 1.0
            )

        elif spending_ratio <= 85:

            spending_score = 70 - (
                (spending_ratio - 70) * 1.5
            )

        elif spending_ratio <= 100:

            spending_score = 47.5 - (
                (spending_ratio - 85) * 1.5
            )

        else:

            spending_score = max(

                0,

                25 - (
                    spending_ratio - 100
                ) * 1.5

            )


    spending_score = min(
        max(
            spending_score,
            0
        ),
        100
    )


    # -----------------------------------------------------
    # 4. GOAL PROGRESS
    # -----------------------------------------------------

    if goal_progress > 0:

        goal_score = min(

            max(
                goal_progress,
                0
            ),

            100

        )

    else:

        # No goal is not treated as a failure.
        # Give a neutral score.

        goal_score = 50


    # -----------------------------------------------------
    # FINAL WEIGHTED SCORE
    # -----------------------------------------------------

    final_score = (

        budget_score * 0.30

        +

        savings_score * 0.30

        +

        spending_score * 0.25

        +

        goal_score * 0.15

    )


    final_score = round(

        min(
            max(
                final_score,
                0
            ),
            100
        )

    )


    # -----------------------------------------------------
    # LABEL + MESSAGE
    # -----------------------------------------------------

    if final_score >= 85:

        label = "Excellent"

        message = (
            "Your finances are in excellent shape. "
            "You're controlling spending and building "
            "strong financial habits."
        )

    elif final_score >= 70:

        label = "Good"

        message = (
            "Your finances are looking healthy. "
            "Keep your spending controlled and "
            "continue building your savings."
        )

    elif final_score >= 50:

        label = "Fair"

        message = (
            "Your finances are moving in the right "
            "direction, but there are areas that "
            "need attention."
        )

    elif final_score >= 30:

        label = "Needs Attention"

        message = (
            "Your finances need some attention. "
            "Focus on controlling spending, "
            "protecting your budget and increasing savings."
        )

    else:

        label = "Critical"

        message = (
            "Your financial health needs immediate "
            "attention. Start by reviewing your "
            "spending and setting a realistic budget."
        )


    return {

        "score":
            final_score,

        "label":
            label,

        "message":
            message,

        "budget":
            round(
                budget_score,
                1
            ),

        "savings":
            round(
                savings_score,
                1
            ),

        "spending":
            round(
                spending_score,
                1
            ),

        "goal":
            round(
                goal_score,
                1
            )

    }


# =========================================================
# DASHBOARD HOME
# =========================================================

@dashboard.route("/")
@login_required
def dashboard_home():

    today = date.today()


    # =====================================================
    # USER EXPENSES
    # =====================================================

    expenses = Expense.query.filter_by(

        user_id=current_user.id

    ).order_by(

        Expense.date.desc()

    ).all()


    # =====================================================
    # TODAY'S EXPENSES
    # =====================================================

    today_expenses = [

        expense

        for expense in expenses

        if expense.date == today

    ]


    # =====================================================
    # CURRENT MONTH EXPENSES
    # =====================================================

    current_month_expenses = [

        expense

        for expense in expenses

        if (
            expense.date.year == today.year
            and
            expense.date.month == today.month
        )

    ]


    # =====================================================
    # TODAY'S SPENDING
    # =====================================================

    today_spending = sum(

        float(expense.amount or 0)

        for expense in today_expenses

    )


    # =====================================================
    # MONTHLY SPENDING
    # =====================================================

    monthly_spending = sum(

        float(expense.amount or 0)

        for expense in current_month_expenses

    )


    # =====================================================
    # CATEGORY TOTALS
    # =====================================================

    category_totals = {}


    for expense in current_month_expenses:

        category = (
            expense.category
            or
            "Others"
        )


        if category not in category_totals:

            category_totals[category] = 0


        category_totals[category] += (

            float(
                expense.amount or 0
            )

        )


    # =====================================================
    # USER MONTHLY BUDGET
    # =====================================================

    monthly_allowance = float(

        current_user.monthly_budget or 0

    )


    # =====================================================
    # REMAINING BUDGET
    # =====================================================

    remaining = max(

        monthly_allowance -
        monthly_spending,

        0

    )


    # =====================================================
    # SAFE DAILY SPENDING
    # =====================================================

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


    if remaining > 0:

        safe_daily_spending = (

            remaining /
            days_remaining

        )

    else:

        safe_daily_spending = 0


    # =====================================================
    # BUDGET PERCENTAGE
    # =====================================================

    if monthly_allowance > 0:

        budget_percent = (

            monthly_spending /
            monthly_allowance

        ) * 100

    else:

        budget_percent = 0


    budget_percent = min(

        max(
            budget_percent,
            0
        ),

        100

    )


    # =====================================================
    # USER INCOME
    # =====================================================

    incomes = Income.query.filter_by(

        user_id=current_user.id

    ).order_by(

        Income.date.desc()

    ).all()


    # =====================================================
    # CURRENT MONTH INCOME
    # =====================================================

    current_month_incomes = [

        income

        for income in incomes

        if (
            income.date.year == today.year
            and
            income.date.month == today.month
        )

    ]


    # =====================================================
    # MONTHLY INCOME
    # =====================================================

    monthly_income = sum(

        float(income.amount or 0)

        for income in current_month_incomes

    )


    # =====================================================
    # MONTHLY SAVINGS
    # =====================================================

    monthly_savings = (

        monthly_income -
        monthly_spending

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


    savings_rate = min(

        max(
            savings_rate,
            0
        ),

        100

    )


    # =====================================================
    # FINANCIAL STATUS
    # =====================================================

    if monthly_income <= 0:

        financial_status = "no_income"

    elif monthly_savings > 0:

        financial_status = "positive"

    elif monthly_savings == 0:

        financial_status = "balanced"

    else:

        financial_status = "negative"


    # =====================================================
    # INCOME VS EXPENSE
    # =====================================================

    income_vs_expense = {

        "income": round(
            monthly_income,
            2
        ),

        "expense": round(
            monthly_spending,
            2
        )

    }


    # =====================================================
    # RECENT EXPENSES
    # =====================================================

    recent_expenses = expenses[:5]


    # =====================================================
    # RECENT INCOME
    # =====================================================

    recent_income = incomes[:5]


    # =====================================================
    # CURRENT SAVINGS GOAL
    # =====================================================

    current_goal = Goal.query.filter_by(

        user_id=current_user.id

    ).order_by(

        Goal.created_at.desc()

    ).first()


    # =====================================================
    # GOAL PROGRESS
    # =====================================================

    goal_progress = 0

    goal_remaining = 0

    goal_completed = False


    if current_goal:

        if current_goal.target_amount > 0:

            goal_progress = (

                current_goal.saved_amount /
                current_goal.target_amount

            ) * 100

        else:

            goal_progress = 0


        goal_progress = min(

            max(
                goal_progress,
                0
            ),

            100

        )


        goal_remaining = max(

            current_goal.target_amount -
            current_goal.saved_amount,

            0

        )


        goal_completed = (

            current_goal.saved_amount >=
            current_goal.target_amount

        )


    # =====================================================
    # STEP 41A - AI EXPENSE PREDICTION
    # =====================================================

    expense_prediction = _calculate_expense_prediction(
        monthly_spending=monthly_spending,
        today=today
    )

    projected_monthly_spending = (
        expense_prediction[
            "projected_monthly_spending"
        ]
    )

    average_daily_spending = (
        expense_prediction[
            "average_daily_spending"
        ]
    )


    # =====================================================
    # PREDICTION VS BUDGET
    # =====================================================

    if monthly_allowance > 0:

        projected_budget_difference = (
            monthly_allowance -
            projected_monthly_spending
        )

    else:

        projected_budget_difference = 0


    if (
        monthly_allowance > 0
        and projected_monthly_spending >
        monthly_allowance
    ):

        expense_prediction_status = (
            "over_budget"
        )

        expense_prediction_message = (
            f"At your current spending pace, "
            f"you may spend approximately "
            f"₹{projected_monthly_spending:,.2f} "
            f"this month, which is about "
            f"₹{abs(projected_budget_difference):,.2f} "
            "above your budget."
        )

    elif (
        monthly_allowance > 0
        and projected_monthly_spending <=
        monthly_allowance
    ):

        expense_prediction_status = (
            "within_budget"
        )

        expense_prediction_message = (
            f"At your current spending pace, "
            f"you may spend approximately "
            f"₹{projected_monthly_spending:,.2f} "
            f"this month, leaving about "
            f"₹{projected_budget_difference:,.2f} "
            "within your budget."
        )

    else:

        expense_prediction_status = (
            "no_budget"
        )

        expense_prediction_message = (
            f"At your current spending pace, "
            f"you may spend approximately "
            f"₹{projected_monthly_spending:,.2f} "
            "this month. Set a budget to compare "
            "this forecast against a target."
        )


    # =====================================================
    # STEP 40 - FINANCIAL HEALTH SCORE
    # =====================================================

    financial_health = (
        _calculate_financial_health_score(

            monthly_income=monthly_income,

            monthly_spending=monthly_spending,

            monthly_allowance=monthly_allowance,

            monthly_savings=monthly_savings,

            savings_rate=savings_rate,

            goal_progress=goal_progress

        )
    )


    financial_health_score = (
        financial_health["score"]
    )

    financial_health_label = (
        financial_health["label"]
    )

    financial_health_message = (
        financial_health["message"]
    )

    financial_health_budget = (
        financial_health["budget"]
    )

    financial_health_savings = (
        financial_health["savings"]
    )

    financial_health_spending = (
        financial_health["spending"]
    )

    financial_health_goal = (
        financial_health["goal"]
    )


    # =====================================================
    # SMART FINANCIAL INSIGHTS
    # STEP 41 - FINANCIAL HEALTH RECOMMENDATION
    # =====================================================

    financial_insights = (
        generate_financial_insights(

            monthly_income=
                monthly_income,

            monthly_spending=
                monthly_spending,

            monthly_allowance=
                monthly_allowance,

            monthly_savings=
                monthly_savings,

            savings_rate=
                savings_rate,

            category_totals=
                category_totals,

            # ---------------------------------------------
            # FINANCIAL HEALTH SCORE
            # ---------------------------------------------

            financial_health_score=
                financial_health_score,

            financial_health_budget=
                financial_health_budget,

            financial_health_savings=
                financial_health_savings,

            financial_health_spending=
                financial_health_spending,

            financial_health_goal=
                financial_health_goal

        )
    )


    # =====================================================
    # SMART FINANCIAL ALERTS
    # =====================================================

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


    # =====================================================
    # GEMINI AI FINANCIAL INSIGHT
    # =====================================================

    signature, _ = (
        _get_financial_state_signature()
    )


    ai_financial_insight, ai_insight_cached = (

        _generate_or_get_ai_insight(

            monthly_income=
                monthly_income,

            monthly_spending=
                monthly_spending,

            monthly_allowance=
                monthly_allowance,

            monthly_savings=
                monthly_savings,

            savings_rate=
                savings_rate,

            safe_daily_spending=
                safe_daily_spending,

            category_totals=
                category_totals,

            goal=
                current_goal,

            signature=
                signature

        )

    )


    # =====================================================
    # SHOW DASHBOARD
    # =====================================================

    return render_template(

        "dashboard/dashboard.html",


        # -------------------------------------------------
        # EXPENSE
        # -------------------------------------------------

        today_spending=
            today_spending,

        monthly_spending=
            monthly_spending,

        recent_expenses=
            recent_expenses,


        # -------------------------------------------------
        # BUDGET
        # -------------------------------------------------

        monthly_allowance=
            monthly_allowance,

        remaining=
            remaining,

        safe_daily_spending=
            safe_daily_spending,

        budget_percent=
            budget_percent,


        # -------------------------------------------------
        # INCOME
        # -------------------------------------------------

        monthly_income=
            monthly_income,

        recent_income=
            recent_income,


        # -------------------------------------------------
        # SAVINGS
        # -------------------------------------------------

        monthly_savings=
            monthly_savings,

        savings_rate=
            savings_rate,

        financial_status=
            financial_status,


        # -------------------------------------------------
        # CHART
        # -------------------------------------------------

        income_vs_expense=
            income_vs_expense,


        # -------------------------------------------------
        # CATEGORY DATA
        # -------------------------------------------------

        category_totals=
            category_totals,


        # -------------------------------------------------
        # SAVINGS GOAL
        # -------------------------------------------------

        current_goal=
            current_goal,

        goal_progress=
            goal_progress,

        goal_remaining=
            goal_remaining,

        goal_completed=
            goal_completed,


        # -------------------------------------------------
        # AI EXPENSE PREDICTION
        # -------------------------------------------------

        expense_prediction=
            expense_prediction,

        projected_monthly_spending=
            projected_monthly_spending,

        average_daily_spending=
            average_daily_spending,

        expense_prediction_status=
            expense_prediction_status,

        expense_prediction_message=
            expense_prediction_message,

        projected_budget_difference=
            projected_budget_difference,


        # -------------------------------------------------
        # FINANCIAL HEALTH SCORE
        # -------------------------------------------------

        financial_health_score=
            financial_health_score,

        financial_health_label=
            financial_health_label,

        financial_health_message=
            financial_health_message,

        financial_health_budget=
            financial_health_budget,

        financial_health_savings=
            financial_health_savings,

        financial_health_spending=
            financial_health_spending,

        financial_health_goal=
            financial_health_goal,


        # -------------------------------------------------
        # SMART FINANCIAL INSIGHTS
        # -------------------------------------------------

        financial_insights=
            financial_insights,


        # -------------------------------------------------
        # SMART FINANCIAL ALERTS
        # -------------------------------------------------

        financial_alerts=
            financial_alerts,


        # -------------------------------------------------
        # GEMINI AI FINANCIAL INSIGHT
        # -------------------------------------------------

        ai_financial_insight=
            ai_financial_insight,

        ai_insight_cached=
            ai_insight_cached

    )


# =========================================================
# GEMINI AI INSIGHT REFRESH ENDPOINT
# =========================================================

@dashboard.route(
    "/ai-insight",
    methods=["GET"]
)
@login_required
def dashboard_ai_insight():

    today = date.today()


    # =====================================================
    # USER EXPENSES
    # =====================================================

    expenses = Expense.query.filter_by(

        user_id=current_user.id

    ).order_by(

        Expense.date.desc()

    ).all()


    # =====================================================
    # CURRENT MONTH EXPENSES
    # =====================================================

    current_month_expenses = [

        expense

        for expense in expenses

        if (
            expense.date.year == today.year
            and
            expense.date.month == today.month
        )

    ]


    # =====================================================
    # MONTHLY SPENDING
    # =====================================================

    monthly_spending = sum(

        float(expense.amount or 0)

        for expense in current_month_expenses

    )


    # =====================================================
    # CATEGORY TOTALS
    # =====================================================

    category_totals = {}


    for expense in current_month_expenses:

        category = (
            expense.category
            or
            "Others"
        )


        if category not in category_totals:

            category_totals[category] = 0


        category_totals[category] += (

            float(
                expense.amount or 0
            )

        )


    # =====================================================
    # USER MONTHLY BUDGET
    # =====================================================

    monthly_allowance = float(

        current_user.monthly_budget or 0

    )


    # =====================================================
    # REMAINING BUDGET
    # =====================================================

    remaining = max(

        monthly_allowance -
        monthly_spending,

        0

    )


    # =====================================================
    # SAFE DAILY SPENDING
    # =====================================================

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


    if remaining > 0:

        safe_daily_spending = (

            remaining /
            days_remaining

        )

    else:

        safe_daily_spending = 0


    # =====================================================
    # USER INCOME
    # =====================================================

    incomes = Income.query.filter_by(

        user_id=current_user.id

    ).order_by(

        Income.date.desc()

    ).all()


    # =====================================================
    # CURRENT MONTH INCOME
    # =====================================================

    current_month_incomes = [

        income

        for income in incomes

        if (
            income.date.year == today.year
            and
            income.date.month == today.month
        )

    ]


    # =====================================================
    # MONTHLY INCOME
    # =====================================================

    monthly_income = sum(

        float(income.amount or 0)

        for income in current_month_incomes

    )


    # =====================================================
    # MONTHLY SAVINGS
    # =====================================================

    monthly_savings = (

        monthly_income -
        monthly_spending

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


    savings_rate = min(

        max(
            savings_rate,
            0
        ),

        100

    )


    # =====================================================
    # CURRENT SAVINGS GOAL
    # =====================================================

    current_goal = Goal.query.filter_by(

        user_id=current_user.id

    ).order_by(

        Goal.created_at.desc()

    ).first()


    # =====================================================
    # CACHE AWARE GEMINI INSIGHT
    # =====================================================

    signature, _ = (
        _get_financial_state_signature()
    )


    force_refresh = (

        request.args.get(
            "force",
            "0"
        ) == "1"

    )


    ai_financial_insight, ai_insight_cached = (

        _generate_or_get_ai_insight(

            monthly_income=
                monthly_income,

            monthly_spending=
                monthly_spending,

            monthly_allowance=
                monthly_allowance,

            monthly_savings=
                monthly_savings,

            savings_rate=
                savings_rate,

            safe_daily_spending=
                safe_daily_spending,

            category_totals=
                category_totals,

            goal=
                current_goal,

            signature=
                signature,

            force=
                force_refresh

        )

    )


    # =====================================================
    # RETURN JSON
    # =====================================================

    return jsonify({

        "success":
            True,

        "insight":
            ai_financial_insight,

        "signature":
            signature,

        "cached":
            ai_insight_cached,

        "monthly_income":
            round(
                monthly_income,
                2
            ),

        "monthly_spending":
            round(
                monthly_spending,
                2
            ),

        "monthly_allowance":
            round(
                monthly_allowance,
                2
            ),

        "monthly_savings":
            round(
                monthly_savings,
                2
            ),

        "savings_rate":
            round(
                savings_rate,
                1
            ),

        "safe_daily_spending":
            round(
                safe_daily_spending,
                2
            ),

        "remaining_budget":
            round(
                remaining,
                2
            )

    })


# =========================================================
# FINANCIAL STATE CHECK ENDPOINT
# =========================================================

@dashboard.route(
    "/ai-state",
    methods=["GET"]
)
@login_required
def dashboard_ai_state():

    signature, state = (
        _get_financial_state_signature()
    )


    return jsonify({

        "success":
            True,

        "signature":
            signature,

        "date":
            state["date"]

    })


# =========================================================
# STEP 24B - AI COMMAND CENTER ENDPOINT
# =========================================================

@dashboard.route(
    "/ai-command-center",
    methods=["GET"]
)
@login_required
def dashboard_ai_command_center():

    today = date.today()


    # =====================================================
    # CURRENT MONTH EXPENSES
    # =====================================================

    expenses = Expense.query.filter_by(

        user_id=current_user.id

    ).all()


    current_month_expenses = [

        expense

        for expense in expenses

        if (
            expense.date.year == today.year
            and
            expense.date.month == today.month
        )

    ]


    monthly_spending = sum(

        float(expense.amount or 0)

        for expense in current_month_expenses

    )


    # =====================================================
    # CATEGORY TOTALS
    # =====================================================

    category_totals = {}


    for expense in current_month_expenses:

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

            float(
                expense.amount or 0
            )

        )


    # =====================================================
    # CURRENT MONTH INCOME
    # =====================================================

    incomes = Income.query.filter_by(

        user_id=current_user.id

    ).all()


    current_month_incomes = [

        income

        for income in incomes

        if (
            income.date.year == today.year
            and
            income.date.month == today.month
        )

    ]


    monthly_income = sum(

        float(income.amount or 0)

        for income in current_month_incomes

    )


    # =====================================================
    # BUDGET
    # =====================================================

    monthly_allowance = float(

        current_user.monthly_budget or 0

    )


    # =====================================================
    # SAVINGS
    # =====================================================

    monthly_savings = (

        monthly_income -
        monthly_spending

    )


    if monthly_income > 0:

        savings_rate = (

            monthly_savings /
            monthly_income

        ) * 100

    else:

        savings_rate = 0


    savings_rate = min(

        max(
            savings_rate,
            0
        ),

        100

    )


    # =====================================================
    # REMAINING BUDGET
    # =====================================================

    remaining_budget = max(

        monthly_allowance -
        monthly_spending,

        0

    )


    # =====================================================
    # SAFE DAILY SPENDING
    # =====================================================

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


    if remaining_budget > 0:

        safe_daily_spending = (

            remaining_budget /
            days_remaining

        )

    else:

        safe_daily_spending = 0


    # =====================================================
    # CURRENT SAVINGS GOAL
    # =====================================================

    current_goal = Goal.query.filter_by(

        user_id=current_user.id

    ).order_by(

        Goal.created_at.desc()

    ).first()


    # =====================================================
    # BUILD COMMAND CENTER
    # =====================================================

    command_center = build_ai_command_center(

        monthly_income=
            monthly_income,

        monthly_spending=
            monthly_spending,

        monthly_allowance=
            monthly_allowance,

        monthly_savings=
            monthly_savings,

        savings_rate=
            savings_rate,

        safe_daily_spending=
            safe_daily_spending,

        category_totals=
            category_totals,

        goal=
            current_goal

    )


    # =====================================================
    # RETURN JSON
    # =====================================================

    return jsonify({

        "success":
            True,

        "command_center":
            command_center

    })
# =========================================================
# WHAT-IF FINANCIAL SIMULATOR
# =========================================================

@dashboard.route(
    "/what-if",
    methods=["POST"]
)
@login_required
def dashboard_what_if():
    """
    Simulate financial changes without modifying the database.

    Supported inputs:
        income_change
        expense_change
        budget_change
        goal_saving

    All values are hypothetical and are calculated from the
    user's current-month financial data.
    """

    today = date.today()

    # -----------------------------------------------------
    # READ REQUEST
    # -----------------------------------------------------

    data = request.get_json(silent=True) or {}

    def safe_float(value, default=0.0):
        try:
            number = float(value)
            if number != number:  # NaN
                return default
            return number
        except (TypeError, ValueError):
            return default

    income_change = safe_float(
        data.get("income_change", 0)
    )

    expense_change = safe_float(
        data.get("expense_change", 0)
    )

    budget_change = safe_float(
        data.get("budget_change", 0)
    )

    goal_saving = max(
        safe_float(
            data.get("goal_saving", 0)
        ),
        0
    )

    # -----------------------------------------------------
    # CURRENT MONTH EXPENSES
    # -----------------------------------------------------

    expenses = Expense.query.filter_by(
        user_id=current_user.id
    ).all()

    current_month_expenses = [
        expense
        for expense in expenses
        if (
            expense.date.year == today.year
            and
            expense.date.month == today.month
        )
    ]

    current_spending = sum(
        float(expense.amount or 0)
        for expense in current_month_expenses
    )

    # -----------------------------------------------------
    # CURRENT MONTH INCOME
    # -----------------------------------------------------

    incomes = Income.query.filter_by(
        user_id=current_user.id
    ).all()

    current_month_incomes = [
        income
        for income in incomes
        if (
            income.date.year == today.year
            and
            income.date.month == today.month
        )
    ]

    current_income = sum(
        float(income.amount or 0)
        for income in current_month_incomes
    )

    # -----------------------------------------------------
    # CURRENT BUDGET
    # -----------------------------------------------------

    current_budget = float(
        current_user.monthly_budget or 0
    )

    # -----------------------------------------------------
    # APPLY HYPOTHETICAL CHANGES
    # -----------------------------------------------------

    simulated_income = max(
        current_income + income_change,
        0
    )

    # Positive expense_change means additional spending.
    # Negative expense_change means reducing spending.
    simulated_spending = max(
        current_spending + expense_change,
        0
    )

    simulated_budget = max(
        current_budget + budget_change,
        0
    )

    # Optional one-time savings contribution to a goal.
    simulated_goal_saving = goal_saving

    # -----------------------------------------------------
    # SAVINGS
    # -----------------------------------------------------

    simulated_savings = (
        simulated_income -
        simulated_spending -
        simulated_goal_saving
    )

    # Savings before goal contribution.
    savings_before_goal = (
        simulated_income -
        simulated_spending
    )

    if simulated_income > 0:
        simulated_savings_rate = (
            savings_before_goal /
            simulated_income
        ) * 100
    else:
        simulated_savings_rate = 0

    simulated_savings_rate = min(
        max(simulated_savings_rate, 0),
        100
    )

    # -----------------------------------------------------
    # BUDGET STATUS
    # -----------------------------------------------------

    if simulated_budget > 0:
        budget_usage = (
            simulated_spending /
            simulated_budget
        ) * 100
    else:
        budget_usage = 0

    budget_remaining = max(
        simulated_budget -
        simulated_spending,
        0
    )

    # -----------------------------------------------------
    # DAYS REMAINING
    # -----------------------------------------------------

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

    if budget_remaining > 0:
        simulated_safe_daily = (
            budget_remaining /
            days_remaining
        )
    else:
        simulated_safe_daily = 0

    # -----------------------------------------------------
    # FINANCIAL HEALTH SCORE
    # -----------------------------------------------------

    current_goal = Goal.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Goal.created_at.desc()
    ).first()

    if current_goal:
        target = float(
            current_goal.target_amount or 0
        )
        saved = float(
            current_goal.saved_amount or 0
        )

        if target > 0:
            goal_progress = min(
                max(
                    (
                        (
                            saved +
                            simulated_goal_saving
                        ) /
                        target
                    ) * 100,
                    0
                ),
                100
            )
        else:
            goal_progress = 0
    else:
        goal_progress = 0

    health = _calculate_financial_health_score(
        monthly_income=simulated_income,
        monthly_spending=simulated_spending,
        monthly_allowance=simulated_budget,
        monthly_savings=simulated_savings,
        savings_rate=simulated_savings_rate,
        goal_progress=goal_progress
    )

    # -----------------------------------------------------
    # IMPACT VS CURRENT FINANCIAL POSITION
    # -----------------------------------------------------

    current_savings = (
        current_income -
        current_spending
    )

    savings_difference = (
        simulated_savings -
        current_savings
    )

    budget_difference = (
        simulated_budget -
        current_budget
    )

    spending_difference = (
        simulated_spending -
        current_spending
    )

    health_difference = (
        health["score"] -
        _calculate_financial_health_score(
            monthly_income=current_income,
            monthly_spending=current_spending,
            monthly_allowance=current_budget,
            monthly_savings=current_savings,
            savings_rate=(
                (
                    current_savings /
                    current_income
                ) * 100
                if current_income > 0
                else 0
            ),
            goal_progress=(
                (
                    float(current_goal.saved_amount or 0) /
                    float(current_goal.target_amount or 1)
                ) * 100
                if current_goal and
                float(current_goal.target_amount or 0) > 0
                else 0
            )
        )["score"]
    )

    # -----------------------------------------------------
    # RESULT STATUS + RECOMMENDATION
    # -----------------------------------------------------

    if simulated_savings < 0:
        result_status = "danger"
        result_icon = "🚨"
        result_title = "This scenario puts you in a deficit."
        recommendation = (
            "Reduce spending or increase income before "
            "following this plan."
        )

    elif health["score"] >= 85:
        result_status = "excellent"
        result_icon = "🚀"
        result_title = "Excellent financial scenario."
        recommendation = (
            "This scenario strengthens your savings and "
            "overall financial health."
        )

    elif health["score"] >= 70:
        result_status = "good"
        result_icon = "🟢"
        result_title = "This scenario looks healthy."
        recommendation = (
            "You are moving in a financially sustainable "
            "direction."
        )

    elif health["score"] >= 50:
        result_status = "fair"
        result_icon = "🟡"
        result_title = "This scenario is workable."
        recommendation = (
            "There is room to improve your savings or "
            "spending control."
        )

    else:
        result_status = "attention"
        result_icon = "⚠️"
        result_title = "This scenario needs attention."
        recommendation = (
            "Try lowering expenses, increasing income, "
            "or setting a more realistic budget."
        )

    # -----------------------------------------------------
    # RETURN SIMULATION
    # -----------------------------------------------------

    return jsonify({
        "success": True,

        "current": {
            "income": round(current_income, 2),
            "spending": round(current_spending, 2),
            "budget": round(current_budget, 2),
            "savings": round(current_savings, 2)
        },

        "changes": {
            "income": round(income_change, 2),
            "expense": round(expense_change, 2),
            "budget": round(budget_change, 2),
            "goal_saving": round(
                simulated_goal_saving,
                2
            )
        },

        "simulation": {
            "income": round(
                simulated_income,
                2
            ),
            "spending": round(
                simulated_spending,
                2
            ),
            "budget": round(
                simulated_budget,
                2
            ),
            "savings": round(
                simulated_savings,
                2
            ),
            "savings_before_goal": round(
                savings_before_goal,
                2
            ),
            "savings_rate": round(
                simulated_savings_rate,
                1
            ),
            "budget_usage": round(
                min(max(budget_usage, 0), 100),
                1
            ),
            "budget_remaining": round(
                budget_remaining,
                2
            ),
            "safe_daily_spending": round(
                simulated_safe_daily,
                2
            ),
            "goal_progress": round(
                goal_progress,
                1
            )
        },

        "health": {
            "score": health["score"],
            "label": health["label"],
            "message": health["message"],
            "budget": health["budget"],
            "savings": health["savings"],
            "spending": health["spending"],
            "goal": health["goal"],
            "difference": round(
                health_difference,
                1
            )
        },

        "impact": {
            "savings_difference": round(
                savings_difference,
                2
            ),
            "spending_difference": round(
                spending_difference,
                2
            ),
            "budget_difference": round(
                budget_difference,
                2
            ),
            "health_difference": round(
                health_difference,
                1
            )
        },

        "result": {
            "status": result_status,
            "icon": result_icon,
            "title": result_title,
            "recommendation": recommendation
        },

        "days_remaining": days_remaining
    })