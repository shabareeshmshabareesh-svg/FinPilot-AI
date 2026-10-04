def generate_financial_alerts(
    monthly_income,
    monthly_spending,
    monthly_allowance,
    monthly_savings,
    safe_daily_spending,
    category_totals
):

    alerts = []


    # =========================================
    # 1. NO BUDGET
    # =========================================

    if monthly_allowance <= 0:

        alerts.append({
            "type": "info",
            "icon": "🎯",
            "title": "Set your monthly budget",
            "message": (
                "Set a monthly budget to get personalized "
                "spending alerts and safe daily limits."
            )
        })


    else:

        # =========================================
        # BUDGET USAGE
        # =========================================

        budget_usage = (
            monthly_spending /
            monthly_allowance
        ) * 100


        # =========================================
        # BUDGET OVER
        # =========================================

        if budget_usage >= 100:

            overspent = (
                monthly_spending -
                monthly_allowance
            )

            alerts.append({
                "type": "danger",
                "icon": "🚨",
                "title": "Budget exceeded",
                "message": (
                    f"You have exceeded your monthly budget "
                    f"by ₹{overspent:.2f}."
                )
            })


        # =========================================
        # 90% BUDGET
        # =========================================

        elif budget_usage >= 90:

            remaining = (
                monthly_allowance -
                monthly_spending
            )

            alerts.append({
                "type": "danger",
                "icon": "🔴",
                "title": "Budget almost exhausted",
                "message": (
                    f"You have used {budget_usage:.1f}% "
                    f"of your budget. Only ₹{remaining:.2f} "
                    "is remaining."
                )
            })


        # =========================================
        # 75% BUDGET
        # =========================================

        elif budget_usage >= 75:

            remaining = (
                monthly_allowance -
                monthly_spending
            )

            alerts.append({
                "type": "warning",
                "icon": "⚠️",
                "title": "Watch your spending",
                "message": (
                    f"You have used {budget_usage:.1f}% "
                    f"of your budget. ₹{remaining:.2f} "
                    "is remaining."
                )
            })


        # =========================================
        # HEALTHY BUDGET
        # =========================================

        else:

            alerts.append({
                "type": "success",
                "icon": "🛡️",
                "title": "Budget is under control",
                "message": (
                    f"You have used {budget_usage:.1f}% "
                    "of your monthly budget."
                )
            })


    # =========================================
    # 2. SPENDING ABOVE INCOME
    # =========================================

    if monthly_income > 0 and monthly_spending > monthly_income:

        overspending = (
            monthly_spending -
            monthly_income
        )

        alerts.append({
            "type": "danger",
            "icon": "💸",
            "title": "Spending is above income",
            "message": (
                f"You have spent ₹{overspending:.2f} "
                "more than your income this month."
            )
        })


    # =========================================
    # 3. SAFE DAILY SPENDING
    # =========================================

    if monthly_allowance > 0:

        alerts.append({
            "type": "info",
            "icon": "🛡️",
            "title": "Today's safe spending limit",
            "message": (
                f"Try to keep today's spending around "
                f"₹{safe_daily_spending:.2f} "
                "to stay within your budget."
            )
        })


    # =========================================
    # 4. TOP SPENDING CATEGORY
    # =========================================

    if category_totals and monthly_spending > 0:

        top_category = max(
            category_totals,
            key=category_totals.get
        )

        top_amount = category_totals[
            top_category
        ]


        category_percentage = (
            top_amount /
            monthly_spending
        ) * 100


        # Alert only when category
        # is a significant portion.

        if category_percentage >= 40:

            alerts.append({
                "type": "warning",
                "icon": "📊",
                "title": f"High {top_category} spending",
                "message": (
                    f"{top_category} accounts for "
                    f"{category_percentage:.1f}% of your "
                    f"monthly spending."
                )
            })


    # =========================================
    # 5. POSITIVE SAVINGS
    # =========================================

    if monthly_income > 0 and monthly_savings > 0:

        alerts.append({
            "type": "success",
            "icon": "🎉",
            "title": "You're saving money",
            "message": (
                f"You have saved ₹{monthly_savings:.2f} "
                "this month. Keep it going!"
            )
        })


    # =========================================
    # RETURN ALERTS
    # =========================================

    return alerts