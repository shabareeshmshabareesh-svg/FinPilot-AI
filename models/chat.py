from datetime import datetime

from models.database import db


class ChatMessage(db.Model):

    __tablename__ = "chat_messages"


    # =========================================
    # PRIMARY KEY
    # =========================================

    id = db.Column(
        db.Integer,
        primary_key=True
    )


    # =========================================
    # USER
    # =========================================

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )


    # =========================================
    # USER QUESTION
    # =========================================

    question = db.Column(
        db.Text,
        nullable=False
    )


    # =========================================
    # AI RESPONSE
    # =========================================

    response = db.Column(
        db.Text,
        nullable=False
    )


    # =========================================
    # AI FEEDBACK
    # =========================================
    #
    # None          = No feedback
    # helpful       = 👍
    # not_helpful   = 👎
    #

    feedback = db.Column(
        db.String(20),
        nullable=True,
        default=None
    )


    # =========================================
    # FEEDBACK TIME
    # =========================================

    feedback_at = db.Column(
        db.DateTime,
        nullable=True,
        default=None
    )


    # =========================================
    # CREATED TIME
    # =========================================

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )


    # =========================================
    # REPRESENTATION
    # =========================================

    def __repr__(self):

        return (
            f"<ChatMessage {self.id}>"
        )