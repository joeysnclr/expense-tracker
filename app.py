from flask import Flask, render_template, flash, redirect, url_for, session, request, logging, g, jsonify
import json, os, api, datetime

app = Flask(__name__)
app.secret_key = os.urandom(32)
port = int(os.environ.get('PORT', 5000))

API_NOT_LOGGED_IN = {"error": "User not logged in."}

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
	return render_template('dashboard.html')

@app.route('/transactions')
def transactions():
	if not session.get('loggedIn', False):
		return redirect(url_for('login'))
	return render_template('transactions.html')

@app.route('/breakdown')
def breakdown():
	if not session.get('loggedIn', False):
		return redirect(url_for('login'))
	return render_template('breakdown.html')

# API routes

@app.route('/api/balance', methods=['GET'])
def apiBalance():
	if not session.get('loggedIn', False):
		return jsonify(API_NOT_LOGGED_IN)
	content = g.user.getBalance()
	return jsonify(content)

@app.route('/api/recenttransactions', methods=['GET'])
def apiRecentTransactions():
	if not session.get('loggedIn', False):
		return jsonify(API_NOT_LOGGED_IN)
	content = g.user.getTransactionsSortedByDate()
	return jsonify(content)

@app.route('/api/breakdowns', methods=['GET'])
def apiBreakdowns():
	if not session.get('loggedIn', False):
		return jsonify(API_NOT_LOGGED_IN)
	content = g.user.getMonthlyBreakdowns()
	return jsonify(content)

@app.route('/api/addtransaction', methods=['POST'])
def apiAddTransaction():
	if not session.get('loggedIn', False):
		return jsonify(API_NOT_LOGGED_IN)
	amount = request.form.get("amount")
	date = request.form.get("date")
	tType = request.form.get("tType")
	category = request.form.get("category")
	name = request.form.get("name")
	g.user.addTransaction(amount, date, tType, category, name)
	content = g.user.getTransactionsSortedByDate()
	return jsonify(content)

@app.route('/api/edittransaction', methods=['POST'])
def apiEditTransaction():
	if not session.get('loggedIn', False):
		return jsonify(API_NOT_LOGGED_IN)
	amount = request.form.get("amount")
	date = request.form.get("date")
	tType = request.form.get("tType")
	category = request.form.get("category")
	name = request.form.get("name")
	g.user.addTransaction(amount, date, tType, category, name)
	content = g.user.getTransactionsSortedByDate()
	return jsonify(content)

@app.route('/api/deletetransaction', methods=['POST'])
def apiDeleteTransaction():
	if not session.get('loggedIn', False):
		return jsonify(API_NOT_LOGGED_IN)
	amount = request.form.get("amount")
	date = request.form.get("date")
	tType = request.form.get("tType")
	category = request.form.get("category")
	name = request.form.get("name")
	g.user.addTransaction(amount, date, tType, category, name)
	content = g.user.getTransactionsSortedByDate()
	return jsonify(content)

app.run(host='0.0.0.0', port=port, debug=True)