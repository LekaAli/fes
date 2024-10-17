from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, NumberRange


class TransactionForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    type = SelectField('Type', choices=[('credit', 'Credit'), ('debit', 'Debit')], validators=[DataRequired()])
    amount = StringField('Amount', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    submit = SubmitField('Create')


class EditTransactionForm(TransactionForm):
    id = StringField('ID', validators=[DataRequired()])
    submit = SubmitField('Save')


class RetrieveTransactionForm(FlaskForm):
    transaction_id = StringField('Transaction ID', validators=[DataRequired()])
    submit = SubmitField('Search')


class DeleteTransactionForm(RetrieveTransactionForm):
    submit = SubmitField('Delete')

