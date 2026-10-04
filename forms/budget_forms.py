from flask_wtf import FlaskForm

from wtforms import FloatField, SubmitField

from wtforms.validators import (
    DataRequired,
    NumberRange
)


class BudgetForm(FlaskForm):

    monthly_budget = FloatField(
        "Monthly Budget",
        validators=[
            DataRequired(),
            NumberRange(
                min=1,
                message="Budget must be greater than ₹0."
            )
        ]
    )

    submit = SubmitField(
        "Save Budget"
    )