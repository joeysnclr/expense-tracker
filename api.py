import database
import os
import hashlib
import random
import string
import datetime


class UserManagement():

	def hashString(self, string):
		# https://nitratine.net/blog/post/how-to-hash-passwords-in-python/ password hashing
		salt = os.urandom(32)
		key = hashlib.pbkdf2_hmac('sha256', string.encode('utf-8'), salt, 50000)
		return salt + key

	def compareStringToHash(self, string, hashedString):
		salt = hashedString[:32] # Get the salt you stored for *this* user
		key = hashedString[32:] # Get this users key calculated
		# Use the exact same setup you used to generate the key, but this time put in the password to check
		new_hash = hashlib.pbkdf2_hmac('sha256', string.encode('utf-8'), salt, 50000)
		return new_hash == key

	def validSignUpCredentials(self, email):
		query = {"email": email}
		result = database.dbusers.find_one(query)
		return result == None

	def addUser(self, email, password):
		userObject = database.getUserSchema()
		userObject['email'] = email
		userObject['password'] = self.hashString(password)
		database.dbusers.insert_one(userObject)

	def validLoginCredentials(self, email, password):
		query = {"email": email}
		potentialUser = database.dbusers.find_one(query)
		if potentialUser: # email exists
			if self.compareStringToHash(password, potentialUser['password']): # password is correct
				return True
		return False

class User():

	def __init__(self, email):
		self.email = email
		self.query = {"email": self.email}

	def getUserInfo(self):
		
		return database.dbusers.find_one(self.query)

	def getBalance(self):
		balance = 0
		user = self.getUserInfo()
		transactions = user['transactions']
		for t in transactions:
			if t['tType'] == "income":
				balance += t['amount']
			else:
				balance -= t['amount']
		return {"balance": balance}

	def addTransaction(self, amount, date, tType, category, name):
		transactionObject = database.getTransactionSchema()
		transactionObject['amount'] = amount
		transactionObject['date'] = date
		transactionObject['tType'] = tType
		transactionObject['category'] = category
		transactionObject['name'] = name

		push = {"$push": {"transactions": transactionObject}}
		database.dbusers.update(self.query, push)

	def editTransaction(self, tId, amount, date, tType, category, name):
		queryExt = {"email": self.email, "transactions.tId": tId}
		updates = { "$set": {
				"transactions.$.amount": amount,
				"transactions.$.date": date,
				"transactions.$.tType": tType,
				"transactions.$.category": category,
				"transactions.$.name": name
			}
		}
		database.dbusers.update(queryExt, updates);

	def deleteTransaction(self, tId):
		pull = {
			"$pull": {
				"transactions": {"tId": tId}
			}
		}
		database.dbusers.update(self.query, pull)
	
	def getTransactionsSortedByDate(self):
		transactions = self.getUserInfo()['transactions']
		return sorted(transactions, key = lambda i: i['date'], reverse=True)

	def getMonthlyBreakdowns(self):
		transactions = self.getTransactionsSortedByDate()
		months = {}
		for t in transactions:
			m = str(t['date'].strftime("%B")) + " " + str(t['date'].year)
			if m not in months:
				months[m] = {
					"spent": {
						"total": 0,
						"categories": [],
						"categoryTotals": []
					},
					"income": {
						"total": 0,
						"categories": [],
						"categoryTotals": []
					}
				}
			if t['category'] not in months[m][t['tType']]['categories']:
				months[m][t['tType']]['categories'].append(t['category'])
				months[m][t['tType']]['categoryTotals'].append(t['amount'])
			else:
				categoryIndex = months[m][t['tType']]['categories'].index(t['category'])
				months[m][t['tType']]['categoryTotals'][categoryIndex] += t['amount']

		return months
