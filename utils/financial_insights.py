# =========================================
# FINPILOT AI - FINANCIAL INSIGHTS
# =========================================


def generate_financial_insights(
    monthly_income=0,
    monthly_spending=0,
    monthly_allowance=0,
    monthly_savings=0,
    savings_rate=0,
    category_totals=None,
    financial_health_score=None,
    financial_health_budget=None,
    financial_health_savings=None,
    financial_health_spending=None,
    financial_health_goal=None
):
    """
    Generate dashboard-friendly financial insights.

    IMPORTANT:
    This function returns a LIST of DICTIONARIES.

    dashboard.html expects:

        insight.type
        insight.icon
        insight.title
        insight.message
    """


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

    category_totals = (
        category_totals or {}
    )


    # =====================================
    # RESULT
    # =====================================

    insights = []


    # =====================================
    # NO INCOME
    # =====================================

    if monthly_income <= 0:

        insights.append({

            "type": "info",

            "icon": "💡",

            "title": "Start Tracking Your Income",

            "message": (
                "Add your income so FinPilot can "
                "calculate your savings rate and "
                "give you more accurate financial guidance."
            )

        })


    # =====================================
    # SAVING MONEY
    # =====================================

    elif monthly_savings > 0:

        insights.append({

            "type": "success",

            "icon": "💰",

            "title": "You're Building Savings",

            "message": (
                f"You've saved ₹{monthly_savings:,.2f} "
                f"this month, which is about "
                f"{savings_rate:.1f}% of your income. "
                "Keep protecting your savings."
            )

        })


    # =====================================
    # SPENDING MORE THAN INCOME
    # =====================================

    elif monthly_savings < 0:

        insights.append({

            "type": "danger",

            "icon": "🚨",

            "title": "Spending Is Higher Than Income",

            "message": (
                f"You're currently spending "
                f"₹{abs(monthly_savings):,.2f} more than "
                "your income this month. Consider "
                "reducing non-essential expenses."
            )

        })


    # =====================================
    # BALANCED
    # =====================================

    else:

        insights.append({

            "type": "warning",

            "icon": "⚖️",

            "title": "Income and Spending Are Balanced",

            "message": (
                "Your income currently matches your "
                "spending. Try reducing unnecessary "
                "expenses so you can start building savings."
            )

        })


    # =====================================
    # BUDGET INSIGHT
    # =====================================

    if monthly_allowance > 0:

        budget_percent = (

            monthly_spending /
            monthly_allowance

        ) * 100


        # ---------------------------------
        # OVER BUDGET
        # ---------------------------------

        if monthly_spending > monthly_allowance:

            overspent = (

                monthly_spending -
                monthly_allowance

            )

            insights.append({

                "type": "danger",

                "icon": "⚠️",

                "title": "Budget Exceeded",

                "message": (
                    f"You are ₹{overspent:,.2f} "
                    "over your monthly budget. "
                    "Try limiting non-essential spending "
                    "for the rest of the month."
                )

            })


        # ---------------------------------
        # VERY HIGH USAGE
        # ---------------------------------

        elif budget_percent >= 90:

            remaining = max(

                monthly_allowance -
                monthly_spending,

                0

            )

            insights.append({

                "type": "warning",

                "icon": "🔴",

                "title": "Your Budget Is Almost Used",

                "message": (
                    f"You've used {budget_percent:.1f}% "
                    f"of your budget. Only "
                    f"₹{remaining:,.2f} remains."
                )

            })


        # ---------------------------------
        # BUDGET GETTING TIGHT
        # ---------------------------------

        elif budget_percent >= 75:

            remaining = max(

                monthly_allowance -
                monthly_spending,

                0

            )

            insights.append({

                "type": "warning",

                "icon": "🟡",

                "title": "Budget Is Getting Tight",

                "message": (
                    f"You've used {budget_percent:.1f}% "
                    f"of your budget. "
                    f"₹{remaining:,.2f} remains, "
                    "so keep larger purchases under control."
                )

            })


        # ---------------------------------
        # HEALTHY BUDGET
        # ---------------------------------

        else:

            remaining = max(

                monthly_allowance -
                monthly_spending,

                0

            )

            insights.append({

                "type": "success",

                "icon": "🛡️",

                "title": "Budget Looks Healthy",

                "message": (
                    f"You've used {budget_percent:.1f}% "
                    f"of your monthly budget and have "
                    f"₹{remaining:,.2f} remaining."
                )

            })


    # =====================================
    # TOP SPENDING CATEGORY
    # =====================================

    if category_totals:

        valid_categories = {

            category: float(amount or 0)

            for category, amount
            in category_totals.items()

        }


        if valid_categories:

            top_category = max(

                valid_categories,

                key=valid_categories.get

            )

            top_amount = valid_categories[
                top_category
            ]


            if top_amount > 0:

                insights.append({

                    "type": "info",

                    "icon": "📊",

                    "title": (
                        f"Top Spending: {top_category}"
                    ),

                    "message": (
                        f"{top_category} is currently "
                        f"your highest spending category "
                        f"at ₹{top_amount:,.2f} this month."
                    )

                })


    # =====================================
    # SAVINGS RATE
    # =====================================

    if monthly_income > 0:

        if savings_rate >= 30:

            insights.append({

                "type": "success",

                "icon": "🚀",

                "title": "Excellent Savings Rate",

                "message": (
                    f"You're saving {savings_rate:.1f}% "
                    "of your income. That's a strong "
                    "saving habit."
                )

            })

        elif savings_rate >= 20:

            insights.append({

                "type": "success",

                "icon": "✨",

                "title": "Good Savings Progress",

                "message": (
                    f"You're saving {savings_rate:.1f}% "
                    "of your income. Keep maintaining "
                    "this habit."
                )

            })

        elif savings_rate > 0:

            insights.append({

                "type": "info",

                "icon": "💡",

                "title": "Room to Increase Savings",

                "message": (
                    f"Your current savings rate is "
                    f"{savings_rate:.1f}%. If possible, "
                    "try gradually increasing the amount "
                    "you save each month."
                )

            })


    # =====================================
    # STEP 41
    # FINANCIAL HEALTH RECOMMENDATION
    # =====================================

    if financial_health_score is not None:

        try:

            health_score = float(
                financial_health_score or 0
            )

        except (
            TypeError,
            ValueError
        ):

            health_score = 0


        # ---------------------------------
        # SAFE FACTOR VALUES
        # ---------------------------------

        factors = {

            "Budget Control":
                float(
                    financial_health_budget or 0
                ),

            "Savings Health":
                float(
                    financial_health_savings or 0
                ),

            "Spending Control":
                float(
                    financial_health_spending or 0
                ),

            "Goal Progress":
                float(
                    financial_health_goal or 0
                )

        }


        # ---------------------------------
        # FIND WEAKEST AREA
        # ---------------------------------

        weakest_area = min(

            factors,

            key=factors.get

        )


        weakest_score = factors[
            weakest_area
        ]


        # ---------------------------------
        # BUDGET RECOMMENDATION
        # ---------------------------------

        if weakest_area == "Budget Control":

            recommendation_title = (
                "Strengthen Your Budget Control"
            )

            recommendation_message = (
                f"Your budget-control score is "
                f"{weakest_score:.0f}/100. "
                "Review your largest expenses and "
                "set a clear spending limit for the "
                "rest of the month."
            )


        # ---------------------------------
        # SAVINGS RECOMMENDATION
        # ---------------------------------

        elif weakest_area == "Savings Health":

            recommendation_title = (
                "Build Your Savings Habit"
            )

            recommendation_message = (
                f"Your savings-health score is "
                f"{weakest_score:.0f}/100. "
                "Try setting aside a fixed amount "
                "from every income entry before "
                "spending on non-essential items."
            )


        # ---------------------------------
        # SPENDING RECOMMENDATION
        # ---------------------------------

        elif weakest_area == "Spending Control":

            recommendation_title = (
                "Control Your Spending"
            )

            recommendation_message = (
                f"Your spending-control score is "
                f"{weakest_score:.0f}/100. "
                "Focus on reducing unnecessary "
                "purchases and keep your daily "
                "spending within FinPilot's safe limit."
            )


        # ---------------------------------
        # GOAL RECOMMENDATION
        # ---------------------------------

        else:

            recommendation_title = (
                "Move Your Savings Goal Forward"
            )

            recommendation_message = (
                f"Your goal-progress score is "
                f"{weakest_score:.0f}/100. "
                "Try increasing your regular "
                "contribution toward your active "
                "savings goal."
            )


        # ---------------------------------
        # SCORE-BASED MESSAGE
        # ---------------------------------

        if health_score >= 85:

            recommendation_type = "success"

            recommendation_icon = "🏆"

            recommendation_title = (
                "Excellent Financial Health"
            )

            recommendation_message = (
                "Your financial health is excellent. "
                f"Your score is {health_score:.0f}/100. "
                "Keep your current habits and continue "
                "building long-term financial stability."
            )


        elif health_score >= 70:

            recommendation_type = "success"

            recommendation_icon = "🚀"

            recommendation_message = (
                f"Your financial health score is "
                f"{health_score:.0f}/100. "
                f"Your main opportunity is improving "
                f"{weakest_area.lower()}. "
                "A few consistent improvements can "
                "push your score even higher."
            )


        elif health_score >= 50:

            recommendation_type = "warning"

            recommendation_icon = "💡"


        elif health_score >= 30:

            recommendation_type = "warning"

            recommendation_icon = "⚠️"

            recommendation_message = (
                f"Your financial health score is "
                f"{health_score:.0f}/100. "
                f"Your biggest area to improve is "
                f"{weakest_area.lower()}. "
                "Start with one small change this month "
                "and build from there."
            )


        else:

            recommendation_type = "danger"

            recommendation_icon = "🚨"

            recommendation_title = (
                "Financial Health Needs Attention"
            )

            recommendation_message = (
                f"Your financial health score is "
                f"{health_score:.0f}/100. "
                f"Start by improving "
                f"{weakest_area.lower()}. "
                "Review your spending and create "
                "a realistic plan for the rest of the month."
            )


        insights.append({

            "type":
                recommendation_type,

            "icon":
                recommendation_icon,

            "title":
                recommendation_title,

            "message":
                recommendation_message,

            "priority":
                "financial_health"

        })


    # =====================================
    # MAXIMUM INSIGHTS
    # =====================================

    insights = insights[:5]


    # =====================================
    # FALLBACK
    # =====================================

    if not insights:

        insights.append({

            "type": "info",

            "icon": "🧠",

            "title": "Keep Tracking",

            "message": (
                "Continue adding your income and "
                "expenses so FinPilot can understand "
                "your financial habits."
            )

        })


    # =====================================
    # RETURN
    # =====================================

    return insights