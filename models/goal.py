from models.database import db


class Goal(db.Model):

    __tablename__ = "goals"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    target_amount = db.Column(
        db.Float,
        nullable=False
    )

    saved_amount = db.Column(
        db.Float,
        default=0,
        nullable=False
    )

    target_date = db.Column(
        db.Date,
        nullable=True
    )

    description = db.Column(
        db.String(255),
        nullable=True
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

        return f"<Goal {self.name}>"