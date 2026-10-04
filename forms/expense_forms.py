from flask_wtf import FlaskForm

from wtforms import (
    FloatField,
    SelectField,
    StringField,
    DateField,
    SubmitField
)

from wtforms.validators import (
    DataRequired,
    NumberRange,
    Optional,
    Length
)


# =========================================================
# FINPILOT EXPENSE CATEGORIES
# =========================================================
#
# Single source of truth.
#
# Both the expense form and the expense list
# filters read from here, so the filter options
# can never drift away from the categories that
# can actually be saved.
# =========================================================

EXPENSE_CATEGORIES = [
    ("Food", "🍔 Food"),
    ("Travel", "🚌 Travel"),
    ("Shopping", "🛍️ Shopping"),
    ("Education", "📚 Education"),
    ("Gym", "🏋️ Gym"),
    ("Health", "💊 Health"),
    ("Entertainment", "🎮 Entertainment"),
    ("Bills", "📱 Bills"),
    ("Other", "📦 Other")
]


# =========================================================
# FINPILOT PAYMENT METHODS
# =========================================================

EXPENSE_PAYMENT_METHODS = [
    ("UPI", "📱 UPI"),
    ("Cash", "💵 Cash"),
    ("Debit Card", "💳 Debit Card"),
    ("Credit Card", "💳 Credit Card"),
    ("Bank Transfer", "🏦 Bank Transfer")
]


class ExpenseForm(FlaskForm):

    amount = FloatField(
        "Amount",
        validators=[
            DataRequired(),
            NumberRange(min=0.01)
        ]
    )

    category = SelectField(
        "Category",
        choices=EXPENSE_CATEGORIES,
        validators=[DataRequired()]
    )

    description = StringField(
        "Description",
        validators=[
            Optional(),
            Length(max=255)
        ]
    )

    payment_method = SelectField(
        "Payment Method",
        choices=EXPENSE_PAYMENT_METHODS,
        validators=[DataRequired()]
    )

    date = DateField(
        "Date",
        validators=[DataRequired()]
    )

    submit = SubmitField("Add Expense")