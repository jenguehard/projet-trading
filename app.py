# This file is bound to create the streamlit application.

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import config
from pymongo import MongoClient

sp500 = pd.read_csv("constituents.csv")

username = config.mongo_user
password = config.mongo_pw

mongobase = config.mongo_db

connection = MongoClient('mongodb+srv://'+str(username)+':'+str(password)+'@'+str(mongobase)+'.mongodb.net/test?authSource=admin&replicaSet=BaseDB-shard-0&readPreference=primary&appname=MongoDB%20Compass%20Community&ssl=true')

stocks = []

for i in connection.list_database_names():
  if i in sp500.Symbol.to_list():
    stocks.append(i)

stocks_name = []

for i in stocks:
    stocks_name.append(sp500[sp500["Symbol"]==i]["Name"].values[0])

option = st.selectbox('On which stock would you like a prediction ?', stocks_name)

symbol = sp500[sp500["Name"]==option]["Symbol"].values[0]

db = connection[symbol]
collection = db.stock

df =  pd.DataFrame(list(collection.find()))
df._id = pd.to_datetime(df._id, infer_datetime_format=True)
df = df.sort_values("_id", ascending = True)
df = df.set_index("_id")
#Visualize the closing price history
plt.figure(figsize=(24,12))
plt.title('Close Price History')
plt.plot(df['close'])
plt.xlabel('Date',fontsize=18)
plt.ylabel('Close Price USD ($)',fontsize=18)
plt.show()

st.pyplot(plt)
