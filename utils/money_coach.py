import re

from utils.gemini_ai import (
    ask_gemini_money_coach
)


# =========================================
# FINPILOT CONVERSATION CONTEXT
# =========================================

def build_contextual_question(question, chat_history):
    """
    Add recent conversation context when history is available.
    This lets FinPilot understand follow-up questions such as
    "why is that high?" or "what about the previous one?".
    """
    clean_question = (question or "").strip()

    if not chat_history:
        return clean_question

    recent = []

    for item in chat_history[-6:]:
        if not isinstance(item, dict):
            continue

        role = str(item.get("role", "")).strip().lower()

        content = (
            item.get("content")
            or item.get("message")
            or item.get("text")
            or ""
        )

        content = str(content).strip()

        if not content:
            continue

        if role in ("user", "human"):
            label = "User"
        elif role in ("assistant", "ai"):
            label = "FinPilot AI"
        else:
            label = role or "Message"

        recent.append(
            f"{label}: {content}"
        )

    if not recent:
        return clean_question

    history_text = "\n".join(recent)

    return (
        "Use the following recent FinPilot AI conversation "
        "as context for the user's latest question. "
        "Resolve references such as 'that', 'it', 'this', "
        "'the previous one', or 'why' using the conversation "
        "when appropriate. Do not repeat the conversation "
        "unless it helps answer the question.\n\n"
        "RECENT CONVERSATION:\n"
        f"{history_text}\n\n"
        "LATEST USER QUESTION:\n"
        f"{clean_question}"
    )


def clean_ai_response(response):
    """
    Normalize escaped line breaks returned by the AI layer.
    """
    if response is None:
        return ""

    cleaned = str(response)

    cleaned = cleaned.replace("\\r\\n", "\n")
    cleaned = cleaned.replace("\\n", "\n")
    cleaned = cleaned.replace("\\r", "")
    cleaned = cleaned.replace("\\t", "\t")

    return cleaned


# =========================================
# FINPILOT INTENT DETECTOR
# =========================================

def detect_financial_intent(question):

    question_lower = (
        question or ""
    ).lower().strip()


    # =====================================
    # DAILY SPENDING
    # =====================================

    daily_keywords = [

        "how much can i spend today",
        "how much can i safely spend today",
        "daily limit",
        "safe daily spending",
        "daily spending limit",
        "daily spending",
        "how much should i spend today",
        "how much can i spend per day",
        "spending limit today",
        "spend today"

    ]

    if any(
        keyword in question_lower
        for keyword in daily_keywords
    ):
        return "daily_spending"


    # =====================================
    # GOAL
    # =====================================

    goal_keywords = [

        "goal",
        "target",
        "saving for",
        "savings goal",
        "goal progress",
        "goal doing",
        "reach my goal",
        "how far am i from my goal"

    ]

    if any(
        keyword in question_lower
        for keyword in goal_keywords
    ):
        return "goal"


    # =====================================
    # SAVINGS
    # =====================================

    savings_keywords = [

        "saving",
        "savings",
        "save money",
        "how much am i saving",
        "monthly saving",
        "monthly savings",
        "save this month",
        "surplus",
        "how much did i save"

    ]

    if any(
        keyword in question_lower
        for keyword in savings_keywords
    ):
        return "savings"


    # =====================================
    # BUDGET
    # =====================================

    budget_keywords = [

        "budget",
        "remaining budget",
        "budget remaining",
        "budget left",
        "how much budget",
        "how much money do i have left",
        "money left",
        "how much can i spend"

    ]

    if any(
        keyword in question_lower
        for keyword in budget_keywords
    ):
        return "budget"


    # =====================================
    # CATEGORY SPENDING
    # =====================================

    category_keywords = [

        "where am i spending the most",
        "where am i spending most",
        "what am i spending the most on",
        "what do i spend the most on",
        "highest spending category",
        "top spending category",
        "top expense category",
        "biggest expense category",
        "biggest spending category",
        "which category do i spend the most",
        "which category am i spending the most",
        "spending by category",
        "expense by category",
        "category spending",
        "my spending categories",
        "my expense categories"

    ]

    if any(
        keyword in question_lower
        for keyword in category_keywords
    ):
        return "category_spending"


    # =====================================
    # PURCHASE
    # =====================================

    purchase_keywords = [

        "buy",
        "purchase",
        "afford",
        "pay",
        "spend",
        "get this",
        "get these",
        "should i get",
        "should i buy",
        "can i get",
        "can i buy",
        "can i pay",
        "is it okay to buy",
        "is it okay if i spend",
        "worth buying",
        "worth it",
        "cost",
        "price",
        "expense",
        "fee",
        "fees",
        "membership",
        "bill",
        "payment",
        "renew",
        "renewal",
        "headphones",
        "shoes",
        "watch",
        "clothes",
        "phone",
        "laptop",
        "subscription",
        "gym"

    ]

    if any(
        keyword in question_lower
        for keyword in purchase_keywords
    ):
        return "purchase"


    # =====================================
    # GENERAL
    # =====================================

    return "general"


# =========================================
# FINPILOT MONEY COACH
# STEP 13 - NATURAL LANGUAGE ENGINE
# =========================================

def _money_coach_response_engine(
    question,
    monthly_income,
    monthly_spending,
    monthly_budget,
    monthly_savings,
    safe_daily_spending,
    goal=None,
    category_totals=None,
    category_percentages=None,
    top_category=None,
    top_category_amount=0,
    chat_history=None
):

    # =====================================
    # CLEAN QUESTION
    # =====================================

    question = (
        question or ""
    ).strip()

    question_lower = question.lower()


    # =====================================
    # CHAT HISTORY
    # =====================================

    if chat_history is None:
        chat_history = []

    contextual_question = build_contextual_question(
        question,
        chat_history
    )


    # =====================================
    # CATEGORY DATA
    # =====================================

    category_totals = category_totals or {}
    category_percentages = category_percentages or {}

    # Convert category amounts safely to floats.
    safe_category_totals = {}

    for category, amount in category_totals.items():

        try:
            safe_category_totals[str(category)] = float(
                amount or 0
            )
        except (TypeError, ValueError):
            continue

    category_totals = safe_category_totals

    # If the caller did not provide percentages,
    # calculate them from monthly spending.
    if not category_percentages and monthly_spending > 0:

        category_percentages = {
            category: (
                amount / monthly_spending
            ) * 100
            for category, amount in category_totals.items()
            if amount > 0
        }

    else:

        safe_category_percentages = {}

        for category, percentage in category_percentages.items():

            try:
                safe_category_percentages[str(category)] = float(
                    percentage or 0
                )
            except (TypeError, ValueError):
                continue

        category_percentages = safe_category_percentages

    # Determine the top category automatically when it is not supplied.
    if category_totals:

        calculated_top_category = max(
            category_totals,
            key=category_totals.get
        )

        calculated_top_amount = category_totals[
            calculated_top_category
        ]

    else:

        calculated_top_category = None
        calculated_top_amount = 0

    top_category = (
        top_category or calculated_top_category
    )

    try:
        top_category_amount = float(
            top_category_amount or calculated_top_amount
        )
    except (TypeError, ValueError):
        top_category_amount = calculated_top_amount


    # =====================================
    # BASIC FINANCIAL CALCULATIONS
    # =====================================

    remaining_budget = max(
        monthly_budget - monthly_spending,
        0
    )

    actual_surplus = (
        monthly_income -
        monthly_spending
    )


    # =====================================
    # BUDGET USAGE
    # =====================================

    spending_percent = 0

    if monthly_budget > 0:

        spending_percent = (
            monthly_spending /
            monthly_budget
        ) * 100


    # =====================================
    # INCOME USAGE
    # =====================================

    income_usage_percent = 0

    if monthly_income > 0:

        income_usage_percent = (
            monthly_spending /
            monthly_income
        ) * 100


    # =====================================
    # FINANCIAL HEALTH
    # =====================================

    if monthly_income <= 0:

        financial_health = "NO_INCOME"

    elif actual_surplus < 0:

        financial_health = "DEFICIT"

    elif (
        monthly_budget > 0
        and monthly_spending > monthly_budget
    ):

        financial_health = "OVER_BUDGET"

    elif income_usage_percent >= 90:

        financial_health = "VERY_TIGHT"

    elif (
        monthly_budget > 0
        and spending_percent >= 80
    ):

        financial_health = "BUDGET_TIGHT"

    else:

        financial_health = "HEALTHY"


    # =====================================
    # EMPTY QUESTION
    # =====================================

    if not question:

        return {

            "type": "info",

            "icon": "🤖",

            "title": "Ask FinPilot anything",

            "message": (
                "Try asking me something like "
                "'Can I afford ₹1500 headphones?', "
                "'How much can I spend today?', "
                "or 'How much am I saving?'"
            )

        }


    # =====================================
    # DETECT INTENT
    # =====================================

    intent = detect_financial_intent(
        question
    )


    # =====================================
    # AMOUNT DETECTION
    # =====================================

    amount_patterns = [

        r"₹\s*(\d+(?:,\d{3})*(?:\.\d+)?)",

        r"(\d+(?:,\d{3})*(?:\.\d+)?)\s*"
        r"(?:rs|inr|rupees|rupee)",

        r"(?:rs\.?|inr)\s*"
        r"(\d+(?:,\d{3})*(?:\.\d+)?)"

    ]


    amounts = []


    for pattern in amount_patterns:

        matches = re.findall(
            pattern,
            question_lower
        )

        for match in matches:

            try:

                if isinstance(
                    match,
                    tuple
                ):
                    match = match[0]

                amount = float(
                    str(match).replace(
                        ",",
                        ""
                    )
                )

                if amount > 0:
                    amounts.append(amount)

            except (
                ValueError,
                TypeError
            ):

                continue


    # =====================================
    # REMOVE DUPLICATES
    # =====================================

    amounts = list(
        dict.fromkeys(amounts)
    )


    # =====================================
    # COMPLEX QUESTION
    # =====================================

    complex_keywords = [

        "what if",
        "also",
        "both",
        "which one",
        "compare",
        "comparison",
        "instead",
        "together",
        "after buying",
        "after paying",
        "next month",
        "this month",
        "saving for",
        "can i afford",
        "worth it",
        "help me decide",
        "what do you recommend",
        "recommend",
        "if i buy",
        "if i spend",
        "should i"

    ]


    is_complex_question = any(

        keyword in question_lower

        for keyword in complex_keywords

    )


    multiple_amounts = (
        len(amounts) >= 2
    )


    # =====================================
    # GEMINI FOR COMPLEX QUESTIONS
    # =====================================

    if (
        is_complex_question
        or multiple_amounts
    ):

        gemini_response = clean_ai_response(
            ask_gemini_money_coach(

                question=contextual_question,

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

                goal=goal,

                chat_history=
                    chat_history

            )
        )


        return {

            "type": "ai",

            "icon": "🤖",

            "title":
                "FinPilot AI Recommendation",

            "message":
                gemini_response

        }


    # =====================================
    # PURCHASE CHECK
    # =====================================

    if (
        intent == "purchase"
        and amounts
    ):

        purchase_amount = sum(
            amounts
        )


        # =================================
        # NO BUDGET
        # =================================

        if monthly_budget <= 0:

            return {

                "type": "warning",

                "icon": "🎯",

                "title":
                    "Set your monthly budget first",

                "message": (

                    f"Recommendation: WAIT\n\n"

                    f"Why:\n"
                    f"You're considering a "
                    f"₹{purchase_amount:,.2f} expense, "
                    f"but your monthly budget is "
                    f"currently ₹0.\n\n"

                    f"Caution:\n"
                    f"Without a monthly budget, "
                    f"I can't reliably determine "
                    f"whether this purchase fits "
                    f"your spending plan.\n\n"

                    f"Next step:\n"
                    f"Set your monthly budget and "
                    f"ask me again."

                )

            }


        budget_after_purchase = (
            remaining_budget -
            purchase_amount
        )


        purchase_impact_percent = 0

        if remaining_budget > 0:

            purchase_impact_percent = (

                purchase_amount /
                remaining_budget

            ) * 100


        surplus_after_purchase = (
            actual_surplus -
            purchase_amount
        )


        # =================================
        # GOAL INFORMATION
        # =================================

        goal_remaining = 0
        goal_name = None

        if goal:

            goal_name = goal.name

            goal_remaining = max(

                goal.target_amount -
                goal.saved_amount,

                0

            )


        # =================================
        # NECESSARY EXPENSE
        # =================================

        necessary_keywords = [

            "gym",
            "membership",
            "fee",
            "fees",
            "college",
            "education",
            "medicine",
            "medical",
            "rent",
            "hostel",
            "food",
            "travel",
            "transport",
            "bill",
            "electricity",
            "internet",
            "recharge"

        ]


        is_necessary = any(

            keyword in question_lower

            for keyword in necessary_keywords

        )


        # =================================
        # DEFICIT
        # =================================

        if financial_health == "DEFICIT":

            return {

                "type": "danger",

                "icon": "🚨",

                "title":
                    "Your finances need attention",

                "message": (

                    f"Recommendation: WAIT\n\n"

                    f"Why:\n"
                    f"Your spending is already "
                    f"₹{abs(actual_surplus):,.2f} "
                    f"higher than your income.\n\n"

                    f"Income: "
                    f"₹{monthly_income:,.2f}\n\n"

                    f"Spending: "
                    f"₹{monthly_spending:,.2f}\n\n"

                    f"Caution:\n"
                    f"Adding another "
                    f"₹{purchase_amount:,.2f} "
                    f"expense would increase "
                    f"the pressure on your finances.\n\n"

                    f"Next step:\n"
                    f"Prioritize essential expenses "
                    f"and avoid non-essential "
                    f"purchases for now."

                )

            }


        # =================================
        # OVER BUDGET
        # =================================

        if (
            monthly_budget > 0
            and monthly_spending > monthly_budget
        ):

            return {

                "type": "danger",

                "icon": "🚨",

                "title":
                    "You're already over budget",

                "message": (

                    f"Recommendation: WAIT\n\n"

                    f"Why:\n"
                    f"You've spent "
                    f"₹{monthly_spending:,.2f} "
                    f"against your "
                    f"₹{monthly_budget:,.2f} "
                    f"monthly budget.\n\n"

                    f"You're already "
                    f"₹{monthly_spending - monthly_budget:,.2f} "
                    f"over budget.\n\n"

                    f"Caution:\n"
                    f"Another "
                    f"₹{purchase_amount:,.2f} "
                    f"purchase would increase "
                    f"your overspending.\n\n"

                    f"Next step:\n"
                    f"Pause non-essential spending "
                    f"and review your expenses."

                )

            }


        # =================================
        # ABOVE REMAINING BUDGET
        # =================================

        if purchase_amount > remaining_budget:

            over_amount = (
                purchase_amount -
                remaining_budget
            )

            return {

                "type": "danger",

                "icon": "🚨",

                "title":
                    "This purchase is over your budget",

                "message": (

                    f"Recommendation: WAIT\n\n"

                    f"Why:\n"
                    f"The purchase costs "
                    f"₹{purchase_amount:,.2f}, "
                    f"but only "
                    f"₹{remaining_budget:,.2f} "
                    f"remains in your budget.\n\n"

                    f"Budget impact:\n"
                    f"You would be "
                    f"₹{over_amount:,.2f} "
                    f"over your remaining budget.\n\n"

                    f"Caution:\n"
                    f"This could make it harder "
                    f"to cover your remaining "
                    f"planned expenses.\n\n"

                    f"Next step:\n"
                    f"Wait, reduce the purchase "
                    f"amount, or review your "
                    f"remaining expenses."

                )

            }


        # =================================
        # TIGHT CASH FLOW
        # =================================

        if (
            income_usage_percent >= 90
            and not is_necessary
        ):

            return {

                "type": "warning",

                "icon": "⚠️",

                "title":
                    "Your available money is getting tight",

                "message": (

                    f"Recommendation: WAIT\n\n"

                    f"Why:\n"
                    f"You've used about "
                    f"{income_usage_percent:.1f}% "
                    f"of your recorded income.\n\n"

                    f"After this purchase, "
                    f"your recorded surplus would be "
                    f"₹{surplus_after_purchase:,.2f}.\n\n"

                    f"Caution:\n"
                    f"Your overall cash flow is "
                    f"getting tight.\n\n"

                    f"Next step:\n"
                    f"Delay non-essential spending "
                    f"until your next income."

                )

            }


        # =================================
        # GOAL IMPACT
        # =================================

        if (
            goal
            and goal_remaining > 0
        ):

            goal_impact_percent = (

                purchase_amount /
                goal_remaining

            ) * 100


            if goal_impact_percent >= 50:

                goal_impact_text = (

                    f"Your '{goal_name}' goal needs "
                    f"₹{goal_remaining:,.2f} more. "
                    f"This purchase would equal about "
                    f"{goal_impact_percent:.1f}% "
                    f"of the amount still needed."

                )

                goal_next_step = (

                    f"Consider waiting and making "
                    f"more progress toward your "
                    f"'{goal_name}' goal."

                )

            else:

                goal_impact_text = (

                    f"Your '{goal_name}' goal needs "
                    f"₹{goal_remaining:,.2f} more. "
                    f"The purchase does not consume "
                    f"most of the remaining goal amount."

                )

                goal_next_step = (

                    f"Continue saving toward "
                    f"'{goal_name}' after the purchase."

                )

        else:

            goal_impact_text = (
                "You don't currently have an "
                "active savings goal affecting "
                "this purchase."
            )

            goal_next_step = (
                "Consider creating a savings "
                "goal for an important future expense."
            )


        # =================================
        # GOAL SIGNIFICANTLY AFFECTED
        # =================================

        if (
            goal
            and goal_remaining > 0
            and purchase_amount >= (
                goal_remaining * 0.5
            )
        ):

            return {

                "type": "warning",

                "icon": "🎯",

                "title":
                    "Affordable, but your goal may suffer",

                "message": (

                    f"Recommendation: "
                    f"YES, WITH CAUTION\n\n"

                    f"Why:\n"
                    f"₹{purchase_amount:,.2f} fits "
                    f"within your remaining budget "
                    f"of ₹{remaining_budget:,.2f}.\n\n"

                    f"Budget impact:\n"
                    f"You would have "
                    f"₹{budget_after_purchase:,.2f} "
                    f"remaining afterward.\n\n"

                    f"Caution:\n"
                    f"{goal_impact_text}\n\n"

                    f"Next step:\n"
                    f"{goal_next_step}"

                )

            }


        # =================================
        # LARGE PURCHASE
        # =================================

        if purchase_impact_percent > 50:

            return {

                "type": "warning",

                "icon": "⚠️",

                "title":
                    "Think twice before buying",

                "message": (

                    f"Recommendation: "
                    f"YES, WITH CAUTION\n\n"

                    f"Why:\n"
                    f"₹{purchase_amount:,.2f} fits "
                    f"your remaining budget, "
                    f"but it uses about "
                    f"{purchase_impact_percent:.1f}% "
                    f"of it.\n\n"

                    f"Remaining before purchase: "
                    f"₹{remaining_budget:,.2f}\n\n"

                    f"Remaining after purchase: "
                    f"₹{budget_after_purchase:,.2f}\n\n"

                    f"Caution:\n"
                    f"This would significantly "
                    f"reduce your available money "
                    f"for the rest of the month.\n\n"

                    f"Next step:\n"
                    f"Consider waiting or saving "
                    f"specifically for this purchase."

                )

            }


        # =================================
        # NECESSARY EXPENSE
        # =================================

        if is_necessary:

            return {

                "type": "success",

                "icon": "🟢",

                "title":
                    "This necessary payment looks affordable",

                "message": (

                    f"Recommendation: YES\n\n"

                    f"Why:\n"
                    f"The payment of "
                    f"₹{purchase_amount:,.2f} "
                    f"fits within your "
                    f"₹{remaining_budget:,.2f} "
                    f"remaining budget.\n\n"

                    f"After paying, you would have "
                    f"₹{budget_after_purchase:,.2f} "
                    f"remaining.\n\n"

                    f"Caution:\n"
                    f"Make sure you don't have "
                    f"other important expenses "
                    f"coming up.\n\n"

                    f"Goal impact:\n"
                    f"{goal_impact_text}\n\n"

                    f"Next step:\n"
                    f"Pay it if it is genuinely "
                    f"necessary and keep the "
                    f"remaining budget available."

                )

            }


        # =================================
        # SMALL PURCHASE
        # =================================

        if purchase_impact_percent <= 10:

            return {

                "type": "success",

                "icon": "🟢",

                "title":
                    "This purchase looks manageable",

                "message": (

                    f"Recommendation: YES\n\n"

                    f"Why:\n"
                    f"₹{purchase_amount:,.2f} fits "
                    f"comfortably within your "
                    f"₹{remaining_budget:,.2f} "
                    f"remaining budget.\n\n"

                    f"After purchase: "
                    f"₹{budget_after_purchase:,.2f}\n\n"

                    f"Budget impact: "
                    f"{purchase_impact_percent:.1f}%\n\n"

                    f"Caution:\n"
                    f"Small purchases can add up "
                    f"over the month.\n\n"

                    f"Next step:\n"
                    f"Make the purchase if it is "
                    f"actually useful and not "
                    f"an impulse purchase."

                )

            }


        # =================================
        # NORMAL PURCHASE
        # =================================

        return {

            "type": "info",

            "icon": "🤖",

            "title":
                "You can afford it, with some caution",

            "message": (

                f"Recommendation: "
                f"YES, WITH CAUTION\n\n"

                f"Why:\n"
                f"₹{purchase_amount:,.2f} fits "
                f"within your remaining budget "
                f"of ₹{remaining_budget:,.2f}.\n\n"

                f"After purchase: "
                f"₹{budget_after_purchase:,.2f}\n\n"

                f"Budget impact: "
                f"{purchase_impact_percent:.1f}%\n\n"

                f"Caution:\n"
                f"Your current recorded "
                f"income minus spending is "
                f"₹{actual_surplus:,.2f}.\n\n"

                f"Goal impact:\n"
                f"{goal_impact_text}\n\n"

                f"Next step:\n"
                f"Check your upcoming essential "
                f"expenses before buying."

            )

        }


    # =====================================
    # CATEGORY SPENDING
    # =====================================

    if intent == "category_spending":

        if not category_totals or monthly_spending <= 0:

            return {

                "type": "info",

                "icon": "📊",

                "title": "No spending category data yet",

                "message": (
                    "I don't have any recorded spending for "
                    "this month yet. Add some expenses and "
                    "I'll show you which categories are taking "
                    "the most of your money."
                )

            }


        sorted_categories = sorted(
            category_totals.items(),
            key=lambda item: item[1],
            reverse=True
        )

        top_category = sorted_categories[0][0]
        top_category_amount = sorted_categories[0][1]

        top_percentage = (
            category_percentages.get(
                top_category,
                (
                    top_category_amount /
                    monthly_spending
                ) * 100
            )
        )


        # Show the leading categories so the user gets
        # useful context instead of only one number.
        category_lines = []

        for category, amount in sorted_categories[:5]:

            percentage = category_percentages.get(
                category,
                (
                    amount /
                    monthly_spending
                ) * 100
            )

            category_lines.append(
                f"{category}: ₹{amount:,.2f} "
                f"({percentage:.1f}%)"
            )


        category_summary = "\n".join(
            category_lines
        )


        return {

            "type": "info",

            "icon": "📊",

            "title": (
                f"Top spending: {top_category}"
            ),

            "message": (
                f"Your highest spending category this "
                f"month is {top_category}, at "
                f"₹{top_category_amount:,.2f}. "
                f"That is about {top_percentage:.1f}% "
                f"of your recorded spending.\\n\\n"
                f"Your monthly spending is "
                f"₹{monthly_spending:,.2f}.\n\n"
                f"Top categories:\n"
                f"{category_summary}\n\n"
                f"💡 Review the highest category first if "
                f"you want to reduce spending and increase "
                f"your savings."
            )

        }


    # =====================================
    # DAILY SPENDING
    # =====================================

    if intent == "daily_spending":

        if financial_health == "DEFICIT":

            return {

                "type": "danger",

                "icon": "🚨",

                "title":
                    "Your daily spending needs attention",

                "message": (

                    f"Your spending is already "
                    f"₹{abs(actual_surplus):,.2f} "
                    f"above your recorded income.\n\n"

                    "Don't treat the daily limit "
                    "as extra money to spend. "
                    "Focus on essential expenses."

                )

            }


        return {

            "type": "success",

            "icon": "🛡️",

            "title":
                "Your safe daily spending",

            "message": (

                f"You can aim to spend around "
                f"₹{safe_daily_spending:,.2f} "
                f"today.\n\n"

                f"Your remaining monthly budget is "
                f"₹{remaining_budget:,.2f}."

            )

        }


    # =====================================
    # BUDGET
    # =====================================

    if intent == "budget":

        if monthly_budget <= 0:

            return {

                "type": "warning",

                "icon": "🎯",

                "title":
                    "Set your budget first",

                "message": (
                    "Set your monthly budget first "
                    "so I can calculate your "
                    "remaining spending room."
                )

            }


        if financial_health == "OVER_BUDGET":

            return {

                "type": "danger",

                "icon": "🚨",

                "title":
                    "You're over your monthly budget",

                "message": (

                    f"You've spent "
                    f"₹{monthly_spending:,.2f} "
                    f"against your "
                    f"₹{monthly_budget:,.2f} budget.\n\n"

                    f"You're "
                    f"₹{monthly_spending - monthly_budget:,.2f} "
                    f"over budget.\n\n"

                    "Consider reducing "
                    "non-essential spending."

                )

            }


        return {

            "type": "info",

            "icon": "🎯",

            "title":
                "Your budget status",

            "message": (

                f"You have "
                f"₹{remaining_budget:,.2f} "
                f"remaining from your "
                f"₹{monthly_budget:,.2f} "
                f"monthly budget.\n\n"

                f"You've used "
                f"{spending_percent:.1f}% "
                f"of it."

            )

        }


    # =====================================
    # SAVINGS
    # =====================================

    if intent == "savings":

        if actual_surplus > 0:

            return {

                "type": "success",

                "icon": "💰",

                "title":
                    "You're currently in surplus",

                "message": (

                    f"Income: "
                    f"₹{monthly_income:,.2f}\n\n"

                    f"Spending: "
                    f"₹{monthly_spending:,.2f}\n\n"

                    f"Current surplus: "
                    f"₹{actual_surplus:,.2f}\n\n"

                    "This is income minus recorded "
                    "spending. It doesn't necessarily "
                    "mean this money has already "
                    "been transferred to savings."

                )

            }


        if actual_surplus == 0:

            return {

                "type": "warning",

                "icon": "⚖️",

                "title":
                    "You're breaking even",

                "message": (

                    "Your recorded income and "
                    "spending are currently equal.\n\n"

                    "Try reducing non-essential "
                    "expenses to create room "
                    "for savings."

                )

            }


        return {

            "type": "danger",

            "icon": "🚨",

            "title":
                "Your spending is above income",

            "message": (

                f"Your spending is "
                f"₹{abs(actual_surplus):,.2f} "
                f"higher than your income.\n\n"

                "Consider reducing "
                "non-essential expenses."

            )

        }


    # =====================================
    # GOAL
    # =====================================

    if intent == "goal":

        if not goal:

            return {

                "type": "info",

                "icon": "🎯",

                "title":
                    "You don't have a goal yet",

                "message": (

                    "Create a savings goal and "
                    "I'll help you track whether "
                    "your spending supports it."

                )

            }


        goal_remaining = max(

            goal.target_amount -
            goal.saved_amount,

            0

        )


        return {

            "type": "info",

            "icon": "🏆",

            "title":
                goal.name,

            "message": (

                f"You need "
                f"₹{goal_remaining:,.2f} more "
                f"to reach your "
                f"₹{goal.target_amount:,.2f} goal.\n\n"

                f"Currently saved: "
                f"₹{goal.saved_amount:,.2f}"

            )

        }


    # =====================================
    # GENERAL → GEMINI
    # =====================================

    gemini_response = (
        ask_gemini_money_coach(

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

            goal=goal,

            chat_history=
                chat_history

        )
    )


    return {

        "type": "ai",

        "icon": "🤖",

        "title":
            "FinPilot AI",

        "message":
            gemini_response

    }


# =========================================
# PUBLIC FINPILOT MONEY COACH
# =========================================
#
# Thin wrapper around the coaching engine.
#
# The rule engine builds multi line answers
# using the literal two character sequence
# "\n" instead of a real line break.
#
# Older front end code only converted those
# sequences back in one place, so the coach
# page and the dashboard chat displayed the
# raw "\n" text.
#
# Normalising here means every consumer gets
# real newlines:
#
#   templates/coach/coach.html      (server side)
#   templates/components/...        (server side)
#   templates/dashboard/...html     (textContent)
#   static/js/script.js             (formatAIText)
#
# It also means the text stored in the
# chat_messages table is clean.
# =========================================

def money_coach_response(
    question,
    monthly_income,
    monthly_spending,
    monthly_budget,
    monthly_savings,
    safe_daily_spending,
    goal=None,
    category_totals=None,
    category_percentages=None,
    top_category=None,
    top_category_amount=0,
    chat_history=None
):

    response = _money_coach_response_engine(

        question=question,

        monthly_income=monthly_income,

        monthly_spending=monthly_spending,

        monthly_budget=monthly_budget,

        monthly_savings=monthly_savings,

        safe_daily_spending=safe_daily_spending,

        goal=goal,

        category_totals=category_totals,

        category_percentages=category_percentages,

        top_category=top_category,

        top_category_amount=top_category_amount,

        chat_history=chat_history

    )


    if isinstance(response, dict) and "message" in response:

        response["message"] = clean_ai_response(
            response["message"]
        )


    return response