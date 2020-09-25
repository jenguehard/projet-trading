"# projet-trading" 

This project was created to test LSTM on stock predictions of the Dow Jones.

We will first get the data through AlphaVantage API's and stock it on MongoDB. The files required are the following :

In order to get your AlphaVantage API's key, please use this [AlphaVantage API key](https://www.alphavantage.co/support/#api-key).

You will also need to create a MongoDB account, please use this [MongoDB link](https://www.mongodb.com/try). You can retrieve your MongoDB credentials from your cluster.

```
load_data_dj30.py
dj30.xls
```

In order to connect to your MongoDB, you will need to install the last version of ```dnspython``` and restart your terminal with the following command :

```
pip3 install pymongo[srv]
```

You will also need to create a file ```config.py``` where you will put your MongoDB's credentials and email credentials for the notifications. This file can't be uploaded to github for obvious reasons.

```
api_key = "Your AlphaVantage API key"
mongo_db = "The name of your MongoDB"
mongo_user = "Your MongoDB username"
mongo_pw = "Your MongoDB password"

email_sender_account = "Your email"
email_sender_username = "Your email username"
email_sender_password = "Your email password"
email_smtp_server = "The smpt address of your mail exchange server (ex : smtp.gmail.com for Gmail)"
email_smtp_port = The smpt port of your mail exchange server (ex: 587 for Gmail)
email_recepients = ["Email address of recipient 1", "Email address of recipient 2", ...]
```

The different files will call the ```config.py``` to work.

The file ```create_model.py``` will create a scaler model and a LSTM model for each company.

You can then use the ```app.py``` file with [Streamlit](https://www.streamlit.io/). The app can be started with the following command :

```
streamlit run app.py
```

Please note that this file will only work if your MongoDB's database is populated with the value of each stock. This is done with ```load_data_dj30.py``` file.
