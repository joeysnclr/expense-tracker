from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, g, jsonify
import json
import os
import api
import datetime

app = Flask(__name__)
app.secret_key = os.urandom(32)
port = int(os.environ.get('PORT', 5000))

API_NOT_LOGGED_IN = {
    "success": False,
    "error": "User not logged in."
}
API_PARAMETER_NOT_FOUND = {
    "success": False,
    "error": "Parameter not found."
}


@app.before_request
def before_request():
    g.userManagement = api.UserManagement()
    userEmail = session.get('email', None)
    userLoggedIn = session.get('loggedIn', False)
    if userLoggedIn:
        g.user = api.User(userEmail)
    else:
        g.user = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('loggedIn', False):
        return redirect(url_for('dashboard'))
    errorMessage = None
    if request.method == 'POST':
        emailField = request.form.get("email")
        passwordField = request.form.get("password")
        if g.userManagement.validLoginCredentials(emailField, passwordField):
            # log user in w/ session
            session['email'] = emailField
            session['loggedIn'] = True
            return redirect(url_for('dashboard'))
        errorMessage = "Invalid Login Credentials"
    return render_template('login.html', errorMessage=errorMessage)


@app.route('/logout')
def logout():
    session['email'] = None
    session['loggedIn'] = False
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if session.get('loggedIn', False):
        return redirect(url_for('dashboard'))
    errorMessage = None
    if request.method == 'POST':
        emailField = request.form.get("email")
        passwordField = request.form.get("password")
        if g.userManagement.validSignUpCredentials(emailField):
            # add account to database
            g.userManagement.addUser(emailField, passwordField)
            # log user in w/ session
            session['email'] = emailField
            session['loggedIn'] = True
            return redirect(url_for('dashboard'))
        errorMessage = "Account With This Email Already Exists"
    return render_template('signup.html', errorMessage=errorMessage)

# logged in routes


@app.route('/dashboard')
def dashboard():
    if not session.get('loggedIn', False):
        return redirect(url_for('login'))
    content = {
        "balance": g.user.getBalance(),
        "transactions": g.user.getTransactionsSortedByDate()
    }
    return render_template('dashboard.html', content=content)


@app.route('/transactions')
def transactions():
    if not session.get('loggedIn', False):
        return redirect(url_for('login'))
    content = {
        "transactions": g.user.getTransactionsSortedByDate(),
        "categories": g.user.getCategories()
    }
    return render_template('transactions.html', content=content)


@app.route('/breakdown')
def breakdown():
    if not session.get('loggedIn', False):
        return redirect(url_for('login'))
    return render_template('breakdown.html')

# logged in actions


@app.route('/addtransaction', methods=['POST'])
def addTransaction():
    if not session.get('loggedIn', False):
        return redirect(url_for('login'))

    amount = float(request.form.get("amount"))
    dateInput = request.form.get("date")
    tType = request.form.get("tType")
    category = request.form.get("category")
    name = request.form.get("name")

    # convert date to datetime object
    year = int(dateInput.split("/")[2])
    month = int(dateInput.split("/")[0])
    day = int(dateInput.split("/")[1])
    date = datetime.datetime(year, month, day)

    g.user.addTransaction(amount, date, tType, category, name)
    return redirect(url_for("transactions"))


@app.route('/deletetransaction/<string:tId>')
def deleteTransaction(tId):
    if not session.get('loggedIn', False):
        return redirect(url_for('login'))
    g.user.deleteTransaction(tId)
    return redirect(url_for('transactions'))


@app.route('/edittransaction', methods=['POST'])
def editTransaction():
    if not session.get('loggedIn', False):
        return redirect(url_for('login'))

    tId = request.form.get('tId')
    amount = float(request.form.get("amount"))
    dateInput = request.form.get("date")
    tType = request.form.get("tType")
    category = request.form.get("category")
    name = request.form.get("name")

    # convert date to datetime object
    year = int(dateInput.split("/")[2])
    month = int(dateInput.split("/")[0])
    day = int(dateInput.split("/")[1])
    date = datetime.datetime(year, month, day)

    g.user.editTransaction(tId, amount, date, tType, category, name)
    return redirect(url_for("transactions"))

# API routes for data that needs to be loaded with Javascript


# TESTED, WORKING
@app.route('/api/balance_data')
def apiBalanceData():
    if not session.get('loggedIn', False):
        return jsonify(API_NOT_LOGGED_IN)
    balanceData = g.user.getBalanceData()
    response = {
        "success": True,
        "data": balanceData
    }
    return jsonify(response)

# NOT TESTED!


@app.route('/api/breakdown_data/<string:monthId>')
def apiBreakdownData(monthId):
    if not session.get('loggedIn', False):
        return jsonify(API_NOT_LOGGED_IN)
    breakdowns = g.user.getMonthlyBreakdowns()
    if monthId in breakdowns:
        response = {
            "success": True,
            "data": breakdowns[monthId]
        }
        return jsonify(response)
    else:
        return jsonify(API_PARAMETER_NOT_FOUND)


app.run(host='0.0.0.0', port=port, debug=True)
