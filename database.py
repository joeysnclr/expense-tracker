import pymongo, json, random, string, datetime, os

URI = os.environ['EXPENSE_MONGO']


client = pymongo.MongoClient(URI)
db = client["expense-tracker"]
dbusers = db["users"]



def getUserSchema():
	return {
		"email": "string",
		"password": "hashed",
		"transactions": []
	}

def getTransactionSchema():
	return {
		"tId": ''.join(random.choices(string.ascii_uppercase + string.digits, k=16)),
		"amount": 0.00,
		"date": datetime.datetime(2020, 1, 1),
		"tType": "income/spent",
		"category": "string",
		"name": "string"
	}


