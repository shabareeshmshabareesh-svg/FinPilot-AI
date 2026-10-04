from flask_wtf import FlaskForm

from wtforms import (
    FloatField,
    StringField,
    DateField,
    SubmitField
)

from wtforms.validators import (
    DataRequired,
    NumberRange,
    Optional
)


class GoalForm(FlaskForm):

    # =========================================
    # GOAL NAME
    # =========================================

    name = StringField(
        "Goal Name",
        validators=[
            DataRequired(
                message="Please enter a goal name."
            )
        ]
    )


    # =========================================
    # TARGET AMOUNT
    # =========================================

    target_amount = FloatField(
        "Target Amount",
        validators=[
            DataRequired(
                message="Please enter your target amount."
            ),
            NumberRange(
                min=0.01,
                message="Target amount must be greater than ₹0."
            )
        ]
    )


    # =========================================
    # SAVED AMOUNT
    # =========================================

    saved_amount = FloatField(
        "Amount Already Saved",
        default=0,

        validators=[
            NumberRange(
                min=0,
                message="Saved amount cannot be negative."
            )
        ]
    )


    # =========================================
    # TARGET DATE
    # =========================================

    target_date = DateField(
        "Target Date",

        validators=[
            Optional()
        ]
    )


    # =========================================
    # DESCRIPTION
    # =========================================

    description = StringField(
        "Description",
        validators=[
            Optional()
        ]
    )


    # =========================================
    # SUBMIT
    # =========================================

    submit = SubmitField(
        "Create Goal"
    )