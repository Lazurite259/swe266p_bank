from datetime import datetime
from flask import Flask, request, url_for, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
import hashlib
import re


# set up flask
app = Flask(__name__)


### Database setting###

# set up database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bank.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# add key
app.secret_key = 'super secret key'

db = SQLAlchemy(app)

# For the table of Accounts


class Account(db.Model):
    __tablename__ = 'accounts'
    # 1 ~ 127 characters long.
    account_id = db.Column(db.String(128), unique=True,
                           nullable=False, primary_key=True)
    password = db.Column(db.String, nullable=False)
    balance = db.Column(db.Float)

# ref: https://www.geeksforgeeks.org/md5-hash-python/
    def __init__(self, acc, pas, bal=0.00):
        self.account_id = acc
        self.password = hashlib.md5(pas.encode()).hexdigest()
        self.balance = bal

    def withdraw(self, amount):
        if self.balance - amount < 0.00:
            return False
        else:
            self.balance -= amount
            return True

    def deposit(self, amount):
        if self.balance + amount > 4294967295.99:
            return False
        else:
            self.balance += amount
            return True

# For the table of Transactions


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    transaction_type = db.Column(db.Text)
    amount = db.Column(db.Float)
    account_id = db.Column(db.Integer, db.ForeignKey(
        'accounts'), nullable=False)
    account = db.relationship(
        'Account', backref=db.backref('transactions', lazy=True))

    def __init__(self, transaction_type, account_id, amount=0):
        self.transaction_type = transaction_type
        self.account_id = account_id
        self.amount = amount


db.create_all()


### web page - Index ###
@app.route('/')
def index():
    return render_template('index.html')

# ref: https://stackoverflow.com/questions/12277933/send-data-from-a-textbox-into-flask?fbclid=IwAR17xLZWQ35XNoxEOZOKwy6g6o5wcOElOQECkTv3o2sG5A-4D0OsKUMUOww
# ref: https://flask.palletsprojects.com/en/2.1.x/patterns/flashing/


@app.route('/', methods=['POST'])
def index_post():
    if request.method == 'POST':
        acc = request.form.get("account")
        password = request.form.get("password")

        sqlcommand_account = "SELECT * FROM accounts where account_id = '" + acc + "'"
        record_account = db.session.execute(sqlcommand_account)
        account_name = (record_account.first())
        if account_name:
            sqlcommand_password = "SELECT * FROM accounts where account_id = '" + acc + \
                "' and password = '" + \
                hashlib.md5(password.encode()).hexdigest() + "'"
            record = db.session.execute(sqlcommand_password)
            account = (record.first())
            if account:
                session['account'] = acc
                session['balance'] = '%.2f' % account.balance if account else 0
                return redirect(url_for('myaccount'))
            else:
                flash("Incorrect account name or password!")
    #             flash("Incorrect account name or password!")
        else:
            flash("Incorrect account name or password!")
    return redirect(url_for('index'))


### web page - MyAccount ###
# ref: https://stackoverflow.com/questions/27539309/how-do-i-create-a-link-to-another-html-page

@app.route('/myaccount', methods=['GET', 'POST'])
def myaccount():
    if request.method == 'GET':
        acc = session['account']
        transactions = Transaction.query.filter_by(
            account_id=acc).order_by(Transaction.date.desc())

    if request.method == 'POST':
        # ref: https://stackoverflow.com/questions/43811779/use-many-submit-buttons-in-the-same-form

        acc = session['account']
        account = Account.query.filter_by(account_id=acc).first()
        # should match /(0|[1-9][0-9]*)/
        pattern = re.compile("^(0|[1-9][0-9]*)")
        action = request.form['action']
        # withdraw
        if action == "Withdraw":
            amount = request.form['withdraw']
#             decimal number is always two digits
            if amount[::-1].find('.') > 2:
                flash("Invalid amount")
                return redirect(url_for('myaccount'))
            if re.match(pattern, amount):
                # withdraw through db
                if account.withdraw(float(amount)):
                    # add new transaction history
                    new_transaction = Transaction(action, acc, float(amount))
                    db.session.add(new_transaction)
                    # update db
                    db.session.commit()
                else:
                    flash("Withdraw failed")
            else:
                flash("Invalid amount")
        # deposit
        elif action == "Deposit":
            amount = request.form['deposit']
            # decimal number is always two digits
            if amount[::-1].find('.') > 2:
                flash("Invalid amount")
                return redirect(url_for('myaccount'))
            if re.match(pattern, amount):
                # deposit through db
                if account.deposit(float(amount)):
                    # add new transaction history
                    new_transaction = Transaction(action, acc, float(amount))
                    db.session.add(new_transaction)
                    # update db
                    db.session.commit()
                else:
                    flash("Deposit failed")
            else:
                flash("Invalid amount")
        # update balance
        session['balance'] = '%.2f' % account.balance
        return redirect(url_for('myaccount'))

    return render_template('myaccount.html', transactions=transactions)


### web page - Signup ###
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    message1 = "Account name and password only contain:"
    message2 = "lowercase letters, digits, "
    message3 = "under-scores, hyphens and dots"
    if request.method == 'POST':
        acc = request.form['account_signup']
        pas = request.form['password_signup']
        # should match /[_\\-\\.0-9a-z]/
        pattern = re.compile("^[_\\-\\.a-z0-9]*$")
        if (len(acc) > 0) & (len(pas) > 0) & (len(acc) < 128) & (len(pas) < 128) :
            if bool(re.match(pattern, acc)) & bool(re.match(pattern, pas)):
                # ref: https://flask-sqlalchemy.palletsprojects.com/en/2.x/queries/
                existingAcc = Account.query.get(acc)
                if existingAcc is None:
                    account = Account(acc, pas)
                    db.session.add(account)
                    db.session.commit()
                    newAcc = Account.query.filter_by(account_id=acc).first()
                    if newAcc is None:
                        message1 = "Fail"
                        message2 = "Please sign up again"
                        message3 = ""
                    else:
                        message1 = "Sign up successfully"
                        message2 = ""
                        message3 = ""
                else:
                    message1 = "Fail"
                    message2 = "Account name has existed"
                    message3 = "Please sign up for another one"
            else:
                message1 = "Fail"
                message2 = "Account name and password only contains:"
                message3 = "a-z0-9._-"
        else:
            message1 = "Fail"
            message2 = "The length of account name and password"
            message3 = "should between 1 to 127"
    return render_template('signup.html', message1=message1, message2=message2, message3=message3)


### Logout ###
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
