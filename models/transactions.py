import enum
from models.users import db


class Type(enum.Enum):
    credit = "Credit"
    debit = "Debit"


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.String(80), unique=True, nullable=False)
    date = db.Column(db.DateTime, server_default=db.func.now())
    type = db.Column(db.Enum(Type), nullable=False)
    description = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f"<Transaction {self.id}>"
