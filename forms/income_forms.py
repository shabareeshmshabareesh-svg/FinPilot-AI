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
    NumberRange
)


class IncomeForm(FlaskForm):

    amount = FloatField(
        "Amount",
        validators=[
            DataRequired(),
            NumberRange(
                min=0.01,
                message="Amount must be greater than 0."
            )
        ]
    )

    source = SelectField(
        "Income Source",
        choices=[
            ("Pocket Money", "Pocket Money"),
            ("Scholarship", "Scholarship"),
            ("Salary", "Salary"),
            ("Freelancing", "Freelancing"),
            ("Other", "Other")
        ],
        validators=[
            DataRequired()
        ]
    )

    description = StringField(
        "Description"
    )

    date = DateField(
        "Date",
        validators=[
            DataRequired()
        ]
    )

    submit = SubmitField(
        "Add Income"
    )