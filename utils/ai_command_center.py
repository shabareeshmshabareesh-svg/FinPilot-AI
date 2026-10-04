# =========================================
# FINPILOT AI COMMAND CENTER
# =========================================

from utils.financial_insights import (
    generate_financial_insights
)

from utils.financial_alerts import (
    generate_financial_alerts
)


# =========================================
# BUILD AI COMMAND CENTER
# =========================================

def build_ai_command_center(
    monthly_income=0,
    monthly_spending=0,
    monthly_allowance=0,
    monthly_savings=0,
    savings_rate=0,
    safe_daily_spending=0,
    category_totals=None,
    goal=None
):

    # =====================================
    # SAFE VALUES
    # =====================================

    monthly_income = float(
        monthly_income or 0
    )

    monthly_spending = float(
        monthly_spending or 0
    )

    monthly_allowance = float(
        monthly_allowance or 0
    )

    monthly_savings = float(
        monthly_savings or 0
    )

    savings_rate = float(
        savings_rate or 0
    )

    safe_daily_spending = float(
        safe_daily_spending or 0
    )


    category_totals = (
        category_totals or {}
    )


    # =====================================
    # FINANCIAL INSIGHTS
    # =====================================

    insights = generate_financial_insights(

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
            category_totals

    )


    # =====================================
    # FINANCIAL ALERTS
    # =====================================

    alerts = generate_financial_alerts(

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


    # =====================================
    # BUDGET USAGE
    # =====================================

    if monthly_allowance > 0:

        budget_usage_percent = (

            monthly_spending /
            monthly_allowance

        ) * 100

    else:

        budget_usage_percent = 0


    budget_usage_percent = round(

        budget_usage_percent,

        1

    )


    # =====================================
    # REMAINING BUDGET
    # =====================================

    remaining_budget = max(

        monthly_allowance -
        monthly_spending,

        0

    )


    # =====================================
    # TOP CATEGORY
    # =====================================

    top_category = None

    top_category_amount = 0

    top_category_percent = 0


    if category_totals:

        cleaned_categories = {

            str(category):
            float(amount or 0)

            for category, amount
            in category_totals.items()

        }


        if cleaned_categories:

            top_category = max(

                cleaned_categories,

                key=cleaned_categories.get

            )


            top_category_amount = (
                cleaned_categories[
                    top_category
                ]
            )


            if monthly_spending > 0:

                top_category_percent = (

                    top_category_amount /
                    monthly_spending

                ) * 100


    top_category_percent = round(

        top_category_percent,

        1

    )


    # =====================================
    # GOAL DATA
    # =====================================

    goal_data = {

        "active": False,

        "name": None,

        "target": 0,

        "saved": 0,

        "remaining": 0,

        "progress_percent": 0

    }


    if goal:

        goal_name = getattr(

            goal,
            "name",
            "Savings Goal"

        )

        goal_target = float(

            getattr(
                goal,
                "target_amount",
                0
            ) or 0

        )

        goal_saved = float(

            getattr(
                goal,
                "saved_amount",
                0
            ) or 0

        )


        goal_remaining = max(

            goal_target -
            goal_saved,

            0

        )


        if goal_target > 0:

            goal_progress = (

                goal_saved /
                goal_target

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


        goal_data = {

            "active": True,

            "name": goal_name,

            "target":
                round(
                    goal_target,
                    2
                ),

            "saved":
                round(
                    goal_saved,
                    2
                ),

            "remaining":
                round(
                    goal_remaining,
                    2
                ),

            "progress_percent":
                round(
                    goal_progress,
                    1
                )

        }


    # =====================================
    # FINANCIAL HEALTH
    # =====================================

    if monthly_income <= 0:

        health_status = "NO_INCOME"

        health_label = (
            "No Income Data"
        )

        health_icon = "ℹ️"


    elif monthly_savings < 0:

        health_status = "DEFICIT"

        health_label = (
            "Spending Above Income"
        )

        health_icon = "🚨"


    elif (
        monthly_allowance > 0
        and monthly_spending >
        monthly_allowance
    ):

        health_status = "OVER_BUDGET"

        health_label = (
            "Over Budget"
        )

        health_icon = "⚠️"


    elif budget_usage_percent >= 90:

        health_status = "VERY_TIGHT"

        health_label = (
            "Budget Almost Exhausted"
        )

        health_icon = "🔴"


    elif budget_usage_percent >= 75:

        health_status = "BUDGET_TIGHT"

        health_label = (
            "Budget Getting Tight"
        )

        health_icon = "🟡"


    else:

        health_status = "HEALTHY"

        health_label = (
            "Healthy"
        )

        health_icon = "🟢"


    # =====================================
    # PRIORITY
    # =====================================

    priority = "GENERAL"

    priority_icon = "💡"


    if health_status == "DEFICIT":

        priority = (
            "REDUCE_SPENDING"
        )

        priority_icon = "🚨"


    elif health_status == "OVER_BUDGET":

        priority = (
            "CONTROL_BUDGET"
        )

        priority_icon = "⚠️"


    elif health_status == "VERY_TIGHT":

        priority = (
            "PROTECT_REMAINING_BUDGET"
        )

        priority_icon = "🔴"


    elif (
        top_category
        and top_category_percent >= 40
    ):

        priority = (
            "REVIEW_TOP_CATEGORY"
        )

        priority_icon = "📊"


    elif (
        goal_data["active"]
        and goal_data["remaining"] > 0
    ):

        priority = (
            "FOCUS_ON_GOAL"
        )

        priority_icon = "🎯"


    elif monthly_savings > 0:

        priority = (
            "PROTECT_SAVINGS"
        )

        priority_icon = "💰"


    # =====================================
    # RECOMMENDED ACTION
    # =====================================

    if priority == "REDUCE_SPENDING":

        recommended_action = (
            "Reduce non-essential spending "
            "and keep new purchases limited."
        )


    elif priority == "CONTROL_BUDGET":

        recommended_action = (
            "Avoid unnecessary purchases "
            "until spending returns within "
            "your monthly budget."
        )


    elif priority == (
        "PROTECT_REMAINING_BUDGET"
    ):

        recommended_action = (
            "Keep daily spending close to "
            "your safe spending limit."
        )


    elif priority == (
        "REVIEW_TOP_CATEGORY"
    ):

        recommended_action = (

            f"Review your {top_category} "
            "spending and reduce avoidable "
            "expenses if possible."

        )


    elif priority == "FOCUS_ON_GOAL":

        recommended_action = (
            "Protect part of your savings "
            "for your current goal."
        )


    elif priority == "PROTECT_SAVINGS":

        recommended_action = (
            "Continue your current saving "
            "habit and avoid unnecessary "
            "withdrawals."
        )


    else:

        recommended_action = (
            "Continue tracking income and "
            "expenses consistently."
        )


    # =====================================
    # RETURN COMMAND CENTER
    # =====================================

    return {

        "financial_health": {

            "status":
                health_status,

            "label":
                health_label,

            "icon":
                health_icon

        },


        "budget": {

            "monthly":
                round(
                    monthly_allowance,
                    2
                ),

            "spent":
                round(
                    monthly_spending,
                    2
                ),

            "remaining":
                round(
                    remaining_budget,
                    2
                ),

            "usage_percent":
                budget_usage_percent

        },


        "income": {

            "monthly":
                round(
                    monthly_income,
                    2
                )

        },


        "savings": {

            "monthly":
                round(
                    monthly_savings,
                    2
                ),

            "rate_percent":
                round(
                    savings_rate,
                    1
                )

        },


        "safe_daily_spending":
            round(
                safe_daily_spending,
                2
            ),


        "top_category": {

            "name":
                top_category,

            "amount":
                round(
                    top_category_amount,
                    2
                ),

            "percentage":
                top_category_percent

        },


        "goal":
            goal_data,


        "priority": {

            "name":
                priority,

            "icon":
                priority_icon,

            "recommended_action":
                recommended_action

        },


        "insights":
            insights,


        "alerts":
            alerts

    }