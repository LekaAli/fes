# app.py

from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from sqlalchemy import func
from sqlalchemy.orm import Session
from forms.login_form import LoginForm
from forms.register_form import RegisterForm
from forms.transaction_form import TransactionForm, RetrieveTransactionForm, EditTransactionForm
from models.users import init_models, User, db
from models.transactions import Transaction
from utils.db_utils import perform_db_operation

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
init_models(app)


@login_manager.user_loader
def load_user(user_id):
    with Session(db.engine) as session:
        return session.get(User, int(user_id))


@app.route('/')
@login_required
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    transaction_id = int(request.args.get("transaction_id", "0"))
    operation_type = int(request.args.get("operation_type", "0"))
    transactions = []
    total_amount = 0

    if transaction_id and operation_type == 1:
        transaction_id = request.args.get("transaction_id")
        transactions = Transaction.query.filter_by(id=transaction_id)
        total_amount = transactions.first().amount if transactions.first() else 0
    elif transaction_id and operation_type == 2:
        transaction_id = request.args.get("transaction_id")
        return redirect(url_for("edit_transaction", transaction_id=transaction_id))
    elif transaction_id and operation_type == 3:
        transaction_id = request.args.get("transaction_id")
        transactions = Transaction.query.filter_by(id=transaction_id)
        perform_db_operation(model_cls_name=transactions.first(), operation="delete")
        print("DEL")

    if operation_type != 1:
        transactions = Transaction.query.all()
        total_amount = db.session.query(func.sum(Transaction.amount)).scalar() or 0
    return render_template(
        'index.html',
        title='Dashboard',
        username=current_user.username,
        transactions=transactions,
        account_balance=total_amount
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=True)  # Add remember=True parameter
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        data = {
            "username": form.username.data,
            "email": form.email.data,
            "password": form.password.data
        }
        perform_db_operation(User, data)
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)


@app.route('/transactions', methods=['GET', 'POST'])
def create_transaction():
    if not current_user.is_authenticated:
        flash('You must be logged in to create transactions.', 'success')
        return redirect(url_for('login'))
    form = TransactionForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            data = {
                "amount": form.amount.data,
                "date": form.date.data,
                "type": form.type.data,
                "description": form.description.data
            }
            perform_db_operation(Transaction, data)
            flash('Transaction was created successfully!', 'success')
            return redirect(url_for('index'))
    return render_template('create_transaction.html', form=form)


@app.route('/transactions/retrieve/', methods=['GET', 'POST'])
def retrieve_transaction():
    if not current_user.is_authenticated:
        flash('You must be logged in to create transactions.', 'success')
        return redirect(url_for('login'))
    form = RetrieveTransactionForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            flash('Transaction was retrieved successfully!', 'success')
            return redirect(
                url_for(
                    'index',
                    transaction_id=form.transaction_id.data,
                    operation_type=request.args.get("operation_type")
                )
            )
        else:
            flash(f"Error: {form.errors}", "success")
    return render_template('retrieve_transaction.html', form=form)


@app.route('/transactions/<string:transaction_id>', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    if not current_user.is_authenticated:
        flash('You must be logged in to edit transactions.', 'success')
        return redirect(url_for('login'))
    form = EditTransactionForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            flash('Transaction was updated successfully!', 'success')
            data = {
                "amount": form.amount.data,
                "date": form.date.data,
                "type": form.type.data,
                "description": form.description.data
            }
            transaction = Transaction.query.filter_by(id=transaction_id).first()
            perform_db_operation(model_cls_name=transaction, data=data, operation="update")
            return redirect(url_for('index'))
        else:
            flash(f"Error: {form.errors}", "success")
    transaction = Transaction.query.filter_by(id=transaction_id)
    form = EditTransactionForm(obj=transaction.first())
    return render_template('edit_transaction.html', form=form, transaction_id=transaction_id)


@app.route('/transactions/<string:transaction_id>', methods=['GET', 'POST'])
def delete_transaction(transaction_id):
    if not current_user.is_authenticated:
        flash('You must be logged in to delete transactions.', 'success')
        return redirect(url_for('login'))
    form = EditTransactionForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            flash('Transaction was deleted successfully!', 'success')
            transaction = Transaction.query.get(id=transaction_id)
            perform_db_operation(model_cls_name=transaction, operation="update")
            return redirect(url_for('index'))
        else:
            flash(f"Error: {form.errors}", "success")
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
