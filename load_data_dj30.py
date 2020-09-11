import requests
from pymongo import MongoClient
import pandas as pd
from bson import json_util
import config
import time

# The objective of this file is to upload the stock value of a company on a Mongo database.
# The stock value is retrieved with Alpha Vantage API.
# On the Dow Jones, each company is defined by a symbol.

# First we need to get the symbol of the company we are looking for. This can be done using the
# "dj30.xls" file.

dj30 = pd.read_excel("dj30.xls")

# Based on the company chose, we get the correct symbol and then get the result from Alpha
# Vantage's API.

for company in dj30["name"].values:
    print(company)

    symbol = dj30[dj30["name"]==company]["ticker"].values[0]

    print(symbol)

    apikey = config.api_key

    url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&outputsize=full&symbol="+symbol+"&apikey="+str(apikey)
    try:
        response = requests.request("GET", url)

        data = json_util.loads(response.text)

        # The next few steps are done to be able to upload a document per day on our Mongo database. We will
        # do one database per company, then one collection for stock and one collection for news.

        # First we get only the data from the key "Time Series (Daily)" of data and rename the columns. It is
        # required by Mongo for the upload. Then we create a list of dictionnary - a dictionnary per day.

        data = pd.DataFrame.from_dict(data["Time Series (Daily)"])
        data = data.rename(index={'1. open':"open", '2. high':"high", '3. low':"low", '4. close':"close", '5. volume':"volume"}).astype(float)
        # print(data)
        data = data.to_dict()
        data_list = []

        for i in list(data.keys()):
            # print(data[i])
            new_dict = {}
            new_dict["_id"] = i
            new_dict["open"] = data[i]["open"]
            new_dict["high"] = data[i]["high"]
            new_dict["low"] = data[i]["low"]
            new_dict["close"] = data[i]["close"]
            new_dict["volume"] = data[i]["volume"]
            data_list.append(new_dict)

        # print(data_list)

        # We make our connection to our database thank to pymongo library.

        username = config.mongo_user
        password = config.mongo_pw

        mongobase = config.mongo_db

        connection = MongoClient('mongodb+srv://'+str(username)+':'+str(password)+'@'+str(mongobase)+'.mongodb.net/test?authSource=admin&replicaSet=BaseDB-shard-0&readPreference=primary&appname=MongoDB%20Compass%20Community&ssl=true')
        # print(connection.list_database_names())

        # We connect to our database and upload the data retrieved from Alpha Vantage's API.

        mydb = connection[symbol]
        mycol = mydb["stock"]

        try :
            mycol.insert_many(data_list)
            print(symbol + ": Stocks added !")
        except:
            print("Already up to date !")
    except:
        pass
    time.sleep(10)