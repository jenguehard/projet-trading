# This file is bound to create the streamlit application.

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
import config
import sys
import tensorflow as tf
from pymongo import MongoClient
from tensorflow.keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
from tensorflow import keras
import joblib
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

st.title("Stock Predictions with LSTM")

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

number_of_days = st.slider("Days to be predicted :", 1, 10)

model = keras.models.load_model('model/'+symbol+".h5")
scaler = joblib.load('model/scaler_'+symbol+'.pkl')

def predictions(days):
  # Create a new dataframe
  new_df = df.filter(['close'])
  # Get the last 60 day closing price 
  last_60_days = new_df[-60:].values
  predicted_prices=[]
  for i in range(days):
    #Scale the data to be values between 0 and 1
    last_60_days_scaled = scaler.transform(last_60_days)
    #Create an empty list
    X_test = []
    #Append teh past 60 days
    X_test.append(last_60_days_scaled)
    #Convert the X_test data set to a numpy array
    X_test = np.array(X_test)
    #Reshape the data
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
    #Get the predicted scaled price
    pred_price = model.predict(X_test)
    #undo the scaling 
    pred_price = scaler.inverse_transform(pred_price)
    predicted_prices.append(float(pred_price[0][0]))
    last_60_days_list = last_60_days.tolist()
    last_60_days_list.pop(0)
    last_60_days_list.append([pred_price[0][0]])
    last_60_days = np.array(last_60_days_list)
  return predicted_prices

pred = round(predictions(number_of_days)[number_of_days-1], 2)

e = '%Y-%m-%d %H:%M:%S'
d = datetime.datetime.strptime(str(df.index[-1]), e)
today = datetime.datetime.strftime(d, '%Y-%m-%d')

st.write("The last quotation on "+str(today)+" was "+str(df.close[-1])+"$.")

st.write("In "+str(number_of_days)+" days, the stock value will be "+str(pred)+"$.")

if df.close[-1] < pred:
  st.write("You should BUY !")
else:
  st.write("You should SELL !")

st.title("Notifications")

stock_notif = st.multiselect("Which stocks are you interested in ?", stocks)


notifications = []

def send_notif():
  if number_of_days == 1:
    email_subject = "Stock predictions for tomorrow."
  else :
    email_subject = "Stock predictions for the next "+ str(number_of_days) +" days."
  email_body = "Hello,\n"

  for i in stock_notif:
    db = connection[symbol]
    collection = db.stock

    df =  pd.DataFrame(list(collection.find()))
    df._id = pd.to_datetime(df._id, infer_datetime_format=True)
    df = df.sort_values("_id", ascending = True)
    df = df.set_index("_id")
    pred = round(predictions(number_of_days)[number_of_days-1], 2)

    if df.close[-1] < pred:
      notif = "You should BUY !"
    else:
      notif = "You should SELL !"
    
    email_body += i + " - " + str(sp500[sp500["Symbol"]==i]["Name"].values[0]) + " : " + notif + " Last closing price was : " + str(df.close[-1])+"$. In "+str(number_of_days)+" days, the stock value will be "+str(pred)+"$.\n"

  server = smtplib.SMTP(config.email_smtp_server,config.email_smtp_port)
  server.starttls()
  server.login(config.email_sender_username, config.email_sender_password)

  for recipient in config.email_recepients:
    print(f"Sending email to {recipient}")
    message = MIMEMultipart('alternative')
    message['From'] = config.email_sender_account
    message['To'] = recipient
    message['Subject'] = email_subject
    message.attach(MIMEText(email_body, 'html'))
    text = message.as_string()
    server.sendmail(config.email_sender_account,recipient,text)
  #All emails sent, log out.
  server.quit()
  
if st.button('Send notifications'):
    send_notif()
    st.write('Notifications have been sent.')

