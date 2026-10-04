from models.database import db


class Income(db.Model):

    __tablename__ = "income"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    amount = db.Column(
        db.Float,
        nullable=False
    )

    source = db.Column(
        db.String(50),
        nullable=False
    )

    description = db.Column(
        db.String(255),
        nullable=True
    )

    date = db.Column(
        db.Date,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    def __repr__(self):

        return f"<Income ₹{self.amount} - {self.source}>"