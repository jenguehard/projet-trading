import requests
from pymongo import MongoClient
from bson import json_util
import math
import numpy as np
import pandas as pd
import tensorflow
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, LSTM, Dropout
import config
import os

username = config.mongo_user
password = config.mongo_pw

mongobase = config.mongo_db

connection = MongoClient('mongodb+srv://'+str(username)+':'+str(password)+'@'+str(mongobase)+'.mongodb.net/test?authSource=admin&replicaSet=BaseDB-shard-0&readPreference=primary&appname=MongoDB%20Compass%20Community&ssl=true')

sp500 = pd.read_csv("constituents.csv")

company = input("Please choose a S&P500 company:")

if company not in sp500["Name"].to_list():
    print("The S&P500 companies are the following: ")
    print(sp500["Name"].to_list())
    company = input("Please choose from this list: ")

print("You have chosen " + company + ".")

# Based on the company chose, we get the correct symbol and then get the data from our Mongo database.

symbol = sp500[sp500["Name"]==company]["Symbol"].reset_index()["Symbol"][0]

print(symbol)

def get_model(symbol):
    db = connection[symbol]
    collection = db.stock
    df =  pd.DataFrame(list(collection.find()))
    df._id = pd.to_datetime(df._id, infer_datetime_format=True)
    df = df.sort_values("_id", ascending = True)
    # Create a new dataframe with only the 'Close' column
    data = df.filter(['close'])
    # Converting the dataframe to a numpy array
    dataset = data.values
    # Get /Compute the number of rows to train the model on
    training_data_len = math.ceil(len(dataset)*.8)
    # Scale the all of the data to be values between 0 and 1 
    scaler = MinMaxScaler(feature_range=(0, 1)) 
    scaled_data = scaler.fit_transform(dataset)
    # Create the scaled training data set 
    train_data = scaled_data[0:training_data_len  , : ]
    # Split the data into x_train and y_train data sets
    x_train=[]
    y_train = []
    for i in range(60,len(train_data)):
        x_train.append(train_data[i-60:i,0])
        y_train.append(train_data[i,0])
    # Convert x_train and y_train to numpy arrays
    x_train, y_train = np.array(x_train), np.array(y_train)
    # Reshape the data into the shape accepted by the LSTM
    x_train = np.reshape(x_train, (x_train.shape[0],x_train.shape[1],1))
    # Build the LSTM network model
    model = Sequential()
    model.add(LSTM(units=50, return_sequences=True,input_shape=(x_train.shape[1],1)))
    model.add(LSTM(units=50, return_sequences=False))
    model.add(Dense(units=25))
    model.add(Dense(units=1))
    # Compile the model
    model.compile(optimizer='adam', loss='mean_squared_error')
    # Train the model
    model.fit(x_train, y_train, batch_size=1, epochs=2)
    # Test data set
    test_data = scaled_data[training_data_len - 60: , : ]
    # Create the x_test and y_test data sets
    x_test = []
    y_test =  dataset[training_data_len : , : ]
    # Get all of the rows from the start of test to the rest and all of the columns 
    # (in this case it's only column 'close')
    for i in range(60,len(test_data)):
        x_test.append(test_data[i-60:i,0])
    # Convert x_test to a numpy array 
    x_test = np.array(x_test)
    # Reshape the data into the shape accepted by the LSTM
    x_test = np.reshape(x_test, (x_test.shape[0],x_test.shape[1],1))
    # Getting the models predicted price values
    predictions = model.predict(x_test) 
    predictions = scaler.inverse_transform(predictions)#Undo scaling
    # Calculate/Get the value of RMSE
    rmse=np.sqrt(np.mean(((predictions- y_test)**2)))
    print("The RMSE of this model is : " + str(rmse))
    # We create a directory "model" to save our model
    if not os.path.exists('model'):
        os.makedirs('model')
    # We save the model in the directory
    model.save("model\\"+symbol+".h5")
    print("The model has been saved.")
    return model

if __name__ == "__main__":
    get_model(symbol)