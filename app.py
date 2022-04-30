from flask import Flask, request, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
import hashlib
import re

# set up flask
app = Flask(__name__)


### Database setting###

# set up database
app.config ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# I don't know about pool_recycle, so I comment and keep below.
# app.config['SQLALCHEMY_POOL_RECYCLE'] = 280


db = SQLAlchemy(app)

# For the table of Accounts
class Accounts(db.Model):
    __tablename__ = 'accounts'
    accountName = db.Column(db.String(128), unique = True, nullable=False, primary_key = True) # 1 ~ 127 characters long.
    password = db.Column(db.String, nullable=False ) #To be HASHED  # string max char: 255; text max char: 30,000
    # Remember check for the input requirement of "balance"
    balance = db.Column(db.Float)

# ref: https://www.geeksforgeeks.org/md5-hash-python/
    def __init__(self, acc, pas, bal = 777):
        self.accountName = acc
        self.password = hashlib.md5(pas.encode()).hexdigest()
        self.balance = bal

db.create_all()

### Add new record ###
### account = Accounts( parameter )
### db.session.add(account)
### db.session.commit()

### Query ###
### newAcc = Accounts.query.filter_by(accountName = acc).first()


### web page - Index ###
@app.route('/')
def index():
    return render_template('index.html')

# ref: https://stackoverflow.com/questions/12277933/send-data-from-a-textbox-into-flask?fbclid=IwAR17xLZWQ35XNoxEOZOKwy6g6o5wcOElOQECkTv3o2sG5A-4D0OsKUMUOww
@app.route('/', methods=['POST'])
def index_post():
    return redirect(url_for('balance'))


### web page - Balance ###
#ref: https://stackoverflow.com/questions/27539309/how-do-i-create-a-link-to-another-html-page
@app.route('/balance', methods=['GET', 'POST'])
def balance():
    if request.method == 'POST':
        # do stuff when the form is submitted

        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        return redirect(url_for('index'))

    # show the form, it wasn't submitted
    return render_template('balance.html')

### web page - Signup ###
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    message1 = "Account name and password only contain:"
    message2 = "lowercase letters, digits"
    message3 = "under-scores, hyphens and dots"
    if request.method == 'POST':
        acc = request.form['accountName_signup']
        pas = request.form['password_signup']
        pattern = re.compile("^[_\\-\\.a-z0-9]*$") # should match /[_\\-\\.0-9a-z]/
        if (len(acc) > 0) & (len(pas) > 0 ) :
            if bool(re.match(pattern, acc)) & bool(re.match(pattern, pas)) :
                # ref: https://flask-sqlalchemy.palletsprojects.com/en/2.x/queries/
                existingAcc = Accounts.query.get(acc)
                if existingAcc is None:
                    account = Accounts(acc, pas)
                    db.session.add(account)
                    db.session.commit()
                    newAcc = Accounts.query.filter_by(accountName = acc).first()
                    if newAcc is None:
                        message1 = "Fail"
                        message2 = "Please sign up again"
                        message3 = ""
                    else:
                        message1 = "Sign up Successfully"
                        message2 = ""
                        message3 = ""
                else:
                    message1 = "Fail"
                    message2 = "Account name has existed"
                    message3 = "Please sign up for another one"
            else:
                message1 = "Fail"
                message2 = "Account name and password only contain:"
                message3 = "a-z0-9._-"
        else:
            message1 = "Fail"
            message2 = "The length of account name and password"
            message3 = "should between 1 to 127"
    return render_template('signup.html', message1 = message1, message2 = message2, message3 = message3)
