from flask import Flask, request, url_for, redirect, render_template




app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


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

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        # do stuff when the form is submitted

        # redirect to end the POST handling
        # the redirect can be to the same route or somewhere else
        return redirect(url_for('index'))

    # show the form, it wasn't submitted
    return render_template('signup.html')
